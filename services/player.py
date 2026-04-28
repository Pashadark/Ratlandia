"""Сервис игрока — создание, статы, уровни, классы, рейтинг"""

from typing import Optional, Dict, List
from core.database import db_ratings


class PlayerService:
    """Работа с игроками"""

    def get_player(self, user_id: int) -> Optional[Dict]:
        """Получить данные игрока"""
        return db_ratings.fetch_one(
            "SELECT * FROM ratings WHERE user_id = ?",
            (user_id,)
        )

    def create_player(self, user_id: int, name: str, nickname: str = None) -> Dict:
        """Создать нового игрока"""
        db_ratings.execute(
            "INSERT OR IGNORE INTO ratings (user_id, name, nickname) VALUES (?, ?, ?)",
            (user_id, name, nickname)
        )
        db_ratings.execute(
            "INSERT OR IGNORE INTO user_currency (user_id, crumbs) VALUES (?, 100)",
            (user_id,)
        )
        db_ratings.execute(
            "INSERT OR IGNORE INTO user_xp (user_id, xp, level, stat_points) VALUES (?, 0, 1, 0)",
            (user_id,)
        )
        return self.get_player(user_id)

    def get_crumbs(self, user_id: int) -> int:
        return db_ratings.get_crumbs(user_id)

    def add_crumbs(self, user_id: int, amount: int) -> int:
        return db_ratings.add_crumbs(user_id, amount)

    def spend_crumbs(self, user_id: int, amount: int) -> bool:
        return db_ratings.spend_crumbs(user_id, amount)

    def get_xp(self, user_id: int) -> int:
        return db_ratings.get_xp(user_id)

    def add_xp(self, user_id: int, amount: int) -> int:
        return db_ratings.add_xp(user_id, amount)

    def get_level(self, user_id: int) -> int:
        return db_ratings.get_level(user_id)

    def set_level(self, user_id: int, level: int) -> None:
        db_ratings.set_level(user_id, level)

    def get_stat_points(self, user_id: int) -> int:
        return db_ratings.get_stat_points(user_id)

    def add_stat_points(self, user_id: int, amount: int) -> None:
        db_ratings.add_stat_points(user_id, amount)

    def spend_stat_points(self, user_id: int, amount: int) -> bool:
        return db_ratings.spend_stat_points(user_id, amount)

    def get_top_players(self, limit: int = 10) -> List[Dict]:
        return db_ratings.get_top_players(limit)

    def update_nickname(self, user_id: int, nickname: str) -> None:
        db_ratings.execute(
            "UPDATE ratings SET nickname = ? WHERE user_id = ?",
            (nickname, user_id)
        )

    def player_exists(self, user_id: int) -> bool:
        return self.get_player(user_id) is not None


# Глобальный экземпляр
player_service = PlayerService()