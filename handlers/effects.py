"""Обработка эффектов предметов для Ратляндии"""

import random
from typing import Dict, Any, Optional
from datetime import datetime, timedelta

from handlers.items import EQUIPMENT, CONSUMABLES
from handlers.inventory import add_xp, get_random_item, add_item, get_equipment, get_active_temp_effects


def get_player_effects(user_id: int, player_role: str = None) -> Dict[str, Any]:
    """Получить все активные эффекты игрока от надетой экипировки и временных эффектов"""
    equipment = get_equipment(user_id)
    effects = {}
    
    # Эффекты экипировки
    for slot, item_id in equipment.items():
        if item_id in EQUIPMENT:
            item = EQUIPMENT[item_id]
            
            # 🆕 ИСПРАВЛЕНО: если player_role == "all" или None — берем ВСЕ предметы!
            if player_role and player_role != "all":
                if item["role"] not in [player_role, "all"]:
                    continue
            
            # Добавляем эффекты
            for effect_name, effect_value in item.get("effect", {}).items():
                if effect_name in effects:
                    if isinstance(effect_value, bool):
                        effects[effect_name] = effects[effect_name] or effect_value
                    elif isinstance(effect_value, (int, float)):
                        effects[effect_name] = effects[effect_name] + effect_value
                    else:
                        effects[effect_name] = effect_value
                else:
                    effects[effect_name] = effect_value
    
    # 🆕 ОБРАБОТКА all_stats — РАСКЛАДЫВАЕМ НА КОНКРЕТНЫЕ ХАРАКТЕРИСТИКИ
    all_stats_bonus = effects.pop("all_stats", 0)
    if all_stats_bonus > 0:
        effects["strength"] = effects.get("strength", 0) + all_stats_bonus
        effects["agility"] = effects.get("agility", 0) + all_stats_bonus
        effects["intelligence"] = effects.get("intelligence", 0) + all_stats_bonus
    
    # 🆕 ВРЕМЕННЫЕ ЭФФЕКТЫ ИЗ БД
    try:
        temp_effects = get_active_temp_effects(user_id)
        for temp in temp_effects:
            eff_name = temp['effect']
            eff_value = temp.get('value', 1)
            if eff_name in effects:
                if isinstance(eff_value, (int, float)):
                    effects[eff_name] = effects[eff_name] + eff_value
                elif isinstance(eff_value, bool):
                    effects[eff_name] = effects[eff_name] or eff_value
                else:
                    effects[eff_name] = eff_value
            else:
                effects[eff_name] = eff_value
    except Exception as e:
        pass  # Если таблицы ещё нет или другая ошибка - игнорируем
    
    # Обработка случайного эффекта (шутовской колпак)
    if effects.get("random_effect"):
        random_eff = get_random_effect()
        for k, v in random_eff.items():
            if k in effects:
                if isinstance(v, (int, float)):
                    effects[k] = effects[k] + v
                else:
                    effects[k] = effects[k] or v
            else:
                effects[k] = v
    
    # Обработка эффекта хаоса (посох хаоса)
    if effects.get("chaos_effect"):
        effects[get_chaos_effect()] = True
    
    return effects


