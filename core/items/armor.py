"""Классовая броня — танк, атакующий, маг, разбойник"""

CLASS_ARMORS = {
    # ===== БРОНЯ ТАНКА (высокая защита, +HP, -ловкость) =====
    "iron_plate": {
        "name": "Железный нагрудник", "type": "equipment", "slot": "armor",
        "role": "all", "rarity": "common",
        "desc": "+3 к силе. +25 HP. -1 к ловкости. Тяжёлая броня.",
        "effect": {"strength": 3, "max_health": 25, "agility": -1},
        "armor": 20, "icon": "🛡️", "price": 800,
        "lore": "Толстая железная пластина. Неповоротливо, но надёжно.",
        "craftable": True,
        "craft_materials": {"iron_gear": 8, "bronze_alloy": 3, "leather_scrap": 2}
    },
    "steel_cuirass": {
        "name": "Стальная кираса", "type": "equipment", "slot": "armor",
        "role": "all", "rarity": "rare",
        "desc": "+5 к силе. +40 HP. -2 к ловкости.",
        "effect": {"strength": 5, "max_health": 40, "agility": -2},
        "armor": 30, "icon": "🛡️", "price": 5000,
        "lore": "Цельный стальной панцирь. Выдерживает прямой удар меча.",
        "craftable": True,
        "craft_materials": {"steel_shard": 6, "iron_gear": 4, "bronze_alloy": 3}
    },
    "mithril_plate": {
        "name": "Мифриловая броня", "type": "equipment", "slot": "armor",
        "role": "all", "rarity": "epic",
        "desc": "+8 к силе. +60 HP. Нет штрафа к ловкости.",
        "effect": {"strength": 8, "max_health": 60},
        "armor": 40, "icon": "✨🛡️", "price": 20000,
        "lore": "Лёгкая как перо, прочная как сталь. Мечта любого танка.",
        "craftable": True,
        "craft_materials": {"mithril_nugget": 5, "steel_shard": 4, "fairy_dust": 2}
    },
    "titan_armor": {
        "name": "Броня титана", "type": "equipment", "slot": "armor",
        "role": "all", "rarity": "legendary",
        "desc": "+12 к силе. +100 HP. Входящий урон -3.",
        "effect": {"strength": 12, "max_health": 100, "damage_reduction": 3},
        "armor": 60, "icon": "🏰", "price": 60000,
        "lore": "Броня, выкованная из сердца горы. Почти непробиваема.",
        "craftable": True,
        "craft_materials": {"adamantite": 3, "mithril_nugget": 5, "magnetic_stone": 2}
    },
    "aegis_divine": {
        "name": "Эгида божественная", "type": "equipment", "slot": "armor",
        "role": "all", "rarity": "mythic",
        "desc": "+20 к силе. +200 HP. Входящий урон -5. Иммунитет к оглушению.",
        "effect": {"strength": 20, "max_health": 200, "damage_reduction": 5, "stun_immune": True},
        "armor": 100, "icon": "⚡🛡️", "price": 200000,
        "lore": "Щит самого Бога-Защитника. Ничто не пробьёт эту защиту.",
        "craftable": True,
        "craft_materials": {"spark_creation": 3, "adamantite": 5, "labyrinth_heart": 2}
    },

    # ===== БРОНЯ АТАКУЮЩЕГО (сила, урон, средняя защита) =====
    "leather_armor_reinforced": {
        "name": "Усиленная кожаная броня", "type": "equipment", "slot": "armor",
        "role": "all", "rarity": "common",
        "desc": "+2 к силе. +1 к минимальному урону. +10 HP.",
        "effect": {"strength": 2, "min_damage": 1, "max_health": 10},
        "armor": 12, "icon": "🦺", "price": 600,
        "lore": "Кожа, усиленная железными вставками. Для тех, кто предпочитает атаку.",
        "craftable": True,
        "craft_materials": {"rat_pelt": 6, "iron_gear": 3, "leather_scrap": 3}
    },
    "berserker_harness": {
        "name": "Упряжь берсерка", "type": "equipment", "slot": "armor",
        "role": "all", "rarity": "rare",
        "desc": "+4 к силе. +2 к урону. -5 HP.",
        "effect": {"strength": 4, "damage": 2, "max_health": -5},
        "armor": 8, "icon": "😤", "price": 4000,
        "lore": "Минимум защиты, максимум ярости. Для тех, кто не боится умереть.",
        "craftable": True,
        "craft_materials": {"steel_shard": 4, "rat_pelt": 5, "bronze_alloy": 2}
    },
    "war_chainmail": {
        "name": "Боевая кольчуга", "type": "equipment", "slot": "armor",
        "role": "all", "rarity": "epic",
        "desc": "+7 к силе. +3 к урону. +25 HP.",
        "effect": {"strength": 7, "damage": 3, "max_health": 25},
        "armor": 25, "icon": "⛓️", "price": 18000,
        "lore": "Кольчуга, закалённая в драконьем пламени. Для настоящих воинов.",
        "craftable": True,
        "craft_materials": {"steel_shard": 6, "mithril_nugget": 2, "iron_gear": 4}
    },
    "dragon_leather": {
        "name": "Драконья шкура", "type": "equipment", "slot": "armor",
        "role": "all", "rarity": "legendary",
        "desc": "+10 к силе. +5 к урону. +40 HP. +10% шанс крита.",
        "effect": {"strength": 10, "damage": 5, "max_health": 40, "crit_chance": 10},
        "armor": 35, "icon": "🐉", "price": 65000,
        "lore": "Шкура легендарного ящера. Пропитана огнём и яростью.",
        "craftable": True,
        "craft_materials": {"obsidian_scale": 5, "steel_shard": 5, "phoenix_ember": 2}
    },
    "ragnarok_armor": {
        "name": "Броня Рагнарёка", "type": "equipment", "slot": "armor",
        "role": "all", "rarity": "mythic",
        "desc": "+18 к силе. +8 к урону. +60 HP. +20% шанс крита.",
        "effect": {"strength": 18, "damage": 8, "max_health": 60, "crit_chance": 20},
        "armor": 55, "icon": "🌋", "price": 220000,
        "lore": "Броня конца времён. Говорят, её носил сам бог войны.",
        "craftable": True,
        "craft_materials": {"spark_creation": 4, "adamantite": 4, "phoenix_ember": 3}
    },

    # ===== БРОНЯ МАГА (интеллект, реген маны, сопротивление магии) =====
    "apprentice_robe": {
        "name": "Роба ученика", "type": "equipment", "slot": "armor",
        "role": "all", "rarity": "common",
        "desc": "+2 к интеллекту. +5% к магическому урону.",
        "effect": {"intelligence": 2, "magic_damage": 5},
        "armor": 4, "icon": "👘", "price": 500,
        "lore": "Простая тканевая роба. Пахнет старыми книгами и свечным воском.",
        "craftable": True,
        "craft_materials": {"linen_scrap": 5, "wool_clump": 3, "candle_stub": 2}
    },
    "sorcerer_robe": {
        "name": "Мантия чародея", "type": "equipment", "slot": "armor",
        "role": "all", "rarity": "rare",
        "desc": "+4 к интеллекту. +10% к магическому урону. +1 реген маны.",
        "effect": {"intelligence": 4, "magic_damage": 10, "mana_regen": 1},
        "armor": 8, "icon": "🧙", "price": 4500,
        "lore": "Мантия, расшитая магическими рунами. Искрит при ходьбе.",
        "craftable": True,
        "craft_materials": {"spider_silk": 4, "fairy_dust": 2, "cloudy_crystal": 2}
    },
    "archmage_robe": {
        "name": "Одеяние архимага", "type": "equipment", "slot": "armor",
        "role": "all", "rarity": "epic",
        "desc": "+7 к интеллекту. +15% к магическому урону. +2 реген маны. +10 HP.",
        "effect": {"intelligence": 7, "magic_damage": 15, "mana_regen": 2, "max_health": 10},
        "armor": 12, "icon": "🔮", "price": 22000,
        "lore": "Одеяние, пропитанное чистой магией. Владелец чувствует потоки силы.",
        "craftable": True,
        "craft_materials": {"moon_silk": 3, "fairy_dust": 4, "mage_blood": 1}
    },
    "void_weave_robe": {
        "name": "Мантия Пустоты", "type": "equipment", "slot": "armor",
        "role": "all", "rarity": "legendary",
        "desc": "+12 к интеллекту. +25% к магическому урону. +3 реген маны. Иммунитет к сайленсу.",
        "effect": {"intelligence": 12, "magic_damage": 25, "mana_regen": 3, "silence_immune": True},
        "armor": 16, "icon": "🌌", "price": 70000,
        "lore": "Соткана из самой ткани мироздания. Между нитями видна бесконечность.",
        "craftable": True,
        "craft_materials": {"void_essence": 2, "star_silk": 3, "ancient_scrap": 2}
    },
    "omniscient_shroud": {
        "name": "Покров Всезнания", "type": "equipment", "slot": "armor",
        "role": "all", "rarity": "mythic",
        "desc": "+20 к интеллекту. +40% к магическому урону. +5 реген маны. Все заклинания усилены.",
        "effect": {"intelligence": 20, "magic_damage": 40, "mana_regen": 5, "all_spells_boost": True},
        "armor": 22, "icon": "🌟", "price": 250000,
        "lore": "Одеяние, дарующее знание всех тайн. Владелец видит прошлое и будущее.",
        "craftable": True,
        "craft_materials": {"spark_creation": 5, "labyrinth_heart": 3, "void_essence": 3}
    },

    # ===== БРОНЯ РАЗБОЙНИКА (ловкость, уклонение, скрытность) =====
    "thief_vest": {
        "name": "Жилет вора", "type": "equipment", "slot": "armor",
        "role": "all", "rarity": "common",
        "desc": "+2 к ловкости. +5% к уклонению. +5 HP.",
        "effect": {"agility": 2, "dodge": 5, "max_health": 5},
        "armor": 6, "icon": "🕵️", "price": 500,
        "lore": "Лёгкий жилет с множеством карманов для краденого.",
        "craftable": True,
        "craft_materials": {"leather_scrap": 5, "linen_scrap": 3, "rat_pelt": 2}
    },
    "shadow_leather": {
        "name": "Теневая кожа", "type": "equipment", "slot": "armor",
        "role": "rat", "rarity": "rare",
        "desc": "+4 к ловкости. +10% к уклонению. +10 HP. Бесшумное движение.",
        "effect": {"agility": 4, "dodge": 10, "max_health": 10, "silent_move": True},
        "armor": 10, "icon": "🌑", "price": 4500,
        "lore": "Кожаный доспех, выкрашенный в цвет ночи. Шагов не слышно.",
        "craftable": True,
        "craft_materials": {"bat_membrane": 3, "spider_silk": 3, "obsidian_scale": 2}
    },
    "ninja_gi": {
        "name": "Одеяние ниндзя", "type": "equipment", "slot": "armor",
        "role": "rat", "rarity": "epic",
        "desc": "+7 к ловкости. +15% к уклонению. +15 HP. +10% шанс двойного удара.",
        "effect": {"agility": 7, "dodge": 15, "max_health": 15, "double_hit_chance": 10},
        "armor": 14, "icon": "🥷", "price": 20000,
        "lore": "Чёрное одеяние, позволяющее двигаться быстрее ветра.",
        "craftable": True,
        "craft_materials": {"spider_silk": 5, "bat_membrane": 4, "snake_skin": 3}
    },
    "phantom_mantle": {
        "name": "Плащ фантома", "type": "equipment", "slot": "armor",
        "role": "rat", "rarity": "legendary",
        "desc": "+12 к ловкости. +20% к уклонению. +25 HP. Невидимость на 1 ход при HP < 30%.",
        "effect": {"agility": 12, "dodge": 20, "max_health": 25, "emergency_invis": True},
        "armor": 18, "icon": "👻", "price": 65000,
        "lore": "Плащ, сотканный из душ умерших воров. Исчезает в момент опасности.",
        "craftable": True,
        "craft_materials": {"moon_silk": 4, "bat_membrane": 5, "void_essence": 1}
    },
    "nightstalker_garb": {
        "name": "Одеяние Ночного Охотника", "type": "equipment", "slot": "armor",
        "role": "rat", "rarity": "mythic",
        "desc": "+20 к ловкости. +30% к уклонению. +40 HP. Все удары из невидимости — критические.",
        "effect": {"agility": 20, "dodge": 30, "max_health": 40, "stealth_crit": True},
        "armor": 25, "icon": "🦇", "price": 230000,
        "lore": "Одеяние легендарного убийцы. Никто не видел его владельца живым.",
        "craftable": True,
        "craft_materials": {"spark_creation": 4, "void_essence": 3, "star_silk": 3}
    },
}