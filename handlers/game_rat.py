import random
import asyncio
import re
from typing import Dict, Optional
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from telegram import constants
import logging
from handlers.inventory import add_crumbs, add_match_record
from handlers.titles import check_and_unlock_titles
from handlers.inventory import open_chest as open_chest_func, CHEST_IMAGES_OPEN
from handlers.items import ALL_ITEMS as ALL_ITEMS_DICT

logger = logging.getLogger(__name__)

import sys
sys.path.append('/root/bot')
from config import MIN_PLAYERS, MAX_PLAYERS, NIGHT_TIME, DAY_TIME, VOTE_TIME
from database import update_rating, delete_game_state
from handlers.inventory import (
    add_xp, update_stats, check_and_unlock_achievements, unlock_achievement,
    add_item, get_random_item, get_inventory, use_consumable, get_achievements,
    get_level, get_available_chests, open_chest as open_chest_func
)

from handlers.items import CONSUMABLES, ALL_ITEMS, CHESTS, EQUIPMENT_SLOTS

# 🆕 ИМПОРТЫ ЭФФЕКТОВ ПЕРЕНЕСЕНЫ ВВЕРХ (ПРАВИЛЬНО!)
from handlers.effects import (
    process_xp_modifiers, process_item_drop_chance, process_legendary_chance, has_gift_item,
    process_survive_chance, process_night_kill_effects, check_death_effects,
    get_disguise_until_kill, is_debuff_immune, get_wisdom_reveal,
    process_vote_effects, process_vote_count_modifiers, get_tie_breaker,
    get_justice_tie, is_vote_hidden, get_revenge_kill, has_unremovable_vote,
    get_ghost_vote, get_vote_visibility, process_kill_xp, apply_consumable_effect,
    get_night_avoid_chance, get_taunt_chance, has_repellent, is_vote_immune,
    get_vote_time_bonus, get_time_bonus, has_day_shot, is_shot_proof,
    has_anon_message, can_awaken, can_catapult, can_net_trap, can_trap_launch,
    has_reveal_role_ability, get_hear_rat
)

active_games: Dict[int, 'RatGame'] = {}

KILL_MESSAGES = [
    "🔪 Этой ночью крыса жестоко расправилась с {victim}. Мыши в ужасе!",
    "🩸 {victim} был найден мёртвым в своей постели. Следы крысиных лап ведут к окну.",
    "😱 Страшная новость! {victim} больше не с нами. Крыса не дремлет!",
    "💀 {victim} стал жертвой крысы. Кто следующий?",
    "🌙 Ночь унесла жизнь {victim}. Мыши скорбят.",
    "🔪 Крыса нанесла удар! {victim} пал от её лап.",
    "🕯️ Зажгите свечу за {victim}. Крыса охотится на нас.",
    "😢 Мы потеряли {victim}. Крыса где-то рядом...",
    "🗡️ Удар в спину! {victim} убит крысой.",
    "🌑 Тьма забрала {victim}. Берегитесь крысы!",
    "🦷 Острые зубы сомкнулись. {victim} не пережил эту ночь.",
    "🧀 Сыр был отравлен... {victim} умер в муках.",
    "🚪 Дверь была взломана. {victim} найден без признаков жизни.",
    "👁️ Крыса следила из тени. {victim} стал её жертвой.",
    "🩸 Кровь на полу. {victim} не проснётся.",
    "🌪️ Бесшумно, как ветер. {victim} убит во сне.",
    "🔮 Пророчество сбылось. {victim} пал этой ночью.",
    "⚰️ Ещё один гроб. {victim} присоединился к предкам.",
    "🥀 Цветы увяли. {victim} больше нет с нами.",
    "🕳️ Крыса утащила {victim} в нору. Никто не услышал крик."
]

EXECUTION_MESSAGES = [
    "⚖️ Народ решил! {player} казнён. Это была {role}.",
    "🪓 Топор палача опустился. {player} ({role}) мёртв.",
    "🔥 {player} сожжён на костре! Оказалось, это {role}.",
    "💀 {player} повешен. Мыши ликуют? Это была {role}.",
    "🗡️ {player} казнён без суда и следствия. Роль: {role}.",
    "⚰️ Прощай, {player}. Ты был {role}.",
    "🏹 Расстрелян! {player} оказался {role}.",
    "🪦 Ещё одна могила. {player} был {role}.",
    "🔪 Заколот толпой! {player} — {role}.",
    "💉 Яд оборвал жизнь {player}. Роль: {role}.",
    "🪤 Мышеловка захлопнулась! {player} ({role}) пойман и казнён.",
    "⚡ Молния правосудия поразила {player}. Это был {role}.",
    "🌊 Утоплен в сыре! {player} ({role}) не выплыл.",
    "🗿 Забросан камнями. {player} оказался {role}.",
    "🔔 Колокол пробил. {player} ({role}) уходит в небытие.",
    "📜 Приговор зачитан. {player} казнён. Роль: {role}.",
    "🕊️ Душа {player} покинула этот мир. Это был {role}.",
    "🧊 Заморожен и разбит! {player} ({role}) рассыпался на куски.",
    "🎭 Маска сброшена! {player} был {role} и поплатился.",
    "🏆 Правосудие свершилось! {player} ({role}) больше не угроза."
]

def escape_markdown(text: str) -> str:
    if not text:
        return ""
    escape_chars = r'_*[]()~`>#+-=|{}.!'
    return re.sub(f'([{re.escape(escape_chars)}])', r'\\\1', text)

class RatGame:
    def __init__(self, chat_id: int, creator_id: int, creator_name: str):
        self.chat_id = chat_id
        self.creator_id = creator_id
        self.players: Dict[int, dict] = {}
        self.phase = "lobby"
        self.votes: Dict[int, int] = {}
        self.night_kill: Optional[int] = None
        self.rat_id: Optional[int] = None
        self.winner: Optional[str] = None
        self.night_ended = False
        self.night_message_id: Optional[int] = None
        self.vote_message_ids: Dict[int, int] = {}
        self.killed_by_rat = []
        self.executed_players = []
        self.items_received: Dict[int, list] = {}
        self.achievements_unlocked: Dict[int, list] = {}
        self.level_ups: Dict[int, tuple] = {}
        
        # Эффекты экипировки и расходников
        self.kill_reveal_role = True
        self.kill_silenced = False
        self.kill_extra_victims = []
        self.delayed_kills = []
        self.skip_next_voting = False
        self.day_time_bonus = 0
        self.trap_set: Dict[int, bool] = {}
        self.perfect_trap_set: Dict[int, bool] = {}
        self.reflect_shield: Dict[int, bool] = {}
        self.night_invisible = []
        self.berserk_mode: Dict[int, bool] = {}
        self.double_kill_next: Dict[int, bool] = {}
        self.double_xp_players = []
        self.guaranteed_legendary = []
        self.dead_messages_allowed: Dict[int, int] = {}
        self.rat_distracted: Dict[int, bool] = {}
        self.extra_votes: Dict[int, int] = {}
        self.accuracy_penalty = 0
        self.fake_roles: Dict[int, str] = {}
        self.rebellion_buff = False
        self.max_luck_players = []
        self.rat_avoid_2: Dict[int, int] = {}
        self.rat_confused = False
        self.temp_survive_boost: Dict[int, int] = {}
        self.soulbound_pairs: Dict[int, int] = {}
        self.night_counter = 0
        self.pending_item_use: Dict[int, str] = {}  # user_id -> item_id для выбора цели
        
        self.add_player(creator_id, creator_name)
        
    def add_player(self, user_id: int, name: str) -> bool:
        if user_id in self.players:
            return False
        if len(self.players) >= MAX_PLAYERS:
            return False
        self.players[user_id] = {
            "name": name, 
            "role": None, 
            "alive": True,
            "shielded": False,
            "silenced": False,
            "poisoned": False,
            "catapulted": False,
        }
        return True
    
    def remove_player(self, user_id: int) -> bool:
        if user_id in self.players and user_id != self.creator_id:
            del self.players[user_id]
            if user_id == self.rat_id:
                self.rat_id = None
            return True
        return False
    
    def start_game(self) -> bool:
        if len(self.players) < MIN_PLAYERS:
            return False
        player_ids = list(self.players.keys())
        self.rat_id = random.choice(player_ids)
        for pid in player_ids:
            self.players[pid]["role"] = "🐀 КРЫСА" if pid == self.rat_id else "🐭 МЫШЬ"
        self.phase = "night"
        return True
    
    def get_alive_players(self) -> list:
        return [pid for pid, data in self.players.items() if data["alive"]]
    
    def get_alive_mice(self) -> list:
        return [pid for pid, data in self.players.items() if data["alive"] and pid != self.rat_id]
    
    def check_game_over(self) -> Optional[str]:
        alive = self.get_alive_players()
        rat_alive = self.rat_id in alive
        mice_alive = [p for p in alive if p != self.rat_id]
        if not rat_alive:
            self.winner = "mice"
            return "mice_win"
        if len(mice_alive) == 0:
            self.winner = "rat"
            return "rat_win"
        return None
    
    def update_all_ratings(self):
        rat_won = (self.winner == "rat")
        mice_won = (self.winner == "mice")
        self.level_ups = {}
        
        for pid, data in self.players.items():
            role = data["role"]
            won = rat_won if "КРЫСА" in role else mice_won
            
            # Записываем в историю матчей
            role_type = "rat" if "КРЫСА" in role else "mouse"
            kills = len(self.killed_by_rat) if pid == self.rat_id else 0
            add_match_record(pid, role_type, won, kills)
            
            # Опыт с учётом эффектов
            base_xp = 10
            modified_xp = process_xp_modifiers(pid, base_xp, won)
            
            # Двойной опыт
            if pid in self.double_xp_players:
                modified_xp *= 2
                self.double_xp_players.remove(pid)
            
            level_up, new_level, old_level = add_xp(pid, modified_xp)
            if level_up:
                self.level_ups[pid] = (new_level, old_level)
            
            if won:
                base_win_xp = 50
                modified_win_xp = process_xp_modifiers(pid, base_win_xp, True)
                level_up_win, new_level_win, old_level_win = add_xp(pid, modified_win_xp)
                if level_up_win and not level_up:
                    self.level_ups[pid] = (new_level_win, old_level_win)
            
            # КРОШКИ (БАЗА + БОНУС ЗА УРОВЕНЬ)
            player_level = get_level(pid)
            
            if won:
                base_crumbs = random.randint(300, 600)
                level_bonus = player_level * 20
            else:
                base_crumbs = random.randint(60, 150)
                level_bonus = player_level * 6
            
            crumbs_earned = base_crumbs + level_bonus
            add_crumbs(pid, crumbs_earned)
            
            update_rating(pid, data["name"], role, won)
            update_stats(
                pid,
                total_games=1,
                total_wins=1 if won else 0,
                rat_wins=1 if won and "КРЫСА" in role else 0,
                mouse_wins=1 if won and "МЫШЬ" in role else 0,
            )
            
            # Предметы
            items_received = []
            if won:
                # Гарантированный легендарный
                guaranteed = pid in self.guaranteed_legendary
                if guaranteed:
                    self.guaranteed_legendary.remove(pid)
                
                # Шанс на сундук
                if random.randint(1, 100) <= 20:
                    chest_rarity = random.choices(
                        ["common", "rare", "epic", "legendary", "mythic"],
                        weights=[50, 30, 12, 6, 2]
                    )[0]
                    chest_id = f"{chest_rarity}_chest"
                    if chest_id in CHESTS:
                        add_item(pid, chest_id)
                        items_received.append(chest_id)
                
                # Обычная выдача
                role_key = "rat" if "КРЫСА" in role else "mouse"
                
                item_find_bonus = process_item_drop_chance(pid, 0)
                legendary_bonus = process_legendary_chance(pid, 0)
                
                if guaranteed:
                    legendary_bonus = 100
                
                item1 = get_random_item(role_key)
                if item1:
                    add_item(pid, item1)
                    items_received.append(item1)
                
                if random.randint(1, 100) <= 40 + item_find_bonus:
                    item2 = get_random_item(role_key)
                    if item2:
                        add_item(pid, item2)
                        items_received.append(item2)
                    
                    if random.randint(1, 100) <= 15 + item_find_bonus:
                        item3 = get_random_item(role_key)
                        if item3:
                            add_item(pid, item3)
                            items_received.append(item3)
                
                # Подарок от шапки Санты
                if has_gift_item(pid):
                    gift_item = get_random_item("all")
                    if gift_item:
                        add_item(pid, gift_item)
                        items_received.append(gift_item)
            
            self.items_received[pid] = items_received
            
            # Достижения
            old_achievements = get_achievements(pid)
            check_and_unlock_achievements(pid)
            new_achievements = get_achievements(pid)
            
            newly_unlocked = []
            for ach in new_achievements:
                if ach.get('unlocked') and ach not in old_achievements:
                    newly_unlocked.append(ach)
            self.achievements_unlocked[pid] = newly_unlocked
            
            # 🆕 ПРОВЕРЯЕМ И РАЗБЛОКИРУЕМ ТИТУЛЫ ПОСЛЕ ИГРЫ
            check_and_unlock_titles(pid)
    
    def _get_mvp(self) -> Optional[int]:
        if self.winner == "rat" and self.rat_id:
            return self.rat_id
        alive_mice = self.get_alive_mice()
        if alive_mice:
            return alive_mice[0]
        return None


