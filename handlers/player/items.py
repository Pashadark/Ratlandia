"""Предметы для Ратляндии — 350+ предметов с ресурсами и рецептами"""
from handlers.crafting import get_player_resources
# ========== УРОН ОРУЖИЯ ==========
WEAPON_DAMAGE = {}
# ========== РЕСУРСЫ ==========
RESOURCES = {
    # 🔩 МЕТАЛЛЫ
    "copper_scrap": {"name": "Медный лом", "type": "resource", "resource_type": "metal", "rarity": "common", "icon": "🔩", "desc": "Обломки труб, монет и проволоки. Мягкий, но ковкий", "price": 50},
    "bronze_alloy": {"name": "Бронзовый сплав", "type": "resource", "resource_type": "metal", "rarity": "common", "icon": "⛓️", "desc": "Колокольная бронза. Глушит звуки, не ржавеет", "price": 80},
    "iron_gear": {"name": "Железная шестерня", "type": "resource", "resource_type": "metal", "rarity": "common", "icon": "⚙️", "desc": "Слизана с крысоловки. Тяжёлая, надёжная", "price": 100},
    "steel_shard": {"name": "Стальной осколок", "type": "resource", "resource_type": "metal", "rarity": "rare", "icon": "🗡️", "desc": "Обломок человечьего меча. Держит заточку", "price": 500},
    "silver_ingot": {"name": "Серебряный слиток", "type": "resource", "resource_type": "metal", "rarity": "rare", "icon": "🛎️", "desc": "Звенит в присутствии магии. Жжёт нежить", "price": 600},
    "emerald_crumb": {"name": "Изумрудная крошка", "type": "resource", "resource_type": "metal", "rarity": "rare", "icon": "🟢", "desc": "Осколки магического кристалла. Усиливает стихии", "price": 700},
    "obsidian_scale": {"name": "Обсидиановая чешуя", "type": "resource", "resource_type": "metal", "rarity": "epic", "icon": "🌑", "desc": "Чёрное вулканическое стекло. Острее бритвы", "price": 2000},
    "mithril_nugget": {"name": "Мифриловый самородок", "type": "resource", "resource_type": "metal", "rarity": "epic", "icon": "✨", "desc": "Лёгкий как перо, прочный как сталь. Светится в темноте", "price": 2500},
    "adamantite": {"name": "Адамантит", "type": "resource", "resource_type": "metal", "rarity": "legendary", "icon": "💀", "desc": "Твёрже всего сущего. Меняет цвет под луной", "price": 10000},
    "rat_god_tooth": {"name": "Зуб Крысиного бога", "type": "resource", "resource_type": "metal", "rarity": "legendary", "icon": "⚜️", "desc": "Не то кость, не то металл. Пульсирует гнилью", "price": 12000},

    # 🧵 ТКАНИ И КОЖА
    "rat_pelt": {"name": "Крысиная шерсть", "type": "resource", "resource_type": "fabric", "rarity": "common", "icon": "🧵", "desc": "Колючая, но тёплая. С неё всё начинается", "price": 30},
    "linen_scrap": {"name": "Льняной лоскут", "type": "resource", "resource_type": "fabric", "rarity": "common", "icon": "🧦", "desc": "Обрывки человечьих тряпок. Мягче шерсти", "price": 40},
    "wool_clump": {"name": "Шерстяной клок", "type": "resource", "resource_type": "fabric", "rarity": "common", "icon": "🧣", "desc": "Плотная вязка. Греет и глушит шаги", "price": 45},
    "leather_scrap": {"name": "Кожаный обрывок", "type": "resource", "resource_type": "fabric", "rarity": "common", "icon": "🧤", "desc": "Кусок старой перчатки. Грубая защита", "price": 50},
    "spider_silk": {"name": "Паучий шёлк", "type": "resource", "resource_type": "fabric", "rarity": "rare", "icon": "🕸️", "desc": "Липкая нить подземных пауков. Эластичная", "price": 400},
    "bat_membrane": {"name": "Перепонка нетопыря", "type": "resource", "resource_type": "fabric", "rarity": "rare", "icon": "🦇", "desc": "Тонкая кожа летучей мыши. Бесшумная", "price": 450},
    "snake_skin": {"name": "Сброшенная кожа ужа", "type": "resource", "resource_type": "fabric", "rarity": "rare", "icon": "🐍", "desc": "Гибкая, водонепроницаемая. Для скрытных плащей", "price": 500},
    "moon_silk": {"name": "Лунный шёлк", "type": "resource", "resource_type": "fabric", "rarity": "epic", "icon": "🌙", "desc": "Ткётся из лунного света пауками-жрецами. Мерцает", "price": 3000},
    "cat_pelt": {"name": "Кошачья шкура", "type": "resource", "resource_type": "fabric", "rarity": "epic", "icon": "🐈", "desc": "Жуткая редкость. Мягкая, тёплая, пахнет страхом", "price": 3500},
    "star_silk": {"name": "Звёздный шёлк", "type": "resource", "resource_type": "fabric", "rarity": "legendary", "icon": "✨", "desc": "Соткан из света умирающих звёзд. Не рвётся, не горит", "price": 15000},

    # 🦴 КОСТИ
    "mouse_bone": {"name": "Мышиная косточка", "type": "resource", "resource_type": "bone", "rarity": "common", "icon": "🦴", "desc": "Лёгкая и хрупкая. Расходник", "price": 20},
    "rat_incisor": {"name": "Крысиный резец", "type": "resource", "resource_type": "bone", "rarity": "common", "icon": "🦷", "desc": "Острый от природы. Наконечники и лезвия", "price": 25},
    "fish_spine": {"name": "Рыбий хребет", "type": "resource", "resource_type": "bone", "rarity": "common", "icon": "🦴", "desc": "Гибкий, гнётся но не ломается", "price": 30},
    "mole_skull": {"name": "Череп крота", "type": "resource", "resource_type": "bone", "rarity": "rare", "icon": "🦉", "desc": "Слепой, но чувствует вибрации. Для амулетов", "price": 350},
    "crow_bone": {"name": "Воронья кость", "type": "resource", "resource_type": "bone", "rarity": "rare", "icon": "🦅", "desc": "Полые, звонкие. Для рун и амулетов", "price": 400},
    "rat_tail_vertebra": {"name": "Хвостовой позвонок Крысы", "type": "resource", "resource_type": "bone", "rarity": "rare", "icon": "🐀", "desc": "Гибкий как хлыст. Для рукоятей", "price": 450},
    "bat_fang": {"name": "Клык нетопыря-вожака", "type": "resource", "resource_type": "bone", "rarity": "epic", "icon": "🦇", "desc": "Проводит магию крови", "price": 2500},
    "rat_king_eye": {"name": "Глаз Крысиного короля", "type": "resource", "resource_type": "bone", "rarity": "epic", "icon": "👁️", "desc": "Всё ещё зрит. Вставляется в оружие", "price": 3000},
    "first_rat_skull": {"name": "Череп Первой Крысы", "type": "resource", "resource_type": "bone", "rarity": "legendary", "icon": "💀", "desc": "Прародительница. Шепчет во сне", "price": 12000},
    "labyrinth_heart": {"name": "Сердце Лабиринта", "type": "resource", "resource_type": "bone", "rarity": "legendary", "icon": "🧿", "desc": "Бьётся. Живое. Первоматерия", "price": 15000},

    # 🧪 АЛХИМИЯ
    "moldy_crumb": {"name": "Плесневелая крошка", "type": "resource", "resource_type": "alchemy", "rarity": "common", "icon": "🧀", "desc": "Слабо ядовита, основа простых зелий", "price": 20},
    "basement_mushroom": {"name": "Подвальный гриб", "type": "resource", "resource_type": "alchemy", "rarity": "common", "icon": "🍄", "desc": "Растёт в темноте. Восстанавливает силы", "price": 25},
    "empty_vial": {"name": "Пустая склянка", "type": "resource", "resource_type": "alchemy", "rarity": "common", "icon": "🧪", "desc": "Для хранения и смешивания", "price": 15},
    "rat_poison": {"name": "Флакон крысиного яда", "type": "resource", "resource_type": "alchemy", "rarity": "rare", "icon": "🩸", "desc": "Из желёз матёрой Крысы", "price": 500},
    "rat_king_tear": {"name": "Слеза Крысиного короля", "type": "resource", "resource_type": "alchemy", "rarity": "rare", "icon": "💧", "desc": "Густая, маслянистая. Усиливает зелья", "price": 600},
    "wall_soot": {"name": "Копоть со стен", "type": "resource", "resource_type": "alchemy", "rarity": "rare", "icon": "🕯️", "desc": "Смесь сажи и магии. Основа для чернил", "price": 350},
    "mandrake": {"name": "Мандрагора подземная", "type": "resource", "resource_type": "alchemy", "rarity": "epic", "icon": "🌿", "desc": "Кричит при сборе. Сильный реагент", "price": 3000},
    "ancient_scrap": {"name": "Обрывок древнего свитка", "type": "resource", "resource_type": "alchemy", "rarity": "epic", "icon": "📜", "desc": "Фрагмент заклинания. Непонятно откуда", "price": 3500},
    "void_essence": {"name": "Эссенция Пустоты", "type": "resource", "resource_type": "alchemy", "rarity": "legendary", "icon": "🧪", "desc": "Чистая магия в жидкой форме", "price": 15000},
    "spark_creation": {"name": "Искра Творения", "type": "resource", "resource_type": "alchemy", "rarity": "legendary", "icon": "💎", "desc": "Застывший свет. Первосоздание", "price": 20000},

    # 🍖 ПРОВИЗИЯ
    "cheese_crust": {"name": "Корка сыра", "type": "resource", "resource_type": "food", "rarity": "common", "icon": "🧀", "desc": "+5 HP. Просто еда", "price": 30},
    "bread_crumb": {"name": "Хлебный мякиш", "type": "resource", "resource_type": "food", "rarity": "common", "icon": "🥖", "desc": "+3 HP. Мягкий, плесень не тронула", "price": 20},
    "clean_water": {"name": "Капля чистой воды", "type": "resource", "resource_type": "food", "rarity": "common", "icon": "💧", "desc": "Снимает лёгкое отравление", "price": 50},
    "smoked_lard": {"name": "Копчёное сало", "type": "resource", "resource_type": "food", "rarity": "rare", "icon": "🥓", "desc": "+10 HP, +5% к защите на 1 ход", "price": 300},
    "honey_drop": {"name": "Капля мёда", "type": "resource", "resource_type": "food", "rarity": "rare", "icon": "🍯", "desc": "+5 HP, снимает отравление", "price": 350},
    "underground_truffle": {"name": "Трюфель Подземья", "type": "resource", "resource_type": "food", "rarity": "epic", "icon": "🍄", "desc": "Полное восстановление HP", "price": 3000},
    "marrow_bone": {"name": "Мозговая косточка", "type": "resource", "resource_type": "food", "rarity": "epic", "icon": "🦴", "desc": "+15 HP, +10% к силе атаки на 2 хода", "price": 2500},
    "forgotten_ale": {"name": "Глоток Забытого Эля", "type": "resource", "resource_type": "food", "rarity": "legendary", "icon": "🍷", "desc": "Полное восстановление HP и снятие всех эффектов", "price": 10000},

    # 📜 ЧЕРТЕЖИ
    "blueprint_cheese_slicer": {"name": "Чертёж: Сырорезка", "type": "resource", "resource_type": "blueprint", "rarity": "rare", "icon": "📄", "desc": "Открывает рецепт крафта оружия", "price": 1000},
    "blueprint_poison_blade": {"name": "Чертёж: Отравленный клинок", "type": "resource", "resource_type": "blueprint", "rarity": "rare", "icon": "📄", "desc": "Открывает рецепт крафта оружия", "price": 1000},
    "blueprint_gambeson": {"name": "Чертёж: Усиленный гамбезон", "type": "resource", "resource_type": "blueprint", "rarity": "rare", "icon": "📄", "desc": "Открывает рецепт крафта брони", "price": 1000},
    "blueprint_invisibility_cloak": {"name": "Чертёж: Плащ-невидимка", "type": "resource", "resource_type": "blueprint", "rarity": "epic", "icon": "📜", "desc": "Открывает рецепт крафта одежды", "price": 5000},
    "blueprint_explosive_vial": {"name": "Чертёж: Взрывная склянка", "type": "resource", "resource_type": "blueprint", "rarity": "epic", "icon": "📜", "desc": "Открывает рецепт крафта расходника", "price": 5000},
    "blueprint_crown": {"name": "Чертёж: Корона Короля", "type": "resource", "resource_type": "blueprint", "rarity": "legendary", "icon": "📜", "desc": "Открывает легендарный рецепт", "price": 15000},

    # 🎴 КОЛЛЕКЦИОННЫЕ
    "wrinkled_card": {"name": "Мятая карта", "type": "resource", "resource_type": "collectible", "rarity": "common", "icon": "🎴", "desc": "Часть пазла. Собери 5 — откроется тайник", "price": 100},
    "smooth_pebble": {"name": "Гладкий камешек", "type": "resource", "resource_type": "collectible", "rarity": "common", "icon": "🪨", "desc": "Приятно держать в лапке", "price": 10},
    "surface_shell": {"name": "Ракушка с Поверхности", "type": "resource", "resource_type": "collectible", "rarity": "rare", "icon": "🐚", "desc": "Откуда она в канализации? Пахнет морем", "price": 300},
    "human_coin": {"name": "Монета людей", "type": "resource", "resource_type": "collectible", "rarity": "rare", "icon": "🪙", "desc": "Странный металл и символы", "price": 400},
    "tiny_matryoshka": {"name": "Крошечная матрёшка", "type": "resource", "resource_type": "collectible", "rarity": "rare", "icon": "🪆", "desc": "Внутри ещё одна. И ещё. Зачем?", "price": 350},
    "ancient_amulet": {"name": "Амулет Древних", "type": "resource", "resource_type": "collectible", "rarity": "epic", "icon": "📿", "desc": "Светится в присутствии тайников", "price": 5000},
    "tapestry_scrap": {"name": "Обрывок гобелена", "type": "resource", "resource_type": "collectible", "rarity": "legendary", "icon": "👑", "desc": "Изображает битву Крысы и Кота. Ценится превыше золота", "price": 20000},

    # 🔮 МАГИЧЕСКИЕ
    "fairy_dust": {"name": "Пыльца феи", "type": "resource", "resource_type": "magic", "rarity": "rare", "icon": "💠", "desc": "Щепотка при зачаровании — вещь получает свечение", "price": 600},
    "moon_dew": {"name": "Лунная роса", "type": "resource", "resource_type": "magic", "rarity": "rare", "icon": "🌙", "desc": "Капля на оружие — +5% урона нежити", "price": 650},
    "mage_blood": {"name": "Кровь мага", "type": "resource", "resource_type": "magic", "rarity": "epic", "icon": "🩸", "desc": "Капля силы. Добавляет +1 магическое свойство при крафте", "price": 4000},
    "phoenix_ember": {"name": "Уголёк феникса", "type": "resource", "resource_type": "magic", "rarity": "epic", "icon": "🔥", "desc": "Вещь получает шанс воспламенить врага", "price": 4500},
    "ice_worm_tear": {"name": "Слеза Ледяного червя", "type": "resource", "resource_type": "magic", "rarity": "legendary", "icon": "❄️", "desc": "Вещь получает ауру холода. Замедляет врагов", "price": 15000},
    "storm_spark": {"name": "Искра Бури", "type": "resource", "resource_type": "magic", "rarity": "legendary", "icon": "⚡", "desc": "Вещь получает шанс призвать молнию", "price": 18000},

    # 🪨 ПРОЧЕЕ
    "stone_shard": {"name": "Осколок камня", "type": "resource", "resource_type": "other", "rarity": "common", "icon": "🪨", "desc": "Из стен туннеля. Везде и всюду", "price": 5},
    "spider_web": {"name": "Паутина", "type": "resource", "resource_type": "other", "rarity": "common", "icon": "🕸️", "desc": "Липкая. Для связок и бинтов", "price": 10},
    "pigeon_feather": {"name": "Перо голубя", "type": "resource", "resource_type": "other", "rarity": "common", "icon": "🪶", "desc": "Мягкое. Для стабилизации стрел", "price": 10},
    "candle_stub": {"name": "Огарок свечи", "type": "resource", "resource_type": "other", "rarity": "common", "icon": "🕯️", "desc": "Воск и фитиль. Источник света", "price": 15},
    "cloudy_crystal": {"name": "Мутный кристалл", "type": "resource", "resource_type": "other", "rarity": "rare", "icon": "🔮", "desc": "Слабо светится. Фокусирует магию", "price": 400},
    "mirror_shard_res": {"name": "Осколок зеркала", "type": "resource", "resource_type": "other", "rarity": "rare", "icon": "🪞", "desc": "Отражает не только свет", "price": 350},
    "magnetic_stone": {"name": "Магнитный камень", "type": "resource", "resource_type": "other", "rarity": "epic", "icon": "🧲", "desc": "Притягивает металл. Ломает стрелы", "price": 3000},
    "hermit_rosary": {"name": "Чётки Отшельника", "type": "resource", "resource_type": "other", "rarity": "epic", "icon": "📿", "desc": "Молятся сами. Дают благословение", "price": 3500},
    "gate_key": {"name": "Ключ от Затворов", "type": "resource", "resource_type": "other", "rarity": "legendary", "icon": "🗝️", "desc": "Открывает любую дверь. Один раз", "price": 20000},
    "labyrinth_seal": {"name": "Печать Лабиринта", "type": "resource", "resource_type": "other", "rarity": "legendary", "icon": "🪬", "desc": "Знак власти над туннелями", "price": 25000},
}

