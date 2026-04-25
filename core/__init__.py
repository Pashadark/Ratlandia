"""Core module - фундамент бота"""

# Импортируем из корневого конфига
import sys
sys.path.insert(0, '/root/bot')

from config import (
    TOKEN, MIN_PLAYERS, MAX_PLAYERS, 
    NIGHT_TIME, DAY_TIME, VOTE_TIME, LOG_FILE,
    settings, dice_settings
)

__all__ = [
    'settings', 
    'dice_settings', 
    'TOKEN', 
    'MIN_PLAYERS', 
    'MAX_PLAYERS',
    'NIGHT_TIME',
    'DAY_TIME', 
    'VOTE_TIME',
    'LOG_FILE'
]