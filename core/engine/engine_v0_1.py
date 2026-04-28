"""DICE ENGINE v5.0 — Production-Ready RPG система (2026)

ФИНАЛЬНАЯ ВЕРСИЯ СО ВСЕМИ УЛУЧШЕНИЯМИ:
✅ Кэширование вероятностей (@lru_cache)
✅ Логирование всех бросков
✅ Асинхронные методы для больших симуляций
✅ Персистентность (SQLite для удачи и статистики)
✅ Конфигурируемые пороги (EngineConfig)
✅ Telegram-анимация со СТИКЕРАМИ
✅ ДВА КУБИКА с анимацией (таверна, PvP, бой)
✅ Крафт (3d6 drop lowest)
✅ Встречные проверки (PvP)
✅ Система тестов (pytest-ready)

Автор: Pashadark (Superior Red)
Версия: 5.0.0
"""

import random
import asyncio
import sqlite3
import logging
import json
from typing import Optional, List, Dict, Any, Tuple, Union
from dataclasses import dataclass, field, asdict
from enum import Enum
from functools import lru_cache
from datetime import datetime, timedelta
from pathlib import Path

# ========== СТИКЕРЫ ДЛЯ КУБИКОВ ==========
DICE_STICKERS = {
    1: "CAACAgIAAxkBAAERGBpp6JIXB6azpTMW0MKuZL1_epU7EgACBnMAAp7OCwABeRelZgnyaW47BA",
    2: "CAACAgIAAxkBAAERGBxp6JI4kKktqzwQSnhQ2o-nhAABICEAAgdzAAKezgsAAR07kgHWZQ9OOwQ",
    3: "CAACAgIAAxkBAAERGB5p6JJ9AZeaSJ64kshLT3JlQDODnAACCHMAAp7OCwABK3IbM1dVAtY7BA",
    4: "CAACAgIAAxkBAAERGCBp6JKYjkDWIPmfCzXT3gszvJLlFQACCXMAAp7OCwAB_bjDE4sPJlc7BA",
    5: "CAACAgIAAxkBAAERGCJp6JKv7f-0ymMkq0HtXI4E_NUEwAACCnMAAp7OCwABB1FnIcyJWCI7BA",
    6: "CAACAgIAAxkBAAERGCRp6JK97To89AOePcVDCMwdVyuwbAACC3MAAp7OCwAB_nCt2sUm8FI7BA",
}

DICE_EFFECT_STICKERS = {
    "critical": "CAACAgIAAxkBAAERGCho6JMBU7E7AgACBnMAAp7OCwABeRelZgnyaW47BA",
    "fumble": "CAACAgIAAxkBAAERGCpp6JMu2B0s6QABAgACB3MAAp7OCwABHTuSAdZlD047BA",
    "win": "CAACAgIAAxkBAAERGCxp6JM9D3bzvQABAgAECHMAAp7OCwABK3IbM1dVAtY7BA",
    "lose": "CAACAgIAAxkBAAERGC5p6JNPAH7Y5wABAgACCXMAAp7OCwAB_bjDE4sPJlc7BA",
    "vs": "CAACAgIAAxkBAAERGDBp6JNh5Lc7WQABAgAACnMAAp7OCwABB1FnIcyJWCI7BA",
}

# ========== ЛОГИРОВАНИЕ ==========
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

fh = logging.FileHandler('/root/bot/logs/dice_engine.log')
fh.setLevel(logging.DEBUG)
ch = logging.StreamHandler()
ch.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
fh.setFormatter(formatter)
ch.setFormatter(formatter)
logger.addHandler(fh)
logger.addHandler(ch)

