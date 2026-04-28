"""Логика инвентаря, экипировки и эффектов"""

import sqlite3
import random
import asyncio
from typing import Dict, List, Optional
from datetime import datetime, timedelta

DB_FILE = "/root/bot/ratings.db"

from handlers.items import ALL_ITEMS, EQUIPMENT, CONSUMABLES, CHESTS, DROP_CHANCES, EQUIPMENT_SLOTS
from handlers.achievements_data import ACHIEVEMENTS
from handlers.character import get_character_stats, sync_level_and_points

import logging
logger = logging.getLogger(__name__)

# ========== КАРТИНКИ СУНДУКОВ ==========
CHEST_IMAGES_CLOSED = {
    "common": "/root/bot/images/chests/chest_common_closed.jpg",
    "rare": "/root/bot/images/chests/chest_rare_closed.jpg",
    "epic": "/root/bot/images/chests/chest_epic_closed.jpg",
    "legendary": "/root/bot/images/chests/chest_legendary_closed.jpg",
    "mythic": "/root/bot/images/chests/chest_mythic_closed.jpg",
}

CHEST_IMAGES_OPEN = {
    "common": "/root/bot/images/chests/chest_common.jpg",
    "rare": "/root/bot/images/chests/chest_rare.jpg",
    "epic": "/root/bot/images/chests/chest_epic.jpg",
    "legendary": "/root/bot/images/chests/chest_legendary.jpg",
    "mythic": "/root/bot/images/chests/chest_mythic.jpg",
}

