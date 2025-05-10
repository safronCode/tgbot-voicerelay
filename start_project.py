import asyncio
import datetime

from storage.database.db_instance import db
from telegram_bot.assistant_bot import client_bot

if __name__ == '__main__':
    db.init_db()
    try:
        asyncio.run(client_bot())
    except Exception as e:
        print(f'❌ Error | {datetime.now()} | Бот не запустился: {e}')
