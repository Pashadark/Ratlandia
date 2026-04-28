"""
ПРОВЕРКА ВСЕХ ИМПОРТОВ НОВОЙ АРХИТЕКТУРЫ
Запускать из корня проекта: python tests/test_imports.py
"""

import sys
import traceback
from pathlib import Path

# Добавляем корень проекта в путь
sys.path.insert(0, str(Path(__file__).parent.parent))

errors = []
ok = 0


def check_import(module_name: str, description: str = ""):
    global ok
    try:
        __import__(module_name)
        print(f"  ✅ {module_name}")
        ok += 1
    except Exception as e:
        msg = f"  ❌ {module_name}: {e}"
        print(msg)
        errors.append((module_name, str(e), description))


print("=" * 60)
print("🧪 ТЕСТ ИМПОРТОВ АРХИТЕКТУРЫ v2")
print("=" * 60)

# ========== CORE ==========
print("\n📦 CORE:")
check_import("core")
check_import("core.database")
check_import("core.engine")
check_import("core.engine.models")
check_import("core.engine.engine_v0_1")
check_import("core.items")
check_import("core.items.models")
check_import("core.items.resources")
check_import("core.items.equipment")
check_import("core.items.weapons")
check_import("core.items.bows")
check_import("core.items.armor")
check_import("core.items.consumables")
check_import("core.items.chests")
check_import("core.items.recipes")
check_import("core.items.gems")
check_import("core.items.scrolls")
check_import("core.items.catalog")

# ========== SERVICES ==========
print("\n🛠️ SERVICES:")
check_import("services")
check_import("services.player")
check_import("services.inventory")
check_import("services.game")
check_import("services.monsters")
check_import("services.rooms")
check_import("services.blacksmith")
check_import("services.city")
check_import("services.clan")
check_import("services.achievement")

# ========== KEYBOARDS ==========
print("\n⌨️ KEYBOARDS:")
check_import("keyboards")
check_import("keyboards.inline")
check_import("keyboards.inline.city")
check_import("keyboards.inline.shop")
check_import("keyboards.inline.blacksmith")
check_import("keyboards.inline.clan")
check_import("keyboards.inline.dice")
check_import("keyboards.inline.profile")
check_import("keyboards.inline.hall_of_fame")
check_import("keyboards.inline.admin")

# ========== HANDLERS (compat) ==========
print("\n📂 HANDLERS (через compat):")
check_import("handlers.compat")
check_import("handlers.logger")
check_import("handlers.instagram")
check_import("handlers.notifications")
check_import("handlers.hall_of_fame")

# ========== HANDLERS (player) ==========
print("\n📂 HANDLERS/player:")
check_import("handlers.player")
check_import("handlers.player.commands")
check_import("handlers.player.profile")
check_import("handlers.player.inventory")
check_import("handlers.player.callbacks")
check_import("handlers.player.character")
check_import("handlers.player.class_selection")
check_import("handlers.player.items")
check_import("handlers.player.titles")

# ========== HANDLERS (city) ==========
print("\n📂 HANDLERS/city:")
check_import("handlers.city")
check_import("handlers.city.commands")
check_import("handlers.city.shop")
check_import("handlers.city.church")
check_import("handlers.city.daily")

# ========== HANDLERS (game) ==========
print("\n📂 HANDLERS/game:")
check_import("handlers.game")
check_import("handlers.game.commands")
check_import("handlers.game.battle")
check_import("handlers.game.rooms")
check_import("handlers.game.effects")
check_import("handlers.game.monsters")
check_import("handlers.game.coop")

# ========== HANDLERS (blacksmith) ==========
print("\n📂 HANDLERS/blacksmith:")
check_import("handlers.blacksmith")
check_import("handlers.blacksmith.commands")
check_import("handlers.blacksmith.crafting")
check_import("handlers.blacksmith.enchant")

# ========== HANDLERS (clan) ==========
print("\n📂 HANDLERS/clan:")
check_import("handlers.clan")
check_import("handlers.clan.commands")

# ========== HANDLERS (achievements) ==========
print("\n📂 HANDLERS/achievements:")
check_import("handlers.achievements")
check_import("handlers.achievements.commands")
check_import("handlers.achievements.data")
check_import("handlers.achievements.healing")
check_import("handlers.achievements.effects")

# ========== HANDLERS (admin, bug_report) ==========
print("\n📂 HANDLERS/admin + bug_report:")
check_import("handlers.admin")
check_import("handlers.admin.commands")
check_import("handlers.bug_report")
check_import("handlers.bug_report.commands")

# ========== КОНФИГ ==========
print("\n⚙️ CONFIG:")
check_import("config")

# ========== ИТОГИ ==========
print("\n" + "=" * 60)
total = ok + len(errors)
print(f"📊 РЕЗУЛЬТАТ: {ok}/{total} OK, {len(errors)} ошибок")

if errors:
    print(f"\n❌ ОШИБКИ ({len(errors)}):")
    for mod, err, desc in errors:
        print(f"  • {mod}")
        print(f"    {err[:120]}")
        if desc:
            print(f"    ({desc})")

if not errors:
    print("\n✅ ВСЕ ИМПОРТЫ РАБОТАЮТ!")
else:
    print(f"\n⚠️ Нужно исправить {len(errors)} импортов")

print("=" * 60)
sys.exit(len(errors))