class_name SettingsPanel
extends PanelContainer

signal back_requested

var status: Label
var resolution_choice: OptionButton


func _ready() -> void:
	if UserSettings.values.is_empty():
		UserSettings.load_and_apply()
	MenuLayout.center(self, Vector2(480, 340))
	var column: VBoxContainer = MenuLayout.content(self, "Settings")
	var volume_row: HBoxContainer = HBoxContainer.new()
	column.add_child(volume_row)
	var label: Label = Label.new()
	label.text = "Master volume"
	label.custom_minimum_size.x = 140
	volume_row.add_child(label)
	var slider: HSlider = HSlider.new()
	slider.name = "MasterVolume"
	slider.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	slider.min_value = 0
	slider.max_value = 100
	slider.value = float(UserSettings.values["master_volume"]) * 100
	volume_row.add_child(slider)
	slider.value_changed.connect(func(value: float) -> void: _update("master_volume", value / 100.0))
	var display_mode: OptionButton = OptionButton.new()
	display_mode.name = "DisplayMode"
	display_mode.add_item("Windowed")
	display_mode.set_item_metadata(0, "windowed")
	display_mode.add_item("Fullscreen Windowed")
	display_mode.set_item_metadata(1, "fullscreen")
	display_mode.select(1 if str(UserSettings.values["display_mode"]) == "fullscreen" else 0)
	column.add_child(display_mode)
	display_mode.item_selected.connect(func(index: int) -> void: _set_display_mode(display_mode.get_item_metadata(index)))
	resolution_choice = OptionButton.new()
	resolution_choice.name = "Resolution"
	var options: Array = UserSettings.resolution_options()
	for index: int in options.size():
		var option: Dictionary = options[index]
		resolution_choice.add_item(str(option.get("label", option.get("value", ""))))
		resolution_choice.set_item_metadata(index, str(option.get("value", "")))
		if str(option.get("value", "")) == str(UserSettings.values["resolution"]):
			resolution_choice.select(index)
	column.add_child(resolution_choice)
	resolution_choice.item_selected.connect(func(index: int) -> void: _update("resolution", str(resolution_choice.get_item_metadata(index))))
	_update_resolution_enabled()
	var vsync: CheckBox = CheckBox.new()
	vsync.text = "VSync"
	vsync.button_pressed = bool(UserSettings.values["vsync"])
	column.add_child(vsync)
	vsync.toggled.connect(func(value: bool) -> void: _update("vsync", value))
	var controls: Label = Label.new()
	controls.text = "WASD: Move  ·  E: Interact  ·  I: Inventory\nB: Botanary  ·  M: Map  ·  Esc: Close / Pause"
	controls.add_theme_font_size_override("font_size", 12)
	column.add_child(controls)
	status = Label.new()
	status.add_theme_font_size_override("font_size", 11)
	column.add_child(status)
	MenuLayout.button(column, "Back", back_requested.emit)


func _set_display_mode(mode: Variant) -> void:
	_update("display_mode", str(mode))
	_update_resolution_enabled()


func _update_resolution_enabled() -> void:
	resolution_choice.disabled = str(UserSettings.values.get("display_mode", "windowed")) == "fullscreen"


func _update(key: String, value: Variant) -> void:
	status.text = "Settings saved." if UserSettings.update(key, value) else "Could not save settings."