def init_inventory_db():
    with sqlite3.connect(DB_FILE) as conn:
        c = conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS inventory (user_id INTEGER, item_id TEXT, quantity INTEGER DEFAULT 1, PRIMARY KEY (user_id, item_id))''')
        c.execute('''CREATE TABLE IF NOT EXISTS equipment (user_id INTEGER, slot TEXT, item_id TEXT, PRIMARY KEY (user_id, slot))''')
        c.execute('''CREATE TABLE IF NOT EXISTS user_achievements (user_id INTEGER, achievement_id TEXT, unlocked_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP, PRIMARY KEY (user_id, achievement_id))''')
        c.execute('''CREATE TABLE IF NOT EXISTS user_stats (
            user_id INTEGER PRIMARY KEY, 
            total_games INTEGER DEFAULT 0, 
            total_wins INTEGER DEFAULT 0, 
            rat_wins INTEGER DEFAULT 0, 
            mouse_wins INTEGER DEFAULT 0, 
            total_kills INTEGER DEFAULT 0, 
            total_votes INTEGER DEFAULT 0, 
            xp INTEGER DEFAULT 0, 
            consecutive_wins INTEGER DEFAULT 0, 
            consecutive_rat_wins INTEGER DEFAULT 0,
            consecutive_mouse_wins INTEGER DEFAULT 0,
            guessed_rat_streak INTEGER DEFAULT 0, 
            framed_innocent INTEGER DEFAULT 0
        )''')
        c.execute('''CREATE TABLE IF NOT EXISTS user_currency (
            user_id INTEGER PRIMARY KEY,
            crumbs INTEGER DEFAULT 0
        )''')
        c.execute('''CREATE TABLE IF NOT EXISTS user_temp_effects (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            effect_name TEXT,
            effect_value TEXT,
            effect_icon TEXT,
            effect_desc TEXT,
            expires_at TIMESTAMP,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )''')
        c.execute('''CREATE TABLE IF NOT EXISTS user_beer_stats (
            user_id INTEGER PRIMARY KEY,
            beer_count INTEGER DEFAULT 0
        )''')
        c.execute('''CREATE TABLE IF NOT EXISTS user_chest_stats (
            user_id INTEGER PRIMARY KEY,
            chests_opened INTEGER DEFAULT 0
        )''')
        c.execute('''CREATE TABLE IF NOT EXISTS user_dice_wins (
            user_id INTEGER PRIMARY KEY,
            dice_wins INTEGER DEFAULT 0
        )''')
        conn.commit()

# ========== ПРЕДМЕТЫ ==========
def add_item(user_id: int, item_id: str, quantity: int = 1) -> bool:
    if item_id not in ALL_ITEMS:
        return False
    with sqlite3.connect(DB_FILE) as conn:
        c = conn.cursor()
        c.execute('INSERT INTO inventory VALUES (?,?,?) ON CONFLICT(user_id, item_id) DO UPDATE SET quantity = quantity + ?', (user_id, item_id, quantity, quantity))
        conn.commit()
        return True

def get_inventory(user_id: int) -> Dict[str, int]:
    with sqlite3.connect(DB_FILE) as conn:
        c = conn.cursor()
        c.execute('SELECT item_id, quantity FROM inventory WHERE user_id = ?', (user_id,))
        return {row[0]: row[1] for row in c.fetchall()}

def get_random_item(winner_role: str) -> Optional[str]:
    role_filter = "rat" if winner_role == "rat" else "mouse"
    available = []
    for iid, data in ALL_ITEMS.items():
        if data.get("type") == "chest":
            continue
        if data.get("role") in [role_filter, "all"]:
            available.append((iid, data["rarity"]))
    if not available:
        return None
    rand = random.randint(1, 100)
    cum = 0
    for iid, rar in available:
        cum += DROP_CHANCES.get(rar, 10)
        if rand <= cum:
            return iid
    return available[0][0]

def get_random_item_by_rarity(rarity: str) -> Optional[str]:
    available = [iid for iid, data in ALL_ITEMS.items() 
                 if data.get("rarity") == rarity and data.get("type") != "chest"]
    if not available:
        return None
    return random.choice(available)

def get_item_count(user_id: int, item_id: str) -> int:
    with sqlite3.connect(DB_FILE) as conn:
        c = conn.cursor()
        c.execute('SELECT quantity FROM inventory WHERE user_id = ? AND item_id = ?', (user_id, item_id))
        row = c.fetchone()
        return row[0] if row else 0

# ========== СУНДУКИ ==========
def open_chest(user_id: int, chest_id: str) -> Optional[Dict]:
    logger.info(f"🔓 open_chest: user={user_id}, chest_id={chest_id}")
    
    if chest_id not in CHESTS:
        logger.warning(f"❌ chest_id '{chest_id}' нет в CHESTS!")
        return None
    
    chest = CHESTS[chest_id]
    rarity = chest["drop_rarity"]
    role_filter = chest.get("role_filter", None)
    
    count = get_item_count(user_id, chest_id)
    logger.info(f"📦 Сундуков '{chest_id}' в инвентаре: {count}")
    
    if count <= 0:
        logger.warning(f"❌ Нет сундуков '{chest_id}' в инвентаре")
        return None
    
    available = []
    for iid, data in ALL_ITEMS.items():
        if data.get("type") == "chest":
            continue
        if data.get("rarity") != rarity:
            continue
        if role_filter and data.get("role") not in [role_filter, "all"]:
            continue
        available.append(iid)
    
    logger.info(f"🎲 Доступно предметов редкости '{rarity}': {len(available)}")
    
    if not available:
        logger.warning(f"❌ Нет доступных предметов редкости '{rarity}'")
        return None
    
    if chest.get("special") == "multiple_cheese":
        cheese_items = [iid for iid in available if "cheese" in iid.lower() or "сыр" in ALL_ITEMS[iid].get("name", "").lower()]
        if not cheese_items:
            cheese_items = available
        count = random.randint(3, 5)
        items_dropped = []
        for _ in range(count):
            if cheese_items:
                dropped = random.choice(cheese_items)
                add_item(user_id, dropped)
                items_dropped.append(dropped)
        
        remove_item(user_id, chest_id, 1)
        add_chest_opened(user_id)
        
        logger.info(f"✅ Сырный сундук открыт, выпало {len(items_dropped)} предметов")
        
        return {
            "type": "multiple",
            "items": items_dropped,
            "chest_name": chest["name"]
        }
    
    dropped = random.choice(available)
    add_item(user_id, dropped)
    remove_item(user_id, chest_id, 1)
    add_chest_opened(user_id)
    
    logger.info(f"✅ Сундук открыт, выпал предмет: {dropped}")
    
    return {
        "type": "single",
        "item_id": dropped,
        "item": ALL_ITEMS[dropped],
        "chest_name": chest["name"]
    }

def remove_item(user_id: int, item_id: str, quantity: int = 1) -> bool:
    with sqlite3.connect(DB_FILE) as conn:
        c = conn.cursor()
        c.execute('SELECT quantity FROM inventory WHERE user_id = ? AND item_id = ?', (user_id, item_id))
        row = c.fetchone()
        if not row or row[0] < quantity:
            return False
        
        if row[0] == quantity:
            c.execute('DELETE FROM inventory WHERE user_id = ? AND item_id = ?', (user_id, item_id))
        else:
            c.execute('UPDATE inventory SET quantity = quantity - ? WHERE user_id = ? AND item_id = ?', (quantity, user_id, item_id))
        conn.commit()
        return True

def get_available_chests(user_id: int) -> List[Dict]:
    inventory = get_inventory(user_id)
    chests = []
    for item_id, qty in inventory.items():
        if item_id in CHESTS and qty > 0:
            chest = CHESTS[item_id].copy()
            chest["id"] = item_id
            chest["quantity"] = qty
            chests.append(chest)
    return chests

def add_chest_opened(user_id: int):
    with sqlite3.connect(DB_FILE) as conn:
        c = conn.cursor()
        c.execute('INSERT INTO user_chest_stats (user_id, chests_opened) VALUES (?, 1) ON CONFLICT(user_id) DO UPDATE SET chests_opened = chests_opened + 1', (user_id,))
        conn.commit()

def get_chests_opened(user_id: int) -> int:
    with sqlite3.connect(DB_FILE) as conn:
        c = conn.cursor()
        c.execute('SELECT chests_opened FROM user_chest_stats WHERE user_id = ?', (user_id,))
        row = c.fetchone()
        return row[0] if row else 0

def add_temp_effect(user_id: int, effect_data: dict, duration_hours: int = 1):
    expires_at = datetime.now() + timedelta(hours=duration_hours)
    with sqlite3.connect(DB_FILE) as conn:
        c = conn.cursor()
        c.execute('''
            INSERT INTO user_temp_effects 
            (user_id, effect_name, effect_value, effect_icon, effect_desc, expires_at)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (
            user_id,
            effect_data['effect'],
            str(effect_data.get('value', 1)),
            effect_data.get('icon', '🍺'),
            effect_data.get('desc', ''),
            expires_at
        ))
        conn.commit()

