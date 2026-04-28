"""Экипировка — шлемы, оружие, броня, аксессуары"""

EQUIPMENT = {
    # ==================== ШЛЕМЫ (HEAD) ====================
    "detective_hat": {
        "name": "Шляпа детектива", "type": "equipment", "slot": "head",
        "role": "all", "rarity": "rare",
        "desc": "+2 к интеллекту. Видишь кто за кого голосовал.",
        "effect": {"intelligence": 2, "see_votes": True},
        "armor": 3, "icon": "🎩", "price": 2000,
        "lore": "Поношенная фетровая шляпа, пропитанная табачным дымом."
    },
    "shadow_hood": {
        "name": "Капюшон тени", "type": "equipment", "slot": "head",
        "role": "rat", "rarity": "epic",
        "desc": "+3 к ловкости. Твои убийства не раскрывают роль жертвы.",
        "effect": {"agility": 3, "hidden_kill_role": True},
        "armor": 5, "icon": "🌑", "price": 8000,
        "lore": "Сотканный из теней Нижних Туннелей."
    },
    "crown_of_rat_king": {
        "name": "Корона Крысиного короля", "type": "equipment", "slot": "head",
        "role": "rat", "rarity": "legendary",
        "desc": "+5 к силе. Все Мыши теряют 1 голос на голосовании.",
        "effect": {"strength": 5, "mice_vote_penalty": 1},
        "armor": 8, "icon": "👑", "price": 25000,
        "lore": "Тяжёлая корона из тёмного железа, усыпанная осколками костей."
    },
    "crown_of_mouse_king": {
        "name": "Корона Мышиного короля", "type": "equipment", "slot": "head",
        "role": "mouse", "rarity": "legendary",
        "desc": "+3 ко всем характеристикам. Твой голос считается за 2.",
        "effect": {"strength": 3, "agility": 3, "intelligence": 3, "double_vote": True},
        "armor": 8, "icon": "👑", "price": 25000,
        "lore": "Изящная золотая корона, украшенная крошечными сырными самоцветами."
    },
    "chef_hat": {
        "name": "Колпак шефа", "type": "equipment", "slot": "head",
        "role": "all", "rarity": "common",
        "desc": "+1 к интеллекту. +5% шанс найти предмет в туннелях.",
        "effect": {"intelligence": 1, "find_chance": 5},
        "armor": 1, "icon": "🧑‍🍳", "price": 500,
        "lore": "Высокий белый колпак, слегка испачканный мукой."
    },
    "top_hat": {
        "name": "Цилиндр джентльмена", "type": "equipment", "slot": "head",
        "role": "all", "rarity": "rare",
        "desc": "+2 ко всем характеристикам.",
        "effect": {"strength": 2, "agility": 2, "intelligence": 2},
        "armor": 3, "icon": "🎩", "price": 2000,
        "lore": "Элегантный чёрный цилиндр, видавший лучшие времена."
    },
    "jester_cap": {
        "name": "Колпак шута", "type": "equipment", "slot": "head",
        "role": "all", "rarity": "epic",
        "desc": "+2 к ловкости. Случайный эффект каждую игру.",
        "effect": {"agility": 2, "random_effect": True},
        "armor": 4, "icon": "🃏", "price": 8000,
        "lore": "Разноцветный колпак с бубенчиками."
    },
    "viking_helmet": {
        "name": "Шлем викинга", "type": "equipment", "slot": "head",
        "role": "all", "rarity": "rare",
        "desc": "+3 к силе. +10 к максимальному здоровью в туннелях.",
        "effect": {"strength": 3, "max_health": 10},
        "armor": 6, "icon": "🪓", "price": 2000,
        "craftable": True,
        "craft_materials": {"iron_gear": 4, "rat_pelt": 2, "bronze_alloy": 1},
        "lore": "Грубый железный шлем, побывавший в сотне стычек."
    },
    "ninja_mask": {
        "name": "Маска ниндзя", "type": "equipment", "slot": "head",
        "role": "rat", "rarity": "rare",
        "desc": "+3 к ловкости. Твой голос на голосовании скрыт.",
        "effect": {"agility": 3, "hidden_vote": True},
        "armor": 2, "icon": "🥷", "price": 2000,
        "lore": "Чёрная маска, оставляющая лишь щёлочку для глаз."
    },
    "wizard_hat": {
        "name": "Шляпа волшебника", "type": "equipment", "slot": "head",
        "role": "all", "rarity": "legendary",
        "desc": "+5 к интеллекту. +20% опыт за игру.",
        "effect": {"intelligence": 5, "xp_boost": 20},
        "armor": 4, "icon": "🧙", "price": 25000,
        "lore": "Высокая остроконечная шляпа, расшитая серебряными звёздами."
    },
    "pirate_hat": {
        "name": "Пиратская треуголка", "type": "equipment", "slot": "head",
        "role": "rat", "rarity": "epic",
        "desc": "+3 к силе. +1 убийство за игру (если Крыса).",
        "effect": {"strength": 3, "extra_kill": 1},
        "armor": 4, "icon": "🏴‍☠️", "price": 8000,
        "lore": "Потрёпанная треуголка с выцветшим черепом."
    },
    "flower_crown": {
        "name": "Венок из цветов", "type": "equipment", "slot": "head",
        "role": "all", "rarity": "common",
        "desc": "+1 к ловкости. +1 HP каждый ход в туннелях.",
        "effect": {"agility": 1, "regen": 1},
        "armor": 0, "icon": "🌸", "price": 500,
        "lore": "Нежный венок из полевых цветов."
    },
    "cowboy_hat": {
        "name": "Ковбойская шляпа", "type": "equipment", "slot": "head",
        "role": "mouse", "rarity": "rare",
        "desc": "+2 к ловкости. Твой голос решающий при ничьей.",
        "effect": {"agility": 2, "tie_breaker": True},
        "armor": 3, "icon": "🤠", "price": 2000,
        "lore": "Широкополая кожаная шляпа."
    },
    "santa_hat": {
        "name": "Шапка Санты", "type": "equipment", "slot": "head",
        "role": "all", "rarity": "legendary",
        "desc": "+2 ко всем. Дарит случайный предмет после победы.",
        "effect": {"strength": 2, "agility": 2, "intelligence": 2, "gift_item": True},
        "armor": 5, "icon": "🎅", "price": 25000,
        "lore": "Пушистая красная шапка с белым помпоном."
    },
    "crown_of_thorns": {
        "name": "Терновый венец", "type": "equipment", "slot": "head",
        "role": "all", "rarity": "mythic",
        "desc": "+5 к силе. -20% опыта, но +50% шанс легендарного предмета.",
        "effect": {"strength": 5, "xp_penalty": 20, "legendary_chance": 50},
        "armor": 6, "icon": "👑", "price": 100000,
        "lore": "Венец из колючих ветвей."
    },
    "beer_hat": {
        "name": "Шляпа с пивом", "type": "equipment", "slot": "head",
        "role": "all", "rarity": "common",
        "desc": "+1 к силе. +1 XP за каждое сообщение в чате.",
        "effect": {"strength": 1, "chat_xp": 1},
        "armor": 1, "icon": "🍺", "price": 500,
        "lore": "Дурацкая шляпа с двумя подстаканниками и трубочками."
    },
    "cheese_wedge_hat": {
        "name": "Шляпа-сырный треугольник", "type": "equipment", "slot": "head",
        "role": "all", "rarity": "common",
        "desc": "+1 ко всем характеристикам. +15 XP за игру.",
        "effect": {"strength": 1, "agility": 1, "intelligence": 1, "bonus_xp": 15},
        "armor": 2, "icon": "🧀", "price": 800,
        "lore": "Большой кусок сыра, каким-то чудом держащийся на голове."
    },
    "rat_king_crown_broken": {
        "name": "Сломанная корона Крысиного короля", "type": "equipment", "slot": "head",
        "role": "rat", "rarity": "epic",
        "desc": "+4 к силе. +10 XP за убийство.",
        "effect": {"strength": 4, "kill_xp": 10},
        "armor": 5, "icon": "👑💔", "price": 9000,
        "lore": "Некогда величественная корона, ныне треснувшая и помятая."
    },
    "mouse_ears": {
        "name": "Мышиные ушки", "type": "equipment", "slot": "head",
        "role": "all", "rarity": "common",
        "desc": "+2 к ловкости. +5% к уклонению в туннелях.",
        "effect": {"agility": 2, "dodge": 5},
        "armor": 1, "icon": "🐭", "price": 400,
        "lore": "Мягкие круглые ушки на ободке."
    },
    "rat_ears": {
        "name": "Крысиные уши", "type": "equipment", "slot": "head",
        "role": "all", "rarity": "common",
        "desc": "+2 к силе. +1 к урону в туннелях.",
        "effect": {"strength": 2, "damage": 1},
        "armor": 1, "icon": "🐀", "price": 400,
        "lore": "Острые серые уши, пришитые к кожаной повязке."
    },
    "turban": {
        "name": "Тюрбан", "type": "equipment", "slot": "head",
        "role": "mouse", "rarity": "epic",
        "desc": "+4 к интеллекту. Видишь кто Крыса после 3-й ночи.",
        "effect": {"intelligence": 4, "wisdom_reveal": True},
        "armor": 2, "icon": "👳", "price": 8500,
        "lore": "Плотно намотанный тюрбан цвета песка."
    },
    "fedora": {
        "name": "Федора", "type": "equipment", "slot": "head",
        "role": "all", "rarity": "rare",
        "desc": "+2 к интеллекту. +1 к находкам в туннелях.",
        "effect": {"intelligence": 2, "find_chance": 3},
        "armor": 2, "icon": "🕵️", "price": 1800,
        "lore": "Классическая фетровая шляпа с лентой."
    },
    "bucket_hat": {
        "name": "Ведро", "type": "equipment", "slot": "head",
        "role": "all", "rarity": "common",
        "desc": "+1 к силе. +5 к максимальному здоровью.",
        "effect": {"strength": 1, "max_health": 5},
        "armor": 4, "icon": "🪣", "price": 300,
        "lore": "Обычное жестяное ведро."
    },

    # ==================== ОРУЖИЕ (WEAPON) ====================
    "rat_dagger": {
        "name": "Крысиный кинжал", "type": "equipment", "slot": "weapon",
        "role": "rat", "rarity": "rare",
        "desc": "+3 к силе. Можешь убить двух мышей за одну ночь (раз в игру).",
        "effect": {"strength": 3, "double_kill": True},
        "armor": 0, "icon": "🗡️", "price": 2500,
        "craftable": True,
        "craft_materials": {"steel_shard": 2, "rat_incisor": 4, "rat_poison": 1},
        "craft_blueprint": "blueprint_poison_blade",
        "lore": "Узкий зазубренный клинок, покрытый тёмными пятнами."
    },
    "poison_vial": {
        "name": "Склянка с ядом", "type": "equipment", "slot": "weapon",
        "role": "rat", "rarity": "epic",
        "desc": "+2 к интеллекту. Жертва не может говорить следующий день.",
        "effect": {"intelligence": 2, "silence_victim": True},
        "armor": 0, "icon": "🧪", "price": 10000,
        "lore": "Маленький пузырёк с зеленоватой жидкостью."
    },
    "magnifying_glass": {
        "name": "Лупа детектива", "type": "equipment", "slot": "weapon",
        "role": "mouse", "rarity": "common",
        "desc": "+1 к интеллекту. Видишь кто за кого голосовал.",
        "effect": {"intelligence": 1, "see_votes": True},
        "armor": 0, "icon": "🔍", "price": 600,
        "lore": "Большая лупа в медной оправе."
    },
    "justice_hammer": {
        "name": "Молот правосудия", "type": "equipment", "slot": "weapon",
        "role": "mouse", "rarity": "legendary",
        "desc": "+5 к силе. При ничьей казнят Крысу.",
        "effect": {"strength": 5, "justice_tie": True},
        "armor": 0, "icon": "🔨", "price": 30000,
        "lore": "Тяжёлый судейский молоток, обитый железом."
    },
    "butcher_knife": {
        "name": "Нож мясника", "type": "equipment", "slot": "weapon",
        "role": "rat", "rarity": "legendary",
        "desc": "+5 к силе. Убийства приносят +10 XP.",
        "effect": {"strength": 5, "kill_xp": 10},
        "armor": 0, "icon": "🔪", "price": 30000,
        "craftable": True,
        "craft_materials": {"steel_shard": 3, "rat_king_eye": 1, "obsidian_scale": 2, "mithril_nugget": 1},
        "lore": "Когда-то этот нож принадлежал старому мяснику."
    },
    "crossbow": {
        "name": "Арбалет", "type": "equipment", "slot": "weapon",
        "role": "mouse", "rarity": "epic",
        "desc": "+3 к ловкости. Можешь выстрелить в игрока днём.",
        "effect": {"agility": 3, "day_shot": True},
        "armor": 0, "icon": "🏹", "price": 10000,
        "craftable": True,
        "craft_materials": {"bronze_alloy": 3, "bat_membrane": 2, "iron_gear": 2},
        "lore": "Компактный арбалет с натянутой тетивой."
    },
    "scepter_of_truth": {
        "name": "Скипетр истины", "type": "equipment", "slot": "weapon",
        "role": "mouse", "rarity": "legendary",
        "desc": "+4 к интеллекту. Раз в игру можешь узнать роль игрока.",
        "effect": {"intelligence": 4, "reveal_role": True},
        "armor": 0, "icon": "🔮", "price": 30000,
        "lore": "Длинный посох с сияющим кристаллом."
    },
    "shadow_blade": {
        "name": "Клинок тени", "type": "equipment", "slot": "weapon",
        "role": "rat", "rarity": "mythic",
        "desc": "+8 к ловкости. Убийства не оставляют следов.",
        "effect": {"agility": 8, "invisible_kill": True},
        "armor": 0, "icon": "🌑", "price": 120000,
        "lore": "Клинок, выкованный из самой темноты."
    },
    "cheese_sword": {
        "name": "Сырный меч", "type": "equipment", "slot": "weapon",
        "role": "all", "rarity": "common",
        "desc": "+2 к силе. +5% опыта за игру.",
        "effect": {"strength": 2, "xp_boost": 5},
        "armor": 0, "icon": "🧀", "price": 600,
        "craftable": True,
        "craft_materials": {"cheese_crust": 3, "rat_incisor": 2, "iron_gear": 1},
        "lore": "Затвердевший кусок сыра, заточенный до состояния клинка."
    },
    "staff_of_chaos": {
        "name": "Посох хаоса", "type": "equipment", "slot": "weapon",
        "role": "rat", "rarity": "mythic",
        "desc": "+5 к интеллекту. Каждую ночь случайный эффект.",
        "effect": {"intelligence": 5, "chaos_effect": True},
        "armor": 0, "icon": "🌀", "price": 120000,
        "lore": "Искривлённый посох, пульсирующий фиолетовой энергией."
    },
    "holy_water": {
        "name": "Святая вода", "type": "equipment", "slot": "weapon",
        "role": "all", "rarity": "rare",
        "desc": "+2 к интеллекту. +5 к максимальному здоровью.",
        "effect": {"intelligence": 2, "max_health": 5},
        "armor": 0, "icon": "💧", "price": 2500,
        "lore": "Склянка с чистой водой, освящённой в древнем храме."
    },
    "boomerang": {
        "name": "Бумеранг", "type": "equipment", "slot": "weapon",
        "role": "all", "rarity": "rare",
        "desc": "+2 к ловкости. Если тебя казнят — казнят и первого голосовавшего.",
        "effect": {"agility": 2, "revenge": True},
        "armor": 0, "icon": "🪃", "price": 2500,
        "lore": "Изогнутая деревянная палка, которая всегда возвращается."
    },
    "lucky_coin": {
        "name": "Счастливая монета", "type": "equipment", "slot": "weapon",
        "role": "all", "rarity": "common",
        "desc": "+1 к удаче. +3% к находкам в туннелях.",
        "effect": {"luck": 1, "find_chance": 3},
        "armor": 0, "icon": "🪙", "price": 600,
        "lore": "Потёртая монета с дырочкой посередине."
    },
    "mouse_trap_launcher": {
        "name": "Мышеловкомёт", "type": "equipment", "slot": "weapon",
        "role": "mouse", "rarity": "legendary",
        "desc": "+4 к интеллекту. Можешь поставить ловушку на игрока.",
        "effect": {"intelligence": 4, "trap_launcher": True},
        "armor": 0, "icon": "🪤🔫", "price": 28000,
        "lore": "Хитроумное устройство, стреляющее мышеловками."
    },
    "bell_of_awakening": {
        "name": "Колокол пробуждения", "type": "equipment", "slot": "weapon",
        "role": "mouse", "rarity": "rare",
        "desc": "+2 к интеллекту. Разбудить спящего игрока.",
        "effect": {"intelligence": 2, "awaken": True},
        "armor": 0, "icon": "🔔", "price": 2300,
        "lore": "Маленький медный колокольчик с чистым звоном."
    },
    "cheese_slicer": {
        "name": "Сырорезка", "type": "equipment", "slot": "weapon",
        "role": "all", "rarity": "common",
        "desc": "+1 к силе. +3 XP за игру.",
        "effect": {"strength": 1, "bonus_xp": 3},
        "armor": 0, "icon": "🔪🧀", "price": 500,
        "lore": "Острая проволочная сырорезка."
    },
    "catapult": {
        "name": "Катапульта", "type": "equipment", "slot": "weapon",
        "role": "mouse", "rarity": "epic",
        "desc": "+3 к силе. Можешь запустить игрока — он не голосует.",
        "effect": {"strength": 3, "catapult": True},
        "armor": 0, "icon": "🏗️", "price": 8500,
        "lore": "Миниатюрная катапульта."
    },
    "net_launcher": {
        "name": "Сеткомёт", "type": "equipment", "slot": "weapon",
        "role": "mouse", "rarity": "rare",
        "desc": "+2 к ловкости. Обездвижить Крысу на одну ночь.",
        "effect": {"agility": 2, "net_trap": True},
        "armor": 0, "icon": "🥅", "price": 2600,
        "lore": "Ручное устройство, выстреливающее прочную сеть."
    },

    # ==================== БРОНЯ (ARMOR) ====================
    "leather_vest": {
        "name": "Кожаный жилет", "type": "equipment", "slot": "armor",
        "role": "all", "rarity": "common",
        "desc": "+1 к ловкости. +10 к максимальному здоровью.",
        "effect": {"agility": 1, "max_health": 10},
        "armor": 8, "icon": "🦺", "price": 650,
        "craftable": True,
        "craft_materials": {"rat_pelt": 5, "linen_scrap": 2, "mouse_bone": 1},
        "lore": "Простой жилет из грубой кожи."
    },
    "faith_shield": {
        "name": "Щит веры", "type": "equipment", "slot": "armor",
        "role": "mouse", "rarity": "epic",
        "desc": "+2 ко всем характеристикам. Полная защита от одного убийства.",
        "effect": {"strength": 2, "agility": 2, "intelligence": 2, "night_shield": True},
        "armor": 20, "icon": "🛡️", "price": 11000,
        "lore": "Сияющий щит, выкованный из чистой веры."
    },
    "rat_skin_cloak": {
        "name": "Крысиный плащ", "type": "equipment", "slot": "armor",
        "role": "rat", "rarity": "legendary",
        "desc": "+4 к ловкости. Мыши не видят твою роль при смерти.",
        "effect": {"agility": 4, "hidden_role": True},
        "armor": 15, "icon": "🐀", "price": 32000,
        "lore": "Плащ, сшитый из шкур сотни крыс."
    },
    "chainmail": {
        "name": "Кольчуга", "type": "equipment", "slot": "armor",
        "role": "all", "rarity": "rare",
        "desc": "+2 к силе. +20 к максимальному здоровью.",
        "effect": {"strength": 2, "max_health": 20},
        "armor": 15, "icon": "⛓️", "price": 2600,
        "craftable": True,
        "craft_materials": {"iron_gear": 6, "bronze_alloy": 2, "leather_scrap": 2},
        "lore": "Сплетённая из стальных колец рубаха."
    },
    "mirror_armor": {
        "name": "Зеркальная броня", "type": "equipment", "slot": "armor",
        "role": "mouse", "rarity": "legendary",
        "desc": "+3 к интеллекту. Отражает атаку Крысы обратно (раз в игру).",
        "effect": {"intelligence": 3, "reflect_kill": True},
        "armor": 22, "icon": "🪞", "price": 32000,
        "lore": "Начищенная до блеска броня."
    },
    "invisibility_cloak": {
        "name": "Плащ-невидимка", "type": "equipment", "slot": "armor",
        "role": "rat", "rarity": "mythic",
        "desc": "+6 к ловкости. Тебя нельзя выбрать целью голосования.",
        "effect": {"agility": 6, "vote_immune": True},
        "armor": 10, "icon": "🎭", "price": 130000,
        "craftable": True,
        "craft_materials": {"moon_silk": 3, "void_essence": 1, "spider_silk": 2, "bat_membrane": 1},
        "craft_blueprint": "blueprint_invisibility_cloak",
        "lore": "Серебристый плащ, струящийся как вода."
    },
    "cheese_armor": {
        "name": "Сырная броня", "type": "equipment", "slot": "armor",
        "role": "all", "rarity": "common",
        "desc": "+2 к силе. +5 к максимальному здоровью.",
        "effect": {"strength": 2, "max_health": 5},
        "armor": 6, "icon": "🧀", "price": 650,
        "lore": "Панцирь из затвердевшего сыра."
    },
    "dragon_scale": {
        "name": "Чешуя дракона", "type": "equipment", "slot": "armor",
        "role": "all", "rarity": "legendary",
        "desc": "+3 ко всем. Иммунитет к дебаффам.",
        "effect": {"strength": 3, "agility": 3, "intelligence": 3, "debuff_immune": True},
        "armor": 25, "icon": "🐉", "price": 32000,
        "lore": "Огромная чешуйка мифического ящера."
    },
    "angel_robes": {
        "name": "Одеяния ангела", "type": "equipment", "slot": "armor",
        "role": "mouse", "rarity": "mythic",
        "desc": "+5 к интеллекту. После смерти можешь защитить одного.",
        "effect": {"intelligence": 5, "death_protect": True},
        "armor": 18, "icon": "👼", "price": 130000,
        "lore": "Белоснежные одежды, сотканные из света."
    },
    "demon_skin": {
        "name": "Шкура демона", "type": "equipment", "slot": "armor",
        "role": "rat", "rarity": "mythic",
        "desc": "+5 к силе. После смерти забираешь одного мыша с собой.",
        "effect": {"strength": 5, "death_kill": True},
        "armor": 20, "icon": "👿", "price": 130000,
        "lore": "Красная чешуйчатая шкура, источающая жар."
    },
    "turtle_shell": {
        "name": "Черепаший панцирь", "type": "equipment", "slot": "armor",
        "role": "all", "rarity": "rare",
        "desc": "+3 к силе. +25 к максимальному здоровью.",
        "effect": {"strength": 3, "max_health": 25},
        "armor": 18, "icon": "🐢", "price": 2600,
        "lore": "Тяжёлый костяной панцирь."
    },
    "gambeson": {
        "name": "Гамбезон", "type": "equipment", "slot": "armor",
        "role": "all", "rarity": "common",
        "desc": "+1 к силе. +15 к максимальному здоровью.",
        "effect": {"strength": 1, "max_health": 15},
        "armor": 10, "icon": "🧥", "price": 650,
        "craftable": True,
        "craft_materials": {"linen_scrap": 4, "rat_pelt": 3, "wool_clump": 2},
        "lore": "Стёганая куртка, набитая конским волосом."
    },
    "bulletproof_vest": {
        "name": "Бронежилет", "type": "equipment", "slot": "armor",
        "role": "all", "rarity": "epic",
        "desc": "+2 к силе. Защита от выстрела из арбалета.",
        "effect": {"strength": 2, "shot_proof": True},
        "armor": 25, "icon": "🔫", "price": 11000,
        "lore": "Современный бронежилет."
    },
    "cloak_of_rat_emperor": {
        "name": "Плащ Крысиного императора", "type": "equipment", "slot": "armor",
        "role": "rat", "rarity": "mythic",
        "desc": "+6 к силе. После смерти показывается фальшивая роль.",
        "effect": {"strength": 6, "fake_role": "МЫШЬ"},
        "armor": 18, "icon": "🏰", "price": 130000,
        "lore": "Пурпурный плащ, подбитый горностаем."
    },
    "cloak_of_mouse_god": {
        "name": "Плащ Бога мышей", "type": "equipment", "slot": "armor",
        "role": "mouse", "rarity": "mythic",
        "desc": "+6 к интеллекту. После смерти все узнают кто Крыса.",
        "effect": {"intelligence": 6, "reveal_rat_on_death": True},
        "armor": 18, "icon": "⚡", "price": 130000,
        "lore": "Серебристый плащ, расшитый молниями."
    },
    "bubble_wrap": {
        "name": "Пузырчатая плёнка", "type": "equipment", "slot": "armor",
        "role": "all", "rarity": "common",
        "desc": "+1 к ловкости. +5 HP, +1 XP.",
        "effect": {"agility": 1, "max_health": 5, "bonus_xp": 1},
        "armor": 3, "icon": "📦", "price": 400,
        "lore": "Загадочный материал из другого мира."
    },

    # ==================== АКСЕССУАРЫ (ACCESSORY) ====================
    "lucky_cheese": {
        "name": "Счастливый сыр", "type": "equipment", "slot": "accessory",
        "role": "all", "rarity": "common",
        "desc": "+1 к удаче. +10 XP за игру.",
        "effect": {"luck": 1, "bonus_xp": 10},
        "armor": 0, "icon": "🧀", "price": 550,
        "lore": "Кусочек сыра с дырочкой в форме клевера."
    },
    "golden_pocket_watch": {
        "name": "Золотые часы", "type": "equipment", "slot": "accessory",
        "role": "all", "rarity": "rare",
        "desc": "+2 к ловкости. +5 секунд на голосование.",
        "effect": {"agility": 2, "vote_time_bonus": 5},
        "armor": 1, "icon": "⌚", "price": 2200,
        "lore": "Старинные часы на цепочке."
    },
    "ghost_amulet": {
        "name": "Амулет призрака", "type": "equipment", "slot": "accessory",
        "role": "all", "rarity": "mythic",
        "desc": "+4 к интеллекту. Можешь голосовать после смерти.",
        "effect": {"intelligence": 4, "ghost_vote": True},
        "armor": 3, "icon": "👻", "price": 110000,
        "lore": "Полупрозрачный амулет, холодный на ощупь."
    },
    "rat_tail_ring": {
        "name": "Кольцо из крысиного хвоста", "type": "equipment", "slot": "accessory",
        "role": "rat", "rarity": "epic",
        "desc": "+3 к силе. +1 голос против любой цели.",
        "effect": {"strength": 3, "extra_vote_against": 1},
        "armor": 1, "icon": "💍", "price": 8800,
        "lore": "Кольцо, сплетённое из засушенного крысиного хвоста."
    },
    "mouse_whisker_ring": {
        "name": "Кольцо из усов мыши", "type": "equipment", "slot": "accessory",
        "role": "mouse", "rarity": "epic",
        "desc": "+3 к ловкости. Твой голос нельзя отменить.",
        "effect": {"agility": 3, "unremovable_vote": True},
        "armor": 1, "icon": "💍", "price": 8800,
        "lore": "Тонкое колечко из мышиных усов."
    },
    "lucky_rabbit_foot": {
        "name": "Кроличья лапка", "type": "equipment", "slot": "accessory",
        "role": "all", "rarity": "rare",
        "desc": "+2 к удаче. +7% к находкам в туннелях.",
        "effect": {"luck": 2, "find_chance": 7},
        "armor": 0, "icon": "🐰", "price": 2200,
        "lore": "Пушистая лапка на верёвочке."
    },
    "four_leaf_clover": {
        "name": "Четырёхлистный клевер", "type": "equipment", "slot": "accessory",
        "role": "all", "rarity": "epic",
        "desc": "+3 к удаче. Один раз избежать смерти в туннелях.",
        "effect": {"luck": 3, "avoid_death_once": True},
        "armor": 0, "icon": "🍀", "price": 8800,
        "lore": "Засушенный листок клевера с четырьмя лепестками."
    },
    "horseshoe": {
        "name": "Подкова", "type": "equipment", "slot": "accessory",
        "role": "all", "rarity": "common",
        "desc": "+1 к удаче. +3% к находкам.",
        "effect": {"luck": 1, "find_chance": 3},
        "armor": 2, "icon": "🧲", "price": 550,
        "lore": "Ржавая подкова."
    },
    "pearl_necklace": {
        "name": "Жемчужное ожерелье", "type": "equipment", "slot": "accessory",
        "role": "all", "rarity": "rare",
        "desc": "+2 к интеллекту. +10% опыта за победу.",
        "effect": {"intelligence": 2, "win_xp_boost": 10},
        "armor": 2, "icon": "📿", "price": 2200,
        "lore": "Нитка речного жемчуга."
    },
    "skull_necklace": {
        "name": "Ожерелье из черепов", "type": "equipment", "slot": "accessory",
        "role": "rat", "rarity": "epic",
        "desc": "+3 к силе. +5 XP за каждое убийство.",
        "effect": {"strength": 3, "kill_xp": 5},
        "armor": 2, "icon": "💀", "price": 8800,
        "lore": "Нитка крошечных черепов."
    },
    "wedding_ring": {
        "name": "Обручальное кольцо", "type": "equipment", "slot": "accessory",
        "role": "all", "rarity": "legendary",
        "desc": "+2 ко всем. Связывает с другим игроком.",
        "effect": {"strength": 2, "agility": 2, "intelligence": 2, "soulbound": True},
        "armor": 3, "icon": "💍", "price": 27500,
        "lore": "Потускневшее золотое кольцо."
    },
    "compass": {
        "name": "Компас", "type": "equipment", "slot": "accessory",
        "role": "mouse", "rarity": "rare",
        "desc": "+2 к интеллекту. Отслеживает голосование Крысы.",
        "effect": {"intelligence": 2, "track_rat": True},
        "armor": 1, "icon": "🧭", "price": 2200,
        "lore": "Старый латунный компас."
    },
    "hourglass": {
        "name": "Песочные часы", "type": "equipment", "slot": "accessory",
        "role": "all", "rarity": "epic",
        "desc": "+2 к интеллекту. +10 секунд ко всем фазам.",
        "effect": {"intelligence": 2, "time_bonus": 10},
        "armor": 1, "icon": "⏳", "price": 8800,
        "lore": "Миниатюрные песочные часы."
    },
    "monocle": {
        "name": "Монокль", "type": "equipment", "slot": "accessory",
        "role": "all", "rarity": "common",
        "desc": "+1 к интеллекту. +2% к точности.",
        "effect": {"intelligence": 1, "all_accuracy": 2},
        "armor": 0, "icon": "🧐", "price": 550,
        "lore": "Стеклянная линза в золотой оправе."
    },
    "spy_earpiece": {
        "name": "Шпионский наушник", "type": "equipment", "slot": "accessory",
        "role": "mouse", "rarity": "rare",
        "desc": "+2 к интеллекту. Слышишь выбор Крысы ночью.",
        "effect": {"intelligence": 2, "hear_rat": True},
        "armor": 0, "icon": "🎧", "price": 2200,
        "lore": "Крошечный наушник."
    },
    "pocket_mirror": {
        "name": "Карманное зеркальце", "type": "equipment", "slot": "accessory",
        "role": "all", "rarity": "rare",
        "desc": "+2 к интеллекту. Отражает проклятия.",
        "effect": {"intelligence": 2, "curse_reflect": True},
        "armor": 1, "icon": "🪞", "price": 2200,
        "lore": "Маленькое зеркальце в серебряной оправе."
    },
    "locket": {
        "name": "Медальон", "type": "equipment", "slot": "accessory",
        "role": "all", "rarity": "epic",
        "desc": "+2 ко всем. +1 жизнь (раз в 5 игр).",
        "effect": {"strength": 2, "agility": 2, "intelligence": 2, "extra_life": 1},
        "armor": 3, "icon": "📿", "price": 8800,
        "lore": "Золотой медальон с портретом неизвестной дамы."
    },
    "rat_king_medallion": {
        "name": "Медальон Крысиного короля", "type": "equipment", "slot": "accessory",
        "role": "rat", "rarity": "legendary",
        "desc": "+4 к силе. Все мыши видят тебя как Мышь до первого убийства.",
        "effect": {"strength": 4, "disguise_until_kill": True},
        "armor": 3, "icon": "🏅", "price": 27000,
        "lore": "Тяжёлый медальон с изображением крысиной головы."
    },
    "ring_of_regeneration": {
        "name": "Кольцо регенерации", "type": "equipment", "slot": "accessory",
        "role": "all", "rarity": "rare",
        "desc": "+1 к ловкости. +5 HP/час.",
        "effect": {"agility": 1, "regen": 5},
        "armor": 1, "icon": "💍", "price": 3000,
        "lore": "Тёплое золотое кольцо."
    },
    "amulet_of_health": {
        "name": "Амулет здоровья", "type": "equipment", "slot": "accessory",
        "role": "all", "rarity": "epic",
        "desc": "+10 HP/час.",
        "effect": {"regen": 10},
        "armor": 2, "icon": "📿", "price": 8000,
        "lore": "Древний амулет с руной жизни."
    },
    "stinky_sock": {
        "name": "Вонючий носок", "type": "equipment", "slot": "accessory",
        "role": "all", "rarity": "common",
        "desc": "+1 к ловкости. Отпугивает всех.",
        "effect": {"agility": 1},
        "armor": 0, "icon": "🧦", "price": 300,
        "lore": "Старый носок, который не стирали месяцами."
    },
    "rubber_duck": {
        "name": "Резиновая уточка", "type": "equipment", "slot": "accessory",
        "role": "all", "rarity": "common",
        "desc": "+1 к удаче. Кря!",
        "effect": {"luck": 1},
        "armor": 0, "icon": "🦆", "price": 250,
        "lore": "Жёлтая резиновая уточка."
    },
}