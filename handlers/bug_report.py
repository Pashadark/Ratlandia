"""Система баг-репортов /bag"""
import sqlite3
import os
from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from telegram import constants
import logging

logger = logging.getLogger(__name__)
DB_FILE = "/root/bot/ratings.db"
GROUP_CHAT_ID = -1003922256958

def init_bug_db():
    with sqlite3.connect(DB_FILE) as conn:
        conn.execute('''CREATE TABLE IF NOT EXISTS bug_reports (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            bug_number INTEGER UNIQUE,
            user_id INTEGER,
            username TEXT,
            description TEXT,
            importance TEXT,
            status TEXT DEFAULT "in_work",
            screenshot_path TEXT,
            message_id INTEGER,
            report_date TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )''')
        conn.execute('''CREATE TABLE IF NOT EXISTS bug_counter (
            id INTEGER PRIMARY KEY,
            last_number INTEGER DEFAULT 20260
        )''')
        conn.execute("INSERT OR IGNORE INTO bug_counter (id, last_number) VALUES (1, 20260)")
        conn.commit()

def get_next_bug_number():
    with sqlite3.connect(DB_FILE) as conn:
        c = conn.cursor()
        c.execute("UPDATE bug_counter SET last_number = last_number + 1 WHERE id = 1")
        c.execute("SELECT last_number FROM bug_counter WHERE id = 1")
        num = c.fetchone()[0]
        conn.commit()
        return num

def save_bug(user_id: int, username: str, description: str, importance: str, screenshot_path: str = None) -> int:
    bug_number = get_next_bug_number()
    report_date = datetime.now().strftime('%d.%m.%Y')
    with sqlite3.connect(DB_FILE) as conn:
        c = conn.cursor()
        c.execute('''INSERT INTO bug_reports (bug_number, user_id, username, description, importance, screenshot_path, report_date)
                     VALUES (?, ?, ?, ?, ?, ?, ?)''',
                  (bug_number, user_id, username, description, importance, screenshot_path, report_date))
        conn.commit()
        return bug_number

def update_bug_status(bug_number: int, status: str):
    with sqlite3.connect(DB_FILE) as conn:
        c = conn.cursor()
        c.execute("UPDATE bug_reports SET status = ? WHERE bug_number = ?", (status, bug_number))
        conn.commit()

def update_bug_message_id(bug_number: int, message_id: int):
    with sqlite3.connect(DB_FILE) as conn:
        c = conn.cursor()
        c.execute("UPDATE bug_reports SET message_id = ? WHERE bug_number = ?", (message_id, bug_number))
        conn.commit()

def get_bug_by_number(bug_number: int):
    with sqlite3.connect(DB_FILE) as conn:
        c = conn.cursor()
        c.execute("SELECT * FROM bug_reports WHERE bug_number = ?", (bug_number,))
        row = c.fetchone()
        if row:
            return {
                "id": row[0], "bug_number": row[1], "user_id": row[2],
                "username": row[3], "description": row[4], "importance": row[5],
                "status": row[6], "screenshot_path": row[7], "message_id": row[8],
                "report_date": row[9], "created_at": row[10]
            }
        return None

def get_user_bugs(user_id: int):
    with sqlite3.connect(DB_FILE) as conn:
        c = conn.cursor()
        c.execute("SELECT * FROM bug_reports WHERE user_id = ? ORDER BY created_at DESC", (user_id,))
        return c.fetchall()

def get_all_bugs():
    with sqlite3.connect(DB_FILE) as conn:
        c = conn.cursor()
        c.execute("SELECT * FROM bug_reports ORDER BY created_at DESC LIMIT 20")
        return c.fetchall()

def get_bug_stats():
    with sqlite3.connect(DB_FILE) as conn:
        c = conn.cursor()
        c.execute("""
            SELECT username, COUNT(*) as count 
            FROM bug_reports 
            GROUP BY user_id 
            ORDER BY count DESC 
            LIMIT 10
        """)
        return c.fetchall()

init_bug_db()

IMPORTANCE_EMOJI = {
    "critical": "🔴",
    "urgent": "🟡", 
    "normal": "🟢"
}

IMPORTANCE_TAGS = {
    "critical": "критический",
    "urgent": "срочный",
    "normal": "нормальный"
}

STATUS_EMOJI = {
    "in_work": "🔄",
    "done": "✅",
    "rejected": "❌"
}

STATUS_NAMES = {
    "in_work": "В работе",
    "done": "Выполнено",
    "rejected": "Отклонено"
}


