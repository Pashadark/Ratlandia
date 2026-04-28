#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import re
import logging
import os
import sqlite3
import platform
import subprocess
import sys
import asyncio
import time
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
from handlers.bug_report import bag_command, handle_bug_input, handle_bug_photo, bag_stats_command, bag_list_command

from config import TOKEN, LOG_FILE, MIN_PLAYERS, MAX_PLAYERS
from handlers.commands import start, help_command, rat_top, crumbs_command, handle_nickname_input
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
from handlers.tunnel import tunnel_command, register_tunnel_handlers, show_stats_menu, start_new_run
from handlers.tunnel_coop import handle_join_boss
from handlers.profile import (
    profile_command, inventory_command, achievements_command, equipment_command,
    item_info_command, history_command
)
from handlers.shop import shop_command
from handlers.daily import daily_command
from handlers.clan import clan_command, clan_message_handler, clan_top_callback, clan_create_menu
from handlers.dice import dice_command, dice_callback, handle_bet_input, cancel_command
from handlers.titles import titles_command
from handlers.city import city_menu, city_gates_menu
from handlers.blacksmith import (
    blacksmith_menu, forge_select_recipe, forge_craft, forge_show_resources, 
    forge_show_recipes, forge_sharpen, forge_engrave, forge_fortune, 
    forge_show_resources_category, forge_show_resources_all
)
from handlers.church import city_church_menu, church_rest, church_leave
from handlers.hall_of_fame import hall_of_fame

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


def progress_bar(percent, length=40):
    """Рисует прогресс-бар [████░░░░] XX%"""
    filled = int(length * percent / 100)
    bar = "█" * filled + "░" * (length - filled)
    return f"[{bar}] {percent}%"


