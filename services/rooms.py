"""Комнаты и события режима Туннели"""

import random
from typing import Dict, Optional, Tuple

from config import settings
from services.game import (
    get_tunnel_run, update_tunnel_run, advance_room, end_tunnel_run,
    add_run_loot, get_room_type, open_treasure_chest,
    get_random_blessing, apply_blessing_effect
)
from services.monsters import (
    get_monster, get_random_monster, TUNNEL_MONSTERS
)


class RoomService:
    """Логика комнат и событий в туннелях"""

    def enter_room(self, user_id: int) -> Dict:
        """
        Вход в комнату. Возвращает данные для отображения.
        {
            "type": "monster" | "treasure" | "altar" | "trap" | "empty" | "boss",
            "room_number": int,
            "text": str,
            "monster": dict | None,
            "actions": list  # доступные действия
        }
        """
        run_data = get_tunnel_run(user_id)
        if not run_data:
            return {"type": "error", "text": "Нет активного забега"}

        current_room = run_data["current_room"]

        if current_room == 20:
            return self._enter_boss_room(user_id, run_data)

        room_type = get_room_type()

        if room_type == "monster":
            return self._enter_monster_room(run_data, current_room)
        elif room_type == "treasure":
            return self._enter_treasure_room(run_data)
        elif room_type == "altar":
            return self._enter_altar_room(run_data)
        elif room_type == "trap":
            return self._enter_trap_room(user_id, run_data)
        else:
            return self._enter_empty_room(user_id, run_data, current_room)

    def _enter_boss_room(self, user_id: int, run_data: Dict) -> Dict:
        from services.game import get_boss_for_room
        boss_id = get_boss_for_room(run_data.get("total_runs", 0))
        boss = get_monster(boss_id)
        return {
            "type": "boss",
            "room_number": 20,
            "text": f"🚪 Комната 20 — Логово босса\n\n{boss['desc']}",
            "monster": boss,
            "boss_id": boss_id,
            "actions": ["fight_boss", "invite_friend", "flee"]
        }

    def _enter_monster_room(self, run_data: Dict, room_num: int) -> Dict:
        if room_num <= 6:
            level = 1
        elif room_num <= 12:
            level = 2
        elif room_num <= 18:
            level = 3
        else:
            level = 4

        monster = get_random_monster(level)
        return {
            "type": "monster",
            "room_number": room_num,
            "text": f"🚪 Комната {room_num}/20\n\nВ углу ты замечаешь движение! Это {monster['name']}!",
            "monster": monster,
            "actions": ["fight", "flee"]
        }

    def _enter_treasure_room(self, run_data: Dict) -> Dict:
        return {
            "type": "treasure",
            "room_number": run_data["current_room"],
            "text": "Ты находишь комнату, полную старых сундуков! Какой откроешь?",
            "actions": ["chest_left", "chest_middle", "chest_right", "skip"]
        }

    def _enter_altar_room(self, run_data: Dict) -> Dict:
        return {
            "type": "altar",
            "room_number": run_data["current_room"],
            "text": f"Древний алтарь. Пожертвуй крошки — получи благословение.\n🧀 В мешке: {run_data['crumbs_collected']}",
            "actions": ["offer", "skip"]
        }

    def _enter_trap_room(self, user_id: int, run_data: Dict) -> Dict:
        from services.character import get_character_stats, take_damage
        stats = get_character_stats(user_id)
        dodge_chance = stats["agility"] * 5
        dodged = random.randint(1, 100) <= dodge_chance

        if dodged:
            return {
                "type": "trap",
                "room_number": run_data["current_room"],
                "text": "Ты замечаешь ловушку и вовремя отпрыгиваешь!",
                "dodged": True,
                "actions": ["next_room"]
            }
        else:
            damage = random.randint(5, 15)
            new_hp = take_damage(user_id, damage)
            result = {
                "type": "trap",
                "room_number": run_data["current_room"],
                "text": f"Ты наступаешь на скрытую плиту! 💔 -{damage} HP\n❤️ Здоровье: {new_hp}/{stats['max_health']}",
                "dodged": False,
                "damage": damage,
                "new_hp": new_hp,
                "actions": ["next_room"]
            }
            if new_hp <= 0:
                result["died"] = True
                result["actions"] = ["go_home"]
            return result

    def _enter_empty_room(self, user_id: int, run_data: Dict, room_num: int) -> Dict:
        from services.character import get_character_stats
        stats = get_character_stats(user_id)
        find_chance = stats["intelligence"] * 3
        extra_text = ""

        if random.randint(1, 100) <= find_chance:
            crumbs_found = random.randint(3, 8)
            new_crumbs = run_data["crumbs_collected"] + crumbs_found
            update_tunnel_run(user_id, crumbs_collected=new_crumbs)
            extra_text = f"\n\nТы находишь {crumbs_found} крошек в углу!"

        return {
            "type": "empty",
            "room_number": room_num,
            "text": f"Комната пуста. Только пыль и паутина.{extra_text}",
            "actions": ["next_room"]
        }

    def handle_chest(self, user_id: int, choice: str) -> Dict:
        """Открытие сундука в сокровищнице"""
        run_data = get_tunnel_run(user_id)
        reward_type, amount, item_id, damage = open_treasure_chest(choice)

        if reward_type == "crumbs":
            new_crumbs = run_data["crumbs_collected"] + amount
            update_tunnel_run(user_id, crumbs_collected=new_crumbs)
            return {
                "type": "reward",
                "text": f"📦 Внутри {amount} крошек!\n🧀 Всего: {new_crumbs}",
                "crumbs": amount
            }
        elif reward_type == "item":
            return {
                "type": "item",
                "text": "📦 Сундук открыт! Внутри предмет!",
                "need_random_item": True
            }
        else:
            from services.character import get_character_stats, take_damage
            new_hp = take_damage(user_id, damage)
            stats = get_character_stats(user_id)
            result = {
                "type": "trap",
                "text": f"📦 Ловушка! -{damage} HP\n❤️ Здоровье: {new_hp}/{stats['max_health']}",
                "damage": damage,
                "new_hp": new_hp
            }
            if new_hp <= 0:
                result["died"] = True
            return result

    def handle_altar(self, user_id: int, crumbs_available: int) -> Dict:
        """Пожертвование на алтаре"""
        if crumbs_available < 10:
            return {"type": "error", "text": "Недостаточно крошек! Нужно 10."}

        from services.inventory import inventory_service
        inventory_service.spend_crumbs(user_id, 10)

        run_data = get_tunnel_run(user_id)
        blessing = get_random_blessing()
        result_text, health_updated, new_hp = apply_blessing_effect(user_id, blessing, run_data)

        return {
            "type": "blessing",
            "text": result_text,
            "blessing": blessing,
            "health_updated": health_updated,
            "new_hp": new_hp
        }

    def go_next_room(self, user_id: int) -> Optional[Dict]:
        """Переход в следующую комнату. Возвращает данные комнаты или None если забег окончен"""
        advance_room(user_id)
        run_data = get_tunnel_run(user_id)
        if run_data and run_data["current_room"] > 20:
            return self._finish_run(user_id)
        return self.enter_room(user_id)

    def skip_room(self, user_id: int) -> Optional[Dict]:
        """Пропуск комнаты"""
        advance_room(user_id)
        run_data = get_tunnel_run(user_id)
        if run_data and run_data["current_room"] > 20:
            return self._finish_run(user_id)
        return self.enter_room(user_id)

    def _finish_run(self, user_id: int) -> Dict:
        """Успешное завершение забега"""
        result = end_tunnel_run(user_id, died=False)
        from services.inventory import inventory_service
        inventory_service.add_crumbs(user_id, result['crumbs'])
        return {
            "type": "finish",
            "text": f"🎉 Забег завершён!\n🧀 Крошек: {result['crumbs']}\n✨ Опыта: {result['xp']}",
            "crumbs": result['crumbs'],
            "xp": result['xp']
        }

    def go_home(self, user_id: int) -> Dict:
        """Добровольное возвращение домой"""
        run_data = get_tunnel_run(user_id)
        if not run_data:
            return {"type": "error", "text": "Нет активного забега"}

        crumbs_lost = int(run_data["crumbs_collected"] * 0.3)
        final_crumbs = run_data["crumbs_collected"] - crumbs_lost
        xp = run_data["xp_collected"]

        end_tunnel_run(user_id, died=False)
        from services.inventory import inventory_service
        inventory_service.add_crumbs(user_id, final_crumbs)
        inventory_service.add_xp(user_id, xp)

        return {
            "type": "go_home",
            "text": f"🏠 Возвращение домой\n🧀 Крошек: {final_crumbs} (потеряно {crumbs_lost})\n✨ Опыта: {xp}",
            "crumbs": final_crumbs,
            "xp": xp
        }


# Глобальный экземпляр
room_service = RoomService()