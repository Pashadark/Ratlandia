"""
ГЛАВНЫЙ РОУТЕР — регистрирует все обработчики
Архитектура: тонкая прослойка, вся логика в services/
"""

from telegram.ext import (
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    filters,
)

from config import TOKEN
from handlers.logger import logger

# Player
from handlers.player.commands import start, help_command, rat_top, crumbs_command, handle_nickname_input
from handlers.player.profile import (
    profile_command, inventory_command, achievements_command, equipment_command,
    item_info_command, history_command
)
from handlers.player.callbacks import button_callback

# Instagram
from handlers.instagram import handle_message, shpite_handler

# City
from handlers.city.commands import city_menu, city_gates_menu
from handlers.city.shop import shop_command
from handlers.city.church import city_church_menu, church_rest, church_leave
from handlers.city.daily import daily_command

# Game (туннели)
from handlers.game.commands import (
    tunnel_command, register_tunnel_handlers, show_stats_menu, start_new_run
)
from handlers.game.coop import handle_join_boss

# Blacksmith
from handlers.blacksmith.commands import (
    blacksmith_menu, forge_select_recipe, forge_craft, forge_show_resources,
    forge_show_recipes, forge_sharpen, forge_engrave, forge_fortune,
    forge_show_resources_category, forge_show_resources_all
)

# Clan
from handlers.clan.commands import (
    clan_command, clan_message_handler, clan_top_callback, clan_create_menu
)

# Achievements & Titles
from handlers.achievements.commands import titles_command

# Dice (таверна)
from handlers.dice.dice import dice_command, dice_callback, handle_bet_input, cancel_command

# Hall of Fame
from handlers.hall_of_fame import hall_of_fame

# Bug Report
from handlers.bug_report.commands import (
    bag_command, handle_bug_input, handle_bug_photo, bag_stats_command, bag_list_command
)


async def error_handler(update, context):
    from telegram.error import NetworkError, TimedOut
    error = context.error
    if isinstance(error, (NetworkError, TimedOut)):
        logger.warning(f"⚠️ Сетевая ошибка: {error}")
    elif "Conflict" in str(error):
        logger.warning("⚠️ Запущено несколько экземпляров бота!")
    else:
        logger.error(f"❌ Ошибка: {error}", exc_info=True)


async def smart_text_handler(update, context):
    text = update.message.text.strip() if update.message.text else ""
    user_id = update.effective_user.id

    import sqlite3
    conn = sqlite3.connect("/root/bot/ratings.db")
    c = conn.cursor()
    c.execute("CREATE TABLE IF NOT EXISTS banned_users (user_id INTEGER PRIMARY KEY, nickname TEXT, banned_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)")
    c.execute("SELECT user_id FROM banned_users WHERE user_id = ?", (user_id,))
    if c.fetchone():
        conn.close()
        return
    conn.close()

    if context.user_data.get("bug_report"):
        if await handle_bug_input(update, context):
            return

    if context.user_data.get("awaiting_nickname"):
        await handle_nickname_input(update, context)
        return

    if context.user_data.get("awaiting_bet"):
        await handle_bet_input(update, context)
        return

    await clan_message_handler(update, context)


async def join_boss_command(update, context):
    args = context.args
    if not args:
        await update.message.reply_text(
            "❌ Укажи код приглашения!\nПример: `/join_boss abc123`",
            parse_mode="Markdown"
        )
        return
    await handle_join_boss(update, context, args[0])


