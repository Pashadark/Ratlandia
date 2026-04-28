"""Комнаты и события режима Туннели"""

import random
import sqlite3
import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from telegram import constants
from handlers.tunnel_effects import get_random_blessing, apply_blessing_effect
from handlers.tunnel_coop import send_coop_invite

# ЕДИНАЯ СИСТЕМА ХАРАКТЕРИСТИК
from handlers.character import (
    get_character_stats, take_damage, heal_damage,
    increment_tunnel_deaths, add_tunnel_crumbs
)

from handlers.tunnel_monsters import (
    get_tunnel_run, advance_room, end_tunnel_run, add_run_loot, set_blessed,
    TUNNEL_MONSTERS, get_random_monster, mark_boss_defeated, update_tunnel_run,
    process_boss_loot
)
from handlers.inventory import add_item, add_crumbs, add_xp, get_crumbs

DB_FILE = "/root/bot/ratings.db"
ROOMS_IMAGE_PATH = "/root/bot/images/tunnel_rooms"


# ========== КАРТЫ КОМНАТ ==========
ROOM_IMAGES = {
    # Основные комнаты по номерам
    1: "room_entrance.jpg",
    2: "room_cat_lair.jpg",
    3: "room_pantry.jpg",
    4: "room_pipe_maze.jpg",
    5: "room_nest.jpg",
    6: "room_flooded.jpg",
    7: "room_garbage.jpg",
    8: "room_draft.jpg",
    9: "room_fork.jpg",
    10: "room_tunnel_deep.jpg",
    11: "room_rat_king_hall.jpg",
    12: "room_crystal_cave.jpg",
    13: "room_mushroom_grove.jpg",
    14: "room_spider_den.jpg",
    15: "room_bone_hall.jpg",
    16: "room_waterfall.jpg",
    17: "room_abandoned_camp.jpg",
    18: "room_fungus_forest.jpg",
    19: "room_ancient_door.jpg",
    20: "room_boss_cat.jpg",
    # Особые комнаты
    "treasure": "room_chest.jpg",
    "altar": "room_altar.jpg",
    "rest": "room_nest.jpg",
    "trap": "room_trap.jpg",
    "empty": "room_draft.jpg",
}


def get_room_image(room_key):
    """Возвращает путь к изображению комнаты"""
    filename = ROOM_IMAGES.get(room_key)
    if filename:
        full_path = f"{ROOMS_IMAGE_PATH}/{filename}"
        if os.path.exists(full_path):
            return full_path
    return None


