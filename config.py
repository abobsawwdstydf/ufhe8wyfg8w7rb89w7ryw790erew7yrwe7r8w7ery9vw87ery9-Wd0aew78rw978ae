"""Конфигурация из переменных окружения"""
import os
from dotenv import load_dotenv

load_dotenv()

# База данных
DATABASE_URL = os.getenv("DATABASE_URL")

# Токены ботов
BOTS = {
    "corporate": os.getenv("CORPORATE_BOT_TOKEN"),
    "link_shortener": os.getenv("LINK_SHORTENER_BOT_TOKEN"),
    "support": os.getenv("SUPPORT_BOT_TOKEN"),
    "uid_info": os.getenv("UID_INFO_BOT_TOKEN"),
}

# Admin ID
ADMIN_ID = int(os.getenv("ADMIN_ID", 0))
