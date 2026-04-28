"""Расходники — зелья, еда, бомбы, свитки (одноразовые)"""

CONSUMABLES = {
    "rat_tail_soup": {
        "name": "Суп из крысиного хвоста", "type": "consumable", "role": "all", "rarity": "common",
        "desc": "Тёплый, но сомнительный бульон. +15 XP",
        "effect": "xp_boost", "value": 15, "icon": "🍲", "price": 150,
        "lore": "Миска мутного бульона, в котором плавает что-то тонкое и розовое."
    },
    "poison_cheese": {
        "name": "Ядовитый сыр", "type": "consumable", "role": "rat", "rarity": "common",
        "desc": "Использовать ночью: жертва умрёт не сразу, а после дня",
        "effect": "delayed_kill", "icon": "🧀", "price": 300,
        "craftable": True,
        "craft_materials": {"cheese_crust": 2, "rat_poison": 2, "basement_mushroom": 1},
        "lore": "Аппетитный кусочек сыра с зеленоватым отливом."
    },
    "smoke_bomb": {
        "name": "Дымовая бомба", "type": "consumable", "role": "rat", "rarity": "rare",
        "desc": "Использовать ночью: отменить голосование следующего дня",
        "effect": "skip_voting", "icon": "💨", "price": 1200,
        "craftable": True,
        "craft_materials": {"wall_soot": 3, "cheese_crust": 1, "empty_vial": 1},
        "lore": "Небольшой глиняный шарик. При броске испускает облако густого дыма."
    },
    "truth_serum": {
        "name": "Сыворотка правды", "type": "consumable", "role": "mouse", "rarity": "epic",
        "desc": "Использовать днём: узнать точную роль выбранного игрока",
        "effect": "reveal_role", "icon": "💉", "price": 5000,
        "lore": "Шприц с прозрачной жидкостью. После укола язык развязывается."
    },
    "resurrection_cookie": {
        "name": "Печенье воскрешения", "type": "consumable", "role": "all", "rarity": "legendary",
        "desc": "Использовать в любой момент: воскресить мёртвого игрока",
        "effect": "resurrect", "icon": "🍪", "price": 15000,
        "lore": "Золотистое печенье с крошечными искорками."
    },
    "lucky_ticket": {
        "name": "Билет удачи", "type": "consumable", "role": "all", "rarity": "common",
        "desc": "Использовать сразу: +100 XP", "effect": "xp_boost", "value": 100, "icon": "🎫", "price": 300,
        "lore": "Мятый лотерейный билетик."
    },
    "energy_drink": {
        "name": "Энергетик", "type": "consumable", "role": "all", "rarity": "common",
        "desc": "Использовать днём: +10 секунд на обсуждение",
        "effect": "day_time_boost", "value": 10, "icon": "🥤", "price": 300,
        "lore": "Банка с яркой этикеткой."
    },
    "night_vision_goggles": {
        "name": "Очки ночного видения", "type": "consumable", "role": "mouse", "rarity": "rare",
        "desc": "Использовать ночью: увидеть кто был целью Крысы",
        "effect": "see_rat_target", "icon": "🥽", "price": 1200,
        "lore": "Громоздкие очки с зелёными линзами."
    },
    "rat_repellent": {
        "name": "Крысоловка", "type": "consumable", "role": "mouse", "rarity": "epic",
        "desc": "Использовать ночью: если Крыса выберет тебя — она умрёт вместо тебя",
        "effect": "trap_rat", "icon": "🪤", "price": 5000,
        "lore": "Большая пружинная ловушка."
    },
    "double_cheese": {
        "name": "Двойной сыр", "type": "consumable", "role": "all", "rarity": "rare",
        "desc": "Использовать сразу: x2 опыт за следующую игру",
        "effect": "double_xp_next_game", "icon": "🧀🧀", "price": 1200,
        "lore": "Два куска сыра, склеенных вместе."
    },
    "lucky_charm": {
        "name": "Талисман удачи", "type": "consumable", "role": "all", "rarity": "legendary",
        "desc": "Использовать перед игрой: 100% шанс получить легендарный предмет при победе",
        "effect": "guaranteed_legendary", "icon": "🍀", "price": 15000,
        "lore": "Крошечный золотой кулон в форме подковы."
    },
    "echo_scroll": {
        "name": "Свиток эха", "type": "consumable", "role": "all", "rarity": "mythic",
        "desc": "Использовать после смерти: отправить одно сообщение живым",
        "effect": "dead_message", "icon": "📜", "price": 60000,
        "lore": "Древний пергамент, исписанный рунами."
    },
    "rat_whistle": {
        "name": "Крысиный свисток", "type": "consumable", "role": "rat", "rarity": "legendary",
        "desc": "Использовать ночью: следующей ночью можешь убить двоих",
        "effect": "next_night_double", "icon": "🪈", "price": 15000,
        "lore": "Свисток, вырезанный из бедренной кости."
    },
    "mouse_trap": {
        "name": "Мышеловка", "type": "consumable", "role": "mouse", "rarity": "mythic",
        "desc": "Использовать днём: если цель — Крыса, она мгновенно умирает. Если нет — умираешь ты.",
        "effect": "russian_roulette", "icon": "🪤", "price": 60000,
        "lore": "Огромная деревянная мышеловка со стальной пружиной."
    },
    "mirror_shard": {
        "name": "Осколок зеркала", "type": "consumable", "role": "mouse", "rarity": "rare",
        "desc": "Использовать ночью: отразить атаку Крысы обратно на неё",
        "effect": "reflect_kill", "icon": "🪞", "price": 1200,
        "lore": "Острый осколок старого зеркала."
    },
    "soul_candy": {
        "name": "Конфета душ", "type": "consumable", "role": "all", "rarity": "epic",
        "desc": "Использовать сразу: +1 уровень", "effect": "level_up", "icon": "🍬", "price": 5000,
        "lore": "Полупрозрачная конфета, светящаяся изнутри."
    },
    "invisibility_potion": {
        "name": "Зелье невидимости", "type": "consumable", "role": "all", "rarity": "legendary",
        "desc": "Использовать ночью: тебя нельзя выбрать целью этой ночью",
        "effect": "night_invisible", "icon": "🧪", "price": 15000,
        "lore": "Пузырёк с мерцающей жидкостью."
    },
    "love_potion": {
        "name": "Любовное зелье", "type": "consumable", "role": "all", "rarity": "rare",
        "desc": "Использовать днём: два игрока не могут голосовать друг против друга",
        "effect": "love_bond", "icon": "💕", "price": 1200,
        "lore": "Розовая жидкость с ароматом роз."
    },
    "berserk_potion": {
        "name": "Зелье берсерка", "type": "consumable", "role": "rat", "rarity": "epic",
        "desc": "Использовать ночью: убиваешь двоих, но твоя роль раскрывается на день",
        "effect": "berserk_kill", "icon": "😤", "price": 5000,
        "lore": "Тёмно-красное зелье, пахнущее железом."
    },
    "holy_water_consumable": {
        "name": "Святая вода", "type": "consumable", "role": "mouse", "rarity": "rare",
        "desc": "Использовать на мёртвого: узнать был ли он Крысой",
        "effect": "check_dead", "icon": "💧", "price": 1200,
        "lore": "Маленький пузырёк с освящённой водой."
    },
    "sleeping_powder": {
        "name": "Сонный порошок", "type": "consumable", "role": "rat", "rarity": "common",
        "desc": "Использовать ночью: жертва просыпает голосование",
        "effect": "sleep_victim", "icon": "😴", "price": 300,
        "lore": "Щепотка мелкого серого порошка."
    },
    "coffee": {
        "name": "Кофе", "type": "consumable", "role": "all", "rarity": "common",
        "desc": "Использовать днём: +5 секунд к обсуждению для всех",
        "effect": "global_day_boost", "value": 5, "icon": "☕", "price": 300,
        "lore": "Чашка горячего чёрного кофе."
    },
    "cheese_wheel": {
        "name": "Колесо сыра", "type": "consumable", "role": "all", "rarity": "rare",
        "desc": "Использовать сразу: +50 XP", "effect": "restore_xp", "value": 50, "icon": "🧀", "price": 1200,
        "lore": "Небольшое колесо выдержанного сыра."
    },
    "golden_cheese": {
        "name": "Золотой сыр", "type": "consumable", "role": "all", "rarity": "legendary",
        "desc": "Использовать сразу: +500 XP и случайный предмет",
        "effect": "jackpot", "icon": "🏆", "price": 15000,
        "lore": "Сыр, отливающий чистым золотом."
    },
    "cursed_doll": {
        "name": "Проклятая кукла", "type": "consumable", "role": "rat", "rarity": "mythic",
        "desc": "Использовать на игрока: он умирает через 2 хода",
        "effect": "curse_death", "icon": "🪆", "price": 60000,
        "lore": "Тряпичная кукла с булавками."
    },
    "angel_feather": {
        "name": "Перо ангела", "type": "consumable", "role": "mouse", "rarity": "mythic",
        "desc": "Использовать на убитого: воскресить его",
        "effect": "resurrect", "icon": "🪶", "price": 60000,
        "lore": "Белоснежное перо, излучающее тепло."
    },
    "beer": {
        "name": "Кружка пива", "type": "consumable", "role": "all", "rarity": "common",
        "desc": "Выпить в таверне: случайный временный эффект на 1 час",
        "effect": "beer_buff", "icon": "🍺", "price": 50,
        "lore": "Пенная кружка прохладного пива."
    },
    "cheese_bomb": {
        "name": "Сырная бомба", "type": "consumable", "role": "all", "rarity": "rare",
        "desc": "Использовать днём: случайный игрок теряет голос",
        "effect": "random_silence", "icon": "🧀💣", "price": 1500,
        "lore": "Шарик из сыра с торчащим фитилём."
    },
    "rat_tracker": {
        "name": "Крысиный трекер", "type": "consumable", "role": "mouse", "rarity": "epic",
        "desc": "Использовать на игрока: узнаешь его передвижения",
        "effect": "track_player", "icon": "📡", "price": 6000,
        "lore": "Небольшой приборчик с антенной."
    },
    "cheese_cake_slice": {
        "name": "Кусочек чизкейка", "type": "consumable", "role": "all", "rarity": "common",
        "desc": "Вкуснятина! +25 XP", "effect": "xp_boost", "value": 25, "icon": "🍰", "price": 200,
        "lore": "Нежный кусочек чизкейка."
    },
    "rat_poison_antidote": {
        "name": "Противоядие от крысиного яда", "type": "consumable", "role": "mouse", "rarity": "rare",
        "desc": "Снимает эффект яда с игрока", "effect": "cure_poison", "icon": "💊", "price": 1300,
        "lore": "Таблетка с горьким вкусом."
    },
    "squeaky_toy": {
        "name": "Пищалка", "type": "consumable", "role": "mouse", "rarity": "common",
        "desc": "Отвлечь Крысу. Она не может убить тебя эту ночь",
        "effect": "distract_rat", "icon": "🧸", "price": 400,
        "lore": "Резиновая игрушка, издающая громкий писк."
    },
    "rat_call": {
        "name": "Крысиный зов", "type": "consumable", "role": "rat", "rarity": "epic",
        "desc": "Призвать ещё одну Крысу на одну ночь", "effect": "summon_rat", "icon": "📯", "price": 7000,
        "lore": "Рог, издающий ультразвуковой сигнал."
    },
    "cheese_fondue": {
        "name": "Сырное фондю", "type": "consumable", "role": "all", "rarity": "rare",
        "desc": "Поделиться с командой. Все Мыши получают +10 XP",
        "effect": "team_xp_boost", "value": 10, "icon": "🫕", "price": 1800,
        "lore": "Горшочек с расплавленным сыром."
    },
    "mouse_whistle": {
        "name": "Мышиный свисток", "type": "consumable", "role": "mouse", "rarity": "rare",
        "desc": "Позвать на помощь. +1 голос на этом голосовании",
        "effect": "extra_vote", "icon": "🪈🐭", "price": 1400,
        "lore": "Серебряный свисток."
    },
    "rat_trap_blueprint": {
        "name": "Чертёж крысоловки", "type": "consumable", "role": "mouse", "rarity": "legendary",
        "desc": "Установить идеальную ловушку. Крыса умрёт если выберет тебя",
        "effect": "perfect_trap", "icon": "📐", "price": 18000,
        "lore": "Пожелтевший чертёж с детальными схемами."
    },
    "rat_mask": {
        "name": "Маска крысы", "type": "consumable", "role": "mouse", "rarity": "epic",
        "desc": "Притвориться Крысой. На один день твоя роль показывается как КРЫСА",
        "effect": "fake_rat_role", "icon": "🎭🐀", "price": 5500,
        "lore": "Уродливая маска с оскаленной мордой."
    },
    "mouse_mask": {
        "name": "Маска мыши", "type": "consumable", "role": "rat", "rarity": "epic",
        "desc": "Притвориться Мышью. На один день твоя роль показывается как МЫШЬ",
        "effect": "fake_mouse_role", "icon": "🎭🐭", "price": 5500,
        "lore": "Милая маска с ушками и усами."
    },
    "rat_king_decree": {
        "name": "Указ Крысиного короля", "type": "consumable", "role": "rat", "rarity": "mythic",
        "desc": "Отменить результаты голосования этого дня",
        "effect": "cancel_voting", "icon": "📜👑", "price": 55000,
        "lore": "Свиток с королевской печатью."
    },
    "mouse_rebellion_flag": {
        "name": "Флаг мышиного восстания", "type": "consumable", "role": "mouse", "rarity": "legendary",
        "desc": "Все Мыши получают +1 голос на этом голосовании",
        "effect": "rebellion_buff", "icon": "🚩", "price": 20000,
        "lore": "Красное полотнище с изображением сыра."
    },
    "lucky_cheese_cube": {
        "name": "Кубик удачного сыра", "type": "consumable", "role": "all", "rarity": "legendary",
        "desc": "+100% удача на одну игру", "effect": "max_luck", "icon": "🎲🧀", "price": 16000,
        "lore": "Идеально ровный кубик сыра."
    },
    "time_sand": {
        "name": "Песок времени", "type": "consumable", "role": "all", "rarity": "mythic",
        "desc": "Перемотка времени. Вернуть игру на одну фазу назад",
        "effect": "time_rewind", "icon": "⌛", "price": 70000,
        "lore": "Щепотка серебристого песка."
    },
}