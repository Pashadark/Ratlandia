from telegram import Update, constants, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
import logging
import sys
import asyncio
import traceback

sys.path.append('/root/bot')
from handlers.game_rat import active_games, RatGame
from telegram_bot_pagination import InlineKeyboardPaginator

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(levelname)-8s | %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

# ИМПОРТЫ ИЗ PROFILE
from handlers.profile import (
    profile_command, inventory_command, equipment_command, 
    achievements_command, handle_equip, handle_unequip, handle_use_consumable,
    handle_inventory_filter, show_filtered_inventory,
    show_available_for_slot, handle_equip_from_list, show_equipment_list_by_slot
)
from handlers.clan import clan_join_menu, clan_achievements_callback
from handlers.city import city_menu, city_gates_menu, city_church_menu
from handlers.titles import set_active_title, titles_command
from handlers.tunnel import show_stats_menu, show_tunnel_menu, start_new_run, upgrade_stat_callback
from handlers.shop import (
    shop_buy_menu, shop_sell_menu, shop_command, handle_shop_sell,
    shop_category, handle_shop_buy, handle_shop_page
)
from handlers.hall_of_fame import hall_of_fame
from handlers.clan import (
    clan_command, clan_top_callback, clan_info_callback,
    clan_create_menu, clan_register, clan_manage,
    clan_members_list, clan_leave, clan_disband,
    clan_join_menu, clan_promote_select, clan_demote_select,
    clan_promote_user, clan_demote_user, clan_achievements_callback
)
from handlers.blacksmith import (
    blacksmith_menu, forge_select_recipe, forge_craft, forge_show_resources, 
    forge_show_recipes, forge_sharpen, forge_engrave, forge_fortune, 
    forge_show_resources_category, forge_show_resources_all
)
from handlers.daily import daily_command
from handlers.game_rat import (
    show_consumables_menu, handle_use_consumable as game_handle_use_consumable,
    show_chests_menu, handle_open_chest, rat_rules, night_phase
)
from handlers.church import church_rest, church_leave
from handlers.tunnel_rooms import (
    enter_room, handle_chest_choice, handle_altar_offer,
    process_room_transition, process_skip_room, go_home
)
from handlers.tunnel_battle import (
    start_battle, handle_tunnel_defend, handle_tunnel_attack,
    handle_tunnel_flee_new, handle_tunnel_break_free, handle_tunnel_continue_battle,
    handle_coop_defend, handle_coop_attack
)
from handlers.tunnel_coop import send_coop_invite
from handlers.tunnel_monsters import get_tunnel_run
from handlers.healing import restore_health_over_time


def escape_markdown(text: str) -> str:
    import re
    if not text:
        return ""
    escape_chars = r'_*[]()~`>#+-=|{}.!'
    return re.sub(f'([{re.escape(escape_chars)}])', r'\\\1', text)


