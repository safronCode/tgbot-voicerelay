import os
from datetime import datetime
import time
import json, jwt

import yandexcloud
from yandex.cloud.iam.v1.iam_token_service_pb2 import CreateIamTokenRequest
from yandex.cloud.iam.v1.iam_token_service_pb2_grpc import IamTokenServiceStub

# Пути к ключу и кэшу токена
BASE_DIR = os.path.dirname(__file__)
CACHE_PATH = os.path.join(BASE_DIR, 'iam_token_cache.json')

if os.path.exists(os.path.join(BASE_DIR, 'authorized_key_local.json')):
    KEY_PATH = os.path.join(BASE_DIR, 'authorized_key_local.json')
    print(f"✅ | {datetime.now()} | Загружен <authorized_key_local.json>")
elif os.path.exists(os.path.join(BASE_DIR, 'authorized_key.json')):
    KEY_PATH = os.path.join(BASE_DIR, 'authorized_key.json')
    print(f"✅ | {datetime.now()} | Загружен <authorized_key.json>")
else:
    print(f"⚠️ | {datetime.now()} | Не найден ни <authorized_key_local.json>, ни <authorized_key.json>")

try:
    with open(KEY_PATH, 'r') as f:
        key_data = json.load(f)
        PRIVATE_KEY = key_data['private_key']
        KEY_ID = key_data['id']
        SERVICE_ACCOUNT_ID = key_data['service_account_id']
except Exception as e:
    print(f"❌ | {datetime.now()} | Ключи токена не обработан: {e}")

def create_jwt() -> str:
    now = int(time.time())
    payload = {
        'aud': 'https://iam.api.cloud.yandex.net/iam/v1/tokens',
        'iss': SERVICE_ACCOUNT_ID,
        'iat': now,
        'exp': now + 3600
    }
    return jwt.encode(
        payload,
        PRIVATE_KEY,
        algorithm='PS256',
        headers={'kid': KEY_ID}
    )

def create_iam_token() -> dict:
    jwt_token = create_jwt()
    sdk = yandexcloud.SDK(service_account_key={
        "id": KEY_ID,
        "service_account_id": SERVICE_ACCOUNT_ID,
        "private_key": PRIVATE_KEY
    })
    iam_service = sdk.client(IamTokenServiceStub)
    iam_token = iam_service.Create(CreateIamTokenRequest(jwt=jwt_token))
    return {
        "token": iam_token.iam_token,
        "expires_at": int(time.time()) + 3600
    }

def get_or_refresh_token() -> str:
    if os.path.exists(CACHE_PATH):
        try:
            with open(CACHE_PATH, 'r') as file:
                cache = json.load(file)
                if cache.get('expires_at', 0) > int(time.time()) + 60:
                    return cache['token']
        except Exception:
            pass  # Повреждённый кэш игнорируем

    new_token_data = create_iam_token()
    with open(CACHE_PATH, 'w') as file:
        json.dump(new_token_data, file)
    return new_token_data['token']

