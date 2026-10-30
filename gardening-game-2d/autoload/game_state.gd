extends Node

var inventory: Dictionary = {}
var bag_tier: int = 0
var cauldron_tier: int = 0
var gold: int = 0
var forest_spawn_day: int = 0
var forest_spawn_phase: String = ""
var forest_plants: Array = []
var can_stay_up_past_midnight: bool = false
var last_recovery: Dictionary = {}
var midnight_bloom_day: int = 0
var midnight_bloom_collected: bool = false
var lantern_tier: int = -1
var current_cave_id: String = "cave_a"
var current_cave_depth: int = 1
var cave_entry_mode: String = "entrance"
var cave_progress: Dictionary = {}
var cave_spawn_day: int = 0
var cave_plants: Dictionary = {}
var discovered_plants: Dictionary = {}
var resume_location: String = "forest"
var last_save_failed: bool = false

var _loss_rng: RandomNumberGenerator = RandomNumberGenerator.new()
var _cave_rng: RandomNumberGenerator = RandomNumberGenerator.new()


func _ready() -> void:
	_loss_rng.randomize()
	_cave_rng.randomize()
	EventBus.day_started.connect(_on_day_started)


func get_item_count(id: String) -> int:
	return int(inventory.get(id, 0))


func get_total_item_count() -> int:
	var total: int = 0
	for count in inventory.values():
		total += int(count)
	return total


func get_bag_capacity() -> int:
	var bag_data: Dictionary = GameData.upgrades.get("bag", {})
	var tiers: Array = bag_data.get("tiers", [])
	if tiers.is_empty():
		push_error("GameState: bag tiers missing from upgrades data")
		return 0

	var index: int = clampi(bag_tier, 0, tiers.size() - 1)
	var tier: Dictionary = tiers[index]
	return int(tier.get("effect", 0))


func get_cauldron_level() -> int:
	var cauldron_data: Dictionary = GameData.upgrades.get("cauldron", {})
	var tiers: Array = cauldron_data.get("tiers", [])
	if tiers.is_empty():
		push_error("GameState: cauldron tiers missing from upgrades data")
		return 0

	var index: int = clampi(cauldron_tier, 0, tiers.size() - 1)
	var tier: Dictionary = tiers[index]
	return int(tier.get("effect", 0))


func get_lantern_level() -> int:
	if lantern_tier < 0:
		return 0
	var lantern_data: Dictionary = GameData.upgrades.get("lantern", {})
	var tiers: Array = lantern_data.get("tiers", [])
	if tiers.is_empty():
		push_error("GameState: lantern tiers missing from upgrades data")
		return 0
	var index: int = clampi(lantern_tier, 0, tiers.size() - 1)
	var tier: Dictionary = tiers[index]
	return int(tier.get("effect", 0))


func get_next_upgrade(line: String) -> Dictionary:
	var line_data: Dictionary = GameData.upgrades.get(line, {})
	var tiers: Array = line_data.get("tiers", [])
	var available_tiers: int = mini(int(line_data.get("available_tiers", tiers.size())), tiers.size())
	var next_index: int = _get_upgrade_tier_index(line) + 1
	if next_index < 0 or next_index >= available_tiers:
		return {}
	var next_tier: Dictionary = tiers[next_index].duplicate(true)
	next_tier["index"] = next_index
	return next_tier


func can_purchase_upgrade(line: String) -> bool:
	var next_upgrade: Dictionary = get_next_upgrade(line)
	if next_upgrade.is_empty():
		return false
	var cost: int = int(next_upgrade.get("cost", -1))
	return cost >= 0 and gold >= cost


func purchase_upgrade(line: String) -> bool:
	if not can_purchase_upgrade(line):
		return false
	var next_upgrade: Dictionary = get_next_upgrade(line)
	var cost: int = int(next_upgrade.get("cost", 0))
	gold -= cost
	_set_upgrade_tier_index(line, int(next_upgrade.get("index", -1)))
	EventBus.gold_changed.emit(gold)
	EventBus.inventory_changed.emit()
	EventBus.upgrades_changed.emit()
	return true


