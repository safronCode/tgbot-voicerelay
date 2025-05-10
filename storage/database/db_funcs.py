import os, sqlite3
from storage.config import project_path

class UserDatabase:
    def __init__(self):
        self.path = os.path.join(project_path, "storage", "database", "users.db")

    def _connect(self):
        return sqlite3.connect(self.path)

    def init_db(self):
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
        with self._connect() as conn:
            cur = conn.cursor()
            cur.execute("""INSERT OR IGNORE INTO users
                (tg_id, username, first_name, last_name, full_name, email,
                 is_registered, channel)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
                        (user.id, user.username, None, None, None, None, 0, 0))

    def get_count_fields(self, search_field: str = None, search_value = None):
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

    def get_field(self, search_field: str, search_value, target_field: str):
        with self._connect() as conn:
            cur = conn.cursor()
            query = f"SELECT {target_field} FROM users WHERE {search_field} = ?"
            cur.execute(query, (search_value,))
            result = cur.fetchone()
            return result[0] if result else None

    def update_field(self, tg_id, field, value):
        with self._connect() as conn:
            cur = conn.cursor()
            query = f"UPDATE users SET {field} = ? WHERE tg_id = ?"
            cur.execute(query, (value, tg_id))



    def get_id_by_name(self, full_name: str) -> str | None:
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

    def fullname_occupied(self, full_name: str) -> bool:
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

    # todo Игорь админ-панель
    def get_all_users(self) -> list:

        from .users_csv import save_users_to_csv

        with self._connect() as conn:
            cur = conn.cursor()
            cur.execute("SELECT * FROM users")
            rows = cur.fetchall()

            save_users_to_csv(rows)
            return rows
