"""Сервис инвентаря — предметы, сундуки, экипировка, расходники, эффекты, достижения, валюта, статы"""
import random
import json
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
import logging

from config import settings
from core.items.catalog import ALL_ITEMS, EQUIPMENT_SLOTS, DROP_CHANCES
from core.database import db_ratings

logger = logging.getLogger(__name__)


class InventoryService:
    """Вся работа с инвентарём и смежными таблицами"""

    # ========== ИНИЦИАЛИЗАЦИЯ ==========
    def init_db(self):
        db_ratings.execute('''CREATE TABLE IF NOT EXISTS inventory (
            user_id INTEGER, item_id TEXT, quantity INTEGER DEFAULT 1,
            PRIMARY KEY (user_id, item_id))''')
        db_ratings.execute('''CREATE TABLE IF NOT EXISTS equipment (
            user_id INTEGER, slot TEXT, item_id TEXT,
            PRIMARY KEY (user_id, slot))''')
        db_ratings.execute('''CREATE TABLE IF NOT EXISTS user_achievements (
            user_id INTEGER, achievement_id TEXT,
            unlocked_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            PRIMARY KEY (user_id, achievement_id))''')
        db_ratings.execute('''CREATE TABLE IF NOT EXISTS user_stats (
            user_id INTEGER PRIMARY KEY,
            total_games INTEGER DEFAULT 0, total_wins INTEGER DEFAULT 0,
            rat_wins INTEGER DEFAULT 0, mouse_wins INTEGER DEFAULT 0,
            total_kills INTEGER DEFAULT 0, total_votes INTEGER DEFAULT 0,
            xp INTEGER DEFAULT 0, consecutive_wins INTEGER DEFAULT 0,
            consecutive_rat_wins INTEGER DEFAULT 0, consecutive_mouse_wins INTEGER DEFAULT 0,
            guessed_rat_streak INTEGER DEFAULT 0, framed_innocent INTEGER DEFAULT 0)''')
        db_ratings.execute('''CREATE TABLE IF NOT EXISTS user_currency (
            user_id INTEGER PRIMARY KEY, crumbs INTEGER DEFAULT 0)''')
        db_ratings.execute('''CREATE TABLE IF NOT EXISTS user_temp_effects (
            id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER,
            effect_name TEXT, effect_value TEXT, effect_icon TEXT,
            effect_desc TEXT, expires_at TIMESTAMP,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')
        db_ratings.execute('''CREATE TABLE IF NOT EXISTS user_beer_stats (
            user_id INTEGER PRIMARY KEY, beer_count INTEGER DEFAULT 0)''')
        db_ratings.execute('''CREATE TABLE IF NOT EXISTS user_chest_stats (
            user_id INTEGER PRIMARY KEY, chests_opened INTEGER DEFAULT 0)''')
        db_ratings.execute('''CREATE TABLE IF NOT EXISTS user_dice_wins (
            user_id INTEGER PRIMARY KEY, dice_wins INTEGER DEFAULT 0)''')
        db_ratings.execute('''CREATE TABLE IF NOT EXISTS dice_stats (
            user_id INTEGER PRIMARY KEY, games_played INTEGER DEFAULT 0)''')
        db_ratings.execute('''CREATE TABLE IF NOT EXISTS dice_rewards_claimed (
            user_id INTEGER, milestone INTEGER, PRIMARY KEY (user_id, milestone))''')
        db_ratings.execute('''CREATE TABLE IF NOT EXISTS match_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER,
            role TEXT, won BOOLEAN, kills INTEGER DEFAULT 0,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')
        db_ratings.execute('''CREATE TABLE IF NOT EXISTS action_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER,
            action TEXT, icon TEXT DEFAULT '📌',
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')

    # ========== ПРЕДМЕТЫ ==========
    def add_item(self, user_id: int, item_id: str, quantity: int = 1) -> bool:
        if item_id not in ALL_ITEMS:
            return False
        db_ratings.execute(
            'INSERT INTO inventory VALUES (?,?,?) ON CONFLICT(user_id, item_id) DO UPDATE SET quantity = quantity + ?',
            (user_id, item_id, quantity, quantity))
        return True

    def remove_item(self, user_id: int, item_id: str, quantity: int = 1) -> bool:
        row = db_ratings.fetch_one('SELECT quantity FROM inventory WHERE user_id = ? AND item_id = ?', (user_id, item_id))
        if not row or row['quantity'] < quantity:
            return False
        if row['quantity'] == quantity:
            db_ratings.execute('DELETE FROM inventory WHERE user_id = ? AND item_id = ?', (user_id, item_id))
        else:
            db_ratings.execute('UPDATE inventory SET quantity = quantity - ? WHERE user_id = ? AND item_id = ?',
                               (quantity, user_id, item_id))
        return True

    def get_inventory(self, user_id: int) -> Dict[str, int]:
        rows = db_ratings.fetch_all('SELECT item_id, quantity FROM inventory WHERE user_id = ?', (user_id,))
        return {row['item_id']: row['quantity'] for row in rows}

    def get_item_count(self, user_id: int, item_id: str) -> int:
        return self.get_inventory(user_id).get(item_id, 0)

    def get_inventory_slots(self, user_id: int, level: int) -> Tuple[int, int]:
        inv = self.get_inventory(user_id)
        items_count = sum(inv.values())
        max_slots = 30 + (level - 1) * 2
        return items_count, max_slots

    # ========== СУНДУКИ ==========
    def get_available_chests(self, user_id: int) -> List[Dict]:
        inventory = self.get_inventory(user_id)
        from core.items.chests import CHESTS
        chests = []
        for item_id, qty in inventory.items():
            if item_id in CHESTS and qty > 0:
                chest = CHESTS[item_id].copy()
                chest["id"] = item_id
                chest["quantity"] = qty
                chests.append(chest)
        return chests

    def open_chest(self, user_id: int, chest_id: str) -> Optional[Dict]:
        from core.items.chests import CHESTS
        if chest_id not in CHESTS:
            return None
        chest = CHESTS[chest_id]
        rarity = chest["drop_rarity"]
        role_filter = chest.get("role_filter")
        count = self.get_item_count(user_id, chest_id)
        if count <= 0:
            return None

        available = [iid for iid, data in ALL_ITEMS.items()
                     if data.get("type") != "chest" and data.get("rarity") == rarity
                     and (not role_filter or data.get("role") in [role_filter, "all"])]
        if not available:
            return None

        if chest.get("special") == "multiple_cheese":
            cheese_items = [iid for iid in available if "cheese" in iid.lower()]
            if not cheese_items:
                cheese_items = available
            cnt = random.randint(3, 5)
            items_dropped = []
            for _ in range(cnt):
                if cheese_items:
                    dropped = random.choice(cheese_items)
                    self.add_item(user_id, dropped)
                    items_dropped.append(dropped)
            self.remove_item(user_id, chest_id, 1)
            self._add_chest_opened(user_id)
            return {"type": "multiple", "items": items_dropped, "chest_name": chest["name"]}

        dropped = random.choice(available)
        self.add_item(user_id, dropped)
        self.remove_item(user_id, chest_id, 1)
        self._add_chest_opened(user_id)
        return {"type": "single", "item_id": dropped, "item": ALL_ITEMS[dropped], "chest_name": chest["name"]}

    def _add_chest_opened(self, user_id: int):
        db_ratings.execute(
            '''INSERT INTO user_chest_stats (user_id, chests_opened) VALUES (?, 1)
               ON CONFLICT(user_id) DO UPDATE SET chests_opened = chests_opened + 1''', (user_id,))

    # ========== ЭКИПИРОВКА ==========
    def equip_item(self, user_id: int, item_id: str) -> bool:
        if item_id not in ALL_ITEMS:
            return False
        item = ALL_ITEMS[item_id]
        if item.get("type") != "equipment":
            return False
        slot = item.get("slot")
        if not slot:
            return False
        if self.get_item_count(user_id, item_id) <= 0:
            return False
        db_ratings.execute(
            'INSERT INTO equipment VALUES (?,?,?) ON CONFLICT(user_id, slot) DO UPDATE SET item_id = ?',
            (user_id, slot, item_id, item_id))
        return True

    def unequip_item(self, user_id: int, slot: str) -> bool:
        db_ratings.execute('DELETE FROM equipment WHERE user_id = ? AND slot = ?', (user_id, slot))
        return True

    def get_equipment(self, user_id: int) -> Dict[str, str]:
        rows = db_ratings.fetch_all('SELECT slot, item_id FROM equipment WHERE user_id = ?', (user_id,))
        return {row['slot']: row['item_id'] for row in rows}

    def get_equipped_effects(self, user_id: int, player_role: str) -> Dict:
        effects = {}
        equipment = self.get_equipment(user_id)
        for slot, item_id in equipment.items():
            if item_id in ALL_ITEMS:
                item = ALL_ITEMS[item_id]
                if item.get("role") in [player_role, "all"]:
                    for k, v in item.get("effect", {}).items():
                        if k in effects:
                            effects[k] = effects[k] or v if isinstance(v, bool) else effects[k] + v
                        else:
                            effects[k] = v
        return effects

    # ========== РАСХОДНИКИ ==========
    def use_consumable(self, user_id: int, item_id: str) -> bool:
        from core.items.consumables import CONSUMABLES
        if item_id not in CONSUMABLES:
            return False
        return self.remove_item(user_id, item_id, 1)

    # ========== ВАЛЮТА (через Database пул) ==========
    def get_crumbs(self, user_id: int) -> int:
        return db_ratings.get_crumbs(user_id)

    def add_crumbs(self, user_id: int, amount: int):
        db_ratings.add_crumbs(user_id, amount)

    def spend_crumbs(self, user_id: int, amount: int) -> bool:
        return db_ratings.spend_crumbs(user_id, amount)

    # ========== XP ==========
    def get_xp(self, user_id: int) -> int:
        return db_ratings.get_xp(user_id)

    def add_xp(self, user_id: int, amount: int) -> Tuple[bool, int, int]:
        old_xp = self.get_xp(user_id)
        old_level = self._get_level_from_xp(old_xp)
        db_ratings.add_xp(user_id, amount)
        new_xp = old_xp + amount
        new_level = self._get_level_from_xp(new_xp)
        return new_level > old_level, new_level, old_level

    def get_level(self, user_id: int) -> int:
        return self._get_level_from_xp(self.get_xp(user_id))

    @staticmethod
    def _get_level_from_xp(xp: int) -> int:
        if xp < 100:
            return 1
        return int((xp // 100) ** 0.5) + 1

    @staticmethod
    def get_xp_for_level(level: int) -> int:
        return ((level - 1) ** 2) * 100

    @staticmethod
    def get_level_progress(xp: int) -> Tuple[int, int, int]:
        level = InventoryService._get_level_from_xp(xp)
        current_level_xp = InventoryService.get_xp_for_level(level)
        next_level_xp = InventoryService.get_xp_for_level(level + 1)
        xp_in_level = xp - current_level_xp
        xp_needed = next_level_xp - current_level_xp
        return level, xp_in_level, xp_needed

    # ========== ВРЕМЕННЫЕ ЭФФЕКТЫ ==========
    def add_temp_effect(self, user_id: int, effect_data: dict, duration_hours: int = 1):
        expires_at = (datetime.now() + timedelta(hours=duration_hours)).strftime('%Y-%m-%d %H:%M:%S')
        db_ratings.execute(
            '''INSERT INTO user_temp_effects (user_id, effect_name, effect_value, effect_icon, effect_desc, expires_at)
               VALUES (?, ?, ?, ?, ?, ?)''',
            (user_id, effect_data['effect'], str(effect_data.get('value', 1)),
             effect_data.get('icon', '🍺'), effect_data.get('desc', ''), expires_at))

    def get_active_temp_effects(self, user_id: int) -> list:
        self._clean_expired_effects(user_id)
        rows = db_ratings.fetch_all(
            '''SELECT effect_name, effect_value, effect_icon, effect_desc,
               strftime('%Y-%m-%d %H:%M:%S', expires_at) as expires_at
               FROM user_temp_effects
               WHERE user_id = ? AND expires_at > datetime('now')
               ORDER BY expires_at''', (user_id,))
        effects = []
        for row in rows:
            val = row['effect_value']
            if val.isdigit():
                val = int(val)
            elif val.lower() == 'true':
                val = True
            elif val.lower() == 'false':
                val = False
            effects.append({'effect': row['effect_name'], 'value': val, 'icon': row['effect_icon'],
                            'desc': row['effect_desc'], 'expires_at': row['expires_at']})
        return effects

    def _clean_expired_effects(self, user_id: int = None):
        if user_id:
            db_ratings.execute('DELETE FROM user_temp_effects WHERE user_id = ? AND expires_at <= datetime("now")', (user_id,))
        else:
            db_ratings.execute('DELETE FROM user_temp_effects WHERE expires_at <= datetime("now")')

    # ========== ПИВО ==========
    def add_beer(self, user_id: int):
        db_ratings.execute(
            '''INSERT INTO user_beer_stats (user_id, beer_count) VALUES (?, 1)
               ON CONFLICT(user_id) DO UPDATE SET beer_count = beer_count + 1''', (user_id,))

    def get_beer_count(self, user_id: int) -> int:
        row = db_ratings.fetch_one('SELECT beer_count FROM user_beer_stats WHERE user_id = ?', (user_id,))
        return row['beer_count'] if row else 0

    # ========== ДАЙС-СТАТЫ ==========
    def add_dice_game(self, user_id: int):
        db_ratings.execute(
            '''INSERT INTO dice_stats (user_id, games_played) VALUES (?, 1)
               ON CONFLICT(user_id) DO UPDATE SET games_played = games_played + 1''', (user_id,))

    def get_dice_games(self, user_id: int) -> int:
        row = db_ratings.fetch_one('SELECT games_played FROM dice_stats WHERE user_id = ?', (user_id,))
        return row['games_played'] if row else 0

    def add_dice_win(self, user_id: int):
        db_ratings.execute(
            '''INSERT INTO user_dice_wins (user_id, dice_wins) VALUES (?, 1)
               ON CONFLICT(user_id) DO UPDATE SET dice_wins = dice_wins + 1''', (user_id,))

    def check_dice_reward(self, user_id: int) -> Optional[str]:
        games = self.get_dice_games(user_id)
        milestones = {10: "common", 25: "rare", 50: "epic", 100: "legendary", 250: "mythic"}
        for milestone, rarity in milestones.items():
            if games >= milestone:
                row = db_ratings.fetch_one(
                    'SELECT 1 FROM dice_rewards_claimed WHERE user_id = ? AND milestone = ?', (user_id, milestone))
                if not row:
                    db_ratings.execute(
                        'INSERT INTO dice_rewards_claimed (user_id, milestone) VALUES (?, ?)', (user_id, milestone))
                    return rarity
        return None

    # ========== СТАТИСТИКА ==========
    def update_stats(self, user_id: int, **kwargs):
        row = db_ratings.fetch_one('SELECT user_id FROM user_stats WHERE user_id = ?', (user_id,))
        if not row:
            fields = ["user_id"] + list(kwargs.keys())
            values = [user_id] + list(kwargs.values())
            placeholders = ','.join(['?'] * len(fields))
            db_ratings.execute(f"INSERT INTO user_stats ({','.join(fields)}) VALUES ({placeholders})", tuple(values))
        else:
            updates = [f"{k} = COALESCE({k}, 0) + ?" for k in kwargs.keys()]
            values = list(kwargs.values()) + [user_id]
            db_ratings.execute(f"UPDATE user_stats SET {','.join(updates)} WHERE user_id = ?", tuple(values))

    # ========== МАТЧ-ИСТОРИЯ ==========
    def add_match_record(self, user_id: int, role: str, won: bool, kills: int = 0):
        db_ratings.execute('INSERT INTO match_history (user_id, role, won, kills) VALUES (?, ?, ?, ?)',
                           (user_id, role, won, kills))

    # ========== ИСТОРИЯ ДЕЙСТВИЙ ==========
    def add_action_history(self, user_id: int, action: str, icon: str = "📌"):
        try:
            count_row = db_ratings.fetch_one('SELECT COUNT(*) as cnt FROM action_history WHERE user_id = ?', (user_id,))
            if count_row and count_row['cnt'] >= 50:
                db_ratings.execute(
                    'DELETE FROM action_history WHERE id = (SELECT MIN(id) FROM action_history WHERE user_id = ?)', (user_id,))
            db_ratings.execute('INSERT INTO action_history (user_id, action, icon) VALUES (?, ?, ?)',
                               (user_id, action, icon))
        except:
            pass

    def get_action_history(self, user_id: int, limit: int = 10) -> list:
        try:
            return db_ratings.fetch_all(
                'SELECT action, icon, timestamp FROM action_history WHERE user_id = ? ORDER BY id DESC LIMIT ?',
                (user_id, limit))
        except:
            return []

    # ========== СЛУЧАЙНЫЕ ПРЕДМЕТЫ ==========
    def get_random_item(self, winner_role: str) -> Optional[str]:
        role_filter = "rat" if winner_role == "rat" else "mouse"
        available = [(iid, data["rarity"]) for iid, data in ALL_ITEMS.items()
                     if data.get("type") != "chest" and data.get("role") in [role_filter, "all"]]
        if not available:
            return None
        rand = random.randint(1, 100)
        cum = 0
        for iid, rar in available:
            cum += DROP_CHANCES.get(rar, 10)
            if rand <= cum:
                return iid
        return available[0][0]

    def get_random_item_by_rarity(self, rarity: str) -> Optional[str]:
        available = [iid for iid, data in ALL_ITEMS.items()
                     if data.get("rarity") == rarity and data.get("type") != "chest"]
        return random.choice(available) if available else None


# Глобальный экземпляр
inventory_service = InventoryService()
inventory_service.init_db()