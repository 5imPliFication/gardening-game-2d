extends Area2D

@export_file("*.tscn") var target_scene: String

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
	if target_scene == "":
		return

	get_viewport().set_input_as_handled()
	get_tree().change_scene_to_file(target_scene)


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