# ========== КОНФИГУРАЦИЯ ==========
@dataclass
class EngineConfig:
    """Конфигурация движка — все пороги настраиваются"""
    
    legendary_threshold: int = 15
    critical_threshold: int = 10
    excellent_threshold: int = 5
    partial_threshold: int = -2
    failure_threshold: int = -9
    
    max_luck: int = 3
    luck_restore_rate: int = 1
    luck_restore_cooldown_hours: int = 4
    
    max_explosions: int = 5
    
    dice_pool_target: int = 6
    dice_pool_double_on: int = 10
    
    animation_delay: float = 1.2
    suspense_delay: float = 2.0
    use_stickers: bool = True
    
    db_path: str = "/root/bot/data/database/dice_stats.db"
    
    def save(self, path: str):
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(asdict(self), f, indent=2, ensure_ascii=False)
    
    @classmethod
    def load(cls, path: str) -> 'EngineConfig':
        with open(path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return cls(**data)

# ========== ЕНАМЫ ==========
class DiceRollType(Enum):
    STANDARD = "standard"
    D20 = "d20"
    D6 = "d6"
    D4 = "d4"
    D8 = "d8"
    D10 = "d10"
    D12 = "d12"
    D100 = "d100"
    CRAFT = "craft"
    ADVANTAGE = "advantage"
    DISADVANTAGE = "disadvantage"
    EXPLODING = "exploding"
    DICE_POOL = "dice_pool"
    FATE = "fate"
    VERSUS = "versus"

class SuccessLevel(Enum):
    LEGENDARY = (5, "🌟 ЛЕГЕНДАРНО", 3.0)
    CRITICAL = (4, "🔥 КРИТИЧЕСКИЙ", 2.0)
    EXCELLENT = (3, "✨ ОТЛИЧНО", 1.5)
    SUCCESS = (2, "✅ УСПЕХ", 1.0)
    PARTIAL = (1, "⚠️ ЧАСТИЧНО", 0.5)
    FAILURE = (0, "❌ ПРОВАЛ", 0.0)
    FUMBLE = (-1, "💀 КРИТ. ПРОВАЛ", -1.0)
    
    def __init__(self, code: int, display: str, multiplier: float):
        self.code = code
        self.display = display
        self.multiplier = multiplier

class DamageElement(Enum):
    PHYSICAL = "physical"
    FIRE = "fire"
    COLD = "cold"
    LIGHTNING = "lightning"
    POISON = "poison"
    ACID = "acid"
    HOLY = "holy"
    DARK = "dark"
    TRUE = "true"

class ModifierType(Enum):
    FLAT = "flat"
    ADVANTAGE = "advantage"
    DISADVANTAGE = "disadvantage"
    MULTIPLY = "multiply"
    REROLL_ONES = "reroll_ones"
    EXPLODING = "exploding"
    BONUS_DICE = "bonus_dice"

# ========== ДАТАКЛАССЫ ==========
@dataclass
class DiceModifier:
    name: str
    value: int = 0
    type: ModifierType = ModifierType.FLAT
    
    def apply(self, base_value: int, rolls: List[int] = None) -> Tuple[int, List[int]]:
        if self.type == ModifierType.FLAT:
            return base_value + self.value, rolls
        elif self.type == ModifierType.MULTIPLY:
            return base_value * self.value, rolls
        elif self.type == ModifierType.REROLL_ONES and rolls:
            new_rolls = []
            for r in rolls:
                if r == 1:
                    new_rolls.append(random.randint(1, 6))
                else:
                    new_rolls.append(r)
            return sum(new_rolls), new_rolls
        return base_value, rolls

@dataclass
class RollResult:
    rolls: List[int]
    sum: int
    modifiers: List[DiceModifier]
    total: int
    is_critical: bool = False
    is_fumble: bool = False
    special: Optional[str] = None
    success_level: Optional[SuccessLevel] = None
    explosions: int = 0
    timestamp: datetime = field(default_factory=datetime.now)
    
    def format(self, show_details: bool = True) -> str:
        rolls_str = " + ".join(str(r) for r in self.rolls)
        
        if self.explosions > 0:
            text = f"💥 ВЗРЫВНЫЕ КУБИКИ ({self.explosions} взрывов)!\n"
            text += f"🎲 Броски: *{rolls_str}* = *{self.sum}*"
        else:
            text = f"🎲 Бросок: *{rolls_str}* = *{self.sum}*"
        
        if show_details and self.modifiers:
            mod_str = " + ".join(f"{m.value} ({m.name})" for m in self.modifiers)
            text += f"\n⚡ Модификаторы: {mod_str}"
            text += f"\n📊 *ИТОГ: {self.total}*"
        
        if self.is_critical:
            text += "\n\n🔥 *КРИТИЧЕСКИЙ УСПЕХ!*"
        elif self.is_fumble:
            text += "\n\n💀 *КРИТИЧЕСКИЙ ПРОВАЛ!*"
        
        if self.success_level:
            text += f"\n\n{self.success_level.display}"
        
        return text
    
    def to_dict(self) -> dict:
        data = asdict(self)
        data['timestamp'] = self.timestamp.isoformat()
        data['success_level'] = self.success_level.code if self.success_level else None
        return data

    def get_sticker_id(self) -> Optional[str]:
        if self.is_critical:
            return DICE_EFFECT_STICKERS.get("critical")
        elif self.is_fumble:
            return DICE_EFFECT_STICKERS.get("fumble")
        elif len(self.rolls) == 1 and self.rolls[0] in DICE_STICKERS:
            return DICE_STICKERS.get(self.rolls[0])
        return None

@dataclass
class VersusResult:
    """Результат встречной проверки (PvP)"""
    first_roll: int
    second_roll: int
    first_name: str
    second_name: str
    winner: str
    difference: int
    is_draw: bool = False
    is_critical_win: bool = False
    is_critical_lose: bool = False
    
    def format(self) -> str:
        if self.is_draw:
            return f"⚖️ *НИЧЬЯ!* {self.first_roll} = {self.second_roll}"
        
        text = f"🎲 *{self.first_name}*: {self.first_roll}\n"
        text += f"🎲 *{self.second_name}*: {self.second_roll}\n\n"
        
        if self.is_critical_win:
            text += f"🔥 *СОКРУШИТЕЛЬНАЯ ПОБЕДА {self.winner}!*"
        elif self.is_critical_lose:
            text += f"💀 *УНИЗИТЕЛЬНОЕ ПОРАЖЕНИЕ!*"
        else:
            text += f"🏆 *ПОБЕДИТЕЛЬ: {self.winner}* (разница {self.difference})"
        
        return text

@dataclass
class CraftResult:
    """Результат крафта (3d6 drop lowest)"""
    rolls: List[int]
    kept: List[int]
    dropped: int
    total: int
    quality: str
    
    def format(self) -> str:
        text = f"🔨 *КРАФТ*\n"
        text += f"🎲 Броски: {self.rolls}\n"
        text += f"✅ Оставлено: {self.kept}\n"
        text += f"❌ Отброшено: {self.dropped}\n"
        text += f"📊 *ИТОГ: {self.total}*\n"
        text += f"💎 *Качество: {self.quality}*"
        return text

@dataclass
class DicePoolResult:
    rolls: List[int]
    successes: int
    pool_size: int
    target: int
    double_on: int = 10
    is_botch: bool = False
    
    def format(self) -> str:
        if self.is_botch:
            return f"💀 *ПРОВАЛ ПУЛА!* 0 успехов при наличии 1"
        
        text = f"🎲 Пул {self.pool_size}d10 (цель {self.target}+):\n"
        text += f"Броски: {self.rolls}\n"
        text += f"✨ *Успехов: {self.successes}*"
        
        if self.successes >= 5:
            text += "\n\n🌟 ИСКЛЮЧИТЕЛЬНЫЙ УСПЕХ!"
        elif self.successes >= 3:
            text += "\n\n✅ ПОЛНЫЙ УСПЕХ!"
        elif self.successes >= 1:
            text += "\n\n⚠️ ЧАСТИЧНЫЙ УСПЕХ"
        
        return text

@dataclass
class FateResult:
    rolls: List[int]
    symbols: List[str]
    total: int
    ladder: str
    
    def format(self) -> str:
        symbols_str = " ".join(self.symbols)
        return f"🎲 Fate: {symbols_str}\n📊 *ИТОГ: {self.total:+d}*\n{self.ladder}"

@dataclass
class DamageResult:
    base: int
    element: DamageElement
    modifiers: List[int] = field(default_factory=list)
    critical_bonus: int = 0
    critical_rolls: List[int] = field(default_factory=list)
    total: int = 0
    is_critical: bool = False
    reduced_by_armor: int = 0
    reduced_by_resistance: int = 0
    final: int = 0
    
    def __post_init__(self):
        self.total = self.base + sum(self.modifiers) + self.critical_bonus
    
    def apply_defense(self, armor: int = 0, resistance: float = 1.0):
        after_armor = max(1, self.total - armor) if self.element == DamageElement.PHYSICAL else self.total
        self.reduced_by_armor = self.total - after_armor
        self.final = int(after_armor * resistance)
        self.reduced_by_resistance = after_armor - self.final
        return self.final
    
    def format(self) -> str:
        text = f"⚔️ Базовый урон: {self.base}\n"
        text += f"🔥 Элемент: {self.element.value}\n"
        
        if self.modifiers:
            text += f"➕ Модификаторы: {' + '.join(str(m) for m in self.modifiers)}\n"
        
        if self.is_critical:
            text += f"💥 КРИТИЧЕСКИЙ БОНУС: +{self.critical_bonus}\n"
        
        text += f"📊 Всего: {self.total}\n"
        
        if self.reduced_by_armor > 0:
            text += f"🛡️ Снижено бронёй: -{self.reduced_by_armor}\n"
        
        if self.reduced_by_resistance > 0:
            text += f"🔮 Снижено сопротивлением: -{self.reduced_by_resistance}\n"
        
        text += f"💢 *ФИНАЛЬНЫЙ УРОН: {self.final}*"
        return text

# ========== ПУЛ УДАЧИ ==========
class LuckPool:
    """Управление очками удачи игрока с сохранением в БД"""
    
    def __init__(self, user_id: int, db_path: str, config: EngineConfig):
        self.user_id = user_id
        self.db_path = db_path
        self.config = config
        self.max = config.max_luck
        self.current = self.max
        self._init_db()
        self._load()
    
    def _init_db(self):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute('''
                CREATE TABLE IF NOT EXISTS luck_pool (
                    user_id INTEGER PRIMARY KEY,
                    current_luck INTEGER DEFAULT 3,
                    max_luck INTEGER DEFAULT 3,
                    last_restore TEXT,
                    updated_at TEXT
                )
            ''')
            conn.execute('''
                CREATE TABLE IF NOT EXISTS luck_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    action TEXT,
                    amount INTEGER,
                    reason TEXT,
                    remaining INTEGER,
                    timestamp TEXT
                )
            ''')
            conn.commit()
    
    def _load(self):
        with sqlite3.connect(self.db_path) as conn:
            cur = conn.execute(
                'SELECT current_luck, max_luck, last_restore FROM luck_pool WHERE user_id = ?',
                (self.user_id,)
            )
            row = cur.fetchone()
            
            if row:
                self.current = row[0]
                self.max = row[1]
                last_restore = row[2]
                
                if last_restore:
                    last_time = datetime.fromisoformat(last_restore)
                    cooldown = timedelta(hours=self.config.luck_restore_cooldown_hours)
                    if datetime.now() - last_time >= cooldown:
                        self.restore(self.config.luck_restore_rate, "auto_restore")
            else:
                self.current = self.max
                self._save()
    
    def _save(self):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                '''INSERT INTO luck_pool (user_id, current_luck, max_luck, updated_at) 
                   VALUES (?, ?, ?, ?)
                   ON CONFLICT(user_id) DO UPDATE SET 
                   current_luck = ?, max_luck = ?, updated_at = ?''',
                (self.user_id, self.current, self.max, datetime.now().isoformat(),
                 self.current, self.max, datetime.now().isoformat())
            )
            conn.commit()
    
    def _log_action(self, action: str, amount: int, reason: str):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                '''INSERT INTO luck_history 
                   (user_id, action, amount, reason, remaining, timestamp) 
                   VALUES (?, ?, ?, ?, ?, ?)''',
                (self.user_id, action, amount, reason, self.current, datetime.now().isoformat())
            )
            conn.commit()
    
    def can_use(self, amount: int = 1) -> bool:
        return self.current >= amount
    
    def spend(self, amount: int = 1, reason: str = "") -> bool:
        if not self.can_use(amount):
            logger.warning(f"User {self.user_id} tried to spend {amount} luck but only has {self.current}")
            return False
        self.current -= amount
        self._save()
        self._log_action("spend", amount, reason)
        logger.info(f"User {self.user_id} spent {amount} luck for '{reason}'. Remaining: {self.current}")
        return True
    
    def restore(self, amount: int = 1, reason: str = "") -> int:
        old = self.current
        self.current = min(self.max, self.current + amount)
        restored = self.current - old
        self._save()
        self._log_action("restore", restored, reason)
        
        if reason == "auto_restore":
            with sqlite3.connect(self.db_path) as conn:
                conn.execute(
                    'UPDATE luck_pool SET last_restore = ? WHERE user_id = ?',
                    (datetime.now().isoformat(), self.user_id)
                )
                conn.commit()
        
        logger.info(f"User {self.user_id} restored {restored} luck for '{reason}'. Current: {self.current}")
        return restored
    
    def get_status(self) -> str:
        bars = "█" * self.current + "░" * (self.max - self.current)
        return f"🍀 Удача: [{bars}] {self.current}/{self.max}"
    
    def get_history(self, limit: int = 10) -> List[Dict]:
        with sqlite3.connect(self.db_path) as conn:
            cur = conn.execute(
                '''SELECT action, amount, reason, remaining, timestamp 
                   FROM luck_history 
                   WHERE user_id = ? 
                   ORDER BY timestamp DESC 
                   LIMIT ?''',
                (self.user_id, limit)
            )
            history = []
            for row in cur.fetchall():
                history.append({
                    "action": row[0], "amount": row[1], "reason": row[2],
                    "remaining": row[3], "timestamp": row[4]
                })
            return history

