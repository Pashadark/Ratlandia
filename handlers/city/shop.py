"""Магазин за крошки — покупка и продажа"""

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from telegram import constants
import sys
import sqlite3
sys.path.append('/root/bot')
from handlers.inventory import get_crumbs, spend_crumbs, add_crumbs, add_item, get_inventory, use_consumable
from handlers.items import EQUIPMENT, CONSUMABLES, CHESTS, ALL_ITEMS
from keyboards.inline.shop import (
    get_shop_main_keyboard,
    get_shop_buy_keyboard,
    get_shop_back_keyboard,
    get_shop_category_keyboard
)

SELL_MULTIPLIER = 0.5
DB_FILE = "/root/bot/ratings.db"

SHOP_CATEGORIES = {
    "weapon": "⚔️ Оружие",
    "armor": "🛡️ Броня",
    "head": "🎩 Шляпы",
    "accessory": "💍 Аксессуары",
    "consumable": "🧪 Расходники",
    "chest": "📦 Сундуки",
}


async def shop_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Главное меню магазина — выбор купить или продать"""
    user_id = update.effective_user.id
    
    if update.callback_query:
        query = update.callback_query
        user_id = query.from_user.id
        chat_id = user_id
        await query.message.delete()
    else:
        chat_id = update.effective_chat.id
    
    crumbs = get_crumbs(user_id)
    
    text = f"""🍔 МАГАЗИН У ЛЁШИ

_Лёша — старый толстый крыс с прокуренными усами и вечно прищуренным левым глазом. Говорят, в молодости он был легендарным контрабандистом и знал каждый туннель от Верхнего Слива до Глубинных Коллекторов. Теперь он держит лавку, где можно найти всё: от ржавого кинжала до мифического сундука. Цены кусаются, но Лёша всегда говорит: «Качество, брат, качество!»_

🧀 Твой кошелёк: *{crumbs}* крошек

Что хочешь сделать?"""
    
    try:
        with open("/root/bot/images/shop.jpg", "rb") as photo:
            await context.bot.send_photo(
                chat_id=chat_id, photo=photo, caption=text,
                parse_mode=constants.ParseMode.MARKDOWN,
                reply_markup=get_shop_main_keyboard()
            )
    except:
        await context.bot.send_message(
            chat_id=chat_id, text=text,
            parse_mode=constants.ParseMode.MARKDOWN,
            reply_markup=get_shop_main_keyboard()
        )


async def shop_buy_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Меню категорий для покупки"""
    query = update.callback_query
    user_id = query.from_user.id
    crumbs = get_crumbs(user_id)
    
    text = f"""🛒 ПОКУПКА

_Лёша лениво указывает лапой на полки: «Выбирай, что душе угодно. Только деньги вперёд!»_

🧀 Твой кошелёк: *{crumbs}* крошек

Что ищешь?"""
    
    await query.message.delete()
    try:
        with open("/root/bot/images/shop.jpg", "rb") as photo:
            await context.bot.send_photo(
                chat_id=user_id, photo=photo, caption=text,
                parse_mode=constants.ParseMode.MARKDOWN,
                reply_markup=get_shop_buy_keyboard()
            )
    except:
        await context.bot.send_message(
            chat_id=user_id, text=text,
            parse_mode=constants.ParseMode.MARKDOWN,
            reply_markup=get_shop_buy_keyboard()
        )


async def shop_sell_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Показывает инвентарь для продажи"""
    query = update.callback_query
    user_id = query.from_user.id
    crumbs = get_crumbs(user_id)
    inventory = get_inventory(user_id)
    
    text = f"""💰 ПРОДАЖА

_Лёша прищуривается и оценивающе смотрит на твои вещи: «Ну, показывай, что принёс. Только не жди, что я дам полную цену — бизнес есть бизнес!»_

🧀 Твой кошелёк: *{crumbs}* крошек
📦 Продажа за *50%* от покупной цены

