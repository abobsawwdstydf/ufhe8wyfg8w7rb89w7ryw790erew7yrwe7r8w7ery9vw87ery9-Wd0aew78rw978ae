#!/usr/bin/env python3
"""
Лаунчер для запуска всех ботов
Запускает всех ботов асинхронно
"""
import subprocess
import sys
import asyncio
import logging
from database import init_db

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)


def install_dependencies():
    """Автоматическая установка зависимостей"""
    logger.info("📦 Проверка зависимостей...")
    try:
        subprocess.check_call(
            [sys.executable, "-m", "pip", "install", "-r", "requirements.txt", "-q"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
        logger.info("✅ Все зависимости установлены")
    except Exception as e:
        logger.error(f"❌ Ошибка установки зависимостей: {e}")
        sys.exit(1)


async def run_bot(name, bot_module):
    """Запускает бота асинхронно"""
    logger.info(f"🚀 Запуск {name}...")
    try:
        app = bot_module.Application.builder().token(bot_module.BOTS[bot_module.BOT_NAME]).build()
        bot_module.register_handlers(app)
        logger.info(f"✅ {name} запущен")
        await app.run_polling(allowed_updates=bot_module.Update.ALL_TYPES)
    except Exception as e:
        logger.error(f"❌ Ошибка {name}: {e}")


async def main_async():
    """Асинхронный запуск всех ботов"""
    # Импортируем модули ботов
    import Dark_Heavens_Corporate_bot as corporate
    import SR_Link_ROBOT as link_shortener
    import support_bot as support
    import uid_info_robot as uid_info
    
    # Инициализируем базу данных
    logger.info("📊 Инициализация базы данных...")
    try:
        init_db()
    except Exception as e:
        logger.error(f"❌ Ошибка инициализации БД: {e}")
        return
    
    # Запускаем всех ботов одновременно
    tasks = [
        run_bot("Corporate Bot", corporate),
        run_bot("Link Shortener Bot", link_shortener),
        run_bot("Support Bot", support),
        run_bot("UID Info Bot", uid_info),
    ]
    
    await asyncio.gather(*tasks)


def main():
    # Автоматическая установка зависимостей
    install_dependencies()
    
    # Запускаем асинхронный цикл
    asyncio.run(main_async())


if __name__ == '__main__':
    main()
