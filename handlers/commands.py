from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from telegram import constants
from handlers.inventory import get_crumbs, get_user_xp, get_level_from_xp, get_inventory, get_level_progress
import sys
import re
import sqlite3
sys.path.append('/root/bot')
from database import get_rating, get_top_players
from handlers.titles import get_active_title
import logging
logger = logging.getLogger(__name__)

def escape_markdown(text: str) -> str:
    if not text:
        return ""
    escape_chars = r'_*[]()~`>#+-=|{}.!'
    return re.sub(f'([{re.escape(escape_chars)}])', r'\\\1', text)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Приветствие и запрос ника"""
    user = update.effective_user
    user_id = user.id
    first_name = user.first_name or "путник"
    
    rating = get_rating(user_id)
    nickname = rating.get("nickname") if rating else None
    
    # ========== ЕСЛИ НЕТ НИКА — ЗАПРАШИВАЕМ ==========
    if not nickname:
        text = (
            f"_Из тёмного угла подземелья на тебя смотрит старая крыса. "
            f"Её усы дёргаются, а левый глаз прищурен._\n\n"
            f"🐀 *«Как тебя звать, путник?»*\n"
            f"_Напиши свой ник в ответ на это сообщение._"
        )
        
        context.user_data["awaiting_nickname"] = True
        
        try:
            with open("/root/bot/images/start_name.jpg", "rb") as photo:
                await update.message.reply_photo(
                    photo=photo,
                    caption=text,
                    parse_mode=constants.ParseMode.MARKDOWN
                )
        except:
            await update.message.reply_text(text, parse_mode=constants.ParseMode.MARKDOWN)
        return
    
    # ========== ЕСЛИ НИК ЕСТЬ — ПРИВЕТСТВУЕМ ==========
    display_name = nickname
    
    # Получаем титул
    active_title = get_active_title(user_id)
    title_text = active_title["name"] if active_title else "🌱 Новичок"
    
    # Статистика
    if rating:
        xp = get_user_xp(user_id)
        level = get_level_from_xp(xp)
        crumbs = get_crumbs(user_id)
        _, xp_in_level, xp_needed = get_level_progress(xp)
        inventory = get_inventory(user_id)
        items_count = sum(inventory.values()) if inventory else 0
    else:
        level = 1
        crumbs = 0
        xp_in_level = 0
        xp_needed = 100
        items_count = 0
    
    text = (
        f"⚔️ *Приветствую тебя, путник!* ⚔️\n\n"
        f"_Сырые стены канализации помнят твои шаги. Крысы шепчутся в тени, а мыши смотрят с надеждой. "
        f"Ты вернулся в Подземное Царство, и ветер туннелей вновь зовёт тебя в бой._\n\n"
        f"⚔️ {escape_markdown(display_name)} | {title_text}\n"
        f"⭐ Уровень {level} | 🧀 {crumbs} крошек\n"
        f"✨ Опыт: {xp_in_level}/{xp_needed} XP\n"
        f"🎒 Предметов: {items_count}\n\n"
        f"🛡️ *Да начнётся охота!*"
    )
    
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("Зайти в город", callback_data="city_menu")]
    ])
    
    try:
        with open("/root/bot/images/start.jpg", "rb") as photo:
            await update.message.reply_photo(
                photo=photo,
                caption=text,
                parse_mode=constants.ParseMode.MARKDOWN,
                reply_markup=keyboard
            )
    except:
        await update.message.reply_text(
            text,
            parse_mode=constants.ParseMode.MARKDOWN,
            reply_markup=keyboard
        )


async def handle_nickname_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обрабатывает ввод ника после /start"""
    if not context.user_data.get("awaiting_nickname"):
        return
    
    user_id = update.effective_user.id
    nickname = update.message.text.strip()[:20]
    
    if len(nickname) < 2:
        await update.message.reply_text("❌ Ник должен быть не короче 2 символов!\nПопробуй ещё раз:")
        return
    
    # СРАЗУ СБРАСЫВАЕМ ФЛАГ
    context.user_data["awaiting_nickname"] = False
    
    try:
        conn = sqlite3.connect("/root/bot/ratings.db")
        c = conn.cursor()
        
        c.execute("SELECT user_id FROM ratings WHERE user_id = ?", (user_id,))
        if c.fetchone():
            c.execute("UPDATE ratings SET nickname = ? WHERE user_id = ?", (nickname, user_id))
        else:
            c.execute("INSERT INTO ratings (user_id, name, nickname) VALUES (?, ?, ?)", 
                      (user_id, update.effective_user.full_name, nickname))
        conn.commit()
        conn.close()
    except Exception as e:
        logger.error(f"Ошибка сохранения ника: {e}")
        # Даже при ошибке — показываем приветствие
        pass
    
    text = (
        f"🐀 *Приятно познакомиться, {escape_markdown(nickname)}!*\n\n"
        f"_Добро пожаловать в Подземное Царство! Твоё имя записано в Книге Крыс._\n\n"
        f"🛡️ *Да начнётся охота, {escape_markdown(nickname)}!*"
    )
    
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("🏰 ЗАЙТИ В ГОРОД", callback_data="city_menu")]
    ])
    
    try:
        with open("/root/bot/images/start.jpg", "rb") as photo:
            await update.message.reply_photo(
                photo=photo,
                caption=text,
                parse_mode=constants.ParseMode.MARKDOWN,
                reply_markup=keyboard
            )
    except Exception as e:
        logger.error(f"Ошибка отправки приветствия: {e}")
        await update.message.reply_text(
            text,
            parse_mode=constants.ParseMode.MARKDOWN,
            reply_markup=keyboard
        )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_name = update.effective_user.full_name
    
    text = (
        f"📖 *СВИТОК ЗНАНИЙ, {escape_markdown(user_name)}*\n\n"
        f"🏰 *ГОРОД*\n"
        f"├─ /city — главное меню города\n"
        f"├─ /profile — твой профиль и статистика\n"
        f"├─ /inventory — рюкзак со всеми предметами\n"
        f"├─ /equipment — надеть или снять предметы\n"
        f"├─ /shop — купить редкие товары за крошки\n"
        f"├─ /daily — ежедневная награда\n"
        f"└─ /crumbs — твой баланс крошек\n\n"
        f"🕳️ *ТУННЕЛИ*\n"
        f"├─ /tunnel — спуститься в туннели\n"
        f"├─ /tunnel\\_stats — прокачка характеристик\n"
        f"└─ /tunnel\\_run — начать забег\n\n"
        f"⚒️ *КУЗНИЦА И ЦЕРКОВЬ*\n"
        f"├─ /forge — кузница (крафт и заточка)\n"
        f"└─ /church — отдых и восстановление здоровья\n\n"
        f"👥 *КЛАНЫ*\n"
        f"└─ /clan — твой клан, топ, создать новый\n\n"
        f"🏆 *ДОСТИЖЕНИЯ*\n"
        f"├─ /achievements — все достижения\n"
        f"├─ /titles — твои титулы\n"
        f"└─ /history — последние действия\n\n"
        f"🎲 *ТАВЕРНА*\n"
        f"└─ /dice — игра в кости на крошки\n\n"
        f"🏆 *СТАТИСТИКА*\n"
        f"└─ /top — лучшие игроки\n"
        f"⚔️ *Удачной охоты!*"
    )
    
    await update.message.reply_text(text, parse_mode=constants.ParseMode.MARKDOWN)
    
    await update.message.reply_text(text, parse_mode=constants.ParseMode.MARKDOWN)


