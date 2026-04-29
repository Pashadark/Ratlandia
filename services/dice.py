"""Сервис таверны — кости, ставки, пиво, турниры"""
import sqlite3
import random
from typing import Optional, Dict, List
from datetime import datetime, timedelta
from config import settings
from core.dice.models import BetResult, DiceGameResult, PlayerStats, GameMode

DB_FILE = settings.main_db_path


class DiceService:
    """Работа с костями и таверной"""

    def get_crumbs(self, user_id: int) -> int:
        from services.inventory import inventory_service
        return inventory_service.get_crumbs(user_id)

    def get_player_stats(self, user_id: int) -> PlayerStats:
        with sqlite3.connect(DB_FILE) as conn:
            c = conn.cursor()
            c.execute('''SELECT total_games, total_wins, total_losses, total_draws,
                         total_crumbs_won, total_crumbs_lost, best_win_streak,
                         current_win_streak, current_lose_streak,
                         luck_points, max_luck, daily_bonus_available
                         FROM dice_stats WHERE user_id = ?''', (user_id,))
            row = c.fetchone()
            if row:
                return PlayerStats(
                    user_id=user_id,
                    total_games=row[0], total_wins=row[1], total_losses=row[2],
                    total_draws=row[3], total_crumbs_won=row[4], total_crumbs_lost=row[5],
                    best_win_streak=row[6], current_win_streak=row[7],
                    current_lose_streak=row[8], luck_points=row[9],
                    max_luck=row[10], daily_bonus_available=bool(row[11])
                )
        return PlayerStats(user_id=user_id)

    def spend_crumbs(self, user_id: int, amount: int) -> bool:
        from services.inventory import inventory_service
        return inventory_service.spend_crumbs(user_id, amount)

    def add_crumbs(self, user_id: int, amount: int):
        from services.inventory import inventory_service
        inventory_service.add_crumbs(user_id, amount)

    def format_stats_message(self, user_id: int) -> str:
        stats = self.get_player_stats(user_id)
        crumbs = self.get_crumbs(user_id)
        import random
        npcs = [
            "_За стойкой сидит угрюмый Шныр и протирает кружки._",
            "_Старая Ильяска подмигивает тебе из-за стойки._",
            "_В углу две крысы играют в кости и громко спорят._",
            "_У камина дремлет пьяный Крысолов, обнимая пустую кружку._",
        ]
        total_profit = stats.total_crumbs_won - stats.total_crumbs_lost
        profit_emoji = "📈" if total_profit >= 0 else "📉"
        return (
            f"*Таверна «Крысиный хвост»*\n\n"
            f"_Тёплый свет масляных ламп, запах эля и жареного сыра. "
            f"В углу крысы бросают кости, кто-то спорит о ставках._\n"
            f"{random.choice(npcs)}\n\n"
            f"🧀 Крошки: *{crumbs:,}*\n"
            f"🎯 Игр: *{stats.total_games}* | Побед: *{stats.total_wins}* ({stats.win_rate:.1f}%)\n"
            f"💸 Поражений: *{stats.total_losses}* | Ничьих: *{stats.total_draws}*\n"
            f"🔥 Серия побед: *{stats.current_win_streak}* | 💀 Поражений подряд: *{stats.current_lose_streak}*\n"
            f"📊 Выиграно: *{stats.total_crumbs_won:,}* 🧀 | Проиграно: *{stats.total_crumbs_lost:,}* 🧀\n"
            f"{profit_emoji} Итог: *{total_profit:+,}* 🧀"
        )

    def buy_beer(self, user_id: int, beer_cost: int = 50) -> tuple:
        if not self.spend_crumbs(user_id, beer_cost):
            return False, None, "❌ Недостаточно крошек!"
        effects = [
            {"name": "🥊 Боевое пиво", "desc": "+1 к урону в туннелях на 1 час",
             "effect": "tunnel_damage", "value": 1, "icon": "🍺", "duration_hours": 1},
            {"name": "🍀 Пиво удачи", "desc": "+10% к находкам в туннелях на 1 час",
             "effect": "tunnel_find", "value": 10, "icon": "🍺", "duration_hours": 1},
            {"name": "🛡️ Пиво стойкости", "desc": "+15 к макс. HP на 1 час",
             "effect": "max_health", "value": 15, "icon": "🍺", "duration_hours": 1},
            {"name": "⚡ Пиво скорости", "desc": "+5% к уклонению на 1 час",
             "effect": "dodge", "value": 5, "icon": "🍺", "duration_hours": 1},
        ]
        effect = random.choice(effects)
        from services.inventory import inventory_service
        inventory_service.add_temp_effect(user_id, effect, effect.get("duration_hours", 1))
        return True, effect, "🍺 Пиво выпито!"

    def get_beer_effects_text(self, user_id: int) -> str:
        from services.inventory import inventory_service
        effects = inventory_service.get_active_temp_effects(user_id)
        if not effects:
            return ""
        text = "\n\n🍺 *Активные эффекты пива:*\n"
        for e in effects:
            text += f"  {e['icon']} {e['desc']}\n"
        return text

    def claim_daily_bonus(self, user_id: int):
        with sqlite3.connect(DB_FILE) as conn:
            c = conn.cursor()
            c.execute('UPDATE dice_stats SET daily_bonus_available = 0 WHERE user_id = ?', (user_id,))
            conn.commit()

    def _save_game_result(self, result: DiceGameResult):
        with sqlite3.connect(DB_FILE) as conn:
            c = conn.cursor()
            c.execute('''INSERT INTO dice_games (user_id, mode, player_roll, shadow_roll,
                         bet_amount, win_amount, is_win, is_critical, timestamp)
                         VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                      (result.user_id, result.mode.value, result.player_roll,
                       result.shadow_roll, result.bet.bet_amount, result.bet.win_amount,
                       result.bet.is_win, result.bet.is_critical,
                       result.timestamp.isoformat()))
            conn.commit()

    def _update_player_stats(self, user_id: int, result: DiceGameResult):
        with sqlite3.connect(DB_FILE) as conn:
            c = conn.cursor()
            if result.bet.is_win:
                c.execute('''UPDATE dice_stats SET
                             total_games = total_games + 1,
                             total_wins = total_wins + 1,
                             total_crumbs_won = total_crumbs_won + ?,
                             current_win_streak = current_win_streak + 1,
                             best_win_streak = MAX(best_win_streak, current_win_streak + 1),
                             current_lose_streak = 0
                             WHERE user_id = ?''',
                          (result.bet.win_amount, user_id))
                # Начислить выигрыш
                self.add_crumbs(user_id, result.bet.win_amount)
            elif result.bet.is_draw:
                c.execute('''UPDATE dice_stats SET
                             total_games = total_games + 1,
                             total_draws = total_draws + 1,
                             current_win_streak = 0,
                             current_lose_streak = 0
                             WHERE user_id = ?''', (user_id,))
                # Возврат ставки при ничьей
                self.add_crumbs(user_id, result.bet.bet_amount)
            else:
                c.execute('''UPDATE dice_stats SET
                             total_games = total_games + 1,
                             total_losses = total_losses + 1,
                             total_crumbs_lost = total_crumbs_lost + ?,
                             current_lose_streak = current_lose_streak + 1,
                             current_win_streak = 0
                             WHERE user_id = ?''',
                          (result.bet.bet_amount, user_id))
                # Крошки уже сняты при ставке, не снимаем повторно
            conn.commit()

    def get_tournament_leaders(self, limit: int = 10) -> List[Dict]:
        with sqlite3.connect(DB_FILE) as conn:
            c = conn.cursor()
            c.execute('''SELECT ds.user_id, r.nickname, ds.total_games, ds.total_wins,
                         ds.total_crumbs_won, ds.best_win_streak
                         FROM dice_stats ds
                         JOIN ratings r ON ds.user_id = r.user_id
                         ORDER BY ds.total_crumbs_won DESC LIMIT ?''', (limit,))
            return [
                {"user_name": row[1] or f"ID:{row[0]}", "games_played": row[2],
                 "wins": row[3], "total_crumbs_won": row[4], "best_streak": row[5]}
                for row in c.fetchall()
            ]


dice_service = DiceService()