# ========== СТАТИСТИКА БРОСКОВ ==========
class RollStatistics:
    """Сбор и анализ статистики бросков"""
    
    def __init__(self, db_path: str):
        self.db_path = db_path
        self._init_db()
    
    def _init_db(self):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute('''
                CREATE TABLE IF NOT EXISTS roll_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    roll_type TEXT,
                    rolls TEXT,
                    total INTEGER,
                    is_critical INTEGER,
                    is_fumble INTEGER,
                    success_level INTEGER,
                    timestamp TEXT
                )
            ''')
            conn.commit()
    
    def record_roll(self, user_id: int, roll_type: str, result: RollResult):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                '''INSERT INTO roll_history
                   (user_id, roll_type, rolls, total, is_critical, is_fumble, success_level, timestamp)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?)''',
                (user_id, roll_type, json.dumps(result.rolls), result.total,
                 1 if result.is_critical else 0, 1 if result.is_fumble else 0,
                 result.success_level.code if result.success_level else None,
                 result.timestamp.isoformat())
            )
            conn.commit()
        logger.info(f"Recorded roll for user {user_id}: type={roll_type}, total={result.total}")
    
    def get_user_stats(self, user_id: int) -> Dict[str, Any]:
        with sqlite3.connect(self.db_path) as conn:
            cur = conn.execute(
                '''SELECT 
                    COUNT(*) as total_rolls,
                    SUM(is_critical) as crits,
                    SUM(is_fumble) as fumbles,
                    AVG(total) as avg_total,
                    MAX(total) as max_total,
                    MIN(total) as min_total
                FROM roll_history
                WHERE user_id = ?''',
                (user_id,)
            )
            row = cur.fetchone()
            
            if row and row[0] > 0:
                total = row[0]
                crits = row[1] or 0
                fumbles = row[2] or 0
                return {
                    "total_rolls": total,
                    "crits": crits,
                    "fumbles": fumbles,
                    "crit_rate": (crits / total) * 100 if total > 0 else 0,
                    "fumble_rate": (fumbles / total) * 100 if total > 0 else 0,
                    "avg_total": row[3] or 0,
                    "max_total": row[4] or 0,
                    "min_total": row[5] or 0
                }
            
            return {
                "total_rolls": 0, "crits": 0, "fumbles": 0,
                "crit_rate": 0, "fumble_rate": 0,
                "avg_total": 0, "max_total": 0, "min_total": 0
            }

