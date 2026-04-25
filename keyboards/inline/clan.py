"""Клавиатуры гильдии"""
from telegram import InlineKeyboardButton, InlineKeyboardMarkup


def get_clan_main_keyboard() -> InlineKeyboardMarkup:
    """Главное меню гильдии"""
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🏗️ Создать", callback_data="clan_create_menu")],
        [InlineKeyboardButton("⚙️ Управление", callback_data="clan_manage")],
        [InlineKeyboardButton("📊 Топ кланов", callback_data="clan_top"),
         InlineKeyboardButton("🔙 В город", callback_data="city_menu")]
    ])


def get_clan_create_keyboard() -> InlineKeyboardMarkup:
    """Меню создания клана"""
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("✅ Зарегистрировать (1000 🧀)", callback_data="clan_register")],
        [InlineKeyboardButton("🔙 Назад", callback_data="profile_clan")]
    ])


def get_clan_manage_no_clan_keyboard() -> InlineKeyboardMarkup:
    """Управление — не в клане"""
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🔍 Вступить", callback_data="clan_join_menu")],
        [InlineKeyboardButton("🔙 Назад", callback_data="profile_clan")]
    ])


def get_clan_manage_member_keyboard(has_leader: bool = False) -> InlineKeyboardMarkup:
    """Управление — в клане (участник или лидер)"""
    keyboard = [
        [InlineKeyboardButton("📋 Участники", callback_data="clan_members"),
         InlineKeyboardButton("🔗 Пригласить", switch_inline_query="Вступай в клан!")],
        [InlineKeyboardButton("⭐ Повысить", callback_data="clan_promote_select"),
         InlineKeyboardButton("⭐ Понизить", callback_data="clan_demote_select")],
        [InlineKeyboardButton("⚔️ Войны", callback_data="clan_wars"),
         InlineKeyboardButton("🏆 Достижения", callback_data="clan_achievements")],
    ]
    if has_leader:
        keyboard.append([InlineKeyboardButton("🗑️ Распустить", callback_data="clan_disband")])
    else:
        keyboard.append([InlineKeyboardButton("🚪 Покинуть", callback_data="clan_leave")])
    keyboard.append([InlineKeyboardButton("🔙 Назад", callback_data="profile_clan")])
    return InlineKeyboardMarkup(keyboard)


def get_clan_join_keyboard() -> InlineKeyboardMarkup:
    """Вступить в клан"""
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🔙 Назад", callback_data="clan_manage")]
    ])


def get_clan_back_keyboard() -> InlineKeyboardMarkup:
    """Кнопка назад к гильдии"""
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🔙 К гильдии", callback_data="profile_clan")]
    ])