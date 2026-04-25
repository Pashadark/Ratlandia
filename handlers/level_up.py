"""Обработчик повышения уровня"""

import os
from telegram import Bot, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.constants import ParseMode

def _get_token():
    env_path = "/root/bot/.env"
    if os.path.exists(env_path):
        with open(env_path) as f:
            for line in f:
                line = line.strip()
                if line.startswith('BOT_TOKEN='):
                    return line.split('=', 1)[1]
    return ""

async def send_level_up_message(context, user_id: int, new_level: int, old_level: int):
    """Отправляет сообщение о повышении уровня с картинкой и кнопками"""
    try:
        token = _get_token()
        bot = context.bot if context else Bot(token=token) if token else None
        
        if not bot:
            return
        
        text = f"🎉 *Поздравляем!*\n\n"
        text += f"Ты достиг *{new_level} уровня*!\n\n"
        text += f"🎯 Получено *1* очко характеристик!\n"
        text += f"❤️ Максимальное здоровье увеличено!\n\n"
        text += f"_Продолжай в том же духе!_"
        
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("🎯 Характеристики", callback_data="tunnel_stats_menu")],
            [InlineKeyboardButton("📊 Профиль", callback_data="profile_equipment")],
            [InlineKeyboardButton("🏙️ В город", callback_data="city_menu")]
        ])
        
        try:
            with open("/root/bot/images/level_up.jpg", "rb") as photo:
                await bot.send_photo(
                    chat_id=user_id,
                    photo=photo,
                    caption=text,
                    parse_mode=ParseMode.MARKDOWN,
                    reply_markup=keyboard
                )
        except:
            await bot.send_message(
                chat_id=user_id,
                text=text,
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=keyboard
            )
    except Exception as e:
        print(f"Ошибка отправки сообщения о повышении уровня: {e}")