"""Система заточки оружия и брони — предметы хранятся в инвентаре как item_id+N"""
import sqlite3
import asyncio
from typing import Tuple

DB_FILE = "/root/bot/ratings.db"
from core.dice.engine import get_dice_engine, DICE_STICKERS

dice_engine = get_dice_engine()


def get_base_item_id(item_id: str) -> str:
    """butcher_knife+5 → butcher_knife"""
    if "+" in item_id:
        parts = item_id.rsplit("+", 1)
        if len(parts) == 2 and parts[1].isdigit():
            return parts[0]
    return item_id


def get_enchant_level(item_id: str) -> int:
    """butcher_knife+5 → 5, butcher_knife → 0"""
    base = get_base_item_id(item_id)
    if base == item_id:
        return 0
    try:
        return int(item_id.rsplit("+", 1)[1])
    except:
        return 0


def get_enchant_bonus(item_id: str) -> dict:
    """Возвращает бонусы от заточки"""
    level = get_enchant_level(item_id)
    if level <= 0:
        return {}
    
    from handlers.items import ALL_ITEMS
    base_id = get_base_item_id(item_id)
    item = ALL_ITEMS.get(base_id, ALL_ITEMS.get(item_id, {}))
    slot = item.get("slot", "")
    
    if slot == "weapon":
        return {"enchant_damage_min": level * 2, "enchant_damage_max": level * 2}
    elif slot in ("armor", "head"):
        return {"enchant_defense": level}
    elif slot == "accessory":
        return {"enchant_magic_defense": level}
    return {}


def format_enchant_level(level: int) -> str:
    """5 → ' +5', 0 → ''"""
    if level <= 0:
        return ""
    return f" +{level}"


def _update_equipment(user_id: int, old_item_id: str, new_item_id: str):
    """Обновляет экипировку если предмет был надет"""
    with sqlite3.connect(DB_FILE) as conn:
        cur = conn.execute("SELECT slot FROM equipment WHERE user_id = ? AND item_id = ?", (user_id, old_item_id))
        row = cur.fetchone()
        if row:
            slot = row[0]
            conn.execute("UPDATE equipment SET item_id = ? WHERE user_id = ? AND slot = ?", (new_item_id, user_id, slot))
            conn.commit()


