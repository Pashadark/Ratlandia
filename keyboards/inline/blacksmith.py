"""Клавиатуры для кузницы"""

from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from handlers.items import ALL_ITEMS, RECIPES


def get_forge_main_keyboard(available_recipes: list, has_recipes: bool) -> InlineKeyboardMarkup:
    """Главное меню кузницы — без списка рецептов"""
    keyboard = []
    
    # Ресурсы и Рецепты
    keyboard.append([
        InlineKeyboardButton("📦 Ресурсы", callback_data="forge_resources"),
        InlineKeyboardButton("📜 Рецепты", callback_data="forge_recipes"),
    ])
    
    # Заточка и Ковать
    keyboard.append([
        InlineKeyboardButton("🗡️ Заточка", callback_data="forge_sharpen"),
        InlineKeyboardButton("⚒️ Ковать", callback_data="forge_recipes"),
    ])
    
    # Инкрустирование
    keyboard.append([InlineKeyboardButton("💎 Инкрустирование", callback_data="forge_engrave")])
    
    # В город
    keyboard.append([InlineKeyboardButton("🏰 В город", callback_data="city_menu")])
    
    return InlineKeyboardMarkup(keyboard)


def get_forge_recipe_keyboard(recipe_id: str, all_have: bool) -> InlineKeyboardMarkup:
    """Клавиатура при выборе рецепта"""
    keyboard = []
    
    if all_have:
        keyboard.append([InlineKeyboardButton("⚒️ Ковать", callback_data=f"forge_craft_{recipe_id}")])
    else:
        keyboard.append([InlineKeyboardButton("❌ Не хватает материалов", callback_data="none")])
    
    keyboard.append([InlineKeyboardButton("🔙 К рецептам", callback_data="city_forge")])
    
    return InlineKeyboardMarkup(keyboard)


def get_forge_craft_result_keyboard() -> InlineKeyboardMarkup:
    """Клавиатура после ковки"""
    keyboard = [
        [InlineKeyboardButton("🔨 Ещё ковать", callback_data="city_forge")],
        [InlineKeyboardButton("🏰 В город", callback_data="city_menu")],
    ]
    return InlineKeyboardMarkup(keyboard)


def get_forge_resources_keyboard() -> InlineKeyboardMarkup:
    """Клавиатура для показа ресурсов по категориям"""
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("🔩 Металлы", callback_data="forge_res_cat_metal"),
            InlineKeyboardButton("🧵 Ткани", callback_data="forge_res_cat_fabric"),
        ],
        [
            InlineKeyboardButton("🦴 Кости", callback_data="forge_res_cat_bone"),
            InlineKeyboardButton("🧪 Алхимия", callback_data="forge_res_cat_alchemy"),
        ],
        [
            InlineKeyboardButton("🍖 Провизия", callback_data="forge_res_cat_food"),
            InlineKeyboardButton("🔮 Магия", callback_data="forge_res_cat_magic"),
        ],
        [
            InlineKeyboardButton("🪨 Прочее", callback_data="forge_res_cat_other"),
            InlineKeyboardButton("📦 Все", callback_data="forge_resources_all"),
        ],
        [
            InlineKeyboardButton("🔙 К кузнице", callback_data="city_forge"),
            InlineKeyboardButton("🏰 В город", callback_data="city_menu"),
        ],
    ])


def get_forge_recipes_keyboard(resources: dict = None) -> InlineKeyboardMarkup:
    """Клавиатура для показа всех рецептов с кнопками Ковать"""
    keyboard = []
    
    if resources:
        for recipe_id, recipe in RECIPES.items():
            qty = resources.get(recipe_id, 0)
            if qty > 0:
                # Проверяем хватает ли материалов
                all_have = True
                for mat_id, mat_qty in recipe["materials"].items():
                    have = resources.get(mat_id, 0)
                    if have < mat_qty:
                        all_have = False
                        break
                
                if all_have:
                    keyboard.append([InlineKeyboardButton(
                        f"⚒️ Ковать: {recipe.get('icon', '📜')} {recipe.get('name', recipe_id)}",
                        callback_data=f"forge_select_{recipe_id}"
                    )])
    
    keyboard.append([InlineKeyboardButton("🔙 К кузнице", callback_data="city_forge")])
    keyboard.append([InlineKeyboardButton("🏰 В город", callback_data="city_menu")])
    
    return InlineKeyboardMarkup(keyboard)