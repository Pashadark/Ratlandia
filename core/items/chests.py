"""Сундуки — открываются и дают случайные предметы"""

CHESTS = {
    "common_chest": {
        "name": "Обычный сундук", "type": "chest", "rarity": "common",
        "desc": "Открыть: случайный обычный предмет",
        "icon": "📦", "drop_rarity": "common", "price": 500,
        "lore": "Простой деревянный сундук, сколоченный из старых досок."
    },
    "rare_chest": {
        "name": "Редкий сундук", "type": "chest", "rarity": "rare",
        "desc": "Открыть: случайный редкий предмет",
        "icon": "🔵", "drop_rarity": "rare", "price": 2000,
        "lore": "Сундук из тёмного дуба, окованный железом."
    },
    "epic_chest": {
        "name": "Эпический сундук", "type": "chest", "rarity": "epic",
        "desc": "Открыть: случайный эпический предмет",
        "icon": "🟣", "drop_rarity": "epic", "price": 8000,
        "lore": "Сундук, украшенный серебряными узорами."
    },
    "legendary_chest": {
        "name": "Легендарный сундук", "type": "chest", "rarity": "legendary",
        "desc": "Открыть: случайный легендарный предмет",
        "icon": "🟡", "drop_rarity": "legendary", "price": 25000,
        "lore": "Золотой сундук, усыпанный драгоценными камнями."
    },
    "mythic_chest": {
        "name": "Мифический сундук", "type": "chest", "rarity": "mythic",
        "desc": "Открыть: случайный мифический предмет",
        "icon": "🔴", "drop_rarity": "mythic", "price": 100000,
        "lore": "Сундук, словно сотканный из звёздного света."
    },
    "rat_chest": {
        "name": "Крысиный сундук", "type": "chest", "rarity": "epic",
        "desc": "Открыть: случайный предмет для Крысы (эпик+)",
        "icon": "🐀📦", "drop_rarity": "epic", "role_filter": "rat", "price": 10000,
        "lore": "Тёмный сундук, обтянутый крысиной шкурой."
    },
    "mouse_chest": {
        "name": "Мышиный сундук", "type": "chest", "rarity": "epic",
        "desc": "Открыть: случайный предмет для Мыши (эпик+)",
        "icon": "🐭📦", "drop_rarity": "epic", "role_filter": "mouse", "price": 10000,
        "lore": "Светлый сундук, украшенный колосьями."
    },
    "cheese_chest": {
        "name": "Сырный сундук", "type": "chest", "rarity": "legendary",
        "desc": "Открыть: 3-5 случайных сырных предметов",
        "icon": "🧀📦", "drop_rarity": "legendary", "special": "multiple_cheese", "price": 35000,
        "lore": "Сундук, целиком сделанный из затвердевшего сыра."
    },
}