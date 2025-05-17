from thefuzz import process
import re
from natasha import (
    Segmenter, MorphVocab, NewsEmbedding, NewsMorphTagger,
    NewsSyntaxParser, NewsNERTagger, NamesExtractor, Doc, PER
)
from pymorphy2 import MorphAnalyzer
from storage.database.db_instance import db

def extract_text(stt_text: str) -> dict | None:
    """
    Функция получает на вход расшифровку от STT (Yandex). Проводит небольшую валидацию на первое слово сообщения.
    Обрабатывает имя+фамилию получателя и проверяет есть ли такой зарегистрированный пользователь.
    Отдаёт None если пользователя нет, full_name если есть. А так же остальное сообщение для дальнейшей обработки
    в GPT и отправке
    :param :
    :return dict | None:
    """
    # Слова, с которых должно начинаться голосовое сообщение
    start_words = [
        "передай", "сообщи", "расскажи", "скажи", "донеси", "напомни", "подскажи", "поведай",
        "отправь", "пошли", "намекни", "обозначь", "уведомь", "уведоми", "извести"
        ]

    words = re.split(r'[,; ]+', stt_text)

    # Проверка на структуру "передай ..."
    if words[0].lower() not in start_words:
        #todo logs
        print('Сообщение должно начинаться с <Передай>\n'
                'Используй более четкую структуру изложения')
        return None
    else:
        # Забираем имя и фамилию получателя
        titled_text = " ".join(word.title() for word in words[1:3])

        # Получаем либо None, либо dict из трех пар ключ-значение
        possible_recipient = extract_name(titled_text)

        # Если всё-таки dict (т.е имя фамилию успешно прошли обработку в pymorphy + Natasha)
        if isinstance(possible_recipient, dict):
            # Пытаемся сопоставить полученное с имеющимся в БД
            confirmed_recipient = fuzz_confirm(possible_recipient['nominative'].lower())

            # Если вернулась строка -> успех. Получатель подтвержден
            if isinstance(confirmed_recipient,str):
                return {'full_name_db':confirmed_recipient,
                        'full_name_gt':possible_recipient['genitive'],
                        'message_text': (" ".join(word.title() for word in words[3:])).capitalize()}
            # Если вернулся None -> неудача. Получатель не подтвержден на уровне 82 thefuzz
            else:
                print('не удалось подтвердить имя')
                return None

        # Если всё-таки None (т.е имя фамилию не прошли обработку в pymorphy + Natasha)
        else:
            print("Не удалось обработать имя")
            return None

def extract_name(name: str) -> dict | None:
    """
        Функция получает на вход расшифровку от STT (Yandex). Проводит небольшую валидацию на первое слово сообщения.
        Обрабатывает имя+фамилию получателя и проверяет есть ли такой зарегистрированный пользователь.
        Отдаёт None если пользователя нет, full_name если есть. А так же остальное сообщение для дальнейшей обработки
        в GPT и отправке
        :param name:
        :return  dict | None:
    """

    #
    if name:
        morph = MorphAnalyzer()

        words = name.split()
        smart_cap = [
            word.capitalize() if 'Name' in morph.parse(word)[0].tag or 'Surn' in morph.parse(word)[0].tag else word
            for word in words
        ]

        prepared_name = " ".join(smart_cap)


        # Инициализация компонентов NATASHA
        segmenter = Segmenter()
        morph_vocab = MorphVocab()
        emb = NewsEmbedding()
        morph_tagger = NewsMorphTagger(emb)
        syntax_parser = NewsSyntaxParser(emb)
        ner_tagger = NewsNERTagger(emb)
        names_extractor = NamesExtractor(morph_vocab)

        #Обработка текста
        doc = Doc(prepared_name)
        doc.segment(segmenter)
        doc.tag_morph(morph_tagger)
        doc.parse_syntax(syntax_parser)
        doc.tag_ner(ner_tagger)

        # Нормализация и извлечение фактов
        for span in doc.spans:
            span.normalize(morph_vocab)
            if span.type == PER:
                span.extract_fact(names_extractor)
                if span.fact:
                    parts = span.normal.split()
                    inflected_parts = []
                    for part in parts:
                        parsed = morph.parse(part)[0]
                        inflected = parsed.inflect({'gent'})
                        if inflected:
                            inflected_parts.append(inflected.word.capitalize())
                        else:
                            inflected_parts.append(part.capitalize())

                    recipient_gent = ' '.join(inflected_parts)

                    return {
                        'original': span.text,
                        'nominative': span.normal,
                        'genitive': recipient_gent
                    }

        print("Не найдено имён")
        return None

    else:
        print("Natasha: входной текст отсутствует.")
        return None


def fuzz_confirm(possible_recipient: str) -> str | None:
    """
    Функция сравнивает по метрике расстояния Левенштейна и находит максимально похожее среди зарегистрированных
    пользователей. Если точность недостаточна (<82) функция возвращает None

    :param possible_recipient:
    :return str | None:
    """
    all_recipients = db.get_fields('full_name') + ['елизавета манник']

    # Рассматриваем варианты: Фамилия + Имя / Имя + Фамилия
    possible_recipient = [possible_recipient] + [(' '.join(possible_recipient.split()[::-1]))]

    # Выполняем два сравнение
    confirm_recipient_1 = process.extractOne(possible_recipient[0], all_recipients)
    confirm_recipient_2 = process.extractOne(possible_recipient[1], all_recipients)

    # Находим наилучшее совпадение
    best_match = max(confirm_recipient_1[1], confirm_recipient_2[1])
    if best_match >= 82:
        return confirm_recipient_1[0]
    else:
        return None








text = 'передаЙ Артёмам Яковиным что мы сейчас пойдем играть в Триалсы вместе с Артёмом Яковиным'
#print(extract_name('Елизавете Камень'))

print('!',extract_text(text))
