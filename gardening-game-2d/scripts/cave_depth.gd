extends Node2D

@onready var player: CharacterBody2D = $Player
@onready var arrival_marker: Marker2D = $ArrivalMarker
@onready var hole_candidates: Node2D = $HoleCandidates
@onready var hole: Area2D = $HiddenHole
@onready var ladder: Area2D = $Ladder
@onready var cave_exit: Area2D = $CaveExit
@onready var depth_label: Label = $HUD/DepthLabel


func _ready() -> void:
	GameClock.is_running = GameClock.current_phase_name() != "Midnight"
	var depth_data: Dictionary = GameData.get_cave_depth(
		GameState.current_cave_id, GameState.current_cave_depth
	)
	if depth_data.is_empty():
		push_error("CaveDepth: missing cave depth data")
		return

	depth_label.visible = true
	depth_label.text = "Cave A - Depth %d | Lantern %d" % [
		GameState.current_cave_depth, GameState.get_lantern_level()
	]
	_configure_hole(depth_data)
	_configure_ladder_and_exit()
	_place_player()


func _configure_hole(depth_data: Dictionary) -> void:
	var next_depth: Dictionary = GameData.get_cave_depth(
		GameState.current_cave_id, GameState.current_cave_depth + 1
	)
	if next_depth.is_empty():
		hole.visible = false
		hole.monitoring = false
		return

	var candidates: Array = depth_data.get("hole_candidates", [])
	var marker_name: String = GameState.get_or_choose_hole(
		GameState.current_cave_id, GameState.current_cave_depth, candidates
	)
	var marker: Marker2D = hole_candidates.get_node_or_null(marker_name)
	if marker == null:
		push_error("CaveDepth: missing hole marker %s" % marker_name)
		hole.visible = false
		hole.monitoring = false
		return
	hole.position = marker.position
	hole.set_found(GameState.is_cave_hole_found(
		GameState.current_cave_id, GameState.current_cave_depth
	))


func _configure_ladder_and_exit() -> void:
	var has_ladder: bool = GameState.has_cave_ladder(
		GameState.current_cave_id, GameState.current_cave_depth
	)
	ladder.position = arrival_marker.position
	ladder.visible = has_ladder
	ladder.monitoring = has_ladder
	cave_exit.visible = GameState.current_cave_depth == 1
	cave_exit.monitoring = cave_exit.visible


func _place_player() -> void:
	if GameState.cave_entry_mode == "hole_return" and hole.visible:
		player.position = hole.position + Vector2(-64, 0)
	else:
		player.position = arrival_marker.position
