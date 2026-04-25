#!/usr/bin/env python3
"""Полная проверка всех систем Ратляндии v0.0.1"""

import sys
sys.path.append('/root/bot')

print("=" * 60)
print("🔍 ПОЛНАЯ ПРОВЕРКА РАТЛЯНДИИ v0.0.1")
print("=" * 60)

# 1. Проверка импортов
print("\n📦 1. ПРОВЕРКА ИМПОРТОВ")
try:
    from handlers.inventory import (
        get_inventory, get_equipment, get_achievements, get_user_xp,
        get_level_progress, add_xp, add_item, get_random_item,
        update_stats, check_and_unlock_achievements, unlock_achievement,
        use_consumable, equip_item, unequip_item, get_crumbs, add_crumbs
    )
    print("✅ inventory.py импортирован (крошки тоже)")
except Exception as e:
    print(f"❌ inventory.py: {e}")

try:
    from handlers.items import ALL_ITEMS, EQUIPMENT, CONSUMABLES, DROP_CHANCES, EQUIPMENT_SLOTS
    print(f"✅ items.py: {len(ALL_ITEMS)} предметов (экипировка: {len(EQUIPMENT)}, расходники: {len(CONSUMABLES)})")
except Exception as e:
    print(f"❌ items.py: {e}")

try:
    from handlers.achievements_data import ACHIEVEMENTS
    print(f"✅ achievements_data.py: {len(ACHIEVEMENTS)} достижений")
except Exception as e:
    print(f"❌ achievements_data.py: {e}")

try:
    from handlers.titles import TITLES, get_active_title, get_unlocked_titles, set_active_title
    print(f"✅ titles.py: {len(TITLES)} титулов")
except Exception as e:
    print(f"❌ titles.py: {e}")

try:
    from database import get_rating, update_rating, get_top_players
    print("✅ database.py импортирован")
except Exception as e:
    print(f"❌ database.py: {e}")

try:
    from config import TOKEN, MIN_PLAYERS, MAX_PLAYERS, NIGHT_TIME, DAY_TIME, VOTE_TIME
    print(f"✅ config.py: MIN={MIN_PLAYERS}, MAX={MAX_PLAYERS}, NIGHT={NIGHT_TIME}s, DAY={DAY_TIME}s, VOTE={VOTE_TIME}s")
except Exception as e:
    print(f"❌ config.py: {e}")

# 2. Проверка базы данных
print("\n🗄️ 2. ПРОВЕРКА БАЗЫ ДАННЫХ")
import sqlite3
conn = sqlite3.connect('/root/bot/ratings.db')
c = conn.cursor()

tables = ['ratings', 'inventory', 'equipment', 'user_achievements', 'user_stats', 'user_titles', 'user_active_title', 'user_currency']
for table in tables:
    c.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table}'")
    if c.fetchone():
        c.execute(f"SELECT COUNT(*) FROM {table}")
        count = c.fetchone()[0]
        print(f"✅ {table}: {count} записей")
    else:
        print(f"❌ {table}: НЕ СУЩЕСТВУЕТ")

conn.close()

# 3. Проверка шансов выпадения
print("\n🎲 3. ПРОВЕРКА ШАНСОВ ВЫПАДЕНИЯ")
print(f"Шансы: {DROP_CHANCES}")
total_chance = sum(DROP_CHANCES.values())
print(f"Сумма шансов: {total_chance}% {'✅' if total_chance == 100 else '❌'}")

# 4. Тест выпадения предметов
print("\n🎁 4. ТЕСТ ВЫПАДЕНИЯ ПРЕДМЕТОВ")
for role in ['rat', 'mouse']:
    items_dropped = []
    for _ in range(100):
        item = get_random_item(role)
        if item:
            items_dropped.append(item)
    
    rarities = {}
    for item_id in items_dropped:
        if item_id in ALL_ITEMS:
            rar = ALL_ITEMS[item_id]['rarity']
            rarities[rar] = rarities.get(rar, 0) + 1
    
    print(f"\nРоль '{role}' (100 попыток):")
    for rar, count in rarities.items():
        print(f"  {rar}: {count}% (ожидалось ~{DROP_CHANCES.get(rar, 0)}%)")

# 5. Проверка профиля и игры
print("\n👤 5. ПРОВЕРКА ПРОФИЛЯ И ИГРЫ")
try:
    from handlers.profile import profile_command, inventory_command, equipment_command, achievements_command
    print("✅ profile.py импортирован")
except Exception as e:
    print(f"❌ profile.py: {e}")

try:
    from handlers.game import RatGame, active_games, rat_start, night_phase, end_game
    print("✅ game.py импортирован")
except Exception as e:
    print(f"❌ game.py: {e}")

try:
    from handlers.callbacks import button_callback
    print("✅ callbacks.py импортирован")
except Exception as e:
    print(f"❌ callbacks.py: {e}")

# 6. Проверка команд
print("\n📋 6. ПРОВЕРКА КОМАНД")
try:
    from handlers.commands import start, help_command, rat_top, rat_me, crumbs_command
    print("✅ commands.py импортирован (включая /crumbs)")
except Exception as e:
    print(f"❌ commands.py: {e}")

# 7. Проверка крошек
print("\n🧀 7. ПРОВЕРКА КРОШЕК")
test_user = 185185047
crumbs = get_crumbs(test_user)
print(f"Крошки у тестового игрока: {crumbs} 🧀")

# 8. Проверка титулов
print("\n🏆 8. ПРОВЕРКА ТИТУЛОВ")
active_title = get_active_title(test_user)
if active_title:
    print(f"Активный титул: {active_title['name']}")
else:
    print("Активный титул: 🌱 Новичок (по умолчанию)")

unlocked = get_unlocked_titles(test_user)
print(f"Разблокировано титулов: {len(unlocked)}/{len(TITLES)}")

print("\n" + "=" * 60)
print("✅ ПРОВЕРКА ЗАВЕРШЕНА!")
print("=" * 60)
