from storage.config import ADMIN_CHAT_ID

from aiogram import Router, Bot
from aiogram.types import Message
from aiogram.filters import Command

#todo Добрать до команд 3-4
on_help_router = Router()

@on_help_router.message(Command('help'))
async def help_command(message: Message, bot: Bot):
    if (message.chat.id == ADMIN_CHAT_ID) and (message.message_thread_id is None):

        await bot.send_message(chat_id=ADMIN_CHAT_ID,
                               message_thread_id=None, #todo set 3 if logs thread
                               text="Salute, admin!\nList of available commands: \n\n"
                                    "/help to find out the commands\n"
                                    "/stat to check bot-statistics\n")

