from aiogram import Router, F, types
from telegram_bot.client.handlers.messages import send_example

to_start_router = Router()

@to_start_router.callback_query(F.data == 'handshake')
async def welcome_message(callback_query: types.CallbackQuery):
    await callback_query.message.delete()
    await send_example(callback_query.message)
    await callback_query.answer()