"""Support Bot - система тикетов поддержки"""
import logging
from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ForceReply
from telegram.ext import (
    Application, CommandHandler, MessageHandler, CallbackQueryHandler,
    ConversationHandler, filters
)
from config import BOTS, ADMIN_ID
from database import (
    create_ticket, update_ticket_status, add_ticket_note, resolve_ticket,
    get_ticket, get_next_ticket_id, get_all_tickets, get_stats
)

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

BOT_NAME = "support"
STATUSES = {"new": "Новый", "progress": "В обработке", "resolved": "Решено"}
PRIORITIES = {"1": "Низкий", "2": "Средний", "3": "Высокий"}

CREATE_TICKET, CHOOSE_PRIORITY, ADD_NOTE = range(3)


async def start(update: Update, context):
    if update.effective_user.id == ADMIN_ID:
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("📋 Тикеты", callback_data="list_tickets")],
            [InlineKeyboardButton("📊 Статистика", callback_data="show_stats")]
        ])
        await update.message.reply_text("Привет, Админ! 👑", reply_markup=keyboard)
    else:
        await update.message.reply_text("Здравствуйте! 👋 Опишите проблему, и я создам тикет. 🚀")


async def help_command(update: Update, context):
    if update.effective_user.id == ADMIN_ID:
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("📋 Тикеты", callback_data="list_tickets")],
            [InlineKeyboardButton("📊 Статистика", callback_data="show_stats")]
        ])
        text = "⚙️ Панель Администратора\n\n/new - Создать тикет\n/list - Показать тикеты"
    else:
        keyboard = InlineKeyboardMarkup([[InlineKeyboardButton("Создать тикет", callback_data="create_ticket")]])
        text = "🆘 Поддержка\n\nОпишите проблему или нажмите кнопку ниже."
    
    await update.message.reply_text(text, reply_markup=keyboard)


async def create_ticket_start(update: Update, context):
    if update.effective_user.id == ADMIN_ID:
        await update.message.reply_text("Админы не могут создавать тикеты. 🚫")
        return ConversationHandler.END
    
    context.user_data['msg'] = update.message.text
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton(f"{v} - {k}", callback_data=f"prio_{k}") for k, v in PRIORITIES.items()]
    ])
    await update.message.reply_text("Выберите приоритет:", reply_markup=keyboard)
    return CHOOSE_PRIORITY


async def set_priority(update: Update, context):
    query = update.callback_query
    await query.answer()
    
    priority = PRIORITIES[query.data.split('_')[1]]
    user = update.effective_user
    
    ticket_id = str(get_next_ticket_id())
    create_ticket(
        ticket_id, user.id, user.username, user.first_name,
        user.last_name or "", context.user_data['msg'], priority
    )
    
    await query.edit_message_text(f"Тикет #{ticket_id} создан! Приоритет: {priority} ✅")
    
    admin_text = (
        f"🚨 Тикет #{ticket_id}\n"
        f"👤 {user.first_name} @{user.username} (ID: {user.id})\n"
        f"📝 {context.user_data['msg']}\n"
        f"Приоритет: {priority}"
    )
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("⏳ В работу", callback_data=f"work_{ticket_id}")],
        [InlineKeyboardButton("✅ Решить", callback_data=f"resolve_{ticket_id}")],
        [InlineKeyboardButton("📝 Заметка", callback_data=f"note_{ticket_id}")]
    ])
    await context.bot.send_message(ADMIN_ID, admin_text, reply_markup=keyboard)
    logger.info(f"Тикет #{ticket_id} создан")
    
    context.user_data.clear()
    return ConversationHandler.END


async def list_tickets(update: Update, context):
    if update.effective_user.id != ADMIN_ID:
        return
    
    tickets = get_all_tickets()
    if not tickets:
        await update.callback_query.answer("Нет активных тикетов!")
        return
    
    for t in tickets:
        text = (
            f"🎫 #{t['ticket_id']}\n"
            f"👤 {t['username']} (ID: {t['user_id']})\n"
            f"📝 {t['message']}\n"
            f"Приоритет: {t['priority']}\n"
            f"Статус: {t['status']}"
        )
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("⏳ В работу", callback_data=f"work_{t['ticket_id']}")],
            [InlineKeyboardButton("✅ Решить", callback_data=f"resolve_{t['ticket_id']}")],
            [InlineKeyboardButton("📝 Заметка", callback_data=f"note_{t['ticket_id']}")]
        ])
        await context.bot.send_message(ADMIN_ID, text, reply_markup=keyboard)
    
    await update.callback_query.answer()


async def show_stats(update: Update, context):
    if update.effective_user.id != ADMIN_ID:
        return
    
    total = get_stats()
    await context.bot.send_message(ADMIN_ID, f"📊 Статистика:\n\nРешено тикетов: {total}")
    await update.callback_query.answer()


async def ticket_callback(update: Update, context):
    query = update.callback_query
    await query.answer()
    
    data = query.data.split('_')
    action, ticket_id = data[0], data[1]
    
    if action == "work":
        update_ticket_status(ticket_id, STATUSES["progress"], update.effective_user.id)
        await query.edit_message_text(f"Тикет #{ticket_id} взят в работу ⏳")
    
    elif action == "resolve":
        resolve_ticket(ticket_id)
        await query.edit_message_text(f"Тикет #{ticket_id} решен ✅")
    
    elif action == "note":
        context.user_data['note_ticket'] = ticket_id
        await query.message.reply_text(f"Заметка для #{ticket_id}:", reply_markup=ForceReply())
        return ADD_NOTE
    
    logger.info(f"Админ {action} тикет #{ticket_id}")


async def add_note(update: Update, context):
    ticket_id = context.user_data.get('note_ticket')
    if not ticket_id:
        return ConversationHandler.END
    
    add_ticket_note(ticket_id, update.message.text)
    await update.message.reply_text(f"Заметка добавлена к #{ticket_id} ✅")
    context.user_data.clear()
    return ConversationHandler.END


async def cancel(update: Update, context):
    context.user_data.clear()
    await update.message.reply_text("Отменено.")
    return ConversationHandler.END


def register_handlers(app):
    """Регистрация хендлеров"""
    conv = ConversationHandler(
        entry_points=[MessageHandler(filters.TEXT & ~filters.COMMAND, create_ticket_start)],
        states={
            CHOOSE_PRIORITY: [CallbackQueryHandler(set_priority, pattern=r"^prio_")],
            ADD_NOTE: [MessageHandler(filters.TEXT & ~filters.COMMAND, add_note)]
        },
        fallbacks=[CommandHandler("cancel", cancel)]
    )
    
    app.add_handler(conv)
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CallbackQueryHandler(ticket_callback, pattern=r"^(work|resolve|note)_"))
    app.add_handler(CallbackQueryHandler(list_tickets, pattern="^list_tickets"))
    app.add_handler(CallbackQueryHandler(show_stats, pattern="^show_stats"))


def main():
    """Для автономного запуска"""
    app = Application.builder().token(BOTS[BOT_NAME]).build()
    register_handlers(app)
    logger.info("Support bot запущен")
    app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == '__main__':
    main()
