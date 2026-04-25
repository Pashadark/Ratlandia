"""Клавиатуры магазина"""

from telegram import InlineKeyboardButton, InlineKeyboardMarkup


def get_shop_main_keyboard() -> InlineKeyboardMarkup:
    """Главное меню магазина — купить или продать"""
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🛒 Купить", callback_data="shop_buy_menu"),
         InlineKeyboardButton("💰 Продать", callback_data="shop_sell_menu")],
        [InlineKeyboardButton("🏰 В город", callback_data="city_menu")]
    ])


def get_shop_buy_keyboard() -> InlineKeyboardMarkup:
    """Меню категорий для покупки"""
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("⚔️ Оружие", callback_data="shop_cat_weapon"),
         InlineKeyboardButton("🛡️ Броня", callback_data="shop_cat_armor")],
        [InlineKeyboardButton("🎩 Шляпы", callback_data="shop_cat_head"),
         InlineKeyboardButton("💍 Аксессуары", callback_data="shop_cat_accessory")],
        [InlineKeyboardButton("🧪 Расходники", callback_data="shop_cat_consumable"),
         InlineKeyboardButton("📦 Сундуки", callback_data="shop_cat_chest")],
        [InlineKeyboardButton("🔙 Назад", callback_data="shop_back_to_main")]
    ])


def get_shop_back_keyboard() -> InlineKeyboardMarkup:
    """Кнопка назад в магазин"""
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🔙 Назад", callback_data="shop_back_to_main")]
    ])


def get_shop_category_keyboard(category: str, page: int, total_pages: int,
                               items: list, crumbs: int) -> tuple[str, InlineKeyboardMarkup]:
    """Генерирует текст и клавиатуру для категории товаров"""
    keyboard = []
    
    for item_id, item in items:
        price = item.get("price", 500)
        can_afford = crumbs >= price
        button_text = f"{item['icon']} Купить — {price} 🧀"
        if not can_afford:
            button_text = f"❌ {button_text}"
        keyboard.append([InlineKeyboardButton(button_text, callback_data=f"shop_buy_{item_id}")])
    
    # Кнопки навигации
    nav_row = []
    if page > 0:
        nav_row.append(InlineKeyboardButton("⬅️", callback_data=f"shop_page_{category}_{page-1}"))
    if page < total_pages - 1:
        nav_row.append(InlineKeyboardButton("➡️", callback_data=f"shop_page_{category}_{page+1}"))
    if nav_row:
        keyboard.append(nav_row)
    
    keyboard.append([InlineKeyboardButton("🔙 К категориям", callback_data="shop_buy_menu")])
    
    return InlineKeyboardMarkup(keyboard)