"""Рецепты крафта — оружие, броня, расходники, луки, классовая броня"""

RECIPES = {
    # ===== СТАРЫЕ РЕЦЕПТЫ =====
    "recipe_cheese_sword": {
        "name": "Рецепт: Сырный меч", "type": "recipe", "rarity": "common",
        "desc": "Открывает крафт Сырного меча",
        "icon": "📜", "price": 500,
        "result_item": "cheese_sword",
        "materials": {"cheese_crust": 3, "rat_incisor": 2, "iron_gear": 1},
        "lore": "Потрёпанный пергамент с рецептом."
    },
    "recipe_leather_vest": {
        "name": "Рецепт: Кожаный жилет", "type": "recipe", "rarity": "common",
        "desc": "Открывает крафт Кожаного жилета",
        "icon": "📜", "price": 500,
        "result_item": "leather_vest",
        "materials": {"rat_pelt": 5, "linen_scrap": 2, "mouse_bone": 1},
        "lore": "Простой, но надёжный рецепт брони."
    },
    "recipe_gambeson": {
        "name": "Рецепт: Гамбезон", "type": "recipe", "rarity": "common",
        "desc": "Открывает крафт Гамбезона",
        "icon": "📜", "price": 500,
        "result_item": "gambeson",
        "materials": {"linen_scrap": 4, "rat_pelt": 3, "wool_clump": 2},
        "lore": "Стёганая броня для настоящих бойцов."
    },
    "recipe_rat_dagger": {
        "name": "Рецепт: Крысиный кинжал", "type": "recipe", "rarity": "rare",
        "desc": "Открывает крафт Крысиного кинжала",
        "icon": "📜", "price": 1500,
        "result_item": "rat_dagger",
        "materials": {"steel_shard": 2, "rat_incisor": 4, "rat_poison": 1},
        "lore": "Клинок, достойный настоящей Крысы."
    },
    "recipe_viking_helmet": {
        "name": "Рецепт: Шлем викинга", "type": "recipe", "rarity": "rare",
        "desc": "Открывает крафт Шлема викинга",
        "icon": "📜", "price": 1500,
        "result_item": "viking_helmet",
        "materials": {"iron_gear": 4, "rat_pelt": 2, "bronze_alloy": 1},
        "lore": "Грубый железный шлем северных воинов."
    },
    "recipe_chainmail": {
        "name": "Рецепт: Кольчуга", "type": "recipe", "rarity": "rare",
        "desc": "Открывает крафт Кольчуги",
        "icon": "📜", "price": 1500,
        "result_item": "chainmail",
        "materials": {"iron_gear": 6, "bronze_alloy": 2, "leather_scrap": 2},
        "lore": "Стальная рубаха, проверенная временем."
    },
    "recipe_crossbow": {
        "name": "Рецепт: Арбалет", "type": "recipe", "rarity": "epic",
        "desc": "Открывает крафт Арбалета",
        "icon": "📜", "price": 5000,
        "result_item": "crossbow",
        "materials": {"bronze_alloy": 3, "bat_membrane": 2, "iron_gear": 2},
        "lore": "Оружие, которое не требует силы — только точности."
    },
    "recipe_butcher_knife": {
        "name": "Рецепт: Нож мясника", "type": "recipe", "rarity": "legendary",
        "desc": "Открывает крафт Ножа мясника",
        "icon": "📜", "price": 15000,
        "result_item": "butcher_knife",
        "materials": {"steel_shard": 3, "rat_king_eye": 1, "obsidian_scale": 2, "mithril_nugget": 1},
        "lore": "Легендарный нож, пропитанный кровью сотен жертв."
    },
    "recipe_invisibility_cloak": {
        "name": "Рецепт: Плащ-невидимка", "type": "recipe", "rarity": "mythic",
        "desc": "Открывает крафт Плаща-невидимки",
        "icon": "📜", "price": 50000,
        "result_item": "invisibility_cloak",
        "materials": {"moon_silk": 3, "void_essence": 1, "spider_silk": 2, "bat_membrane": 1},
        "lore": "Древний секрет, позволяющий ходить среди теней незамеченным."
    },
    "recipe_crown_of_rat_king": {
        "name": "Рецепт: Корона Крысиного короля", "type": "recipe", "rarity": "mythic",
        "desc": "Открывает крафт Короны Крысиного короля",
        "icon": "📜", "price": 50000,
        "result_item": "crown_of_rat_king",
        "materials": {"rat_god_tooth": 1, "adamantite": 1, "first_rat_skull": 1},
        "lore": "Только истинный правитель достоин носить эту корону."
    },
    "recipe_crown_of_mouse_king": {
        "name": "Рецепт: Корона Мышиного короля", "type": "recipe", "rarity": "mythic",
        "desc": "Открывает крафт Короны Мышиного короля",
        "icon": "📜", "price": 50000,
        "result_item": "crown_of_mouse_king",
        "materials": {"star_silk": 1, "mithril_nugget": 3, "phoenix_ember": 1},
        "lore": "Символ надежды для всех Мышей."
    },
    "recipe_poison_cheese": {
        "name": "Рецепт: Ядовитый сыр", "type": "recipe", "rarity": "common",
        "desc": "Открывает крафт Ядовитого сыра",
        "icon": "📜", "price": 500,
        "result_item": "poison_cheese",
        "materials": {"cheese_crust": 2, "rat_poison": 2, "basement_mushroom": 1},
        "lore": "Простой рецепт для незаметного убийства."
    },
    "recipe_smoke_bomb": {
        "name": "Рецепт: Дымовая бомба", "type": "recipe", "rarity": "rare",
        "desc": "Открывает крафт Дымовой бомбы",
        "icon": "📜", "price": 1500,
        "result_item": "smoke_bomb",
        "materials": {"wall_soot": 3, "cheese_crust": 1, "empty_vial": 1},
        "lore": "Идеально для тактического отступления."
    },

    # ===== РЕЦЕПТЫ НОВОГО ОРУЖИЯ =====
    "recipe_rusty_sword": {
        "name": "Рецепт: Ржавый меч", "type": "recipe", "rarity": "common",
        "desc": "Открывает крафт Ржавого меча",
        "icon": "📜", "price": 300,
        "result_item": "rusty_sword",
        "materials": {"iron_gear": 3, "copper_scrap": 2, "stone_shard": 2},
        "lore": "Базовый рецепт для начинающих кузнецов."
    },
    "recipe_iron_blade": {
        "name": "Рецепт: Железный клинок", "type": "recipe", "rarity": "common",
        "desc": "Открывает крафт Железного клинка",
        "icon": "📜", "price": 500,
        "result_item": "iron_blade",
        "materials": {"iron_gear": 5, "bronze_alloy": 2, "leather_scrap": 1},
        "lore": "Проверенный рецепт из поколения в поколение."
    },
    "recipe_steel_sword": {
        "name": "Рецепт: Стальной меч", "type": "recipe", "rarity": "rare",
        "desc": "Открывает крафт Стального меча",
        "icon": "📜", "price": 2000,
        "result_item": "steel_sword",
        "materials": {"steel_shard": 4, "bronze_alloy": 3, "iron_gear": 2},
        "lore": "Требует умелых лап и хорошей печи."
    },
    "recipe_rapier": {
        "name": "Рецепт: Рапира", "type": "recipe", "rarity": "mythic",
        "desc": "Открывает крафт Рапиры",
        "icon": "📜", "price": 100000,
        "result_item": "rapier",
        "materials": {"spark_creation": 5, "adamantite": 4, "labyrinth_heart": 2},
        "lore": "Легендарный рецепт, известный лишь избранным мастерам."
    },
    "recipe_poison_stiletto": {
        "name": "Рецепт: Отравленный стилет", "type": "recipe", "rarity": "rare",
        "desc": "Открывает крафт Отравленного стилета",
        "icon": "📜", "price": 3000,
        "result_item": "poison_stiletto",
        "materials": {"steel_shard": 3, "rat_poison": 3, "empty_vial": 2},
        "lore": "Оружие для тех, кто предпочитает тихую смерть."
    },
    "recipe_blood_dagger": {
        "name": "Рецепт: Кровавый кинжал", "type": "recipe", "rarity": "legendary",
        "desc": "Открывает крафт Кровавого кинжала",
        "icon": "📜", "price": 25000,
        "result_item": "blood_dagger",
        "materials": {"mithril_nugget": 4, "bat_fang": 5, "rat_king_eye": 2},
        "lore": "Кровь врагов станет твоей силой."
    },
    "recipe_rat_catcher_sword": {
        "name": "Рецепт: Меч Крысолова", "type": "recipe", "rarity": "legendary",
        "desc": "Открывает крафт Меча Крысолова",
        "icon": "📜", "price": 30000,
        "result_item": "rat_catcher_sword",
        "materials": {"mithril_nugget": 5, "rat_king_eye": 2, "obsidian_scale": 3},
        "lore": "Создан для истребления грызунов всех мастей."
    },
    "recipe_first_hero_sword": {
        "name": "Рецепт: Меч Первого героя", "type": "recipe", "rarity": "mythic",
        "desc": "Открывает крафт Меча Первого героя",
        "icon": "📜", "price": 100000,
        "result_item": "first_hero_sword",
        "materials": {"spark_creation": 2, "adamantite": 3, "labyrinth_heart": 1},
        "lore": "Рецепт, написанный рукой самого Первого героя."
    },

    # ===== РЕЦЕПТЫ ЛУКОВ =====
    "recipe_wooden_bow": {
        "name": "Рецепт: Деревянный лук", "type": "recipe", "rarity": "common",
        "desc": "Открывает крафт Деревянного лука",
        "icon": "📜", "price": 300,
        "result_item": "wooden_bow",
        "materials": {"pigeon_feather": 3, "mouse_bone": 2, "spider_web": 2},
        "lore": "Базовый рецепт для начинающих лучников."
    },
    "recipe_elven_bow": {
        "name": "Рецепт: Эльфийский лук", "type": "recipe", "rarity": "epic",
        "desc": "Открывает крафт Эльфийского лука",
        "icon": "📜", "price": 12000,
        "result_item": "elven_bow",
        "materials": {"mithril_nugget": 2, "spider_silk": 4, "fairy_dust": 3},
        "lore": "Рецепт древних эльфов, сохранённый в веках."
    },
    "recipe_longbow_of_truth": {
        "name": "Рецепт: Длинный лук Истины", "type": "recipe", "rarity": "legendary",
        "desc": "Открывает крафт Длинного лука Истины",
        "icon": "📜", "price": 35000,
        "result_item": "longbow_of_truth",
        "materials": {"mithril_nugget": 5, "moon_silk": 3, "rat_king_eye": 2},
        "lore": "Лук, который видит ложь и поражает её."
    },
    "recipe_celestial_longbow": {
        "name": "Рецепт: Небесный длинный лук", "type": "recipe", "rarity": "mythic",
        "desc": "Открывает крафт Небесного длинного лука",
        "icon": "📜", "price": 120000,
        "result_item": "celestial_longbow",
        "materials": {"spark_creation": 5, "star_silk": 4, "labyrinth_heart": 2},
        "lore": "Рецепт, начертанный на небесах звёздами."
    },

    # ===== РЕЦЕПТЫ КЛАССОВОЙ БРОНИ =====
    "recipe_iron_plate": {
        "name": "Рецепт: Железный нагрудник", "type": "recipe", "rarity": "common",
        "desc": "Открывает крафт Железного нагрудника",
        "icon": "📜", "price": 500,
        "result_item": "iron_plate",
        "materials": {"iron_gear": 8, "bronze_alloy": 3, "leather_scrap": 2},
        "lore": "Рецепт для тех, кто хочет стать непробиваемым."
    },
    "recipe_apprentice_robe": {
        "name": "Рецепт: Роба ученика", "type": "recipe", "rarity": "common",
        "desc": "Открывает крафт Робы ученика",
        "icon": "📜", "price": 400,
        "result_item": "apprentice_robe",
        "materials": {"linen_scrap": 5, "wool_clump": 3, "candle_stub": 2},
        "lore": "Первый шаг на пути магического искусства."
    },
    "recipe_thief_vest": {
        "name": "Рецепт: Жилет вора", "type": "recipe", "rarity": "common",
        "desc": "Открывает крафт Жилета вора",
        "icon": "📜", "price": 400,
        "result_item": "thief_vest",
        "materials": {"leather_scrap": 5, "linen_scrap": 3, "rat_pelt": 2},
        "lore": "Для тех, кто предпочитает действовать из тени."
    },
    "recipe_berserker_harness": {
        "name": "Рецепт: Упряжь берсерка", "type": "recipe", "rarity": "rare",
        "desc": "Открывает крафт Упряжи берсерка",
        "icon": "📜", "price": 2500,
        "result_item": "berserker_harness",
        "materials": {"steel_shard": 4, "rat_pelt": 5, "bronze_alloy": 2},
        "lore": "Для тех, кто не боится боли."
    },
    "recipe_sorcerer_robe": {
        "name": "Рецепт: Мантия чародея", "type": "recipe", "rarity": "rare",
        "desc": "Открывает крафт Мантии чародея",
        "icon": "📜", "price": 3000,
        "result_item": "sorcerer_robe",
        "materials": {"spider_silk": 4, "fairy_dust": 2, "cloudy_crystal": 2},
        "lore": "Мантия, усиливающая потоки магии."
    },
    "recipe_titan_armor": {
        "name": "Рецепт: Броня титана", "type": "recipe", "rarity": "legendary",
        "desc": "Открывает крафт Брони титана",
        "icon": "📜", "price": 35000,
        "result_item": "titan_armor",
        "materials": {"adamantite": 3, "mithril_nugget": 5, "magnetic_stone": 2},
        "lore": "Броня, достойная величайших героев."
    },
    "recipe_nightstalker_garb": {
        "name": "Рецепт: Одеяние Ночного Охотника", "type": "recipe", "rarity": "mythic",
        "desc": "Открывает крафт Одеяния Ночного Охотника",
        "icon": "📜", "price": 100000,
        "result_item": "nightstalker_garb",
        "materials": {"spark_creation": 4, "void_essence": 3, "star_silk": 3},
        "lore": "Легендарный рецепт, известный лишь Гильдии Теней."
    },
}

# Собираем всё вместе для совместимости
ALL_RECIPES = {**RECIPES}