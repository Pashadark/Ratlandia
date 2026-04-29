"""Сервис бегов тараканов — ставки, забеги, анимация"""

import uuid
import random
from typing import Optional, Dict, List
from config import settings

DB_FILE = settings.main_db_path

# Тараканы
COCKROACHES = [
    {"id": "rusher", "name": "⚡ Шустрик", "color": "⚡", "speed": 2},
    {"id": "whiskers", "name": "🔥 Усач", "color": "🔥", "speed": 1},
    {"id": "sprinter", "name": "💨 Прух", "color": "💨", "speed": 2},
    {"id": "hexapod", "name": "🏆 Шестиногий", "color": "🏆", "speed": 1},
]


class TavernRaceService:
    """Бега тараканов"""

    def create_race(self, user_id: int, bet: int, roach_id: str) -> Optional[str]:
        """Создать новый забег. Возвращает race_id"""
        import sqlite3
        from services.inventory import inventory_service

        if not inventory_service.spend_crumbs(user_id, bet):
            return None

        valid_ids = [r["id"] for r in COCKROACHES]
        if roach_id not in valid_ids:
            return None

        race_id = str(uuid.uuid4())[:8]

        with sqlite3.connect(DB_FILE) as conn:
            c = conn.cursor()
            c.execute(
                """INSERT INTO tavern_races (race_id, user_id, bet, roach_id, status, positions)
                   VALUES (?, ?, ?, ?, 'active', '{"rusher":0,"whiskers":0,"sprinter":0,"hexapod":0}')""",
                (race_id, user_id, bet, roach_id)
            )
            conn.commit()

        return race_id

    def get_race(self, race_id: str) -> Optional[Dict]:
        import sqlite3, json
        with sqlite3.connect(DB_FILE) as conn:
            c = conn.cursor()
            c.execute(
                "SELECT race_id, user_id, bet, roach_id, status, positions FROM tavern_races WHERE race_id = ?",
                (race_id,)
            )
            row = c.fetchone()
            if not row:
                return None
            return {
                "race_id": row[0], "user_id": row[1], "bet": row[2],
                "roach_id": row[3], "status": row[4],
                "positions": json.loads(row[5]) if row[5] else {}
            }

    def process_race_step(self, race_id: str) -> Dict:
        """Один шаг забега — все тараканы бросают d6 + speed"""
        race = self.get_race(race_id)
        if not race or race["status"] != "active":
            return {"finished": True, "winner": None}

        import sqlite3, json
        positions = race["positions"]

        # Каждый таракан двигается
        for roach in COCKROACHES:
            roll = random.randint(1, 6)
            step = roll + roach["speed"]
            positions[roach["id"]] = positions.get(roach["id"], 0) + step

        # Проверяем победителя
        winner_id = None
        for roach_id, pos in positions.items():
            if pos >= 20:
                winner_id = roach_id
                break

        new_status = "active" if not winner_id else "finished"

        with sqlite3.connect(DB_FILE) as conn:
            conn.execute(
                "UPDATE tavern_races SET positions = ?, status = ? WHERE race_id = ?",
                (json.dumps(positions), new_status, race_id)
            )
            conn.commit()

        return {
            "race_id": race_id,
            "positions": positions,
            "finished": winner_id is not None,
            "winner_id": winner_id,
            "user_roach": race["roach_id"],
            "bet": race["bet"],
            "user_id": race["user_id"],
        }

    def get_race_result_text(self, race_data: Dict) -> str:
        """Форматирует результат забега"""
        pos = race_data["positions"]
        user_roach = race_data["user_roach"]
        bet = race_data["bet"]

        # Сортируем по позиции
        sorted_roaches = sorted(pos.items(), key=lambda x: x[1], reverse=True)
        winner_id = sorted_roaches[0][0] if sorted_roaches else None
        winner = next((r for r in COCKROACHES if r["id"] == winner_id), None)

        user_won = (winner_id == user_roach)
        win_amount = bet * 3 if user_won else 0

        # Начисляем выигрыш
        if user_won:
            from services.inventory import inventory_service
            inventory_service.add_crumbs(race_data["user_id"], win_amount)

        # Прогресс-бары
        text = f"🪳 *ЗАБЕГ ЗАВЕРШЁН!*\n\n"
        for roach_id, position in sorted_roaches:
            roach = next((r for r in COCKROACHES if r["id"] == roach_id), None)
            if roach:
                bar_len = 20
                filled = min(bar_len, int(position / 20 * bar_len))
                bar = "█" * filled + "░" * (bar_len - filled)
                medal = "🥇" if roach_id == winner_id else ""
                marker = " ← *твоя ставка*" if roach_id == user_roach else ""
                text += f"{roach['name']} {medal}\n{bar} {position}/20{marker}\n\n"

        if user_won:
            text += f"🎉 *ПОБЕДА!* Твой таракан пришёл первым!\n💰 Выигрыш: *+{win_amount}* 🧀"
        else:
            text += f"💸 Твой таракан проиграл.\nПотеряно: *{bet}* 🧀"

        return text

    def get_race_positions_text(self, race_data: Dict) -> str:
        """Текущие позиции для анимации"""
        pos = race_data["positions"]
        user_roach = race_data["user_roach"]

        sorted_roaches = sorted(pos.items(), key=lambda x: x[1], reverse=True)

        text = f"🪳 *ЗАБЕГ!*\n\n"
        for roach_id, position in sorted_roaches:
            roach = next((r for r in COCKROACHES if r["id"] == roach_id), None)
            if roach:
                bar_len = 20
                filled = min(bar_len, int(position / 20 * bar_len))
                bar = "█" * filled + "░" * (bar_len - filled)
                marker = " ← *твоя*" if roach_id == user_roach else ""
                text += f"{roach['name']}{marker}\n{bar} {position}/20\n\n"

        return text


tavern_race_service = TavernRaceService()