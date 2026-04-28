"""Эффекты и благословения для режима Туннелей"""

import random
from typing import Dict, List, Any

# ========== БЛАГОСЛОВЕНИЯ АЛТАРЯ ==========
ALTAR_BLESSINGS = [
    # Боевые
    {
        "id": "damage_boost",
        "name": "💪 Благословение силы",
        "desc": "+1 к урону до конца забега",
        "effect": "damage",
        "value": 1,
        "duration": "run",
        "icon": "💪"
    },
    {
        "id": "crit_blessing",
        "name": "💥 Благословение крита",
        "desc": "+15% шанс критического удара",
        "effect": "crit_chance",
        "value": 15,
        "duration": "run",
        "icon": "💥"
    },
    {
        "id": "vampirism_blessing",
        "name": "🦇 Благословение вампира",
        "desc": "Восстанавливаешь 1 HP при ударе",
        "effect": "vampirism",
        "value": 1,
        "duration": "run",
        "icon": "🦇"
    },
    {
        "id": "double_strike",
        "name": "⚡ Благословение скорости",
        "desc": "10% шанс атаковать дважды",
        "effect": "double_attack_chance",
        "value": 10,
        "duration": "run",
        "icon": "⚡"
    },
    
    # Защитные
    {
        "id": "health_boost",
        "name": "❤️ Благословение жизни",
        "desc": "+15 к максимальному здоровью",
        "effect": "max_health",
        "value": 15,
        "duration": "run",
        "icon": "❤️"
    },
    {
        "id": "dodge_boost",
        "name": "🍀 Благословение ловкости",
        "desc": "+10% к шансу уклонения",
        "effect": "dodge",
        "value": 10,
        "duration": "run",
        "icon": "🍀"
    },
    {
        "id": "shield_blessing",
        "name": "🛡️ Благословение щита",
        "desc": "Блокирует первую атаку врага",
        "effect": "shield",
        "value": 1,
        "duration": "run",
        "icon": "🛡️"
    },
    {
        "id": "regen_blessing",
        "name": "✨ Благословение регенерации",
        "desc": "+1 HP каждый ход",
        "effect": "regen",
        "value": 1,
        "duration": "run",
        "icon": "✨"
    },
    {
        "id": "thorns_blessing",
        "name": "🌵 Благословение шипов",
        "desc": "Враг получает 2 урона при атаке",
        "effect": "thorns",
        "value": 2,
        "duration": "run",
        "icon": "🌵"
    },
    
    # Удачные
    {
        "id": "find_boost",
        "name": "🔍 Благословение поиска",
        "desc": "+15% к шансу найти тайник",
        "effect": "find_chance",
        "value": 15,
        "duration": "run",
        "icon": "🔍"
    },
    {
        "id": "crumbs_boost",
        "name": "🧀 Благословение изобилия",
        "desc": "+50% крошек с монстров",
        "effect": "crumbs_multiplier",
        "value": 1.5,
        "duration": "run",
        "icon": "🧀"
    },
    {
        "id": "xp_boost",
        "name": "⭐ Благословение мудрости",
        "desc": "+50% опыта с монстров",
        "effect": "xp_multiplier",
        "value": 1.5,
        "duration": "run",
        "icon": "⭐"
    },
    {
        "id": "lucky_blessing",
        "name": "🎲 Благословение удачи",
        "desc": "+10% ко всем шансам",
        "effect": "all_chances",
        "value": 10,
        "duration": "run",
        "icon": "🎲"
    },
    
    # Мгновенные (не сохраняются в run_data)
    {
        "id": "instant_heal",
        "name": "💚 Мгновенное исцеление",
        "desc": "Восстанавливает 30 HP",
        "effect": "instant_heal",
        "value": 30,
        "duration": "instant",
        "icon": "💚"
    },
    {
        "id": "full_heal",
        "name": "🌟 Полное исцеление",
        "desc": "Восстанавливает всё здоровье",
        "effect": "full_heal",
        "value": 100,
        "duration": "instant",
        "icon": "🌟"
    },
    {
        "id": "stat_point",
        "name": "🎯 Дар мудрости",
        "desc": "+1 очко характеристик",
        "effect": "stat_point",
        "value": 1,
        "duration": "instant",
        "icon": "🎯"
    },
    {
        "id": "free_reroll",
        "name": "🔄 Дар перемен",
        "desc": "+1 бесплатная смена комнаты",
        "effect": "free_reroll",
        "value": 1,
        "duration": "instant",
        "icon": "🔄"
    },
]


