from aiogram.types import Message

from storage.database.db_instance import db
from telegram_bot.client.keyboards.inline import select_channel

# Пайп лайн после команды /channel
async def channel_after_chacom(message: Message):
    current_channel = db.get_field('tg_id', message.chat.id, 'channel')
    await message.answer("Назначь каналы куда передавать вам сообщения от других пользователей?",
                         reply_markup=select_channel(current_channel))

# Пайп лайн после команды /reg
async def channel_after_regcom(message: Message):
    current_channel = db.get_field('tg_id', message.chat.id, 'channel')
    await message.answer(
                    text='✅ Регистрация завершена\n\n'
                         'Назначь каналы куда передавать вам сообщения от других пользователей?',
                    reply_markup=select_channel(current_channel))