async def bag_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Начать создание баг-репорта"""
    user_id = update.effective_user.id
    
    context.user_data["bug_report"] = {"step": "description"}
    
    await update.message.reply_text(
        "🐛 *НОВЫЙ БАГ-РЕПОРТ*\n\n"
        "Опиши баг подробнее:",
        parse_mode='Markdown'
    )


async def handle_bug_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик ввода для баг-репорта"""
    user_id = update.effective_user.id
    text = update.message.text.strip() if update.message.text else ""
    
    if not context.user_data.get("bug_report"):
        return False
    
    bug_data = context.user_data["bug_report"]
    
    if bug_data["step"] == "description" and text != "/skip":
        bug_data["description"] = text
        bug_data["step"] = "screenshot"
        context.user_data["bug_report"] = bug_data
        
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("⏭️ Пропустить", callback_data="bug_skip_screenshot")]
        ])
        
        await update.message.reply_text(
            "📸 Пришли скриншот бага:",
            reply_markup=keyboard
        )
        return True
    
    return False


async def handle_bug_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик фото для баг-репорта"""
    user_id = update.effective_user.id
    
    if not context.user_data.get("bug_report"):
        return False
    
    bug_data = context.user_data["bug_report"]
    
    if bug_data["step"] == "screenshot":
        photo = update.message.photo[-1]
        file = await context.bot.get_file(photo.file_id)
        
        os.makedirs("/root/bot/bug_screenshots", exist_ok=True)
        filepath = f"/root/bot/bug_screenshots/bug_{user_id}_{datetime.now().timestamp()}.jpg"
        await file.download_to_drive(filepath)
        
        bug_data["screenshot_path"] = filepath
        bug_data["step"] = "importance"
        context.user_data["bug_report"] = bug_data
        
        await show_importance_buttons(update, context)
        return True
    
    return False


async def bug_skip_screenshot(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Пропустить скриншот"""
    query = update.callback_query
    user_id = query.from_user.id
    
    if not context.user_data.get("bug_report"):
        await query.answer("❌ Нет активного баг-репорта!", show_alert=True)
        return
    
    bug_data = context.user_data["bug_report"]
    bug_data["screenshot_path"] = None
    bug_data["step"] = "importance"
    context.user_data["bug_report"] = bug_data
    
    await query.message.delete()
    await show_importance_buttons(update, context)


async def show_importance_buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Показать кнопки выбора важности"""
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("🔴 Критично", callback_data="bug_importance_critical")],
        [InlineKeyboardButton("🟡 Срочно", callback_data="bug_importance_urgent")],
        [InlineKeyboardButton("🟢 Нормально", callback_data="bug_importance_normal")],
    ])
    
    if update.callback_query:
        await context.bot.send_message(
            chat_id=update.effective_user.id,
            text="⚡ *Выбери важность бага:*",
            parse_mode='Markdown',
            reply_markup=keyboard
        )
    else:
        await update.message.reply_text(
            "⚡ *Выбери важность бага:*",
            parse_mode='Markdown',
            reply_markup=keyboard
        )


async def bug_set_importance(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Установить важность и отправить в группу"""
    query = update.callback_query
    user_id = query.from_user.id
    
    if not context.user_data.get("bug_report"):
        await query.answer("❌ Нет активного баг-репорта!", show_alert=True)
        return
    
    importance = query.data.replace("bug_importance_", "")
    bug_data = context.user_data["bug_report"]
    
    username = query.from_user.username or query.from_user.full_name
    bug_number = save_bug(user_id, username, bug_data["description"], importance, bug_data.get("screenshot_path"))
    
    bug = get_bug_by_number(bug_number)
    report_date = bug["report_date"] if bug else datetime.now().strftime('%d.%m.%Y')
    
    importance_emoji = IMPORTANCE_EMOJI.get(importance, "🟢")
    importance_tag = IMPORTANCE_TAGS.get(importance, "нормальный")
    
    caption = (
        f"🐛 Найден баг номер: *#{bug_number}*\n\n"
        f"Кем: @{username}\n\n"
        f"Описание: *{bug_data['description']}*\n\n"
        f"#баг #{importance_tag} #{username} #{report_date}"
    )
    
    keyboard = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("✅ Выполнено", callback_data=f"bug_status_done_{bug_number}"),
            InlineKeyboardButton("🔄 В работе", callback_data=f"bug_status_work_{bug_number}"),
        ],
        [InlineKeyboardButton("❌ Отклонено", callback_data=f"bug_status_reject_{bug_number}")],
    ])
    
    try:
        if bug_data.get("screenshot_path"):
            with open(bug_data["screenshot_path"], "rb") as photo:
                msg = await context.bot.send_photo(
                    chat_id=GROUP_CHAT_ID,
                    photo=photo,
                    caption=caption,
                    parse_mode='Markdown',
                    reply_markup=keyboard
                )
        else:
            msg = await context.bot.send_message(
                chat_id=GROUP_CHAT_ID,
                text=caption,
                parse_mode='Markdown',
                reply_markup=keyboard
            )
        
        update_bug_message_id(bug_number, msg.message_id)
        
        await query.message.delete()
        await context.bot.send_message(
            chat_id=user_id,
            text=f"✅ *Баг отправлен!*\n\n"
                 f"Номер: *#{bug_number}*\n"
                 f"Важность: {importance_emoji} {importance_tag}\n"
                 f"Дата: {report_date}\n\n"
                 f"_Спасибо за помощь в улучшении игры!_",
            parse_mode='Markdown'
        )
        
        # Очищаем данные
        context.user_data.pop("bug_report", None)
        
    except Exception as e:
        logger.error(f"Ошибка отправки бага: {e}")
        await query.answer("❌ Ошибка отправки!", show_alert=True)


