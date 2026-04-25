#!/usr/bin/env python3
"""Проверка наличия всех картинок для Ратляндии"""

import os

print("=" * 60)
print("🖼️ ПРОВЕРКА КАРТИНОК РАТЛЯНДИИ")
print("=" * 60)

IMAGES_DIR = "/root/bot/images"

# Список всех нужных картинок
REQUIRED_IMAGES = [
    "mice_win.jpg",      # 1. Победа мышей
    "rat_win.jpg",       # 2. Победа крысы
    "night.jpg",         # 3. Ночь
    "day.jpg",           # 4. День
    "voting.jpg",        # 5. Голосование
    "rat_kill.jpg",      # 6. Убийство
    "role_cards.jpg",    # 7. Раздача ролей
    "item_drop.jpg",     # 8. Получение предмета
    "leaderboard.jpg",   # 9. Топ игроков
    "profile.jpg",       # 10. Профиль
    "achievement.jpg",   # 11. Достижение
    "lobby.jpg",         # 12. Лобби
    "inventory.jpg",     # 13. Инвентарь (опционально)
    "equipment.jpg",     # 14. Экипировка (опционально)
]

print("\n📁 ПАПКА: /root/bot/images\n")

found = []
missing = []
sizes = []

for img in REQUIRED_IMAGES:
    path = os.path.join(IMAGES_DIR, img)
    if os.path.exists(path):
        size = os.path.getsize(path)
        size_kb = size / 1024
        found.append(img)
        sizes.append((img, size_kb))
        print(f"✅ {img:<20} ({size_kb:.1f} KB)")
    else:
        missing.append(img)
        print(f"❌ {img:<20} - ОТСУТСТВУЕТ")

print("\n" + "=" * 60)
print(f"📊 ИТОГ: {len(found)}/{len(REQUIRED_IMAGES)} картинок найдено")
print("=" * 60)

if missing:
    print("\n❌ ОТСУТСТВУЮТ:")
    for m in missing:
        print(f"   - {m}")

# Проверка папки
if not os.path.exists(IMAGES_DIR):
    print(f"\n❌ ПАПКА {IMAGES_DIR} НЕ СУЩЕСТВУЕТ!")
    print("   Создай: mkdir -p /root/bot/images")
else:
    all_files = os.listdir(IMAGES_DIR)
    images = [f for f in all_files if f.endswith(('.jpg', '.jpeg', '.png'))]
    print(f"\n📸 ВСЕГО КАРТИНОК В ПАПКЕ: {len(images)}")
    
    # Лишние файлы
    extra = set(images) - set(REQUIRED_IMAGES)
    if extra:
        print("\n⚠️ ЛИШНИЕ ФАЙЛЫ:")
        for e in extra:
            print(f"   - {e}")

print("\n" + "=" * 60)

# Проверка импорта в код
print("\n🔧 ПРОВЕРКА ИСПОЛЬЗОВАНИЯ В КОДЕ:")
import sys
sys.path.append('/root/bot')

try:
    from handlers.game import active_games
    print("✅ game.py импортирован")
except Exception as e:
    print(f"❌ game.py: {e}")

try:
    from handlers.profile import profile_command
    print("✅ profile.py импортирован")
except Exception as e:
    print(f"❌ profile.py: {e}")

try:
    from handlers.commands import rat_top
    print("✅ commands.py импортирован")
except Exception as e:
    print(f"❌ commands.py: {e}")

try:
    from handlers.callbacks import button_callback
    print("✅ callbacks.py импортирован")
except Exception as e:
    print(f"❌ callbacks.py: {e}")

print("\n" + "=" * 60)
print("✅ ПРОВЕРКА ЗАВЕРШЕНА!")
print("=" * 60)
