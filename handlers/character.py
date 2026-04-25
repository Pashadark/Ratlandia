"""Единая система характеристик для всей игры"""

import sqlite3
from datetime import datetime
from typing import Dict, Optional, List

DB_FILE = "/root/bot/ratings.db"


def init_character_db():
    """Проверяет наличие колонок (создаются через ALTER)"""
    pass  # Колонки уже добавлены через SSH


# ========== ПОЛУЧЕНИЕ ХАРАКТЕРИСТИК ==========

def get_character_stats(user_id: int) -> Dict:
    """Возвращает текущие характеристики игрока"""
    with sqlite3.connect(DB_FILE) as conn:
        c = conn.cursor()
        
        # Проверяем существование записи
        c.execute('SELECT user_id FROM user_stats WHERE user_id = ?', (user_id,))
        if not c.fetchone():
            c.execute('''INSERT INTO user_stats (user_id, strength, agility, intelligence, 
                         max_health, current_health, level, stat_points, xp) 
                         VALUES (?, 3, 3, 3, 110, 110, 1, 0, 0)''', (user_id,))
            conn.commit()
            return {
                "strength": 3,
                "agility": 3,
                "intelligence": 3,
                "max_health": 110,
                "current_health": 110,
                "xp": 0,
                "level": 1,
                "stat_points": 0,
                "total_tunnel_runs": 0,
                "last_health_update": None
            }
        
        # Получаем данные из БД
        c.execute('''SELECT strength, agility, intelligence, max_health, current_health,
                     xp, level, stat_points, total_tunnel_runs, last_health_update
                     FROM user_stats WHERE user_id = ?''', (user_id,))
        row = c.fetchone()
        
        if row:
            base_stats = {
                "strength": row[0],
                "agility": row[1],
                "intelligence": row[2],
                "max_health": row[3],
                "current_health": row[4],
                "xp": row[5] if row[5] is not None else 0,
                "level": row[6] if row[6] is not None else 1,
                "stat_points": row[7] if row[7] is not None else 0,
                "total_tunnel_runs": row[8] if row[8] is not None else 0,
                "last_health_update": row[9]
            }
        else:
            base_stats = {
                "strength": 3,
                "agility": 3,
                "intelligence": 3,
                "max_health": 110,
                "current_health": 110,
                "xp": 0,
                "level": 1,
                "stat_points": 0,
                "total_tunnel_runs": 0,
                "last_health_update": None
            }
    
    # 🆕 ДОБАВЛЯЕМ БОНУСЫ ОТ ЭКИПИРОВКИ (ИМПОРТ ВНУТРИ ФУНКЦИИ!)
    try:
        from handlers.effects import get_player_effects
        effects = get_player_effects(user_id, "all")
        
        base_stats["strength"] = base_stats["strength"] + effects.get("strength", 0)
        base_stats["agility"] = base_stats["agility"] + effects.get("agility", 0)
        base_stats["intelligence"] = base_stats["intelligence"] + effects.get("intelligence", 0)
        base_stats["max_health"] = base_stats["max_health"] + effects.get("max_health", 0)
        
        # Бонус ко всем характеристикам
        all_stats = effects.get("all_stats", 0)
        if all_stats > 0:
            base_stats["strength"] = base_stats["strength"] + all_stats
            base_stats["agility"] = base_stats["agility"] + all_stats
            base_stats["intelligence"] = base_stats["intelligence"] + all_stats
    except Exception as e:
        pass  # Если эффекты не загрузились - игнорируем
    
    return base_stats


def update_character_stats(user_id: int, **kwargs):
    """Обновляет характеристики игрока"""
    with sqlite3.connect(DB_FILE) as conn:
        c = conn.cursor()
        
        c.execute('SELECT user_id FROM user_stats WHERE user_id = ?', (user_id,))
        if not c.fetchone():
            c.execute('''INSERT INTO user_stats (user_id, strength, agility, intelligence, 
                         max_health, current_health, level) 
                         VALUES (?, 3, 3, 3, 110, 110, 1)''', (user_id,))
        
        updates = [f"{k} = ?" for k in kwargs.keys()]
        values = list(kwargs.values()) + [user_id]
        c.execute(f"UPDATE user_stats SET {','.join(updates)} WHERE user_id = ?", values)
        conn.commit()


# ========== ПРОКАЧКА ХАРАКТЕРИСТИК ==========