async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    data = query.data
    user_id = query.from_user.id
    chat_id = update.effective_chat.id
    user_name = query.from_user.full_name
    
    restore_health_over_time(user_id, context)
    
    logger.info(f"🔘 Нажата кнопка: {data} от user_id={user_id}")
    
    try:
        # ========== ПРОФИЛЬ ==========
        if data == "profile_achievements":
            await achievements_command(update, context)
        elif data == "dice_tournament":
            from handlers.dice import show_tournament
            await show_tournament(update, context)
        elif data == "profile_inventory":
            await inventory_command(update, context)
        elif data == "city_menu":
            await city_menu(update, context)
        elif data == "achievements_all":
            await achievements_command(update, context, show_all=True)
        elif data == "achievements_compact":
            await achievements_command(update, context, show_all=False)
        elif data == "city_rules":
            await rat_rules(update, context)
        elif data == "set_title_none":
            set_active_title(user_id, None)
            await profile_command(update, context)
        elif data == "profile_history":
            from handlers.profile import history_command
            await history_command(update, context)
        elif data == "profile_history_all":
            from handlers.profile import history_command_all
            await history_command_all(update, context)
        elif data == "profile_equipment":
            await equipment_command(update, context)
        elif data == "tunnel_enter_room":
            await enter_room(update, context, user_id)
        elif data == "tunnel_stats_menu":
            await show_stats_menu(update, context, user_id)
        elif data.startswith("inventory_filter_"):
            filter_type = data.replace("inventory_filter_", "")
            await handle_inventory_filter(update, context, filter_type)
        elif data.startswith("equipment_list_"):
            slot = data.replace("equipment_list_", "")
            await show_equipment_list_by_slot(update, context, slot)
        elif data.startswith("inventory_page_"):
            parts = data.replace("inventory_page_", "").split("#")
            filter_type = parts[0]
            page = int(parts[1]) if len(parts) > 1 else 1
            await show_filtered_inventory(update, context, user_id, filter_type, page)
        
        # ========== МАГАЗИН ==========
        elif data == "shop_buy_menu":
            await shop_buy_menu(update, context)
        elif data == "shop_sell_menu":
            await shop_sell_menu(update, context)
        elif data == "shop_back_to_main":
            await shop_command(update, context)
        elif data.startswith("shop_sell_"):
            item_id = data.replace("shop_sell_", "")
            await handle_shop_sell(update, context, item_id)
        elif data.startswith("shop_cat_"):
            category = data.replace("shop_cat_", "")
            await shop_category(update, context, category)
        
        # ========== КУЗНИЦА ==========
        elif data == "city_forge":
            await blacksmith_menu(update, context)
        elif data.startswith("forge_select_"):
            recipe_id = data.replace("forge_select_", "")
            await forge_select_recipe(update, context, recipe_id)
        elif data.startswith("forge_craft_"):
            recipe_id = data.replace("forge_craft_", "")
            await forge_craft(update, context, recipe_id)
        elif data == "forge_resources":
            await forge_show_resources(update, context)
        elif data == "forge_resources_all":
            await forge_show_resources_all(update, context, 1)
        elif data.startswith("forge_all_page_"):
            page = int(data.replace("forge_all_page_", ""))
            await forge_show_resources_all(update, context, page)
        elif data == "forge_recipes":
            await forge_show_recipes(update, context)
        elif data == "forge_sharpen":
            await forge_sharpen(update, context)
        elif data == "forge_engrave":
            await forge_engrave(update, context)
        elif data == "forge_fortune":
            await forge_fortune(update, context)
        elif data.startswith("forge_res_cat_"):
            category = data.replace("forge_res_cat_", "")
            await forge_show_resources_category(update, context, category)
        
        # ========== ЗАТОЧКА ==========
        elif data.startswith("enchant_"):
            logger.info(f"⚡ Заточка: data={data}")
            # Убираем ТОЛЬКО первый "enchant_"
            data_without_prefix = data[8:]  # "enchant_" = 8 символов
            
            scroll_id = None
            item_id = None
            for sid in ["blessed_scroll_weapon", "blessed_scroll_armor", 
                         "crystal_scroll_weapon", "crystal_scroll_armor",
                         "enchant_scroll_weapon", "enchant_scroll_armor"]:
                if data_without_prefix.endswith("_" + sid):
                    scroll_id = sid
                    item_id = data_without_prefix[:-(len(sid)+1)]
                    break
            
            logger.info(f"⚡ Разобрано: item_id={item_id}, scroll_id={scroll_id}")
            
            if not scroll_id or not item_id:
                await query.answer("❌ Ошибка: неверный формат заточки!", show_alert=True)
                return
            
            from handlers.enchant import perform_enchant_animation
            
            scroll_type = "normal"
            if "blessed" in scroll_id:
                scroll_type = "blessed"
            elif "crystal" in scroll_id:
                scroll_type = "crystal"
            
            await query.answer("⚡ Заточка...")
            await query.message.delete()
            
            from handlers.inventory import remove_item
            remove_item(user_id, scroll_id, 1)
            
            logger.info(f"⚡ Запуск анимации: user={user_id}, item={item_id}, type={scroll_type}")
            success, message, new_item_id = await perform_enchant_animation(context, user_id, item_id, scroll_type)
            logger.info(f"⚡ Результат: success={success}, msg={message[:50]}")
            
            # perform_enchant_animation уже отправила результат с фото
            # Здесь добавляем только клавиатуру
            keyboard = InlineKeyboardMarkup([
                [InlineKeyboardButton("🔨 Ещё заточка", callback_data="forge_sharpen"),
                 InlineKeyboardButton("🏰 В город", callback_data="city_menu")],
            ])
            
            await context.bot.send_message(chat_id=user_id, text="⚡ *Что дальше?*", 
                                           parse_mode='Markdown', reply_markup=keyboard)
        
        # ========== ЦЕРКОВЬ ==========
        elif data == "church_rest":
            await church_rest(update, context)
        elif data == "church_leave":
            await church_leave(update, context)
        
        # ========== ЭКИПИРОВКА ==========
        elif data.startswith("change_slot_"):
            slot = data.replace("change_slot_", "")
            await show_available_for_slot(update, context, slot, page=1)
        elif data.startswith("available_slot_"):
            parts = data.replace("available_slot_", "").split("#")
            slot = parts[0]
            page = int(parts[1]) if len(parts) > 1 else 1
            await show_available_for_slot(update, context, slot, page)
        elif data.startswith("equip_from_list_"):
            item_id = data.replace("equip_from_list_", "")
            await handle_equip_from_list(update, context, item_id)
        elif data == "shop_back_to_categories":
            await shop_buy_menu(update, context)
        elif data.startswith("shop_buy_"):
            item_id = data.replace("shop_buy_", "")
            await handle_shop_buy(update, context, item_id)
        elif data.startswith("shop_page_"):
            parts = data.replace("shop_page_", "").split("_")
            category = parts[0]
            page = int(parts[1]) if len(parts) > 1 else 0
            await handle_shop_page(update, context, category, page)
        
        # ========== ТАВЕРНА ==========
        elif data == "profile_dice":
            from handlers.dice import dice_command
            await dice_command(update, context)
        elif data.startswith("dice_"):
            from handlers.dice import dice_callback
            await dice_callback(update, context)
        elif data == "beer_buff":
            from handlers.dice import buy_beer
            await buy_beer(update, context)
        
        # ========== ВЫБОР КЛАССА ==========
        elif data == "class_selection_back":
            await query.message.delete()
            from handlers.class_selection import send_class_selection
            await send_class_selection(context, user_id, is_reroll=False)
        elif data.startswith("class_info_"):
            class_name = data.replace("class_info_", "")
            await query.message.delete()
            from handlers.class_selection import send_class_info
            await send_class_info(context, user_id, class_name)
        elif data.startswith("class_confirm_"):
            parts = data.replace("class_confirm_", "").split("_")
            class_name = parts[0]
            is_reroll = parts[1] == "1"
            
            if is_reroll:
                from handlers.inventory import get_crumbs, spend_crumbs
                crumbs = get_crumbs(user_id)
                if crumbs < 5000:
                    await query.answer("❌ Нужно 5000 крошек для смены класса!", show_alert=True)
                    return
                spend_crumbs(user_id, 5000)
            
            class_stats = {
                "warrior": {"strength": 2, "agility": 1, "intelligence": 1, "max_health": 0, "max_mana": 0},
                "tank": {"strength": 3, "agility": 1, "intelligence": 0, "max_health": 50, "max_mana": 0},
                "mage": {"strength": 1, "agility": 1, "intelligence": 3, "max_health": 0, "max_mana": 50},
                "rogue": {"strength": 1, "agility": 3, "intelligence": 1, "max_health": 0, "max_mana": 0},
                "berserker": {"strength": 3, "agility": 2, "intelligence": 0, "max_health": -20, "max_mana": 0},
                "archer": {"strength": 1, "agility": 3, "intelligence": 1, "max_health": 0, "max_mana": 0},
            }
            
            if class_name in class_stats:
                from handlers.character import get_character_stats, update_character_stats
                stats_base = get_character_stats(user_id)
                bonuses = class_stats[class_name]
                
                update_character_stats(user_id, 
                    strength=stats_base['strength'] + bonuses['strength'],
                    agility=stats_base['agility'] + bonuses['agility'],
                    intelligence=stats_base['intelligence'] + bonuses['intelligence'],
                    max_health=stats_base['max_health'] + bonuses['max_health'],
                    current_health=stats_base['current_health'] + bonuses['max_health'],
                    max_mana=stats_base['max_mana'] + bonuses['max_mana'],
                    mana=stats_base['mana'] + bonuses['max_mana'],
                    player_class=class_name
                )
                
                class_names_ru = {
                    "warrior": "⚔️ Воин", "tank": "🛡️ Танк", "mage": "🔮 Маг",
                    "rogue": "🗡️ Разбойник", "berserker": "💪 Берсерк", "archer": "🏹 Лучник"
                }
                
                await query.answer(f"✅ Класс: {class_names_ru[class_name]}!" + (" (-5000 🧀)" if is_reroll else ""))
                await query.message.delete()
                
                keyboard = InlineKeyboardMarkup([
                    [InlineKeyboardButton("👤 Профиль", callback_data="back_to_profile"),
                     InlineKeyboardButton("🏰 В город", callback_data="city_menu")],
                ])
                
                await context.bot.send_message(
                    chat_id=user_id,
                    text=f"🎉 *КЛАСС ВЫБРАН!*\n\nТы стал *{class_names_ru[class_name]}*!\n\n_Характеристики обновлены. Проверь профиль._",
                    parse_mode='Markdown', reply_markup=keyboard
                )
        elif data == "change_class_menu":
            from handlers.inventory import get_crumbs
            crumbs = get_crumbs(user_id)
            if crumbs < 5000:
                await query.answer("❌ Нужно 5000 крошек для смены класса!", show_alert=True)
                return
            await query.message.delete()
            from handlers.class_selection import send_class_selection
            await send_class_selection(context, user_id, is_reroll=True)
        
        # ========== ПРОФИЛЬ И ТИТУЛЫ ==========
        elif data == "back_to_profile" or data == "profile_back":
            await profile_command(update, context)
        elif data == "profile_titles":
            await titles_command(update, context)
        elif data == "profile_shop":
            await shop_command(update, context)
        elif data == "profile_daily":
            await daily_command(update, context)
        elif data.startswith("set_title_"):
            title_id = data.replace("set_title_", "")
            set_active_title(user_id, title_id)
            await profile_command(update, context)
        elif data.startswith("equip_"):
            item_id = data.replace("equip_", "")
            await handle_equip(update, context, item_id)
        elif data.startswith("unequip_"):
            slot = data.replace("unequip_", "")
            await handle_unequip(update, context, slot)
        elif data.startswith("use_consumable_"):
            item_id = data.replace("use_consumable_", "")
            await handle_use_consumable(update, context, item_id)
        
        # ========== ЗАЛ СЛАВЫ ==========
        elif data == "city_leaderboard":
            await hall_of_fame(update, context)
        
        # ========== СУНДУКИ ==========
        elif data == "chests_menu":
            await show_chests_menu(update, context)
        elif data.startswith("open_chest_"):
            chest_id = data.replace("open_chest_", "")
            if not chest_id.endswith("_chest"):
                chest_id = f"{chest_id}_chest"
            await handle_open_chest(update, context, chest_id)
        
        # ========== ЛОКАЦИИ ==========
        elif data == "city_church":
            await city_church_menu(update, context)
        elif data == "city_gates":
            await city_gates_menu(update, context)
        elif data == "gates_forest":
            await query.answer()
            msg = await context.bot.send_message(chat_id=user_id, text="🌲 *ТРОПА В ЛЕСА*\n\n_Старая карта указывает путь через заброшенный водосток. Но проход завален. Пока недоступно._", parse_mode=constants.ParseMode.MARKDOWN)
            await asyncio.sleep(3.0)
            await msg.delete()
        elif data == "gates_ruins":
            await query.answer()
            msg = await context.bot.send_message(chat_id=user_id, text="🏚️ *ПУТЬ В РУИНЫ*\n\n_Древняя канализация ведёт к руинам. Но дорога обвалилась. Пока недоступно._", parse_mode=constants.ParseMode.MARKDOWN)
            await asyncio.sleep(3.0)
            await msg.delete()
        elif data == "gates_cemetery":
            await query.answer()
            msg = await context.bot.send_message(chat_id=user_id, text="🪦 *СТАРОЕ КЛАДБИЩЕ*\n\n_Древние могильные плиты покоятся в тишине. Земля здесь пропитана тёмной магией. Пока недоступно._", parse_mode=constants.ParseMode.MARKDOWN)
            await asyncio.sleep(3.0)
            await msg.delete()
        
        # ========== КЛАН ==========
        elif data == "profile_clan":
            await clan_command(update, context)
        elif data == "clan_top":
            await clan_top_callback(update, context)
        elif data == "clan_info":
            await clan_info_callback(update, context)
        elif data == "clan_create_menu":
            await clan_create_menu(update, context)
        elif data == "clan_register":
            await clan_register(update, context)
        elif data == "clan_manage":
            await clan_manage(update, context)
        elif data == "clan_members":
            await clan_members_list(update, context)
        elif data == "clan_leave":
            await clan_leave(update, context)
        elif data == "clan_disband":
            await clan_disband(update, context)
        elif data == "clan_join_menu":
            await clan_join_menu(update, context)
        elif data == "clan_promote_select":
            await clan_promote_select(update, context)
        elif data == "clan_demote_select":
            await clan_demote_select(update, context)
        elif data.startswith("clan_promote_"):
            target_id = int(data.replace("clan_promote_", ""))
            await clan_promote_user(update, context, target_id)
        elif data.startswith("clan_demote_"):
            target_id = int(data.replace("clan_demote_", ""))
            await clan_demote_user(update, context, target_id)
        elif data == "clan_achievements":
            await clan_achievements_callback(update, context)
        
        # ========== ТУННЕЛИ ==========
        elif data == "tunnel_menu":
            await show_tunnel_menu(update, context, user_id)
        elif data == "tunnel_start":
            await start_new_run(update, context, user_id)
        elif data == "tunnel_continue":
            await enter_room(update, context, user_id)
        elif data == "tunnel_next_room":
            await process_room_transition(update, context, user_id)
        elif data == "tunnel_skip_room":
            await process_skip_room(update, context, user_id)
        elif data == "tunnel_go_home":
            await go_home(update, context, user_id)
        elif data.startswith("tunnel_fight_"):
            monster_id = data.replace("tunnel_fight_", "")
            await start_battle(update, context, user_id, monster_id)
        elif data.startswith("chest_"):
            choice = data.replace("chest_", "")
            await handle_chest_choice(update, context, user_id, choice)
        elif data == "altar_offer":
            await handle_altar_offer(update, context, user_id)
        elif data in ["tunnel_stat_strength", "tunnel_stat_agility", "tunnel_stat_intelligence"]:
            stat = data.replace("tunnel_stat_", "")
            await upgrade_stat_callback(update, context, stat)
        elif data.startswith("tunnel_defend_"):
            defense_part = data.replace("tunnel_defend_", "")
            await handle_tunnel_defend(update, context, defense_part)
        elif data.startswith("tunnel_attack_"):
            body_part = data.replace("tunnel_attack_", "")
            if body_part == "random":
                import random
                body_part = random.choice(["head", "paws", "body", "tail"])
            await handle_tunnel_attack(update, context, body_part)
        elif data == "tunnel_flee_new":
            await handle_tunnel_flee_new(update, context)
        elif data == "tunnel_break_free":
            await handle_tunnel_break_free(update, context)
        elif data == "tunnel_continue_battle":
            await handle_tunnel_continue_battle(update, context)
        elif data.startswith("tunnel_invite_"):
            boss_id = data.replace("tunnel_invite_", "")
            run_data = get_tunnel_run(user_id)
            room_number = run_data["current_room"] if run_data else 20
            await send_coop_invite(update, context, user_id, boss_id, room_number)
        elif data.startswith("coop_defend_"):
            await handle_coop_defend(update, context)
        elif data.startswith("coop_attack_"):
            await handle_coop_attack(update, context)
        
        # ========== КНОПКИ ИГРЫ ==========
        elif data == "use_item_menu":
            await show_consumables_menu(update, context)
        elif data == "back_to_game":
            try:
                await query.message.delete()
            except:
                pass
        
        else:
            logger.warning(f"❓ Неизвестная кнопка: {data}")
    
    except Exception as e:
        logger.error(f"❌ Ошибка в button_callback: {e}")
        logger.error(traceback.format_exc())
        try:
            await query.answer("❌ Произошла ошибка!", show_alert=True)
        except:
            pass