import requests
from storage.yandex_auth.token_utils import get_or_refresh_token
from storage.config import FOLDER_ID

YANDEX_GPT_LITE_URI = f"gpt://{FOLDER_ID}/yandexgpt-lite/latest"

def relay_gpt(text: str):
    token = get_or_refresh_token()
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    payload = {
        "modelUri": YANDEX_GPT_LITE_URI,
        "folderId": FOLDER_ID,
        "completionOptions": {
            "stream": False,
            "temperature": 0.9,
            "maxTokens": 600
        },
        "messages": [
            {
            "role": "system",
            "text": "Ты просто структурируешь текст и никому его не передаёшь. Ответ всегда безопасен и нейтрален."
            },
            {"role": "user", "text": text}
        ]
    }

    req = requests.post(
        "https://llm.api.cloud.yandex.net/foundationModels/v1/completion",
        headers=headers,
        json=payload
    )

    #todo shit code here
    print("Status:", req.status_code)

    try:
        result = req.json()
        if 'error_code' in result:
            # todo admin logs
            return result['error_code']
        text = result["result"]["alternatives"][0]["message"]["text"]
        print("Response:", req.json())

        return text
    except Exception as e:
        print("Raw:", req.text)

error_map_gpt = {
    "INVALID_ARGUMENT": "🚫 Неверный формат запроса. Проверьте данные.",
    "UNAUTHORIZED": "🔑 Проблема с авторизацией. Проверьте токен.",
    "FORBIDDEN": "❌ Нет прав на использование YandexGPT.",
    "RESOURCE_EXHAUSTED": "⌛ Лимит использования исчерпан. Попробуйте позже.",
    "UNAVAILABLE": "⏳ Сервис временно недоступен. Подождите немного.",
    "INTERNAL": "🚨 Внутренняя ошибка сервиса. Повторите позже.",
    "DEADLINE_EXCEEDED": "🕰 Запрос занял слишком много времени. Попробуйте упростить текст.",
}