# ========== ЭКИПИРОВКА (можно надеть/снять, действует постоянно пока надето) ==========
EQUIPMENT = {
    # ==================== ШЛЯПЫ (HEAD) ====================
    "detective_hat": {
        "name": "Шляпа детектива", "type": "equipment", "slot": "head",
        "role": "all", "rarity": "rare",
        "desc": "+2 к интеллекту. Видишь кто за кого голосовал в Мафии.",
        "effect": {"intelligence": 2, "see_votes": True},
        "icon": "🎩", "price": 2000,
        "lore": "Поношенная фетровая шляпа, пропитанная табачным дымом и запахом старых архивов. Её предыдущий владелец раскрыл десятки преступлений, прежде чем сам стал жертвой."
    },
    "shadow_hood": {
        "name": "Капюшон тени", "type": "equipment", "slot": "head",
        "role": "rat", "rarity": "epic",
        "desc": "+3 к ловкости. Твои убийства не раскрывают роль жертвы.",
        "effect": {"agility": 3, "hidden_kill_role": True},
        "icon": "🌑", "price": 8000,
        "lore": "Сотканный из теней Нижних Туннелей, этот капюшон скрывает не только лицо, но и следы твоих деяний. Никто не узнает, кем была жертва."
    },
    "crown_of_rat_king": {
        "name": "Корона Крысиного короля", "type": "equipment", "slot": "head",
        "role": "rat", "rarity": "legendary",
        "desc": "+5 к силе. Все Мыши теряют 1 голос на голосовании.",
        "effect": {"strength": 5, "mice_vote_penalty": 1},
        "icon": "👑", "price": 25000,
        "lore": "Тяжёлая корона из тёмного железа, усыпанная осколками костей. Когда Крысиный король носит её, даже самые смелые Мыши теряют волю к сопротивлению."
    },
    "crown_of_mouse_king": {
        "name": "Корона Мышиного короля", "type": "equipment", "slot": "head",
        "role": "mouse", "rarity": "legendary",
        "desc": "+3 ко всем характеристикам. Твой голос считается за 2.",
        "effect": {"strength": 3, "agility": 3, "intelligence": 3, "double_vote": True},
        "icon": "👑", "price": 25000,
        "lore": "Изящная золотая корона, украшенная крошечными сырными самоцветами. Символ надежды для всех Мышей, дарующий своему владельцу право решающего слова."
    },
    "chef_hat": {
        "name": "Колпак шефа", "type": "equipment", "slot": "head",
        "role": "all", "rarity": "common",
        "desc": "+1 к интеллекту. +5% шанс найти предмет в туннелях.",
        "effect": {"intelligence": 1, "find_chance": 5},
        "icon": "🧑‍🍳", "price": 500,
        "lore": "Высокий белый колпак, слегка испачканный мукой и сырной пылью. Говорят, его носил легендарный повар, способный приготовить пир из ничего."
    },
    "top_hat": {
        "name": "Цилиндр джентльмена", "type": "equipment", "slot": "head",
        "role": "all", "rarity": "rare",
        "desc": "+2 ко всем характеристикам.",
        "effect": {"strength": 2, "agility": 2, "intelligence": 2},
        "icon": "🎩", "price": 2000,
        "lore": "Элегантный чёрный цилиндр, видавший лучшие времена. Несмотря на потёртости, он всё ещё придаёт владельцу благородный вид и толику удачи."
    },
    "jester_cap": {
        "name": "Колпак шута", "type": "equipment", "slot": "head",
        "role": "all", "rarity": "epic",
        "desc": "+2 к ловкости. Случайный эффект каждую игру в Мафии.",
        "effect": {"agility": 2, "random_effect": True},
        "icon": "🃏", "price": 8000,
        "lore": "Разноцветный колпак с бубенчиками, который звенит в самый неподходящий момент. Никто не знает, что он выкинет в следующую секунду — как и его владелец."
    },
    "viking_helmet": {
        "name": "Шлем викинга", "type": "equipment", "slot": "head",
        "role": "all", "rarity": "rare",
        "desc": "+3 к силе. +10 к максимальному здоровью в туннелях.",
        "effect": {"strength": 3, "max_health": 10},
        "icon": "🪓", "price": 2000,
        "lore": "Грубый железный шлем, побывавший в сотне стычек. Пахнет потом, элем и старой кровью. Внушает уважение и дарит стойкость."
    },
    "ninja_mask": {
        "name": "Маска ниндзя", "type": "equipment", "slot": "head",
        "role": "rat", "rarity": "rare",
        "desc": "+3 к ловкости. Твой голос на голосовании скрыт.",
        "effect": {"agility": 3, "hidden_vote": True},
        "icon": "🥷", "price": 2000,
        "lore": "Чёрная маска, оставляющая лишь щёлочку для глаз. Никто не узнает, за кого ты проголосовал — идеально для тайных интриг."
    },
    "wizard_hat": {
        "name": "Шляпа волшебника", "type": "equipment", "slot": "head",
        "role": "all", "rarity": "legendary",
        "desc": "+5 к интеллекту. +20% опыт за игру.",
        "effect": {"intelligence": 5, "xp_boost": 20},
        "icon": "🧙", "price": 25000,
        "lore": "Высокая остроконечная шляпа, расшитая серебряными звёздами. Говорят, она принадлежала великому магу, который познал все тайны Подземного Царства."
    },
    "pirate_hat": {
        "name": "Пиратская треуголка", "type": "equipment", "slot": "head",
        "role": "rat", "rarity": "epic",
        "desc": "+3 к силе. +1 убийство за игру (если Крыса).",
        "effect": {"strength": 3, "extra_kill": 1},
        "icon": "🏴‍☠️", "price": 8000,
        "lore": "Потрёпанная треуголка с выцветшим черепом. Её владелец не знает пощады и всегда готов нанести ещё один удар."
    },
    "flower_crown": {
        "name": "Венок из цветов", "type": "equipment", "slot": "head",
        "role": "all", "rarity": "common",
        "desc": "+1 к ловкости. +1 HP каждый ход в туннелях.",
        "effect": {"agility": 1, "regen": 1},
        "icon": "🌸", "price": 500,
        "lore": "Нежный венок из полевых цветов. Удивительно, но он до сих пор пахнет весной и дарит своему владельцу немного жизненных сил."
    },
    "cowboy_hat": {
        "name": "Ковбойская шляпа", "type": "equipment", "slot": "head",
        "role": "mouse", "rarity": "rare",
        "desc": "+2 к ловкости. Твой голос решающий при ничьей.",
        "effect": {"agility": 2, "tie_breaker": True},
        "icon": "🤠", "price": 2000,
        "lore": "Широкополая кожаная шляпа, видавшая пыль прерий и духоту салунов. Когда мнения расходятся, последнее слово всегда за ковбоем."
    },
    "santa_hat": {
        "name": "Шапка Санты", "type": "equipment", "slot": "head",
        "role": "all", "rarity": "legendary",
        "desc": "+2 ко всем характеристикам. Дарит случайный предмет после каждой победы.",
        "effect": {"strength": 2, "agility": 2, "intelligence": 2, "gift_item": True},
        "icon": "🎅", "price": 25000,
        "lore": "Пушистая красная шапка с белым помпоном. Пахнет мандаринами и волшебством. Побеждая, ты находишь подарки там, где их не должно быть."
    },
    "crown_of_thorns": {
        "name": "Терновый венец", "type": "equipment", "slot": "head",
        "role": "all", "rarity": "mythic",
        "desc": "+5 к силе. -20% опыта, но +50% шанс легендарного предмета.",
        "effect": {"strength": 5, "xp_penalty": 20, "legendary_chance": 50},
        "icon": "👑", "price": 100000,
        "lore": "Венец из колючих ветвей, который больно впивается в лоб. Страдания закаляют дух, и удача поворачивается лицом, испытывая тебя на прочность."
    },
    "beer_hat": {
        "name": "Шляпа с пивом", "type": "equipment", "slot": "head",
        "role": "all", "rarity": "common",
        "desc": "+1 к силе. +1 XP за каждое сообщение в чате.",
        "effect": {"strength": 1, "chat_xp": 1},
        "icon": "🍺", "price": 500,
        "lore": "Дурацкая шляпа с двумя подстаканниками и трубочками. Выглядит нелепо, но с каждым глотком пива приходит мудрость... или её подобие."
    },
    "cheese_wedge_hat": {
        "name": "Шляпа-сырный треугольник", "type": "equipment", "slot": "head",
        "role": "all", "rarity": "common",
        "desc": "+1 ко всем характеристикам. +15 XP за игру.",
        "effect": {"strength": 1, "agility": 1, "intelligence": 1, "bonus_xp": 15},
        "icon": "🧀", "price": 800,
        "lore": "Большой кусок сыра, каким-то чудом держащийся на голове. Пахнет соответственно, но дарит своему владельцу сырную удачу."
    },
    "rat_king_crown_broken": {
        "name": "Сломанная корона Крысиного короля", "type": "equipment", "slot": "head",
        "role": "rat", "rarity": "epic",
        "desc": "+4 к силе. +10 XP за убийство в Мафии.",
        "effect": {"strength": 4, "kill_xp": 10},
        "icon": "👑💔", "price": 9000,
        "lore": "Некогда величественная корона, ныне треснувшая и помятая. Всё ещё хранит отголоски былой власти и жаждет крови."
    },
    "mouse_ears": {
        "name": "Мышиные ушки", "type": "equipment", "slot": "head",
        "role": "all", "rarity": "common",
        "desc": "+2 к ловкости. +5% к уклонению в туннелях.",
        "effect": {"agility": 2, "dodge": 5},
        "icon": "🐭", "price": 400,
        "lore": "Мягкие круглые ушки на ободке. Ты слышишь опасность задолго до её появления и легко уворачиваешься от ударов."
    },
    "rat_ears": {
        "name": "Крысиные уши", "type": "equipment", "slot": "head",
        "role": "all", "rarity": "common",
        "desc": "+2 к силе. +1 к урону в туннелях.",
        "effect": {"strength": 2, "damage": 1},
        "icon": "🐀", "price": 400,
        "lore": "Острые серые уши, пришитые к кожаной повязке. Ты чувствуешь себя более агрессивным и готовым рвать добычу на части."
    },
    "turban": {
        "name": "Тюрбан", "type": "equipment", "slot": "head",
        "role": "mouse", "rarity": "epic",
        "desc": "+4 к интеллекту. Видишь кто Крыса после 3-й ночи.",
        "effect": {"intelligence": 4, "wisdom_reveal": True},
        "icon": "👳", "price": 8500,
        "lore": "Плотно намотанный тюрбан цвета песка. Говорят, он открывает третий глаз и позволяет видеть истинную суть вещей."
    },
    "fedora": {
        "name": "Федора", "type": "equipment", "slot": "head",
        "role": "all", "rarity": "rare",
        "desc": "+2 к интеллекту. +1 к находкам в туннелях.",
        "effect": {"intelligence": 2, "find_chance": 3},
        "icon": "🕵️", "price": 1800,
        "lore": "Классическая фетровая шляпа с лентой. Придаёт загадочный вид и обостряет чутьё на спрятанные ценности."
    },
    "bucket_hat": {
        "name": "Ведро", "type": "equipment", "slot": "head",
        "role": "all", "rarity": "common",
        "desc": "+1 к силе. +5 к максимальному здоровью.",
        "effect": {"strength": 1, "max_health": 5},
        "icon": "🪣", "price": 300,
        "lore": "Обычное жестяное ведро. Немного гремит, немного мешает обзору, но зато защищает голову от случайного кирпича."
    },
    
    # ==================== ОРУЖИЕ (WEAPON) ====================
    "rat_dagger": {
        "name": "Крысиный кинжал", "type": "equipment", "slot": "weapon",
        "role": "rat", "rarity": "rare",
        "desc": "+3 к силе. Можешь убить двух мышей за одну ночь (раз в игру).",
        "effect": {"strength": 3, "double_kill": True},
        "icon": "🗡️", "price": 2500,
        "lore": "Узкий зазубренный клинок, покрытый тёмными пятнами. В умелых лапах способен оборвать две жизни за один выпад."
    },
    "poison_vial": {
        "name": "Склянка с ядом", "type": "equipment", "slot": "weapon",
        "role": "rat", "rarity": "epic",
        "desc": "+2 к интеллекту. Жертва не может говорить следующий день.",
        "effect": {"intelligence": 2, "silence_victim": True},
        "icon": "🧪", "price": 10000,
        "lore": "Маленький пузырёк с зеленоватой жидкостью. Один глоток — и язык прилипает к нёбу, не в силах вымолвить ни слова."
    },
    "magnifying_glass": {
        "name": "Лупа детектива", "type": "equipment", "slot": "weapon",
        "role": "mouse", "rarity": "common",
        "desc": "+1 к интеллекту. Видишь кто за кого голосовал.",
        "effect": {"intelligence": 1, "see_votes": True},
        "icon": "🔍", "price": 600,
        "lore": "Большая лупа в медной оправе. Позволяет разглядеть мельчайшие детали и понять, кто кому пожимал лапу."
    },
    "justice_hammer": {
        "name": "Молот правосудия", "type": "equipment", "slot": "weapon",
        "role": "mouse", "rarity": "legendary",
        "desc": "+5 к силе. При ничьей казнят Крысу.",
        "effect": {"strength": 5, "justice_tie": True},
        "icon": "🔨", "price": 30000,
        "lore": "Тяжёлый судейский молоток, обитый железом. Когда голоса разделяются, он опускается на сторону истины, сокрушая виновного."
    },
    "butcher_knife": {
        "name": "Нож мясника", "type": "equipment", "slot": "weapon",
        "role": "rat", "rarity": "legendary",
        "desc": "+5 к силе. Убийства приносят +10 XP.",
        "effect": {"strength": 5, "kill_xp": 10},
        "icon": "🔪", "price": 30000,
        "lore": "Когда-то этот нож принадлежал старому мяснику из Нижних Туннелей. Говорят, он забил им сотню крыс, прежде чем сам пал от их зубов. Лезвие до сих пор пахнет кровью и железом."
    },
    "crossbow": {
        "name": "Арбалет", "type": "equipment", "slot": "weapon",
        "role": "mouse", "rarity": "epic",
        "desc": "+3 к ловкости. Можешь выстрелить в игрока днём.",
        "effect": {"agility": 3, "day_shot": True},
        "icon": "🏹", "price": 10000,
        "lore": "Компактный арбалет с натянутой тетивой. Один меткий выстрел может решить исход дня, не дожидаясь ночи."
    },
    "scepter_of_truth": {
        "name": "Скипетр истины", "type": "equipment", "slot": "weapon",
        "role": "mouse", "rarity": "legendary",
        "desc": "+4 к интеллекту. Раз в игру можешь узнать роль игрока.",
        "effect": {"intelligence": 4, "reveal_role": True},
        "icon": "🔮", "price": 30000,
        "lore": "Длинный посох с сияющим кристаллом на вершине. Прикоснувшись к цели, он показывает её истинную сущность."
    },
    "shadow_blade": {
        "name": "Клинок тени", "type": "equipment", "slot": "weapon",
        "role": "rat", "rarity": "mythic",
        "desc": "+8 к ловкости. Убийства не оставляют следов.",
        "effect": {"agility": 8, "invisible_kill": True},
        "icon": "🌑", "price": 120000,
        "lore": "Клинок, выкованный из самой темноты. Он не отражает свет и не оставляет ран. Жертва просто исчезает, будто её никогда не было."
    },
    "cheese_sword": {
        "name": "Сырный меч", "type": "equipment", "slot": "weapon",
        "role": "all", "rarity": "common",
        "desc": "+2 к силе. +5% опыта за игру.",
        "effect": {"strength": 2, "xp_boost": 5},
        "icon": "🧀", "price": 600,
        "lore": "Затвердевший кусок сыра, заточенный до состояния клинка. Пахнет аппетитно, но может оставить серьёзную царапину."
    },
    "staff_of_chaos": {
        "name": "Посох хаоса", "type": "equipment", "slot": "weapon",
        "role": "rat", "rarity": "mythic",
        "desc": "+5 к интеллекту. Каждую ночь случайный эффект.",
        "effect": {"intelligence": 5, "chaos_effect": True},
        "icon": "🌀", "price": 120000,
        "lore": "Искривлённый посох, пульсирующий фиолетовой энергией. Никто, даже сам владелец, не знает, что он сотворит следующей ночью."
    },
    "holy_water": {
        "name": "Святая вода", "type": "equipment", "slot": "weapon",
        "role": "all", "rarity": "rare",
        "desc": "+2 к интеллекту. +5 к максимальному здоровью.",
        "effect": {"intelligence": 2, "max_health": 5},
        "icon": "💧", "price": 2500,
        "lore": "Склянка с чистой водой, освящённой в древнем храме. Придаёт сил и очищает разум."
    },
    "boomerang": {
        "name": "Бумеранг", "type": "equipment", "slot": "weapon",
        "role": "all", "rarity": "rare",
        "desc": "+2 к ловкости. Если тебя казнят — казнят и первого голосовавшего.",
        "effect": {"agility": 2, "revenge": True},
        "icon": "🪃", "price": 2500,
        "lore": "Изогнутая деревянная палка, которая всегда возвращается. Запущенное тобой зло вернётся к тому, кто его послал."
    },
    "lucky_coin": {
        "name": "Счастливая монета", "type": "equipment", "slot": "weapon",
        "role": "all", "rarity": "common",
        "desc": "+1 к удаче. +3% к находкам в туннелях.",
        "effect": {"luck": 1, "find_chance": 3},
        "icon": "🪙", "price": 600,
        "lore": "Потёртая монета с дырочкой посередине. Говорят, она приносит удачу тому, кто носит её с собой."
    },
    "mouse_trap_launcher": {
        "name": "Мышеловкомёт", "type": "equipment", "slot": "weapon",
        "role": "mouse", "rarity": "legendary",
        "desc": "+4 к интеллекту. Можешь поставить ловушку на игрока.",
        "effect": {"intelligence": 4, "trap_launcher": True},
        "icon": "🪤🔫", "price": 28000,
        "lore": "Хитроумное устройство, стреляющее мышеловками. Позволяет установить смертельную ловушку прямо под носом у ничего не подозревающей цели."
    },
    "bell_of_awakening": {
        "name": "Колокол пробуждения", "type": "equipment", "slot": "weapon",
        "role": "mouse", "rarity": "rare",
        "desc": "+2 к интеллекту. Разбудить спящего игрока.",
        "effect": {"intelligence": 2, "awaken": True},
        "icon": "🔔", "price": 2300,
        "lore": "Маленький медный колокольчик с чистым звоном. Его звук способен развеять любые чары сна."
    },
    "cheese_slicer": {
        "name": "Сырорезка", "type": "equipment", "slot": "weapon",
        "role": "all", "rarity": "common",
        "desc": "+1 к силе. +3 XP за игру.",
        "effect": {"strength": 1, "bonus_xp": 3},
        "icon": "🔪🧀", "price": 500,
        "lore": "Острая проволочная сырорезка. Режет не только сыр, но и врагов, принося немного опыта."
    },
    "catapult": {
        "name": "Катапульта", "type": "equipment", "slot": "weapon",
        "role": "mouse", "rarity": "epic",
        "desc": "+3 к силе. Можешь запустить игрока — он не голосует.",
        "effect": {"strength": 3, "catapult": True},
        "icon": "🏗️", "price": 8500,
        "lore": "Миниатюрная катапульта, стреляющая небольшими камнями. Попадание в лоб гарантирует, что цель пропустит голосование."
    },
    "net_launcher": {
        "name": "Сеткомёт", "type": "equipment", "slot": "weapon",
        "role": "mouse", "rarity": "rare",
        "desc": "+2 к ловкости. Обездвижить Крысу на одну ночь.",
        "effect": {"agility": 2, "net_trap": True},
        "icon": "🥅", "price": 2600,
        "lore": "Ручное устройство, выстреливающее прочную сеть. Опутывает цель, лишая возможности двигаться."
    },
    
    # ==================== БРОНЯ (ARMOR) ====================
    "leather_vest": {
        "name": "Кожаный жилет", "type": "equipment", "slot": "armor",
        "role": "all", "rarity": "common",
        "desc": "+1 к ловкости. +10 к максимальному здоровью в туннелях.",
        "effect": {"agility": 1, "max_health": 10},
        "icon": "🦺", "price": 650,
        "lore": "Простой жилет из грубой кожи. Пахнет дубильными веществами и немного защищает от ударов."
    },
    "faith_shield": {
        "name": "Щит веры", "type": "equipment", "slot": "armor",
        "role": "mouse", "rarity": "epic",
        "desc": "+2 ко всем характеристикам. Полная защита от одного убийства.",
        "effect": {"strength": 2, "agility": 2, "intelligence": 2, "night_shield": True},
        "icon": "🛡️", "price": 11000,
        "lore": "Сияющий щит, выкованный из чистой веры. Он принимает на себя смертельный удар и рассыпается, спасая жизнь владельца."
    },
    "rat_skin_cloak": {
        "name": "Крысиный плащ", "type": "equipment", "slot": "armor",
        "role": "rat", "rarity": "legendary",
        "desc": "+4 к ловкости. Мыши не видят твою роль при смерти.",
        "effect": {"agility": 4, "hidden_role": True},
        "icon": "🐀", "price": 32000,
        "lore": "Плащ, сшитый из шкур сотни крыс. Он скрывает истинную сущность владельца даже после его гибели."
    },
    "chainmail": {
        "name": "Кольчуга", "type": "equipment", "slot": "armor",
        "role": "all", "rarity": "rare",
        "desc": "+2 к силе. +20 к максимальному здоровью.",
        "effect": {"strength": 2, "max_health": 20},
        "icon": "⛓️", "price": 2600,
        "lore": "Сплетённая из стальных колец рубаха. Тяжёлая, но надёжная защита от клыков и когтей."
    },
    "mirror_armor": {
        "name": "Зеркальная броня", "type": "equipment", "slot": "armor",
        "role": "mouse", "rarity": "legendary",
        "desc": "+3 к интеллекту. Отражает атаку Крысы обратно (раз в игру).",
        "effect": {"intelligence": 3, "reflect_kill": True},
        "icon": "🪞", "price": 32000,
        "lore": "Начищенная до блеска броня, отражающая свет и злые умыслы. Один раз за игру она возвращает атаку отправителю."
    },
    "invisibility_cloak": {
        "name": "Плащ-невидимка", "type": "equipment", "slot": "armor",
        "role": "rat", "rarity": "mythic",
        "desc": "+6 к ловкости. Тебя нельзя выбрать целью голосования.",
        "effect": {"agility": 6, "vote_immune": True},
        "icon": "🎭", "price": 130000,
        "lore": "Серебристый плащ, струящийся как вода. Он скрывает владельца от глаз толпы, и никто не может поднять на него руку."
    },
    "cheese_armor": {
        "name": "Сырная броня", "type": "equipment", "slot": "armor",
        "role": "all", "rarity": "common",
        "desc": "+2 к силе. +5 к максимальному здоровью.",
        "effect": {"strength": 2, "max_health": 5},
        "icon": "🧀", "price": 650,
        "lore": "Панцирь из затвердевшего сыра. Крошится при ударах, но пахнет просто восхитительно."
    },
    "dragon_scale": {
        "name": "Чешуя дракона", "type": "equipment", "slot": "armor",
        "role": "all", "rarity": "legendary",
        "desc": "+3 ко всем характеристикам. Иммунитет к дебаффам.",
        "effect": {"strength": 3, "agility": 3, "intelligence": 3, "debuff_immune": True},
        "icon": "🐉", "price": 32000,
        "lore": "Огромная чешуйка мифического ящера. Она пульсирует теплом и отторгает любые попытки ослабить владельца."
    },
    "angel_robes": {
        "name": "Одеяния ангела", "type": "equipment", "slot": "armor",
        "role": "mouse", "rarity": "mythic",
        "desc": "+5 к интеллекту. После смерти можешь защитить одного игрока.",
        "effect": {"intelligence": 5, "death_protect": True},
        "icon": "👼", "price": 130000,
        "lore": "Белоснежные одежды, сотканные из света. Даже покидая этот мир, владелец может одарить защитой одного из живых."
    },
    "demon_skin": {
        "name": "Шкура демона", "type": "equipment", "slot": "armor",
        "role": "rat", "rarity": "mythic",
        "desc": "+5 к силе. После смерти забираешь одного мыша с собой.",
        "effect": {"strength": 5, "death_kill": True},
        "icon": "👿", "price": 130000,
        "lore": "Красная чешуйчатая шкура, источающая жар. Умирая, владелец тянет за собой в бездну своего убийцу или случайную жертву."
    },
    "turtle_shell": {
        "name": "Черепаший панцирь", "type": "equipment", "slot": "armor",
        "role": "all", "rarity": "rare",
        "desc": "+3 к силе. +25 к максимальному здоровью.",
        "effect": {"strength": 3, "max_health": 25},
        "icon": "🐢", "price": 2600,
        "lore": "Тяжёлый костяной панцирь. Носить его неудобно, но он дарует отличную защиту."
    },
    "gambeson": {
        "name": "Гамбезон", "type": "equipment", "slot": "armor",
        "role": "all", "rarity": "common",
        "desc": "+1 к силе. +15 к максимальному здоровью.",
        "effect": {"strength": 1, "max_health": 15},
        "icon": "🧥", "price": 650,
        "lore": "Стёганая куртка, набитая конским волосом. Смягчает удары и согревает в холодных туннелях."
    },
    "bulletproof_vest": {
        "name": "Бронежилет", "type": "equipment", "slot": "armor",
        "role": "all", "rarity": "epic",
        "desc": "+2 к силе. Защита от выстрела из арбалета.",
        "effect": {"strength": 2, "shot_proof": True},
        "icon": "🔫", "price": 11000,
        "lore": "Современный бронежилет, чудом попавший в Подземное Царство. Останавливает арбалетные болты."
    },
    "cloak_of_rat_emperor": {
        "name": "Плащ Крысиного императора", "type": "equipment", "slot": "armor",
        "role": "rat", "rarity": "mythic",
        "desc": "+6 к силе. Все мыши видят фальшивую роль при твоей смерти.",
        "effect": {"strength": 6, "fake_role": "МЫШЬ"},
        "icon": "🏰", "price": 130000,
        "lore": "Пурпурный плащ, подбитый горностаем. Даже после смерти он скрывает истинную природу владельца, заставляя всех думать, что пал невинный."
    },
    "cloak_of_mouse_god": {
        "name": "Плащ Бога мышей", "type": "equipment", "slot": "armor",
        "role": "mouse", "rarity": "mythic",
        "desc": "+6 к интеллекту. После твоей смерти все узнают кто Крыса.",
        "effect": {"intelligence": 6, "reveal_rat_on_death": True},
        "icon": "⚡", "price": 130000,
        "lore": "Серебристый плащ, расшитый молниями. Гибель владельца озаряет истину, и все узнают, кто был Крысой."
    },
    "bubble_wrap": {
        "name": "Пузырчатая плёнка", "type": "equipment", "slot": "armor",
        "role": "all", "rarity": "common",
        "desc": "+1 к ловкости. +5 к максимальному здоровью, +1 XP.",
        "effect": {"agility": 1, "max_health": 5, "bonus_xp": 1},
        "icon": "📦", "price": 400,
        "lore": "Загадочный материал из другого мира. Приятно лопается и почему-то защищает от ударов."
    },
    
    # ==================== АКСЕССУАРЫ (ACCESSORY) ====================
    "lucky_cheese": {
        "name": "Счастливый сыр", "type": "equipment", "slot": "accessory",
        "role": "all", "rarity": "common",
        "desc": "+1 к удаче. +10 XP за игру.",
        "effect": {"luck": 1, "bonus_xp": 10},
        "icon": "🧀", "price": 550,
        "lore": "Кусочек сыра с дырочкой в форме клевера. Приносит немного удачи и опыта."
    },
    "golden_pocket_watch": {
        "name": "Золотые часы", "type": "equipment", "slot": "accessory",
        "role": "all", "rarity": "rare",
        "desc": "+2 к ловкости. +5 секунд на голосование.",
        "effect": {"agility": 2, "vote_time_bonus": 5},
        "icon": "⌚", "price": 2200,
        "lore": "Старинные часы на цепочке. Их ход замедляется в решающий момент, давая лишние секунды на раздумья."
    },
    "ghost_amulet": {
        "name": "Амулет призрака", "type": "equipment", "slot": "accessory",
        "role": "all", "rarity": "mythic",
        "desc": "+4 к интеллекту. Можешь голосовать после смерти.",
        "effect": {"intelligence": 4, "ghost_vote": True},
        "icon": "👻", "price": 110000,
        "lore": "Полупрозрачный амулет, холодный на ощупь. Даже покинув мир живых, владелец может влиять на исход голосования."
    },
    "rat_tail_ring": {
        "name": "Кольцо из крысиного хвоста", "type": "equipment", "slot": "accessory",
        "role": "rat", "rarity": "epic",
        "desc": "+3 к силе. +1 голос против любой цели.",
        "effect": {"strength": 3, "extra_vote_against": 1},
        "icon": "💍", "price": 8800,
        "lore": "Кольцо, сплетённое из засушенного крысиного хвоста. Усиливает влияние владельца на голосовании."
    },
    "mouse_whisker_ring": {
        "name": "Кольцо из усов мыши", "type": "equipment", "slot": "accessory",
        "role": "mouse", "rarity": "epic",
        "desc": "+3 к ловкости. Твой голос нельзя отменить.",
        "effect": {"agility": 3, "unremovable_vote": True},
        "icon": "💍", "price": 8800,
        "lore": "Тонкое колечко из мышиных усов. Голос владельца звучит твёрдо, и его нельзя заглушить."
    },
    "lucky_rabbit_foot": {
        "name": "Кроличья лапка", "type": "equipment", "slot": "accessory",
        "role": "all", "rarity": "rare",
        "desc": "+2 к удаче. +7% к находкам в туннелях.",
        "effect": {"luck": 2, "find_chance": 7},
        "icon": "🐰", "price": 2200,
        "lore": "Пушистая лапка на верёвочке. Старый добрый талисман на удачу."
    },
    "four_leaf_clover": {
        "name": "Четырёхлистный клевер", "type": "equipment", "slot": "accessory",
        "role": "all", "rarity": "epic",
        "desc": "+3 к удаче. Один раз за игру избежать смерти в туннелях.",
        "effect": {"luck": 3, "avoid_death_once": True},
        "icon": "🍀", "price": 8800,
        "lore": "Засушенный листок клевера с четырьмя лепестками. Один раз он отведёт смертельную опасность."
    },
    "horseshoe": {
        "name": "Подкова", "type": "equipment", "slot": "accessory",
        "role": "all", "rarity": "common",
        "desc": "+1 к удаче. +3% к находкам.",
        "effect": {"luck": 1, "find_chance": 3},
        "icon": "🧲", "price": 550,
        "lore": "Ржавая подкова. Прибить бы её над входом, но носить с собой тоже сойдёт."
    },
    "pearl_necklace": {
        "name": "Жемчужное ожерелье", "type": "equipment", "slot": "accessory",
        "role": "all", "rarity": "rare",
        "desc": "+2 к интеллекту. +10% опыта за победу.",
        "effect": {"intelligence": 2, "win_xp_boost": 10},
        "icon": "📿", "price": 2200,
        "lore": "Нитка речного жемчуга. Придаёт мыслям ясность и увеличивает награду за победу."
    },
    "skull_necklace": {
        "name": "Ожерелье из черепов", "type": "equipment", "slot": "accessory",
        "role": "rat", "rarity": "epic",
        "desc": "+3 к силе. +5 XP за каждое убийство.",
        "effect": {"strength": 3, "kill_xp": 5},
        "icon": "💀", "price": 8800,
        "lore": "Нитка крошечных черепов. Каждый символизирует поверженного врага и дарует толику опыта."
    },
    "wedding_ring": {
        "name": "Обручальное кольцо", "type": "equipment", "slot": "accessory",
        "role": "all", "rarity": "legendary",
        "desc": "+2 ко всем характеристикам. Связывает с другим игроком.",
        "effect": {"strength": 2, "agility": 2, "intelligence": 2, "soulbound": True},
        "icon": "💍", "price": 27500,
        "lore": "Потускневшее золотое кольцо. Связывает судьбы двух существ, и если один уходит, второй следует за ним."
    },
    "compass": {
        "name": "Компас", "type": "equipment", "slot": "accessory",
        "role": "mouse", "rarity": "rare",
        "desc": "+2 к интеллекту. Отслеживает голосование Крысы.",
        "effect": {"intelligence": 2, "track_rat": True},
        "icon": "🧭", "price": 2200,
        "lore": "Старый латунный компас. Его стрелка указывает не на север, а на того, за кого проголосовала Крыса."
    },
    "hourglass": {
        "name": "Песочные часы", "type": "equipment", "slot": "accessory",
        "role": "all", "rarity": "epic",
        "desc": "+2 к интеллекту. +10 секунд ко всем фазам.",
        "effect": {"intelligence": 2, "time_bonus": 10},
        "icon": "⏳", "price": 8800,
        "lore": "Миниатюрные песочные часы. Время вокруг владельца течёт чуть медленнее."
    },
    "monocle": {
        "name": "Монокль", "type": "equipment", "slot": "accessory",
        "role": "all", "rarity": "common",
        "desc": "+1 к интеллекту. +2% к точности.",
        "effect": {"intelligence": 1, "all_accuracy": 2},
        "icon": "🧐", "price": 550,
        "lore": "Стеклянная линза в золотой оправе. Помогает лучше видеть детали и целиться."
    },
    "spy_earpiece": {
        "name": "Шпионский наушник", "type": "equipment", "slot": "accessory",
        "role": "mouse", "rarity": "rare",
        "desc": "+2 к интеллекту. Слышишь выбор Крысы ночью.",
        "effect": {"intelligence": 2, "hear_rat": True},
        "icon": "🎧", "price": 2200,
        "lore": "Крошечный наушник, улавливающий шёпот теней. Позволяет подслушать, кого Крыса выбрала жертвой."
    },
    "pocket_mirror": {
        "name": "Карманное зеркальце", "type": "equipment", "slot": "accessory",
        "role": "all", "rarity": "rare",
        "desc": "+2 к интеллекту. Отражает проклятия.",
        "effect": {"intelligence": 2, "curse_reflect": True},
        "icon": "🪞", "price": 2200,
        "lore": "Маленькое зеркальце в серебряной оправе. Отражает направленные на владельца проклятия обратно."
    },
    "locket": {
        "name": "Медальон", "type": "equipment", "slot": "accessory",
        "role": "all", "rarity": "epic",
        "desc": "+2 ко всем характеристикам. +1 жизнь (раз в 5 игр).",
        "effect": {"strength": 2, "agility": 2, "intelligence": 2, "extra_life": 1},
        "icon": "📿", "price": 8800,
        "lore": "Золотой медальон с портретом неизвестной дамы. Раз в несколько игр он дарует владельцу второй шанс."
    },
    "rat_king_medallion": {
        "name": "Медальон Крысиного короля", "type": "equipment", "slot": "accessory",
        "role": "rat", "rarity": "legendary",
        "desc": "+4 к силе. Все мыши видят тебя как Мышь до первого убийства.",
        "effect": {"strength": 4, "disguise_until_kill": True},
        "icon": "🏅", "price": 27000,
        "lore": "Тяжёлый медальон с изображением крысиной головы. Пока не прольётся первая кровь, все видят в тебе невинную Мышь."
    },
    "ring_of_regeneration": {
        "name": "Кольцо регенерации", "type": "equipment", "slot": "accessory",
        "role": "all", "rarity": "rare",
        "desc": "+1 к ловкости. +5 HP/час к лечению.",
        "effect": {"agility": 1, "regen": 5},
        "icon": "💍", "price": 3000,
        "lore": "Тёплое золотое кольцо. Пульсирует в такт сердцебиению."
    },
    "amulet_of_health": {
        "name": "Амулет здоровья", "type": "equipment", "slot": "accessory",
        "role": "all", "rarity": "epic",
        "desc": "+10 HP/час к лечению.",
        "effect": {"regen": 10},
        "icon": "📿", "price": 8000,
        "lore": "Древний амулет с руной жизни. Его тепло ускоряет заживление ран."
    },
    "stinky_sock": {
        "name": "Вонючий носок", "type": "equipment", "slot": "accessory",
        "role": "all", "rarity": "common",
        "desc": "+1 к ловкости. Отпугивает всех.",
        "effect": {"agility": 1},
        "icon": "🧦", "price": 300,
        "lore": "Старый носок, который не стирали месяцами. Воняет так, что даже враги предпочитают держаться подальше."
    },
    "rubber_duck": {
        "name": "Резиновая уточка", "type": "equipment", "slot": "accessory",
        "role": "all", "rarity": "common",
        "desc": "+1 к удаче. Кря!",
        "effect": {"luck": 1},
        "icon": "🦆", "price": 250,
        "lore": "Жёлтая резиновая уточка. Если сжать её в трудную минуту, она издаст ободряющее «Кря!»."
    },
}

