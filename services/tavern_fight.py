"""Сервис драк в таверне — вызовы, бои, награды"""

import uuid
import random
from typing import Optional, Dict, List
from config import settings

DB_FILE = settings.main_db_path


class TavernFightService:
    """Драки в таверне"""

    def get_tavern_players(self, exclude_user_id: int = None) -> List[Dict]:
        """Кто сейчас в таверне"""
        import sqlite3
        with sqlite3.connect(DB_FILE) as conn:
            c = conn.cursor()
            if exclude_user_id:
                c.execute(
                    """SELECT tp.user_id, r.nickname, us.level, us.current_health, us.max_health
                       FROM tavern_players tp
                       JOIN ratings r ON tp.user_id = r.user_id
                       JOIN user_stats us ON tp.user_id = us.user_id
                       WHERE tp.user_id != ?
                       ORDER BY r.nickname""",
                    (exclude_user_id,)
                )
            else:
                c.execute(
                    """SELECT tp.user_id, r.nickname, us.level, us.current_health, us.max_health
                       FROM tavern_players tp
                       JOIN ratings r ON tp.user_id = r.user_id
                       JOIN user_stats us ON tp.user_id = us.user_id
                       ORDER BY r.nickname"""
                )
            return [
                {"user_id": row[0], "nickname": row[1] or f"ID:{row[0]}",
                 "level": row[2] or 1, "hp": row[3] or 50, "max_hp": row[4] or 50}
                for row in c.fetchall()
            ]

    def get_tavern_count(self) -> int:
        import sqlite3
        with sqlite3.connect(DB_FILE) as conn:
            return conn.execute("SELECT COUNT(*) FROM tavern_players").fetchone()[0]

    def join_tavern(self, user_id: int):
        import sqlite3
        with sqlite3.connect(DB_FILE) as conn:
            conn.execute("INSERT OR REPLACE INTO tavern_players (user_id) VALUES (?)", (user_id,))
            conn.commit()

    def leave_tavern(self, user_id: int):
        import sqlite3
        with sqlite3.connect(DB_FILE) as conn:
            conn.execute("DELETE FROM tavern_players WHERE user_id = ?", (user_id,))
            conn.commit()

    def challenge_player(self, challenger_id: int, target_id: int) -> Optional[str]:
        """Бросить вызов. Возвращает fight_id или None"""
        import sqlite3
        # Проверяем что оба в таверне
        with sqlite3.connect(DB_FILE) as conn:
            c = conn.cursor()
            c.execute("SELECT user_id FROM tavern_players WHERE user_id = ?", (target_id,))
            if not c.fetchone():
                return None
            c.execute("SELECT user_id FROM tavern_players WHERE user_id = ?", (challenger_id,))
            if not c.fetchone():
                return None

        fight_id = str(uuid.uuid4())[:8]
        with sqlite3.connect(DB_FILE) as conn:
            conn.execute(
                """INSERT INTO tavern_fights (fight_id, challenger_id, target_id, status)
                   VALUES (?, ?, ?, 'pending')""",
                (fight_id, challenger_id, target_id)
            )
            conn.commit()
        return fight_id

    def get_pending_fight(self, user_id: int) -> Optional[Dict]:
        """Есть ли входящий вызов"""
        import sqlite3
        with sqlite3.connect(DB_FILE) as conn:
            c = conn.cursor()
            c.execute(
                """SELECT f.fight_id, f.challenger_id, r.nickname, us.level
                   FROM tavern_fights f
                   JOIN ratings r ON f.challenger_id = r.user_id
                   JOIN user_stats us ON f.challenger_id = us.user_id
                   WHERE f.target_id = ? AND f.status = 'pending'""",
                (user_id,)
            )
            row = c.fetchone()
            if row:
                return {"fight_id": row[0], "challenger_id": row[1],
                        "challenger_name": row[2] or f"ID:{row[1]}", "challenger_level": row[3] or 1}
        return None

    def accept_fight(self, fight_id: str, target_id: int) -> Optional[Dict]:
        """Принять бой. Возвращает данные боя"""
        import sqlite3
        with sqlite3.connect(DB_FILE) as conn:
            c = conn.cursor()
            c.execute(
                "SELECT challenger_id, target_id FROM tavern_fights WHERE fight_id = ? AND status = 'pending' AND target_id = ?",
                (fight_id, target_id)
            )
            row = c.fetchone()
            if not row:
                return None

            # Получаем статы обоих
            c.execute("SELECT strength, current_health FROM user_stats WHERE user_id = ?", (row[0],))
            c1 = c.fetchone()
            c.execute("SELECT strength, current_health FROM user_stats WHERE user_id = ?", (row[1],))
            c2 = c.fetchone()

            if not c1 or not c2:
                return None

            challenger_hp = c1[1] or 50
            target_hp = c2[1] or 50

            c.execute(
                """UPDATE tavern_fights SET status = 'active',
                   challenger_hp = ?, target_hp = ?
                   WHERE fight_id = ?""",
                (challenger_hp, target_hp, fight_id)
            )
            conn.commit()

            return {
                "fight_id": fight_id,
                "challenger_id": row[0],
                "target_id": row[1],
                "challenger_strength": c1[0] or 5,
                "target_strength": c2[0] or 5,
                "challenger_hp": challenger_hp,
                "target_hp": target_hp,
                "round": 1,
            }

    def get_active_fight(self, fight_id: str) -> Optional[Dict]:
        import sqlite3
        with sqlite3.connect(DB_FILE) as conn:
            c = conn.cursor()
            c.execute(
                """SELECT fight_id, challenger_id, target_id, challenger_hp, target_hp, round
                   FROM tavern_fights WHERE fight_id = ? AND status = 'active'""",
                (fight_id,)
            )
            row = c.fetchone()
            if not row:
                return None
            return {
                "fight_id": row[0], "challenger_id": row[1], "target_id": row[2],
                "challenger_hp": row[3], "target_hp": row[4], "round": row[5]
            }

    def process_punch(self, fight_id: str, attacker_id: int) -> Optional[Dict]:
        """Удар в драке. Возвращает результат раунда"""
        import sqlite3
        fight = self.get_active_fight(fight_id)
        if not fight:
            return None

        with sqlite3.connect(DB_FILE) as conn:
            c = conn.cursor()
            c.execute("SELECT strength FROM user_stats WHERE user_id = ?", (attacker_id,))
            row = c.fetchone()
            attacker_strength = row[0] if row else 5

        # Определяем защитника
        if attacker_id == fight["challenger_id"]:
            defender_id = fight["target_id"]
            defender_hp = fight["target_hp"]
            attacker_hp = fight["challenger_hp"]
        else:
            defender_id = fight["challenger_id"]
            defender_hp = fight["challenger_hp"]
            attacker_hp = fight["target_hp"]

        # Бросок атаки
        attack_roll = random.randint(1, 6) + attacker_strength

        # Защитник тоже бросает
        with sqlite3.connect(DB_FILE) as conn:
            c = conn.cursor()
            c.execute("SELECT strength FROM user_stats WHERE user_id = ?", (defender_id,))
            row = c.fetchone()
            defender_strength = row[0] if row else 5
        defend_roll = random.randint(1, 6) + defender_strength

        # Урон
        if attack_roll > defend_roll:
            damage = attack_roll - defend_roll
            defender_hp = max(0, defender_hp - damage)
            hit = True
        else:
            damage = 0
            hit = False

        # Обновляем HP
        with sqlite3.connect(DB_FILE) as conn:
            c = conn.cursor()
            if attacker_id == fight["challenger_id"]:
                c.execute(
                    "UPDATE tavern_fights SET challenger_hp = ?, target_hp = ?, round = round + 1 WHERE fight_id = ?",
                    (attacker_hp, defender_hp, fight_id)
                )
            else:
                c.execute(
                    "UPDATE tavern_fights SET challenger_hp = ?, target_hp = ?, round = round + 1 WHERE fight_id = ?",
                    (defender_hp, attacker_hp, fight_id)
                )
            conn.commit()

        winner_id = None
        if defender_hp <= 0:
            winner_id = attacker_id

        return {
            "fight_id": fight_id,
            "attacker_id": attacker_id,
            "defender_id": defender_id,
            "attack_roll": attack_roll,
            "defend_roll": defend_roll,
            "damage": damage,
            "hit": hit,
            "attacker_hp": attacker_hp if attacker_id == fight["challenger_id"] else defender_hp,
            "defender_hp": defender_hp if attacker_id != fight["challenger_id"] else attacker_hp,
            "round": fight["round"] + 1,
            "winner_id": winner_id,
            "max_rounds": 3,
        }

    def resolve_fight(self, fight_id: str, winner_id: int) -> Dict:
        """Завершить драку и выдать награду"""
        import sqlite3
        loser_id = None
        with sqlite3.connect(DB_FILE) as conn:
            c = conn.cursor()
            c.execute(
                "SELECT challenger_id, target_id FROM tavern_fights WHERE fight_id = ?",
                (fight_id,)
            )
            row = c.fetchone()
            if row:
                loser_id = row[0] if row[1] == winner_id else row[1]

            c.execute(
                "UPDATE tavern_fights SET status = 'finished', winner_id = ? WHERE fight_id = ?",
                (winner_id, fight_id)
            )
            conn.commit()

        # Награда победителю
        crumbs_stolen = random.randint(10, 50)
        xp_earned = random.randint(5, 20)

        # Случайный ресурс с проигравшего
        from core.items.resources import RESOURCES
        possible_resources = [rid for rid, data in RESOURCES.items()
                              if data.get("rarity") in ["common", "rare"]]
        resource_stolen = random.choice(possible_resources) if possible_resources and random.random() < 0.3 else None

        # Выдача наград
        from services.inventory import inventory_service
        inventory_service.add_crumbs(winner_id, crumbs_stolen)
        inventory_service.spend_crumbs(loser_id, crumbs_stolen)
        inventory_service.add_xp(winner_id, xp_earned)

        if resource_stolen:
            inventory_service.add_item(winner_id, resource_stolen)

        # Обновляем HP победителя в user_stats
        with sqlite3.connect(DB_FILE) as conn:
            c = conn.cursor()
            c.execute("SELECT challenger_hp, target_hp FROM tavern_fights WHERE fight_id = ?", (fight_id,))
            row = c.fetchone()
            final_hp = row[0] if winner_id == row[0] else row[1] if row else 50
            c.execute("UPDATE user_stats SET current_health = ? WHERE user_id = ?", (max(1, final_hp), winner_id))
            conn.commit()

        result = {
            "winner_id": winner_id,
            "loser_id": loser_id,
            "crumbs_stolen": crumbs_stolen,
            "xp_earned": xp_earned,
            "resource_stolen": resource_stolen,
        }

        if resource_stolen:
            result["resource_name"] = RESOURCES.get(resource_stolen, {}).get("name", "Ресурс")
            result["resource_icon"] = RESOURCES.get(resource_stolen, {}).get("icon", "📦")

        return result


tavern_fight_service = TavernFightService()