# ========== ЭФФЕКТЫ ЗЕЛИЙ ==========
POTION_EFFECTS = {
    "health_potion": {
        "name": "Зелье здоровья",
        "effect": "heal",
        "value": 30,
        "icon": "🧪"
    },
    "strength_potion": {
        "name": "Зелье силы",
        "effect": "temp_damage",
        "value": 2,
        "duration": 3,
        "icon": "💪"
    },
    "dodge_potion": {
        "name": "Зелье ловкости",
        "effect": "temp_dodge",
        "value": 20,
        "duration": 3,
        "icon": "🍀"
    },
    "invisibility_potion": {
        "name": "Зелье невидимости",
        "effect": "invisible",
        "value": 1,
        "duration": 1,
        "icon": "👻"
    },
}


# ========== ЭФФЕКТЫ ПРОКЛЯТИЙ (ЛОВУШКИ/СУНДУКИ) ==========
CURSE_EFFECTS = [
    {"name": "Проклятие слабости", "effect": "temp_weaken", "value": 1, "duration": 2, "icon": "⬇️"},
    {"name": "Проклятие уязвимости", "effect": "temp_vulnerable", "value": 2, "duration": 2, "icon": "💔"},
    {"name": "Проклятие замедления", "effect": "temp_slow", "value": 1, "duration": 2, "icon": "🐌"},
    {"name": "Проклятие потери", "effect": "lose_crumbs", "value": 10, "duration": "instant", "icon": "🧀"},
]


# ========== ФУНКЦИИ ДЛЯ РАБОТЫ С ЭФФЕКТАМИ ==========

def get_random_blessing() -> Dict:
    """Возвращает случайное благословение алтаря"""
    return random.choice(ALTAR_BLESSINGS).copy()


def get_blessing_by_id(blessing_id: str) -> Dict:
    """Возвращает благословение по ID"""
    for blessing in ALTAR_BLESSINGS:
        if blessing["id"] == blessing_id:
            return blessing.copy()
    return None


def get_all_blessings() -> List[Dict]:
    """Возвращает список всех благословений"""
    return ALTAR_BLESSINGS.copy()


def apply_blessing_effect(user_id: int, blessing: Dict, run_data: Dict) -> tuple:
    """
    Применяет эффект благословения.
    Возвращает (текст_результата, нужно_обновить_здоровье, новое_здоровье)
    """
    from handlers.character import get_character_stats, heal_damage, update_character_stats
    from handlers.tunnel_monsters import update_tunnel_run
    import sqlite3
    
    effect = blessing["effect"]
    value = blessing["value"]
    duration = blessing.get("duration", "run")
    
    stats = get_character_stats(user_id)
    new_hp = None
    update_health = False
    
    if duration == "instant":
        # Мгновенные эффекты
        if effect == "instant_heal":
            new_hp = heal_damage(user_id, value)
            update_health = True
            return f"❤️ Восстановлено {value} здоровья!", True, new_hp
        
        elif effect == "full_heal":
            max_hp = stats['max_health']
            new_hp = heal_damage(user_id, max_hp)
            update_health = True
            return f"🌟 Здоровье полностью восстановлено!", True, new_hp
        
        elif effect == "stat_point":
            update_character_stats(user_id, stat_points=stats['stat_points'] + value)
            return f"🎯 Получено {value} очко характеристик!", False, None
        
        elif effect == "free_reroll":
            DB_FILE = "/root/bot/ratings.db"
            with sqlite3.connect(DB_FILE) as conn:
                c = conn.cursor()
                c.execute('UPDATE tunnel_stats SET free_rerolls = COALESCE(free_rerolls, 0) + ? WHERE user_id = ?', 
                          (value, user_id))
                conn.commit()
            return f"🔄 Получена бесплатная смена комнаты!", False, None
    
    else:
        # Эффекты на весь забег — сохраняем в run_data
        current_blessings = run_data.get("blessings", [])
        if not isinstance(current_blessings, list):
            current_blessings = []
        
        # Проверяем, нет ли уже такого же эффекта
        for b in current_blessings:
            if b.get("effect") == effect:
                # Увеличиваем значение
                b["value"] = b.get("value", 0) + value
                update_tunnel_run(user_id, blessings=current_blessings)
                return f"{blessing['icon']} Эффект усилен! {blessing['desc']}", False, None
        
        current_blessings.append(blessing)
        update_tunnel_run(user_id, blessings=current_blessings)
        
        # Особые эффекты, влияющие на здоровье
        if effect == "max_health":
            new_max = stats['max_health'] + value
            new_current = stats['current_health'] + value
            update_character_stats(user_id, max_health=new_max, current_health=new_current)
            update_health = True
            new_hp = new_current
        
        return blessing["desc"], update_health, new_hp
    
    return blessing["desc"], False, None


