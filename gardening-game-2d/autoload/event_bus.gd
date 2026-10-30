extends Node

signal day_started(day: int)
signal phase_changed(phase: String)
signal time_warning(seconds_left: int)
signal midnight_reached
signal inventory_changed
signal item_collected(item_id: String, count: int)
signal inventory_full(item_id: String)
signal plant_collected(spawn_id: String, item_id: String)
signal crafting_requested
signal sell_bin_requested
signal shop_requested
signal sleep_requested
signal ladder_requested
signal upgrade_requested
signal upgrades_changed
signal home_menu_requested
signal botanary_changed
signal message_requested(text: String)
signal shop_opened
signal shop_closed
signal item_crafted(recipe_id: String, item_id: String, count: int)
signal item_sold(item_id: String, count: int, gold_earned: int)
signal gold_changed(total_gold: int)
signal menu_opened
signal menu_closed
