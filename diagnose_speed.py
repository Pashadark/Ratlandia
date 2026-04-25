#!/usr/bin/env python3
"""ДИАГНОСТИКА СКОРОСТИ БОТА — ЧТО ТОРМОЗИТ?"""

import time
import sys
sys.path.append('/root/bot')

def test_speed(name: str, func, *args, **kwargs):
    """Замеряет время выполнения функции"""
    start = time.time()
    result = func(*args, **kwargs)
    elapsed = time.time() - start
    print(f"⏱️ {name}: {elapsed:.3f} сек")
    if elapsed > 0.5:
        print(f"   ⚠️ МЕДЛЕННО! ({elapsed:.3f} сек)")
    return result

print("=" * 60)
print("🔍 ДИАГНОСТИКА СКОРОСТИ БОТА")
print("=" * 60)

# 1. Импорт config
print("\n📦 1. ИМПОРТ КОНФИГА")
test_speed("import config", lambda: __import__('config'))

# 2. Импорт движка
print("\n🎲 2. ИМПОРТ ДВИЖКА")
test_speed("import engine", lambda: __import__('core.dice.engine'))

# 3. Импорт сервисов
print("\n🔧 3. ИМПОРТ СЕРВИСОВ")
test_speed("import dice_service", lambda: __import__('services.dice_service'))
test_speed("import tavern_service", lambda: __import__('services.tavern_service'))

# 4. Подключение к БД
print("\n🗄️ 4. ПОДКЛЮЧЕНИЕ К БД")
import sqlite3
def connect_db():
    conn = sqlite3.connect('/root/bot/ratings.db')
    conn.close()
test_speed("connect to ratings.db", connect_db)

def query_db():
    conn = sqlite3.connect('/root/bot/ratings.db')
    cur = conn.execute('SELECT COUNT(*) FROM ratings')
    cur.fetchone()
    conn.close()
test_speed("SELECT COUNT(*) FROM ratings", query_db)

def query_dice():
    conn = sqlite3.connect('/root/bot/ratings.db')
    cur = conn.execute('SELECT COUNT(*) FROM dice_history')
    cur.fetchone()
    conn.close()
test_speed("SELECT COUNT(*) FROM dice_history", query_dice)

# 5. Проверка таблиц
print("\n📊 5. ПРОВЕРКА ТАБЛИЦ")
def check_tables():
    conn = sqlite3.connect('/root/bot/ratings.db')
    cur = conn.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = [row[0] for row in cur.fetchall()]
    conn.close()
    return tables
tables = test_speed("get all tables", check_tables)
print(f"   Таблиц в БД: {len(tables)}")

# 6. Проверка размера БД
print("\n💾 6. РАЗМЕР БД")
import os
db_size = os.path.getsize('/root/bot/ratings.db') / 1024 / 1024
print(f"   ratings.db: {db_size:.1f} MB")

# 7. Проверка логов
print("\n📝 7. ПРОВЕРКА ЛОГОВ")
log_files = ['/root/bot/logs/bot.log', '/root/bot/logs/dice_engine.log']
for log_file in log_files:
    if os.path.exists(log_file):
        size = os.path.getsize(log_file) / 1024 / 1024
        lines = sum(1 for _ in open(log_file))
        print(f"   {log_file}: {size:.1f} MB ({lines} строк)")
        if size > 50:
            print(f"   ⚠️ ЛОГ-ФАЙЛ ОГРОМНЫЙ! Надо очистить!")

# 8. Проверка импортов handlers
print("\n📂 8. ИМПОРТ ХЕНДЛЕРОВ")
test_speed("import dice handler", lambda: __import__('handlers.dice.dice'))
test_speed("import callbacks", lambda: __import__('handlers.callbacks'))

# 9. Проверка движка (создание)
print("\n🎯 9. СОЗДАНИЕ ДВИЖКА")
from core.dice.engine import DiceEngine, EngineConfig
def create_engine():
    engine = DiceEngine()
    return engine
engine = test_speed("DiceEngine()", create_engine)

# 10. Проверка броска
print("\n🎲 10. БРОСОК КУБИКА")
def roll_dice():
    return engine.roll_1d6()
result = test_speed("roll_1d6()", roll_dice)
print(f"   Результат: {result}")

# 11. Проверка tavern_service
print("\n🍺 11. TAVERN SERVICE")
from services.tavern_service import tavern_service
stats = test_speed("get_player_stats(185185047)", tavern_service.get_player_stats, 185185047)
text = test_speed("format_stats_message(185185047)", tavern_service.format_stats_message, 185185047)

print("\n" + "=" * 60)
print("✅ ДИАГНОСТИКА ЗАВЕРШЕНА!")
print("=" * 60)

# ИТОГИ
print("\n📋 РЕКОМЕНДАЦИИ:")
if db_size > 10:
    print("⚠️ БД больше 10 MB — надо оптимизировать!")
for log_file in log_files:
    if os.path.exists(log_file):
        size = os.path.getsize(log_file) / 1024 / 1024
        if size > 50:
            print(f"⚠️ {log_file} больше 50 MB — очисти! > /root/bot/logs/bot.log")
print("✅ Если все проверки < 0.5 сек — проблема в сетевых запросах к Telegram API")