def apply_consumable_effect(game: Any, user_id: int, item_id: str, context: Any = None) -> str:
    """Применить эффект расходника. Возвращает сообщение о результате."""
    
    item = CONSUMABLES.get(item_id, {})
    effect = item.get("effect", "")
    value = item.get("value", 0)
    
    # ========== XP ЭФФЕКТЫ ==========
    if effect == "xp_boost":
        add_xp(user_id, value)
        return f"✨ +{value} XP!"
    
    elif effect == "level_up":
        from handlers.inventory import get_level
        current_level = get_level(user_id)
        xp_needed = (current_level + 1) * 100
        add_xp(user_id, xp_needed)
        return "⭐ Уровень повышен!"
    
    elif effect == "restore_xp":
        add_xp(user_id, value)
        return f"✨ +{value} XP!"
    
    elif effect == "jackpot":
        add_xp(user_id, 500)
        new_item = get_random_item("all")
        if new_item:
            add_item(user_id, new_item)
        return "🏆 +500 XP и случайный предмет!"
    
    elif effect == "team_xp_boost":
        if game:
            for pid in game.players:
                if game.players[pid]["alive"] and "МЫШЬ" in game.players[pid]["role"]:
                    add_xp(pid, value)
            return f"🧀 Все Мыши получили +{value} XP!"
        add_xp(user_id, value)
        return f"✨ +{value} XP!"
    
    # ========== ИГРОВЫЕ ЭФФЕКТЫ ==========
    elif effect == "delayed_kill":
        if not hasattr(game, 'delayed_kills'):
            game.delayed_kills = []
        if game.night_kill:
            game.delayed_kills.append(game.night_kill)
        return "⏳ Яд подействует после дня..."
    
    elif effect == "skip_voting":
        game.skip_next_voting = True
        return "💨 Голосование следующего дня отменено!"
    
    elif effect == "cancel_voting":
        game.skip_next_voting = True
        game.phase = "day"
        return "📜👑 Указ Короля! Голосование отменено!"
    
    elif effect == "reveal_role":
        return "🔮 Выбери игрока для проверки"
    
    elif effect == "resurrect":
        return "🍪 Выбери кого воскресить"
    
    elif effect == "day_time_boost":
        if not hasattr(game, 'day_time_bonus'):
            game.day_time_bonus = 0
        game.day_time_bonus += value
        return f"⏰ +{value} сек к обсуждению!"
    
    elif effect == "global_day_boost":
        if not hasattr(game, 'day_time_bonus'):
            game.day_time_bonus = 0
        game.day_time_bonus += value
        return f"☕ +{value} сек обсуждения для всех!"
    
    elif effect == "see_rat_target":
        if game.rat_id and game.night_kill:
            target_name = game.players[game.night_kill]["name"]
            return f"👁️ Крыса выбрала целью: {target_name}"
        return "👁️ Крыса никого не выбрала"
    
    elif effect == "trap_rat":
        if not hasattr(game, 'trap_set'):
            game.trap_set = {}
        game.trap_set[user_id] = True
        return "🪤 Крысоловка установлена!"
    
    elif effect == "perfect_trap":
        if not hasattr(game, 'perfect_trap_set'):
            game.perfect_trap_set = {}
        game.perfect_trap_set[user_id] = True
        return "🪤✨ ИДЕАЛЬНАЯ крысоловка установлена! Крыса гарантированно умрёт!"
    
    elif effect == "double_xp_next_game":
        if not hasattr(game, 'double_xp_players'):
            game.double_xp_players = []
        game.double_xp_players.append(user_id)
        return "🧀🧀 Следующая игра принесёт x2 опыта!"
    
    elif effect == "guaranteed_legendary":
        if not hasattr(game, 'guaranteed_legendary'):
            game.guaranteed_legendary = []
        game.guaranteed_legendary.append(user_id)
        return "🍀 Следующая победа гарантирует легендарный предмет!"
    
    elif effect == "dead_message":
        if not hasattr(game, 'dead_messages_allowed'):
            game.dead_messages_allowed = {}
        game.dead_messages_allowed[user_id] = 1
        return "📜 Ты сможешь отправить сообщение после смерти!"
    
    elif effect == "next_night_double":
        if not hasattr(game, 'double_kill_next'):
            game.double_kill_next = {}
        game.double_kill_next[user_id] = True
        return "🪈 Следующей ночью сможешь убить двоих!"
    
    elif effect == "summon_rat":
        if not hasattr(game, 'double_kill_next'):
            game.double_kill_next = {}
        game.double_kill_next[user_id] = True
        return "📯 Крысиный зов! Следующей ночью убьёшь двоих!"
    
    elif effect == "russian_roulette":
        return "🪤 Выбери цель для мышеловки"
    
    elif effect == "reflect_kill":
        if not hasattr(game, 'reflect_shield'):
            game.reflect_shield = {}
        game.reflect_shield[user_id] = True
        return "🪞 Атака Крысы будет отражена!"
    
    elif effect == "night_invisible":
        if not hasattr(game, 'night_invisible'):
            game.night_invisible = []
        game.night_invisible.append(user_id)
        return "🧪 Ты невидим для Крысы этой ночью!"
    
    elif effect == "love_bond":
        return "💕 Выбери двух игроков для связи"
    
    elif effect == "berserk_kill":
        if not hasattr(game, 'berserk_mode'):
            game.berserk_mode = {}
        game.berserk_mode[user_id] = True
        return "😤 Режим берсерка активирован! Убьёшь двоих, но роль раскроется!"
    
    elif effect == "check_dead":
        return "💧 Выбери мёртвого игрока для проверки"
    
    elif effect == "track_player":
        return "📡 Выбери игрока для отслеживания"
    
    elif effect == "sleep_victim":
        if game.night_kill and game.night_kill in game.players:
            game.players[game.night_kill]["silenced"] = True
            return f"😴 {game.players[game.night_kill]['name']} проспит голосование!"
        return "😴 Жертва уснёт"
    
    elif effect == "random_silence":
        if game:
            alive = game.get_alive_players()
            if alive:
                target = random.choice(alive)
                game.players[target]["silenced"] = True
                return f"🤫 {game.players[target]['name']} не сможет говорить!"
        return "🤫 Случайный игрок замолчал!"
    
    elif effect == "curse_death":
        return "🪆 Выбери цель для проклятия"
    
    elif effect == "cure_poison":
        if hasattr(game, 'delayed_kills') and game.delayed_kills:
            game.delayed_kills = []
            return "💊 Яд обезврежен!"
        return "💊 Нет активного яда"
    
    elif effect == "distract_rat":
        if not hasattr(game, 'rat_distracted'):
            game.rat_distracted = {}
        game.rat_distracted[user_id] = True
        return "🧸 Крыса отвлечена! Она не сможет выбрать тебя этой ночью!"
    
    elif effect == "extra_vote":
        if not hasattr(game, 'extra_votes'):
            game.extra_votes = {}
        game.extra_votes[user_id] = game.extra_votes.get(user_id, 0) + 1
        return f"🪈 +1 голос на этом голосовании!"
    
    elif effect == "global_accuracy_penalty":
        if not hasattr(game, 'accuracy_penalty'):
            game.accuracy_penalty = 0
        game.accuracy_penalty += value
        return f"💨 Все игроки потеряли {value}% точности!"
    
    elif effect == "fake_rat_role":
        if not hasattr(game, 'fake_roles'):
            game.fake_roles = {}
        game.fake_roles[user_id] = "🐀 КРЫСА"
        return "🎭 Твоя роль теперь показывается как КРЫСА!"
    
    elif effect == "fake_mouse_role":
        if not hasattr(game, 'fake_roles'):
            game.fake_roles = {}
        game.fake_roles[user_id] = "🐭 МЫШЬ"
        return "🎭 Твоя роль теперь показывается как МЫШЬ!"
    
    elif effect == "rebellion_buff":
        if not hasattr(game, 'rebellion_buff'):
            game.rebellion_buff = False
        game.rebellion_buff = True
        return "🚩 ВОССТАНИЕ! Все Мыши получают +1 голос!"
    
    elif effect == "max_luck":
        if not hasattr(game, 'max_luck_players'):
            game.max_luck_players = []
        game.max_luck_players.append(user_id)
        return "🎲 Максимальная удача активирована на эту игру!"
    
    elif effect == "rat_avoid_2":
        if not hasattr(game, 'rat_avoid_2'):
            game.rat_avoid_2 = {}
        game.rat_avoid_2[user_id] = 2
        return "🪔 Крыса не сможет выбрать тебя 2 ночи!"
    
    elif effect == "confuse_rat":
        if not hasattr(game, 'rat_confused'):
            game.rat_confused = True
        return "🌫️ Крыса в замешательстве! Шанс случайной цели +5%!"
    
    elif effect == "time_rewind":
        if game and game.phase in ["day", "voting"]:
            game.phase = "night"
            return "⌛ Время отмотано назад! Возвращаемся к ночи!"
        return "⌛ Нельзя перемотать время сейчас"
    
    elif effect == "temp_survive_boost":
        if not hasattr(game, 'temp_survive_boost'):
            game.temp_survive_boost = {}
        game.temp_survive_boost[user_id] = value
        return f"🍲 +{value}% шанс выжить этой ночью!"
    
    return f"✅ {item.get('name', 'Предмет')} использован!"


