from telegram import Update, constants, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
import sys
import logging
from datetime import datetime
from telegram_bot_pagination import InlineKeyboardPaginator

sys.path.append('/root/bot')
from database import get_rating
from handlers.inventory import (
    get_inventory, get_equipment, get_achievements, get_user_xp, 
    get_level_progress, equip_item, unequip_item, use_consumable, get_crumbs,
    get_available_chests, format_temp_effects, get_active_temp_effects
)
from handlers.items import ALL_ITEMS, EQUIPMENT, CONSUMABLES, EQUIPMENT_SLOTS, CHESTS
from handlers.achievements_data import ACHIEVEMENTS
from handlers.titles import get_active_title, check_and_unlock_titles
from handlers.game_rat import active_games
from handlers.character import get_character_stats, sync_level_and_points
from handlers.healing import restore_health_over_time
from handlers.tunnel_monsters import get_tunnel_run
from handlers.tunnel_effects import get_active_blessings
from handlers.effects import get_player_effects
from keyboards.inline.profile import (
    get_profile_keyboard,
    get_inventory_keyboard,
    get_equipment_keyboard,
    get_equipment_slots_keyboard,
    get_achievements_keyboard,
    get_item_card_keyboard
)

logger = logging.getLogger(__name__)

RARITY_EMOJI = {
    "common": "⚪",
    "rare": "🔵",
    "epic": "🟣",
    "legendary": "🟡",
    "mythic": "🔴"
}

def escape_markdown(text: str) -> str:
    import re
    if not text:
        return ""
    escape_chars = r'_*[]()~`>#+-=|{}.!'
    return re.sub(f'([{re.escape(escape_chars)}])', r'\\\1', text)

def format_profile_text(user_name: str, rating: dict, equipment: dict, achievements: list, 
                        inventory: dict, xp: int, level: int, xp_in_level: int, xp_needed: int,
                        user_id: int) -> str:
    logger.info(f"📝 format_profile_text: user={user_id}")
    
    try:
        nickname = rating.get("nickname", user_name)
        active_title = get_active_title(user_id)
        title_text = active_title["name"] if active_title else "🌱 Новичок"
        crumbs = get_crumbs(user_id)
        items_count = sum(inventory.values())
        rat_wins = rating.get('wins_as_rat', 0)
        rat_games = rating.get('games_as_rat', 0)
        mouse_wins = rating.get('wins_as_mouse', 0)
        mouse_games = rating.get('games_as_mouse', 0)
        base_stats = get_character_stats(user_id)
        effects = get_player_effects(user_id, None)
        bonus_strength = effects.get("strength", 0)
        bonus_agility = effects.get("agility", 0)
        bonus_intelligence = effects.get("intelligence", 0)
        bonus_health = effects.get("max_health", 0)
        effects_list = []
        temp_effects = get_active_temp_effects(user_id)
        for eff in temp_effects[:5]:
            icon = eff.get('icon', '✨')
            desc = eff.get('desc', eff.get('effect_name', 'Эффект'))
            expires_str = eff.get('expires_at', '')
            if expires_str:
                try:
                    if '.' in expires_str:
                        expires_str = expires_str.split('.')[0]
                    expiry = datetime.strptime(expires_str, '%Y-%m-%d %H:%M:%S')
                    time_left = expiry - datetime.now()
                    minutes_left = int(time_left.total_seconds() / 60)
                    if minutes_left > 60:
                        hours = minutes_left // 60
                        mins = minutes_left % 60
                        time_str = f"{hours} ч {mins} мин"
                    elif minutes_left > 0:
                        time_str = f"{minutes_left} мин"
                    else:
                        time_str = "истекает"
                    effects_list.append(f"  {icon} {desc} ({time_str})")
                except Exception as e:
                    logger.warning(f"Ошибка форматирования эффекта: {e}")
                    effects_list.append(f"  {icon} {desc}")
            else:
                effects_list.append(f"  {icon} {desc}")
        run_data = get_tunnel_run(user_id)
        if run_data and run_data.get("blessed"):
            effects_list.append(f"  ✨ Благословение алтаря (до конца забега)")
        if run_data and run_data.get("blessings"):
            blessings = get_active_blessings(run_data)
            for b in blessings:
                effects_list.append(f"  {b['icon']} {b['name']} (до конца забега)")
        effects_list = list(dict.fromkeys(effects_list))
        effects_text = ""
        if effects_list:
            effects_text = "\n\n*Эффекты:*\n" + "\n".join(effects_list)
        def format_slot(slot_key, icon):
            if slot_key in equipment and equipment[slot_key] in EQUIPMENT:
                item = EQUIPMENT[equipment[slot_key]]
                name = item['name']
                return f"{icon} *{name}*"
            else:
                return f"{icon} _пусто_"
        head_line = format_slot('head', '🎩')
        weapon_line = format_slot('weapon', '⚔️')
        armor_line = format_slot('armor', '🛡️')
        access_line = format_slot('accessory', '💍')
        strength_text = f"💪 Сила: {base_stats['strength']}"
        if bonus_strength > 0:
            strength_text += f" (+{bonus_strength})"
        agility_text = f"🍀 Ловкость: {base_stats['agility']}"
        if bonus_agility > 0:
            agility_text += f" (+{bonus_agility})"
        intelligence_text = f"🧠 Интеллект: {base_stats['intelligence']}"
        if bonus_intelligence > 0:
            intelligence_text += f" (+{bonus_intelligence})"
        health_text = f"❤️ Здоровье: {base_stats['current_health']}/{base_stats['max_health']}"
        if bonus_health > 0:
            health_text += f" (+{bonus_health})"
        text = f"""*Профиль:*

⚔️ {escape_markdown(nickname)} | {title_text}
⭐ Уровень {level} | 🧀 Крошек: {crumbs}
✨ Опыт: {xp_in_level}/{xp_needed} XP
🎒 Предметов: {items_count}

*Статистика:*
🎮 Игр: {rating['games']} | 🏆 Побед: {rating['wins']}
🐀 Крыса: {rat_wins}/{rat_games} | 🐭 Мышь: {mouse_wins}/{mouse_games}
🕳️ Походов: {base_stats.get('total_tunnel_runs', 0)}

*Характеристики:*
{strength_text}
{agility_text}
{intelligence_text}
{health_text}
🎯 Свободных очков: {base_stats['stat_points']}{effects_text}

*Экипировка:*
{head_line}
{weapon_line}
{armor_line}
{access_line}"""
        return text
    except Exception as e:
        logger.error(f"❌ Ошибка в format_profile_text: {e}", exc_info=True)
        return "❌ Ошибка при формировании профиля"

