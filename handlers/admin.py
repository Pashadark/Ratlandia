"""Админ-панель"""

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from telegram import constants
import sqlite3

DB_FILE = "/root/bot/ratings.db"
ADMIN_IDS = [185185047]  # Твой ID

def is_admin(user_id: int) -> bool:
    return user_id in ADMIN_IDS


async def admin_panel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Админ-панель"""
    query = update.callback_query
    user_id = query.from_user.id
    
    if not is_admin(user_id):
        await query.answer("❌ Нет доступа!", show_alert=True)
        return
    
    from keyboards.inline.admin import get_admin_keyboard
    
    await query.message.delete()
    await context.bot.send_message(
        chat_id=user_id,
        text="🛡️ *АДМИН-ПАНЕЛЬ*\n\nВыбери действие:",
        parse_mode='Markdown',
        reply_markup=get_admin_keyboard()
    )


async def admin_heal_all(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Вылечить всех игроков"""
    query = update.callback_query
    user_id = query.from_user.id
    
    if not is_admin(user_id):
        await query.answer("❌ Нет доступа!", show_alert=True)
        return
    
    with sqlite3.connect(DB_FILE) as conn:
        c = conn.cursor()
        c.execute("""
            SELECT r.user_id, r.nickname, s.max_health 
            FROM ratings r 
            LEFT JOIN user_stats s ON r.user_id = s.user_id 
            WHERE r.nickname IS NOT NULL
        """)
        players = c.fetchall()
        
        healed = 0
        names = []
        for uid, nick, max_hp in players:
            if max_hp and max_hp > 0:
                c.execute("UPDATE user_stats SET current_health = ? WHERE user_id = ?", (max_hp, uid))
                healed += 1
                names.append(nick[:15])
        
        conn.commit()
    
    # Сообщение в ЛС админу
    names_list = "\n".join([f"  💚 {n}" for n in names])
    await context.bot.send_message(
        chat_id=user_id,
        text=f"💚 *ВСЕ ИГРОКИ ВЫЛЕЧЕНЫ!*\n\nВылечено: {healed}\n\n{names_list}",
        parse_mode='Markdown'
    )
    
    await query.answer(f"✅ Вылечено {healed} игроков!", show_alert=True)
    
    # Сообщение в группу
    GROUP_CHAT_ID = -1003922256958
    try:
        await context.bot.send_message(
            chat_id=GROUP_CHAT_ID,
            text=f"💚 *БОЖЕСТВЕННОЕ ИСЦЕЛЕНИЕ!*\n\n_Верховный администратор восстановил здоровье всем героям Подземного Царства!_\n\nВылечено игроков: {healed}",
            parse_mode='Markdown'
        )
    except Exception as e:
        logger.warning(f"Не удалось отправить в группу: {e}")


