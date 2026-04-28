#!/usr/bin/env python3
"""Проверяет наличие всех команд из /help в обработчиках main.py"""
import re

with open('/root/bot/main.py', 'r') as f:
    content = f.read()

# Все команды из /help
commands = [
    "/city", "/start", "/profile", "/inventory", "/equipment",
    "/shop", "/daily", "/crumbs", "/tunnel", "/tunnel_stats",
    "/tunnel_run", "/forge", "/forge_resources", "/forge_recipes",
    "/forge_sharpen", "/church", "/clan", "/clan_top", "/clan_create",
    "/achievements", "/titles", "/history", "/dice", "/top"
]

print("=" * 60)
print("🔍 ПРОВЕРКА КОМАНД В main.py")
print("=" * 60)

found = []
missing = []

for cmd in commands:
    cmd_name = cmd.replace("/", "")
    # Ищем CommandHandler(f"command", ...) или pattern
    if f'CommandHandler("{cmd_name}"' in content or f"CommandHandler('{cmd_name}'" in content:
        found.append(cmd)
        print(f"  ✅ {cmd}")
    else:
        missing.append(cmd)
        print(f"  ❌ {cmd} — НЕ НАЙДЕН!")

print(f"\n📊 Итого: {len(found)} найдено, {len(missing)} не хватает")

if missing:
    print(f"\n❌ ОТСУТСТВУЮТ: {', '.join(missing)}")
    print("\n📝 Нужно добавить в main.py:")
    for cmd in missing:
        cmd_name = cmd.replace("/", "")
        print(f'    app.add_handler(CommandHandler("{cmd_name}", {cmd_name}_command))')
else:
    print("\n✅ ВСЕ КОМАНДЫ НА МЕСТЕ!")