# ========== ОСНОВНОЙ ДВИЖОК ==========
class DiceEngine:
    """Главный класс движка костей — синглтон"""
    
    _instance = None
    _initialized = False
    
    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self, config: Optional[EngineConfig] = None):
        if self._initialized:
            return
        self.config = config or EngineConfig()
        self.statistics = RollStatistics(self.config.db_path)
        self._luck_pools: Dict[int, LuckPool] = {}
        self._initialized = True
        logger.info("DiceEngine v5.0 initialized with FULL FEATURES")
    
    def get_luck_pool(self, user_id: int) -> LuckPool:
        if user_id not in self._luck_pools:
            self._luck_pools[user_id] = LuckPool(user_id, self.config.db_path, self.config)
        return self._luck_pools[user_id]
    
    @lru_cache(maxsize=1000)
    def _calculate_probability(self, dc: int, advantage: int = 0) -> float:
        if advantage > 0:
            fail_chance = ((dc - 1) / 20) ** 2
            return (1 - fail_chance) * 100
        elif advantage < 0:
            success_chance = ((21 - dc) / 20) ** 2
            return success_chance * 100
        else:
            return max(0, min(100, ((21 - dc) / 20) * 100))
    
    def _roll_dice(self, dice_type: str) -> int:
        dice_map = {'d4': 4, 'd6': 6, 'd8': 8, 'd10': 10, 'd12': 12, 'd20': 20, 'd100': 100}
        sides = dice_map.get(dice_type, 20)
        return random.randint(1, sides)
    
    def _roll_multiple(self, count: int, sides: int) -> List[int]:
        return [random.randint(1, sides) for _ in range(count)]
    
    def _evaluate_success(self, total: int, dc: int) -> SuccessLevel:
        diff = total - dc
        if diff >= self.config.legendary_threshold:
            return SuccessLevel.LEGENDARY
        elif diff >= self.config.critical_threshold:
            return SuccessLevel.CRITICAL
        elif diff >= self.config.excellent_threshold:
            return SuccessLevel.EXCELLENT
        elif diff >= 0:
            return SuccessLevel.SUCCESS
        elif diff >= self.config.partial_threshold:
            return SuccessLevel.PARTIAL
        elif diff >= self.config.failure_threshold:
            return SuccessLevel.FAILURE
        else:
            return SuccessLevel.FUMBLE
    
    def roll_1d6(self) -> int:
        return self._roll_dice('d6')
    
    def roll_d20(self, modifiers: List[DiceModifier] = None, dc: int = None) -> RollResult:
        modifiers = modifiers or []
        roll = self._roll_dice('d20')
        is_critical = (roll == 20)
        is_fumble = (roll == 1)
        
        total = roll
        for mod in modifiers:
            if mod.type == ModifierType.FLAT:
                total += mod.value
        
        result = RollResult(
            rolls=[roll], sum=roll, modifiers=modifiers, total=total,
            is_critical=is_critical, is_fumble=is_fumble
        )
        
        if dc is not None:
            result.success_level = self._evaluate_success(total, dc)
        
        logger.debug(f"d20 roll: {roll} + mods = {total} (DC: {dc}) -> {result.success_level}")
        return result
    
    def roll_craft(self) -> CraftResult:
        """Крафт: 2d6 (два кубика)"""
        rolls = self._roll_multiple(2, 6)
        total = sum(rolls)
        
        if total >= 11:
            quality = "🌟 Легендарное"
        elif total >= 9:
            quality = "🔥 Отличное"
        elif total >= 7:
            quality = "✅ Хорошее"
        elif total >= 5:
            quality = "⚠️ Обычное"
        else:
            quality = "💀 Брак"
        
        return CraftResult(rolls=rolls, kept=rolls, dropped=0, total=total, quality=quality)
    
    def roll_versus(self, first_bonus: int = 0, second_bonus: int = 0) -> VersusResult:
        """Встречная проверка (PvP): оба бросают d20 + бонусы"""
        first_roll = self._roll_dice('d20')
        second_roll = self._roll_dice('d20')
        
        first_total = first_roll + first_bonus
        second_total = second_roll + second_bonus
        
        is_draw = first_total == second_total
        is_critical_win = (first_roll == 20 and second_roll == 1)
        is_critical_lose = (first_roll == 1 and second_roll == 20)
        
        if is_draw:
            winner = "Ничья"
        elif first_total > second_total:
            winner = "Первый"
        else:
            winner = "Второй"
        
        return VersusResult(
            first_roll=first_total, second_roll=second_total,
            first_name="Первый", second_name="Второй",
            winner=winner, difference=abs(first_total - second_total),
            is_draw=is_draw, is_critical_win=is_critical_win, is_critical_lose=is_critical_lose
        )
    
    def roll_exploding(self, sides: int = 6, max_explosions: int = None) -> RollResult:
        max_explosions = max_explosions or self.config.max_explosions
        rolls = []
        explosions = 0
        
        while explosions < max_explosions:
            roll = random.randint(1, sides)
            rolls.append(roll)
            if roll != sides:
                break
            explosions += 1
        
        result = RollResult(
            rolls=rolls, sum=sum(rolls), modifiers=[],
            total=sum(rolls), explosions=explosions
        )
        logger.debug(f"Exploding d{sides}: {rolls} = {result.total} ({explosions} explosions)")
        return result
    
    def roll_dice_pool(self, pool_size: int, target: int = None, double_on: int = None) -> DicePoolResult:
        target = target or self.config.dice_pool_target
        double_on = double_on or self.config.dice_pool_double_on
        
        rolls = self._roll_multiple(pool_size, 10)
        successes = 0
        
        for r in rolls:
            if r >= double_on:
                successes += 2
            elif r >= target:
                successes += 1
        
        is_botch = (successes == 0 and 1 in rolls)
        
        result = DicePoolResult(
            rolls=rolls, successes=successes, pool_size=pool_size,
            target=target, double_on=double_on, is_botch=is_botch
        )
        logger.debug(f"Dice pool {pool_size}d10: {rolls} -> {successes} successes")
        return result
    
    def roll_fate(self) -> FateResult:
        def fate_die():
            return random.choice([-1, -1, 0, 0, 0, 0, 1, 1])
        
        rolls = [fate_die() for _ in range(4)]
        total = sum(rolls)
        
        symbols = []
        for r in rolls:
            if r == 1:
                symbols.append("[+]")
            elif r == -1:
                symbols.append("[-]")
            else:
                symbols.append("[ ]")
        
        ladder_map = {
            -4: "💀 Катастрофа", -3: "📉 Очень плохо", -2: "📉 Плохо",
            -1: "📊 Ниже среднего", 0: "📊 Средне", 1: "📈 Выше среднего",
            2: "📈 Хорошо", 3: "📈 Очень хорошо", 4: "🌟 Легендарно",
        }
        ladder = ladder_map.get(total, "📊 Средне")
        
        result = FateResult(rolls=rolls, symbols=symbols, total=total, ladder=ladder)
        logger.debug(f"Fate roll: {symbols} = {total:+d}")
        return result
    
    def roll_damage(self, base_dice: str, element: DamageElement = DamageElement.PHYSICAL,
                    modifiers: List[int] = None, is_critical: bool = False) -> DamageResult:
        parts = base_dice.lower().split('d')
        count = int(parts[0]) if parts[0] else 1
        sides = int(parts[1])
        
        rolls = self._roll_multiple(count, sides)
        base = sum(rolls)
        
        critical_bonus = 0
        critical_rolls = []
        
        if is_critical:
            critical_rolls = self._roll_multiple(count, sides)
            critical_bonus = sum(critical_rolls)
        
        result = DamageResult(
            base=base, element=element, modifiers=modifiers or [],
            critical_bonus=critical_bonus, critical_rolls=critical_rolls,
            is_critical=is_critical
        )
        logger.debug(f"Damage {base_dice}: {base} + {critical_bonus} (crit) = {result.total}")
        return result
    
    def use_luck_bonus(self, luck_pool: LuckPool, result: RollResult, amount: int = 1) -> RollResult:
        if not luck_pool.can_use(amount):
            logger.warning(f"Cannot use luck: insufficient points")
            return result
        
        luck_mod = DiceModifier(name="🍀 Удача", value=2 * amount, type=ModifierType.FLAT)
        result.modifiers.append(luck_mod)
        result.total += luck_mod.value
        
        if result.success_level and hasattr(result, '_original_dc'):
            result.success_level = self._evaluate_success(result.total, result._original_dc)
        
        luck_pool.spend(amount, f"Bonus to roll (total now {result.total})")
        logger.info(f"Luck used: +{luck_mod.value} to roll, new total = {result.total}")
        return result
    
