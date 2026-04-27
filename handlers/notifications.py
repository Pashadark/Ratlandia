"""Единый сервис уведомлений — все сообщения бота здесь"""

import os
from telegram import Bot, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.constants import ParseMode


def _get_token():
    """Получает токен из .env"""
    env_path = "/root/bot/.env"
    if os.path.exists(env_path):
        with open(env_path) as f:
            for line in f:
                line = line.strip()
                if line.startswith('BOT_TOKEN='):
                    return line.split('=', 1)[1]
    return ""


async def send_level_up_message(context, user_id: int, new_level: int, old_level: int):
    """Отправляет сообщение о повышении уровня"""
    try:
        token = _get_token()
        bot = context.bot if context else Bot(token=token) if token else None
        
        if not bot:
            return
        
        text = (
            f"🎉 *Уровень повышен!*\n\n"
            f"⭐ Ты достиг *{new_level} уровня*!\n"
            f"🎯 Получено *1* очко характеристик!\n"
            f"❤️ Максимальное здоровье +10!\n\n"
            f"_Продолжай в том же духе!_"
        )
        
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
        print(f"Ошибка отправки уведомления о повышении уровня: {e}")


async def send_achievement_unlocked(context, user_id: int, achievement: dict):
    """Отправляет уведомление о новом достижении"""
    try:
        token = _get_token()
        bot = context.bot if context else Bot(token=token) if token else None
        
        if not bot:
            return
        
        text = (
            f"🏆 *ДОСТИЖЕНИЕ РАЗБЛОКИРОВАНО!*\n\n"
            f"**{achievement.get('name', 'Достижение')}**\n"
            f"_{achievement.get('desc', '')}_\n\n"
            f"✨ +{achievement.get('xp', 0)} XP"
        )
        
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("🏆 Все достижения", callback_data="profile_achievements")]
        ])
        
        try:
            with open("/root/bot/images/achievement.jpg", "rb") as photo:
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
        print(f"Ошибка отправки уведомления о достижении: {e}")


async def send_item_received(context, user_id: int, item: dict):
    """Отправляет уведомление о получении предмета"""
    try:
        token = _get_token()
        bot = context.bot if context else Bot(token=token) if token else None
        
        if not bot:
            return
        
        icon = item.get('icon', '📦')
        name = item.get('name', 'Предмет')
        desc = item.get('desc', '')
        rarity = item.get('rarity', 'common')
        
        rarity_colors = {
            "common": "⚪",
            "rare": "🔵",
            "epic": "🟣",
            "legendary": "🟡",
            "mythic": "🔴",
        }
        
        text = (
            f"🎁 *Получен предмет!*\n\n"
            f"{icon} **{name}**\n"
            f"{rarity_colors.get(rarity, '⚪')} {rarity.upper()}\n"
            f"_{desc}_"
        )
        
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("🎒 Инвентарь", callback_data="profile_inventory")]
        ])
        
        try:
            with open("/root/bot/images/item_drop.jpg", "rb") as photo:
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
        print(f"Ошибка отправки уведомления о предмете: {e}")