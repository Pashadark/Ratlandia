"""core/restore.py — пассивное восстановление здоровья и маны"""
from datetime import datetime
from core.database import db_ratings
from typing import Tuple

# Базовые скорости (HP/час, MP/час)
BASE_HP_RATE = 10
BASE_MP_RATE = 5

# Множители
CHURCH_BLESSING_MULTIPLIER = 2.0      # x2
BEER_MULTIPLIER = 1.5                  # +50%
REGEN_AMULET_BONUS = 10               # +10 HP/час
SLEEP_MULTIPLIER = 2.5                # офлайн > 4ч


def _get_bonus_multiplier(user_id: int) -> float:
    mult = 1.0
    # Проверяем временные эффекты
    effects = db_ratings.fetch_all(
        "SELECT effect_name FROM user_temp_effects WHERE user_id = ? AND expires_at > datetime('now')",
        (user_id,)
    )
    for e in effects:
        if e['effect_name'] == 'church_blessing':
            mult *= CHURCH_BLESSING_MULTIPLIER
        elif e['effect_name'] in ('tunnel_damage', 'tunnel_find', 'max_health', 'dodge'):
            mult *= BEER_MULTIPLIER
    
    # Проверяем экипировку (амулет регенерации)
    equip = db_ratings.fetch_all(
        "SELECT item_id FROM equipment WHERE user_id = ? AND slot = 'accessory'",
        (user_id,)
    )
    for eq in equip:
        if eq['item_id'] == 'ring_of_regeneration':
            mult += REGEN_AMULET_BONUS / BASE_HP_RATE
    
    return mult


def _get_last_active_time(user_id: int) -> datetime:
    """Время последней активности (может быть в user_stats или логах)"""
    row = db_ratings.fetch_one(
        "SELECT last_health_update FROM user_stats WHERE user_id = ?",
        (user_id,)
    )
    if row and row['last_health_update']:
        try:
            return datetime.fromisoformat(row['last_health_update'])
        except:
            pass
    return datetime.now()


def get_current_hp(user_id: int) -> int:
    """Получить актуальное HP с пассивным восстановлением"""
    row = db_ratings.fetch_one(
        "SELECT current_health, max_health, last_health_update FROM user_stats WHERE user_id = ?",
        (user_id,)
    )
    if not row:
        return 50
    
    current = row['current_health'] or 0
    max_hp = row['max_health'] or 50
    
    if current >= max_hp:
        return max_hp
    
    last_update = row['last_health_update']
    if not last_update:
        return current
    
    try:
        last_time = datetime.fromisoformat(last_update)
        hours_passed = (datetime.now() - last_time).total_seconds() / 3600
        
        if hours_passed > 0:
            mult = _get_bonus_multiplier(user_id)
            
            # Сон (офлайн > 4 часов)
            if hours_passed >= 4:
                mult *= SLEEP_MULTIPLIER
            
            rate = BASE_HP_RATE * mult
            healed = min(int(rate * hours_passed), max_hp - current)
            
            if healed > 0:
                new_hp = current + healed
                db_ratings.execute(
                    "UPDATE user_stats SET current_health = ?, last_health_update = ? WHERE user_id = ?",
                    (new_hp, datetime.now().isoformat(), user_id)
                )
                return new_hp
    except:
        pass
    
    return current


def get_current_mana(user_id: int) -> int:
    """Получить актуальную ману с пассивным восстановлением"""
    row = db_ratings.fetch_one(
        "SELECT mana, max_mana, last_health_update FROM user_stats WHERE user_id = ?",
        (user_id,)
    )
    if not row:
        return 0
    
    current = row['mana'] or 0
    max_mana = row['max_mana'] or 0
    
    if max_mana == 0 or current >= max_mana:
        return current if max_mana > 0 else 0
    
    last_update = row['last_health_update']
    if not last_update:
        return current
    
    try:
        last_time = datetime.fromisoformat(last_update)
        hours_passed = (datetime.now() - last_time).total_seconds() / 3600
        
        if hours_passed > 0:
            mult = _get_bonus_multiplier(user_id)
            rate = BASE_MP_RATE * mult
            restored = min(int(rate * hours_passed), max_mana - current)
            
            if restored > 0:
                new_mana = current + restored
                db_ratings.execute(
                    "UPDATE user_stats SET mana = ? WHERE user_id = ?",
                    (new_mana, user_id)
                )
                return new_mana
    except:
        pass
    
    return current


def get_hp_restore_info(user_id: int) -> Tuple[int, int, float]:
    """
    Возвращает (текущее HP, макс HP, часов до полного восстановления)
    """
    row = db_ratings.fetch_one(
        "SELECT current_health, max_health FROM user_stats WHERE user_id = ?",
        (user_id,)
    )
    if not row:
        return 50, 50, 0
    
    current = row['current_health'] or 0
    max_hp = row['max_health'] or 50
    
    if current >= max_hp:
        return max_hp, max_hp, 0
    
    mult = _get_bonus_multiplier(user_id)
    rate = BASE_HP_RATE * mult
    hours_needed = (max_hp - current) / rate
    
    return current, max_hp, hours_needed


def get_mana_restore_info(user_id: int) -> Tuple[int, int, float]:
    """(текущая мана, макс мана, часов до полного восстановления)"""
    row = db_ratings.fetch_one(
        "SELECT mana, max_mana FROM user_stats WHERE user_id = ?",
        (user_id,)
    )
    if not row:
        return 0, 0, 0
    
    current = row['mana'] or 0
    max_mana = row['max_mana'] or 0
    
    if max_mana == 0 or current >= max_mana:
        return current, max_mana, 0
    
    mult = _get_bonus_multiplier(user_id)
    rate = BASE_MP_RATE * mult
    hours_needed = (max_mana - current) / rate
    
    return current, max_mana, hours_needed


def take_damage(user_id: int, damage: int) -> int:
    """Нанести урон"""
    hp = get_current_hp(user_id)
    new_hp = max(0, hp - damage)
    db_ratings.execute(
        "UPDATE user_stats SET current_health = ?, last_health_update = ? WHERE user_id = ?",
        (new_hp, datetime.now().isoformat(), user_id)
    )
    return new_hp


def heal_damage(user_id: int, amount: int) -> int:
    """Мгновенное лечение"""
    row = db_ratings.fetch_one(
        "SELECT current_health, max_health FROM user_stats WHERE user_id = ?",
        (user_id,)
    )
    if not row:
        return 50
    new_hp = min(row['max_health'] or 50, (row['current_health'] or 0) + amount)
    db_ratings.execute(
        "UPDATE user_stats SET current_health = ?, last_health_update = ? WHERE user_id = ?",
        (new_hp, datetime.now().isoformat(), user_id)
    )
    return new_hp


def use_mana(user_id: int, amount: int) -> int:
    """Потратить ману"""
    mana = get_current_mana(user_id)
    new_mana = max(0, mana - amount)
    db_ratings.execute(
        "UPDATE user_stats SET mana = ? WHERE user_id = ?",
        (new_mana, user_id)
    )
    return new_mana


def restore_mana(user_id: int, amount: int) -> int:
    """Восстановить ману"""
    row = db_ratings.fetch_one(
        "SELECT mana, max_mana FROM user_stats WHERE user_id = ?",
        (user_id,)
    )
    if not row:
        return 0
    new_mana = min(row['max_mana'] or 0, (row['mana'] or 0) + amount)
    db_ratings.execute(
        "UPDATE user_stats SET mana = ? WHERE user_id = ?",
        (new_mana, user_id)
    )
    return new_mana