"""Pydantic модели для системы костей"""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum

class GameMode(str, Enum):
    """Режимы игры в кости"""
    VS_SHADOW = "vs_shadow"      # Против Тени
    VS_PLAYER = "vs_player"      # Против игрока
    TOURNAMENT = "tournament"    # Турнир
    LUCKY_ROLL = "lucky_roll"    # Проверка удачи

class BetResult(BaseModel):
    """Результат ставки"""
    bet_amount: int
    win_amount: int
    net_profit: int
    multiplier: float
    is_win: bool
    is_critical: bool = False
    is_draw: bool = False

class DiceGameResult(BaseModel):
    """Результат игры в кости"""
    user_id: int
    mode: GameMode
    player_roll: int
    shadow_roll: Optional[int] = None
    opponent_roll: Optional[int] = None
    bet: BetResult
    win_streak: int = 0
    lose_streak: int = 0
    luck_used: bool = False
    daily_bonus_used: bool = False
    timestamp: datetime = Field(default_factory=datetime.now)
    
    def to_dict(self) -> Dict[str, Any]:
        """Сериализация для БД"""
        return {
            'user_id': self.user_id,
            'mode': self.mode.value,
            'player_roll': self.player_roll,
            'shadow_roll': self.shadow_roll,
            'opponent_roll': self.opponent_roll,
            'bet_amount': self.bet.bet_amount,
            'win_amount': self.bet.win_amount,
            'is_win': self.bet.is_win,
            'is_critical': self.bet.is_critical,
            'timestamp': self.timestamp.isoformat()
        }

class PlayerStats(BaseModel):
    """Статистика игрока в кости"""
    user_id: int
    total_games: int = 0
    total_wins: int = 0
    total_losses: int = 0
    total_draws: int = 0
    total_crumbs_won: int = 0
    total_crumbs_lost: int = 0
    best_win_streak: int = 0
    current_win_streak: int = 0
    current_lose_streak: int = 0
    luck_points: int = 3
    max_luck: int = 3
    shadow_skill: int = 0
    daily_bonus_available: bool = True
    last_daily_claim: Optional[datetime] = None
    
    @property
    def win_rate(self) -> float:
        """Процент побед"""
        if self.total_games == 0:
            return 0.0
        return (self.total_wins / self.total_games) * 100
    
    @property
    def net_profit(self) -> int:
        """Чистая прибыль"""
        return self.total_crumbs_won - self.total_crumbs_lost
    
    @property
    def luck_status(self) -> str:
        """Строка статуса удачи"""
        bars = "█" * self.luck_points + "░" * (self.max_luck - self.luck_points)
        return f"[{bars}] {self.luck_points}/{self.max_luck}"

class GameSession(BaseModel):
    """Игровая сессия в таверне"""
    user_id: int
    chat_id: int
    mode: GameMode = GameMode.VS_SHADOW
    current_bet: int = 50
    free_reroll_available: bool = False
    beer_effects: List[Dict[str, Any]] = Field(default_factory=list)
    started_at: datetime = Field(default_factory=datetime.now)
    
    def has_beer_effect(self, effect_name: str) -> bool:
        """Проверяет наличие эффекта пива"""
        return any(e.get('effect') == effect_name for e in self.beer_effects)
    
    def get_beer_multiplier(self) -> float:
        """Получает множитель от пива"""
        multiplier = 1.0
        for effect in self.beer_effects:
            if effect.get('effect') == 'xp_boost':
                multiplier *= 1.1
            elif effect.get('effect') == 'luck':
                multiplier *= 1.05
        return multiplier

class TournamentEntry(BaseModel):
    """Запись в турнирной таблице"""
    user_id: int
    user_name: str
    games_played: int
    wins: int
    losses: int
    total_crumbs_won: int
    best_streak: int
    
    @property
    def win_rate(self) -> float:
        if self.games_played == 0:
            return 0.0
        return (self.wins / self.games_played) * 100

class DiceDropReward(BaseModel):
    """Награда за игры в кости"""
    user_id: int
    games_played: int
    reward_rarity: str  # common, rare, epic, legendary, mythic
    item_id: str
    item_name: str
    item_icon: str
    claimed_at: datetime = Field(default_factory=datetime.now)