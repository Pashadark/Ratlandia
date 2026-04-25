"""Скрипт проверки кузницы — запусти чтобы проверить что всё работает"""

import sys
sys.path.append('/root/bot')

print("=" * 60)
print("🔨 ПРОВЕРКА КУЗНИЦЫ")
print("=" * 60)

errors = []

# 1. Проверка импортов из items
print("\n1. Проверка handlers.items...")
try:
    from handlers.items import ALL_ITEMS, RECIPES, get_available_recipes, get_craft_recipe
    print(f"   ✅ ALL_ITEMS: {len(ALL_ITEMS)} предметов")
    print(f"   ✅ RECIPES: {len(RECIPES)} рецептов")
    print(f"   ✅ get_available_recipes: OK")
    print(f"   ✅ get_craft_recipe: OK")
except Exception as e:
    errors.append(f"items.py: {e}")
    print(f"   ❌ ОШИБКА: {e}")

# 2. Проверка импортов из crafting
print("\n2. Проверка handlers.crafting...")
try:
    from handlers.crafting import (
        get_player_resources, spend_materials, has_materials,
        roll_craft_dice, check_craft_success, check_craft_critical,
        get_quality_from_roll, save_crafted_item, get_craft_difficulty_info,
        CraftQuality
    )
    print(f"   ✅ get_player_resources: OK")
    print(f"   ✅ spend_materials: OK")
    print(f"   ✅ has_materials: OK")
    print(f"   ✅ roll_craft_dice: OK")
    print(f"   ✅ check_craft_success: OK")
    print(f"   ✅ check_craft_critical: OK")
    print(f"   ✅ get_quality_from_roll: OK")
    print(f"   ✅ save_crafted_item: OK")
    print(f"   ✅ get_craft_difficulty_info: OK")
    print(f"   ✅ CraftQuality: OK")
except Exception as e:
    errors.append(f"crafting.py: {e}")
    print(f"   ❌ ОШИБКА: {e}")

# 3. Проверка клавиатур
print("\n3. Проверка keyboards.inline.blacksmith...")
try:
    from keyboards.inline.blacksmith import (
        get_forge_main_keyboard, get_forge_recipe_keyboard,
        get_forge_craft_result_keyboard, get_forge_resources_keyboard
    )
    # Проверяем что функции возвращают клавиатуры
    test_main = get_forge_main_keyboard([], False)
    test_recipe = get_forge_recipe_keyboard("test", True)
    test_result = get_forge_craft_result_keyboard()
    test_resources = get_forge_resources_keyboard()
    print(f"   ✅ Все 4 клавиатуры работают")
except Exception as e:
    errors.append(f"keyboards/inline/blacksmith.py: {e}")
    print(f"   ❌ ОШИБКА: {e}")

# 4. Проверка функций кузницы
print("\n4. Проверка handlers.blacksmith...")
try:
    from handlers.blacksmith import (
        blacksmith_menu, forge_select_recipe, forge_craft,
        forge_show_resources, forge_fortune, get_user_data, update_user_data
    )
    print(f"   ✅ blacksmith_menu: OK")
    print(f"   ✅ forge_select_recipe: OK")
    print(f"   ✅ forge_craft: OK")
    print(f"   ✅ forge_show_resources: OK")
    print(f"   ✅ forge_fortune: OK")
    print(f"   ✅ get_user_data: OK")
    print(f"   ✅ update_user_data: OK")
except Exception as e:
    errors.append(f"blacksmith.py: {e}")
    print(f"   ❌ ОШИБКА: {e}")

# 5. Проверка тестового броска
print("\n5. Проверка броска кубиков...")
try:
    result = roll_craft_dice()
    print(f"   ✅ Бросок: {result} (должен быть 2-12)")
    if not (2 <= result <= 12):
        errors.append(f"Бросок вне диапазона: {result}")
        print(f"   ❌ ВНЕ ДИАПАЗОНА!")
except Exception as e:
    errors.append(f"Бросок: {e}")
    print(f"   ❌ ОШИБКА: {e}")

