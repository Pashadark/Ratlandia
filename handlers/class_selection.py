"""Выбор класса при достижении 10 уровня"""
from telegram import InlineKeyboardMarkup, InlineKeyboardButton

CLASS_IMAGES = {
    "warrior": "/root/bot/images/classes/class_warrior.jpg",
    "tank": "/root/bot/images/classes/class_tank.jpg",
    "mage": "/root/bot/images/classes/class_mage.jpg",
    "rogue": "/root/bot/images/classes/class_rogue.jpg",
    "berserker": "/root/bot/images/classes/class_berserker.jpg",
    "archer": "/root/bot/images/classes/class_archer.jpg",
}

CLASS_NAMES = {
    "warrior": "⚔️ Воин",
    "tank": "🛡️ Танк",
    "mage": "🔮 Маг",
    "rogue": "🗡️ Разбойник",
    "berserker": "💪 Берсерк",
    "archer": "🏹 Лучник",
}

CLASS_DESC = {
    "warrior": "+2💪 +1🍀 +1🧠\nМечи, топоры\nСредняя/тяжёлая броня",
    "tank": "+3💪 +1🍀 +50❤️\nМечи\nТяжёлая броня",
    "mage": "+1💪 +1🍀 +3🧠 +50🔮\nПосохи\nРобы",
    "rogue": "+1💪 +3🍀 +1🧠\nКинжалы, луки\nЛёгкая броня",
    "berserker": "+3💪 +2🍀 -20❤️\nМечи, топоры\nСредняя броня",
    "archer": "+1💪 +3🍀 +1🧠\nЛуки\nЛёгкая/средняя броня",
}

async def send_class_selection(context, user_id: int, is_reroll: bool = False):
    """Отправляет выбор класса"""
    text = """🎯 *ВЫБОР КЛАССА*

_Ты достиг 10 уровня! Пришло время выбрать свой путь._

⚔️ *Воин* — сбалансированный боец
🛡️ *Танк* — защитник команды
🔮 *Маг* — повелитель стихий
🗡️ *Разбойник* — мастер скрытности
💪 *Берсерк* — яростный воин
🏹 *Лучник* — мастер дальнего боя

_Выбери класс чтобы увидеть подробности:_"""

    if is_reroll:
        text = """🔄 *СМЕНА КЛАССА*

_Стоимость: 5000 🧀_

Выбери новый класс:"""

    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("⚔️ Воин", callback_data="class_info_warrior"),
         InlineKeyboardButton("🛡️ Танк", callback_data="class_info_tank")],
        [InlineKeyboardButton("🔮 Маг", callback_data="class_info_mage"),
         InlineKeyboardButton("🗡️ Разбойник", callback_data="class_info_rogue")],
        [InlineKeyboardButton("💪 Берсерк", callback_data="class_info_berserker"),
         InlineKeyboardButton("🏹 Лучник", callback_data="class_info_archer")],
    ])
    
    try:
        with open("/root/bot/images/classes/class_selection.jpg", "rb") as photo:
            await context.bot.send_photo(chat_id=user_id, photo=photo, caption=text, 
                                         parse_mode='Markdown', reply_markup=keyboard)
    except:
        await context.bot.send_message(chat_id=user_id, text=text, 
                                       parse_mode='Markdown', reply_markup=keyboard)


async def send_class_info(context, user_id: int, class_name: str, is_reroll: bool = False):
    """Показывает подробную информацию о классе"""
    text = f"""*{CLASS_NAMES[class_name]}*

_{CLASS_DESC[class_name]}_

_⚠️ Выбор нельзя изменить!_"""

    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton(f"✅ Выбрать: {CLASS_NAMES[class_name]}", 
                             callback_data=f"class_confirm_{class_name}_{1 if is_reroll else 0}")],
        [InlineKeyboardButton("🔙 Назад", callback_data="class_selection_back")],
    ])
    
    try:
        with open(CLASS_IMAGES[class_name], "rb") as photo:
            await context.bot.send_photo(chat_id=user_id, photo=photo, caption=text, 
                                         parse_mode='Markdown', reply_markup=keyboard)
    except:
        await context.bot.send_message(chat_id=user_id, text=text, 
                                       parse_mode='Markdown', reply_markup=keyboard)