extends Control

var main_panel: PanelContainer
var settings: SettingsPanel
var saves: SaveLoadPanel
var appearance: OptionButton
var continue_button: Button
var status: Label


func _ready() -> void:
	GameClock.is_running = false
	UserSettings.load_and_apply()
	theme = load("res://ui/menu_theme.tres") as Theme
	MenuLayout.background(self)
	main_panel = PanelContainer.new()
	main_panel.name = "MainPanel"
	add_child(main_panel)
	MenuLayout.center(main_panel, Vector2(280, 306))
	var column: VBoxContainer = MenuLayout.content(main_panel, "Potion Forager")
	appearance = OptionButton.new()
	appearance.name = "Appearance"
	for key: Variant in GameData.visuals.get("characters", {}):
		appearance.add_item("Adventurer: " + str(key).capitalize())
		appearance.set_item_metadata(appearance.item_count - 1, str(key))
		if str(key) == GameState.appearance:
			appearance.select(appearance.item_count - 1)
	column.add_child(appearance)
	var new_game_button: Button = MenuLayout.button(column, "New Game", _new_game)
	continue_button = MenuLayout.button(column, "Continue", _continue_game)
	continue_button.disabled = SaveManager.latest_slot().is_empty()
	MenuLayout.button(column, "Load Game", _show_load)
	MenuLayout.button(column, "Settings", _show_settings)
	MenuLayout.button(column, "Quit", get_tree().quit)
	status = Label.new()
	status.add_theme_font_size_override("font_size", 11)
	column.add_child(status)
	settings = SettingsPanel.new()
	settings.name = "Settings"
	settings.visible = false
	add_child(settings)
	settings.back_requested.connect(_show_main)
	saves = SaveLoadPanel.new()
	saves.name = "SaveLoad"
	saves.visible = false
	add_child(saves)
	saves.back_requested.connect(_show_main)
	saves.loaded.connect(_loaded)
	if continue_button.disabled:
		new_game_button.grab_focus()
	else:
		continue_button.grab_focus()


func _unhandled_input(event: InputEvent) -> void:
	if event.is_action_pressed("cancel") and not main_panel.visible:
		_show_main()
		get_viewport().set_input_as_handled()


func _new_game() -> void:
	GameState.reset_for_new_game(str(appearance.get_selected_metadata()))
	get_tree().change_scene_to_file("res://scenes/town_square.tscn")


func _continue_game() -> void:
	var path: String = SaveManager.latest_slot()
	if not path.is_empty() and SaveManager.load_slot(path):
		_loaded()
	else:
		status.text = "No valid save is available."


func _loaded() -> void:
	if SaveManager.resume_game() != OK:
		status.text = "Could not open the saved area."


func _show_main() -> void:
	main_panel.visible = true
	settings.visible = false
	saves.visible = false
	continue_button.disabled = SaveManager.latest_slot().is_empty()


func _show_load() -> void:
	main_panel.visible = false
	saves.open_mode("load")


func _show_settings() -> void:
	main_panel.visible = false
	settings.visible = true
