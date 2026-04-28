#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🐀 Ratlandia — точка входа
Архитектура: handlers → services → core
"""
import os
import sys
import asyncio
import sqlite3
import platform
import subprocess
import handlers.compat  # noqa — временная совместимость старых импортов
from datetime import datetime

from telegram.ext import ApplicationBuilder

from config import TOKEN, settings
from handlers.router import register_all_handlers
from handlers.logger import logger


def progress_bar(percent, length=40):
    filled = int(length * percent / 100)
    bar = "█" * filled + "░" * (length - filled)
    return f"[{bar}] {percent}%"


def get_server_info():
    info = {}
    info['time'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    info['timezone'] = datetime.now().astimezone().tzname()
    info['system'] = platform.system()
    info['release'] = platform.release()
    info['machine'] = platform.machine()
    try:
        df = subprocess.check_output(['df', '-h', '/']).decode().strip().split('\n')[1]
        info['disk_usage'] = df.split()[4].replace('%', '')
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
    server_info = get_server_info()
    all_ok = True
    warnings = []
    DB_FILE = settings.main_db_path

    print("=" * 80)
    print("                    🐀 РАТЛЯНДИЯ — ЗАПУСК СИСТЕМЫ")
    print("=" * 80)

    # Сервер
    print(f"\n🖥️ [1/5] СЕРВЕР")
    try:
        print(f"   {progress_bar(100)} ✅")
        print(f"   ⏰ {server_info['time']} ({server_info['timezone']}) | 💻 {server_info['system']} {server_info['release']} | 🐍 Python {server_info['python']}")
        print(f"   💾 Диск: {server_info['disk_usage']} | 🧠 RAM: {server_info['memory']}")
    except Exception as e:
        print(f"   {progress_bar(0)} ❌ {str(e)[:50]}")
        all_ok = False

    # База данных
    print(f"\n🗄️ [2/5] БАЗА ДАННЫХ")
    if not os.path.exists(DB_FILE):
        print(f"   {progress_bar(0)} ❌ Файл не найден: {DB_FILE}")
        all_ok = False
    else:
        try:
            conn = sqlite3.connect(DB_FILE)
            c = conn.cursor()
            c.execute("SELECT COUNT(*) FROM ratings")
            players = c.fetchone()[0]
            c.execute("SELECT COUNT(*) FROM inventory")
            items = c.fetchone()[0]
            size_kb = os.path.getsize(DB_FILE) / 1024
            conn.close()
            print(f"   {progress_bar(100)} ✅")
            print(f"   📦 {size_kb:.1f} KB | 👥 {players} игроков | 🎒 {items} предметов")
        except Exception as e:
            print(f"   {progress_bar(0)} ❌ {str(e)[:50]}")
            all_ok = False

    # Токен
    print(f"\n⚙️ [3/5] КОНФИГУРАЦИЯ")
    if not TOKEN or len(TOKEN) < 30:
        print(f"   {progress_bar(0)} ❌ Токен невалиден!")
        all_ok = False
    else:
        print(f"   {progress_bar(100)} ✅ Токен OK")

    # Core
    print(f"\n🧩 [4/5] МОДУЛИ")
    try:
        from core.database import db_ratings
        from core.items.catalog import ALL_ITEMS
        from services.player import player_service
        from services.inventory import inventory_service
        from services.game import init_game_db
        from services.monsters import TUNNEL_MONSTERS
        print(f"   {progress_bar(100)} ✅")
        print(f"   🗃️ core OK | 🎒 {len(ALL_ITEMS)} предметов | 👹 {len(TUNNEL_MONSTERS)} монстров | 🛠️ services OK")
    except Exception as e:
        print(f"   {progress_bar(0)} ❌ {str(e)[:80]}")
        all_ok = False

    # Telegram API
    print(f"\n🌐 [5/5] TELEGRAM API")
    try:
        import requests
        response = requests.get(f"https://api.telegram.org/bot{TOKEN}/getMe", timeout=5)
        if response.status_code == 200 and response.json().get('ok'):
            bot_name = response.json()['result']['username']
            print(f"   {progress_bar(100)} ✅ @{bot_name}")
        else:
            print(f"   {progress_bar(0)} ❌")
            all_ok = False
    except:
        print(f"   {progress_bar(0)} ❌ Нет соединения")
        warnings.append("⚠️ Нет подключения к Telegram API")

    if warnings:
        print(f"\n{'='*80}")
        for w in warnings:
            print(f"   {w}")

    print(f"\n{'='*80}")
    if all_ok:
        print(f"                    ✅ ВСЕ СИСТЕМЫ ГОТОВЫ!")
    else:
        print(f"                    ⚠️ ЗАПУСК ПРОДОЛЖАЕТСЯ...")
    print(f"{'='*80}\n")
    return all_ok


async def main():
    """Точка входа"""
    run_startup_checks()

    app = ApplicationBuilder() \
        .token(TOKEN) \
        .connect_timeout(30) \
        .read_timeout(30) \
        .write_timeout(30) \
        .build()

    register_all_handlers(app)

    GROUP_CHAT_ID = -1003922256958

    async def post_init(app):
        await asyncio.sleep(2)
        try:
            text = f"""🟢 *РАТЛЯНДИЯ ЗАПУЩЕНА*

_Сервер пробудился, туннели открыты._

🕐 {datetime.now().strftime('%d.%m.%Y %H:%M')} UTC
⚡ Статус: Онлайн

_Добро пожаловать в Подземное Царство!_"""
            await app.bot.send_message(chat_id=GROUP_CHAT_ID, text=text, parse_mode='Markdown')
        except Exception as e:
            logger.warning(f"Не удалось отправить сообщение о запуске: {e}")

    app.post_init = post_init

    print("\n✅ Бот запущен! @testpasha_bot")
    print("=" * 80)

    await app.run_polling(drop_pending_updates=True)


if __name__ == "__main__":
    asyncio.run(main())