def get_avatar_path(level: int) -> str:
    logger.info(f"🖼️ get_avatar_path: level={level}")
    if level < 5: return "/root/bot/images/avatars/level_1_4.jpg"
    elif level < 10: return "/root/bot/images/avatars/level_5_9.jpg"
    elif level < 15: return "/root/bot/images/avatars/level_10_14.jpg"
    elif level < 20: return "/root/bot/images/avatars/level_15_19.jpg"
    elif level < 25: return "/root/bot/images/avatars/level_20_24.jpg"
    elif level < 30: return "/root/bot/images/avatars/level_25_29.jpg"
    elif level < 40: return "/root/bot/images/avatars/level_30_39.jpg"
    elif level < 50: return "/root/bot/images/avatars/level_40_49.jpg"
    elif level < 75: return "/root/bot/images/avatars/level_50_74.jpg"
    elif level < 100: return "/root/bot/images/avatars/level_75_99.jpg"
    else: return "/root/bot/images/avatars/level_100.jpg"

async def profile_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.info(f"📊 profile_command вызван")
    if update.effective_chat.type != "private":
        if update.callback_query:
            await update.callback_query.answer("❌ Профиль можно смотреть только в личных сообщениях бота!", show_alert=True)
        else:
            await update.message.reply_text("❌ Профиль можно смотреть только в личных сообщениях бота!\n\n👉 Напиши мне в личку: @testpasha_bot")
        return
    user_id = update.effective_user.id
    user_name = update.effective_user.full_name
    logger.info(f"📊 Профиль запрошен: user_id={user_id}")
    try:
        rating = get_rating(user_id)
        inventory = get_inventory(user_id)
        equipment = get_equipment(user_id)
        achievements = get_achievements(user_id)
        xp = get_user_xp(user_id)
        level, xp_in_level, xp_needed = get_level_progress(xp)
        if not rating:
            text = "📊 Ты ещё не играл в Ратляндию!"
            if update.callback_query:
                await update.callback_query.edit_message_text(text)
            else:
                await update.message.reply_text(text)
            return
        restore_health_over_time(user_id, context)
        sync_level_and_points(user_id, level)
        check_and_unlock_titles(user_id)
        text = format_profile_text(user_name, rating, equipment, achievements, inventory, xp, level, xp_in_level, xp_needed, user_id)
        keyboard = get_profile_keyboard(user_name, level, rating['wins'])
        avatar_path = get_avatar_path(level)
        try:
            with open(avatar_path, "rb") as photo:
                if update.callback_query:
                    await update.callback_query.message.delete()
                    await context.bot.send_photo(chat_id=user_id, photo=photo, caption=text, parse_mode=constants.ParseMode.MARKDOWN, reply_markup=keyboard)
                else:
                    await update.message.reply_photo(photo=photo, caption=text, parse_mode=constants.ParseMode.MARKDOWN, reply_markup=keyboard)
        except Exception as e:
            logger.warning(f"Не удалось загрузить аватар {avatar_path}: {e}")
            try:
                with open("/root/bot/images/profile.jpg", "rb") as photo:
                    if update.callback_query:
                        await update.callback_query.message.delete()
                        await context.bot.send_photo(chat_id=user_id, photo=photo, caption=text, parse_mode=constants.ParseMode.MARKDOWN, reply_markup=keyboard)
                    else:
                        await update.message.reply_photo(photo=photo, caption=text, parse_mode=constants.ParseMode.MARKDOWN, reply_markup=keyboard)
            except Exception as e2:
                logger.warning(f"Не удалось загрузить profile.jpg: {e2}")
                if update.callback_query:
                    await update.callback_query.edit_message_text(text, parse_mode=constants.ParseMode.MARKDOWN, reply_markup=keyboard)
                else:
                    await update.message.reply_text(text, parse_mode=constants.ParseMode.MARKDOWN, reply_markup=keyboard)
    except Exception as e:
        logger.error(f"❌ Ошибка в profile_command: {e}", exc_info=True)
        await update.message.reply_text("❌ Произошла ошибка при загрузке профиля")