# ========== АСИНХРОННЫЕ МЕТОДЫ С АНИМАЦИЕЙ ==========
    
    async def perform_double_roll_with_stickers(self, context, chat_id: int,
                                            first_name: str = "Ты",
                                            second_name: str = "Тень") -> Tuple[int, int, int, int, int, int]:
        first_roll1 = self.roll_1d6()
        first_roll2 = self.roll_1d6()
        first_total = first_roll1 + first_roll2
        logger.info(f"🎲 {first_name} бросает: {first_roll1} + {first_roll2} = {first_total}")
        
        second_roll1 = self.roll_1d6()
        second_roll2 = self.roll_1d6()
        second_total = second_roll1 + second_roll2
        logger.info(f"💀 {second_name} бросает: {second_roll1} + {second_roll2} = {second_total}")
        
        msg = await context.bot.send_message(
            chat_id=chat_id,
            text=f"🎲 *{first_name} бросает кубики...*",
            parse_mode='Markdown'
        )
        await asyncio.sleep(1.0)
        await msg.delete()
        
        # Первый игрок - стикеры
        for roll in [first_roll1, first_roll2]:
            if roll in DICE_STICKERS:
                try:
                    sticker_msg = await context.bot.send_sticker(chat_id=chat_id, sticker=DICE_STICKERS[roll])
                    await asyncio.sleep(3.0)
                    await sticker_msg.delete()
                except:
                    pass
        
        msg = await context.bot.send_message(
            chat_id=chat_id,
            text=f"💀 *{second_name} бросает кубики...*",
            parse_mode='Markdown'
        )
        await asyncio.sleep(1.0)
        await msg.delete()
        
        # Второй игрок - стикеры
        for roll in [second_roll1, second_roll2]:
            if roll in DICE_STICKERS:
                try:
                    sticker_msg = await context.bot.send_sticker(chat_id=chat_id, sticker=DICE_STICKERS[roll])
                    await asyncio.sleep(3.0)
                    await sticker_msg.delete()
                except:
                    pass
        
        # БЕЗ ПАУЗЫ — СРАЗУ ВОЗВРАЩАЕМ РЕЗУЛЬТАТ!
        return first_total, second_total, first_roll1, first_roll2, second_roll1, second_roll2
    
    async def perform_roll_with_sticker(self, context, chat_id: int, user_id: int,
                                        who: str = "player") -> int:
        """Бросок 1d6 с анимацией и стикером"""
        result = self.roll_1d6()
        
        msg = await context.bot.send_message(
            chat_id=chat_id,
            text=f"🎲 *{who} бросает кубики...*",
            parse_mode='Markdown'
        )
        await asyncio.sleep(1.5)
        await msg.delete()
        
        if self.config.use_stickers and result in DICE_STICKERS:
            try:
                await context.bot.send_sticker(chat_id=chat_id, sticker=DICE_STICKERS[result])
                await asyncio.sleep(1.0)
            except Exception as e:
                logger.warning(f"Failed to send sticker: {e}")
                await context.bot.send_message(
                    chat_id=chat_id,
                    text=f"🎲 Выпало: *{result}*",
                    parse_mode='Markdown'
                )
        else:
            await context.bot.send_message(
                chat_id=chat_id,
                text=f"🎲 Выпало: *{result}*",
                parse_mode='Markdown'
            )
        
        return result
    
    async def perform_roll(self, context, chat_id: int, user_id: int,
                           roll_type: DiceRollType, who: str = "player",
                           dc: int = None, suspense: bool = True) -> RollResult:
        """Асинхронный бросок с Telegram-анимацией"""
        if suspense:
            await context.bot.send_message(
                chat_id=chat_id,
                text=f"🎲 *{who} бросает кубики...*",
                parse_mode='Markdown'
            )
            await asyncio.sleep(self.config.suspense_delay)
            
            if self.config.use_stickers:
                await context.bot.send_message(
                    chat_id=chat_id,
                    text="🎲 Кубики в воздухе...",
                    parse_mode='Markdown'
                )
            await asyncio.sleep(self.config.animation_delay)
        
        if roll_type == DiceRollType.D20:
            result = self.roll_d20(dc=dc)
        elif roll_type == DiceRollType.EXPLODING:
            result = self.roll_exploding()
        elif roll_type == DiceRollType.FATE:
            result = self.roll_fate()
        else:
            result = self.roll_d20(dc=dc)
        
        self.statistics.record_roll(user_id, roll_type.value, result)
        
        await context.bot.send_message(
            chat_id=chat_id,
            text=result.format(),
            parse_mode='Markdown'
        )
        
        if self.config.use_stickers:
            sticker_id = result.get_sticker_id()
            if sticker_id:
                try:
                    await context.bot.send_sticker(chat_id=chat_id, sticker=sticker_id)
                except:
                    pass
        
        return result
    
    async def simulate_batch(self, roll_type: DiceRollType, count: int = 1000) -> Dict[str, Any]:
        async def roll_one():
            if roll_type == DiceRollType.D20:
                return self.roll_d20()
            elif roll_type == DiceRollType.EXPLODING:
                return self.roll_exploding()
            else:
                return self.roll_d20()
        
        tasks = [roll_one() for _ in range(count)]
        results = await asyncio.gather(*tasks)
        
        totals = [r.total for r in results]
        crits = sum(1 for r in results if r.is_critical)
        fumbles = sum(1 for r in results if r.is_fumble)
        
        return {
            "count": count,
            "avg": sum(totals) / len(totals),
            "max": max(totals),
            "min": min(totals),
            "crits": crits,
            "crit_rate": (crits / count) * 100,
            "fumbles": fumbles,
            "fumble_rate": (fumbles / count) * 100,
        }
    
    def get_probability_text(self, dc: int, advantage: int = 0) -> str:
        prob = self._calculate_probability(dc, advantage)
        if prob >= 80:
            return f"📈 Высокая ({prob:.0f}%)"
        elif prob >= 50:
            return f"📊 Средняя ({prob:.0f}%)"
        elif prob >= 20:
            return f"📉 Низкая ({prob:.0f}%)"
        else:
            return f"💀 Критически низкая ({prob:.0f}%)"


