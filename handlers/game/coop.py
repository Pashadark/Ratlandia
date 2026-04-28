"""Кооперативный режим для битв с боссами в Туннелях"""

import sqlite3
import random
import uuid
from datetime import datetime, timedelta
from typing import Dict, Optional, List
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from telegram import constants
from handlers.character import get_character_stats
from handlers.tunnel_monsters import TUNNEL_MONSTERS
from handlers.inventory import add_item
from handlers.items import ALL_ITEMS

DB_FILE = "/root/bot/ratings.db"


# ========== БАЗА ДАННЫХ ==========

def init_coop_db():
    """Создаёт таблицы для кооператива"""
    with sqlite3.connect(DB_FILE) as conn:
        c = conn.cursor()
        
        c.execute('''CREATE TABLE IF NOT EXISTS tunnel_invites (
            invite_id TEXT PRIMARY KEY,
            host_id INTEGER,
            guest_id INTEGER,
            boss_id TEXT,
            room_number INTEGER,
            status TEXT DEFAULT 'pending',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            expires_at TIMESTAMP
        )''')
        
        c.execute('''CREATE TABLE IF NOT EXISTS tunnel_coop_battles (
            battle_id TEXT PRIMARY KEY,
            boss_id TEXT,
            host_id INTEGER,
            guest_id INTEGER,
            boss_hp INTEGER,
            boss_max_hp INTEGER,
            turn INTEGER DEFAULT 1,
            current_player INTEGER,
            host_hp INTEGER,
            guest_hp INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )''')
        
        conn.commit()


def generate_invite_id() -> str:
    """Генерирует уникальный ID приглашения"""
    return str(uuid.uuid4())[:8]


def create_coop_invite(host_id: int, boss_id: str, room_number: int) -> str:
    """Создаёт приглашение для друга"""
    invite_id = generate_invite_id()
    expires_at = datetime.now() + timedelta(minutes=5)
    
    print(f"🔥 СОЗДАЁМ ПРИГЛАШЕНИЕ: {invite_id}, host={host_id}, boss={boss_id}")
    
    with sqlite3.connect(DB_FILE) as conn:
        c = conn.cursor()
        c.execute('''INSERT INTO tunnel_invites 
                     (invite_id, host_id, boss_id, room_number, expires_at)
                     VALUES (?, ?, ?, ?, ?)''',
                  (invite_id, host_id, boss_id, room_number, expires_at))
        conn.commit()
        
        # 🆕 ПРОВЕРЯЕМ ЧТО СОХРАНИЛОСЬ
        c.execute("SELECT * FROM tunnel_invites WHERE invite_id = ?", (invite_id,))
        saved = c.fetchone()
        print(f"🔥 СОХРАНЕНО В БАЗУ: {saved}")
    
    return invite_id


def get_pending_invite(invite_id: str) -> Optional[Dict]:
    """Получает активное приглашение"""
    with sqlite3.connect(DB_FILE) as conn:
        c = conn.cursor()
        c.execute('''SELECT invite_id, host_id, boss_id, room_number, status, expires_at
                     FROM tunnel_invites 
                     WHERE invite_id = ? AND status = 'pending' AND expires_at > datetime('now')''',
                  (invite_id,))
        row = c.fetchone()
        if row:
            return {
                "invite_id": row[0],
                "host_id": row[1],
                "boss_id": row[2],
                "room_number": row[3],
                "status": row[4],
                "expires_at": row[5]
            }
    return None


def accept_coop_invite(invite_id: str, guest_id: int) -> bool:
    """Принимает приглашение"""
    with sqlite3.connect(DB_FILE) as conn:
        c = conn.cursor()
        c.execute('''UPDATE tunnel_invites 
                     SET guest_id = ?, status = 'accepted' 
                     WHERE invite_id = ? AND status = 'pending' AND expires_at > datetime('now')''',
                  (guest_id, invite_id))
        conn.commit()
        return c.rowcount > 0


