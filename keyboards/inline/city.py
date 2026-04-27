"""Клавиатуры города"""
from telegram import InlineKeyboardButton, InlineKeyboardMarkup


def get_city_keyboard() -> InlineKeyboardMarkup:
    """Главное меню города"""
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("📦 Магазин", callback_data="profile_shop"),
         InlineKeyboardButton("🛡️ Гильдия", callback_data="profile_clan")],
        [InlineKeyboardButton("🎁 Ежедневная", callback_data="profile_daily"),
         InlineKeyboardButton("🍺 Таверна", callback_data="profile_dice")],
        [InlineKeyboardButton("🔨 Кузница", callback_data="city_forge"),
         InlineKeyboardButton("⛪ Церковь", callback_data="city_church")],
        [InlineKeyboardButton("🏆 Зал славы", callback_data="city_leaderboard"),
         InlineKeyboardButton("⚜️ Профиль", callback_data="back_to_profile")],
        [InlineKeyboardButton("📜 Правила", callback_data="city_rules")],
        [InlineKeyboardButton("🚪 За ворота", callback_data="city_gates")]
    ])


def get_gates_keyboard() -> InlineKeyboardMarkup:
    """Подменю 'За воротами'"""
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🕸 В туннели", callback_data="tunnel_menu")],
        [InlineKeyboardButton("🌲 леса", callback_data="gates_forest")],
        [InlineKeyboardButton("🪨 В руины", callback_data="gates_ruins")],
        [InlineKeyboardButton("⚰️ На кладбище", callback_data="city_menu")],
        [InlineKeyboardButton("🏰 В город", callback_data="city_menu")]
    ])