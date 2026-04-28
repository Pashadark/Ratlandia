"""Модели предметов Ratlandia"""

from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any
from enum import Enum


class ItemRarity(str, Enum):
    COMMON = "common"
    UNCOMMON = "uncommon"
    RARE = "rare"
    EPIC = "epic"
    LEGENDARY = "legendary"
    MYTHIC = "mythic"


class ItemType(str, Enum):
    WEAPON = "weapon"
    ARMOR = "armor"
    ACCESSORY = "accessory"
    CONSUMABLE = "consumable"
    RESOURCE = "resource"
    CHEST = "chest"


class EquipmentSlot(str, Enum):
    WEAPON = "weapon"
    ARMOR = "armor"
    ACCESSORY = "accessory"


@dataclass
class Item:
    """Базовый предмет"""
    item_id: str
    name: str
    description: str
    icon: str
    rarity: ItemRarity
    item_type: ItemType
    stackable: bool = False
    max_stack: int = 1
    sell_price: int = 0
    buy_price: int = 0
    tradeable: bool = True

    def to_dict(self) -> Dict[str, Any]:
        return {
            'item_id': self.item_id,
            'name': self.name,
            'description': self.description,
            'icon': self.icon,
            'rarity': self.rarity.value,
            'item_type': self.item_type.value,
            'stackable': self.stackable,
            'max_stack': self.max_stack,
            'sell_price': self.sell_price,
            'buy_price': self.buy_price,
            'tradeable': self.tradeable,
        }


@dataclass
class Equipment(Item):
    """Экипировка"""
    slot: EquipmentSlot = EquipmentSlot.WEAPON
    level_required: int = 1
    strength_bonus: int = 0
    agility_bonus: int = 0
    intelligence_bonus: int = 0
    health_bonus: int = 0
    damage_bonus: int = 0
    armor_bonus: int = 0
    upgrade_level: int = 0
    max_upgrade_level: int = 10
    socket: Optional[str] = None
    effects: List[Dict[str, Any]] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        base = super().to_dict()
        base.update({
            'slot': self.slot.value,
            'level_required': self.level_required,
            'strength_bonus': self.strength_bonus,
            'agility_bonus': self.agility_bonus,
            'intelligence_bonus': self.intelligence_bonus,
            'health_bonus': self.health_bonus,
            'damage_bonus': self.damage_bonus,
            'armor_bonus': self.armor_bonus,
            'upgrade_level': self.upgrade_level,
            'max_upgrade_level': self.max_upgrade_level,
            'socket': self.socket,
            'effects': self.effects,
        })
        return base


@dataclass
class Consumable(Item):
    """Расходник"""
    heal_hp: int = 0
    heal_percent: float = 0.0
    buff_effect: Optional[str] = None
    buff_duration_minutes: int = 0
    xp_bonus: int = 0

    def to_dict(self) -> Dict[str, Any]:
        base = super().to_dict()
        base.update({
            'heal_hp': self.heal_hp,
            'heal_percent': self.heal_percent,
            'buff_effect': self.buff_effect,
            'buff_duration_minutes': self.buff_duration_minutes,
            'xp_bonus': self.xp_bonus,
        })
        return base


@dataclass
class Chest(Item):
    """Сундук"""
    drop_table: List[Dict[str, Any]] = field(default_factory=list)
    min_drops: int = 1
    max_drops: int = 3

    def to_dict(self) -> Dict[str, Any]:
        base = super().to_dict()
        base.update({
            'drop_table': self.drop_table,
            'min_drops': self.min_drops,
            'max_drops': self.max_drops,
        })
        return base


@dataclass
class Recipe:
    """Рецепт крафта"""
    recipe_id: str
    name: str
    result_item_id: str
    result_quantity: int = 1
    ingredients: Dict[str, int] = field(default_factory=dict)
    required_level: int = 1
    success_rate: float = 100.0
    crumbs_cost: int = 0
    category: str = "misc"

    def to_dict(self) -> Dict[str, Any]:
        return {
            'recipe_id': self.recipe_id,
            'name': self.name,
            'result_item_id': self.result_item_id,
            'result_quantity': self.result_quantity,
            'ingredients': self.ingredients,
            'required_level': self.required_level,
            'success_rate': self.success_rate,
            'crumbs_cost': self.crumbs_cost,
            'category': self.category,
        }