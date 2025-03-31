import os
from dotenv import load_dotenv

# Загружаем переменные окружения из .env
load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
DATABASE_NAME = os.getenv("DB_NAME")
PAYMENT_TOKEN = os.getenv("PAYMENT_TOKEN")

# Проверяем, загружен ли токен
if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN не найден! Проверьте файл .env")

if not DATABASE_NAME:
    raise ValueError("DATABASE_NAME не найден! Проверьте файл .env")
