"""Система титулов для Ратляндии"""

import sqlite3
from typing import Dict, List, Optional
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram import constants
from telegram.ext import ContextTypes

DB_FILE = "/root/bot/ratings.db"

# ========== ВСЕ ТИТУЛЫ ==========
TITLES = {
    # 🎓 ТИТУЛЫ ЗА УРОВЕНЬ
    "novice": {"name": "🌱 Новичок", "type": "level", "level": 1, "icon": "🌱", "desc": "Начало пути"},
    "curious": {"name": "👀 Любопытный", "type": "level", "level": 5, "icon": "👀", "desc": "Первые шаги в норе"},
    "explorer": {"name": "🔍 Исследователь", "type": "level", "level": 10, "icon": "🔍", "desc": "Познаёт тайны норы"},
    "experienced": {"name": "🧀 Бывалый", "type": "level", "level": 15, "icon": "🧀", "desc": "Знает где лежит сыр"},
    "hunter": {"name": "🎯 Охотник", "type": "level", "level": 20, "icon": "🎯", "desc": "Острый нюх на Крысу"},
    "veteran": {"name": "⚔️ Ветеран", "type": "level", "level": 25, "icon": "⚔️", "desc": "Закалён в битвах"},
    "master": {"name": "🏆 Мастер", "type": "level", "level": 30, "icon": "🏆", "desc": "Мастер своего дела"},
    "expert": {"name": "💎 Эксперт", "type": "level", "level": 40, "icon": "💎", "desc": "Эксперт по выживанию"},
    "legend": {"name": "👑 Легенда", "type": "level", "level": 50, "icon": "👑", "desc": "Легенда Ратляндии"},
    "myth": {"name": "🌟 Миф", "type": "level", "level": 75, "icon": "🌟", "desc": "Мифический герой"},
    "god": {"name": "⚡ Бог норы", "type": "level", "level": 100, "icon": "⚡", "desc": "Вершина эволюции"},
    
    # 🎯 ТИТУЛЫ ЗА ДОСТИЖЕНИЯ
    "rat_king": {"name": "🐀👑 Крысиный король", "type": "achievement", "ach_id": "rat_king", "icon": "🐀👑", "desc": "15 побед за Крысу"},
    "rat_emperor": {"name": "🏰🐀 Крысиный император", "type": "achievement", "ach_id": "rat_emperor", "icon": "🏰", "desc": "50 побед за Крысу"},
    "pack_leader": {"name": "🐭👑 Вожак стаи", "type": "achievement", "ach_id": "pack_leader", "icon": "🐭👑", "desc": "30 побед за Мышь"},
    "mouse_god": {"name": "⚡🐭 Бог мышей", "type": "achievement", "ach_id": "mouse_god", "icon": "⚡", "desc": "100 побед за Мышь"},
    "merciless": {"name": "🔪 Мясник", "type": "achievement", "ach_id": "merciless", "icon": "🔪", "desc": "25 убийств"},
    "butcher": {"name": "💀 Безжалостный", "type": "achievement", "ach_id": "butcher", "icon": "💀", "desc": "100 убийств"},
    "psychic": {"name": "🔮 Экстрасенс", "type": "achievement", "ach_id": "psychic", "icon": "🔮", "desc": "Угадать Крысу 5 раз подряд"},
    "puppeteer": {"name": "🎪 Кукольник", "type": "achievement", "ach_id": "puppeteer", "icon": "🎪", "desc": "Подставить невиновного"},
    "eagle_eye": {"name": "🔍 Детектив", "type": "achievement", "ach_id": "eagle_eye", "icon": "🔍", "desc": "Угадать Крысу с первого раза"},
    "night_hunter": {"name": "🌙 Ночной охотник", "type": "achievement", "ach_id": "night_hunter", "icon": "🌙", "desc": "Убивать каждую ночь"},
    
    # 🔥 ТИТУЛЫ ЗА СЕРИИ
    "lucky": {"name": "🍀 Везунчик", "type": "streak", "streak": 3, "icon": "🍀", "desc": "3 победы подряд"},
    "invincible": {"name": "🔥 Непобедимый", "type": "streak", "streak": 5, "icon": "🔥", "desc": "5 побед подряд"},
    "legendary_streak": {"name": "🌟 Легендарный", "type": "streak", "streak": 10, "icon": "🌟", "desc": "10 побед подряд"},
    "machine": {"name": "🤖 Машина", "type": "streak", "streak": 15, "icon": "🤖", "desc": "15 побед подряд"},
    
    # 🎁 ТИТУЛЫ ЗА КОЛЛЕКЦИЮ
    "collector": {"name": "📦 Собиратель", "type": "collection", "items": 20, "icon": "📦", "desc": "20 предметов в инвентаре"},
    "hoarder": {"name": "🏺 Коллекционер", "type": "collection", "items": 50, "icon": "🏺", "desc": "50 предметов"},
    "cheese_tycoon": {"name": "🧀💎 Сырный магнат", "type": "collection", "legendary": 10, "icon": "🧀💎", "desc": "10 легендарных предметов"},
    "mythic_hunter": {"name": "🌌 Мифический охотник", "type": "collection", "mythic": 5, "icon": "🌌", "desc": "5 мифических предметов"},
    
    # 🎲 ТИТУЛЫ ЗА КОСТИ (ТАВЕРНА)
    "dice_novice": {"name": "🎲 Новичок таверны", "type": "dice", "games": 5, "icon": "🎲", "desc": "Сыграть 5 игр в кости"},
    "dice_player": {"name": "🃏 Игрок", "type": "dice", "games": 25, "icon": "🃏", "desc": "Сыграть 25 игр в кости"},
    "dice_gambler": {"name": "💰 Азартный", "type": "dice", "games": 50, "icon": "💰", "desc": "Сыграть 50 игр в кости"},
    "dice_shadow": {"name": "🌑 Любимец Тени", "type": "dice", "games": 100, "icon": "🌑", "desc": "Сыграть 100 игр в кости"},
    "dice_legend": {"name": "🏆 Легенда таверны", "type": "dice", "games": 250, "icon": "🏆", "desc": "Сыграть 250 игр в кости"},
    
    # 🍺 ТИТУЛЫ ЗА ПИВО (ИЛЬЯС ЭЛЬ)
    "beer_lover": {"name": "🍺 Ценитель эля", "type": "beer", "count": 5, "icon": "🍺", "desc": "Выпить 5 кружек Ильяс эля"},
    "beer_connoisseur": {"name": "🍻 Знаток", "type": "beer", "count": 15, "icon": "🍻", "desc": "Выпить 15 кружек Ильяс эля"},
    "beer_king": {"name": "👑 Король таверны", "type": "beer", "count": 50, "icon": "👑", "desc": "Выпить 50 кружек Ильяс эля"},
    
    # 💰 ТИТУЛЫ ЗА КРОШКИ
    "crumbs_1000": {"name": "🧀 Сырный", "type": "crumbs", "amount": 1000, "icon": "🧀", "desc": "Накопить 1000 крошек"},
    "crumbs_5000": {"name": "💰 Богач", "type": "crumbs", "amount": 5000, "icon": "💰", "desc": "Накопить 5000 крошек"},
    "crumbs_10000": {"name": "💎 Магнат", "type": "crumbs", "amount": 10000, "icon": "💎", "desc": "Накопить 10000 крошек"},
    "crumbs_50000": {"name": "🏦 Крёз", "type": "crumbs", "amount": 50000, "icon": "🏦", "desc": "Накопить 50000 крошек"},
    
    # 📦 ТИТУЛЫ ЗА СУНДУКИ
    "chest_opener_10": {"name": "📦 Открыватель", "type": "chest", "count": 10, "icon": "📦", "desc": "Открыть 10 сундуков"},
    "chest_opener_50": {"name": "🔓 Взломщик", "type": "chest", "count": 50, "icon": "🔓", "desc": "Открыть 50 сундуков"},
    "chest_opener_100": {"name": "🗝️ Мастер ключей", "type": "chest", "count": 100, "icon": "🗝️", "desc": "Открыть 100 сундуков"},
    
    # 🎪 СЕКРЕТНЫЕ ТИТУЛЫ
    "ghost": {"name": "👻 Призрак", "type": "secret", "icon": "👻", "desc": "Победить после смерти", "hidden": True},
    "traitor": {"name": "🗡️💔 Предатель", "type": "secret", "icon": "🗡️", "desc": "Крыса убила Крысу", "hidden": True},
    "victim": {"name": "⚰️ Жертва", "type": "secret", "icon": "⚰️", "desc": "Умереть первым 10 раз", "hidden": True},
    "phoenix": {"name": "🔥🪽 Феникс", "type": "secret", "icon": "🔥", "desc": "Воскреснуть и победить", "hidden": True},
    "chosen": {"name": "✨👁️ Избранный", "type": "secret", "icon": "✨", "desc": "Разблокировать все достижения", "hidden": True},
    
    # 🎭 ТИТУЛЫ ЗА СТИЛЬ
    "diplomat": {"name": "🤝 Дипломат", "type": "style", "icon": "🤝", "desc": "Убедить всех голосовать за Крысу"},
    "silent": {"name": "🤐 Молчун", "type": "style", "icon": "🤐", "desc": "5 игр без сообщений"},
    "talker": {"name": "🗣️ Болтун", "type": "style", "icon": "🗣️", "desc": "1000 сообщений в чате"},
    "strategist": {"name": "♟️ Стратег", "type": "style", "icon": "♟️", "desc": "Победить за 2 дня"},
    "kamikaze": {"name": "💥 Камикадзе", "type": "style", "icon": "💥", "desc": "Пожертвовать собой"},
}


