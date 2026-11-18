class_name SaveLoadPanel
extends PanelContainer

signal back_requested
signal loaded

var mode: String = "load"
var rows: VBoxContainer
var status: Label
var heading: Label


func _ready() -> void:
	MenuLayout.center(self, Vector2(520, 306))
	var column: VBoxContainer = MenuLayout.content(self, "Load Game")
	heading = column.get_child(0) as Label
	rows = VBoxContainer.new()
	column.add_child(rows)
	status = Label.new()
	status.add_theme_font_size_override("font_size", 11)
	column.add_child(status)
	MenuLayout.button(column, "Back", back_requested.emit)
	_refresh()


func open_mode(value: String) -> void:
	mode = value
	visible = true
	_refresh()


func _refresh() -> void:
	if rows == null:
		return
	heading.text = "Save Game" if mode == "save" else "Load Game"
	for child: Node in rows.get_children():
		rows.remove_child(child)
		child.queue_free()
	for value: Variant in GameData.interface_data.get("save_slots", []):
		var slot: Dictionary = value
		var path: String = str(slot["path"])
		var info: Dictionary = SaveManager.inspect_slot(path)
		var row: HBoxContainer = HBoxContainer.new()
		var label: Label = Label.new()
		label.custom_minimum_size = Vector2(350, 36)
		label.add_theme_font_size_override("font_size", 12)
		label.text = str(slot["name"]) + "\n"
		if bool(info.get("valid", false)):
			label.text += "Day %d · %s · %d gold%s" % [int(info["day"]), str(info["location"]), int(info["gold"]), " (backup)" if info["backup"] else ""]
		else:
			label.text += "Unavailable" if info.get("exists", false) else "Empty"
		row.add_child(label)
		var button: Button = MenuLayout.button(row, "Save" if mode == "save" else "Load", _activate.bind(path))
		button.custom_minimum_size.x = 100
		button.disabled = mode == "load" and not bool(info.get("valid", false))
		rows.add_child(row)


func _activate(path: String) -> void:
	if mode == "save":
		status.text = "Game saved." if SaveManager.save_to_path(path) else "Save failed."
		_refresh()
	elif SaveManager.load_slot(path):
		loaded.emit()
	else:
		status.text = "This save could not be loaded."
