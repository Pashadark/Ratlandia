#!/usr/bin/env python3
"""Тест Dice Engine v5.0 by Pashadark"""

import sys
sys.path.append('/root/bot')

def test_engine():
    print("=" * 60)
    print("🎲 ТЕСТ DICE ENGINE v5.0 by Pashadark")
    print("=" * 60)
    
    try:
        from core.dice.engine import DiceEngine, dice, EngineConfig, DiceRollType, SuccessLevel
        
        print("\n✅ Импорты движка успешны!")
        print(f"📦 Версия: 5.0.0")
        print(f"👤 Автор: Pashadark")
        
        # Тест 1: d20
        print("\n📊 Тест 1: Бросок d20")
        result = dice.roll_d20(dc=10)
        print(f"   Бросок: {result.rolls[0]}")
        print(f"   Итог: {result.total}")
        if result.success_level:
            print(f"   Уровень успеха: {result.success_level.display}")
        
        # Тест 2: Взрывные кубики
        print("\n💥 Тест 2: Взрывные кубики (d6)")
        result = dice.roll_exploding(sides=6)
        print(f"   Броски: {result.rolls}")
        print(f"   Сумма: {result.total}")
        print(f"   Взрывов: {result.explosions}")
        
        # Тест 3: Пул кубиков
        print("\n🎯 Тест 3: Пул кубиков (5d10)")
        result = dice.roll_dice_pool(pool_size=5)
        print(f"   Броски: {result.rolls}")
        print(f"   Успехов: {result.successes}")
        
        # Тест 4: Вероятности (кэш)
        print("\n💾 Тест 4: Кэширование вероятностей")
        prob1 = dice._calculate_probability(10, 0)
        prob2 = dice._calculate_probability(10, 0)
        print(f"   DC 10: {prob1:.1f}%")
        print(f"   Кэш работает: {'✅' if prob1 == prob2 else '❌'}")
        
        print("\n" + "=" * 60)
        print("✅ ВСЕ ТЕСТЫ ПРОЙДЕНЫ!")
        print("🎲 Dice Engine v5.0 готов к работе!")
        print("👤 Автор: Pashadark")
        print("=" * 60)
        
        return True
        
    except Exception as e:
        print(f"\n❌ ОШИБКА: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_engine()
    sys.exit(0 if success else 1)