# ========== ФУНКЦИИ РАБОТЫ С ТИТУЛАМИ ==========

def init_titles_db():
    """Создаёт таблицы для титулов"""
    with sqlite3.connect(DB_FILE) as conn:
        c = conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS user_titles (user_id INTEGER, title_id TEXT, unlocked_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP, PRIMARY KEY (user_id, title_id))''')
        c.execute('''CREATE TABLE IF NOT EXISTS user_active_title (user_id INTEGER PRIMARY KEY, title_id TEXT)''')
        conn.commit()


def unlock_title(user_id: int, title_id: str) -> bool:
    """Разблокирует титул"""
    if title_id not in TITLES:
        return False
    with sqlite3.connect(DB_FILE) as conn:
        c = conn.cursor()
        try:
            c.execute('INSERT INTO user_titles (user_id, title_id) VALUES (?, ?)', (user_id, title_id))
            conn.commit()
            return True
        except sqlite3.IntegrityError:
            return False


def get_unlocked_titles(user_id: int) -> List[Dict]:
    """Возвращает список разблокированных титулов"""
    with sqlite3.connect(DB_FILE) as conn:
        c = conn.cursor()
        c.execute('SELECT title_id, unlocked_at FROM user_titles WHERE user_id = ? ORDER BY unlocked_at DESC', (user_id,))
        result = []
        for row in c.fetchall():
            if row[0] in TITLES:
                title = TITLES[row[0]].copy()
                title["id"] = row[0]
                title["unlocked_at"] = row[1]
                result.append(title)
        return result


def set_active_title(user_id: int, title_id: Optional[str]) -> bool:
    """Устанавливает активный титул"""
    with sqlite3.connect(DB_FILE) as conn:
        c = conn.cursor()
        if title_id is None:
            c.execute('DELETE FROM user_active_title WHERE user_id = ?', (user_id,))
        else:
            c.execute('INSERT OR REPLACE INTO user_active_title (user_id, title_id) VALUES (?, ?)', (user_id, title_id))
        conn.commit()
        return True


def get_active_title(user_id: int) -> Optional[Dict]:
    """Возвращает активный титул игрока"""
    with sqlite3.connect(DB_FILE) as conn:
        c = conn.cursor()
        c.execute('SELECT title_id FROM user_active_title WHERE user_id = ?', (user_id,))
        row = c.fetchone()
        if row and row[0] in TITLES:
            title = TITLES[row[0]].copy()
            title["id"] = row[0]
            return title
    return None


def get_title_by_level(level: int) -> Optional[str]:
    """Возвращает ID титула по уровню"""
    best_title = None
    best_level = 0
    for tid, data in TITLES.items():
        if data.get("type") == "level" and data.get("level", 0) <= level:
            if data["level"] > best_level:
                best_level = data["level"]
                best_title = tid
    return best_title


def check_and_unlock_titles(user_id: int):
    """Проверяет и разблокирует титулы по условиям"""
    from handlers.inventory import (
        get_user_xp, get_level_from_xp, get_inventory, get_achievements_count,
        get_crumbs, get_dice_games, get_dice_wins, get_beer_count,
        get_chests_opened
    )
    
    # Титулы за уровень
    xp = get_user_xp(user_id)
    level = get_level_from_xp(xp)
    for tid, data in TITLES.items():
        if data.get("type") == "level" and data.get("level", 0) <= level:
            unlock_title(user_id, tid)
    
    # Титулы за коллекцию
    inventory = get_inventory(user_id)
    total_items = sum(inventory.values())
    legendary_count = sum(1 for iid, qty in inventory.items() if iid in ALL_ITEMS and ALL_ITEMS[iid].get("rarity") == "legendary")
    mythic_count = sum(1 for iid, qty in inventory.items() if iid in ALL_ITEMS and ALL_ITEMS[iid].get("rarity") == "mythic")
    
    for tid, data in TITLES.items():
        if data.get("type") == "collection":
            if data.get("items", 0) and total_items >= data["items"]:
                unlock_title(user_id, tid)
            if data.get("legendary", 0) and legendary_count >= data["legendary"]:
                unlock_title(user_id, tid)
            if data.get("mythic", 0) and mythic_count >= data["mythic"]:
                unlock_title(user_id, tid)
    
    # Титулы за кости
    dice_games = get_dice_games(user_id)
    dice_wins = get_dice_wins(user_id) if hasattr(get_dice_wins, '__call__') else 0
    
    for tid, data in TITLES.items():
        if data.get("type") == "dice" and dice_games >= data.get("games", 0):
            unlock_title(user_id, tid)
        if data.get("type") == "dice_wins" and dice_wins >= data.get("wins", 0):
            unlock_title(user_id, tid)
    
    # Титулы за пиво
    beer_count = get_beer_count(user_id) if hasattr(get_beer_count, '__call__') else 0
    for tid, data in TITLES.items():
        if data.get("type") == "beer" and beer_count >= data.get("count", 0):
            unlock_title(user_id, tid)
    
    # Титулы за крошки
    crumbs = get_crumbs(user_id)
    for tid, data in TITLES.items():
        if data.get("type") == "crumbs" and crumbs >= data.get("amount", 0):
            unlock_title(user_id, tid)
    
    # Титулы за сундуки
    chests_opened = get_chests_opened(user_id) if hasattr(get_chests_opened, '__call__') else 0
    for tid, data in TITLES.items():
        if data.get("type") == "chest" and chests_opened >= data.get("count", 0):
            unlock_title(user_id, tid)
    
    # Титулы за достижения
    ach_count = get_achievements_count(user_id)
    if ach_count >= len(ACHIEVEMENTS) - sum(1 for a in ACHIEVEMENTS.values() if a.get("hidden", False)):
        unlock_title(user_id, "chosen")
    
    # Автоматически устанавливаем титул по уровню если нет активного
    active = get_active_title(user_id)
    if not active:
        level_title = get_title_by_level(level)
        if level_title:
            set_active_title(user_id, level_title)


async def titles_command(update: Update, context: ContextTypes.DEFAULT_TYPE, show_all: bool = False):
    # ЗАПРЕТ В ГРУППАХ
    if update.effective_chat.type != "private":
        if update.callback_query:
            await update.callback_query.answer("❌ Титулы можно смотреть только в личных сообщениях бота!", show_alert=True)
        return
    
    user_id = update.effective_user.id
    
    check_and_unlock_titles(user_id)
    
    unlocked_titles = get_unlocked_titles(user_id)
    active_title = get_active_title(user_id)
    active_title_name = active_title["name"] if active_title else "🌱 Новичок"
    
    # Собираем заблокированные
    unlocked_ids = [t['id'] for t in unlocked_titles]
    locked_titles = []
    for tid, tdata in TITLES.items():
        if tid not in unlocked_ids and not tdata.get('hidden', False):
            locked_titles.append({"id": tid, **tdata})
    
    text = f"""🎖️ ГАЛЕРЕЯ ТИТУЛОВ

_В этом древнем зале, на бархатных подушках под стеклянными колпаками, хранятся знаки отличия величайших воинов Подземного Царства. Каждый титул — это не просто слово, это признание твоих подвигов. Носи их с гордостью, и пусть враги трепещут при виде твоего имени!_

▸ АКТИВНЫЙ ТИТУЛ
  {active_title_name}

"""
    
    if show_all:
        text += f"▸ ВСЕ ТИТУЛЫ ({len(unlocked_titles)}/{len(TITLES)})\n\n"
        
        keyboard = []
        if unlocked_titles:
            for t in unlocked_titles:
                status = "✅" if active_title and t['id'] == active_title['id'] else "  "
                text += f"  {status} {t['name']}\n     {t['desc']}\n\n"
                if not active_title or t['id'] != active_title['id']:
                    keyboard.append([InlineKeyboardButton(f"{t['icon']} Выбрать {t['name']}", callback_data=f"set_title_{t['id']}")])
        
        for t in locked_titles:
            text += f"  🔒 {t['name']}\n     {t['desc']}\n\n"
        
        if active_title:
            keyboard.append([InlineKeyboardButton("❌ Снять титул", callback_data="set_title_none")])
        
        keyboard.append([InlineKeyboardButton("📋 Свернуть", callback_data="titles_compact")])
        keyboard.append([InlineKeyboardButton("🔙 В профиль", callback_data="back_to_profile")])
    else:
        text += f"▸ РАЗБЛОКИРОВАННЫЕ ({len(unlocked_titles)})\n\n"
        
        keyboard = []
        if unlocked_titles:
            for t in unlocked_titles[:5]:
                status = "✅" if active_title and t['id'] == active_title['id'] else "  "
                text += f"  {status} {t['name']}\n     {t['desc']}\n\n"
                if not active_title or t['id'] != active_title['id']:
                    keyboard.append([InlineKeyboardButton(f"{t['icon']} Выбрать {t['name']}", callback_data=f"set_title_{t['id']}")])
            if len(unlocked_titles) > 5:
                text += f"  ... и ещё {len(unlocked_titles) - 5}\n\n"
        else:
            text += "  ❌ Нет разблокированных титулов\n\n"
        
        text += f"▸ ДОСТУПНЫЕ ДЛЯ ПОЛУЧЕНИЯ\n\n"
        for t in locked_titles[:3]:
            text += f"  🔒 {t['name']}\n     {t['desc']}\n\n"
        
        if len(locked_titles) > 3:
            text += f"  ... и ещё {len(locked_titles) - 3} титулов\n"
        
        if active_title:
            keyboard.append([InlineKeyboardButton("❌ Снять титул", callback_data="set_title_none")])
        
        keyboard.append([InlineKeyboardButton("📋 Все титулы", callback_data="titles_all")])
        keyboard.append([InlineKeyboardButton("🔙 В профиль", callback_data="back_to_profile")])
    
    query = update.callback_query
    await query.message.delete()
    
    try:
        with open("/root/bot/images/titles_hall.jpg", "rb") as photo:
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


# Импорты для проверки
from handlers.items import ALL_ITEMS
from handlers.achievements_data import ACHIEVEMENTS

# Инициализация
init_titles_db()