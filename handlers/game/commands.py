"""Режим Туннели — главный обработчик"""

import random
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, CommandHandler, CallbackQueryHandler
from telegram import constants
from handlers.inventory import get_level, use_consumable, get_inventory

# 🆕 ЕДИНАЯ СИСТЕМА ХАРАКТЕРИСТИК
from handlers.character import (
    get_character_stats, update_character_stats,
    take_damage, heal_damage, upgrade_stat, increment_tunnel_runs,
    sync_level_and_points, get_tunnel_statistics, get_defeated_bosses,
    get_active_effects
)
from handlers.healing import restore_health_over_time


from handlers.tunnel_monsters import (
    get_tunnel_run, start_tunnel_run, end_tunnel_run, TUNNEL_MONSTERS,
    init_tunnel_monsters_db
)
from handlers.tunnel_battle import (
    start_battle, handle_tunnel_attack, handle_tunnel_flee_new,
    handle_tunnel_break_free, handle_tunnel_continue_battle,
    handle_tunnel_defend
)
from handlers.tunnel_rooms import (
    enter_room, process_room_transition, process_skip_room,
    handle_chest_choice, handle_altar_offer, go_home
)


# ========== КОМАНДЫ И МЕНЮ ==========

async def tunnel_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Команда /tunnel — вход в режим Туннелей"""
    user_id = update.effective_user.id
    
    if update.effective_chat.type != "private":
        if update.callback_query:
            await update.callback_query.answer("❌ Туннели доступны только в личных сообщениях!", show_alert=True)
        else:
            await update.message.reply_text("❌ Туннели доступны только в личных сообщениях!\n\n👉 Напиши мне в личку: @testpasha_bot")
        return
    
    if update.callback_query:
        query = update.callback_query
        await query.message.delete()
        await show_tunnel_menu(update, context, user_id)
    else:
        await show_tunnel_menu(update, context, user_id)


async def handle_use_potion(update: Update, context: ContextTypes.DEFAULT_TYPE, user_id: int):
    """Использование зелья здоровья"""
    query = update.callback_query
    inventory = get_inventory(user_id)
    
    if inventory.get("health_potion", 0) <= 0:
        await query.answer("❌ Нет зелий здоровья!", show_alert=True)
        return
    
    stats = get_character_stats(user_id)
    
    if stats['current_health'] >= stats['max_health']:
        await query.answer("❌ Здоровье уже полное!", show_alert=True)
        return
    
    if use_consumable(user_id, "health_potion"):
        heal = 30
        new_hp = heal_damage(user_id, heal)
        await query.answer(f"✅ Восстановлено {heal} здоровья!")
        await show_tunnel_menu(update, context, user_id)
    else:
        await query.answer("❌ Не удалось использовать зелье!", show_alert=True)


async def show_tunnel_menu(update: Update, context: ContextTypes.DEFAULT_TYPE, user_id: int):
    """Показывает главное меню туннелей"""
    
    restore_health_over_time(user_id, context)
    main_level = get_level(user_id)
    sync_level_and_points(user_id, main_level)
    
    stats = get_character_stats(user_id)
    run_data = get_tunnel_run(user_id)
    
    # Расчёт значений
    damage_min = stats['strength']
    damage_max = stats['strength'] + 3
    dodge = min(40, stats['agility'] * 5)
    find = stats['intelligence'] * 3
    
    # Получаем статистику туннелей
    tunnel_stats = get_tunnel_statistics(user_id)
    
    # Получаем поверженных боссов
    defeated_bosses = get_defeated_bosses(user_id)
    all_bosses = ["mother_rat", "two_headed_rat", "black_ferret", "old_blind_cat"]
    bosses_defeated_count = len(defeated_bosses)
    
    # Получаем активные эффекты
    active_effects = get_active_effects(user_id)
    
    # Проверяем наличие зелий здоровья
    inventory = get_inventory(user_id)
    health_potions = inventory.get("health_potion", 0)
    
    text = f"""🕳️ *Туннели Ратляндии*

_Старые заброшенные туннели уходят глубоко под землю. Здесь обитают странные существа, забытые временем. Опасность поджидает за каждым углом, но награда стоит риска._

"""
    
    # Активные эффекты
    text += "▸ *Твои эффекты:*\n"
    if active_effects:
        for effect in active_effects:
            text += f"  {effect}\n"
    else:
        text += "  ✨ Нет активных эффектов"
    
    text += f"""