def get_active_temp_effects(user_id: int) -> list:
    clean_expired_effects(user_id)
    with sqlite3.connect(DB_FILE) as conn:
        c = conn.cursor()
        c.execute('''
            SELECT effect_name, effect_value, effect_icon, effect_desc, 
                   strftime('%Y-%m-%d %H:%M:%S', expires_at) as expires_at
            FROM user_temp_effects
            WHERE user_id = ? AND expires_at > datetime('now')
            ORDER BY expires_at
        ''', (user_id,))
        rows = c.fetchall()
        
        effects = []
        for row in rows:
            val = row[1]
            if val.isdigit():
                val = int(val)
            elif val.lower() == 'true':
                val = True
            elif val.lower() == 'false':
                val = False
            
            effects.append({
                'effect': row[0],
                'value': val,
                'icon': row[2],
                'desc': row[3],
                'expires_at': row[4]
            })
        return effects

def clean_expired_effects(user_id: int = None):
    with sqlite3.connect(DB_FILE) as conn:
        c = conn.cursor()
        if user_id:
            c.execute('DELETE FROM user_temp_effects WHERE user_id = ? AND expires_at <= datetime("now")', (user_id,))
        else:
            c.execute('DELETE FROM user_temp_effects WHERE expires_at <= datetime("now")')
        conn.commit()

