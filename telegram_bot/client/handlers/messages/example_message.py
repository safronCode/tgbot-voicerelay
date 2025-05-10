from aiogram.types import Message

from storage.database.db_instance import db
from telegram_bot.client.keyboards.inline import register_user, update_user

example_text = (
         '⁺₊✧⋆₊⁺₊✧⋆⁺₊✧✩ ♬ ₊\\.🎧⋆☾⋆⁺₊✧⋆⁺₊✧⁺₊✧₊✧⋆\n'
         'Смотри, как со мной нужно работать:\n\n'
         '1\\. Сначала зарегистрируйся\n'
         '2\\. Выбери каналы, куда мне передать сообщение\n'
         '3\\. Запиши голосовое сообщение\n'
         '4\\.1 Я приму твоё сообщение и расшифрую его в текст\n'
         '4\\.2 Обработаю и формализую твои мысли\n'
         '4\\.3 Отправлю сообщение выбранному человеку\n'
         '━━━━━━━━━━━━━━━━━\n'
         '*Очень важно*\n'
         '🌠 Начинай говорить со слов \\(передай, сообщи, доложи и т\\.д\\.\\)\n'
         '🌠 Обязательно скажи \\*имя и фамилию\\* получателя\n'
         '🌠 Избегай эмоций \\- мои алгоритмы могут словить триггер\n\n'
         'Жми кнопку и мы продолжим')

async def send_example(message: Message):
    if db.get_field('tg_id',message.from_user.id, 'is_registered') == 1:
        keyboard = update_user()
    else:
        keyboard = register_user()

    await message.answer(
        text=example_text,
        parse_mode='MarkdownV2',
        reply_markup=keyboard
    )
