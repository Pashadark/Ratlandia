"""Сервис туннелей — забеги, бой, комнаты, благословения, кооператив"""

import sqlite3
import random
import json
import uuid
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta

from config import settings

DB_FILE = settings.main_db_path


# ========== БАЗА ДАННЫХ ==========

def init_game_db():
    """Создаёт все таблицы для туннелей"""
    with sqlite3.connect(DB_FILE) as conn:
        c = conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS tunnel_run (
            user_id INTEGER PRIMARY KEY, current_room INTEGER DEFAULT 1,
            rooms_completed INTEGER DEFAULT 0, crumbs_collected INTEGER DEFAULT 0,
            xp_collected INTEGER DEFAULT 0, kill_streak INTEGER DEFAULT 0,
            monsters_killed INTEGER DEFAULT 0, path_choice TEXT DEFAULT 'normal',
            blessed BOOLEAN DEFAULT 0, blessings TEXT, run_seed TEXT)''')
        c.execute('''CREATE TABLE IF NOT EXISTS tunnel_bosses_defeated (
            user_id INTEGER, monster_id TEXT,
            defeated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            PRIMARY KEY (user_id, monster_id))''')
        c.execute('''CREATE TABLE IF NOT EXISTS tunnel_records (
            user_id INTEGER PRIMARY KEY, max_rooms INTEGER DEFAULT 0,
            max_crumbs INTEGER DEFAULT 0, max_kills INTEGER DEFAULT 0,
            total_bosses_killed INTEGER DEFAULT 0)''')
        c.execute('''CREATE TABLE IF NOT EXISTS tunnel_invites (
            invite_id TEXT PRIMARY KEY, host_id INTEGER, guest_id INTEGER,
            boss_id TEXT, room_number INTEGER, status TEXT DEFAULT 'pending',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP, expires_at TIMESTAMP)''')
        c.execute('''CREATE TABLE IF NOT EXISTS tunnel_coop_battles (
            battle_id TEXT PRIMARY KEY, boss_id TEXT, host_id INTEGER, guest_id INTEGER,
            boss_hp INTEGER, boss_max_hp INTEGER, turn INTEGER DEFAULT 1,
            current_player INTEGER, host_hp INTEGER, guest_hp INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')
        c.execute('''CREATE TABLE IF NOT EXISTS action_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER,
            action TEXT, icon TEXT DEFAULT '📌',
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')
        conn.commit()


# ========== ЗАБЕГИ ==========

def start_tunnel_run(user_id: int) -> Dict:
    """Начинает новый забег"""
    with sqlite3.connect(DB_FILE) as conn:
        c = conn.cursor()
        c.execute('''INSERT OR REPLACE INTO tunnel_run 
                     (user_id, current_room, rooms_completed, crumbs_collected, xp_collected,
                      kill_streak, monsters_killed, blessed, run_seed)
                     VALUES (?, 1, 0, 0, 0, 0, 0, 0, ?)''',
                  (user_id, str(random.randint(1000, 9999))))
        conn.commit()
    return {"success": True}


def get_tunnel_run(user_id: int) -> Optional[Dict]:
    """Возвращает активный забег"""
    with sqlite3.connect(DB_FILE) as conn:
        c = conn.cursor()
        c.execute('''SELECT current_room, rooms_completed, crumbs_collected, xp_collected,
                     kill_streak, monsters_killed, path_choice, blessed, blessings
                     FROM tunnel_run WHERE user_id = ?''', (user_id,))
        row = c.fetchone()
        if row:
            blessings = row[8]
            if blessings and isinstance(blessings, str):
                try:
                    blessings = json.loads(blessings)
                except:
                    blessings = []
            return {
                "current_room": row[0], "rooms_completed": row[1],
                "crumbs_collected": row[2], "xp_collected": row[3],
                "kill_streak": row[4], "monsters_killed": row[5],
                "path_choice": row[6], "blessed": bool(row[7]),
                "blessings": blessings if blessings else []
            }
    return None


def update_tunnel_run(user_id: int, **kwargs) -> bool:
    """Обновляет данные активного забега"""
    with sqlite3.connect(DB_FILE) as conn:
        c = conn.cursor()
        c.execute('SELECT user_id FROM tunnel_run WHERE user_id = ?', (user_id,))
        if not c.fetchone():
            return False
        updates = []
        values = []
        for k, v in kwargs.items():
            updates.append(f"{k} = ?")
            values.append(json.dumps(v) if isinstance(v, list) else v)
        values.append(user_id)
        c.execute(f"UPDATE tunnel_run SET {','.join(updates)} WHERE user_id = ?", values)
        conn.commit()
        return True


def advance_room(user_id: int):
    """Переходит в следующую комнату"""
    with sqlite3.connect(DB_FILE) as conn:
        c = conn.cursor()
        c.execute('''UPDATE tunnel_run SET current_room = current_room + 1,
                     rooms_completed = rooms_completed + 1 WHERE user_id = ?''', (user_id,))
        conn.commit()


def end_tunnel_run(user_id: int, died: bool = False) -> Dict:
    """Завершает забег и обновляет рекорды"""
    with sqlite3.connect(DB_FILE) as conn:
        c = conn.cursor()
        c.execute('''SELECT crumbs_collected, xp_collected, rooms_completed, monsters_killed
                     FROM tunnel_run WHERE user_id = ?''', (user_id,))
        row = c.fetchone()
        if not row:
            return {"crumbs": 0, "xp": 0, "rooms": 0, "kills": 0}
        crumbs = row[0] // 2 if died else row[0]
        xp = row[1]
        rooms = row[2]
        kills = row[3]
        c.execute('''INSERT INTO tunnel_records (user_id, max_rooms, max_crumbs, max_kills)
                     VALUES (?, ?, ?, ?)
                     ON CONFLICT(user_id) DO UPDATE SET
                     max_rooms = MAX(max_rooms, ?), max_crumbs = MAX(max_crumbs, ?),
                     max_kills = MAX(max_kills, ?)''',
                  (user_id, rooms, crumbs, kills, rooms, crumbs, kills))
        c.execute('DELETE FROM tunnel_run WHERE user_id = ?', (user_id,))
        conn.commit()
        return {"crumbs": crumbs, "xp": xp, "rooms": rooms, "kills": kills}


def add_run_loot(user_id: int, crumbs: int, xp: int, increment_kills: bool = True):
    """Добавляет добычу в текущий забег"""
    with sqlite3.connect(DB_FILE) as conn:
        c = conn.cursor()
        if increment_kills:
            c.execute('''UPDATE tunnel_run SET crumbs_collected = crumbs_collected + ?,
                         xp_collected = xp_collected + ?, kill_streak = kill_streak + 1,
                         monsters_killed = monsters_killed + 1 WHERE user_id = ?''',
                      (crumbs, xp, user_id))
        else:
            c.execute('''UPDATE tunnel_run SET crumbs_collected = crumbs_collected + ?,
                         xp_collected = xp_collected + ? WHERE user_id = ?''',
                      (crumbs, xp, user_id))
        conn.commit()


def reset_kill_streak(user_id: int):
    """Сбрасывает серию убийств"""
    with sqlite3.connect(DB_FILE) as conn:
        c = conn.cursor()
        c.execute('UPDATE tunnel_run SET kill_streak = 0 WHERE user_id = ?', (user_id,))
        conn.commit()


def set_blessed(user_id: int, blessed: bool):
    """Устанавливает благословение на забег"""
    with sqlite3.connect(DB_FILE) as conn:
        c = conn.cursor()
        c.execute('UPDATE tunnel_run SET blessed = ? WHERE user_id = ?',
                  (1 if blessed else 0, user_id))
        conn.commit()


def is_boss_defeated(user_id: int, monster_id: str) -> bool:
    """Проверяет, побеждал ли игрок этого босса"""
    with sqlite3.connect(DB_FILE) as conn:
        c = conn.cursor()
        c.execute('SELECT 1 FROM tunnel_bosses_defeated WHERE user_id = ? AND monster_id = ?',
                  (user_id, monster_id))
        return c.fetchone() is not None


def mark_boss_defeated(user_id: int, monster_id: str):
    """Отмечает босса как побеждённого"""
    with sqlite3.connect(DB_FILE) as conn:
        c = conn.cursor()
        try:
            c.execute('INSERT INTO tunnel_bosses_defeated (user_id, monster_id) VALUES (?, ?)',
                      (user_id, monster_id))
            c.execute('UPDATE tunnel_records SET total_bosses_killed = total_bosses_killed + 1 WHERE user_id = ?',
                      (user_id,))
            conn.commit()
        except sqlite3.IntegrityError:
            pass


def get_tunnel_records(user_id: int) -> Dict:
    """Возвращает рекорды игрока в туннелях"""
    with sqlite3.connect(DB_FILE) as conn:
        c = conn.cursor()
        c.execute('''SELECT max_rooms, max_crumbs, max_kills, total_bosses_killed
                     FROM tunnel_records WHERE user_id = ?''', (user_id,))
        row = c.fetchone()
        if row:
            return {"max_rooms": row[0], "max_crumbs": row[1],
                    "max_kills": row[2], "total_bosses_killed": row[3]}
    return {"max_rooms": 0, "max_crumbs": 0, "max_kills": 0, "total_bosses_killed": 0}


def add_action_history(user_id: int, action: str, icon: str = "📌"):
    """Добавляет запись в историю действий"""
    try:
        with sqlite3.connect(DB_FILE) as conn:
            c = conn.cursor()
            c.execute('SELECT COUNT(*) FROM action_history WHERE user_id = ?', (user_id,))
            if c.fetchone()[0] >= 50:
                c.execute(
                    'DELETE FROM action_history WHERE id = (SELECT MIN(id) FROM action_history WHERE user_id = ?)',
                    (user_id,))
            c.execute('INSERT INTO action_history (user_id, action, icon) VALUES (?, ?, ?)',
                      (user_id, action, icon))
            conn.commit()
    except:
        pass


# ========== ТИПЫ КОМНАТ ==========

def get_room_type() -> str:
    """Случайный тип комнаты"""
    return random.choices(
        ["monster", "treasure", "altar", "trap", "empty"],
        weights=[50, 20, 10, 15, 5]
    )[0]


# ========== СУНДУКИ В КОМНАТАХ ==========

def open_treasure_chest(choice: str) -> Tuple[str, Optional[int], Optional[str], Optional[int]]:
    """
    Открытие сундука в сокровищнице.
    Возвращает (reward_type, amount, item_id, damage)
    reward_type: "crumbs", "item", "trap"
    """
    roll = random.randint(1, 100)

    if choice == "left":
        if roll <= 50:
            return ("crumbs", random.randint(10, 20), None, None)
        elif roll <= 80:
            return ("item", None, None, None)
        else:
            return ("trap", None, None, random.randint(5, 10))
    elif choice == "middle":
        if roll <= 30:
            return ("crumbs", random.randint(15, 25), None, None)
        elif roll <= 70:
            return ("item", None, None, None)
        else:
            return ("trap", None, None, random.randint(8, 15))
    else:
        if roll <= 40:
            return ("crumbs", random.randint(5, 15), None, None)
        elif roll <= 90:
            return ("item", None, None, None)
        else:
            return ("trap", None, None, random.randint(3, 8))


# ========== БЛАГОСЛОВЕНИЯ ==========

ALTAR_BLESSINGS = [
    {"id": "damage_boost", "name": "💪 Благословение силы", "desc": "+1 к урону до конца забега",
     "effect": "damage", "value": 1, "duration": "run", "icon": "💪"},
    {"id": "crit_blessing", "name": "💥 Благословение крита", "desc": "+15% шанс критического удара",
     "effect": "crit_chance", "value": 15, "duration": "run", "icon": "💥"},
    {"id": "vampirism_blessing", "name": "🦇 Благословение вампира", "desc": "Восстанавливаешь 1 HP при ударе",
     "effect": "vampirism", "value": 1, "duration": "run", "icon": "🦇"},
    {"id": "double_strike", "name": "⚡ Благословение скорости", "desc": "10% шанс атаковать дважды",
     "effect": "double_attack_chance", "value": 10, "duration": "run", "icon": "⚡"},
    {"id": "health_boost", "name": "❤️ Благословение жизни", "desc": "+15 к максимальному здоровью",
     "effect": "max_health", "value": 15, "duration": "run", "icon": "❤️"},
    {"id": "dodge_boost", "name": "🍀 Благословение ловкости", "desc": "+10% к шансу уклонения",
     "effect": "dodge", "value": 10, "duration": "run", "icon": "🍀"},
    {"id": "shield_blessing", "name": "🛡️ Благословение щита", "desc": "Блокирует первую атаку врага",
     "effect": "shield", "value": 1, "duration": "run", "icon": "🛡️"},
    {"id": "regen_blessing", "name": "✨ Благословение регенерации", "desc": "+1 HP каждый ход",
     "effect": "regen", "value": 1, "duration": "run", "icon": "✨"},
    {"id": "thorns_blessing", "name": "🌵 Благословение шипов", "desc": "Враг получает 2 урона при атаке",
     "effect": "thorns", "value": 2, "duration": "run", "icon": "🌵"},
    {"id": "find_boost", "name": "🔍 Благословение поиска", "desc": "+15% к шансу найти тайник",
     "effect": "find_chance", "value": 15, "duration": "run", "icon": "🔍"},
    {"id": "crumbs_boost", "name": "🧀 Благословение изобилия", "desc": "+50% крошек с монстров",
     "effect": "crumbs_multiplier", "value": 1.5, "duration": "run", "icon": "🧀"},
    {"id": "xp_boost", "name": "⭐ Благословение мудрости", "desc": "+50% опыта с монстров",
     "effect": "xp_multiplier", "value": 1.5, "duration": "run", "icon": "⭐"},
    {"id": "lucky_blessing", "name": "🎲 Благословение удачи", "desc": "+10% ко всем шансам",
     "effect": "all_chances", "value": 10, "duration": "run", "icon": "🎲"},
    {"id": "instant_heal", "name": "💚 Мгновенное исцеление", "desc": "Восстанавливает 30 HP",
     "effect": "instant_heal", "value": 30, "duration": "instant", "icon": "💚"},
    {"id": "full_heal", "name": "🌟 Полное исцеление", "desc": "Восстанавливает всё здоровье",
     "effect": "full_heal", "value": 100, "duration": "instant", "icon": "🌟"},
    {"id": "stat_point", "name": "🎯 Дар мудрости", "desc": "+1 очко характеристик",
     "effect": "stat_point", "value": 1, "duration": "instant", "icon": "🎯"},
    {"id": "free_reroll", "name": "🔄 Дар перемен", "desc": "+1 бесплатная смена комнаты",
     "effect": "free_reroll", "value": 1, "duration": "instant", "icon": "🔄"},
]


def get_random_blessing() -> Dict:
    """Возвращает случайное благословение алтаря"""
    return random.choice(ALTAR_BLESSINGS).copy()


def apply_blessing_effect(user_id: int, blessing: Dict, run_data: Dict) -> Tuple[str, bool, Optional[int]]:
    """
    Применяет эффект благословения.
    Возвращает (текст_результата, нужно_обновить_здоровье, новое_здоровье)
    """
    effect = blessing["effect"]
    value = blessing["value"]
    duration = blessing.get("duration", "run")

    if duration == "instant":
        if effect in ("instant_heal", "full_heal"):
            with sqlite3.connect(DB_FILE) as conn:
                c = conn.cursor()
                c.execute('SELECT current_health, max_health FROM user_stats WHERE user_id = ?', (user_id,))
                row = c.fetchone()
                if row:
                    heal = value if effect == "instant_heal" else row[1]
                    new_hp = min(row[1], row[0] + heal)
                    c.execute('UPDATE user_stats SET current_health = ? WHERE user_id = ?', (new_hp, user_id))
                    conn.commit()
                    return (f"❤️ Восстановлено {heal} здоровья!" if effect == "instant_heal"
                            else "🌟 Здоровье полностью восстановлено!", True, new_hp)
        elif effect == "stat_point":
            with sqlite3.connect(DB_FILE) as conn:
                c = conn.cursor()
                c.execute('UPDATE user_stats SET stat_points = stat_points + ? WHERE user_id = ?', (value, user_id))
                conn.commit()
        return (blessing["desc"], False, None)

    # Эффекты на весь забег
    current_blessings = run_data.get("blessings", [])
    if not isinstance(current_blessings, list):
        current_blessings = []

    for b in current_blessings:
        if b.get("effect") == effect:
            b["value"] = b.get("value", 0) + value
            update_tunnel_run(user_id, blessings=current_blessings)
            return (f"{blessing['icon']} Эффект усилен! {blessing['desc']}", False, None)

    current_blessings.append(blessing)
    update_tunnel_run(user_id, blessings=current_blessings)

    if effect == "max_health":
        with sqlite3.connect(DB_FILE) as conn:
            c = conn.cursor()
            c.execute('SELECT current_health, max_health FROM user_stats WHERE user_id = ?', (user_id,))
            row = c.fetchone()
            if row:
                new_max = row[1] + value
                new_current = row[0] + value
                c.execute('UPDATE user_stats SET max_health = ?, current_health = ? WHERE user_id = ?',
                          (new_max, new_current, user_id))
                conn.commit()
                return (blessing["desc"], True, new_current)

    return (blessing["desc"], False, None)


# ========== БОЕВЫЕ РАСЧЁТЫ ==========

def calculate_player_damage(strength: int, blessed: bool = False) -> int:
    """Рассчитывает урон игрока"""
    base = strength
    bonus = random.randint(1, 3)
    if blessed:
        bonus += 1
    return base + bonus


def calculate_monster_damage(monster: Dict) -> int:
    """Рассчитывает урон монстра"""
    return random.randint(monster["min_damage"], monster["max_damage"])


def apply_body_part_effect(body_part: str, monster_state: Dict) -> str:
    """Применяет эффект от попадания по части тела"""
    if body_part == "head":
        monster_state["stunned"] = 1
        return "💫 Враг оглушён! Пропускает следующий ход."
    elif body_part == "paws":
        monster_state["weakened"] = 1
        return "⬇️ Враг замедлен! В следующем ходу нанесёт меньше урона."
    elif body_part == "body":
        monster_state["bleeding"] = 2
        return "🩸 Кровотечение! Враг будет терять по 1 HP каждый ход."
    elif body_part == "tail":
        monster_state["disoriented"] = 1
        return "😵 Враг дезориентирован! В следующем ходу атакует случайно."
    return ""


# ========== КООПЕРАТИВ ==========

def generate_invite_id() -> str:
    return str(uuid.uuid4())[:8]


def create_coop_invite(host_id: int, boss_id: str, room_number: int) -> str:
    invite_id = generate_invite_id()
    expires_at = datetime.now() + timedelta(minutes=5)
    with sqlite3.connect(DB_FILE) as conn:
        c = conn.cursor()
        c.execute('''INSERT INTO tunnel_invites (invite_id, host_id, boss_id, room_number, expires_at)
                     VALUES (?, ?, ?, ?, ?)''', (invite_id, host_id, boss_id, room_number, expires_at))
        conn.commit()
    return invite_id


def get_pending_invite(invite_id: str) -> Optional[Dict]:
    cleanup_expired_invites()
    with sqlite3.connect(DB_FILE) as conn:
        c = conn.cursor()
        c.execute('''SELECT invite_id, host_id, boss_id, room_number, status, expires_at
                     FROM tunnel_invites WHERE invite_id = ? AND status = 'pending' AND expires_at > datetime('now')''',
                  (invite_id,))
        row = c.fetchone()
        if row:
            return {"invite_id": row[0], "host_id": row[1], "boss_id": row[2],
                    "room_number": row[3], "status": row[4], "expires_at": row[5]}
    return None


def accept_coop_invite(invite_id: str, guest_id: int) -> bool:
    with sqlite3.connect(DB_FILE) as conn:
        c = conn.cursor()
        c.execute('''UPDATE tunnel_invites SET guest_id = ?, status = 'accepted'
                     WHERE invite_id = ? AND status = 'pending' AND expires_at > datetime('now')''',
                  (guest_id, invite_id))
        conn.commit()
        return c.rowcount > 0


def create_coop_battle(host_id: int, guest_id: int, boss_id: str,
                       host_hp: int, guest_hp: int, boss_hp: int) -> str:
    battle_id = str(uuid.uuid4())[:8]
    with sqlite3.connect(DB_FILE) as conn:
        c = conn.cursor()
        c.execute('''INSERT INTO tunnel_coop_battles
                     (battle_id, boss_id, host_id, guest_id, boss_hp, boss_max_hp,
                      current_player, host_hp, guest_hp)
                     VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                  (battle_id, boss_id, host_id, guest_id, boss_hp, boss_hp,
                   host_id, host_hp, guest_hp))
        conn.commit()
    return battle_id


def get_coop_battle(battle_id: str) -> Optional[Dict]:
    with sqlite3.connect(DB_FILE) as conn:
        c = conn.cursor()
        c.execute('''SELECT battle_id, boss_id, host_id, guest_id, boss_hp, boss_max_hp,
                     turn, current_player, host_hp, guest_hp
                     FROM tunnel_coop_battles WHERE battle_id = ?''', (battle_id,))
        row = c.fetchone()
        if row:
            return {"battle_id": row[0], "boss_id": row[1], "host_id": row[2], "guest_id": row[3],
                    "boss_hp": row[4], "boss_max_hp": row[5], "turn": row[6],
                    "current_player": row[7], "host_hp": row[8], "guest_hp": row[9]}
    return None


def update_coop_battle(battle_id: str, **kwargs):
    with sqlite3.connect(DB_FILE) as conn:
        c = conn.cursor()
        updates = [f"{k} = ?" for k in kwargs.keys()]
        values = list(kwargs.values()) + [battle_id]
        c.execute(f"UPDATE tunnel_coop_battles SET {','.join(updates)} WHERE battle_id = ?", values)
        conn.commit()


def delete_coop_battle(battle_id: str):
    with sqlite3.connect(DB_FILE) as conn:
        c = conn.cursor()
        c.execute('DELETE FROM tunnel_coop_battles WHERE battle_id = ?', (battle_id,))
        conn.commit()


def cleanup_expired_invites():
    with sqlite3.connect(DB_FILE) as conn:
        c = conn.cursor()
        c.execute('DELETE FROM tunnel_invites WHERE expires_at < datetime("now")')
        conn.commit()


# ========== БОСС ДЛЯ КООПА ==========

def get_boss_for_room(total_runs: int) -> str:
    """Возвращает ID босса в зависимости от количества забегов"""
    if total_runs >= 10:
        return "old_blind_cat"
    elif total_runs >= 5:
        return "two_headed_rat"
    return "black_ferret"


# Инициализация при импорте
init_game_db()