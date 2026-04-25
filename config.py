"""ЕДИНЫЙ КОНФИГ РАТЛЯНДИИ — все настройки в одном месте"""

import os
import json
from dataclasses import dataclass, field, asdict

# ========== ЗАГРУЗКА .env ==========
def _load_env():
    env_path = "/root/bot/.env"
    if os.path.exists(env_path):
        with open(env_path) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    os.environ[key.strip()] = value.strip()

_load_env()

# ============================================================
# ОСНОВНЫЕ КОНСТАНТЫ (для быстрого импорта)
# ============================================================

# Telegram
TOKEN = os.environ.get("BOT_TOKEN", "")

# Настройки игры
MIN_PLAYERS = 3
MAX_PLAYERS = 10
NIGHT_TIME = 30      # секунд
DAY_TIME = 60        # секунд
VOTE_TIME = 30       # секунд

# Логирование
LOG_FILE = "bot.log"

# База данных
DB_FILE = "/root/bot/ratings.db"
DICE_DB_FILE = "/root/bot/data/database/dice_stats.db"

# ============================================================
# НАСТРОЙКИ КОСТЕЙ (DICE ENGINE v5.0 by Pashadark)
# ============================================================

# Пороги успеха для d20
LEGENDARY_THRESHOLD = 15
CRITICAL_THRESHOLD = 10
EXCELLENT_THRESHOLD = 5
PARTIAL_THRESHOLD = -2
FAILURE_THRESHOLD = -9

# Система удачи
MAX_LUCK = 3
LUCK_RESTORE_RATE = 1
LUCK_RESTORE_COOLDOWN_HOURS = 4

# Взрывные кубики
MAX_EXPLOSIONS = 5

# Пул кубиков (WoD style)
DICE_POOL_TARGET = 6
DICE_POOL_DOUBLE_ON = 10

# Анимация в Telegram
ANIMATION_DELAY = 1.2      # пауза между сообщениями
SUSPENSE_DELAY = 2.0       # драматическая пауза

# ============================================================
# НАСТРОЙКИ ТАВЕРНЫ
# ============================================================

BEER_COST = 50             # стоимость пива в крошках
BEER_DURATION_HOURS = 1    # длительность эффекта пива

# Ставки по умолчанию
DEFAULT_BETS = [50, 100, 250, 500]

# Награды за игры в кости (кол-во игр -> редкость сундука)
DICE_REWARD_MILESTONES = {
    10: "common",
    25: "rare", 
    50: "epic",
    100: "legendary",
    250: "mythic"
}

# ============================================================
# НАСТРОЙКИ ПЕРСОНАЖА
# ============================================================

START_CRUMBS = 100
START_XP = 0
START_LEVEL = 1

# Базовые статы
BASE_STRENGTH = 5
BASE_AGILITY = 5
BASE_INTELLIGENCE = 5
BASE_HEALTH = 50

# Стат-поинты за уровень
STAT_POINTS_PER_LEVEL = 3

# ============================================================
# НАСТРОЙКИ ТУННЕЛЕЙ
# ============================================================

TUNNEL_BASE_XP = 10
TUNNEL_BASE_CRUMBS = 5
TUNNEL_BOSS_MULTIPLIER = 3

# ============================================================
# ДАТАКЛАССЫ ДЛЯ УДОБНОЙ РАБОТЫ
# ============================================================

@dataclass
class BotSettings:
    """Все настройки бота в одном объекте"""
    token: str = TOKEN
    min_players: int = MIN_PLAYERS
    max_players: int = MAX_PLAYERS
    night_time: int = NIGHT_TIME
    day_time: int = DAY_TIME
    vote_time: int = VOTE_TIME
    log_file: str = LOG_FILE
    main_db_path: str = DB_FILE 
    start_crumbs: int = START_CRUMBS
    base_strength: int = BASE_STRENGTH
    base_agility: int = BASE_AGILITY
    base_intelligence: int = BASE_INTELLIGENCE
    base_health: int = BASE_HEALTH
    
    def save(self, path: str = "/root/bot/data/configs/settings.json"):
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(asdict(self), f, indent=2, ensure_ascii=False)

@dataclass
class DiceSettings:
    """Настройки системы костей"""
    legendary_threshold: int = LEGENDARY_THRESHOLD
    critical_threshold: int = CRITICAL_THRESHOLD
    excellent_threshold: int = EXCELLENT_THRESHOLD
    partial_threshold: int = PARTIAL_THRESHOLD
    failure_threshold: int = FAILURE_THRESHOLD
    max_luck: int = MAX_LUCK
    luck_restore_rate: int = LUCK_RESTORE_RATE
    luck_restore_cooldown_hours: int = LUCK_RESTORE_COOLDOWN_HOURS
    max_explosions: int = MAX_EXPLOSIONS
    dice_pool_target: int = DICE_POOL_TARGET
    dice_pool_double_on: int = DICE_POOL_DOUBLE_ON
    animation_delay: float = ANIMATION_DELAY
    suspense_delay: float = SUSPENSE_DELAY
    db_path: str = DICE_DB_FILE
    beer_cost: int = BEER_COST
    beer_duration_hours: int = BEER_DURATION_HOURS
    default_bets: list = field(default_factory=lambda: DEFAULT_BETS)
    reward_milestones: dict = field(default_factory=lambda: DICE_REWARD_MILESTONES)

# Глобальные экземпляры для удобства
settings = BotSettings()
dice_settings = DiceSettings()

# ============================================================
# ФУНКЦИИ ДЛЯ РАБОТЫ С КОНФИГОМ
# ============================================================

def reload_settings():
    """Перезагружает настройки (если были изменены)"""
    global settings, dice_settings
    settings = BotSettings()
    dice_settings = DiceSettings()
    return settings, dice_settings

def get_dice_config() -> dict:
    """Возвращает настройки костей как словарь"""
    return asdict(dice_settings)

def print_config():
    """Выводит текущую конфигурацию"""
    print("=" * 60)
    print("🐀 РАТЛЯНДИЯ — КОНФИГУРАЦИЯ")
    print("=" * 60)
    print(f"🎮 Игра: {MIN_PLAYERS}-{MAX_PLAYERS} игроков")
    print(f"⏱️ Фазы: Ночь {NIGHT_TIME}с / День {DAY_TIME}с / Голосование {VOTE_TIME}с")
    print(f"🎲 Кости: Удача {MAX_LUCK}, Ставки {DEFAULT_BETS}")
    print(f"🍺 Пиво: {BEER_COST}🧀, длительность {BEER_DURATION_HOURS}ч")
    print(f"💪 Статы: СИЛ {BASE_STRENGTH} / ЛВК {BASE_AGILITY} / ИНТ {BASE_INTELLIGENCE}")
    print("=" * 60)

if __name__ == "__main__":
    print_config()