func get_upgrade_effect(line: String) -> int:
	var index: int = _get_upgrade_tier_index(line)
	if index < 0:
		return 0
	var line_data: Dictionary = GameData.upgrades.get(line, {})
	var tiers: Array = line_data.get("tiers", [])
	if index >= tiers.size():
		return 0
	var tier: Dictionary = tiers[index]
	return int(tier.get("effect", 0))


func _get_upgrade_tier_index(line: String) -> int:
	if line == "bag":
		return bag_tier
	if line == "lantern":
		return lantern_tier
	if line == "cauldron":
		return cauldron_tier
	return -1


func _set_upgrade_tier_index(line: String, index: int) -> void:
	if line == "bag":
		bag_tier = index
	elif line == "lantern":
		lantern_tier = index
	elif line == "cauldron":
		cauldron_tier = index


func can_add_item(id: String, amount: int = 1) -> bool:
	if amount <= 0:
		return false
	if GameData.get_item(id).is_empty():
		return false
	return get_total_item_count() + amount <= get_bag_capacity()


func add_item(id: String, amount: int = 1) -> bool:
	if not can_add_item(id, amount):
		if not GameData.get_item(id).is_empty():
			EventBus.inventory_full.emit(id)
		return false

	inventory[id] = get_item_count(id) + amount
	_discover_item(id)
	EventBus.inventory_changed.emit()
	EventBus.item_collected.emit(id, amount)
	return true


func remove_item(id: String, amount: int = 1) -> bool:
	if amount <= 0:
		return false
	if get_item_count(id) < amount:
		return false

	_set_item_count(id, get_item_count(id) - amount)
	EventBus.inventory_changed.emit()
	return true


func can_craft(recipe_id: String) -> bool:
	var recipe: Dictionary = GameData.get_recipe(recipe_id)
	if recipe.is_empty():
		return false

	var required_tier: int = int(recipe.get("cauldron_tier", 0))
	if required_tier <= 0 or required_tier > get_cauldron_level():
		return false

	var requirements: Dictionary = _get_recipe_requirements(recipe)
	if requirements.is_empty():
		return false

	var consumed_count: int = 0
	for id_variant in requirements:
		var item_id: String = str(id_variant)
		var amount: int = int(requirements[id_variant])
		if get_item_count(item_id) < amount:
			return false
		consumed_count += amount

	var output: Dictionary = recipe.get("output", {})
	var output_id: String = str(output.get("item", ""))
	var output_count: int = int(output.get("count", 0))
	if output_id == "" or output_count <= 0 or GameData.get_item(output_id).is_empty():
		return false

	return get_total_item_count() - consumed_count + output_count <= get_bag_capacity()


func craft(recipe_id: String) -> bool:
	if not can_craft(recipe_id):
		return false

	var recipe: Dictionary = GameData.get_recipe(recipe_id)
	var requirements: Dictionary = _get_recipe_requirements(recipe)
	for id_variant in requirements:
		var item_id: String = str(id_variant)
		_set_item_count(item_id, get_item_count(item_id) - int(requirements[id_variant]))

	var output: Dictionary = recipe.get("output", {})
	var output_id: String = str(output.get("item", ""))
	var output_count: int = int(output.get("count", 0))
	_set_item_count(output_id, get_item_count(output_id) + output_count)

	EventBus.inventory_changed.emit()
	EventBus.item_crafted.emit(recipe_id, output_id, output_count)
	return true


func get_sell_price(id: String) -> int:
	var item: Dictionary = GameData.get_item(id)
	var base_price: int = int(item.get("base_price", 0))
	var multiplier: float = float(GameData.customers.get("sell_bin_multiplier", 0.0))
	if base_price <= 0 or multiplier <= 0.0:
		return 0
	return roundi(base_price * multiplier)


func sell_item(id: String, amount: int = 1) -> bool:
	var unit_price: int = get_sell_price(id)
	if amount <= 0 or unit_price <= 0 or get_item_count(id) < amount:
		return false
	return _complete_sale(id, amount, unit_price * amount)


