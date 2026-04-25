"""Монстры для режима Туннели — 20+ врагов с прогрессией и дропом ресурсов"""

import sqlite3
import random
from typing import Dict, List, Optional
from handlers.inventory import add_crumbs, add_xp

DB_FILE = "/root/bot/ratings.db"

from handlers.character import (
    get_character_stats, 
    update_character_stats,
    increment_tunnel_runs
)

# ========== ВСЕ МОНСТРЫ ==========
TUNNEL_MONSTERS = {
    # ===== УРОВЕНЬ 1: ОБИТАТЕЛИ ВЕРХНИХ ТУННЕЛЕЙ =====
    "blind_mole": {
        "name": "Слепой Крот",
        "level": 1,
        "rarity": "common",
        "health": 8,
        "min_damage": 1,
        "max_damage": 2,
        "base_crumbs": 5,
        "base_xp": 3,
        "ability": None,
        "ability_desc": None,
        "icon": "🦔",
        "desc": "_Из земли вырывается огромный слепой крот._",
        "death_text": "_Крот заваливается на бок и замирает._",
        "loot_table": {
            "crumbs": {"multiplier": 1.0},
            "items": [
                {"item_id": "leather_vest", "chance": 8},
                {"item_id": "cheese_wedge_hat", "chance": 4},
                {"item_id": "common_chest", "chance": 2},
            ],
            "resources": [
                {"item_id": "stone_shard", "chance": 40},
                {"item_id": "mouse_bone", "chance": 30},
                {"item_id": "rat_pelt", "chance": 20},
                {"item_id": "copper_scrap", "chance": 15},
                {"item_id": "cheese_crust", "chance": 20},
                {"item_id": "bread_crumb", "chance": 15},
            ]
        },
    },
    
    "giant_woodlouse": {
        "name": "Мокрица-переросток",
        "level": 1,
        "rarity": "common",
        "health": 6,
        "min_damage": 1,
        "max_damage": 3,
        "base_crumbs": 4,
        "base_xp": 2,
        "ability": "curl",
        "ability_desc": "_Сворачивается в клубок при HP < 50%_",
        "icon": "🪲",
        "desc": "_Огромная мокрица копошится в гнилых досках._",
        "death_text": "_Мокрица переворачивается на спину и замирает._",
        "loot_table": {
            "crumbs": {"multiplier": 1.0},
            "items": [
                {"item_id": "gambeson", "chance": 6},
                {"item_id": "bubble_wrap", "chance": 8},
            ],
            "resources": [
                {"item_id": "stone_shard", "chance": 35},
                {"item_id": "copper_scrap", "chance": 20},
                {"item_id": "rat_incisor", "chance": 25},
                {"item_id": "spider_web", "chance": 20},
                {"item_id": "linen_scrap", "chance": 15},
                {"item_id": "moldy_crumb", "chance": 20},
            ]
        },
    },
    
    "earthworm": {
        "name": "Дождевой Червь",
        "level": 1,
        "rarity": "common",
        "health": 10,
        "min_damage": 1,
        "max_damage": 1,
        "base_crumbs": 6,
        "base_xp": 4,
        "ability": "regeneration",
        "ability_desc": "_Восстанавливает 1 HP каждый ход_",
        "icon": "🪱",
        "desc": "_Толстый розовый червь выползает из стены._",
        "death_text": "_Червь распадается на две половинки._",
        "loot_table": {
            "crumbs": {"multiplier": 1.0},
            "items": [
                {"item_id": "holy_water", "chance": 6},
                {"item_id": "poison_vial", "chance": 4},
            ],
            "resources": [
                {"item_id": "mouse_bone", "chance": 35},
                {"item_id": "fish_spine", "chance": 25},
                {"item_id": "rat_pelt", "chance": 15},
                {"item_id": "clean_water", "chance": 25},
                {"item_id": "basement_mushroom", "chance": 20},
                {"item_id": "empty_vial", "chance": 10},
            ]
        },
    },
    
    "rustler": {
        "name": "Шуршун",
        "level": 1,
        "rarity": "uncommon",
        "health": 5,
        "min_damage": 2,
        "max_damage": 4,
        "base_crumbs": 10,
        "base_xp": 6,
        "ability": "fast",
        "ability_desc": "_20% шанс атаковать дважды_",
        "icon": "🐀",
        "desc": "_Маленькое юркое существо мечется из угла в угол._",
        "death_text": "_Шуршун замирает и падает._",
        "loot_table": {
            "crumbs": {"multiplier": 1.5},
            "items": [
                {"item_id": "lucky_coin", "chance": 12},
                {"item_id": "ninja_mask", "chance": 4},
            ],
            "resources": [
                {"item_id": "rat_pelt", "chance": 30},
                {"item_id": "rat_incisor", "chance": 30},
                {"item_id": "copper_scrap", "chance": 25},
                {"item_id": "leather_scrap", "chance": 20},
                {"item_id": "wool_clump", "chance": 15},
                {"item_id": "pigeon_feather", "chance": 15},
                {"item_id": "smooth_pebble", "chance": 10},
            ]
        },
    },
    
    "moldling": {
        "name": "Плесневик",
        "level": 1,
        "rarity": "common",
        "health": 12,
        "min_damage": 0,
        "max_damage": 2,
        "base_crumbs": 3,
        "base_xp": 5,
        "ability": "spores",
        "ability_desc": "_30% шанс отравить на 2 хода_",
        "icon": "🍄",
        "desc": "_Комок серо-зелёной плесени медленно ползёт._",
        "death_text": "_Плесневик высыхает в порошок._",
        "loot_table": {
            "crumbs": {"multiplier": 0.8},
            "items": [
                {"item_id": "poison_cheese", "chance": 15},
                {"item_id": "rat_poison_antidote", "chance": 8},
            ],
            "resources": [
                {"item_id": "moldy_crumb", "chance": 40},
                {"item_id": "basement_mushroom", "chance": 35},
                {"item_id": "empty_vial", "chance": 15},
                {"item_id": "rat_poison", "chance": 10},
                {"item_id": "spider_web", "chance": 15},
                {"item_id": "candle_stub", "chance": 10},
            ]
        },
    },
    
    # ===== УРОВЕНЬ 2: ГЛУБИННЫЕ ОБИТАТЕЛИ =====
    "renegade_rat": {
        "name": "Крыса-Отступница",
        "level": 2,
        "rarity": "uncommon",
        "health": 14,
        "min_damage": 2,
        "max_damage": 5,
        "base_crumbs": 15,
        "base_xp": 10,
        "ability": "block",
        "ability_desc": "_Раз в 3 хода блокирует атаку_",
        "icon": "🐀",
        "desc": "_Огромная крыса со шрамами на морде._",
        "death_text": "_Крыса падает на бок._",
        "loot_table": {
            "crumbs": {"multiplier": 1.5},
            "items": [
                {"item_id": "rat_dagger", "chance": 10},
                {"item_id": "rat_ears", "chance": 8},
                {"item_id": "rare_chest", "chance": 3},
            ],
            "resources": [
                {"item_id": "iron_gear", "chance": 30},
                {"item_id": "bronze_alloy", "chance": 25},
                {"item_id": "rat_pelt", "chance": 25},
                {"item_id": "rat_incisor", "chance": 20},
                {"item_id": "smoked_lard", "chance": 15},
                {"item_id": "spider_silk", "chance": 15},
                {"item_id": "mole_skull", "chance": 10},
            ]
        },
    },
    
    "scolopendra": {
        "name": "Сколопендра Многоножка",
        "level": 2,
        "rarity": "common",
        "health": 18,
        "min_damage": 1,
        "max_damage": 3,
        "base_crumbs": 12,
        "base_xp": 12,
        "ability": "many_legs",
        "ability_desc": "_Всегда атакует дважды_",
        "icon": "🐛",
        "desc": "_Длинная многоножка с десятками сегментов._",
        "death_text": "_Многоножка сворачивается в спираль._",
        "loot_table": {
            "crumbs": {"multiplier": 1.2},
            "items": [
                {"item_id": "chainmail", "chance": 8},
                {"item_id": "poison_vial", "chance": 10},
            ],
            "resources": [
                {"item_id": "fish_spine", "chance": 30},
                {"item_id": "rat_tail_vertebra", "chance": 25},
                {"item_id": "bat_membrane", "chance": 20},
                {"item_id": "iron_gear", "chance": 15},
                {"item_id": "wall_soot", "chance": 20},
                {"item_id": "honey_drop", "chance": 10},
            ]
        },
    },
    
    "grinder_beetle": {
        "name": "Жук-Точильщик",
        "level": 2,
        "rarity": "uncommon",
        "health": 20,
        "min_damage": 2,
        "max_damage": 3,
        "base_crumbs": 18,
        "base_xp": 14,
        "ability": "hard_shell",
        "ability_desc": "_Каждую 3-ю атаку игнорирует_",
        "icon": "🪲",
        "desc": "_Огромный чёрный жук с блестящим панцирем._",
        "death_text": "_Панцирь жука трескается._",
        "loot_table": {
            "crumbs": {"multiplier": 1.5},
            "items": [
                {"item_id": "turtle_shell", "chance": 8},
                {"item_id": "bulletproof_vest", "chance": 6},
                {"item_id": "rare_chest", "chance": 4},
            ],
            "resources": [
                {"item_id": "bronze_alloy", "chance": 35},
                {"item_id": "iron_gear", "chance": 30},
                {"item_id": "snake_skin", "chance": 20},
                {"item_id": "mole_skull", "chance": 15},
                {"item_id": "smoked_lard", "chance": 15},
                {"item_id": "surface_shell", "chance": 10},
            ]
        },
    },
    
    "giant_slug": {
        "name": "Слизень-Гигант",
        "level": 2,
        "rarity": "common",
        "health": 25,
        "min_damage": 1,
        "max_damage": 2,
        "base_crumbs": 10,
        "base_xp": 15,
        "ability": "slow",
        "ability_desc": "_При попадании замедляет на 1 ход_",
        "icon": "🐌",
        "desc": "_Огромный слизистый комок._",
        "death_text": "_Слизень растекается лужей._",
        "loot_table": {
            "crumbs": {"multiplier": 1.0},
            "items": [
                {"item_id": "stinky_sock", "chance": 15},
                {"item_id": "holy_water", "chance": 8},
            ],
            "resources": [
                {"item_id": "rat_pelt", "chance": 25},
                {"item_id": "spider_silk", "chance": 25},
                {"item_id": "bat_membrane", "chance": 20},
                {"item_id": "empty_vial", "chance": 20},
                {"item_id": "clean_water", "chance": 15},
                {"item_id": "honey_drop", "chance": 10},
            ]
        },
    },
    
    "vampire_bat": {
        "name": "Летучая Мышь-Кровосос",
        "level": 2,
        "rarity": "rare",
        "health": 12,
        "min_damage": 3,
        "max_damage": 5,
        "base_crumbs": 25,
        "base_xp": 18,
        "ability": "vampirism",
        "ability_desc": "_Восстанавливает половину урона_",
        "icon": "🦇",
        "desc": "_Тёмный силуэт срывается с потолка._",
        "death_text": "_Мышь падает на пол и затихает._",
        "loot_table": {
            "crumbs": {"multiplier": 2.0},
            "items": [
                {"item_id": "shadow_hood", "chance": 8},
                {"item_id": "vampire_bat_fang", "chance": 4},
                {"item_id": "epic_chest", "chance": 2},
            ],
            "resources": [
                {"item_id": "bat_membrane", "chance": 40},
                {"item_id": "bat_fang", "chance": 15},
                {"item_id": "rat_king_tear", "chance": 15},
                {"item_id": "steel_shard", "chance": 10},
                {"item_id": "fairy_dust", "chance": 10},
                {"item_id": "human_coin", "chance": 8},
            ]
        },
    },
    
    # ===== УРОВЕНЬ 3: СТРАЖИ ГЛУБИН =====
    "weaver_spider": {
        "name": "Паук-Ткач",
        "level": 3,
        "rarity": "uncommon",
        "health": 30,
        "min_damage": 3,
        "max_damage": 6,
        "base_crumbs": 30,
        "base_xp": 25,
        "ability": "web",
        "ability_desc": "_Раз в 3 хода опутывает паутиной_",
        "icon": "🕷️",
        "desc": "_Огромный паук с мохнатыми лапами._",
        "death_text": "_Паук падает с паутины._",
        "loot_table": {
            "crumbs": {"multiplier": 1.8},
            "items": [
                {"item_id": "ninja_mask", "chance": 10},
                {"item_id": "net_launcher", "chance": 8},
                {"item_id": "epic_chest", "chance": 5},
            ],
            "resources": [
                {"item_id": "spider_silk", "chance": 40},
                {"item_id": "steel_shard", "chance": 25},
                {"item_id": "silver_ingot", "chance": 20},
                {"item_id": "rat_poison", "chance": 20},
                {"item_id": "crow_bone", "chance": 15},
                {"item_id": "marrow_bone", "chance": 15},
                {"item_id": "cloudy_crystal", "chance": 10},
            ]
        },
    },
    
    "armadillo_centipede": {
        "name": "Сороконожка-Броненосец",
        "level": 3,
        "rarity": "uncommon",
        "health": 35,
        "min_damage": 2,
        "max_damage": 4,
        "base_crumbs": 25,
        "base_xp": 22,
        "ability": "curl_ball",
        "ability_desc": "_При HP < 30% сворачивается в шар_",
        "icon": "🪱",
        "desc": "_Существо из твёрдых сегментов._",
        "death_text": "_Броненосец рассыпается на части._",
        "loot_table": {
            "crumbs": {"multiplier": 1.5},
            "items": [
                {"item_id": "turtle_shell", "chance": 12},
                {"item_id": "bulletproof_vest", "chance": 8},
            ],
            "resources": [
                {"item_id": "iron_gear", "chance": 30},
                {"item_id": "steel_shard", "chance": 25},
                {"item_id": "rat_tail_vertebra", "chance": 20},
                {"item_id": "emerald_crumb", "chance": 15},
                {"item_id": "rat_king_tear", "chance": 15},
                {"item_id": "mirror_shard_res", "chance": 10},
            ]
        },
    },
    
    "rat_ghoul": {
        "name": "Крысиный Упырь",
        "level": 3,
        "rarity": "rare",
        "health": 28,
        "min_damage": 4,
        "max_damage": 7,
        "base_crumbs": 40,
        "base_xp": 30,
        "ability": "frenzy",
        "ability_desc": "_При HP < 50% впадает в ярость_",
        "icon": "🐀💀",
        "desc": "_Тощая серая крыса с белыми глазами._",
        "death_text": "_Тело упыря затихает._",
        "loot_table": {
            "crumbs": {"multiplier": 2.0},
            "items": [
                {"item_id": "butcher_knife", "chance": 8},
                {"item_id": "demon_skin", "chance": 4},
                {"item_id": "legendary_chest", "chance": 2},
            ],
            "resources": [
                {"item_id": "steel_shard", "chance": 30},
                {"item_id": "silver_ingot", "chance": 25},
                {"item_id": "rat_poison", "chance": 25},
                {"item_id": "crow_bone", "chance": 20},
                {"item_id": "fairy_dust", "chance": 15},
                {"item_id": "moon_dew", "chance": 15},
                {"item_id": "underground_truffle", "chance": 10},
            ]
        },
    },
    
    "giant_cockroach": {
        "name": "Подземный Таракан-Гигант",
        "level": 3,
        "rarity": "common",
        "health": 22,
        "min_damage": 1,
        "max_damage": 8,
        "base_crumbs": 20,
        "base_xp": 18,
        "ability": "survival",
        "ability_desc": "_50% шанс при смерти восстановить HP_",
        "icon": "🪳",
        "desc": "_Усатый монстр размером с собаку._",
        "death_text": "_Таракан переворачивается на спину._",
        "loot_table": {
            "crumbs": {"multiplier": 1.2},
            "items": [
                {"item_id": "garbage_can_armor", "chance": 15},
                {"item_id": "lucky_rabbit_foot", "chance": 6},
            ],
            "resources": [
                {"item_id": "rat_pelt", "chance": 25},
                {"item_id": "iron_gear", "chance": 20},
                {"item_id": "bronze_alloy", "chance": 20},
                {"item_id": "spider_silk", "chance": 15},
                {"item_id": "marrow_bone", "chance": 15},
                {"item_id": "human_coin", "chance": 10},
            ]
        },
    },
    
    "sewer_leech": {
        "name": "Пиявка Сточная",
        "level": 3,
        "rarity": "uncommon",
        "health": 40,
        "min_damage": 1,
        "max_damage": 3,
        "base_crumbs": 28,
        "base_xp": 26,
        "ability": "attach",
        "ability_desc": "_Присасывается к туловищу_",
        "icon": "🪱🩸",
        "desc": "_Чёрная блестящая тварь в грязной воде._",
        "death_text": "_Пиявка сжимается в комок._",
        "loot_table": {
            "crumbs": {"multiplier": 1.5},
            "items": [
                {"item_id": "holy_water", "chance": 15},
                {"item_id": "rat_poison_antidote", "chance": 10},
            ],
            "resources": [
                {"item_id": "rat_poison", "chance": 30},
                {"item_id": "rat_king_tear", "chance": 25},
                {"item_id": "fish_spine", "chance": 20},
                {"item_id": "clean_water", "chance": 20},
                {"item_id": "silver_ingot", "chance": 15},
                {"item_id": "honey_drop", "chance": 10},
            ]
        },
    },
    
    # ===== УРОВЕНЬ 4: КОШМАРЫ ПОДЗЕМЕЛЬЯ =====
    "black_ferret": {
        "name": "Чёрный Хорёк",
        "level": 4,
        "rarity": "rare",
        "health": 45,
        "min_damage": 5,
        "max_damage": 8,
        "base_crumbs": 50,
        "base_xp": 40,
        "ability": "hypnosis",
        "ability_desc": "_Раз в 4 хода гипнотизирует_",
        "icon": "🦡",
        "desc": "_Грациозное чёрное тело скользит в темноте._",
        "death_text": "_Хорёк издаёт визг и падает._",
        "loot_table": {
            "crumbs": {"multiplier": 2.5},
            "items": [
                {"item_id": "shadow_hood", "chance": 12},
                {"item_id": "invisibility_cloak", "chance": 5},
                {"item_id": "legendary_chest", "chance": 4},
            ],
            "resources": [
                {"item_id": "obsidian_scale", "chance": 25},
                {"item_id": "mithril_nugget", "chance": 20},
                {"item_id": "bat_fang", "chance": 20},
                {"item_id": "moon_silk", "chance": 15},
                {"item_id": "phoenix_ember", "chance": 10},
                {"item_id": "magnetic_stone", "chance": 10},
                {"item_id": "forgotten_ale", "chance": 8},
            ]
        },
    },
    
    "two_headed_rat": {
        "name": "Крыса-Мутант с Двумя Головами",
        "level": 4,
        "rarity": "epic",
        "health": 60,
        "min_damage": 4,
        "max_damage": 8,
        "base_crumbs": 70,
        "base_xp": 60,
        "ability": "two_heads",
        "ability_desc": "_Всегда атакует дважды_",
        "icon": "🐀🐀",
        "desc": "_Огромная крыса с двумя головами._",
        "death_text": "_Обе головы испускают хрип._",
        "loot_table": {
            "crumbs": {"multiplier": 3.0},
            "items": [
                {"item_id": "crown_of_rat_king", "chance": 8},
                {"item_id": "rat_king_crown_broken", "chance": 12},
                {"item_id": "mythic_chest", "chance": 2},
            ],
            "resources": [
                {"item_id": "mithril_nugget", "chance": 30},
                {"item_id": "obsidian_scale", "chance": 25},
                {"item_id": "rat_king_eye", "chance": 20},
                {"item_id": "cat_pelt", "chance": 15},
                {"item_id": "mage_blood", "chance": 15},
                {"item_id": "ancient_scrap", "chance": 10},
                {"item_id": "ancient_amulet", "chance": 8},
            ]
        },
    },
    
    "basement_snake": {
        "name": "Подвальный Уж",
        "level": 4,
        "rarity": "rare",
        "health": 35,
        "min_damage": 4,
        "max_damage": 9,
        "base_crumbs": 55,
        "base_xp": 50,
        "ability": "constrict",
        "ability_desc": "_40% шанс обвить при атаке_",
        "icon": "🐍",
        "desc": "_Длинное мускулистое тело скользит по трубе._",
        "death_text": "_Тело ужа обмякает._",
        "loot_table": {
            "crumbs": {"multiplier": 2.5},
            "items": [
                {"item_id": "rat_tail_whip", "chance": 10},
                {"item_id": "dragon_scale", "chance": 5},
                {"item_id": "legendary_chest", "chance": 4},
            ],
            "resources": [
                {"item_id": "snake_skin", "chance": 35},
                {"item_id": "obsidian_scale", "chance": 25},
                {"item_id": "rat_tail_vertebra", "chance": 20},
                {"item_id": "mandrake", "chance": 15},
                {"item_id": "hermit_rosary", "chance": 10},
                {"item_id": "phoenix_ember", "chance": 8},
            ]
        },
    },
    
    # ===== ЭЛИТНЫЕ МОНСТРЫ =====
    "elite_mole_king": {
        "name": "Король Кротов",
        "level": 3,
        "rarity": "elite",
        "health": 50,
        "min_damage": 5,
        "max_damage": 10,
        "base_crumbs": 80,
        "base_xp": 50,
        "ability": "summon",
        "ability_desc": "_Призывает кротов-помощников_",
        "icon": "👑🦔",
        "desc": "_Огромный крот с короной из костей._",
        "death_text": "_Король кротов падает, туннель дрожит._",
        "loot_table": {
            "crumbs": {"multiplier": 4.0},
            "items": [
                {"item_id": "crown_of_mouse_king", "chance": 15},
                {"item_id": "epic_chest", "chance": 20},
                {"item_id": "legendary_chest", "chance": 8},
            ],
            "resources": [
                {"item_id": "obsidian_scale", "chance": 35},
                {"item_id": "mithril_nugget", "chance": 30},
                {"item_id": "moon_silk", "chance": 25},
                {"item_id": "bat_fang", "chance": 20},
                {"item_id": "rat_king_eye", "chance": 20},
                {"item_id": "mage_blood", "chance": 15},
                {"item_id": "phoenix_ember", "chance": 12},
                {"item_id": "magnetic_stone", "chance": 15},
                {"item_id": "ancient_scrap", "chance": 12},
                {"item_id": "void_essence", "chance": 5},
            ]
        },
    },
    
    "elite_spider_queen": {
        "name": "Королева Пауков",
        "level": 4,
        "rarity": "elite",
        "health": 80,
        "min_damage": 6,
        "max_damage": 12,
        "base_crumbs": 120,
        "base_xp": 80,
        "ability": "summon_spiders",
        "ability_desc": "_Призывает пауков каждые 3 хода_",
        "icon": "👑🕷️",
        "desc": "_Гигантская паучиха с тысячами детёнышей на спине._",
        "death_text": "_Королева пауков издаёт предсмертный визг._",
        "loot_table": {
            "crumbs": {"multiplier": 5.0},
            "items": [
                {"item_id": "cloak_of_mouse_god", "chance": 10},
                {"item_id": "mythic_chest", "chance": 8},
                {"item_id": "legendary_chest", "chance": 15},
            ],
            "resources": [
                {"item_id": "spider_silk", "chance": 50},
                {"item_id": "moon_silk", "chance": 35},
                {"item_id": "mithril_nugget", "chance": 30},
                {"item_id": "obsidian_scale", "chance": 25},
                {"item_id": "bat_fang", "chance": 20},
                {"item_id": "rat_king_eye", "chance": 20},
                {"item_id": "mage_blood", "chance": 18},
                {"item_id": "phoenix_ember", "chance": 15},
                {"item_id": "void_essence", "chance": 10},
                {"item_id": "adamantite", "chance": 8},
                {"item_id": "star_silk", "chance": 8},
            ]
        },
    },
    
    # ===== БОСС =====
    "old_blind_cat": {
        "name": "Старый Слепой Кот",
        "level": 5,
        "rarity": "boss",
        "health": 100,
        "min_damage": 8,
        "max_damage": 15,
        "base_crumbs": 650,
        "base_xp": 450,
        "ability": "multiple",
        "ability_desc": "_Восстанавливает HP, оглушает, иммунитет к хвосту_",
        "icon": "🐈",
        "desc": "_Огромный облезлый кот с бельмами на глазах._",
        "death_text": "_Старый кот медленно опускается на пол._",
        "coop_health_multiplier": 2.0,
        "loot_table": {
            "crumbs": {"multiplier": 10.0},
            "items": [
                {"item_id": "crown_of_mouse_king", "chance": 100},
                {"item_id": "cloak_of_mouse_god", "chance": 100},
                {"item_id": "mythic_chest", "chance": 50},
                {"item_id": "amulet_of_cat_claw", "chance": 30},
            ],
            "resources": [
                {"item_id": "mithril_nugget", "chance": 50},
                {"item_id": "obsidian_scale", "chance": 40},
                {"item_id": "adamantite", "chance": 30},
                {"item_id": "rat_god_tooth", "chance": 25},
                {"item_id": "star_silk", "chance": 30},
                {"item_id": "first_rat_skull", "chance": 20},
                {"item_id": "labyrinth_heart", "chance": 15},
                {"item_id": "void_essence", "chance": 30},
                {"item_id": "spark_creation", "chance": 15},
                {"item_id": "phoenix_ember", "chance": 25},
                {"item_id": "ice_worm_tear", "chance": 25},
                {"item_id": "storm_spark", "chance": 25},
                {"item_id": "mage_blood", "chance": 30},
                {"item_id": "gate_key", "chance": 15},
                {"item_id": "labyrinth_seal", "chance": 15},
                {"item_id": "tapestry_scrap", "chance": 15},
                {"item_id": "forgotten_ale", "chance": 20},
            ]
        },
    },
}


