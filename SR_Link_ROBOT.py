"""SR Link - сокращатель и раскрыватель ссылок"""
import logging
import requests
from uuid import uuid4
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, InlineQueryHandler, filters
from config import BOTS
from database import add_shortened_link, get_user_links_count

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

BOT_NAME = "link_shortener"


def shorten_url(long_url):
    """Сокращаем ссылку через clck.ru"""
    try:
        resp = requests.get('https://clck.ru/--', params={'url': long_url}, timeout=5)
        resp.raise_for_status()
        return resp.text.strip()
    except Exception as e:
        logger.error(f"Ошибка сокращения URL: {e}")
        return None


def is_valid_url(url):
    """Проверка валидности URL"""
    return url.startswith(('http://', 'https://')) and ' ' not in url


async def start(update: Update, context):
    name = update.effective_user.first_name or "Пользователь"
    text = (
        f"Привет, {name}! 👋\n\n"
        "Я Сокращатель ссылок SR Link! 🔗\n\n"
        "Что я умею:\n"
        "✂️ Сокращать длинные ссылки\n"
        "🔍 Раскрывать короткие ссылки\n\n"
        "Просто отправь мне URL!"
    )
    try:
        await update.message.reply_photo(
            photo="https://www.darkheavens.ru/cec89b42919ff8b77a477b35d71a1a17.jpg",
            caption=text
        )
    except:
        await update.message.reply_text(text)


async def handle_message(update: Update, context):
    link = update.message.text
    
    if not is_valid_url(link):
        await update.message.reply_text("⚠️ Некорректный URL. Должен начинаться с http:// или https://")
        return
    
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("Сократить ✂️", callback_data=f"short:{link}")],
        [InlineKeyboardButton("Раскрыть 🔍", callback_data=f"unshort:{link}")]
    ])
    await update.message.reply_text("Выберите действие:", reply_markup=keyboard)


async def callback_handler(update: Update, context):
    query = update.callback_query
    await query.answer()
    
    action, link = query.data.split(':', 1)
    
    if action == "unshort":
        try:
            resp = requests.get(link, allow_redirects=False, timeout=5)
            expanded = resp.headers.get('Location', link)
            await query.edit_message_text(f"Раскрытый URL:\n{expanded}")
        except Exception as e:
            await query.edit_message_text(f"⚠️ Не удалось раскрыть URL: {e}")
    
    elif action == "short":
        shortened = shorten_url(link)
        if shortened:
            add_shortened_link(update.effective_user.id, link, shortened.split('/')[-1])
            await query.edit_message_text(f"Сокращенный URL:\n{shortened}")
        else:
            await query.edit_message_text("⚠️ Не удалось сократить URL")


async def inline_query(update: Update, context):
    link = update.inline_query.query
    
    if not is_valid_url(link):
        results = [{
            'type': 'article', 'id': uuid4().hex,
            'title': "Некорректный URL",
            'input_message_content': {'message_text': "Введите валидный URL"},
            'description': "URL должен начинаться с http:// или https://"
        }]
        await update.answer(results)
        return
    
    shortened = shorten_url(link)
    results = [
        {
            'type': 'article', 'id': uuid4().hex,
            'title': "Сократить ✂️",
            'input_message_content': {'message_text': shortened or "Ошибка"},
            'description': "Нажмите для сокращения"
        },
        {
            'type': 'article', 'id': uuid4().hex,
            'title': "Раскрыть 🔍",
            'input_message_content': {'message_text': link},
            'description': "Нажмите для раскрытия"
        }
    ]
    await update.answer(results)


def register_handlers(app):
    """Регистрация хендлеров"""
    app.add_handler(CommandHandler('start', start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.add_handler(CallbackQueryHandler(callback_handler))
    app.add_handler(InlineQueryHandler(inline_query))


def main():
    """Для автономного запуска"""
    app = Application.builder().token(BOTS[BOT_NAME]).build()
    register_handlers(app)
    logger.info("Link Shortener bot запущен")
    app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == '__main__':
    main()
