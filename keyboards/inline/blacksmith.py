"""Клавиатуры для кузницы"""

from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from handlers.items import ALL_ITEMS, RECIPES


def get_forge_main_keyboard(available_recipes: list, has_recipes: bool) -> InlineKeyboardMarkup:
    """Главное меню кузницы"""
    keyboard = []
    
    # Доступные рецепты как кнопки
    for recipe_id in available_recipes[:8]:
        recipe = RECIPES.get(recipe_id, {})
        cursed_mark = "💀" if recipe.get("cursed") else ""
        keyboard.append([InlineKeyboardButton(
            f"{cursed_mark}{recipe.get('icon', '📜')} {recipe.get('name', recipe_id)}",
            callback_data=f"forge_select_{recipe_id}"
        )])
    
    # Кнопки управления
    keyboard.append([
        InlineKeyboardButton("📦 Ресурсы", callback_data="forge_resources"),
        InlineKeyboardButton("📜 Рецепты", callback_data="forge_recipes"),
    ])
    keyboard.append([
        InlineKeyboardButton("🗡️ Заточка", callback_data="forge_sharpen"),
        InlineKeyboardButton("💎 Инкрустирование", callback_data="forge_engrave"),
    ])
    keyboard.append([InlineKeyboardButton("🏰 В город", callback_data="city_menu")])
    
    return InlineKeyboardMarkup(keyboard)


def get_forge_recipe_keyboard(recipe_id: str, all_have: bool) -> InlineKeyboardMarkup:
    """Клавиатура при выборе рецепта"""
    keyboard = []
    
    if all_have:
        keyboard.append([InlineKeyboardButton("⚒️ КОВАТЬ!", callback_data=f"forge_craft_{recipe_id}")])
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
    """Клавиатура для показа ресурсов"""
    keyboard = [
        [InlineKeyboardButton("🔙 К кузнице", callback_data="city_forge")],
        [InlineKeyboardButton("🏰 В город", callback_data="city_menu")],
    ]
    return InlineKeyboardMarkup(keyboard)


def get_forge_recipes_keyboard() -> InlineKeyboardMarkup:
    """Клавиатура для показа всех рецептов"""
    keyboard = [
        [InlineKeyboardButton("🔙 К кузнице", callback_data="city_forge")],
        [InlineKeyboardButton("🏰 В город", callback_data="city_menu")],
    ]
    return InlineKeyboardMarkup(keyboard)