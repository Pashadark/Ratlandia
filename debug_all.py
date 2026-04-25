#!/usr/bin/env python3
"""Полная диагностика всех систем Ратляндии"""

import os
import sys
import sqlite3
import importlib
from pathlib import Path

sys.path.append('/root/bot')

print("=" * 70)
print("🔍 ПОЛНАЯ ДИАГНОСТИКА РАТЛЯНДИИ")
print("=" * 70)

errors = []
warnings = []

# 1. ПРОВЕРКА ХЕНДЛЕРОВ В main.py
print("\n📋 1. ПРОВЕРКА ХЕНДЛЕРОВ В main.py")
print("-" * 70)

main_file = "/root/bot/main.py"
if os.path.exists(main_file):
    with open(main_file, 'r') as f:
        content = f.read()
    
    checks = [
        ("rat_rules", "CommandHandler(\"rat_rules\""),
        ("rat_top", "CommandHandler(\"rat_top\""),
        ("rat_start", "CommandHandler(\"rat_start\""),
        ("rat_stop", "CommandHandler(\"rat_stop\""),
        ("profile", "CommandHandler(\"profile\""),
        ("shop", "CommandHandler(\"shop\""),
        ("daily", "CommandHandler(\"daily\""),
        ("clan", "CommandHandler(\"clan\""),
    ]
    
    for name, pattern in checks:
        if pattern in content:
            print(f"✅ {name}: хендлер найден")
        else:
            print(f"❌ {name}: хендлер НЕ НАЙДЕН")
            errors.append(f"Хендлер {name} отсутствует в main.py")

# 2. ПРОВЕРКА ИМПОРТОВ В main.py
print("\n📦 2. ПРОВЕРКА ИМПОРТОВ В main.py")
print("-" * 70)

import_checks = [
    ("rat_rules", "from handlers.game import", "rat_rules"),
    ("rat_top", "from handlers.commands import", "rat_top"),
    ("shop_command", "from handlers.shop import", "shop_command"),
    ("daily_command", "from handlers.daily import", "daily_command"),
    ("clan_command", "from handlers.clan import", "clan_command"),
]

for name, import_line, func_name in import_checks:
    if import_line in content and func_name in content:
        print(f"✅ {name}: импорт найден")
    else:
        print(f"❌ {name}: импорт НЕ НАЙДЕН")
        errors.append(f"Импорт {name} отсутствует в main.py")

# 3. ПРОВЕРКА НАЛИЧИЯ ФУНКЦИЙ В МОДУЛЯХ
print("\n🔧 3. ПРОВЕРКА ФУНКЦИЙ В МОДУЛЯХ")
print("-" * 70)

modules_to_check = [
    ("handlers.game", ["rat_rules", "rat_start", "rat_stop"]),
    ("handlers.commands", ["rat_top", "rat_me", "start", "help_command"]),
    ("handlers.shop", ["shop_command", "handle_shop_buy"]),
    ("handlers.daily", ["daily_command"]),
    ("handlers.clan", ["clan_command"]),
    ("handlers.profile", ["profile_command", "inventory_command", "equipment_command"]),
    ("handlers.inventory", ["get_crumbs", "add_crumbs", "spend_crumbs", "add_xp"]),
]

for module_name, funcs in modules_to_check:
    try:
        module = importlib.import_module(module_name)
        for func in funcs:
            if hasattr(module, func):
                print(f"✅ {module_name}.{func}: OK")
            else:
                print(f"❌ {module_name}.{func}: НЕ НАЙДЕНА")
                errors.append(f"Функция {func} не найдена в {module_name}")
    except Exception as e:
        print(f"❌ {module_name}: ОШИБКА ИМПОРТА - {e}")
        errors.append(f"Не удалось импортировать {module_name}: {e}")

# 4. ПРОВЕРКА КАРТИНОК
print("\n🖼️ 4. ПРОВЕРКА КАРТИНОК")
print("-" * 70)

images_dir = "/root/bot/images"
required_images = [
    "mice_win.jpg", "rat_win.jpg", "night.jpg", "day.jpg", "voting.jpg",
    "rat_kill.jpg", "role_cards.jpg", "item_drop.jpg", "leaderboard.jpg",
    "profile.jpg", "achievement.jpg", "lobby.jpg", "inventory.jpg",
    "equipment.jpg", "rat_choose.jpg", "use_item_prompt.jpg",
    "loading.jpg", "rules.jpg", "level_up.jpg"
]

if os.path.exists(images_dir):
    for img in required_images:
        path = os.path.join(images_dir, img)
        if os.path.exists(path):
            print(f"✅ {img}")
        else:
            print(f"❌ {img} - ОТСУТСТВУЕТ")
            warnings.append(f"Картинка {img} отсутствует")
