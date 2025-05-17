import os
import asyncio

from aiogram import Router, Bot, F
from aiogram.types import Message
from aiogram.enums import ContentType, ChatAction

from storage.database.db_instance import db
from voice_processing.name_extractor import extract_text
from voice_processing.text2speech import recognize_speech_ogg, error_map_stt
from voice_processing.voice_pipeline import build_relay_prompt, parse_summary_response, escape_markdown
from voice_processing.yandexgpt import relay_gpt, error_map_gpt
from datetime import datetime
from telegram_bot.client.handlers.email.email_sender import email_sender

to_voice_router = Router()

#todo проработать нейминг в голосовых модулях
@to_voice_router.message(F.content_type == ContentType.VOICE)
async def handle_voice(message: Message, bot: Bot):
    # Проверяем зарегистрирован ли юзер
    user_id = message.from_user.id

    if db.get_field('tg_id', user_id, 'is_registered') != 1:
        return await message.answer(
                        text='Для начала необходимо быть зарегистрированным \n\n'
                             'Пожалуйста, зарегистрируйся: /reg')

    # Пути к файлам + временное хранение аудио
    BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", ".."))
    #todo чекнуть как ведет себя если нет storage/voice_ogg
    STORAGE_PATH = os.path.join(BASE_DIR, "storage", "voice_ogg")
    os.makedirs(STORAGE_PATH, exist_ok=True)
    OGG_PATH = os.path.join(STORAGE_PATH, f"voice_{message.chat.id}.ogg")

    file = await bot.get_file(message.voice.file_id)
    await bot.download_file(file.file_path, OGG_PATH)

    await bot.send_chat_action(message.chat.id, ChatAction.TYPING)

    try:
        await asyncio.sleep(0.1)

        # Обращения к моделям + парсинг конечного ответа
        #todo выпил
        text_from_voice = recognize_speech_ogg(OGG_PATH)

        stt_text = recognize_speech_ogg(OGG_PATH)

        if stt_text in error_map_stt:
            return await message.reply(text=error_map_stt[stt_text])

        text_pile = extract_text(stt_text)

        if text_pile is None:
            return await message.reply(text='Произошла ошибка при обработки голосового. Попробуйте позже')

        text_from_gpt = relay_gpt(build_relay_prompt(text_pile['message_text'])).capitalize()
        topic_message = relay_gpt(f'О чем говориться в тексте, твой ответ 2-3 слова: {text_from_gpt}')
        if text_from_gpt in error_map_gpt:
            return await message.reply(error_map_gpt[text_from_voice])

        #answer = parse_summary_response(text_from_gpt)

        #if isinstance(answer, dict):

        # Пример использования:
        email_template = {
            "subject": topic_message.capitalize(),
            "message": text_from_gpt,
            "sender": f"telegram: @{message.from_user.username} ({(db.get_field('tg_id', message.from_user.id,'full_name')).title()})",
            "date": datetime.now().strftime("%d.%m.%Y %H:%M")
        }

        recipient_id = db.get_id_by_name(text_pile['full_name_db'])

        # if recipient_id is None:
        #     await message.reply(
        #                 text=f"У нас в базе отсутствует: {answer['recipient']}\n\n"
        #                       "Подскажите этому пользователю зарегистрироваться! :)")

        recipient_channel = db.get_field('tg_id', recipient_id, 'channel')

        if recipient_channel == 0:
            recipient_username = db.get_field('tg_id',recipient_id,'username')
            return await message.reply(
                    text=f"Сообщение не доставлено... ❌\n"
                         f"@{recipient_username} не готов принять сообщения")

        elif recipient_channel == 1:
            sender_username = message.from_user.username
            recipient_username = db.get_field('tg_id', recipient_id, 'username')
            await message.reply(
                text=f"Сообщение отправлено на tg и email {text_pile['full_name_gt']} (@{recipient_username}) ✅\n\n"
                     "Вот что увидит пользователь:\n"
                     "━━━━━━━━━━━━━━━━━\n"
                     "📩 Получено новое сообщение\n"
                     f"👤 от @{message.from_user.username} ({(db.get_field('tg_id', message.from_user.id,'full_name')).title()})\n\n\n"
                     f"{text_from_gpt}")
            await message.bot.send_message(
                chat_id=recipient_id,
                text="📩 Получено новое сообщение\n"
                     f"👤 от @{message.from_user.username} ({(db.get_field('tg_id', message.from_user.id, 'full_name')).title()})\n\n\n"
                     f"{text_from_gpt}")


        elif recipient_channel == 2:
            recipient_email = db.get_field('tg_id', recipient_id, 'email')
            recipient_username = db.get_field('tg_id', recipient_id, 'username')

            await message.reply(
                text=f"Сообщение отправлено на tg и email {text_pile['full_name_gt']} (@{recipient_username}) ✅\n\n"
                     "Вот что увидит пользователь:\n"
                     "━━━━━━━━━━━━━━━━━\n"
                     "📩 Получено новое сообщение\n"
                     f"👤 от @{message.from_user.username} ({(db.get_field('tg_id', message.from_user.id,'full_name')).title()})\n\n\n"
                     f"{text_from_gpt}")
            email_sender(email_template, recipient_email)

        elif recipient_channel == 3:
            sender_username = message.from_user.username
            recipient_username = db.get_field('tg_id', recipient_id, 'username')
            recipient_email = db.get_field('tg_id', recipient_id, 'email')
            print({escape_markdown(text_from_gpt)})
            await message.reply(
                text=f"Сообщение отправлено на tg и email {text_pile['full_name_gt']} (@{recipient_username}) ✅\n\n"
                      "Вот что увидит пользователь:\n"
                      "━━━━━━━━━━━━━━━━━\n"
                      "📩 Получено новое сообщение\n"
                     f"👤 от @{message.from_user.username} ({(db.get_field('tg_id', message.from_user.id,'full_name')).title()})\n\n\n"
                     f"{text_from_gpt}")

            await message.bot.send_message(
                chat_id=recipient_id,
                text="📩 Получено новое сообщение\n"
                    f"👤 от @{message.from_user.username} ({(db.get_field('tg_id', message.from_user.id,'full_name')).title()})\n\n\n"
                    f"{text_from_gpt}")

            email_sender(email_template, recipient_email)

    except PermissionError as e:
        await message.reply(
            text="❌ Ошибка доступа к файлу. Попробуй ещё раз.")
        print(f"PermissionError: {e}")

    finally:
        #Не храним голосовые сообщения юзеров
        if os.path.exists(OGG_PATH):
            os.remove(OGG_PATH)
