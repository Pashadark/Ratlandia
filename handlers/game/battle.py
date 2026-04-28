"""Боевая система для режима Туннели — с выбором защиты и кооперативом"""

import random
import sqlite3
import json
from typing import Dict, Tuple
import asyncio
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from telegram import constants
from handlers.tunnel_rooms import go_home
from handlers.character import (
    get_character_stats, 
    update_character_stats,
    increment_tunnel_deaths, 
    add_tunnel_crumbs
)

from handlers.tunnel_monsters import (
    get_monster, 
    process_loot,
    get_tunnel_run, 
    add_run_loot, 
    end_tunnel_run, 
    mark_boss_defeated
)

from handlers.tunnel_coop import (
    get_coop_battle, 
    update_coop_battle, 
    delete_coop_battle,
    give_coop_loot, 
    process_boss_loot as coop_process_boss_loot
)

from handlers.items import ALL_ITEMS
from handlers.inventory import add_crumbs, add_xp, add_item

DB_FILE = "/root/bot/ratings.db"

import logging
logger = logging.getLogger(__name__)

# ========== СОХРАНЕНИЕ БОЯ В БД ==========

def save_battle_to_db(user_id: int, battle_state: dict, monster_state: dict, player_state: dict, player_defense: str):
    """Сохраняет состояние боя в БД"""
    try:
        with sqlite3.connect(DB_FILE) as conn:
            conn.execute("""INSERT OR REPLACE INTO tunnel_battle_save 
                           (user_id, battle_state, monster_state, player_state, player_defense, saved_at)
                           VALUES (?, ?, ?, ?, ?, datetime('now'))""",
                        (user_id, json.dumps(battle_state), json.dumps(monster_state), 
                         json.dumps(player_state), player_defense))
            conn.commit()
        logger.info(f"💾 Бой сохранён в БД для user_id={user_id}")
    except Exception as e:
        logger.error(f"❌ Ошибка сохранения боя: {e}")


def load_battle_from_db(user_id: int):
    """Загружает состояние боя из БД"""
    try:
        with sqlite3.connect(DB_FILE) as conn:
            row = conn.execute("""SELECT battle_state, monster_state, player_state, player_defense 
                                  FROM tunnel_battle_save WHERE user_id = ?""", (user_id,)).fetchone()
            if row:
                logger.info(f"📂 Бой загружен из БД для user_id={user_id}")
                return {
                    "battle_state": json.loads(row[0]),
                    "monster_state": json.loads(row[1]),
                    "player_state": json.loads(row[2]),
                    "player_defense": row[3]
                }
    except Exception as e:
        logger.error(f"❌ Ошибка загрузки боя: {e}")
    return None


def delete_battle_from_db(user_id: int):
    """Удаляет сохранённый бой из БД"""
    try:
        with sqlite3.connect(DB_FILE) as conn:
            conn.execute("DELETE FROM tunnel_battle_save WHERE user_id = ?", (user_id,))
            conn.commit()
        logger.info(f"🗑️ Бой удалён из БД для user_id={user_id}")
    except Exception as e:
        logger.error(f"❌ Ошибка удаления боя: {e}")


# ========== ВСПОМОГАТЕЛЬНАЯ ФУНКЦИЯ ==========

