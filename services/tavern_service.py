"""Логика таверны - игры, пиво, атмосфера"""

import random
import asyncio
from typing import Optional, Dict, Any, List, Tuple
from datetime import datetime, timedelta

from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.constants import ParseMode

from services.dice_service import dice_service
from core.dice.models import GameMode, DiceGameResult, PlayerStats
from core.database import db

class TavernService:
    """Сервис для работы таверны"""
    
    # Фразы для атмосферы
    PLAYER_ROLL_TEXTS = [
        "🎲 Ты трясёшь кость в лапах... Бросок!",
        "🎲 Кость летит по столу... Стук... Стук...",
        "🎲 Решающий момент! Кость в воздухе!",
        "🎲 Ты шепчешь молитву крысиным богам... Бросок!",
        "🎲 Ты задерживаешь дыхание и бросаешь...",
    ]
    
    SHADOW_ROLL_TEXTS = [
        "💀 Тень усмехается и бросает кость...",
        "💀 Из тьмы доносится стук кости...",
        "💀 Холодная лапа Тени бросает...",
        "💀 Тень прищуривается... Бросок!",
        "💀 Тьма сгущается... Кость Тени в воздухе!",
    ]
    
    WIN_TEXTS = [
        "🎉 *ПОБЕДА! Ты обыграл Тень!*",
        "🏆 *ТРИУМФ! Удача на твоей стороне!*",
        "⚡ *ВЕЛИКОЛЕПНО! Тень повержена!*",
        "👑 *КОРОЛЕВСКИЙ БРОСОК! Победа за тобой!*",
        "🌟 *ФАНТАСТИКА! Ты сорвал банк!*",
    ]
    
    LOSE_TEXTS = [
        "💔 *ПРОИГРЫШ... Тень оказалась сильнее.*",
        "🌑 *ТЬМА ПОБЕДИЛА... Может, в следующий раз?*",
        "😢 *НЕУДАЧА... Судьба сегодня не на твоей стороне.*",
        "🍂 *ПОРАЖЕНИЕ... Но ты ещё вернёшься!*",
        "🥀 *УВЫ... Тень забрала твои крошки.*",
    ]
    
    DRAW_TEXTS = [
        "⚖️ *НИЧЬЯ! Судьба колеблется... Бросаем снова!*",
        "🔄 *РАВЕНСТВО! Тень и свет сошлись в схватке!*",
        "⚖️ *НИКТО НЕ УСТУПАЕТ! Переброс!*",
    ]
    
    WIN_FLAVOR_TEXTS = [
        "_Сама Тень склоняется перед твоей удачей!_",
        "_Трактирщик одобрительно кивает из-за стойки!_",
        "_Крысиные боги сегодня на твоей стороне!_",
        "_Тень недовольно ворчит, отступая в угол..._",
        "_Удача любит смелых! И сегодня ты это доказал!_",
    ]
    
    LOSE_FLAVOR_TEXTS = [
        "_Тень усмехается из своего угла. Может, в следующий раз?_",
        "_Трактирщик сочувственно качает головой._",
        "_Сегодня не твой день. Но тьма не вечна!_",
        "_Тень забирает твои крошки с холодным смехом..._",
        "_Удача отвернулась, но она вернётся!_",
    ]
    
    CRIT_WIN_TEXTS = [
        "🔥 *ЛЕГЕНДАРНАЯ ПОБЕДА! 6 против 1!*",
        "💫 *НЕВЕРОЯТНО! Тень в шоке!*",
        "⚡ *ЭПИЧЕСКИЙ БРОСОК! Такое видят раз в жизни!*",
    ]
    
    CRIT_LOSE_TEXTS = [
        "💀 *СОКРУШИТЕЛЬНОЕ ПОРАЖЕНИЕ! 1 против 6...*",
        "🌑 *ТЬМА ПОГЛОТИЛА ТЕБЯ... Полный провал!*",
        "😱 *КОШМАР! Тень смеётся над тобой!*",
    ]
    
    DOUBLE_SIX_TEXTS = [
        "🌟 *НЕВЕРОЯТНО! ДВЕ ШЕСТЁРКИ! Тень в шоке!*",
        "💫 *ЛЕГЕНДАРНЫЙ ДУБЛЬ! Шесть и шесть!*",
        "👑 *КОРОЛЬ КОСТЕЙ! Две шестёрки — это знак свыше!*",
    ]
    
    DOUBLE_ONE_TEXTS = [
        "🐀 *КРЫСИНЫЙ ДУБЛЬ! Две единицы! Тень смеётся...*",
        "💀 *ПРОКЛЯТИЕ ТЕНИ! Дважды по единице...*",
        "🍂 *НЕВЕЗЕНИЕ! Единица и единица. Бывает...*",
    ]
    
    BEER_EFFECTS = [
        {"name": "🧀 Сырный дух", "effect": "xp_boost", "value": 10, "icon": "🧀", "desc": "+10% XP за игру"},
        {"name": "🛡️ Хмельная удача", "effect": "luck", "value": 5, "icon": "🛡️", "desc": "+5% к удаче в костях"},
        {"name": "⚔️ Пьяная ярость", "effect": "damage_boost", "value": 5, "icon": "⚔️", "desc": "+5% к урону"},
        {"name": "👁️ Зоркий глаз", "effect": "crit_chance", "value": 3, "icon": "👁️", "desc": "+3% шанс крита"},
        {"name": "🍀 Пьяная удача", "effect": "item_find", "value": 5, "icon": "🍀", "desc": "+5% шанс найти предмет"},
        {"name": "🔍 Сырный нюх", "effect": "bonus_crumbs", "value": 10, "icon": "🔍", "desc": "+10% крошек с побед"},
    ]
    
    BEER_DRINK_TEXTS = [
        """_Ты подносишь кружку к губам и делаешь большой глоток. Пенная жидкость обжигает горло, но тут же разливается приятным теплом по всему телу. Старый трактирщик одобрительно кивает из-за стойки._

_«Добрый Ильяс эль, — бормочешь ты, вытирая пену с усов. — Чувствую, удача сегодня на моей стороне!»_""",
        """_Ты берёшь запотевшую кружку и вдыхаешь аромат хмеля и сырной закваски. Первый глоток обжигает, но тут же согревает изнутри. Трактирщик подмигивает тебе из-за стойки._

_«Ильяс эль — лучший в Ратляндии, — думаешь ты, делая второй глоток. — Сегодня я точно сорву банк!»_""",
        """_Пена стекает по стенкам кружки, пока ты делаешь жадный глоток. Знакомый вкус Ильяс эля — терпкий, с нотками выдержанного сыра и дубовой бочки. Трактирщик кивает с уважением._

_«Хороший выбор, — говорит он. — Этот эль варят по древнему рецепту подземных пивоваров!»_""",
    ]
    
    # ========== ОСНОВНЫЕ МЕТОДЫ ==========
    
    def get_player_stats(self, user_id: int) -> PlayerStats:
        """Получает статистику игрока для таверны"""
        return dice_service.get_player_stats(user_id)
    
    def get_crumbs(self, user_id: int) -> int:
        """Получает баланс крошек"""
        return db.get_crumbs(user_id)
    
    def play_dice_game(self, user_id: int, bet: int, 
                       use_daily_bonus: bool = False,
                       free_reroll: bool = False) -> Tuple[DiceGameResult, Dict[str, Any]]:
        """Играет в кости и возвращает результат + данные для анимации"""
        
        # Проверяем баланс
        if not free_reroll:
            crumbs = self.get_crumbs(user_id)
            if crumbs < bet:
                return None, {"error": "insufficient_funds", "required": bet, "have": crumbs}
        
        # Играем
        result = dice_service.play_vs_shadow(
            user_id, bet, 
            daily_bonus=use_daily_bonus,
            free_reroll=free_reroll
        )
        
        # Если ничья - рекурсивно перебрасываем
        if result.bet.is_draw:
            return self.play_dice_game(user_id, bet, use_daily_bonus, free_reroll)
        
        # Генерируем данные для анимации
        animation_data = self._generate_animation_data(result)
        
        return result, animation_data
    
    def _generate_animation_data(self, result: DiceGameResult) -> Dict[str, Any]:
        """Генерирует данные для анимации броска"""
        
        # Тексты для анимации
        player_text = random.choice(self.PLAYER_ROLL_TEXTS)
        shadow_text = random.choice(self.SHADOW_ROLL_TEXTS)
        
        # Текст результата
        if result.bet.is_win:
            if result.bet.is_critical:
                title = random.choice(self.CRIT_WIN_TEXTS)
            elif result.player_roll == 6 and result.shadow_roll == 6:
                title = random.choice(self.DOUBLE_SIX_TEXTS)
            else:
                title = random.choice(self.WIN_TEXTS)
            flavor = random.choice(self.WIN_FLAVOR_TEXTS)
        else:
            if result.player_roll == 1 and result.shadow_roll == 6:
                title = random.choice(self.CRIT_LOSE_TEXTS)
            elif result.player_roll == 1 and result.shadow_roll == 1:
                title = random.choice(self.DOUBLE_ONE_TEXTS)
            else:
                title = random.choice(self.LOSE_TEXTS)
            flavor = random.choice(self.LOSE_FLAVOR_TEXTS)
        
        # Проверка на счастливую семёрку (возврат половины при проигрыше)
        is_lucky_seven = (not result.bet.is_win and 
                          result.player_roll + result.shadow_roll == 7)
        
        return {
            "player_text": player_text,
            "shadow_text": shadow_text,
            "title": title,
            "flavor": flavor,
            "player_roll": result.player_roll,
            "shadow_roll": result.shadow_roll,
            "is_win": result.bet.is_win,
            "is_critical": result.bet.is_critical,
            "is_lucky_seven": is_lucky_seven,
            "multiplier": result.bet.multiplier,
            "win_amount": result.bet.win_amount,
            "net_profit": result.bet.net_profit,
            "win_streak": result.win_streak,
            "lose_streak": result.lose_streak
        }
    
    def buy_beer(self, user_id: int, beer_cost: int = 50) -> Tuple[bool, Optional[Dict], str]:
        """Покупает пиво и возвращает эффект"""
        
        # Проверяем баланс
        crumbs = self.get_crumbs(user_id)
        if crumbs < beer_cost:
            return False, None, f"❌ Недостаточно крошек! Нужно {beer_cost} 🧀, у тебя {crumbs} 🧀"
        
        # Списываем крошки
        if not db.spend_crumbs(user_id, beer_cost):
            return False, None, "❌ Ошибка при списании крошек!"
        
        # Выбираем случайный эффект
        effect = random.choice(self.BEER_EFFECTS).copy()
        
        # Добавляем эффект
        dice_service.add_beer_effect(user_id, effect, duration_hours=1)
        
        # Текст для атмосферы
        drink_text = random.choice(self.BEER_DRINK_TEXTS)
        
        return True, effect, drink_text
    
    def get_beer_effects_text(self, user_id: int) -> str:
        """Форматирует активные эффекты пива"""
        effects = dice_service.get_active_beer_effects(user_id)
        
        if not effects:
            return ""
        
        text = "\n\n🍺 *АКТИВНЫЕ ЭФФЕКТЫ ПИВА:*\n"
        for eff in effects[:5]:
            # Парсим время до конца
            try:
                expires = datetime.fromisoformat(eff['expires_at'])
                time_left = expires - datetime.now()
                minutes_left = int(time_left.total_seconds() / 60)
                
                if minutes_left > 60:
                    hours = minutes_left // 60
                    mins = minutes_left % 60
                    time_str = f"{hours}ч {mins}мин"
                elif minutes_left > 0:
                    time_str = f"{minutes_left}мин"
                else:
                    time_str = "истекает"
            except:
                time_str = "активен"
            
            # Ищем иконку
            icon = "🍺"
            for beer in self.BEER_EFFECTS:
                if beer['effect'] == eff['effect']:
                    icon = beer['icon']
                    break
            
            text += f"  {icon} {eff['name']} ({time_str})\n"
        
        return text
    
    def check_free_reroll(self, user_id: int, lose_streak: int) -> bool:
        """Проверяет возможность бесплатного переброса"""
        if lose_streak >= 3:
            return random.randint(1, 100) <= 30  # 30% шанс
        return False
    
    def format_stats_message(self, user_id: int) -> str:
        """Форматирует сообщение со статистикой для таверны"""
        stats = self.get_player_stats(user_id)
        crumbs = self.get_crumbs(user_id)
        
        daily_status = "✅ *ДОСТУПЕН!*" if stats.daily_bonus_available else "❌ Уже использован"
        
        text = f"""🎲 *ТАВЕРНА «ХРОМАЯ КРЫСА»*

_В тёмном углу таверны, под тусклым светом масляной лампы, стоит старый игорный стол. Местные говорят, что по ночам здесь играет сама Тень — древний дух канализации..._

🎯 *Правила:* ты и Тень бросаете кубик. У кого больше — тот побеждает!
⚖️ Ничья — переброс

🧀 Твой баланс: *{crumbs}* крошек
🎮 Сыграно игр: *{stats.total_games}*
🏆 Побед: *{stats.total_wins}* | 💔 Поражений: *{stats.total_losses}*
📊 Винрейт: *{stats.win_rate:.1f}%*

🔥 Серия побед: *{stats.current_win_streak}*
💀 Серия поражений: *{stats.current_lose_streak}*
{stats.luck_status}

🎁 Ежедневный бонус: {daily_status}"""
        
        # Добавляем эффекты пива
        text += self.get_beer_effects_text(user_id)
        
        return text
    
    def format_result_message(self, result: DiceGameResult, 
                              animation_data: Dict[str, Any]) -> str:
        """Форматирует сообщение с результатом игры"""
        
        data = animation_data
        crumbs = self.get_crumbs(result.user_id)
        
        text = f"{data['title']}\n\n{data['flavor']}\n\n"
        text += f"🎲 Твой кубик: *{data['player_roll']}*  |  💀 Кубик Тени: *{data['shadow_roll']}*\n\n"
        
        if result.bet.is_win:
            text += f"🏆 Выигрыш: *+{data['net_profit']}* 🧀 (x{data['multiplier']:.1f})\n"
            text += f"📦 Всего в кошельке: *{crumbs}* 🧀\n\n"
            text += f"🔥 Серия побед: *{data['win_streak']}*"
        else:
            text += f"💸 Потеряно: *{result.bet.bet_amount}* 🧀\n"
            text += f"📦 Осталось в кошельке: *{crumbs}* 🧀\n\n"
            
            if data.get('is_lucky_seven'):
                text += "🍀 *Счастливая семёрка!* Возвращена половина ставки!\n"
            
            text += f"💀 Серия поражений: *{data['lose_streak']}*"
        
        return text
    
    def get_main_keyboard(self, show_free_reroll: bool = False,
                          free_reroll_bet: int = None) -> InlineKeyboardMarkup:
        """Создаёт главную клавиатуру таверны"""
        
        if show_free_reroll:
            return InlineKeyboardMarkup([
                [InlineKeyboardButton("🍀 Бесплатный переброс", callback_data="dice_free_reroll")],
                [InlineKeyboardButton("🔙 В таверну", callback_data="profile_dice")]
            ])
        
        return InlineKeyboardMarkup([
            [InlineKeyboardButton("🎲 Играть снова", callback_data="dice_play_again")],
            [InlineKeyboardButton("🔙 В таверну", callback_data="profile_dice")]
        ])
    
    def get_bet_keyboard(self) -> InlineKeyboardMarkup:
        """Создаёт клавиатуру выбора ставки"""
        return InlineKeyboardMarkup([
            [InlineKeyboardButton("💰 50 🧀", callback_data="dice_start_50"),
             InlineKeyboardButton("💰 100 🧀", callback_data="dice_start_100")],
            [InlineKeyboardButton("💰 250 🧀", callback_data="dice_start_250"),
             InlineKeyboardButton("💰 500 🧀", callback_data="dice_start_500")],
            [InlineKeyboardButton("🍺 Выпить пива (50 🧀)", callback_data="beer_buff")],
            [InlineKeyboardButton("🏆 Турнир костей", callback_data="dice_tournament")],
            [InlineKeyboardButton("✏️ Своя ставка", callback_data="dice_custom_bet")],
            [InlineKeyboardButton("🔙 В город", callback_data="city_menu")]
        ])


# Глобальный экземпляр сервиса (ленивый)
_tavern_service = None

def get_tavern_service() -> 'TavernService':
    """Возвращает глобальный экземпляр TavernService (создаёт при первом вызове)"""
    global _tavern_service
    if _tavern_service is None:
        _tavern_service = TavernService()
    return _tavern_service

# Для обратной совместимости
tavern_service = get_tavern_service()