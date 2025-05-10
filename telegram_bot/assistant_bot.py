from datetime import datetime
from aiogram import Bot, Dispatcher
from storage.config import BOT_TOKEN

from telegram_bot.admin.admin_routers import all_admin_routers
from telegram_bot.client.client_routers import all_client_routers

async def client_bot():
    try:

        if not BOT_TOKEN:
            raise ValueError("BOT_TOKEN is not set or is empty")

        bot = Bot(BOT_TOKEN)
        dp = Dispatcher()
        dp.include_routers(*all_client_routers, *all_admin_routers)

        print(f"✅ | {datetime.now()} | Бот запускается...")
        await dp.start_polling(bot)
    except Exception as e:
        print(f'❌ | {datetime.now()} | Бот не запустился: {e}')