def register_all_handlers(app):
    """Регистрирует все обработчики в приложении"""

    # ========== ОСНОВНЫЕ КОМАНДЫ ==========
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("profile", profile_command))
    app.add_handler(CommandHandler("inventory", inventory_command))
    app.add_handler(CommandHandler("equipment", equipment_command))
    app.add_handler(CommandHandler("achievements", achievements_command))
    app.add_handler(CommandHandler("crumbs", crumbs_command))
    app.add_handler(CommandHandler("top", rat_top))
    app.add_handler(CommandHandler("bag", bag_command))
    app.add_handler(CommandHandler("bags", bag_list_command))
    app.add_handler(CommandHandler("bagstats", bag_stats_command))

    # ========== ГОРОД ==========
    async def city_cmd(update, context):
        from keyboards.inline.city import get_city_keyboard
        from telegram import constants
        text = """🏰 *ДОБРО ПОЖАЛОВАТЬ В ГОРОД*

_Ты — один из жителей этого мира. Выбери свой путь, испытай удачу и стань легендой Ратляндии!_

Выбери куда пойти:"""
        keyboard = get_city_keyboard()
        try:
            with open("/root/bot/images/city_main.jpg", "rb") as photo:
                await update.message.reply_photo(
                    photo=photo, caption=text,
                    parse_mode=constants.ParseMode.MARKDOWN,
                    reply_markup=keyboard
                )
        except:
            await update.message.reply_text(
                text=text, parse_mode=constants.ParseMode.MARKDOWN,
                reply_markup=keyboard
            )
    app.add_handler(CommandHandler("city", city_cmd))
    app.add_handler(CommandHandler("shop", shop_command))
    app.add_handler(CommandHandler("daily", daily_command))

    # ========== ТУННЕЛИ ==========
    app.add_handler(CommandHandler("tunnel", tunnel_command))
    app.add_handler(CommandHandler("join_boss", join_boss_command))

    async def tunnel_stats_cmd(update, context):
        await show_stats_menu(update, context, update.effective_user.id)
    app.add_handler(CommandHandler("tunnel_stats", tunnel_stats_cmd))

    async def tunnel_run_cmd(update, context):
        await start_new_run(update, context, update.effective_user.id)
    app.add_handler(CommandHandler("tunnel_run", tunnel_run_cmd))

    # ========== КУЗНИЦА ==========
    async def forge_cmd(update, context):
        await blacksmith_menu(update, context)
    app.add_handler(CommandHandler("forge", forge_cmd))

    async def forge_resources_cmd(update, context):
        await forge_show_resources(update, context)
    app.add_handler(CommandHandler("forge_resources", forge_resources_cmd))

    async def forge_recipes_cmd(update, context):
        await forge_show_recipes(update, context)
    app.add_handler(CommandHandler("forge_recipes", forge_recipes_cmd))

    async def forge_sharpen_cmd(update, context):
        await forge_sharpen(update, context)
    app.add_handler(CommandHandler("forge_sharpen", forge_sharpen_cmd))

    # ========== ЦЕРКОВЬ ==========
    async def church_cmd(update, context):
        await city_church_menu(update, context)
    app.add_handler(CommandHandler("church", church_cmd))

    # ========== КЛАНЫ ==========
    app.add_handler(CommandHandler("clan", clan_command))
    async def clan_top_cmd(update, context):
        await clan_top_callback(update, context)
    app.add_handler(CommandHandler("clan_top", clan_top_cmd))
    async def clan_create_cmd(update, context):
        await clan_create_menu(update, context)
    app.add_handler(CommandHandler("clan_create", clan_create_cmd))

    # ========== ТИТУЛЫ И ИСТОРИЯ ==========
    app.add_handler(CommandHandler("titles", titles_command))
    app.add_handler(CommandHandler("history", history_command))

    # ========== ТАВЕРНА ==========
    app.add_handler(CommandHandler("dice", dice_command))
    app.add_handler(CommandHandler("cancel", cancel_command))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_bet_input), group=1)

    # ========== ЗАЛ СЛАВЫ ==========
    async def hall_cmd(update, context):
        await hall_of_fame(update, context)
    app.add_handler(CommandHandler("hall", hall_cmd))

    # ========== КАРТОЧКИ ПРЕДМЕТОВ ==========
    app.add_handler(MessageHandler(filters.Regex(r'^/i_[a-zA-Z0-9_+]+$'), item_info_command))

    # ========== ОСНОВНОЙ КОЛБЭК ==========
    app.add_handler(CallbackQueryHandler(button_callback))

    # ========== ТУННЕЛИ (колбэки) ==========
    register_tunnel_handlers(app)

    # ========== ОБРАБОТЧИК ФОТО (БАГ-РЕПОРТЫ) ==========
    app.add_handler(MessageHandler(filters.PHOTO, handle_bug_photo))

    # ========== ТЕКСТОВЫЕ СООБЩЕНИЯ ==========
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, smart_text_handler))

    # ========== ОШИБКИ ==========
    app.add_error_handler(error_handler)