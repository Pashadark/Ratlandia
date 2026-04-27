"""Кузница — вход из города, крафт предметов"""

from telegram import Update
from telegram.ext import ContextTypes
from telegram import constants
import sys
sys.path.append('/root/bot')

from handlers.items import ALL_ITEMS, RECIPES, get_available_recipes
from handlers.inventory import add_item, get_crumbs, spend_crumbs, add_action_history
from handlers.crafting import (
    get_player_resources, spend_materials, has_materials,
    roll_craft_dice, check_craft_success, check_craft_critical,
    get_quality_from_roll, save_crafted_item, get_craft_difficulty_info,
    CraftQuality
)
from keyboards.inline.blacksmith import (
    get_forge_main_keyboard, get_forge_recipe_keyboard,
    get_forge_craft_result_keyboard, get_forge_resources_keyboard,
    get_forge_recipes_keyboard
)
from core.dice.engine import get_dice_engine
import random
import asyncio

# Единый движок кубиков
dice_engine = get_dice_engine()


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
    """Главное меню кузницы"""
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
    
    # АНИМАЦИЯ КОВКИ
    anim_msgs = ["🔥 *Разогрев горна...*", "⚒️ *Удар молота!*", "✨ *Закалка в масле...*"]
    anim_msg = await context.bot.send_message(chat_id=user_id, text=anim_msgs[0], parse_mode=constants.ParseMode.MARKDOWN)
    for i in range(1, 3):
        await asyncio.sleep(0.5)
        await anim_msg.edit_text(anim_msgs[i], parse_mode=constants.ParseMode.MARKDOWN)
    await asyncio.sleep(0.5)
    await anim_msg.delete()
    
    # 🎲 БРОСОК КУБИКОВ ЧЕРЕЗ DICE ENGINE
    craft_result = dice_engine.roll_craft()
    dice_sum = craft_result.total
    
    # Проклятый рецепт
    if recipe.get("cursed"):
        success_chance = recipe.get("success_chance", 0.3)
        if random.random() > success_chance:
            spend_materials(user_id, recipe["materials"])
            text = f"💀 *ПРОКЛЯТАЯ КОВКА — ПРОВАЛ!*\n\n"
            text += craft_result.format() + "\n\n"
            text += f"💔 *Рецепт поглотил материалы!*\n"
            if recipe.get("fail_result"):
                fail_item = ALL_ITEMS.get(recipe["fail_result"], {})
                add_item(user_id, recipe["fail_result"])
                text += f"📦 Вместо предмета: {fail_item.get('icon','💔')} *{fail_item.get('name','???')}*\n"
            
            keyboard = get_forge_craft_result_keyboard()
            image_path = "/root/bot/images/forge_fail.jpg"
            try:
                with open(image_path, "rb") as photo:
                    await context.bot.send_photo(chat_id=user_id, photo=photo, caption=text, parse_mode=constants.ParseMode.MARKDOWN, reply_markup=keyboard)
            except:
                await context.bot.send_message(chat_id=user_id, text=text, parse_mode=constants.ParseMode.MARKDOWN, reply_markup=keyboard)
            
            update_user_data(user_id, "forge_fails", get_user_data(user_id, "forge_fails", 0) + 1)
            return
    
    # Проверка успеха
    success, fail_reason = check_craft_success(dice_sum, rarity)
    
    if not success:
        spend_materials(user_id, recipe["materials"])
        
        if random.random() < 0.3:
            from handlers.inventory import remove_item
            remove_item(user_id, recipe_id, 1)
            text = f"💔 *КОВКА ПРОВАЛЕНА!*\n\n{craft_result.format()}\n\n📜 *Рецепт уничтожен!*\n❌ {fail_reason}"
        elif random.random() < 0.5:
            text = f"❌ *КОВКА ПРОВАЛЕНА!*\n\n{craft_result.format()}\n\n📦 *Материалы потеряны!*\n❌ {fail_reason}"
        else:
            add_item(user_id, result_item_id)
            quality, bonuses = get_quality_from_roll(dice_sum)
            text = f"⚒️ *КОВКА ЗАВЕРШЕНА!*\n\n{craft_result.format()}\n\n💎 Качество: {quality.color} *{quality.display.upper()}*\n📦 Создано: {result_item.get('icon','📦')} *{result_item.get('name','???')}*\n"
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
                await context.bot.send_photo(chat_id=user_id, photo=photo, caption=text, parse_mode=constants.ParseMode.MARKDOWN, reply_markup=keyboard)
        except:
            await context.bot.send_message(chat_id=user_id, text=text, parse_mode=constants.ParseMode.MARKDOWN, reply_markup=keyboard)
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
    
    text = f"⚒️ *КОВКА ЗАВЕРШЕНА!*\n\n{craft_result.format()}\n\n"
    text += f"💎 Качество: {quality.color} *{quality.display.upper()}*\n"
    text += f"👤 Создал: *{crafter_name}*\n"
    text += f"📦 Создано: {result_item.get('icon','📦')} *{result_item.get('name','???')}*\n"
    if is_critical:
        text += "\n🌟 *КРИТИЧЕСКИЙ УСПЕХ!* Качество повышено!\n"
    if crit:
        text += "\n🌟 *ДВОЙНАЯ КОВКА!* Создано 2 предмета!\n"
    if bonuses:
        text += "\n✨ *Бонусы качества:*\n" + "\n".join([f"  +{v} к {k}" for k, v in bonuses.items()])
    
    update_user_data(user_id, "forge_fails", 0)
    keyboard = get_forge_craft_result_keyboard()
    image_path = "/root/bot/images/forge_success.jpg" if dice_sum >= 8 else "/root/bot/images/forge_fail.jpg"
    
    try:
        with open(image_path, "rb") as photo:
            await context.bot.send_photo(chat_id=user_id, photo=photo, caption=text, parse_mode=constants.ParseMode.MARKDOWN, reply_markup=keyboard)
    except:
        await context.bot.send_message(chat_id=user_id, text=text, parse_mode=constants.ParseMode.MARKDOWN, reply_markup=keyboard)


