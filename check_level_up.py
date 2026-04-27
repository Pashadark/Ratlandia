"""Скрипт проверки системы Level Up"""

import sys
sys.path.append('/root/bot')

print("=" * 60)
print("🔍 ПРОВЕРКА СИСТЕМЫ LEVEL UP")
print("=" * 60)

# 1. Проверка наличия файлов
import os

print("\n1. ПРОВЕРКА ФАЙЛОВ:")
if os.path.exists('/root/bot/handlers/notifications.py'):
    print("✅ handlers/notifications.py — существует")
else:
    print("❌ handlers/notifications.py — НЕ СУЩЕСТВУЕТ! Создай его!")

if os.path.exists('/root/bot/handlers/level_up.py'):
    print("⚠️ handlers/level_up.py — существует (нужно удалить!)")
else:
    print("✅ handlers/level_up.py — удалён (правильно)")

# 2. Проверка импорта
print("\n2. ПРОВЕРКА ИМПОРТОВ:")
try:
    from handlers.notifications import send_level_up_message
    print("✅ send_level_up_message — импортируется")
except Exception as e:
    print(f"❌ Ошибка импорта: {e}")

# 3. Проверка вызова в inventory.py
print("\n3. ПРОВЕРКА ВЫЗОВА В inventory.py:")
with open('/root/bot/handlers/inventory.py', 'r') as f:
    content = f.read()
    
if '_send_level_up_notification' in content:
    print("❌ Найдена СТАРАЯ функция _send_level_up_notification! Нужно удалить!")
else:
    print("✅ Старая функция удалена")

if 'send_level_up_message' in content:
    print("✅ Вызов send_level_up_message найден в add_xp")
else:
    print("❌ Вызов send_level_up_message НЕ НАЙДЕН в add_xp!")

# 4. Проверка кнопок
print("\n4. ПРОВЕРКА КНОПОК:")
with open('/root/bot/handlers/notifications.py', 'r') as f:
    notif_content = f.read()

for btn in ['tunnel_stats_menu', 'profile_equipment', 'city_menu']:
    if btn in notif_content:
        print(f"✅ Кнопка {btn} — есть")
    else:
        print(f"❌ Кнопка {btn} — НЕТ!")

# 5. Проверка что XP реально начисляется
print("\n5. ПРОВЕРКА НАЧИСЛЕНИЯ XP:")
from handlers.inventory import add_xp, get_user_xp, get_level

test_user = 185185047
old_xp = get_user_xp(test_user)
old_level = get_level(test_user)

print(f"Текущий XP: {old_xp}, Уровень: {old_level}")

# Добавляем 100 XP (не сохраняем)
level_up, new_level, old_level_result = add_xp(test_user, 100, context=None)
print(f"После +100 XP: уровень повышен = {level_up}")

# 6. Проверка триггеров
print("\n6. ПРОВЕРКА ТРИГГЕРОВ:")
triggers = []
for filename in ['game_rat.py', 'tunnel_battle.py', 'tunnel.py', 'daily.py', 'effects.py']:
    path = f'/root/bot/handlers/{filename}'
    if os.path.exists(path):
        with open(path, 'r') as f:
            if 'add_xp' in f.read():
                triggers.append(filename)

print(f"Файлы вызывающие add_xp: {triggers}")
print(f"Всего триггеров: {len(triggers)}")

print("\n" + "=" * 60)
print("✅ ПРОВЕРКА ЗАВЕРШЕНА!")
print("=" * 60)
