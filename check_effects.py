#!/usr/bin/env python3
import sys
sys.path.append('/root/bot')

print("=" * 60)
print("🔍 ПРОВЕРКА ЭФФЕКТОВ ПРЕДМЕТОВ")
print("=" * 60)

# Проверка импорта
try:
    from handlers.effects import (
        get_player_effects, apply_consumable_effect,
        process_night_kill_effects, process_survive_chance,
        process_vote_effects, process_xp_modifiers
    )
    print("✅ effects.py импортирован")
except Exception as e:
    print(f"❌ effects.py: {e}")
    sys.exit(1)

# Проверка предметов с эффектами
from handlers.items import EQUIPMENT, CONSUMABLES

print("\n📦 ПРЕДМЕТЫ С ЭФФЕКТАМИ:")
for item_id, item in EQUIPMENT.items():
    if item.get("effect"):
        print(f"  ✅ {item['icon']} {item['name']}: {list(item['effect'].keys())}")

print("\n🧪 РАСХОДНИКИ С ЭФФЕКТАМИ:")
for item_id, item in CONSUMABLES.items():
    if item.get("effect"):
        print(f"  ✅ {item['icon']} {item['name']}: {item['effect']}")

print("\n" + "=" * 60)
print("✅ ПРОВЕРКА ЗАВЕРШЕНА")
print("=" * 60)