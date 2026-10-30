extends Node

const SAVE_VERSION: int = 1
const DEFAULT_SAVE_PATH: String = "user://save.json"

var save_path: String = DEFAULT_SAVE_PATH


func _ready() -> void:
	if load_game():
		call_deferred("_resume_saved_location")


func save_game(resume_location: String = "") -> bool:
	if resume_location != "":
		GameState.resume_location = _validated_resume_location(resume_location)
	return save_to_path(save_path)


func load_game() -> bool:
	if load_from_path(save_path):
		return true
	return load_from_path(save_path + ".bak")


func save_to_path(path: String) -> bool:
	var temporary_path: String = path + ".tmp"
	var backup_path: String = path + ".bak"
	var file: FileAccess = FileAccess.open(temporary_path, FileAccess.WRITE)
	if file == null:
		push_error("SaveManager: unable to write %s" % temporary_path)
		return false
	file.store_string(JSON.stringify(_build_save_data(), "\t"))
	var write_error: Error = file.get_error()
	file.close()
	if write_error != OK:
		DirAccess.remove_absolute(ProjectSettings.globalize_path(temporary_path))
		push_error("SaveManager: failed while writing save data")
		return false

	var absolute_path: String = ProjectSettings.globalize_path(path)
	var absolute_temporary: String = ProjectSettings.globalize_path(temporary_path)
	var absolute_backup: String = ProjectSettings.globalize_path(backup_path)
	if FileAccess.file_exists(path):
		if FileAccess.file_exists(backup_path):
			DirAccess.remove_absolute(absolute_backup)
		var backup_error: Error = DirAccess.rename_absolute(absolute_path, absolute_backup)
		if backup_error != OK:
			DirAccess.remove_absolute(absolute_temporary)
			push_error("SaveManager: unable to back up existing save")
			return false
	var replace_error: Error = DirAccess.rename_absolute(absolute_temporary, absolute_path)
	if replace_error != OK:
		if FileAccess.file_exists(backup_path):
			DirAccess.rename_absolute(absolute_backup, absolute_path)
		push_error("SaveManager: unable to install new save")
		return false
	return true


func load_from_path(path: String) -> bool:
	if not FileAccess.file_exists(path):
		return false
	var file: FileAccess = FileAccess.open(path, FileAccess.READ)
	if file == null:
		push_error("SaveManager: unable to read %s" % path)
		return false
	var parsed: Variant = JSON.parse_string(file.get_as_text())
	file.close()
	if not parsed is Dictionary:
		push_warning("SaveManager: invalid save JSON")
		return false
	var data: Dictionary = parsed
	if int(data.get("version", 0)) != SAVE_VERSION:
		push_warning("SaveManager: unsupported save version")
		return false
	if not _validate_save_data(data):
		push_warning("SaveManager: malformed save data")
		return false
	_apply_save_data(data)
	return true


func _build_save_data() -> Dictionary:
	return {
		"version": SAVE_VERSION,
		"day": GameClock.day,
		"phase_index": GameClock.phase_index,
		"seconds_into_phase": GameClock.seconds_into_phase,
		"gold": GameState.gold,
		"inventory": GameState.inventory,
		"upgrade_tiers": {
			"bag": GameState.bag_tier,
			"lantern": GameState.lantern_tier,
			"cauldron": GameState.cauldron_tier,
		},
		"botanary": GameState.discovered_plants,
		"cave_progress": GameState.cave_progress,
		"flags": {
			"can_stay_up_past_midnight": GameState.can_stay_up_past_midnight,
		},
		"current_cave": {
			"id": GameState.current_cave_id,
			"depth": GameState.current_cave_depth,
			"entry_mode": GameState.cave_entry_mode,
		},
		"last_recovery": GameState.last_recovery,
		"resume_location": GameState.resume_location,
		"world": {
			"forest_spawn_day": GameState.forest_spawn_day,
			"forest_spawn_phase": GameState.forest_spawn_phase,
			"forest_plants": GameState.forest_plants,
			"midnight_bloom_day": GameState.midnight_bloom_day,
			"midnight_bloom_collected": GameState.midnight_bloom_collected,
			"cave_spawn_day": GameState.cave_spawn_day,
			"cave_plants": GameState.cave_plants,
		},
	}