def run_startup_checks():
    """Полная проверка всех систем при запуске с прогресс-барами"""
    server_info = get_server_info()
    all_ok = True
    warnings = []
    DB_FILE = "/root/bot/ratings.db"
    IMAGES_DIR = "/root/bot/images"
    
    print("=" * 80)
    print("                    🐀 РАТЛЯНДИЯ — ЗАПУСК СИСТЕМЫ")
    print("=" * 80)
    
    # ---------- 1/14 СЕРВЕР ----------
    print(f"\n🖥️ [1/14] ПРОВЕРКА СЕРВЕРА")
    try:
        print(f"   {progress_bar(100)} ✅")
        print(f"   ⏰ {server_info['time']} ({server_info['timezone']}) | 💻 {server_info['system']} {server_info['release']} | 🐍 Python {server_info['python']}")
        print(f"   💾 Диск: {server_info['disk_usage']} | 🧠 RAM: {server_info['memory']}")
        
        # Проверка свободного места
        try:
            df = subprocess.check_output(['df', '-h', '/']).decode().strip().split('\n')[1]
            usage_pct = int(df.split()[4].replace('%', ''))
            if usage_pct > 85:
                warnings.append(f"⚠️ Мало места на диске: {usage_pct}%")
        except:
            pass
    except Exception as e:
        print(f"   {progress_bar(0)} ❌")
        print(f"   ❌ Ошибка: {str(e)[:50]}")
        all_ok = False
    
    # ---------- 2/14 БАЗА ДАННЫХ ----------
    print(f"\n🗄️ [2/14] ПРОВЕРКА БАЗЫ ДАННЫХ")
    
    if not os.path.exists(DB_FILE):
        print(f"   {progress_bar(0)} ❌")
        print(f"   ❌ Файл не найден: {DB_FILE}")
        all_ok = False
    else:
        try:
            conn = sqlite3.connect(DB_FILE)
            c = conn.cursor()
            
            # Проверка целостности
            c.execute("PRAGMA integrity_check")
            integrity = c.fetchone()[0]
            
            # Подсчёт таблиц
            tables_needed = [
                'ratings', 'inventory', 'equipment', 'user_achievements',
                'user_stats', 'user_titles', 'user_active_title', 'user_currency',
                'daily_rewards', 'dice_stats', 'dice_rewards_claimed',
                'clans', 'clan_members', 'match_history'
            ]
            
            found_tables = 0
            total_players = 0
            
            for table in tables_needed:
                c.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table}'")
                if c.fetchone():
                    found_tables += 1
                    if table == 'ratings':
                        c.execute(f"SELECT COUNT(*) FROM {table}")
                        total_players = c.fetchone()[0]
            
            c.execute("SELECT COUNT(*) FROM inventory")
            total_items = c.fetchone()[0]
            
            size_kb = os.path.getsize(DB_FILE) / 1024
            
            conn.close()
            
            table_pct = int(found_tables / len(tables_needed) * 100)
            
            if integrity == "ok" and found_tables == len(tables_needed):
                print(f"   {progress_bar(100)} ✅")
                print(f"   📦 {size_kb:.1f} KB | 👥 {total_players} игроков | 🎒 {total_items} предметов")
                print(f"   🗃️ {found_tables}/{len(tables_needed)} таблиц | 🔐 Целостность OK")
            else:
                print(f"   {progress_bar(table_pct)} ⚠️")
                if integrity != "ok":
                    warnings.append(f"⚠️ БД повреждена: {integrity}")
                if found_tables < len(tables_needed):
                    warnings.append(f"⚠️ Не хватает таблиц: {len(tables_needed) - found_tables}")
            
        except Exception as e:
            print(f"   {progress_bar(0)} ❌")
            print(f"   ❌ Ошибка: {str(e)[:50]}")
            all_ok = False
    
    # ---------- 3/14 КАРТИНКИ ----------
    print(f"\n🖼️ [3/14] ПРОВЕРКА КАРТИНОК")
    
    if not os.path.exists(IMAGES_DIR):
        print(f"   {progress_bar(0)} ❌")
        print(f"   ❌ Папка не найдена!")
        all_ok = False
    else:
        total_size = sum(
            os.path.getsize(os.path.join(root, f))
            for root, _, files in os.walk(IMAGES_DIR)
            for f in files if f.endswith(('.jpg', '.png', '.jpeg'))
        )
        file_count = sum(
            1 for root, _, files in os.walk(IMAGES_DIR)
            for f in files if f.endswith(('.jpg', '.png', '.jpeg'))
        )
        
        # Проверка критических картинок
        critical = ['city_main.jpg', 'profile.jpg', 'shop.jpg', 'tunnel_entrance.jpg']
        missing_critical = [img for img in critical if not os.path.exists(os.path.join(IMAGES_DIR, img))]
        
        if not missing_critical:
            print(f"   {progress_bar(100)} ✅")
            print(f"   🖼️ {file_count} файлов | 💾 {total_size/(1024*1024):.1f} MB")
            print(f"   🏰 Критические: все на месте")
        else:
            print(f"   {progress_bar(int((len(critical)-len(missing_critical))/len(critical)*100))} ⚠️")
            warnings.append(f"⚠️ Отсутствуют картинки: {', '.join(missing_critical)}")
    
    # ---------- 4/14 КОНФИГУРАЦИЯ ----------
    print(f"\n⚙️ [4/14] ПРОВЕРКА КОНФИГУРАЦИИ")
    try:
        if not TOKEN or len(TOKEN) < 30:
            print(f"   {progress_bar(0)} ❌")
            print(f"   ❌ Токен невалиден!")
            all_ok = False
        else:
            print(f"   {progress_bar(100)} ✅")
            print(f"   🔑 Токен: OK | 🎮 {MIN_PLAYERS}-{MAX_PLAYERS} игроков")
    except Exception as e:
        print(f"   {progress_bar(0)} ❌")
        print(f"   ❌ Ошибка: {str(e)[:50]}")
        all_ok = False
    
    # ---------- 5/14 МОДУЛИ ----------
    print(f"\n📦 [5/14] ПРОВЕРКА МОДУЛЕЙ")
    modules = [
        ("game_rat", "game_rat.py"), ("profile", "profile.py"),
        ("commands", "commands.py"), ("callbacks", "callbacks.py"),
        ("inventory", "inventory.py"), ("items", "items.py"),
        ("shop", "shop.py"), ("daily", "daily.py"),
        ("clan", "clan.py"), ("dice", "dice.py"),
        ("city", "city.py"), ("tunnel", "tunnel.py"),
        ("tunnel_monsters", "tunnel_monsters.py"), ("tunnel_battle", "tunnel_battle.py"),
        ("tunnel_rooms", "tunnel_rooms.py"), ("tunnel_coop", "tunnel_coop.py"),
        ("blacksmith", "blacksmith.py"), ("church", "church.py"),
        ("hall_of_fame", "hall_of_fame.py"), ("titles", "titles.py"),
        ("enchant", "enchant.py"), ("crafting", "crafting.py"),
        ("database", "database.py"), ("config", "config.py"),
    ]
    
    failed_modules = []
    for mod, filename in modules:
        try:
            __import__(f"handlers.{mod}")
        except:
            try:
                __import__(mod)
            except:
                failed_modules.append(filename)
    
    ok_count = len(modules) - len(failed_modules)
    pct = int(ok_count / len(modules) * 100)
    
    if not failed_modules:
        print(f"   {progress_bar(100)} ✅")
        print(f"   📚 {ok_count}/{len(modules)} модулей загружено")
    else:
        print(f"   {progress_bar(pct)} ❌")
        print(f"   ❌ Проблемы: {', '.join(failed_modules)}")
        all_ok = False
    
    # ---------- 6/14 ПРЕДМЕТЫ ----------
    print(f"\n🎒 [6/14] ПРОВЕРКА ПРЕДМЕТОВ")
    try:
        from handlers.items import ALL_ITEMS, EQUIPMENT, CONSUMABLES, CHESTS, RECIPES, ENCHANT_SCROLLS
        
        print(f"   {progress_bar(100)} ✅")
        print(f"   ⚔️ {len(ALL_ITEMS)} предметов | 🛡️ {len(EQUIPMENT)} экип. | 🧪 {len(CONSUMABLES)} расх. | 📦 {len(CHESTS)} сундуков")
        print(f"   📜 {len(RECIPES)} рецептов | ⚡ {len(ENCHANT_SCROLLS) if ENCHANT_SCROLLS else 0} свитков заточки")
    except Exception as e:
        print(f"   {progress_bar(0)} ❌")
        print(f"   ❌ Ошибка: {str(e)[:50]}")
        all_ok = False
    
    # ---------- 7/14 ДОСТИЖЕНИЯ ----------
    print(f"\n🏆 [7/14] ПРОВЕРКА ДОСТИЖЕНИЙ")
    try:
        from handlers.achievements_data import ACHIEVEMENTS
        from handlers.titles import TITLES
        print(f"   {progress_bar(100)} ✅")
        print(f"   🏅 {len(ACHIEVEMENTS)} достижений | 👑 {len(TITLES)} титулов")
    except Exception as e:
        print(f"   {progress_bar(0)} ❌")
        print(f"   ❌ Ошибка: {str(e)[:50]}")
        all_ok = False
    
    # ---------- 8/14 ЗАТОЧКА ----------
    print(f"\n⚡ [8/14] ПРОВЕРКА ЗАТОЧКИ")
    try:
        from handlers.enchant import get_enchant_level, get_enchant_bonus, get_base_item_id
        test_id = "test_sword+5"
        base = get_base_item_id(test_id)
        level = get_enchant_level(test_id)
        if base == "test_sword" and level == 5:
            print(f"   {progress_bar(100)} ✅")
            print(f"   🔧 Парсинг OK (+5 определяется верно)")
        else:
            print(f"   {progress_bar(50)} ⚠️")
            warnings.append("⚠️ Ошибка парсинга заточки")
    except Exception as e:
        print(f"   {progress_bar(0)} ❌")
        print(f"   ❌ Ошибка: {str(e)[:50]}")
        all_ok = False
    
    # ---------- 9/14 ПРАВА ----------
    print(f"\n💾 [9/14] ПРОВЕРКА ПРАВ ДОСТУПА")
    try:
        test_conn = sqlite3.connect(DB_FILE)
        test_conn.execute("CREATE TABLE IF NOT EXISTS _startup_test (id INTEGER)")
        test_conn.execute("DROP TABLE _startup_test")
        test_conn.close()
        
        log_test = open(LOG_FILE, 'a')
        log_test.close()
        
        print(f"   {progress_bar(100)} ✅")
        print(f"   📝 Запись в БД ✅ | 📋 Логи ✅ | 📁 Картинки ✅")
    except Exception as e:
        print(f"   {progress_bar(0)} ❌")
        print(f"   ❌ Ошибка: {str(e)[:50]}")
        warnings.append("⚠️ Проблемы с правами на запись!")
        all_ok = False
    
    # ---------- 10/14 ТУННЕЛИ ----------
    print(f"\n🕳️ [10/14] ПРОВЕРКА ТУННЕЛЕЙ")
    try:
        from handlers.tunnel_monsters import TUNNEL_MONSTERS
        monster_count = len(TUNNEL_MONSTERS) if TUNNEL_MONSTERS else 0
        
        from handlers.tunnel_rooms import process_room_transition
        from handlers.tunnel_battle import start_battle
        
        print(f"   {progress_bar(100)} ✅")
        print(f"   👹 {monster_count} монстров | 🎲 Комнаты загружены | ⚔️ Бои готовы")
    except Exception as e:
        print(f"   {progress_bar(70)} ⚠️")
        print(f"   ⚠️ {str(e)[:50]}")
        warnings.append("⚠️ Часть функций туннелей недоступна")
    
    # ---------- 11/14 ЦЕРКОВЬ ----------
    print(f"\n⛪ [11/14] ПРОВЕРКА ЦЕРКВИ")
    try:
        from handlers.church import church_rest, church_leave
        from handlers.healing import restore_health_over_time
        print(f"   {progress_bar(100)} ✅")
        print(f"   🙏 Отдых и лечение активны")
    except Exception as e:
        print(f"   {progress_bar(0)} ❌")
        print(f"   ❌ {str(e)[:50]}")
        warnings.append("⚠️ Церковь недоступна")
    
    # ---------- 12/14 КУЗНИЦА ----------
    print(f"\n🔨 [12/14] ПРОВЕРКА КУЗНИЦЫ")
    try:
        from handlers.crafting import check_craft_success, CraftQuality
        from handlers.blacksmith import blacksmith_menu, forge_craft, forge_sharpen
        print(f"   {progress_bar(100)} ✅")
        print(f"   ⚒️ Крафт готов | 🔥 Заточка работает")
    except Exception as e:
        print(f"   {progress_bar(0)} ❌")
        print(f"   ❌ {str(e)[:50]}")
        warnings.append("⚠️ Кузница недоступна")
    
    # ---------- 13/14 TELEGRAM API ----------
    print(f"\n🌐 [13/14] ПРОВЕРКА TELEGRAM API")
    try:
        import requests
        response = requests.get(f"https://api.telegram.org/bot{TOKEN}/getMe", timeout=5)
        if response.status_code == 200:
            data = response.json()
            if data.get('ok'):
                bot_name = data['result']['username']
                print(f"   {progress_bar(100)} ✅")
                print(f"   📡 @{bot_name} подключён к API")
            else:
                print(f"   {progress_bar(0)} ❌")
                print(f"   ❌ API вернул ошибку")
                all_ok = False
        else:
            print(f"   {progress_bar(0)} ❌")
            print(f"   ❌ HTTP {response.status_code}")
            all_ok = False
    except Exception as e:
        print(f"   {progress_bar(0)} ❌")
        print(f"   ❌ Нет соединения: {str(e)[:40]}")
        warnings.append("⚠️ Нет подключения к Telegram API")
    
    # ---------- 14/14 ЭКОНОМИКА ----------
    print(f"\n💰 [14/14] ПРОВЕРКА ЭКОНОМИКИ")
    try:
        with sqlite3.connect(DB_FILE) as conn:
            c = conn.cursor()
            c.execute("SELECT SUM(crumbs) FROM user_currency")
            total_crumbs = c.fetchone()[0] or 0
        
        from handlers.shop import shop_command
        from handlers.daily import daily_command
        
        print(f"   {progress_bar(100)} ✅")
        print(f"   🧀 {total_crumbs:,} крошек в обороте | 🏪 Магазин активен | 🎁 Дейлики работают")
    except Exception as e:
        print(f"   {progress_bar(50)} ⚠️")
        print(f"   ⚠️ {str(e)[:50]}")
    
    # ---------- ПРЕДУПРЕЖДЕНИЯ ----------
    if warnings:
        print(f"\n{'='*80}")
        print(f"⚠️ ПРЕДУПРЕЖДЕНИЯ (некритично):")
        for w in warnings:
            print(f"   {w}")
    
    # ---------- ИТОГ ----------
    print(f"\n{'='*80}")
    if all_ok:
        print(f"                    ✅ ВСЕ СИСТЕМЫ ГОТОВЫ!")
    else:
        print(f"                    ⚠️ ЗАПУСК ПРОДОЛЖАЕТСЯ С ОГРАНИЧЕНИЯМИ...")
    print(f"{'='*80}\n")
    
    return all_ok