async def bug_change_status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Изменить статус бага"""
    query = update.callback_query
    user_id = query.from_user.id
    
    data = query.data
    bug_number = int(data.split("_")[-1])
    
    if "done" in data:
        status = "done"
    elif "work" in data:
        status = "in_work"
    elif "reject" in data:
        status = "rejected"
    else:
        return
    
    update_bug_status(bug_number, status)
    
    bug = get_bug_by_number(bug_number)
    if not bug:
        await query.answer("❌ Баг не найден!", show_alert=True)
        return
    
    importance_tag = IMPORTANCE_TAGS.get(bug["importance"], "нормальный")
    status_emoji = STATUS_EMOJI.get(status, "🔄")
    status_name = STATUS_NAMES.get(status, "В работе")
    report_date = bug.get("report_date", datetime.now().strftime('%d.%m.%Y'))
    
    new_caption = (
        f"🐛 Найден баг номер: *#{bug_number}*\n\n"
        f"Кем: @{bug['username']}\n\n"
        f"Описание: *{bug['description']}*\n\n"
        f"Статус: {status_emoji} {status_name}\n\n"
        f"#баг #{importance_tag} #{bug['username']} #{report_date}"
    )
    
    keyboard = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("✅ Выполнено", callback_data=f"bug_status_done_{bug_number}"),
            InlineKeyboardButton("🔄 В работе", callback_data=f"bug_status_work_{bug_number}"),
        ],
        [InlineKeyboardButton("❌ Отклонено", callback_data=f"bug_status_reject_{bug_number}")],
    ])
    
    try:
        await query.message.edit_caption(
            caption=new_caption,
            parse_mode='Markdown',
            reply_markup=keyboard
        )
    except:
        await query.message.edit_text(
            text=new_caption,
            parse_mode='Markdown',
            reply_markup=keyboard
        )
    
    # Уведомить игрока
    try:
        await context.bot.send_message(
            chat_id=bug["user_id"],
            text=f"🐛 *Твой баг #{bug_number} обновлён!*\n\n"
                 f"Статус: {status_emoji} *{status_name}*",
            parse_mode='Markdown'
        )
    except:
        pass
    
    # Награда за выполненный баг
    if status == "done":
        from handlers.inventory import add_item
        import random
        chests = ["common_chest", "common_chest", "rare_chest", "epic_chest", "legendary_chest"]
        reward = random.choice(chests)
        add_item(bug["user_id"], reward)
        
        try:
            await context.bot.send_message(
                chat_id=bug["user_id"],
                text=f"🎁 *Награда за найденный баг!*\n\n"
                     f"Ты получил сундук за баг #{bug_number}!",
                parse_mode='Markdown'
            )
        except:
            pass
    
    await query.answer(f"✅ Статус: {status_name}")


async def bag_stats_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Статистика охотников на баги"""
    stats = get_bug_stats()
    
    if not stats:
        await update.message.reply_text("📊 Пока никто не нашёл багов!")
        return
    
    text = "🐛 *ТОП ОХОТНИКОВ НА БАГИ*\n\n"
    
    medals = ["🥇", "🥈", "🥉"]
    for i, (username, count) in enumerate(stats):
        medal = medals[i] if i < 3 else f"{i+1}."
        text += f"{medal} @{username}: *{count}* багов\n"
    
    await update.message.reply_text(text, parse_mode='Markdown')


async def bag_list_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Список багов игрока"""
    user_id = update.effective_user.id
    bugs = get_user_bugs(user_id)
    
    if not bugs:
        await update.message.reply_text("🐛 У тебя пока нет баг-репортов!")
        return
    
    text = "🐛 *ТВОИ БАГ-РЕПОРТЫ*\n\n"
    
    for bug in bugs[:10]:
        status_emoji = STATUS_EMOJI.get(bug[6], "🔄")
        importance_emoji = IMPORTANCE_EMOJI.get(bug[5], "🟢")
        report_date = bug[9] if bug[9] else ""
        text += f"#{bug[1]} {importance_emoji} {status_emoji} {report_date} _{bug[4][:50]}..._\n"
    
    await update.message.reply_text(text, parse_mode='Markdown')