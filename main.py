#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import re
import logging
import os
import sqlite3
import platform
import subprocess
import sys
from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, constants
from telegram.error import NetworkError, TimedOut
from telegram.ext import (
    Application,
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    filters,
    ContextTypes
)

from config import TOKEN, LOG_FILE, MIN_PLAYERS, MAX_PLAYERS
from handlers.commands import start, help_command, rat_top, rat_me, crumbs_command, handle_nickname_input
from handlers.game_rat import (
    rat_start, rat_stop, rat_rules,
    handle_rat_kill, handle_rat_kill_none,
    handle_rat_vote, handle_rat_vote_skip,
    handle_ghost_vote, back_to_game,
    show_consumables_menu, handle_use_consumable,
    show_player_selection_for_item, handle_item_target_selection,
    show_day_shot_menu, handle_day_shot,
    handle_dead_message,
    show_chests_menu, handle_open_chest,
    escape_markdown,
    active_games,
    night_phase
)
from handlers.instagram import handle_message, shpite_handler
from handlers.callbacks import button_callback
from handlers.tunnel import tunnel_command, register_tunnel_handlers
from handlers.tunnel_coop import handle_join_boss
from handlers.profile import (
    profile_command, inventory_command, achievements_command, equipment_command,
    item_info_command
)
from handlers.shop import shop_command
from handlers.daily import daily_command
from handlers.clan import clan_command, clan_message_handler
from handlers.dice import dice_command, dice_callback, handle_bet_input, cancel_command