func sell_to_customer(id: String, payment: int) -> bool:
	var item: Dictionary = GameData.get_item(id)
	var base_price: int = int(item.get("base_price", 0))
	var minimum_multiplier: float = float(GameData.customers.get("price_multiplier_min", 0.0))
	var maximum_multiplier: float = float(GameData.customers.get("price_multiplier_max", 0.0))
	var minimum_payment: int = ceili(base_price * minimum_multiplier)
	var maximum_payment: int = floori(base_price * maximum_multiplier)
	if payment < minimum_payment or payment > maximum_payment or get_item_count(id) < 1:
		return false
	return _complete_sale(id, 1, payment)


func _complete_sale(id: String, amount: int, gold_earned: int) -> bool:
	_set_item_count(id, get_item_count(id) - amount)
	gold += gold_earned

	EventBus.inventory_changed.emit()
	EventBus.gold_changed.emit(gold)
	EventBus.item_sold.emit(id, amount, gold_earned)
	return true


func has_current_forest_spawns() -> bool:
	return forest_spawn_day == GameClock.day \
		and forest_spawn_phase == GameClock.current_phase_name()


func set_forest_spawns(spawns: Array) -> void:
	forest_spawn_day = GameClock.day
	forest_spawn_phase = GameClock.current_phase_name()
	forest_plants = spawns.duplicate(true)


func remove_forest_spawn(spawn_id: String) -> void:
	for index in forest_plants.size():
		var record: Dictionary = forest_plants[index]
		if str(record.get("id", "")) == spawn_id:
			forest_plants.remove_at(index)
			return


func add_forest_spawn(record: Dictionary) -> void:
	forest_plants.append(record.duplicate(true))


func prepare_midnight_bloom_day() -> void:
	if midnight_bloom_day == GameClock.day:
		return
	midnight_bloom_day = GameClock.day
	midnight_bloom_collected = false


func mark_midnight_bloom_collected() -> void:
	prepare_midnight_bloom_day()
	midnight_bloom_collected = true


func apply_pass_out() -> Dictionary:
	var lost_items: Dictionary = {}
	for id_variant in inventory.keys():
		var item_id: String = str(id_variant)
		var carried_count: int = get_item_count(item_id)
		var lost_count: int = 0
		for _unit in carried_count:
			if _loss_rng.randf() < Config.PASS_OUT_ITEM_LOSS_CHANCE:
				lost_count += 1
		if lost_count > 0:
			lost_items[item_id] = lost_count
			_set_item_count(item_id, carried_count - lost_count)

	var fine: int = mini(
		gold,
		maxi(Config.PASS_OUT_MIN_FINE, roundi(gold * Config.PASS_OUT_FINE_RATE))
	)
	gold -= fine
	last_recovery = {
		"reason": "pass_out",
		"lost_items": lost_items,
		"fine": fine,
	}
	EventBus.inventory_changed.emit()
	EventBus.gold_changed.emit(gold)
	return last_recovery.duplicate(true)


func prepare_sleep() -> Dictionary:
	last_recovery = {
		"reason": "sleep",
		"lost_items": {},
		"fine": 0,
	}
	return last_recovery.duplicate(true)


func can_access_cave_depth(cave_id: String, depth: int) -> bool:
	var depth_data: Dictionary = GameData.get_cave_depth(cave_id, depth)
	if depth_data.is_empty():
		return false
	return get_lantern_level() >= int(depth_data.get("required_tier", 0))


func enter_cave(cave_id: String, depth: int, entry_mode: String) -> void:
	current_cave_id = cave_id
	current_cave_depth = depth
	cave_entry_mode = entry_mode
	if depth > 1 and entry_mode == "arrival":
		mark_cave_ladder(cave_id, depth)


func get_or_choose_hole(cave_id: String, depth: int, candidates: Array) -> String:
	if candidates.is_empty():
		return ""
	var progress: Dictionary = _get_cave_progress(cave_id)
	var positions: Dictionary = progress.get("hole_positions", {})
	var key: String = str(depth)
	if positions.has(key):
		return str(positions[key])
	var chosen: String = str(candidates[_cave_rng.randi_range(0, candidates.size() - 1)])
	positions[key] = chosen
	progress["hole_positions"] = positions
	cave_progress[cave_id] = progress
	return chosen


func mark_cave_hole_found(cave_id: String, depth: int) -> void:
	var progress: Dictionary = _get_cave_progress(cave_id)
	var found: Array = progress.get("found_holes", [])
	if not found.has(depth):
		found.append(depth)
	progress["found_holes"] = found
	cave_progress[cave_id] = progress


