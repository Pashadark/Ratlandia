"""Система крафта — ТОЛЬКО механика: броски, качество, сложность"""

import random
import sqlite3
from typing import Optional, Dict, List, Tuple
from enum import Enum

DB_FILE = "/root/bot/ratings.db"


class CraftQuality(Enum):
    TERRIBLE = ("ужасный", "💩", 0.5)
    POOR = ("плохой", "🟤", 0.7)
    NORMAL = ("обычный", "⚪", 1.0)
    GOOD = ("хороший", "🟢", 1.2)
    EXCELLENT = ("отличный", "🔵", 1.5)
    FLAWLESS = ("безупречный", "🟣", 2.0)
    MASTERFUL = ("мастерский", "🟡", 3.0)
    LEGENDARY = ("легендарный", "🟠", 5.0)
    DIVINE = ("божественный", "🔴", 10.0)
    
    def __init__(self, display: str, color: str, multiplier: float):
        self.display = display
        self.color = color
        self.multiplier = multiplier


CRAFT_DIFFICULTY = {
    "common":    {"min_roll": 3,  "fail_desc": "2",       "crit_roll": 12},
    "rare":      {"min_roll": 5,  "fail_desc": "2-3",     "crit_roll": 12},
    "epic":      {"min_roll": 7,  "fail_desc": "2-4",     "crit_roll": 11},
    "legendary": {"min_roll": 9,  "fail_desc": "2-5",     "crit_roll": 12},
    "mythic":    {"min_roll": 11, "fail_desc": "2-6",     "crit_roll": 12},
}


def roll_craft_dice() -> int:
    """Бросок двух кубиков для крафта (2-12)"""
    return random.randint(1, 6) + random.randint(1, 6)


def check_craft_success(dice_sum: int, rarity: str) -> Tuple[bool, str]:
    """Проверяет успех крафта. Возвращает (успех, причина_провала)"""
    diff = CRAFT_DIFFICULTY.get(rarity, CRAFT_DIFFICULTY["common"])
    if dice_sum < diff["min_roll"]:
        return False, f"Нужно {diff['min_roll']}+, выброшено {dice_sum}"
    return True, ""


def check_craft_critical(dice_sum: int, rarity: str) -> bool:
    """Проверяет критический успех"""
    diff = CRAFT_DIFFICULTY.get(rarity, CRAFT_DIFFICULTY["common"])
    return dice_sum >= diff["crit_roll"]


def get_quality_from_roll(dice_sum: int) -> Tuple[CraftQuality, Dict[str, int]]:
    """Определяет качество и бонусы по сумме кубиков"""
    if dice_sum >= 18:       return CraftQuality.DIVINE, {"all_stats": 5, "max_health": 30}
    elif dice_sum >= 16:     return CraftQuality.LEGENDARY, {"all_stats": 3, "max_health": 20}
    elif dice_sum >= 14:     return CraftQuality.MASTERFUL, {"all_stats": 2, "max_health": 15}
    elif dice_sum >= 12:     return CraftQuality.FLAWLESS, {"all_stats": 2, "max_health": 10}
    elif dice_sum >= 10:     return CraftQuality.EXCELLENT, {"all_stats": 1, "max_health": 5}
    elif dice_sum >= 8:      return CraftQuality.GOOD, {"intelligence": 1}
    elif dice_sum >= 6:      return CraftQuality.NORMAL, {}
    elif dice_sum >= 4:      return CraftQuality.POOR, {}
    else:                    return CraftQuality.TERRIBLE, {}


def has_materials(user_id: int, materials: Dict[str, int]) -> bool:
    """Проверяет есть ли все материалы"""
    with sqlite3.connect(DB_FILE) as conn:
        c = conn.cursor()
        for mat_id, qty in materials.items():
            c.execute('SELECT quantity FROM inventory WHERE user_id = ? AND item_id = ?',
                      (user_id, mat_id))
            row = c.fetchone()
            if not row or row[0] < qty:
                return False
    return True


def spend_materials(user_id: int, materials: Dict[str, int]) -> bool:
    """Списывает материалы"""
    try:
        with sqlite3.connect(DB_FILE) as conn:
            c = conn.cursor()
            for mat_id, qty in materials.items():
                c.execute('UPDATE inventory SET quantity = quantity - ? WHERE user_id = ? AND item_id = ?',
                          (qty, user_id, mat_id))
            conn.commit()
        return True
    except:
        return False


