extends CanvasLayer

@onready var up_button: Button = $Window/UpButton
@onready var exit_button: Button = $Window/ExitButton
@onready var cancel_button: Button = $Window/CancelButton


func _ready() -> void:
	visible = false
	EventBus.ladder_requested.connect(_open)
	up_button.pressed.connect(_go_up)
	exit_button.pressed.connect(_get_out)
	cancel_button.pressed.connect(_close)


func _unhandled_input(event: InputEvent) -> void:
	if visible and event.is_action_pressed("cancel"):
		_close()
		get_viewport().set_input_as_handled()


func _exit_tree() -> void:
	if visible:
		EventBus.menu_closed.emit()


func _open() -> void:
	if visible:
		return
	visible = true
	EventBus.menu_opened.emit()


func _close() -> void:
	if not visible:
		return
	visible = false
	EventBus.menu_closed.emit()


func _go_up() -> void:
	if not GameState.go_up_cave_depth():
		return
	_close()
	get_tree().change_scene_to_file("res://scenes/cave_depth.tscn")


func _get_out() -> void:
	_close()
	get_tree().change_scene_to_file("res://scenes/forest.tscn")
