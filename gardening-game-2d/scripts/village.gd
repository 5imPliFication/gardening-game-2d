extends "res://scripts/world_location.gd"

const PORTAL: PackedScene = preload("res://scenes/world_portal.tscn")


func _ready() -> void:
	var definition: Dictionary = GameData.maps.get("locations", {}).get(map_id, {})
	var environment_path: String = str(definition.get("environment", ""))
	if not environment_path.is_empty():
		var environment: Node2D = (load(environment_path) as PackedScene).instantiate()
		$Environment.add_child(environment)
	for value: Variant in definition.get("structures", []):
		_add_portal(value, true)
	for value: Variant in definition.get("exits", []):
		_add_portal(value, false)
	super._ready()
	GameClock.is_running = GameClock.current_phase_name() != "Midnight"


func _add_portal(definition: Dictionary, pending: bool) -> void:
	var portal: Area2D = PORTAL.instantiate()
	var point: Array = definition["position"]
	portal.position = Vector2(float(point[0]), float(point[1]))
	portal.set("title", str(definition["name"]))
	portal.set("pending_structure", pending)
	portal.set("target_scene", str(definition.get("target_scene", "")))
	portal.set("target_spawn", str(definition.get("target_spawn", "")))
	portal.name = str(definition["name"]).replace(" ", "")
	add_child(portal, true)