# ========== СУНДУКИ (открываются и дают случайный предмет) ==========
CHESTS = {
    "common_chest": {
        "name": "Обычный сундук", "type": "chest", "rarity": "common",
        "desc": "Открыть: случайный обычный предмет",
        "icon": "📦", "drop_rarity": "common", "price": 500,
        "lore": "Простой деревянный сундук, сколоченный из старых досок. Что внутри? Скорее всего, что-то полезное, но не выдающееся."
    },
    "rare_chest": {
        "name": "Редкий сундук", "type": "chest", "rarity": "rare",
        "desc": "Открыть: случайный редкий предмет",
        "icon": "🔵", "drop_rarity": "rare", "price": 2000,
        "lore": "Сундук из тёмного дуба, окованный железом. Внутри определённо лежит что-то ценное."
    },
    "epic_chest": {
        "name": "Эпический сундук", "type": "chest", "rarity": "epic",
        "desc": "Открыть: случайный эпический предмет",
        "icon": "🟣", "drop_rarity": "epic", "price": 8000,
        "lore": "Сундук, украшенный серебряными узорами. От него исходит слабое сияние. Внутри скрыта настоящая сила."
    },
    "legendary_chest": {
        "name": "Легендарный сундук", "type": "chest", "rarity": "legendary",
        "desc": "Открыть: случайный легендарный предмет",
        "icon": "🟡", "drop_rarity": "legendary", "price": 25000,
        "lore": "Золотой сундук, усыпанный драгоценными камнями. Он хранит в себе артефакт, достойный саг и легенд."
    },
    "mythic_chest": {
        "name": "Мифический сундук", "type": "chest", "rarity": "mythic",
        "desc": "Открыть: случайный мифический предмет",
        "icon": "🔴", "drop_rarity": "mythic", "price": 100000,
        "lore": "Сундук, словно сотканный из звёздного света. Говорят, в таких хранятся предметы, способные изменить саму реальность."
    },
    "rat_chest": {
        "name": "Крысиный сундук", "type": "chest", "rarity": "epic",
        "desc": "Открыть: случайный предмет для Крысы (эпик+)",
        "icon": "🐀📦", "drop_rarity": "epic", "role_filter": "rat", "price": 10000,
        "lore": "Тёмный сундук, обтянутый крысиной шкурой. Внутри лежит нечто, что пригодится только тому, кто привык прятаться во тьме."
    },
    "mouse_chest": {
        "name": "Мышиный сундук", "type": "chest", "rarity": "epic",
        "desc": "Открыть: случайный предмет для Мыши (эпик+)",
        "icon": "🐭📦", "drop_rarity": "epic", "role_filter": "mouse", "price": 10000,
        "lore": "Светлый сундук, украшенный колосьями. Внутри хранится подарок для тех, кто сражается за правое дело."
    },
    "cheese_chest": {
        "name": "Сырный сундук", "type": "chest", "rarity": "legendary",
        "desc": "Открыть: 3-5 случайных сырных предметов",
        "icon": "🧀📦", "drop_rarity": "legendary", "special": "multiple_cheese", "price": 35000,
        "lore": "Сундук, целиком сделанный из затвердевшего сыра. Пахнет просто божественно, и внутри наверняка не один кусочек."
    },
}
# ========== РЕЦЕПТЫ КРАФТА (выпадают с мобов, можно хранить в инвентаре) ==========
RECIPES = {
    "recipe_cheese_sword": {
        "name": "Рецепт: Сырный меч", "type": "recipe", "rarity": "common",
        "desc": "Открывает крафт Сырного меча",
        "icon": "📜", "price": 500,
        "result_item": "cheese_sword",
        "materials": {"cheese_crust": 3, "rat_incisor": 2, "iron_gear": 1},
        "lore": "Потрёпанный пергамент с рецептом. Сырный меч — классика, с которой начинают все крысы."
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
}

# ========== РАСХОДНИКИ (используются один раз во время игры) ==========
CONSUMABLES = {
    "rat_tail_soup": {
        "name": "Суп из крысиного хвоста", "type": "consumable", "role": "all", "rarity": "common",
        "desc": "Тёплый, но сомнительный бульон. +15 XP",
        "effect": "xp_boost", "value": 15, "icon": "🍲", "price": 150,
        "lore": "Миска мутного бульона, в котором плавает что-то тонкое и розовое. На вкус... ну, говорят, полезно."
    },
    "poison_cheese": {
        "name": "Ядовитый сыр", "type": "consumable", "role": "rat", "rarity": "common",
        "desc": "Использовать ночью: жертва умрёт не сразу, а после дня",
        "effect": "delayed_kill", "icon": "🧀", "price": 300,
        "lore": "Аппетитный кусочек сыра с зеленоватым отливом. Смерть от него наступает не сразу, что даёт убийце время замести следы."
    },
    "smoke_bomb": {
        "name": "Дымовая бомба", "type": "consumable", "role": "rat", "rarity": "rare",
        "desc": "Использовать ночью: отменить голосование следующего дня",
        "effect": "skip_voting", "icon": "💨", "price": 1200,
        "lore": "Небольшой глиняный шарик. При броске испускает облако густого дыма, срывая планы на день."
    },
    "truth_serum": {
        "name": "Сыворотка правды", "type": "consumable", "role": "mouse", "rarity": "epic",
        "desc": "Использовать днём: узнать точную роль выбранного игрока",
        "effect": "reveal_role", "icon": "💉", "price": 5000,
        "lore": "Шприц с прозрачной жидкостью. После укола язык развязывается, и тайное становится явным."
    },
    "resurrection_cookie": {
        "name": "Печенье воскрешения", "type": "consumable", "role": "all", "rarity": "legendary",
        "desc": "Использовать в любой момент: воскресить мёртвого игрока",
        "effect": "resurrect", "icon": "🍪", "price": 15000,
        "lore": "Золотистое печенье с крошечными искорками. Один укус — и жизнь возвращается в бездыханное тело."
    },
    "lucky_ticket": {
        "name": "Билет удачи", "type": "consumable", "role": "all", "rarity": "common",
        "desc": "Использовать сразу: +100 XP", "effect": "xp_boost", "value": 100, "icon": "🎫", "price": 300,
        "lore": "Мятый лотерейный билетик. Сотри защитный слой — может, повезёт?"
    },
    "energy_drink": {
        "name": "Энергетик", "type": "consumable", "role": "all", "rarity": "common",
        "desc": "Использовать днём: +10 секунд на обсуждение",
        "effect": "day_time_boost", "value": 10, "icon": "🥤", "price": 300,
        "lore": "Банка с яркой этикеткой. Обещает бодрость на целый день, но даёт лишь десять секунд."
    },
    "night_vision_goggles": {
        "name": "Очки ночного видения", "type": "consumable", "role": "mouse", "rarity": "rare",
        "desc": "Использовать ночью: увидеть кто был целью Крысы",
        "effect": "see_rat_target", "icon": "🥽", "price": 1200,
        "lore": "Громоздкие очки с зелёными линзами. Позволяют разглядеть во тьме, кого выбрала Крыса."
    },
    "rat_repellent": {
        "name": "Крысоловка", "type": "consumable", "role": "mouse", "rarity": "epic",
        "desc": "Использовать ночью: если Крыса выберет тебя — она умрёт вместо тебя",
        "effect": "trap_rat", "icon": "🪤", "price": 5000,
        "lore": "Большая пружинная ловушка. Если Крыса сунется к тебе этой ночью, она сильно пожалеет."
    },
    "double_cheese": {
        "name": "Двойной сыр", "type": "consumable", "role": "all", "rarity": "rare",
        "desc": "Использовать сразу: x2 опыт за следующую игру",
        "effect": "double_xp_next_game", "icon": "🧀🧀", "price": 1200,
        "lore": "Два куска сыра, склеенных вместе. Говорят, приносят двойную удачу."
    },
    "lucky_charm": {
        "name": "Талисман удачи", "type": "consumable", "role": "all", "rarity": "legendary",
        "desc": "Использовать перед игрой: 100% шанс получить легендарный предмет при победе",
        "effect": "guaranteed_legendary", "icon": "🍀", "price": 15000,
        "lore": "Крошечный золотой кулон в форме подковы. С ним победа пахнет не только триумфом, но и легендарной добычей."
    },
    "echo_scroll": {
        "name": "Свиток эха", "type": "consumable", "role": "all", "rarity": "mythic",
        "desc": "Использовать после смерти: отправить одно сообщение живым",
        "effect": "dead_message", "icon": "📜", "price": 60000,
        "lore": "Древний пергамент, исписанный рунами. Даже мёртвый, ты можешь прошептать последнее слово."
    },
    "rat_whistle": {
        "name": "Крысиный свисток", "type": "consumable", "role": "rat", "rarity": "legendary",
        "desc": "Использовать ночью: следующей ночью можешь убить двоих",
        "effect": "next_night_double", "icon": "🪈", "price": 15000,
        "lore": "Свисток, вырезанный из бедренной кости. Его звук призывает саму суть Крысы, даруя силу для двойного удара."
    },
    "mouse_trap": {
        "name": "Мышеловка", "type": "consumable", "role": "mouse", "rarity": "mythic",
        "desc": "Использовать днём: если цель — Крыса, она мгновенно умирает. Если нет — умираешь ты.",
        "effect": "russian_roulette", "icon": "🪤", "price": 60000,
        "lore": "Огромная деревянная мышеловка со стальной пружиной. Или ты, или она. Ставки сделаны."
    },
    "mirror_shard": {
        "name": "Осколок зеркала", "type": "consumable", "role": "mouse", "rarity": "rare",
        "desc": "Использовать ночью: отразить атаку Крысы обратно на неё",
        "effect": "reflect_kill", "icon": "🪞", "price": 1200,
        "lore": "Острый осколок старого зеркала. Отражает не только свет, но и злые намерения."
    },
    "soul_candy": {
        "name": "Конфета душ", "type": "consumable", "role": "all", "rarity": "epic",
        "desc": "Использовать сразу: +1 уровень", "effect": "level_up", "icon": "🍬", "price": 5000,
        "lore": "Полупрозрачная конфета, светящаяся изнутри. Съешь её — и почувствуешь прилив невероятной силы."
    },
    "invisibility_potion": {
        "name": "Зелье невидимости", "type": "consumable", "role": "all", "rarity": "legendary",
        "desc": "Использовать ночью: тебя нельзя выбрать целью этой ночью",
        "effect": "night_invisible", "icon": "🧪", "price": 15000,
        "lore": "Пузырёк с мерцающей жидкостью. Один глоток — и ты растворишься в тенях, недоступный для чужих глаз."
    },
    "love_potion": {
        "name": "Любовное зелье", "type": "consumable", "role": "all", "rarity": "rare",
        "desc": "Использовать днём: два игрока не могут голосовать друг против друга",
        "effect": "love_bond", "icon": "💕", "price": 1200,
        "lore": "Розовая жидкость с ароматом роз. Связывает двоих узами симпатии, мешая им голосовать друг против друга."
    },
    "berserk_potion": {
        "name": "Зелье берсерка", "type": "consumable", "role": "rat", "rarity": "epic",
        "desc": "Использовать ночью: убиваешь двоих, но твоя роль раскрывается на день",
        "effect": "berserk_kill", "icon": "😤", "price": 5000,
        "lore": "Тёмно-красное зелье, пахнущее железом. Дарует ярость и силу, но срывает маску."
    },
    "holy_water_consumable": {
        "name": "Святая вода", "type": "consumable", "role": "mouse", "rarity": "rare",
        "desc": "Использовать на мёртвого: узнать был ли он Крысой",
        "effect": "check_dead", "icon": "💧", "price": 1200,
        "lore": "Маленький пузырёк с освящённой водой. Окропи ею тело, и истина откроется."
    },
    "sleeping_powder": {
        "name": "Сонный порошок", "type": "consumable", "role": "rat", "rarity": "common",
        "desc": "Использовать ночью: жертва просыпает голосование",
        "effect": "sleep_victim", "icon": "😴", "price": 300,
        "lore": "Щепотка мелкого серого порошка. Попадая в нос, вызывает непреодолимую сонливость."
    },
    "coffee": {
        "name": "Кофе", "type": "consumable", "role": "all", "rarity": "common",
        "desc": "Использовать днём: +5 секунд к обсуждению для всех",
        "effect": "global_day_boost", "value": 5, "icon": "☕", "price": 300,
        "lore": "Чашка горячего чёрного кофе. Бодрит всех вокруг, даря лишние секунды на разговоры."
    },
    "cheese_wheel": {
        "name": "Колесо сыра", "type": "consumable", "role": "all", "rarity": "rare",
        "desc": "Использовать сразу: +50 XP", "effect": "restore_xp", "value": 50, "icon": "🧀", "price": 1200,
        "lore": "Небольшое колесо выдержанного сыра. Очень сытное и питательное."
    },
    "golden_cheese": {
        "name": "Золотой сыр", "type": "consumable", "role": "all", "rarity": "legendary",
        "desc": "Использовать сразу: +500 XP и случайный предмет",
        "effect": "jackpot", "icon": "🏆", "price": 15000,
        "lore": "Сыр, отливающий чистым золотом. Вкус непередаваем, а удача, которую он приносит, просто невероятна."
    },
    "cursed_doll": {
        "name": "Проклятая кукла", "type": "consumable", "role": "rat", "rarity": "mythic",
        "desc": "Использовать на игрока: он умирает через 2 хода",
        "effect": "curse_death", "icon": "🪆", "price": 60000,
        "lore": "Тряпичная кукла с булавками. Вонзи булавку в сердце, и цель обречена, хоть и не сразу."
    },
    "angel_feather": {
        "name": "Перо ангела", "type": "consumable", "role": "mouse", "rarity": "mythic",
        "desc": "Использовать на убитого: воскресить его",
        "effect": "resurrect", "icon": "🪶", "price": 60000,
        "lore": "Белоснежное перо, излучающее тепло. Прикоснись им к павшему товарищу, и он снова встанет в строй."
    },
    "beer": {
        "name": "Кружка пива", "type": "consumable", "role": "all", "rarity": "common",
        "desc": "Выпить в таверне: случайный временный эффект на 1 час",
        "effect": "beer_buff", "icon": "🍺", "price": 50,
        "lore": "Пенная кружка прохладного пива. Что может быть лучше после тяжёлого дня? Эффект непредсказуем, но всегда приятен."
    },
    "cheese_bomb": {
        "name": "Сырная бомба", "type": "consumable", "role": "all", "rarity": "rare",
        "desc": "Использовать днём: случайный игрок теряет голос",
        "effect": "random_silence", "icon": "🧀💣", "price": 1500,
        "lore": "Шарик из сыра с торчащим фитилём. Взрывается без шума, но лишает кого-то права голоса."
    },
    "rat_tracker": {
        "name": "Крысиный трекер", "type": "consumable", "role": "mouse", "rarity": "epic",
        "desc": "Использовать на игрока: узнаешь его передвижения",
        "effect": "track_player", "icon": "📡", "price": 6000,
        "lore": "Небольшой приборчик с антенной. Позволяет отследить, куда ходил игрок этой ночью."
    },
    "cheese_cake_slice": {
        "name": "Кусочек чизкейка", "type": "consumable", "role": "all", "rarity": "common",
        "desc": "Вкуснятина! +25 XP", "effect": "xp_boost", "value": 25, "icon": "🍰", "price": 200,
        "lore": "Нежный кусочек чизкейка. Тает во рту и дарит немного радости и опыта."
    },
    "rat_poison_antidote": {
        "name": "Противоядие от крысиного яда", "type": "consumable", "role": "mouse", "rarity": "rare",
        "desc": "Снимает эффект яда с игрока", "effect": "cure_poison", "icon": "💊", "price": 1300,
        "lore": "Таблетка с горьким вкусом. Нейтрализует действие крысиного яда."
    },
    "squeaky_toy": {
        "name": "Пищалка", "type": "consumable", "role": "mouse", "rarity": "common",
        "desc": "Отвлечь Крысу. Она не может убить тебя эту ночь",
        "effect": "distract_rat", "icon": "🧸", "price": 400,
        "lore": "Резиновая игрушка, издающая громкий писк. Крысы терпеть не могут этот звук и предпочтут уйти подальше."
    },
    "rat_call": {
        "name": "Крысиный зов", "type": "consumable", "role": "rat", "rarity": "epic",
        "desc": "Призвать ещё одну Крысу на одну ночь", "effect": "summon_rat", "icon": "📯", "price": 7000,
        "lore": "Рог, издающий ультразвуковой сигнал. Призывает подмогу из глубин туннелей."
    },
    "cheese_fondue": {
        "name": "Сырное фондю", "type": "consumable", "role": "all", "rarity": "rare",
        "desc": "Поделиться с командой. Все Мыши получают +10 XP",
        "effect": "team_xp_boost", "value": 10, "icon": "🫕", "price": 1800,
        "lore": "Горшочек с расплавленным сыром. Стоит поделиться с соратниками, и всем становится немного лучше."
    },
    "mouse_whistle": {
        "name": "Мышиный свисток", "type": "consumable", "role": "mouse", "rarity": "rare",
        "desc": "Позвать на помощь. +1 голос на этом голосовании",
        "effect": "extra_vote", "icon": "🪈🐭", "price": 1400,
        "lore": "Серебряный свисток. Его звук придаёт твоему голосу больший вес."
    },
    "rat_trap_blueprint": {
        "name": "Чертёж крысоловки", "type": "consumable", "role": "mouse", "rarity": "legendary",
        "desc": "Установить идеальную ловушку. Крыса гарантированно умрёт если выберет тебя",
        "effect": "perfect_trap", "icon": "📐", "price": 18000,
        "lore": "Пожелтевший чертёж с детальными схемами. Следуя ему, можно соорудить ловушку, из которой не вырваться."
    },
    "rat_mask": {
        "name": "Маска крысы", "type": "consumable", "role": "mouse", "rarity": "epic",
        "desc": "Притвориться Крысой. На один день твоя роль показывается как КРЫСА",
        "effect": "fake_rat_role", "icon": "🎭🐀", "price": 5500,
        "lore": "Уродливая маска с оскаленной мордой. Надень её, и все примут тебя за того, кем ты не являешься."
    },
    "mouse_mask": {
        "name": "Маска мыши", "type": "consumable", "role": "rat", "rarity": "epic",
        "desc": "Притвориться Мышью. На один день твоя роль показывается как МЫШЬ",
        "effect": "fake_mouse_role", "icon": "🎭🐭", "price": 5500,
        "lore": "Милая маска с ушками и усами. Идеально для того, чтобы затеряться в толпе."
    },
    "rat_king_decree": {
        "name": "Указ Крысиного короля", "type": "consumable", "role": "rat", "rarity": "mythic",
        "desc": "Отменить результаты голосования этого дня",
        "effect": "cancel_voting", "icon": "📜👑", "price": 55000,
        "lore": "Свиток с королевской печатью. Один росчерк пера — и решение толпы теряет силу."
    },
    "mouse_rebellion_flag": {
        "name": "Флаг мышиного восстания", "type": "consumable", "role": "mouse", "rarity": "legendary",
        "desc": "Все Мыши получают +1 голос на этом голосовании",
        "effect": "rebellion_buff", "icon": "🚩", "price": 20000,
        "lore": "Красное полотнище с изображением сыра. Подними его, и сердца Мышей наполнятся отвагой."
    },
    "lucky_cheese_cube": {
        "name": "Кубик удачного сыра", "type": "consumable", "role": "all", "rarity": "legendary",
        "desc": "+100% удача на одну игру", "effect": "max_luck", "icon": "🎲🧀", "price": 16000,
        "lore": "Идеально ровный кубик сыра. Говорят, он приносит абсолютную удачу своему владельцу на одну игру."
    },
    "time_sand": {
        "name": "Песок времени", "type": "consumable", "role": "all", "rarity": "mythic",
        "desc": "Перемотка времени. Вернуть игру на одну фазу назад",
        "effect": "time_rewind", "icon": "⌛", "price": 70000,
        "lore": "Щепотка серебристого песка. Брось его, и время отступит на шаг назад, давая шанс всё исправить."
    },
}

# ========== ДОБАВЛЯЕМ РЕЦЕПТЫ К ПРЕДМЕТАМ ==========
EQUIPMENT["cheese_sword"]["craftable"] = True
EQUIPMENT["cheese_sword"]["craft_materials"] = {"cheese_crust": 3, "rat_incisor": 2, "iron_gear": 1}

EQUIPMENT["rat_dagger"]["craftable"] = True
EQUIPMENT["rat_dagger"]["craft_materials"] = {"steel_shard": 2, "rat_incisor": 4, "rat_poison": 1}
EQUIPMENT["rat_dagger"]["craft_blueprint"] = "blueprint_poison_blade"

EQUIPMENT["viking_helmet"]["craftable"] = True
EQUIPMENT["viking_helmet"]["craft_materials"] = {"iron_gear": 4, "rat_pelt": 2, "bronze_alloy": 1}

EQUIPMENT["leather_vest"]["craftable"] = True
EQUIPMENT["leather_vest"]["craft_materials"] = {"rat_pelt": 5, "linen_scrap": 2, "mouse_bone": 1}

EQUIPMENT["gambeson"]["craftable"] = True
EQUIPMENT["gambeson"]["craft_materials"] = {"linen_scrap": 4, "rat_pelt": 3, "wool_clump": 2}

EQUIPMENT["chainmail"]["craftable"] = True
EQUIPMENT["chainmail"]["craft_materials"] = {"iron_gear": 6, "bronze_alloy": 2, "leather_scrap": 2}

EQUIPMENT["crossbow"]["craftable"] = True
EQUIPMENT["crossbow"]["craft_materials"] = {"bronze_alloy": 3, "bat_membrane": 2, "iron_gear": 2}

EQUIPMENT["butcher_knife"]["craftable"] = True
EQUIPMENT["butcher_knife"]["craft_materials"] = {"steel_shard": 3, "rat_king_eye": 1, "obsidian_scale": 2, "mithril_nugget": 1}

EQUIPMENT["invisibility_cloak"]["craftable"] = True
EQUIPMENT["invisibility_cloak"]["craft_materials"] = {"moon_silk": 3, "void_essence": 1, "spider_silk": 2, "bat_membrane": 1}
EQUIPMENT["invisibility_cloak"]["craft_blueprint"] = "blueprint_invisibility_cloak"

EQUIPMENT["crown_of_rat_king"]["craftable"] = True
EQUIPMENT["crown_of_rat_king"]["craft_materials"] = {"rat_god_tooth": 1, "adamantite": 1, "first_rat_skull": 1}
EQUIPMENT["crown_of_rat_king"]["craft_blueprint"] = "blueprint_crown"

EQUIPMENT["crown_of_mouse_king"]["craftable"] = True
EQUIPMENT["crown_of_mouse_king"]["craft_materials"] = {"star_silk": 1, "mithril_nugget": 3, "phoenix_ember": 1}
EQUIPMENT["crown_of_mouse_king"]["craft_blueprint"] = "blueprint_crown"

CONSUMABLES["poison_cheese"]["craftable"] = True
CONSUMABLES["poison_cheese"]["craft_materials"] = {"cheese_crust": 2, "rat_poison": 2, "basement_mushroom": 1}

CONSUMABLES["smoke_bomb"]["craftable"] = True
CONSUMABLES["smoke_bomb"]["craft_materials"] = {"wall_soot": 3, "cheese_crust": 1, "empty_vial": 1}

# ========== НОВОЕ ОРУЖИЕ (ТУННЕЛИ) ==========
NEW_WEAPONS = {
    # ===== МЕЧИ =====
    "rusty_sword": {
        "name": "Ржавый меч", "type": "equipment", "slot": "weapon",
        "role": "all", "rarity": "common",
        "desc": "+2 к силе. Базовое оружие.",
        "effect": {"strength": 2},
        "icon": "🗡️", "price": 300,
        "lore": "Покрытый ржавчиной клинок, найденный в старом сундуке. Ещё послужит.",
        "craftable": True,
        "craft_materials": {"iron_gear": 3, "copper_scrap": 2, "stone_shard": 2}
    },
    "iron_blade": {
        "name": "Железный клинок", "type": "equipment", "slot": "weapon",
        "role": "all", "rarity": "common",
        "desc": "+3 к силе.",
        "effect": {"strength": 3},
        "icon": "⚔️", "price": 600,
        "lore": "Простой, но надёжный меч. Верный спутник начинающего искателя приключений.",
        "craftable": True,
        "craft_materials": {"iron_gear": 5, "bronze_alloy": 2, "leather_scrap": 1}
    },
    "steel_sword": {
        "name": "Стальной меч", "type": "equipment", "slot": "weapon",
        "role": "all", "rarity": "rare",
        "desc": "+5 к силе. +1 к минимальному урону.",
        "effect": {"strength": 5, "min_damage": 1},
        "icon": "🗡️", "price": 3000,
        "lore": "Клинок из закалённой стали. Хороший баланс между весом и остротой.",
        "craftable": True,
        "craft_materials": {"steel_shard": 4, "bronze_alloy": 3, "iron_gear": 2}
    },
    "mithril_sword": {
        "name": "Мифриловый меч", "type": "equipment", "slot": "weapon",
        "role": "all", "rarity": "epic",
        "desc": "+8 к силе. Светится в темноте.",
        "effect": {"strength": 8},
        "icon": "✨", "price": 15000,
        "lore": "Лёгкий клинок из мифрила. Сияет голубоватым светом в присутствии опасности.",
        "craftable": True,
        "craft_materials": {"mithril_nugget": 3, "silver_ingot": 2, "fairy_dust": 1}
    },
    "shadow_blade_sword": {
        "name": "Клинок Теней", "type": "equipment", "slot": "weapon",
        "role": "rat", "rarity": "epic",
        "desc": "+6 к ловкости. +10% шанс критического удара.",
        "effect": {"agility": 6, "crit_chance": 10},
        "icon": "🌑", "price": 18000,
        "lore": "Клинок, выкованный в абсолютной темноте. Не отражает свет.",
        "craftable": True,
        "craft_materials": {"obsidian_scale": 4, "steel_shard": 3, "bat_fang": 2}
    },
    "cheese_blade": {
        "name": "Сырной клинок", "type": "equipment", "slot": "weapon",
        "role": "all", "rarity": "rare",
        "desc": "+4 к силе. +5% опыта за бой.",
        "effect": {"strength": 4, "xp_boost": 5},
        "icon": "🧀", "price": 4000,
        "lore": "Затвердевший пармезан, заточенный до бритвенной остроты. Пахнет божественно.",
        "craftable": True,
        "craft_materials": {"cheese_crust": 8, "iron_gear": 2, "honey_drop": 1}
    },
    "rat_catcher_sword": {
        "name": "Меч Крысолова", "type": "equipment", "slot": "weapon",
        "role": "mouse", "rarity": "legendary",
        "desc": "+10 к силе. +25% урона против крыс и грызунов.",
        "effect": {"strength": 10, "rat_damage_bonus": 25},
        "icon": "⚔️🐀", "price": 40000,
        "lore": "Прославленный меч легендарного Крысолова. Поёт, когда рядом враг.",
        "craftable": True,
        "craft_materials": {"mithril_nugget": 5, "rat_king_eye": 2, "obsidian_scale": 3}
    },
    "king_blade": {
        "name": "Клинок Короля", "type": "equipment", "slot": "weapon",
        "role": "all", "rarity": "legendary",
        "desc": "+12 к силе. +15% к максимальному здоровью.",
        "effect": {"strength": 12, "max_health_percent": 15},
        "icon": "👑", "price": 50000,
        "lore": "Меч, достойный монарха. Его владелец чувствует прилив королевской мощи.",
        "craftable": True,
        "craft_materials": {"adamantite": 2, "mithril_nugget": 4, "star_silk": 1}
    },
    "divine_sword": {
        "name": "Божественный меч", "type": "equipment", "slot": "weapon",
        "role": "mouse", "rarity": "mythic",
        "desc": "+18 к силе. Святой урон — игнорирует защиту нежити.",
        "effect": {"strength": 18, "holy_damage": True},
        "icon": "⚡", "price": 150000,
        "lore": "Клинок, благословлённый самим Мышиным Богом. Разит нежить без пощады.",
        "craftable": True,
        "craft_materials": {"spark_creation": 1, "mithril_nugget": 6, "phoenix_ember": 2}
    },
    "first_hero_sword": {
        "name": "Меч Первого героя", "type": "equipment", "slot": "weapon",
        "role": "all", "rarity": "mythic",
        "desc": "+22 к силе. +20% ко всем характеристикам.",
        "effect": {"strength": 22, "all_stats_percent": 20},
        "icon": "🏆", "price": 200000,
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
        "icon": "🦴", "price": 200,
        "lore": "Грубо обтёсанная кость. Лучше, чем ничего.",
        "craftable": True,
        "craft_materials": {"mouse_bone": 5, "rat_incisor": 2, "stone_shard": 1}
    },
    "jagged_dagger": {
        "name": "Зазубренный кинжал", "type": "equipment", "slot": "weapon",
        "role": "all", "rarity": "common",
        "desc": "+2 к ловкости. Кровотечение — 2 урона на 2 хода (шанс 15%).",
        "effect": {"agility": 2, "bleed_chance": 15},
        "icon": "🗡️", "price": 500,
        "lore": "Лезвие с зубцами. Оставляет рваные раны.",
        "craftable": True,
        "craft_materials": {"iron_gear": 3, "rat_incisor": 4, "copper_scrap": 2}
    },
    "poison_stiletto": {
        "name": "Отравленный стилет", "type": "equipment", "slot": "weapon",
        "role": "rat", "rarity": "rare",
        "desc": "+4 к ловкости. Яд — 3 урона/ход на 3 хода (шанс 20%).",
        "effect": {"agility": 4, "poison_chance": 20},
        "icon": "🧪", "price": 5000,
        "lore": "Тонкое лезвие, смазанное ядом. Один укол — и враг обречён.",
        "craftable": True,
        "craft_materials": {"steel_shard": 3, "rat_poison": 3, "empty_vial": 2}
    },
    "shadow_dagger": {
        "name": "Теневой клинок", "type": "equipment", "slot": "weapon",
        "role": "rat", "rarity": "epic",
        "desc": "+7 к ловкости. +15% шанс двойного удара.",
        "effect": {"agility": 7, "double_hit_chance": 15},
        "icon": "🌑", "price": 16000,
        "lore": "Кинжал, скрытый от глаз. Бьёт дважды, прежде чем жертва поймёт.",
        "craftable": True,
        "craft_materials": {"obsidian_scale": 3, "bat_membrane": 2, "spider_silk": 2}
    },
    "assassin_dagger": {
        "name": "Кинжал ассасина", "type": "equipment", "slot": "weapon",
        "role": "rat", "rarity": "epic",
        "desc": "+8 к ловкости. +20% урона при атаке со спины.",
        "effect": {"agility": 8, "backstab_bonus": 20},
        "icon": "🔪", "price": 20000,
        "lore": "Изогнутый клинок профессионального убийцы. Смертелен в умелых лапах.",
        "craftable": True,
        "craft_materials": {"steel_shard": 5, "bat_fang": 3, "rat_poison": 2}
    },
    "blood_dagger": {
        "name": "Кровавый кинжал", "type": "equipment", "slot": "weapon",
        "role": "rat", "rarity": "legendary",
        "desc": "+10 к ловкости. Вампиризм — восстанавливает 30% урона.",
        "effect": {"agility": 10, "vampirism": 30},
        "icon": "🩸", "price": 45000,
        "lore": "Красное лезвие, которое пьёт кровь врага, отдавая силу владельцу.",
        "craftable": True,
        "craft_materials": {"mithril_nugget": 4, "bat_fang": 5, "rat_king_eye": 2}
    },
    "death_whisper": {
        "name": "Шёпот смерти", "type": "equipment", "slot": "weapon",
        "role": "rat", "rarity": "legendary",
        "desc": "+12 к ловкости. Бесшумное убийство — жертва не кричит.",
        "effect": {"agility": 12, "silent_kill": True},
        "icon": "💀", "price": 55000,
        "lore": "Кинжал, который убивает в полной тишине. Никто не услышит предсмертный писк.",
        "craftable": True,
        "craft_materials": {"obsidian_scale": 5, "bat_membrane": 4, "void_essence": 1}
    },
    "demon_fang": {
        "name": "Клык демона", "type": "equipment", "slot": "weapon",
        "role": "rat", "rarity": "mythic",
        "desc": "+16 к ловкости. +25% шанс двойного удара. Вампиризм 50%.",
        "effect": {"agility": 16, "double_hit_chance": 25, "vampirism": 50},
        "icon": "👿", "price": 160000,
        "lore": "Кинжал, вырванный из пасти демона. Живёт своей жизнью и жаждет крови.",
        "craftable": True,
        "craft_materials": {"spark_creation": 1, "obsidian_scale": 6, "first_rat_skull": 1}
    },
    "soul_reaper": {
        "name": "Душегуб", "type": "equipment", "slot": "weapon",
        "role": "rat", "rarity": "mythic",
        "desc": "+18 к ловкости. Убийство даёт +50% опыта.",
        "effect": {"agility": 18, "kill_xp_bonus": 50},
        "icon": "⚰️", "price": 180000,
        "lore": "Клинок, пожирающий души. Каждая смерть делает владельца сильнее.",
        "craftable": True,
        "craft_materials": {"spark_creation": 2, "labyrinth_heart": 1, "rat_god_tooth": 1}
    },
    "last_breath": {
        "name": "Последний вздох", "type": "equipment", "slot": "weapon",
        "role": "all", "rarity": "mythic",
        "desc": "+20 к ловкости. При HP < 20%: +50% урона и вампиризм 100%.",
        "effect": {"agility": 20, "desperation_bonus": 50, "desperation_vampirism": 100},
        "icon": "💨", "price": 200000,
        "lore": "На грани смерти этот кинжал раскрывает истинную мощь. Последний шанс или верная смерть.",
        "craftable": True,
        "craft_materials": {"spark_creation": 3, "labyrinth_heart": 2, "void_essence": 2}
    },

    # ===== РАПИРА (единственная) =====
    "rapier": {
        "name": "Рапира", "type": "equipment", "slot": "weapon",
        "role": "all", "rarity": "mythic",
        "desc": "+25 к силе. Огромный урон! Но 8% шанс пораниться при атаке (3 урона себе).",
        "effect": {"strength": 25, "self_damage_chance": 8, "self_damage": 3},
        "icon": "⚔️✨", "price": 250000,
        "lore": "Элегантная и смертоносная рапира из звёздного металла. Настолько острая, что иногда ранит владельца.",
        "craftable": True,
        "craft_materials": {"spark_creation": 5, "adamantite": 4, "labyrinth_heart": 2}
    },
}

# ========== КАМНИ ДЛЯ ИНКРУСТАЦИИ ОРУЖИЯ ==========
ENCHANT_GEMS = {
    "gem_emerald": {
        "name": "Изумруд", "type": "gem", "rarity": "rare",
        "desc": "Ядовитый камень. При атаке: отравляет врага (3 урона/ход, 3 хода).",
        "effect": {"poison": 3, "poison_duration": 3},
        "icon": "🟢", "price": 3000,
        "lore": "Зелёный камень, пахнущий миндалём. Смертельно опасен в умелых лапах."
    },
    "gem_ruby": {
        "name": "Рубин", "type": "gem", "rarity": "rare",
        "desc": "Огненный камень. При атаке: +5 к урону (шанс 15%).",
        "effect": {"fire_damage": 5},
        "icon": "🔴", "price": 3500,
        "lore": "Кроваво-красный камень, тёплый на ощупь. Хранит в себе жар подземного пламени."
    },
    "gem_sapphire": {
        "name": "Сапфир", "type": "gem", "rarity": "epic",
        "desc": "Ледяной камень. При атаке: замораживает врага на 1 ход (шанс 10%).",
        "effect": {"freeze": 1},
        "icon": "🔵", "price": 8000,
        "lore": "Синий как глубина океана. Его холод способен остановить даже самого быстрого врага."
    },
    "gem_topaz": {
        "name": "Топаз", "type": "gem", "rarity": "epic",
        "desc": "Камень стана. При атаке: оглушает врага на 1 ход (шанс 8%).",
        "effect": {"stun": 1},
        "icon": "🟡", "price": 9000,
        "lore": "Золотистый камень, искрящийся статическим электричеством. Парализует прикосновением."
    },
    "gem_amethyst": {
        "name": "Аметист", "type": "gem", "rarity": "epic",
        "desc": "Магический камень. При атаке: игнорирует защиту врага (шанс 12%).",
        "effect": {"ignore_defense": True},
        "icon": "🟣", "price": 10000,
        "lore": "Фиолетовый кристалл, пульсирующий магической энергией. Пробивает любую броню."
    },
    "gem_diamond": {
        "name": "Алмаз", "type": "gem", "rarity": "epic",
        "desc": "Камень кровотечения. При атаке: 2 урона/ход на 4 хода (шанс 18%).",
        "effect": {"bleed": 2, "bleed_duration": 4},
        "icon": "⚪", "price": 7500,
        "lore": "Чистейший алмаз, острый как бритва. Оставляет долго незаживающие раны."
    },
    "gem_onyx": {
        "name": "Оникс", "type": "gem", "rarity": "legendary",
        "desc": "Камень вампиризма. При атаке: восстанавливает 50% урона (шанс 15%).",
        "effect": {"vampirism": 50},
        "icon": "🟤", "price": 25000,
        "lore": "Чёрный камень, впитывающий жизненную силу. Отдаёт её владельцу."
    },
    "gem_citrine": {
        "name": "Цитрин", "type": "gem", "rarity": "legendary",
        "desc": "Камень скорости. При атаке: двойной удар (шанс 5%).",
        "effect": {"double_hit": True},
        "icon": "🟠", "price": 30000,
        "lore": "Оранжевый камень, ускоряющий движения. В бою каждая секунда на счету."
    },
    "gem_obsidian": {
        "name": "Обсидиан", "type": "gem", "rarity": "legendary",
        "desc": "Камень проклятия. При атаке: снижает урон врага на 2 на 2 хода (шанс 10%).",
        "effect": {"weaken": 2, "weaken_duration": 2},
        "icon": "⚫", "price": 28000,
        "lore": "Вулканическое стекло, пропитанное древним проклятием. Ослабляет того, кого коснётся."
    },
    "gem_moonstone": {
        "name": "Лунный камень", "type": "gem", "rarity": "mythic",
        "desc": "Камень хаоса. При атаке: случайный эффект из всех возможных (шанс 25%).",
        "effect": {"random_effect": True},
        "icon": "🔮", "price": 80000,
        "lore": "Переливающийся камень, рождённый из лунного света. Никто не знает, что он сотворит в следующее мгновение."
    },
}

# ========== СВИТКИ ЗАТОЧКИ ==========
ENCHANT_SCROLLS = {
    "enchant_scroll_weapon": {
        "name": "Свиток заточки оружия", "type": "scroll", "rarity": "rare",
        "desc": "Заточить оружие: +1 уровень. При неудаче с +4 вещь может сломаться.",
        "effect": "enchant_weapon",
        "icon": "📜⚔️", "price": 5000,
        "lore": "Древний пергамент с рунами усиления. Кузнецы молятся перед его использованием."
    },
    "enchant_scroll_armor": {
        "name": "Свиток заточки брони", "type": "scroll", "rarity": "rare",
        "desc": "Заточить броню: +1 уровень. При неудаче с +4 вещь может сломаться.",
        "effect": "enchant_armor",
        "icon": "📜🛡️", "price": 4000,
        "lore": "Пергамент, пропитанный защитной магией. Делает броню прочнее."
    },
    "blessed_scroll_weapon": {
        "name": "Благословенный свиток оружия", "type": "scroll", "rarity": "epic",
        "desc": "Заточить оружие: +1 уровень. При неудаче сброс на 0, но вещь цела.",
        "effect": "enchant_weapon_blessed",
        "icon": "📜✨", "price": 25000,
        "lore": "Свиток, освящённый жрецами Мышиного Бога. Даже при неудаче оружие остаётся целым."
    },
    "blessed_scroll_armor": {
        "name": "Благословенный свиток брони", "type": "scroll", "rarity": "epic",
        "desc": "Заточить броню: +1 уровень. При неудаче сброс на 0, но вещь цела.",
        "effect": "enchant_armor_blessed",
        "icon": "📜✨", "price": 20000,
        "lore": "Свиток, окроплённый святой водой. Броня не ломается, даже если заточка не удалась."
    },
    "crystal_scroll_weapon": {
        "name": "Кристальный свиток оружия", "type": "scroll", "rarity": "legendary",
        "desc": "Заточить оружие: +1 уровень. Повышенный шанс успеха (x1.5).",
        "effect": "enchant_weapon_crystal",
        "icon": "📜💎", "price": 50000,
        "lore": "Свиток, инкрустированный кристальной пылью. Шанс успешной заточки значительно выше."
    },
    "crystal_scroll_armor": {
        "name": "Кристальный свиток брони", "type": "scroll", "rarity": "legendary",
        "desc": "Заточить броню: +1 уровень. Повышенный шанс успеха (x1.5).",
        "effect": "enchant_armor_crystal",
        "icon": "📜💎", "price": 45000,
        "lore": "Свиток, сверкающий как алмаз. Даже опытные кузнецы ценят его."
    },
}

# ========== НОВЫЕ РЕЦЕПТЫ ДЛЯ ОРУЖИЯ ==========
NEW_RECIPES = {
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
}
# ========== БРОНЯ ПО КЛАССАМ ==========
CLASS_ARMORS = {
    # ===== БРОНЯ ТАНКА (высокая защита, +HP, -ловкость) =====
    "iron_plate": {
        "name": "Железный нагрудник", "type": "equipment", "slot": "armor",
        "role": "all", "rarity": "common",
        "desc": "+3 к силе. +25 HP. -1 к ловкости. Тяжёлая броня.",
        "effect": {"strength": 3, "max_health": 25, "agility": -1},
        "icon": "🛡️", "price": 800,
        "lore": "Толстая железная пластина. Неповоротливо, но надёжно.",
        "craftable": True,
        "craft_materials": {"iron_gear": 8, "bronze_alloy": 3, "leather_scrap": 2}
    },
    "steel_cuirass": {
        "name": "Стальная кираса", "type": "equipment", "slot": "armor",
        "role": "all", "rarity": "rare",
        "desc": "+5 к силе. +40 HP. -2 к ловкости.",
        "effect": {"strength": 5, "max_health": 40, "agility": -2},
        "icon": "🛡️", "price": 5000,
        "lore": "Цельный стальной панцирь. Выдерживает прямой удар меча.",
        "craftable": True,
        "craft_materials": {"steel_shard": 6, "iron_gear": 4, "bronze_alloy": 3}
    },
    "mithril_plate": {
        "name": "Мифриловая броня", "type": "equipment", "slot": "armor",
        "role": "all", "rarity": "epic",
        "desc": "+8 к силе. +60 HP. Нет штрафа к ловкости.",
        "effect": {"strength": 8, "max_health": 60},
        "icon": "✨🛡️", "price": 20000,
        "lore": "Лёгкая как перо, прочная как сталь. Мечта любого танка.",
        "craftable": True,
        "craft_materials": {"mithril_nugget": 5, "steel_shard": 4, "fairy_dust": 2}
    },
    "titan_armor": {
        "name": "Броня титана", "type": "equipment", "slot": "armor",
        "role": "all", "rarity": "legendary",
        "desc": "+12 к силе. +100 HP. Входящий урон -3.",
        "effect": {"strength": 12, "max_health": 100, "damage_reduction": 3},
        "icon": "🏰", "price": 60000,
        "lore": "Броня, выкованная из сердца горы. Почти непробиваема.",
        "craftable": True,
        "craft_materials": {"adamantite": 3, "mithril_nugget": 5, "magnetic_stone": 2}
    },
    "aegis_divine": {
        "name": "Эгида божественная", "type": "equipment", "slot": "armor",
        "role": "all", "rarity": "mythic",
        "desc": "+20 к силе. +200 HP. Входящий урон -5. Иммунитет к оглушению.",
        "effect": {"strength": 20, "max_health": 200, "damage_reduction": 5, "stun_immune": True},
        "icon": "⚡🛡️", "price": 200000,
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
        "icon": "🦺", "price": 600,
        "lore": "Кожа, усиленная железными вставками. Для тех, кто предпочитает атаку.",
        "craftable": True,
        "craft_materials": {"rat_pelt": 6, "iron_gear": 3, "leather_scrap": 3}
    },
    "berserker_harness": {
        "name": "Упряжь берсерка", "type": "equipment", "slot": "armor",
        "role": "all", "rarity": "rare",
        "desc": "+4 к силе. +2 к урону. -5 HP.",
        "effect": {"strength": 4, "damage": 2, "max_health": -5},
        "icon": "😤", "price": 4000,
        "lore": "Минимум защиты, максимум ярости. Для тех, кто не боится умереть.",
        "craftable": True,
        "craft_materials": {"steel_shard": 4, "rat_pelt": 5, "bronze_alloy": 2}
    },
    "war_chainmail": {
        "name": "Боевая кольчуга", "type": "equipment", "slot": "armor",
        "role": "all", "rarity": "epic",
        "desc": "+7 к силе. +3 к урону. +25 HP.",
        "effect": {"strength": 7, "damage": 3, "max_health": 25},
        "icon": "⛓️", "price": 18000,
        "lore": "Кольчуга, закалённая в драконьем пламени. Для настоящих воинов.",
        "craftable": True,
        "craft_materials": {"steel_shard": 6, "mithril_nugget": 2, "iron_gear": 4}
    },
    "dragon_leather": {
        "name": "Драконья шкура", "type": "equipment", "slot": "armor",
        "role": "all", "rarity": "legendary",
        "desc": "+10 к силе. +5 к урону. +40 HP. +10% шанс крита.",
        "effect": {"strength": 10, "damage": 5, "max_health": 40, "crit_chance": 10},
        "icon": "🐉", "price": 65000,
        "lore": "Шкура легендарного ящера. Пропитана огнём и яростью.",
        "craftable": True,
        "craft_materials": {"obsidian_scale": 5, "steel_shard": 5, "phoenix_ember": 2}
    },
    "ragnarok_armor": {
        "name": "Броня Рагнарёка", "type": "equipment", "slot": "armor",
        "role": "all", "rarity": "mythic",
        "desc": "+18 к силе. +8 к урону. +60 HP. +20% шанс крита.",
        "effect": {"strength": 18, "damage": 8, "max_health": 60, "crit_chance": 20},
        "icon": "🌋", "price": 220000,
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
        "icon": "👘", "price": 500,
        "lore": "Простая тканевая роба. Пахнет старыми книгами и свечным воском.",
        "craftable": True,
        "craft_materials": {"linen_scrap": 5, "wool_clump": 3, "candle_stub": 2}
    },
    "sorcerer_robe": {
        "name": "Мантия чародея", "type": "equipment", "slot": "armor",
        "role": "all", "rarity": "rare",
        "desc": "+4 к интеллекту. +10% к магическому урону. +1 реген маны.",
        "effect": {"intelligence": 4, "magic_damage": 10, "mana_regen": 1},
        "icon": "🧙", "price": 4500,
        "lore": "Мантия, расшитая магическими рунами. Искрит при ходьбе.",
        "craftable": True,
        "craft_materials": {"spider_silk": 4, "fairy_dust": 2, "cloudy_crystal": 2}
    },
    "archmage_robe": {
        "name": "Одеяние архимага", "type": "equipment", "slot": "armor",
        "role": "all", "rarity": "epic",
        "desc": "+7 к интеллекту. +15% к магическому урону. +2 реген маны. +10 HP.",
        "effect": {"intelligence": 7, "magic_damage": 15, "mana_regen": 2, "max_health": 10},
        "icon": "🔮", "price": 22000,
        "lore": "Одеяние, пропитанное чистой магией. Владелец чувствует потоки силы.",
        "craftable": True,
        "craft_materials": {"moon_silk": 3, "fairy_dust": 4, "mage_blood": 1}
    },
    "void_weave_robe": {
        "name": "Мантия Пустоты", "type": "equipment", "slot": "armor",
        "role": "all", "rarity": "legendary",
        "desc": "+12 к интеллекту. +25% к магическому урону. +3 реген маны. Иммунитет к сайленсу.",
        "effect": {"intelligence": 12, "magic_damage": 25, "mana_regen": 3, "silence_immune": True},
        "icon": "🌌", "price": 70000,
        "lore": "Соткана из самой ткани мироздания. Между нитями видна бесконечность.",
        "craftable": True,
        "craft_materials": {"void_essence": 2, "star_silk": 3, "ancient_scrap": 2}
    },
    "omniscient_shroud": {
        "name": "Покров Всезнания", "type": "equipment", "slot": "armor",
        "role": "all", "rarity": "mythic",
        "desc": "+20 к интеллекту. +40% к магическому урону. +5 реген маны. Все заклинания усилены.",
        "effect": {"intelligence": 20, "magic_damage": 40, "mana_regen": 5, "all_spells_boost": True},
        "icon": "🌟", "price": 250000,
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
        "icon": "🕵️", "price": 500,
        "lore": "Лёгкий жилет с множеством карманов для краденого.",
        "craftable": True,
        "craft_materials": {"leather_scrap": 5, "linen_scrap": 3, "rat_pelt": 2}
    },
    "shadow_leather": {
        "name": "Теневая кожа", "type": "equipment", "slot": "armor",
        "role": "rat", "rarity": "rare",
        "desc": "+4 к ловкости. +10% к уклонению. +10 HP. Бесшумное движение.",
        "effect": {"agility": 4, "dodge": 10, "max_health": 10, "silent_move": True},
        "icon": "🌑", "price": 4500,
        "lore": "Кожаный доспех, выкрашенный в цвет ночи. Шагов не слышно.",
        "craftable": True,
        "craft_materials": {"bat_membrane": 3, "spider_silk": 3, "obsidian_scale": 2}
    },
    "ninja_gi": {
        "name": "Одеяние ниндзя", "type": "equipment", "slot": "armor",
        "role": "rat", "rarity": "epic",
        "desc": "+7 к ловкости. +15% к уклонению. +15 HP. +10% шанс двойного удара.",
        "effect": {"agility": 7, "dodge": 15, "max_health": 15, "double_hit_chance": 10},
        "icon": "🥷", "price": 20000,
        "lore": "Чёрное одеяние, позволяющее двигаться быстрее ветра.",
        "craftable": True,
        "craft_materials": {"spider_silk": 5, "bat_membrane": 4, "snake_skin": 3}
    },
    "phantom_mantle": {
        "name": "Плащ фантома", "type": "equipment", "slot": "armor",
        "role": "rat", "rarity": "legendary",
        "desc": "+12 к ловкости. +20% к уклонению. +25 HP. Невидимость на 1 ход при HP < 30%.",
        "effect": {"agility": 12, "dodge": 20, "max_health": 25, "emergency_invis": True},
        "icon": "👻", "price": 65000,
        "lore": "Плащ, сотканный из душ умерших воров. Исчезает в момент опасности.",
        "craftable": True,
        "craft_materials": {"moon_silk": 4, "bat_membrane": 5, "void_essence": 1}
    },
    "nightstalker_garb": {
        "name": "Одеяние Ночного Охотника", "type": "equipment", "slot": "armor",
        "role": "rat", "rarity": "mythic",
        "desc": "+20 к ловкости. +30% к уклонению. +40 HP. Все удары из невидимости — критические.",
        "effect": {"agility": 20, "dodge": 30, "max_health": 40, "stealth_crit": True},
        "icon": "🦇", "price": 230000,
        "lore": "Одеяние легендарного убийцы. Никто не видел его владельца живым.",
        "craftable": True,
        "craft_materials": {"spark_creation": 4, "void_essence": 3, "star_silk": 3}
    },
}

# ========== РЕЦЕПТЫ КЛАССОВОЙ БРОНИ ==========
CLASS_ARMOR_RECIPES = {
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
# ========== ОБНОВЛЕНИЕ ОРУЖИЯ — ДОБАВЛЯЕМ УРОН ==========
# Мечи — базовый урон + сила
WEAPON_DAMAGE.update({
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
    # Кинжалы — меньше урон, но быстрее
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
    # Рапира — огромный урон
    "rapier": {"min_damage": 18, "max_damage": 35},
    # Старое оружие
    "cheese_sword": {"min_damage": 2, "max_damage": 5},
    "rat_dagger": {"min_damage": 3, "max_damage": 7},
    "butcher_knife": {"min_damage": 8, "max_damage": 16},
    "crossbow": {"min_damage": 5, "max_damage": 10},
})

# ========== ЛУКИ ДЛЯ ЛУЧНИКА ==========
NEW_BOWS = {
    "wooden_bow": {
        "name": "Деревянный лук", "type": "equipment", "slot": "weapon",
        "role": "all", "rarity": "common",
        "desc": "+2 к ловкости. Дальний бой.",
        "effect": {"agility": 2},
        "icon": "🏹", "price": 400,
        "lore": "Простой лук из ветки вяза. С чего-то надо начинать.",
        "craftable": True,
        "craft_materials": {"pigeon_feather": 3, "mouse_bone": 2, "spider_web": 2}
    },
    "hunter_bow": {
        "name": "Лук охотника", "type": "equipment", "slot": "weapon",
        "role": "all", "rarity": "common",
        "desc": "+3 к ловкости. +1 к минимальному урону.",
        "effect": {"agility": 3, "min_damage": 1},
        "icon": "🏹", "price": 700,
        "lore": "Надёжный лук для охоты на мелкую дичь.",
        "craftable": True,
        "craft_materials": {"pigeon_feather": 5, "rat_pelt": 3, "bronze_alloy": 1}
    },
    "composite_bow": {
        "name": "Композитный лук", "type": "equipment", "slot": "weapon",
        "role": "all", "rarity": "rare",
        "desc": "+5 к ловкости. +2 к минимальному урону. +5% к точности.",
        "effect": {"agility": 5, "min_damage": 2, "accuracy": 5},
        "icon": "🏹", "price": 4000,
        "lore": "Лук из рога и сухожилий. Бьёт дальше и точнее.",
        "craftable": True,
        "craft_materials": {"bronze_alloy": 4, "leather_scrap": 3, "rat_tail_vertebra": 2}
    },
    "elven_bow": {
        "name": "Эльфийский лук", "type": "equipment", "slot": "weapon",
        "role": "mouse", "rarity": "epic",
        "desc": "+8 к ловкости. +3 к минимальному урону. +10% к точности.",
        "effect": {"agility": 8, "min_damage": 3, "accuracy": 10},
        "icon": "🧝🏹", "price": 18000,
        "lore": "Изящный лук, созданный древними эльфами. Поёт при натяжении тетивы.",
        "craftable": True,
        "craft_materials": {"mithril_nugget": 2, "spider_silk": 4, "fairy_dust": 3}
    },
    "crossbow_repeating": {
        "name": "Многозарядный арбалет", "type": "equipment", "slot": "weapon",
        "role": "mouse", "rarity": "epic",
        "desc": "+6 к ловкости. Атакует дважды за ход (шанс 30%).",
        "effect": {"agility": 6, "double_hit_chance": 30},
        "icon": "🏹🔄", "price": 22000,
        "lore": "Арбалет с барабанным механизмом. Выпускает две стрелы разом.",
        "craftable": True,
        "craft_materials": {"steel_shard": 5, "bronze_alloy": 4, "iron_gear": 3}
    },
    "longbow_of_truth": {
        "name": "Длинный лук Истины", "type": "equipment", "slot": "weapon",
        "role": "mouse", "rarity": "legendary",
        "desc": "+12 к ловкости. +5 к минимальному урону. +15% к точности. Игнорирует уклонение.",
        "effect": {"agility": 12, "min_damage": 5, "accuracy": 15, "ignore_dodge": True},
        "icon": "🎯", "price": 55000,
        "lore": "Лук, который никогда не промахивается. Стрела всегда находит цель.",
        "craftable": True,
        "craft_materials": {"mithril_nugget": 5, "moon_silk": 3, "rat_king_eye": 2}
    },
    "storm_bow": {
        "name": "Лук Бури", "type": "equipment", "slot": "weapon",
        "role": "mouse", "rarity": "legendary",
        "desc": "+15 к ловкости. Молния — +8 урона (шанс 15%).",
        "effect": {"agility": 15, "lightning_damage": 8},
        "icon": "⚡🏹", "price": 60000,
        "lore": "Лук, вырезанный из дерева, в которое ударила молния. Искрит в руках.",
        "craftable": True,
        "craft_materials": {"mithril_nugget": 4, "storm_spark": 2, "phoenix_ember": 2}
    },
    "phoenix_bow": {
        "name": "Лук Феникса", "type": "equipment", "slot": "weapon",
        "role": "mouse", "rarity": "mythic",
        "desc": "+18 к ловкости. Огненные стрелы — +12 урона огнём (шанс 20%).",
        "effect": {"agility": 18, "fire_damage": 12},
        "icon": "🔥🏹", "price": 180000,
        "lore": "Лук, пылающий вечным огнём. Стрелы загораются в полёте.",
        "craftable": True,
        "craft_materials": {"spark_creation": 2, "phoenix_ember": 4, "star_silk": 2}
    },
    "void_bow": {
        "name": "Лук Бездны", "type": "equipment", "slot": "weapon",
        "role": "rat", "rarity": "mythic",
        "desc": "+16 к ловкости. Теневые стрелы — игнорируют броню.",
        "effect": {"agility": 16, "ignore_defense": True},
        "icon": "🌑🏹", "price": 190000,
        "lore": "Лук из самой темноты. Его стрелы проходят сквозь любую защиту.",
        "craftable": True,
        "craft_materials": {"void_essence": 3, "obsidian_scale": 5, "spark_creation": 2}
    },
    "celestial_longbow": {
        "name": "Небесный длинный лук", "type": "equipment", "slot": "weapon",
        "role": "mouse", "rarity": "mythic",
        "desc": "+22 к ловкости. +8 к минимальному урону. +25% к точности. Звёздный дождь — атакует 3 раза (шанс 10%).",
        "effect": {"agility": 22, "min_damage": 8, "accuracy": 25, "triple_hit_chance": 10},
        "icon": "🌟🏹", "price": 250000,
        "lore": "Лук, сотканный из звёздного света. Выпускает целый град стрел.",
        "craftable": True,
        "craft_materials": {"spark_creation": 5, "star_silk": 4, "labyrinth_heart": 2}
    },
}

# ========== УРОН ЛУКОВ ==========
WEAPON_DAMAGE.update({
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
})

# ========== РЕЦЕПТЫ ЛУКОВ ==========
NEW_BOW_RECIPES = {
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
}
# ========== ВСЕ ПРЕДМЕТЫ ==========
ALL_ITEMS = {**RESOURCES, **EQUIPMENT, **NEW_WEAPONS, **NEW_BOWS, **CLASS_ARMORS, **ENCHANT_GEMS, **ENCHANT_SCROLLS, **CONSUMABLES, **CHESTS, **RECIPES, **NEW_RECIPES, **NEW_BOW_RECIPES, **CLASS_ARMOR_RECIPES}

# ========== ШАНСЫ ВЫПАДЕНИЯ ==========
DROP_CHANCES = {
    "common": 45,
    "rare": 30,
    "epic": 15,
    "legendary": 7,
    "mythic": 3,
}

# ========== СЛОТЫ ЭКИПИРОВКИ ==========
EQUIPMENT_SLOTS = {
    "head": "Голова",
    "weapon": "Оружие",
    "armor": "Броня",
    "accessory": "Аксессуар",
}

# ========== ФУНКЦИИ КРАФТА ==========
def get_craft_recipe(item_id: str) -> dict:
    """Возвращает рецепт крафта для предмета"""
    item = ALL_ITEMS.get(item_id, {})
    if not item or not item.get("craftable"):
        return None
    return {
        "rarity": item.get("rarity", "common"),
        "materials": item.get("craft_materials", {}),
        "blueprint_required": item.get("craft_blueprint"),
    }


# ========== ФУНКЦИИ КРАФТА (замени старые на эти) ==========

def get_available_recipes(user_id: int) -> list:
    """Возвращает список ID рецептов которые игрок может использовать (рецепт есть в инвентаре + хватает материалов)"""
    resources = get_player_resources(user_id)
    available = []
    
    for recipe_id, recipe in RECIPES.items():
        # Проверяем, есть ли у игрока этот рецепт
        if resources.get(recipe_id, 0) < 1:
            continue
        
        # Проверяем, хватает ли материалов
        can_craft = True
        for mat_id, qty in recipe["materials"].items():
            if resources.get(mat_id, 0) < qty:
                can_craft = False
                break
        
        if can_craft:
            available.append(recipe_id)
    
    return available


def get_craft_recipe(recipe_id: str) -> dict:
    """Возвращает рецепт крафта по ID рецепта"""
    recipe = RECIPES.get(recipe_id)
    if not recipe:
        return None
    return {
        "result_item": recipe.get("result_item"),
        "materials": recipe.get("materials", {}),
        "rarity": recipe.get("rarity", "common"),
    }


def get_all_recipes() -> dict:
    """Возвращает все рецепты (для выпадения с мобов)"""
    return RECIPES