# ========== ФУНКЦИИ ДЛЯ РАБОТЫ С МОНСТРАМИ ==========

def init_tunnel_monsters_db():
    """Создаёт таблицы для туннелей"""
    with sqlite3.connect(DB_FILE) as conn:
        c = conn.cursor()
        
        c.execute('''CREATE TABLE IF NOT EXISTS tunnel_run (
            user_id INTEGER PRIMARY KEY,
            current_room INTEGER DEFAULT 1,
            rooms_completed INTEGER DEFAULT 0,
            crumbs_collected INTEGER DEFAULT 0,
            xp_collected INTEGER DEFAULT 0,
            kill_streak INTEGER DEFAULT 0,
            monsters_killed INTEGER DEFAULT 0,
            path_choice TEXT DEFAULT 'normal',
            blessed BOOLEAN DEFAULT 0,
            blessings TEXT,
            run_seed TEXT
        )''')
        
        c.execute('''CREATE TABLE IF NOT EXISTS tunnel_bosses_defeated (
            user_id INTEGER,
            monster_id TEXT,
            defeated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            PRIMARY KEY (user_id, monster_id)
        )''')
        
        c.execute('''CREATE TABLE IF NOT EXISTS tunnel_records (
            user_id INTEGER PRIMARY KEY,
            max_rooms INTEGER DEFAULT 0,
            max_crumbs INTEGER DEFAULT 0,
            max_kills INTEGER DEFAULT 0,
            total_bosses_killed INTEGER DEFAULT 0
        )''')
        
        conn.commit()


