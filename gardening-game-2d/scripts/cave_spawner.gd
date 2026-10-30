extends Node2D

const PLANT_SCENE: PackedScene = preload("res://scenes/plant.tscn")

@onready var spawn_markers: Node2D = $SpawnMarkers
@onready var plants: Node2D = $Plants

var _markers: Array = []
var _marker_lookup: Dictionary = {}


func _ready() -> void:
	_markers = spawn_markers.get_children()
	for marker_variant in _markers:
		var marker: Marker2D = marker_variant
		_marker_lookup[str(marker.name)] = marker
	EventBus.plant_collected.connect(_on_plant_collected)
	EventBus.day_started.connect(_on_day_started)
	_rebuild()


func _rebuild() -> void:
	for plant in plants.get_children():
		plant.queue_free()

	if GameState.has_cave_spawn_records(GameState.current_cave_id, GameState.current_cave_depth):
		_spawn_records(GameState.get_cave_spawn_records(
			GameState.current_cave_id, GameState.current_cave_depth
		))
		return

	var depth_data: Dictionary = GameData.get_cave_depth(
		GameState.current_cave_id, GameState.current_cave_depth
	)
	var table_id: String = str(depth_data.get("spawn_table", ""))
	var cave_tables: Dictionary = GameData.spawns.get("cave_depths", {})
	var entries: Array = cave_tables.get(table_id, [])
	var available_markers: Array = _markers.duplicate()
	available_markers.shuffle()
	var records: Array = []
	var remaining: Dictionary = {}
	var total_spawns: int = 0

	for entry_variant in entries:
		if not entry_variant is Dictionary:
			continue
		var entry: Dictionary = entry_variant
		var item_id: String = str(entry.get("item", ""))
		var max_count: int = int(entry.get("max", 0))
		if item_id == "" or max_count <= 0:
			continue
		remaining[item_id] = int(remaining.get(item_id, 0)) + max_count
		total_spawns += max_count

	for _index in total_spawns:
		var item_id: String = _pick_item(entries, remaining)
		if item_id == "" or available_markers.is_empty():
			break
		var marker: Marker2D = available_markers.pop_back()
		records.append({
			"id": "cave:%d:%s:%d:%s" % [
				GameClock.day,
				GameState.current_cave_id,
				GameState.current_cave_depth,
				marker.name,
			],
			"item": item_id,
			"marker": str(marker.name),
		})
		remaining[item_id] = int(remaining[item_id]) - 1

	GameState.set_cave_spawn_records(
		GameState.current_cave_id, GameState.current_cave_depth, records
	)
	_spawn_records(records)


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


func _on_plant_collected(spawn_id: String, _item_id: String) -> void:
	GameState.remove_cave_spawn(
		GameState.current_cave_id, GameState.current_cave_depth, spawn_id
	)


func _on_day_started(_day: int) -> void:
	_rebuild()


func _pick_item(entries: Array, remaining: Dictionary) -> String:
	var total_weight: float = 0.0
	for entry_variant in entries:
		if not entry_variant is Dictionary:
			continue
		var entry: Dictionary = entry_variant
		var item_id: String = str(entry.get("item", ""))
		if int(remaining.get(item_id, 0)) > 0:
			total_weight += float(entry.get("weight", 0.0))
	if total_weight <= 0.0:
		return ""

	var roll: float = randf() * total_weight
	for entry_variant in entries:
		if not entry_variant is Dictionary:
			continue
		var entry: Dictionary = entry_variant
		var item_id: String = str(entry.get("item", ""))
		if int(remaining.get(item_id, 0)) <= 0:
			continue
		roll -= float(entry.get("weight", 0.0))
		if roll <= 0.0:
			return item_id
	return ""
