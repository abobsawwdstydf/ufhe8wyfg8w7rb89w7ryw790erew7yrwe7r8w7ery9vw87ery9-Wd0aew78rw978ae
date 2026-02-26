#!/usr/bin/env python3
"""
Лаунчер для запуска всех ботов
Запускает ботов по очереди с интервалом 1 секунда
"""
import subprocess
import sys
import time
import threading
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


def run_bot(name, module):
    """Запускает бота в отдельном потоке"""
    try:
        logger.info(f"🚀 Запуск {name}...")
        module.main()
    except Exception as e:
        logger.error(f"❌ Ошибка {name}: {e}")


def main():
    # Автоматическая установка зависимостей
    install_dependencies()
    
    # Инициализируем базу данных
    logger.info("📊 Инициализация базы данных...")
    try:
        init_db()
    except Exception as e:
        logger.error(f"❌ Ошибка инициализации БД: {e}")
        return
    
    # Импортируем модули ботов
    import Dark_Heavens_Corporate_bot as corporate
    import SR_Link_ROBOT as link_shortener
    import support_bot as support
    import uid_info_robot as uid_info
    
    bots = [
        ("Corporate Bot", corporate),
        ("Link Shortener Bot", link_shortener),
        ("Support Bot", support),
        ("UID Info Bot", uid_info),
    ]
    
    threads = []
    
    # Запускаем каждого бота с интервалом 1 секунда
    for name, module in bots:
        thread = threading.Thread(target=run_bot, args=(name, module), daemon=True)
        thread.start()
        threads.append(thread)
        logger.info(f"✅ {name} запущен")
        time.sleep(1)  # Интервал между запусками
    
    logger.info("🎉 Все боты запущены!")
    
    # Ждем завершения всех потоков
    for thread in threads:
        thread.join()


if __name__ == '__main__':
    main()