async def admin_crumbs_all(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Дать крошки всем"""
    query = update.callback_query
    user_id = query.from_user.id
    
    if not is_admin(user_id):
        await query.answer("❌ Нет доступа!", show_alert=True)
        return
    
    with sqlite3.connect(DB_FILE) as conn:
        c = conn.cursor()
        c.execute("SELECT user_id FROM user_stats")
        users = c.fetchall()
        
        for (uid,) in users:
            c.execute("INSERT INTO user_currency (user_id, crumbs) VALUES (?, 100) ON CONFLICT(user_id) DO UPDATE SET crumbs = crumbs + 100", (uid,))
        
        conn.commit()
    
    await query.answer(f"✅ {len(users)} игроков получили +100 🧀!", show_alert=True)


async def admin_stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Статистика сервера"""
    query = update.callback_query
    user_id = query.from_user.id
    
    if not is_admin(user_id):
        await query.answer("❌ Нет доступа!", show_alert=True)
        return
    
    with sqlite3.connect(DB_FILE) as conn:
        c = conn.cursor()
        c.execute("SELECT COUNT(*) FROM ratings")
        players = c.fetchone()[0]
        c.execute("SELECT COUNT(*) FROM inventory")
        items = c.fetchone()[0]
        c.execute("SELECT SUM(crumbs) FROM user_currency")
        crumbs = c.fetchone()[0] or 0
        c.execute("SELECT SUM(xp) FROM user_stats")
        xp = c.fetchone()[0] or 0
    
    text = f"""📊 *СТАТИСТИКА СЕРВЕРА*

👥 Игроков: {players}
🎒 Предметов: {items}
🧀 Крошек: {crumbs:,}
✨ Опыта: {xp:,} XP"""
    
    await query.answer()
    await query.message.delete()
    await context.bot.send_message(
        chat_id=user_id,
        text=text,
        parse_mode='Markdown'
    )


async def admin_ban_list(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Показать список игроков для бана"""
    query = update.callback_query
    user_id = query.from_user.id
    
    if not is_admin(user_id):
        await query.answer("❌ Нет доступа!", show_alert=True)
        return
    
    # Инициализируем таблицу забаненных если нет
    with sqlite3.connect(DB_FILE) as conn:
        conn.execute('''CREATE TABLE IF NOT EXISTS banned_users 
                        (user_id INTEGER PRIMARY KEY, 
                         nickname TEXT, 
                         banned_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')
        conn.commit()
    
    from keyboards.inline.admin import get_ban_list_keyboard
    
    await query.message.delete()
    
    with sqlite3.connect(DB_FILE) as conn:
        c = conn.cursor()
        c.execute("SELECT r.user_id, r.nickname, CASE WHEN b.user_id IS NOT NULL THEN 1 ELSE 0 END as banned FROM ratings r LEFT JOIN banned_users b ON r.user_id = b.user_id ORDER BY banned DESC, r.nickname")
        users = c.fetchall()
    
    text = "🚫 *СПИСОК ИГРОКОВ*\n\n_Нажми на игрока чтобы заблокировать/разблокировать:_\n\n"
    
    for uid, nick, banned in users:
        status = "🔴" if banned else "🟢"
        text += f"{status} {nick}\n"
    
    text += f"\nВсего: {len(users)} игроков"
    
    await context.bot.send_message(
        chat_id=user_id,
        text=text,
        parse_mode='Markdown',
        reply_markup=get_ban_list_keyboard(users)
    )


async def admin_toggle_ban(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Забанить/разбанить игрока"""
    query = update.callback_query
    admin_id = query.from_user.id
    
    if not is_admin(admin_id):
        await query.answer("❌ Нет доступа!", show_alert=True)
        return
    
    target_id = int(query.data.replace("admin_ban_", "").replace("admin_unban_", ""))
    
    with sqlite3.connect(DB_FILE) as conn:
        c = conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS banned_users 
                        (user_id INTEGER PRIMARY KEY, 
                         nickname TEXT, 
                         banned_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')
        
        c.execute("SELECT user_id FROM banned_users WHERE user_id = ?", (target_id,))
        is_banned = c.fetchone()
        
        if is_banned:
            # Разбанить
            c.execute("DELETE FROM banned_users WHERE user_id = ?", (target_id,))
            conn.commit()
            
            # Получаем ник
            c.execute("SELECT nickname FROM ratings WHERE user_id = ?", (target_id,))
            row = c.fetchone()
            nick = row[0] if row else str(target_id)
            
            await query.answer(f"✅ {nick} разблокирован!")
        else:
            # Забанить
            c.execute("SELECT nickname FROM ratings WHERE user_id = ?", (target_id,))
            row = c.fetchone()
            nick = row[0] if row else str(target_id)
            
            c.execute("INSERT OR REPLACE INTO banned_users (user_id, nickname) VALUES (?, ?)", (target_id, nick))
            conn.commit()
            
            await query.answer(f"🚫 {nick} заблокирован!")
    
    # Обновляем список
    await admin_ban_list(update, context)