from telegram import Update, constants, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
import logging
import sys
import asyncio
sys.path.append('/root/bot')
from handlers.game_rat import active_games, RatGame
from telegram_bot_pagination import InlineKeyboardPaginator
logger = logging.getLogger(__name__)

# ИМПОРТЫ ИЗ PROFILE
from handlers.profile import (
    profile_command, inventory_command, equipment_command, 
    achievements_command, handle_equip, handle_unequip, handle_use_consumable,
    handle_inventory_filter, show_filtered_inventory,
    show_available_for_slot, handle_equip_from_list, show_equipment_list_by_slot
)
from handlers.clan import clan_join_menu, clan_achievements_callback
# ИМПОРТЫ ИЗ ГОРОДА И КОМАНД
from handlers.city import city_menu, city_gates_menu, city_church_menu
from handlers.commands import rat_top
from handlers.titles import set_active_title, titles_command
from handlers.tunnel import show_stats_menu, show_tunnel_menu, start_new_run, upgrade_stat_callback
from handlers.shop import (
    shop_buy_menu, shop_sell_menu, shop_command, handle_shop_sell,
    shop_category, handle_shop_buy, handle_shop_page
)
from handlers.clan import (
    clan_command, clan_top_callback, clan_info_callback,
    clan_create_menu, clan_register, clan_manage,
    clan_members_list, clan_leave, clan_disband,
    clan_join_menu, clan_promote_select, clan_demote_select,
    clan_promote_user, clan_demote_user, clan_achievements_callback
)
from handlers.daily import daily_command
from handlers.blacksmith import blacksmith_menu, forge_select_recipe, forge_craft, forge_show_resources
# ИМПОРТЫ ИЗ ИГРЫ КРЫСА
from handlers.game_rat import (
    show_consumables_menu, handle_use_consumable as game_handle_use_consumable,
    show_chests_menu, handle_open_chest, rat_rules, night_phase
)
from handlers.city import church_rest
from handlers.city import church_leave
# ИМПОРТЫ ДЛЯ ТУННЕЛЕЙ И КООПЕРАТИВА
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
    
    logger.info(f"🔘 Нажата кнопка: {data} от user_id={user_id}")
    
    # ========== КНОПКИ ПРОФИЛЯ ==========
    if data == "profile_achievements":
        await achievements_command(update, context)
        return
    elif data == "dice_tournament":
        from handlers.dice import show_tournament
        await show_tournament(update, context)
        return
    elif data == "profile_inventory":
        await inventory_command(update, context)
        return
    elif data == "city_menu":
        await city_menu(update, context)
        return
    elif data == "city_leaderboard":
        await rat_top(update, context)
        return
    elif data == "achievements_all":
        await achievements_command(update, context, show_all=True)
        return
    elif data == "achievements_compact":
        await achievements_command(update, context, show_all=False)
        return
    elif data == "city_rules":
        await rat_rules(update, context)
        return
    elif data == "set_title_none":
        set_active_title(user_id, None)
        await profile_command(update, context)
        return
    elif data == "profile_equipment":
        await equipment_command(update, context)
        return
    elif data == "tunnel_enter_room":
        await enter_room(update, context, user_id)
        return
    elif data == "tunnel_stats_menu":
        await show_stats_menu(update, context, user_id)
        return
    elif data.startswith("inventory_filter_"):
        filter_type = data.replace("inventory_filter_", "")
        await handle_inventory_filter(update, context, filter_type)
        return
    elif data.startswith("equipment_list_"):
        slot = data.replace("equipment_list_", "")
        await show_equipment_list_by_slot(update, context, slot)
        return
    elif data.startswith("inventory_page_"):
        parts = data.replace("inventory_page_", "").split("#")
        filter_type = parts[0]
        page = int(parts[1]) if len(parts) > 1 else 1
        await show_filtered_inventory(update, context, user_id, filter_type, page)
        return
    elif data == "shop_buy_menu":
        await shop_buy_menu(update, context)
        return
    elif data == "shop_sell_menu":
        await shop_sell_menu(update, context)
        return
    elif data == "shop_back_to_main":
        await shop_command(update, context)
        return
    elif data.startswith("shop_sell_"):
        item_id = data.replace("shop_sell_", "")
        await handle_shop_sell(update, context, item_id)
        return
    elif data.startswith("shop_cat_"):
        category = data.replace("shop_cat_", "")
        await shop_category(update, context, category)
        return
    
    # ========== Кузница ==========
    elif data == "city_forge":
        await blacksmith_menu(update, context)
        return

    elif data == "forge_fortune":
        from handlers.blacksmith import forge_fortune
        await forge_fortune(update, context)
        return

    elif data.startswith("forge_select_"):
        recipe_id = data.replace("forge_select_", "")
        await forge_select_recipe(update, context, recipe_id)
        return

    elif data.startswith("forge_craft_"):
        recipe_id = data.replace("forge_craft_", "")
        await forge_craft(update, context, recipe_id)
        return

    elif data == "forge_resources":
        await forge_show_resources(update, context)
        return
    # ========== ЦЕРКОВЬ ==========

    elif data == "church_rest":
        await church_rest(update, context)
        return

    elif data == "church_leave":
        await church_leave(update, context)
        return

    # ========== ЭКИПИРОВКА ==========
    elif data.startswith("change_slot_"):
        slot = data.replace("change_slot_", "")
        await show_available_for_slot(update, context, slot, page=1)
        return
    elif data.startswith("available_slot_"):
        parts = data.replace("available_slot_", "").split("#")
        slot = parts[0]
        page = int(parts[1]) if len(parts) > 1 else 1
        await show_available_for_slot(update, context, slot, page)
        return
    elif data.startswith("equip_from_list_"):
        item_id = data.replace("equip_from_list_", "")
        await handle_equip_from_list(update, context, item_id)
        return
    elif data == "shop_back_to_categories":
        await shop_buy_menu(update, context)
        return
    elif data.startswith("shop_buy_"):
        item_id = data.replace("shop_buy_", "")
        await handle_shop_buy(update, context, item_id)
        return
    elif data.startswith("shop_page_"):
        parts = data.replace("shop_page_", "").split("_")
        category = parts[0]
        page = int(parts[1]) if len(parts) > 1 else 0
        await handle_shop_page(update, context, category, page)
        return
    
    # ========== КНОПКИ КОСТЕЙ (ЛЕНИВЫЕ ИМПОРТЫ) ==========
    elif data == "profile_dice":
        from handlers.dice import dice_command
        await dice_command(update, context)
        return
    elif data.startswith("dice_"):
        from handlers.dice import dice_callback
        await dice_callback(update, context)
        return
    elif data == "beer_buff":
        from handlers.dice import buy_beer
        await buy_beer(update, context)
        return
    
    # ========== ОСТАЛЬНЫЕ КНОПКИ ==========
    elif data == "back_to_profile" or data == "profile_back":
        await profile_command(update, context)
        return
    elif data == "profile_titles":
        await titles_command(update, context)
        return
    elif data == "profile_shop":
        await shop_command(update, context)
        return
    elif data == "profile_daily":
        await daily_command(update, context)
        return
    elif data.startswith("set_title_"):
        title_id = data.replace("set_title_", "")
        set_active_title(user_id, title_id)
        await profile_command(update, context)
        return
    elif data.startswith("equip_"):
        item_id = data.replace("equip_", "")
        await handle_equip(update, context, item_id)
        return
    elif data.startswith("unequip_"):
        slot = data.replace("unequip_", "")
        await handle_unequip(update, context, slot)
        return
    elif data.startswith("use_consumable_"):
        item_id = data.replace("use_consumable_", "")
        await handle_use_consumable(update, context, item_id)
        return
    
    # ========== КНОПКИ ИГРЫ ==========
    elif data == "use_item_menu":
        await show_consumables_menu(update, context)
        return
    elif data == "back_to_game":
        try:
            await query.message.delete()
        except:
            pass
        return
    
    # ========== СУНДУКИ ==========
    elif data == "chests_menu":
        await show_chests_menu(update, context)
        return
    elif data.startswith("open_chest_"):
        chest_id = data.replace("open_chest_", "")
        if not chest_id.endswith("_chest"):
            chest_id = f"{chest_id}_chest"
        await handle_open_chest(update, context, chest_id)
        return
    
    # ========== НОВЫЕ ЛОКАЦИИ (ЗАГЛУШКИ) ==========
    elif data == "city_church":
        await city_church_menu(update, context)
        return

    elif data == "city_gates":
        await city_gates_menu(update, context)
        return

    elif data == "gates_forest":
        await query.answer()
        msg = await context.bot.send_message(
            chat_id=user_id,
            text="🌲 *ТРОПА В ЛЕСА*\n\n_Старая карта указывает путь через заброшенный водосток. Но проход завален. Пока недоступно._",
            parse_mode=constants.ParseMode.MARKDOWN
        )
        await asyncio.sleep(3.0)
        await msg.delete()
        return

    elif data == "gates_ruins":
        await query.answer()
        msg = await context.bot.send_message(
            chat_id=user_id,
            text="🏚️ *ПУТЬ В РУИНЫ*\n\n_Древняя канализация ведёт к руинам. Но дорога обвалилась. Пока недоступно._",
            parse_mode=constants.ParseMode.MARKDOWN
        )
        await asyncio.sleep(3.0)
        await msg.delete()
        return

    # ========== КЛАН ==========
    elif data == "profile_clan":
        await clan_command(update, context)
        return
    elif data == "clan_top":
        await clan_top_callback(update, context)
        return
    elif data == "clan_info":
        await clan_info_callback(update, context)
        return
    elif data == "clan_create_menu":
        await clan_create_menu(update, context)
        return
    elif data == "clan_register":
        await clan_register(update, context)
        return
    elif data == "clan_manage":
        await clan_manage(update, context)
        return
    elif data == "clan_members":
        await clan_members_list(update, context)
        return
    elif data == "clan_leave":
        await clan_leave(update, context)
        return
    elif data == "clan_disband":
        await clan_disband(update, context)
        return
    elif data == "clan_join_menu":
        await clan_join_menu(update, context)
        return
    elif data == "clan_promote_select":
        await clan_promote_select(update, context)
        return
    elif data == "clan_demote_select":
        await clan_demote_select(update, context)
        return
    elif data.startswith("clan_promote_"):
        target_id = int(data.replace("clan_promote_", ""))
        await clan_promote_user(update, context, target_id)
        return
    elif data.startswith("clan_demote_"):
        target_id = int(data.replace("clan_demote_", ""))
        await clan_demote_user(update, context, target_id)
        return
    elif data == "clan_wars":
        await query.answer("⚔️ Клановые войны скоро появятся!", show_alert=True)
        return
    elif data == "clan_achievements":
        await clan_achievements_callback(update, context)
        return
    # ========== ТУННЕЛИ ==========
    elif data == "tunnel_menu":
        await show_tunnel_menu(update, context, user_id)
        return
    elif data == "tunnel_start":
        await start_new_run(update, context, user_id)
        return
    elif data == "tunnel_continue":
        await enter_room(update, context, user_id)
        return
    elif data == "tunnel_next_room":
        await process_room_transition(update, context, user_id)
        return
    elif data == "tunnel_skip_room":
        await process_skip_room(update, context, user_id)
        return
    elif data == "tunnel_go_home":
        await go_home(update, context, user_id)
        return
    elif data.startswith("tunnel_fight_"):
        monster_id = data.replace("tunnel_fight_", "")
        await start_battle(update, context, user_id, monster_id)
        return
    elif data.startswith("chest_"):
        choice = data.replace("chest_", "")
        await handle_chest_choice(update, context, user_id, choice)
        return
    elif data == "altar_offer":
        await handle_altar_offer(update, context, user_id)
        return
    
    # КОЛБЭКИ ХАРАКТЕРИСТИК
    elif data == "tunnel_stat_strength":
        await upgrade_stat_callback(update, context, "strength")
        return
    elif data == "tunnel_stat_agility":
        await upgrade_stat_callback(update, context, "agility")
        return
    elif data == "tunnel_stat_intelligence":
        await upgrade_stat_callback(update, context, "intelligence")
        return
    
    # КОЛБЭКИ ЗАЩИТЫ
    elif data.startswith("tunnel_defend_"):
        defense_part = data.replace("tunnel_defend_", "")
        await handle_tunnel_defend(update, context, defense_part)
        return
    
    # КОЛБЭКИ АТАКИ
    elif data.startswith("tunnel_attack_"):
        body_part = data.replace("tunnel_attack_", "")
        if body_part == "random":
            import random
            body_part = random.choice(["head", "paws", "body", "tail"])
        await handle_tunnel_attack(update, context, body_part)
        return
    
    elif data == "tunnel_flee_new":
        await handle_tunnel_flee_new(update, context)
        return
    elif data == "tunnel_break_free":
        await handle_tunnel_break_free(update, context)
        return
    elif data == "tunnel_continue_battle":
        await handle_tunnel_continue_battle(update, context)
        return
    
    # ========== КООПЕРАТИВ ==========
    elif data.startswith("tunnel_invite_"):
        logger.info(f"🔥 НАЖАТА КНОПКА tunnel_invite! user={user_id}")
        boss_id = data.replace("tunnel_invite_", "")
        run_data = get_tunnel_run(user_id)
        room_number = run_data["current_room"] if run_data else 20
        await send_coop_invite(update, context, user_id, boss_id, room_number)
        return
    elif data.startswith("coop_defend_"):
        await handle_coop_defend(update, context)
        return
    elif data.startswith("coop_attack_"):
        await handle_coop_attack(update, context)
        return

    # ========== ЛОББИ ==========
    elif data == "rat_lobby_join":
        game = active_games.get(chat_id)
        if not game:
            await query.edit_message_text("❌ Игра не найдена!")
            return
        if game.phase != "lobby":
            await query.answer("❌ Игра уже началась!", show_alert=True)
            return
        if game.add_player(user_id, user_name):
            players_list = "\n".join([f"• {escape_markdown(p['name'])}" for p in game.players.values()])
            creator_name = escape_markdown(game.players[game.creator_id]['name'])
            keyboard = [
                [InlineKeyboardButton("✅ Присоединиться", callback_data="rat_lobby_join"),
                 InlineKeyboardButton("👋 Выйти", callback_data="rat_lobby_leave")],
                [InlineKeyboardButton("🎮 Начать игру", callback_data="rat_lobby_start")]
            ]
            caption = f"🐀 *РАТЛЯНДИЯ*\n\nИгроков: {len(game.players)}/10\nСоздатель: {creator_name}\n\n*Участники:*\n{players_list}"
            try:
                await query.edit_message_caption(caption=caption, parse_mode=constants.ParseMode.MARKDOWN, reply_markup=InlineKeyboardMarkup(keyboard))
            except:
                await query.edit_message_text(caption, parse_mode=constants.ParseMode.MARKDOWN, reply_markup=InlineKeyboardMarkup(keyboard))
            await query.answer(f"✅ {user_name} присоединился!")
        else:
            await query.answer("❌ Ты уже в игре или лобби заполнено!", show_alert=True)
        return
    
    elif data == "rat_lobby_leave":
        game = active_games.get(chat_id)
        if not game:
            await query.edit_message_text("❌ Игра не найдена!")
            return
        if game.phase != "lobby":
            await query.answer("❌ Игра уже началась!", show_alert=True)
            return
        if user_id == game.creator_id:
            await query.answer("❌ Создатель не может выйти! Используйте /rat_stop", show_alert=True)
            return
        if game.remove_player(user_id):
            players_list = "\n".join([f"• {escape_markdown(p['name'])}" for p in game.players.values()])
            creator_name = escape_markdown(game.players[game.creator_id]['name'])
            keyboard = [
                [InlineKeyboardButton("✅ Присоединиться", callback_data="rat_lobby_join"),
                 InlineKeyboardButton("👋 Выйти", callback_data="rat_lobby_leave")],
                [InlineKeyboardButton("🎮 Начать игру", callback_data="rat_lobby_start")]
            ]
            caption = f"🐀 *РАТЛЯНДИЯ*\n\nИгроков: {len(game.players)}/10\nСоздатель: {creator_name}\n\n*Участники:*\n{players_list}"
            try:
                await query.edit_message_caption(caption=caption, parse_mode=constants.ParseMode.MARKDOWN, reply_markup=InlineKeyboardMarkup(keyboard))
            except:
                await query.edit_message_text(caption, parse_mode=constants.ParseMode.MARKDOWN, reply_markup=InlineKeyboardMarkup(keyboard))
            await query.answer(f"👋 {user_name} покинул лобби!")
        else:
            await query.answer("❌ Ты не в игре!", show_alert=True)
        return
    
    elif data == "rat_lobby_start":
        game = active_games.get(chat_id)
        if not game:
            await query.edit_message_text("❌ Игра не найдена!")
            return
        if user_id != game.creator_id:
            await query.answer("❌ Только создатель может начать игру!", show_alert=True)
            return
        if not game.start_game():
            await query.answer(f"❌ Нужно от 3 до 10 игроков! Сейчас: {len(game.players)}", show_alert=True)
            return
        try:
            with open("/root/bot/images/role_cards.jpg", "rb") as photo:
                await context.bot.send_photo(chat_id=chat_id, photo=photo, caption="🎭 *РОЛИ РАЗДАНЫ!* Проверь личные сообщения!", parse_mode=constants.ParseMode.MARKDOWN)
        except:
            await context.bot.send_message(chat_id, "🎭 *РОЛИ РАЗДАНЫ!* Проверь личные сообщения!", parse_mode=constants.ParseMode.MARKDOWN)
        for pid, data in game.players.items():
            try:
                await context.bot.send_message(pid, f"🎭 Твоя роль: *{data['role']}*", parse_mode=constants.ParseMode.MARKDOWN)
            except:
                pass
        try:
            await query.edit_message_caption(caption=f"🎮 *РАТЛЯНДИЯ НАЧАЛАСЬ!*\nИгроков: {len(game.players)}\n🌙 Первая ночь...", parse_mode=constants.ParseMode.MARKDOWN)
        except:
            await query.edit_message_text(f"🎮 *РАТЛЯНДИЯ НАЧАЛАСЬ!*\nИгроков: {len(game.players)}\n🌙 Первая ночь...", parse_mode=constants.ParseMode.MARKDOWN)
        asyncio.create_task(night_phase(context, chat_id))
        return
    
    # ========== КНОПКИ УБИЙСТВА ==========
    elif data.startswith("rat_kill_"):
        game = None
        for g in active_games.values():
            if g.rat_id == user_id and g.phase == "night" and not g.night_ended:
                game = g
                break
        if not game:
            await query.edit_message_text("❌ Сейчас не время для убийства или ты не крыса!")
            return
        if data == "rat_kill_none":
            game.night_kill = None
            try:
                await query.edit_message_caption(caption="😇 Ты решила никого не убивать.")
            except:
                await query.edit_message_text("😇 Ты решила никого не убивать.")
            game.night_ended = True
        else:
            try:
                victim_id = int(data.replace("rat_kill_", ""))
                if victim_id in game.get_alive_mice():
                    game.night_kill = victim_id
                    victim_name = escape_markdown(game.players[victim_id]["name"])
                    try:
                        await query.edit_message_caption(caption=f"🔪 Ты выбрала жертву: *{victim_name}*", parse_mode=constants.ParseMode.MARKDOWN)
                    except:
                        await query.edit_message_text(f"🔪 Ты выбрала жертву: *{victim_name}*", parse_mode=constants.ParseMode.MARKDOWN)
                    game.night_ended = True
                else:
                    await query.edit_message_text("❌ Этот игрок уже мёртв или это крыса!")
            except ValueError:
                await query.edit_message_text("❌ Ошибка выбора!")
        return
    
    # ========== КНОПКИ ГОЛОСОВАНИЯ ==========
    elif data.startswith("rat_vote_"):
        game = None
        for g in active_games.values():
            if user_id in g.players and g.phase == "voting" and g.players[user_id]["alive"]:
                game = g
                break
        if not game:
            await query.edit_message_text("❌ Сейчас не время для голосования или ты мёртв!")
            return
        if user_id in game.votes:
            await query.edit_message_text("❌ Ты уже проголосовал!")
            return
        if data == "rat_vote_skip":
            game.votes[user_id] = None
            try:
                await query.edit_message_caption(caption="⏭ Ты пропустил голосование.")
            except:
                await query.edit_message_text("⏭ Ты пропустил голосование.")
        else:
            try:
                target_id = int(data.replace("rat_vote_", ""))
                if target_id in game.get_alive_players() and target_id != user_id:
                    game.votes[user_id] = target_id
                    target_name = escape_markdown(game.players[target_id]["name"])
                    try:
                        await query.edit_message_caption(caption=f"⚖️ Ты проголосовал за *{target_name}*", parse_mode=constants.ParseMode.MARKDOWN)
                    except:
                        await query.edit_message_text(f"⚖️ Ты проголосовал за *{target_name}*", parse_mode=constants.ParseMode.MARKDOWN)
                else:
                    await query.edit_message_text("❌ Нельзя голосовать за этого игрока!")
            except ValueError:
                await query.edit_message_text("❌ Ошибка голосования!")
        return
    
    else:
        logger.warning(f"❓ Неизвестная кнопка: {data}")