from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

def select_channel(current_channel: int) -> InlineKeyboardMarkup:
    """
    current_channel:
        0 — don`t disturb
        1 — only tg
        2 — only email
        3 — email + tg
    """

    tg_text = '✈️ TG'
    email_text = '✉️ EMAIL'

    if current_channel == 0:
        tg_text += '\t| (Inactive ❌)'
        email_text += '\t| (Inactive ❌)'
    elif current_channel == 1:
        tg_text += '\t| (Active ✅)'
        email_text += '\t| (Inactive ❌)'
    elif current_channel == 2:
        tg_text += '\t| (Inactive ❌)'
        email_text += '\t| (Active ✅)'
    else:
        tg_text += '\t| (Active ✅)'
        email_text += '\t| (Active ✅)'

    keyboard = InlineKeyboardBuilder()
    keyboard.add(
        InlineKeyboardButton(text=tg_text, callback_data='tg_button'),
        InlineKeyboardButton(text=email_text, callback_data='email_button'),
        InlineKeyboardButton(text='Сохранить', callback_data='save_button')
    )

    keyboard.adjust(1)

    return keyboard.as_markup()