async def rat_top(update: Update, context: ContextTypes.DEFAULT_TYPE):
    from handlers.clan import get_user_clan
    
    top = get_top_players(10)
    if not top:
        text = "📊 Зал славы пока пустует... Стань первым героем!"
        if update.callback_query:
            await update.callback_query.message.delete()
            await context.bot.send_message(
                chat_id=update.callback_query.from_user.id,
                text=text
            )
        else:
            await update.message.reply_text(text)
        return
    
    text = f"""🏆 *ЗАЛ СЛАВЫ*

_Здесь, на древних стенах из сырного камня, высечены имена величайших воинов Подземного Царства. Крысы и мыши, герои и злодеи — все они сражались за место в истории. Их подвиги помнят туннели, их имена шепчет ветер канализации. Сможешь ли ты подняться на вершину и оставить свой след?_

"""
    
    medals = ["🥇", "🥈", "🥉"]
    for i, p in enumerate(top):
        pid = p['user_id']
        name = escape_markdown(p['name'][:20])
        wins = p['wins']
        games = p['games']
        winrate = round(wins / games * 100) if games > 0 else 0
        
        active_title = get_active_title(pid)
        title_icon = active_title["icon"] if active_title else ""
        title_name = active_title["name"] if active_title else ""
        title_str = f"{title_icon} {title_name}".strip()
        
        clan = get_user_clan(pid)
        clan_tag = f" [{clan['tag']}]" if clan else ""
        
        if i < 3:
            text += f"{medals[i]} *{name}*{clan_tag}\n"
            if title_str:
                text += f"   {title_str}\n"
            text += f"   🏆{wins}  🎮{games}  📊{winrate}%\n\n"
        else:
            text += f"{i+1}. *{name}*{clan_tag}\n"
            if title_str:
                text += f"   {title_str}\n"
            text += f"   🏆{wins}  🎮{games}  📊{winrate}%\n\n"
    
    text += "⚔️ *Сразись и впиши своё имя в историю!*"
    
    keyboard = [[InlineKeyboardButton("🔙 В город", callback_data="city_menu")]]
    
    if update.callback_query:
        query = update.callback_query
        await query.message.delete()
        try:
            with open("/root/bot/images/leaderboard.jpg", "rb") as photo:
                await context.bot.send_photo(
                    chat_id=query.from_user.id,
                    photo=photo,
                    caption=text,
                    parse_mode=constants.ParseMode.MARKDOWN,
                    reply_markup=InlineKeyboardMarkup(keyboard)
                )
        except:
            await context.bot.send_message(
                chat_id=query.from_user.id,
                text=text,
                parse_mode=constants.ParseMode.MARKDOWN,
                reply_markup=InlineKeyboardMarkup(keyboard)
            )
    else:
        try:
            with open("/root/bot/images/leaderboard.jpg", "rb") as photo:
                await update.message.reply_photo(
                    photo=photo,
                    caption=text,
                    parse_mode=constants.ParseMode.MARKDOWN,
                    reply_markup=InlineKeyboardMarkup(keyboard)
                )
        except:
            await update.message.reply_text(text, parse_mode=constants.ParseMode.MARKDOWN, reply_markup=InlineKeyboardMarkup(keyboard))

async def crumbs_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user_name = update.effective_user.full_name
    
    r = get_rating(user_id)
    display_name = r.get("nickname") if r else user_name
    
    crumbs = get_crumbs(user_id)
    
    if crumbs == 0:
        text = f"🧀 *{escape_markdown(display_name)}*, твой кошелёк пуст...\nСыграй в Ратляндию, чтобы заработать крошки!"
    elif crumbs < 100:
        text = f"🧀 *{escape_markdown(display_name)}*, у тебя *{crumbs}* крошек.\nЕщё немного — и сможешь заглянуть в /shop!"
    elif crumbs < 500:
        text = f"🧀 *{escape_markdown(display_name)}*, у тебя *{crumbs}* крошек.\nНеплохой запас! Присмотрись к товарам в /shop."
    elif crumbs < 1000:
        text = f"🧀 *{escape_markdown(display_name)}*, у тебя *{crumbs}* крошек.\nВнушительное состояние! Можно купить редкие предметы в /shop."
    else:
        text = f"🧀 *{escape_markdown(display_name)}*, у тебя *{crumbs}* крошек!\nТы — сырный магнат Ратляндии! 👑"
    
    await update.message.reply_text(text, parse_mode=constants.ParseMode.MARKDOWN)