# 6. Проверка качества
print("\n6. Проверка качества...")
try:
    for roll in [2, 5, 8, 12, 18]:
        quality, bonuses = get_quality_from_roll(roll)
        print(f"   ✅ Бросок {roll}: {quality.display} (множитель x{quality.multiplier})")
except Exception as e:
    errors.append(f"Качество: {e}")
    print(f"   ❌ ОШИБКА: {e}")

# 7. Проверка сложности крафта
print("\n7. Проверка сложности...")
try:
    for rarity in ["common", "rare", "epic", "legendary", "mythic"]:
        diff = get_craft_difficulty_info(rarity)
        print(f"   ✅ {rarity}: мин {diff['min_roll']}, крит {diff['crit_roll']}")
except Exception as e:
    errors.append(f"Сложность: {e}")
    print(f"   ❌ ОШИБКА: {e}")

# 8. Проверка рецептов
print("\n8. Проверка рецептов...")
try:
    for recipe_id, recipe in RECIPES.items():
        result_item_id = recipe.get("result_item", "")
        result_item = ALL_ITEMS.get(result_item_id, {})
        if not result_item:
            errors.append(f"Рецепт {recipe_id}: предмет {result_item_id} не найден!")
            print(f"   ❌ {recipe['name']}: предмет {result_item_id} НЕ НАЙДЕН!")
        else:
            print(f"   ✅ {recipe['name']} → {result_item.get('name', '???')}")
except Exception as e:
    errors.append(f"Рецепты: {e}")
    print(f"   ❌ ОШИБКА: {e}")

# 9. Проверка колбэков в callbacks.py
print("\n9. Проверка callbacks.py...")
try:
    import ast
    with open("/root/bot/handlers/callbacks.py", "r") as f:
        content = f.read()
    
    checks = {
        "city_forge": "elif data == \"city_forge\":",
        "forge_select": "elif data.startswith(\"forge_select_\"):",
        "forge_craft": "elif data.startswith(\"forge_craft_\"):",
        "forge_resources": "elif data == \"forge_resources\":",
        "forge_fortune": "forge_fortune",
        "import blacksmith": "from handlers.blacksmith import",
    }
    
    for name, pattern in checks.items():
        if pattern in content:
            print(f"   ✅ {name}: найден")
        else:
            errors.append(f"callbacks.py: {name} не найден!")
            print(f"   ❌ {name}: НЕ НАЙДЕН!")
    
    # Проверка на дубликат city_forge
    count = content.count('"city_forge"')
    if count > 1:
        errors.append(f"callbacks.py: ДУБЛИКАТ city_forge ({count} раз)!")
        print(f"   ⚠️ ДУБЛИКАТ city_forge: {count} раз!")
    else:
        print(f"   ✅ Дубликатов city_forge нет")
        
except Exception as e:
    errors.append(f"callbacks.py: {e}")
    print(f"   ❌ ОШИБКА: {e}")

# 10. Проверка БД
print("\n10. Проверка БД...")
try:
    import sqlite3
    conn = sqlite3.connect("/root/bot/ratings.db")
    tables = conn.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()
    table_names = [t[0] for t in tables]
    
    required = ["inventory", "equipment", "user_data"]
    for t in required:
        if t in table_names:
            print(f"   ✅ Таблица {t}: существует")
        else:
            print(f"   ⚠️ Таблица {t}: будет создана при первом использовании")
    conn.close()
except Exception as e:
    errors.append(f"БД: {e}")
    print(f"   ❌ ОШИБКА: {e}")

# ИТОГ
print("\n" + "=" * 60)
if errors:
    print(f"❌ НАЙДЕНО ОШИБОК: {len(errors)}")
    for i, err in enumerate(errors, 1):
        print(f"   {i}. {err}")
else:
    print("✅ ВСЕ ПРОВЕРКИ ПРОЙДЕНЫ! КУЗНИЦА ГОТОВА К РАБОТЕ!")
print("=" * 60)