▸ *Статистика:*
  🕳️ Вылазок: {tunnel_stats['total_runs']}
  💀 Смертей: {tunnel_stats['deaths']}
  👑 Боссов побеждено: {bosses_defeated_count}/{len(all_bosses)}
  🧀 Всего крошек добыто: {tunnel_stats['total_crumbs']}

"""
    
    # Поверженные боссы
    text += "▸ *Поверженные боссы:*\n"
    boss_names = {
        "mother_rat": "Мать-Крыса",
        "two_headed_rat": "Двухголовый",
        "black_ferret": "Чёрный Хорёк",
        "old_blind_cat": "Старый Слепой Кот"
    }
    for boss_id in all_bosses:
        if boss_id in defeated_bosses:
            text += f"  ✅ {boss_names[boss_id]}\n"
        else:
            text += f"  🔒 {boss_names[boss_id]}\n"
    
    if run_data:
        text += f"""
▸ *Активный забег:*
  📍 Комната: {run_data['current_room']}/10
  🧀 Крошек: {run_data['crumbs_collected']}
  ✨ Опыта: {run_data['xp_collected']}

"""
        # Кнопки для активного забега
        keyboard = [
            [InlineKeyboardButton("🗡 Продолжить забег", callback_data="tunnel_continue")],
        ]
        if health_potions > 0:
            keyboard.append([InlineKeyboardButton(f"🧪 Использовать зелье здоровья ({health_potions})", callback_data="tunnel_use_potion")])
        keyboard.extend([
            [InlineKeyboardButton("🎒 Инвентарь", callback_data="tunnel_inventory")],
            [InlineKeyboardButton("🏰 В город", callback_data="city_menu")],
        ])
    else:
        if stats['current_health'] > 3:
            text += "\n_Ты полон сил и готов к вылазке!_"
            
            # Кнопки для нового забега
            keyboard = [
                [InlineKeyboardButton("🗡 Заползти внутрь", callback_data="tunnel_start")],
            ]
            if health_potions > 0:
                keyboard.append([InlineKeyboardButton(f"🧪 Использовать зелье здоровья ({health_potions})", callback_data="tunnel_use_potion")])
            keyboard.extend([
                [InlineKeyboardButton("🎒 Инвентарь", callback_data="tunnel_inventory")],
                [InlineKeyboardButton("🏰 В город", callback_data="city_menu")],
            ])
        else:
            text += "\n_Ты слишком слаб для вылазки. Отдохни._"
            keyboard = [
                [InlineKeyboardButton("🛌 Отдых", callback_data="tunnel_rest_info")],
            ]
            if health_potions > 0:
                keyboard.append([InlineKeyboardButton(f"🧪 Использовать зелье здоровья ({health_potions})", callback_data="tunnel_use_potion")])
            keyboard.append([InlineKeyboardButton("🏰 В город", callback_data="city_menu")])
    
    if update.callback_query:
        await update.callback_query.message.delete()
    
    try:
        await context.bot.send_photo(
            chat_id=user_id,
            photo=open("/root/bot/images/tunnel_entrance.jpg", "rb"),
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


async def show_stats_menu(update: Update, context: ContextTypes.DEFAULT_TYPE, user_id: int):
    """Показывает меню распределения характеристик"""
    query = update.callback_query
    
    # ВСЕГДА УДАЛЯЕМ ПРЕДЫДУЩЕЕ СООБЩЕНИЕ С ФОТО
    try:
        await query.message.delete()
    except:
        pass
    
    stats = get_character_stats(user_id)
    
    text = f"""📊 *Распределение характеристик*

_У тебя есть {stats['stat_points']} свободных очков._

▸ *Текущие характеристики:*
  💪 Сила: {stats['strength']} — +{stats['strength']} к урону (+10 к здоровью)
  🍀 Ловкость: {stats['agility']} — +{stats['agility'] * 5}% шанс уклонения (макс 40%)
  🧠 Интеллект: {stats['intelligence']} — +{stats['intelligence'] * 3}% шанс найти тайник

