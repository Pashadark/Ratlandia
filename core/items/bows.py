"""Луки и арбалеты с уроном"""

NEW_BOWS = {
    "wooden_bow": {
        "name": "Деревянный лук", "type": "equipment", "slot": "weapon",
        "role": "all", "rarity": "common",
        "desc": "+2 к ловкости. Дальний бой.",
        "effect": {"agility": 2},
        "armor": 0, "icon": "🏹", "price": 400,
        "lore": "Простой лук из ветки вяза. С чего-то надо начинать.",
        "craftable": True,
        "craft_materials": {"pigeon_feather": 3, "mouse_bone": 2, "spider_web": 2}
    },
    "hunter_bow": {
        "name": "Лук охотника", "type": "equipment", "slot": "weapon",
        "role": "all", "rarity": "common",
        "desc": "+3 к ловкости. +1 к минимальному урону.",
        "effect": {"agility": 3, "min_damage": 1},
        "armor": 0, "icon": "🏹", "price": 700,
        "lore": "Надёжный лук для охоты на мелкую дичь.",
        "craftable": True,
        "craft_materials": {"pigeon_feather": 5, "rat_pelt": 3, "bronze_alloy": 1}
    },
    "composite_bow": {
        "name": "Композитный лук", "type": "equipment", "slot": "weapon",
        "role": "all", "rarity": "rare",
        "desc": "+5 к ловкости. +2 к минимальному урону. +5% к точности.",
        "effect": {"agility": 5, "min_damage": 2, "accuracy": 5},
        "armor": 0, "icon": "🏹", "price": 4000,
        "lore": "Лук из рога и сухожилий. Бьёт дальше и точнее.",
        "craftable": True,
        "craft_materials": {"bronze_alloy": 4, "leather_scrap": 3, "rat_tail_vertebra": 2}
    },
    "elven_bow": {
        "name": "Эльфийский лук", "type": "equipment", "slot": "weapon",
        "role": "mouse", "rarity": "epic",
        "desc": "+8 к ловкости. +3 к минимальному урону. +10% к точности.",
        "effect": {"agility": 8, "min_damage": 3, "accuracy": 10},
        "armor": 0, "icon": "🧝🏹", "price": 18000,
        "lore": "Изящный лук, созданный древними эльфами. Поёт при натяжении тетивы.",
        "craftable": True,
        "craft_materials": {"mithril_nugget": 2, "spider_silk": 4, "fairy_dust": 3}
    },
    "crossbow_repeating": {
        "name": "Многозарядный арбалет", "type": "equipment", "slot": "weapon",
        "role": "mouse", "rarity": "epic",
        "desc": "+6 к ловкости. Атакует дважды за ход (шанс 30%).",
        "effect": {"agility": 6, "double_hit_chance": 30},
        "armor": 0, "icon": "🏹🔄", "price": 22000,
        "lore": "Арбалет с барабанным механизмом. Выпускает две стрелы разом.",
        "craftable": True,
        "craft_materials": {"steel_shard": 5, "bronze_alloy": 4, "iron_gear": 3}
    },
    "longbow_of_truth": {
        "name": "Длинный лук Истины", "type": "equipment", "slot": "weapon",
        "role": "mouse", "rarity": "legendary",
        "desc": "+12 к ловкости. +5 к мин. урону. +15% к точности. Игнорирует уклонение.",
        "effect": {"agility": 12, "min_damage": 5, "accuracy": 15, "ignore_dodge": True},
        "armor": 0, "icon": "🎯", "price": 55000,
        "lore": "Лук, который никогда не промахивается. Стрела всегда находит цель.",
        "craftable": True,
        "craft_materials": {"mithril_nugget": 5, "moon_silk": 3, "rat_king_eye": 2}
    },
    "storm_bow": {
        "name": "Лук Бури", "type": "equipment", "slot": "weapon",
        "role": "mouse", "rarity": "legendary",
        "desc": "+15 к ловкости. Молния — +8 урона (шанс 15%).",
        "effect": {"agility": 15, "lightning_damage": 8},
        "armor": 0, "icon": "⚡🏹", "price": 60000,
        "lore": "Лук, вырезанный из дерева, в которое ударила молния. Искрит в руках.",
        "craftable": True,
        "craft_materials": {"mithril_nugget": 4, "storm_spark": 2, "phoenix_ember": 2}
    },
    "phoenix_bow": {
        "name": "Лук Феникса", "type": "equipment", "slot": "weapon",
        "role": "mouse", "rarity": "mythic",
        "desc": "+18 к ловкости. Огненные стрелы — +12 урона огнём (шанс 20%).",
        "effect": {"agility": 18, "fire_damage": 12},
        "armor": 0, "icon": "🔥🏹", "price": 180000,
        "lore": "Лук, пылающий вечным огнём. Стрелы загораются в полёте.",
        "craftable": True,
        "craft_materials": {"spark_creation": 2, "phoenix_ember": 4, "star_silk": 2}
    },
    "void_bow": {
        "name": "Лук Бездны", "type": "equipment", "slot": "weapon",
        "role": "rat", "rarity": "mythic",
        "desc": "+16 к ловкости. Теневые стрелы — игнорируют броню.",
        "effect": {"agility": 16, "ignore_defense": True},
        "armor": 0, "icon": "🌑🏹", "price": 190000,
        "lore": "Лук из самой темноты. Его стрелы проходят сквозь любую защиту.",
        "craftable": True,
        "craft_materials": {"void_essence": 3, "obsidian_scale": 5, "spark_creation": 2}
    },
    "celestial_longbow": {
        "name": "Небесный длинный лук", "type": "equipment", "slot": "weapon",
        "role": "mouse", "rarity": "mythic",
        "desc": "+22 к ловкости. +8 к мин. урону. +25% к точности. Звёздный дождь — атакует 3 раза (шанс 10%).",
        "effect": {"agility": 22, "min_damage": 8, "accuracy": 25, "triple_hit_chance": 10},
        "armor": 0, "icon": "🌟🏹", "price": 250000,
        "lore": "Лук, сотканный из звёздного света. Выпускает целый град стрел.",
        "craftable": True,
        "craft_materials": {"spark_creation": 5, "star_silk": 4, "labyrinth_heart": 2}
    },
}

# ========== УРОН ЛУКОВ ==========
BOW_DAMAGE = {
    "wooden_bow": {"min_damage": 2, "max_damage": 4},
    "hunter_bow": {"min_damage": 3, "max_damage": 5},
    "composite_bow": {"min_damage": 4, "max_damage": 7},
    "elven_bow": {"min_damage": 5, "max_damage": 10},
    "crossbow_repeating": {"min_damage": 4, "max_damage": 8},
    "longbow_of_truth": {"min_damage": 7, "max_damage": 14},
    "storm_bow": {"min_damage": 8, "max_damage": 16},
    "phoenix_bow": {"min_damage": 10, "max_damage": 20},
    "void_bow": {"min_damage": 9, "max_damage": 18},
    "celestial_longbow": {"min_damage": 14, "max_damage": 26},
}