extends Control


func _ready() -> void:
	GameClock.is_running = false
	UserSettings.load_and_apply()
	theme = load("res://ui/menu_theme.tres") as Theme
	MenuLayout.background(self)
	var column: VBoxContainer = VBoxContainer.new()
	column.add_theme_constant_override("separation", 14)
	add_child(column)
	MenuLayout.center(column, Vector2(430, 220))
	var title: Label = Label.new()
	title.text = "POTION FORAGER"
	title.add_theme_font_size_override("font_size", 32)
	title.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	column.add_child(title)
	var subtitle: Label = Label.new()
	subtitle.text = "Gather a little magic."
	subtitle.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	column.add_child(subtitle)
	var spacer: Control = Control.new()
	spacer.custom_minimum_size.y = 24
	column.add_child(spacer)
	var begin: Button = MenuLayout.button(column, "Begin", _begin)
	begin.custom_minimum_size.y = 38
	begin.grab_focus()
	var hint: Label = Label.new()
	hint.text = "Enter / Space or click to begin"
	hint.add_theme_font_size_override("font_size", 12)
	hint.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	column.add_child(hint)


func _begin() -> void:
	get_tree().change_scene_to_file("res://ui/main_menu.tscn")