def get_active_blessings(run_data: Dict) -> List[Dict]:
    """Возвращает список активных благословений из забега"""
    if not run_data:
        return []
    blessings = run_data.get("blessings", [])
    if isinstance(blessings, list):
        return blessings
    return []


def format_blessings_text(blessings: List[Dict]) -> str:
    """Форматирует список благословений для отображения"""
    if not blessings:
        return "  ✨ Нет активных благословений"
    
    text = ""
    for b in blessings:
        text += f"  {b['icon']} {b['name']}: {b['desc']}\n"
    return text.strip()


def calculate_damage_with_blessings(base_damage: int, blessings: List[Dict]) -> tuple:
    """Рассчитывает урон с учётом благословений"""
    damage = base_damage
    crit = False
    double = False
    vampirism = 0
    
    for b in blessings:
        if b["effect"] == "damage":
            damage += b["value"]
        elif b["effect"] == "crit_chance":
            if random.randint(1, 100) <= b["value"]:
                damage *= 2
                crit = True
        elif b["effect"] == "double_attack_chance":
            if random.randint(1, 100) <= b["value"]:
                double = True
        elif b["effect"] == "vampirism":
            vampirism = b["value"]
    
    return damage, crit, double, vampirism


def calculate_dodge_with_blessings(base_dodge: int, blessings: List[Dict]) -> int:
    """Рассчитывает шанс уклонения с учётом благословений"""
    dodge = base_dodge
    for b in blessings:
        if b["effect"] == "dodge":
            dodge += b["value"]
        elif b["effect"] == "all_chances":
            dodge += b["value"]
    return min(90, dodge)


def calculate_find_with_blessings(base_find: int, blessings: List[Dict]) -> int:
    """Рассчитывает шанс находки с учётом благословений"""
    find = base_find
    for b in blessings:
        if b["effect"] == "find_chance":
            find += b["value"]
        elif b["effect"] == "all_chances":
            find += b["value"]
    return min(90, find)


def apply_thorns(blessings: List[Dict]) -> int:
    """Возвращает урон от шипов"""
    for b in blessings:
        if b["effect"] == "thorns":
            return b["value"]
    return 0


def has_shield(blessings: List[Dict]) -> bool:
    """Проверяет наличие щита"""
    for b in blessings:
        if b["effect"] == "shield":
            return True
    return False


def get_regen_amount(blessings: List[Dict]) -> int:
    """Возвращает количество регенерации за ход"""
    for b in blessings:
        if b["effect"] == "regen":
            return b["value"]
    return 0


def get_crumbs_multiplier(blessings: List[Dict]) -> float:
    """Возвращает множитель крошек"""
    multiplier = 1.0
    for b in blessings:
        if b["effect"] == "crumbs_multiplier":
            multiplier *= b["value"]
    return multiplier


def get_xp_multiplier(blessings: List[Dict]) -> float:
    """Возвращает множитель опыта"""
    multiplier = 1.0
    for b in blessings:
        if b["effect"] == "xp_multiplier":
            multiplier *= b["value"]
    return multiplier


# ========== ДОБАВИТЬ КОЛОНКУ В БД ==========
# ALTER TABLE tunnel_run ADD COLUMN blessings TEXT;