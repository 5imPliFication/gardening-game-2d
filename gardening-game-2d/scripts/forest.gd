extends Node2D


func _ready() -> void:
	GameClock.is_running = GameClock.current_phase_name() != "Midnight"
