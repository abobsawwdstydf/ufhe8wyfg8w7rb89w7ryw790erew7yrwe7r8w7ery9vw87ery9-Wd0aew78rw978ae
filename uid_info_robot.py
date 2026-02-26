"""UID Info Bot - получение ID пользователя по username"""
import logging
from uuid import uuid4
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, InlineQueryHandler, filters
from telegram.error import BadRequest
from config import BOTS
from database import add_uid_request, get_user_requests_count

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)


async def start(update: Update, context):
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("🧑‍💻 Разработчик", url="https://t.me/haker_one")],
        [InlineKeyboardButton("🛠️ Техподдержка", url="https://t.me/dark_heavens_support_bot")]
    ])
    
    text = (
        "Привет! 👋 Я бот для получения ID пользователя Telegram.\n\n"
        "**Как использовать:**\n"
        "1. Отправь username с @ (например, @telegram)\n"
        "2. Или используй inline: @uid_info_robot @username\n"
    )
    
    try:
        await update.message.reply_photo(
            photo="https://www.darkheavens.ru/e5d8a8cf9640c657f9daae6587e33d94.jpg",
            caption=text,
            reply_markup=keyboard,
            parse_mode='Markdown'
        )
    except:
        await update.message.reply_text(text, reply_markup=keyboard, parse_mode='Markdown')


async def handle_username(update: Update, context):
    username = update.message.text
    
    if not username.startswith('@'):
        await update.message.reply_text("Username должен начинаться с @ 🙁")
        return
    
    try:
        # Получаем ID пользователя
        chat = await context.bot.get_chat(username)
        user_id = chat.id
        
        # Сохраняем в БД
        add_uid_request(update.effective_user.id, username, user_id)
        
        await update.message.reply_text(
            f"ID пользователя {username}: `{user_id}`",
            parse_mode='Markdown'
        )
        logger.info(f"Запрос ID для {username} от пользователя {update.effective_user.id}")
        
    except BadRequest as e:
        await update.message.reply_text(f"Не удалось найти пользователя {username} 😔\nОшибка: {e}")
    except Exception as e:
        await update.message.reply_text(f"Произошла ошибка: {e}")


async def inline_query(update: Update, context):
    query = update.inline_query.query
    
    if not query.startswith('@'):
        results = [{
            'type': 'article', 'id': uuid4().hex,
            'title': "Пример использования",
            'input_message_content': {'message_text': "Используйте: @uid_info_robot @username"},
            'description': "Например: @uid_info_robot @telegram"
        }]
        await update.answer(results)
        return
    
    try:
        chat = await context.bot.get_chat(query)
        user_id = chat.id
        
        # Сохраняем в БД
        add_uid_request(update.effective_user.id, query, user_id)
        
        results = [{
            'type': 'article', 'id': uuid4().hex,
            'title': f"ID: {user_id}",
            'input_message_content': {'message_text': f"ID пользователя {query}: `{user_id}`"},
            'description': f"Нажмите чтобы отправить ID"
        }]
        await update.answer(results, cache_time=0)
        
    except Exception as e:
        results = [{
            'type': 'article', 'id': uuid4().hex,
            'title': "Ошибка",
            'input_message_content': {'message_text': f"Не удалось найти пользователя {query}"},
            'description': str(e)
        }]
        await update.answer(results)


def main():
    app = Application.builder().token(BOTS["uid_info"]).build()
    
    app.add_handler(CommandHandler('start', start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_username))
    app.add_handler(InlineQueryHandler(inline_query))
    
    logger.info("UID Info bot запущен")
    app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == '__main__':
    main()
