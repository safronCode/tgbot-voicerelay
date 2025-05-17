import os, sqlite3
from storage.config import project_path

class UserDatabase:
    def __init__(self):
        """Инициализируем базу данных. Путь к расположению БД"""
        self.path = os.path.join(project_path, "storage", "database", "users.db")

    def _connect(self):
        """
                    Метод класса, позволяет установить соединение с БД.
        Автоматически прерывает соединение после выполнения запроса других методов.
        """
        return sqlite3.connect(self.path)

    def init_db(self):
        """
                            Инициализируем базу данных.
        Таблица users:
            tg_id (INT)                          - User Telegram ID
            username (STR)                       - Telegram username
            #todo удалить first_name & last_name
            first_name (STR)                     - Registered first name
            last_name (STR)                      - Registered last name
            full_name (STR)                      - Registered full name
            email (STR)                          - Registered user email
            is_registered (INT <boolean> : 1, 0) - Registration procedure status
            channel (INT: 0,1,2,3)               - Established communication channel
        """
        with self._connect() as conn:
            cur = conn.cursor()
            cur.execute("""CREATE TABLE IF NOT EXISTS users (
                tg_id INTEGER PRIMARY KEY,
                username VARCHAR(50),
                first_name VARCHAR(50),
                last_name VARCHAR(50),
                full_name VARCHAR(100),
                email VARCHAR(50) UNIQUE,
                is_registered INTEGER DEFAULT 0,
                channel INTEGER DEFAULT 0
            )""")

    def create_user(self, user):
        """
                                Метод создает пользователя в базе данных.
        Используется при запуске бота через команду /start или другие начальные взаимодействия.
                                                                                    См. client
        """
        with self._connect() as conn:
            cur = conn.cursor()
            cur.execute("""INSERT OR IGNORE INTO users
                (tg_id, username, first_name, last_name, full_name, email,
                 is_registered, channel)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
                        (user.id, user.username, None, None, None, None, 0, 0))

    def get_fields(self, target_field: str) -> list:
        """
                Метод возвращает все записи определенного атрибута в виде списка <list>.
        Используется для подтверждения существования пользователя с помощью библиотеки thefuzz
                                                                См. voice_processing/name_extractor.py
        """
        with self._connect() as conn:
            cur = conn.cursor()
            query = f"SELECT {target_field} FROM users"
            cur.execute(query)
            rows = cur.fetchall()
            return list([row[0] for row in rows if row[0] is not None])


    def get_field(self, search_field: str, search_value, target_field: str):
        """
            Метод возвращает значение атрибута, где другой атрибут равен определенному значению.
        Используется например для поиска email по tg_id
                                                                             См. client
        """
        with self._connect() as conn:
            cur = conn.cursor()
            query = f"SELECT {target_field} FROM users WHERE {search_field} = ?"
            cur.execute(query, (search_value,))
            result = cur.fetchone()
            return result[0] if result else None

    def update_field(self, tg_id, field, value):
        """
            Метод заменяет значение атрибута, где другой атрибут равен определенному значению.
        Используется например для замены поля определенного юзера по tg_id
                                                                             См. client
        """
        with self._connect() as conn:
            cur = conn.cursor()
            query = f"UPDATE users SET {field} = ? WHERE tg_id = ?"
            cur.execute(query, (value, tg_id))



    def get_id_by_name(self, full_name: str) -> str | None:
        """
            NONE
        """
        # todo возможно не понадобиться
        parts = full_name.lower().strip().split()
        if len(parts) != 2:
            return None
        name1, name2 = parts

        with self._connect() as conn:
            cur = conn.cursor()
            cur.execute("""
                SELECT tg_id FROM users
                WHERE (LOWER(first_name) = ? AND LOWER(last_name) = ?)
                   OR (LOWER(first_name) = ? AND LOWER(last_name) = ?)
                LIMIT 1
            """, (name1, name2, name2, name1))
            result = cur.fetchone()
            return result[0] if result else None

    def fullname_occupied(self, full_name: str) -> bool | None:
        """
        NONE
        """
        # todo возможно не понадобиться

        parts = full_name.lower().strip().split()
        if len(parts) != 2:
            return None
        name1, name2 = parts
        with self._connect() as conn:
            cur = conn.cursor()
            cur.execute("""
                        SELECT EXISTS (
                            SELECT 1 FROM users
                            WHERE (LOWER(first_name) = ? AND LOWER(last_name) = ?)
                               OR (LOWER(first_name) = ? AND LOWER(last_name) = ?)
                            LIMIT 1
                        )
                    """, (name1, name2, name2, name1))
            (exists,) = cur.fetchone()
            return bool(exists)

    def get_all_users(self) -> list:
        """ Метод возвращает количество записей в БД. См. admin """
        from .users_csv import save_users_to_csv

        with self._connect() as conn:
            cur = conn.cursor()
            cur.execute("SELECT * FROM users")
            rows = cur.fetchall()

            save_users_to_csv(rows)
            return rows

    def get_count_fields(self, search_field: str = None, search_value = None):
        """
        Метод возвращает количество записей соответствующие определенному значению определенного поля.
        Используется для анализа работы системы. Команда /stat в админ-панели.
                                                                                    См. admin
        """
        with self._connect() as conn:
            cur = conn.cursor()

            if (search_field is not None) and (search_value is not None) :
                query = f"SELECT COUNT(*) FROM users WHERE {search_field} = ?"
                cur.execute(query, (search_value,))
            else:
                query = f"SELECT COUNT(*) FROM users"
                cur.execute(query)

            (count, ) = cur.fetchone()
            return count