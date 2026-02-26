#!/usr/bin/env python3
"""
Лаунчер для запуска всех ботов
"""
import subprocess
import sys
import asyncio
import logging
import os
from http.server import HTTPServer, BaseHTTPRequestHandler
from telegram import Update
from telegram.ext import Application
from telegram.error import TimedOut, NetworkError
from database import init_db

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)


class HealthHandler(BaseHTTPRequestHandler):
    """HTTP сервер для health checks"""
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/plain')
        self.end_headers()
        self.wfile.write(b'OK')
    
    def log_message(self, format, *args):
        pass  # Отключаем логи HTTP


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
    """Запускает бота с перезапуском при ошибках сети"""
    from telegram.error import Conflict
    
    retry_count = 0
    max_retries = 10
    
    while retry_count < max_retries:
        try:
            logger.info(f"🚀 Запуск {name} (попытка {retry_count + 1})...")
            
            app = Application.builder().token(token).build()
            register_func(app)
            
            # Инициализируем и запускаем polling
            await app.initialize()
            await app.updater.start_polling(allowed_updates=Update.ALL_TYPES)
            
            logger.info(f"✅ {name} запущен")
            
            # Держим бота запущенным
            while True:
                await asyncio.sleep(1)
                
        except Conflict as e:
            logger.error(f"❌ {name}: конфликт (другой экземпляр запущен). Ждём 10 сек...")
            retry_count += 1
            await asyncio.sleep(10)
        except (TimedOut, NetworkError) as e:
            retry_count += 1
            logger.warning(f"⚠️ {name}: ошибка сети ({e}), перезапуск через 5 сек...")
            await asyncio.sleep(5)
        except Exception as e:
            logger.error(f"❌ Ошибка {name}: {e}")
            raise


async def run_health_server():
    """Запускает HTTP сервер для health checks"""
    port = int(os.environ.get('PORT', 8080))
    server = HTTPServer(('0.0.0.0', port), HealthHandler)
    logger.info(f"🌐 Health server запущен на порту {port}")
    await asyncio.get_event_loop().run_in_executor(None, server.serve_forever)


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
    
    # Запускаем health server и ботов одновременно
    tasks = [
        run_health_server(),
        run_bot("Corporate Bot", BOTS["corporate"], corporate.register_handlers),
        run_bot("Link Shortener Bot", BOTS["link_shortener"], link_shortener.register_handlers),
        run_bot("Support Bot", BOTS["support"], support.register_handlers),
        run_bot("UID Info Bot", BOTS["uid_info"], uid_info.register_handlers),
    ]
    
    logger.info("🎉 Запуск всех ботов...")
    await asyncio.gather(*tasks)


def main():
    install_dependencies()
    asyncio.run(main_async())


if __name__ == '__main__':
    main()
