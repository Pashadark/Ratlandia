#!/usr/bin/env python3
"""Скрипт проверки системы опыта"""

import sys
sys.path.append('/root/bot')

from handlers.inventory import (
    get_user_xp, add_xp, get_level_progress, 
    get_level_from_xp, init_inventory_db
)
from database import get_rating

def check_xp_system():
    print("=" * 50)
    print("🔍 ПРОВЕРКА СИСТЕМЫ ОПЫТА")
    print("=" * 50)
    
    # Тестовый user_id
    test_user_id = 185185047
    
    # Получаем текущий опыт
    xp_before = get_user_xp(test_user_id)
    print(f"\n📊 Текущий опыт: {xp_before} XP")
    
    level_before = get_level_from_xp(xp_before)
    print(f"⭐ Текущий уровень: {level_before}")
    
    # Показываем прогресс
    level, xp_in, xp_need = get_level_progress(xp_before)
    print(f"📈 Прогресс: {xp_in}/{xp_need} XP до следующего уровня")
    
    # Проверяем рейтинг
    rating = get_rating(test_user_id)
    if rating:
        print(f"\n📊 СТАТИСТИКА ИГРОКА:")
        print(f"👤 Имя: {rating['name']}")
        print(f"🎮 Игр: {rating['games']}")
        print(f"🏆 Побед: {rating['wins']}")
        print(f"🐀 Крыса: {rating['wins_as_rat']}/{rating['games_as_rat']}")
        print(f"🐭 Мышь: {rating['wins_as_mouse']}/{rating['games_as_mouse']}")
    else:
        print("\n❌ Игрок ещё не играл!")
    
    print("\n" + "=" * 50)
    print("🧪 ТЕСТ ДОБАВЛЕНИЯ ОПЫТА")
    print("=" * 50)
    
    # Тест: добавить 10 XP (участие)
    print("\n📝 Добавляем +10 XP (участие в игре)...")
    add_xp(test_user_id, 10)
    xp_after_10 = get_user_xp(test_user_id)
    print(f"✅ Опыт после +10: {xp_after_10} XP")
    
    # Тест: добавить 50 XP (победа)
    print("\n📝 Добавляем +50 XP (победа)...")
    add_xp(test_user_id, 50)
    xp_after_50 = get_user_xp(test_user_id)
    print(f"✅ Опыт после +50: {xp_after_50} XP")
    
    # Проверяем итог
    xp_final = get_user_xp(test_user_id)
    level_final = get_level_from_xp(xp_final)
    level, xp_in, xp_need = get_level_progress(xp_final)
    
    print("\n" + "=" * 50)
    print("📊 ИТОГИ")
    print("=" * 50)
    print(f"✨ Опыт ДО: {xp_before} XP (Уровень {level_before})")
    print(f"✨ Опыт ПОСЛЕ: {xp_final} XP (Уровень {level_final})")
    print(f"📈 Прогресс: {xp_in}/{xp_need} XP")
    
    if xp_final > xp_before:
        print("\n✅ СИСТЕМА ОПЫТА РАБОТАЕТ!")
    else:
        print("\n❌ ОПЫТ НЕ НАЧИСЛЯЕТСЯ!")
    
    print("\n" + "=" * 50)
    print("🔧 ПРОВЕРКА ТАБЛИЦ В БД")
    print("=" * 50)
    
    import sqlite3
    conn = sqlite3.connect('/root/bot/ratings.db')
    cursor = conn.cursor()
    
    # Проверяем таблицу user_stats
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='user_stats'")
    if cursor.fetchone():
        print("✅ Таблица user_stats существует")
        cursor.execute("PRAGMA table_info(user_stats)")
        columns = cursor.fetchall()
        print(f"   Колонки: {', '.join([c[1] for c in columns])}")
        
        cursor.execute("SELECT * FROM user_stats WHERE user_id = ?", (test_user_id,))
        row = cursor.fetchone()
        if row:
            print(f"   Данные игрока: {row}")
        else:
            print("   ⚠️ Нет данных для этого игрока")
    else:
        print("❌ Таблица user_stats НЕ существует!")
    
    # Проверяем таблицу ratings
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='ratings'")
    if cursor.fetchone():
        print("✅ Таблица ratings существует")
    else:
        print("❌ Таблица ratings НЕ существует!")
    
    conn.close()

if __name__ == "__main__":
    check_xp_system()