async def perform_enchant_animation(context, user_id: int, item_id: str, scroll_type: str) -> Tuple[bool, str, str]:
    """Заточка с анимацией. Возвращает (успех, сообщение, новый_item_id)"""
    base_id = get_base_item_id(item_id)
    current_level = get_enchant_level(item_id)
    
    if current_level >= 16:
        return False, "❌ Максимальный уровень заточки +16!", item_id
    
    from handlers.items import ALL_ITEMS
    item = ALL_ITEMS.get(base_id, ALL_ITEMS.get(item_id, {}))
    item_name = item.get('name', 'Предмет')
    item_icon = item.get('icon', '⚔️')
    
    # 🎲 БРОСОК КУБИКОВ
    roll1 = dice_engine.roll_1d6()
    roll2 = dice_engine.roll_1d6()
    total = roll1 + roll2
    
    # "Бросаем кубики..."
    msg = await context.bot.send_message(chat_id=user_id, text="🎲 *Бросаем кубики...*", parse_mode='Markdown')
    await asyncio.sleep(1.0)
    await msg.delete()
    
    # Показываем кубики по 3 секунды
    sticker_msgs = []
    for i, roll in enumerate([roll1, roll2]):
        label = "Первый" if i == 0 else "Второй"
        if roll in DICE_STICKERS:
            try:
                msg = await context.bot.send_sticker(chat_id=user_id, sticker=DICE_STICKERS[roll])
                sticker_msgs.append(msg)
            except:
                msg = await context.bot.send_message(chat_id=user_id, text=f"🎲 {label} кубик: *{roll}*", parse_mode='Markdown')
                sticker_msgs.append(msg)
        else:
            msg = await context.bot.send_message(chat_id=user_id, text=f"🎲 {label} кубик: *{roll}*", parse_mode='Markdown')
            sticker_msgs.append(msg)
        await asyncio.sleep(3.0)
    
    # Удаляем ВСЕ кубики
    for msg in sticker_msgs:
        try:
            await msg.delete()
        except:
            pass
    
    await asyncio.sleep(1.0)
    
    # Определяем результат
    is_critical = (total == 12)
    is_fumble = (total <= 3)
    is_safe_zone = (current_level < 4)
    
    if scroll_type == "crystal":
        success_threshold = 5
    elif scroll_type == "blessed":
        success_threshold = 5
    else:
        success_threshold = 7
    
    success = total >= success_threshold
    
    from handlers.inventory import remove_item, add_item
    
    # Убираем старый предмет
    remove_item(user_id, item_id, 1)
    
    if is_critical:
        new_level = min(16, current_level + 2)
        new_item_id = f"{base_id}+{new_level}"
        add_item(user_id, new_item_id, 1)
        _update_equipment(user_id, item_id, new_item_id)
        
        glow_image = "enchant_gold.jpg"
        title = "🌟 КРИТИЧЕСКАЯ ЗАТОЧКА!"
        result = f"+{new_level} (+2 уровня!)"
        flavor = "_Древняя магия свитка сливается с металлом, создавая невероятную мощь!_"
        
    elif success:
        new_level = current_level + 1
        new_item_id = f"{base_id}+{new_level}"
        add_item(user_id, new_item_id, 1)
        _update_equipment(user_id, item_id, new_item_id)
        
        if new_level <= 5:
            glow_image = "enchant_blue.jpg"
            flavor = "_Предмет впитывает магию свитка, становясь прочнее._"
        elif new_level <= 7:
            glow_image = "enchant_red.jpg"
            flavor = "_Сила древних рун пробуждается в этом предмете._"
        elif new_level <= 12:
            glow_image = "enchant_bright_red.jpg"
            flavor = "_Энергия переполняет предмет, заставляя его вибрировать._"
        else:
            glow_image = "enchant_gold.jpg"
            flavor = "_Сам воздух дрожит от мощи, заключённой в этом предмете._"
        
        title = "✅ Заточка успешна!"
        result = f"+{new_level}"
        
    elif is_fumble:
        glow_image = "enchant_fail.jpg"
        title = "💀 КРИТИЧЕСКИЙ ПРОВАЛ!"
        result = "Уничтожен"
        flavor = "_Магия рассеивается, оставляя лишь пепел и разочарование._"
        
        message = f"{item_icon} *{item_name}*\n\n{title}\n🎲 {roll1}+{roll2}=*{total}*\n▸ *{result}*\n\n{flavor}"
        try:
            with open(f"/root/bot/images/{glow_image}", "rb") as photo:
                await context.bot.send_photo(chat_id=user_id, photo=photo, caption=message, parse_mode='Markdown')
        except:
            await context.bot.send_message(chat_id=user_id, text=message, parse_mode='Markdown')
        return False, message, item_id
        
    elif is_safe_zone:
        add_item(user_id, item_id, 1)
        glow_image = "enchant_fail.jpg"
        title = "❌ Неудача"
        result = f"Не изменился (+{current_level})"
        flavor = "_Свиток вспыхнул, но магия не смогла пробиться сквозь защиту._"
        
        message = f"{item_icon} *{item_name}*\n\n{title}\n🎲 {roll1}+{roll2}=*{total}*\n▸ *{result}*\n\n{flavor}"
        try:
            with open(f"/root/bot/images/{glow_image}", "rb") as photo:
                await context.bot.send_photo(chat_id=user_id, photo=photo, caption=message, parse_mode='Markdown')
        except:
            await context.bot.send_message(chat_id=user_id, text=message, parse_mode='Markdown')
        return False, message, item_id
        
    elif scroll_type == "blessed":
        new_item_id = base_id
        add_item(user_id, new_item_id, 1)
        _update_equipment(user_id, item_id, new_item_id)
        glow_image = "enchant_fail.jpg"
        title = "💔 Неудача"
        result = "Сброшен на 0"
        flavor = "_Благословение спасло предмет от разрушения, но заточка сброшена._"
        
        message = f"{item_icon} *{item_name}*\n\n{title}\n🎲 {roll1}+{roll2}=*{total}*\n▸ *{result}*\n\n{flavor}"
        try:
            with open(f"/root/bot/images/{glow_image}", "rb") as photo:
                await context.bot.send_photo(chat_id=user_id, photo=photo, caption=message, parse_mode='Markdown')
        except:
            await context.bot.send_message(chat_id=user_id, text=message, parse_mode='Markdown')
        return False, message, new_item_id
        
    else:
        glow_image = "enchant_fail.jpg"
        title = "💀 Вещь сломалась!"
        result = f"Уничтожен (+{current_level})"
        flavor = "_Металл не выдержал напряжения и рассыпался в прах._"
        
        message = f"{item_icon} *{item_name}*\n\n{title}\n🎲 {roll1}+{roll2}=*{total}*\n▸ *{result}*\n\n{flavor}"
        try:
            with open(f"/root/bot/images/{glow_image}", "rb") as photo:
                await context.bot.send_photo(chat_id=user_id, photo=photo, caption=message, parse_mode='Markdown')
        except:
            await context.bot.send_message(chat_id=user_id, text=message, parse_mode='Markdown')
        return False, message, item_id
    
    # ТОЛЬКО УСПЕХ — показываем результат ОДИН раз
    message = f"{item_icon} *{item_name}*\n\n{title}\n🎲 {roll1}+{roll2}=*{total}*\n▸ Результат: *{result}*\n\n{flavor}"
    
    try:
        with open(f"/root/bot/images/{glow_image}", "rb") as photo:
            await context.bot.send_photo(chat_id=user_id, photo=photo, caption=message, parse_mode='Markdown')
    except:
        await context.bot.send_message(chat_id=user_id, text=message, parse_mode='Markdown')
    
    return (success, message, new_item_id)