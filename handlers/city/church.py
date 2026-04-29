"""Церковь Подземного Ордена"""

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from telegram import constants
import sys
sys.path.append('/root/bot')

from handlers.character import get_character_stats


async def city_church_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Меню церкви"""
    query = update.callback_query
    user_id = query.from_user.id
    
    stats = enter_church(user_id, context)
    
    text = f"""⛪ *ЦЕРКОВЬ ПОДЗЕМНОГО ОРДЕНА*

_Ты входишь в тихую каменную часовню. Монахи подземного ордена молча кивают, разрешая тебе остаться. Вдоль стен горят свечи, воздух пропитан ладаном и покоем._

❤️ Здоровье: *{stats['current_health']}/{stats['max_health']}*
{get_healing_status(user_id, context)}

_«Да пребудут с тобой Хранители Туннелей», — шепчет старый монах._"""
    
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
    """Отдых в церкви — пассивное лечение 20 HP/час"""
    query = update.callback_query
    user_id = query.from_user.id
    
    if not context.user_data.get('in_church'):
        await query.answer("❌ Ты не в церкви!", show_alert=True)
        return
    
    await query.answer()
    
    heal_amount, current, maximum = restore_health_in_church(user_id, context)
    
    if heal_amount > 0:
        text = f"🙏 *Ты отдыхаешь в церкви...*\n\n"
        text += f"_Тёплый свет наполняет тело, раны затягиваются._\n\n"
        text += f"❤️ Восстановлено: *+{heal_amount}* HP\n"
        text += f"❤️ Здоровье: *{current}/{maximum}*\n"
        text += f"⛪ Лечение: 20 HP/час\n\n"
        text += f"_«Да пребудут с тобой Хранители», — доносится шёпот из алтаря._"
    else:
        text = f"🙏 *Ты отдыхаешь...*\n\n"
        text += f"_Покой и тишина окутывают тебя. Раны затягиваются сами собой._\n\n"
        text += f"❤️ Здоровье: *{current}/{maximum}*\n"
        text += f"⛪ Лечение: 20 HP/час (ожидай немного)\n\n"
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
                chat_id=user_id, photo=photo, caption=text,
                parse_mode=constants.ParseMode.MARKDOWN, reply_markup=keyboard
            )
    except:
        await context.bot.send_message(
            chat_id=user_id, text=text,
            parse_mode=constants.ParseMode.MARKDOWN, reply_markup=keyboard
        )


async def church_leave(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Покинуть церковь"""
    query = update.callback_query
    user_id = query.from_user.id
    
    leave_church(user_id, context)
    
    await query.answer("🚪 Ты покинул церковь.", show_alert=True)
    
    from handlers.city import city_menu
    await city_menu(update, context)