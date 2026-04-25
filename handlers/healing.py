"""Система лечения и отдыха — ВСЁ лечение здесь: обычное, церковь, отдых"""

import logging
import sqlite3
from datetime import datetime, timedelta
from handlers.character import get_character_stats, heal_damage

logger = logging.getLogger(__name__)

DB_FILE = "/root/bot/ratings.db"

BASE_HEAL_PER_HOUR = 10
CHURCH_HEAL_PER_HOUR = 20


def _get_last_heal_time(user_id: int) -> datetime:
    try:
        with sqlite3.connect(DB_FILE) as conn:
            c = conn.cursor()
            c.execute('''SELECT value FROM user_settings 
                         WHERE user_id = ? AND key = 'last_heal_time' ''', (user_id,))
            row = c.fetchone()
            if row:
                return datetime.fromisoformat(row[0])
    except:
        pass
    return datetime.now() - timedelta(hours=2)


def _set_last_heal_time(user_id: int, heal_time: datetime):
    try:
        with sqlite3.connect(DB_FILE) as conn:
            c = conn.cursor()
            c.execute('''CREATE TABLE IF NOT EXISTS user_settings 
                         (user_id INTEGER, key TEXT, value TEXT, 
                          PRIMARY KEY (user_id, key))''')
            c.execute('''INSERT OR REPLACE INTO user_settings (user_id, key, value) 
                         VALUES (?, 'last_heal_time', ?)''', 
                      (user_id, heal_time.isoformat()))
            conn.commit()
    except Exception as e:
        logger.error(f"Ошибка сохранения времени лечения: {e}")


def is_in_church(user_id: int, context=None) -> bool:
    if context and hasattr(context, 'user_data'):
        return context.user_data.get('in_church', False)
    return False


def restore_health_over_time(user_id: int, context=None) -> tuple:
    """ВЕЗДЕ 10 HP/час — профиль, туннели, город, таверна, магазин"""
    stats = get_character_stats(user_id)
    current_hp = stats['current_health']
    max_hp = stats['max_health']
    
    if current_hp >= max_hp:
        return 0, current_hp, max_hp
    
    last_heal = _get_last_heal_time(user_id)
    now = datetime.now()
    hours_passed = (now - last_heal).total_seconds() / 3600
    
    heal_amount = int(BASE_HEAL_PER_HOUR * hours_passed)
    
    if heal_amount <= 0:
        return 0, current_hp, max_hp
    
    new_hp = min(max_hp, current_hp + heal_amount)
    heal_damage(user_id, -(new_hp - current_hp))
    _set_last_heal_time(user_id, now)
    
    logger.info(f"❤️ Восстановлено {new_hp - current_hp} HP для user={user_id} (прошло {hours_passed:.1f}ч)")
    
    return new_hp - current_hp, new_hp, max_hp


def restore_health_in_church(user_id: int, context=None) -> tuple:
    """ТОЛЬКО кнопка Отдыхать в церкви — 20 HP/час"""
    stats = get_character_stats(user_id)
    current_hp = stats['current_health']
    max_hp = stats['max_health']
    
    if current_hp >= max_hp:
        return 0, current_hp, max_hp
    
    last_heal = _get_last_heal_time(user_id)
    now = datetime.now()
    hours_passed = (now - last_heal).total_seconds() / 3600
    
    heal_amount = int(CHURCH_HEAL_PER_HOUR * hours_passed)
    
    if heal_amount <= 0:
        return 0, current_hp, max_hp
    
    new_hp = min(max_hp, current_hp + heal_amount)
    heal_damage(user_id, -(new_hp - current_hp))
    _set_last_heal_time(user_id, now)
    
    logger.info(f"⛪ Восстановлено {new_hp - current_hp} HP в церкви для user={user_id} (прошло {hours_passed:.1f}ч)")
    
    return new_hp - current_hp, new_hp, max_hp


def enter_church(user_id: int, context) -> dict:
    """Вход в церковь — флаг in_church"""
    if hasattr(context, 'user_data'):
        context.user_data['in_church'] = True
        context.user_data['church_enter_time'] = datetime.now().isoformat()
    return get_character_stats(user_id)


def leave_church(user_id: int, context) -> bool:
    """Выход из церкви — сброс флага"""
    was_in_church = False
    if hasattr(context, 'user_data'):
        was_in_church = context.user_data.get('in_church', False)
        context.user_data.pop('in_church', None)
        context.user_data.pop('church_enter_time', None)
    if was_in_church:
        logger.info(f"🚪 User={user_id} покинул церковь")
    return was_in_church


def get_healing_status(user_id: int, context=None) -> str:
    """Статус лечения для отображения"""
    in_church = is_in_church(user_id, context)
    if in_church:
        return f"⛪ Вы в церкви — кнопка Отдыхать даст x2 лечение (+{CHURCH_HEAL_PER_HOUR} HP/час)"
    return f"💤 Лечение +{BASE_HEAL_PER_HOUR} HP/час"


def get_hp_until_full(user_id: int) -> int:
    """Сколько HP до полного здоровья"""
    stats = get_character_stats(user_id)
    return max(0, stats['max_health'] - stats['current_health'])


def get_time_until_next_heal(user_id: int) -> int:
    """Сколько минут до следующего лечения"""
    last_heal = _get_last_heal_time(user_id)
    now = datetime.now()
    seconds_passed = (now - last_heal).total_seconds()
    seconds_until_next = max(0, 3600 - seconds_passed)
    return int(seconds_until_next / 60)


def get_heal_amount(user_id: int, context=None) -> int:
    """Сколько HP восстановится сейчас"""
    return BASE_HEAL_PER_HOUR