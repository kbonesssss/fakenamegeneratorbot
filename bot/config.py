"""
Конфигурационный файл бота
"""
import os
import logging
from dotenv import load_dotenv

logger = logging.getLogger(__name__)

load_dotenv()

# Получаем токен бота из переменной окружения
BOT_TOKEN = os.getenv("BOT_TOKEN", "your_token_here")

# Список ID администраторов
ADMIN_IDS = [
    123456789,  # Замените на ваш Telegram ID
]

# Настройки базы данных
DATABASE_URL = "sqlite:///bot.db"

# Настройки логирования
LOG_LEVEL = "INFO"
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
LOG_FILE = "logs/bot.log"

logger.info(f"Loading admin IDs from env: {ADMIN_IDS}")

try:
    # Устанавливаем ID администратора напрямую
    ADMIN_IDS = [178580829]  # Ваш ID
    logger.info(f"Using hardcoded admin IDs: {ADMIN_IDS}")
except Exception as e:
    logger.error(f"Error setting admin IDs: {e}")
    ADMIN_IDS = []

CHANNEL_ID = os.getenv('CHANNEL_ID')
RANDOM_USER_API = os.getenv('RANDOM_USER_API', 'https://randomuser.me/api/') 