"""Система улучшенного логирования"""
import sqlite3
import logging
from config import settings

DB_FILE = settings.main_db_path

logger = logging.getLogger("ratlandia")
logger.setLevel(logging.INFO)

file_handler = logging.FileHandler(settings.log_file, encoding='utf-8')
file_handler.setLevel(logging.INFO)
file_handler.setFormatter(logging.Formatter('%(asctime)s | %(message)s', datefmt='%H:%M:%S'))

console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)
console_handler.setFormatter(logging.Formatter('%(asctime)s | %(message)s', datefmt='%H:%M:%S'))

logger.addHandler(file_handler)
logger.addHandler(console_handler)

logging.getLogger("httpx").setLevel(logging.WARNING)
logging.getLogger("telegram.request").setLevel(logging.WARNING)
logging.getLogger("telegram.ext").setLevel(logging.WARNING)


def get_user_info(user_id: int) -> dict:
    try:
        conn = sqlite3.connect(DB_FILE)
        c = conn.cursor()
        c.execute("SELECT nickname, wins, games FROM ratings WHERE user_id = ?", (user_id,))
        row = c.fetchone()
        conn.close()
        if row:
            return {"nickname": row[0] or f"ID:{user_id}", "wins": row[1] or 0, "games": row[2] or 0}
        return {"nickname": f"ID:{user_id}", "wins": 0, "games": 0}
    except:
        return {"nickname": f"ID:{user_id}", "wins": 0, "games": 0}


def format_user(user_id: int, username: str = None) -> str:
    info = get_user_info(user_id)
    nick = info["nickname"]
    if username and username.lower() not in nick.lower():
        nick = f"{nick} (@{username})"
    return f"{nick} [ID:{user_id}]"


def log_action(user_id: int, action: str, emoji: str = "🔘", username: str = None, details: str = None, is_admin: bool = False):
    user_str = format_user(user_id, username)
    crown = "👑 " if is_admin else ""
    if details:
        logger.info(f"{emoji} | {crown}{user_str} | {action} | {details}")
    else:
        logger.info(f"{emoji} | {crown}{user_str} | {action}")


def log_system(action: str, emoji: str = "📡"):
    logger.info(f"{emoji} | СИСТЕМА | {action}")


def log_error(action: str, error: str = None, user_id: int = None, username: str = None):
    if user_id:
        user_str = format_user(user_id, username)
        logger.warning(f"⚠️ | {user_str} | ❌ {action} | {error}")
    else:
        logger.warning(f"⚠️ | СИСТЕМА | ❌ {action} | {error}")


def log_critical(action: str, error: str = None):
    logger.error(f"🚨 | СИСТЕМА | 💀 {action} | {error}")