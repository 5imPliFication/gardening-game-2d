extends Node2D
## Shared location registration and one-shot arrival placement for map-aware scenes.

@export var map_id: String = "forest"


func _ready() -> void:
	GameState.current_map_id = map_id
	EventBus.location_changed.emit(map_id)
	var locations: Dictionary = GameData.maps.get("locations", {})
	var definition: Dictionary = locations.get(map_id, {})
	if bool(definition.get("resume_allowed", false)):
		GameState.resume_location = map_id
	var spawns: Dictionary = definition.get("spawns", {})
	var arrival: String = GameState.pending_spawn
	GameState.pending_spawn = ""
	if GameState.has_pending_position:
		GameState.has_pending_position = false
		EventBus.player_spawn_requested.emit(GameState.pending_position)
	elif spawns.has(arrival):
		var position_data: Array = spawns[arrival]
		EventBus.player_spawn_requested.emit(Vector2(float(position_data[0]), float(position_data[1])))