def format_temp_effects(user_id: int) -> str:
    effects = get_active_temp_effects(user_id)
    if not effects:
        return ""
    
    text = "\n🍺 *Активные эффекты:*\n"
    for eff in effects:
        expires_str = eff['expires_at']
        if '.' in expires_str:
            expires_str = expires_str.split('.')[0]
        
        expiry_time = datetime.strptime(expires_str, '%Y-%m-%d %H:%M:%S')
        time_left = expiry_time - datetime.now()
        minutes_left = int(time_left.total_seconds() / 60)
        hours_left = minutes_left // 60
        minutes_left = minutes_left % 60
        
        if hours_left > 0:
            time_str = f"{hours_left} ч {minutes_left} мин"
        else:
            time_str = f"{minutes_left} мин"
        
        text += f"  {eff['icon']} {eff['desc']} (ещё {time_str})\n"
    
    return text

def add_beer_count(user_id: int):
    with sqlite3.connect(DB_FILE) as conn:
        c = conn.cursor()
        c.execute('INSERT INTO user_beer_stats (user_id, beer_count) VALUES (?, 1) ON CONFLICT(user_id) DO UPDATE SET beer_count = beer_count + 1', (user_id,))
        conn.commit()

def get_beer_count(user_id: int) -> int:
    with sqlite3.connect(DB_FILE) as conn:
        c = conn.cursor()
        c.execute('SELECT beer_count FROM user_beer_stats WHERE user_id = ?', (user_id,))
        row = c.fetchone()
        return row[0] if row else 0

def init_dice_stats():
    with sqlite3.connect(DB_FILE) as conn:
        c = conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS dice_stats (user_id INTEGER PRIMARY KEY, games_played INTEGER DEFAULT 0)''')
        c.execute('''CREATE TABLE IF NOT EXISTS dice_rewards_claimed (user_id INTEGER, milestone INTEGER, PRIMARY KEY (user_id, milestone))''')
        conn.commit()

def add_dice_game(user_id: int):
    with sqlite3.connect(DB_FILE) as conn:
        c = conn.cursor()
        c.execute('INSERT INTO dice_stats (user_id, games_played) VALUES (?, 1) ON CONFLICT(user_id) DO UPDATE SET games_played = games_played + 1', (user_id,))
        conn.commit()

def get_dice_games(user_id: int) -> int:
    with sqlite3.connect(DB_FILE) as conn:
        c = conn.cursor()
        c.execute('SELECT games_played FROM dice_stats WHERE user_id = ?', (user_id,))
        row = c.fetchone()
        return row[0] if row else 0

def add_dice_win(user_id: int):
    with sqlite3.connect(DB_FILE) as conn:
        c = conn.cursor()
        c.execute('INSERT INTO user_dice_wins (user_id, dice_wins) VALUES (?, 1) ON CONFLICT(user_id) DO UPDATE SET dice_wins = dice_wins + 1', (user_id,))
        conn.commit()

def get_dice_wins(user_id: int) -> int:
    with sqlite3.connect(DB_FILE) as conn:
        c = conn.cursor()
        c.execute('SELECT dice_wins FROM user_dice_wins WHERE user_id = ?', (user_id,))
        row = c.fetchone()
        return row[0] if row else 0

def check_dice_reward(user_id: int) -> Optional[str]:
    games = get_dice_games(user_id)
    milestones = {10: "common", 25: "rare", 50: "epic", 100: "legendary", 250: "mythic"}
    
    for milestone, rarity in milestones.items():
        if games >= milestone:
            with sqlite3.connect(DB_FILE) as conn:
                c = conn.cursor()
                c.execute('SELECT 1 FROM dice_rewards_claimed WHERE user_id = ? AND milestone = ?', (user_id, milestone))
                if not c.fetchone():
                    c.execute('INSERT INTO dice_rewards_claimed (user_id, milestone) VALUES (?, ?)', (user_id, milestone))
                    conn.commit()
                    return rarity
    return None

def init_match_history():
    with sqlite3.connect(DB_FILE) as conn:
        c = conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS match_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            role TEXT,
            won BOOLEAN,
            kills INTEGER DEFAULT 0,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )''')
        conn.commit()