async def send_room_message(user_id, text, keyboard, context, room_key=None):
    """Отправляет сообщение с фото комнаты или текстом"""
    image_path = get_room_image(room_key) if room_key else None
    
    if image_path:
        try:
            with open(image_path, "rb") as photo:
                await context.bot.send_photo(
                    chat_id=user_id,
                    photo=photo,
                    caption=text,
                    parse_mode=constants.ParseMode.MARKDOWN,
                    reply_markup=InlineKeyboardMarkup(keyboard)
                )
                return
        except:
            pass
    
    await context.bot.send_message(
        chat_id=user_id,
        text=text,
        parse_mode=constants.ParseMode.MARKDOWN,
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


async def safe_edit_or_send(query, user_id, text, keyboard, context, room_key=None):
    """Безопасно редактирует сообщение или отправляет новое с фото"""
    try:
        await query.message.edit_text(
            text,
            parse_mode=constants.ParseMode.MARKDOWN,
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
    except Exception as e:
        try:
            await query.message.delete()
        except:
            pass
        await send_room_message(user_id, text, keyboard, context, room_key)


# ========== ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ ==========

def update_tunnel_run_local(user_id: int, **kwargs):
    """Обновляет данные активного забега"""
    with sqlite3.connect(DB_FILE) as conn:
        c = conn.cursor()
        updates = [f"{k} = ?" for k in kwargs.keys()]
        values = list(kwargs.values()) + [user_id]
        c.execute(f"UPDATE tunnel_run SET {','.join(updates)} WHERE user_id = ?", values)
        conn.commit()


# ========== ВХОД В КОМНАТУ ==========

async def enter_room(update: Update, context: ContextTypes.DEFAULT_TYPE, user_id: int):
    """Вход в комнату (текущую или следующую)"""
    query = update.callback_query
    
    run_data = get_tunnel_run(user_id)
    stats = get_character_stats(user_id)
    
    if not run_data:
        await query.answer("❌ У тебя нет активного забега!")
        return
    
    current_room = run_data["current_room"]
    
    if current_room == 20:
        await enter_boss_room(update, context, user_id, run_data)
        return
    
    room_type = random.choices(
        ["monster", "treasure", "altar", "trap", "empty"],
        weights=[50, 20, 10, 15, 5]
    )[0]
    
    if room_type == "monster":
        await enter_monster_room(update, context, user_id, run_data, current_room)
    elif room_type == "treasure":
        await enter_treasure_room(update, context, user_id, run_data)
    elif room_type == "altar":
        await enter_altar_room(update, context, user_id, run_data)
    elif room_type == "trap":
        await enter_trap_room(update, context, user_id, run_data)
    else:
        await enter_empty_room(update, context, user_id, run_data, current_room)


async def enter_boss_room(update: Update, context: ContextTypes.DEFAULT_TYPE, user_id: int, run_data: dict):
    """Вход в комнату с боссом"""
    query = update.callback_query
    
    stats = get_character_stats(user_id)
    total_runs = stats.get("total_tunnel_runs", 0)
    
    if total_runs >= 10:
        boss_id = "old_blind_cat"
    elif total_runs >= 5:
        boss_id = "two_headed_rat"
    else:
        boss_id = "black_ferret"
    
    boss = TUNNEL_MONSTERS.get(boss_id)
    
    text = f"""🚪 *Комната 20 — Логово босса*

_Ты чувствуешь, что это последняя комната. Воздух тяжёлый, пахнет опасностью..._

Впереди ты видишь *{boss['name']}*!

_{boss['desc']}_

⚔️ Приготовься к битве!
"""
    
    # 🆕 ДОБАВЛЕНА КНОПКА "СБЕЖАТЬ"
    keyboard = [
        [InlineKeyboardButton("⚔️ Сразиться с боссом", callback_data=f"tunnel_fight_{boss_id}")],
        [InlineKeyboardButton("👥 Позвать друга", callback_data=f"tunnel_invite_{boss_id}")],
        [InlineKeyboardButton("🏃 Сбежать", callback_data="tunnel_flee_new")],
    ]
    
    await query.message.delete()
    await send_room_message(user_id, text, keyboard, context, 10)


async def enter_monster_room(update: Update, context: ContextTypes.DEFAULT_TYPE, user_id: int, run_data: dict, room_num: int):
    """Вход в комнату с монстром"""
    query = update.callback_query
    
    if room_num <= 6:
        level = 1
    elif room_num <= 12:
        level = 2
    elif room_num <= 18:
        level = 3
    else:
        level = 4
    
    monster = get_random_monster(level)
    
    if not monster:
        monster = TUNNEL_MONSTERS.get("blind_mole")
        monster["id"] = "blind_mole"
    
    text = f"""🚪 *Комната {room_num}/20*

_Ты осторожно заходишь в тёмную комнату..._

В углу ты замечаешь движение! Это *{monster['name']}*!

_{monster['desc']}_

Что будешь делать?
"""
    
    keyboard = [
        [InlineKeyboardButton("⚔️ Атаковать", callback_data=f"tunnel_fight_{monster['id']}")],
        [InlineKeyboardButton("🏃 Попытаться сбежать", callback_data="tunnel_flee_new")],
    ]
    
    await query.message.delete()
    await send_room_message(user_id, text, keyboard, context, room_num)


async def enter_treasure_room(update: Update, context: ContextTypes.DEFAULT_TYPE, user_id: int, run_data: dict):
    """Вход в сокровищницу"""
    query = update.callback_query
    
    text = f"""🚪 *Комната {run_data['current_room']}/20 — Сокровищница*

_Ты находишь комнату, полную старых сундуков!_

Перед тобой три сундука. Какой откроешь?
"""
    
    keyboard = [
        [InlineKeyboardButton("📦 Левый сундук", callback_data="chest_left")],
        [InlineKeyboardButton("📦 Средний сундук", callback_data="chest_middle")],
        [InlineKeyboardButton("📦 Правый сундук", callback_data="chest_right")],
        [InlineKeyboardButton("🚶 Пропустить", callback_data="tunnel_skip_room")],
    ]
    
    await query.message.delete()
    await send_room_message(user_id, text, keyboard, context, "treasure")


async def enter_altar_room(update: Update, context: ContextTypes.DEFAULT_TYPE, user_id: int, run_data: dict):
    """Вход в комнату с алтарём"""
    query = update.callback_query
    
    text = f"""🚪 *Комната {run_data['current_room']}/20 — Древний алтарь*

_В центре комнаты стоит древний алтарь, покрытый мхом и паутиной. Ты чувствуешь странную энергию, исходящую от него._

На алтаре надпись: *"Пожертвуй крошки — получи благословение"*

🧀 У тебя в мешке: {run_data['crumbs_collected']} крошек

Что сделаешь?
"""
    
    keyboard = [
        [InlineKeyboardButton("✨ Пожертвовать 10 крошек", callback_data="altar_offer")],
        [InlineKeyboardButton("🚶 Пройти мимо", callback_data="tunnel_skip_room")],
    ]
    
    await query.message.delete()
    await send_room_message(user_id, text, keyboard, context, "altar")


async def enter_trap_room(update: Update, context: ContextTypes.DEFAULT_TYPE, user_id: int, run_data: dict):
    """Вход в комнату с ловушкой"""
    query = update.callback_query
    
    stats = get_character_stats(user_id)
    
    dodge_chance = stats["agility"] * 5
    dodged = random.randint(1, 100) <= dodge_chance
    
    if dodged:
        text = f"""🚪 *Комната {run_data['current_room']}/20 — Ловушка!*

_Ты замечаешь натянутую верёвку и вовремя отпрыгиваешь!_

✅ Ловушка обезврежена! Ты проходишь дальше.
"""
    else:
        damage = random.randint(5, 15)
        new_hp = take_damage(user_id, damage)
        
        text = f"""🚪 *Комната {run_data['current_room']}/20 — Ловушка!*

_Ты наступаешь на скрытую плиту, и в тебя летят дротики!_

💔 Ты получаешь {damage} урона!
❤️ Здоровье: {new_hp}/{stats['max_health']}
"""
        
        if new_hp <= 0:
            increment_tunnel_deaths(user_id)
            result = end_tunnel_run(user_id, died=True)
            add_tunnel_crumbs(user_id, result['crumbs'])
            text += f"\n\n💀 *Ты погиб!*\nПотеряно крошек: {result['crumbs']}"
            keyboard = [[InlineKeyboardButton("🏠 В нору", callback_data="tunnel_menu")]]
            await query.message.delete()
            await send_room_message(user_id, text, keyboard, context, "trap")
            return
    
    keyboard = [[InlineKeyboardButton("➡️ Идти дальше", callback_data="tunnel_next_room")]]
    await query.message.delete()
    await send_room_message(user_id, text, keyboard, context, run_data['current_room'])


async def enter_empty_room(update: Update, context: ContextTypes.DEFAULT_TYPE, user_id: int, run_data: dict, room_num: int):
    """Вход в пустую комнату"""
    query = update.callback_query
    
    stats = get_character_stats(user_id)
    find_chance = stats["intelligence"] * 3
    
    extra_text = ""
    if random.randint(1, 100) <= find_chance:
        crumbs_found = random.randint(3, 8)
        new_crumbs = run_data["crumbs_collected"] + crumbs_found
        update_tunnel_run(user_id, crumbs_collected=new_crumbs)
        extra_text = f"\n\n_Благодаря своей внимательности ты находишь {crumbs_found} крошек в углу!_"
    
    text = f"""🚪 *Комната {room_num}/20*

_Комната пуста. Только пыль и паутина._{extra_text}
"""
    
    keyboard = [[InlineKeyboardButton("➡️ Идти дальше", callback_data="tunnel_next_room")]]
    await query.message.delete()
    await send_room_message(user_id, text, keyboard, context, room_num)


# ========== ОБРАБОТКА СОБЫТИЙ ==========

async def handle_chest_choice(update: Update, context: ContextTypes.DEFAULT_TYPE, user_id: int, choice: str):
    """Обработка выбора сундука"""
    query = update.callback_query
    
    run_data = get_tunnel_run(user_id)
    
    roll = random.randint(1, 100)
    
    if choice == "left":
        if roll <= 50:
            reward_type = "crumbs"
            amount = random.randint(10, 20)
        elif roll <= 80:
            reward_type = "item"
        else:
            reward_type = "trap"
            damage = random.randint(5, 10)
    elif choice == "middle":
        if roll <= 30:
            reward_type = "crumbs"
            amount = random.randint(15, 25)
        elif roll <= 70:
            reward_type = "item"
        else:
            reward_type = "trap"
            damage = random.randint(8, 15)
    else:
        if roll <= 40:
            reward_type = "crumbs"
            amount = random.randint(5, 15)
        elif roll <= 90:
            reward_type = "item"
        else:
            reward_type = "trap"
            damage = random.randint(3, 8)
    
    if reward_type == "crumbs":
        new_crumbs = run_data["crumbs_collected"] + amount
        update_tunnel_run(user_id, crumbs_collected=new_crumbs)
        text = f"📦 *Сундук открыт!*\n\nВнутри ты находишь *{amount} крошек*!\n🧀 Всего в мешке: {new_crumbs}"
    
    elif reward_type == "item":
        from handlers.items import ALL_ITEMS
        possible_items = [id for id, item in ALL_ITEMS.items() if item.get("type") in ["consumable", "equipment"]]
        if possible_items:
            item_id = random.choice(possible_items)
            item = ALL_ITEMS[item_id]
            add_item(user_id, item_id)
            text = f"📦 *Сундук открыт!*\n\nВнутри ты находишь: {item['icon']} *{item['name']}*!"
        else:
            text = f"📦 *Сундук открыт!*\n\nВнутри пусто..."
    
    else:
        new_hp = take_damage(user_id, damage)
        stats = get_character_stats(user_id)
        text = f"📦 *Сундук открыт!*\n\n💥 *Ловушка!* Из сундука вылетают дротики!\n💔 Ты получаешь {damage} урона!\n❤️ Здоровье: {new_hp}/{stats['max_health']}"
        
        if new_hp <= 0:
            increment_tunnel_deaths(user_id)
            result = end_tunnel_run(user_id, died=True)
            add_tunnel_crumbs(user_id, result['crumbs'])
            text += f"\n\n💀 *Ты погиб!*\nПотеряно крошек: {result['crumbs']}"
            keyboard = [[InlineKeyboardButton("🏠 В нору", callback_data="tunnel_menu")]]
            await safe_edit_or_send(query, user_id, text, keyboard, context, "treasure")
            return
    
    keyboard = [[InlineKeyboardButton("➡️ Идти дальше", callback_data="tunnel_next_room")]]
    await safe_edit_or_send(query, user_id, text, keyboard, context, "treasure")


async def handle_altar_offer(update: Update, context: ContextTypes.DEFAULT_TYPE, user_id: int):
    """Обработка пожертвования на алтаре"""
    query = update.callback_query
    
    total_crumbs = get_crumbs(user_id)
    
    if total_crumbs < 10:
        await query.answer(f"❌ Недостаточно крошек! У тебя {total_crumbs}, нужно 10.", show_alert=True)
        return
    
    add_crumbs(user_id, -10)
    
    run_data = get_tunnel_run(user_id)
    blessing = get_random_blessing()
    result_text, health_updated, new_hp = apply_blessing_effect(user_id, blessing, run_data)
    
    await query.answer(f"✨ Получено: {blessing['name']}!\n{blessing['desc']}", show_alert=True)
    
    blessing_texts = {
        "instant_heal": "_Древний алтарь старых мышей вспыхивает золотым светом. Ты слышишь шёпот предков, что сражались в этих туннелях тысячи лет назад. Их духи благословляют тебя, залечивая раны, нанесённые в жестоких битвах с котами и крысами._",
        "full_heal": "_Древний алтарь старых мышей озаряется ослепительным сиянием. Великие целители прошлого, что спасали целые выводки от гибели, направляют всю свою мощь на тебя. Твои раны закрываются на глазах, а усталость уходит прочь._",
        "damage_boost": "_Древний алтарь старых мышей наливается алым сиянием. Ты чувствуешь ярость великих воинов, что пали в битвах с котами и крысами. Их боевой дух наполняет твои мышцы невиданной мощью._",
        "crit_blessing": "_Древний алтарь старых мышей вспыхивает ярко-оранжевым пламенем. Великие охотники на котов, что находили слабые места даже у самых грозных врагов, даруют тебе свой смертоносный глаз._",
        "vampirism_blessing": "_Древний алтарь старых мышей наполняется тёмно-багровым сиянием. Безжалостные воины прошлого, что выживали в самых кровавых битвах, делятся с тобой своей жаждой жизни._",
        "double_strike": "_Древний алтарь старых мышей окутывается изумрудным туманом. Духи разведчиков и лазутчиков, что проникали в самые тёмные норы, делятся с тобой своей ловкостью и быстротой._",
        "health_boost": "_Древний алтарь старых мышей сияет тёплым янтарным светом. Хранители нор и защитники выводков, что отдали жизни за свой народ, укрепляют твоё тело незримой бронёй._",
        "dodge_boost": "_Древний алтарь старых мышей мерцает серебристыми искрами. Тени прошлого, что ускользали от самых цепких кошачьих лап, учат тебя искусству уклонения._",
        "shield_blessing": "_Древний алтарь старых мышей сияет лазурным светом. Защитники нор и хранители выводков, что отдали жизни за свой народ, окружают тебя незримым щитом._",
        "regen_blessing": "_Древний алтарь старых мышей источает нежно-зелёное сияние. Мудрые травники и целители древности, что знали секреты быстрого восстановления, благословляют тебя._",
        "thorns_blessing": "_Древний алтарь старых мышей покрывается колючим терновым узором. Духи мстителей, что забирали врагов с собой в могилу, окутывают тебя аурой боли._",
        "find_boost": "_Древний алтарь старых мышей мерцает фиолетовыми искрами. Мудрецы и хранители знаний, что веками изучали тайны подземелий, открывают тебе секреты древних туннелей._",
        "crumbs_boost": "_Древний алтарь старых мышей переливается золотисто-коричневым светом. Щедрые собиратели прошлого, что находили еду в самых пустых комнатах, делятся с тобой своим чутьём._",
        "xp_boost": "_Древний алтарь старых мышей светится мягким голубым сиянием. Великие герои древности, чьи имена высечены на стенах Зала Достижений, благословляют твой путь к славе._",
        "lucky_blessing": "_Древний алтарь старых мышей переливается всеми цветами радуги. Самые везучие искатели приключений, что находили сокровища в пустых комнатах, делятся своей удачей._",
        "stat_point": "_Древний алтарь старых мышей излучает чистое белое сияние. Древние мудрецы, что постигли все тайны этого мира, даруют тебе частицу своих знаний._",
        "free_reroll": "_Древний алтарь старых мышей мерцает переливчатым светом. Духи-трикстеры, что вечно играли с судьбой, даруют тебе шанс изменить предначертанное._"
    }
    
    blessing_id = blessing.get("id", "")
    flavor_text = blessing_texts.get(blessing_id, "_Древний алтарь старых мышей принимает твоё подношение. Ты чувствуешь, как древняя магия наполняет тебя силой._")
    
    text = f"✨ *Алтарь принимает твой дар!*\n\n{flavor_text}\n\n*Даруют тебе:* {blessing['icon']} *{blessing['name']}*\n(_{blessing['desc']}_)"
    
    if health_updated and new_hp is not None:
        stats = get_character_stats(user_id)
        text += f"\n\n❤️ Здоровье: {new_hp}/{stats['max_health']}"
    
    keyboard = [[InlineKeyboardButton("➡️ Идти дальше", callback_data="tunnel_next_room")]]
    
    blessing_to_image = {
        "instant_heal": "blessing_heal.jpg",
        "full_heal": "blessing_heal.jpg",
        "damage_boost": "blessing_strength.jpg",
        "crit_blessing": "blessing_crit.jpg",
        "vampirism_blessing": "blessing_vampirism.jpg",
        "double_strike": "blessing_agility.jpg",
        "dodge_boost": "blessing_agility.jpg",
        "health_boost": "blessing_heal.jpg",
        "shield_blessing": "blessing_shield.jpg",
        "regen_blessing": "blessing_regen.jpg",
        "thorns_blessing": "blessing_thorns.jpg",
        "find_boost": "blessing_intelligence.jpg",
        "crumbs_boost": "blessing_luck.jpg",
        "xp_boost": "blessing_intelligence.jpg",
        "lucky_blessing": "blessing_luck.jpg",
        "stat_point": "blessing_intelligence.jpg",
        "free_reroll": "blessing_luck.jpg"
    }
    
    image_file = blessing_to_image.get(blessing_id, "blessing_heal.jpg")
    image_path = f"/root/bot/images/tunnel_altar/{image_file}"
    
    await query.message.delete()
    
    try:
        with open(image_path, "rb") as photo:
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


# ========== ПЕРЕХОДЫ ==========

async def process_room_transition(update: Update, context: ContextTypes.DEFAULT_TYPE, user_id: int):
    """Переход в следующую комнату"""
    query = update.callback_query
    
    run_data = get_tunnel_run(user_id)
    
    if not run_data:
        await query.answer("❌ Забег не найден!")
        return
    
    advance_room(user_id)
    run_data = get_tunnel_run(user_id)
    
    if run_data["current_room"] > 20:
        await finish_run(update, context, user_id)
    else:
        await enter_room(update, context, user_id)


async def process_skip_room(update: Update, context: ContextTypes.DEFAULT_TYPE, user_id: int):
    """Пропуск комнаты (без награды)"""
    query = update.callback_query
    
    run_data = get_tunnel_run(user_id)
    
    if not run_data:
        await query.answer("❌ Забег не найден!")
        return
    
    advance_room(user_id)
    run_data = get_tunnel_run(user_id)
    
    if run_data["current_room"] > 20:
        await finish_run(update, context, user_id)
    else:
        await enter_room(update, context, user_id)


async def finish_run(update: Update, context: ContextTypes.DEFAULT_TYPE, user_id: int):
    """Завершение забега (успешное)"""
    query = update.callback_query
    
    result = end_tunnel_run(user_id, died=False, context=context)
    
    add_tunnel_crumbs(user_id, result['crumbs'])
    
    text = f"""🎉 *Забег завершён!*

_Ты успешно выбрался из туннелей!_

▸ *Итоги:*
  🧀 Крошек добыто: {result['crumbs']}
  ✨ Опыта получено: {result['xp']}

_Отличная работа, искатель приключений!_
"""
    
    keyboard = [[InlineKeyboardButton("🏠 В нору", callback_data="tunnel_menu")]]
    
    await safe_edit_or_send(query, user_id, text, keyboard, context)


async def go_home(update: Update, context: ContextTypes.DEFAULT_TYPE, user_id: int):
    """Добровольное возвращение домой"""
    query = update.callback_query
    
    run_data = get_tunnel_run(user_id)
    
    if not run_data:
        await query.answer("❌ Нет активного забега!")
        return
    
    crumbs_lost = int(run_data["crumbs_collected"] * 0.3)
    final_crumbs = run_data["crumbs_collected"] - crumbs_lost
    
    add_tunnel_crumbs(user_id, final_crumbs)
    
    with sqlite3.connect(DB_FILE) as conn:
        c = conn.cursor()
        c.execute('DELETE FROM tunnel_run WHERE user_id = ?', (user_id,))
        conn.commit()
    
    add_crumbs(user_id, final_crumbs)
    add_xp(user_id, run_data["xp_collected"], context)
    
    text = f"""🏠 *Возвращение домой*

_Ты решаешь не рисковать и возвращаешься в нору._

▸ *Итоги:*
  🧀 Крошек добыто: {final_crumbs} (потеряно {crumbs_lost})
  ✨ Опыта получено: {run_data['xp_collected']}

_Лучше быть живым и с небольшим уловом, чем мёртвым героем!_
"""
    
    keyboard = [[InlineKeyboardButton("🏠 В нору", callback_data="tunnel_menu")]]
    
    image_path = "/root/bot/images/tunnel_go_home.jpg"
    await query.message.delete()
    
    try:
        with open(image_path, "rb") as photo:
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