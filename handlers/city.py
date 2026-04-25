"""Город Ратляндия"""

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from telegram import constants
import sys
sys.path.append('/root/bot')
from keyboards.inline.city import get_city_keyboard, get_gates_keyboard
from handlers.healing import enter_church, leave_church, get_healing_status, restore_health_in_church, get_healing_status
from handlers.character import get_character_stats


async def city_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Главное меню города"""
    query = update.callback_query
    user_id = query.from_user.id
    
    text = f"""🏰 *ДОБРО ПОЖАЛОВАТЬ В ГОРОД*

_Ты — один из жителей этого мира. Выбери свой путь, испытай удачу и стань легендой Ратляндии!_

Выбери куда пойти:"""
    
    keyboard = get_city_keyboard()
    
    await query.message.delete()
    
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

async def city_church_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Меню церкви — лечебный покой"""
    query = update.callback_query
    user_id = query.from_user.id
    
    # Входим в церковь
    stats = enter_church(user_id, context)
    
    text = f"""⛪ *ЦЕРКОВЬ ПОДЗЕМНОГО ОРДЕНА*

_Ты входишь в тихую каменную часовню. Монахи подземного ордена молча кивают, разрешая тебе остаться. Вдоль стен горят свечи, воздух пропитан ладаном и покоем. Твои раны затягиваются быстрее в этом священном месте._

❤️ Здоровье: *{stats['current_health']}/{stats['max_health']}*
{get_healing_status(user_id, context)}

_«Да пребудут с тобой Хранители Туннелей», — шепчет старый монах, проходя мимо._"""
    
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("🛌 Отдыхать", callback_data="church_rest")],
        [InlineKeyboardButton("🚪 Покинуть церковь", callback_data="church_leave")],
    ])
    
    await query.message.delete()
    
    try:
        with open("/root/bot/images/church.jpg", "rb") as photo:
            await context.bot.send_photo(
                chat_id=user_id, photo=photo, caption=text,
                parse_mode=constants.ParseMode.MARKDOWN, reply_markup=keyboard
            )
    except:
        await context.bot.send_message(
            chat_id=user_id, text=text,
            parse_mode=constants.ParseMode.MARKDOWN, reply_markup=keyboard
        )


async def church_rest(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Отдых в церкви — восстановление здоровья"""
    query = update.callback_query
    user_id = query.from_user.id
    
    if not context.user_data.get('in_church'):
        await query.answer("❌ Ты не в церкви!", show_alert=True)
        return
    
    await query.answer()
    
    heal_amount, current, maximum = restore_health_in_church(user_id, context)
    
    if heal_amount > 0:
        text = f"🙏 *Ты возносишь молитву Хранителям Туннелей...*\n\n"
        text += f"_Тёплый свет наполняет тело, раны затягиваются._\n\n"
        text += f"❤️ Восстановлено: *+{heal_amount}* HP\n"
        text += f"❤️ Здоровье: *{current}/{maximum}*\n"
        text += f"⚡ Лечение x2 (+20 HP/час) ⛪\n\n"
        text += f"_«Да пребудут с тобой Хранители», — доносится шёпот из алтаря._"
    else:
        text = f"🙏 *Ты отдыхаешь...*\n\n"
        text += f"_Покой и тишина окутывают тебя._\n\n"
        text += f"❤️ Здоровье: *{current}/{maximum}* — полностью восстановлено!\n\n"
        text += f"_«Ступай с миром, дитя», — кивает старый монах._"
    
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("🛌 Ещё отдыхать", callback_data="church_rest")],
        [InlineKeyboardButton("🚪 Покинуть церковь", callback_data="church_leave")],
    ])
    
    try:
        await query.message.delete()
    except:
        pass
    
    try:
        with open("/root/bot/images/church_rest.jpg", "rb") as photo:
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


async def church_leave(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Покинуть церковь — сброс бонуса лечения"""
    query = update.callback_query
    user_id = query.from_user.id
    
    leave_church(user_id, context)
    
    await query.answer("🚪 Ты покинул церковь. Лечение вернулось к обычной скорости.", show_alert=True)
    await city_menu(update, context)

async def city_gates_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Подменю 'За воротами'"""
    query = update.callback_query
    user_id = query.from_user.id
    
    text = f"""🚪 *ЗА ВОРОТАМИ*

_Ты стоишь у массивных дубовых ворот, ведущих в опасные земли за пределами города. Куда направишься?_"""
    
    keyboard = get_gates_keyboard()
    
    await query.message.delete()
    
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