def add_match_record(user_id: int, role: str, won: bool, kills: int = 0):
    with sqlite3.connect(DB_FILE) as conn:
        c = conn.cursor()
        c.execute('INSERT INTO match_history (user_id, role, won, kills) VALUES (?, ?, ?, ?)',
                  (user_id, role, won, kills))
        conn.commit()

def get_match_history(user_id: int, limit: int = 10):
    with sqlite3.connect(DB_FILE) as conn:
        c = conn.cursor()
        c.execute('''SELECT role, won, kills, timestamp FROM match_history 
                     WHERE user_id = ? ORDER BY timestamp DESC LIMIT ?''',
                  (user_id, limit))
        return c.fetchall()

# ========== ЭКИПИРОВКА ==========
def equip_item(user_id: int, item_id: str) -> bool:
    if item_id not in ALL_ITEMS:
        return False
    item = ALL_ITEMS[item_id]
    if item.get("type") != "equipment":
        return False
    slot = item.get("slot")
    if not slot:
        return False
    
    with sqlite3.connect(DB_FILE) as conn:
        c = conn.cursor()
        c.execute('SELECT quantity FROM inventory WHERE user_id = ? AND item_id = ?', (user_id, item_id))
        row = c.fetchone()
        if not row or row[0] <= 0:
            return False
        
        c.execute('INSERT INTO equipment VALUES (?,?,?) ON CONFLICT(user_id, slot) DO UPDATE SET item_id = ?', (user_id, slot, item_id, item_id))
        conn.commit()
        return True

def unequip_item(user_id: int, slot: str) -> bool:
    with sqlite3.connect(DB_FILE) as conn:
        c = conn.cursor()
        c.execute('DELETE FROM equipment WHERE user_id = ? AND slot = ?', (user_id, slot))
        conn.commit()
        return True

def get_equipment(user_id: int) -> Dict[str, str]:
    with sqlite3.connect(DB_FILE) as conn:
        c = conn.cursor()
        c.execute('SELECT slot, item_id FROM equipment WHERE user_id = ?', (user_id,))
        return {row[0]: row[1] for row in c.fetchall()}

def get_equipped_effects(user_id: int, player_role: str) -> Dict:
    effects = {}
    equipment = get_equipment(user_id)
    for slot, item_id in equipment.items():
        if item_id in ALL_ITEMS:
            item = ALL_ITEMS[item_id]
            if item.get("role") in [player_role, "all"]:
                for k, v in item.get("effect", {}).items():
                    if k in effects:
                        if isinstance(v, bool):
                            effects[k] = effects[k] or v
                        else:
                            effects[k] = effects[k] + v
                    else:
                        effects[k] = v
    return effects

# ========== РАСХОДНИКИ ==========
def use_consumable(user_id: int, item_id: str) -> bool:
    if item_id not in CONSUMABLES:
        return False
    
    with sqlite3.connect(DB_FILE) as conn:
        c = conn.cursor()
        c.execute('SELECT quantity FROM inventory WHERE user_id = ? AND item_id = ?', (user_id, item_id))
        row = c.fetchone()
        if not row or row[0] <= 0:
            return False
        
        if row[0] == 1:
            c.execute('DELETE FROM inventory WHERE user_id = ? AND item_id = ?', (user_id, item_id))
        else:
            c.execute('UPDATE inventory SET quantity = quantity - 1 WHERE user_id = ? AND item_id = ?', (user_id, item_id))
        conn.commit()
        return True

