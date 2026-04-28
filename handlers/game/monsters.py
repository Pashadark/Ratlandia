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
        "base_crumbs": 15,
        "base_xp": 30,
        "ability": None,
        "ability_desc": None,
        "icon": "🦔",
        "desc": "_Из земли вырывается огромный слепой крот._",
        "death_text": "_Крот заваливается на бок и замирает._",
        "loot_table": {
            "crumbs": {"multiplier": 1.0},
            "items": [
                {"item_id": "leather_vest", "chance": 5},
                {"item_id": "cheese_wedge_hat", "chance": 3},
                {"item_id": "common_chest", "chance": 2},
                {"item_id": "recipe_cheese_sword", "chance": 4},
                {"item_id": "recipe_leather_vest", "chance": 4},
                {"item_id": "rusty_sword", "chance": 3},
                {"item_id": "bone_knife", "chance": 3},
                {"item_id": "recipe_rusty_sword", "chance": 2},
            ],
            "resources": [
                {"item_id": "stone_shard", "chance": 25},
                {"item_id": "mouse_bone", "chance": 20},
                {"item_id": "rat_pelt", "chance": 15},
                {"item_id": "copper_scrap", "chance": 10},
                {"item_id": "cheese_crust", "chance": 15},
                {"item_id": "bread_crumb", "chance": 10},
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
        "base_crumbs": 12,
        "base_xp": 25,
        "ability": "curl",
        "ability_desc": "_Сворачивается в клубок при HP < 50%_",
        "icon": "🪲",
        "desc": "_Огромная мокрица копошится в гнилых досках._",
        "death_text": "_Мокрица переворачивается на спину и замирает._",
        "loot_table": {
            "crumbs": {"multiplier": 1.0},
            "items": [
                {"item_id": "gambeson", "chance": 4},
                {"item_id": "bubble_wrap", "chance": 5},
                {"item_id": "recipe_gambeson", "chance": 4},
                {"item_id": "recipe_poison_cheese", "chance": 3},
                {"item_id": "wooden_bow", "chance": 3},
                {"item_id": "recipe_wooden_bow", "chance": 2},
                {"item_id": "recipe_apprentice_robe", "chance": 2},
            ],
            "resources": [
                {"item_id": "stone_shard", "chance": 20},
                {"item_id": "copper_scrap", "chance": 15},
                {"item_id": "rat_incisor", "chance": 15},
                {"item_id": "spider_web", "chance": 12},
                {"item_id": "linen_scrap", "chance": 10},
                {"item_id": "moldy_crumb", "chance": 12},
                {"item_id": "pigeon_feather", "chance": 10},
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
        "base_crumbs": 18,
        "base_xp": 35,
        "ability": "regeneration",
        "ability_desc": "_Восстанавливает 1 HP каждый ход_",
        "icon": "🪱",
        "desc": "_Толстый розовый червь выползает из стены._",
        "death_text": "_Червь распадается на две половинки._",
        "loot_table": {
            "crumbs": {"multiplier": 1.0},
            "items": [
                {"item_id": "holy_water", "chance": 4},
                {"item_id": "poison_vial", "chance": 3},
                {"item_id": "recipe_cheese_sword", "chance": 3},
                {"item_id": "iron_blade", "chance": 3},
                {"item_id": "recipe_iron_blade", "chance": 2},
            ],
            "resources": [
                {"item_id": "mouse_bone", "chance": 20},
                {"item_id": "fish_spine", "chance": 15},
                {"item_id": "rat_pelt", "chance": 10},
                {"item_id": "clean_water", "chance": 15},
                {"item_id": "basement_mushroom", "chance": 12},
                {"item_id": "empty_vial", "chance": 8},
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
        "base_crumbs": 25,
        "base_xp": 50,
        "ability": "fast",
        "ability_desc": "_20% шанс атаковать дважды_",
        "icon": "🐀",
        "desc": "_Маленькое юркое существо мечется из угла в угол._",
        "death_text": "_Шуршун замирает и падает._",
        "loot_table": {
            "crumbs": {"multiplier": 1.5},
            "items": [
                {"item_id": "lucky_coin", "chance": 8},
                {"item_id": "ninja_mask", "chance": 3},
                {"item_id": "jagged_dagger", "chance": 4},
                {"item_id": "hunter_bow", "chance": 4},
                {"item_id": "recipe_thief_vest", "chance": 3},
                {"item_id": "enchant_scroll_weapon", "chance": 1},
            ],
            "resources": [
                {"item_id": "rat_pelt", "chance": 20},
                {"item_id": "rat_incisor", "chance": 20},
                {"item_id": "copper_scrap", "chance": 15},
                {"item_id": "leather_scrap", "chance": 12},
                {"item_id": "wool_clump", "chance": 10},
                {"item_id": "pigeon_feather", "chance": 10},
                {"item_id": "smooth_pebble", "chance": 8},
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
        "base_crumbs": 10,
        "base_xp": 40,
        "ability": "spores",
        "ability_desc": "_30% шанс отравить на 2 хода_",
        "icon": "🍄",
        "desc": "_Комок серо-зелёной плесени медленно ползёт._",
        "death_text": "_Плесневик высыхает в порошок._",
        "loot_table": {
            "crumbs": {"multiplier": 0.8},
            "items": [
                {"item_id": "poison_cheese", "chance": 10},
                {"item_id": "rat_poison_antidote", "chance": 5},
                {"item_id": "recipe_poison_cheese", "chance": 5},
                {"item_id": "apprentice_robe", "chance": 3},
                {"item_id": "recipe_apprentice_robe", "chance": 2},
            ],
            "resources": [
                {"item_id": "moldy_crumb", "chance": 25},
                {"item_id": "basement_mushroom", "chance": 20},
                {"item_id": "empty_vial", "chance": 10},
                {"item_id": "rat_poison", "chance": 8},
                {"item_id": "spider_web", "chance": 10},
                {"item_id": "candle_stub", "chance": 8},
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
        "base_crumbs": 40,
        "base_xp": 80,
        "ability": "block",
        "ability_desc": "_Раз в 3 хода блокирует атаку_",
        "icon": "🐀",
        "desc": "_Огромная крыса со шрамами на морде._",
        "death_text": "_Крыса падает на бок._",
        "loot_table": {
            "crumbs": {"multiplier": 1.5},
            "items": [
                {"item_id": "rat_dagger", "chance": 6},
                {"item_id": "rat_ears", "chance": 5},
                {"item_id": "rare_chest", "chance": 2},
                {"item_id": "recipe_rat_dagger", "chance": 5},
                {"item_id": "recipe_viking_helmet", "chance": 5},
                {"item_id": "steel_sword", "chance": 3},
                {"item_id": "recipe_steel_sword", "chance": 2},
                {"item_id": "enchant_scroll_armor", "chance": 1},
            ],
            "resources": [
                {"item_id": "iron_gear", "chance": 20},
                {"item_id": "bronze_alloy", "chance": 15},
                {"item_id": "rat_pelt", "chance": 15},
                {"item_id": "rat_incisor", "chance": 12},
                {"item_id": "smoked_lard", "chance": 10},
                {"item_id": "spider_silk", "chance": 10},
                {"item_id": "mole_skull", "chance": 8},
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
        "base_crumbs": 30,
        "base_xp": 60,
        "ability": "many_legs",
        "ability_desc": "_Всегда атакует дважды_",
        "icon": "🐛",
        "desc": "_Длинная многоножка с десятками сегментов._",
        "death_text": "_Многоножка сворачивается в спираль._",
        "loot_table": {
            "crumbs": {"multiplier": 1.2},
            "items": [
                {"item_id": "chainmail", "chance": 5},
                {"item_id": "poison_vial", "chance": 6},
                {"item_id": "recipe_chainmail", "chance": 5},
                {"item_id": "poison_stiletto", "chance": 2},
                {"item_id": "recipe_poison_stiletto", "chance": 2},
            ],
            "resources": [
                {"item_id": "fish_spine", "chance": 20},
                {"item_id": "rat_tail_vertebra", "chance": 15},
                {"item_id": "bat_membrane", "chance": 12},
                {"item_id": "iron_gear", "chance": 10},
                {"item_id": "wall_soot", "chance": 12},
                {"item_id": "honey_drop", "chance": 8},
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
        "base_crumbs": 45,
        "base_xp": 90,
        "ability": "hard_shell",
        "ability_desc": "_Каждую 3-ю атаку игнорирует_",
        "icon": "🪲",
        "desc": "_Огромный чёрный жук с блестящим панцирем._",
        "death_text": "_Панцирь жука трескается._",
        "loot_table": {
            "crumbs": {"multiplier": 1.5},
            "items": [
                {"item_id": "turtle_shell", "chance": 5},
                {"item_id": "bulletproof_vest", "chance": 4},
                {"item_id": "rare_chest", "chance": 2},
                {"item_id": "recipe_viking_helmet", "chance": 5},
                {"item_id": "recipe_smoke_bomb", "chance": 4},
                {"item_id": "iron_plate", "chance": 3},
                {"item_id": "recipe_iron_plate", "chance": 2},
                {"item_id": "enchant_scroll_armor", "chance": 1},
            ],
            "resources": [
                {"item_id": "bronze_alloy", "chance": 20},
                {"item_id": "iron_gear", "chance": 18},
                {"item_id": "snake_skin", "chance": 12},
                {"item_id": "mole_skull", "chance": 10},
                {"item_id": "smoked_lard", "chance": 10},
                {"item_id": "surface_shell", "chance": 8},
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
        "base_crumbs": 25,
        "base_xp": 70,
        "ability": "slow",
        "ability_desc": "_При попадании замедляет на 1 ход_",
        "icon": "🐌",
        "desc": "_Огромный слизистый комок._",
        "death_text": "_Слизень растекается лужей._",
        "loot_table": {
            "crumbs": {"multiplier": 1.0},
            "items": [
                {"item_id": "stinky_sock", "chance": 10},
                {"item_id": "holy_water", "chance": 5},
                {"item_id": "recipe_chainmail", "chance": 5},
                {"item_id": "composite_bow", "chance": 3},
                {"item_id": "gem_emerald", "chance": 2},
            ],
            "resources": [
                {"item_id": "rat_pelt", "chance": 15},
                {"item_id": "spider_silk", "chance": 15},
                {"item_id": "bat_membrane", "chance": 12},
                {"item_id": "empty_vial", "chance": 12},
                {"item_id": "clean_water", "chance": 10},
                {"item_id": "honey_drop", "chance": 8},
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
        "base_crumbs": 60,
        "base_xp": 120,
        "ability": "vampirism",
        "ability_desc": "_Восстанавливает половину урона_",
        "icon": "🦇",
        "desc": "_Тёмный силуэт срывается с потолка._",
        "death_text": "_Мышь падает на пол и затихает._",
        "loot_table": {
            "crumbs": {"multiplier": 2.0},
            "items": [
                {"item_id": "shadow_hood", "chance": 5},
                {"item_id": "epic_chest", "chance": 1},
                {"item_id": "recipe_crossbow", "chance": 4},
                {"item_id": "shadow_dagger", "chance": 2},
                {"item_id": "blessed_scroll_weapon", "chance": 1},
            ],
            "resources": [
                {"item_id": "bat_membrane", "chance": 25},
                {"item_id": "bat_fang", "chance": 10},
                {"item_id": "rat_king_tear", "chance": 10},
                {"item_id": "steel_shard", "chance": 8},
                {"item_id": "fairy_dust", "chance": 8},
                {"item_id": "human_coin", "chance": 5},
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
        "base_crumbs": 75,
        "base_xp": 140,
        "ability": "web",
        "ability_desc": "_Раз в 3 хода опутывает паутиной_",
        "icon": "🕷️",
        "desc": "_Огромный паук с мохнатыми лапами._",
        "death_text": "_Паук падает с паутины._",
        "loot_table": {
            "crumbs": {"multiplier": 1.8},
            "items": [
                {"item_id": "ninja_mask", "chance": 6},
                {"item_id": "net_launcher", "chance": 5},
                {"item_id": "epic_chest", "chance": 3},
                {"item_id": "recipe_crossbow", "chance": 5},
                {"item_id": "recipe_butcher_knife", "chance": 3},
                {"item_id": "assassin_dagger", "chance": 2},
                {"item_id": "shadow_leather", "chance": 2},
                {"item_id": "gem_diamond", "chance": 2},
            ],
            "resources": [
                {"item_id": "spider_silk", "chance": 25},
                {"item_id": "steel_shard", "chance": 15},
                {"item_id": "silver_ingot", "chance": 12},
                {"item_id": "rat_poison", "chance": 12},
                {"item_id": "crow_bone", "chance": 10},
                {"item_id": "marrow_bone", "chance": 10},
                {"item_id": "cloudy_crystal", "chance": 8},
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
        "base_crumbs": 65,
        "base_xp": 130,
        "ability": "curl_ball",
        "ability_desc": "_При HP < 30% сворачивается в шар_",
        "icon": "🪱",
        "desc": "_Существо из твёрдых сегментов._",
        "death_text": "_Броненосец рассыпается на части._",
        "loot_table": {
            "crumbs": {"multiplier": 1.5},
            "items": [
                {"item_id": "turtle_shell", "chance": 8},
                {"item_id": "bulletproof_vest", "chance": 5},
                {"item_id": "recipe_butcher_knife", "chance": 3},
                {"item_id": "steel_cuirass", "chance": 3},
                {"item_id": "mithril_sword", "chance": 2},
                {"item_id": "gem_topaz", "chance": 2},
            ],
            "resources": [
                {"item_id": "iron_gear", "chance": 18},
                {"item_id": "steel_shard", "chance": 15},
                {"item_id": "rat_tail_vertebra", "chance": 12},
                {"item_id": "emerald_crumb", "chance": 10},
                {"item_id": "rat_king_tear", "chance": 10},
                {"item_id": "mirror_shard_res", "chance": 8},
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
        "base_crumbs": 100,
        "base_xp": 200,
        "ability": "frenzy",
        "ability_desc": "_При HP < 50% впадает в ярость_",
        "icon": "🐀💀",
        "desc": "_Тощая серая крыса с белыми глазами._",
        "death_text": "_Тело упыря затихает._",
        "loot_table": {
            "crumbs": {"multiplier": 2.0},
            "items": [
                {"item_id": "butcher_knife", "chance": 4},
                {"item_id": "demon_skin", "chance": 2},
                {"item_id": "legendary_chest", "chance": 1},
                {"item_id": "recipe_butcher_knife", "chance": 4},
                {"item_id": "recipe_invisibility_cloak", "chance": 3},
                {"item_id": "blood_dagger", "chance": 2},
                {"item_id": "berserker_harness", "chance": 2},
                {"item_id": "blessed_scroll_weapon", "chance": 1},
            ],
            "resources": [
                {"item_id": "steel_shard", "chance": 18},
                {"item_id": "silver_ingot", "chance": 15},
                {"item_id": "rat_poison", "chance": 15},
                {"item_id": "crow_bone", "chance": 12},
                {"item_id": "fairy_dust", "chance": 10},
                {"item_id": "moon_dew", "chance": 10},
                {"item_id": "underground_truffle", "chance": 8},
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
        "base_crumbs": 50,
        "base_xp": 100,
        "ability": "survival",
        "ability_desc": "_50% шанс при смерти восстановить HP_",
        "icon": "🪳",
        "desc": "_Усатый монстр размером с собаку._",
        "death_text": "_Таракан переворачивается на спину._",
        "loot_table": {
            "crumbs": {"multiplier": 1.2},
            "items": [
                {"item_id": "lucky_rabbit_foot", "chance": 4},
                {"item_id": "recipe_crossbow", "chance": 4},
                {"item_id": "cheese_blade", "chance": 3},
                {"item_id": "gem_ruby", "chance": 2},
            ],
            "resources": [
                {"item_id": "rat_pelt", "chance": 15},
                {"item_id": "iron_gear", "chance": 12},
                {"item_id": "bronze_alloy", "chance": 12},
                {"item_id": "spider_silk", "chance": 10},
                {"item_id": "marrow_bone", "chance": 10},
                {"item_id": "human_coin", "chance": 8},
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
        "base_crumbs": 70,
        "base_xp": 150,
        "ability": "attach",
        "ability_desc": "_Присасывается к туловищу_",
        "icon": "🪱🩸",
        "desc": "_Чёрная блестящая тварь в грязной воде._",
        "death_text": "_Пиявка сжимается в комок._",
        "loot_table": {
            "crumbs": {"multiplier": 1.5},
            "items": [
                {"item_id": "holy_water", "chance": 10},
                {"item_id": "rat_poison_antidote", "chance": 6},
                {"item_id": "recipe_invisibility_cloak", "chance": 3},
                {"item_id": "shadow_leather", "chance": 2},
                {"item_id": "gem_sapphire", "chance": 2},
            ],
            "resources": [
                {"item_id": "rat_poison", "chance": 18},
                {"item_id": "rat_king_tear", "chance": 15},
                {"item_id": "fish_spine", "chance": 12},
                {"item_id": "clean_water", "chance": 12},
                {"item_id": "silver_ingot", "chance": 10},
                {"item_id": "honey_drop", "chance": 8},
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
        "base_crumbs": 120,
        "base_xp": 300,
        "ability": "hypnosis",
        "ability_desc": "_Раз в 4 хода гипнотизирует_",
        "icon": "🦡",
        "desc": "_Грациозное чёрное тело скользит в темноте._",
        "death_text": "_Хорёк издаёт визг и падает._",
        "loot_table": {
            "crumbs": {"multiplier": 2.5},
            "items": [
                {"item_id": "shadow_hood", "chance": 8},
                {"item_id": "invisibility_cloak", "chance": 3},
                {"item_id": "legendary_chest", "chance": 2},
                {"item_id": "recipe_crown_of_rat_king", "chance": 4},
                {"item_id": "recipe_invisibility_cloak", "chance": 4},
                {"item_id": "death_whisper", "chance": 2},
                {"item_id": "mithril_plate", "chance": 2},
                {"item_id": "elven_bow", "chance": 2},
                {"item_id": "crystal_scroll_weapon", "chance": 1},
            ],
            "resources": [
                {"item_id": "obsidian_scale", "chance": 15},
                {"item_id": "mithril_nugget", "chance": 12},
                {"item_id": "bat_fang", "chance": 12},
                {"item_id": "moon_silk", "chance": 10},
                {"item_id": "phoenix_ember", "chance": 8},
                {"item_id": "magnetic_stone", "chance": 8},
                {"item_id": "forgotten_ale", "chance": 5},
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
        "base_crumbs": 175,
        "base_xp": 500,
        "ability": "two_heads",
        "ability_desc": "_Всегда атакует дважды_",
        "icon": "🐀🐀",
        "desc": "_Огромная крыса с двумя головами._",
        "death_text": "_Обе головы испускают хрип._",
        "loot_table": {
            "crumbs": {"multiplier": 3.0},
            "items": [
                {"item_id": "crown_of_rat_king", "chance": 4},
                {"item_id": "rat_king_crown_broken", "chance": 6},
                {"item_id": "mythic_chest", "chance": 1},
                {"item_id": "recipe_crown_of_mouse_king", "chance": 5},
                {"item_id": "rat_catcher_sword", "chance": 2},
                {"item_id": "sorcerer_robe", "chance": 2},
                {"item_id": "crystal_scroll_armor", "chance": 1},
            ],
            "resources": [
                {"item_id": "mithril_nugget", "chance": 18},
                {"item_id": "obsidian_scale", "chance": 15},
                {"item_id": "rat_king_eye", "chance": 12},
                {"item_id": "cat_pelt", "chance": 10},
                {"item_id": "mage_blood", "chance": 10},
                {"item_id": "ancient_scrap", "chance": 8},
                {"item_id": "ancient_amulet", "chance": 5},
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
        "base_crumbs": 140,
        "base_xp": 360,
        "ability": "constrict",
        "ability_desc": "_40% шанс обвить при атаке_",
        "icon": "🐍",
        "desc": "_Длинное мускулистое тело скользит по трубе._",
        "death_text": "_Тело ужа обмякает._",
        "loot_table": {
            "crumbs": {"multiplier": 2.5},
            "items": [
                {"item_id": "dragon_scale", "chance": 3},
                {"item_id": "legendary_chest", "chance": 2},
                {"item_id": "recipe_crown_of_rat_king", "chance": 4},
                {"item_id": "king_blade", "chance": 1},
                {"item_id": "dragon_leather", "chance": 2},
                {"item_id": "gem_onyx", "chance": 1},
            ],
            "resources": [
                {"item_id": "snake_skin", "chance": 20},
                {"item_id": "obsidian_scale", "chance": 15},
                {"item_id": "rat_tail_vertebra", "chance": 12},
                {"item_id": "mandrake", "chance": 10},
                {"item_id": "hermit_rosary", "chance": 8},
                {"item_id": "phoenix_ember", "chance": 5},
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
        "base_crumbs": 200,
        "base_xp": 400,
        "ability": "summon",
        "ability_desc": "_Призывает кротов-помощников_",
        "icon": "👑🦔",
        "desc": "_Огромный крот с короной из костей._",
        "death_text": "_Король кротов падает, туннель дрожит._",
        "loot_table": {
            "crumbs": {"multiplier": 4.0},
            "items": [
                {"item_id": "crown_of_mouse_king", "chance": 10},
                {"item_id": "epic_chest", "chance": 12},
                {"item_id": "legendary_chest", "chance": 5},
                {"item_id": "recipe_crown_of_rat_king", "chance": 6},
                {"item_id": "recipe_crown_of_mouse_king", "chance": 6},
                {"item_id": "recipe_butcher_knife", "chance": 5},
                {"item_id": "titan_armor", "chance": 2},
                {"item_id": "mithril_plate", "chance": 3},
                {"item_id": "longbow_of_truth", "chance": 2},
                {"item_id": "blessed_scroll_armor", "chance": 2},
                {"item_id": "gem_amethyst", "chance": 2},
            ],
            "resources": [
                {"item_id": "obsidian_scale", "chance": 20},
                {"item_id": "mithril_nugget", "chance": 18},
                {"item_id": "moon_silk", "chance": 15},
                {"item_id": "bat_fang", "chance": 12},
                {"item_id": "rat_king_eye", "chance": 12},
                {"item_id": "mage_blood", "chance": 10},
                {"item_id": "phoenix_ember", "chance": 8},
                {"item_id": "magnetic_stone", "chance": 10},
                {"item_id": "ancient_scrap", "chance": 8},
                {"item_id": "void_essence", "chance": 3},
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
        "base_crumbs": 300,
        "base_xp": 700,
        "ability": "summon_spiders",
        "ability_desc": "_Призывает пауков каждые 3 хода_",
        "icon": "👑🕷️",
        "desc": "_Гигантская паучиха с тысячами детёнышей на спине._",
        "death_text": "_Королева пауков издаёт предсмертный визг._",
        "loot_table": {
            "crumbs": {"multiplier": 5.0},
            "items": [
                {"item_id": "cloak_of_mouse_god", "chance": 6},
                {"item_id": "mythic_chest", "chance": 5},
                {"item_id": "legendary_chest", "chance": 10},
                {"item_id": "recipe_crown_of_rat_king", "chance": 6},
                {"item_id": "recipe_crown_of_mouse_king", "chance": 6},
                {"item_id": "recipe_invisibility_cloak", "chance": 5},
                {"item_id": "storm_bow", "chance": 2},
                {"item_id": "archmage_robe", "chance": 2},
                {"item_id": "ninja_gi", "chance": 2},
                {"item_id": "gem_obsidian", "chance": 2},
                {"item_id": "crystal_scroll_weapon", "chance": 1},
            ],
            "resources": [
                {"item_id": "spider_silk", "chance": 30},
                {"item_id": "moon_silk", "chance": 20},
                {"item_id": "mithril_nugget", "chance": 18},
                {"item_id": "obsidian_scale", "chance": 15},
                {"item_id": "bat_fang", "chance": 12},
                {"item_id": "rat_king_eye", "chance": 12},
                {"item_id": "mage_blood", "chance": 10},
                {"item_id": "phoenix_ember", "chance": 10},
                {"item_id": "void_essence", "chance": 8},
                {"item_id": "adamantite", "chance": 5},
                {"item_id": "star_silk", "chance": 5},
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
        "base_xp": 800,
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
                {"item_id": "mythic_chest", "chance": 30},
                {"item_id": "recipe_crown_of_rat_king", "chance": 15},
                {"item_id": "recipe_crown_of_mouse_king", "chance": 15},
                {"item_id": "recipe_invisibility_cloak", "chance": 10},
                {"item_id": "recipe_butcher_knife", "chance": 10},
                {"item_id": "first_hero_sword", "chance": 5},
                {"item_id": "divine_sword", "chance": 5},
                {"item_id": "celestial_longbow", "chance": 5},
                {"item_id": "aegis_divine", "chance": 5},
                {"item_id": "ragnarok_armor", "chance": 5},
                {"item_id": "omniscient_shroud", "chance": 5},
                {"item_id": "nightstalker_garb", "chance": 5},
                {"item_id": "rapier", "chance": 3},
                {"item_id": "gem_moonstone", "chance": 5},
                {"item_id": "crystal_scroll_weapon", "chance": 8},
                {"item_id": "crystal_scroll_armor", "chance": 8},
                {"item_id": "blessed_scroll_weapon", "chance": 10},
                {"item_id": "blessed_scroll_armor", "chance": 10},
                {"item_id": "enchant_scroll_weapon", "chance": 15},
                {"item_id": "enchant_scroll_armor", "chance": 15},
                {"item_id": "recipe_rapier", "chance": 5},
                {"item_id": "recipe_first_hero_sword", "chance": 5},
                {"item_id": "recipe_celestial_longbow", "chance": 5},
            ],
            "resources": [
                {"item_id": "mithril_nugget", "chance": 30},
                {"item_id": "obsidian_scale", "chance": 25},
                {"item_id": "adamantite", "chance": 18},
                {"item_id": "rat_god_tooth", "chance": 15},
                {"item_id": "star_silk", "chance": 18},
                {"item_id": "first_rat_skull", "chance": 12},
                {"item_id": "labyrinth_heart", "chance": 10},
                {"item_id": "void_essence", "chance": 18},
                {"item_id": "spark_creation", "chance": 10},
                {"item_id": "phoenix_ember", "chance": 15},
                {"item_id": "ice_worm_tear", "chance": 15},
                {"item_id": "storm_spark", "chance": 15},
                {"item_id": "mage_blood", "chance": 18},
                {"item_id": "gate_key", "chance": 10},
                {"item_id": "labyrinth_seal", "chance": 10},
                {"item_id": "tapestry_scrap", "chance": 10},
                {"item_id": "forgotten_ale", "chance": 12},
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


def calculate_monster_stats(monster: Dict, room_number: int, player_level: int = 1, kill_streak: int = 0) -> Dict:
    """Рассчитывает характеристики монстра и опыт с учётом номера комнаты, уровня игрока и серии убийств"""
    monster_copy = monster.copy()
    
    # Характеристики монстра
    room_multiplier = 1.0 + (room_number * 0.05)
    monster_copy["health"] = int(monster["health"] * room_multiplier)
    monster_copy["min_damage"] = max(1, int(monster["min_damage"] * room_multiplier))
    monster_copy["max_damage"] = max(2, int(monster["max_damage"] * room_multiplier))
    
    # ОПЫТ: Увеличенная формула
    base_xp = monster.get("base_xp", 10)
    
    # Модификатор уровня игрока
    if player_level <= 5:
        level_mod = 1.5
    elif player_level <= 10:
        level_mod = 1.2
    elif player_level <= 20:
        level_mod = 1.0
    else:
        level_mod = 0.8
    
    # Модификатор редкости
    rarity_mods = {
        "common": 1.0,
        "uncommon": 1.5,
        "rare": 2.5,
        "epic": 4.0,
        "elite": 6.0,
        "boss": 10.0,
    }
    rarity_mod = rarity_mods.get(monster.get("rarity", "common"), 1.0)
    
    # Бонус за глубину
    if room_number <= 5:
        depth_bonus = 1.1
    elif room_number <= 10:
        depth_bonus = 1.25
    elif room_number <= 15:
        depth_bonus = 1.5
    elif room_number <= 19:
        depth_bonus = 1.75
    else:
        depth_bonus = 2.0
    
    # Бонус за серию убийств
    streak_bonus = 1.0 + min(1.0, kill_streak * 0.1)
    
    total_xp = int(base_xp * level_mod * rarity_mod * depth_bonus * streak_bonus)
    monster_copy["xp"] = max(10, total_xp)
    
    # Крошки (увеличено)
    monster_copy["crumbs"] = int(monster["base_crumbs"] * (1.0 + room_number * 0.15))
    
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
    
    return monster


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
        "common": 0.5,
        "uncommon": 0.4,
        "rare": 0.3,
        "epic": 0.2,
        "elite": 1.0,
        "boss": 1.0,
    }
    
    monster_rarity = monster.get("rarity", "common")
    drop_multiplier = rarity_multipliers.get(monster_rarity, 0.5)
    
    for item_data in loot_table.get("items", []):
        original_chance = item_data.get("chance", 0)
        if original_chance <= 0:
            continue
        reduced_chance = max(1, int(original_chance * drop_multiplier))
        streak_bonus = min(15, kill_streak * 1)
        
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