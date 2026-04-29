"""Клавиатуры таверны — главная, кости, драки, бега, турнир"""

from telegram import InlineKeyboardButton, InlineKeyboardMarkup


def get_tavern_main_keyboard() -> InlineKeyboardMarkup:
    """Главное меню таверны"""
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🍺 Пиво", callback_data="beer_buff"),
         InlineKeyboardButton("🎯 Турнир", callback_data="dice_tournament")],
        [InlineKeyboardButton("👂 Подслушать", callback_data="tavern_eavesdrop"),
         InlineKeyboardButton("🎲 Кости", callback_data="tavern_dice")],
        [InlineKeyboardButton("🪳 Бега", callback_data="tavern_race_menu"),
         InlineKeyboardButton("👊 Подраться", callback_data="tavern_fight_menu")],
        [InlineKeyboardButton("📊 Профиль", callback_data="profile_equipment")],
        [InlineKeyboardButton("🏰 В город", callback_data="city_menu")],
    ])


# ===== КОСТИ =====

def get_bet_keyboard() -> InlineKeyboardMarkup:
    """Клавиатура выбора ставки"""
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("✏️ Своя ставка", callback_data="dice_custom_bet")],
        [InlineKeyboardButton("50 🧀", callback_data="dice_start_50"),
         InlineKeyboardButton("100 🧀", callback_data="dice_start_100"),
         InlineKeyboardButton("250 🧀", callback_data="dice_start_250")],
        [InlineKeyboardButton("500 🧀", callback_data="dice_start_500"),
         InlineKeyboardButton("1000 🧀", callback_data="dice_start_1000"),
         InlineKeyboardButton("5000 🧀", callback_data="dice_start_5000")],
        [InlineKeyboardButton("10000 🧀", callback_data="dice_start_10000"),
         InlineKeyboardButton("25000 🧀", callback_data="dice_start_25000"),
         InlineKeyboardButton("50000 🧀", callback_data="dice_start_50000")],
        [InlineKeyboardButton("🔙 Таверна", callback_data="profile_dice")],
    ])


def get_play_again_keyboard() -> InlineKeyboardMarkup:
    """Клавиатура после игры в кости"""
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🔄 Играть ещё", callback_data="dice_play_again")],
        [InlineKeyboardButton("🔙 Таверна", callback_data="profile_dice")],
    ])


def get_beer_keyboard() -> InlineKeyboardMarkup:
    """Клавиатура после пива"""
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🍺 Ещё пива", callback_data="beer_buff")],
        [InlineKeyboardButton("🔙 Таверна", callback_data="profile_dice")],
    ])


def get_custom_bet_back_keyboard() -> InlineKeyboardMarkup:
    """Клавиатура при вводе своей ставки"""
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🔙 Таверна", callback_data="profile_dice")],
    ])


# ===== ТУРНИР =====

def get_tournament_back_keyboard() -> InlineKeyboardMarkup:
    """Турнир — заглушка"""
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("📝 Записаться", callback_data="dice_tournament_join")],
        [InlineKeyboardButton("🔙 Таверна", callback_data="profile_dice")],
    ])


# ===== ДРАКИ =====

def get_fight_menu_keyboard(players: list) -> InlineKeyboardMarkup:
    """Клавиатура выбора соперника для драки"""
    keyboard = []
    for p in players:
        keyboard.append([InlineKeyboardButton(
            f"👊 {p['nickname']}",
            callback_data=f"tavern_challenge_{p['user_id']}"
        )])
    keyboard.append([InlineKeyboardButton("🔙 Таверна", callback_data="profile_dice")])
    return InlineKeyboardMarkup(keyboard)


def get_fight_active_keyboard(fight_id: str) -> InlineKeyboardMarkup:
    """Клавиатура во время драки"""
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("👊 Бить!", callback_data=f"tavern_punch_{fight_id}")],
        [InlineKeyboardButton("🛡️ Защита", callback_data=f"tavern_defend_{fight_id}")],
    ])


def get_fight_challenge_keyboard(fight_id: str) -> InlineKeyboardMarkup:
    """Принять/отклонить вызов"""
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("👊 Принять бой", callback_data=f"tavern_accept_{fight_id}")],
        [InlineKeyboardButton("🏃 Отказаться", callback_data=f"tavern_decline_{fight_id}")],
    ])


def get_fight_result_keyboard() -> InlineKeyboardMarkup:
    """После драки"""
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🔙 Таверна", callback_data="profile_dice")],
    ])


# ===== БЕГА ТАРАКАНОВ =====

def get_race_menu_keyboard() -> InlineKeyboardMarkup:
    """Выбор таракана"""
    from services.tavern_race import COCKROACHES
    keyboard = []
    row = []
    for i, roach in enumerate(COCKROACHES):
        row.append(InlineKeyboardButton(roach['name'], callback_data=f"tavern_race_pick_{roach['id']}"))
        if len(row) == 2:
            keyboard.append(row)
            row = []
    if row:
        keyboard.append(row)
    keyboard.append([InlineKeyboardButton("🔙 Таверна", callback_data="profile_dice")])
    return InlineKeyboardMarkup(keyboard)


def get_race_bet_keyboard(roach_id: str) -> InlineKeyboardMarkup:
    """Выбор ставки на таракана"""
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("✏️ Своя ставка", callback_data=f"tavern_race_custom_{roach_id}")],
        [InlineKeyboardButton("50 🧀", callback_data=f"tavern_race_start_{roach_id}_50"),
         InlineKeyboardButton("100 🧀", callback_data=f"tavern_race_start_{roach_id}_100"),
         InlineKeyboardButton("250 🧀", callback_data=f"tavern_race_start_{roach_id}_250")],
        [InlineKeyboardButton("500 🧀", callback_data=f"tavern_race_start_{roach_id}_500"),
         InlineKeyboardButton("1000 🧀", callback_data=f"tavern_race_start_{roach_id}_1000"),
         InlineKeyboardButton("5000 🧀", callback_data=f"tavern_race_start_{roach_id}_5000")],
        [InlineKeyboardButton("10000 🧀", callback_data=f"tavern_race_start_{roach_id}_10000"),
         InlineKeyboardButton("25000 🧀", callback_data=f"tavern_race_start_{roach_id}_25000"),
         InlineKeyboardButton("50000 🧀", callback_data=f"tavern_race_start_{roach_id}_50000")],
        [InlineKeyboardButton("🔙 Таверна", callback_data="profile_dice")],
    ])


def get_race_result_keyboard() -> InlineKeyboardMarkup:
    """После забега"""
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🔄 Ещё забег", callback_data="tavern_race_menu")],
        [InlineKeyboardButton("🔙 Таверна", callback_data="profile_dice")],
    ])