# ========== ДОСТИЖЕНИЯ ==========
def unlock_achievement(user_id: int, achievement_id: str) -> bool:
    if achievement_id not in ACHIEVEMENTS:
        return False
    with sqlite3.connect(DB_FILE) as conn:
        c = conn.cursor()
        try:
            c.execute('INSERT INTO user_achievements (user_id, achievement_id) VALUES (?, ?)', (user_id, achievement_id))
            conn.commit()
            add_xp(user_id, ACHIEVEMENTS[achievement_id]["xp"])
            
            from handlers.titles import check_and_unlock_titles
            check_and_unlock_titles(user_id)
            
            return True
        except sqlite3.IntegrityError:
            return False

def get_achievements(user_id: int) -> List[Dict]:
    with sqlite3.connect(DB_FILE) as conn:
        c = conn.cursor()
        c.execute('SELECT achievement_id FROM user_achievements WHERE user_id = ?', (user_id,))
        unlocked = [row[0] for row in c.fetchall()]
    result = []
    for ach_id, ach_data in ACHIEVEMENTS.items():
        if not ach_data.get("hidden", False) or ach_id in unlocked:
            ach_copy = ach_data.copy()
            ach_copy["id"] = ach_id
            ach_copy["unlocked"] = ach_id in unlocked
            result.append(ach_copy)
    return result

def get_achievements_count(user_id: int) -> int:
    with sqlite3.connect(DB_FILE) as conn:
        c = conn.cursor()
        c.execute('SELECT COUNT(*) FROM user_achievements WHERE user_id = ?', (user_id,))
        return c.fetchone()[0]

# ========== ОПЫТ И УРОВНИ ==========
def add_xp(user_id: int, amount: int, context=None):
    """Добавляет опыт и возвращает (был_ли_повышен_уровень, новый_уровень, старый_уровень)"""
    with sqlite3.connect(DB_FILE) as conn:
        c = conn.cursor()
        
        c.execute('SELECT xp FROM user_stats WHERE user_id = ?', (user_id,))
        row = c.fetchone()
        old_xp = row[0] if row else 0
        old_level = get_level_from_xp(old_xp)
        
        c.execute('INSERT INTO user_stats (user_id, xp) VALUES (?, ?) ON CONFLICT(user_id) DO UPDATE SET xp = xp + ?', (user_id, amount, amount))
        conn.commit()
        
        new_xp = old_xp + amount
        new_level = get_level_from_xp(new_xp)
        
        level_up = new_level > old_level
        
        if level_up and context:
            sync_level_and_points(user_id, new_level)
            add_action_history(user_id, f"Достигнут {new_level} уровень", "🎉")
            
            # Если 10 уровень — предлагаем выбрать класс
            if new_level == 10:
                from handlers.class_selection import send_class_selection
                asyncio.create_task(send_class_selection(context, user_id))
            
            from handlers.notifications import send_level_up_message
            asyncio.create_task(send_level_up_message(context, user_id, new_level, old_level))
        
        return level_up, new_level, old_level


def get_user_xp(user_id: int) -> int:
    with sqlite3.connect(DB_FILE) as conn:
        c = conn.cursor()
        c.execute('SELECT xp FROM user_stats WHERE user_id = ?', (user_id,))
        row = c.fetchone()
        return row[0] if row else 0

