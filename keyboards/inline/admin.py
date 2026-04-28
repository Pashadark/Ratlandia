"""Клавиатуры админ-панели"""

from telegram import InlineKeyboardButton, InlineKeyboardMarkup


def get_admin_keyboard() -> InlineKeyboardMarkup:
    """Главная админ-панель"""
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("💚 Вылечить всех", callback_data="admin_heal_all")],
        [InlineKeyboardButton("🧀 Дать крошки (+100)", callback_data="admin_crumbs_all")],
        [InlineKeyboardButton("🚫 Заблокировать/разблокировать", callback_data="admin_ban_list")],
        [InlineKeyboardButton("📊 Статистика", callback_data="admin_stats")],
        [InlineKeyboardButton("🔙 Закрыть", callback_data="back_to_profile")]
    ])


def get_ban_list_keyboard(users: list) -> InlineKeyboardMarkup:
    """Клавиатура со списком игроков для бана"""
    keyboard = []
    
    for uid, nick, banned in users:
        status = "🔴" if banned else "🟢"
        action = "unban" if banned else "ban"
        keyboard.append([InlineKeyboardButton(
            f"{status} {nick}",
            callback_data=f"admin_{action}_{uid}"
        )])
    
    keyboard.append([InlineKeyboardButton("🔙 В админ-панель", callback_data="admin_panel")])
    
    return InlineKeyboardMarkup(keyboard)