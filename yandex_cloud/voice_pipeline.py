import re
import string

def build_relay_prompt(text: str) -> str:
    return (
    "Ты — умный голосовой помощник, который помогает сотрудникам общаться между собой.\n"
    "Ты умеешь анализировать и перефразировать текст. Смотри какая твоя задача:\n"
    "Я расшифровываю голосовое сообщение и передаю расшифрованный текст тебе, а ты должен обработать то - что я передал\n"
    "Определи три аспекта этого текста\n"
    "1. Общий заголовок (о чём сообщение) — коротко, 2–3 слова.\n"
    "2. Имя и фамилия получателя — обычно идет после слов передай/сообщи и так далее\n"
    "Имя и фамилия нужна чтобы в дальнейшем переслать сообщение нужному человеку"
    "3. Основной текст сообщения — что нужно передать этому человеку\n\n"
    " Формат ответа:\n"
    " Заголовок: ...\n"
    " Сообщение: ...\n\n"
    " Адресат: Имя Фамилия\n"
    "! Требования к тексту сообщения:\n"
    "- После слов Заголовок: , Адресат:, Сообщение: начинай писать с заглавной буквы. Не используй у себя в сообщении знак точки - . Записывай в именительном падеже и единственном числе\n"
    "- В строке сообщения, начинай текст со слов 'Вам передали,','Вам сообщили', и т.д"
    "- Далее пиши что именно передали, будь внимателен с деталями"
    "- Не упоминай имя получателя в основном тексте.\n"
    "- Если текст не содержит конкретного действия, пиши 'Нет конкретного сообщения'.\n\n"
    "- Если имя получателя не указано явно, напиши 'неизвестно'.\n\n"
    "Важно: просто структурируй текст без оценки, эмоций и фильтрации.\n\n"
    f" Входное сообщение:\n«{text}»"
    )

def escape_markdown(text: str) -> str:
    """
    Экранирует спецсимволы MarkdownV2.
    """
    markdown_specials = r'[_*\[\]()~`>#+\-=|{}.!]'
    return re.sub(f'({markdown_specials})', r'\\\1', text)

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