def get_level_from_xp(xp: int) -> int:
    if xp < 100:
        return 1
    return int((xp // 100) ** 0.5) + 1

def get_xp_for_level(level: int) -> int:
    return ((level - 1) ** 2) * 100

def get_level_progress(xp: int) -> tuple:
    level = get_level_from_xp(xp)
    current_level_xp = get_xp_for_level(level)
    next_level_xp = get_xp_for_level(level + 1)
    xp_in_level = xp - current_level_xp
    xp_needed = next_level_xp - current_level_xp
    return level, xp_in_level, xp_needed

def get_level(user_id: int) -> int:
    xp = get_user_xp(user_id)
    return get_level_from_xp(xp)

def get_xp(user_id: int) -> int:
    return get_user_xp(user_id)

# ========== ВАЛЮТА (КРОШКИ) ==========
def add_crumbs(user_id: int, amount: int):
    with sqlite3.connect(DB_FILE) as conn:
        c = conn.cursor()
        c.execute('INSERT INTO user_currency (user_id, crumbs) VALUES (?, ?) ON CONFLICT(user_id) DO UPDATE SET crumbs = crumbs + ?', (user_id, amount, amount))
        conn.commit()

def spend_crumbs(user_id: int, amount: int) -> bool:
    with sqlite3.connect(DB_FILE) as conn:
        c = conn.cursor()
        c.execute('SELECT crumbs FROM user_currency WHERE user_id = ?', (user_id,))
        row = c.fetchone()
        if not row or row[0] < amount:
            return False
        c.execute('UPDATE user_currency SET crumbs = crumbs - ? WHERE user_id = ?', (amount, user_id))
        conn.commit()
        return True

def get_crumbs(user_id: int) -> int:
    with sqlite3.connect(DB_FILE) as conn:
        c = conn.cursor()
        c.execute('SELECT crumbs FROM user_currency WHERE user_id = ?', (user_id,))
        row = c.fetchone()
        return row[0] if row else 0
    
def get_temp_effects(user_id: int) -> list:
    effects = []
    with sqlite3.connect(DB_FILE) as conn:
        c = conn.cursor()
        c.execute('''SELECT effect_type, effect_name, effect_value, duration 
                     FROM temp_effects WHERE user_id = ? AND duration > 0''', (user_id,))
        for row in c.fetchall():
            effects.append({
                "type": row[0],
                "name": row[1],
                "value": row[2],
                "duration": row[3]
            })
    return effects

def get_inventory_slots(user_id: int) -> tuple:
    inventory = get_inventory(user_id)
    items_count = sum(inventory.values())
    stats = get_character_stats(user_id)
    level = stats.get('level', 1)
    max_slots = 30 + (level - 1) * 2
    return items_count, max_slots

# ========== ИСТОРИЯ ДЕЙСТВИЙ ==========
def add_action_history(user_id: int, action: str, icon: str = "📌"):
    """Добавляет запись в историю действий (хранит последние 50)"""
    try:
        with sqlite3.connect(DB_FILE) as conn:
            c = conn.cursor()
            c.execute('SELECT COUNT(*) FROM action_history WHERE user_id = ?', (user_id,))
            if c.fetchone()[0] >= 50:
                c.execute('DELETE FROM action_history WHERE id = (SELECT MIN(id) FROM action_history WHERE user_id = ?)', (user_id,))
            c.execute('INSERT INTO action_history (user_id, action, icon) VALUES (?, ?, ?)', (user_id, action, icon))
            conn.commit()
    except:
        pass  # Если таблицы ещё нет — ничего страшного


def get_action_history(user_id: int, limit: int = 10) -> list:
    """Возвращает последние N действий"""
    try:
        with sqlite3.connect(DB_FILE) as conn:
            c = conn.cursor()
            c.execute('SELECT action, icon, timestamp FROM action_history WHERE user_id = ? ORDER BY id DESC LIMIT ?', (user_id, limit))
            return c.fetchall()
    except:
        return []
    
# ========== СТАТИСТИКА ==========
def update_stats(user_id: int, **kwargs):
    with sqlite3.connect(DB_FILE) as conn:
        c = conn.cursor()
        c.execute('SELECT user_id FROM user_stats WHERE user_id = ?', (user_id,))
        if not c.fetchone():
            fields = ["user_id"] + list(kwargs.keys())
            values = [user_id] + list(kwargs.values())
            placeholders = ','.join(['?'] * len(fields))
            c.execute(f"INSERT INTO user_stats ({','.join(fields)}) VALUES ({placeholders})", values)
        else:
            updates = [f"{k} = COALESCE({k}, 0) + ?" for k in kwargs.keys()]
            values = list(kwargs.values()) + [user_id]
            c.execute(f"UPDATE user_stats SET {','.join(updates)} WHERE user_id = ?", values)
        conn.commit()

def check_and_unlock_achievements(user_id: int):
    with sqlite3.connect(DB_FILE) as conn:
        c = conn.cursor()
        c.execute('SELECT * FROM user_stats WHERE user_id = ?', (user_id,))
        row = c.fetchone()
        if not row:
            return
        
        c.execute('PRAGMA table_info(user_stats)')
        columns = [col[1] for col in c.fetchall()]
        row_dict = dict(zip(columns, row))
        
        stats = {
            "total_games": row_dict.get("total_games", 0),
            "total_wins": row_dict.get("total_wins", 0),
            "rat_wins": row_dict.get("rat_wins", 0),
            "mouse_wins": row_dict.get("mouse_wins", 0),
            "total_kills": row_dict.get("total_kills", 0),
            "total_votes": row_dict.get("total_votes", 0),
            "consecutive_wins": row_dict.get("consecutive_wins", 0),
            "consecutive_rat_wins": row_dict.get("consecutive_rat_wins", 0),
            "consecutive_mouse_wins": row_dict.get("consecutive_mouse_wins", 0),
            "guessed_rat_streak": row_dict.get("guessed_rat_streak", 0),
            "framed_innocent": row_dict.get("framed_innocent", 0),
            "xp": row_dict.get("xp", 0),
        }
    
    if stats["total_kills"] >= 1:
        unlock_achievement(user_id, "first_blood")
    if stats["rat_wins"] >= 1:
        unlock_achievement(user_id, "master_of_disguise")
    if stats["mouse_wins"] >= 1:
        unlock_achievement(user_id, "nest_defender")
    if stats["consecutive_rat_wins"] >= 3:
        unlock_achievement(user_id, "serial_killer")
    if stats["rat_wins"] >= 15:
        unlock_achievement(user_id, "rat_king")
    if stats["mouse_wins"] >= 30:
        unlock_achievement(user_id, "pack_leader")
    if stats["total_kills"] >= 25:
        unlock_achievement(user_id, "merciless")
    if stats["total_votes"] >= 50:
        unlock_achievement(user_id, "voice_of_people")
    if stats["framed_innocent"] >= 1:
        unlock_achievement(user_id, "puppeteer")
    if stats["guessed_rat_streak"] >= 5:
        unlock_achievement(user_id, "psychic")
    if stats["rat_wins"] >= 50:
        unlock_achievement(user_id, "rat_emperor")
    if stats["mouse_wins"] >= 100:
        unlock_achievement(user_id, "mouse_god")
    if stats["consecutive_wins"] >= 10:
        unlock_achievement(user_id, "invincible")
    if stats["rat_wins"] >= 50 and stats["mouse_wins"] >= 50:
        unlock_achievement(user_id, "two_faced")
    if stats["total_kills"] >= 100:
        unlock_achievement(user_id, "butcher")
    if stats["total_games"] >= 500:
        unlock_achievement(user_id, "history_keeper")
    if stats["framed_innocent"] >= 5:
        unlock_achievement(user_id, "grand_manipulator")
    
    ach_count = get_achievements_count(user_id)
    total_ach = len([a for a in ACHIEVEMENTS.values() if not a.get("hidden", False)])
    if ach_count >= total_ach:
        unlock_achievement(user_id, "the_one")

# Инициализация
init_inventory_db()
init_dice_stats()
init_match_history()