else:
    print(f"❌ Папка {images_dir} не существует!")
    errors.append(f"Папка {images_dir} не существует")

# 5. ПРОВЕРКА ТАБЛИЦ БД
print("\n🗄️ 5. ПРОВЕРКА ТАБЛИЦ БАЗЫ ДАННЫХ")
print("-" * 70)

db_file = "/root/bot/ratings.db"
required_tables = [
    "ratings", "inventory", "equipment", "user_achievements",
    "user_stats", "user_titles", "user_active_title", "user_currency",
    "daily_rewards", "clans", "clan_members"
]

if os.path.exists(db_file):
    try:
        conn = sqlite3.connect(db_file)
        c = conn.cursor()
        c.execute("SELECT name FROM sqlite_master WHERE type='table'")
        existing = [row[0] for row in c.fetchall()]
        
        for table in required_tables:
            if table in existing:
                c.execute(f"SELECT COUNT(*) FROM {table}")
                count = c.fetchone()[0]
                print(f"✅ {table:<20} ({count} записей)")
            else:
                print(f"⚠️ {table:<20} - НЕ СУЩЕСТВУЕТ")
                warnings.append(f"Таблица {table} не существует")
        conn.close()
    except Exception as e:
        print(f"❌ Ошибка БД: {e}")
        errors.append(f"Ошибка БД: {e}")
else:
    print(f"❌ Файл БД не найден: {db_file}")
    errors.append(f"Файл БД не найден: {db_file}")

# 6. ПРОВЕРКА КОНФИГУРАЦИИ
print("\n⚙️ 6. ПРОВЕРКА КОНФИГУРАЦИИ")
print("-" * 70)

try:
    from config import TOKEN, MIN_PLAYERS, MAX_PLAYERS, NIGHT_TIME, DAY_TIME, VOTE_TIME
    print(f"✅ TOKEN: {TOKEN[:10]}...")
    print(f"✅ MIN_PLAYERS: {MIN_PLAYERS}")
    print(f"✅ MAX_PLAYERS: {MAX_PLAYERS}")
    print(f"✅ NIGHT_TIME: {NIGHT_TIME}")
    print(f"✅ DAY_TIME: {DAY_TIME}")
    print(f"✅ VOTE_TIME: {VOTE_TIME}")
except Exception as e:
    print(f"❌ Ошибка конфигурации: {e}")
    errors.append(f"Ошибка конфигурации: {e}")

# 7. ПРОВЕРКА СИНТАКСИСА PYTHON ФАЙЛОВ
print("\n🐍 7. ПРОВЕРКА СИНТАКСИСА PYTHON")
print("-" * 70)

py_files = [
    "/root/bot/main.py",
    "/root/bot/handlers/game.py",
    "/root/bot/handlers/commands.py",
    "/root/bot/handlers/callbacks.py",
    "/root/bot/handlers/profile.py",
    "/root/bot/handlers/shop.py",
    "/root/bot/handlers/daily.py",
    "/root/bot/handlers/clan.py",
]

for py_file in py_files:
    if os.path.exists(py_file):
        result = os.system(f"python3 -m py_compile {py_file} 2>/dev/null")
        if result == 0:
            print(f"✅ {os.path.basename(py_file)}")
        else:
            print(f"❌ {os.path.basename(py_file)} - ОШИБКА СИНТАКСИСА")
            errors.append(f"Ошибка синтаксиса в {py_file}")
    else:
        print(f"⚠️ {os.path.basename(py_file)} - файл не найден")

# ИТОГ
print("\n" + "=" * 70)
print("📊 ИТОГИ ДИАГНОСТИКИ")
print("=" * 70)

if errors:
    print(f"\n❌ НАЙДЕНО ОШИБОК: {len(errors)}")
    for e in errors:
        print(f"   - {e}")
else:
    print("\n✅ КРИТИЧЕСКИХ ОШИБОК НЕ НАЙДЕНО!")

if warnings:
    print(f"\n⚠️ ПРЕДУПРЕЖДЕНИЯ: {len(warnings)}")
    for w in warnings:
        print(f"   - {w}")

print("\n" + "=" * 70)

# РЕКОМЕНДАЦИИ
print("\n💡 РЕКОМЕНДАЦИИ:")
if errors:
    print("   1. Исправь ошибки из списка выше")
    print("   2. Перезапусти бота")
else:
    print("   ✅ Все системы работают корректно!")
    print("   🚀 Можно запускать бота: cd /root/bot && PYTHONPATH=/root/bot python3 main.py")

print("=" * 70)
