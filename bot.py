import asyncio
import os
from aiogram import Bot, Dispatcher
from dotenv import load_dotenv
from handlers import router
from admin_handlers import admin_router

# Загружаем токен
load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")

if not BOT_TOKEN:
    raise ValueError("Ошибка: BOT_TOKEN не найден. Проверьте файл .env!")

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# Подключаем обработчики
dp.include_router(router)  # Обычные команды
dp.include_router(admin_router)  # Админские команды

async def main():
    print("Бот запущен...")
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot, skip_updates=False)

if __name__ == "__main__":
    asyncio.run(main())