async def safe_edit_or_send(query, user_id, text, keyboard, context):
    """Безопасно редактирует сообщение или отправляет новое"""
    try:
        await query.message.edit_text(
            text,
            parse_mode=constants.ParseMode.MARKDOWN,
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
    except:
        await query.message.delete()
        await context.bot.send_message(
            chat_id=user_id,
            text=text,
            parse_mode=constants.ParseMode.MARKDOWN,
            reply_markup=InlineKeyboardMarkup(keyboard)
        )


# ========== ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ ==========

def calculate_player_damage(strength: int, blessed: bool = False) -> int:
    """Рассчитывает урон игрока"""
    base = strength
    bonus = random.randint(1, 3)
    if blessed:
        bonus += 1
    return base + bonus


def calculate_monster_damage(monster: Dict) -> int:
    """Рассчитывает урон монстра"""
    return random.randint(monster["min_damage"], monster["max_damage"])


def apply_body_part_effect(body_part: str, monster_state: Dict) -> str:
    """Применяет эффект от попадания по части тела"""
    effect_text = ""
    
    if body_part == "head":
        monster_state["stunned"] = 1
        effect_text = "💫 Враг оглушён! Пропускает следующий ход."
    elif body_part == "paws":
        monster_state["weakened"] = 1
        effect_text = "⬇️ Враг замедлен! В следующем ходу нанесёт меньше урона."
    elif body_part == "body":
        monster_state["bleeding"] = 2
        effect_text = "🩸 Кровотечение! Враг будет терять по 1 HP каждый ход."
    elif body_part == "tail":
        monster_state["disoriented"] = 1
        effect_text = "😵 Враг дезориентирован! В следующем ходу атакует случайно."
    
    return effect_text


def get_monster_body_part() -> str:
    """Враг выбирает случайную часть тела игрока для атаки"""
    return random.choice(["head", "paws", "body", "tail"])


def get_monster_defense() -> str:
    """Монстр выбирает случайную часть тела для защиты"""
    return random.choice(["head", "paws", "body", "tail"])


def update_tunnel_run(user_id: int, **kwargs):
    """Обновляет данные активного забега"""
    with sqlite3.connect(DB_FILE) as conn:
        c = conn.cursor()
        updates = [f"{k} = ?" for k in kwargs.keys()]
        values = list(kwargs.values()) + [user_id]
        c.execute(f"UPDATE tunnel_run SET {','.join(updates)} WHERE user_id = ?", values)
        conn.commit()


def apply_monster_hit_effect(body_part: str, damage: int, player_state: Dict, run_data: Dict) -> Tuple[int, str]:
    """Применяет эффект от попадания врага по игроку"""
    effect_text = ""
    final_damage = damage
    
    if body_part == "head":
        final_damage += 2
        effect_text = f"💥 Критический урон! +2 к урону."
    elif body_part == "paws":
        player_state["weakened"] = 1
        effect_text = f"⬇️ Ты ослаблен! В следующем ходу нанесёшь меньше урона."
    elif body_part == "body":
        effect_text = f"👊 Обычный удар."
    elif body_part == "tail":
        lost_crumbs = min(damage * 2, run_data.get("crumbs_collected", 0))
        if lost_crumbs > 0:
            run_data["crumbs_collected"] -= lost_crumbs
            update_tunnel_run(user_id=run_data.get("user_id", 0), crumbs_collected=run_data["crumbs_collected"])
            effect_text = f"😱 Паника! Ты выронил {lost_crumbs} крошек."
        else:
            effect_text = f"😰 Удар по хвосту, но крошек нет."
    
    return final_damage, effect_text


# ========== ОСОБЫЕ СПОСОБНОСТИ МОНСТРОВ ==========

def trigger_monster_ability(monster: Dict, monster_state: Dict, monster_hp: int, max_hp: int) -> Tuple[int, str]:
    """Активирует особую способность монстра"""
    ability = monster.get("ability")
    effect_text = ""
    heal = 0
    
    if ability == "regeneration":
        if monster_hp < max_hp:
            heal = 1
            effect_text = "🔄 Червь восстанавливает 1 здоровье!"
    
    elif ability == "curl":
        if "curl_used" not in monster_state and monster_hp <= max_hp // 2:
            monster_state["curl_used"] = True
            monster_state["curled"] = 2
            effect_text = "🛡️ Мокрица сворачивается в клубок! -1 к получаемому урону на 2 хода."
    
    elif ability == "fast":
        if random.randint(1, 100) <= 20:
            monster_state["double_attack"] = True
            effect_text = "⚡ Шуршун двигается невероятно быстро! Атакует дважды!"
    
    elif ability == "spores":
        if random.randint(1, 100) <= 30:
            monster_state["poisoned_player"] = 2
            effect_text = "☠️ Плесневик выпускает споры! Ты отравлен на 2 хода."
    
    elif ability == "block":
        if "block_cooldown" not in monster_state:
            monster_state["block_cooldown"] = 0
        if monster_state["block_cooldown"] <= 0:
            if random.randint(1, 100) <= 50:
                monster_state["blocking"] = True
                monster_state["block_cooldown"] = 3
                effect_text = "🛡️ Отступница готовится блокировать атаку!"
        else:
            monster_state["block_cooldown"] -= 1
    
    elif ability == "many_legs":
        monster_state["double_attack"] = True
        effect_text = "🐛 Многоножка атакует дважды!"
    
    elif ability == "hard_shell":
        if "attack_count" not in monster_state:
            monster_state["attack_count"] = 0
        monster_state["attack_count"] += 1
        if monster_state["attack_count"] % 3 == 0:
            monster_state["shell_block"] = True
            effect_text = "🛡️ Жук подставляет панцирь! Следующая атака не пройдёт!"
    
    elif ability == "slow":
        if random.randint(1, 100) <= 40:
            monster_state["slowed_player"] = 1
            effect_text = "🐌 Слизь замедляет тебя! В следующем ходу атакуешь случайно."
    
    elif ability == "vampirism":
        monster_state["vampirism"] = True
    
    elif ability == "web":
        if "web_cooldown" not in monster_state:
            monster_state["web_cooldown"] = 0
        if monster_state["web_cooldown"] <= 0:
            if random.randint(1, 100) <= 60:
                monster_state["webbed_player"] = True
                monster_state["web_cooldown"] = 3
                effect_text = "🕸️ Паук опутывает тебя паутиной! Ты пропускаешь следующий ход!"
        else:
            monster_state["web_cooldown"] -= 1
    
    elif ability == "curl_ball":
        if "curl_ball_used" not in monster_state and monster_hp <= max_hp * 0.3:
            monster_state["curl_ball_used"] = True
            monster_state["curled_ball"] = 3
            heal = 10
            effect_text = "🛡️ Сороконожка сворачивается в шар! Восстанавливает 10 HP и получает половинный урон на 3 хода!"
    
    elif ability == "frenzy":
        if "frenzy_used" not in monster_state and monster_hp <= max_hp // 2:
            monster_state["frenzy_used"] = True
            monster_state["frenzied"] = True
            effect_text = "😤 Упырь впадает в ярость! +2 к урону до конца боя!"
    
    elif ability == "survival":
        if "survival_used" not in monster_state and monster_hp <= 0:
            if random.randint(1, 100) <= 50:
                monster_state["survival_used"] = True
                heal = max_hp // 2
                effect_text = "💪 Таракан отказывается умирать! Восстанавливает половину здоровья!"
                return heal, effect_text
    
    elif ability == "attach":
        if "attached" not in monster_state:
            if random.randint(1, 100) <= 50:
                monster_state["attached"] = True
                effect_text = "🩸 Пиявка присосалась! Ты теряешь 2 здоровья каждый ход! Атакуй в голову или лапы чтобы оторвать!"
    
    elif ability == "hypnosis":
        if "hypnosis_cooldown" not in monster_state:
            monster_state["hypnosis_cooldown"] = 0
        if monster_state["hypnosis_cooldown"] <= 0:
            monster_state["hypnotized_player"] = True
            monster_state["hypnosis_cooldown"] = 4
            effect_text = "👁️ Хорёк гипнотизирует тебя! Ты пропускаешь ход и получишь двойной урон!"
        else:
            monster_state["hypnosis_cooldown"] -= 1
    
    elif ability == "two_heads":
        monster_state["double_attack"] = True
        if "heads" not in monster_state:
            monster_state["heads"] = 2
        effect_text = "🐀🐀 Две головы атакуют дважды!"
    
    elif ability == "constrict":
        if "constricted" not in monster_state:
            if random.randint(1, 100) <= 40:
                monster_state["constricted"] = True
                effect_text = "🐍 Уж обвивает тебя! Ты теряешь 2 здоровья каждый ход! Нанеси 10 урона за ход чтобы вырваться!"
    
    elif ability == "multiple":
        if "heal_used" not in monster_state and monster_hp <= max_hp // 3:
            monster_state["heal_used"] = True
            heal = 20
            effect_text = "💚 Кот восстанавливает 20 здоровья!"
        elif "roar_cooldown" not in monster_state:
            monster_state["roar_cooldown"] = 0
        if monster_state.get("roar_cooldown", 0) <= 0:
            if random.randint(1, 100) <= 40:
                monster_state["roared"] = True
                monster_state["roar_cooldown"] = 4
                effect_text = "🗣️ Кот издаёт оглушающий вопль! Ты пропускаешь ход!"
        if "roar_cooldown" in monster_state:
            monster_state["roar_cooldown"] -= 1
    
    return heal, effect_text


# ========== ОСНОВНАЯ БОЕВАЯ ФУНКЦИЯ ==========

async def start_battle(update: Update, context: ContextTypes.DEFAULT_TYPE, 
                       user_id: int, monster_id: str):
    """Начинает бой с монстром"""
    
    monster = get_monster(monster_id)
    if not monster:
        return
    
    stats = get_character_stats(user_id)
    run_data = get_tunnel_run(user_id)
    
    battle_state = {
        "monster_id": monster_id,
        "monster_hp": monster["health"],
        "monster_max_hp": monster["health"],
        "player_hp": stats["current_health"],
        "player_max_hp": stats["max_health"],
        "turn": 1,
        "blessed": run_data.get("blessed", False) if run_data else False
    }
    
    monster_state = {}
    player_state = {}
    
    context.user_data["tunnel_battle"] = battle_state
    context.user_data["tunnel_monster_state"] = monster_state
    context.user_data["tunnel_player_state"] = player_state
    context.user_data["tunnel_battle_log"] = ""
    context.user_data["tunnel_player_defense"] = ""
    
    # 💾 Сохраняем бой в БД
    save_battle_to_db(user_id, battle_state, monster_state, player_state, "")
    
    await show_defense_selection(update, context, user_id, monster, battle_state, monster_state, player_state)


async def show_defense_selection(update: Update, context: ContextTypes.DEFAULT_TYPE,
                                  user_id: int, monster: Dict, battle_state: Dict,
                                  monster_state: Dict, player_state: Dict):
    """Показывает выбор защиты перед атакой"""
    query = update.callback_query
    
    monster_id = battle_state["monster_id"]
    battle_log = context.user_data.get("tunnel_battle_log", "")
    
    difficulty_names = {1: "лёгкий", 2: "средний", 3: "сложный", 4: "очень сложный", 5: "босс"}
    difficulty = difficulty_names.get(monster.get("level", 1), "обычный")
    
    status_text = f"⚔️ *Бой с {monster['name']}* ({difficulty})\n\n"
    
    if battle_log:
        status_text += battle_log + "\n"
    else:
        status_text += f"⚔️ *Ход {battle_state['turn']}*\n\n"
        status_text += f"❤️ Твоё здоровье: *{battle_state['player_hp']}/{battle_state['player_max_hp']}*\n"
        status_text += f"💀 Здоровье врага: *{battle_state['monster_hp']}/{battle_state['monster_max_hp']}*\n\n"
        status_text += f"_{monster['desc']}_\n\n"
    
    active_effects = []
    if player_state.get("poisoned_player", 0) > 0:
        active_effects.append(f"☠️ Ты отравлен ({player_state['poisoned_player']} хода)")
    if player_state.get("weakened", 0) > 0:
        active_effects.append(f"⬇️ Ты ослаблен ({player_state['weakened']} хода)")
    if player_state.get("hypnotized_player"):
        active_effects.append("👁️ Ты загипнотизирован (1 ход)")
    if monster_state.get("bleeding", 0) > 0:
        active_effects.append(f"🩸 Враг кровоточит ({monster_state['bleeding']} хода)")
    if monster_state.get("stunned", 0) > 0:
        active_effects.append("💫 Враг оглушён (1 ход)")
    if monster_state.get("weakened", 0) > 0:
        active_effects.append(f"⬇️ Враг ослаблен ({monster_state['weakened']} хода)")
    if monster_state.get("curled", 0) > 0:
        active_effects.append(f"🛡️ Враг в клубке ({monster_state['curled']} хода)")
    
    if active_effects:
        status_text += f"*Эффекты:*\n  " + "\n  ".join(active_effects) + "\n\n"
    
    status_text += f"*🛡️ Какую часть тела будешь защищать?*"
    
    keyboard = [
        [InlineKeyboardButton("🧠 Защищать голову", callback_data="tunnel_defend_head")],
        [InlineKeyboardButton("🦾 Защищать лапы", callback_data="tunnel_defend_paws")],
        [InlineKeyboardButton("🫁 Защищать туловище", callback_data="tunnel_defend_body")],
        [InlineKeyboardButton("🪢 Защищать хвост", callback_data="tunnel_defend_tail")],
        [InlineKeyboardButton("🏃 Сбежать", callback_data="tunnel_flee_new")],
    ]
    
    await query.message.delete()
    
    try:
        await context.bot.send_photo(
            chat_id=user_id,
            photo=open(f"/root/bot/images/tunnel_monsters/{monster_id}.jpg", "rb"),
            caption=status_text,
            parse_mode=constants.ParseMode.MARKDOWN,
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
    except:
        await context.bot.send_message(
            chat_id=user_id,
            text=status_text,
            parse_mode=constants.ParseMode.MARKDOWN,
            reply_markup=InlineKeyboardMarkup(keyboard)
        )


async def show_attack_selection(update: Update, context: ContextTypes.DEFAULT_TYPE,
                                 user_id: int, monster: Dict, battle_state: Dict,
                                 monster_state: Dict, player_state: Dict,
                                 player_defense: str):
    """Показывает выбор атаки после выбора защиты"""
    query = update.callback_query
    
    monster_id = battle_state["monster_id"]
    battle_log = context.user_data.get("tunnel_battle_log", "")
    defense_names = {"head": "голову", "paws": "лапы", "body": "туловище", "tail": "хвост"}
    
    difficulty_names = {1: "лёгкий", 2: "средний", 3: "сложный", 4: "очень сложный", 5: "босс"}
    difficulty = difficulty_names.get(monster.get("level", 1), "обычный")
    
    status_text = f"⚔️ *Бой с {monster['name']}* ({difficulty})\n\n"
    
    if battle_log:
        status_text += battle_log + "\n"
    
    status_text += f"❤️ Твоё здоровье: *{battle_state['player_hp']}/{battle_state['player_max_hp']}*\n"
    status_text += f"💀 Здоровье врага: *{battle_state['monster_hp']}/{battle_state['monster_max_hp']}*\n\n"
    status_text += f"🛡️ Ты защищаешь: *{defense_names.get(player_defense, player_defense)}*\n\n"
    status_text += "*⚔️ Выбери куда будешь бить:*"
    
    keyboard = []
    
    can_attack = not (player_state.get("webbed_player") or 
                      player_state.get("hypnotized_player") or
                      player_state.get("roared"))
    
    if can_attack:
        if player_state.get("slowed_player", 0) > 0:
            keyboard.append([InlineKeyboardButton("🎲 Случайная атака (замедлен)", callback_data="tunnel_attack_random")])
        else:
            keyboard.extend([
                [InlineKeyboardButton("🧠 Бить в голову (оглушение)", callback_data="tunnel_attack_head")],
                [InlineKeyboardButton("🦾 Бить в лапы (замедление)", callback_data="tunnel_attack_paws")],
                [InlineKeyboardButton("🫁 Бить в туловище (кровотечение)", callback_data="tunnel_attack_body")],
                [InlineKeyboardButton("🪢 Бить в хвост (дезориентация)", callback_data="tunnel_attack_tail")],
            ])
    
    if monster_state.get("attached"):
        keyboard = [
            [InlineKeyboardButton("🧠 Ударить в голову (оторвать)", callback_data="tunnel_attack_head")],
            [InlineKeyboardButton("🦾 Ударить по лапам (оторвать)", callback_data="tunnel_attack_paws")],
        ]
    elif monster_state.get("constricted"):
        keyboard = [
            [InlineKeyboardButton("💪 Попытаться вырваться", callback_data="tunnel_break_free")],
        ]
    
    await query.message.delete()
    
    try:
        await context.bot.send_photo(
            chat_id=user_id,
            photo=open(f"/root/bot/images/tunnel_monsters/{monster_id}.jpg", "rb"),
            caption=status_text,
            parse_mode=constants.ParseMode.MARKDOWN,
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
    except:
        await context.bot.send_message(
            chat_id=user_id,
            text=status_text,
            parse_mode=constants.ParseMode.MARKDOWN,
            reply_markup=InlineKeyboardMarkup(keyboard)
        )


async def process_defense_choice(update: Update, context: ContextTypes.DEFAULT_TYPE,
                                  user_id: int, defense_part: str):
    """Обрабатывает выбор защиты"""
    query = update.callback_query
    
    battle_state = context.user_data.get("tunnel_battle", {})
    monster_state = context.user_data.get("tunnel_monster_state", {})
    player_state = context.user_data.get("tunnel_player_state", {})
    
    if not battle_state:
        # 🔄 Пытаемся восстановить бой из БД
        saved = load_battle_from_db(user_id)
        if saved:
            context.user_data["tunnel_battle"] = saved["battle_state"]
            context.user_data["tunnel_monster_state"] = saved["monster_state"]
            context.user_data["tunnel_player_state"] = saved["player_state"]
            context.user_data["tunnel_player_defense"] = saved["player_defense"]
            battle_state = saved["battle_state"]
            monster_state = saved["monster_state"]
            player_state = saved["player_state"]
            await query.answer("⚠️ Бой восстановлен из сохранения!", show_alert=True)
        else:
            await query.answer("❌ Бой не найден!")
            return
    
    context.user_data["tunnel_player_defense"] = defense_part
    monster = get_monster(battle_state["monster_id"])
    
    # 💾 Сохраняем бой в БД
    save_battle_to_db(user_id, battle_state, monster_state, player_state, defense_part)
    
    await query.answer(f"🛡️ Ты защищаешь {defense_part}!")
    await show_attack_selection(update, context, user_id, monster, battle_state, monster_state, player_state, defense_part)


async def process_player_attack(update: Update, context: ContextTypes.DEFAULT_TYPE,
                                 user_id: int, body_part: str):
    """Обрабатывает атаку игрока с учётом защиты"""
    query = update.callback_query
    
    battle_state = context.user_data.get("tunnel_battle", {})
    monster_state = context.user_data.get("tunnel_monster_state", {})
    player_state = context.user_data.get("tunnel_player_state", {})
    player_defense = context.user_data.get("tunnel_player_defense", "body")
    run_data = get_tunnel_run(user_id)
    
    if not battle_state:
        await safe_edit_or_send(query, user_id, "❌ Бой не найден!", [], context)
        return
    
    monster = get_monster(battle_state["monster_id"])
    stats = get_character_stats(user_id)
    
    parts_ru = {"head": "голову", "paws": "лапы", "body": "туловище", "tail": "хвост"}
    parts_ru_nominative = {"head": "голова", "paws": "лапы", "body": "туловище", "tail": "хвост"}
    
    battle_log = f"❤️ Твоё здоровье: *{battle_state['player_hp']}/{battle_state['player_max_hp']}*\n"
    battle_log += f"💀 Здоровье врага: *{battle_state['monster_hp']}/{battle_state['monster_max_hp']}*\n\n"
    battle_log += f"*Твоя атака:*\n"
    
    monster_defense = get_monster_defense()
    
    if body_part == monster_defense:
        damage = 0
        defense_ru = parts_ru.get(monster_defense, monster_defense)
        battle_log += f"  🛡️ *Монстр заблокировал!* Он защищал *{defense_ru}*!\n"
    else:
        damage = calculate_player_damage(stats["strength"], battle_state["blessed"])
        base_damage = damage
        
        if player_state.get("weakened", 0) > 0:
            damage = max(1, damage - 1)
            battle_log += f"  ⬇️ Ты ослаблен! Урон снижен с {base_damage} до {damage}\n"
            player_state["weakened"] -= 1
        
        if monster_state.get("blocking"):
            damage = 0
            monster_state["blocking"] = False
            battle_log += f"  🛡️ Враг заблокировал атаку!\n"
        elif monster_state.get("shell_block"):
            damage = 0
            monster_state["shell_block"] = False
            battle_log += f"  🛡️ Панцирь отразил атаку!\n"
        elif monster_state.get("curled", 0) > 0:
            damage = max(1, damage - 1)
            body_ru = parts_ru.get(body_part, body_part)
            battle_log += f"  🎯 Попадание в *{body_ru}*! Урон снижен до *{damage}* (враг в клубке)\n"
        elif monster_state.get("curled_ball", 0) > 0:
            damage = damage // 2
            body_ru = parts_ru.get(body_part, body_part)
            battle_log += f"  🎯 Попадание в *{body_ru}*! Урон снижен до *{damage}* (враг в шаре)\n"
        else:
            body_ru = parts_ru.get(body_part, body_part)
            defense_ru = parts_ru.get(monster_defense, monster_defense)
            battle_log += f"  🎯 *Попадание!* Ты ударил в *{body_ru}* (враг защищал *{defense_ru}*)!\n"
        
        if damage > 0:
            battle_state["monster_hp"] -= damage
            battle_log += f"  ⚔️ Нанесено *{damage}* урона!\n"
            effect_text = apply_body_part_effect(body_part, monster_state)
            if effect_text:
                battle_log += f"  {effect_text}\n"
        
        if monster_state.get("vampirism") and damage > 0:
            heal = damage // 2
            battle_state["monster_hp"] = min(battle_state["monster_hp"] + heal, battle_state["monster_max_hp"])
            battle_log += f"  🦇 Враг восстановил {heal} здоровья (вампиризм)!\n"
        
        if monster_state.get("attached") and body_part in ["head", "paws"]:
            monster_state["attached"] = False
            battle_log += f"  🩸 Ты оторвал пиявку!\n"
    
    if battle_state["monster_hp"] <= 0:
        if monster.get("ability") == "survival" and "survival_used" not in monster_state:
            heal, effect_text = trigger_monster_ability(monster, monster_state, 0, battle_state["monster_max_hp"])
            if heal > 0:
                battle_state["monster_hp"] = heal
                battle_log += f"💪 *{effect_text}*\n\n"
                context.user_data["tunnel_battle"] = battle_state
                context.user_data["tunnel_monster_state"] = monster_state
                context.user_data["tunnel_player_state"] = player_state
                context.user_data["tunnel_battle_log"] = battle_log
                save_battle_to_db(user_id, battle_state, monster_state, player_state, player_defense)
                await show_defense_selection(update, context, user_id, monster, battle_state, monster_state, player_state)
                return
        
        context.user_data["tunnel_battle_log"] = battle_log
        delete_battle_from_db(user_id)
        await end_battle_victory(update, context, user_id, monster, battle_state)
        return
    
    has_effects = False
    effects_log = ""
    
    if player_state.get("poisoned_player", 0) > 0:
        battle_state["player_hp"] -= 1
        player_state["poisoned_player"] -= 1
        effects_log += f"  ☠️ Ты получил 1 урона от яда!\n"
        has_effects = True
    
    if monster_state.get("bleeding", 0) > 0:
        battle_state["monster_hp"] -= 1
        monster_state["bleeding"] -= 1
        effects_log += f"  🩸 Враг получил 1 урона от кровотечения!\n"
        has_effects = True
    
    if monster_state.get("attached"):
        battle_state["player_hp"] -= 2
        effects_log += f"  🩸 Пиявка высосала 2 здоровья!\n"
        has_effects = True
    
    if monster_state.get("constricted"):
        battle_state["player_hp"] -= 2
        effects_log += f"  🐍 Уж сдавливает тебя! -2 здоровья!\n"
        has_effects = True
    
    if has_effects:
        battle_log += f"\n*Эффекты:*\n{effects_log}"
    
    if monster_state.get("curled", 0) > 0:
        monster_state["curled"] -= 1
    if monster_state.get("curled_ball", 0) > 0:
        monster_state["curled_ball"] -= 1
    
    player_state["slowed_player"] = 0
    player_state["webbed_player"] = False
    player_state["hypnotized_player"] = False
    player_state["roared"] = False
    
    if battle_state["player_hp"] <= 0:
        context.user_data["tunnel_battle_log"] = battle_log
        delete_battle_from_db(user_id)
        await end_battle_defeat(update, context, user_id, monster, battle_state)
        return
    
    if battle_state["monster_hp"] <= 0:
        context.user_data["tunnel_battle_log"] = battle_log
        delete_battle_from_db(user_id)
        await end_battle_victory(update, context, user_id, monster, battle_state)
        return
    
    battle_state["turn"] += 1
    
    battle_log += f"\n*Ход врага:*\n"
    
    heal, ability_text = trigger_monster_ability(monster, monster_state, battle_state["monster_hp"], battle_state["monster_max_hp"])
    if heal > 0:
        battle_state["monster_hp"] = min(battle_state["monster_hp"] + heal, battle_state["monster_max_hp"])
        battle_log += f"  {ability_text}\n"
    elif ability_text:
        battle_log += f"  {ability_text}\n"
    
    if not monster_state.get("stunned", 0) > 0:
        attack_count = 2 if monster_state.get("double_attack") else 1
        monster_state["double_attack"] = False
        
        for i in range(attack_count):
            if attack_count > 1:
                battle_log += f"\n  *Атака {i+1}:*\n"
            
            if monster_state.get("disoriented", 0) > 0:
                target_part = random.choice(["head", "paws", "body", "tail"])
                battle_log += f"  😵 Враг дезориентирован! Бьёт случайно в *{parts_ru.get(target_part, target_part)}*\n"
                monster_state["disoriented"] -= 1
            else:
                target_part = get_monster_body_part()
                battle_log += f"  👊 Враг целится в твоё *{parts_ru_nominative.get(target_part, target_part)}*\n"
            
            monster_damage = calculate_monster_damage(monster)
            
            if monster_state.get("frenzied"):
                monster_damage += 2
                battle_log += f"  😤 Враг в ярости! +2 к урону\n"
            
            if monster_state.get("weakened", 0) > 0:
                old_damage = monster_damage
                monster_damage = max(1, monster_damage - 1)
                battle_log += f"  ⬇️ Враг ослаблен! Урон снижен с {old_damage} до {monster_damage}\n"
                monster_state["weakened"] -= 1
            
            if target_part == player_defense:
                monster_damage = monster_damage // 2
                battle_log += f"  🛡️ *Ты заблокировал!* Урон снижен вдвое до *{monster_damage}*!\n"
                hit_effect = ""
            else:
                final_damage, hit_effect = apply_monster_hit_effect(target_part, monster_damage, player_state, run_data)
                monster_damage = final_damage
                defense_ru = parts_ru_nominative.get(player_defense, player_defense)
                battle_log += f"  💔 Враг попал в *{parts_ru_nominative.get(target_part, target_part)}* (ты защищал *{defense_ru}*)!\n"
            
            if player_state.get("hypnotized_player"):
                monster_damage *= 2
                battle_log += f"  👁️ Двойной урон от гипноза!\n"
            
            battle_state["player_hp"] -= monster_damage
            battle_log += f"  💥 Нанесено *{monster_damage}* урона!"
            if hit_effect:
                battle_log += f" {hit_effect}"
            battle_log += "\n"
    else:
        battle_log += f"  💫 Враг оглушён! Пропускает ход.\n"
    
    monster_state["stunned"] = 0
    monster_state["disoriented"] = 0
    
    if battle_state["player_hp"] <= 0:
        context.user_data["tunnel_battle_log"] = battle_log
        delete_battle_from_db(user_id)
        await end_battle_defeat(update, context, user_id, monster, battle_state)
        return
    
    if battle_state["monster_hp"] <= 0:
        context.user_data["tunnel_battle_log"] = battle_log
        delete_battle_from_db(user_id)
        await end_battle_victory(update, context, user_id, monster, battle_state)
        return
    
    context.user_data["tunnel_battle"] = battle_state
    context.user_data["tunnel_monster_state"] = monster_state
    context.user_data["tunnel_player_state"] = player_state
    context.user_data["tunnel_battle_log"] = battle_log
    
    # 💾 Сохраняем бой после каждого хода
    save_battle_to_db(user_id, battle_state, monster_state, player_state, player_defense)
    
    await show_defense_selection(update, context, user_id, monster, battle_state, monster_state, player_state)


async def end_battle_victory(update: Update, context: ContextTypes.DEFAULT_TYPE,
                              user_id: int, monster: Dict, battle_state: Dict):
    """Завершение боя победой"""
    query = update.callback_query
    
    battle_log = context.user_data.get("tunnel_battle_log", "")
    
    loot = process_loot(battle_state["monster_id"])
    from handlers.inventory import add_action_history
    add_action_history(user_id, f"Убит {monster['name']}", monster.get('icon', '👹'))
    add_run_loot(user_id, loot["crumbs"], monster.get("xp", monster.get("base_xp", 10)))
    update_character_stats(user_id, current_health=battle_state["player_hp"])
    
    if monster["level"] == 5:
        mark_boss_defeated(user_id, battle_state["monster_id"])
    
    text = f"{battle_log}\n\n" if battle_log else ""
    text += f"🎉 *Победа!*\n\n"
    text += f"{monster['death_text']}\n\n"
    text += f"*Получено:*\n"
    text += f"  🧀 Крошек: {loot['crumbs']}\n"
    text += f"  ✨ Опыта: {monster.get('xp', monster.get('base_xp', 10))}\n"
    
    if loot["items"]:
        text += f"\n🎁 *Добыча:*\n"
        for item_id in loot["items"]:
            item = ALL_ITEMS.get(item_id, {"name": item_id, "icon": "📦"})
            text += f"  {item['icon']} {item['name']}\n"
            add_item(user_id, item_id)
    
    if loot.get("resources"):
        text += f"\n📦 *Ресурсы:*\n"
        for res_id in loot["resources"]:
            res = ALL_ITEMS.get(res_id, {"name": res_id, "icon": "📦"})
            text += f"  {res.get('icon', '📦')} {res.get('name', res_id)}\n"
            add_item(user_id, res_id)
    
    keyboard = [
        [InlineKeyboardButton("➡️ Идти дальше", callback_data="tunnel_next_room")],
        [InlineKeyboardButton("🏠 Вернуться домой", callback_data="tunnel_go_home")],
    ]
    
    await query.message.delete()
    
    image_path = "/root/bot/images/battle_victory.jpg"
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
    
    context.user_data.pop("tunnel_battle", None)
    context.user_data.pop("tunnel_monster_state", None)
    context.user_data.pop("tunnel_player_state", None)
    context.user_data.pop("tunnel_player_defense", None)
    context.user_data.pop("tunnel_battle_log", None)


async def end_battle_defeat(update: Update, context: ContextTypes.DEFAULT_TYPE,
                             user_id: int, monster: Dict, battle_state: Dict):
    """Завершение боя поражением"""
    query = update.callback_query
    
    battle_log = context.user_data.get("tunnel_battle_log", "")
    
    increment_tunnel_deaths(user_id)
    
    result = end_tunnel_run(user_id, died=True)
    add_tunnel_crumbs(user_id, result['crumbs'])
    update_character_stats(user_id, current_health=1, last_health_update=None)
    
    text = f"{battle_log}\n\n" if battle_log else ""
    text += f"💀 *Поражение...*\n\n"
    text += f"Ты пал в бою с {monster['name']}.\n\n"
    text += f"*Потеряно крошек:* {result['crumbs']}\n"
    text += f"\n_Ты возвращаешься в нору, чтобы залечить раны..._"
    
    keyboard = [[InlineKeyboardButton("🏠 В нору", callback_data="tunnel_menu")]]
    
    await safe_edit_or_send(query, user_id, text, keyboard, context)
    
    context.user_data.pop("tunnel_battle", None)
    context.user_data.pop("tunnel_monster_state", None)
    context.user_data.pop("tunnel_player_state", None)
    context.user_data.pop("tunnel_player_defense", None)
    context.user_data.pop("tunnel_battle_log", None)


# ========== КООПЕРАТИВНЫЙ БОЙ ==========

async def start_coop_battle(update: Update, context: ContextTypes.DEFAULT_TYPE,
                            host_id: int, guest_id: int, boss_id: str, battle_id: str):
    """Запускает кооперативный бой с боссом"""
    battle = get_coop_battle(battle_id)
    if not battle:
        return
    
    boss = get_monster(boss_id)
    if not boss:
        return
    
    await show_coop_defense_selection(context, battle_id, host_id, boss)


async def show_coop_defense_selection(context: ContextTypes.DEFAULT_TYPE,
                                       battle_id: str, player_id: int, boss: Dict):
    """Показывает выбор защиты в кооперативном бою"""
    battle = get_coop_battle(battle_id)
    if not battle:
        return
    
    player_hp = battle["host_hp"] if player_id == battle["host_id"] else battle["guest_hp"]
    
    text = f"""⚔️ *Бой с {boss['name']}* (кооператив)

❤️ Твоё здоровье: *{player_hp}*
💀 Здоровье босса: *{battle['boss_hp']}/{battle['boss_max_hp']}*
🔄 Ход: *{battle['turn']}*

*🛡️ Какую часть тела будешь защищать?*"""

    keyboard = [
        [InlineKeyboardButton("🧠 Защищать голову", callback_data=f"coop_defend_head_{battle_id}")],
        [InlineKeyboardButton("🦾 Защищать лапы", callback_data=f"coop_defend_paws_{battle_id}")],
        [InlineKeyboardButton("🫁 Защищать туловище", callback_data=f"coop_defend_body_{battle_id}")],
        [InlineKeyboardButton("🪢 Защищать хвост", callback_data=f"coop_defend_tail_{battle_id}")],
    ]
    
    try:
        await context.bot.send_photo(
            chat_id=player_id,
            photo=open(f"/root/bot/images/tunnel_monsters/{battle['boss_id']}.jpg", "rb"),
            caption=text,
            parse_mode=constants.ParseMode.MARKDOWN,
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
    except:
        await context.bot.send_message(
            chat_id=player_id,
            text=text,
            parse_mode=constants.ParseMode.MARKDOWN,
            reply_markup=InlineKeyboardMarkup(keyboard)
        )


async def show_coop_attack_selection(context: ContextTypes.DEFAULT_TYPE,
                                      battle_id: str, player_id: int, boss: Dict,
                                      defense_part: str):
    """Показывает выбор атаки в кооперативном бою"""
    battle = get_coop_battle(battle_id)
    if not battle:
        return
    
    player_hp = battle["host_hp"] if player_id == battle["host_id"] else battle["guest_hp"]
    defense_names = {"head": "голову", "paws": "лапы", "body": "туловище", "tail": "хвост"}
    
    text = f"""⚔️ *Бой с {boss['name']}* (кооператив)

❤️ Твоё здоровье: *{player_hp}*
💀 Здоровье босса: *{battle['boss_hp']}/{battle['boss_max_hp']}*
🛡️ Ты защищаешь: *{defense_names.get(defense_part, defense_part)}*

*⚔️ Выбери куда будешь бить:*"""

    keyboard = [
        [InlineKeyboardButton("🧠 Бить в голову", callback_data=f"coop_attack_head_{battle_id}_{defense_part}")],
        [InlineKeyboardButton("🦾 Бить в лапы", callback_data=f"coop_attack_paws_{battle_id}_{defense_part}")],
        [InlineKeyboardButton("🫁 Бить в туловище", callback_data=f"coop_attack_body_{battle_id}_{defense_part}")],
        [InlineKeyboardButton("🪢 Бить в хвост", callback_data=f"coop_attack_tail_{battle_id}_{defense_part}")],
    ]
    
    try:
        await context.bot.send_photo(
            chat_id=player_id,
            photo=open(f"/root/bot/images/tunnel_monsters/{battle['boss_id']}.jpg", "rb"),
            caption=text,
            parse_mode=constants.ParseMode.MARKDOWN,
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
    except:
        await context.bot.send_message(
            chat_id=player_id,
            text=text,
            parse_mode=constants.ParseMode.MARKDOWN,
            reply_markup=InlineKeyboardMarkup(keyboard)
        )


async def process_coop_attack(update: Update, context: ContextTypes.DEFAULT_TYPE,
                               user_id: int, battle_id: str, attack_part: str, defense_part: str):
    """Обрабатывает атаку игрока в кооперативном бою"""
    query = update.callback_query
    
    battle = get_coop_battle(battle_id)
    if not battle:
        await query.answer("❌ Бой не найден!")
        return
    
    if user_id != battle["current_player"]:
        await query.answer("❌ Сейчас не твой ход!")
        return
    
    boss = get_monster(battle["boss_id"])
    if not boss:
        await query.answer("❌ Босс не найден!")
        return
    
    is_host = (user_id == battle["host_id"])
    player_hp = battle["host_hp"] if is_host else battle["guest_hp"]
    other_player_id = battle["guest_id"] if is_host else battle["host_id"]
    
    stats = get_character_stats(user_id)
    damage = calculate_player_damage(stats["strength"])
    
    new_boss_hp = max(0, battle["boss_hp"] - damage)
    
    parts_ru = {"head": "голову", "paws": "лапы", "body": "туловище", "tail": "хвост"}
    battle_log = f"⚔️ Игрок атакует в *{parts_ru.get(attack_part, attack_part)}* и наносит *{damage}* урона!\n"
    
    if new_boss_hp <= 0:
        await query.message.delete()
        
        loot = give_coop_loot(battle["host_id"], battle["guest_id"], battle["boss_id"])
        
        mark_boss_defeated(battle["host_id"], battle["boss_id"])
        mark_boss_defeated(battle["guest_id"], battle["boss_id"])
        
        crumbs_each = boss.get("base_crumbs", 100) // 2
        xp_each = boss.get("base_xp", 100) // 2
        
        add_run_loot(battle["host_id"], crumbs_each, xp_each)
        add_run_loot(battle["guest_id"], crumbs_each, xp_each)
        
        victory_text = f"""🎉 *ПОБЕДА НАД БОССОМ!*

{battle_log}
💀 *{boss['name']}* повержен!

*Награда каждому:*
🧀 Крошек: {crumbs_each}
✨ Опыта: {xp_each}
"""
        
        if loot["host_items"]:
            victory_text += "\n🎁 *Твоя добыча:*\n"
            for item_id in loot["host_items"]:
                item = ALL_ITEMS.get(item_id, {"name": item_id, "icon": "📦"})
                victory_text += f"  {item['icon']} {item['name']}\n"
        
        keyboard = [[InlineKeyboardButton("🏠 В нору", callback_data="tunnel_menu")]]
        
        image_path = "/root/bot/images/coop_victory.jpg"
        try:
            with open(image_path, "rb") as photo:
                await context.bot.send_photo(
                    chat_id=battle["host_id"],
                    photo=photo,
                    caption=victory_text,
                    parse_mode=constants.ParseMode.MARKDOWN,
                    reply_markup=InlineKeyboardMarkup(keyboard)
                )
        except:
            await context.bot.send_message(battle["host_id"], victory_text, 
                                           parse_mode=constants.ParseMode.MARKDOWN,
                                           reply_markup=InlineKeyboardMarkup(keyboard))
        
        if loot["guest_items"]:
            guest_text = f"""🎉 *ПОБЕДА НАД БОССОМ!*

{battle_log}
💀 *{boss['name']}* повержен!

*Награда каждому:*
🧀 Крошек: {crumbs_each}
✨ Опыта: {xp_each}

🎁 *Твоя добыча:*
"""
            for item_id in loot["guest_items"]:
                item = ALL_ITEMS.get(item_id, {"name": item_id, "icon": "📦"})
                guest_text += f"  {item['icon']} {item['name']}\n"
            
            try:
                with open(image_path, "rb") as photo:
                    await context.bot.send_photo(
                        chat_id=battle["guest_id"],
                        photo=photo,
                        caption=guest_text,
                        parse_mode=constants.ParseMode.MARKDOWN,
                        reply_markup=InlineKeyboardMarkup(keyboard)
                    )
            except:
                await context.bot.send_message(battle["guest_id"], guest_text,
                                               parse_mode=constants.ParseMode.MARKDOWN,
                                               reply_markup=InlineKeyboardMarkup(keyboard))
        
        delete_coop_battle(battle_id)
        return
    
    update_coop_battle(battle_id, boss_hp=new_boss_hp, turn=battle["turn"] + 1)
    
    boss_damage = calculate_monster_damage(boss)
    new_player_hp = max(0, player_hp - boss_damage)
    battle_log += f"💥 Босс наносит *{boss_damage}* урона в ответ!\n"
    
    if is_host:
        update_coop_battle(battle_id, host_hp=new_player_hp, current_player=other_player_id)
    else:
        update_coop_battle(battle_id, guest_hp=new_player_hp, current_player=other_player_id)
    
    await query.message.delete()
    
    if new_player_hp <= 0:
        defeat_text = f"""💀 *Поражение...*

{battle_log}
Ты пал в бою с *{boss['name']}*.
"""
        await context.bot.send_message(user_id, defeat_text, parse_mode=constants.ParseMode.MARKDOWN)
        await context.bot.send_message(other_player_id, 
                                       f"💀 Твой напарник пал в бою! Бой окончен.",
                                       parse_mode=constants.ParseMode.MARKDOWN)
        delete_coop_battle(battle_id)
        return
    
    await context.bot.send_message(user_id, f"✅ Твой ход завершён!\n\n{battle_log}", 
                                   parse_mode=constants.ParseMode.MARKDOWN)
    
    await show_coop_defense_selection(context, battle_id, other_player_id, boss)


async def handle_coop_defend(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик выбора защиты в кооперативе"""
    query = update.callback_query
    user_id = query.from_user.id
    data = query.data
    
    parts = data.split("_")
    defense_part = parts[2]
    battle_id = parts[3]
    
    battle = get_coop_battle(battle_id)
    if not battle:
        await query.answer("❌ Бой не найден!")
        return
    
    boss = get_monster(battle["boss_id"])
    
    await query.answer(f"🛡️ Защищаешь {defense_part}!")
    await query.message.delete()
    await show_coop_attack_selection(context, battle_id, user_id, boss, defense_part)


async def handle_coop_attack(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик атаки в кооперативе"""
    query = update.callback_query
    user_id = query.from_user.id
    data = query.data
    
    parts = data.split("_")
    attack_part = parts[2]
    battle_id = parts[3]
    defense_part = parts[4] if len(parts) > 4 else "body"
    
    await process_coop_attack(update, context, user_id, battle_id, attack_part, defense_part)


async def process_flee(update: Update, context: ContextTypes.DEFAULT_TYPE, user_id: int):
    """Попытка сбежать из боя"""
    query = update.callback_query
    
    stats = get_character_stats(user_id)
    battle_state = context.user_data.get("tunnel_battle", {})
    
    if not battle_state or "monster_id" not in battle_state:
        from handlers.tunnel_rooms import go_home
        await go_home(update, context, user_id)
        return
    
    flee_chance = 30 + stats["agility"] * 5
    if battle_state.get("blessed"):
        flee_chance += 10
    
    if random.randint(1, 100) <= flee_chance:
        text = f"🏃 *Побег удался!*\n\n"
        text += f"Ты смог ускользнуть от врага и вернуться в предыдущую комнату.\n"
        text += f"❤️ Здоровье: {battle_state['player_hp']}/{battle_state['player_max_hp']}"
        
        update_character_stats(user_id, current_health=battle_state["player_hp"])
        
        keyboard = [
            [InlineKeyboardButton("➡️ Продолжить", callback_data="tunnel_continue")],
            [InlineKeyboardButton("🏰 В город", callback_data="city_menu")],
        ]
        
        context.user_data.pop("tunnel_battle", None)
        context.user_data.pop("tunnel_monster_state", None)
        context.user_data.pop("tunnel_player_state", None)
        context.user_data.pop("tunnel_player_defense", None)
        context.user_data.pop("tunnel_battle_log", None)
        delete_battle_from_db(user_id)
        
        await safe_edit_or_send(query, user_id, text, keyboard, context)
    else:
        monster = get_monster(battle_state["monster_id"])
        monster_damage = calculate_monster_damage(monster)
        battle_state["player_hp"] -= monster_damage
        
        text = f"❌ *Побег не удался!*\n\n"
        text += f"Враг наносит тебе *{monster_damage}* урона!\n"
        text += f"❤️ Здоровье: {battle_state['player_hp']}/{battle_state['player_max_hp']}"
        
        if battle_state["player_hp"] <= 0:
            delete_battle_from_db(user_id)
            await end_battle_defeat(update, context, user_id, monster, battle_state)
            return
        
        update_character_stats(user_id, current_health=battle_state["player_hp"])
        context.user_data["tunnel_battle"] = battle_state
        save_battle_to_db(user_id, battle_state, 
                         context.user_data.get("tunnel_monster_state", {}),
                         context.user_data.get("tunnel_player_state", {}),
                         context.user_data.get("tunnel_player_defense", ""))
        
        keyboard = [[InlineKeyboardButton("⚔️ Продолжить бой", callback_data="tunnel_continue_battle")]]
        
        await safe_edit_or_send(query, user_id, text, keyboard, context)


# ========== ОБРАБОТЧИКИ КОЛБЭКОВ ==========

async def handle_tunnel_defend(update: Update, context: ContextTypes.DEFAULT_TYPE, defense_part: str):
    """Обработчик выбора защиты"""
    user_id = update.callback_query.from_user.id
    await process_defense_choice(update, context, user_id, defense_part)


async def handle_tunnel_attack(update: Update, context: ContextTypes.DEFAULT_TYPE, body_part: str):
    """Обработчик атаки"""
    user_id = update.callback_query.from_user.id
    await process_player_attack(update, context, user_id, body_part)


async def handle_tunnel_flee_new(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Попытка сбежать из боя с бросанием кубиков"""
    query = update.callback_query
    user_id = query.from_user.id
    
    logger.info("🔴🔴🔴 handle_tunnel_flee_new ВЫЗВАНА!")
    
    battle_state = context.user_data.get("tunnel_battle", {})
    
    # 🔄 Если battle_state пустой — пробуем восстановить из БД
    if not battle_state:
        logger.warning("🔴🔴🔴 battle_state ПУСТОЙ! Ищем в БД...")
        saved = load_battle_from_db(user_id)
        if saved:
            context.user_data["tunnel_battle"] = saved["battle_state"]
            context.user_data["tunnel_monster_state"] = saved["monster_state"]
            context.user_data["tunnel_player_state"] = saved["player_state"]
            context.user_data["tunnel_player_defense"] = saved["player_defense"]
            battle_state = saved["battle_state"]
            await query.answer("⚠️ Бой восстановлен! Продолжай сражаться.", show_alert=True)
            logger.info("🔴🔴🔴 Бой восстановлен из БД!")
        else:
            # Пробуем найти run_data и вернуть в туннели
            run_data = get_tunnel_run(user_id)
            if run_data:
                logger.warning("🔴🔴🔴 Боя нет, но есть run_data. Возвращаем в туннели.")
                await query.answer("⚠️ Данные боя утеряны. Возвращаю в туннели.", show_alert=True)
                from handlers.tunnel_rooms import enter_room
                await enter_room(update, context, user_id)
                return
            else:
                logger.warning("🔴🔴🔴 Ни боя, ни run_data. Отправляем домой.")
                from handlers.tunnel_rooms import go_home
                await go_home(update, context, user_id)
                return
    
    monster = get_monster(battle_state["monster_id"])
    
    await query.message.delete()
    
    dice1 = random.randint(1, 6)
    dice2 = random.randint(1, 6)
    total = dice1 + dice2
    
    # 🎲 ПЕРВЫЙ КУБИК
    try:
        with open("/root/bot/images/dice_1.jpg", "rb") as photo:
            msg = await context.bot.send_photo(
                chat_id=user_id,
                photo=photo,
                caption=f"🎲 *Ты бросаешь кубики...*\n\nПервый кубик: *{dice1}*",
                parse_mode=constants.ParseMode.MARKDOWN
            )
    except:
        msg = await context.bot.send_message(
            chat_id=user_id,
            text=f"🎲 *Ты бросаешь кубики...*\n\nПервый кубик: *{dice1}*",
            parse_mode=constants.ParseMode.MARKDOWN
        )
    
    await asyncio.sleep(2)
    
    try:
        await msg.delete()
    except:
        pass
    
    # 🎲 ВТОРОЙ КУБИК
    try:
        with open("/root/bot/images/dice_1.jpg", "rb") as photo:
            msg = await context.bot.send_photo(
                chat_id=user_id,
                photo=photo,
                caption=f"🎲 *Ты бросаешь кубики...*\n\n{dice1} + *{dice2}* = *{total}*",
                parse_mode=constants.ParseMode.MARKDOWN
            )
    except:
        msg = await context.bot.send_message(
            chat_id=user_id,
            text=f"🎲 *Ты бросаешь кубики...*\n\n{dice1} + *{dice2}* = *{total}*",
            parse_mode=constants.ParseMode.MARKDOWN
        )
    
    await asyncio.sleep(2)
    
    try:
        await msg.delete()
    except:
        pass
    
    if total > 7:
        run_data = get_tunnel_run(user_id)
        crumbs = run_data["crumbs_collected"]
        xp = run_data["xp_collected"]
        
        with sqlite3.connect(DB_FILE) as conn:
            c = conn.cursor()
            c.execute('DELETE FROM tunnel_run WHERE user_id = ?', (user_id,))
            conn.commit()
        
        add_crumbs(user_id, crumbs)
        add_xp(user_id, xp, context)
        add_tunnel_crumbs(user_id, crumbs)
        delete_battle_from_db(user_id)
        
        text = f"""🏃 *Побег удался!*

🎲 {dice1} + {dice2} = *{total}* > 7

_Ты ловко уворачиваешься и убегаешь в тень, унося с собой всё награбленное!_

▸ *Итоги:*
  🧀 Крошек добыто: {crumbs}
  ✨ Опыта получено: {xp}

_Отличная работа, искатель приключений!_"""
        
        keyboard = [[InlineKeyboardButton("🏠 В нору", callback_data="tunnel_menu")]]
        
        try:
            with open("/root/bot/images/dice_win.jpg", "rb") as photo:
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
    else:
        text = f"""😱 *Побег провален!*

🎲 {dice1} + {dice2} = *{total}* ≤ 7

_Ты спотыкаешься! Монстр настигает тебя!_

Придётся сражаться!"""
        
        keyboard = [[InlineKeyboardButton("⚔️ В бой", callback_data="tunnel_continue_battle")]]
        
        try:
            with open("/root/bot/images/dice_lose.jpg", "rb") as photo:
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
    
    await query.answer()


async def handle_tunnel_break_free(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик вырывания из ужа"""
    user_id = update.callback_query.from_user.id
    await process_player_attack(update, context, user_id, "break_free")


async def handle_tunnel_continue_battle(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Продолжение боя после неудачного побега"""
    query = update.callback_query
    user_id = query.from_user.id
    
    battle_state = context.user_data.get("tunnel_battle", {})
    monster_state = context.user_data.get("tunnel_monster_state", {})
    player_state = context.user_data.get("tunnel_player_state", {})
    
    if not battle_state:
        # 🔄 Пробуем восстановить из БД
        saved = load_battle_from_db(user_id)
        if saved:
            context.user_data["tunnel_battle"] = saved["battle_state"]
            context.user_data["tunnel_monster_state"] = saved["monster_state"]
            context.user_data["tunnel_player_state"] = saved["player_state"]
            context.user_data["tunnel_player_defense"] = saved["player_defense"]
            battle_state = saved["battle_state"]
            monster_state = saved["monster_state"]
            player_state = saved["player_state"]
            await query.answer("⚠️ Бой восстановлен из сохранения!", show_alert=True)
        else:
            await safe_edit_or_send(query, user_id, "❌ Бой не найден!", [], context)
            return
    
    monster = get_monster(battle_state["monster_id"])
    await show_defense_selection(update, context, user_id, monster, battle_state, monster_state, player_state)