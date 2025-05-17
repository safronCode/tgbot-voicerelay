import requests
from storage.config import IAM_TOKEN, FOLDER_ID

def recognize_speech_ogg(filename: str) -> str:
    print(IAM_TOKEN, FOLDER_ID)
    with open(filename, 'rb') as f:
        audio_data = f.read()
    headers = {
        "Authorization": f"Bearer {IAM_TOKEN}",
    }
    params = {
        "lang": "ru-RU",
        "folderId": FOLDER_ID,
        "format": "oggopus",
        "sampleRateHertz": 48000,
    }
    response = requests.post(
        "https://stt.api.cloud.yandex.net/speech/v1/stt:recognize",
        params=params,
        headers=headers,
        data=audio_data
    )
    result = response.json()
    print(result)
    if 'error_code' in result:
        #todo admin logs
        return result['error_code']
    return result.get('result', "Не удалось распознать")

error_map_stt = {
            "BAD_REQUEST": "❌ Неверный запрос.\n Возможно, аудио слишком длинное или повреждено.\n\nАудио должно быть не длиннее 30 секунд",
            "UNAUTHORIZED": "❗ Пожалуйста, попробуйте позже\nСообщите о проблеме : @ogPow3r",
            "FORBIDDEN": "❗ Пожалуйста, попробуйте позже\nСообщите о проблеме : @ogPow3r",
            "TOO_MANY_REQUESTS": "⏳ Слишком много запросов. Попробуйте через минуту.",
            "INTERNAL_SERVER_ERROR": "🚨 Ошибка на сервере Яндекса. Попробуйте позже.",
            "SERVICE_UNAVAILABLE": "⏳ Сервис временно недоступен. Подождите немного.",
            "UNSUPPORTED_AUDIO_FORMAT": "❗ Пожалуйста, попробуйте позже\nСообщите о проблеме : @ogPow3r",
            "AUDIO_TOO_LARGE": "❗ Пожалуйста, попробуйте позже\nСообщите о проблеме : @ogPow3r",
            "AUDIO_DECODING_ERROR": "❗ Ошибка декодирования аудио. Попробуйте перезаписать голосовое сообщение.",
            "BAD_AUDIO_QUALITY": "❗ Плохое качество записи. Пожалуйста, перезапишите сообщение."
        }
