from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from telegram_bot.client.handlers.messages import send_welcome
from telegram_bot.client.handlers.callbacks import to_start_router
from storage.database.db_instance import db

on_start_router = Router()
on_start_router.include_router(to_start_router)

@on_start_router.message(Command('start'))
async def start_command(message: Message):
    try:
        db.create_user(message.from_user)

    # todo адекватные логи
    except Exception as e:
        print(message.chat.id)
        print(f"Ошибка при добавлении юзера в БД: {e}")

    await send_welcome(message)