def upgrade_stat(user_id: int, stat: str) -> tuple:
    """Повышает характеристику на 1. Возвращает (успех, сообщение, новые_значения)"""
    stats = get_character_stats(user_id)
    
    if stats['stat_points'] <= 0:
        return False, "❌ Нет свободных очков характеристик!", None
    
    update_data = {}
    
    if stat == "strength":
        new_strength = stats['strength'] + 1
        new_max_hp = 80 + (new_strength * 10)
        hp_diff = new_max_hp - stats['max_health']
        
        update_data = {
            "strength": new_strength,
            "max_health": new_max_hp,
            "current_health": stats['current_health'] + hp_diff,
            "stat_points": stats['stat_points'] - 1
        }
        update_character_stats(user_id, **update_data)
        return True, f"💪 Сила повышена до {new_strength}!", update_data
    
    elif stat == "agility":
        update_data = {
            "agility": stats['agility'] + 1,
            "stat_points": stats['stat_points'] - 1
        }
        update_character_stats(user_id, **update_data)
        return True, f"🍀 Ловкость повышена до {stats['agility'] + 1}!", update_data
    
    elif stat == "intelligence":
        update_data = {
            "intelligence": stats['intelligence'] + 1,
            "stat_points": stats['stat_points'] - 1
        }
        update_character_stats(user_id, **update_data)
        return True, f"🧠 Интеллект повышен до {stats['intelligence'] + 1}!", update_data
    
    return False, "❌ Неизвестная характеристика!", None


# ========== СИНХРОНИЗАЦИЯ УРОВНЯ ==========

def sync_level_and_points(user_id: int, new_level: int):
    """Вызывается при повышении основного уровня. Начисляет очки характеристик."""
    stats = get_character_stats(user_id)
    current_level = stats.get('level', 1)
    
    if new_level > current_level:
        points_to_add = new_level - current_level
        update_character_stats(
            user_id,
            level=new_level,
            stat_points=stats['stat_points'] + points_to_add
        )
        return points_to_add
    return 0


def get_tunnel_statistics(user_id: int) -> Dict:
    """Возвращает статистику туннелей"""
    with sqlite3.connect(DB_FILE) as conn:
        c = conn.cursor()
        c.execute('''SELECT total_tunnel_runs, tunnel_deaths, total_tunnel_crumbs 
                     FROM user_stats WHERE user_id = ?''', (user_id,))
        row = c.fetchone()
        if row:
            return {
                "total_runs": row[0] or 0,
                "deaths": row[1] or 0,
                "total_crumbs": row[2] or 0
            }
        return {"total_runs": 0, "deaths": 0, "total_crumbs": 0}


def get_defeated_bosses(user_id: int) -> List[str]:
    """Возвращает список побеждённых боссов"""
    with sqlite3.connect(DB_FILE) as conn:
        c = conn.cursor()
        c.execute('SELECT monster_id FROM tunnel_bosses_defeated WHERE user_id = ?', (user_id,))
        return [row[0] for row in c.fetchall()]


def get_active_effects(user_id: int) -> List[str]:
    """Возвращает список активных эффектов"""
    effects = []
    
    try:
        from handlers.tunnel_monsters import get_tunnel_run
        run_data = get_tunnel_run(user_id)
        if run_data and run_data.get("blessed"):
            effects.append("✨ Благословение алтаря: +1 урона")
    except:
        pass
    
    return effects


# ========== ЗДОРОВЬЕ ==========

def take_damage(user_id: int, damage: int) -> int:
    """Наносит урон игроку. Возвращает новое здоровье."""
    stats = get_character_stats(user_id)
    new_hp = max(1, stats['current_health'] - damage)
    update_character_stats(user_id, current_health=new_hp)
    return new_hp


def heal_damage(user_id: int, heal: int) -> int:
    """Восстанавливает здоровье. Возвращает новое здоровье."""
    stats = get_character_stats(user_id)
    new_hp = min(stats['max_health'], stats['current_health'] + heal)
    update_character_stats(user_id, current_health=new_hp)
    return new_hp


def is_alive(user_id: int) -> bool:
    """Проверяет жив ли игрок (HP > 1)""" 
    stats = get_character_stats(user_id)
    return stats['current_health'] > 1


# ========== ТУННЕЛИ ==========

def increment_tunnel_deaths(user_id: int):
    """Увеличивает счётчик смертей в туннелях"""
    with sqlite3.connect(DB_FILE) as conn:
        c = conn.cursor()
        c.execute('UPDATE user_stats SET tunnel_deaths = COALESCE(tunnel_deaths, 0) + 1 WHERE user_id = ?', (user_id,))
        conn.commit()


def add_tunnel_crumbs(user_id: int, amount: int):
    """Добавляет крошки в общую статистику туннелей"""
    with sqlite3.connect(DB_FILE) as conn:
        c = conn.cursor()
        c.execute('UPDATE user_stats SET total_tunnel_crumbs = COALESCE(total_tunnel_crumbs, 0) + ? WHERE user_id = ?', (amount, user_id))
        conn.commit()


def increment_tunnel_runs(user_id: int):
    """Увеличивает счётчик походов в туннели"""
    stats = get_character_stats(user_id)
    update_character_stats(user_id, total_tunnel_runs=stats.get('total_tunnel_runs', 0) + 1)


def get_tunnel_runs(user_id: int) -> int:
    """Возвращает количество походов в туннели"""
    stats = get_character_stats(user_id)
    return stats.get('total_tunnel_runs', 0)