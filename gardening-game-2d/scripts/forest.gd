extends "res://scripts/world_location.gd"


func _ready() -> void:
	super._ready()
	GameClock.is_running = GameClock.current_phase_name() != "Midnight"