async def inventory_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.info(f"🎒 inventory_command вызван")
    if update.effective_chat.type != "private":
        if update.callback_query:
            await update.callback_query.answer("❌ Инвентарь можно смотреть только в личных сообщениях бота!", show_alert=True)
        return
    user_id = update.effective_user.id
    await show_inventory_main(update, context, user_id)

async def show_inventory_main(update: Update, context: ContextTypes.DEFAULT_TYPE, user_id: int):
    query = update.callback_query
    logger.info(f"📦 show_inventory_main: user_id={user_id}")
    try:
        inventory = get_inventory(user_id)
        crumbs = get_crumbs(user_id)
        all_count = sum(inventory.values())
        weapon_count = sum(qty for iid, qty in inventory.items() if ALL_ITEMS.get(iid, {}).get("slot") == "weapon")
        armor_count = sum(qty for iid, qty in inventory.items() if ALL_ITEMS.get(iid, {}).get("type") == "equipment" and ALL_ITEMS.get(iid, {}).get("slot") in ["armor", "head"])
        consumable_count = sum(qty for iid, qty in inventory.items() if ALL_ITEMS.get(iid, {}).get("type") == "consumable")
        accessory_count = sum(qty for iid, qty in inventory.items() if ALL_ITEMS.get(iid, {}).get("slot") == "accessory")
        total_chests = 0
        try:
            chests_list = get_available_chests(user_id)
            if chests_list:
                total_chests = sum(c['quantity'] for c in chests_list)
        except: pass
        short_caption = f"🎒 *Рюкзак искателя*\n\n_Потрёпанный, пропахший сыром и порохом._\n\n🧀 Крошек: *{crumbs}*\n\n*Инвентарь:*\n📦 Всего: *{all_count}*\n⚔️ Оружие: *{weapon_count}*\n🛡️ Одежда: *{armor_count}*\n🧪 Расходники: *{consumable_count}*\n💍 Аксессуары: *{accessory_count}*"
        keyboard = get_inventory_keyboard(all_count, weapon_count, armor_count, consumable_count, accessory_count, total_chests)
        if query:
            try: await query.message.delete()
            except: pass
            try:
                with open("/root/bot/images/inventory.jpg", "rb") as photo:
                    await context.bot.send_photo(chat_id=user_id, photo=photo, caption=short_caption, parse_mode=constants.ParseMode.MARKDOWN, reply_markup=keyboard)
                    logger.info(f"✅ Фото инвентаря отправлено")
            except:
                await context.bot.send_message(chat_id=user_id, text=short_caption, parse_mode=constants.ParseMode.MARKDOWN, reply_markup=keyboard)
        else:
            try:
                with open("/root/bot/images/inventory.jpg", "rb") as photo:
                    await update.message.reply_photo(photo=photo, caption=short_caption, parse_mode=constants.ParseMode.MARKDOWN, reply_markup=keyboard)
            except:
                await update.message.reply_text(short_caption, parse_mode=constants.ParseMode.MARKDOWN, reply_markup=keyboard)
    except Exception as e:
        logger.error(f"❌ Ошибка в show_inventory_main: {e}", exc_info=True)

