extends Area2D

@export var cave_id: String = "cave_a"

@onready var prompt: Label = $Prompt

var _player_nearby: bool = false
var _menu_count: int = 0


func _ready() -> void:
	body_entered.connect(_on_body_entered)
	body_exited.connect(_on_body_exited)
	EventBus.menu_opened.connect(_on_menu_opened)
	EventBus.menu_closed.connect(_on_menu_closed)
	_update_prompt()


func _unhandled_input(event: InputEvent) -> void:
	if not _player_nearby or _menu_count > 0 or not event.is_action_pressed("interact"):
		return
	get_viewport().set_input_as_handled()
	if not GameState.can_access_cave_depth(cave_id, 1):
		EventBus.message_requested.emit("Too dark to enter. A lantern is required.")
		return
	GameState.enter_cave(cave_id, 1, "entrance")
	get_tree().change_scene_to_file("res://scenes/cave_depth.tscn")


func _on_body_entered(body: Node2D) -> void:
	if body.is_in_group("player"):
		_player_nearby = true
		_update_prompt()


func _on_body_exited(body: Node2D) -> void:
	if body.is_in_group("player"):
		_player_nearby = false
		_update_prompt()


func _on_menu_opened() -> void:
	_menu_count += 1
	_update_prompt()


func _on_menu_closed() -> void:
	_menu_count = max(0, _menu_count - 1)
	_update_prompt()


func _update_prompt() -> void:
	prompt.visible = _player_nearby and _menu_count == 0