sys.path.append('/root/bot')

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(levelname)-8s | %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
    handlers=[
        logging.FileHandler(LOG_FILE, encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


async def error_handler(update, context):
    error = context.error
    if isinstance(error, (NetworkError, TimedOut)):
        logger.warning(f"⚠️ Сетевая ошибка: {error}")
    elif "Conflict" in str(error):
        logger.warning("⚠️ Запущено несколько экземпляров бота!")
    else:
        logger.error(f"❌ Ошибка: {error}", exc_info=True)


def get_server_info():
    """Получает информацию о сервере"""
    info = {}
    info['time'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    info['timezone'] = datetime.now().astimezone().tzname()
    info['system'] = platform.system()
    info['release'] = platform.release()
    info['machine'] = platform.machine()
    
    try:
        df = subprocess.check_output(['df', '-h', '/']).decode().strip().split('\n')[1]
        usage = df.split()[4].replace('%', '')
        info['disk_usage'] = f"{usage}%"
    except:
        info['disk_usage'] = "N/A"
    
    try:
        mem = subprocess.check_output(['free', '-m']).decode().strip().split('\n')[1]
        mem_parts = mem.split()
        total = int(mem_parts[1])
        used = int(mem_parts[2])
        info['memory'] = f"{used}/{total} MB ({(used/total)*100:.1f}%)"
    except:
        info['memory'] = "N/A"
    
    info['python'] = platform.python_version()
    return info


def run_startup_checks():
    """Полная проверка всех систем при запуске"""
    server_info = get_server_info()
    
    print("=" * 80)
    print("🔍 ЗАПУСК ПРОВЕРКИ ВСЕХ СИСТЕМ РАТЛЯНДИИ")
    print("=" * 80)
    
    print("\n🖥️ ИНФОРМАЦИЯ О СЕРВЕРЕ")
    print("-" * 80)
    print(f"   🕐 Время сервера: {server_info['time']} ({server_info['timezone']})")
    print(f"   💻 Система: {server_info['system']} {server_info['release']} ({server_info['machine']})")
    print(f"   🐍 Python: {server_info['python']}")
    print(f"   💾 Диск: {server_info['disk_usage']}")
    print(f"   🧠 Память: {server_info['memory']}")
    
    print("\n🗄️ 1. ПРОВЕРКА БАЗЫ ДАННЫХ")
    print("-" * 80)
    
    DB_FILE = "/root/bot/ratings.db"
    if not os.path.exists(DB_FILE):
        print(f"❌ Файл БД не найден: {DB_FILE}")
    else:
        size = os.path.getsize(DB_FILE) / 1024
        print(f"✅ Файл БД найден: {size:.1f} KB")
        
        try:
            conn = sqlite3.connect(DB_FILE)
            c = conn.cursor()
            
            tables = [
                'ratings', 'inventory', 'equipment', 'user_achievements',
                'user_stats', 'user_titles', 'user_active_title', 'user_currency',
                'daily_rewards', 'dice_stats', 'dice_rewards_claimed',
                'clans', 'clan_members', 'match_history'
            ]
            
            total_players = 0
            total_games = 0
            total_kills = 0
            total_crumbs = 0
            
            for table in tables:
                c.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table}'")
                if c.fetchone():
                    c.execute(f"SELECT COUNT(*) FROM {table}")
                    count = c.fetchone()[0]
                    print(f"   ✅ {table:<22} {count:>6} записей")
                    if table == 'ratings':
                        total_players = count
                    elif table == 'match_history':
                        total_games = count
                else:
                    print(f"   ⚠️ {table:<22} НЕ СУЩЕСТВУЕТ (создастся автоматически)")
            
            try:
                c.execute("SELECT SUM(total_kills) FROM user_stats")
                total_kills = c.fetchone()[0] or 0
                c.execute("SELECT SUM(crumbs) FROM user_currency")
                total_crumbs = c.fetchone()[0] or 0
            except:
                pass
            
            conn.close()
            
            print(f"\n   👥 ВСЕГО ИГРОКОВ: {total_players}")
            print(f"   🎮 ВСЕГО ИГР СЫГРАНО: {total_games}")
            print(f"   💀 ВСЕГО УБИЙСТВ: {total_kills}")
            print(f"   🧀 КРОШЕК В ОБРАЩЕНИИ: {total_crumbs}")
            
        except Exception as e:
            print(f"❌ Ошибка подключения к БД: {e}")
    
    print("\n🖼️ 2. ПРОВЕРКА КАРТИНОК")
    print("-" * 80)
    
    IMAGES_DIR = "/root/bot/images"
    AVATARS_DIR = "/root/bot/images/avatars"
    CHESTS_DIR = "/root/bot/images/chests"
    TUNNEL_MONSTERS_DIR = "/root/bot/images/tunnel_monsters"
    
    main_images = [
        "mice_win.jpg", "mice_win_2.jpg", "mice_win_3.jpg", "mice_win_4.jpg",
        "rat_win.jpg", "rat_win_2.jpg", "rat_win_3.jpg", "rat_win_4.jpg",
        "rat_kill.jpg", "rat_kill_2.jpg", "rat_kill_3.jpg", "rat_kill_4.jpg",
        "night.jpg", "day.jpg", "voting.jpg", "lobby.jpg", "rules.jpg",
        "role_cards.jpg", "item_drop.jpg", "leaderboard.jpg",
        "profile.jpg", "achievement_hall.jpg", "inventory.jpg",
        "equipment.jpg", "rat_choose.jpg", "use_item_prompt.jpg",
        "loading.jpg", "level_up.jpg", "shop.jpg", "tunnel_entrance.jpg",
        "daily_reward.jpg", "clan.jpg", "dice_game.jpg", "dice_1.jpg",
        "city_main.jpg", "weapon_drop.jpg", "consumable_drop.jpg"
    ]
    
    if os.path.exists(IMAGES_DIR):
        found_main = sum(1 for img in main_images if os.path.exists(os.path.join(IMAGES_DIR, img)))
        print(f"   ✅ Основные картинки: {found_main}/{len(main_images)}")
        
        avatar_files = [
            "level_1_4.jpg", "level_5_9.jpg", "level_10_14.jpg",
            "level_15_19.jpg", "level_20_24.jpg", "level_25_29.jpg",
            "level_30_39.jpg", "level_40_49.jpg", "level_50_74.jpg",
            "level_75_99.jpg", "level_100.jpg"
        ]
        
        if os.path.exists(AVATARS_DIR):
            found_avatars = sum(1 for ava in avatar_files if os.path.exists(os.path.join(AVATARS_DIR, ava)))
            print(f"   ✅ Аватарки по уровням: {found_avatars}/{len(avatar_files)}")
        else:
            print(f"   ⚠️ Папка с аватарками не найдена")
        
        chest_files = ["chest_common.jpg", "chest_rare.jpg", "chest_epic.jpg", "chest_legendary.jpg", "chest_mythic.jpg"]
        if os.path.exists(CHESTS_DIR):
            found_chests = sum(1 for ch in chest_files if os.path.exists(os.path.join(CHESTS_DIR, ch)))
            print(f"   ✅ Картинки сундуков: {found_chests}/{len(chest_files)}")
        
        monster_files = [
            "blind_mole.jpg", "giant_woodlouse.jpg", "earthworm.jpg",
            "rustler.jpg", "moldling.jpg", "renegade_rat.jpg",
            "scolopendra.jpg", "grinder_beetle.jpg", "giant_slug.jpg",
            "vampire_bat.jpg", "weaver_spider.jpg", "armadillo_centipede.jpg",
            "rat_ghoul.jpg", "giant_cockroach.jpg", "sewer_leech.jpg",
            "black_ferret.jpg", "two_headed_rat.jpg", "basement_snake.jpg",
            "baby_rat.jpg", "old_blind_cat.jpg"
        ]
        if os.path.exists(TUNNEL_MONSTERS_DIR):
            found_monsters = sum(1 for m in monster_files if os.path.exists(os.path.join(TUNNEL_MONSTERS_DIR, m)))
            print(f"   ✅ Картинки монстров: {found_monsters}/{len(monster_files)}")
        else:
            print(f"   ⚠️ Папка с монстрами не найдена")
        
        total_size = 0
        for root, dirs, files in os.walk(IMAGES_DIR):
            for file in files:
                if file.endswith(('.jpg', '.png', '.jpeg')):
                    total_size += os.path.getsize(os.path.join(root, file))
        print(f"   📦 Общий размер картинок: {total_size / (1024*1024):.1f} MB")
    else:
        print(f"   ❌ Папка с картинками не найдена")
    
    print("\n📦 3. ПРОВЕРКА ИМПОРТОВ МОДУЛЕЙ")
    print("-" * 80)
    
    modules_to_check = [
        ("handlers.game_rat", "game_rat.py"),
        ("handlers.profile", "profile.py"),
        ("handlers.commands", "commands.py"),
        ("handlers.callbacks", "callbacks.py"),
        ("handlers.inventory", "inventory.py"),
        ("handlers.items", "items.py"),
        ("handlers.achievements_data", "achievements_data.py"),
        ("handlers.titles", "titles.py"),
        ("handlers.effects", "effects.py"),
        ("handlers.shop", "shop.py"),
        ("handlers.daily", "daily.py"),
        ("handlers.clan", "clan.py"),
        ("handlers.dice", "dice.py"),
        ("handlers.city", "city.py"),
        ("handlers.tunnel", "tunnel.py"),
        ("handlers.tunnel_monsters", "tunnel_monsters.py"),
        ("handlers.tunnel_battle", "tunnel_battle.py"),
        ("handlers.tunnel_rooms", "tunnel_rooms.py"),
        ("handlers.tunnel_coop", "tunnel_coop.py"),
        ("database", "database.py"),
        ("config", "config.py"),
    ]
    
    for module, filename in modules_to_check:
        try:
            __import__(module)
            print(f"   ✅ {filename:<25} OK")
        except Exception as e:
            print(f"   ❌ {filename:<25} ОШИБКА: {str(e)[:40]}")
    
    print("\n⚙️ 4. ПРОВЕРКА КОНФИГУРАЦИИ ИГРЫ")
    print("-" * 80)
    
    try:
        from config import TOKEN, MIN_PLAYERS, MAX_PLAYERS, NIGHT_TIME, DAY_TIME, VOTE_TIME
        print(f"   ✅ TOKEN: {TOKEN[:10]}...{TOKEN[-10:]}")
        print(f"   ✅ Игроков: от {MIN_PLAYERS} до {MAX_PLAYERS}")
        print(f"   ✅ Фазы: Ночь {NIGHT_TIME}с / День {DAY_TIME}с / Голосование {VOTE_TIME}с")
    except Exception as e:
        print(f"   ❌ Ошибка конфигурации: {e}")
    
    print("\n🎒 5. ПРОВЕРКА ФУНКЦИЙ ИНВЕНТАРЯ")
    print("-" * 80)
    
    try:
        from handlers.inventory import (
            get_crumbs, add_crumbs, add_xp, get_user_xp,
            get_level_from_xp, add_item, get_inventory, get_available_chests, open_chest
        )
        from handlers.items import ALL_ITEMS, EQUIPMENT, CONSUMABLES, CHESTS
        print("   ✅ Все функции инвентаря импортируются")
        print(f"   📦 Всего предметов в игре: {len(ALL_ITEMS)}")
        print(f"      ├─ Экипировка: {len(EQUIPMENT)}")
        print(f"      ├─ Расходники: {len(CONSUMABLES)}")
        print(f"      └─ Сундуки: {len(CHESTS)}")
        
        test_user = 185185047
        crumbs = get_crumbs(test_user)
        xp = get_user_xp(test_user)
        level = get_level_from_xp(xp)
        print(f"\n   ✅ Тестовый пользователь {test_user}:")
        print(f"      🧀 Крошки: {crumbs}")
        print(f"      ✨ Опыт: {xp} XP")
        print(f"      ⭐ Уровень: {level}")
        
    except Exception as e:
        print(f"   ❌ Ошибка инвентаря: {e}")
    
    print("\n🏆 6. ПРОВЕРКА ДОСТИЖЕНИЙ")
    print("-" * 80)
    
    try:
        from handlers.achievements_data import ACHIEVEMENTS
        from handlers.titles import TITLES
        print(f"   ✅ Достижений: {len(ACHIEVEMENTS)}")
        print(f"   ✅ Титулов: {len(TITLES)}")
        
        rarity_count = {}
        for ach in ACHIEVEMENTS.values():
            rar = ach.get('rarity', 'common')
            rarity_count[rar] = rarity_count.get(rar, 0) + 1
        print(f"   📊 По редкостям: {rarity_count}")
    except Exception as e:
        print(f"   ❌ Ошибка достижений: {e}")
    
    print("\n" + "=" * 80)
    print("✅ ПОЛНАЯ ПРОВЕРКА ЗАВЕРШЕНА! ЗАПУСК БОТА...")
    print("=" * 80)

async def smart_text_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Единый обработчик текстовых сообщений"""
    text = update.message.text.strip() if update.message.text else ""
    
    if context.user_data.get("awaiting_nickname"):
        await handle_nickname_input(update, context)
        return
    
    if re.search(r'(?i)шпите', text):
        await shpite_handler(update, context)
        return
    
    if context.user_data.get("awaiting_bet"):
        await handle_bet_input(update, context)
        return
    
    if 'instagram.com' in text:
        await handle_message(update, context)
        return
    
    await clan_message_handler(update, context)

def main():
    run_startup_checks()
    
    print("\n" + "=" * 80)
    print("🐀 РАТЛЯНДИЯ — INSTAGRAM + ИГРА «КРЫСА» + SQLITE")
    print("=" * 80)
    print(f"📅 Запуск: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"🕐 Время сервера: {datetime.now().astimezone().tzname()}")
    print("=" * 80)

    app = ApplicationBuilder() \
        .token(TOKEN) \
        .connect_timeout(30) \
        .read_timeout(30) \
        .write_timeout(30) \
        .build()

    # Общие команды
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("rat_top", rat_top))
    app.add_handler(CommandHandler("rat_me", rat_me))
    app.add_handler(CommandHandler("crumbs", crumbs_command))
    app.add_handler(CommandHandler("profile", profile_command))
    app.add_handler(CommandHandler("inventory", inventory_command))
    app.add_handler(CommandHandler("achievements", achievements_command))

    # ТУННЕЛИ И КООПЕРАТИВ
    app.add_handler(CommandHandler("tunnel", tunnel_command))
    app.add_handler(CommandHandler("join_boss", join_boss_command))

    # Игра
    app.add_handler(CommandHandler("rat_start", rat_start))
    app.add_handler(CommandHandler("rat_stop", rat_stop))
    app.add_handler(CommandHandler("rat_rules", rat_rules))

    # Новые команды
    app.add_handler(CommandHandler("shop", shop_command))
    app.add_handler(CommandHandler("daily", daily_command))
    app.add_handler(CommandHandler("clan", clan_command))
    app.add_handler(CommandHandler("dice", dice_command))
    app.add_handler(CommandHandler("cancel", cancel_command))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_bet_input), group=1)

    # 🔥 ОБРАБОТЧИК ДЛЯ КАРТОЧЕК ПРЕДМЕТОВ /i_<item_id>
    app.add_handler(MessageHandler(filters.Regex(r'^/i_[a-zA-Z0-9_]+$'), item_info_command))

    # КОЛБЭКИ ИГРЫ
    app.add_handler(CallbackQueryHandler(
        lambda u, c: handle_rat_kill(u, c, int(u.callback_query.data.split('_')[2])),
        pattern=r"^rat_kill_\d+$"
    ))
    app.add_handler(CallbackQueryHandler(handle_rat_kill_none, pattern="^rat_kill_none$"))
    app.add_handler(CallbackQueryHandler(
        lambda u, c: handle_rat_vote(u, c, int(u.callback_query.data.split('_')[2])),
        pattern=r"^rat_vote_\d+$"
    ))
    app.add_handler(CallbackQueryHandler(handle_rat_vote_skip, pattern="^rat_vote_skip$"))
    app.add_handler(CallbackQueryHandler(
        lambda u, c: handle_ghost_vote(u, c, int(u.callback_query.data.split('_')[2])),
        pattern=r"^ghost_vote_\d+$"
    ))
    app.add_handler(CallbackQueryHandler(show_consumables_menu, pattern="^use_item_menu$"))
    app.add_handler(CallbackQueryHandler(
        lambda u, c: handle_use_consumable(u, c, u.callback_query.data.split('_')[2]),
        pattern=r"^use_consumable_.*"
    ))
    app.add_handler(CallbackQueryHandler(
        lambda u, c: show_player_selection_for_item(u, c, u.callback_query.data.split('_')[2]),
        pattern=r"^item_menu_.*"
    ))
    app.add_handler(CallbackQueryHandler(
        lambda u, c: handle_item_target_selection(u, c, 
            item_id=u.callback_query.data.split('_')[2],
            target_id=int(u.callback_query.data.split('_')[3])
        ),
        pattern=r"^item_target_.*"
    ))
    app.add_handler(CallbackQueryHandler(show_day_shot_menu, pattern="^day_shot_menu$"))
    app.add_handler(CallbackQueryHandler(
        lambda u, c: handle_day_shot(u, c, int(u.callback_query.data.split('_')[2])),
        pattern=r"^day_shot_\d+$"
    ))
    app.add_handler(CallbackQueryHandler(handle_dead_message, pattern="^dead_message$"))
    app.add_handler(CallbackQueryHandler(handle_dead_message, pattern="^anon_message$"))
    app.add_handler(CallbackQueryHandler(show_chests_menu, pattern="^chests_menu$"))
    app.add_handler(CallbackQueryHandler(
        lambda u, c: handle_open_chest(u, c, u.callback_query.data.split('_')[2]),
        pattern=r"^open_chest_.*"
    ))
    
    # СПОСОБНОСТИ
    app.add_handler(CallbackQueryHandler(
        lambda u, c: show_player_selection_for_item(u, c, "reveal_role_temp"),
        pattern="^reveal_role_menu$"
    ))
    app.add_handler(CallbackQueryHandler(
        lambda u, c: show_player_selection_for_item(u, c, "awaken_temp"),
        pattern="^awaken_menu$"
    ))
    app.add_handler(CallbackQueryHandler(
        lambda u, c: show_player_selection_for_item(u, c, "catapult_temp"),
        pattern="^catapult_menu$"
    ))
    app.add_handler(CallbackQueryHandler(
        lambda u, c: show_player_selection_for_item(u, c, "net_trap_temp"),
        pattern="^net_trap_menu$"
    ))
    app.add_handler(CallbackQueryHandler(
        lambda u, c: show_player_selection_for_item(u, c, "trap_launch_temp"),
        pattern="^trap_launch_menu$"
    ))
    
    # ЛОББИ
    app.add_handler(CallbackQueryHandler(handle_lobby_join, pattern="^rat_lobby_join$"))
    app.add_handler(CallbackQueryHandler(handle_lobby_leave, pattern="^rat_lobby_leave$"))
    app.add_handler(CallbackQueryHandler(handle_lobby_start, pattern="^rat_lobby_start$"))
    app.add_handler(CallbackQueryHandler(back_to_game, pattern="^back_to_game$"))

    # 🔥 ВАЖНО! СНАЧАЛА ОСНОВНОЙ КОЛБЭК, ПОТОМ ТУННЕЛИ!
    app.add_handler(CallbackQueryHandler(button_callback))
    
    # ТУННЕЛИ (после основного колбэка!)
    register_tunnel_handlers(app)

    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, smart_text_handler))

    print("\n✅ Бот запущен!")
    print("📱 @testpasha_bot")
    print("🗄️ SQLite активен!")
    print("🏰 Город | 🏪 Магазин | 🎁 Ежедневная | 🎲 Кости | 🛡️ Гильдия | 🕳️ Туннели")
    print("📦 Сундуки работают!")
    print("🐀 Ратляндия v0.0.5 — КООПЕРАТИВНЫЙ РЕЖИМ!")
    print("=" * 80)

    app.run_polling(drop_pending_updates=True)


# ========== ОБРАБОТЧИКИ ЛОББИ ==========

async def handle_lobby_join(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    user_name = query.from_user.full_name
    chat_id = query.message.chat_id
    
    game = active_games.get(chat_id)
    if not game or game.phase != "lobby":
        await query.answer("❌ Игра уже началась!", show_alert=True)
        return
    
    if game.add_player(user_id, user_name):
        await query.answer("✅ Ты присоединился!")
        keyboard = [
            [InlineKeyboardButton("✅ Присоединиться", callback_data="rat_lobby_join"),
             InlineKeyboardButton("👋 Выйти", callback_data="rat_lobby_leave")],
            [InlineKeyboardButton("🎮 Начать игру", callback_data="rat_lobby_start")]
        ]
        caption = f"🐀 *РАТЛЯНДИЯ v0.0.5*\n\nИгроков: {len(game.players)}/{MAX_PLAYERS}\nСоздатель: {escape_markdown(game.players[game.creator_id]['name'])}\n\nНажмите кнопку чтобы присоединиться!"
        try:
            await query.message.edit_caption(
                caption=caption,
                parse_mode=constants.ParseMode.MARKDOWN,
                reply_markup=InlineKeyboardMarkup(keyboard)
            )
        except:
            pass
    else:
        await query.answer("❌ Не удалось присоединиться!", show_alert=True)


async def handle_lobby_leave(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    chat_id = query.message.chat_id
    
    game = active_games.get(chat_id)
    if not game or game.phase != "lobby":
        await query.answer("❌ Игра уже началась!", show_alert=True)
        return
    
    if game.remove_player(user_id):
        await query.answer("👋 Ты вышел!")
        keyboard = [
            [InlineKeyboardButton("✅ Присоединиться", callback_data="rat_lobby_join"),
             InlineKeyboardButton("👋 Выйти", callback_data="rat_lobby_leave")],
            [InlineKeyboardButton("🎮 Начать игру", callback_data="rat_lobby_start")]
        ]
        caption = f"🐀 *РАТЛЯНДИЯ v0.0.5*\n\nИгроков: {len(game.players)}/{MAX_PLAYERS}\nСоздатель: {escape_markdown(game.players[game.creator_id]['name'])}\n\nНажмите кнопку чтобы присоединиться!"
        try:
            await query.message.edit_caption(
                caption=caption,
                parse_mode=constants.ParseMode.MARKDOWN,
                reply_markup=InlineKeyboardMarkup(keyboard)
            )
        except:
            pass
    else:
        await query.answer("❌ Нельзя выйти (создатель не может выйти)!", show_alert=True)


async def handle_lobby_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    chat_id = query.message.chat_id
    
    game = active_games.get(chat_id)
    if not game or game.phase != "lobby":
        await query.answer("❌ Игра уже началась!", show_alert=True)
        return
    
    if user_id != game.creator_id:
        await query.answer("❌ Только создатель может начать!", show_alert=True)
        return
    
    if not game.start_game():
        await query.answer(f"❌ Нужно минимум {MIN_PLAYERS} игроков!", show_alert=True)
        return
    
    await query.answer("🎮 Игра начинается!")
    await query.message.delete()
    await night_phase(context, chat_id)


async def join_boss_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Команда /join_boss <код>"""
    args = context.args
    if not args:
        await update.message.reply_text("❌ Укажи код приглашения!\nПример: `/join_boss abc123`", parse_mode=constants.ParseMode.MARKDOWN)
        return
    
    invite_id = args[0]
    await handle_join_boss(update, context, invite_id)


if __name__ == "__main__":
    main()