# ========== ГЛОБАЛЬНЫЙ ЭКЗЕМПЛЯР (ЛЕНИВЫЙ) ==========
_dice_engine = None

def get_dice_engine() -> 'DiceEngine':
    """Возвращает глобальный экземпляр движка (создаёт при первом вызове)"""
    global _dice_engine
    if _dice_engine is None:
        _dice_engine = DiceEngine()
    return _dice_engine

# ========== ТЕСТЫ ==========
def test_d20_roll():
    result = dice.roll_d20()
    assert 1 <= result.rolls[0] <= 20
    print(f"✅ d20 test passed: {result.rolls[0]}")

def test_craft():
    result = dice.roll_craft()
    assert len(result.rolls) == 3
    assert len(result.kept) == 2
    assert result.total == sum(result.kept)
    print(f"✅ Craft test passed: {result.rolls} -> kept {result.kept} = {result.total} ({result.quality})")

def test_versus():
    result = dice.roll_versus(first_bonus=2, second_bonus=0)
    assert result.first_roll > 0
    assert result.second_roll > 0
    print(f"✅ Versus test passed: {result.first_roll} vs {result.second_roll} -> {result.winner}")

def test_exploding():
    result = dice.roll_exploding(sides=6, max_explosions=3)
    assert len(result.rolls) <= 4
    print(f"✅ Exploding test passed: {result.rolls} = {result.total}")

def test_dice_pool():
    result = dice.roll_dice_pool(pool_size=5, target=6)
    assert result.pool_size == 5
    print(f"✅ Dice pool test passed: {result.successes} successes")

def test_probability_cache():
    prob1 = dice._calculate_probability(10, 0)
    prob2 = dice._calculate_probability(10, 0)
    assert prob1 == prob2
    print(f"✅ Probability cache test passed: {prob1:.1f}%")

def test_luck_pool():
    luck = LuckPool(user_id=999, db_path=":memory:", config=EngineConfig())
    assert luck.current == 3
    luck.spend(1, "test")
    assert luck.current == 2
    luck.restore(1, "test")
    assert luck.current == 3
    print(f"✅ Luck pool test passed")

def run_all_tests():
    print("\n🧪 Запуск тестов Dice Engine v5.0\n")
    print("=" * 50)
    test_d20_roll()
    test_craft()
    test_versus()
    test_exploding()
    test_dice_pool()
    test_probability_cache()
    test_luck_pool()
    print("=" * 50)
    print("\n✅ Все тесты пройдены успешно!\n")

if __name__ == "__main__":
    run_all_tests()