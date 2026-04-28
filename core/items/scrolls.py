"""Свитки заточки оружия, брони и бижутерии"""

ENCHANT_SCROLLS = {
    # ===== ОРУЖИЕ =====
    "enchant_scroll_weapon": {
        "name": "Свиток заточки оружия", "type": "scroll", "rarity": "rare",
        "desc": "Заточить оружие: +1 уровень. При неудаче с +4 вещь может сломаться.",
        "effect": "enchant_weapon",
        "icon": "📜⚔️", "price": 5000,
        "lore": "Древний пергамент с рунами усиления."
    },
    "blessed_scroll_weapon": {
        "name": "Благословенный свиток оружия", "type": "scroll", "rarity": "epic",
        "desc": "Заточить оружие: +1 уровень. При неудаче сброс на 0, но вещь цела.",
        "effect": "enchant_weapon_blessed",
        "icon": "📜✨", "price": 25000,
        "lore": "Свиток, освящённый жрецами Мышиного Бога."
    },
    "crystal_scroll_weapon": {
        "name": "Кристальный свиток оружия", "type": "scroll", "rarity": "legendary",
        "desc": "Заточить оружие: +1 уровень. Повышенный шанс успеха (x1.5).",
        "effect": "enchant_weapon_crystal",
        "icon": "📜💎", "price": 50000,
        "lore": "Свиток, инкрустированный кристальной пылью."
    },

    # ===== БРОНЯ =====
    "enchant_scroll_armor": {
        "name": "Свиток заточки брони", "type": "scroll", "rarity": "rare",
        "desc": "Заточить броню: +1 уровень. При неудаче с +4 вещь может сломаться.",
        "effect": "enchant_armor",
        "icon": "📜🛡️", "price": 4000,
        "lore": "Пергамент, пропитанный защитной магией."
    },
    "blessed_scroll_armor": {
        "name": "Благословенный свиток брони", "type": "scroll", "rarity": "epic",
        "desc": "Заточить броню: +1 уровень. При неудаче сброс на 0, но вещь цела.",
        "effect": "enchant_armor_blessed",
        "icon": "📜✨", "price": 20000,
        "lore": "Свиток, окроплённый святой водой."
    },
    "crystal_scroll_armor": {
        "name": "Кристальный свиток брони", "type": "scroll", "rarity": "legendary",
        "desc": "Заточить броню: +1 уровень. Повышенный шанс успеха (x1.5).",
        "effect": "enchant_armor_crystal",
        "icon": "📜💎", "price": 45000,
        "lore": "Свиток, сверкающий как алмаз."
    },

    # ===== БИЖУТЕРИЯ =====
    "enchant_scroll_accessory": {
        "name": "Свиток заточки бижутерии", "type": "scroll", "rarity": "rare",
        "desc": "Заточить бижутерию: +1 уровень. При неудаче с +4 вещь может сломаться.",
        "effect": "enchant_accessory",
        "icon": "📜💍", "price": 3000,
        "lore": "Пергамент с рунами усиления амулетов и колец."
    },
    "blessed_scroll_accessory": {
        "name": "Благословенный свиток бижутерии", "type": "scroll", "rarity": "epic",
        "desc": "Заточить бижутерию: +1 уровень. При неудаче сброс на 0, но вещь цела.",
        "effect": "enchant_accessory_blessed",
        "icon": "📿✨", "price": 15000,
        "lore": "Свиток, благословлённый на удачу и защиту."
    },
    "crystal_scroll_accessory": {
        "name": "Кристальный свиток бижутерии", "type": "scroll", "rarity": "legendary",
        "desc": "Заточить бижутерию: +1 уровень. Повышенный шанс успеха (x1.5).",
        "effect": "enchant_accessory_crystal",
        "icon": "💎💍", "price": 35000,
        "lore": "Кристальный пергамент, усиливающий магию украшений."
    },
}