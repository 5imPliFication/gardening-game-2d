extends CanvasLayer

@onready var mini_panel: Panel = $MiniPanel
@onready var location_label: Label = $MiniPanel/Location
@onready var window: Panel = $WorldWindow
@onready var world_canvas: WorldMapCanvas = $WorldWindow/Canvas
@onready var description: Label = $WorldWindow/Description

var _menu_count: int = 0


func _ready() -> void:
	window.visible = false
	EventBus.menu_opened.connect(_on_menu_opened)
	EventBus.menu_closed.connect(_on_menu_closed)
	EventBus.location_changed.connect(_on_location_changed)
	$WorldWindow/Close.pressed.connect(_close)
	world_canvas.location_selected.connect(_show_description)
	_on_location_changed(GameState.current_map_id)


func _unhandled_input(event: InputEvent) -> void:
	if event.is_echo():
		return
	if event.is_action_pressed("open_map"):
		_set_open(not window.visible)
		get_viewport().set_input_as_handled()
	elif window.visible and event.is_action_pressed("cancel"):
		_set_open(false)
		get_viewport().set_input_as_handled()


func _set_open(should_open: bool) -> void:
	if window.visible == should_open or (should_open and _menu_count > 0):
		return
	window.visible = should_open
	$Dimmer.visible = should_open
	mini_panel.visible = not should_open
	if should_open:
		_on_location_changed(GameState.current_map_id)
		EventBus.menu_opened.emit()
	else:
		EventBus.menu_closed.emit()


func _close() -> void:
	_set_open(false)


func _exit_tree() -> void:
	if is_instance_valid(window) and window.visible:
		EventBus.menu_closed.emit()


func _on_location_changed(id: String) -> void:
	var definition: Dictionary = GameData.maps.get("locations", {}).get(id, {})
	location_label.text = str(definition.get("name", id))
	world_canvas.selected_id = str(definition.get("world_parent", id))
	world_canvas.queue_redraw()
	_show_description(world_canvas.selected_id)


func _show_description(id: String) -> void:
	var locations: Dictionary = GameData.maps.get("locations", {})
	var definition: Dictionary = locations.get(id, {})
	var current: Dictionary = locations.get(GameState.current_map_id, {})
	description.text = "You are in: %s\n%s" % [str(current.get("name", GameState.current_map_id)), str(definition.get("description", ""))]


func _on_menu_opened() -> void:
	_menu_count += 1


func _on_menu_closed() -> void:
	_menu_count = maxi(0, _menu_count - 1)
