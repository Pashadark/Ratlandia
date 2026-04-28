"""Система достижений, предметов и уровней"""

from typing import Dict, List, Optional
from enum import Enum
import random
import sqlite3

DB_FILE = "/root/bot/ratings.db"

class ItemRarity(Enum):
    COMMON = "common"
    RARE = "rare"
    EPIC = "epic"
    LEGENDARY = "legendary"
    MYTHIC = "mythic"

ACHIEVEMENTS = {
    "first_blood": {"name": "🩸 Первая кровь", "desc": "Совершить первое убийство", "rarity": "common", "xp": 100},
    "master_of_disguise": {"name": "🎭 Мастер маскировки", "desc": "Победить за Крысу", "rarity": "rare", "xp": 250},
    "nest_defender": {"name": "🛡️ Защитник норы", "desc": "Победить за Мышь", "rarity": "common", "xp": 100},
    "serial_killer": {"name": "🔥 Серийный убийца", "desc": "3 победы за Крысу подряд", "rarity": "epic", "xp": 500},
    "eagle_eye": {"name": "🎯 Меткий глаз", "desc": "Угадать Крысу с первого голосования", "rarity": "rare", "xp": 250},
    "rat_king": {"name": "👑 Король крыс", "desc": "10 побед за Крысу", "rarity": "legendary", "xp": 1000},
    "pack_leader": {"name": "🐭 Вожак стаи", "desc": "25 побед за Мышь", "rarity": "legendary", "xp": 1000},
    "merciless": {"name": "💀 Безжалостный", "desc": "Убить 50 игроков", "rarity": "epic", "xp": 500},
    "night_hunter": {"name": "🌙 Ночной охотник", "desc": "Убивать каждую ночь", "rarity": "epic", "xp": 500},
    "rat_emperor": {"name": "🏰 Крысиный император", "desc": "50 побед за Крысу", "rarity": "mythic", "xp": 2000},
    "mouse_god": {"name": "⚡ Бог мышей", "desc": "100 побед за Мышь", "rarity": "mythic", "xp": 2000},
}

ITEMS = {
    "poison_cheese": {"name": "🧀 Ядовитый сыр", "type": "rat", "rarity": "common", "desc": "+1 сек к ночи"},
    "shadow_cloak": {"name": "🌑 Плащ тени", "type": "rat", "rarity": "rare", "desc": "Убить дважды за ночь"},
    "detective_loupe": {"name": "🔍 Лупа детектива", "type": "mouse", "rarity": "common", "desc": "+5% точность голосования"},
    "faith_shield": {"name": "🛡️ Щит веры", "type": "mouse", "rarity": "rare", "desc": "Защита от убийства на ночь"},
    "lucky_ticket": {"name": "🎫 Билет удачи", "type": "neutral", "rarity": "common", "desc": "+50 XP"},
    "champion_cup": {"name": "🏆 Кубок чемпиона", "type": "neutral", "rarity": "legendary", "desc": "x2 XP за победу"},
}

DROP_CHANCES = {"common": 60, "rare": 25, "epic": 10, "legendary": 4, "mythic": 1}

