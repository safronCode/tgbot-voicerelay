from aiogram.types import Message
from telegram_bot.client.keyboards.inline import handshake

async def send_welcome(message: Message):
    await message.answer(
        f' Привет, *{message.from_user.first_name}*\\!\nЯ голосовой помощник *\\< Say \\& Do \\>* \n\n'
        'Жми на кнопку и я расскажу о своих возможностях',
        parse_mode="MarkdownV2",
        reply_markup = handshake()
    )