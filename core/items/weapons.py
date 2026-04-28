"""Оружие ближнего боя — мечи и кинжалы с уроном"""

# ========== ОРУЖИЕ БЛИЖНЕГО БОЯ ==========
NEW_WEAPONS = {
    # ===== МЕЧИ =====
    "rusty_sword": {
        "name": "Ржавый меч", "type": "equipment", "slot": "weapon",
        "role": "all", "rarity": "common",
        "desc": "+2 к силе. Базовое оружие.",
        "effect": {"strength": 2},
        "armor": 0, "icon": "🗡️", "price": 300,
        "lore": "Покрытый ржавчиной клинок, найденный в старом сундуке. Ещё послужит.",
        "craftable": True,
        "craft_materials": {"iron_gear": 3, "copper_scrap": 2, "stone_shard": 2}
    },
    "iron_blade": {
        "name": "Железный клинок", "type": "equipment", "slot": "weapon",
        "role": "all", "rarity": "common",
        "desc": "+3 к силе.",
        "effect": {"strength": 3},
        "armor": 0, "icon": "⚔️", "price": 600,
        "lore": "Простой, но надёжный меч. Верный спутник начинающего искателя.",
        "craftable": True,
        "craft_materials": {"iron_gear": 5, "bronze_alloy": 2, "leather_scrap": 1}
    },
    "steel_sword": {
        "name": "Стальной меч", "type": "equipment", "slot": "weapon",
        "role": "all", "rarity": "rare",
        "desc": "+5 к силе. +1 к минимальному урону.",
        "effect": {"strength": 5, "min_damage": 1},
        "armor": 0, "icon": "🗡️", "price": 3000,
        "lore": "Клинок из закалённой стали. Хороший баланс между весом и остротой.",
        "craftable": True,
        "craft_materials": {"steel_shard": 4, "bronze_alloy": 3, "iron_gear": 2}
    },
    "mithril_sword": {
        "name": "Мифриловый меч", "type": "equipment", "slot": "weapon",
        "role": "all", "rarity": "epic",
        "desc": "+8 к силе. Светится в темноте.",
        "effect": {"strength": 8},
        "armor": 0, "icon": "✨", "price": 15000,
        "lore": "Лёгкий клинок из мифрила. Сияет голубоватым светом в присутствии опасности.",
        "craftable": True,
        "craft_materials": {"mithril_nugget": 3, "silver_ingot": 2, "fairy_dust": 1}
    },
    "shadow_blade_sword": {
        "name": "Клинок Теней", "type": "equipment", "slot": "weapon",
        "role": "rat", "rarity": "epic",
        "desc": "+6 к ловкости. +10% шанс критического удара.",
        "effect": {"agility": 6, "crit_chance": 10},
        "armor": 0, "icon": "🌑", "price": 18000,
        "lore": "Клинок, выкованный в абсолютной темноте. Не отражает свет.",
        "craftable": True,
        "craft_materials": {"obsidian_scale": 4, "steel_shard": 3, "bat_fang": 2}
    },
    "cheese_blade": {
        "name": "Сырной клинок", "type": "equipment", "slot": "weapon",
        "role": "all", "rarity": "rare",
        "desc": "+4 к силе. +5% опыта за бой.",
        "effect": {"strength": 4, "xp_boost": 5},
        "armor": 0, "icon": "🧀", "price": 4000,
        "lore": "Затвердевший пармезан, заточенный до бритвенной остроты. Пахнет божественно.",
        "craftable": True,
        "craft_materials": {"cheese_crust": 8, "iron_gear": 2, "honey_drop": 1}
    },
    "rat_catcher_sword": {
        "name": "Меч Крысолова", "type": "equipment", "slot": "weapon",
        "role": "mouse", "rarity": "legendary",
        "desc": "+10 к силе. +25% урона против крыс и грызунов.",
        "effect": {"strength": 10, "rat_damage_bonus": 25},
        "armor": 0, "icon": "⚔️🐀", "price": 40000,
        "lore": "Прославленный меч легендарного Крысолова. Поёт, когда рядом враг.",
        "craftable": True,
        "craft_materials": {"mithril_nugget": 5, "rat_king_eye": 2, "obsidian_scale": 3}
    },
    "king_blade": {
        "name": "Клинок Короля", "type": "equipment", "slot": "weapon",
        "role": "all", "rarity": "legendary",
        "desc": "+12 к силе. +15% к максимальному здоровью.",
        "effect": {"strength": 12, "max_health_percent": 15},
        "armor": 0, "icon": "👑", "price": 50000,
        "lore": "Меч, достойный монарха. Его владелец чувствует прилив королевской мощи.",
        "craftable": True,
        "craft_materials": {"adamantite": 2, "mithril_nugget": 4, "star_silk": 1}
    },
    "divine_sword": {
        "name": "Божественный меч", "type": "equipment", "slot": "weapon",
        "role": "mouse", "rarity": "mythic",
        "desc": "+18 к силе. Святой урон — игнорирует защиту нежити.",
        "effect": {"strength": 18, "holy_damage": True},
        "armor": 0, "icon": "⚡", "price": 150000,
        "lore": "Клинок, благословлённый самим Мышиным Богом. Разит нежить без пощады.",
        "craftable": True,
        "craft_materials": {"spark_creation": 1, "mithril_nugget": 6, "phoenix_ember": 2}
    },
    "first_hero_sword": {
        "name": "Меч Первого героя", "type": "equipment", "slot": "weapon",
        "role": "all", "rarity": "mythic",
        "desc": "+22 к силе. +20% ко всем характеристикам.",
        "effect": {"strength": 22, "all_stats_percent": 20},
        "armor": 0, "icon": "🏆", "price": 200000,
        "lore": "Оружие самого первого искателя приключений. Пропитано духом первооткрывателя.",
        "craftable": True,
        "craft_materials": {"spark_creation": 2, "adamantite": 3, "labyrinth_heart": 1}
    },

    # ===== КИНЖАЛЫ =====
    "bone_knife": {
        "name": "Костяной нож", "type": "equipment", "slot": "weapon",
        "role": "all", "rarity": "common",
        "desc": "+1 к ловкости. +5% шанс двойного удара.",
        "effect": {"agility": 1, "double_hit_chance": 5},
        "armor": 0, "icon": "🦴", "price": 200,
        "lore": "Грубо обтёсанная кость. Лучше, чем ничего.",
        "craftable": True,
        "craft_materials": {"mouse_bone": 5, "rat_incisor": 2, "stone_shard": 1}
    },
    "jagged_dagger": {
        "name": "Зазубренный кинжал", "type": "equipment", "slot": "weapon",
        "role": "all", "rarity": "common",
        "desc": "+2 к ловкости. Кровотечение — 2 урона на 2 хода (шанс 15%).",
        "effect": {"agility": 2, "bleed_chance": 15},
        "armor": 0, "icon": "🗡️", "price": 500,
        "lore": "Лезвие с зубцами. Оставляет рваные раны.",
        "craftable": True,
        "craft_materials": {"iron_gear": 3, "rat_incisor": 4, "copper_scrap": 2}
    },
    "poison_stiletto": {
        "name": "Отравленный стилет", "type": "equipment", "slot": "weapon",
        "role": "rat", "rarity": "rare",
        "desc": "+4 к ловкости. Яд — 3 урона/ход на 3 хода (шанс 20%).",
        "effect": {"agility": 4, "poison_chance": 20},
        "armor": 0, "icon": "🧪", "price": 5000,
        "lore": "Тонкое лезвие, смазанное ядом. Один укол — и враг обречён.",
        "craftable": True,
        "craft_materials": {"steel_shard": 3, "rat_poison": 3, "empty_vial": 2}
    },
    "shadow_dagger": {
        "name": "Теневой клинок", "type": "equipment", "slot": "weapon",
        "role": "rat", "rarity": "epic",
        "desc": "+7 к ловкости. +15% шанс двойного удара.",
        "effect": {"agility": 7, "double_hit_chance": 15},
        "armor": 0, "icon": "🌑", "price": 16000,
        "lore": "Кинжал, скрытый от глаз. Бьёт дважды, прежде чем жертва поймёт.",
        "craftable": True,
        "craft_materials": {"obsidian_scale": 3, "bat_membrane": 2, "spider_silk": 2}
    },
    "assassin_dagger": {
        "name": "Кинжал ассасина", "type": "equipment", "slot": "weapon",
        "role": "rat", "rarity": "epic",
        "desc": "+8 к ловкости. +20% урона при атаке со спины.",
        "effect": {"agility": 8, "backstab_bonus": 20},
        "armor": 0, "icon": "🔪", "price": 20000,
        "lore": "Изогнутый клинок профессионального убийцы. Смертелен в умелых лапах.",
        "craftable": True,
        "craft_materials": {"steel_shard": 5, "bat_fang": 3, "rat_poison": 2}
    },
    "blood_dagger": {
        "name": "Кровавый кинжал", "type": "equipment", "slot": "weapon",
        "role": "rat", "rarity": "legendary",
        "desc": "+10 к ловкости. Вампиризм — восстанавливает 30% урона.",
        "effect": {"agility": 10, "vampirism": 30},
        "armor": 0, "icon": "🩸", "price": 45000,
        "lore": "Красное лезвие, которое пьёт кровь врага, отдавая силу владельцу.",
        "craftable": True,
        "craft_materials": {"mithril_nugget": 4, "bat_fang": 5, "rat_king_eye": 2}
    },
    "death_whisper": {
        "name": "Шёпот смерти", "type": "equipment", "slot": "weapon",
        "role": "rat", "rarity": "legendary",
        "desc": "+12 к ловкости. Бесшумное убийство — жертва не кричит.",
        "effect": {"agility": 12, "silent_kill": True},
        "armor": 0, "icon": "💀", "price": 55000,
        "lore": "Кинжал, который убивает в полной тишине. Никто не услышит предсмертный писк.",
        "craftable": True,
        "craft_materials": {"obsidian_scale": 5, "bat_membrane": 4, "void_essence": 1}
    },
    "demon_fang": {
        "name": "Клык демона", "type": "equipment", "slot": "weapon",
        "role": "rat", "rarity": "mythic",
        "desc": "+16 к ловкости. +25% шанс двойного удара. Вампиризм 50%.",
        "effect": {"agility": 16, "double_hit_chance": 25, "vampirism": 50},
        "armor": 0, "icon": "👿", "price": 160000,
        "lore": "Кинжал, вырванный из пасти демона. Живёт своей жизнью и жаждет крови.",
        "craftable": True,
        "craft_materials": {"spark_creation": 1, "obsidian_scale": 6, "first_rat_skull": 1}
    },
    "soul_reaper": {
        "name": "Душегуб", "type": "equipment", "slot": "weapon",
        "role": "rat", "rarity": "mythic",
        "desc": "+18 к ловкости. Убийство даёт +50% опыта.",
        "effect": {"agility": 18, "kill_xp_bonus": 50},
        "armor": 0, "icon": "⚰️", "price": 180000,
        "lore": "Клинок, пожирающий души. Каждая смерть делает владельца сильнее.",
        "craftable": True,
        "craft_materials": {"spark_creation": 2, "labyrinth_heart": 1, "rat_god_tooth": 1}
    },
    "last_breath": {
        "name": "Последний вздох", "type": "equipment", "slot": "weapon",
        "role": "all", "rarity": "mythic",
        "desc": "+20 к ловкости. При HP < 20%: +50% урона и вампиризм 100%.",
        "effect": {"agility": 20, "desperation_bonus": 50, "desperation_vampirism": 100},
        "armor": 0, "icon": "💨", "price": 200000,
        "lore": "На грани смерти этот кинжал раскрывает истинную мощь.",
        "craftable": True,
        "craft_materials": {"spark_creation": 3, "labyrinth_heart": 2, "void_essence": 2}
    },

    # ===== РАПИРА =====
    "rapier": {
        "name": "Рапира", "type": "equipment", "slot": "weapon",
        "role": "all", "rarity": "mythic",
        "desc": "+25 к силе. Огромный урон! Но 8% шанс пораниться при атаке (3 урона себе).",
        "effect": {"strength": 25, "self_damage_chance": 8, "self_damage": 3},
        "armor": 0, "icon": "⚔️✨", "price": 250000,
        "lore": "Элегантная и смертоносная рапира из звёздного металла.",
        "craftable": True,
        "craft_materials": {"spark_creation": 5, "adamantite": 4, "labyrinth_heart": 2}
    },
}