"""
    
    keyboard = []
    
    if stats['stat_points'] > 0:
        keyboard.extend([
            [InlineKeyboardButton("💪 +1 Сила", callback_data="tunnel_stat_strength")],
            [InlineKeyboardButton("🍀 +1 Ловкость", callback_data="tunnel_stat_agility")],
            [InlineKeyboardButton("🧠 +1 Интеллект", callback_data="tunnel_stat_intelligence")],
        ])
    
    keyboard.append([InlineKeyboardButton("🔙 Назад", callback_data="tunnel_menu")])
    
    # ОТПРАВЛЯЕМ НОВОЕ ФОТО
    image_path = "/root/bot/images/tunnel_stats.jpg"
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

async def handle_stat_upgrade(update: Update, context: ContextTypes.DEFAULT_TYPE, user_id: int, stat: str):
    """Обрабатывает повышение характеристики"""
    query = update.callback_query
    
    success, message, new_stats = upgrade_stat(user_id, stat)
    
    if success:
        await query.answer(message)
        # УДАЛЯЕМ ПРЕДЫДУЩЕЕ СООБЩЕНИЕ ПЕРЕД ПОКАЗОМ МЕНЮ
        try:
            await query.message.delete()
        except:
            pass
        await show_stats_menu(update, context, user_id)
    else:
        await query.answer(message, show_alert=True)


async def show_rest_info(update: Update, context: ContextTypes.DEFAULT_TYPE, user_id: int):
    """Показывает информацию об отдыхе"""
    query = update.callback_query
    
    # Восстанавливаем здоровье
    restore_health_over_time(user_id, context)
    stats = get_character_stats(user_id)
    
    text = f"""🛌 *Отдых и восстановление*

_Твоё здоровье восстанавливается со временем._

❤️ Текущее: {stats['current_health']}/{stats['max_health']}
⏳ +10 здоровья каждый час

"""
    
    if stats['current_health'] < stats['max_health']:
        hours_needed = max(1, (stats['max_health'] - stats['current_health']) // 10)
        text += f"\n_До полного восстановления: ~{hours_needed} ч._"
    
    keyboard = [[InlineKeyboardButton("🔙 Назад", callback_data="tunnel_menu")]]
    
    await query.message.delete()
    
    # 🆕 ОТПРАВЛЯЕМ С КАРТИНКОЙ
    image_path = "/root/bot/images/tunnel_rest.jpg"
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


async def show_inventory(update: Update, context: ContextTypes.DEFAULT_TYPE, user_id: int):
    """Показывает инвентарь для туннелей"""
    query = update.callback_query
    
    from handlers.items import ALL_ITEMS
    
    inventory = get_inventory(user_id)
    
    text = f"""🎒 *ИНВЕНТАРЬ*

_Предметы, которые помогут в вылазке:_

"""
    
    has_items = False
    for item_id, qty in inventory.items():
        item = ALL_ITEMS.get(item_id, {})
        if item.get("type") == "consumable":
            text += f"  {item['icon']} {item['name']} x{qty}\n     {item['desc']}\n\n"
            has_items = True
    
    if not has_items:
        text += "_У тебя нет расходников._\n"
    
    keyboard = [[InlineKeyboardButton("🔙 Назад", callback_data="tunnel_menu")]]
    
    await query.message.delete()
    await context.bot.send_message(
        chat_id=user_id,
        text=text,
        parse_mode=constants.ParseMode.MARKDOWN,
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def upgrade_stat_callback(update: Update, context: ContextTypes.DEFAULT_TYPE, stat: str):
    """Обработчик прокачки характеристики"""
    query = update.callback_query
    user_id = query.from_user.id
    
    success, message, new_stats = upgrade_stat(user_id, stat)
    
    if success:
        await query.answer(f"✅ {message}")
        await show_stats_menu(update, context, user_id)
    else:
        await query.answer(f"❌ {message}", show_alert=True)

# ========== ЗАПУСК ЗАБЕГА ==========

async def start_new_run(update: Update, context: ContextTypes.DEFAULT_TYPE, user_id: int):
    """Начинает новый забег"""
    query = update.callback_query
    
    stats = get_character_stats(user_id)
    
    if stats['current_health'] <= 3:
        await query.answer("❌ Слишком мало здоровья! Отдохни.", show_alert=True)
        return
    
    start_tunnel_run(user_id)
    increment_tunnel_runs(user_id)
    
    # 🆕 Получаем слоты инвентаря
    from handlers.inventory import get_inventory_slots
    items_count, max_slots = get_inventory_slots(user_id)
    
    text = f"""🕳️ *Вылазка началась!*

_Ты делаешь глубокий вдох и шагаешь в темноту..._

❤️ Здоровье: {stats['current_health']}/{stats['max_health']}
🧀 Крошек в мешке: 0
🎒 Рюкзак: {items_count}/{max_slots} мест

