#!/usr/bin/env python3
"""
Лаунчер для запуска всех ботов
"""
import subprocess
import sys
import asyncio
import logging
from telegram import Update
from telegram.ext import Application
from database import init_db

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)


def install_dependencies():
    """Автоматическая установка зависимостей"""
    logger.info("📦 Установка зависимостей...")
    try:
        subprocess.check_call(
            [sys.executable, "-m", "pip", "install", "--upgrade", "--force-reinstall", "-r", "requirements.txt"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
        logger.info("✅ Все зависимости установлены")
    except Exception as e:
        logger.error(f"❌ Ошибка установки зависимостей: {e}")
        sys.exit(1)


async def run_bot(name, token, register_func):
    """Запускает бота"""
    logger.info(f"🚀 Запуск {name}...")
    try:
        app = Application.builder().token(token).build()
        register_func(app)
        
        # Инициализируем и запускаем polling
        await app.initialize()
        await app.updater.start_polling(allowed_updates=Update.ALL_TYPES)
        logger.info(f"✅ {name} запущен")
        
        # Держим бота запущенным
        while True:
            await asyncio.sleep(1)
    except Exception as e:
        logger.error(f"❌ Ошибка {name}: {e}")
        raise


async def main_async():
    """Асинхронный запуск всех ботов"""
    # Импортируем модули ботов
    import Dark_Heavens_Corporate_bot as corporate
    import SR_Link_ROBOT as link_shortener
    import support_bot as support
    import uid_info_robot as uid_info
    from config import BOTS
    
    # Инициализируем базу данных
    logger.info("📊 Инициализация базы данных...")
    try:
        init_db()
        logger.info("✅ База данных готова")
    except Exception as e:
        logger.error(f"❌ Ошибка инициализации БД: {e}")
        return
    
    # Запускаем всех ботов одновременно
    tasks = [
        run_bot("Corporate Bot", BOTS["corporate"], corporate.register_handlers),
        run_bot("Link Shortener Bot", BOTS["link_shortener"], link_shortener.register_handlers),
        run_bot("Support Bot", BOTS["support"], support.register_handlers),
        run_bot("UID Info Bot", BOTS["uid_info"], uid_info.register_handlers),
    ]
    
    logger.info("🎉 Запуск всех ботов...")
    try:
        await asyncio.gather(*tasks)
    except Exception as e:
        logger.error(f"❌ Критическая ошибка: {e}")
        raise


def main():
    install_dependencies()
    asyncio.run(main_async())


if __name__ == '__main__':
    main()
