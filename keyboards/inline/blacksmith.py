"""Клавиатуры для кузницы"""

from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from handlers.items import ALL_ITEMS, RECIPES


def get_forge_main_keyboard(available_recipes: list, has_recipes: bool) -> InlineKeyboardMarkup:
    """Главное меню кузницы"""
    keyboard = []
    
    for recipe_id in available_recipes[:8]:
        recipe = RECIPES.get(recipe_id, {})
        cursed_mark = "💀" if recipe.get("cursed") else ""
        keyboard.append([InlineKeyboardButton(
            f"{cursed_mark}{recipe.get('icon', '📜')} {recipe.get('name', recipe_id)}",
            callback_data=f"forge_select_{recipe_id}"
        )])
    
    if not has_recipes:
        keyboard.append([InlineKeyboardButton("📜 Нет рецептов — убей мобов!", callback_data="none")])
    
    keyboard.append([InlineKeyboardButton("📦 Мои ресурсы", callback_data="forge_resources")])
    keyboard.append([InlineKeyboardButton("🔮 Гадание (5 🍞)", callback_data="forge_fortune")])
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
    """Клавиатура для показа ресурсов"""
    keyboard = [
        [InlineKeyboardButton("🔙 К кузнице", callback_data="city_forge")],
        [InlineKeyboardButton("🏰 В город", callback_data="city_menu")],
    ]
    return InlineKeyboardMarkup(keyboard)