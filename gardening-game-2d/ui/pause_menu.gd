extends CanvasLayer

var overlay: Control
var main_panel: PanelContainer
var settings: SettingsPanel
var saves: SaveLoadPanel
var status: Label
var _menu_count: int = 0


func _ready() -> void:
	layer = 6
	EventBus.menu_opened.connect(_on_menu_opened)
	EventBus.menu_closed.connect(_on_menu_closed)
	overlay = Control.new()
	overlay.name = "Overlay"
	add_child(overlay)
	overlay.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	overlay.theme = load("res://ui/menu_theme.tres") as Theme
	var dimmer: ColorRect = ColorRect.new()
	dimmer.color = Color(0.06, 0.06, 0.1, 0.75)
	overlay.add_child(dimmer)
	dimmer.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	main_panel = PanelContainer.new()
	main_panel.name = "PausePanel"
	overlay.add_child(main_panel)
	MenuLayout.center(main_panel, Vector2(280, 286))
	var column: VBoxContainer = MenuLayout.content(main_panel, "Paused")
	MenuLayout.button(column, "Resume", _close)
	MenuLayout.button(column, "Save Game", _show_save)
	MenuLayout.button(column, "Load Game", _show_load)
	MenuLayout.button(column, "Settings", _show_settings)
	MenuLayout.button(column, "Save & Main Menu", _leave)
	status = Label.new()
	status.add_theme_font_size_override("font_size", 11)
	column.add_child(status)
	settings = SettingsPanel.new()
	settings.visible = false
	overlay.add_child(settings)
	settings.back_requested.connect(_show_main)
	saves = SaveLoadPanel.new()
	saves.visible = false
	overlay.add_child(saves)
	saves.back_requested.connect(_show_main)
	saves.loaded.connect(_loaded)
	overlay.visible = false


func _unhandled_input(event: InputEvent) -> void:
	if event.is_echo() or not event.is_action_pressed("cancel"):
		return
	if overlay.visible:
		if not main_panel.visible:
			_show_main()
		else:
			_close()
		get_viewport().set_input_as_handled()
	elif _menu_count == 0:
		overlay.visible = true
		_show_main()
		EventBus.menu_opened.emit()
		get_viewport().set_input_as_handled()


func _close() -> void:
	if overlay.visible:
		overlay.visible = false
		EventBus.menu_closed.emit()


func _exit_tree() -> void:
	if is_instance_valid(overlay) and overlay.visible:
		EventBus.menu_closed.emit()


func _show_main() -> void:
	main_panel.visible = true
	settings.visible = false
	saves.visible = false


func _show_save() -> void:
	main_panel.visible = false
	saves.open_mode("save")


func _show_load() -> void:
	main_panel.visible = false
	saves.open_mode("load")


func _show_settings() -> void:
	main_panel.visible = false
	settings.visible = true


func _loaded() -> void:
	_close()
	SaveManager.resume_game()


func _leave() -> void:
	if not SaveManager.save_game():
		status.text = "Save failed. Please try again."
		return
	_close()
	get_tree().change_scene_to_file("res://ui/main_menu.tscn")


func _on_menu_opened() -> void:
	_menu_count += 1


func _on_menu_closed() -> void:
	_menu_count = maxi(0, _menu_count - 1)