async def handle_inventory_filter(update: Update, context: ContextTypes.DEFAULT_TYPE, filter_type: str):
    query = update.callback_query
    user_id = query.from_user.id
    await show_filtered_inventory(update, context, user_id, filter_type, page=1)

async def show_filtered_inventory(update: Update, context: ContextTypes.DEFAULT_TYPE, user_id: int, filter_type: str, page: int = 1):
    query = update.callback_query
    try:
        inventory = get_inventory(user_id)
        equipment = get_equipment(user_id)
        rarity_tags = {"common": "\\[ОБЫЧ]", "rare": "\\[РЕДК]", "epic": "\\[ЭПИК]", "legendary": "\\[ЛЕГ]", "mythic": "\\[МИФ]"}
        rarity_order = {"mythic": 5, "legendary": 4, "epic": 3, "rare": 2, "common": 1}
        filtered_items = []
        for item_id, qty in inventory.items():
            item = ALL_ITEMS.get(item_id, {})
            if qty <= 0 or not item: continue
            if filter_type == "all": fits_filter = True
            elif filter_type == "weapon" and item.get("slot") == "weapon": fits_filter = True
            elif filter_type == "armor" and item.get("type") == "equipment" and item.get("slot") in ["armor", "head"]: fits_filter = True
            elif filter_type == "consumable" and item.get("type") == "consumable": fits_filter = True
            elif filter_type == "accessory" and item.get("slot") == "accessory": fits_filter = True
            else: fits_filter = False
            if fits_filter:
                for _ in range(qty):
                    filtered_items.append((item_id, item, 1))
        filtered_items.sort(key=lambda x: rarity_order.get(x[1].get("rarity", "common"), 0), reverse=True)
        ITEMS_PER_PAGE = 10
        total_items = len(filtered_items)
        total_pages = max(1, (total_items + ITEMS_PER_PAGE - 1) // ITEMS_PER_PAGE)
        page = max(1, min(page, total_pages))
        start_idx = (page - 1) * ITEMS_PER_PAGE
        end_idx = min(start_idx + ITEMS_PER_PAGE, total_items)
        page_items = filtered_items[start_idx:end_idx]
        if not filtered_items:
            text = "🎒 _Тут пусто._"
        else:
            text = ""
            for idx, (item_id, item, qty) in enumerate(page_items, start_idx + 1):
                equipped = " (надето)" if item_id in equipment.values() else ""
                rarity = item.get("rarity", "common")
                tag = rarity_tags.get(rarity, "[ОБЫЧ]")
                desc = item.get("desc", "")
                if "—" in desc: desc = desc.split("—")[-1].strip()
                icon = item.get('icon', '📦')
                name = item.get('name', 'Предмет')
                text += f"{idx}. {icon} {tag} *{name}*{equipped}\n    _{desc}_\n\n"
        if total_pages > 1:
            paginator = InlineKeyboardPaginator(total_pages, current_page=page, data_pattern=f'inventory_page_{filter_type}#{{page}}')
            paginator.add_after(InlineKeyboardButton("Назад", callback_data="profile_inventory"))
            reply_markup = paginator.markup
        else:
            reply_markup = InlineKeyboardMarkup([[InlineKeyboardButton("Назад", callback_data="profile_inventory")]])
        if query:
            try: await query.message.delete()
            except: pass
            await context.bot.send_message(chat_id=user_id, text=text, parse_mode=constants.ParseMode.MARKDOWN, reply_markup=reply_markup)
        else:
            await update.message.reply_text(text, parse_mode=constants.ParseMode.MARKDOWN, reply_markup=reply_markup)
    except Exception as e:
        logger.error(f"❌ Ошибка в show_filtered_inventory: {e}", exc_info=True)

async def equipment_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.type != "private":
        if update.callback_query:
            await update.callback_query.answer("❌ Экипировку можно менять только в личных сообщениях бота!", show_alert=True)
        return
    user_id = update.effective_user.id
    query = update.callback_query
    try:
        equipment = get_equipment(user_id)
        inventory = get_inventory(user_id)
        available_count = 0
        for item_id, qty in inventory.items():
            if item_id in EQUIPMENT and qty > 0 and item_id not in equipment.values():
                available_count += qty
        text = f"🛡️ <b>ЭКИПИРОВКА</b>\n\n"
        slots = [('head', '🎩', 'Шлем'), ('weapon', '⚔️', 'Оружие'), ('armor', '🛡️', 'Броня'), ('accessory', '💍', 'Аксессуар')]
        for slot, emoji, name in slots:
            if slot in equipment and equipment[slot] in EQUIPMENT:
                item = EQUIPMENT[equipment[slot]]
                item_id = equipment[slot]
                qty = inventory.get(item_id, 1)
                qty_text = f" (x{qty})" if qty > 1 else ""
                text += f"🧳 <b>{name}</b>: {emoji} <b>{item['name']}</b>{qty_text} /i_{item_id}\n"
            else:
                text += f"🧳 <b>{name}</b>: <i>пусто</i>\n"
        text += f"\n📦 <b>Доступно предметов</b>: {available_count}\n"
        keyboard = get_equipment_keyboard()
        if query:
            try: await query.message.delete()
            except: pass
            try:
                with open("/root/bot/images/equipment.jpg", "rb") as photo:
                    await context.bot.send_photo(chat_id=user_id, photo=photo, caption=text, parse_mode=constants.ParseMode.HTML, reply_markup=keyboard)
            except:
                await context.bot.send_message(chat_id=user_id, text=text, parse_mode=constants.ParseMode.HTML, reply_markup=keyboard)
        else:
            try:
                with open("/root/bot/images/equipment.jpg", "rb") as photo:
                    await update.message.reply_photo(photo=photo, caption=text, parse_mode=constants.ParseMode.HTML, reply_markup=keyboard)
            except:
                await update.message.reply_text(text, parse_mode=constants.ParseMode.HTML, reply_markup=keyboard)
    except Exception as e:
        logger.error(f"❌ Ошибка в equipment_command: {e}", exc_info=True)

async def show_available_for_slot(update: Update, context: ContextTypes.DEFAULT_TYPE, slot: str, page: int = 1):
    query = update.callback_query
    user_id = query.from_user.id
    try:
        inventory = get_inventory(user_id)
        equipment = get_equipment(user_id)
        available_items = []
        for item_id, qty in inventory.items():
            if item_id in EQUIPMENT and qty > 0:
                item = EQUIPMENT[item_id]
                if item.get("slot") == slot and item_id not in equipment.values():
                    for _ in range(qty):
                        available_items.append((item_id, item))
        available_items.sort(key=lambda x: {"mythic": 5, "legendary": 4, "epic": 3, "rare": 2, "common": 1}.get(x[1].get("rarity", "common"), 0), reverse=True)
        ITEMS_PER_PAGE = 5
        total_items = len(available_items)
        total_pages = max(1, (total_items + ITEMS_PER_PAGE - 1) // ITEMS_PER_PAGE)
        page = max(1, min(page, total_pages))
        start_idx = (page - 1) * ITEMS_PER_PAGE
        end_idx = min(start_idx + ITEMS_PER_PAGE, total_items)
        page_items = available_items[start_idx:end_idx]
        slot_names = {'head': 'ШЛЕМ', 'weapon': 'ОРУЖИЕ', 'armor': 'БРОНЯ', 'accessory': 'АКСЕССУАР'}
        slot_emoji = {'head': '🎩', 'weapon': '⚔️', 'armor': '🛡️', 'accessory': '💍'}
        text = f"{slot_emoji[slot]} <b>ДОСТУПНО: {slot_names[slot]}</b>\n\n"
        if not available_items:
            text += "<i>Нет доступных предметов</i>"
            reply_markup = InlineKeyboardMarkup([[InlineKeyboardButton("🛡️ Назад к экипировке", callback_data="profile_equipment")]])
        else:
            rarity_tags = {"common": "\\[ОБЫЧ]", "rare": "\\[РЕДК]", "epic": "\\[ЭПИК]", "legendary": "\\[ЛЕГ]", "mythic": "\\[МИФ]"}
            for idx, (item_id, item) in enumerate(page_items, start_idx + 1):
                rarity = item.get("rarity", "common")
                tag = rarity_tags.get(rarity, "\\[ОБЫЧ]")
                desc = item.get("desc", "")
                if "—" in desc: desc = desc.split("—")[-1].strip()
                text += f"{idx}. {tag} <b>{item['name']}</b>\n   <i>{desc}</i>\n\n"
            keyboard = []
            for idx, (item_id, item) in enumerate(page_items, start_idx + 1):
                keyboard.append([InlineKeyboardButton(f"{idx}. Надеть", callback_data=f"equip_from_list_{item_id}")])
            if total_pages > 1:
                paginator = InlineKeyboardPaginator(total_pages, current_page=page, data_pattern=f'available_slot_{slot}#{{page}}')
                for row in keyboard:
                    for btn in row:
                        paginator.add_before(btn)
                paginator.add_after(InlineKeyboardButton("🛡️ Назад", callback_data="profile_equipment"))
                reply_markup = paginator.markup
            else:
                keyboard.append([InlineKeyboardButton("🛡️ Назад", callback_data="profile_equipment")])
                reply_markup = InlineKeyboardMarkup(keyboard)
        await query.message.delete()
        await context.bot.send_message(chat_id=user_id, text=text, parse_mode=constants.ParseMode.HTML, reply_markup=reply_markup)
    except Exception as e:
        logger.error(f"❌ Ошибка в show_available_for_slot: {e}", exc_info=True)

async def show_equipment_list_by_slot(update: Update, context: ContextTypes.DEFAULT_TYPE, slot: str):
    query = update.callback_query
    user_id = query.from_user.id
    inventory = get_inventory(user_id)
    equipment = get_equipment(user_id)
    slot_names = {'head': 'ШЛЕМЫ', 'weapon': 'ОРУЖИЕ', 'armor': 'БРОНЯ', 'accessory': 'АКСЕССУАРЫ'}
    slot_emoji = {'head': '🎩', 'weapon': '⚔️', 'armor': '🛡️', 'accessory': '💍'}
    text = f"{slot_emoji[slot]} <b>{slot_names[slot]} В ИНВЕНТАРЕ</b>\n\n"
    found_items = []
    for item_id, qty in inventory.items():
        if item_id in EQUIPMENT and qty > 0:
            item = EQUIPMENT[item_id]
            if item.get("slot") == slot:
                found_items.append((item_id, item, qty))
    if not found_items:
        text += "<i>Нет предметов этого типа</i>"
    else:
        for item_id, item, qty in found_items:
            qty_text = f" (x{qty})" if qty > 1 else ""
            equipped = " ✅" if item_id in equipment.values() else ""
            text += f"{item['icon']} {item['name']}{qty_text} /i_{item_id}{equipped}\n"
    keyboard = get_equipment_slots_keyboard()
    await query.message.delete()
    await context.bot.send_message(chat_id=user_id, text=text, parse_mode=constants.ParseMode.HTML, reply_markup=keyboard)

async def handle_equip_from_list(update: Update, context: ContextTypes.DEFAULT_TYPE, item_id: str):
    user_id = update.effective_user.id
    try:
        if equip_item(user_id, item_id):
            await update.callback_query.answer(f"✅ {ALL_ITEMS[item_id]['name']} надет!")
        else:
            await update.callback_query.answer("❌ Не удалось надеть предмет!", show_alert=True)
        await equipment_command(update, context)
    except Exception as e:
        logger.error(f"❌ Ошибка в handle_equip_from_list: {e}", exc_info=True)

async def handle_unequip(update: Update, context: ContextTypes.DEFAULT_TYPE, slot: str):
    user_id = update.effective_user.id
    try:
        if unequip_item(user_id, slot):
            await update.callback_query.answer(f"✅ Предмет снят!")
        else:
            await update.callback_query.answer("❌ Не удалось снять предмет!", show_alert=True)
        await equipment_command(update, context)
    except Exception as e:
        logger.error(f"❌ Ошибка в handle_unequip: {e}", exc_info=True)

async def achievements_command(update: Update, context: ContextTypes.DEFAULT_TYPE, show_all: bool = False):
    if update.effective_chat.type != "private":
        if update.callback_query:
            await update.callback_query.answer("❌ Достижения можно смотреть только в личных сообщениях бота!", show_alert=True)
        return
    user_id = update.effective_user.id
    try:
        user_achievements = get_achievements(user_id)
        unlocked = [ach for ach in user_achievements if ach.get('unlocked', False)]
        locked = [ach for ach in user_achievements if not ach.get('unlocked', False) and not ach.get('hidden', False)]
        text = f"""🏆 ЗАЛ ДОСТИЖЕНИЙ

_На древних каменных стенах этого зала высечены имена величайших героев Подземного Царства..._

"""
        if show_all:
            text += f"▸ ВСЕ ДОСТИЖЕНИЯ ({len(unlocked)}/{len(ACHIEVEMENTS)})\n\n"
            for ach in user_achievements:
                if ach.get('hidden', False) and not ach.get('unlocked', False): continue
                status = "✅" if ach.get('unlocked', False) else "🔒"
                text += f"  {status} {ach['name']}\n     {ach['desc']}\n\n"
        else:
            if unlocked:
                text += f"▸ ПОЛУЧЕННЫЕ ({len(unlocked)})\n\n"
                for ach in unlocked[:5]:
                    text += f"  ✅ {ach['name']}\n     {ach['desc']}\n\n"
                if len(unlocked) > 5: text += f"  ... и ещё {len(unlocked) - 5}\n\n"
            else:
                text += "▸ ПОЛУЧЕННЫЕ\n\n  Пока нет полученных достижений\n\n"
            if locked:
                text += f"▸ БЛИЖАЙШИЕ К РАЗБЛОКИРОВКЕ\n\n"
                for ach in locked[:3]:
                    text += f"  🔒 {ach['name']}\n     {ach['desc']}\n\n"
            text += f"Прогресс: {len(unlocked)}/{len(ACHIEVEMENTS)} ({round(len(unlocked)/len(ACHIEVEMENTS)*100)}%)"
        keyboard = get_achievements_keyboard(show_all)
        if update.callback_query:
            query = update.callback_query
            await query.message.delete()
            try:
                with open("/root/bot/images/achievement_hall.jpg", "rb") as photo:
                    await context.bot.send_photo(chat_id=user_id, photo=photo, caption=text, parse_mode=constants.ParseMode.MARKDOWN, reply_markup=keyboard)
            except:
                await context.bot.send_message(chat_id=user_id, text=text, parse_mode=constants.ParseMode.MARKDOWN, reply_markup=keyboard)
        else:
            try:
                with open("/root/bot/images/achievement_hall.jpg", "rb") as photo:
                    await update.message.reply_photo(photo=photo, caption=text, parse_mode=constants.ParseMode.MARKDOWN, reply_markup=keyboard)
            except:
                await update.message.reply_text(text, parse_mode=constants.ParseMode.MARKDOWN, reply_markup=keyboard)
    except Exception as e:
        logger.error(f"❌ Ошибка в achievements_command: {e}", exc_info=True)

async def item_info_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.text: return
    text = update.message.text.strip()
    if not text.startswith('/i_'): return
    item_id = text.replace('/i_', '').split()[0]
    user_id = update.effective_user.id
    item = ALL_ITEMS.get(item_id)
    if not item:
        await update.message.reply_text("❌ Предмет не найден"); return
    inventory = get_inventory(user_id)
    qty = inventory.get(item_id, 0)
    if qty <= 0:
        await update.message.reply_text("❌ У тебя нет этого предмета"); return
    rarity = item.get("rarity", "common")
    rarity_names = {"common": "Обычное", "rare": "Редкое", "epic": "Эпическое", "legendary": "Легендарное", "mythic": "Мифическое"}
    rarity_name = rarity_names.get(rarity, "Обычное")
    icon = item.get('icon', '📦')
    name = item.get('name', 'Предмет')
    text = f"{icon} *{name}*\n\n"
    lore = item.get('lore', '')
    if lore: text += f"_{lore}_\n\n"
    text += "*Характеристики:*\n"
    if item.get("slot"):
        slot_names = {'head': 'Шлем', 'weapon': 'Оружие', 'armor': 'Броня', 'accessory': 'Аксессуар'}
        text += f"🗡️ Тип: {slot_names.get(item['slot'], item['slot'])}\n"
    elif item.get("type") == "consumable": text += f"🧪 Тип: Расходник\n"
    elif item.get("type") == "chest": text += f"📦 Тип: Сундук\n"
    text += f"💎 Редкость: {rarity_name}\n"
    effects = item.get("effect", {})
    for key, value in effects.items():
        if key == "strength": text += f"💪 Сила: +{value}\n"
        elif key == "agility": text += f"🍀 Ловкость: +{value}\n"
        elif key == "intelligence": text += f"🧠 Интеллект: +{value}\n"
        elif key == "max_health": text += f"❤️ Здоровье: +{value}\n"
        elif key == "luck": text += f"🍀 Удача: +{value}\n"
        elif key == "bonus_xp": text += f"✨ Бонус XP: +{value}\n"
        elif key == "xp_boost": text += f"✨ XP: +{value}%\n"
        elif key == "find_chance": text += f"🔍 Находки: +{value}%\n"
        elif key == "kill_xp": text += f"💀 XP за убийство: +{value}\n"
    if item.get("desc"):
        desc = item['desc']
        if "—" in desc: desc = desc.split("—")[-1].strip()
        if desc and not any(str(v) in desc for v in effects.values()): text += f"\n_{desc}_\n"
    text += f"\n📦 В наличии: {qty} шт."
    equipment = get_equipment(user_id)
    is_equipped = item_id in equipment.values()
    slot = item.get("slot")
    keyboard = get_item_card_keyboard(item_id, item.get("type", "misc"), slot, is_equipped)
    await update.message.reply_text(text, parse_mode=constants.ParseMode.MARKDOWN, reply_markup=keyboard)

async def handle_equip(update: Update, context: ContextTypes.DEFAULT_TYPE, item_id: str):
    user_id = update.effective_user.id
    try:
        if equip_item(user_id, item_id):
            await update.callback_query.answer(f"✅ {ALL_ITEMS[item_id]['name']} надет!")
        else:
            await update.callback_query.answer("❌ Не удалось надеть предмет!", show_alert=True)
        await equipment_command(update, context)
    except Exception as e:
        logger.error(f"❌ Ошибка в handle_equip: {e}", exc_info=True)

async def handle_use_consumable(update: Update, context: ContextTypes.DEFAULT_TYPE, item_id: str):
    user_id = update.effective_user.id
    try:
        game = None
        for g in active_games.values():
            if user_id in g.players and g.players[user_id]["alive"]:
                game = g
                break
        if not game:
            await update.callback_query.answer("❌ Ты не в игре или мёртв!", show_alert=True)
            return
        if use_consumable(user_id, item_id):
            item = CONSUMABLES.get(item_id, ALL_ITEMS.get(item_id, {"name": "Предмет"}))
            await update.callback_query.answer(f"✅ {item['name']} использован!")
        else:
            await update.callback_query.answer("❌ Не удалось использовать предмет!", show_alert=True)
    except Exception as e:
        logger.error(f"❌ Ошибка в handle_use_consumable: {e}", exc_info=True)