def get_player_resources(user_id: int) -> Dict[str, int]:
    """Возвращает все ресурсы И рецепты игрока"""
    resources = {}
    with sqlite3.connect(DB_FILE) as conn:
        c = conn.cursor()
        c.execute('SELECT item_id, quantity FROM inventory WHERE user_id = ? AND quantity > 0', (user_id,))
        for row in c.fetchall():
            item_id = row[0]
            qty = row[1]
            # Ресурсы (есть в RESOURCE_IDS) ИЛИ рецепты (начинаются с recipe_)
            if item_id in RESOURCE_IDS or item_id.startswith('recipe_'):
                resources[item_id] = qty
    return resources


# Список ID всех ресурсов
RESOURCE_IDS = {
    "copper_scrap", "bronze_alloy", "iron_gear", "steel_shard", "silver_ingot",
    "emerald_crumb", "obsidian_scale", "mithril_nugget", "adamantite", "rat_god_tooth",
    "rat_pelt", "linen_scrap", "wool_clump", "leather_scrap", "spider_silk",
    "bat_membrane", "snake_skin", "moon_silk", "cat_pelt", "star_silk",
    "mouse_bone", "rat_incisor", "fish_spine", "mole_skull", "crow_bone",
    "rat_tail_vertebra", "bat_fang", "rat_king_eye", "first_rat_skull", "labyrinth_heart",
    "moldy_crumb", "basement_mushroom", "empty_vial", "rat_poison", "rat_king_tear",
    "wall_soot", "mandrake", "ancient_scrap", "void_essence", "spark_creation",
    "cheese_crust", "bread_crumb", "clean_water", "smoked_lard", "honey_drop",
    "underground_truffle", "marrow_bone", "forgotten_ale",
    "blueprint_cheese_slicer", "blueprint_poison_blade", "blueprint_gambeson",
    "blueprint_invisibility_cloak", "blueprint_explosive_vial", "blueprint_crown",
    "wrinkled_card", "smooth_pebble", "surface_shell", "human_coin", "tiny_matryoshka",
    "ancient_amulet", "tapestry_scrap",
    "fairy_dust", "moon_dew", "mage_blood", "phoenix_ember", "ice_worm_tear", "storm_spark",
    "stone_shard", "spider_web", "pigeon_feather", "candle_stub",
    "cloudy_crystal", "mirror_shard", "magnetic_stone", "hermit_rosary",
    "gate_key", "labyrinth_seal", "recipe_cheese_sword", "recipe_leather_vest", "recipe_gambeson",
    "recipe_rat_dagger", "recipe_viking_helmet", "recipe_chainmail",
    "recipe_crossbow", "recipe_butcher_knife", "recipe_invisibility_cloak",
    "recipe_crown_of_rat_king", "recipe_crown_of_mouse_king",
    "recipe_poison_cheese", "recipe_smoke_bomb",
}


def save_crafted_item(user_id: int, item_id: str, quality: str, dice_sum: int,
                      bonuses: dict, crafter_name: str) -> int:
    """Сохраняет созданный предмет в БД"""
    with sqlite3.connect(DB_FILE) as conn:
        c = conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS crafted_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER, original_owner INTEGER, item_id TEXT,
            quality TEXT, dice_sum INTEGER,
            bonus_strength INTEGER DEFAULT 0, bonus_agility INTEGER DEFAULT 0,
            bonus_intelligence INTEGER DEFAULT 0, bonus_health INTEGER DEFAULT 0,
            bonus_all_stats INTEGER DEFAULT 0,
            crafted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP, crafter_name TEXT)''')
        c.execute('''INSERT INTO crafted_items 
                     (user_id, original_owner, item_id, quality, dice_sum,
                      bonus_strength, bonus_agility, bonus_intelligence, 
                      bonus_health, bonus_all_stats, crafter_name)
                     VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                  (user_id, user_id, item_id, quality, dice_sum,
                   bonuses.get('strength', 0), bonuses.get('agility', 0),
                   bonuses.get('intelligence', 0), bonuses.get('max_health', 0),
                   bonuses.get('all_stats', 0), crafter_name))
        conn.commit()
        return c.lastrowid


def get_craft_difficulty_info(rarity: str) -> dict:
    """Возвращает инфу о сложности для отображения"""
    return CRAFT_DIFFICULTY.get(rarity, CRAFT_DIFFICULTY["common"])