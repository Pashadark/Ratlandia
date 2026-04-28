#!/usr/bin/env python3
"""Проверка импортов всех актуальных модулей Ratlandia (без побочных эффектов)"""

import sys
import importlib

MODULES = [
    # Core
    "config",
    "database",
    "core.dice.engine",
    "core.dice.models",

    # Services
    "services.dice_service",
    "services.tavern_service",

    # Handlers
    "handlers.commands",
    "handlers.callbacks",
    "handlers.profile",
    "handlers.inventory",
    "handlers.items",
    "handlers.character",
    "handlers.class_selection",
    "handlers.shop",
    "handlers.daily",
    "handlers.clan",
    "handlers.dice.dice",
    "handlers.titles",
    "handlers.city",
    "handlers.blacksmith",
    "handlers.crafting",
    "handlers.enchant",
    "handlers.church",
    "handlers.healing",
    "handlers.effects",
    "handlers.achievements_data",
    "handlers.hall_of_fame",
    "handlers.tunnel",
    "handlers.tunnel_battle",
    "handlers.tunnel_monsters",
    "handlers.tunnel_rooms",
    "handlers.tunnel_coop",
    "handlers.tunnel_effects",
    "handlers.admin",
    "handlers.bug_report",
    "handlers.notifications",
    "handlers.instagram",
    "handlers.logger",

    # Keyboards
    "keyboards.inline.city",
    "keyboards.inline.shop",
    "keyboards.inline.blacksmith",
    "keyboards.inline.clan",
    "keyboards.inline.dice",
    "keyboards.inline.profile",
    "keyboards.inline.hall_of_fame",
    "keyboards.inline.admin",
]

print("=" * 60)
print("📦 ПРОВЕРКА ИМПОРТОВ ВСЕХ МОДУЛЕЙ")
print("=" * 60)

ok = 0
fail = 0

for module_name in MODULES:
    try:
        importlib.import_module(module_name)
        print(f"   ✅ {module_name}")
        ok += 1
    except Exception as e:
        print(f"   ❌ {module_name} — {str(e)[:80]}")
        fail += 1

print(f"\n{'=' * 60}")
print(f"📊 Итого: {ok} OK, {fail} FAIL из {len(MODULES)}")
print(f"{'=' * 60}")