def create_coop_battle(host_id: int, guest_id: int, boss_id: str, 
                       host_hp: int, guest_hp: int, boss_hp: int) -> str:
    """Создаёт кооперативный бой"""
    battle_id = str(uuid.uuid4())[:8]
    
    with sqlite3.connect(DB_FILE) as conn:
        c = conn.cursor()
        c.execute('''INSERT INTO tunnel_coop_battles 
                     (battle_id, boss_id, host_id, guest_id, boss_hp, boss_max_hp,
                      current_player, host_hp, guest_hp)
                     VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                  (battle_id, boss_id, host_id, guest_id, boss_hp, boss_hp,
                   host_id, host_hp, guest_hp))
        conn.commit()
    
    return battle_id


def get_coop_battle(battle_id: str) -> Optional[Dict]:
    """Получает данные кооперативного боя"""
    with sqlite3.connect(DB_FILE) as conn:
        c = conn.cursor()
        c.execute('''SELECT battle_id, boss_id, host_id, guest_id, boss_hp, boss_max_hp,
                     turn, current_player, host_hp, guest_hp
                     FROM tunnel_coop_battles WHERE battle_id = ?''',
                  (battle_id,))
        row = c.fetchone()
        if row:
            return {
                "battle_id": row[0],
                "boss_id": row[1],
                "host_id": row[2],
                "guest_id": row[3],
                "boss_hp": row[4],
                "boss_max_hp": row[5],
                "turn": row[6],
                "current_player": row[7],
                "host_hp": row[8],
                "guest_hp": row[9]
            }
    return None


def update_coop_battle(battle_id: str, **kwargs):
    """Обновляет данные кооперативного боя"""
    with sqlite3.connect(DB_FILE) as conn:
        c = conn.cursor()
        updates = [f"{k} = ?" for k in kwargs.keys()]
        values = list(kwargs.values()) + [battle_id]
        c.execute(f"UPDATE tunnel_coop_battles SET {','.join(updates)} WHERE battle_id = ?", values)
        conn.commit()


def delete_coop_battle(battle_id: str):
    """Удаляет кооперативный бой"""
    with sqlite3.connect(DB_FILE) as conn:
        c = conn.cursor()
        c.execute('DELETE FROM tunnel_coop_battles WHERE battle_id = ?', (battle_id,))
        conn.commit()


def cleanup_expired_invites():
    """Удаляет просроченные приглашения"""
    with sqlite3.connect(DB_FILE) as conn:
        c = conn.cursor()
        c.execute('DELETE FROM tunnel_invites WHERE expires_at < datetime("now")')
        conn.commit()


# ========== ОБРАБОТЧИКИ ПРИГЛАШЕНИЙ ==========

async def send_coop_invite(update: Update, context: ContextTypes.DEFAULT_TYPE, 
                           host_id: int, boss_id: str, room_number: int):
    """Отправляет приглашение другу"""
    query = update.callback_query
    
    invite_id = create_coop_invite(host_id, boss_id, room_number)
    
    # Получаем имя босса
    boss = TUNNEL_MONSTERS.get(boss_id, {})
    boss_name = boss.get("name", "Боссом")
    
    # СЛУЧАЙНЫЙ ВЫБОР РЕЧИ
    import random
    speeches = [
        f"""👥 *ПРИГЛАШЕНИЕ НА БОССА!*

Привет, брат! Мне нужна твоя помощь в битве со *{boss_name}*! 
Один я не справлюсь — этот гад слишком силён. 
Давай вместе наваляем ему и поделим лут!

🔗 *Ссылка:*
`/join_boss {invite_id}`

⚔️ _Приглашение действительно 5 минут._""",

        f"""👥 *ПРИГЛАШЕНИЕ НА БОССА!*

Слышишь зов приключений? *{boss_name}* охраняет несметные сокровища! 
Один я не возьму эту крепость — нужен верный напарник! 
Вместе мы войдём в легенды! 🐀⚔️🐀

🔗 *Ссылка:*
`/join_boss {invite_id}`

⏳ _Приглашение действительно 5 минут._""",

        f"""👥 *ПРИГЛАШЕНИЕ НА БОССА!*

Эй, напарник! Тут какой-то *{boss_name}* строит из себя хозяина туннелей! 
Поможешь объяснить ему кто здесь главный? Обещаю поделиться добычей 50/50! 🧀💰

🔗 *Ссылка:*
`/join_boss {invite_id}`

⌛ _5 минут и я иду без тебя!_""",

        f"""👥 *SOS! НУЖНА ПОМОЩЬ!*

Я застрял в логове *{boss_name}*! 
Один я долго не продержусь! Спаси меня, и мы вместе разорвём этого монстра! 

🔗 *Ссылка:*
`/join_boss {invite_id}`

🆘 _Приглашение действительно 5 минут!_""",

        f"""👥 *ТАЙНОЕ ПРИГЛАШЕНИЕ*

Шёпот древних говорит... *{boss_name}* пробудился. 
Лишь двое избранных могут победить его. 
Ты — один из них. Примешь вызов?

🔗 *Ссылка:*
`/join_boss {invite_id}`

🌙 _Приглашение исчезнет через 5 минут._"""
    ]
    
    text = random.choice(speeches)
    
    keyboard = [[InlineKeyboardButton("🔙 К боссу", callback_data="tunnel_continue")]]
    
    await query.message.delete()
    
    # ОТПРАВЛЯЕМ С КАРТИНКОЙ!
    image_path = "/root/bot/images/coop_invite.jpg"
    try:
        with open(image_path, "rb") as photo:
            await context.bot.send_photo(
                chat_id=host_id,
                photo=photo,
                caption=text,
                parse_mode=constants.ParseMode.MARKDOWN,
                reply_markup=InlineKeyboardMarkup(keyboard)
            )
    except:
        await context.bot.send_message(
            chat_id=host_id,
            text=text,
            parse_mode=constants.ParseMode.MARKDOWN,
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
    
    await query.answer("✅ Приглашение создано! Перешли его другу!")


async def handle_join_boss(update: Update, context: ContextTypes.DEFAULT_TYPE, invite_id: str):
    """Обрабатывает команду /join_boss"""
    user_id = update.effective_user.id
    user_name = update.effective_user.full_name
    
    cleanup_expired_invites()
    
    invite = get_pending_invite(invite_id)
    if not invite:
        await update.message.reply_text("❌ Приглашение не найдено или истекло!")
        return
    
    if invite["host_id"] == user_id:
        await update.message.reply_text("❌ Нельзя присоединиться к самому себе!")
        return
    
    if not accept_coop_invite(invite_id, user_id):
        await update.message.reply_text("❌ Не удалось принять приглашение!")
        return
    
    host_stats = get_character_stats(invite["host_id"])
    guest_stats = get_character_stats(user_id)
    
    boss = TUNNEL_MONSTERS.get(invite["boss_id"])
    if not boss:
        await update.message.reply_text("❌ Босс не найден!")
        return
    
    boss_hp = boss["health"] * 2
    
    battle_id = create_coop_battle(
        invite["host_id"], user_id, invite["boss_id"],
        host_stats["current_health"], guest_stats["current_health"], boss_hp
    )
    
    text = f"""⚔️ *КООПЕРАТИВНЫЙ БОЙ НАЧИНАЕТСЯ!*

🐀 *{user_name}* присоединяется к битве!

👥 *Босс:* {boss['name']}
❤️ Здоровье босса: *{boss_hp}* (усилен для двоих!)

🎮 *Ход первого игрока...*"""
    
    await context.bot.send_message(
        chat_id=invite["host_id"],
        text=text,
        parse_mode=constants.ParseMode.MARKDOWN
    )
    
    await update.message.reply_text(
        text,
        parse_mode=constants.ParseMode.MARKDOWN
    )
    
    await start_coop_battle(update, context, battle_id)


async def start_coop_battle(update: Update, context: ContextTypes.DEFAULT_TYPE, battle_id: str):
    """Запускает кооперативный бой"""
    battle = get_coop_battle(battle_id)
    if not battle:
        return
    
    boss = TUNNEL_MONSTERS.get(battle["boss_id"])
    
    context.user_data["coop_battle_id"] = battle_id
    context.user_data["coop_boss"] = boss
    
    current_player = battle["current_player"]
    
    text = f"""⚔️ *Бой с {boss['name']}* (кооператив)

❤️ Твоё здоровье: *{battle['host_hp'] if current_player == battle['host_id'] else battle['guest_hp']}*
💀 Здоровье босса: *{battle['boss_hp']}/{battle['boss_max_hp']}*

🎮 *Твой ход!*

*🛡️ Какую часть тела будешь защищать?*"""
    
    keyboard = [
        [InlineKeyboardButton("🧠 Защищать голову", callback_data=f"coop_defend_head_{battle_id}")],
        [InlineKeyboardButton("🦾 Защищать лапы", callback_data=f"coop_defend_paws_{battle_id}")],
        [InlineKeyboardButton("🫁 Защищать туловище", callback_data=f"coop_defend_body_{battle_id}")],
        [InlineKeyboardButton("🪢 Защищать хвост", callback_data=f"coop_defend_tail_{battle_id}")],
    ]
    
    await context.bot.send_message(
        chat_id=current_player,
        text=text,
        parse_mode=constants.ParseMode.MARKDOWN,
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


# ========== ГАРАНТИРОВАННЫЙ ДРОП С БОССА ==========

def process_boss_loot(boss_id: str) -> List[str]:
    """Обрабатывает дроп с босса (гарантированный предмет)"""
    items = []
    
    # Гарантированный обычный ИЛИ редкий предмет
    if random.randint(1, 100) <= 50:
        common_items = [iid for iid, data in ALL_ITEMS.items() 
                        if data.get("rarity") == "common" and data.get("type") == "equipment"]
        if common_items:
            items.append(random.choice(common_items))
    else:
        rare_items = [iid for iid, data in ALL_ITEMS.items() 
                      if data.get("rarity") == "rare" and data.get("type") == "equipment"]
        if rare_items:
            items.append(random.choice(rare_items))
    
    # Шанс на легендарку (15%)
    if random.randint(1, 100) <= 15:
        legendary_items = [iid for iid, data in ALL_ITEMS.items() 
                           if data.get("rarity") == "legendary" and data.get("type") == "equipment"]
        if legendary_items:
            items.append(random.choice(legendary_items))
    
    # Шанс на мифик (5%)
    if random.randint(1, 100) <= 5:
        mythic_items = [iid for iid, data in ALL_ITEMS.items() 
                        if data.get("rarity") == "mythic" and data.get("type") == "equipment"]
        if mythic_items:
            items.append(random.choice(mythic_items))
    
    return items


def give_coop_loot(host_id: int, guest_id: int, boss_id: str) -> Dict:
    """Выдаёт лут обоим игрокам"""
    host_loot = process_boss_loot(boss_id)
    guest_loot = process_boss_loot(boss_id)
    
    for item_id in host_loot:
        add_item(host_id, item_id)
    for item_id in guest_loot:
        add_item(guest_id, item_id)
    
    return {
        "host_items": host_loot,
        "guest_items": guest_loot
    }


# Инициализация
init_coop_db()