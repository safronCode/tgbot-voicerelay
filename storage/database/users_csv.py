import os, csv
from storage.config import project_path

# todo сделать кулдаун на сохранение под /stat или подругому обыграть
# Плохо что каждый раз записывает новый файл - если бд большая - это может занять больший ресурс

def save_users_to_csv(users: list):
    # Задаём заголовки в нужном порядке (в каком у тебя лежат поля в таблице)
    headers = [
        "tg_id", "username", "first_name", "last_name",
        "full_name", "email", "is_registered", "channel"
    ]

    with open(os.path.join(project_path, 'storage','database','users.csv'), mode='w', encoding='utf-8', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(headers)       # пишем заголовок
        writer.writerows(users)        # пишем все строки


