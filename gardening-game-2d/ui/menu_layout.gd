class_name MenuLayout
extends RefCounted


static func background(parent: Control) -> void:
	var texture: TextureRect = TextureRect.new()
	texture.texture = load("res://assets/menu/background.png") as Texture2D
	texture.expand_mode = TextureRect.EXPAND_IGNORE_SIZE
	texture.stretch_mode = TextureRect.STRETCH_KEEP_ASPECT_COVERED
	texture.mouse_filter = Control.MOUSE_FILTER_IGNORE
	texture.texture_filter = CanvasItem.TEXTURE_FILTER_NEAREST
	parent.add_child(texture)
	texture.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	var dimmer: ColorRect = ColorRect.new()
	dimmer.color = Color(0.08, 0.07, 0.13, 0.58)
	dimmer.mouse_filter = Control.MOUSE_FILTER_IGNORE
	parent.add_child(dimmer)
	dimmer.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)


static func center(control: Control, dimensions: Vector2) -> void:
	control.set_anchors_preset(Control.PRESET_CENTER)
	control.offset_left = -dimensions.x * 0.5
	control.offset_top = -dimensions.y * 0.5
	control.offset_right = dimensions.x * 0.5
	control.offset_bottom = dimensions.y * 0.5


static func content(panel: Control, title: String) -> VBoxContainer:
	var margins: MarginContainer = MarginContainer.new()
	margins.name = "Margins"
	for side: String in ["left", "top", "right", "bottom"]:
		margins.add_theme_constant_override("margin_" + side, 12)
	panel.add_child(margins)
	var column: VBoxContainer = VBoxContainer.new()
	column.name = "Content"
	column.add_theme_constant_override("separation", 4)
	margins.add_child(column)
	var label: Label = Label.new()
	label.text = title
	label.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	label.add_theme_font_size_override("font_size", 20)
	column.add_child(label)
	return column


static func button(parent: Node, title: String, callback: Callable) -> Button:
	var control: Button = Button.new()
	control.text = title
	control.custom_minimum_size.y = 28
	control.pressed.connect(callback)
	parent.add_child(control)
	return control