_Удачи, искатель приключений!_
"""
    
    keyboard = [[InlineKeyboardButton("▶️ Войти в первую комнату", callback_data="tunnel_enter_room")]]
    
    await query.message.delete()
    
    try:
        await context.bot.send_photo(
            chat_id=user_id,
            photo=open("/root/bot/images/tunnel_start_run.jpg", "rb"),
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


async def continue_run(update: Update, context: ContextTypes.DEFAULT_TYPE, user_id: int):
    """Продолжает активный забег"""
    await enter_room(update, context, user_id)

# ========== ОБРАБОТЧИКИ КОЛБЭКОВ ==========

async def tunnel_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Главный обработчик колбэков туннелей"""
    query = update.callback_query
    data = query.data
    user_id = query.from_user.id
    
    await query.answer()
    
    # Меню
    if data == "tunnel_menu":
        await show_tunnel_menu(update, context, user_id)
    
    elif data == "tunnel_stats_menu":
        await show_stats_menu(update, context, user_id)
    
    elif data == "tunnel_rest_info":
        await show_rest_info(update, context, user_id)
    
    elif data == "tunnel_inventory":
        await show_inventory(update, context, user_id)
    
    # Характеристики
    elif data == "tunnel_stat_strength":
        await handle_stat_upgrade(update, context, user_id, "strength")
    
    elif data == "tunnel_stat_agility":
        await handle_stat_upgrade(update, context, user_id, "agility")
    
    elif data == "tunnel_stat_intelligence":
        await handle_stat_upgrade(update, context, user_id, "intelligence")
    
    # Защита
    elif data == "tunnel_defend_head":
        await handle_tunnel_defend(update, context, "head")
    elif data == "tunnel_defend_paws":
        await handle_tunnel_defend(update, context, "paws")
    elif data == "tunnel_defend_body":
        await handle_tunnel_defend(update, context, "body")
    elif data == "tunnel_defend_tail":
        await handle_tunnel_defend(update, context, "tail")
    
    # Забег
    elif data == "tunnel_start":
        await start_new_run(update, context, user_id)
    
    elif data == "tunnel_continue":
        await continue_run(update, context, user_id)
        
    elif data == "tunnel_enter_room":
        await query.message.delete()
        await enter_room(update, context, user_id)
    elif data == "tunnel_next_room":
        await process_room_transition(update, context, user_id)
    
    elif data == "tunnel_skip_room":
        await process_skip_room(update, context, user_id)
    
    elif data == "tunnel_go_home":
        await go_home(update, context, user_id)
    
    elif data == "tunnel_continue_battle":
        await handle_tunnel_continue_battle(update, context)
    
    # Особые комнаты
    elif data == "chest_left":
        await handle_chest_choice(update, context, user_id, "left")
    
    elif data == "chest_middle":
        await handle_chest_choice(update, context, user_id, "middle")
    
    elif data == "chest_right":
        await handle_chest_choice(update, context, user_id, "right")
    
    elif data == "altar_offer":
        await handle_altar_offer(update, context, user_id)
    
# Бой
    elif data.startswith("tunnel_fight_"):
        monster_id = data.replace("tunnel_fight_", "")
        await start_battle(update, context, user_id, monster_id)
    
    elif data == "tunnel_attack_head":
        await handle_tunnel_attack(update, context, "head")
    
    elif data == "tunnel_attack_paws":
        await handle_tunnel_attack(update, context, "paws")
    
    elif data == "tunnel_attack_body":
        await handle_tunnel_attack(update, context, "body")
    
    elif data == "tunnel_attack_tail":
        await handle_tunnel_attack(update, context, "tail")
    
    elif data == "tunnel_attack_random":
        part = random.choice(["head", "paws", "body", "tail"])
        await handle_tunnel_attack(update, context, part)
    
    elif data == "tunnel_flee_new":
        await handle_tunnel_flee_new(update, context)
        return
    
    elif data == "tunnel_break_free":
        await handle_tunnel_break_free(update, context)
    
    elif data == "tunnel_use_potion":
        await handle_use_potion(update, context, user_id)

# ========== РЕГИСТРАЦИЯ ОБРАБОТЧИКОВ ==========

def register_tunnel_handlers(app):
    """Регистрирует все обработчики туннелей"""
    
    app.add_handler(CommandHandler("tunnel", tunnel_command))
    app.add_handler(CallbackQueryHandler(tunnel_callback, pattern="^tunnel_.*"))
    app.add_handler(CallbackQueryHandler(tunnel_callback, pattern="^chest_.*"))
    app.add_handler(CallbackQueryHandler(tunnel_callback, pattern="^altar_.*"))


# Инициализация
init_tunnel_monsters_db()