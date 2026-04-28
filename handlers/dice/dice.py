"""Хендлеры для игры в кости (таверна)"""

import asyncio
import random
import sqlite3
from telegram import Update
from telegram.ext import ContextTypes
from telegram import constants

from services.dice import dice_service
from core.dice.engine import get_dice_engine
from keyboards.inline.dice import (
    get_bet_keyboard,
    get_play_again_keyboard,
    get_beer_keyboard,
    get_tournament_back_keyboard,
    get_custom_bet_back_keyboard
)
from core.dice.models import BetResult, DiceGameResult, GameMode

dice = get_dice_engine()

# Пути к картинкам
DICE_GAME_IMAGE = "/root/bot/images/dice_game.jpg"
DICE_WIN_IMAGE = "/root/bot/images/dice_win.jpg"
DICE_LOSE_IMAGE = "/root/bot/images/dice_lose.jpg"
BEER_DRINK_IMAGE = "/root/bot/images/beer_drink.jpg"


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


async def dice_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    
    if update.callback_query:
        query = update.callback_query
        user_id = query.from_user.id
        text = tavern_service.format_stats_message(user_id)
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
    
    text = tavern_service.format_stats_message(user_id)
    text += "\n\nВыбери ставку или введи `/dice [сумма]`:"
    try:
        with open(DICE_GAME_IMAGE, "rb") as photo:
            await update.message.reply_photo(
                photo=photo, caption=text,
                parse_mode=constants.ParseMode.MARKDOWN,
                reply_markup=get_bet_keyboard()
            )
    except:
        await update.message.reply_text(
            text, parse_mode=constants.ParseMode.MARKDOWN,
            reply_markup=get_bet_keyboard()
        )


async def dice_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
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
    crumbs = tavern_service.get_crumbs(user_id)
    if crumbs < bet:
        await query.answer(f"❌ Недостаточно крошек! Нужно {bet} 🧀", show_alert=True)
        return
    await query.message.delete()
    await play_dice_round(update, context, user_id, bet)


async def start_dice_game(update: Update, context: ContextTypes.DEFAULT_TYPE,
                          user_id: int, bet: int):
    crumbs = tavern_service.get_crumbs(user_id)
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
    stats = tavern_service.get_player_stats(user_id)
    daily_bonus = stats.daily_bonus_available
    
    if daily_bonus and not free_reroll:
        dice_service.claim_daily_bonus(user_id)
    
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
    
    crumbs = tavern_service.get_crumbs(user_id)
    
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


async def buy_beer(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    success, effect, drink_text = tavern_service.buy_beer(user_id)
    if not success:
        await query.answer(drink_text, show_alert=True)
        return
    
    effects_text = tavern_service.get_beer_effects_text(user_id)
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


async def show_tournament(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    leaders = dice_service.get_tournament_leaders(10)
    
    text = "🏆 *ТУРНИР КОСТЕЙ — ТОП-10*\n\n"
    for i, entry in enumerate(leaders, 1):
        medal = "🥇" if i == 1 else "🥈" if i == 2 else "🥉" if i == 3 else f"{i}."
        text += f"{medal} *{entry.user_name[:20]}*: {entry.total_crumbs_won} 🧀\n"
        text += f"   └─ {entry.wins}/{entry.games_played} побед\n\n"
    
    await query.message.delete()
    await context.bot.send_message(
        chat_id=user_id, text=text,
        parse_mode=constants.ParseMode.MARKDOWN,
        reply_markup=get_tournament_back_keyboard()
    )


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
    await start_dice_game(update, context, user_id, bet)


async def cancel_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['awaiting_bet'] = False
    await update.message.reply_text("❌ Ввод ставки отменён.")