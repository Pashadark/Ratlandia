"""Город Ратляндия"""

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from telegram import constants
import sys
sys.path.append('/root/bot')
from keyboards.inline.city import get_city_keyboard, get_gates_keyboard
from handlers.city.church import city_church_menu, church_rest, church_leave


async def city_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Главное меню города"""
    query = update.callback_query
    user_id = query.from_user.id
    
    text = f"""🏰 *ДОБРО ПОЖАЛОВАТЬ В ГОРОД*

_Ты — один из жителей этого мира. Выбери свой путь, испытай удачу и стань легендой Ратляндии!_

Выбери куда пойти:"""
    
    keyboard = get_city_keyboard()
    
    try:
        await query.message.delete()
    except:
        pass
    
    try:
        with open("/root/bot/images/city_main.jpg", "rb") as photo:
            await context.bot.send_photo(
                chat_id=user_id,
                photo=photo,
                caption=text,
                parse_mode=constants.ParseMode.MARKDOWN,
                reply_markup=keyboard
            )
    except Exception as e:
        await context.bot.send_message(
            chat_id=user_id,
            text=text,
            parse_mode=constants.ParseMode.MARKDOWN,
            reply_markup=keyboard
        )


async def city_gates_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Подменю 'За воротами'"""
    query = update.callback_query
    user_id = query.from_user.id
    
    text = f"""🚪 *ЗА ВОРОТАМИ*

_Ты стоишь у массивных дубовых ворот, ведущих в опасные земли за пределами города. Куда направишься?_"""
    
    keyboard = get_gates_keyboard()
    
    try:
        await query.message.delete()
    except:
        pass
    
    try:
        with open("/root/bot/images/gates.jpg", "rb") as photo:
            await context.bot.send_photo(
                chat_id=user_id,
                photo=photo,
                caption=text,
                parse_mode=constants.ParseMode.MARKDOWN,
                reply_markup=keyboard
            )
    except:
        await context.bot.send_message(
            chat_id=user_id,
            text=text,
            parse_mode=constants.ParseMode.MARKDOWN,
            reply_markup=keyboard
        )