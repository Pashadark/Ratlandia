"""Ежедневные награды"""

import sqlite3
import random
import logging
from datetime import datetime, timedelta
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from telegram import constants
import sys
sys.path.append('/root/bot')
from handlers.inventory import add_crumbs, add_xp, add_item

logger = logging.getLogger(__name__)

DB_FILE = "/root/bot/ratings.db"

def init_daily_db():
    with sqlite3.connect(DB_FILE) as conn:
        c = conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS daily_rewards (user_id INTEGER PRIMARY KEY, last_claim TIMESTAMP)''')
        conn.commit()

def can_claim_daily(user_id: int) -> bool:
    with sqlite3.connect(DB_FILE) as conn:
        c = conn.cursor()
        c.execute('SELECT last_claim FROM daily_rewards WHERE user_id = ?', (user_id,))
        row = c.fetchone()
        if not row:
            return True
        last_claim = datetime.fromisoformat(row[0])
        return datetime.now() - last_claim > timedelta(hours=24)

def claim_daily(user_id: int):
    with sqlite3.connect(DB_FILE) as conn:
        c = conn.cursor()
        c.execute('INSERT OR REPLACE INTO daily_rewards (user_id, last_claim) VALUES (?, ?)',
                  (user_id, datetime.now().isoformat()))
        conn.commit()

async def daily_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    
    if not can_claim_daily(user_id):
        text = "⏳ Ты уже забирал награду сегодня! Приходи завтра."
        if update.callback_query:
            query = update.callback_query
            await query.answer(text, show_alert=True)
            await query.message.delete()
            keyboard = [[InlineKeyboardButton("🔙 Назад", callback_data="back_to_profile")]]
            await context.bot.send_message(
                chat_id=user_id,
                text=text,
                reply_markup=InlineKeyboardMarkup(keyboard)
            )
        else:
            await update.message.reply_text(text)
        return
    
    crumbs = random.randint(50, 150)
    xp = random.randint(50, 100)
    
    item_dropped = None
    if random.randint(1, 100) <= 10:
        from handlers.inventory import get_random_item
        item_dropped = get_random_item("all")
        if item_dropped:
            add_item(user_id, item_dropped)
    
    add_crumbs(user_id, crumbs)
    add_xp(user_id, xp)
    claim_daily(user_id)
    
    text = f"🎁 *ЕЖЕДНЕВНАЯ НАГРАДА ПОЛУЧЕНА!*\n\n"
    text += f"🧀 Крошки: +{crumbs}\n"
    text += f"✨ Опыт: +{xp} XP\n"
    if item_dropped:
        from handlers.items import ALL_ITEMS
        item = ALL_ITEMS.get(item_dropped, {"name": "Предмет"})
        text += f"🎁 Предмет: {item['name']}\n"
    text += f"\nПриходи завтра за новой наградой!"
    
    keyboard = [[InlineKeyboardButton("🔙 Назад", callback_data="back_to_profile")]]
    
    if update.callback_query:
        query = update.callback_query
        await query.message.delete()
        try:
            with open("/root/bot/images/daily_reward.jpg", "rb") as photo:
                await context.bot.send_photo(
                    chat_id=user_id,
                    photo=photo,
                    caption=text,
                    parse_mode=constants.ParseMode.MARKDOWN,
                    reply_markup=InlineKeyboardMarkup(keyboard)
                )
        except:
            await context.bot.send_message(
                chat_id=user_id,
                text=text,
                parse_mode=constants.ParseMode.MARKDOWN,
                reply_markup=InlineKeyboardMarkup(keyboard)
            )
    else:
        try:
            with open("/root/bot/images/daily_reward.jpg", "rb") as photo:
                await update.message.reply_photo(
                    photo=photo,
                    caption=text,
                    parse_mode=constants.ParseMode.MARKDOWN,
                    reply_markup=InlineKeyboardMarkup(keyboard)
                )
        except:
            await update.message.reply_text(
                text,
                parse_mode=constants.ParseMode.MARKDOWN,
                reply_markup=InlineKeyboardMarkup(keyboard)
            )

init_daily_db()