# Система уровней
def get_level_from_xp(xp: int) -> int:
    return int((xp // 100) ** 0.5) + 1

def get_xp_for_level(level: int) -> int:
    return ((level - 1) ** 2) * 100

def get_level_progress(xp: int) -> tuple:
    level = get_level_from_xp(xp)
    current_level_xp = get_xp_for_level(level)
    next_level_xp = get_xp_for_level(level + 1)
    xp_in_level = xp - current_level_xp
    xp_needed = next_level_xp - current_level_xp
    progress = int(xp_in_level / xp_needed * 10)
    return level, xp, progress, xp_needed - xp_in_level

def init_db():
    with sqlite3.connect(DB_FILE) as conn:
        c = conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS inventory (user_id INTEGER, item_id TEXT, quantity INTEGER DEFAULT 1, PRIMARY KEY (user_id, item_id))''')
        c.execute('''CREATE TABLE IF NOT EXISTS user_achievements (user_id INTEGER, achievement_id TEXT, unlocked_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP, PRIMARY KEY (user_id, achievement_id))''')
        c.execute('''CREATE TABLE IF NOT EXISTS user_stats (user_id INTEGER PRIMARY KEY, total_games INTEGER DEFAULT 0, total_wins INTEGER DEFAULT 0, rat_wins INTEGER DEFAULT 0, mouse_wins INTEGER DEFAULT 0, total_kills INTEGER DEFAULT 0, total_votes INTEGER DEFAULT 0, xp INTEGER DEFAULT 0)''')
        conn.commit()

def add_xp(user_id: int, amount: int):
    with sqlite3.connect(DB_FILE) as conn:
        c = conn.cursor()
        c.execute('UPDATE user_stats SET xp = xp + ? WHERE user_id = ?', (amount, user_id))
        conn.commit()

def get_user_xp(user_id: int) -> int:
    with sqlite3.connect(DB_FILE) as conn:
        c = conn.cursor()
        c.execute('SELECT xp FROM user_stats WHERE user_id = ?', (user_id,))
        row = c.fetchone()
        return row[0] if row else 0

def add_item(user_id: int, item_id: str, quantity: int = 1):
    with sqlite3.connect(DB_FILE) as conn:
        c = conn.cursor()
        c.execute('INSERT INTO inventory VALUES (?,?,?) ON CONFLICT(user_id, item_id) DO UPDATE SET quantity = quantity + ?', (user_id, item_id, quantity, quantity))
        conn.commit()

def get_inventory(user_id: int) -> Dict[str, int]:
    with sqlite3.connect(DB_FILE) as conn:
        c = conn.cursor()
        c.execute('SELECT item_id, quantity FROM inventory WHERE user_id = ?', (user_id,))
        return {row[0]: row[1] for row in c.fetchall()}

def get_random_item(winner_role: str) -> Optional[str]:
    available = [(iid, data["rarity"]) for iid, data in ITEMS.items() if data["type"] in [winner_role, "neutral"]]
    if not available:
        return None
    rand = random.randint(1, 100)
    cum = 0
    for iid, rar in available:
        cum += DROP_CHANCES[rar]
        if rand <= cum:
            return iid
    return available[0][0]

def unlock_achievement(user_id: int, achievement_id: str) -> bool:
    if achievement_id not in ACHIEVEMENTS:
        return False
    with sqlite3.connect(DB_FILE) as conn:
        c = conn.cursor()
        try:
            c.execute('INSERT INTO user_achievements (user_id, achievement_id) VALUES (?, ?)', (user_id, achievement_id))
            conn.commit()
            add_xp(user_id, ACHIEVEMENTS[achievement_id]["xp"])
            return True
        except sqlite3.IntegrityError:
            return False

def get_achievements(user_id: int) -> List[Dict]:
    with sqlite3.connect(DB_FILE) as conn:
        c = conn.cursor()
        c.execute('SELECT achievement_id FROM user_achievements WHERE user_id = ?', (user_id,))
        return [ACHIEVEMENTS[row[0]] for row in c.fetchall() if row[0] in ACHIEVEMENTS]

def update_stats(user_id: int, **kwargs):
    with sqlite3.connect(DB_FILE) as conn:
        c = conn.cursor()
        c.execute('SELECT user_id FROM user_stats WHERE user_id = ?', (user_id,))
        if not c.fetchone():
            fields = ["user_id"] + list(kwargs.keys())
            values = [user_id] + list(kwargs.values())
            c.execute(f"INSERT INTO user_stats ({','.join(fields)}) VALUES ({','.join(['?']*len(fields))})", values)
        else:
            updates = [f"{k} = {k} + ?" for k in kwargs]
            c.execute(f"UPDATE user_stats SET {','.join(updates)} WHERE user_id = ?", list(kwargs.values()) + [user_id])
        conn.commit()

def check_and_unlock_achievements(user_id: int):
    with sqlite3.connect(DB_FILE) as conn:
        c = conn.cursor()
        c.execute('SELECT * FROM user_stats WHERE user_id = ?', (user_id,))
        row = c.fetchone()
        if not row:
            return
        stats = {"total_games": row[1], "total_wins": row[2], "rat_wins": row[3], "mouse_wins": row[4], "total_kills": row[5]}
    if stats["total_kills"] >= 1:
        unlock_achievement(user_id, "first_blood")
    if stats["rat_wins"] >= 1:
        unlock_achievement(user_id, "master_of_disguise")
    if stats["mouse_wins"] >= 1:
        unlock_achievement(user_id, "nest_defender")
    if stats["rat_wins"] >= 10:
        unlock_achievement(user_id, "rat_king")
    if stats["mouse_wins"] >= 25:
        unlock_achievement(user_id, "pack_leader")
    if stats["total_kills"] >= 50:
        unlock_achievement(user_id, "merciless")
    if stats["rat_wins"] >= 50:
        unlock_achievement(user_id, "rat_emperor")
    if stats["mouse_wins"] >= 100:
        unlock_achievement(user_id, "mouse_god")

init_db()
