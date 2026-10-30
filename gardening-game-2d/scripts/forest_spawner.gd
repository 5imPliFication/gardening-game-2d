extends Node2D

const PLANT_SCENE: PackedScene = preload("res://scenes/plant.tscn")

@onready var spawn_markers: Node2D = $SpawnMarkers
@onready var plants: Node2D = $Plants

var _markers: Array = []
var _marker_lookup: Dictionary = {}


func _ready() -> void:
	randomize()
	_markers = spawn_markers.get_children()
	for marker_variant in _markers:
		var marker: Marker2D = marker_variant
		_marker_lookup[str(marker.name)] = marker
	EventBus.phase_changed.connect(_on_phase_changed)
	EventBus.time_warning.connect(_on_time_warning)
	EventBus.plant_collected.connect(_on_plant_collected)
	_rebuild()


func _on_phase_changed(_phase: String) -> void:
	_rebuild()


func _on_time_warning(seconds_left: int) -> void:
	var bloom_data: Dictionary = GameData.spawns.get("midnight_bloom", {})
	if seconds_left <= int(bloom_data.get("window_seconds", 0)):
		_ensure_midnight_bloom()


func _rebuild() -> void:
	for plant in plants.get_children():
		plant.queue_free()

	if GameState.has_current_forest_spawns():
		_spawn_records(GameState.forest_plants)
		_ensure_midnight_bloom()
		return

	var phase: String = GameClock.current_phase_name()
	var forest_tables: Dictionary = GameData.spawns.get("forest", {})
	var entries: Array = forest_tables.get(phase, [])
	if entries.is_empty():
		GameState.set_forest_spawns([])
		_ensure_midnight_bloom()
		return

	var available_markers: Array = _markers.duplicate()
	available_markers.shuffle()

	var remaining: Dictionary = {}
	var total_spawns: int = 0
	var spawn_records: Array = []

	for entry in entries:
		if not entry is Dictionary:
			continue
		var row: Dictionary = entry
		var item_id: String = str(row.get("item", ""))
		var max_count: int = int(row.get("max", 0))
		if item_id == "" or max_count <= 0:
			continue
		remaining[item_id] = int(remaining.get(item_id, 0)) + max_count
		total_spawns += max_count

	for _i in total_spawns:
		var item_id: String = _pick_item(entries, remaining)
		if item_id == "" or available_markers.is_empty():
			break
		var marker: Marker2D = available_markers.pop_back()
		spawn_records.append({
			"id": "%d:%s:%s" % [GameClock.day, phase, marker.name],
			"item": item_id,
			"marker": str(marker.name),
		})
		remaining[item_id] = int(remaining[item_id]) - 1

	GameState.set_forest_spawns(spawn_records)
	_spawn_records(spawn_records)
	_ensure_midnight_bloom()


func _spawn_records(records: Array) -> void:
	for record_variant in records:
		if not record_variant is Dictionary:
			continue
		var record: Dictionary = record_variant
		var marker_name: String = str(record.get("marker", ""))
		if not _marker_lookup.has(marker_name):
			continue
		var marker: Marker2D = _marker_lookup[marker_name]
		var plant: Node2D = PLANT_SCENE.instantiate()
		plant.set("item_id", str(record.get("item", "")))
		plant.set("spawn_id", str(record.get("id", "")))
		plant.position = marker.position
		plants.add_child(plant)


func _on_plant_collected(spawn_id: String, item_id: String) -> void:
	GameState.remove_forest_spawn(spawn_id)
	var bloom_data: Dictionary = GameData.spawns.get("midnight_bloom", {})
	if item_id == str(bloom_data.get("item", "")):
		GameState.mark_midnight_bloom_collected()


func _ensure_midnight_bloom() -> void:
	if GameClock.current_phase_name() != "Evening":
		return

	var bloom_data: Dictionary = GameData.spawns.get("midnight_bloom", {})
	var item_id: String = str(bloom_data.get("item", ""))
	var max_count: int = int(bloom_data.get("max", 0))
	var window_seconds: float = float(bloom_data.get("window_seconds", 0.0))
	var seconds_left: float = Config.PHASE_SECONDS - GameClock.seconds_into_phase
	if item_id == "" or max_count <= 0 or window_seconds <= 0.0 or seconds_left > window_seconds:
		return

	GameState.prepare_midnight_bloom_day()
	if GameState.midnight_bloom_collected:
		return

	var existing_count: int = 0
	var used_markers: Array[String] = []
	for record_variant in GameState.forest_plants:
		if not record_variant is Dictionary:
			continue
		var record: Dictionary = record_variant
		used_markers.append(str(record.get("marker", "")))
		if str(record.get("item", "")) == item_id:
			existing_count += 1
	if existing_count >= max_count:
		return

	var available_markers: Array = []
	for marker_variant in _markers:
		var marker: Marker2D = marker_variant
		if not used_markers.has(str(marker.name)):
			available_markers.append(marker)
	available_markers.shuffle()

	var new_records: Array = []
	for _index in max_count - existing_count:
		if available_markers.is_empty():
			break
		var marker: Marker2D = available_markers.pop_back()
		var record: Dictionary = {
			"id": "%d:Evening:bloom:%s" % [GameClock.day, marker.name],
			"item": item_id,
			"marker": str(marker.name),
		}
		GameState.add_forest_spawn(record)
		new_records.append(record)
	_spawn_records(new_records)


func _pick_item(entries: Array, remaining: Dictionary) -> String:
	var total_weight: float = 0.0
	for entry in entries:
		if not entry is Dictionary:
			continue
		var row: Dictionary = entry
		var item_id: String = str(row.get("item", ""))
		if int(remaining.get(item_id, 0)) > 0:
			total_weight += float(row.get("weight", 0))

	if total_weight <= 0.0:
		return ""

	var roll: float = randf() * total_weight
	for entry in entries:
		if not entry is Dictionary:
			continue
		var row: Dictionary = entry
		var item_id: String = str(row.get("item", ""))
		if int(remaining.get(item_id, 0)) <= 0:
			continue
		roll -= float(row.get("weight", 0))
		if roll <= 0.0:
			return item_id

	return ""
