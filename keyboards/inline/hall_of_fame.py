from telegram import InlineKeyboardButton, InlineKeyboardMarkup

def get_hall_of_fame_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🏆 Достижения", callback_data="profile_achievements"),
         InlineKeyboardButton("🎖️ Титулы", callback_data="profile_titles")],
        [InlineKeyboardButton("🏰 В город", callback_data="city_menu")],
    ])