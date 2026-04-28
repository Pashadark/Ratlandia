"""Достижения для Ратляндии"""

ACHIEVEMENTS = {
    # ========== БАЗОВЫЕ ==========
    "first_blood": {
        "name": "🩸 Первая кровь",
        "desc": "Совершить первое убийство",
        "rarity": "common",
        "xp": 100,
        "icon": "🩸",
        "hidden": False
    },
    "nest_defender": {
        "name": "🛡️ Защитник норы",
        "desc": "Победить за Мышь",
        "rarity": "common",
        "xp": 100,
        "icon": "🛡️",
        "hidden": False
    },
    "survivor": {
        "name": "🏃 Выживший",
        "desc": "Дожить до конца игры и победить",
        "rarity": "common",
        "xp": 150,
        "icon": "🏃",
        "hidden": False
    },
    "voice_of_people": {
        "name": "🗳️ Голос народа",
        "desc": "Проголосовать 50 раз",
        "rarity": "common",
        "xp": 100,
        "icon": "🗳️",
        "hidden": False
    },
    
    # ========== РЕДКИЕ ==========
    "master_of_disguise": {
        "name": "🎭 Мастер маскировки",
        "desc": "Победить за Крысу",
        "rarity": "rare",
        "xp": 250,
        "icon": "🎭",
        "hidden": False
    },
    "eagle_eye": {
        "name": "🎯 Меткий глаз",
        "desc": "Угадать Крысу с первого голосования",
        "rarity": "rare",
        "xp": 250,
        "icon": "🎯",
        "hidden": False
    },
    "pacifist": {
        "name": "😇 Пацифист",
        "desc": "Победить за Мышь, ни разу не голосовав",
        "rarity": "rare",
        "xp": 300,
        "icon": "😇",
        "hidden": False
    },
    "lucky_cheese": {
        "name": "🧀 Сырный магнат",
        "desc": "Собрать 10 предметов",
        "rarity": "rare",
        "xp": 200,
        "icon": "🧀",
        "hidden": False
    },
    "ghost_whisper": {
        "name": "👻 Шёпот призрака",
        "desc": "Победить после своей смерти",
        "rarity": "rare",
        "xp": 350,
        "icon": "👻",
        "hidden": False
    },
    
    # ========== ЭПИЧЕСКИЕ ==========
    "serial_killer": {
        "name": "🔥 Серийный убийца",
        "desc": "Выиграть 3 игры за Крысу подряд",
        "rarity": "epic",
        "xp": 500,
        "icon": "🔥",
        "hidden": False
    },
    "merciless": {
        "name": "💀 Безжалостный",
        "desc": "Совершить 25 убийств",
        "rarity": "epic",
        "xp": 500,
        "icon": "💀",
        "hidden": False
    },
    "night_hunter": {
        "name": "🌙 Ночной охотник",
        "desc": "Убивать каждую ночь в течение одной игры",
        "rarity": "epic",
        "xp": 400,
        "icon": "🌙",
        "hidden": False
    },
    "puppeteer": {
        "name": "🎪 Кукольник",
        "desc": "Победить за Крысу, подставив невиновного на голосовании",
        "rarity": "epic",
        "xp": 450,
        "icon": "🎪",
        "hidden": False
    },
    "day_detective": {
        "name": "☀️ Дневной детектив",
        "desc": "Найти и казнить Крысу за первые 2 дня",
        "rarity": "epic",
        "xp": 450,
        "icon": "☀️",
        "hidden": False
    },
    "rat_slayer": {
        "name": "⚔️ Крысобой",
        "desc": "Убить Крысу 10 раз",
        "rarity": "epic",
        "xp": 500,
        "icon": "⚔️",
        "hidden": False
    },
    "mouse_massacre": {
        "name": "🐭 Мышиная резня",
        "desc": "Убить 30 мышей",
        "rarity": "epic",
        "xp": 500,
        "icon": "🐭",
        "hidden": True  # СКРЫТОЕ достижение!
    },
    
    # ========== ЛЕГЕНДАРНЫЕ ==========
    "rat_king": {
        "name": "👑 Король крыс",
        "desc": "Одержать 15 побед за Крысу",
        "rarity": "legendary",
        "xp": 1000,
        "icon": "👑",
        "hidden": False
    },
    "pack_leader": {
        "name": "🐭 Вожак стаи",
        "desc": "Одержать 30 побед за Мышь",
        "rarity": "legendary",
        "xp": 1000,
        "icon": "🐭",
        "hidden": False
    },
    "psychic": {
        "name": "🔮 Экстрасенс",
        "desc": "Угадать Крысу 5 раз подряд",
        "rarity": "legendary",
        "xp": 1200,
        "icon": "🔮",
        "hidden": False
    },
    "grand_manipulator": {
        "name": "🎪 Великий манипулятор",
        "desc": "Подставить невиновного 5 раз",
        "rarity": "legendary",
        "xp": 1000,
        "icon": "🎪",
        "hidden": False
    },
    "immortal": {
        "name": "💪 Бессмертный",
        "desc": "Выжить 10 игр подряд",
        "rarity": "legendary",
        "xp": 1500,
        "icon": "💪",
        "hidden": False
    },
    "collector": {
        "name": "🏺 Коллекционер",
        "desc": "Собрать 50 предметов",
        "rarity": "legendary",
        "xp": 800,
        "icon": "🏺",
        "hidden": False
    },
    "perfect_game": {
        "name": "✨ Идеальная игра",
        "desc": "Победить за Крысу не получив ни одного голоса",
        "rarity": "legendary",
        "xp": 1500,
        "icon": "✨",
        "hidden": True  # СКРЫТОЕ!
    },
    
    # ========== МИФИЧЕСКИЕ ==========
    "rat_emperor": {
        "name": "🏰 Крысиный император",
        "desc": "Одержать 50 побед за Крысу",
        "rarity": "mythic",
        "xp": 2500,
        "icon": "🏰",
        "hidden": False
    },
    "mouse_god": {
        "name": "⚡ Бог мышей",
        "desc": "Одержать 100 побед за Мышь",
        "rarity": "mythic",
        "xp": 3000,
        "icon": "⚡",
        "hidden": False
    },
    "invincible": {
        "name": "🌟 Непобедимый",
        "desc": "Выиграть 10 игр подряд",
        "rarity": "mythic",
        "xp": 3000,
        "icon": "🌟",
        "hidden": False
    },
    "two_faced": {
        "name": "🎭 Двуликий",
        "desc": "Одержать по 50 побед за каждую роль",
        "rarity": "mythic",
        "xp": 4000,
        "icon": "🎭",
        "hidden": False
    },
    "butcher": {
        "name": "🔪 Мясник",
        "desc": "Совершить 100 убийств",
        "rarity": "mythic",
        "xp": 2500,
        "icon": "🔪",
        "hidden": False
    },
    "history_keeper": {
        "name": "📜 Хранитель истории",
        "desc": "Сыграть 500 игр",
        "rarity": "mythic",
        "xp": 5000,
        "icon": "📜",
        "hidden": False
    },
    "rat_apocalypse": {
        "name": "🌑 Крысиный апокалипсис",
        "desc": "Победить за Крысу в игре с 10 игроками, убив всех лично",
        "rarity": "mythic",
        "xp": 3000,
        "icon": "🌑",
        "hidden": True  # СКРЫТОЕ!
    },
    "the_one": {
        "name": "👁️ Избранный",
        "desc": "Разблокировать все остальные достижения",
        "rarity": "mythic",
        "xp": 10000,
        "icon": "👁️",
        "hidden": False
    },
        # ========== ДОСТИЖЕНИЯ КЛАНА ==========
    "clan_birth": {
        "name": "🏰 Основание",
        "desc": "Создать клан",
        "rarity": "common",
        "xp": 200,
        "icon": "🏰",
        "hidden": False
    },
    "clan_five": {
        "name": "👥 Пятёрка смелых",
        "desc": "Накопить 5 участников в клане",
        "rarity": "rare",
        "xp": 500,
        "icon": "👥",
        "hidden": False
    },
    "clan_ten": {
        "name": "⚔️ Десятка воинов",
        "desc": "Накопить 10 участников в клане",
        "rarity": "epic",
        "xp": 1000,
        "icon": "⚔️",
        "hidden": False
    },
    "clan_twenty": {
        "name": "🏛️ Армия туннелей",
        "desc": "Накопить 20 участников в клане",
        "rarity": "legendary",
        "xp": 2000,
        "icon": "🏛️",
        "hidden": False
    },
    "clan_fifty": {
        "name": "🐉 Легион",
        "desc": "Накопить 50 участников в клане",
        "rarity": "mythic",
        "xp": 5000,
        "icon": "🐉",
        "hidden": False
    },
    "clan_leader": {
        "name": "👑 Лидер",
        "desc": "Стать лидером клана",
        "rarity": "common",
        "xp": 300,
        "icon": "👑",
        "hidden": False
    },
    "clan_recruiter": {
        "name": "📯 Вербовщик",
        "desc": "Пригласить 3 игроков в клан",
        "rarity": "rare",
        "xp": 400,
        "icon": "📯",
        "hidden": False
    },
    "clan_elder": {
        "name": "🛡️ Старейшина",
        "desc": "Получить звание Старейшины",
        "rarity": "epic",
        "xp": 600,
        "icon": "🛡️",
        "hidden": False
    },
    "clan_veteran": {
        "name": "⚔️ Ветеран",
        "desc": "Получить звание Ветерана",
        "rarity": "legendary",
        "xp": 1500,
        "icon": "⚔️",
        "hidden": False
    },
    "clan_war_winner": {
        "name": "🏆 Победитель войн",
        "desc": "Выиграть первую клановую войну",
        "rarity": "rare",
        "xp": 500,
        "icon": "🏆",
        "hidden": False
    },
    "clan_war_veteran": {
        "name": "⚔️ Ветеран войн",
        "desc": "Выиграть 10 клановых войн",
        "rarity": "epic",
        "xp": 2000,
        "icon": "⚔️",
        "hidden": False
    },
    "clan_war_legend": {
        "name": "🌟 Легенда войн",
        "desc": "Выиграть 50 клановых войн",
        "rarity": "mythic",
        "xp": 5000,
        "icon": "🌟",
        "hidden": False
    },
    "clan_war_streak": {
        "name": "🔥 Неудержимые",
        "desc": "Выиграть 5 клановых войн подряд",
        "rarity": "legendary",
        "xp": 3000,
        "icon": "🔥",
        "hidden": False
    },
    "clan_donator": {
        "name": "💰 Казначей",
        "desc": "Пожертвовать 10,000 крошек в казну клана",
        "rarity": "rare",
        "xp": 500,
        "icon": "💰",
        "hidden": False
    },
    "clan_rich": {
        "name": "💎 Богатство клана",
        "desc": "Накопить 100,000 крошек в казне",
        "rarity": "legendary",
        "xp": 3000,
        "icon": "💎",
        "hidden": False
    },
    "clan_loyal": {
        "name": "🤝 Верность",
        "desc": "Быть в одном клане 30 дней",
        "rarity": "rare",
        "xp": 500,
        "icon": "🤝",
        "hidden": False
    },
    "clan_ancient": {
        "name": "📜 Древний клан",
        "desc": "Быть в одном клане 365 дней",
        "rarity": "mythic",
        "xp": 5000,
        "icon": "📜",
        "hidden": False
    },
    "clan_dynasty": {
        "name": "👑 Династия",
        "desc": "Передать лидерство и остаться в клане",
        "rarity": "legendary",
        "xp": 2000,
        "icon": "👑",
        "hidden": False
    },
    "clan_mentor": {
        "name": "🎓 Наставник",
        "desc": "Помочь 10 новобранцам получить повышение",
        "rarity": "epic",
        "xp": 1500,
        "icon": "🎓",
        "hidden": False
    },
    "clan_hunter": {
        "name": "🎯 Охотник за головами",
        "desc": "Убить 100 вражеских клановцев в войнах",
        "rarity": "legendary",
        "xp": 3000,
        "icon": "🎯",
        "hidden": False
    },
    "clan_unity": {
        "name": "🤝 Единство",
        "desc": "В клане 10+ участников и все активны 7 дней",
        "rarity": "epic",
        "xp": 1500,
        "icon": "🤝",
        "hidden": False
    },
    "clan_supremacy": {
        "name": "🔱 Превосходство",
        "desc": "Занять 1 место в топе кланов",
        "rarity": "mythic",
        "xp": 5000,
        "icon": "🔱",
        "hidden": False
    },
}