# ========== ЗАТОЧКА + ИНКРУСТИРОВАНИЕ (ЗАГЛУШКИ) ==========
async def forge_sharpen(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Заточка оружия — заглушка"""
    query = update.callback_query
    await query.answer("🗡️ Заточка скоро появится! Мастер точит камни...", show_alert=True)

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
    text = f"📦 *МОИ РЕСУРСЫ*\n\n"
    
    if not resources:
        text += "_Нет ресурсов._\n"
    else:
        text += "📜 *РЕЦЕПТЫ:*\n"
        has_recipes = False
        for res_id, qty in resources.items():
            res = ALL_ITEMS.get(res_id, {})
            if res.get('type') == 'recipe' and qty > 0:
                text += f"  {res.get('icon','📜')} {res.get('name',res_id)}: *{qty}* шт.\n"
                has_recipes = True
        if not has_recipes:
            text += "  _Нет рецептов (убей мобов в туннелях!)_\n"
        
        categories = {
            "metal": "🔩 МЕТАЛЛЫ", "fabric": "🧵 ТКАНИ", "bone": "🦴 КОСТИ",
            "alchemy": "🧪 АЛХИМИЯ", "food": "🍖 ПРОВИЗИЯ", "blueprint": "📜 ЧЕРТЕЖИ",
            "magic": "🔮 МАГИЯ", "other": "🪨 ПРОЧЕЕ"
        }
        for cat_id, cat_name in categories.items():
            cat_items = []
            for res_id, qty in resources.items():
                res = ALL_ITEMS.get(res_id, {})
                if res.get("resource_type") == cat_id and qty > 0:
                    cat_items.append(f"  {res.get('icon','📦')} {res.get('name',res_id)}: *{qty}*")
            if cat_items:
                text += f"\n{cat_name}:\n" + "\n".join(cat_items) + "\n"
    
    keyboard = get_forge_resources_keyboard()
    await query.message.delete()
    
    # 🆕 КАРТИНКА ДЛЯ РЕСУРСОВ
    try:
        with open("/root/bot/images/forge_resources.jpg", "rb") as photo:
            await context.bot.send_photo(chat_id=user_id, photo=photo, caption=text, 
                                         parse_mode=constants.ParseMode.MARKDOWN, reply_markup=keyboard)
    except:
        await context.bot.send_message(chat_id=user_id, text=text, 
                                       parse_mode=constants.ParseMode.MARKDOWN, reply_markup=keyboard)


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

async def forge_show_recipes(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Показывает ВСЕ рецепты игрока"""
    query = update.callback_query
    user_id = query.from_user.id
    
    resources = get_player_resources(user_id)
    
    text = f"📜 *МОИ РЕЦЕПТЫ*\n\n"
    
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
            
            if all_have:
                text += f"  ✅ {recipe['icon']} {recipe['name']}: *{qty}* шт. — можно ковать\n"
            else:
                text += f"  ❌ {recipe['icon']} {recipe['name']}: *{qty}* шт.\n"
                text += f"     _не хватает: {', '.join(missing)}_\n"
    
    if not has_recipes:
        text += "_Нет рецептов. Убей мобов в туннелях чтобы получить!_"
    
    keyboard = get_forge_recipes_keyboard()
    await query.message.delete()
    
    # 🆕 КАРТИНКА ДЛЯ РЕЦЕПТОВ
    try:
        with open("/root/bot/images/forge_recipes.jpg", "rb") as photo:
            await context.bot.send_photo(chat_id=user_id, photo=photo, caption=text,
                                         parse_mode=constants.ParseMode.MARKDOWN, reply_markup=keyboard)
    except:
        await context.bot.send_message(chat_id=user_id, text=text,
                                       parse_mode=constants.ParseMode.MARKDOWN, reply_markup=keyboard)

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