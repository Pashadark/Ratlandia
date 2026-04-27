"""Зал Славы — рейтинг игроков по реальной статистике"""

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from telegram import constants
import sqlite3
from datetime import datetime, timedelta
from handlers.titles import get_active_title
from handlers.clan import get_user_clan
from keyboards.inline.hall_of_fame import get_hall_of_fame_keyboard

DB_FILE = "/root/bot/ratings.db"


def escape_markdown(text: str) -> str:
    import re
    if not text:
        return ""
    escape_chars = r'_*[]()~`>#+-=|{}.!'
    return re.sub(f'([{re.escape(escape_chars)}])', r'\\\1', text)


def _init_ranking_db():
    """Создаёт таблицу для хранения истории рейтинга"""
    with sqlite3.connect(DB_FILE) as conn:
        conn.execute('''
            CREATE TABLE IF NOT EXISTS ranking_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                position INTEGER,
                power INTEGER,
                week_start TEXT,
                recorded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        conn.commit()


def _save_current_ranking(players: list):
    """Сохраняет текущие позиции в историю (обновляет записи за этот день)"""
    today = datetime.now()
    this_monday = (today - timedelta(days=today.weekday())).strftime('%Y-%m-%d')
    
    with sqlite3.connect(DB_FILE) as conn:
        # Удаляем старые записи за этот день
        conn.execute('DELETE FROM ranking_history WHERE week_start = ?', (this_monday,))
        
        # Сохраняем новые
        for pos, p in enumerate(players, 1):
            conn.execute('''
                INSERT INTO ranking_history (user_id, position, power, week_start)
                VALUES (?, ?, ?, ?)
            ''', (p['user_id'], pos, p['power'], this_monday))
        conn.commit()


def _get_last_week_positions() -> dict:
    """Возвращает позиции игроков из ПРЕДЫДУЩЕГО сохранения (не сегодня)"""
    today = datetime.now()
    this_monday = (today - timedelta(days=today.weekday())).strftime('%Y-%m-%d')
    
    with sqlite3.connect(DB_FILE) as conn:
        c = conn.cursor()
        # Ищем записи с другой датой (не сегодня)
        c.execute('''
            SELECT user_id, position FROM ranking_history 
            WHERE week_start != ?
            ORDER BY week_start DESC, position
        ''', (this_monday,))
        rows = c.fetchall()
        
        if not rows:
            return {}
        
        return {row[0]: row[1] for row in rows}


def get_top_players(limit: int = 10) -> list:
    """Возвращает топ игроков по общей мощности"""
    _init_ranking_db()
    
    with sqlite3.connect(DB_FILE) as conn:
        c = conn.cursor()
        c.execute('''
            SELECT us.user_id, r.nickname, r.name,
                   us.level,
                   COALESCE(tr.max_kills, 0) as tunnel_kills,
                   COALESCE(tr.total_bosses_killed, 0) as bosses_killed,
                   (us.level * 10 + us.strength + us.agility + us.intelligence + 
                    COALESCE(tr.max_kills, 0) * 3 + COALESCE(tr.max_rooms, 0) * 2 + 
                    COALESCE(tr.total_bosses_killed, 0) * 50) as power
            FROM user_stats us
            JOIN ratings r ON us.user_id = r.user_id
            LEFT JOIN tunnel_records tr ON us.user_id = tr.user_id
            ORDER BY power DESC
            LIMIT ?
        ''', (limit,))
        
        result = []
        for row in c.fetchall():
            total_kills = (row[4] or 0) + (row[5] or 0)
            result.append({
                "user_id": row[0],
                "nickname": row[1] or row[2],
                "level": row[3] or 1,
                "total_kills": total_kills,
                "power": row[6] or 0,
            })
        
        # Сохраняем рейтинг для истории (обновляется каждый день)
        _save_current_ranking(result)
        
        return result


def _get_position_change(current_pos: int, user_id: int) -> str:
    """Возвращает стрелку изменения позиции"""
    last_week = _get_last_week_positions()
    if user_id not in last_week:
        return ""  # Пусто для новых игроков или первого дня
    
    old_pos = last_week[user_id]
    diff = old_pos - current_pos
    
    if diff > 0:
        return f" ↑{diff}"
    elif diff < 0:
        return f" ↓{abs(diff)}"
    return " •0"


def get_player_rank(user_id: int) -> int:
    """Возвращает место игрока в общем рейтинге"""
    with sqlite3.connect(DB_FILE) as conn:
        c = conn.cursor()
        c.execute('''
            SELECT COUNT(*) + 1 FROM user_stats us
            LEFT JOIN tunnel_records tr ON us.user_id = tr.user_id
            WHERE (us.level * 10 + us.strength + us.agility + us.intelligence + 
                   COALESCE(tr.max_kills, 0) * 3 + COALESCE(tr.max_rooms, 0) * 2 + 
                   COALESCE(tr.total_bosses_killed, 0) * 50) > 
                  (SELECT us2.level * 10 + us2.strength + us2.agility + us2.intelligence + 
                          COALESCE(tr2.max_kills, 0) * 3 + COALESCE(tr2.max_rooms, 0) * 2 + 
                          COALESCE(tr2.total_bosses_killed, 0) * 50
                   FROM user_stats us2
                   LEFT JOIN tunnel_records tr2 ON us2.user_id = tr2.user_id
                   WHERE us2.user_id = ?)
        ''', (user_id,))
        return c.fetchone()[0]


async def hall_of_fame(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Зал Славы — топ игроков"""
    if update.callback_query:
        user_id = update.callback_query.from_user.id
    else:
        user_id = update.effective_user.id
    
    top = get_top_players(10)
    
    keyboard = get_hall_of_fame_keyboard()
    
    if not top:
        text = "🏆 *ЗАЛ СЛАВЫ*\n\n_Пока пустует... Стань первым героем Подземного Царства!_"
        if update.callback_query:
            query = update.callback_query
            await query.message.delete()
            await context.bot.send_message(chat_id=query.from_user.id, text=text, 
                                           parse_mode=constants.ParseMode.MARKDOWN, reply_markup=keyboard)
        else:
            await update.message.reply_text(text, parse_mode=constants.ParseMode.MARKDOWN, reply_markup=keyboard)
        return
    
    text = f"""🏆 *ЗАЛ СЛАВЫ*

_Здесь, на древних стенах из сырного камня, высечены имена величайших воинов Подземного Царства. Их подвиги помнят туннели, их имена шепчет ветер канализации._

"""
    
    medals = ["🥇", "🥈", "🥉"]
    for i, p in enumerate(top):
        pos = i + 1
        name = escape_markdown(p['nickname'][:20])
        
        active_title = get_active_title(p['user_id'])
        title_name = active_title["name"] if active_title else "Новичок"
        
        clan = get_user_clan(p['user_id'])
        clan_tag = f" [{clan['tag']}]" if clan else ""
        
        # Стрелка прогресса
        change = _get_position_change(pos, p['user_id'])
        
        if pos <= 3:
            text += f"{medals[i]} *{name}*{clan_tag} ({title_name}){change}\n"
        else:
            text += f"{pos}. *{name}*{clan_tag} ({title_name}){change}\n"
        
        text += f"   ⭐ Ур.{p['level']} | 👹 Убийств: {p['total_kills']} | ⚡ Сила: {p['power']}\n\n"
    
    # Место текущего игрока
    player_rank = get_player_rank(user_id)
    text += f"\n📊 *Твоё место: {player_rank}*"
    
    text += "\n\n⚔️ *Сразись и впиши своё имя в историю!*"
    
    if update.callback_query:
        query = update.callback_query
        await query.message.delete()
        try:
            with open("/root/bot/images/leaderboard.jpg", "rb") as photo:
                await context.bot.send_photo(
                    chat_id=query.from_user.id, photo=photo, caption=text,
                    parse_mode=constants.ParseMode.MARKDOWN, reply_markup=keyboard
                )
        except:
            await context.bot.send_message(
                chat_id=query.from_user.id, text=text,
                parse_mode=constants.ParseMode.MARKDOWN, reply_markup=keyboard
            )
    else:
        try:
            with open("/root/bot/images/leaderboard.jpg", "rb") as photo:
                await update.message.reply_photo(photo=photo, caption=text,
                                                  parse_mode=constants.ParseMode.MARKDOWN, reply_markup=keyboard)
        except:
            await update.message.reply_text(text, parse_mode=constants.ParseMode.MARKDOWN, reply_markup=keyboard)