extends Node

var _transitioning: bool = false


func _ready() -> void:
	EventBus.midnight_reached.connect(_on_midnight_reached)
	EventBus.sleep_requested.connect(_on_sleep_requested)


func _on_midnight_reached() -> void:
	if _transitioning or GameState.can_stay_up_past_midnight:
		return
	_transitioning = true
	GameState.apply_pass_out()
	GameClock.start_next_day()
	GameState.last_save_failed = not SaveManager.save_game("clinic")
	get_tree().call_deferred("change_scene_to_file", "res://scenes/clinic.tscn")


func _on_sleep_requested() -> void:
	if _transitioning:
		return
	_transitioning = true
	GameState.prepare_sleep()
	GameClock.start_next_day()
	GameState.last_save_failed = not SaveManager.save_game("home")
	get_tree().call_deferred("change_scene_to_file", "res://scenes/home.tscn")
