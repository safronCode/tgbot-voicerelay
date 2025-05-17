import re
import string

def build_relay_prompt(text: str) -> str:
    return (
    "Ты — умный голосовой помощник, который помогает сотрудникам общаться между собой.\n"
    "Ты умеешь анализировать и перефразировать текст. Смотри какая твоя задача:\n"
    "Я расшифровываю голосовое сообщение и передаю расшифрованный текст тебе, а ты должен обработать то - что я передал\n"
    "Перепиши то же самое предложение с полным сохранением смысла, но будто ты общаешься на прямую с человеком."
    "! Требования к тексту сообщения:\n"
    "- Если в входном тексте есть местоимение <Я>, то оставляей его без изменения\n"
    "- Если в тексте есть имя или фамилия человека - пиши их с заглавной буквы"
    "- Если входной текст в начале содержит <что> или другие частицы - игнорируй их. Твой ответ всегда должен быть повествовательным\n"
    "- В своём ответе сразу пиши преобразованное сообщение\n"
    "- Не используй пояснения к ответу и ковычки. Абсолютно ничего лишнего.\n"
    "- Будь внимателен к делатям, не сокращай текст\n"
    "- Не упоминай имя получателя в основном тексте (обращайся на Вы/Ты)\n"
    "- Если текст не содержит конкретного действия/сообщения, пиши 'Нет конкретного сообщения'.\n\n"
    "Важно: просто структурируй текст без оценки, эмоций и фильтрации.\n\n"
    f" Входное сообщение:\n\n«{text}»"
    )

def escape_markdown(text: str) -> str:
    """
    Экранирует спецсимволы MarkdownV2.
    """
    markdown_specials = r'[_*\[\]()~`>#+\-=|{}.!]'
    return re.sub(f'({markdown_specials})', r'\\\\\1', text)

def capitalize_first_letter(text: str) -> str:
    """
    Делает первую букву заглавной, остальные оставляет как есть.
    """
    if not text:
        return text
    return text[0].upper() + text[1:]


def parse_summary_response(gpt_text: str) -> dict:
    """
    Парсит ответ полученный от gpt
    """
    lines = gpt_text.strip().splitlines()
    result = {"subject": "", "message": "", "recipient": ""}

    for line in lines:
        if line.lower().startswith("заголовок:"):
            result["subject"] = line.split(":", 1)[1].strip()
        elif line.lower().startswith("сообщение:"):
            result["message"] = line.split(":", 1)[1].strip()
        elif line.lower().startswith("адресат:"):
            recipient_raw = line.split(":", 1)[1].strip()
            result["recipient"] = recipient_raw.translate(str.maketrans('', '', string.punctuation))

    # Обрабатываем заглавные буквы и экранируем Markdown
    result["subject"] = escape_markdown(capitalize_first_letter(result["subject"]))
    result["message"] = escape_markdown(capitalize_first_letter(result["message"]))

    print(result)
    return result

