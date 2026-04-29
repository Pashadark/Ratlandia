"""
УНИВЕРСАЛЬНЫЙ ПУЛ СОЕДИНЕНИЙ С БАЗАМИ ДАННЫХ
Поддерживает ratings.db, ratgames.db, bot.db, dice_stats.db
Лежат в data/database/
"""

import sqlite3
import os
from typing import Optional, Dict, List, Any
from contextlib import contextmanager


# ========== ПУТИ К БАЗАМ ==========
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data", "database")

DB_PATHS = {
    "ratings": os.path.join(DATA_DIR, "ratings.db"),
    "ratgames": os.path.join(DATA_DIR, "ratgames.db"),
    "bot": os.path.join(DATA_DIR, "bot.db"),
    "dice_stats": os.path.join(DATA_DIR, "dice_stats.db"),
}


class Database:
    """Пул соединений с конкретной базой"""

    def __init__(self, db_name: str = "ratings"):
        self.db_path = DB_PATHS.get(db_name, DB_PATHS["ratings"])
        self._ensure_db_exists()
        # Включаем WAL-режим для параллельного доступа
        with self.get_connection() as conn:
            conn.execute("PRAGMA journal_mode=WAL")
            conn.execute("PRAGMA busy_timeout=5000")

    def _ensure_db_exists(self):
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)

    @contextmanager
    def get_connection(self):
        conn = sqlite3.connect(self.db_path, timeout=10)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
        finally:
            conn.close()

    def execute(self, query: str, params: tuple = ()) -> int:
        with self.get_connection() as conn:
            cursor = conn.execute(query, params)
            conn.commit()
            return cursor.lastrowid

    def executemany(self, query: str, params_list: List[tuple]) -> int:
        with self.get_connection() as conn:
            cursor = conn.executemany(query, params_list)
            conn.commit()
            return cursor.rowcount

    def fetch_one(self, query: str, params: tuple = ()) -> Optional[Dict]:
        with self.get_connection() as conn:
            cursor = conn.execute(query, params)
            row = cursor.fetchone()
            return dict(row) if row else None

    def fetch_all(self, query: str, params: tuple = ()) -> List[Dict]:
        with self.get_connection() as conn:
            cursor = conn.execute(query, params)
            return [dict(row) for row in cursor.fetchall()]

    def table_exists(self, table_name: str) -> bool:
        result = self.fetch_one(
            "SELECT name FROM sqlite_master WHERE type='table' AND name=?",
            (table_name,)
        )
        return result is not None

    # ========== МИГРАЦИИ ==========

    def init_ratings_tables(self):
        """Таблицы рейтинга, валюты, опыта"""
        self.execute('''
            CREATE TABLE IF NOT EXISTS ratings (
                user_id INTEGER PRIMARY KEY,
                name TEXT,
                nickname TEXT,
                games INTEGER DEFAULT 0,
                wins INTEGER DEFAULT 0,
                games_as_rat INTEGER DEFAULT 0,
                wins_as_rat INTEGER DEFAULT 0,
                games_as_mouse INTEGER DEFAULT 0,
                wins_as_mouse INTEGER DEFAULT 0,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        self.execute('''
            CREATE TABLE IF NOT EXISTS user_currency (
                user_id INTEGER PRIMARY KEY,
                crumbs INTEGER DEFAULT 0,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        self.execute('''
            CREATE TABLE IF NOT EXISTS user_xp (
                user_id INTEGER PRIMARY KEY,
                xp INTEGER DEFAULT 0,
                level INTEGER DEFAULT 1,
                stat_points INTEGER DEFAULT 0,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

    # ========== РЕЙТИНГ ==========

    def get_rating(self, user_id: int) -> Optional[Dict]:
        return self.fetch_one(
            "SELECT * FROM ratings WHERE user_id = ?",
            (user_id,)
        )

    def create_rating(self, user_id: int, name: str) -> int:
        return self.execute(
            "INSERT INTO ratings (user_id, name) VALUES (?, ?)",
            (user_id, name)
        )

    def update_rating(self, user_id: int, **kwargs) -> bool:
        if not kwargs:
            return False
        set_clause = ", ".join(f"{k} = ?" for k in kwargs.keys())
        values = list(kwargs.values()) + [user_id]
        self.execute(
            f"UPDATE ratings SET {set_clause}, updated_at = CURRENT_TIMESTAMP WHERE user_id = ?",
            tuple(values)
        )
        return True

    def get_top_players(self, limit: int = 10) -> List[Dict]:
        return self.fetch_all(
            "SELECT * FROM ratings ORDER BY wins DESC LIMIT ?",
            (limit,)
        )

    # ========== КРОШКИ ==========

    def get_crumbs(self, user_id: int) -> int:
        result = self.fetch_one(
            "SELECT crumbs FROM user_currency WHERE user_id = ?",
            (user_id,)
        )
        return result['crumbs'] if result else 0

    def add_crumbs(self, user_id: int, amount: int) -> int:
        self.execute('''
            INSERT INTO user_currency (user_id, crumbs) VALUES (?, ?)
            ON CONFLICT(user_id) DO UPDATE SET
            crumbs = crumbs + ?, updated_at = CURRENT_TIMESTAMP
        ''', (user_id, amount, amount))
        return self.get_crumbs(user_id)

    def spend_crumbs(self, user_id: int, amount: int) -> bool:
        current = self.get_crumbs(user_id)
        if current < amount:
            return False
        self.execute('''
            UPDATE user_currency SET crumbs = crumbs - ?, updated_at = CURRENT_TIMESTAMP
            WHERE user_id = ?
        ''', (amount, user_id))
        return True

    # ========== ОПЫТ ==========

    def get_xp(self, user_id: int) -> int:
        result = self.fetch_one(
            "SELECT xp FROM user_xp WHERE user_id = ?",
            (user_id,)
        )
        return result['xp'] if result else 0

    def add_xp(self, user_id: int, amount: int) -> int:
        self.execute('''
            INSERT INTO user_xp (user_id, xp) VALUES (?, ?)
            ON CONFLICT(user_id) DO UPDATE SET
            xp = xp + ?, updated_at = CURRENT_TIMESTAMP
        ''', (user_id, amount, amount))
        return self.get_xp(user_id)

    def get_level(self, user_id: int) -> int:
        result = self.fetch_one(
            "SELECT level FROM user_xp WHERE user_id = ?",
            (user_id,)
        )
        return result['level'] if result else 1

    def set_level(self, user_id: int, level: int) -> None:
        self.execute('''
            INSERT INTO user_xp (user_id, level) VALUES (?, ?)
            ON CONFLICT(user_id) DO UPDATE SET
            level = ?, updated_at = CURRENT_TIMESTAMP
        ''', (user_id, level, level))

    def get_stat_points(self, user_id: int) -> int:
        result = self.fetch_one(
            "SELECT stat_points FROM user_xp WHERE user_id = ?",
            (user_id,)
        )
        return result['stat_points'] if result else 0

    def add_stat_points(self, user_id: int, amount: int) -> None:
        self.execute('''
            INSERT INTO user_xp (user_id, stat_points) VALUES (?, ?)
            ON CONFLICT(user_id) DO UPDATE SET
            stat_points = stat_points + ?, updated_at = CURRENT_TIMESTAMP
        ''', (user_id, amount, amount))

    def spend_stat_points(self, user_id: int, amount: int) -> bool:
        current = self.get_stat_points(user_id)
        if current < amount:
            return False
        self.execute('''
            UPDATE user_xp SET stat_points = stat_points - ?, updated_at = CURRENT_TIMESTAMP
            WHERE user_id = ?
        ''', (amount, user_id))
        return True


# ========== ГЛОБАЛЬНЫЕ ЭКЗЕМПЛЯРЫ ==========
db_ratings = Database("ratings")
db_ratgames = Database("ratgames")
db_bot = Database("bot")
db_dice = Database("dice_stats")

# Инициализация таблиц при импорте
db_ratings.init_ratings_tables()