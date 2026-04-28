"""Система кланов"""

import sqlite3
import asyncio
import logging
from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from telegram import constants
import sys
sys.path.append('/root/bot')
from handlers.inventory import get_crumbs, spend_crumbs, unlock_achievement
from handlers.instagram import handle_message
from handlers.achievements_data import ACHIEVEMENTS
from keyboards.inline.clan import (
    get_clan_main_keyboard,
    get_clan_create_keyboard,
    get_clan_manage_no_clan_keyboard,
    get_clan_manage_member_keyboard,
    get_clan_join_keyboard,
    get_clan_back_keyboard
)

logger = logging.getLogger(__name__)
DB_FILE = "/root/bot/ratings.db"

CLAN_RANKS = {
    "leader": {"name": "Лидер", "icon": "👑", "level": 6},
    "elder": {"name": "Старейшина", "icon": "🛡️", "level": 5},
    "veteran": {"name": "Ветеран", "icon": "⚔️", "level": 4},
    "warrior": {"name": "Воитель", "icon": "🗡️", "level": 3},
    "scout": {"name": "Следопыт", "icon": "🏹", "level": 2},
    "newcomer": {"name": "Новобранец", "icon": "🌱", "level": 1},
}


def init_clan_db():
    with sqlite3.connect(DB_FILE) as conn:
        c = conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS clans (
            id INTEGER PRIMARY KEY AUTOINCREMENT, 
            name TEXT UNIQUE, 
            tag TEXT UNIQUE,
            leader_id INTEGER, 
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )''')
        c.execute('''CREATE TABLE IF NOT EXISTS clan_members (
            user_id INTEGER PRIMARY KEY, 
            clan_id INTEGER, 
            rank TEXT DEFAULT 'newcomer',
            war_wins INTEGER DEFAULT 0,
            joined_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )''')
        c.execute("UPDATE clan_members SET rank = 'leader' WHERE user_id IN (SELECT leader_id FROM clans)")
        conn.commit()


def get_user_clan(user_id: int):
    with sqlite3.connect(DB_FILE) as conn:
        c = conn.cursor()
        c.execute('''SELECT c.id, c.name, c.tag, c.leader_id, cm.rank
                     FROM clans c JOIN clan_members cm ON c.id = cm.clan_id
                     WHERE cm.user_id = ?''', (user_id,))
        row = c.fetchone()
        if row:
            return {"id": row[0], "name": row[1], "tag": row[2], "leader_id": row[3], "rank": row[4]}
        return None


def get_clan_rank_counts(clan_id: int) -> dict:
    with sqlite3.connect(DB_FILE) as conn:
        c = conn.cursor()
        c.execute('''SELECT rank, COUNT(*) FROM clan_members 
                     WHERE clan_id = ? GROUP BY rank''', (clan_id,))
        counts = {"leader": 0, "elder": 0, "veteran": 0, "warrior": 0, "scout": 0, "newcomer": 0}
        for row in c.fetchall():
            if row[0] in counts:
                counts[row[0]] = row[1]
        return counts


def create_clan(user_id: int, name: str, tag: str) -> tuple:
    with sqlite3.connect(DB_FILE) as conn:
        c = conn.cursor()
        c.execute('SELECT clan_id FROM clan_members WHERE user_id = ?', (user_id,))
        if c.fetchone():
            return False, "❌ Ты уже состоишь в клане!"
        c.execute('SELECT id FROM clans WHERE name = ?', (name,))
        if c.fetchone():
            return False, "❌ Такое название уже занято!"
        c.execute('SELECT id FROM clans WHERE tag = ?', (tag,))
        if c.fetchone():
            return False, "❌ Такой тег уже занят!"
        c.execute('INSERT INTO clans (name, tag, leader_id) VALUES (?, ?, ?)', (name, tag, user_id))
        clan_id = c.lastrowid
        c.execute('INSERT INTO clan_members (user_id, clan_id, rank) VALUES (?, ?, ?)', 
                  (user_id, clan_id, 'leader'))
        conn.commit()
        logger.info(f"✅ Клан создан: {name} [{tag}], лидер: {user_id}")
        return True, f"✅ Клан *{name}* [{tag}] создан!"


def join_clan(user_id: int, clan_name: str) -> tuple:
    with sqlite3.connect(DB_FILE) as conn:
        c = conn.cursor()
        c.execute('SELECT clan_id FROM clan_members WHERE user_id = ?', (user_id,))
        if c.fetchone():
            return False, "❌ Ты уже состоишь в клане!"
        c.execute('SELECT id, name, tag FROM clans WHERE name = ? OR tag = ?', (clan_name, clan_name))
        clan = c.fetchone()
        if not clan:
            return False, "❌ Клан не найден!"
        clan_id, name, tag = clan
        c.execute('INSERT INTO clan_members (user_id, clan_id, rank) VALUES (?, ?, ?)', 
                  (user_id, clan_id, 'newcomer'))
        conn.commit()
        return True, f"✅ Ты вступил в клан *{name}* [{tag}]!"


def leave_clan(user_id: int) -> tuple:
    with sqlite3.connect(DB_FILE) as conn:
        c = conn.cursor()
        c.execute('''SELECT c.id, c.name, c.leader_id FROM clans c
                     JOIN clan_members cm ON c.id = cm.clan_id WHERE cm.user_id = ?''', (user_id,))
        row = c.fetchone()
        if not row:
            return False, "❌ Ты не состоишь в клане!"
        clan_id, clan_name, leader_id = row
        if leader_id == user_id:
            return False, "❌ Лидер не может покинуть клан! Используй роспуск."
        c.execute('DELETE FROM clan_members WHERE user_id = ?', (user_id,))
        conn.commit()
        return True, f"👋 Ты покинул клан *{clan_name}*"


def promote_member(clan_id: int, target_id: int, by_user_id: int) -> tuple:
    """Повышает звание участника"""
    with sqlite3.connect(DB_FILE) as conn:
        c = conn.cursor()
        c.execute('SELECT rank FROM clan_members WHERE user_id = ? AND clan_id = ?', (by_user_id, clan_id))
        promoter = c.fetchone()
        if not promoter or promoter[0] not in ['leader', 'elder']:
            return False, "❌ Нет прав для повышения!"
        
        c.execute('SELECT rank FROM clan_members WHERE user_id = ? AND clan_id = ?', (target_id, clan_id))
        target = c.fetchone()
        if not target:
            return False, "❌ Игрок не в клане!"
        
        rank_order = ['newcomer', 'scout', 'warrior', 'veteran', 'elder']
        current_idx = rank_order.index(target[0]) if target[0] in rank_order else 0
        if current_idx >= len(rank_order) - 1:
            return False, "❌ Достигнут максимальный ранг!"
        
        new_rank = rank_order[current_idx + 1]
        c.execute('UPDATE clan_members SET rank = ? WHERE user_id = ? AND clan_id = ?', (new_rank, target_id, clan_id))
        conn.commit()
        return True, f"✅ Игрок повышен до *{CLAN_RANKS[new_rank]['name']}*!"


def demote_member(clan_id: int, target_id: int, by_user_id: int) -> tuple:
    """Понижает звание участника"""
    with sqlite3.connect(DB_FILE) as conn:
        c = conn.cursor()
        c.execute('SELECT rank FROM clan_members WHERE user_id = ? AND clan_id = ?', (by_user_id, clan_id))
        promoter = c.fetchone()
        if not promoter or promoter[0] not in ['leader', 'elder']:
            return False, "❌ Нет прав для понижения!"
        
        c.execute('SELECT rank FROM clan_members WHERE user_id = ? AND clan_id = ?', (target_id, clan_id))
        target = c.fetchone()
        if not target:
            return False, "❌ Игрок не в клане!"
        if target[0] == 'leader':
            return False, "❌ Нельзя понизить лидера!"
        
        rank_order = ['newcomer', 'scout', 'warrior', 'veteran', 'elder']
        current_idx = rank_order.index(target[0]) if target[0] in rank_order else len(rank_order) - 1
        if current_idx <= 0:
            return False, "❌ Достигнут минимальный ранг!"
        
        new_rank = rank_order[current_idx - 1]
        c.execute('UPDATE clan_members SET rank = ? WHERE user_id = ? AND clan_id = ?', (new_rank, target_id, clan_id))
        conn.commit()
        return True, f"✅ Игрок понижен до *{CLAN_RANKS[new_rank]['name']}*!"


def get_clan_info(user_id: int):
    with sqlite3.connect(DB_FILE) as conn:
        c = conn.cursor()
        c.execute('''SELECT c.id, c.name, c.tag, c.leader_id, c.created_at,
                     (SELECT COUNT(*) FROM clan_members WHERE clan_id = c.id) as members
                     FROM clans c JOIN clan_members cm ON c.id = cm.clan_id WHERE cm.user_id = ?''', (user_id,))
        row = c.fetchone()
        if not row:
            return None
        return {"id": row[0], "name": row[1], "tag": row[2], "leader_id": row[3],
                "created_at": row[4], "members": row[5]}


def get_clan_members(clan_id: int):
    with sqlite3.connect(DB_FILE) as conn:
        c = conn.cursor()
        c.execute('''SELECT r.user_id, r.nickname, r.name, cm.rank, cm.war_wins
                     FROM clan_members cm
                     LEFT JOIN ratings r ON cm.user_id = r.user_id
                     WHERE cm.clan_id = ?
                     ORDER BY CASE cm.rank 
                        WHEN 'leader' THEN 1 
                        WHEN 'elder' THEN 2 
                        WHEN 'veteran' THEN 3 
                        WHEN 'warrior' THEN 4 
                        WHEN 'scout' THEN 5 
                        ELSE 6 END''', (clan_id,))
        return [{"user_id": row[0], "nickname": row[1] or row[2] or f"ID:{row[0]}", 
                 "rank": row[3], "war_wins": row[4]} for row in c.fetchall()]


def get_top_clans(limit: int = 10):
    with sqlite3.connect(DB_FILE) as conn:
        c = conn.cursor()
        c.execute('''SELECT c.name, c.tag, COUNT(cm.user_id) as members
                     FROM clans c LEFT JOIN clan_members cm ON c.id = cm.clan_id
                     GROUP BY c.id ORDER BY members DESC LIMIT ?''', (limit,))
        return [{"name": row[0], "tag": row[1], "members": row[2]} for row in c.fetchall()]


def disband_clan(user_id: int) -> tuple:
    with sqlite3.connect(DB_FILE) as conn:
        c = conn.cursor()
        c.execute('SELECT id, name FROM clans WHERE leader_id = ?', (user_id,))
        clan = c.fetchone()
        if not clan:
            return False, "❌ Ты не лидер клана!"
        clan_id, clan_name = clan
        c.execute('DELETE FROM clan_members WHERE clan_id = ?', (clan_id,))
        c.execute('DELETE FROM clans WHERE id = ?', (clan_id,))
        conn.commit()
        return True, f"💔 Клан *{clan_name}* распущен"

async def clan_achievements_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Показывает достижения клана"""
    query = update.callback_query
    user_id = query.from_user.id
    
    clan = get_user_clan(user_id)
    if not clan:
        await query.answer("❌ Ты не в клане!", show_alert=True)
        return
    
    # Все достижения клана
    all_clan_achievements = {k: v for k, v in ACHIEVEMENTS.items() if k.startswith('clan_')}
    
    # Получаем разблокированные
    with sqlite3.connect(DB_FILE) as conn:
        c = conn.cursor()
        c.execute('''SELECT achievement_id FROM user_achievements 
                     WHERE user_id = ? AND achievement_id LIKE 'clan_%'
                     ORDER BY unlocked_at DESC''', (user_id,))
        unlocked = [row[0] for row in c.fetchall()]
    
    text = f"🏆 *ДОСТИЖЕНИЯ КЛАНА* [{clan['tag']}]\n\n"
    text += f"_Разблокировано: {len(unlocked)}/{len(all_clan_achievements)}_\n\n"
    
    for ach_id, ach in all_clan_achievements.items():
        status = "✅" if ach_id in unlocked else "🔒"
        text += f"{status} {ach['icon']} *{ach['name']}*\n"
        text += f"   _{ach['desc']}_\n\n"
    
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("🔙 Назад", callback_data="clan_manage")]
    ])
    
    await query.message.delete()
    await context.bot.send_message(chat_id=user_id, text=text,
                                  parse_mode=constants.ParseMode.MARKDOWN, reply_markup=keyboard)
# ========== КОМАНДЫ ==========

async def clan_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user_clan = get_user_clan(user_id)
    
    text = f"""🛡️ *ГИЛЬДИЯ ТЕНЕЙ*

_В тёмных туннелях подземного города сила измеряется не только острыми клыками, но и верностью братству. Здесь рождаются легендарные кланы — союзы крыс и мышей, готовых сражаться плечом к плечу._"""
    
    if user_clan:
        rank_info = CLAN_RANKS.get(user_clan.get('rank', 'newcomer'), CLAN_RANKS['newcomer'])
        text += f"\n\n*Твой клан:* {user_clan['name']} [{user_clan['tag']}]\n*Звание:* {rank_info['icon']} {rank_info['name']}"
    
    keyboard = get_clan_main_keyboard()
    
    if update.callback_query:
        query = update.callback_query
        await query.message.delete()
    else:
        query = None
    
    try:
        with open("/root/bot/images/clan.jpg", "rb") as photo:
            if query:
                await context.bot.send_photo(chat_id=query.from_user.id, photo=photo, caption=text,
                                             parse_mode=constants.ParseMode.MARKDOWN, reply_markup=keyboard)
            else:
                await update.message.reply_photo(photo=photo, caption=text,
                                                 parse_mode=constants.ParseMode.MARKDOWN, reply_markup=keyboard)
    except:
        if query:
            await context.bot.send_message(chat_id=query.from_user.id, text=text,
                                          parse_mode=constants.ParseMode.MARKDOWN, reply_markup=keyboard)
        else:
            await update.message.reply_text(text, parse_mode=constants.ParseMode.MARKDOWN, reply_markup=keyboard)

async def clan_promote_select(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Выбор участника для повышения"""
    query = update.callback_query
    user_id = query.from_user.id
    
    clan = get_user_clan(user_id)
    if not clan:
        await query.answer("❌ Ты не в клане!", show_alert=True)
        return
    
    my_rank = clan['rank']
    if my_rank not in ['leader', 'elder']:
        await query.answer("❌ Нет прав для повышения!", show_alert=True)
        return
    
    members = get_clan_members(clan['id'])
    
    # Убираем себя и лидера
    promotable = [m for m in members if m['user_id'] != user_id and m['rank'] != 'leader']
    
    if not promotable:
        await query.answer("❌ Некого повышать!", show_alert=True)
        return
    
    text = f"⭐ *ПОВЫШЕНИЕ*\n\nВыбери участника:\n"
    keyboard = []
    
    for m in promotable:
        rank_info = CLAN_RANKS.get(m['rank'], CLAN_RANKS['newcomer'])
        text += f"\n{rank_info['icon']} {m['nickname']} — *{rank_info['name']}*"
        keyboard.append([InlineKeyboardButton(
            f"{rank_info['icon']} {m['nickname']} — повысить",
            callback_data=f"clan_promote_{m['user_id']}"
        )])
    
    keyboard.append([InlineKeyboardButton("🔙 Назад", callback_data="clan_manage")])
    
    await query.message.delete()
    await context.bot.send_message(chat_id=user_id, text=text,
                                  parse_mode=constants.ParseMode.MARKDOWN,
                                  reply_markup=InlineKeyboardMarkup(keyboard))


async def clan_demote_select(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Выбор участника для понижения"""
    query = update.callback_query
    user_id = query.from_user.id
    
    clan = get_user_clan(user_id)
    if not clan:
        await query.answer("❌ Ты не в клане!", show_alert=True)
        return
    
    my_rank = clan['rank']
    if my_rank not in ['leader', 'elder']:
        await query.answer("❌ Нет прав для понижения!", show_alert=True)
        return
    
    members = get_clan_members(clan['id'])
    
    # Убираем себя и лидера
    demotable = [m for m in members if m['user_id'] != user_id and m['rank'] not in ['leader', 'newcomer']]
    
    if not demotable:
        await query.answer("❌ Некого понижать!", show_alert=True)
        return
    
    text = f"⭐ *ПОНИЖЕНИЕ*\n\nВыбери участника:\n"
    keyboard = []
    
    for m in demotable:
        rank_info = CLAN_RANKS.get(m['rank'], CLAN_RANKS['newcomer'])
        text += f"\n{rank_info['icon']} {m['nickname']} — *{rank_info['name']}*"
        keyboard.append([InlineKeyboardButton(
            f"{rank_info['icon']} {m['nickname']} — понизить",
            callback_data=f"clan_demote_{m['user_id']}"
        )])
    
    keyboard.append([InlineKeyboardButton("🔙 Назад", callback_data="clan_manage")])
    
    await query.message.delete()
    await context.bot.send_message(chat_id=user_id, text=text,
                                  parse_mode=constants.ParseMode.MARKDOWN,
                                  reply_markup=InlineKeyboardMarkup(keyboard))


async def clan_promote_user(update: Update, context: ContextTypes.DEFAULT_TYPE, target_id: int):
    """Повышает конкретного участника"""
    query = update.callback_query
    user_id = query.from_user.id
    
    clan = get_user_clan(user_id)
    if not clan:
        await query.answer("❌ Ты не в клане!", show_alert=True)
        return
    
    success, message = promote_member(clan['id'], target_id, user_id)
    await query.answer(message, show_alert=True)
    
    if success:
        await clan_members_list(update, context)


async def clan_demote_user(update: Update, context: ContextTypes.DEFAULT_TYPE, target_id: int):
    """Понижает конкретного участника"""
    query = update.callback_query
    user_id = query.from_user.id
    
    clan = get_user_clan(user_id)
    if not clan:
        await query.answer("❌ Ты не в клане!", show_alert=True)
        return
    
    success, message = demote_member(clan['id'], target_id, user_id)
    await query.answer(message, show_alert=True)
    
    if success:
        await clan_members_list(update, context)
        
async def clan_create_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    crumbs = get_crumbs(user_id)
    
    text = f"""🏗️ *СОЗДАНИЕ КЛАНА*

⚠️ Стоимость: *1000* 🧀
🧀 Твой баланс: *{crumbs}* 🧀

Для создания клана нажми кнопку ниже и введи данные в формате:
`Название ТЕГ`

Пример: `Теневые Крысы ТКР`"""
    
    keyboard = get_clan_create_keyboard()
    await query.message.delete()
    await context.bot.send_message(chat_id=user_id, text=text,
                                  parse_mode=constants.ParseMode.MARKDOWN, reply_markup=keyboard)


async def clan_register(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    
    if get_user_clan(user_id):
        await query.answer("❌ Ты уже состоишь в клане!", show_alert=True)
        return
    
    context.user_data['awaiting_clan_create'] = True
    logger.info(f"🔍 Установлен флаг awaiting_clan_create для user={user_id}")
    
    await query.message.delete()
    await context.bot.send_message(
        chat_id=user_id,
        text="✏️ Отправь название и тег клана:\n\n`Название ТЕГ`\n\nПример: `Теневые Крысы ТКР`\n\nДля отмены нажми /cancel",
        parse_mode=constants.ParseMode.MARKDOWN
    )


async def clan_manage(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Меню управления кланом"""
    query = update.callback_query
    user_id = query.from_user.id
    
    clan = get_clan_info(user_id)
    await query.message.delete()
    
    if not clan:
        text = f"""⚙️ *УПРАВЛЕНИЕ*

❌ Ты не состоишь в клане."""
        keyboard = get_clan_manage_no_clan_keyboard()
    else:
        is_leader = (clan['leader_id'] == user_id)
        
        conn = sqlite3.connect(DB_FILE)
        cur = conn.execute('SELECT nickname FROM ratings WHERE user_id = ?', (clan['leader_id'],))
        row = cur.fetchone()
        conn.close()
        leader_name = row[0] if row and row[0] else f"ID:{clan['leader_id']}"
        
        ranks = get_clan_rank_counts(clan['id'])
        clan_level = min(clan['members'], 10)
        
        # Достижения клана
        clan_achievements = []
        with sqlite3.connect(DB_FILE) as aconn:
            acur = aconn.execute('''SELECT achievement_id FROM user_achievements 
                         WHERE user_id = ? AND achievement_id LIKE 'clan_%'
                         ORDER BY unlocked_at DESC LIMIT 5''', (user_id,))
            clan_achievements = [row[0] for row in acur.fetchall()]
        
        text = f"""⚙️ *{clan['name']}* [{clan['tag']}]

_Братство, рождённое в туннелях Ратляндии. Вместе вы сила, что сотрясает подземные своды._

👑 Лидер: *{leader_name}*
🛡️ Старейшин: *{ranks.get('elder', 0)}*
⚔️ Воителей: *{ranks.get('warrior', 0) + ranks.get('veteran', 0)}*
🌱 Новобранцев: *{ranks.get('newcomer', 0) + ranks.get('scout', 0)}*
👥 Всего участников: *{clan['members']}*
⭐ Уровень клана: *{clan_level}*
📅 Создан: *{clan['created_at'][:10]}*"""
        
        if clan_achievements:
            text += "\n\n🏆 *Достижения клана:*\n"
            for ach_id in clan_achievements[:3]:
                if ach_id in ACHIEVEMENTS:
                    ach = ACHIEVEMENTS[ach_id]
                    text += f"  {ach['icon']} {ach['name']}\n"
        
        keyboard = get_clan_manage_member_keyboard(is_leader)
    
    try:
        with open("/root/bot/images/clan_manage.jpg", "rb") as photo:
            await context.bot.send_photo(chat_id=user_id, photo=photo, caption=text,
                                        parse_mode=constants.ParseMode.MARKDOWN, reply_markup=keyboard)
    except:
        await context.bot.send_message(chat_id=user_id, text=text,
                                      parse_mode=constants.ParseMode.MARKDOWN, reply_markup=keyboard)


async def handle_clan_create_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обрабатывает ввод названия и тега клана"""
    user_id = update.effective_user.id
    text = update.message.text.strip() if update.message else ""
    
    if text.startswith("http") or text.startswith("www"):
        return
    
    logger.info(f"🔍 handle_clan_create_input ВЫЗВАН! user={user_id}, text='{text}', awaiting={context.user_data.get('awaiting_clan_create')}")
    
    if not context.user_data.get('awaiting_clan_create'):
        logger.info(f"⏭ Пропускаем — нет флага awaiting_clan_create")
        return
    
    context.user_data['awaiting_clan_create'] = False
    
    parts = text.split()
    if len(parts) < 2:
        await update.message.reply_text("❌ Неверный формат! Отправь: Название ТЕГ\nПример: Теневые Крысы ТКР")
        return
    
    tag = parts[-1].upper()
    name = " ".join(parts[:-1])
    crumbs = get_crumbs(user_id)
    
    if crumbs < 1000:
        await update.message.reply_text(f"❌ Недостаточно крошек! Нужно 1000 🧀, у тебя {crumbs} 🧀")
        return
    
    if not spend_crumbs(user_id, 1000):
        await update.message.reply_text("❌ Ошибка при списании крошек!")
        return
    
    success, message = create_clan(user_id, name, tag)
    
    if success:
        unlock_achievement(user_id, 'clan_birth')
        unlock_achievement(user_id, 'clan_leader')
        
        conn = sqlite3.connect(DB_FILE)
        cur = conn.execute('SELECT nickname FROM ratings WHERE user_id = ?', (user_id,))
        row = cur.fetchone()
        conn.close()
        nickname = row[0] if row and row[0] else f"ID:{user_id}"
        
        today = datetime.now().strftime('%d.%m.%Y')
        
        caption = f"✅ *Клан создан!*\n\n"
        caption += f"_Ты встаёшь во главе нового братства. Туннели Ратляндии наполняются шёпотом: «Слышал? Появились {name}!» Теперь твоя задача — собрать верных соратников и привести клан к величию. Пусть тег {tag} гремит в каждом уголке Подземного Царства!_\n\n"
        caption += f"👑 *Лидер:* {nickname}\n"
        caption += f"🛡️ *Клан:* {name}\n"
        caption += f"🪦 *Тег:* {tag}\n"
        caption += f"📅 *Создан:* {today}\n\n"
        caption += f"_Да начнётся славная история!_"
        
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("🔙 В гильдию", callback_data="profile_clan")]
        ])
        
        try:
            with open("/root/bot/images/clan_created.jpg", "rb") as photo:
                await update.message.reply_photo(photo=photo, caption=caption,
                                                parse_mode=constants.ParseMode.MARKDOWN, reply_markup=keyboard)
        except:
            await update.message.reply_text(caption, parse_mode=constants.ParseMode.MARKDOWN, reply_markup=keyboard)
    else:
        await update.message.reply_text(message, parse_mode=constants.ParseMode.MARKDOWN)


async def handle_clan_join_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обрабатывает вступление в клан"""
    user_id = update.effective_user.id
    text = update.message.text.strip() if update.message else ""
    
    if text.startswith("http") or text.startswith("www"):
        return
    
    if not context.user_data.get('awaiting_clan_join'):
        return
    
    context.user_data['awaiting_clan_join'] = False
    
    success, message = join_clan(user_id, text)
    
    if success:
        unlock_achievement(user_id, 'clan_recruiter')  # Попытка
        await update.message.reply_text(message, parse_mode=constants.ParseMode.MARKDOWN)
        await clan_command(update, context)
    else:
        await update.message.reply_text(message, parse_mode=constants.ParseMode.MARKDOWN)


async def clan_join_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Меню вступления в клан"""
    query = update.callback_query
    user_id = query.from_user.id
    
    if get_user_clan(user_id):
        await query.answer("❌ Ты уже состоишь в клане!", show_alert=True)
        return
    
    context.user_data['awaiting_clan_join'] = True
    logger.info(f"🔍 Установлен флаг awaiting_clan_join для user={user_id}")
    
    await query.message.delete()
    await context.bot.send_message(
        chat_id=user_id,
        text="✏️ Отправь название или тег клана для вступления:\n\nДля отмены нажми /cancel",
        parse_mode=constants.ParseMode.MARKDOWN
    )


async def clan_members_list(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Список участников клана с званиями и кнопками управления"""
    query = update.callback_query
    user_id = query.from_user.id
    
    clan = get_user_clan(user_id)
    if not clan:
        await query.answer("❌ Ты не в клане!", show_alert=True)
        return
    
    my_rank = get_user_clan(user_id)['rank']
    can_manage = my_rank in ['leader', 'elder']
    
    members = get_clan_members(clan['id'])
    
    text = f"📋 *УЧАСТНИКИ* [{clan['tag']}]\n\n"
    for i, m in enumerate(members, 1):
        rank_info = CLAN_RANKS.get(m['rank'], CLAN_RANKS['newcomer'])
        text += f"{i}. {rank_info['icon']} {m['nickname']} — *{rank_info['name']}*\n"
        if m['war_wins'] > 0:
            text += f"   ⚔️ Побед в войнах: {m['war_wins']}\n"
    
    keyboard = []
    if can_manage:
        keyboard.append([
            InlineKeyboardButton("⭐ Повысить", callback_data="clan_promote_select"),
            InlineKeyboardButton("⭐ Понизить", callback_data="clan_demote_select")
        ])
    keyboard.append([InlineKeyboardButton("🔙 Назад", callback_data="clan_manage")])
    
    await query.message.delete()
    await context.bot.send_message(chat_id=user_id, text=text,
                                  parse_mode=constants.ParseMode.MARKDOWN, 
                                  reply_markup=InlineKeyboardMarkup(keyboard))


async def clan_leave(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    success, message = leave_clan(user_id)
    await query.answer(message, show_alert=True)
    if success:
        await clan_command(update, context)


async def clan_disband(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    success, message = disband_clan(user_id)
    await query.answer(message, show_alert=True)
    if success:
        await clan_command(update, context)


async def clan_info_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    clan = get_clan_info(user_id)
    
    if not clan:
        text = "❌ Ты не состоишь в клане!"
    else:
        text = f"""🛡️ *{clan['name']}* [{clan['tag']}]

👥 Участников: {clan['members']}
📅 Создан: {clan['created_at'][:10]}

_Вместе вы сила!_"""
    
    keyboard = get_clan_back_keyboard()
    await query.message.delete()
    await context.bot.send_message(chat_id=user_id, text=text,
                                  parse_mode=constants.ParseMode.MARKDOWN, reply_markup=keyboard)

async def clan_message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    text = update.message.text.strip() if update.message else ""
    
    # Ссылки — сразу в инстаграм!
    if text.startswith("http") or text.startswith("www"):
        await handle_message(update, context)
        return
    
    logger.info(f"🔥 clan_message_handler ВЫЗВАН! user={user_id}, text='{text}'")
    
    if context.user_data.get('awaiting_clan_create'):
        logger.info(f"🏗️ Передаём в handle_clan_create_input")
        await handle_clan_create_input(update, context)
        return
    
    if context.user_data.get('awaiting_clan_join'):
        logger.info(f"🔍 Передаём в handle_clan_join_input")
        await handle_clan_join_input(update, context)
        return
    
    # Остальное — в инстаграм
    await handle_message(update, context)
    return

async def clan_top_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    top = get_top_clans(10)
    
    text = "🏆 *ТОП КЛАНОВ*\n\n"
    medals = ["🥇", "🥈", "🥉"]
    
    for i, clan in enumerate(top):
        prefix = medals[i] if i < 3 else f"{i+1}."
        text += f"{prefix} *{clan['name']}* [{clan['tag']}] — {clan['members']} уч.\n"
    
    if not top:
        text += "_Пока нет кланов. Создай первый!_\n"
    
    keyboard = get_clan_back_keyboard()
    await query.message.delete()
    await context.bot.send_message(chat_id=user_id, text=text,
                                  parse_mode=constants.ParseMode.MARKDOWN, reply_markup=keyboard)


init_clan_db()