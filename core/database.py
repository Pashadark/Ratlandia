"""Работа с базой данных"""

import sqlite3
import json
import os
from typing import Optional, Dict, List, Any
from datetime import datetime
from contextlib import contextmanager

from config import settings

class Database:
    """Менеджер базы данных"""
    
    def __init__(self, db_path: str = None):
        self.db_path = db_path or settings.main_db_path
        self._ensure_db_exists()
    
    def _ensure_db_exists(self):
        """Создаёт папку для БД если её нет"""
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
    
    @contextmanager
    def get_connection(self):
        """Контекстный менеджер для соединения с БД"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
        finally:
            conn.close()
    
    def execute(self, query: str, params: tuple = ()) -> int:
        """Выполняет запрос и возвращает lastrowid"""
        with self.get_connection() as conn:
            cursor = conn.execute(query, params)
            conn.commit()
            return cursor.lastrowid
    
    def fetch_one(self, query: str, params: tuple = ()) -> Optional[Dict]:
        """Возвращает одну запись"""
        with self.get_connection() as conn:
            cursor = conn.execute(query, params)
            row = cursor.fetchone()
            return dict(row) if row else None
    
    def fetch_all(self, query: str, params: tuple = ()) -> List[Dict]:
        """Возвращает все записи"""
        with self.get_connection() as conn:
            cursor = conn.execute(query, params)
            return [dict(row) for row in cursor.fetchall()]
    
    def table_exists(self, table_name: str) -> bool:
        """Проверяет существование таблицы"""
        result = self.fetch_one(
            "SELECT name FROM sqlite_master WHERE type='table' AND name=?",
            (table_name,)
        )
        return result is not None
    
    # ========== МЕТОДЫ ДЛЯ РЕЙТИНГА ==========
    
    def init_ratings_tables(self):
        """Создаёт таблицы для рейтинга"""
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
    
    def get_rating(self, user_id: int) -> Optional[Dict]:
        """Получает рейтинг игрока"""
        return self.fetch_one(
            "SELECT * FROM ratings WHERE user_id = ?",
            (user_id,)
        )
    
    def create_rating(self, user_id: int, name: str) -> int:
        """Создаёт запись рейтинга"""
        return self.execute(
            "INSERT INTO ratings (user_id, name) VALUES (?, ?)",
            (user_id, name)
        )
    
    def update_rating(self, user_id: int, **kwargs) -> bool:
        """Обновляет рейтинг игрока"""
        if not kwargs:
            return False
        
        set_clause = ", ".join(f"{k} = ?" for k in kwargs.keys())
        values = list(kwargs.values()) + [user_id]
        
        self.execute(
            f"UPDATE ratings SET {set_clause}, updated_at = CURRENT_TIMESTAMP WHERE user_id = ?",
            tuple(values)
        )
        return True
    
    # ========== МЕТОДЫ ДЛЯ КРОШЕК ==========
    
    def get_crumbs(self, user_id: int) -> int:
        """Получает баланс крошек"""
        result = self.fetch_one(
            "SELECT crumbs FROM user_currency WHERE user_id = ?",
            (user_id,)
        )
        return result['crumbs'] if result else 0
    
    def add_crumbs(self, user_id: int, amount: int) -> int:
        """Добавляет крошки"""
        self.execute('''
            INSERT INTO user_currency (user_id, crumbs) VALUES (?, ?)
            ON CONFLICT(user_id) DO UPDATE SET 
            crumbs = crumbs + ?, updated_at = CURRENT_TIMESTAMP
        ''', (user_id, amount, amount))
        return self.get_crumbs(user_id)
    
    def spend_crumbs(self, user_id: int, amount: int) -> bool:
        """Тратит крошки"""
        current = self.get_crumbs(user_id)
        if current < amount:
            return False
        
        self.execute('''
            UPDATE user_currency SET crumbs = crumbs - ?, updated_at = CURRENT_TIMESTAMP
            WHERE user_id = ?
        ''', (amount, user_id))
        return True
    
    # ========== МЕТОДЫ ДЛЯ XP ==========
    
    def get_xp(self, user_id: int) -> int:
        """Получает опыт игрока"""
        result = self.fetch_one(
            "SELECT xp FROM user_xp WHERE user_id = ?",
            (user_id,)
        )
        return result['xp'] if result else 0
    
    def add_xp(self, user_id: int, amount: int) -> int:
        """Добавляет опыт"""
        self.execute('''
            INSERT INTO user_xp (user_id, xp) VALUES (?, ?)
            ON CONFLICT(user_id) DO UPDATE SET 
            xp = xp + ?, updated_at = CURRENT_TIMESTAMP
        ''', (user_id, amount, amount))
        return self.get_xp(user_id)
    
    def get_level(self, user_id: int) -> int:
        """Получает уровень игрока"""
        result = self.fetch_one(
            "SELECT level FROM user_xp WHERE user_id = ?",
            (user_id,)
        )
        return result['level'] if result else 1
    
    def set_level(self, user_id: int, level: int) -> None:
        """Устанавливает уровень игрока"""
        self.execute('''
            INSERT INTO user_xp (user_id, level) VALUES (?, ?)
            ON CONFLICT(user_id) DO UPDATE SET 
            level = ?, updated_at = CURRENT_TIMESTAMP
        ''', (user_id, level, level))
    
    def get_stat_points(self, user_id: int) -> int:
        """Получает очки характеристик"""
        result = self.fetch_one(
            "SELECT stat_points FROM user_xp WHERE user_id = ?",
            (user_id,)
        )
        return result['stat_points'] if result else 0
    
    def add_stat_points(self, user_id: int, amount: int) -> None:
        """Добавляет очки характеристик"""
        self.execute('''
            INSERT INTO user_xp (user_id, stat_points) VALUES (?, ?)
            ON CONFLICT(user_id) DO UPDATE SET 
            stat_points = stat_points + ?, updated_at = CURRENT_TIMESTAMP
        ''', (user_id, amount, amount))
    
    def spend_stat_points(self, user_id: int, amount: int) -> bool:
        """Тратит очки характеристик"""
        current = self.get_stat_points(user_id)
        if current < amount:
            return False
        
        self.execute('''
            UPDATE user_xp SET stat_points = stat_points - ?, updated_at = CURRENT_TIMESTAMP
            WHERE user_id = ?
        ''', (amount, user_id))
        return True


# Глобальный экземпляр БД
db = Database()
db.init_ratings_tables()