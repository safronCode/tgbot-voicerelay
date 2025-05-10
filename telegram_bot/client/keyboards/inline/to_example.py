from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

def register_user() -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardBuilder()
    keyboard.add(InlineKeyboardButton(
        text='🔗 Регистрация 🧾',
        callback_data='register'),
    )
    return keyboard.as_markup()

def update_user() -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardBuilder()
    keyboard.add(InlineKeyboardButton(
        text='🔗 Обновить данные 🔄',
        callback_data='update'),
    )
    return keyboard.as_markup()