# ========== УРОН ОРУЖИЯ ==========
WEAPON_DAMAGE = {
    # Мечи
    "rusty_sword": {"min_damage": 2, "max_damage": 5},
    "iron_blade": {"min_damage": 3, "max_damage": 6},
    "steel_sword": {"min_damage": 4, "max_damage": 8},
    "mithril_sword": {"min_damage": 6, "max_damage": 12},
    "shadow_blade_sword": {"min_damage": 5, "max_damage": 11},
    "cheese_blade": {"min_damage": 3, "max_damage": 7},
    "rat_catcher_sword": {"min_damage": 8, "max_damage": 16},
    "king_blade": {"min_damage": 9, "max_damage": 18},
    "divine_sword": {"min_damage": 12, "max_damage": 24},
    "first_hero_sword": {"min_damage": 15, "max_damage": 28},
    # Кинжалы
    "bone_knife": {"min_damage": 1, "max_damage": 3},
    "jagged_dagger": {"min_damage": 2, "max_damage": 4},
    "poison_stiletto": {"min_damage": 3, "max_damage": 6},
    "shadow_dagger": {"min_damage": 4, "max_damage": 8},
    "assassin_dagger": {"min_damage": 5, "max_damage": 9},
    "blood_dagger": {"min_damage": 6, "max_damage": 12},
    "death_whisper": {"min_damage": 8, "max_damage": 14},
    "demon_fang": {"min_damage": 10, "max_damage": 18},
    "soul_reaper": {"min_damage": 12, "max_damage": 20},
    "last_breath": {"min_damage": 14, "max_damage": 22},
    # Рапира
    "rapier": {"min_damage": 18, "max_damage": 35},
    # Старое оружие
    "cheese_sword": {"min_damage": 2, "max_damage": 5},
    "rat_dagger": {"min_damage": 3, "max_damage": 7},
    "butcher_knife": {"min_damage": 8, "max_damage": 16},
    "crossbow": {"min_damage": 5, "max_damage": 10},
}