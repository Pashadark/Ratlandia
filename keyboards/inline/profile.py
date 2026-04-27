"""Клавиатуры профиля, инвентаря, экипировки"""

from telegram import InlineKeyboardButton, InlineKeyboardMarkup


def get_profile_keyboard(user_name: str, level: int, wins: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("🎒 Инвентарь", callback_data="profile_inventory"),
            InlineKeyboardButton("🛡️ Экипировка", callback_data="profile_equipment"),
        ],
        [
            InlineKeyboardButton("📊 Характеристики", callback_data="tunnel_stats_menu"),
            InlineKeyboardButton("📜 История", callback_data="profile_history"),
        ],
        [
            InlineKeyboardButton("⚙️ Настройки", callback_data="profile_settings"),
            InlineKeyboardButton("📤 Поделиться", switch_inline_query=f"⚔️ {user_name} | ⭐ Ур.{level} | 🏆 {wins} побед | 🐀 Ратляндия"),
        ],
        [
            InlineKeyboardButton("🏰 В город", callback_data="city_menu"),
        ]
    ])


def get_inventory_keyboard(all_count: int, weapon_count: int, armor_count: int,
                           consumable_count: int, accessory_count: int,
                           total_chests: int) -> InlineKeyboardMarkup:
    """Клавиатура инвентаря"""
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton(f"📦 Всё ({all_count})", callback_data="inventory_filter_all"),
            InlineKeyboardButton(f"⚔️ Оружие ({weapon_count})", callback_data="inventory_filter_weapon")
        ],
        [
            InlineKeyboardButton(f"🛡️ Одежда ({armor_count})", callback_data="inventory_filter_armor"),
            InlineKeyboardButton(f"🧪 Расходники ({consumable_count})", callback_data="inventory_filter_consumable")
        ],
        [
            InlineKeyboardButton(f"💍 Аксессуары ({accessory_count})", callback_data="inventory_filter_accessory"),
            InlineKeyboardButton(f"📦 Сундуки ({total_chests})", callback_data="chests_menu")
        ],
        [
            InlineKeyboardButton("👑 Профиль", callback_data="back_to_profile"),
            InlineKeyboardButton("🏰 Город", callback_data="city_menu")
        ]
    ])


def get_equipment_keyboard() -> InlineKeyboardMarkup:
    """Клавиатура экипировки"""
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("🎩 Шлемы", callback_data="equipment_list_head"),
            InlineKeyboardButton("⚔️ Оружие", callback_data="equipment_list_weapon"),
        ],
        [
            InlineKeyboardButton("🛡️ Броня", callback_data="equipment_list_armor"),
            InlineKeyboardButton("💍 Аксессуары", callback_data="equipment_list_accessory"),
        ],
        [
            InlineKeyboardButton("👑 Профиль", callback_data="back_to_profile")
        ]
    ])


def get_equipment_slots_keyboard() -> InlineKeyboardMarkup:
    """Клавиатура слотов экипировки (для списка предметов)"""
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("🎩 Шлемы", callback_data="equipment_list_head"),
            InlineKeyboardButton("⚔️ Оружие", callback_data="equipment_list_weapon"),
        ],
        [
            InlineKeyboardButton("🛡️ Броня", callback_data="equipment_list_armor"),
            InlineKeyboardButton("💍 Аксессуары", callback_data="equipment_list_accessory"),
        ],
        [
            InlineKeyboardButton("🛡️ К экипировке", callback_data="profile_equipment"),
            InlineKeyboardButton("👑 Профиль", callback_data="back_to_profile")
        ]
    ])


def get_achievements_keyboard(show_all: bool = False) -> InlineKeyboardMarkup:
    """Клавиатура достижений"""
    if show_all:
        return InlineKeyboardMarkup([
            [InlineKeyboardButton("Свернуть", callback_data="achievements_compact")],
            [InlineKeyboardButton("В профиль", callback_data="back_to_profile")]
        ])
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🎖 Все достижения", callback_data="achievements_all")],
        [InlineKeyboardButton("👑 Профиль", callback_data="back_to_profile")]
    ])


def get_item_card_keyboard(item_id: str, item_type: str, slot: str = None,
                           is_equipped: bool = False) -> InlineKeyboardMarkup:
    """Клавиатура карточки предмета"""
    keyboard = []
    
    if item_type == "equipment":
        if not is_equipped:
            keyboard.append([InlineKeyboardButton("✅ НАДЕТЬ", callback_data=f"equip_{item_id}")])
        else:
            keyboard.append([InlineKeyboardButton("🗑️ СНЯТЬ", callback_data=f"unequip_{slot}")])
    elif item_type == "chest":
        keyboard.append([InlineKeyboardButton("📦 ОТКРЫТЬ", callback_data=f"open_chest_{item_id}")])
    elif item_type == "consumable":
        keyboard.append([InlineKeyboardButton("🧪 ИСПОЛЬЗОВАТЬ", callback_data=f"use_consumable_{item_id}")])
    
    keyboard.append([
        InlineKeyboardButton("🛡️ К ЭКИПИРОВКЕ", callback_data="profile_equipment"),
        InlineKeyboardButton("🎒 В ИНВЕНТАРЬ", callback_data="profile_inventory")
    ])
    
    return InlineKeyboardMarkup(keyboard)