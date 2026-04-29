"""Хендлеры для игры в кости (таверна) — полный файл"""

import asyncio
import random
import sqlite3
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from telegram import constants

from services.dice import dice_service
from core.dice.engine import get_dice_engine
from keyboards.inline.dice import (
    get_bet_keyboard,
    get_play_again_keyboard,
    get_beer_keyboard,
    get_tournament_back_keyboard,
    get_custom_bet_back_keyboard,
    get_tavern_main_keyboard,
    get_fight_menu_keyboard,
    get_fight_active_keyboard,
    get_fight_challenge_keyboard,
    get_fight_result_keyboard,
    get_race_menu_keyboard,
    get_race_bet_keyboard,
    get_race_result_keyboard,
)
from core.dice.models import BetResult, DiceGameResult, GameMode
from services.tavern_fight import tavern_fight_service
from services.tavern_race import tavern_race_service, COCKROACHES

dice = get_dice_engine()

# Пути к картинкам
DICE_GAME_IMAGE = "/root/bot/images/dice_game.jpg"
DICE_WIN_IMAGE = "/root/bot/images/dice_win.jpg"
DICE_LOSE_IMAGE = "/root/bot/images/dice_lose.jpg"
BEER_DRINK_IMAGE = "/root/bot/images/beer_drink.jpg"
TAVERN_MAIN_IMAGE = "/root/bot/images/tavern_main.jpg"
TAVERN_FIGHT_IMAGE = "/root/bot/images/tavern_fight.jpg"
TAVERN_RACE_IMAGE = "/root/bot/images/tarakan_race.jpg"


def get_player_nickname(user_id: int) -> str:
    try:
        conn = sqlite3.connect('/root/bot/ratings.db')
        cur = conn.execute('SELECT nickname FROM ratings WHERE user_id = ?', (user_id,))
        row = cur.fetchone()
        conn.close()
        if row and row[0]:
            return row[0]
    except:
        pass
    return "Искатель"


# ========== ГЛАВНОЕ МЕНЮ ТАВЕРНЫ ==========

async def tavern_main_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Главное меню таверны"""
    query = update.callback_query
    user_id = query.from_user.id

    tavern_fight_service.join_tavern(user_id)

    text = dice_service.format_stats_message(user_id)

    players = tavern_fight_service.get_tavern_players(exclude_user_id=user_id)
    if players:
        text += "\n\n*Сейчас в таверне:*"
        for p in players[:5]:
            text += f"\n  🐀 *{p['nickname']}*"

    text += "\n\n*Выбери что делать:*"

    await query.message.delete()
    try:
        with open(TAVERN_MAIN_IMAGE, "rb") as photo:
            await context.bot.send_photo(
                chat_id=user_id, photo=photo, caption=text,
                parse_mode=constants.ParseMode.MARKDOWN,
                reply_markup=get_tavern_main_keyboard()
            )
    except:
        await context.bot.send_message(
            chat_id=user_id, text=text,
            parse_mode=constants.ParseMode.MARKDOWN,
            reply_markup=get_tavern_main_keyboard()
        )


# ========== КОСТИ ==========

async def dice_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Команда /dice"""
    user_id = update.effective_user.id

    if update.callback_query:
        query = update.callback_query
        user_id = query.from_user.id
        await tavern_main_menu(update, context)
        return

    args = context.args
    if args:
        try:
            bet = int(args[0])
            if bet <= 0:
                raise ValueError
            await start_dice_game(update, context, user_id, bet)
            return
        except:
            await update.message.reply_text("❌ Ставка должна быть положительным числом!")
            return

    await tavern_main_menu(update, context)


async def tavern_dice_menu_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Меню выбора ставки"""
    query = update.callback_query
    user_id = query.from_user.id
    crumbs = dice_service.get_crumbs(user_id)
    stats = dice_service.get_player_stats(user_id)
    total_profit = stats.total_crumbs_won - stats.total_crumbs_lost
    profit_emoji = "📈" if total_profit >= 0 else "📉"

    import random
    tips = [
        "«Две шестёрки против двух единиц — x5 к выигрышу! Рискуй!»",
        "«Серия из 3 побед удваивает множитель. Не останавливайся!»",
        "«Ежедневный бонус удваивает выигрыш. Заходи каждый день!»",
        "«При ничьей ставка возвращается. Иногда лучше не проиграть.»",
        "«Тень любит новичков. Первый бросок часто везёт.»",
        "«Критическая победа — это 12 против 6 или меньше. Тогда x5!»",
    ]

    text = f"""🎲 *Игра в кости*