func _apply_save_data(data: Dictionary) -> void:
	GameState.gold = maxi(0, int(data.get("gold", 0)))
	GameState.inventory = _sanitize_inventory(data.get("inventory", {}))

	var tiers: Dictionary = _as_dictionary(data.get("upgrade_tiers", {}))
	GameState.bag_tier = _clamp_tier("bag", int(tiers.get("bag", 0)), 0)
	GameState.lantern_tier = _clamp_tier("lantern", int(tiers.get("lantern", -1)), -1)
	GameState.cauldron_tier = _clamp_tier("cauldron", int(tiers.get("cauldron", 0)), 0)
	GameState.discovered_plants = _sanitize_discoveries(data.get("botanary", {}))
	GameState.cave_progress = _sanitize_cave_progress(data.get("cave_progress", {}))

	var flags: Dictionary = _as_dictionary(data.get("flags", {}))
	GameState.can_stay_up_past_midnight = bool(flags.get("can_stay_up_past_midnight", false))
	var current_cave: Dictionary = _as_dictionary(data.get("current_cave", {}))
	GameState.current_cave_id = str(current_cave.get("id", "cave_a"))
	GameState.current_cave_depth = maxi(1, int(current_cave.get("depth", 1)))
	GameState.cave_entry_mode = str(current_cave.get("entry_mode", "entrance"))
	GameState.last_recovery = _as_dictionary(data.get("last_recovery", {})).duplicate(true)
	GameState.resume_location = _validated_resume_location(str(data.get("resume_location", "forest")))

	var world: Dictionary = _as_dictionary(data.get("world", {}))
	GameState.forest_spawn_day = int(world.get("forest_spawn_day", 0))
	GameState.forest_spawn_phase = str(world.get("forest_spawn_phase", ""))
	GameState.forest_plants = _as_array(world.get("forest_plants", [])).duplicate(true)
	GameState.midnight_bloom_day = int(world.get("midnight_bloom_day", 0))
	GameState.midnight_bloom_collected = bool(world.get("midnight_bloom_collected", false))
	GameState.cave_spawn_day = int(world.get("cave_spawn_day", 0))
	GameState.cave_plants = _as_dictionary(world.get("cave_plants", {})).duplicate(true)

	EventBus.inventory_changed.emit()
	EventBus.gold_changed.emit(GameState.gold)
	EventBus.upgrades_changed.emit()
	EventBus.botanary_changed.emit()
	GameClock.restore_state(
		int(data.get("day", Config.START_DAY)),
		int(data.get("phase_index", 0)),
		float(data.get("seconds_into_phase", 0.0))
	)


func _sanitize_inventory(value: Variant) -> Dictionary:
	var result: Dictionary = {}
	var saved: Dictionary = _as_dictionary(value)
	for id_variant in saved:
		var item_id: String = str(id_variant)
		var count: int = int(saved[id_variant])
		if count > 0 and not GameData.get_item(item_id).is_empty():
			result[item_id] = count
	return result


func _sanitize_discoveries(value: Variant) -> Dictionary:
	var result: Dictionary = {}
	var saved: Dictionary = _as_dictionary(value)
	for id_variant in saved:
		var item_id: String = str(id_variant)
		var item: Dictionary = GameData.get_item(item_id)
		if bool(saved[id_variant]) and bool(item.get("botanary", false)):
			result[item_id] = true
	return result


func _sanitize_cave_progress(value: Variant) -> Dictionary:
	var result: Dictionary = {}
	var saved: Dictionary = _as_dictionary(value)
	for cave_id_variant in saved:
		var cave_id: String = str(cave_id_variant)
		var progress: Dictionary = _as_dictionary(saved[cave_id_variant])
		var positions: Dictionary = {}
		var saved_positions: Dictionary = _as_dictionary(progress.get("hole_positions", {}))
		for depth_variant in saved_positions:
			positions[str(depth_variant)] = str(saved_positions[depth_variant])
		var found_holes: Array = []
		for depth_variant in _as_array(progress.get("found_holes", [])):
			found_holes.append(int(depth_variant))
		var ladders: Array = []
		for depth_variant in _as_array(progress.get("ladders", [])):
			ladders.append(int(depth_variant))
		result[cave_id] = {
			"hole_positions": positions,
			"found_holes": found_holes,
			"ladders": ladders,
		}
	return result


func _clamp_tier(line: String, value: int, minimum: int) -> int:
	var line_data: Dictionary = GameData.upgrades.get(line, {})
	var tiers: Array = line_data.get("tiers", [])
	if tiers.is_empty():
		return minimum
	var available_tiers: int = mini(int(line_data.get("available_tiers", tiers.size())), tiers.size())
	return clampi(value, minimum, available_tiers - 1)


