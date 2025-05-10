import os
import asyncio

from aiogram import Router, Bot, F
from aiogram.types import Message
from aiogram.enums import ContentType, ChatAction

from storage.database.db_instance import db
from yandex_cloud.text2speech import recognize_speech_ogg, error_map_stt
from yandex_cloud.voice_pipeline import build_relay_prompt, parse_summary_response
from yandex_cloud.yandexgpt import relay_gpt, error_map_gpt
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
    STORAGE_PATH = os.path.join(BASE_DIR, "storage", "voice_ogg")
    os.makedirs(STORAGE_PATH, exist_ok=True)
    OGG_PATH = os.path.join(STORAGE_PATH, f"voice_{message.chat.id}.ogg")

    file = await bot.get_file(message.voice.file_id)
    await bot.download_file(file.file_path, OGG_PATH)

    await bot.send_chat_action(message.chat.id, ChatAction.TYPING)

    try:
        await asyncio.sleep(0.1)

        # Обращения к моделям + парсинг конечного ответа
        text_from_voice = recognize_speech_ogg(OGG_PATH)
        if text_from_voice in error_map_stt:
            return await message.reply(error_map_stt[text_from_voice])

        prompt_to_gpt = build_relay_prompt(text_from_voice)
        text_from_gpt = relay_gpt(prompt_to_gpt)
        if text_from_gpt in error_map_gpt:
            return await message.reply(error_map_gpt[text_from_voice])
        answer = parse_summary_response(text_from_gpt)

        print(answer)
        # Пример использования:
        email_template = {
            "subject": answer['subject'].replace("/", ""),
            "message": answer['message'].replace("/", ""),
            "sender": f"telegram: @{message.from_user.username} ({db.get_field('tg_id', message.from_user.id,'full_name')}",
            "date": datetime.now().strftime("%d.%m.%Y %H:%M")
        }

        if answer['recipient'] == 'неизвестно':
            return await message.reply(
                            text="*Я не услышал кому это нужно передать \\:с*\n\n"
                                 "_Пожалуйста, скажите имя и фамилию получателя в голосовом сообщении_",
                            parse_mode='MarkdownV2')
        else:
            recipient_id = db.get_id_by_name(answer['recipient'])

            if recipient_id is None:
                await message.reply(
                            text=f"У нас в базе отсутствует: {answer['recipient']}\n\n"
                                  "Подскажите этому пользователю зарегистрироваться! :)")

            else:
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
                        text=f"Сообщение отправлено на tg @{recipient_username} ✅\n\n"
                              "Вот что увидит пользователь:\n"
                              "━━━━━━━━━━━━━━━━━\n"
                              "_📩 Получено новое сообщение_\n"
                             f"_👤 от @{sender_username} \\({db.get_field('tg_id', message.from_user.id,'full_name')}\\)_\n"
                             f"_*{answer['subject']}*_\n"
                             f"_{answer['message']}_",
                        parse_mode='MarkdownV2')
                    await message.bot.send_message(
                        chat_id=recipient_id,
                        text="📩 Получено новое сообщение\n"
                            f"👤 @{sender_username} \\({db.get_field('tg_id', message.from_user.id,'full_name')}\\)\n\n\n"
                            f"*{answer['subject']}*\n"
                            f"{answer['message']}",
                        parse_mode='MarkdownV2')


                elif recipient_channel == 2:
                    recipient_email = db.get_field('tg_id', recipient_id, 'email')
                    recipient_username = db.get_field('tg_id', recipient_id, 'username')

                    await message.reply(

                        text=f"Сообщение отправлено на email @{recipient_username} ✅\n\n"
                             "Вот что увидит пользователь:\n"
                             "━━━━━━━━━━━━━━━━━\n"
                             "_📩 Получено новое сообщение_\n"
                             f"_👤 от @{message.from_user.username} \\({db.get_field('tg_id', message.from_user.id,'full_name')}\\)_\n"
                             f"_*{answer['subject']}*_\n"
                             f"_{answer['message']}_",
                        parse_mode='MarkdownV2')
                    email_sender(email_template, recipient_email)

                elif recipient_channel == 3:
                    sender_username = message.from_user.username
                    recipient_username = db.get_field('tg_id', recipient_id, 'username')
                    recipient_email = db.get_field('tg_id', recipient_id, 'email')
                    await message.reply(
                        text=f"Сообщение отправлено на tg и email @{recipient_username} ✅\n\n"
                             "Вот что увидит пользователь:\n"
                             "━━━━━━━━━━━━━━━━━\n"
                             "_📩 Получено новое сообщение_\n"
                             f"_👤 от @{message.from_user.username} \\({db.get_field('tg_id', message.from_user.id,'full_name')}\\)_\n"
                             f"_*{answer['subject']}*_\n"
                             f"_{answer['message']}_",
                        parse_mode='MarkdownV2')

                    await message.bot.send_message(chat_id=recipient_id,
                                                   text="📩 Получено новое сообщение\n"
                                                        f"👤 от @{message.from_user.username} \\({db.get_field('tg_id', message.from_user.id,'full_name')}\\)\n\n\n"
                                                        f"*{answer['subject']}*\n"
                                                        f"{answer['message']}",
                                                   parse_mode='MarkdownV2')

                    email_sender(email_template, recipient_email)

    except PermissionError as e:
        await message.reply(
            text="❌ Ошибка доступа к файлу. Попробуй ещё раз.")
        print(f"PermissionError: {e}")
    finally:
        #Не храним голосовые сообщения юзеров
        if os.path.exists(OGG_PATH):
            os.remove(OGG_PATH)