_Древняя игра подземелья. Ты против Тени — самой удачи._
_Два кубика решат, кто сегодня уйдёт с крошками, а кто — с пустыми лапами._

🧀 Крошки: *{crumbs:,}*
🎯 Игр: *{stats.total_games}* | Побед: *{stats.total_wins}* ({stats.win_rate:.1f}%)
🔥 Серия побед: *{stats.current_win_streak}* | 💀 Поражений подряд: *{stats.current_lose_streak}*
{profit_emoji} Итог: *{total_profit:+,}* 🧀

💡 _Совет от Шныра:_
{random.choice(tips)}

*Выбери ставку:*"""

    await query.message.delete()
    try:
        with open(DICE_GAME_IMAGE, "rb") as photo:
            await context.bot.send_photo(
                chat_id=user_id, photo=photo, caption=text,
                parse_mode=constants.ParseMode.MARKDOWN,
                reply_markup=get_bet_keyboard()
            )
    except:
        await context.bot.send_message(
            chat_id=user_id, text=text,
            parse_mode=constants.ParseMode.MARKDOWN,
            reply_markup=get_bet_keyboard()
        )


async def dice_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработка колбэков костей"""
    query = update.callback_query
    user_id = query.from_user.id
    data = query.data
    bet = context.user_data.get('dice_bet', 50)

    if data == "dice_play_again":
        await query.message.delete()
        await play_dice_round(update, context, user_id, bet)
    elif data == "dice_free_reroll":
        await query.message.delete()
        await play_dice_round(update, context, user_id, bet, free_reroll=True)
    elif data.startswith("dice_start_"):
        bet = int(data.replace("dice_start_", ""))
        context.user_data['dice_bet'] = bet
        await start_dice_game_callback(update, context, user_id, bet)
    elif data == "beer_buff":
        await buy_beer(update, context)
    elif data == "dice_tournament":
        await show_tournament(update, context)
    elif data == "dice_custom_bet":
        await query.message.delete()
        await context.bot.send_message(
            chat_id=user_id,
            text="✏️ *ВВЕДИ СВОЮ СТАВКУ:*\n\nОтправь число — сумму в крошках.\n\nДля отмены нажми /cancel",
            parse_mode=constants.ParseMode.MARKDOWN,
            reply_markup=get_custom_bet_back_keyboard()
        )
        context.user_data['awaiting_bet'] = True


async def start_dice_game_callback(update: Update, context: ContextTypes.DEFAULT_TYPE,
                                   user_id: int, bet: int):
    query = update.callback_query
    crumbs = dice_service.get_crumbs(user_id)
    if crumbs < bet:
        await query.answer(f"❌ Недостаточно крошек! Нужно {bet} 🧀", show_alert=True)
        return
    await query.message.delete()
    await play_dice_round(update, context, user_id, bet)


async def start_dice_game(update: Update, context: ContextTypes.DEFAULT_TYPE,
                          user_id: int, bet: int):
    crumbs = dice_service.get_crumbs(user_id)
    if crumbs < bet:
        await update.message.reply_text(
            f"❌ У тебя только *{crumbs}* 🧀! Не хватает на ставку *{bet}* 🧀.",
            parse_mode=constants.ParseMode.MARKDOWN
        )
        return
    context.user_data['dice_bet'] = bet
    await play_dice_round(update, context, user_id, bet)


