"""Система пассивного восстановления здоровья — Ratlandia Healing System v4.0 Final"""

import sqlite3
import logging
from datetime import datetime, timedelta
from typing import Tuple

from handlers.character import get_character_stats, heal_damage

logger = logging.getLogger(__name__)
DB_FILE = "/root/bot/ratings.db"

# ═══════════════════════════════════════
# КОНСТАНТЫ
# ═══════════════════════════════════════
HP_PER_HOUR = 10           # Базовое лечение: 10 HP/час
HP_PER_HOUR_CHURCH = 20    # В церкви: 20 HP/час


def _get_last_update(user_id: int) -> datetime:
    """Когда последний раз обновляли HP"""
    try:
        with sqlite3.connect(DB_FILE) as conn:
            c = conn.cursor()
            c.execute('''CREATE TABLE IF NOT EXISTS user_settings 
                         (user_id INTEGER, key TEXT, value TEXT, 
                          PRIMARY KEY (user_id, key))''')
            conn.commit()
            c.execute('''SELECT value FROM user_settings 
                         WHERE user_id = ? AND key = 'last_hp_update' ''', (user_id,))
            row = c.fetchone()
            if row:
                return datetime.fromisoformat(row[0])
    except:
        pass
    return datetime.now()


def _set_last_update(user_id: int, time: datetime):
    """Сохраняет время последнего обновления HP"""
    try:
        with sqlite3.connect(DB_FILE) as conn:
            c = conn.cursor()
            c.execute('''CREATE TABLE IF NOT EXISTS user_settings 
                         (user_id INTEGER, key TEXT, value TEXT, 
                          PRIMARY KEY (user_id, key))''')
            c.execute('''INSERT OR REPLACE INTO user_settings (user_id, key, value) 
                         VALUES (?, 'last_hp_update', ?)''', 
                      (user_id, time.isoformat()))
            conn.commit()
    except Exception as e:
        logger.error(f"Ошибка сохранения времени: {e}")


def _get_equipment_regen(user_id: int) -> int:
    """Считает бонус к регенерации от надетой экипировки"""
    try:
        from handlers.inventory import get_equipment
        from handlers.items import EQUIPMENT
        equipment = get_equipment(user_id)
        regen_bonus = 0
        for slot, item_id in equipment.items():
            if item_id in EQUIPMENT:
                item = EQUIPMENT[item_id]
                regen_bonus += item.get("effect", {}).get("regen", 0)
        return regen_bonus
    except:
        return 0


def restore_health_over_time(user_id: int, context=None) -> tuple:
    """
    Пассивное лечение: 10 HP/час + бонус от экипировки.
    Вызывается при ЛЮБОМ действии игрока.
    """
    stats = get_character_stats(user_id)
    current_hp = stats['current_health']
    max_hp = stats['max_health']
    
    if current_hp >= max_hp:
        return 0, current_hp, max_hp
    
    last_update = _get_last_update(user_id)
    now = datetime.now()
    hours_passed = (now - last_update).total_seconds() / 3600
    
    if hours_passed < 0.01:
        return 0, current_hp, max_hp
    
    # Базовое лечение + бонус от экипировки
    equipment_bonus = _get_equipment_regen(user_id)
    total_hp_per_hour = HP_PER_HOUR + equipment_bonus
    
    heal_amount = int(total_hp_per_hour * hours_passed)
    
    if heal_amount <= 0:
        return 0, current_hp, max_hp
    
    heal_amount = min(heal_amount, max_hp - current_hp)
    new_hp = current_hp + heal_amount
    
    heal_damage(user_id, -heal_amount)
    _set_last_update(user_id, now)
    
    logger.info(f"💤 +{heal_amount} HP для user={user_id} ({total_hp_per_hour} HP/ч, прошло {hours_passed:.1f}ч)")
    
    return heal_amount, new_hp, max_hp


def restore_health_in_church(user_id: int, context=None) -> tuple:
    """Лечение в церкви: 20 HP/час + бонус от экипировки."""
    stats = get_character_stats(user_id)
    current_hp = stats['current_health']
    max_hp = stats['max_health']
    
    if current_hp >= max_hp:
        return 0, current_hp, max_hp
    
    last_update = _get_last_update(user_id)
    now = datetime.now()
    hours_passed = (now - last_update).total_seconds() / 3600
    
    equipment_bonus = _get_equipment_regen(user_id)
    total_hp_per_hour = HP_PER_HOUR_CHURCH + equipment_bonus
    
    heal_amount = int(total_hp_per_hour * hours_passed)
    
    if heal_amount <= 0:
        return 0, current_hp, max_hp
    
    heal_amount = min(heal_amount, max_hp - current_hp)
    new_hp = current_hp + heal_amount
    
    heal_damage(user_id, -heal_amount)
    _set_last_update(user_id, now)
    
    logger.info(f"⛪ +{heal_amount} HP в церкви для user={user_id} ({total_hp_per_hour} HP/ч)")
    
    return heal_amount, new_hp, max_hp


def get_healing_status(user_id: int, context=None) -> str:
    """Статус для отображения"""
    stats = get_character_stats(user_id)
    hp_left = max(0, stats['max_health'] - stats['current_health'])
    equipment_bonus = _get_equipment_regen(user_id)
    total = HP_PER_HOUR + equipment_bonus
    
    if hp_left <= 0:
        return "❤️ HP: полностью"
    
    hours_to_full = hp_left / total
    if hours_to_full < 1:
        mins = int(hours_to_full * 60)
        return f"💤 +{total} HP/час | До полного: ~{mins} мин"
    else:
        return f"💤 +{total} HP/час | До полного: ~{int(hours_to_full)} ч"


def get_hp_until_full(user_id: int) -> int:
    stats = get_character_stats(user_id)
    return max(0, stats['max_health'] - stats['current_health'])


def get_time_until_next_heal(user_id: int) -> int:
    return 0


def get_heal_amount(user_id: int, context=None) -> int:
    stats = get_character_stats(user_id)
    hp_left = max(0, stats['max_health'] - stats['current_health'])
    return min(HP_PER_HOUR + _get_equipment_regen(user_id), hp_left)


# ═══════════════════════════════════
# ЦЕРКОВЬ (вход/выход)
# ═══════════════════════════════════

def is_in_church(user_id: int, context=None) -> bool:
    if context and hasattr(context, 'user_data'):
        return context.user_data.get('in_church', False)
    return False


def enter_church(user_id: int, context) -> dict:
    if hasattr(context, 'user_data'):
        context.user_data['in_church'] = True
        context.user_data['church_enter_time'] = datetime.now().isoformat()
    return get_character_stats(user_id)


def leave_church(user_id: int, context) -> bool:
    if hasattr(context, 'user_data'):
        context.user_data.pop('in_church', None)
        context.user_data.pop('church_enter_time', None)
        return True
    return False


# ═══════════════════════════════════
# СОВМЕСТИМОСТЬ
# ═══════════════════════════════════

def can_heal(user_id: int, context=None) -> tuple:
    return True, 0


def do_heal(user_id: int, context=None) -> tuple:
    return restore_health_over_time(user_id, context)