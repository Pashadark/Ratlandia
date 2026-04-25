#!/usr/bin/env python3
"""Полная проверка всех картинок и их использования в коде"""

import os
import sys
sys.path.append('/root/bot')

print("=" * 70)
print("🖼️ ПОЛНАЯ ПРОВЕРКА КАРТИНОК РАТЛЯНДИИ")
print("=" * 70)

IMAGES_DIR = "/root/bot/images"

# Все необходимые картинки
REQUIRED_IMAGES = {
    "mice_win.jpg": "Победа мышей",
    "rat_win.jpg": "Победа крысы",
    "night.jpg": "Ночь",
    "day.jpg": "День",
    "voting.jpg": "Голосование",
    "rat_kill.jpg": "Убийство",
    "role_cards.jpg": "Раздача ролей",
    "item_drop.jpg": "Получение предмета",
    "leaderboard.jpg": "Топ игроков",
    "profile.jpg": "Профиль",
    "achievement.jpg": "Достижение",
    "lobby.jpg": "Лобби",
    "inventory.jpg": "Инвентарь",
    "equipment.jpg": "Экипировка",
    "rat_choose.jpg": "Выбор жертвы",
    "use_item_prompt.jpg": "Использовать предмет",
    "loading.jpg": "Загрузка",
    "rules.jpg": "Правила",
    "level_up.jpg": "Уровень повышен",
}

# Проверка наличия файлов
print("\n📁 1. ПРОВЕРКА НАЛИЧИЯ ФАЙЛОВ")
print("-" * 70)

found = []
missing = []
corrupted = []

for filename, desc in REQUIRED_IMAGES.items():
    path = os.path.join(IMAGES_DIR, filename)
    if os.path.exists(path):
        try:
            with open(path, 'rb') as f:
                header = f.read(4)
                if header[:2] == b'\xff\xd8' or header[:4] == b'\x89PNG':
                    size = os.path.getsize(path) / 1024
                    found.append((filename, size))
                    print(f"✅ {filename:<25} {desc:<20} ({size:.1f} KB)")
                else:
                    corrupted.append(filename)
                    print(f"⚠️ {filename:<25} {desc:<20} - ПОВРЕЖДЁН")
        except:
            corrupted.append(filename)
            print(f"❌ {filename:<25} {desc:<20} - ОШИБКА ЧТЕНИЯ")
    else:
        missing.append((filename, desc))
        print(f"❌ {filename:<25} {desc:<20} - ОТСУТСТВУЕТ")

# Проверка использования в коде
print("\n🔧 2. ПРОВЕРКА ИСПОЛЬЗОВАНИЯ В КОДЕ")
print("-" * 70)

# Сканируем файлы на упоминания картинок
import re
from pathlib import Path

code_files = [
    "/root/bot/handlers/game.py",
    "/root/bot/handlers/profile.py",
    "/root/bot/handlers/commands.py",
    "/root/bot/handlers/callbacks.py",
]

used_images = set()
for code_file in code_files:
    if os.path.exists(code_file):
        with open(code_file, 'r', encoding='utf-8') as f:
            content = f.read()
            for img in REQUIRED_IMAGES.keys():
                if img in content:
                    used_images.add(img)

for img in REQUIRED_IMAGES.keys():
    if img in used_images:
        print(f"✅ {img:<25} - используется в коде")
    else:
        print(f"⚠️ {img:<25} - НЕ ИСПОЛЬЗУЕТСЯ")

# Проверка импортов модулей
print("\n📦 3. ПРОВЕРКА ИМПОРТОВ МОДУЛЕЙ")
print("-" * 70)

modules = [
    ("handlers.game", "game.py"),
    ("handlers.profile", "profile.py"),
    ("handlers.commands", "commands.py"),
    ("handlers.callbacks", "callbacks.py"),
    ("handlers.inventory", "inventory.py"),
    ("handlers.items", "items.py"),
    ("handlers.achievements_data", "achievements_data.py"),
    ("handlers.titles", "titles.py"),
]

for module, filename in modules:
    try:
        __import__(module)
        print(f"✅ {filename:<25} - импортируется")
    except Exception as e:
        print(f"❌ {filename:<25} - ОШИБКА: {str(e)[:50]}")

# Проверка синтаксиса Python файлов
print("\n🐍 4. ПРОВЕРКА СИНТАКСИСА PYTHON")
print("-" * 70)

py_files = [
    "/root/bot/handlers/game.py",
    "/root/bot/handlers/profile.py",
    "/root/bot/handlers/commands.py",
    "/root/bot/handlers/callbacks.py",
    "/root/bot/handlers/inventory.py",
    "/root/bot/handlers/items.py",
    "/root/bot/main.py",
]

for py_file in py_files:
    if os.path.exists(py_file):
        result = os.system(f"python3 -m py_compile {py_file} 2>/dev/null")
        if result == 0:
            print(f"✅ {os.path.basename(py_file):<25} - синтаксис OK")
        else:
            print(f"❌ {os.path.basename(py_file):<25} - ОШИБКА СИНТАКСИСА")
    else:
        print(f"⚠️ {os.path.basename(py_file):<25} - файл не найден")

# Проверка прав доступа
print("\n🔐 5. ПРОВЕРКА ПРАВ ДОСТУПА")
print("-" * 70)

if os.path.exists(IMAGES_DIR):
    perms = oct(os.stat(IMAGES_DIR).st_mode)[-3:]
    print(f"✅ Папка images: права {perms}")
    
    for filename, _ in found[:5]:
        path = os.path.join(IMAGES_DIR, filename)
        perms = oct(os.stat(path).st_mode)[-3:]
        print(f"✅ {filename}: права {perms}")
else:
    print(f"❌ Папка {IMAGES_DIR} не существует")

# ИТОГ
print("\n" + "=" * 70)
print("📊 ИТОГИ ПРОВЕРКИ")
print("=" * 70)

print(f"\n🖼️ КАРТИНКИ:")
print(f"   ✅ Найдено: {len(found)}/{len(REQUIRED_IMAGES)}")
if missing:
    print(f"   ❌ Отсутствует: {len(missing)}")
    for filename, desc in missing:
        print(f"      - {filename} ({desc})")
if corrupted:
    print(f"   ⚠️ Повреждено: {len(corrupted)}")

print(f"\n💻 КОД:")
print(f"   ✅ Используется в коде: {len(used_images)}/{len(REQUIRED_IMAGES)}")
unused = set(REQUIRED_IMAGES.keys()) - used_images
if unused:
    print(f"   ⚠️ Не используется: {len(unused)}")
    for img in unused:
        print(f"      - {img}")

print("\n" + "=" * 70)
if len(found) == len(REQUIRED_IMAGES) and not corrupted:
    print("✅ ВСЕ КАРТИНКИ НА МЕСТЕ И НЕ ПОВРЕЖДЕНЫ!")
else:
    print("⚠️ ТРЕБУЕТСЯ ВНИМАНИЕ! Проверьте отсутствующие файлы.")
print("=" * 70)