func is_cave_hole_found(cave_id: String, depth: int) -> bool:
	var progress: Dictionary = _get_cave_progress(cave_id)
	var found: Array = progress.get("found_holes", [])
	return found.has(depth)


func mark_cave_ladder(cave_id: String, depth: int) -> void:
	var progress: Dictionary = _get_cave_progress(cave_id)
	var ladders: Array = progress.get("ladders", [])
	if not ladders.has(depth):
		ladders.append(depth)
	progress["ladders"] = ladders
	cave_progress[cave_id] = progress


func has_cave_ladder(cave_id: String, depth: int) -> bool:
	var progress: Dictionary = _get_cave_progress(cave_id)
	var ladders: Array = progress.get("ladders", [])
	return ladders.has(depth)


func try_descend_cave() -> bool:
	var next_depth: int = current_cave_depth + 1
	if GameData.get_cave_depth(current_cave_id, next_depth).is_empty():
		return false
	mark_cave_hole_found(current_cave_id, current_cave_depth)
	if not can_access_cave_depth(current_cave_id, next_depth):
		return false
	enter_cave(current_cave_id, next_depth, "arrival")
	return true


func go_up_cave_depth() -> bool:
	if current_cave_depth <= 1:
		return false
	current_cave_depth -= 1
	cave_entry_mode = "hole_return"
	return true


func get_cave_spawn_records(cave_id: String, depth: int) -> Array:
	_prepare_cave_spawn_day()
	var key: String = _cave_spawn_key(cave_id, depth)
	var records: Array = cave_plants.get(key, [])
	return records.duplicate(true)


func has_cave_spawn_records(cave_id: String, depth: int) -> bool:
	_prepare_cave_spawn_day()
	return cave_plants.has(_cave_spawn_key(cave_id, depth))


func set_cave_spawn_records(cave_id: String, depth: int, records: Array) -> void:
	_prepare_cave_spawn_day()
	cave_plants[_cave_spawn_key(cave_id, depth)] = records.duplicate(true)


func remove_cave_spawn(cave_id: String, depth: int, spawn_id: String) -> void:
	var records: Array = get_cave_spawn_records(cave_id, depth)
	for index in records.size():
		var record: Dictionary = records[index]
		if str(record.get("id", "")) == spawn_id:
			records.remove_at(index)
			set_cave_spawn_records(cave_id, depth, records)
			return


func _get_cave_progress(cave_id: String) -> Dictionary:
	if not cave_progress.has(cave_id):
		cave_progress[cave_id] = {
			"hole_positions": {},
			"found_holes": [],
			"ladders": [],
		}
	var progress: Dictionary = cave_progress[cave_id]
	return progress


func _prepare_cave_spawn_day() -> void:
	if cave_spawn_day == GameClock.day:
		return
	cave_spawn_day = GameClock.day
	cave_plants.clear()


func _cave_spawn_key(cave_id: String, depth: int) -> String:
	return "%s:%d" % [cave_id, depth]


func _on_day_started(day: int) -> void:
	if cave_spawn_day == day:
		return
	cave_spawn_day = day
	cave_plants.clear()


func _discover_item(id: String) -> void:
	var item: Dictionary = GameData.get_item(id)
	if not bool(item.get("botanary", false)) or bool(discovered_plants.get(id, false)):
		return
	discovered_plants[id] = true
	EventBus.botanary_changed.emit()


func _get_recipe_requirements(recipe: Dictionary) -> Dictionary:
	var requirements: Dictionary = {}
	var inputs: Array = recipe.get("inputs", [])
	for input_variant in inputs:
		if not input_variant is Dictionary:
			return {}
		var input: Dictionary = input_variant
		var item_id: String = str(input.get("item", ""))
		var amount: int = int(input.get("count", 0))
		if item_id == "" or amount <= 0 or GameData.get_item(item_id).is_empty():
			return {}
		requirements[item_id] = int(requirements.get(item_id, 0)) + amount
	return requirements


func _set_item_count(id: String, amount: int) -> void:
	if amount <= 0:
		inventory.erase(id)
	else:
		inventory[id] = amount
