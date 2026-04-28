"""Ресурсы Ратляндии — металлы, ткани, кости, алхимия, провизия, чертежи, коллекционные, магические, прочее"""

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