from aiogram import Router, F, types
from aiogram.fsm.context import FSMContext

from telegram_bot.client.handlers.commands.on_reg_command import reg_command


to_reg_router = Router()

@to_reg_router.callback_query(F.data.in_(['register', 'update']))
async def reg_message(callback_query: types.CallbackQuery, state: FSMContext):
    await callback_query.message.delete()
    await reg_command(callback_query.message, state)
    await callback_query.answer()
