import sqlite3
import json
from typing import Dict, Optional
from datetime import datetime

DB_FILE = "ratings.db"

def init_db():
    """Создаёт таблицы, если их нет"""
    with sqlite3.connect(DB_FILE) as conn:
        cursor = conn.cursor()
        
        # Таблица рейтинга
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS ratings (
                user_id INTEGER PRIMARY KEY,
                name TEXT,
                games INTEGER DEFAULT 0,
                wins INTEGER DEFAULT 0,
                games_as_rat INTEGER DEFAULT 0,
                wins_as_rat INTEGER DEFAULT 0,
                games_as_mouse INTEGER DEFAULT 0,
                wins_as_mouse INTEGER DEFAULT 0,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Таблица активных игр (для восстановления после перезапуска)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS active_games (
                chat_id INTEGER PRIMARY KEY,
                game_state TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.commit()

def update_rating(user_id: int, name: str, role: str, won: bool):
    """Обновляет рейтинг игрока"""
    with sqlite3.connect(DB_FILE) as conn:
        cursor = conn.cursor()
        
        # Получаем текущие данные
        cursor.execute('SELECT * FROM ratings WHERE user_id = ?', (user_id,))
        row = cursor.fetchone()
        
        if row:
            # Обновляем существующего игрока
            games = row[2] + 1
            wins = row[3] + (1 if won else 0)
            games_as_rat = row[4] + (1 if 'КРЫСА' in role else 0)
            wins_as_rat = row[5] + (1 if won and 'КРЫСА' in role else 0)
            games_as_mouse = row[6] + (1 if 'МЫШЬ' in role else 0)
            wins_as_mouse = row[7] + (1 if won and 'МЫШЬ' in role else 0)
            
            cursor.execute('''
                UPDATE ratings SET 
                    name = ?, games = ?, wins = ?,
                    games_as_rat = ?, wins_as_rat = ?,
                    games_as_mouse = ?, wins_as_mouse = ?,
                    updated_at = CURRENT_TIMESTAMP
                WHERE user_id = ?
            ''', (name, games, wins, games_as_rat, wins_as_rat, games_as_mouse, wins_as_mouse, user_id))
        else:
            # Новый игрок
            cursor.execute('''
                INSERT INTO ratings (user_id, name, games, wins, games_as_rat, wins_as_rat, games_as_mouse, wins_as_mouse)
                VALUES (?, ?, 1, ?, ?, ?, ?, ?)
            ''', (
                user_id, name,
                1 if won else 0,
                1 if 'КРЫСА' in role else 0,
                1 if won and 'КРЫСА' in role else 0,
                1 if 'МЫШЬ' in role else 0,
                1 if won and 'МЫШЬ' in role else 0
            ))
        
        conn.commit()

def get_rating(user_id: int) -> Optional[Dict]:
    """Получает статистику игрока"""
    with sqlite3.connect(DB_FILE) as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM ratings WHERE user_id = ?', (user_id,))
        row = cursor.fetchone()
        
        if row:
            return dict(row)
        return None

def get_top_players(limit: int = 10) -> list:
    """Возвращает топ игроков"""
    with sqlite3.connect(DB_FILE) as conn:
        cursor = conn.cursor()
        cursor.execute('''
            SELECT user_id, name, games, wins, 
                   ROUND(CAST(wins AS FLOAT) / games * 100) as winrate
            FROM ratings 
            WHERE games > 0
            ORDER BY wins DESC, winrate DESC
            LIMIT ?
        ''', (limit,))
        
        return [
            {
                "user_id": row[0],
                "name": row[1],
                "games": row[2],
                "wins": row[3],
                "winrate": row[4] or 0
            }
            for row in cursor.fetchall()
        ]

def save_game_state(chat_id: int, state: dict):
    """Сохраняет состояние игры (для восстановления)"""
    with sqlite3.connect(DB_FILE) as conn:
        cursor = conn.cursor()
        cursor.execute('''
            INSERT OR REPLACE INTO active_games (chat_id, game_state, created_at)
            VALUES (?, ?, CURRENT_TIMESTAMP)
        ''', (chat_id, json.dumps(state)))
        conn.commit()

def load_game_state(chat_id: int) -> Optional[dict]:
    """Загружает состояние игры"""
    with sqlite3.connect(DB_FILE) as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT game_state FROM active_games WHERE chat_id = ?', (chat_id,))
        row = cursor.fetchone()
        if row:
            return json.loads(row[0])
        return None

def delete_game_state(chat_id: int):
    """Удаляет состояние игры"""
    with sqlite3.connect(DB_FILE) as conn:
        cursor = conn.cursor()
        cursor.execute('DELETE FROM active_games WHERE chat_id = ?', (chat_id,))
        conn.commit()

# Инициализируем БД при импорте
init_db()
