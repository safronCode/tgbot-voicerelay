import time
from aiogram import Router, F, types
from aiogram.fsm.context import FSMContext

from storage.database.db_instance import db
from telegram_bot.client.keyboards.inline import select_channel

to_channel_router = Router()

@to_channel_router.callback_query(F.data.in_(["tg_button", "email_button"]))
async def change_channel(callback: types.CallbackQuery, state: FSMContext):
    user_data = await state.get_data()
    current_channel = user_data.get('channel_mode', 0)

    if callback.data == 'tg_button':
        if current_channel in (0, 2):
            current_channel += 1
        else:
            current_channel -= 1
    elif callback.data == 'email_button':
        if current_channel in (0, 1):
            current_channel += 2
        else:
            current_channel -= 2

    await state.update_data(channel_mode=current_channel)

    await callback.message.edit_reply_markup(
        reply_markup=select_channel(current_channel)
    )
    await callback.answer()

@to_channel_router.callback_query(F.data =='save_button')
async def save_channel(callback: types.CallbackQuery, state: FSMContext):
    user_data = await state.get_data()

    # Получаем время последнего сохранения
    last_save_time = user_data.get('last_save_time', 0)
    current_time = time.time()

    # Проверка кулдауна
    if current_time - last_save_time < 10:
        await callback.answer("⏳ Подождите немного перед следующим сохранением", show_alert=True)
        return

    # Сохраняем новый канал в БД
    channel_mode = user_data.get('channel_mode', 0)
    db.update_field(callback.from_user.id, 'channel', channel_mode)

    # Обновляем время последнего сохранения
    await state.update_data(last_save_time=current_time)
    await callback.answer(
        text="✅ Ваш выбор успешно сохранён!\n\n"
             "Можете отправлять голосовое\nЯ буду ждать :)",
        show_alert=True)
