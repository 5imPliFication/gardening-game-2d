extends Area2D

@onready var body_rect: ColorRect = $Body
@onready var found_label: Label = $FoundLabel
@onready var prompt: Label = $Prompt

var _player_nearby: bool = false
var _menu_count: int = 0


func _ready() -> void:
	body_entered.connect(_on_body_entered)
	body_exited.connect(_on_body_exited)
	EventBus.menu_opened.connect(_on_menu_opened)
	EventBus.menu_closed.connect(_on_menu_closed)
	_update_prompt()


func set_found(is_found: bool) -> void:
	found_label.visible = is_found
	body_rect.color = Color(0.12, 0.1, 0.08, 1) if is_found else Color(0.15, 0.15, 0.16, 1)


func _unhandled_input(event: InputEvent) -> void:
	if not _player_nearby or _menu_count > 0 or not event.is_action_pressed("interact"):
		return
	get_viewport().set_input_as_handled()
	if GameState.try_descend_cave():
		get_tree().change_scene_to_file("res://scenes/cave_depth.tscn")
		return
	set_found(true)
	var next_depth: int = GameState.current_cave_depth + 1
	if GameData.get_cave_depth(GameState.current_cave_id, next_depth).is_empty():
		EventBus.message_requested.emit("This is the deepest reachable point.")
	else:
		EventBus.message_requested.emit("Too dark to go on.")


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
