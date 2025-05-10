from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message


from storage.database.db_instance import db
from telegram_bot.client.handlers.callbacks import to_channel_router
from telegram_bot.client.handlers.messages.channel_message import channel_after_chacom

on_channel_router = Router()
on_channel_router.include_router(to_channel_router)

@on_channel_router.message(Command('channel'))
async def start_command(message: Message):
    if db.get_field('tg_id', message.chat.id, 'is_registered') == 1:
        await channel_after_chacom(message)
    else:
        await message.answer('Для выполнения этой команды необходимо быть зарегистрированным \n\n'
                             'Пожалуйста, зарегистрируйся: /reg')
