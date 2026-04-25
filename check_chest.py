#!/usr/bin/env python3
"""Скрипт проверки открытия сундуков"""

import sys
sys.path.append('/root/bot')

print("=" * 60)
print("🔍 ПРОВЕРКА ЦЕПОЧКИ ОТКРЫТИЯ СУНДУКА")
print("=" * 60)

# 1. Проверяем колбэк в callbacks.py
print("\n1️⃣ ПРОВЕРКА callbacks.py:")
with open('/root/bot/handlers/callbacks.py', 'r') as f:
    content = f.read()
    
    if "elif data.startswith(\"open_chest_\"):" in content:
        print("   ✅ Обработчик open_chest_ найден")
        
        # Ищем строку с исправлением
        if "endswith(\"_chest\")" in content:
            print("   ✅ Исправление chest_id найдено")
        else:
            print("   ❌ Исправление chest_id ОТСУТСТВУЕТ!")
    else:
        print("   ❌ Обработчик open_chest_ НЕ НАЙДЕН!")

# 2. Проверяем CHESTS в items.py
print("\n2️⃣ ПРОВЕРКА CHESTS в items.py:")
from handlers.items import CHESTS

print(f"   📦 Доступные сундуки: {list(CHESTS.keys())}")
print(f"   ✅ 'epic_chest' в CHESTS: {'epic_chest' in CHESTS}")
print(f"   ✅ 'mythic_chest' в CHESTS: {'mythic_chest' in CHESTS}")
print(f"   ❌ 'epic' в CHESTS: {'epic' in CHESTS}")
print(f"   ❌ 'mythic' в CHESTS: {'mythic' in CHESTS}")

# 3. Проверяем функцию open_chest в inventory.py
print("\n3️⃣ ПРОВЕРКА open_chest в inventory.py:")
with open('/root/bot/handlers/inventory.py', 'r') as f:
    inv_content = f.read()
    
    if "def open_chest(user_id: int, chest_id: str)" in inv_content:
        print("   ✅ Функция open_chest найдена")
    else:
        print("   ❌ Функция open_chest НЕ НАЙДЕНА!")

# 4. Проверяем handle_open_chest в game.py
print("\n4️⃣ ПРОВЕРКА handle_open_chest в game.py:")
with open('/root/bot/handlers/game.py', 'r') as f:
    game_content = f.read()
    
    if "async def handle_open_chest" in game_content:
        print("   ✅ Функция handle_open_chest найдена")
        
        # Ищем исправление в handle_open_chest
        if "endswith(\"_chest\")" in game_content and "handle_open_chest" in game_content:
            print("   ✅ Исправление chest_id в handle_open_chest найдено")
        else:
            print("   ⚠️ Исправление chest_id в handle_open_chest ОТСУТСТВУЕТ!")
    else:
        print("   ❌ Функция handle_open_chest НЕ НАЙДЕНА!")

# 5. Проверяем что отправляется в колбэке из show_chests_menu
print("\n5️⃣ ПРОВЕРКА callback_data в show_chests_menu:")
if "callback_data=f\"open_chest_{chest['id']}\"" in game_content:
    print("   ✅ callback_data формируется как open_chest_{chest['id']}")
    
    # Проверяем что такое chest['id']
    print("   📝 chest['id'] берётся из CHESTS, значит должно быть 'epic_chest'")
else:
    print("   ❌ Не найдено формирование callback_data!")

# 6. Проверяем инвентарь пользователя
print("\n6️⃣ ПРОВЕРКА ИНВЕНТАРЯ ПОЛЬЗОВАТЕЛЯ:")
import sqlite3
conn = sqlite3.connect('/root/bot/ratings.db')
c = conn.cursor()
c.execute("SELECT item_id, quantity FROM inventory WHERE user_id=185185047 AND item_id LIKE '%chest%'")
rows = c.fetchall()
if rows:
    for item_id, qty in rows:
        print(f"   📦 {item_id}: {qty} шт.")
else:
    print("   ❌ Сундуков в инвентаре нет!")
conn.close()

print("\n" + "=" * 60)
print("🏁 ПРОВЕРКА ЗАВЕРШЕНА")
print("=" * 60)