"""
    
    if not inventory:
        text += "❌ У тебя нет предметов для продажи."
        keyboard = get_shop_back_keyboard()
    else:
        text += "Что продаёшь?"
        keyboard = []
        
        equip_items = []
        consumable_items = []
        chest_items = []
        
        for item_id, qty in inventory.items():
            if item_id in ALL_ITEMS:
                item = ALL_ITEMS[item_id]
                buy_price = item.get("price", 500)
                sell_price = int(buy_price * SELL_MULTIPLIER)
                
                if item.get("type") == "equipment":
                    equip_items.append((item_id, item, qty, sell_price))
                elif item.get("type") == "consumable":
                    consumable_items.append((item_id, item, qty, sell_price))
                elif item.get("type") == "chest":
                    chest_items.append((item_id, item, qty, sell_price))
        
        if equip_items:
            text += "\n\n▸ ЭКИПИРОВКА"
            for item_id, item, qty, sell_price in equip_items[:5]:
                text += f"\n  {item['icon']} {item['name']} x{qty} — *{sell_price}* 🧀"
                keyboard.append([InlineKeyboardButton(
                    f"{item['icon']} Продать {item['name']}",
                    callback_data=f"shop_sell_{item_id}"
                )])
        
        if consumable_items:
            text += "\n\n▸ РАСХОДНИКИ"
            for item_id, item, qty, sell_price in consumable_items[:3]:
                text += f"\n  {item['icon']} {item['name']} x{qty} — *{sell_price}* 🧀"
                keyboard.append([InlineKeyboardButton(
                    f"{item['icon']} Продать {item['name']}",
                    callback_data=f"shop_sell_{item_id}"
                )])
        
        if chest_items:
            text += "\n\n▸ СУНДУКИ"
            for item_id, item, qty, sell_price in chest_items:
                text += f"\n  {item['icon']} {item['name']} x{qty} — *{sell_price}* 🧀"
                keyboard.append([InlineKeyboardButton(
                    f"{item['icon']} Продать {item['name']}",
                    callback_data=f"shop_sell_{item_id}"
                )])
        
        keyboard.append([InlineKeyboardButton("🔙 Назад", callback_data="shop_back_to_main")])
    
    await query.message.delete()
    try:
        with open("/root/bot/images/shop.jpg", "rb") as photo:
            await context.bot.send_photo(
                chat_id=user_id, photo=photo, caption=text,
                parse_mode=constants.ParseMode.MARKDOWN,
                reply_markup=InlineKeyboardMarkup(keyboard)
            )
    except:
        await context.bot.send_message(
            chat_id=user_id, text=text,
            parse_mode=constants.ParseMode.MARKDOWN,
            reply_markup=InlineKeyboardMarkup(keyboard)
        )


async def shop_category(update: Update, context: ContextTypes.DEFAULT_TYPE, category: str, page: int = 0):
    """Показывает товары в выбранной категории с пагинацией"""
    query = update.callback_query
    user_id = query.from_user.id
    crumbs = get_crumbs(user_id)
    
    title = SHOP_CATEGORIES.get(category, "ТОВАРЫ")
    items_to_show = []
    
    if category == "weapon":
        items_to_show = [(iid, item) for iid, item in EQUIPMENT.items() if item.get("slot") == "weapon"]
    elif category == "armor":
        items_to_show = [(iid, item) for iid, item in EQUIPMENT.items() if item.get("slot") == "armor"]
    elif category == "head":
        items_to_show = [(iid, item) for iid, item in EQUIPMENT.items() if item.get("slot") == "head"]
    elif category == "accessory":
        items_to_show = [(iid, item) for iid, item in EQUIPMENT.items() if item.get("slot") == "accessory"]
    elif category == "consumable":
        items_to_show = [(iid, item) for iid, item in CONSUMABLES.items()]
    elif category == "chest":
        items_to_show = [(iid, item) for iid, item in CHESTS.items()]
    
    ITEMS_PER_PAGE = 5
    total_pages = max(1, (len(items_to_show) + ITEMS_PER_PAGE - 1) // ITEMS_PER_PAGE)
    page = max(0, min(page, total_pages - 1))
    
    start_idx = page * ITEMS_PER_PAGE
    end_idx = min(start_idx + ITEMS_PER_PAGE, len(items_to_show))
    current_items = items_to_show[start_idx:end_idx]
    
    text = f"""🛒 {title.upper()}