def get_monster(monster_id: str) -> Optional[Dict]:
    """Возвращает данные монстра по ID"""
    return TUNNEL_MONSTERS.get(monster_id)


def calculate_monster_stats(monster: Dict, room_number: int) -> Dict:
    """Рассчитывает характеристики монстра с учётом номера комнаты"""
    monster_copy = monster.copy()
    
    room_multiplier = 1.0 + (room_number * 0.05)
    
    monster_copy["health"] = int(monster["health"] * room_multiplier)
    monster_copy["min_damage"] = max(1, int(monster["min_damage"] * room_multiplier))
    monster_copy["max_damage"] = max(2, int(monster["max_damage"] * room_multiplier))
    
    monster_copy["xp"] = int(monster["base_xp"] * (1.0 + room_number * 0.15))
    monster_copy["crumbs"] = int(monster["base_crumbs"] * (1.0 + room_number * 0.12))
    
    return monster_copy


def get_random_monster(room_number: int, exclude_boss: bool = True) -> Dict:
    """Возвращает случайного монстра подходящего уровня"""
    if room_number <= 6:
        max_level = 1
    elif room_number <= 12:
        max_level = 2
    elif room_number <= 18:
        max_level = 3
    else:
        max_level = 4
    
    elite_chance = 5 + (room_number // 5)
    
    available = []
    for mid, data in TUNNEL_MONSTERS.items():
        if exclude_boss and data.get("rarity") == "boss":
            continue
        
        if data.get("rarity") == "elite":
            if random.randint(1, 100) <= elite_chance:
                available.append((mid, data))
        elif data["level"] <= max_level and data.get("rarity") != "boss":
            available.append((mid, data))
    
    if not available:
        return {"id": "blind_mole", **TUNNEL_MONSTERS["blind_mole"]}
    
    mid, data = random.choice(available)
    monster = {"id": mid, **data}
    
    return calculate_monster_stats(monster, room_number)


def get_monster_pack(room_number: int) -> List[Dict]:
    """Создаёт стаю монстров (2-3 слабых)"""
    pack_size = random.randint(2, 3)
    monsters = []
    
    for _ in range(pack_size):
        pack_room = max(1, room_number - 2)
        monster = get_random_monster(pack_room)
        monster["health"] = int(monster["health"] * 0.6)
        monster["crumbs"] = int(monster["crumbs"] * 0.7)
        monsters.append(monster)
    
    return monsters


def process_loot(monster_id: str, room_number: int = 1, kill_streak: int = 0) -> Dict:
    """Обрабатывает дроп с монстра с учётом прогрессии и ресурсов"""
    monster = TUNNEL_MONSTERS.get(monster_id)
    if not monster:
        return {"crumbs": 0, "items": [], "resources": []}
    
    loot = {"crumbs": 0, "items": [], "resources": []}
    
    loot_table = monster.get("loot_table", {})
    
    # Прогрессивные крошки
    loot["crumbs"] = calculate_progressive_crumbs(monster, room_number, kill_streak)
    
    # Обрабатываем ресурсы из loot_table монстра
    for resource_data in loot_table.get("resources", []):
        chance = resource_data.get("chance", 10)
        if random.randint(1, 100) <= chance:
            loot["resources"].append(resource_data["item_id"])
    
    # Обрабатываем предметы
    rarity_multipliers = {
        "common": 0.6,
        "uncommon": 0.5,
        "rare": 0.4,
        "epic": 0.3,
        "elite": 1.0,
        "boss": 1.0,
    }
    
    monster_rarity = monster.get("rarity", "common")
    drop_multiplier = rarity_multipliers.get(monster_rarity, 0.5)
    
    for item_data in loot_table.get("items", []):
        original_chance = item_data.get("chance", 0)
        reduced_chance = max(1, int(original_chance * drop_multiplier))
        streak_bonus = min(20, kill_streak * 2)
        
        if random.randint(1, 100) <= reduced_chance + streak_bonus:
            loot["items"].append(item_data["item_id"])
    
    return loot


def calculate_progressive_crumbs(monster: Dict, room_number: int, kill_streak: int = 0) -> int:
    """Рассчитывает прогрессивные крошки"""
    base_crumbs = monster.get("base_crumbs", 10)
    multiplier = monster.get("loot_table", {}).get("crumbs", {}).get("multiplier", 1.0)
    
    room_bonus = 1.0 + (room_number * 0.1)
    streak_bonus = 1.0 + (min(10, kill_streak) * 0.05)
    
    total = int(base_crumbs * multiplier * room_bonus * streak_bonus)
    
    return random.randint(int(total * 0.8), int(total * 1.2))


def process_boss_loot(boss_id: str) -> List[str]:
    """Обрабатывает дроп с босса (гарантированный предмет)"""
    from handlers.items import ALL_ITEMS
    items = []
    
    boss = TUNNEL_MONSTERS.get(boss_id, {})
    loot_table = boss.get("loot_table", {}).get("items", [])
    
    for item_data in loot_table:
        if item_data.get("chance", 0) >= 100:
            items.append(item_data["item_id"])
        elif random.randint(1, 100) <= item_data.get("chance", 0):
            items.append(item_data["item_id"])
    
    if not items:
        common_items = [iid for iid, data in ALL_ITEMS.items() 
                        if data.get("rarity") == "common" and data.get("type") == "equipment"]
        if common_items:
            items.append(random.choice(common_items))
    
    return items


def start_tunnel_run(user_id: int):
    """Начинает новый забег"""
    stats = get_character_stats(user_id)
    
    with sqlite3.connect(DB_FILE) as conn:
        c = conn.cursor()
        
        increment_tunnel_runs(user_id)
        
        c.execute('''INSERT OR REPLACE INTO tunnel_run 
                     (user_id, current_room, rooms_completed, crumbs_collected, xp_collected, 
                      kill_streak, monsters_killed, blessed, run_seed)
                     VALUES (?, 1, 0, 0, 0, 0, 0, 0, ?)''',
                  (user_id, str(random.randint(1000, 9999))))
        conn.commit()
    
    return {"success": True, "stats": stats}


def update_tunnel_run(user_id: int, **kwargs):
    """Обновляет данные активного забега"""
    with sqlite3.connect(DB_FILE) as conn:
        c = conn.cursor()
        c.execute('SELECT user_id FROM tunnel_run WHERE user_id = ?', (user_id,))
        if not c.fetchone():
            return False
        
        updates = []
        values = []
        for k, v in kwargs.items():
            updates.append(f"{k} = ?")
            if isinstance(v, list):
                import json
                values.append(json.dumps(v))
            else:
                values.append(v)
        
        values.append(user_id)
        c.execute(f"UPDATE tunnel_run SET {','.join(updates)} WHERE user_id = ?", values)
        conn.commit()
        return True


def end_tunnel_run(user_id: int, died: bool = False, context=None):
    """Завершает забег и обновляет рекорды"""
    with sqlite3.connect(DB_FILE) as conn:
        c = conn.cursor()
        c.execute('''SELECT crumbs_collected, xp_collected, rooms_completed, monsters_killed
                     FROM tunnel_run WHERE user_id = ?''', (user_id,))
        row = c.fetchone()
        if row:
            crumbs = row[0]
            xp = row[1]
            rooms = row[2]
            kills = row[3]
            
            if died:
                crumbs = crumbs // 2
            
            if crumbs > 0:
                add_crumbs(user_id, crumbs)
            if xp > 0:
                add_xp(user_id, xp, context)
            
            c.execute('''INSERT INTO tunnel_records (user_id, max_rooms, max_crumbs, max_kills)
                         VALUES (?, ?, ?, ?)
                         ON CONFLICT(user_id) DO UPDATE SET
                         max_rooms = MAX(max_rooms, ?),
                         max_crumbs = MAX(max_crumbs, ?),
                         max_kills = MAX(max_kills, ?)''',
                      (user_id, rooms, crumbs, kills, rooms, crumbs, kills))
            
            c.execute('DELETE FROM tunnel_run WHERE user_id = ?', (user_id,))
            conn.commit()
            
            return {"crumbs": crumbs, "xp": xp, "rooms": rooms, "kills": kills}
    return {"crumbs": 0, "xp": 0, "rooms": 0, "kills": 0}


def get_tunnel_run(user_id: int) -> Optional[Dict]:
    """Возвращает активный забег"""
    with sqlite3.connect(DB_FILE) as conn:
        c = conn.cursor()
        c.execute('''SELECT current_room, rooms_completed, crumbs_collected, xp_collected, 
                     kill_streak, monsters_killed, path_choice, blessed, blessings
                     FROM tunnel_run WHERE user_id = ?''', (user_id,))
        row = c.fetchone()
        if row:
            import json
            blessings = row[8]
            if blessings and isinstance(blessings, str):
                try:
                    blessings = json.loads(blessings)
                except:
                    blessings = []
            return {
                "current_room": row[0],
                "rooms_completed": row[1],
                "crumbs_collected": row[2],
                "xp_collected": row[3],
                "kill_streak": row[4],
                "monsters_killed": row[5],
                "path_choice": row[6],
                "blessed": bool(row[7]),
                "blessings": blessings if blessings else []
            }
    return None


def advance_room(user_id: int):
    """Переходит в следующую комнату"""
    with sqlite3.connect(DB_FILE) as conn:
        c = conn.cursor()
        c.execute('''UPDATE tunnel_run 
                     SET current_room = current_room + 1, rooms_completed = rooms_completed + 1 
                     WHERE user_id = ?''', (user_id,))
        conn.commit()


def add_run_loot(user_id: int, crumbs: int, xp: int, increment_kills: bool = True):
    """Добавляет добычу в текущий забег и обновляет серию убийств"""
    with sqlite3.connect(DB_FILE) as conn:
        c = conn.cursor()
        if increment_kills:
            c.execute('''UPDATE tunnel_run 
                         SET crumbs_collected = crumbs_collected + ?, 
                             xp_collected = xp_collected + ?,
                             kill_streak = kill_streak + 1,
                             monsters_killed = monsters_killed + 1
                         WHERE user_id = ?''', (crumbs, xp, user_id))
        else:
            c.execute('''UPDATE tunnel_run 
                         SET crumbs_collected = crumbs_collected + ?, 
                             xp_collected = xp_collected + ?
                         WHERE user_id = ?''', (crumbs, xp, user_id))
        conn.commit()


def reset_kill_streak(user_id: int):
    """Сбрасывает серию убийств"""
    with sqlite3.connect(DB_FILE) as conn:
        c = conn.cursor()
        c.execute('UPDATE tunnel_run SET kill_streak = 0 WHERE user_id = ?', (user_id,))
        conn.commit()


def set_blessed(user_id: int, blessed: bool):
    """Устанавливает благословение на забег"""
    with sqlite3.connect(DB_FILE) as conn:
        c = conn.cursor()
        c.execute('UPDATE tunnel_run SET blessed = ? WHERE user_id = ?', (1 if blessed else 0, user_id))
        conn.commit()


def set_path_choice(user_id: int, path: str):
    """Устанавливает выбор пути (easy/hard)"""
    with sqlite3.connect(DB_FILE) as conn:
        c = conn.cursor()
        c.execute('UPDATE tunnel_run SET path_choice = ? WHERE user_id = ?', (path, user_id))
        conn.commit()


def is_boss_defeated(user_id: int, monster_id: str) -> bool:
    """Проверяет, побеждал ли игрок этого босса"""
    with sqlite3.connect(DB_FILE) as conn:
        c = conn.cursor()
        c.execute('SELECT 1 FROM tunnel_bosses_defeated WHERE user_id = ? AND monster_id = ?', (user_id, monster_id))
        return c.fetchone() is not None


def mark_boss_defeated(user_id: int, monster_id: str):
    """Отмечает босса как побеждённого"""
    with sqlite3.connect(DB_FILE) as conn:
        c = conn.cursor()
        try:
            c.execute('INSERT INTO tunnel_bosses_defeated (user_id, monster_id) VALUES (?, ?)', (user_id, monster_id))
            c.execute('UPDATE tunnel_records SET total_bosses_killed = total_bosses_killed + 1 WHERE user_id = ?', (user_id,))
            conn.commit()
        except sqlite3.IntegrityError:
            pass


def get_tunnel_records(user_id: int) -> Dict:
    """Возвращает рекорды игрока в туннелях"""
    with sqlite3.connect(DB_FILE) as conn:
        c = conn.cursor()
        c.execute('''SELECT max_rooms, max_crumbs, max_kills, total_bosses_killed 
                     FROM tunnel_records WHERE user_id = ?''', (user_id,))
        row = c.fetchone()
        if row:
            return {
                "max_rooms": row[0],
                "max_crumbs": row[1],
                "max_kills": row[2],
                "total_bosses_killed": row[3]
            }
    return {"max_rooms": 0, "max_crumbs": 0, "max_kills": 0, "total_bosses_killed": 0}


# Инициализация
init_tunnel_monsters_db()