"""Dark Heavens Corporate Bot - визитка с ссылками на другие боты"""
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler
from config import BOTS
from database import add_corporate_user

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

IMAGE_URL = "https://www.darkheavens.ru/17e6eda0db7a08ef104de6cade1fd77a.jpg"

KEYBOARD = [
    [InlineKeyboardButton("DH Learning 🐍🧠", url="https://t.me/DH_Learningbot")],
    [InlineKeyboardButton("DHA AI V8.6 🧠🧠", url="https://t.me/dhaai_bot")],
    [InlineKeyboardButton("Создай своего ИИ агента 🎭", url="https://t.me/Create_AI_agents_bot")],
    [InlineKeyboardButton("Wi_iW 🤖", url="https://t.me/Wi_iW_bot")],
    [InlineKeyboardButton("Заметочник 📝", url="https://t.me/hity_byli_bot")],
    [InlineKeyboardButton("Узнай любой айди 🆔", url="https://t.me/uid_info_robot")],
    [InlineKeyboardButton("Кликер 🖱️", url="https://t.me/DH_clicker_bot")],
    [InlineKeyboardButton("Угадай число 🔢", url="https://t.me/Guess_number_robot")],
    [InlineKeyboardButton("Создавай inline кнопки ➕", url="https://t.me/K_inline_bot")],
    [InlineKeyboardButton("Сокращатель ссылок 🔗", url="https://t.me/SR_Link_ROBOT")],
    [InlineKeyboardButton("Анонимный чат 💬", url="https://t.me/Endipi_bot")],
    [InlineKeyboardButton("Голос в текст 🗣️", url="https://t.me/DH_Voxity_bot")],
    [InlineKeyboardButton("Шахта бот ⛏️", url="https://t.me/DH_SHAHTA_ROBOT")],
    [InlineKeyboardButton("Botify ✨", url="https://t.me/DH_Botify_bot")],
    [InlineKeyboardButton("Dark GPT бот 🧠", url="https://t.me/Dark_ai_GPT_bot")],
    [InlineKeyboardButton("Продвижение 📈", url="https://t.me/dark_heavens_promotions_bot")],
    [InlineKeyboardButton("Noir AI 🎨", url="https://t.me/Noir_AI_bot")],
    [InlineKeyboardButton("Dark SIM 📱", url="https://t.me/dark_heavens_sim_bot")],
    [InlineKeyboardButton("BILLY CLICKS 🎮", url="https://t.me/Billy_clicksbot")],
    [InlineKeyboardButton("BILLY CLICKS (сайт)", url="http://billy.darkheavens.ru:25463")],
    [InlineKeyboardButton("DH GPT (APK) 🤖📱", url="https://www.darkheavens.ru/Dark_Heavens_GPT.apk")],
    [InlineKeyboardButton("DH PROXY🤖", url="https://proxy.darkheavens.ru")],
    [InlineKeyboardButton("DH Learning (сайт)", url="https://learning.darkheavens.ru/")],
    [InlineKeyboardButton("Канал 📰", url="https://t.me/dark_heavens_ru")],
    [InlineKeyboardButton("ТехПоддержка 🆘", url="https://t.me/dark_heavens_support_bot")],
    [InlineKeyboardButton("Разработчик 👨‍💻", url="https://t.me/haker_one")]
]


async def start(update: Update, context):
    user = update.effective_user
    name = user.first_name or user.username or "Пользователь"
    
    # Сохраняем пользователя в БД
    add_corporate_user(user.id, user.username, user.first_name)
    
    message = f"👋 Привет, {name}!\n🤖 Я - бот Dark Heavens Corporate! 🌌\n\nВсе разработки ниже от @haker_one."
    
    await context.bot.send_photo(
        chat_id=update.effective_chat.id,
        photo=IMAGE_URL,
        caption=message,
        reply_markup=InlineKeyboardMarkup(KEYBOARD)
    )


def main():
    app = Application.builder().token(BOTS["corporate"]).build()
    app.add_handler(CommandHandler('start', start))
    logger.info("Corporate bot запущен")
    app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == '__main__':
    main()