# ========== ВРЕМЕННЫЕ ЭФФЕКТЫ ПИВА ==========
BEER_EFFECTS = [
    {"name": "🧀 Сырный дух", "effect": "xp_boost", "value": 10, "icon": "🧀", "desc": "+10 XP за игру"},
    {"name": "🛡️ Хмельная удача", "effect": "survive_chance", "value": 5, "icon": "🛡️", "desc": "+5% шанс выжить ночью"},
    {"name": "⚔️ Пьяная ярость", "effect": "double_vote", "value": 1, "icon": "⚔️", "desc": "Твой голос считается за 2"},
    {"name": "👁️ Зоркий глаз", "effect": "vote_accuracy", "value": 5, "icon": "👁️", "desc": "+5% точность голосования"},
    {"name": "🍀 Пьяная удача", "effect": "luck", "value": 5, "icon": "🍀", "desc": "+5% к удаче"},
    {"name": "🔍 Сырный нюх", "effect": "item_find", "value": 5, "icon": "🔍", "desc": "+5% шанс найти предмет"},
]


# ========== ОБРАБОТКА ЭФФЕКТОВ ЭКИПИРОВКИ ==========

def process_night_kill_effects(game: Any, rat_id: int, victim_id: int) -> tuple:
    """Обрабатывает эффекты при убийстве ночью."""
    effects = get_player_effects(rat_id, "rat")
    
    reveal_role = True
    if effects.get("hidden_kill_role") or effects.get("invisible_kill"):
        reveal_role = False
    
    silenced = effects.get("silence_victim", False)
    
    # Шанс молчания
    silence_chance = effects.get("silence_chance", 0)
    if silence_chance > 0 and random.randint(1, 100) <= silence_chance:
        silenced = True
    
    # Шанс скрытного убийства
    stealth_chance = effects.get("stealth_kill", 0)
    if stealth_chance > 0 and random.randint(1, 100) <= stealth_chance:
        reveal_role = False
    
    extra_victims = []
    
    # Двойное убийство
    if effects.get("double_kill"):
        extra_victims.append("random")
    
    # Шанс двойного убийства
    double_chance = effects.get("double_kill_chance", 0)
    if double_chance > 0 and random.randint(1, 100) <= double_chance:
        extra_victims.append("random")
    
    # Дополнительное убийство
    if effects.get("extra_kill", 0) > 0:
        for _ in range(effects["extra_kill"]):
            extra_victims.append("random")
    
    # Отложенное убийство от оружия
    if effects.get("delayed_kill_weapon"):
        if not hasattr(game, 'delayed_kills'):
            game.delayed_kills = []
        game.delayed_kills.append(victim_id)
    
    return reveal_role, silenced, extra_victims


