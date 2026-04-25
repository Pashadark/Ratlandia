"""Клавиатуры таверны"""
from telegram import InlineKeyboardButton, InlineKeyboardMarkup


def get_bet_keyboard() -> InlineKeyboardMarkup:
    """Клавиатура выбора ставки"""
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("💰 50 🧀", callback_data="dice_start_50"),
         InlineKeyboardButton("💰 100 🧀", callback_data="dice_start_100")],
        [InlineKeyboardButton("💰 250 🧀", callback_data="dice_start_250"),
         InlineKeyboardButton("💰 500 🧀", callback_data="dice_start_500")],
        [InlineKeyboardButton("🍺 Пиво (50 🧀)", callback_data="beer_buff")],
        [InlineKeyboardButton("🏆 Турнир", callback_data="dice_tournament")],
        [InlineKeyboardButton("✏️ Своя ставка", callback_data="dice_custom_bet")],
        [InlineKeyboardButton("🔙 В город", callback_data="city_menu")]
    ])


def get_play_again_keyboard() -> InlineKeyboardMarkup:
    """Клавиатура после игры"""
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🎲 Играть снова", callback_data="dice_play_again")],
        [InlineKeyboardButton("🔙 В таверну", callback_data="profile_dice")]
    ])


def get_beer_keyboard() -> InlineKeyboardMarkup:
    """Клавиатура после пива"""
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🍺 Выпить ещё", callback_data="beer_buff")],
        [InlineKeyboardButton("🎲 Играть", callback_data="profile_dice")],
        [InlineKeyboardButton("🏰 В город", callback_data="city_menu")]
    ])


def get_tournament_back_keyboard() -> InlineKeyboardMarkup:
    """Клавиатура возврата из турнира"""
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🔙 В таверну", callback_data="profile_dice")]
    ])


def get_custom_bet_back_keyboard() -> InlineKeyboardMarkup:
    """Клавиатура при вводе своей ставки"""
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🔙 Назад", callback_data="profile_dice")]
    ])