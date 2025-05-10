import os

from storage.config import ADMIN_CHAT_ID, project_path
from storage.database.db_instance import db

from aiogram import Router, Bot
from aiogram.types import Message, FSInputFile
from aiogram.filters import Command

on_stat_router = Router()

@on_stat_router.message(Command('stat'))
async def on_stat(message: Message, bot: Bot):
    if (message.chat.id == ADMIN_CHAT_ID) and (message.message_thread_id is None):

        #todo не самое лучше решение - говнокод
        db.get_all_users()

        await bot.send_document(
            chat_id=ADMIN_CHAT_ID,
            message_thread_id=None,
            document=FSInputFile(os.path.join(project_path, 'storage','database','users.csv')),
            caption="📎 Статистики <SayAndDo>\n\n"
                    f"Всего использовало: {db.get_count_fields()-1} юзер(а/ов)\n"
                    f"Зарегистрировано: {db.get_count_fields('is_registered', 1)} юзер(а/ов)"
        )
