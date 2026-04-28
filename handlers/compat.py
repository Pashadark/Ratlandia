"""
СОВМЕСТИМОСТЬ — реэкспорт из новой структуры под старыми именами
"""
import sys

# player
import handlers.player.commands as _p_cmd
import handlers.player.profile as _p_prof
import handlers.player.inventory as _p_inv
import handlers.player.callbacks as _p_cb
import handlers.player.character as _p_char
import handlers.player.class_selection as _p_cs
import handlers.player.items as _p_items
import handlers.player.titles as _p_titles

sys.modules['handlers.commands'] = _p_cmd
sys.modules['handlers.profile'] = _p_prof
sys.modules['handlers.inventory'] = _p_inv
sys.modules['handlers.callbacks'] = _p_cb
sys.modules['handlers.character'] = _p_char
sys.modules['handlers.class_selection'] = _p_cs
sys.modules['handlers.items'] = _p_items
sys.modules['handlers.titles'] = _p_titles

# city
sys.modules['handlers.shop'] = __import__('handlers.city.shop', fromlist=['*'])
sys.modules['handlers.church'] = __import__('handlers.city.church', fromlist=['*'])
sys.modules['handlers.daily'] = __import__('handlers.city.daily', fromlist=['*'])

# game
sys.modules['handlers.tunnel'] = __import__('handlers.game.commands', fromlist=['*'])
sys.modules['handlers.tunnel_battle'] = __import__('handlers.game.battle', fromlist=['*'])
sys.modules['handlers.tunnel_rooms'] = __import__('handlers.game.rooms', fromlist=['*'])
sys.modules['handlers.tunnel_effects'] = __import__('handlers.game.effects', fromlist=['*'])
sys.modules['handlers.tunnel_monsters'] = __import__('handlers.game.monsters', fromlist=['*'])
sys.modules['handlers.tunnel_coop'] = __import__('handlers.game.coop', fromlist=['*'])

# blacksmith
sys.modules['handlers.crafting'] = __import__('handlers.blacksmith.crafting', fromlist=['*'])
sys.modules['handlers.enchant'] = __import__('handlers.blacksmith.enchant', fromlist=['*'])

# clan
sys.modules['handlers.clan'] = __import__('handlers.clan.commands', fromlist=['*'])

# achievements
sys.modules['handlers.achievements_data'] = __import__('handlers.achievements.data', fromlist=['*'])
sys.modules['handlers.healing'] = __import__('handlers.achievements.healing', fromlist=['*'])
sys.modules['handlers.effects'] = __import__('handlers.achievements.effects', fromlist=['*'])

# admin & bug_report
sys.modules['handlers.admin'] = __import__('handlers.admin.commands', fromlist=['*'])
sys.modules['handlers.bug_report'] = __import__('handlers.bug_report.commands', fromlist=['*'])