func _validate_save_data(data: Dictionary) -> bool:
	var required_keys: Array[String] = [
		"day", "phase_index", "seconds_into_phase", "gold", "inventory",
		"upgrade_tiers", "botanary", "cave_progress", "flags", "current_cave",
		"last_recovery", "world",
	]
	for key in required_keys:
		if not data.has(key):
			return false
	if not _is_number(data["day"]) or not _is_number(data["phase_index"]):
		return false
	if not _is_number(data["seconds_into_phase"]) or not _is_number(data["gold"]):
		return false
	for key in ["inventory", "upgrade_tiers", "botanary", "cave_progress", "flags", "current_cave", "last_recovery", "world"]:
		if not data[key] is Dictionary:
			return false
	if data.has("resume_location"):
		if not data["resume_location"] is String:
			return false
		if not _is_valid_resume_location(str(data["resume_location"])):
			return false

	var inventory: Dictionary = data["inventory"]
	for count_variant in inventory.values():
		if not _is_number(count_variant):
			return false
	var tiers: Dictionary = data["upgrade_tiers"]
	for key in ["bag", "lantern", "cauldron"]:
		if not tiers.has(key) or not _is_number(tiers[key]):
			return false
	var cave_progress: Dictionary = data["cave_progress"]
	if not _validate_cave_progress(cave_progress):
		return false
	var botanary: Dictionary = data["botanary"]
	for discovered_variant in botanary.values():
		if not discovered_variant is bool:
			return false
	var flags: Dictionary = data["flags"]
	if not flags.has("can_stay_up_past_midnight") \
		or not flags["can_stay_up_past_midnight"] is bool:
		return false
	var current_cave: Dictionary = data["current_cave"]
	if not _validate_current_cave(current_cave):
		return false
	var recovery: Dictionary = data["last_recovery"]
	if not _validate_recovery(recovery):
		return false
	var world: Dictionary = data["world"]
	return _validate_world_data(world)


func _validate_cave_progress(saved: Dictionary) -> bool:
	for progress_variant in saved.values():
		if not progress_variant is Dictionary:
			return false
		var progress: Dictionary = progress_variant
		if not progress.has("hole_positions") or not progress["hole_positions"] is Dictionary:
			return false
		var positions: Dictionary = progress["hole_positions"]
		for marker_variant in positions.values():
			if not marker_variant is String:
				return false
		if not progress.has("found_holes") or not progress["found_holes"] is Array:
			return false
		if not progress.has("ladders") or not progress["ladders"] is Array:
			return false
		for depth_variant in progress["found_holes"]:
			if not _is_number(depth_variant):
				return false
		for depth_variant in progress["ladders"]:
			if not _is_number(depth_variant):
				return false
	return true


func _validate_current_cave(current_cave: Dictionary) -> bool:
	if not current_cave.has("id") or not current_cave["id"] is String:
		return false
	if not current_cave.has("depth") or not _is_number(current_cave["depth"]):
		return false
	if not current_cave.has("entry_mode") or not current_cave["entry_mode"] is String:
		return false
	var entry_mode: String = str(current_cave["entry_mode"])
	return entry_mode == "entrance" or entry_mode == "arrival" or entry_mode == "hole_return"


func _validate_recovery(recovery: Dictionary) -> bool:
	if recovery.is_empty():
		return true
	if not recovery.has("reason") or not recovery["reason"] is String:
		return false
	var reason: String = str(recovery["reason"])
	if reason != "sleep" and reason != "pass_out":
		return false
	if not recovery.has("lost_items") or not recovery["lost_items"] is Dictionary:
		return false
	var lost_items: Dictionary = recovery["lost_items"]
	for count_variant in lost_items.values():
		if not _is_number(count_variant):
			return false
	return recovery.has("fine") and _is_number(recovery["fine"])


func _validate_world_data(world: Dictionary) -> bool:
	var required_keys: Array[String] = [
		"forest_spawn_day", "forest_spawn_phase", "forest_plants",
		"midnight_bloom_day", "midnight_bloom_collected", "cave_spawn_day", "cave_plants",
	]
	for key in required_keys:
		if not world.has(key):
			return false
	if not _is_number(world["forest_spawn_day"]) or not world["forest_spawn_phase"] is String:
		return false
	if not world["forest_plants"] is Array or not _validate_spawn_records(world["forest_plants"]):
		return false
	if not _is_number(world["midnight_bloom_day"]) or not world["midnight_bloom_collected"] is bool:
		return false
	if not _is_number(world["cave_spawn_day"]) or not world["cave_plants"] is Dictionary:
		return false
	var cave_plants: Dictionary = world["cave_plants"]
	for records_variant in cave_plants.values():
		if not records_variant is Array or not _validate_spawn_records(records_variant):
			return false
	return true


func _validate_spawn_records(records: Array) -> bool:
	for record_variant in records:
		if not record_variant is Dictionary:
			return false
		var record: Dictionary = record_variant
		for key in ["id", "item", "marker"]:
			if not record.has(key) or not record[key] is String:
				return false
	return true


func _is_number(value: Variant) -> bool:
	return typeof(value) == TYPE_INT or typeof(value) == TYPE_FLOAT


func _validated_resume_location(value: String) -> String:
	if value == "home" or value == "clinic":
		return value
	return "forest"


func _is_valid_resume_location(value: String) -> bool:
	return value == "forest" or value == "home" or value == "clinic"


func _resume_saved_location() -> void:
	if GameState.resume_location == "home":
		get_tree().change_scene_to_file("res://scenes/home.tscn")
	elif GameState.resume_location == "clinic":
		get_tree().change_scene_to_file("res://scenes/clinic.tscn")


func _as_dictionary(value: Variant) -> Dictionary:
	if value is Dictionary:
		var result: Dictionary = value
		return result
	return {}


func _as_array(value: Variant) -> Array:
	if value is Array:
		var result: Array = value
		return result
	return []