🧀 Твой кошелёк: *{crumbs}* крошек
📄 Страница {page + 1}/{total_pages}

"""
    
    if not items_to_show:
        text += "❌ В этой категории пока нет товаров."
        keyboard = get_shop_back_keyboard()
    else:
        text += "*Товары:*"
        for item_id, item in current_items:
            price = item.get("price", 500)
            can_afford = "✅" if crumbs >= price else "❌"
            text += f"\n\n{can_afford} {item['icon']} *{item['name']}*\n   _{item['desc']}_\n   💰 *{price}* 🧀"
        
        keyboard = get_shop_category_keyboard(category, page, total_pages, current_items, crumbs)
    
    await query.message.delete()
    try:
        with open("/root/bot/images/shop.jpg", "rb") as photo:
            await context.bot.send_photo(
                chat_id=user_id, photo=photo, caption=text,
                parse_mode=constants.ParseMode.MARKDOWN, reply_markup=keyboard
            )
    except:
        await context.bot.send_message(
            chat_id=user_id, text=text,
            parse_mode=constants.ParseMode.MARKDOWN, reply_markup=keyboard
        )


async def handle_shop_buy(update: Update, context: ContextTypes.DEFAULT_TYPE, item_id: str):
    """Покупка товара"""
    query = update.callback_query
    user_id = query.from_user.id
    
    item = ALL_ITEMS.get(item_id)
    if not item:
        await query.answer("❌ Товар не найден!", show_alert=True)
        return
    
    price = item.get("price", 500)
    
    if not spend_crumbs(user_id, price):
        await query.answer(f"❌ Недостаточно крошек! Нужно {price} 🧀", show_alert=True)
        return
    
    add_item(user_id, item_id)
    await query.answer(f"✅ Куплено: {item['name']}!", show_alert=True)
    
    if item_id in EQUIPMENT:
        category = item.get("slot", "head")
    elif item_id in CONSUMABLES:
        category = "consumable"
    elif item_id in CHESTS:
        category = "chest"
    else:
        category = "weapon"
    
    await shop_category(update, context, category, 0)


async def handle_shop_sell(update: Update, context: ContextTypes.DEFAULT_TYPE, item_id: str):
    """Продажа предмета"""
    query = update.callback_query
    user_id = query.from_user.id
    
    item = ALL_ITEMS.get(item_id)
    if not item:
        await query.answer("❌ Предмет не найден!", show_alert=True)
        return
    
    inventory = get_inventory(user_id)
    if item_id not in inventory or inventory[item_id] <= 0:
        await query.answer("❌ У тебя нет этого предмета!", show_alert=True)
        return
    
    buy_price = item.get("price", 500)
    sell_price = int(buy_price * SELL_MULTIPLIER)
    
    if item.get("type") == "consumable":
        use_consumable(user_id, item_id)
    else:
        with sqlite3.connect(DB_FILE) as conn:
            c = conn.cursor()
            c.execute('SELECT quantity FROM inventory WHERE user_id = ? AND item_id = ?', (user_id, item_id))
            row = c.fetchone()
            if row and row[0] > 1:
                c.execute('UPDATE inventory SET quantity = quantity - 1 WHERE user_id = ? AND item_id = ?', (user_id, item_id))
            else:
                c.execute('DELETE FROM inventory WHERE user_id = ? AND item_id = ?', (user_id, item_id))
            conn.commit()
    
    add_crumbs(user_id, sell_price)
    await query.answer(f"✅ Продано за {sell_price} 🧀!", show_alert=True)
    await shop_sell_menu(update, context)


async def handle_shop_page(update: Update, context: ContextTypes.DEFAULT_TYPE, category: str, page: int):
    """Обрабатывает переключение страниц в магазине"""
    await shop_category(update, context, category, page)