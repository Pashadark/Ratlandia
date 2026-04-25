"""Services layer - бизнес-логика"""

from services.dice_service import get_dice_service
from services.tavern_service import get_tavern_service

__all__ = ['get_dice_service', 'get_tavern_service']