"""Бизнес-логика Ratlandia — 7 доменов"""
from services.player import player_service
from services.inventory import inventory_service
from services.game import (
    start_tunnel_run, get_tunnel_run, end_tunnel_run, add_run_loot,
    advance_room, mark_boss_defeated, is_boss_defeated,
    create_coop_invite, get_pending_invite, accept_coop_invite,
    create_coop_battle, get_coop_battle, update_coop_battle, delete_coop_battle
)
from services.monsters import (
    get_monster, calculate_monster_stats, get_random_monster,
    process_loot, process_boss_loot, TUNNEL_MONSTERS
)
from services.rooms import room_service