def process_survive_chance(game: Any, victim_id: int) -> bool:
    """Проверяет выживет ли игрок при нападении"""
    effects = get_player_effects(victim_id, "mouse")
    
    # Абсолютная защита
    if effects.get("night_shield"):
        return True
    
    # Временный буст выживания
    if hasattr(game, 'temp_survive_boost') and victim_id in game.temp_survive_boost:
        survive_chance = game.temp_survive_boost[victim_id]
        if random.randint(1, 100) <= survive_chance:
            return True
    
    # Базовый шанс выживания
    survive_chance = effects.get("survive_chance", 0)
    
    # Добавляем удачу
    luck = effects.get("luck", 0)
    all_chances = effects.get("all_chances", 0)
    survive_chance += luck + all_chances
    
    # Добавляем точность
    all_accuracy = effects.get("all_accuracy", 0)
    survive_chance += all_accuracy // 2
    
    if survive_chance > 0 and random.randint(1, 100) <= survive_chance:
        return True
    
    # Избежать смерти один раз
    if effects.get("avoid_death_once"):
        return True
    
    # Защита при голосовании
    if effects.get("vote_survive") and game.phase == "voting":
        if random.randint(1, 100) <= effects["vote_survive"]:
            return True
    
    return False


def process_vote_effects(game: Any, voter_id: int) -> int:
    """Обрабатывает эффекты при голосовании. Возвращает количество голосов."""
    role = game.players[voter_id]["role"]
    player_role = "rat" if "КРЫСА" in role else "mouse"
    effects = get_player_effects(voter_id, player_role)
    
    votes = 1
    
    # Двойной голос
    if effects.get("double_vote"):
        votes = 2
    
    # Дополнительные голоса
    if effects.get("extra_vote_against", 0) > 0:
        votes += effects["extra_vote_against"]
    
    # Восстание
    if hasattr(game, 'rebellion_buff') and game.rebellion_buff and player_role == "mouse":
        votes += 1
    
    # Дополнительный голос от расходника
    if hasattr(game, 'extra_votes') and voter_id in game.extra_votes:
        votes += game.extra_votes[voter_id]
    
    # Точность голосования
    vote_accuracy = effects.get("vote_accuracy", 0)
    if vote_accuracy > 0:
        if random.randint(1, 100) <= vote_accuracy:
            votes += 1
    
    # Штраф к голосам
    vote_penalty = effects.get("vote_penalty", 0)
    votes = max(0, votes - vote_penalty)
    
    return votes


