"""
КАТАЛОГ ВСЕХ ПРЕДМЕТОВ РАТЛЯНДИИ
Собирает все категории предметов в один словарь ALL_ITEMS
"""

from core.items.resources import RESOURCES
from core.items.equipment import EQUIPMENT
from core.items.weapons import NEW_WEAPONS, WEAPON_DAMAGE
from core.items.bows import NEW_BOWS, BOW_DAMAGE
from core.items.armor import CLASS_ARMORS
from core.items.consumables import CONSUMABLES
from core.items.chests import CHESTS
from core.items.recipes import ALL_RECIPES
from core.items.gems import ENCHANT_GEMS
from core.items.scrolls import ENCHANT_SCROLLS

# ========== ВСЕ ПРЕДМЕТЫ ==========
ALL_ITEMS = {
    **RESOURCES,
    **EQUIPMENT,
    **NEW_WEAPONS,
    **NEW_BOWS,
    **CLASS_ARMORS,
    **CONSUMABLES,
    **CHESTS,
    **ALL_RECIPES,
    **ENCHANT_GEMS,
    **ENCHANT_SCROLLS,
}

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


# ========== ФУНКЦИИ ==========

def get_craft_recipe(item_id: str) -> dict:
    """Возвращает рецепт крафта для предмета (из item_id)"""
    item = ALL_ITEMS.get(item_id, {})
    if not item or not item.get("craftable"):
        return None
    return {
        "rarity": item.get("rarity", "common"),
        "materials": item.get("craft_materials", {}),
        "blueprint_required": item.get("craft_blueprint"),
    }


def get_recipe_by_id(recipe_id: str) -> dict:
    """Возвращает рецепт по ID рецепта"""
    recipe = ALL_RECIPES.get(recipe_id)
    if not recipe:
        return None
    return {
        "result_item": recipe.get("result_item"),
        "materials": recipe.get("materials", {}),
        "rarity": recipe.get("rarity", "common"),
    }


def get_all_recipes() -> dict:
    """Возвращает все рецепты"""
    return ALL_RECIPES