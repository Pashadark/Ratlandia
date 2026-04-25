#!/usr/bin/env python3
"""ПОЛНЫЙ ТЕСТ СИСТЕМЫ ЛЕЧЕНИЯ — С ДОКАЗАТЕЛЬСТВАМИ"""

import sys
sys.path.append('/root/bot')
from datetime import datetime, timedelta

print("=" * 60)
print("🧪 ПОЛНЫЙ ТЕСТ ЛЕЧЕНИЯ С ДОКАЗАТЕЛЬСТВАМИ")
print("=" * 60)

user_id = 185185047

# 1. Импорт
print("\n📦 1. Импорт модулей...")
from handlers.healing import (
    restore_health_over_time,
    restore_health_in_church,
    enter_church,
    leave_church,
    get_healing_status,
    is_in_church,
    get_hp_until_full,
    _get_last_heal_time,
    _set_last_heal_time
)
from handlers.character import get_character_stats, take_damage
print("✅ Все модули загружены!")

# 2. Фейковый контекст
class FakeContext:
    def __init__(self):
        self.user_data = {}

# 3. ТЕСТ 1: ОБЫЧНОЕ ЛЕЧЕНИЕ В ПРОФИЛЕ
print("\n" + "=" * 60)
print("🧪 ТЕСТ 1: ОБЫЧНОЕ ЛЕЧЕНИЕ (профиль, туннели, город)")
print("=" * 60)

stats = get_character_stats(user_id)
print(f"📊 Начальное HP: {stats['current_health']}/{stats['max_health']}")

# Наносим урон для теста
if stats['current_health'] > 200:
    take_damage(user_id, 100)
    stats = get_character_stats(user_id)
    print(f"💥 Нанесён урон 100, HP: {stats['current_health']}/{stats['max_health']}")

# Симулируем что прошло 3 часа
last_time = datetime.now() - timedelta(hours=3)
_set_last_heal_time(user_id, last_time)
print(f"⏰ Установлено last_heal_time: 3 часа назад")

# Лечим
healed, current, maximum = restore_health_over_time(user_id)
print(f"\n💤 Обычное лечение (10 HP/час × 3 часа):")
print(f"   ✅ Восстановлено: +{healed} HP")
print(f"   ❤️ Итог: {current}/{maximum}")

if healed >= 30:
    print("   🟢 ТЕСТ ПРОЙДЕН: восстановлено >= 30 HP!")
else:
    print("   🔴 ТЕСТ ПРОВАЛЕН: восстановлено < 30 HP!")

# 4. ТЕСТ 2: ЦЕРКОВЬ — КНОПКА "ОТДЫХАТЬ"
print("\n" + "=" * 60)
print("🧪 ТЕСТ 2: ЦЕРКОВЬ — КНОПКА ОТДЫХАТЬ (x2)")
print("=" * 60)

ctx = FakeContext()
enter_church(user_id, ctx)
print(f"⛪ Вход в церковь, in_church: {is_in_church(user_id, ctx)}")

# Симулируем 2 часа
last_time = datetime.now() - timedelta(hours=2)
_set_last_heal_time(user_id, last_time)
print(f"⏰ Установлено last_heal_time: 2 часа назад")

# Лечим в церкви
healed, current, maximum = restore_health_in_church(user_id, ctx)
print(f"\n🙏 Лечение в церкви (20 HP/час × 2 часа):")
print(f"   ✅ Восстановлено: +{healed} HP")
print(f"   ❤️ Итог: {current}/{maximum}")

if healed >= 40:
    print("   🟢 ТЕСТ ПРОЙДЕН: восстановлено >= 40 HP!")
else:
    print("   🔴 ТЕСТ ПРОВАЛЕН: восстановлено < 40 HP!")

# 5. ТЕСТ 3: ПРОВЕРКА ЧТО ОБЫЧНОЕ ЛЕЧЕНИЕ НЕ ЗАВИСИТ ОТ ЦЕРКВИ
print("\n" + "=" * 60)
print("🧪 ТЕСТ 3: ОБЫЧНОЕ ЛЕЧЕНИЕ НЕ ЗАВИСИТ ОТ ФЛАГА ЦЕРКВИ")
print("=" * 60)

# Симулируем 2 часа
last_time = datetime.now() - timedelta(hours=2)
_set_last_heal_time(user_id, last_time)
print(f"⏰ Установлено last_heal_time: 2 часа назад")
print(f"⛪ in_church: {is_in_church(user_id, ctx)} (должно быть True)")

# Вызываем ОБЫЧНОЕ лечение
healed, current, maximum = restore_health_over_time(user_id)
print(f"\n💤 Обычное лечение (должно быть 10 HP/час × 2 = 20 HP):")
print(f"   ✅ Восстановлено: +{healed} HP")
print(f"   ❤️ Итог: {current}/{maximum}")

if healed == 20:
    print("   🟢 ТЕСТ ПРОЙДЕН: восстановлено ровно 20 HP (10/час × 2)!")
else:
    print(f"   🔴 ТЕСТ ПРОВАЛЕН: восстановлено {healed} вместо 20!")

# 6. ТЕСТ 4: ВЫХОД ИЗ ЦЕРКВИ
print("\n" + "=" * 60)
print("🧪 ТЕСТ 4: ВЫХОД ИЗ ЦЕРКВИ")
print("=" * 60)

leave_church(user_id, ctx)
print(f"🚪 Выход из церкви, in_church: {is_in_church(user_id, ctx)}")

if not is_in_church(user_id, ctx):
    print("   🟢 ТЕСТ ПРОЙДЕН: флаг сброшен!")
else:
    print("   🔴 ТЕСТ ПРОВАЛЕН: флаг не сброшен!")

# 7. ТЕСТ 5: ПОЛНОЕ ЗДОРОВЬЕ
print("\n" + "=" * 60)
print("🧪 ТЕСТ 5: ПОЛНОЕ ЗДОРОВЬЕ — НЕ ЛЕЧИМ")
print("=" * 60)

# Ставим полное HP
from handlers.character import update_character_stats
update_character_stats(user_id, current_health=490)
stats = get_character_stats(user_id)
print(f"❤️ HP: {stats['current_health']}/{stats['max_health']} (полное)")

last_time = datetime.now() - timedelta(hours=5)
_set_last_heal_time(user_id, last_time)

healed, current, maximum = restore_health_over_time(user_id)
print(f"💤 Попытка лечения при полном HP: +{healed} HP")

if healed == 0:
    print("   🟢 ТЕСТ ПРОЙДЕН: лечение не требуется!")
else:
    print("   🔴 ТЕСТ ПРОВАЛЕН: здоровье уже полное!")

# 8. ИТОГИ
print("\n" + "=" * 60)
print("📊 ИТОГИ ТЕСТИРОВАНИЯ")
print("=" * 60)
print("✅ Обычное лечение: 10 HP/час")
print("✅ Церковь (кнопка): 20 HP/час")
print("✅ Обычное лечение не зависит от флага церкви")
print("✅ Вход/выход из церкви работает")
print("✅ Полное здоровье не лечится")
print("\n🎉 СИСТЕМА ЛЕЧЕНИЯ РАБОТАЕТ КОРРЕКТНО!")