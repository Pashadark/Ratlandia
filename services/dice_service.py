"""Прослойка между хендлерами и движком костей"""

import random
import sqlite3
from typing import Optional, Tuple, Dict, Any, List
from datetime import datetime, timedelta
from pathlib import Path

from core.dice.engine import (
    get_dice_engine, DiceEngine, EngineConfig, 
    DiceRollType, SuccessLevel, LuckPool, RollStatistics
)

from core.dice.models import (
    GameMode, BetResult, DiceGameResult, 
    PlayerStats, TournamentEntry, DiceDropReward
)
from config import dice_settings, settings
from core.database import db

class DiceService:
    """Сервис для работы с костями"""
    
    def __init__(self):
        self.engine = get_dice_engine()
        self.config = dice_settings
        self._init_db()
    
    def _init_db(self):
        """Инициализирует таблицы для костей"""
        with sqlite3.connect(settings.main_db_path) as conn:
            # Статистика игр
            conn.execute('''
                CREATE TABLE IF NOT EXISTS dice_games (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    games_played INTEGER DEFAULT 0,
                    last_reward_at TEXT,
                    updated_at TEXT
                )
            ''')
            
            # История игр
            conn.execute('''
                CREATE TABLE IF NOT EXISTS dice_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    player_roll INTEGER,
                    shadow_roll INTEGER,
                    bet INTEGER,
                    win_amount INTEGER,
                    is_win INTEGER,
                    is_critical INTEGER,
                    win_streak INTEGER,
                    lose_streak INTEGER,
                    timestamp TEXT
                )
            ''')
            
            # Эффекты пива
            conn.execute('''
                CREATE TABLE IF NOT EXISTS beer_effects (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    effect_name TEXT,
                    effect_type TEXT,
                    value INTEGER,
                    expires_at TEXT,
                    created_at TEXT
                )
            ''')
            
            conn.commit()
    
    # ========== БРОСКИ ==========
    
    def roll_1d6(self) -> int:
        """Бросок 1d6 (старый интерфейс)"""
        return random.randint(1, 6)
    
    def roll_with_luck(self, user_id: int, dc: int = 10) -> Tuple[int, bool]:
        """Бросок d20 с учётом удачи игрока"""
        luck_pool = self.engine.get_luck_pool(user_id)
        result = self.engine.roll_d20(dc=dc)
        
        luck_used = False
        if not result.success_level or result.success_level.code < 2:
            if luck_pool.can_use(1):
                result = self.engine.use_luck_bonus(luck_pool, result, 1)
                luck_used = True
        
        return result.total, luck_used
    
    def check_skill(self, user_id: int, skill_name: str, dc: int) -> Dict[str, Any]:
        """Проверка навыка (сила/ловка/интеллект)"""
        stats = self._get_player_stats_for_check(user_id)
        
        bonus = 0
        if skill_name == "strength":
            bonus = stats.get("strength", 0)
        elif skill_name == "agility":
            bonus = stats.get("agility", 0)
        elif skill_name == "intelligence":
            bonus = stats.get("intelligence", 0)
        
        result = self.engine.roll_d20(dc=dc)
        result.total += bonus
        
        if dc:
            result.success_level = self.engine._evaluate_success(result.total, dc)
        
        return {
            "roll": result.rolls[0],
            "bonus": bonus,
            "total": result.total,
            "dc": dc,
            "success": result.total >= dc if dc else None,
            "success_level": result.success_level.display if result.success_level else None,
            "is_critical": result.is_critical,
            "is_fumble": result.is_fumble
        }
    
    def _get_player_stats_for_check(self, user_id: int) -> Dict[str, int]:
        """Получает статы игрока для проверки"""
        return {"strength": 0, "agility": 0, "intelligence": 0}
    
    # ========== ИГРА ПРОТИВ ТЕНИ ==========
    
    def play_vs_shadow(self, user_id: int, bet: int, 
                       daily_bonus: bool = False,
                       free_reroll: bool = False) -> DiceGameResult:
        """Игра против Тени"""
        
        player_roll = self.roll_1d6()
        shadow_roll = self.roll_1d6()
        
        stats = self.get_player_stats(user_id)
        
        is_win = player_roll > shadow_roll
        is_draw = player_roll == shadow_roll
        is_critical = (player_roll == 6 and shadow_roll == 1)
        is_crit_lose = (player_roll == 1 and shadow_roll == 6)
        
        multiplier = self._calculate_multiplier(
            player_roll, shadow_roll, 
            stats.current_win_streak, 
            is_critical, is_crit_lose
        )
        
        if daily_bonus and is_win:
            multiplier *= 2
        
        if is_win:
            win_amount = int(bet * multiplier)
            net_profit = win_amount - bet
        else:
            win_amount = 0
            net_profit = -bet
        
        bet_result = BetResult(
            bet_amount=bet,
            win_amount=win_amount,
            net_profit=net_profit,
            multiplier=multiplier,
            is_win=is_win,
            is_critical=is_critical,
            is_draw=is_draw
        )
        
        result = DiceGameResult(
            user_id=user_id,
            mode=GameMode.VS_SHADOW,
            player_roll=player_roll,
            shadow_roll=shadow_roll,
            bet=bet_result,
            win_streak=stats.current_win_streak + (1 if is_win else 0),
            lose_streak=0 if is_win else stats.current_lose_streak + 1,
            daily_bonus_used=daily_bonus
        )
        
        self._save_game_result(result)
        self._update_player_stats(user_id, result)
        
        return result
    
    def _calculate_multiplier(self, player_roll: int, shadow_roll: int,
                              win_streak: int, is_critical: bool,
                              is_crit_lose: bool) -> float:
        """Рассчитывает множитель выигрыша"""
        base = 2.0
        
        if win_streak >= 5:
            base = 3.0
        elif win_streak >= 3:
            base = 2.5
        
        if is_critical:
            base = 5.0
        elif player_roll == 6 and shadow_roll == 6:
            base = 10.0
        
        return base
    
    # ========== СТАТИСТИКА ==========
    
    def get_player_stats(self, user_id: int) -> PlayerStats:
        """Получает статистику игрока"""
        with sqlite3.connect(settings.main_db_path) as conn:
            conn.row_factory = sqlite3.Row
            
            cur = conn.execute('''
                SELECT 
                    COUNT(*) as total_games,
                    COALESCE(SUM(CASE WHEN is_win = 1 THEN 1 ELSE 0 END), 0) as wins,
                    COALESCE(SUM(CASE WHEN is_win = 0 THEN 1 ELSE 0 END), 0) as losses,
                    COALESCE(SUM(CASE WHEN player_roll = shadow_roll THEN 1 ELSE 0 END), 0) as draws,
                    COALESCE(SUM(CASE WHEN is_win = 1 THEN win_amount - bet ELSE 0 END), 0) as crumbs_won,
                    COALESCE(SUM(CASE WHEN is_win = 0 THEN bet ELSE 0 END), 0) as crumbs_lost
                FROM dice_history 
                WHERE user_id = ?
            ''', (user_id,))
            row = cur.fetchone()
            
            games_cur = conn.execute(
                'SELECT games_played, last_reward_at FROM dice_games WHERE user_id = ?',
                (user_id,)
            )
            games_row = games_cur.fetchone()
            total_games_played = games_row['games_played'] if games_row else 0
            
            daily_available = True
            last_daily = None
            if games_row and games_row['last_reward_at']:
                try:
                    last_daily = datetime.fromisoformat(games_row['last_reward_at'])
                    daily_available = datetime.now().date() > last_daily.date()
                except:
                    pass
            
            streaks = self._calculate_streaks(user_id)
            luck_pool = self.engine.get_luck_pool(user_id)
            
            return PlayerStats(
                user_id=user_id,
                total_games=row['total_games'] if row else 0,
                total_wins=row['wins'] if row else 0,
                total_losses=row['losses'] if row else 0,
                total_draws=row['draws'] if row else 0,
                total_crumbs_won=row['crumbs_won'] or 0,
                total_crumbs_lost=row['crumbs_lost'] or 0,
                best_win_streak=streaks.get('best_win', 0),
                current_win_streak=streaks.get('current_win', 0),
                current_lose_streak=streaks.get('current_lose', 0),
                luck_points=luck_pool.current,
                max_luck=luck_pool.max,
                daily_bonus_available=daily_available,
                last_daily_claim=last_daily
            )
    
    def _calculate_streaks(self, user_id: int) -> Dict[str, int]:
        """Рассчитывает серии побед/поражений"""
        with sqlite3.connect(settings.main_db_path) as conn:
            conn.row_factory = sqlite3.Row
            cur = conn.execute('''
                SELECT is_win FROM dice_history 
                WHERE user_id = ? 
                ORDER BY timestamp DESC 
                LIMIT 50
            ''', (user_id,))
            
            current_win = 0
            current_lose = 0
            best_win = 0
            current_streak_type = None
            
            for i, row in enumerate(cur.fetchall()):
                is_win = row['is_win']
                
                if i == 0:
                    current_streak_type = 'win' if is_win else 'lose'
                
                if is_win:
                    if current_streak_type == 'win' or current_streak_type is None:
                        current_win += 1
                        best_win = max(best_win, current_win)
                    else:
                        break
                else:
                    if current_streak_type == 'lose' or current_streak_type is None:
                        current_lose += 1
                    else:
                        break
            
            return {
                'current_win': current_win,
                'current_lose': current_lose,
                'best_win': best_win
            }
    
    def _save_game_result(self, result: DiceGameResult):
        """Сохраняет результат игры"""
        with sqlite3.connect(settings.main_db_path) as conn:
            conn.execute('''
                INSERT INTO dice_history 
                (user_id, player_roll, shadow_roll, bet, win_amount, 
                 is_win, is_critical, win_streak, lose_streak, timestamp)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                result.user_id,
                result.player_roll,
                result.shadow_roll,
                result.bet.bet_amount,
                result.bet.win_amount,
                1 if result.bet.is_win else 0,
                1 if result.bet.is_critical else 0,
                result.win_streak,
                result.lose_streak,
                result.timestamp.isoformat()
            ))
            
            conn.execute('''
                INSERT INTO dice_games (user_id, games_played, updated_at)
                VALUES (?, 1, ?)
                ON CONFLICT(user_id) DO UPDATE SET
                games_played = games_played + 1,
                updated_at = ?
            ''', (result.user_id, datetime.now().isoformat(), datetime.now().isoformat()))
            
            conn.commit()
    
    def _update_player_stats(self, user_id: int, result: DiceGameResult):
        """Обновляет статистику игрока"""
        if result.bet.is_win:
            db.add_crumbs(user_id, result.bet.win_amount)
        else:
            db.spend_crumbs(user_id, result.bet.bet_amount)
    
    # ========== ТУРНИРЫ ==========
    
    def get_tournament_leaders(self, limit: int = 10) -> List[TournamentEntry]:
        """Получает лидеров турнира"""
        with sqlite3.connect(settings.main_db_path) as conn:
            conn.row_factory = sqlite3.Row
            cur = conn.execute('''
                SELECT 
                    h.user_id,
                    r.name as user_name,
                    COUNT(*) as games_played,
                    COALESCE(SUM(CASE WHEN h.is_win = 1 THEN 1 ELSE 0 END), 0) as wins,
                    COALESCE(SUM(CASE WHEN h.is_win = 0 THEN 1 ELSE 0 END), 0) as losses,
                    COALESCE(SUM(CASE WHEN h.is_win = 1 THEN h.win_amount - h.bet ELSE 0 END), 0) as total_crumbs_won
                FROM dice_history h
                LEFT JOIN ratings r ON h.user_id = r.user_id
                GROUP BY h.user_id
                HAVING games_played >= 5
                ORDER BY total_crumbs_won DESC
                LIMIT ?
            ''', (limit,))
            
            leaders = []
            for row in cur.fetchall():
                streaks = self._calculate_streaks(row['user_id'])
                
                leaders.append(TournamentEntry(
                    user_id=row['user_id'],
                    user_name=row['user_name'] or f"Игрок {row['user_id']}",
                    games_played=row['games_played'],
                    wins=row['wins'] or 0,
                    losses=row['losses'] or 0,
                    total_crumbs_won=row['total_crumbs_won'] or 0,
                    best_streak=streaks.get('best_win', 0)
                ))
            
            return leaders
    
    # ========== НАГРАДЫ ==========
    
    def check_and_get_reward(self, user_id: int, games_played: int) -> Optional[DiceDropReward]:
        """Проверяет и выдаёт награду за игры"""
        reward_milestones = {
            10: "common",
            25: "rare",
            50: "epic",
            100: "legendary",
            250: "mythic"
        }
        
        reward_rarity = None
        for milestone, rarity in sorted(reward_milestones.items()):
            if games_played >= milestone:
                reward_rarity = rarity
        
        if not reward_rarity:
            return None
        
        with sqlite3.connect(settings.main_db_path) as conn:
            cur = conn.execute(
                'SELECT last_reward_at FROM dice_games WHERE user_id = ?',
                (user_id,)
            )
            row = cur.fetchone()
        
        return DiceDropReward(
            user_id=user_id,
            games_played=games_played,
            reward_rarity=reward_rarity,
            item_id=f"{reward_rarity}_chest",
            item_name=f"{reward_rarity.upper()} СУНДУК",
            item_icon="📦"
        )
    
    def claim_daily_bonus(self, user_id: int) -> bool:
        """Активирует ежедневный бонус"""
        with sqlite3.connect(settings.main_db_path) as conn:
            conn.execute('''
                UPDATE dice_games 
                SET last_reward_at = ?
                WHERE user_id = ?
            ''', (datetime.now().isoformat(), user_id))
            conn.commit()
        return True
    
    # ========== ПИВО И ЭФФЕКТЫ ==========
    
    def add_beer_effect(self, user_id: int, effect: Dict[str, Any], duration_hours: int = 1):
        """Добавляет эффект пива"""
        expires_at = datetime.now() + timedelta(hours=duration_hours)
        
        with sqlite3.connect(settings.main_db_path) as conn:
            conn.execute('''
                INSERT INTO beer_effects 
                (user_id, effect_name, effect_type, value, expires_at, created_at)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                user_id,
                effect.get('name', 'Неизвестный эффект'),
                effect.get('effect', 'unknown'),
                effect.get('value', 0),
                expires_at.isoformat(),
                datetime.now().isoformat()
            ))
            conn.commit()
    
    def get_active_beer_effects(self, user_id: int) -> List[Dict[str, Any]]:
        """Получает активные эффекты пива"""
        with sqlite3.connect(settings.main_db_path) as conn:
            conn.row_factory = sqlite3.Row
            cur = conn.execute('''
                SELECT * FROM beer_effects 
                WHERE user_id = ? AND expires_at > ?
                ORDER BY expires_at
            ''', (user_id, datetime.now().isoformat()))
            
            effects = []
            for row in cur.fetchall():
                effects.append({
                    'name': row['effect_name'],
                    'effect': row['effect_type'],
                    'value': row['value'],
                    'expires_at': row['expires_at']
                })
            
            return effects
    
    def clean_expired_effects(self, user_id: int):
        """Удаляет истекшие эффекты"""
        with sqlite3.connect(settings.main_db_path) as conn:
            conn.execute(
                'DELETE FROM beer_effects WHERE user_id = ? AND expires_at <= ?',
                (user_id, datetime.now().isoformat())
            )
            conn.commit()


# Глобальный экземпляр сервиса (ленивый)
_dice_service = None

def get_dice_service() -> 'DiceService':
    """Возвращает глобальный экземпляр DiceService (создаёт при первом вызове)"""
    global _dice_service
    if _dice_service is None:
        _dice_service = DiceService()
    return _dice_service

# Для обратной совместимости
dice_service = get_dice_service()