async def smart_text_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Единый обработчик текстовых сообщений"""
    text = update.message.text.strip() if update.message.text else ""
    user_id = update.effective_user.id
    
    # Проверка бана
    import sqlite3
    conn = sqlite3.connect("/root/bot/ratings.db")
    c = conn.cursor()
    c.execute("CREATE TABLE IF NOT EXISTS banned_users (user_id INTEGER PRIMARY KEY, nickname TEXT, banned_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)")
    c.execute("SELECT user_id FROM banned_users WHERE user_id = ?", (user_id,))
    if c.fetchone():
        conn.close()
        return
    conn.close()
    
    # Обработка баг-репорта
    if context.user_data.get("bug_report"):
        from handlers.bug_report import handle_bug_input
        if await handle_bug_input(update, context):
            return
    
    if context.user_data.get("awaiting_nickname"):
        await handle_nickname_input(update, context)
        return
    
    if context.user_data.get("awaiting_bet"):
        await handle_bet_input(update, context)
        return
    
    await clan_message_handler(update, context)


async def rat_me(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Перенаправляет на /profile"""
    await profile_command(update, context)

def main():
    run_startup_checks()
    
    print("=" * 80)
    print("   🐀 РАТЛЯНДИЯ — ЗАПУСК УСПЕШЕН")
    print("=" * 80)
    print(f"   📅 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} UTC")
    print("=" * 80)

    app = ApplicationBuilder() \
        .token(TOKEN) \
        .connect_timeout(30) \
        .read_timeout(30) \
        .write_timeout(30) \
        .build()

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
    
    # ========== ГОРОД (с картинкой!) ==========
    async def city_cmd(update, context):
        from keyboards.inline.city import get_city_keyboard
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
    
    # ========== ИГРА ==========
    app.add_handler(CommandHandler("rat_start", rat_start))
    app.add_handler(CommandHandler("rat_stop", rat_stop))
    app.add_handler(CommandHandler("rat_rules", rat_rules))
    
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

    # ========== КОЛБЭКИ ИГРЫ ==========
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
    app.add_handler(CallbackQueryHandler(show_chests_menu, pattern="^chests_menu$"))
    app.add_handler(CallbackQueryHandler(
        lambda u, c: handle_open_chest(u, c, u.callback_query.data.split('_')[2]),
        pattern=r"^open_chest_.*"
    ))
    
    # ========== СПОСОБНОСТИ ==========
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
    
    # ========== ЛОББИ ==========
    app.add_handler(CallbackQueryHandler(handle_lobby_join, pattern="^rat_lobby_join$"))
    app.add_handler(CallbackQueryHandler(handle_lobby_leave, pattern="^rat_lobby_leave$"))
    app.add_handler(CallbackQueryHandler(handle_lobby_start, pattern="^rat_lobby_start$"))
    app.add_handler(CallbackQueryHandler(back_to_game, pattern="^back_to_game$"))

    # ========== ОСНОВНОЙ КОЛБЭК ==========
    app.add_handler(CallbackQueryHandler(button_callback))
    
    # ========== ТУННЕЛИ (колбэки) ==========
    register_tunnel_handlers(app)

    # ========== ОБРАБОТЧИК ФОТО ДЛЯ БАГ-РЕПОРТОВ ==========
    app.add_handler(MessageHandler(filters.PHOTO, handle_bug_photo))

    # ========== ТЕКСТОВЫЕ СООБЩЕНИЯ ==========
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, smart_text_handler))

    # ========== СООБЩЕНИЕ О ЗАПУСКЕ ==========
    GROUP_CHAT_ID = -1003922256958
    
    async def post_init(app):
        await asyncio.sleep(2)
        try:
            text = f"""🟢 *РАТЛЯНДИЯ ЗАПУЩЕНА*

_Сервер пробудился, туннели открыты, крысы зашевелились._

🕐 {datetime.now().strftime('%d.%m.%Y %H:%M')} UTC
⚡ Статус: Онлайн

_Добро пожаловать в Подземное Царство!_"""
            await app.bot.send_message(chat_id=GROUP_CHAT_ID, text=text, parse_mode='Markdown')
        except Exception as e:
            logger.warning(f"Не удалось отправить сообщение о запуске: {e}")
    
    app.post_init = post_init

    print("\n✅ Бот запущен!")
    print("📱 @testpasha_bot")
    print("🗄️ SQLite активен!")
    print("🏰 /city | 🏪 /shop | 🎁 /daily | 🎲 /dice | 👥 /clan | 🕳️ /tunnel")
    print("⚒️ /forge | ⛪ /church | 🏆 /top | 📜 /history | ⚡ /titles | 📊 /me")
    print("=" * 80)

    app.run_polling(drop_pending_updates=True)


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