class_name UserSettings
extends RefCounted

const PATH: String = "user://settings.cfg"
const DISPLAY_MODES: Array[String] = ["windowed", "fullscreen"]
static var values: Dictionary = {}


static func load_and_apply() -> void:
	var defaults: Dictionary = GameData.interface_data.get("settings_defaults", {})
	values = defaults.duplicate(true)
	var file: ConfigFile = ConfigFile.new()
	if file.load(PATH) == OK:
		var legacy_fullscreen: Variant = file.get_value("settings", "fullscreen", null)
		for key: Variant in defaults:
			var value: Variant = file.get_value("settings", str(key), defaults[key])
			if key == "master_volume" and (value is float or value is int):
				values[key] = clampf(float(value), 0.0, 1.0)
			elif key == "display_mode" and value is String and DISPLAY_MODES.has(value):
				values[key] = value
			elif key == "resolution" and value is String and _has_resolution(value):
				values[key] = value
			elif key == "vsync" and value is bool:
				values[key] = value
		if not file.has_section_key("settings", "display_mode") and legacy_fullscreen is bool:
			values["display_mode"] = "fullscreen" if legacy_fullscreen else "windowed"
	apply()


static func update(key: String, value: Variant) -> bool:
	values[key] = value
	apply()
	var file: ConfigFile = ConfigFile.new()
	for name: Variant in values:
		file.set_value("settings", str(name), values[name])
	return file.save(PATH) == OK


static func apply() -> void:
	var volume: float = float(values.get("master_volume", 0.8))
	AudioServer.set_bus_mute(0, volume <= 0.0)
	AudioServer.set_bus_volume_db(0, linear_to_db(maxf(volume, 0.001)))
	if DisplayServer.get_name() == "headless":
		return
	var tree: SceneTree = Engine.get_main_loop() as SceneTree
	var window: Window = tree.root
	var fullscreen: bool = str(values.get("display_mode", "windowed")) == "fullscreen"
	if fullscreen:
		window.mode = Window.MODE_FULLSCREEN
	else:
		window.mode = Window.MODE_WINDOWED
		window.size = resolution_size()
		window.move_to_center()
	DisplayServer.window_set_vsync_mode(DisplayServer.VSYNC_ENABLED if bool(values.get("vsync", true)) else DisplayServer.VSYNC_DISABLED)


static func resolution_options() -> Array:
	return GameData.interface_data.get("resolutions", [])


static func resolution_size() -> Vector2i:
	var desired: Vector2i = _parse_size(str(values.get("resolution", "1280x720")))
	if desired == Vector2i.ZERO:
		desired = Vector2i(1280, 720)
	if DisplayServer.get_name() == "headless":
		return desired
	var usable: Vector2i = DisplayServer.screen_get_usable_rect().size
	if usable.x > 0 and usable.y > 0 and (desired.x > usable.x or desired.y > usable.y):
		var factor: float = minf(float(usable.x) / float(desired.x), float(usable.y) / float(desired.y))
		desired = Vector2i(int(float(desired.x) * factor), int(float(desired.y) * factor))
	return desired


static func _has_resolution(value: String) -> bool:
	for entry: Variant in resolution_options():
		if value == str((entry as Dictionary).get("value", "")):
			return true
	return false


static func _parse_size(value: String) -> Vector2i:
	var parts: PackedStringArray = value.split("x")
	if parts.size() != 2:
		return Vector2i.ZERO
	return Vector2i(int(parts[0]), int(parts[1]))