def process_vote_count_modifiers(game: Any, target_id: int) -> int:
    """Модификаторы голосов против цели"""
    modifier = 0
    
    if game.rat_id:
        rat_effects = get_player_effects(game.rat_id, "rat")
        if rat_effects.get("mice_vote_penalty", 0) > 0:
            if game.players[target_id]["role"] == "🐭 МЫШЬ":
                modifier -= rat_effects["mice_vote_penalty"]
    
    # Штраф голосов против цели
    target_effects = get_player_effects(target_id, "all")
    if target_effects.get("vote_against_penalty", 0) > 0:
        modifier -= target_effects["vote_against_penalty"]
    
    # Глобальный штраф точности
    if hasattr(game, 'accuracy_penalty') and game.accuracy_penalty > 0:
        modifier -= game.accuracy_penalty // 10
    
    return modifier


def process_xp_modifiers(user_id: int, base_xp: int, won: bool) -> int:
    """Модификаторы опыта"""
    effects = get_player_effects(user_id, "all")
    
    xp = base_xp
    xp_boost = effects.get("xp_boost", 0)
    xp_penalty = effects.get("xp_penalty", 0)
    
    if won:
        win_boost = effects.get("win_xp_boost", 0)
        xp_boost += win_boost
    
    # Двойной XP
    game = get_current_game(user_id)
    if game and hasattr(game, 'double_xp_players') and user_id in game.double_xp_players:
        xp_boost += 100
    
    xp = int(xp * (1 + xp_boost / 100))
    xp = int(xp * (1 - xp_penalty / 100))
    
    bonus_xp = effects.get("bonus_xp", 0)
    xp += bonus_xp
    
    return max(0, xp)


def process_kill_xp(rat_id: int) -> int:
    """Дополнительный опыт за убийство"""
    effects = get_player_effects(rat_id, "rat")
    base_kill_xp = effects.get("kill_xp", 0)
    
    # Множитель за убийство Крысы
    multiplier = effects.get("rat_kill_xp_multiplier", 1)
    
    return base_kill_xp * multiplier


def process_item_drop_chance(user_id: int, base_chance: int) -> int:
    """Модификаторы шанса выпадения предметов"""
    effects = get_player_effects(user_id, "all")
    bonus = effects.get("item_find", 0)
    
    # Добавляем удачу
    luck = effects.get("luck", 0)
    bonus += luck // 2
    
    return base_chance + bonus


def process_legendary_chance(user_id: int, base_chance: int) -> int:
    """Модификаторы шанса легендарного предмета"""
    effects = get_player_effects(user_id, "all")
    bonus = effects.get("legendary_chance", 0)
    
    # Максимальная удача
    game = get_current_game(user_id)
    if game and hasattr(game, 'max_luck_players') and user_id in game.max_luck_players:
        bonus += 50
    
    return base_chance + bonus


def check_death_effects(game: Any, user_id: int, role: str) -> Dict:
    """Эффекты при смерти игрока"""
    player_role = "rat" if "КРЫСА" in role else "mouse"
    effects = get_player_effects(user_id, player_role)
    
    result = {
        "fake_role": effects.get("fake_role"),
        "reveal_rat": effects.get("reveal_rat_on_death", False),
        "protect_target": effects.get("death_protect", False),
        "kill_target": effects.get("death_kill", False),
        "can_message": effects.get("dead_message", False),
        "hidden_role": effects.get("hidden_role", False),
    }
    
    # Фальшивая роль от расходника
    if hasattr(game, 'fake_roles') and user_id in game.fake_roles:
        result["fake_role"] = game.fake_roles[user_id]
    
    return result