async def play_dice_round(update: Update, context: ContextTypes.DEFAULT_TYPE,
                          user_id: int, bet: int, free_reroll: bool = False):
    stats = dice_service.get_player_stats(user_id)
    daily_bonus = stats.daily_bonus_available

    if daily_bonus and not free_reroll:
        dice_service.claim_daily_bonus(user_id)
        # Снять ставку
    if not free_reroll:
        dice_service.spend_crumbs(user_id, bet)
    player_nickname = get_player_nickname(user_id)

    player_total, shadow_total, p1, p2, s1, s2 = await dice.perform_double_roll_with_stickers(
        context=context, chat_id=user_id,
        first_name=player_nickname, second_name="Тень"
    )

    is_win = player_total > shadow_total
    is_draw = player_total == shadow_total
    is_critical = (player_total == 12 and shadow_total <= 6)
    is_crit_lose = (shadow_total == 12 and player_total <= 6)

    multiplier = 2.0
    if stats.current_win_streak >= 5: multiplier = 3.0
    elif stats.current_win_streak >= 3: multiplier = 2.5
    if is_critical: multiplier = 5.0
    elif player_total == 12 and shadow_total == 12: multiplier = 10.0
    if daily_bonus and is_win: multiplier *= 2

    if is_win:
        win_amount = int(bet * multiplier)
        net_profit = win_amount - bet
    else:
        win_amount = 0
        net_profit = -bet

    bet_result = BetResult(
        bet_amount=bet, win_amount=win_amount, net_profit=net_profit,
        multiplier=multiplier, is_win=is_win, is_critical=is_critical, is_draw=is_draw
    )

    result = DiceGameResult(
        user_id=user_id, mode=GameMode.VS_SHADOW,
        player_roll=player_total, shadow_roll=shadow_total, bet=bet_result,
        win_streak=stats.current_win_streak + (1 if is_win else 0),
        lose_streak=0 if is_win else stats.current_lose_streak + 1,
        daily_bonus_used=daily_bonus
    )

    dice_service._save_game_result(result)
    dice_service._update_player_stats(user_id, result)

    if is_draw: title = "⚖️ *НИЧЬЯ!*"
    elif is_win:
        if is_critical: title = "🔥 *ЛЕГЕНДАРНАЯ ПОБЕДА!*"
        elif player_total == 12: title = "🌟 *ДВЕ ШЕСТЁРКИ!*"
        else: title = "🎉 *ПОБЕДА!*"
    else:
        if is_crit_lose: title = "💀 *СОКРУШИТЕЛЬНОЕ ПОРАЖЕНИЕ!*"
        elif player_total == 2: title = "🐀 *ДВЕ ЕДИНИЦЫ!*"
        else: title = "💔 *ПРОИГРЫШ...*"

    crumbs = dice_service.get_crumbs(user_id)

    result_text = f"{title}\n\n"
    result_text += f"🎲 Твои кубики: *{p1} + {p2} = {player_total}*\n"
    result_text += f"💀 Кубики Тени: *{s1} + {s2} = {shadow_total}*\n\n"

    if is_win:
        result_text += f"🏆 Выигрыш: *+{net_profit}* 🧀 (x{multiplier:.1f})\n📦 Всего: *{crumbs}* 🧀\n\n🔥 Серия побед: *{result.win_streak}*"
    else:
        result_text += f"💸 Потеряно: *{bet}* 🧀\n📦 Осталось: *{crumbs}* 🧀\n\n💀 Серия поражений: *{result.lose_streak}*"

    image_path = DICE_WIN_IMAGE if is_win else DICE_LOSE_IMAGE
    if is_draw: image_path = DICE_GAME_IMAGE

    try:
        with open(image_path, "rb") as photo:
            await context.bot.send_photo(
                chat_id=user_id, photo=photo, caption=result_text,
                parse_mode=constants.ParseMode.MARKDOWN,
                reply_markup=get_play_again_keyboard()
            )
    except:
        await context.bot.send_message(
            chat_id=user_id, text=result_text,
            parse_mode=constants.ParseMode.MARKDOWN,
            reply_markup=get_play_again_keyboard()
        )


# ========== ПИВО ==========

