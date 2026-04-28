#!/usr/bin/env python3
"""Единый тест всех систем Ratlandia — только чтение, без изменений"""

import os
import sys
import sqlite3
import importlib

print("=" * 60)
print("🧪 ЕДИНЫЙ ТЕСТ ВСЕХ СИСТЕМ РАТЛЯНДИИ")
print("=" * 60)

DB_FILE = "/root/bot/ratings.db"
errors = []


def check(condition, msg):
    if condition:
        print(f"   ✅ {msg}")
    else:
        print(f"   ❌ {msg}")
        errors.append(msg)


# 1. ИМПОРТЫ
print("\n📦 1. ИМПОРТЫ ВСЕХ МОДУЛЕЙ")
modules_ok = 0
modules_fail = 0
all_modules = [
    "config", "database",
    "handlers.commands", "handlers.callbacks", "handlers.profile",
    "handlers.inventory", "handlers.items", "handlers.character",
    "handlers.shop", "handlers.daily", "handlers.clan",
    "handlers.titles", "handlers.city", "handlers.blacksmith",
    "handlers.crafting", "handlers.enchant", "handlers.church",
    "handlers.healing", "handlers.effects", "handlers.tunnel",
    "handlers.tunnel_battle", "handlers.tunnel_monsters",
    "handlers.tunnel_rooms", "handlers.tunnel_coop",
    "handlers.admin", "handlers.bug_report",
    "handlers.hall_of_fame", "handlers.achievements_data",
    "handlers.notifications",
]
for mod in all_modules:
    try:
        importlib.import_module(mod)
        modules_ok += 1
    except Exception as e:
        print(f"   ❌ {mod}: {str(e)[:60]}")
        modules_fail += 1
print(f"   📊 Модулей загружено: {modules_ok}/{len(all_modules)}")

# 2. БАЗА ДАННЫХ
print("\n🗄️ 2. БАЗА ДАННЫХ")
if os.path.exists(DB_FILE):
    try:
        conn = sqlite3.connect(DB_FILE)
        c = conn.cursor()
        c.execute("PRAGMA integrity_check")
        integrity = c.fetchone()[0]
        check(integrity == "ok", f"Целостность БД: {integrity}")

        c.execute("SELECT COUNT(*) FROM ratings")
        players = c.fetchone()[0]
        check(players > 0, f"Игроков в БД: {players}")

        c.execute("SELECT COUNT(*) FROM inventory")
        items = c.fetchone()[0]
        check(items > 0, f"Предметов в инвентарях: {items}")

        c.execute("SELECT COUNT(*) FROM user_currency")
        curr = c.fetchone()[0]
        print(f"   ✅ Записей валюты: {curr}")

        conn.close()
    except Exception as e:
        check(False, f"Ошибка БД: {str(e)[:60]}")
else:
    check(False, f"Файл БД не найден: {DB_FILE}")

# 3. КАРТИНКИ
print("\n🖼️ 3. КРИТИЧЕСКИЕ КАРТИНКИ")
critical = [
    "city_main.jpg", "profile.jpg", "shop.jpg", "tunnel_entrance.jpg",
    "start.jpg", "start_name.jpg", "inventory.jpg", "equipment.jpg",
]
for img in critical:
    path = f"/root/bot/images/{img}"
    check(os.path.exists(path), img)

# 4. КОНФИГ
print("\n⚙️ 4. КОНФИГУРАЦИЯ")
try:
    from config import TOKEN, MIN_PLAYERS, MAX_PLAYERS

    check(len(TOKEN) > 30, f"Токен валиден (длина {len(TOKEN)})")
    check(MIN_PLAYERS >= 2, f"MIN_PLAYERS = {MIN_PLAYERS}")
    check(MAX_PLAYERS <= 20, f"MAX_PLAYERS = {MAX_PLAYERS}")
except Exception as e:
    check(False, f"Ошибка config: {e}")

# 5. ПРЕДМЕТЫ
print("\n🎒 5. ПРЕДМЕТЫ")
try:
    from handlers.items import ALL_ITEMS, EQUIPMENT, CONSUMABLES, CHESTS, RECIPES

    check(len(ALL_ITEMS) > 100, f"ALL_ITEMS: {len(ALL_ITEMS)}")
    check(len(EQUIPMENT) > 10, f"EQUIPMENT: {len(EQUIPMENT)}")
    check(len(CONSUMABLES) > 10, f"CONSUMABLES: {len(CONSUMABLES)}")
    check(len(CHESTS) > 0, f"CHESTS: {len(CHESTS)}")
    check(len(RECIPES) > 0, f"RECIPES: {len(RECIPES)}")
except Exception as e:
    check(False, f"Ошибка items: {e}")

# 6. ДОСТИЖЕНИЯ И ТИТУЛЫ
print("\n🏆 6. ДОСТИЖЕНИЯ И ТИТУЛЫ")
try:
    from handlers.achievements_data import ACHIEVEMENTS
    from handlers.titles import TITLES

    check(len(ACHIEVEMENTS) > 0, f"Достижений: {len(ACHIEVEMENTS)}")
    check(len(TITLES) > 0, f"Титулов: {len(TITLES)}")
except Exception as e:
    check(False, f"Ошибка: {e}")

# 7. ТУННЕЛИ
print("\n🕳️ 7. ТУННЕЛИ")
try:
    from handlers.tunnel_monsters import TUNNEL_MONSTERS

    check(len(TUNNEL_MONSTERS) > 0, f"Монстров: {len(TUNNEL_MONSTERS)}")
except Exception as e:
    check(False, f"Ошибка монстров: {e}")

try:
    from handlers.tunnel_rooms import process_room_transition

    check(callable(process_room_transition), "process_room_transition импортирован")
except Exception as e:
    check(False, f"Ошибка комнат: {e}")

try:
    from handlers.tunnel_battle import start_battle

    check(callable(start_battle), "start_battle импортирован")
except Exception as e:
    check(False, f"Ошибка битвы: {e}")

# 8. КУЗНИЦА
print("\n🔨 8. КУЗНИЦА")
try:
    from handlers.crafting import roll_craft_dice, get_quality_from_roll

    result = roll_craft_dice()
    check(2 <= result <= 12, f"Бросок 2d6: {result}")
    quality, _ = get_quality_from_roll(8)
    check(quality is not None, f"Качество для 8: {quality.display if quality else 'None'}")
except Exception as e:
    check(False, f"Ошибка кузницы: {e}")

# 9. ДАЙС-ДВИЖОК
print("\n🎲 9. ДАЙС-ДВИЖОК")
try:
    from core.dice.engine import DiceEngine

    engine = DiceEngine()
    r = engine.roll_1d6()
    check(1 <= r <= 6, f"Бросок 1d6: {r}")
except Exception as e:
    check(False, f"Ошибка дайсов: {e}")

# 10. СЕРВИСЫ
print("\n🔧 10. СЕРВИСЫ")
try:
    from services.dice_service import dice_service

    check(dice_service is not None, "dice_service загружен")
except Exception as e:
    print(f"   ⚠️ dice_service: {e}")

try:
    from services.tavern_service import tavern_service

    check(tavern_service is not None, "tavern_service загружен")
except Exception as e:
    print(f"   ⚠️ tavern_service: {e}")

# ИТОГ
print(f"\n{'=' * 60}")
if errors:
    print(f"❌ НАЙДЕНО ОШИБОК: {len(errors)}")
    for e in errors:
        print(f"   - {e}")
else:
    print("✅ ВСЕ ПРОВЕРКИ ПРОЙДЕНЫ!")
print(f"{'=' * 60}")