"""Кузница — вход из города, крафт предметов"""

from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes
from telegram import constants
import sys
sys.path.append('/root/bot')

from handlers.items import ALL_ITEMS, RECIPES, get_available_recipes
from handlers.inventory import add_item, get_crumbs, spend_crumbs, add_action_history
from handlers.crafting import (
    get_player_resources, spend_materials, has_materials,
    check_craft_success, check_craft_critical,
    get_quality_from_roll, save_crafted_item, get_craft_difficulty_info,
    CraftQuality
)
from keyboards.inline.blacksmith import (
    get_forge_main_keyboard, get_forge_recipe_keyboard,
    get_forge_craft_result_keyboard, get_forge_resources_keyboard,
    get_forge_recipes_keyboard
)
from core.dice.engine import get_dice_engine, DICE_STICKERS
import random
import asyncio

# Единый движок кубиков
dice_engine = get_dice_engine()

# Эмодзи редкости
RARITY_EMOJI = {
    "common": "⚪", "rare": "🔵", "epic": "🟣", "legendary": "🟡", "mythic": "🔴"
}


# ========== ГАДАЛКА ==========
async def forge_fortune(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Гадание на удачу — имитация броска"""
    query = update.callback_query
    user_id = query.from_user.id
    
    crumbs = get_crumbs(user_id)
    if crumbs < 5:
        await query.answer("❌ Нужно 5 🍞 для гадания!", show_alert=True)
        return
    
    spend_crumbs(user_id, 5)
    fake_roll = random.randint(4, 10)
    stars = "⭐" * (fake_roll // 2)
    
    await query.answer(f"🔮 Звёзды шепчут: качество будет ~{fake_roll}/12 {stars}", show_alert=True)


# ========== ГЛАВНОЕ МЕНЮ ==========
async def blacksmith_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Главное меню кузницы — без списка рецептов"""
    query = update.callback_query
    user_id = query.from_user.id
    
    text = f"""🔨 *КУЗНИЦА*

_Тяжёлые молоты, жар горна и запах раскалённого металла._

🎲 Два кубика решают качество
📦 Материалы из рюкзака
📜 Нужны рецепты (выпадают с мобов!)

Выбери что сковать:"""
    
    available = get_available_recipes(user_id)
    keyboard = get_forge_main_keyboard(available, len(available) > 0)
    
    await query.message.delete()
    
    try:
        with open("/root/bot/images/forge.jpg", "rb") as photo:
            await context.bot.send_photo(
                chat_id=user_id, photo=photo, caption=text,
                parse_mode=constants.ParseMode.MARKDOWN, reply_markup=keyboard
            )
    except:
        await context.bot.send_message(
            chat_id=user_id, text=text,
            parse_mode=constants.ParseMode.MARKDOWN, reply_markup=keyboard
        )


# ========== ВЫБОР РЕЦЕПТА ==========
async def forge_select_recipe(update: Update, context: ContextTypes.DEFAULT_TYPE, recipe_id: str = None):
    """Показывает информацию о рецепте"""
    query = update.callback_query
    user_id = query.from_user.id
    
    if not recipe_id:
        callback_data = query.data
        if callback_data.startswith("forge_select_"):
            recipe_id = callback_data.replace("forge_select_", "")
    
    recipe = RECIPES.get(recipe_id, {})
    if not recipe:
        await query.answer("❌ Рецепт не найден!", show_alert=True)
        return
    
    result_item = ALL_ITEMS.get(recipe.get("result_item", ""), {})
    resources = get_player_resources(user_id)
    diff = get_craft_difficulty_info(recipe.get("rarity", "common"))
    
    text = f"📜 *{recipe.get('name', recipe_id)}*\n\n"
    text += f"_{recipe.get('desc', '')}_\n\n"
    text += f"⭐ Редкость: *{recipe.get('rarity', 'common').upper()}*\n\n"
    text += f"🎯 *Сложность:*\n"
    text += f"  Нужно выбросить: *{diff['min_roll']}+*\n"
    text += f"  ⚠️ Провал при: *{diff['fail_desc']}*\n"
    text += f"  🌟 Крит при: *{diff['crit_roll']}*\n\n"
    
    if recipe.get("cursed"):
        text += f"💀 *ПРОКЛЯТЫЙ РЕЦЕПТ!*\n"
        text += f"_Шанс успеха: {int(recipe.get('success_chance', 0.3) * 100)}%_\n"
        if recipe.get("fail_result"):
            fail_item = ALL_ITEMS.get(recipe["fail_result"], {})
            text += f"_При провале: {fail_item.get('icon','💔')} {fail_item.get('name','Сломанный предмет')}_\n"
        text += "\n"
    
    text += f"📦 *Требуется:*\n"
    
    all_have = True
    for mat_id, qty in recipe["materials"].items():
        mat = ALL_ITEMS.get(mat_id, {"name": mat_id, "icon": "📦"})
        have = resources.get(mat_id, 0)
        check = "✅" if have >= qty else "❌"
        text += f"  {check} {mat.get('icon', '📦')} {mat.get('name', mat_id)}: {have}/{qty}\n"
        if have < qty:
            all_have = False
    
    if recipe.get("blueprint_required"):
        have_bp = resources.get(recipe["blueprint_required"], 0)
        check = "✅" if have_bp > 0 else "❌"
        text += f"  {check} 📜 Чертёж\n"
        if have_bp <= 0:
            all_have = False
    
    text += f"\n🎲 *Результат:* {result_item.get('icon', '📦')} {result_item.get('name', '???')}"
    
    keyboard = get_forge_recipe_keyboard(recipe_id, all_have)
    
    await query.message.delete()
    await context.bot.send_message(
        chat_id=user_id, text=text,
        parse_mode=constants.ParseMode.MARKDOWN, reply_markup=keyboard
    )


# ========== ПРОЦЕСС КОВКИ (DICE ENGINE v5.0) ==========
async def forge_craft(update: Update, context: ContextTypes.DEFAULT_TYPE, recipe_id: str = None):
    """Крафт предмета с анимацией — ИСПОЛЬЗУЕТ DICE ENGINE"""
    query = update.callback_query
    user_id = query.from_user.id
    
    if not recipe_id:
        callback_data = query.data
        if callback_data.startswith("forge_craft_"):
            recipe_id = callback_data.replace("forge_craft_", "")
    
    recipe = RECIPES.get(recipe_id, {})
    if not recipe:
        await query.answer("❌ Рецепт не найден!", show_alert=True)
        return
    
    result_item_id = recipe.get("result_item")
    result_item = ALL_ITEMS.get(result_item_id, {})
    rarity = recipe.get("rarity", "common")
    
    if not has_materials(user_id, recipe["materials"]):
        await query.answer("❌ Не хватает материалов!", show_alert=True)
        return
    
    await query.answer("⚒️ Начинаем ковку...")
    await query.message.delete()
    
    # АНИМАЦИЯ КОВКИ С ФОТО (каждое фото 3.0 сек)
    anim_data = [
        ("/root/bot/images/forge_fire.jpg", "🔥 *Разогрев горна...*"),
        ("/root/bot/images/forge_hammer.jpg", "⚒️ *Удар молота!*"),
        ("/root/bot/images/forge_quench.jpg", "✨ *Закалка в масле...*"),
    ]
    
    for image_path, caption in anim_data:
        try:
            with open(image_path, "rb") as photo:
                anim_photo = await context.bot.send_photo(
                    chat_id=user_id, photo=photo, caption=caption,
                    parse_mode=constants.ParseMode.MARKDOWN
                )
        except:
            anim_photo = await context.bot.send_message(
                chat_id=user_id, text=caption,
                parse_mode=constants.ParseMode.MARKDOWN
            )
        await asyncio.sleep(3.0)
        try:
            await anim_photo.delete()
        except:
            pass
    
    # 🎲 АНИМАЦИЯ БРОСКА КУБИКОВ СО СТИКЕРАМИ (каждый этап 3.0 сек)
    anim_msg = await context.bot.send_message(
        chat_id=user_id, 
        text="🎲 *Бросаем кубики...*", 
        parse_mode=constants.ParseMode.MARKDOWN
    )
    await asyncio.sleep(3.0)
    await anim_msg.delete()
    
    # 🎲 БРОСОК КУБИКОВ
    craft_result = dice_engine.roll_craft()
    dice_sum = craft_result.total
    
    sticker_msgs = []
    for roll in craft_result.rolls:
        if roll in DICE_STICKERS:
            try:
                msg = await context.bot.send_sticker(chat_id=user_id, sticker=DICE_STICKERS[roll])
                sticker_msgs.append(msg)
            except:
                msg = await context.bot.send_message(
                    chat_id=user_id, 
                    text=f"🎲 Выпало: *{roll}*", 
                    parse_mode=constants.ParseMode.MARKDOWN
                )
                sticker_msgs.append(msg)
        else:
            msg = await context.bot.send_message(
                chat_id=user_id, 
                text=f"🎲 Выпало: *{roll}*", 
                parse_mode=constants.ParseMode.MARKDOWN
            )
            sticker_msgs.append(msg)
        await asyncio.sleep(3.0)
    
    # Удаляем ВСЕ сообщения кубиков
    for msg in sticker_msgs:
        try:
            await msg.delete()
        except:
            pass
    
    # ФОРМИРОВАНИЕ РЕЗУЛЬТАТА
    text = f"⚒️ *КОВКА ЗАВЕРШЕНА!*\n\n"
    text += f"🎲 Выпало: *{craft_result.rolls[0]}* + *{craft_result.rolls[1]}* = *{craft_result.total}*\n\n"
    
    # Проклятый рецепт
    if recipe.get("cursed"):
        success_chance = recipe.get("success_chance", 0.3)
        if random.random() > success_chance:
            spend_materials(user_id, recipe["materials"])
            text += f"💀 *ПРОКЛЯТАЯ КОВКА — ПРОВАЛ!*\n\n"
            text += f"💔 *Рецепт поглотил материалы!*\n"
            if recipe.get("fail_result"):
                fail_item = ALL_ITEMS.get(recipe["fail_result"], {})
                add_item(user_id, recipe["fail_result"])
                text += f"📦 Вместо предмета: {fail_item.get('icon','💔')} *{fail_item.get('name','???')}*\n"
            
            keyboard = get_forge_craft_result_keyboard()
            image_path = "/root/bot/images/forge_fail.jpg"
            try:
                with open(image_path, "rb") as photo:
                    await context.bot.send_photo(
                        chat_id=user_id, photo=photo, caption=text, 
                        parse_mode=constants.ParseMode.MARKDOWN, reply_markup=keyboard
                    )
            except:
                await context.bot.send_message(
                    chat_id=user_id, text=text, 
                    parse_mode=constants.ParseMode.MARKDOWN, reply_markup=keyboard
                )
            
            update_user_data(user_id, "forge_fails", get_user_data(user_id, "forge_fails", 0) + 1)
            return
    
    # Проверка успеха
    success, fail_reason = check_craft_success(dice_sum, rarity)
    
    if not success:
        spend_materials(user_id, recipe["materials"])
        
        if random.random() < 0.3:
            from handlers.inventory import remove_item
            remove_item(user_id, recipe_id, 1)
            text += f"💔 *КОВКА ПРОВАЛЕНА!*\n\n📜 *Рецепт уничтожен!*\n❌ {fail_reason}"
        elif random.random() < 0.5:
            text += f"❌ *КОВКА ПРОВАЛЕНА!*\n\n📦 *Материалы потеряны!*\n❌ {fail_reason}"
        else:
            add_item(user_id, result_item_id)
            quality, bonuses = get_quality_from_roll(dice_sum)
            text += f"💎 Качество: {quality.color} *{quality.display.upper()}*\n📦 Создано: {result_item.get('icon','📦')} *{result_item.get('name','???')}*\n"
            add_action_history(user_id, f"Скрафчен {result_item.get('name', 'предмет')} ({quality.display})", "🔨")
        
        update_user_data(user_id, "forge_fails", get_user_data(user_id, "forge_fails", 0) + 1)
        
        fails = get_user_data(user_id, "forge_fails", 0)
        if fails >= 5:
            available_recipes = [rid for rid in RECIPES.keys() if not RECIPES[rid].get("cursed") and rid != recipe_id]
            if available_recipes:
                random_recipe = random.choice(available_recipes)
                add_item(user_id, random_recipe)
                text += f"\n\n🎁 *Утешительный приз!*\n📜 Получен рецепт: *{RECIPES[random_recipe]['name']}*"
                update_user_data(user_id, "forge_fails", 0)
        
        keyboard = get_forge_craft_result_keyboard()
        image_path = "/root/bot/images/forge_fail.jpg"
        try:
            with open(image_path, "rb") as photo:
                await context.bot.send_photo(
                    chat_id=user_id, photo=photo, caption=text, 
                    parse_mode=constants.ParseMode.MARKDOWN, reply_markup=keyboard
                )
        except:
            await context.bot.send_message(
                chat_id=user_id, text=text, 
                parse_mode=constants.ParseMode.MARKDOWN, reply_markup=keyboard
            )
        return
    
    # УСПЕХ
    quality, bonuses = get_quality_from_roll(dice_sum)
    is_critical = check_craft_critical(dice_sum, rarity)
    
    if is_critical and quality not in [CraftQuality.DIVINE, CraftQuality.LEGENDARY]:
        quality = CraftQuality.LEGENDARY if quality in [CraftQuality.MASTERFUL, CraftQuality.FLAWLESS] else CraftQuality.DIVINE
    
    spend_materials(user_id, recipe["materials"])
    add_item(user_id, result_item_id)
    add_action_history(user_id, f"Скрафчен {result_item.get('name', 'предмет')} ({quality.display})", "🔨")
    
    import sqlite3
    conn = sqlite3.connect("/root/bot/ratings.db")
    cur = conn.execute('SELECT nickname FROM ratings WHERE user_id = ?', (user_id,))
    row = cur.fetchone()
    conn.close()
    crafter_name = row[0] if row and row[0] else f"ID:{user_id}"
    
    save_crafted_item(user_id, result_item_id, quality.name, dice_sum, bonuses, crafter_name)
    
    crit = is_critical and random.random() < 0.1
    if crit:
        add_item(user_id, result_item_id)
        add_action_history(user_id, f"Двойная ковка: {result_item.get('name', 'предмет')}", "🌟")
        text += "\n🌟 *ДВОЙНАЯ КОВКА!* Создано 2 предмета!\n"
    
    text += f"💎 Качество: {quality.color} *{quality.display.upper()}*\n"
    text += f"👤 Создал: *{crafter_name}*\n"
    text += f"📦 Создано: {result_item.get('icon','📦')} *{result_item.get('name','???')}*\n"
    
    if is_critical:
        text += "\n🌟 *КРИТИЧЕСКИЙ УСПЕХ!* Качество повышено!\n"
    
    if bonuses:
        stat_names = {
            "strength": "💪 Силе", 
            "agility": "🍀 Ловкости", 
            "intelligence": "🧠 Интеллекту", 
            "max_health": "❤️ Здоровью", 
            "all_stats": "⭐ Всем характеристикам"
        }
        text += "\n✨ *Бонусы качества:*\n" + "\n".join([f"  +{v} к {stat_names.get(k, k)}" for k, v in bonuses.items()])
    
    # Атмосферная фраза
    phrases = [
        "_Ты чувствуешь как древняя магия наполняет предмет силой..._",
        "_Искры разлетаются в стороны, озаряя кузницу золотым светом..._",
        "_Мастер довольно кивает — отличная работа!_",
        "_Этот предмет займёт достойное место в твоём арсенале._"
    ]
    text += f"\n\n{random.choice(phrases)}"
    
    update_user_data(user_id, "forge_fails", 0)
    keyboard = get_forge_craft_result_keyboard()
    image_path = "/root/bot/images/forge_success.jpg" if dice_sum >= 8 else "/root/bot/images/forge_fail.jpg"
    
    try:
        with open(image_path, "rb") as photo:
            await context.bot.send_photo(
                chat_id=user_id, photo=photo, caption=text, 
                parse_mode=constants.ParseMode.MARKDOWN, reply_markup=keyboard
            )
    except:
        await context.bot.send_message(
            chat_id=user_id, text=text, 
            parse_mode=constants.ParseMode.MARKDOWN, reply_markup=keyboard
        )


# ========== ЗАТОЧКА ПРЕДМЕТОВ ==========
async def forge_sharpen(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Заточка предметов"""
    query = update.callback_query
    user_id = query.from_user.id
    
    from handlers.inventory import get_inventory, get_equipment
    from handlers.items import ALL_ITEMS, ENCHANT_SCROLLS
    from handlers.enchant import get_enchant_level, get_enchant_bonus
    
    equipment = get_equipment(user_id)
    inventory = get_inventory(user_id)
    
    scrolls = {}
    for scroll_id, scroll in ENCHANT_SCROLLS.items():
        qty = inventory.get(scroll_id, 0)
        if qty > 0:
            scrolls[scroll_id] = qty
    
    if not scrolls:
        await query.answer("❌ Нет свитков заточки!", show_alert=True)
        return
    
    text = "⚡ *ЗАТОЧКА ПРЕДМЕТОВ*\n\n_Выбери предмет который хочешь заточить:_\n\n"
    
    keyboard = []
    for slot_key, slot_icon in [('weapon', '⚔️'), ('armor', '🛡️'), ('head', '🎩'), ('accessory', '💍')]:
        item_id = equipment.get(slot_key, '')
        if item_id:
            base_id = item_id.rsplit("+", 1)[0] if "+" in item_id else item_id
            item = ALL_ITEMS.get(base_id, ALL_ITEMS.get(item_id, {}))
            if item:
                ench_level = get_enchant_level(item_id)
                ench_bonus = get_enchant_bonus(item_id)
                ench_text = f" +{ench_level}" if ench_level > 0 else ""
                bonus_text = ""
                if ench_bonus.get('enchant_damage_min'):
                    bonus_text = f" (+{ench_bonus['enchant_damage_min']} урона)"
                elif ench_bonus.get('enchant_defense'):
                    bonus_text = f" (+{ench_bonus['enchant_defense']} защиты)"
                elif ench_bonus.get('enchant_magic_defense'):
                    bonus_text = f" (+{ench_bonus['enchant_magic_defense']} м. защиты)"
                text += f"{slot_icon} {item.get('icon','📦')} *{item.get('name','Предмет')}*{ench_text}{bonus_text}\n"
                
                for scroll_id, qty in scrolls.items():
                    scroll = ENCHANT_SCROLLS[scroll_id]
                    if "weapon" in scroll_id and slot_key != "weapon":
                        continue
                    if "armor" in scroll_id and slot_key not in ["armor", "head"]:
                        continue
                    keyboard.append([InlineKeyboardButton(
                        f"{slot_icon} {item.get('name','')}{ench_text} — {scroll['name']} (x{qty})",
                        callback_data=f"enchant_{item_id}_{scroll_id}"
                    )])
    
    text += f"\n_Доступные свитки:_\n"
    for scroll_id, qty in scrolls.items():
        scroll = ENCHANT_SCROLLS[scroll_id]
        text += f"  {scroll['icon']} {scroll['name']} (x{qty})\n"
    
    keyboard.append([InlineKeyboardButton("🔙 В кузницу", callback_data="city_forge")])
    
    await query.message.delete()
    await context.bot.send_message(chat_id=user_id, text=text, parse_mode='Markdown', 
                                   reply_markup=InlineKeyboardMarkup(keyboard))


# ========== ИНКРУСТИРОВАНИЕ (ЗАГЛУШКА) ==========
async def forge_engrave(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Инкрустирование — заглушка"""
    query = update.callback_query
    await query.answer("💎 Инкрустирование скоро появится! Ювелир в пути...", show_alert=True)


# ========== ПОКАЗ РЕСУРСОВ ==========
async def forge_show_resources(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Показывает ресурсы игрока"""
    query = update.callback_query
    user_id = query.from_user.id
    
    resources = get_player_resources(user_id)
    
    cats = {"metal": 0, "fabric": 0, "bone": 0, "alchemy": 0, "food": 0, "magic": 0, "other": 0}
    for res_id, qty in resources.items():
        res = ALL_ITEMS.get(res_id, {})
        cat = res.get("resource_type", "other")
        if cat in cats:
            cats[cat] += qty
    
    from handlers.inventory import get_inventory_slots
    used, total = get_inventory_slots(user_id)
    
    text = f"📦 *Мои ресурсы*\n\n"
    text += f"_Потрёпанная сумка искателя подземелий._\n\n"
    text += f"🎒 Занято мест: {used}/{total}\n\n"
    text += f"🔩 Металлы: {cats['metal']}  |  🧵 Ткани: {cats['fabric']}  |  🦴 Кости: {cats['bone']}\n"
    text += f"🧪 Алхимия: {cats['alchemy']}  |  🍖 Провизия: {cats['food']}  |  🔮 Магия: {cats['magic']}\n"
    text += f"🪨 Прочее: {cats['other']}"
    
    keyboard = get_forge_resources_keyboard()
    await query.message.delete()
    
    try:
        with open("/root/bot/images/forge_resources.jpg", "rb") as photo:
            await context.bot.send_photo(chat_id=user_id, photo=photo, caption=text, 
                                         parse_mode=constants.ParseMode.MARKDOWN, reply_markup=keyboard)
    except:
        await context.bot.send_message(chat_id=user_id, text=text, 
                                       parse_mode=constants.ParseMode.MARKDOWN, reply_markup=keyboard)


async def forge_show_resources_category(update: Update, context: ContextTypes.DEFAULT_TYPE, category: str):
    """Показывает ресурсы по категории с редкостью"""
    query = update.callback_query
    user_id = query.from_user.id
    
    resources = get_player_resources(user_id)
    
    cat_names = {
        "metal": "🔩 Металлы", "fabric": "🧵 Ткани", "bone": "🦴 Кости",
        "alchemy": "🧪 Алхимия", "food": "🍖 Провизия", "magic": "🔮 Магия", "other": "🪨 Прочее"
    }
    
    text = f"📦 *{cat_names.get(category, category)}*\n\n"
    
    found = False
    for res_id, qty in resources.items():
        res = ALL_ITEMS.get(res_id, {})
        if res.get("resource_type") == category and qty > 0:
            rarity = res.get("rarity", "common")
            rarity_emoji = RARITY_EMOJI.get(rarity, "⚪")
            icon = res.get('icon', '📦')
            name = res.get('name', res_id)
            text += f"  [{rarity_emoji}] {icon} {name}({qty})\n"
            found = True
    
    if not found:
        text += "_Нет ресурсов этой категории_"
    
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("🔙 К ресурсам", callback_data="forge_resources")],
    ])
    
    await query.message.delete()
    await context.bot.send_message(chat_id=user_id, text=text, parse_mode=constants.ParseMode.MARKDOWN, reply_markup=keyboard)


async def forge_show_resources_all(update: Update, context: ContextTypes.DEFAULT_TYPE, page: int = 1):
    """Показывает ВСЕ ресурсы с пагинацией"""
    query = update.callback_query
    user_id = query.from_user.id
    
    resources = get_player_resources(user_id)
    
    all_resources = []
    for res_id, qty in resources.items():
        res = ALL_ITEMS.get(res_id, {})
        if res.get('type') == 'resource' and qty > 0:
            rarity = res.get("rarity", "common")
            rarity_emoji = RARITY_EMOJI.get(rarity, "⚪")
            icon = res.get('icon', '📦')
            name = res.get('name', res_id)
            all_resources.append(f"[{rarity_emoji}] {icon} {name}({qty})")
    
    ITEMS_PER_PAGE = 15
    total = len(all_resources)
    total_pages = max(1, (total + ITEMS_PER_PAGE - 1) // ITEMS_PER_PAGE)
    page = max(1, min(page, total_pages))
    
    start = (page - 1) * ITEMS_PER_PAGE
    end = min(start + ITEMS_PER_PAGE, total)
    
    text = f"📦 *Все ресурсы* ({page}/{total_pages})\n\n"
    
    if total == 0:
        text += "_Нет ресурсов_"
    else:
        for item in all_resources[start:end]:
            text += f"  {item}\n"
    
    keyboard = []
    nav_row = []
    if page > 1:
        nav_row.append(InlineKeyboardButton("◀ Назад", callback_data=f"forge_all_page_{page-1}"))
    if page < total_pages:
        nav_row.append(InlineKeyboardButton("Вперёд ▶", callback_data=f"forge_all_page_{page+1}"))
    if nav_row:
        keyboard.append(nav_row)
    
    keyboard.append([InlineKeyboardButton("🔙 К ресурсам", callback_data="forge_resources")])
    
    await query.message.delete()
    await context.bot.send_message(chat_id=user_id, text=text, 
                                   parse_mode=constants.ParseMode.MARKDOWN, 
                                   reply_markup=InlineKeyboardMarkup(keyboard))


async def forge_show_recipes(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Показывает ВСЕ рецепты игрока с кнопками Ковать"""
    query = update.callback_query
    user_id = query.from_user.id
    
    resources = get_player_resources(user_id)
    
    text = f"📜 *Мои рецепты*\n\n"
    
    has_recipes = False
    for recipe_id, recipe in RECIPES.items():
        qty = resources.get(recipe_id, 0)
        if qty > 0:
            has_recipes = True
            all_have = True
            missing = []
            for mat_id, mat_qty in recipe["materials"].items():
                have = resources.get(mat_id, 0)
                if have < mat_qty:
                    all_have = False
                    mat = ALL_ITEMS.get(mat_id, {"name": mat_id})
                    missing.append(f"{mat.get('name', mat_id)} ({have}/{mat_qty})")
            
            rarity = recipe.get("rarity", "common")
            rarity_emoji = RARITY_EMOJI.get(rarity, "⚪")
            
            if all_have:
                text += f"  ✅ [{rarity_emoji}] {recipe['icon']} {recipe['name']}({qty}) — *можно ковать*\n"
            else:
                text += f"  ❌ [{rarity_emoji}] {recipe['icon']} {recipe['name']}({qty})\n"
                if missing:
                    text += f"     _не хватает: {', '.join(missing)}_\n"
    
    if not has_recipes:
        text += "_Нет рецептов. Убей мобов в туннелях чтобы получить!_"
    
    keyboard = get_forge_recipes_keyboard(resources)
    await query.message.delete()
    
    try:
        with open("/root/bot/images/forge_recipes.jpg", "rb") as photo:
            await context.bot.send_photo(chat_id=user_id, photo=photo, caption=text,
                                         parse_mode=constants.ParseMode.MARKDOWN, 
                                         reply_markup=keyboard)
    except:
        await context.bot.send_message(chat_id=user_id, text=text,
                                       parse_mode=constants.ParseMode.MARKDOWN, 
                                       reply_markup=keyboard)


# ========== ХРАНЕНИЕ ДАННЫХ КУЗНИЦЫ ==========
def get_user_data(user_id: int, key: str, default=None):
    """Получает данные игрока из БД"""
    import sqlite3
    with sqlite3.connect("/root/bot/ratings.db") as conn:
        c = conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS user_data 
                     (user_id INTEGER, key TEXT, value TEXT, 
                      PRIMARY KEY (user_id, key))''')
        conn.commit()
        c.execute('SELECT value FROM user_data WHERE user_id = ? AND key = ?', (user_id, key))
        row = c.fetchone()
        if row:
            return int(row[0]) if row[0].isdigit() else row[0]
        return default


def update_user_data(user_id: int, key: str, value):
    """Обновляет данные игрока в БД"""
    import sqlite3
    with sqlite3.connect("/root/bot/ratings.db") as conn:
        c = conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS user_data 
                     (user_id INTEGER, key TEXT, value TEXT, 
                      PRIMARY KEY (user_id, key))''')
        conn.commit()
        c.execute('''INSERT INTO user_data VALUES (?, ?, ?) 
                     ON CONFLICT(user_id, key) DO UPDATE SET value = ?''',
                 (user_id, key, str(value), str(value)))
        conn.commit()