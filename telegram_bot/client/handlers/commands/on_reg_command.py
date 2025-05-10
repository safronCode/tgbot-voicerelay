import re
from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message
from aiogram.fsm.context import FSMContext

from storage.database.db_instance import db
from telegram_bot.client.handlers.messages import channel_after_regcom
from telegram_bot.client.states.reg_state import RegState

on_reg_router = Router()

@on_reg_router.message(Command("reg"))
async def reg_command(message: Message, state: FSMContext):
    #todo адекватные логи
    try:
        db.create_user(message.from_user)
    except Exception as e:
        print(f"Ошибка при добавлении юзера в БД: {e}")

    await message.answer(
        text='Введите ваше *имя* и *фамилию*\n\n'
             '━━━━━━━━━━━━━━━━━\n'
             '💡_Например: \\"Иван Иванов\\"_',
        parse_mode='MarkdownV2'
    )
    await state.set_state(RegState.name)

# Имя и фамилия
@on_reg_router.message(RegState.name)
async def process_name(message: Message, state: FSMContext):
    full_name = message.text.strip()

    # Валидация: уникальность пользователя
    if db.fullname_occupied(full_name) == True:
        if db.get_id_by_name(full_name) == message.from_user.id:
            print('Кайфушки')
            pass
        else:
            return await message.answer("❗ Мы уже регистрировали такого пользователя :с\n"
                                        "\tВведите другие данные, например псевдоним")

    # Валидация: только кириллица, две части (имя и фамилия)
    if not re.fullmatch(r"[А-Яа-яЁё]{2,}( [А-Яа-яЁё]{2,})", full_name):
        return await message.answer("❗ Пожалуйста, введите имя и фамилию на русском (пример: Иван Иванов).")


    first_name, last_name = full_name.split()
    db.update_field(message.from_user.id,'first_name', first_name.lower())
    db.update_field(message.from_user.id,'last_name', last_name.lower())
    db.update_field(message.from_user.id, 'full_name',full_name.lower())

    await message.answer(
        text='Введите ваш *email*\n\n'
             '━━━━━━━━━━━━━━━━━\n'
             '💡_Например: \\"example@mymail\\.com\\"_',
        parse_mode='MarkdownV2'
    )
    await state.set_state(RegState.email)

# Email
@on_reg_router.message(RegState.email)
async def process_email(message: Message, state: FSMContext):
    email = message.text.strip()

    # 🔍 Валидация email
    if not re.fullmatch(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b", email):
        await message.answer("❗ Введите корректный email (например: example@mail.ru)")
        return

    try:
        db.update_field(message.from_user.id, 'email', email)
        db.update_field(message.from_user.id, 'is_registered', 1)
    except Exception as e:
        print(f"Не удалось занести завершить регистрацию юзера\n{e}")

    await channel_after_regcom(message)
    await state.clear()

