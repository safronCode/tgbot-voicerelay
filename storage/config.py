import os
from datetime import datetime
from dotenv import load_dotenv
from storage.yandex_auth.token_utils import get_or_refresh_token

def find_project_root_by_name(project_name: str) -> str:
    current = os.path.abspath(__file__)
    while True:
        current = os.path.dirname(current)
        if os.path.basename(current) == project_name:
            return current
        if current == os.path.dirname(current):
            raise FileNotFoundError(f"❌ Папка проекта '{project_name}' не найдена.")

STORAGE_PATH = os.path.dirname(__file__)
local_env = os.path.join(STORAGE_PATH, 'local.env')
default_env = os.path.join(STORAGE_PATH, '.env')

if os.path.exists(local_env):
    load_dotenv(local_env)
    print(f"✅ | {datetime.now()} | Загружен <local.env>")
elif os.path.exists(default_env):
    load_dotenv(default_env)
    print(f"✅ | {datetime.now()} | Загружен <.env>")
else:
    print(f"⚠️ | {datetime.now()} | Не найден ни <local.env>, ни <.env>")

try:
    BOT_TOKEN = os.getenv('BOT_TOKEN')
    ADMIN_CHAT_ID = int(os.getenv('ADMIN_CHAT_ID'))

    EMAIL_SENDER = os.getenv('EMAIL_SENDER')
    EMAIL_PASSWORD = os.getenv('EMAIL_PASSWORD')

    FOLDER_ID = os.getenv('FOLDER_ID')
    IAM_TOKEN = get_or_refresh_token()
    YANDEX_GPT_LITE_URI = os.getenv('YANDEX_GPT_LITE_URI')

    project_path = find_project_root_by_name('tgbot-voicerelay')

except Exception as e:
    print(f'❌ Error | {datetime.now()} | Файл окружения не загрузился: {e}')