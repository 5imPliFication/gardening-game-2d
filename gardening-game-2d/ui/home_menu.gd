extends CanvasLayer

@onready var save_button: Button = $Window/SaveButton
@onready var close_button: Button = $Window/CloseButton
@onready var status_label: Label = $Window/StatusLabel

var _menu_count: int = 0


func _ready() -> void:
	visible = false
	EventBus.home_menu_requested.connect(_on_home_menu_requested)
	EventBus.menu_opened.connect(_on_menu_opened)
	EventBus.menu_closed.connect(_on_menu_closed)
	save_button.pressed.connect(_on_save_pressed)
	close_button.pressed.connect(_on_close_pressed)


func _unhandled_input(event: InputEvent) -> void:
	if visible and event.is_action_pressed("cancel"):
		_set_open(false)
		get_viewport().set_input_as_handled()


func _set_open(should_open: bool) -> void:
	if visible == should_open:
		return
	if should_open and _menu_count > 0:
		return
	visible = should_open
	if should_open:
		status_label.text = ""
		EventBus.menu_opened.emit()
	else:
		EventBus.menu_closed.emit()


func _exit_tree() -> void:
	if visible:
		EventBus.menu_closed.emit()


func _on_home_menu_requested() -> void:
	_set_open(true)


func _on_save_pressed() -> void:
	status_label.text = "Game saved." if SaveManager.save_game("home") else "Save failed."


func _on_close_pressed() -> void:
	_set_open(false)


func _on_menu_opened() -> void:
	_menu_count += 1


func _on_menu_closed() -> void:
	_menu_count = max(0, _menu_count - 1)