# ========== КОМАНДЫ ==========

async def rat_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    user_id = update.effective_user.id
    user_name = update.effective_user.full_name
    
    if chat_id in active_games:
        await update.message.reply_text("❌ Игра уже идёт в этом чате!")
        return
    
    game = RatGame(chat_id, user_id, user_name)
    active_games[chat_id] = game
    
    keyboard = [
        [InlineKeyboardButton("✅ Присоединиться", callback_data="rat_lobby_join"),
         InlineKeyboardButton("👋 Выйти", callback_data="rat_lobby_leave")],
        [InlineKeyboardButton("🎮 Начать игру", callback_data="rat_lobby_start")]
    ]
    
    # ФОРМИРУЕМ СПИСОК ИГРОКОВ
    players_list = ""
    for i, (pid, data) in enumerate(game.players.items(), 1):
        crown = "👑 " if pid == game.creator_id else ""
        players_list += f"\n{i}. {crown}{escape_markdown(data['name'])}"
    
    caption = f"""🐀 *РАТЛЯНДИЯ v0.0.3*

👥 *ИГРОКИ ({len(game.players)}/{MAX_PLAYERS}):*{players_list}

Нажмите кнопку чтобы присоединиться!"""
    
    try:
        with open("/root/bot/images/lobby.jpg", "rb") as photo:
            await update.message.reply_photo(
                photo=photo,
                caption=caption,
                parse_mode=constants.ParseMode.MARKDOWN,
                reply_markup=InlineKeyboardMarkup(keyboard)
            )
    except:
        await update.message.reply_text(
            caption,
            parse_mode=constants.ParseMode.MARKDOWN,
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
    
    # СООБЩЕНИЕ СОЗДАТЕЛЮ В ЛИЧКУ
    try:
        await context.bot.send_message(
            chat_id=user_id,
            text=f"✅ *Игра создана!*\n\n"
                 f"👥 Игроков: 1/{MAX_PLAYERS}\n"
                 f"⏳ Через 30 секунд будет отправлен созыв в группу.\n\n"
                 f"Нажми «Начать игру» когда соберётся достаточно игроков!",
            parse_mode=constants.ParseMode.MARKDOWN
        )
    except:
        pass
    
    # СОЗЫВ С ФОТО, КНОПКОЙ, АВТОУДАЛЕНИЕМ И УВЕДОМЛЕНИЯМИ В ЛИЧКУ
    async def send_lobby_reminder():
        await asyncio.sleep(30)
        if chat_id in active_games:
            game = active_games[chat_id]
            if game.phase == "lobby" and len(game.players) < MIN_PLAYERS:
                # Формируем текст созыва
                mention_text = f"🎲 *СОЗЫВ В ЛОББИ!*\n\n"
                mention_text += f"👤 {escape_markdown(user_name)} создал игру и ждёт игроков!\n"
                mention_text += f"👥 Сейчас в лобби: {len(game.players)}/{MAX_PLAYERS}\n"
                mention_text += f"❓ Нужно ещё *{MIN_PLAYERS - len(game.players)}* игроков\n\n"
                
                # Список кто уже в игре
                if len(game.players) > 0:
                    mention_text += "*Уже в игре:*\n"
                    for pid, data in game.players.items():
                        crown = "👑 " if pid == game.creator_id else ""
                        mention_text += f"  • {crown}{escape_markdown(data['name'])}\n"
                
                # КНОПКА ПРИСОЕДИНИТЬСЯ В САМОМ СОЗЫВЕ
                join_keyboard = InlineKeyboardMarkup([
                    [InlineKeyboardButton("✅ Присоединиться к игре", callback_data="rat_lobby_join")]
                ])
                
                # Отправляем фото с созывом в группу
                try:
                    with open("/root/bot/images/lobby_call.jpg", "rb") as photo:
                        msg = await context.bot.send_photo(
                            chat_id=chat_id,
                            photo=photo,
                            caption=mention_text,
                            parse_mode=constants.ParseMode.MARKDOWN,
                            reply_markup=join_keyboard
                        )
                        
                        # Удаляем через 60 секунд
                        async def delete_later():
                            await asyncio.sleep(60)
                            try:
                                await msg.delete()
                            except:
                                pass
                        
                        asyncio.create_task(delete_later())
                        
                except Exception as e:
                    logger.error(f"Ошибка отправки фото созыва: {e}")
                    # Fallback на текст с кнопкой
                    msg = await context.bot.send_message(
                        chat_id=chat_id,
                        text=mention_text,
                        parse_mode=constants.ParseMode.MARKDOWN,
                        reply_markup=join_keyboard
                    )
                    
                    async def delete_later():
                        await asyncio.sleep(60)
                        try:
                            await msg.delete()
                        except:
                            pass
                    
                    asyncio.create_task(delete_later())
                
                # ОТПРАВЛЯЕМ УВЕДОМЛЕНИЯ В ЛИЧКУ ВСЕМ КТО УЖЕ В ЛОББИ
                for pid in game.players.keys():
                    if pid != user_id:  # Создателю не отправляем (он уже получил)
                        try:
                            await context.bot.send_message(
                                chat_id=pid,
                                text=f"🎲 *СОЗЫВ В ЛОББИ!*\n\n"
                                     f"👤 {escape_markdown(user_name)} ждёт игроков в группе!\n"
                                     f"👥 Сейчас в лобби: {len(game.players)}/{MAX_PLAYERS}\n"
                                     f"❓ Нужно ещё *{MIN_PLAYERS - len(game.players)}* игроков",
                                parse_mode=constants.ParseMode.MARKDOWN
                            )
                        except:
                            pass
    
    # Запускаем таймер
    asyncio.create_task(send_lobby_reminder())

async def rat_stop(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    if chat_id in active_games:
        del active_games[chat_id]
        delete_game_state(chat_id)
        await update.message.reply_text("🛑 Игра остановлена.")
    else:
        await update.message.reply_text("❌ Нет активной игры.")

async def rat_rules(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = (
        f"🐀 РАТЛЯНДИЯ — ПОЛНОЕ РУКОВОДСТВО\n\n"
        f"🎭 РОЛИ ИГРОКОВ ({MIN_PLAYERS}-{MAX_PLAYERS} человек):\n"
        f"• Мыши — мирные жители. Их цель: найти и казнить Крысу днём на голосовании.\n"
        f"• Крыса (всегда одна) — тайный убийца. Каждую ночь выбирает одну жертву среди Мышей.\n\n"
        f"🌙 ФАЗЫ ИГРЫ:\n"
        f"1. Ночь ({NIGHT_TIME} сек) — Крыса выбирает жертву в личных сообщениях. Мыши спят.\n"
        f"2. Утро — объявляется результат ночи (кто убит или ночь прошла спокойно).\n"
        f"3. День ({DAY_TIME} сек) — все живые игроки обсуждают произошедшее в общем чате.\n"
        f"4. Голосование ({VOTE_TIME} сек) — каждый живой игрок голосует в личных сообщениях.\n"
        f"5. Казнь — игрок, набравший большинство голосов, выбывает.\n\n"
        f"🏆 УСЛОВИЯ ПОБЕДЫ:\n"
        f"• Мыши побеждают, если Крыса казнена.\n"
        f"• Крыса побеждает, если количество Мышей = количеству Крыс.\n\n"
        f"Удачной охоты в Ратляндии!"
    )
    
    keyboard = [[InlineKeyboardButton("🔙 В город", callback_data="city_menu")]]
    
    if update.callback_query:
        query = update.callback_query
        user_id = query.from_user.id
        await query.message.delete()
        try:
            with open("/root/bot/images/rules.jpg", "rb") as photo:
                await context.bot.send_photo(
                    chat_id=user_id,
                    photo=photo,
                    caption=text,
                    reply_markup=InlineKeyboardMarkup(keyboard)
                )
        except:
            await context.bot.send_message(
                chat_id=user_id,
                text=text,
                reply_markup=InlineKeyboardMarkup(keyboard)
            )
    else:
        try:
            with open("/root/bot/images/rules.jpg", "rb") as photo:
                await update.message.reply_photo(photo=photo, caption=text)
        except:
            await update.message.reply_text(text)


# ========== ФАЗЫ ИГРЫ ==========

async def night_phase(context: ContextTypes.DEFAULT_TYPE, chat_id: int):
    game = active_games.get(chat_id)
    if not game or game.phase == "ended":
        return
    
    game.phase = "night"
    game.night_kill = None
    game.night_ended = False
    game.night_message_id = None
    game.night_counter += 1
    
    # Сбрасываем эффекты дня
    for pid in game.players:
        game.players[pid]["catapulted"] = False
    
    try:
        with open("/root/bot/images/night.jpg", "rb") as photo:
            await context.bot.send_photo(
                chat_id=chat_id,
                photo=photo,
                caption=f"🌙 *НОЧЬ {game.night_counter}.* Крыса выбирает жертву... ({NIGHT_TIME} сек)",
                parse_mode=constants.ParseMode.MARKDOWN
            )
    except:
        await context.bot.send_message(chat_id, f"🌙 *НОЧЬ {game.night_counter}.* Крыса выбирает жертву... ({NIGHT_TIME} сек)", parse_mode=constants.ParseMode.MARKDOWN)
    
    # 🆕 Шпионский наушник - показываем выбор Крысы мышам с этой способностью
    if game.rat_id and game.players[game.rat_id]["alive"]:
        for pid in game.get_alive_mice():
            if get_hear_rat(pid):
                await context.bot.send_message(
                    pid,
                    "🎧 *ШПИОНСКИЙ НАУШНИК АКТИВЕН!* Ты увидишь выбор Крысы...",
                    parse_mode=constants.ParseMode.MARKDOWN
                )
    
    if game.rat_id and game.players[game.rat_id]["alive"]:
        alive_mice = game.get_alive_mice()
        
        targetable_mice = []
        taunted_mice = []
        
        for pid in alive_mice:
            if pid in game.night_invisible:
                continue
            
            avoid_chance = get_night_avoid_chance(pid)
            
            if has_repellent(pid):
                avoid_chance = 100
            
            if avoid_chance > 0 and random.randint(1, 100) <= avoid_chance:
                continue
            
            if game.rat_confused and random.randint(1, 100) <= 5:
                continue
            
            targetable_mice.append(pid)
            
            taunt_chance = get_taunt_chance(pid)
            if taunt_chance > 0 and random.randint(1, 100) <= taunt_chance:
                taunted_mice.append(pid)
        
        for pid, distracted in game.rat_distracted.items():
            if distracted and pid in targetable_mice:
                targetable_mice.remove(pid)
                game.rat_distracted[pid] = False
        
        if taunted_mice and random.randint(1, 100) <= 70:
            game.night_kill = random.choice(taunted_mice)
            game.night_ended = True
        
        if not game.night_ended and targetable_mice:
            keyboard = []
            for pid in targetable_mice:
                name = escape_markdown(game.players[pid]["name"])
                keyboard.append([InlineKeyboardButton(f"🔪 {name}", callback_data=f"rat_kill_{pid}")])
            keyboard.append([InlineKeyboardButton("😇 Никого", callback_data="rat_kill_none")])
            keyboard.append([InlineKeyboardButton("🎒 Использовать предмет", callback_data="use_item_menu")])
            
            # 🆕 Кнопка выстрела из арбалета для Мышей
            if has_day_shot(game.rat_id):
                keyboard.append([InlineKeyboardButton("🏹 Выстрелить из арбалета", callback_data="day_shot_menu")])
            
            try:
                with open("/root/bot/images/rat_choose.jpg", "rb") as photo:
                    msg = await context.bot.send_photo(
                        chat_id=game.rat_id,
                        photo=photo,
                        caption="🌙 *Выбери жертву:*",
                        parse_mode=constants.ParseMode.MARKDOWN,
                        reply_markup=InlineKeyboardMarkup(keyboard)
                    )
                    game.night_message_id = msg.message_id
            except:
                msg = await context.bot.send_message(
                    game.rat_id, f"🌙 *Выбери жертву:*",
                    parse_mode=constants.ParseMode.MARKDOWN, reply_markup=InlineKeyboardMarkup(keyboard)
                )
                game.night_message_id = msg.message_id
        else:
            game.night_ended = True
    else:
        game.night_ended = True
    
    await asyncio.sleep(NIGHT_TIME)
    
    if game.night_message_id and game.rat_id:
        try:
            await context.bot.edit_message_reply_markup(chat_id=game.rat_id, message_id=game.night_message_id)
        except:
            pass
    
    await morning_phase(context, chat_id)

async def morning_phase(context: ContextTypes.DEFAULT_TYPE, chat_id: int):
    game = active_games.get(chat_id)
    if not game or game.phase == "ended":
        return
    
    # Мудрость тюрбана
    if game.night_counter >= 3:
        for pid in game.get_alive_mice():
            if get_wisdom_reveal(pid) and game.rat_id:
                await context.bot.send_message(
                    pid,
                    f"🧠 *МУДРОСТЬ ВЕКОВ!* Ты узнал что Крыса — {escape_markdown(game.players[game.rat_id]['name'])}!",
                    parse_mode=constants.ParseMode.MARKDOWN
                )
    
    if game.night_kill and game.night_kill in game.players:
        # Проверяем идеальную крысоловку
        if game.night_kill in game.perfect_trap_set and game.perfect_trap_set[game.night_kill]:
            if game.rat_id and game.players[game.rat_id]["alive"]:
                game.players[game.rat_id]["alive"] = False
                await context.bot.send_message(
                    chat_id,
                    f"☀️ *УТРО.* 🪤✨ ИДЕАЛЬНАЯ ЛОВУШКА! Крыса попалась у {escape_markdown(game.players[game.night_kill]['name'])} и мертва!",
                    parse_mode=constants.ParseMode.MARKDOWN
                )
                result = game.check_game_over()
                if result:
                    await end_game(context, chat_id, result)
                    return
                game.night_kill = None
        
        # Проверяем отражение атаки
        elif game.night_kill in game.reflect_shield and game.reflect_shield[game.night_kill]:
            game.reflect_shield[game.night_kill] = False
            if game.rat_id and game.players[game.rat_id]["alive"]:
                game.players[game.rat_id]["alive"] = False
                await context.bot.send_message(
                    chat_id,
                    f"☀️ *УТРО.* 🪞 {escape_markdown(game.players[game.night_kill]['name'])} отразил атаку! Крыса мертва!",
                    parse_mode=constants.ParseMode.MARKDOWN
                )
                result = game.check_game_over()
                if result:
                    await end_game(context, chat_id, result)
                    return
                game.night_kill = None
        
        # Проверяем обычную крысоловку
        elif game.night_kill in game.trap_set and game.trap_set[game.night_kill]:
            game.trap_set[game.night_kill] = False
            if game.rat_id and game.players[game.rat_id]["alive"]:
                game.players[game.rat_id]["alive"] = False
                await context.bot.send_message(
                    chat_id,
                    f"☀️ *УТРО.* 🪤 Крыса попалась в крысоловку у {escape_markdown(game.players[game.night_kill]['name'])}! Крыса мертва!",
                    parse_mode=constants.ParseMode.MARKDOWN
                )
                result = game.check_game_over()
                if result:
                    await end_game(context, chat_id, result)
                    return
                game.night_kill = None
        
        # Проверяем выживание
        elif process_survive_chance(game, game.night_kill):
            game.players[game.night_kill]["shielded"] = False
            await context.bot.send_message(
                chat_id,
                f"☀️ *УТРО.* 🛡️ {escape_markdown(game.players[game.night_kill]['name'])} чудом выжил этой ночью!",
                parse_mode=constants.ParseMode.MARKDOWN
            )
            game.night_kill = None
        
        else:
            if not game.players[game.night_kill].get("shielded", False):
                # Применяем эффекты убийства
                if game.rat_id:
                    reveal_role, silenced, extra_victims = process_night_kill_effects(game, game.rat_id, game.night_kill)
                    game.kill_reveal_role = reveal_role
                    game.kill_silenced = silenced
                    game.kill_extra_victims = extra_victims
                    
                    if get_disguise_until_kill(game.rat_id):
                        game.kill_reveal_role = False
                
                if is_debuff_immune(game.night_kill):
                    game.kill_silenced = False
                
                game.players[game.night_kill]["alive"] = False
                game.players[game.night_kill]["silenced"] = game.kill_silenced
                victim_name = escape_markdown(game.players[game.night_kill]["name"])
                
                if game.night_kill in game.fake_roles:
                    victim_role = game.fake_roles[game.night_kill]
                else:
                    victim_role = game.players[game.night_kill]["role"] if game.kill_reveal_role else "???"
                
                if game.rat_id:
                    update_stats(game.rat_id, total_kills=1)
                    game.killed_by_rat.append(game.night_kill)
                    unlock_achievement(game.rat_id, "night_hunter")
                    
                    kill_xp = process_kill_xp(game.rat_id)
                    if kill_xp > 0:
                        add_xp(game.rat_id, kill_xp)
                
                kill_msg = random.choice(KILL_MESSAGES).replace("{victim}", victim_name)
                
                kill_photos = [
                    "/root/bot/images/rat_kill.jpg",
                    "/root/bot/images/rat_kill_2.jpg",
                    "/root/bot/images/rat_kill_3.jpg",
                    "/root/bot/images/rat_kill_4.jpg"
                ]
                selected_photo = random.choice(kill_photos)
                
                try:
                    with open(selected_photo, "rb") as photo:
                        await context.bot.send_photo(
                            chat_id=chat_id,
                            photo=photo,
                            caption=kill_msg
                        )
                except Exception as e:
                    logger.error(f"Ошибка отправки фото убийства: {e}")
                    await context.bot.send_message(chat_id, kill_msg)
                
                await context.bot.send_message(
                    chat_id,
                    f"☀️ *УТРО.* Убита *{victim_name}* ({victim_role}).",
                    parse_mode=constants.ParseMode.MARKDOWN
                )
                
                # 🆕 Шпионский наушник - сообщаем мышам кто был целью
                for pid in game.get_alive_mice():
                    if get_hear_rat(pid):
                        await context.bot.send_message(
                            pid,
                            f"🎧 *КРЫСА ВЫБРАЛА ЦЕЛЬЮ:* {victim_name}",
                            parse_mode=constants.ParseMode.MARKDOWN
                        )
                
                # Дополнительные жертвы
                for extra in game.kill_extra_victims:
                    if extra == "random":
                        alive_mice = game.get_alive_mice()
                        if alive_mice:
                            extra_victim = random.choice(alive_mice)
                            game.players[extra_victim]["alive"] = False
                            await context.bot.send_message(
                                chat_id,
                                f"💀 *ДОПОЛНИТЕЛЬНАЯ ЖЕРТВА!* {escape_markdown(game.players[extra_victim]['name'])} тоже мёртв.",
                                parse_mode=constants.ParseMode.MARKDOWN
                            )
                
                # Эффекты при смерти жертвы
                death_effects = check_death_effects(game, game.night_kill, victim_role)
                if death_effects.get("reveal_rat") and game.rat_id:
                    await context.bot.send_message(
                        chat_id,
                        f"⚡ *{escape_markdown(game.players[game.night_kill]['name'])} раскрыл правду! Крыса — {escape_markdown(game.players[game.rat_id]['name'])}!*",
                        parse_mode=constants.ParseMode.MARKDOWN
                    )
                
                if death_effects.get("kill_target") and game.rat_id:
                    game.players[game.rat_id]["alive"] = False
                    await context.bot.send_message(
                        chat_id,
                        f"👿 *ПОСЛЕДНЯЯ МЕСТЬ!* {escape_markdown(game.players[game.night_kill]['name'])} забрал Крысу с собой!",
                        parse_mode=constants.ParseMode.MARKDOWN
                    )
                
                # Связанные души
                if game.night_kill in game.soulbound_pairs:
                    bound_id = game.soulbound_pairs[game.night_kill]
                    if bound_id in game.players and game.players[bound_id]["alive"]:
                        game.players[bound_id]["alive"] = False
                        await context.bot.send_message(
                            chat_id,
                            f"💔 *СВЯЗАННЫЕ ДУШИ!* {escape_markdown(game.players[bound_id]['name'])} умер от разрыва связи!",
                            parse_mode=constants.ParseMode.MARKDOWN
                        )
            else:
                game.players[game.night_kill]["shielded"] = False
                await context.bot.send_message(
                    chat_id,
                    f"☀️ *УТРО.* 🛡️ Щит веры спас {escape_markdown(game.players[game.night_kill]['name'])}!",
                    parse_mode=constants.ParseMode.MARKDOWN
                )
    else:
        await context.bot.send_message(chat_id, "☀️ *УТРО.* Ночь прошла спокойно.", parse_mode=constants.ParseMode.MARKDOWN)
    
    # Обрабатываем отложенные убийства
    if hasattr(game, 'delayed_kills') and game.delayed_kills:
        for victim_id in list(game.delayed_kills):
            if victim_id in game.players and game.players[victim_id]["alive"]:
                game.players[victim_id]["alive"] = False
                await context.bot.send_message(
                    chat_id,
                    f"⏳ *ЯД ПОДЕЙСТВОВАЛ!* {escape_markdown(game.players[victim_id]['name'])} умер от отравления.",
                    parse_mode=constants.ParseMode.MARKDOWN
                )
        game.delayed_kills = []
    
    # Сбрасываем флаги эффектов
    game.kill_reveal_role = True
    game.kill_silenced = False
    game.kill_extra_victims = []
    game.night_invisible = []
    game.accuracy_penalty = 0
    game.rebellion_buff = False
    game.rat_confused = False
    
    # Очищаем фальшивые роли мёртвых
    for pid in list(game.fake_roles.keys()):
        if pid in game.players and not game.players[pid]["alive"]:
            del game.fake_roles[pid]
    
    if game.rat_id and game.rat_id in game.double_kill_next:
        game.double_kill_next[game.rat_id] = False
    
    result = game.check_game_over()
    if result:
        await end_game(context, chat_id, result)
        return
    
    game.phase = "day"
    
    day_time = DAY_TIME + game.day_time_bonus
    try:
        with open("/root/bot/images/day.jpg", "rb") as photo:
            await context.bot.send_photo(
                chat_id=chat_id,
                photo=photo,
                caption=f"💬 *ДЕНЬ.* Обсуждение. Живых: {len(game.get_alive_players())} ({day_time} сек)",
                parse_mode=constants.ParseMode.MARKDOWN
            )
    except:
        await context.bot.send_message(chat_id, f"💬 *ДЕНЬ.* Обсуждение. Живых: {len(game.get_alive_players())} ({day_time} сек)", parse_mode=constants.ParseMode.MARKDOWN)
    
    for pid in game.get_alive_players():
        if not game.players[pid].get("catapulted", False):
            try:
                keyboard = [[InlineKeyboardButton("🎒 Использовать предмет", callback_data="use_item_menu")]]
                
                # 🆕 Кнопки для особых способностей
                if has_day_shot(pid):
                    keyboard.append([InlineKeyboardButton("🏹 Выстрелить из арбалета", callback_data="day_shot_menu")])
                if has_anon_message(pid):
                    keyboard.append([InlineKeyboardButton("📜 Анонимное сообщение", callback_data="anon_message")])
                if has_reveal_role_ability(pid):
                    keyboard.append([InlineKeyboardButton("🔮 Узнать роль", callback_data="reveal_role_menu")])
                if can_awaken(pid):
                    keyboard.append([InlineKeyboardButton("🔔 Разбудить", callback_data="awaken_menu")])
                if can_catapult(pid):
                    keyboard.append([InlineKeyboardButton("🏗️ Катапульта", callback_data="catapult_menu")])
                if can_net_trap(pid):
                    keyboard.append([InlineKeyboardButton("🥅 Сеткомёт", callback_data="net_trap_menu")])
                if can_trap_launch(pid):
                    keyboard.append([InlineKeyboardButton("🪤 Запустить ловушку", callback_data="trap_launch_menu")])
                
                await context.bot.send_message(
                    pid, "🎒 *Хочешь использовать предмет или способность?*",
                    parse_mode=constants.ParseMode.MARKDOWN,
                    reply_markup=InlineKeyboardMarkup(keyboard)
                )
            except:
                pass
    
    # 🆕 Предлагаем мёртвым отправить сообщение
    for pid in game.players:
        if not game.players[pid]["alive"] and pid in game.dead_messages_allowed and game.dead_messages_allowed[pid] > 0:
            try:
                await context.bot.send_message(
                    pid,
                    f"📜 *У тебя есть {game.dead_messages_allowed[pid]} сообщение после смерти!*",
                    parse_mode=constants.ParseMode.MARKDOWN,
                    reply_markup=InlineKeyboardMarkup([[
                        InlineKeyboardButton("📜 Отправить сообщение живым", callback_data="dead_message")
                    ]])
                )
            except:
                pass
    
    await asyncio.sleep(day_time)
    
    if game.phase == "ended":
        return
    
    if game.skip_next_voting:
        game.skip_next_voting = False
        await context.bot.send_message(chat_id, "💨 Голосование отменено! Переходим к ночи.")
        await night_phase(context, chat_id)
        return
    
    await voting_phase(context, chat_id)

async def voting_phase(context: ContextTypes.DEFAULT_TYPE, chat_id: int):
    game = active_games.get(chat_id)
    if not game or game.phase == "ended":
        return
    
    game.phase = "voting"
    game.votes = {}
    game.vote_message_ids = {}
    alive = game.get_alive_players()
    
    if len(alive) <= 1:
        result = game.check_game_over()
        if result:
            await end_game(context, chat_id, result)
        return
    
    try:
        with open("/root/bot/images/voting.jpg", "rb") as photo:
            await context.bot.send_photo(
                chat_id=chat_id,
                photo=photo,
                caption=f"🗳️ *ГОЛОСОВАНИЕ.* Голосуйте в ЛС ({VOTE_TIME} сек)",
                parse_mode=constants.ParseMode.MARKDOWN
            )
    except:
        await context.bot.send_message(chat_id, f"🗳️ *ГОЛОСОВАНИЕ.* Голосуйте в ЛС ({VOTE_TIME} сек)", parse_mode=constants.ParseMode.MARKDOWN)
    
    for pid in alive:
        if game.players[pid].get("silenced", False) or game.players[pid].get("catapulted", False):
            continue
        keyboard = []
        for target_id in alive:
            if target_id != pid:
                if is_vote_immune(target_id):
                    continue
                name = escape_markdown(game.players[target_id]["name"])
                keyboard.append([InlineKeyboardButton(f"⚖️ {name}", callback_data=f"rat_vote_{target_id}")])
        keyboard.append([InlineKeyboardButton("⏭ Пропустить", callback_data="rat_vote_skip")])
        keyboard.append([InlineKeyboardButton("🎒 Использовать предмет", callback_data="use_item_menu")])
        try:
            msg = await context.bot.send_message(pid, f"🗳️ *За кого голосуешь?*", parse_mode=constants.ParseMode.MARKDOWN, reply_markup=InlineKeyboardMarkup(keyboard))
            game.vote_message_ids[pid] = msg.message_id
        except:
            pass
    
    # 🆕 Голоса призраков
    for pid in game.players:
        if not game.players[pid]["alive"] and get_ghost_vote(pid):
            try:
                keyboard = []
                for target_id in alive:
                    name = escape_markdown(game.players[target_id]["name"])
                    keyboard.append([InlineKeyboardButton(f"👻 {name}", callback_data=f"ghost_vote_{target_id}")])
                await context.bot.send_message(
                    pid, "👻 *Твой призрачный голос!*",
                    parse_mode=constants.ParseMode.MARKDOWN,
                    reply_markup=InlineKeyboardMarkup(keyboard)
                )
            except:
                pass
    
    vote_time = VOTE_TIME
    for pid in alive:
        vote_time += get_vote_time_bonus(pid)
        vote_time += get_time_bonus(pid)
    
    await asyncio.sleep(max(VOTE_TIME, vote_time))
    
    for pid, msg_id in game.vote_message_ids.items():
        try:
            await context.bot.edit_message_reply_markup(chat_id=pid, message_id=msg_id)
        except:
            pass
    
    if game.phase == "ended":
        return
    
    for pid in game.votes.keys():
        update_stats(pid, total_votes=1)
    
    await execution_phase(context, chat_id)

async def execution_phase(context: ContextTypes.DEFAULT_TYPE, chat_id: int):
    game = active_games.get(chat_id)
    if not game or game.phase == "ended":
        return
    
    vote_count = {}
    
    for voter_id, target_id in game.votes.items():
        if target_id:
            weight = process_vote_effects(game, voter_id)
            
            if not game.players[voter_id]["alive"] and not get_ghost_vote(voter_id):
                continue
            
            vote_count[target_id] = vote_count.get(target_id, 0) + weight
    
    for target_id in list(vote_count.keys()):
        modifier = process_vote_count_modifiers(game, target_id)
        vote_count[target_id] = max(0, vote_count[target_id] + modifier)
    
    if not vote_count:
        await context.bot.send_message(chat_id, "🤷 Никто не набрал голосов. Переходим к ночи.")
        await night_phase(context, chat_id)
        return
    
    max_votes = max(vote_count.values())
    candidates = [pid for pid, votes in vote_count.items() if votes == max_votes]
    
    executed_id = None
    if len(candidates) > 1:
        for voter_id in game.votes.keys():
            if get_tie_breaker(voter_id) and game.votes[voter_id] in candidates:
                executed_id = game.votes[voter_id]
                break
        
        if not executed_id:
            for voter_id in game.votes.keys():
                if get_justice_tie(voter_id) and game.rat_id in candidates:
                    executed_id = game.rat_id
                    break
        
        if not executed_id:
            executed_id = random.choice(candidates)
    else:
        executed_id = candidates[0]
    
    executed_name = escape_markdown(game.players[executed_id]["name"])
    
    if executed_id in game.fake_roles:
        executed_role = game.fake_roles[executed_id]
    else:
        executed_role = game.players[executed_id]["role"]
    
    votes = vote_count[executed_id]
    
    game.players[executed_id]["alive"] = False
    game.executed_players.append(executed_id)
    
    revenge_voters = []
    for voter_id, target_id in game.votes.items():
        if target_id == executed_id:
            revenge_voters.append(voter_id)
            if executed_id == game.rat_id:
                update_stats(voter_id, guessed_rat_streak=1)
                unlock_achievement(voter_id, "eagle_eye")
    
    if get_revenge_kill(executed_id) and revenge_voters:
        first_voter = revenge_voters[0]
        if first_voter in game.players and game.players[first_voter]["alive"]:
            game.players[first_voter]["alive"] = False
            await context.bot.send_message(
                chat_id,
                f"🪃 *МЕСТЬ!* {escape_markdown(game.players[executed_id]['name'])} забрал с собой {escape_markdown(game.players[first_voter]['name'])}!",
                parse_mode=constants.ParseMode.MARKDOWN
            )
    
    exec_msg = random.choice(EXECUTION_MESSAGES).replace("{player}", executed_name).replace("{role}", executed_role)
    await context.bot.send_message(chat_id, exec_msg)
    
    for pid in game.get_alive_players():
        if get_vote_visibility(pid):
            vote_details = f"▸ 🗳️ *ГОЛОСА ПРОТИВ {executed_name}:* {votes}\n"
            await context.bot.send_message(pid, vote_details, parse_mode=constants.ParseMode.MARKDOWN)
    
    await context.bot.send_message(
        chat_id,
        f"⚖️ *КАЗНЬ!* {executed_name} ({executed_role}) получил {votes} голосов.",
        parse_mode=constants.ParseMode.MARKDOWN
    )
    
    if executed_id in game.soulbound_pairs:
        bound_id = game.soulbound_pairs[executed_id]
        if bound_id in game.players and game.players[bound_id]["alive"]:
            game.players[bound_id]["alive"] = False
            await context.bot.send_message(
                chat_id,
                f"💔 *СВЯЗАННЫЕ ДУШИ!* {escape_markdown(game.players[bound_id]['name'])} казнён вместе с {executed_name}!",
                parse_mode=constants.ParseMode.MARKDOWN
            )
    
    result = game.check_game_over()
    if result:
        await end_game(context, chat_id, result)
        return
    
    await night_phase(context, chat_id)

async def end_game(context: ContextTypes.DEFAULT_TYPE, chat_id: int, result: str):
    game = active_games.get(chat_id)
    if not game:
        return
    
    game.update_all_ratings()
    
    if result == "mice_win":
        msg = "🎉 *МЫШИ ПОБЕДИЛИ!* 🐭"
        win_photos = [
            "/root/bot/images/mice_win.jpg",
            "/root/bot/images/mice_win_2.jpg",
            "/root/bot/images/mice_win_3.jpg",
            "/root/bot/images/mice_win_4.jpg"
        ]
    else:
        msg = "🐀 *КРЫСА ПОБЕДИЛА!*"
        win_photos = [
            "/root/bot/images/rat_win.jpg",
            "/root/bot/images/rat_win_2.jpg",
            "/root/bot/images/rat_win_3.jpg",
            "/root/bot/images/rat_win_4.jpg"
        ]
    
    selected_photo = random.choice(win_photos)
    
    try:
        with open(selected_photo, "rb") as photo:
            await context.bot.send_photo(
                chat_id=chat_id,
                photo=photo,
                caption=msg,
                parse_mode=constants.ParseMode.MARKDOWN
            )
    except Exception as e:
        logger.error(f"Ошибка отправки фото победы: {e}")
        await context.bot.send_message(chat_id, msg, parse_mode=constants.ParseMode.MARKDOWN)
    
    total_items_dropped = 0
    total_chests_dropped = 0
    
    for pid, items in game.items_received.items():
        for item_id in items:
            item = ALL_ITEMS.get(item_id, {})
            if item.get("type") == "chest":
                total_chests_dropped += 1
            else:
                total_items_dropped += 1
    
    xp_text = "▸ ✨ *ПОЛУЧЕНО ОПЫТА*\n"
    for pid, data in game.players.items():
        won = (result == "mice_win" and "МЫШЬ" in data["role"]) or (result == "rat_win" and "КРЫСА" in data["role"])
        xp_gained = 10 + (50 if won else 0)
        name = escape_markdown(data['name'][:15])
        icon = "🏆" if won else "📊"
        xp_text += f"  ├─ {icon} {name}: +{xp_gained} XP\n"
    xp_text = xp_text.replace("├─", "└─", 1)
    
    await context.bot.send_message(chat_id, xp_text, parse_mode=constants.ParseMode.MARKDOWN)
    
    crumbs_text = "▸ 🧀 *ПОЛУЧЕНО КРОШЕК*\n"
    for pid, data in game.players.items():
        won = (result == "mice_win" and "МЫШЬ" in data["role"]) or (result == "rat_win" and "КРЫСА" in data["role"])
        
        player_level = get_level(pid)
        
        if won:
            crumbs_gained = random.randint(300, 600) + (player_level * 20)
        else:
            crumbs_gained = random.randint(60, 150) + (player_level * 6)
        
        name = escape_markdown(data['name'][:15])
        icon = "🏆" if won else "📊"
        crumbs_text += f"  ├─ {icon} {name}: +{crumbs_gained} 🧀\n"
    crumbs_text = crumbs_text.replace("├─", "└─", 1)
    
    await context.bot.send_message(chat_id, crumbs_text, parse_mode=constants.ParseMode.MARKDOWN)
    
    if total_items_dropped > 0 or total_chests_dropped > 0:
        loot_text = "▸ 🎁 *ДОБЫЧА*\n"
        if total_items_dropped > 0:
            loot_text += f"  ├─ 🎒 Найдено предметов: {total_items_dropped}\n"
        if total_chests_dropped > 0:
            loot_text += f"  └─ 📦 Получено сундуков: {total_chests_dropped}\n"
        loot_text = loot_text.replace("├─", "└─", 1) if total_items_dropped == 0 else loot_text
        await context.bot.send_message(chat_id, loot_text, parse_mode=constants.ParseMode.MARKDOWN)
    
    roles_text = "▸ 🎭 *ИТОГОВЫЕ РОЛИ*\n"
    for pid, data in game.players.items():
        status = "💀" if not data["alive"] else "✅"
        name = escape_markdown(data['name'][:15])
        role_to_show = data['role']
        if pid in game.fake_roles and not data["alive"]:
            role_to_show = game.fake_roles[pid]
        roles_text += f"  ├─ {status} {name}: {role_to_show}\n"
    roles_text = roles_text.replace("├─", "└─", 1)
    
    await context.bot.send_message(chat_id, roles_text, parse_mode=constants.ParseMode.MARKDOWN)
    
    await context.bot.send_message(
        chat_id,
        "📊 *Битва завершена!*\n"
        "/profile — твой профиль\n"
        "/rat_top — зал славы",
        parse_mode=constants.ParseMode.MARKDOWN
    )
    
    # 🆕 ИМПОРТИРУЕМ КАРТИНКИ ЗАКРЫТЫХ СУНДУКОВ
    from handlers.inventory import CHEST_IMAGES_CLOSED
    
    for pid, items in game.items_received.items():
        if items:
            for item_id in items:
                item = ALL_ITEMS.get(item_id, {"name": "Предмет", "desc": "", "icon": "🎁", "type": "equipment"})
                
                if item.get("type") == "chest":
                    rarity = item.get("rarity", "common")
                    # 🆕 ИСПОЛЬЗУЕМ ЗАКРЫТЫЙ СУНДУК ПРИ ПОЛУЧЕНИИ
                    image_path = CHEST_IMAGES_CLOSED.get(rarity, "/root/bot/images/chests/chest_common_closed.jpg")
                    caption = f"🎁 Ты получил сундук: *{item['name']}*\n└─ {item['desc']}"
                elif item.get("type") == "equipment":
                    image_path = "/root/bot/images/weapon_drop.jpg" if item.get("slot") == "weapon" else "/root/bot/images/item_drop.jpg"
                    caption = f"🎁 Ты получил экипировку: *{item['name']}*\n└─ {item['desc']}"
                elif item.get("type") == "consumable":
                    image_path = "/root/bot/images/consumable_drop.jpg"
                    caption = f"🎁 Ты получил расходник: *{item['name']}*\n└─ {item['desc']}"
                else:
                    image_path = "/root/bot/images/item_drop.jpg"
                    caption = f"🎁 Ты получил предмет: *{item['name']}*\n└─ {item['desc']}"
                
                try:
                    with open(image_path, "rb") as photo:
                        await context.bot.send_photo(
                            chat_id=pid,
                            photo=photo,
                            caption=caption,
                            parse_mode=constants.ParseMode.MARKDOWN
                        )
                except:
                    await context.bot.send_message(pid, caption, parse_mode=constants.ParseMode.MARKDOWN)
    
    for pid, achievements in game.achievements_unlocked.items():
        if achievements:
            for ach in achievements:
                try:
                    with open("/root/bot/images/achievement.jpg", "rb") as photo:
                        await context.bot.send_photo(
                            chat_id=pid,
                            photo=photo,
                            caption=f"🏆 *ДОСТИЖЕНИЕ РАЗБЛОКИРОВАНО!*\n\n{ach['name']}\n└─ {ach['desc']}",
                            parse_mode=constants.ParseMode.MARKDOWN
                        )
                except:
                    await context.bot.send_message(
                        pid,
                        f"🏆 *ДОСТИЖЕНИЕ РАЗБЛОКИРОВАНО!*\n\n{ach['name']}\n└─ {ach['desc']}",
                        parse_mode=constants.ParseMode.MARKDOWN
                    )
    
    if hasattr(game, 'level_ups') and game.level_ups:
        for pid, (new_level, old_level) in game.level_ups.items():
            keyboard = InlineKeyboardMarkup([
                [InlineKeyboardButton("📊 Профиль", callback_data="profile")],
                [InlineKeyboardButton("🏙️ В город", callback_data="city")]
            ])
            try:
                with open("/root/bot/images/level_up.jpg", "rb") as photo:
                    await context.bot.send_photo(
                        chat_id=pid,
                        photo=photo,
                        caption=f"⭐ *УРОВЕНЬ ПОВЫШЕН!*\n\n{old_level} → {new_level}",
                        parse_mode=constants.ParseMode.MARKDOWN,
                        reply_markup=keyboard
                    )
            except:
                await context.bot.send_message(
                    pid,
                    f"⭐ *УРОВЕНЬ ПОВЫШЕН!*\n\n{old_level} → {new_level}",
                    parse_mode=constants.ParseMode.MARKDOWN,
                    reply_markup=keyboard
                )
    
    game.phase = "ended"
    del active_games[chat_id]
    delete_game_state(chat_id)


# ========== МЕНЮ РАСХОДНИКОВ И СПОСОБНОСТЕЙ ==========

async def show_consumables_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    
    inventory = get_inventory(user_id)
    consumables = [(iid, CONSUMABLES[iid], qty) for iid, qty in inventory.items() if iid in CONSUMABLES and qty > 0]
    
    if not consumables:
        await query.answer("❌ Нет доступных расходников!", show_alert=True)
        return
    
    text = "*🎒 ВЫБЕРИ ПРЕДМЕТ ДЛЯ ИСПОЛЬЗОВАНИЯ:*\n\n"
    keyboard = []
    for item_id, item, qty in consumables:
        text += f"{item['icon']} {item['name']} x{qty}\n└ {item['desc']}\n\n"
        keyboard.append([InlineKeyboardButton(f"{item['icon']} Использовать {item['name']}", callback_data=f"use_consumable_{item_id}")])
    keyboard.append([InlineKeyboardButton("🔙 Назад", callback_data="back_to_game")])
    
    await query.message.delete()
    try:
        with open("/root/bot/images/use_item_prompt.jpg", "rb") as photo:
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

async def handle_use_consumable(update: Update, context: ContextTypes.DEFAULT_TYPE, item_id: str):
    query = update.callback_query
    user_id = query.from_user.id
    
    game = None
    for g in active_games.values():
        if user_id in g.players and g.players[user_id]["alive"]:
            game = g
            break
    
    if not game:
        await query.answer("❌ Ты не в игре или мёртв!", show_alert=True)
        return
    
    item = CONSUMABLES.get(item_id, {"name": "Предмет", "icon": "🎒", "effect": ""})
    effect = item.get("effect", "")
    
    # 🆕 Предметы требующие выбора цели
    if effect in ["reveal_role", "track_player", "resurrect", "love_bond", "russian_roulette", "check_dead", "curse_death"]:
        game.pending_item_use[user_id] = item_id
        await show_player_selection_for_item(update, context, item_id)
        return
    
    if use_consumable(user_id, item_id):
        await query.answer(f"✅ {item['name']} использован!", show_alert=True)
        
        effect_msg = apply_consumable_effect(game, user_id, item_id, context)
        await context.bot.send_message(user_id, effect_msg, parse_mode=constants.ParseMode.MARKDOWN)
        
        item_name = item.get('name', 'Предмет')
        item_icon = item.get('icon', '🎒')
        public_msg = f"{item_icon} *Кто-то использовал {item_name}!*"
        
        try:
            await context.bot.send_message(
                chat_id=game.chat_id,
                text=public_msg,
                parse_mode=constants.ParseMode.MARKDOWN
            )
        except Exception as e:
            logger.error(f"Ошибка отправки в общий чат: {e}")
        
        try:
            await query.message.delete()
        except:
            pass
    else:
        await query.answer("❌ Не удалось использовать предмет!", show_alert=True)


# 🆕 ВЫБОР ЦЕЛИ ДЛЯ ПРЕДМЕТОВ
async def show_player_selection_for_item(update: Update, context: ContextTypes.DEFAULT_TYPE, item_id: str):
    query = update.callback_query
    user_id = query.from_user.id
    
    game = None
    for g in active_games.values():
        if user_id in g.players:
            game = g
            break
    
    if not game:
        await query.answer("❌ Ты не в игре!", show_alert=True)
        return
    
    item = CONSUMABLES.get(item_id, {"name": "Предмет", "icon": "🎒", "effect": ""})
    effect = item.get("effect", "")
    
    if effect in ["reveal_role", "track_player", "russian_roulette"]:
        targets = [pid for pid, data in game.players.items() if data["alive"] and pid != user_id]
        title = "🔍 *Выбери игрока для проверки:*"
    elif effect == "check_dead":
        targets = [pid for pid, data in game.players.items() if not data["alive"]]
        title = "💀 *Выбери мёртвого игрока для проверки:*"
    elif effect == "resurrect":
        targets = [pid for pid, data in game.players.items() if not data["alive"]]
        title = "🍪 *Выбери кого воскресить:*"
    elif effect == "love_bond":
        targets = [pid for pid, data in game.players.items() if data["alive"] and pid != user_id]
        title = "💕 *Выбери первого игрока для связи:*"
    elif effect == "curse_death":
        targets = [pid for pid, data in game.players.items() if data["alive"]]
        title = "🪆 *Выбери цель для проклятия:*"
    else:
        await query.answer("❌ Неизвестный эффект!", show_alert=True)
        return
    
    if not targets:
        await query.answer("❌ Нет доступных целей!", show_alert=True)
        return
    
    keyboard = []
    for pid in targets:
        name = escape_markdown(game.players[pid]["name"])
        status = "✅" if game.players[pid]["alive"] else "💀"
        keyboard.append([InlineKeyboardButton(f"{status} {name}", callback_data=f"item_target_{item_id}_{pid}")])
    keyboard.append([InlineKeyboardButton("🔙 Отмена", callback_data="use_item_menu")])
    
    await query.message.delete()
    try:
        await context.bot.send_message(
            chat_id=user_id,
            text=title,
            parse_mode=constants.ParseMode.MARKDOWN,
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
    except:
        pass


async def handle_item_target_selection(update: Update, context: ContextTypes.DEFAULT_TYPE, item_id: str, target_id: int):
    query = update.callback_query
    user_id = query.from_user.id
    
    game = None
    for g in active_games.values():
        if user_id in g.players:
            game = g
            break
    
    if not game:
        await query.answer("❌ Ты не в игре!", show_alert=True)
        return
    
    item = CONSUMABLES.get(item_id, {"name": "Предмет", "icon": "🎒", "effect": ""})
    effect = item.get("effect", "")
    
    if not use_consumable(user_id, item_id):
        await query.answer("❌ Не удалось использовать предмет!", show_alert=True)
        return
    
    await query.answer(f"✅ {item['name']} использован!")
    
    # Применяем эффект с целью
    if effect == "reveal_role":
        role = game.players[target_id]["role"]
        await context.bot.send_message(
            user_id,
            f"🔮 *Роль игрока {escape_markdown(game.players[target_id]['name'])}:* {role}",
            parse_mode=constants.ParseMode.MARKDOWN
        )
    elif effect == "track_player":
        role = game.players[target_id]["role"]
        is_rat = "КРЫСА" in role
        await context.bot.send_message(
            user_id,
            f"📡 *Отслеживание {escape_markdown(game.players[target_id]['name'])}:* {'🐀 КРЫСА' if is_rat else '🐭 МЫШЬ'}",
            parse_mode=constants.ParseMode.MARKDOWN
        )
    elif effect == "resurrect":
        if not game.players[target_id]["alive"]:
            game.players[target_id]["alive"] = True
            game.players[target_id]["shielded"] = False
            game.players[target_id]["silenced"] = False
            await context.bot.send_message(
                game.chat_id,
                f"🍪 *ВОСКРЕШЕНИЕ!* {escape_markdown(game.players[target_id]['name'])} вернулся к жизни!",
                parse_mode=constants.ParseMode.MARKDOWN
            )
    elif effect == "check_dead":
        if not game.players[target_id]["alive"]:
            role = game.players[target_id]["role"]
            await context.bot.send_message(
                user_id,
                f"💧 *{escape_markdown(game.players[target_id]['name'])} был:* {role}",
                parse_mode=constants.ParseMode.MARKDOWN
            )
    elif effect == "russian_roulette":
        is_rat = "КРЫСА" in game.players[target_id]["role"]
        if is_rat:
            game.players[target_id]["alive"] = False
            await context.bot.send_message(
                game.chat_id,
                f"🪤 *МЫШЕЛОВКА!* {escape_markdown(game.players[target_id]['name'])} оказался КРЫСОЙ и погиб!",
                parse_mode=constants.ParseMode.MARKDOWN
            )
        else:
            game.players[user_id]["alive"] = False
            await context.bot.send_message(
                game.chat_id,
                f"🪤 *МЫШЕЛОВКА!* {escape_markdown(game.players[user_id]['name'])} ошибся и погиб...",
                parse_mode=constants.ParseMode.MARKDOWN
            )
    
    item_name = item.get('name', 'Предмет')
    item_icon = item.get('icon', '🎒')
    public_msg = f"{item_icon} *Кто-то использовал {item_name}!*"
    try:
        await context.bot.send_message(
            chat_id=game.chat_id,
            text=public_msg,
            parse_mode=constants.ParseMode.MARKDOWN
        )
    except:
        pass
    
    try:
        await query.message.delete()
    except:
        pass

# ========== ОТКРЫТИЕ СУНДУКОВ ==========
async def show_chests_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Показывает меню сундуков для открытия"""
    query = update.callback_query
    user_id = query.from_user.id
    
    from handlers.inventory import get_available_chests, CHEST_IMAGES_CLOSED
    
    chests = get_available_chests(user_id)
    
    if not chests:
        await query.answer("❌ У тебя нет сундуков!", show_alert=True)
        return
    
    text = "*📦 ТВОИ СУНДУКИ*\n\n"
    text += "Выбери сундук чтобы открыть:\n\n"
    
    keyboard = []
    for chest in chests:
        text += f"{chest['icon']} {chest['name']} x{chest['quantity']}\n└ {chest['desc']}\n\n"
        keyboard.append([
            InlineKeyboardButton(
                f"{chest['icon']} Открыть {chest['name']}",
                callback_data=f"open_chest_{chest['id']}"
            )
        ])
    
    keyboard.append([InlineKeyboardButton("🔙 Назад", callback_data="city_menu")])
    
    await query.message.delete()
    
    # 🆕 ПОКАЗЫВАЕМ ЗАКРЫТЫЙ СУНДУК
    first_chest = chests[0]
    rarity = first_chest.get("rarity", "common")
    image_path = CHEST_IMAGES_CLOSED.get(rarity, "/root/bot/images/chests/chest_common_closed.jpg")
    
    try:
        with open(image_path, "rb") as photo:
            await context.bot.send_photo(
                chat_id=user_id,
                photo=photo,
                caption=text,
                parse_mode=constants.ParseMode.MARKDOWN,
                reply_markup=InlineKeyboardMarkup(keyboard)
            )
    except Exception as e:
        logger.error(f"Ошибка отправки меню сундуков: {e}")
        await context.bot.send_message(
            chat_id=user_id,
            text=text,
            parse_mode=constants.ParseMode.MARKDOWN,
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
    
    await query.answer()


async def handle_open_chest(update: Update, context: ContextTypes.DEFAULT_TYPE, chest_id: str):
    """Открывает выбранный сундук"""
    query = update.callback_query
    user_id = query.from_user.id
    
    # 🔥🔥🔥 ХАРДКОРНЫЙ ФИКС 🔥🔥🔥
    if not chest_id.endswith("_chest"):
        old_id = chest_id
        chest_id = f"{chest_id}_chest"
        logger.info(f"🔥🔥🔥 ХАРДКОРНЫЙ ФИКС: {old_id} -> {chest_id}")
    
    logger.info(f"📦 handle_open_chest: user={user_id}, chest_id={chest_id}")
    
    result = open_chest_func(user_id, chest_id)
    
    if not result:
        logger.warning(f"❌ open_chest_func вернул None для chest_id={chest_id}")
        await query.answer("❌ Не удалось открыть сундук!", show_alert=True)
        return
    
    chest_name = result["chest_name"]
    
    if result["type"] == "single":
        item = result["item"]
        
        rarity = item.get("rarity", "common")
        chest_open_image = CHEST_IMAGES_OPEN.get(rarity, "/root/bot/images/chests/chest_common.jpg")
        
        if item.get("type") == "equipment":
            caption = f"📦 *СУНДУК ОТКРЫТ!*\n\n{chest_name}\n\n🎁 Выпал предмет:\n*{item['name']}*\n└ {item['desc']}"
        elif item.get("type") == "consumable":
            caption = f"📦 *СУНДУК ОТКРЫТ!*\n\n{chest_name}\n\n🎁 Выпал расходник:\n*{item['name']}*\n└ {item['desc']}"
        else:
            caption = f"📦 *СУНДУК ОТКРЫТ!*\n\n{chest_name}\n\n🎁 Выпал предмет:\n*{item['name']}*\n└ {item['desc']}"
        
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("Назад", callback_data="profile_inventory")]
        ])
        
        try:
            with open(chest_open_image, "rb") as photo:
                await context.bot.send_photo(
                    chat_id=user_id,
                    photo=photo,
                    caption=caption,
                    parse_mode=constants.ParseMode.MARKDOWN,
                    reply_markup=keyboard
                )
        except Exception as e:
            logger.error(f"Ошибка отправки результата открытия: {e}")
            await context.bot.send_message(
                chat_id=user_id,
                text=caption,
                parse_mode=constants.ParseMode.MARKDOWN,
                reply_markup=keyboard
            )
        
        await query.answer(f"✅ Получено: {item['name']}!")
    
    elif result["type"] == "multiple":
        items_dropped = result["items"]
        
        image_path = CHEST_IMAGES_OPEN.get("legendary", "/root/bot/images/chests/chest_legendary.jpg")
        caption = f"📦 *СЫРНЫЙ СУНДУК ОТКРЫТ!*\n\n{chest_name}\n\n🎁 Выпало {len(items_dropped)} предметов:\n"
        
        for drop_id in items_dropped[:5]:
            drop_item = ALL_ITEMS_DICT.get(drop_id, {"name": "Предмет", "icon": "🎁"})
            caption += f"\n{drop_item['icon']} {drop_item['name']}"
        
        if len(items_dropped) > 5:
            caption += f"\n\n... и ещё {len(items_dropped) - 5} предметов!"
        
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("Назад", callback_data="profile_inventory")]
        ])
        
        try:
            with open(image_path, "rb") as photo:
                await context.bot.send_photo(
                    chat_id=user_id,
                    photo=photo,
                    caption=caption,
                    parse_mode=constants.ParseMode.MARKDOWN,
                    reply_markup=keyboard
                )
        except Exception as e:
            logger.error(f"Ошибка отправки результата открытия: {e}")
            await context.bot.send_message(
                chat_id=user_id,
                text=caption,
                parse_mode=constants.ParseMode.MARKDOWN,
                reply_markup=keyboard
            )
        
        await query.answer(f"✅ Получено {len(items_dropped)} предметов!")
    
    try:
        await query.message.delete()
    except:
        pass
    
# 🆕 ВЫСТРЕЛ ИЗ АРБАЛЕТА
async def show_day_shot_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    
    game = None
    for g in active_games.values():
        if user_id in g.players and g.players[user_id]["alive"]:
            game = g
            break
    
    if not game:
        await query.answer("❌ Ты не в игре или мёртв!", show_alert=True)
        return
    
    targets = [pid for pid, data in game.players.items() if data["alive"] and pid != user_id]
    
    if not targets:
        await query.answer("❌ Нет доступных целей!", show_alert=True)
        return
    
    keyboard = []
    for pid in targets:
        name = escape_markdown(game.players[pid]["name"])
        keyboard.append([InlineKeyboardButton(f"🏹 {name}", callback_data=f"day_shot_{pid}")])
    keyboard.append([InlineKeyboardButton("🔙 Отмена", callback_data="back_to_game")])
    
    await query.message.delete()
    try:
        await context.bot.send_message(
            chat_id=user_id,
            text="🏹 *Выбери цель для выстрела:*",
            parse_mode=constants.ParseMode.MARKDOWN,
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
    except:
        pass


async def handle_day_shot(update: Update, context: ContextTypes.DEFAULT_TYPE, target_id: int):
    query = update.callback_query
    user_id = query.from_user.id
    
    game = None
    for g in active_games.values():
        if user_id in g.players:
            game = g
            break
    
    if not game:
        await query.answer("❌ Ты не в игре!", show_alert=True)
        return
    
    if target_id not in game.players or not game.players[target_id]["alive"]:
        await query.answer("❌ Нельзя выбрать эту цель!", show_alert=True)
        return
    
    is_rat = "КРЫСА" in game.players[target_id]["role"]
    target_name = escape_markdown(game.players[target_id]["name"])
    shooter_name = escape_markdown(game.players[user_id]["name"])
    
    # 50% шанс успеха
    if random.randint(1, 100) <= 50:
        if is_rat:
            game.players[target_id]["alive"] = False
            await context.bot.send_message(
                game.chat_id,
                f"🏹 *ВЫСТРЕЛ!* {shooter_name} попал в {target_name} и убил КРЫСУ!",
                parse_mode=constants.ParseMode.MARKDOWN
            )
            unlock_achievement(user_id, "eagle_eye")
        else:
            game.players[target_id]["alive"] = False
            await context.bot.send_message(
                game.chat_id,
                f"🏹 *ВЫСТРЕЛ!* {shooter_name} попал в {target_name}. Это была МЫШЬ...",
                parse_mode=constants.ParseMode.MARKDOWN
            )
    else:
        # Проверяем защиту цели
        if is_shot_proof(target_id):
            await context.bot.send_message(
                game.chat_id,
                f"🏹 *ВЫСТРЕЛ!* {shooter_name} выстрелил в {target_name}, но пуля не пробила броню!",
                parse_mode=constants.ParseMode.MARKDOWN
            )
        else:
            await context.bot.send_message(
                game.chat_id,
                f"🏹 *ВЫСТРЕЛ!* {shooter_name} промахнулся!",
                parse_mode=constants.ParseMode.MARKDOWN
            )
    
    await query.answer("✅ Выстрел произведён!")
    try:
        await query.message.delete()
    except:
        pass


# 🆕 АНОНИМНОЕ СООБЩЕНИЕ ОТ МЁРТВЫХ
async def handle_dead_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    
    game = None
    for g in active_games.values():
        if user_id in g.players:
            game = g
            break
    
    if not game:
        await query.answer("❌ Ты не в игре!", show_alert=True)
        return
    
    if user_id not in game.dead_messages_allowed or game.dead_messages_allowed[user_id] <= 0:
        await query.answer("❌ У тебя нет права на сообщение!", show_alert=True)
        return
    
    game.pending_dead_message = user_id
    game.dead_messages_allowed[user_id] -= 1
    
    await query.answer("📜 Напиши сообщение в чат бота (не в группу!)")
    await query.message.delete()
    
    # Ждём сообщение от пользователя
    context.user_data["awaiting_dead_message"] = True
    context.user_data["dead_message_game"] = game.chat_id


# ========== КОЛБЭКИ ==========
async def handle_rat_kill(update: Update, context: ContextTypes.DEFAULT_TYPE, target_id: int):
    query = update.callback_query
    user_id = query.from_user.id
    chat_id = None
    
    for cid, g in active_games.items():
        if user_id in g.players:
            chat_id = cid
            break
    
    game = active_games.get(chat_id)
    if not game or game.phase != "night" or user_id != game.rat_id:
        await query.answer("❌ Нельзя сейчас!", show_alert=True)
        return
    
    if target_id in game.players and game.players[target_id]["alive"]:
        game.night_kill = target_id
        game.night_ended = True
        await query.answer("✅ Жертва выбрана!")
        
        if user_id in game.berserk_mode and game.berserk_mode[user_id]:
            game.berserk_mode[user_id] = False
            await context.bot.send_message(
                chat_id,
                f"😤 *БЕРСЕРК!* {escape_markdown(game.players[user_id]['name'])} раскрыл себя! Он КРЫСА!",
                parse_mode=constants.ParseMode.MARKDOWN
            )
        
        try:
            await query.message.delete()
        except:
            pass
    else:
        await query.answer("❌ Нельзя выбрать этого игрока!", show_alert=True)

async def handle_rat_kill_none(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    chat_id = None
    
    for cid, g in active_games.items():
        if user_id in g.players:
            chat_id = cid
            break
    
    game = active_games.get(chat_id)
    if not game or game.phase != "night" or user_id != game.rat_id:
        await query.answer("❌ Нельзя сейчас!", show_alert=True)
        return
    
    game.night_kill = None
    game.night_ended = True
    await query.answer("😇 Никого не убиваешь")
    
    try:
        await query.message.delete()
    except:
        pass

async def handle_rat_vote(update: Update, context: ContextTypes.DEFAULT_TYPE, target_id: int):
    query = update.callback_query
    user_id = query.from_user.id
    chat_id = None
    
    for cid, g in active_games.items():
        if user_id in g.players:
            chat_id = cid
            break
    
    game = active_games.get(chat_id)
    if not game or game.phase != "voting":
        await query.answer("❌ Сейчас не голосование!", show_alert=True)
        return
    
    if user_id not in game.players or not game.players[user_id]["alive"]:
        await query.answer("❌ Ты не можешь голосовать!", show_alert=True)
        return
    
    if target_id in game.players and game.players[target_id]["alive"] and target_id != user_id:
        game.votes[user_id] = target_id
        await query.answer(f"✅ Голос за {game.players[target_id]['name']}")
        try:
            await query.message.delete()
        except:
            pass
    else:
        await query.answer("❌ Нельзя голосовать за этого игрока!", show_alert=True)

async def handle_rat_vote_skip(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    chat_id = None
    
    for cid, g in active_games.items():
        if user_id in g.players:
            chat_id = cid
            break
    
    game = active_games.get(chat_id)
    if not game or game.phase != "voting":
        await query.answer("❌ Сейчас не голосование!", show_alert=True)
        return
    
    if user_id not in game.players or not game.players[user_id]["alive"]:
        await query.answer("❌ Ты не можешь голосовать!", show_alert=True)
        return
    
    game.votes[user_id] = None
    await query.answer("⏭ Пропустил голосование")
    try:
        await query.message.delete()
    except:
        pass

async def handle_ghost_vote(update: Update, context: ContextTypes.DEFAULT_TYPE, target_id: int):
    query = update.callback_query
    user_id = query.from_user.id
    chat_id = None
    
    for cid, g in active_games.items():
        if user_id in g.players:
            chat_id = cid
            break
    
    game = active_games.get(chat_id)
    if not game or game.phase != "voting":
        await query.answer("❌ Сейчас не голосование!", show_alert=True)
        return
    
    if user_id not in game.players or game.players[user_id]["alive"]:
        await query.answer("❌ Ты живой!", show_alert=True)
        return
    
    if target_id in game.players and game.players[target_id]["alive"]:
        game.votes[user_id] = target_id
        await query.answer(f"👻 Призрачный голос за {game.players[target_id]['name']}")
        try:
            await query.message.delete()
        except:
            pass
    else:
        await query.answer("❌ Нельзя голосовать!", show_alert=True)

async def back_to_game(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.message.delete()
    await query.answer("🔙 Возвращайся к игре!")