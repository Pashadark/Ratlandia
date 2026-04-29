"""Yadro Ratlandia - dvizhok, bazy dannykh, predmety, vosstanovlenie"""
from core.database import Database, db_ratings, db_ratgames, db_bot, db_dice
from core.restore import get_current_hp, get_current_mana, take_damage, heal_damage, use_mana, restore_mana, get_hp_restore_info, get_mana_restore_info