def get_vote_visibility(user_id: int) -> bool:
    """Видит ли игрок кто за кого голосовал"""
    effects = get_player_effects(user_id, "mouse")
    return effects.get("see_votes", False)


def get_tie_breaker(user_id: int) -> bool:
    """Решающий голос при ничьей"""
    effects = get_player_effects(user_id, "mouse")
    return effects.get("tie_breaker", False)


def get_justice_tie(user_id: int) -> bool:
    """При ничьей казнят Крысу"""
    effects = get_player_effects(user_id, "mouse")
    return effects.get("justice_tie", False)


def is_vote_hidden(user_id: int) -> bool:
    """Скрыт ли голос игрока"""
    effects = get_player_effects(user_id, "rat")
    return effects.get("hidden_vote", False)


def is_vote_immune(user_id: int) -> bool:
    """Нельзя ли голосовать против игрока"""
    effects = get_player_effects(user_id, "rat")
    return effects.get("vote_immune", False)


def get_night_avoid_chance(user_id: int) -> int:
    """Шанс что Крыса не сможет выбрать целью"""
    effects = get_player_effects(user_id, "mouse")
    base_chance = effects.get("avoid_night", 0)
    
    # Временное избегание
    game = get_current_game(user_id)
    if game:
        if hasattr(game, 'rat_distracted') and user_id in game.rat_distracted:
            return 100
        if hasattr(game, 'rat_avoid_2') and user_id in game.rat_avoid_2:
            if game.rat_avoid_2[user_id] > 0:
                game.rat_avoid_2[user_id] -= 1
                return 100
    
    # Добавляем удачу
    luck = effects.get("luck", 0)
    all_chances = effects.get("all_chances", 0)
    
    return min(100, base_chance + luck + all_chances)


def get_taunt_chance(user_id: int) -> int:
    """Шанс что Крыса выберет именно этого игрока"""
    effects = get_player_effects(user_id, "all")
    base_chance = effects.get("taunt", 0)
    
    # Если игрок раскрыт Крысе
    if effects.get("reveal_to_rat"):
        base_chance += 20
    
    return min(100, base_chance)


def is_shot_proof(user_id: int) -> bool:
    """Защита от выстрела"""
    effects = get_player_effects(user_id, "all")
    return effects.get("shot_proof", False)


def get_ghost_vote(user_id: int) -> bool:
    """Может ли голосовать после смерти"""
    effects = get_player_effects(user_id, "all")
    return effects.get("ghost_vote", False)


def get_revenge_kill(user_id: int) -> bool:
    """Убивает ли первого голосовавшего при казни"""
    effects = get_player_effects(user_id, "all")
    return effects.get("revenge", False)


def is_debuff_immune(user_id: int) -> bool:
    """Иммунитет к дебаффам"""
    effects = get_player_effects(user_id, "all")
    return effects.get("debuff_immune", False)


def can_awaken(user_id: int) -> bool:
    """Может ли разбудить игрока"""
    effects = get_player_effects(user_id, "mouse")
    return effects.get("awaken", False)


def can_catapult(user_id: int) -> bool:
    """Может ли запустить игрока катапультой"""
    effects = get_player_effects(user_id, "mouse")
    return effects.get("catapult", False)


def can_net_trap(user_id: int) -> bool:
    """Может ли обездвижить Крысу"""
    effects = get_player_effects(user_id, "mouse")
    return effects.get("net_trap", False)


def has_repellent(user_id: int) -> bool:
    """Есть ли спрей от крыс"""
    effects = get_player_effects(user_id, "mouse")
    return effects.get("repellent", False)


def can_trap_launch(user_id: int) -> bool:
    """Может ли запустить мышеловку"""
    effects = get_player_effects(user_id, "mouse")
    return effects.get("trap_launcher", False)


def get_wisdom_reveal(user_id: int) -> bool:
    """Видит ли Крысу после 3-й ночи (тюрбан)"""
    effects = get_player_effects(user_id, "mouse")
    return effects.get("wisdom_reveal", False)


