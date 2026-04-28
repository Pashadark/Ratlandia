"""Система логирования с никами"""
import sqlite3
import logging

DB_FILE = "/root/bot/ratings.db"

logger = logging.getLogger("ratlandia")
logger.setLevel(logging.INFO)

# Только консоль
console = logging.StreamHandler()
console.setLevel(logging.INFO)
console.setFormatter(logging.Formatter('%(asctime)s | %(message)s', datefmt='%H:%M:%S'))
logger.addHandler(console)

def log(user_id, action, emoji="🔘", username=None, details=None):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("SELECT nickname FROM ratings WHERE user_id = ?", (user_id,))
    row = c.fetchone()
    nick = row[0] if row and row[0] else f"ID:{user_id}"
    conn.close()
    
    name = f"{nick} (@{username})" if username else nick
    if details:
        logger.info(f"{emoji} | {name} [ID:{user_id}] | {action} | {details}")
    else:
        logger.info(f"{emoji} | {name} [ID:{user_id}] | {action}")

def log_system(msg, emoji="📡"):
    logger.info(f"{emoji} | {msg}")