async def buy_beer(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    success, effect, drink_text = dice_service.buy_beer(user_id)
    if not success:
        await query.answer(drink_text, show_alert=True)
        return

    effects_text = dice_service.get_beer_effects_text(user_id)
    text = f"""🍺 *ПИВО ИЛЬЯС ВЫПИТО!*

{drink_text}

Получен эффект: {effect['icon']} *{effect['name']}*
└─ {effect['desc']}

Длительность: *1 час*{effects_text}"""

    await query.answer(f"🍺 Получен эффект: {effect['name']}!")
    await query.message.delete()
    try:
        with open(BEER_DRINK_IMAGE, "rb") as photo:
            await context.bot.send_photo(
                chat_id=user_id, photo=photo, caption=text,
                parse_mode=constants.ParseMode.MARKDOWN,
                reply_markup=get_beer_keyboard()
            )
    except:
        await context.bot.send_message(
            chat_id=user_id, text=text,
            parse_mode=constants.ParseMode.MARKDOWN,
            reply_markup=get_beer_keyboard()
        )


# ========== ТУРНИР ==========

async def show_tournament(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id

    text = f"""*Сырные игры*

_Главное событие таверны! Восемь бойцов, один чемпион._
_Ставка 250 🧀 с каждого. Победитель забирает всё — 2 000 🧀!_
_Два кубика решают судьбу. Кто рискует — тот пьёт эль бесплатно!_

📋 *Правила:*
• 8 участников • Ставка 250 🧀
• Играют по очереди против Тени
• У кого больше сумма — проходит дальше
• Четвертьфинал → Полуфинал → Финал
• 🏆 Победитель забирает банк: *2 000 🧀*

•Пока турнир не набирается!

_Заглядывай позже или зови друзей в таверну!_"""

    await query.message.delete()
    try:
        with open("/root/bot/images/tavern_tournament.jpg", "rb") as photo:
            await context.bot.send_photo(
                chat_id=user_id, photo=photo, caption=text,
                parse_mode=constants.ParseMode.MARKDOWN,
                reply_markup=get_tournament_back_keyboard()
            )
    except:
        await context.bot.send_message(
            chat_id=user_id, text=text,
            parse_mode=constants.ParseMode.MARKDOWN,
            reply_markup=get_tournament_back_keyboard()
        )


# ========== ПОДСЛУШАТЬ ==========

async def tavern_eavesdrop_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Подслушать разговоры"""
    query = update.callback_query
    user_id = query.from_user.id

    rumors = [
        "💬 «Слыхал, в Нижних Туннелях завёлся Крысиный Упырь. Говорят, с него падает легендарный клинок...»",
        "💬 «Шныр говорил, что на Поверхности видели белого кота. Это плохой знак.»",
        "💬 «Вчера кто-то сорвал куш на бегах — поставил на Шустрика и ушёл с 1500 крошек!»",
        "💬 «Старая Ильяска варит лучшее пиво в Подземье. Секретный ингредиент — плесень с сыра.»",
        "💬 «Говорят, в Зале Славы появилось новое имя. Кто-то убил Старого Слепого Кота.»",
        "💬 «Не ставь на Шестиногого — он читерит. У него шесть ног, это нечестно!»",
    ]

    text = f"👂 *ПОДСЛУШАТЬ*\n\n_Ты подсаживаешься ближе к компании за соседним столом..._\n\n{random.choice(rumors)}"

    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("👂 Ещё", callback_data="tavern_eavesdrop")],
        [InlineKeyboardButton("🔙 Таверна", callback_data="profile_dice")],
    ])

    await query.message.delete()
    await context.bot.send_message(
        chat_id=user_id, text=text,
        parse_mode=constants.ParseMode.MARKDOWN, reply_markup=keyboard
    )


# ========== ДРАКИ ==========

async def tavern_fight_menu_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Меню выбора соперника"""
    query = update.callback_query
    user_id = query.from_user.id

    players = tavern_fight_service.get_tavern_players(exclude_user_id=user_id)

    if not players:
        text = f"""👊 *ПОДРАТЬСЯ*

_В таверне сейчас никого нет, кому ты хочешь набить морду?_

_Возвращайся позже, когда кто-нибудь зайдёт выпить пива._

_Мистер Гауда покачал головой: «Ты пьян, парень. Иди домой!»_"""

        await query.message.delete()
        try:
            with open(TAVERN_FIGHT_IMAGE, "rb") as photo:
                await context.bot.send_photo(
                    chat_id=user_id, photo=photo, caption=text,
                    parse_mode=constants.ParseMode.MARKDOWN,
                    reply_markup=InlineKeyboardMarkup([[
                        InlineKeyboardButton("🔙 Таверна", callback_data="profile_dice")
                    ]])
                )
        except:
            await context.bot.send_message(
                chat_id=user_id, text=text,
                parse_mode=constants.ParseMode.MARKDOWN,
                reply_markup=InlineKeyboardMarkup([[
                    InlineKeyboardButton("🔙 Таверна", callback_data="profile_dice")
                ]])
            )
        return

    text = f"""👊 *ПОДРАТЬСЯ*

_Кому хочешь набить морду? Бой на кулаках — без оружия и брони._

*В таверне:*"""
    for p in players:
        text += f"\n  🐀 *{p['nickname']}* — ур. {p['level']} (❤️ {p['hp']}/{p['max_hp']})"

    await query.message.delete()
    try:
        with open(TAVERN_FIGHT_IMAGE, "rb") as photo:
            await context.bot.send_photo(
                chat_id=user_id, photo=photo, caption=text,
                parse_mode=constants.ParseMode.MARKDOWN,
                reply_markup=get_fight_menu_keyboard(players)
            )
    except:
        await context.bot.send_message(
            chat_id=user_id, text=text,
            parse_mode=constants.ParseMode.MARKDOWN,
            reply_markup=get_fight_menu_keyboard(players)
        )


async def tavern_challenge_handler(update: Update, context: ContextTypes.DEFAULT_TYPE, target_id: int):
    """Бросить вызов"""
    query = update.callback_query
    challenger_id = query.from_user.id

    fight_id = tavern_fight_service.challenge_player(challenger_id, target_id)
    if not fight_id:
        await query.answer("❌ Игрок покинул таверну!", show_alert=True)
        return

    try:
        await context.bot.send_message(
            chat_id=target_id,
            text=f"👊 *ВЫЗОВ НА ДРАКУ!*\n\n"
                 f"🐀 *{query.from_user.full_name}* хочет подраться с тобой!\n\n"
                 f"_Бой на кулаках — без оружия и брони._",
            parse_mode=constants.ParseMode.MARKDOWN,
            reply_markup=get_fight_challenge_keyboard(fight_id)
        )
    except:
        pass

    await query.answer("✅ Вызов отправлен! Жди ответа.")
    await tavern_fight_menu_handler(update, context)


async def tavern_accept_fight(update: Update, context: ContextTypes.DEFAULT_TYPE, fight_id: str):
    """Принять бой"""
    query = update.callback_query
    user_id = query.from_user.id

    fight = tavern_fight_service.accept_fight(fight_id, user_id)
    if not fight:
        await query.answer("❌ Бой не найден!", show_alert=True)
        return

    context.user_data["tavern_fight"] = fight
    context.user_data["tavern_fight_id"] = fight_id

    text = f"""👊 *ДРАКА!*

⚡ Бой начался!

❤️ Ты: {fight['target_hp']}
❤️ Противник: {fight['challenger_hp']}

Раунд 1/3

*Твой ход!*"""

    await query.message.delete()
    await context.bot.send_message(
        chat_id=user_id, text=text,
        parse_mode=constants.ParseMode.MARKDOWN,
        reply_markup=get_fight_active_keyboard(fight_id)
    )
    await context.bot.send_message(
        chat_id=fight["challenger_id"],
        text=f"👊 *ДРАКА НАЧАЛАСЬ!*\n\nПротивник принял вызов! Жди своего хода.",
        parse_mode=constants.ParseMode.MARKDOWN
    )


async def tavern_decline_fight(update: Update, context: ContextTypes.DEFAULT_TYPE, fight_id: str):
    """Отклонить бой"""
    query = update.callback_query
    user_id = query.from_user.id

    import sqlite3
    with sqlite3.connect('/root/bot/ratings.db') as conn:
        conn.execute("UPDATE tavern_fights SET status = 'declined' WHERE fight_id = ?", (fight_id,))
        conn.commit()

    await query.message.delete()
    await context.bot.send_message(
        chat_id=user_id,
        text="🏃 Ты отказался от драки.",
        parse_mode=constants.ParseMode.MARKDOWN
    )


async def tavern_punch_handler(update: Update, context: ContextTypes.DEFAULT_TYPE, fight_id: str):
    """Удар в драке"""
    query = update.callback_query
    user_id = query.from_user.id

    result = tavern_fight_service.process_punch(fight_id, user_id)
    if not result:
        await query.answer("❌ Бой не найден!", show_alert=True)
        return

    if result["winner_id"]:
        fight_result = tavern_fight_service.resolve_fight(fight_id, result["winner_id"])
        is_winner = (result["winner_id"] == user_id)

        text = f"🏆 *{'ПОБЕДА!' if is_winner else 'ПОРАЖЕНИЕ...'}*\n\n"
        text += f"_Ты {'поколотил' if is_winner else 'проиграл'} соперника!_\n\n"

        if is_winner:
            text += f"💰 Украдено: *{fight_result['crumbs_stolen']}* 🧀\n"
            text += f"✨ XP: *+{fight_result['xp_earned']}*\n"
            if fight_result.get("resource_stolen"):
                text += f"📦 Со шкуры упало: {fight_result['resource_icon']} *{fight_result['resource_name']}*\n"

        # Обновить HP в user_stats
        from services.inventory import inventory_service
        inventory_service.add_xp(user_id, fight_result['xp_earned'] if is_winner else 5)

        await query.message.delete()
        await context.bot.send_message(
            chat_id=user_id, text=text,
            parse_mode=constants.ParseMode.MARKDOWN,
            reply_markup=get_fight_result_keyboard()
        )

        # Уведомить соперника
        other_id = result["defender_id"] if result["attacker_id"] == user_id else result["attacker_id"]
        other_text = f"👊 *ДРАКА ОКОНЧЕНА!*\n\n"
        other_text += f"{'Ты победил!' if not is_winner else 'Ты проиграл...'}\n"
        await context.bot.send_message(
            chat_id=other_id, text=other_text,
            parse_mode=constants.ParseMode.MARKDOWN,
            reply_markup=get_fight_result_keyboard()
        )
        return

    # Бой продолжается
    text = f"""👊 *ДРАКА!*

🎲 Атака: {result['attack_roll']}
🛡️ Защита: {result['defend_roll']}
{'💥 Попадание! -' + str(result['damage']) + ' HP' if result['hit'] else '🛡️ Заблокировано!'}

❤️ Ты: {result['attacker_hp'] if result['attacker_id'] == user_id else result['defender_hp']}
❤️ Противник: {result['defender_hp'] if result['attacker_id'] == user_id else result['attacker_hp']}

Раунд {result['round']}/{result['max_rounds']}"""

    await query.message.delete()
    await context.bot.send_message(
        chat_id=user_id, text=text,
        parse_mode=constants.ParseMode.MARKDOWN,
        reply_markup=get_fight_active_keyboard(fight_id)
    )


# ========== БЕГА ТАРАКАНОВ ==========

async def tavern_race_menu_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Меню выбора таракана"""
    query = update.callback_query
    user_id = query.from_user.id
    crumbs = dice_service.get_crumbs(user_id)
    stats = dice_service.get_player_stats(user_id)
    total_profit = stats.total_crumbs_won - stats.total_crumbs_lost
    profit_emoji = "📈" if total_profit >= 0 else "📉"

    text = f"""🪳 *БЕГА ТАРАКАНОВ*

_Четыре усатых бегуна готовятся к забегу!_
_Ставь на своего чемпиона и болей за него._

🧀 Крошки: *{crumbs:,}*
{profit_emoji} Итог в таверне: *{total_profit:+,}* 🧀

💡 _Совет от Ильяски:_
{random.choice([
    "«Шустрик быстрый но нервный. Усач — стабильный середняк.»",
    "«Прух выигрывает когда на него никто не ставит. Проверено!»",
    "«Шестиногий — читер но я никому не говорила.»",
    "«Ставь на того кто жрёт больше всех перед забегом!»",
    "«Говорят если поставить на всех сразу — точно проиграешь.»",
    "«Победитель прошлого забега редко выигрывает дважды.»",
    "«Тараканы чувствуют страх. Не бойся ставить по-крупному!»",
    "«После пива они бегают быстрее. Или это только кажется.»",
])}

*Выбери своего чемпиона:*"""

    await query.message.delete()
    try:
        with open(TAVERN_RACE_IMAGE, "rb") as photo:
            await context.bot.send_photo(
                chat_id=user_id, photo=photo, caption=text,
                parse_mode=constants.ParseMode.MARKDOWN,
                reply_markup=get_race_menu_keyboard()
            )
    except:
        await context.bot.send_message(
            chat_id=user_id, text=text,
            parse_mode=constants.ParseMode.MARKDOWN,
            reply_markup=get_race_menu_keyboard()
        )

async def tavern_race_pick_handler(update: Update, context: ContextTypes.DEFAULT_TYPE, roach_id: str):
    """Выбор ставки для таракана"""
    query = update.callback_query
    user_id = query.from_user.id
    context.user_data['race_roach'] = roach_id

    roach = next((r for r in COCKROACHES if r["id"] == roach_id), None)
    roach_name = roach["name"] if roach else roach_id

    text = f"""🪳 *БЕГА ТАРАКАНОВ*

Ты выбрал: {roach_name}

*Выбери ставку:*"""

    await query.message.delete()
    await context.bot.send_message(
        chat_id=user_id, text=text,
        parse_mode=constants.ParseMode.MARKDOWN,
        reply_markup=get_race_bet_keyboard(roach_id)
    )


async def tavern_race_start_handler(update: Update, context: ContextTypes.DEFAULT_TYPE, roach_id: str, bet: int):
    """Запуск забега"""
    query = update.callback_query
    user_id = query.from_user.id

    race_id = tavern_race_service.create_race(user_id, bet, roach_id)
    if not race_id:
        await query.answer("❌ Недостаточно крошек!", show_alert=True)
        return

    context.user_data['race_id'] = race_id
    context.user_data['race_bet'] = bet

    await query.answer(f"🪳 Ставка {bet} 🧀 принята! Забег начинается!")
    await query.message.delete()

    # Шаг 1
    race_data = tavern_race_service.process_race_step(race_id)
    if race_data["finished"]:
        text = tavern_race_service.get_race_result_text(race_data)
        await context.bot.send_message(
            chat_id=user_id, text=text,
            parse_mode=constants.ParseMode.MARKDOWN,
            reply_markup=get_race_result_keyboard()
        )
    else:
        text = tavern_race_service.get_race_positions_text(race_data)
        text += "\n_Забег продолжается..._"
        msg = await context.bot.send_message(
            chat_id=user_id, text=text,
            parse_mode=constants.ParseMode.MARKDOWN
        )
        # Анимация — ещё 2 шага
        for _ in range(2):
            await asyncio.sleep(1.5)
            race_data = tavern_race_service.process_race_step(race_id)
            if race_data["finished"]:
                text = tavern_race_service.get_race_result_text(race_data)
                await msg.delete()
                await context.bot.send_message(
                    chat_id=user_id, text=text,
                    parse_mode=constants.ParseMode.MARKDOWN,
                    reply_markup=get_race_result_keyboard()
                )
                return
            else:
                text = tavern_race_service.get_race_positions_text(race_data)
                try:
                    await msg.edit_text(text, parse_mode=constants.ParseMode.MARKDOWN)
                except:
                    pass

        # Финальный шаг
        await asyncio.sleep(1.5)
        race_data = tavern_race_service.process_race_step(race_id)
        text = tavern_race_service.get_race_result_text(race_data)
        try:
            await msg.delete()
        except:
            pass
        await context.bot.send_message(
            chat_id=user_id, text=text,
            parse_mode=constants.ParseMode.MARKDOWN,
            reply_markup=get_race_result_keyboard()
        )


# ========== ВВОД СТАВКИ ==========

async def handle_bet_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if not context.user_data.get('awaiting_bet'): return
    context.user_data['awaiting_bet'] = False
    try:
        bet = int(update.message.text)
        if bet <= 0: raise ValueError
    except:
        await update.message.reply_text("❌ Ставка должна быть положительным числом!")
        return
    context.user_data['dice_bet'] = bet
    await update.message.delete()
    await start_dice_game(update, context, user_id, bet)


async def cancel_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['awaiting_bet'] = False
    await update.message.reply_text("❌ Ввод ставки отменён.")