def get_disguise_until_kill(user_id: int) -> bool:
    """Маскировка до первого убийства"""
    effects = get_player_effects(user_id, "rat")
    return effects.get("disguise_until_kill", False)


def get_hear_rat(user_id: int) -> bool:
    """Слышит ли выбор Крысы"""
    effects = get_player_effects(user_id, "mouse")
    return effects.get("hear_rat", False)


def get_track_rat(user_id: int) -> bool:
    """Отслеживает ли голосование Крысы"""
    effects = get_player_effects(user_id, "mouse")
    return effects.get("track_rat", False)


def get_random_effect() -> Dict[str, Any]:
    """Случайный эффект для шутовского колпака"""
    effects_list = [
        {"xp_boost": 10},
        {"survive_chance": 10},
        {"bonus_xp": 20},
        {"double_vote": True},
        {"night_shield": True},
        {"avoid_night": 15},
        {"vote_accuracy": 10},
        {"item_find": 10},
        {"luck": 5},
        {"all_chances": 5},
        {"kill_xp": 5},
        {"hidden_vote": True},
    ]
    return random.choice(effects_list)


def get_chaos_effect() -> str:
    """Случайный эффект для посоха хаоса"""
    effects = [
        "double_kill",
        "silence_victim",
        "hidden_kill_role",
        "extra_kill",
        "invisible_kill",
        "delayed_kill_weapon",
        "stealth_kill",
    ]
    return random.choice(effects)


def get_current_game(user_id: int):
    """Получить текущую игру игрока"""
    try:
        from handlers.game_rat import active_games
        for game in active_games.values():
            if user_id in game.players:
                return game
    except:
        pass
    return None


def get_all_stats_bonus(user_id: int) -> int:
    """Бонус ко всем характеристикам"""
    effects = get_player_effects(user_id, "all")
    return effects.get("all_stats", 0)


def get_all_chances_bonus(user_id: int) -> int:
    """Бонус ко всем шансам"""
    effects = get_player_effects(user_id, "all")
    return effects.get("all_chances", 0)


def get_vote_time_bonus(user_id: int) -> int:
    """Бонус ко времени голосования"""
    effects = get_player_effects(user_id, "all")
    return effects.get("vote_time_bonus", 0)


def get_time_bonus(user_id: int) -> int:
    """Бонус ко всем фазам"""
    effects = get_player_effects(user_id, "all")
    return effects.get("time_bonus", 0)


def has_rat_protection(user_id: int) -> bool:
    """Защита от обращения в Крысу"""
    effects = get_player_effects(user_id, "mouse")
    return effects.get("rat_protection", False)


def has_curse_reflect(user_id: int) -> bool:
    """Отражает ли проклятия"""
    effects = get_player_effects(user_id, "all")
    return effects.get("curse_reflect", False)


def has_unremovable_vote(user_id: int) -> bool:
    """Нельзя ли отменить голос"""
    effects = get_player_effects(user_id, "mouse")
    return effects.get("unremovable_vote", False)


def is_soulbound(user_id: int) -> bool:
    """Связан ли с другим игроком"""
    effects = get_player_effects(user_id, "all")
    return effects.get("soulbound", False)


def has_gift_item(user_id: int) -> bool:
    """Дарит ли предмет после победы"""
    effects = get_player_effects(user_id, "all")
    return effects.get("gift_item", False)


def has_anon_message(user_id: int) -> bool:
    """Может ли отправить анонимное сообщение"""
    effects = get_player_effects(user_id, "mouse")
    return effects.get("anon_message", False)


def has_day_shot(user_id: int) -> bool:
    """Может ли выстрелить днём"""
    effects = get_player_effects(user_id, "mouse")
    return effects.get("day_shot", False)


def has_reveal_role_ability(user_id: int) -> bool:
    """Может ли узнать роль"""
    effects = get_player_effects(user_id, "mouse")
    return effects.get("reveal_role", False)


def get_chat_xp(user_id: int) -> int:
    """XP за сообщение в чате"""
    effects = get_player_effects(user_id, "all")
    return effects.get("chat_xp", 0)


def get_extra_life(user_id: int) -> int:
    """Дополнительные жизни"""
    effects = get_player_effects(user_id, "all")
    return effects.get("extra_life", 0)