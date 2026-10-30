extends CanvasLayer

@onready var progress_label: Label = $Window/ProgressLabel
@onready var entry_list: VBoxContainer = $Window/EntryScroll/EntryList
@onready var close_button: Button = $Window/CloseButton

var _menu_count: int = 0


func _ready() -> void:
	visible = false
	EventBus.botanary_changed.connect(_refresh)
	EventBus.menu_opened.connect(_on_menu_opened)
	EventBus.menu_closed.connect(_on_menu_closed)
	close_button.pressed.connect(_on_close_pressed)
	_refresh()


func _unhandled_input(event: InputEvent) -> void:
	if event.is_action_pressed("open_botanary"):
		if visible:
			_set_open(false)
			get_viewport().set_input_as_handled()
		elif _menu_count == 0:
			_set_open(true)
			get_viewport().set_input_as_handled()
	elif visible and event.is_action_pressed("cancel"):
		_set_open(false)
		get_viewport().set_input_as_handled()


func _set_open(should_open: bool) -> void:
	if visible == should_open:
		return
	if should_open and _menu_count > 0:
		return
	visible = should_open
	if should_open:
		_refresh()
		EventBus.menu_opened.emit()
	else:
		EventBus.menu_closed.emit()


func _exit_tree() -> void:
	if visible:
		EventBus.menu_closed.emit()


func _refresh() -> void:
	for child in entry_list.get_children():
		entry_list.remove_child(child)
		child.queue_free()

	var total: int = 0
	var discovered: int = 0
	for id_variant in GameData.items:
		var item_id: String = str(id_variant)
		var item: Dictionary = GameData.get_item(item_id)
		if not bool(item.get("botanary", false)):
			continue
		total += 1
		var is_discovered: bool = bool(GameState.discovered_plants.get(item_id, false))
		if is_discovered:
			discovered += 1
		entry_list.add_child(_make_entry(item_id, item, is_discovered))
	progress_label.text = "Discovered: %d / %d" % [discovered, total]


func _make_entry(item_id: String, item: Dictionary, is_discovered: bool) -> HBoxContainer:
	var row: HBoxContainer = HBoxContainer.new()
	row.custom_minimum_size = Vector2(0, 58)
	row.set_meta("item_id", item_id)
	row.set_meta("discovered", is_discovered)

	if is_discovered:
		var icon: TextureRect = TextureRect.new()
		icon.custom_minimum_size = Vector2(48, 48)
		icon.expand_mode = TextureRect.EXPAND_IGNORE_SIZE
		icon.stretch_mode = TextureRect.STRETCH_KEEP_ASPECT_CENTERED
		icon.texture = _load_icon(item)
		row.add_child(icon)
	else:
		var silhouette: ColorRect = ColorRect.new()
		silhouette.custom_minimum_size = Vector2(48, 48)
		silhouette.color = Color(0.03, 0.03, 0.04, 1)
		silhouette.mouse_filter = Control.MOUSE_FILTER_IGNORE
		row.add_child(silhouette)

	var text: VBoxContainer = VBoxContainer.new()
	text.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	var name_label: Label = Label.new()
	name_label.text = str(item.get("name", item_id)) if is_discovered else "????"
	text.add_child(name_label)
	var detail_label: Label = Label.new()
	if is_discovered:
		var lore: String = str(item.get("lore", ""))
		detail_label.text = lore if lore != "" else "No lore recorded yet."
	else:
		detail_label.text = str(item.get("hint", "No hint available."))
	text.add_child(detail_label)
	row.add_child(text)
	return row


func _load_icon(item: Dictionary) -> Texture2D:
	var icon_path: String = str(item.get("icon", ""))
	if icon_path != "" and ResourceLoader.exists(icon_path):
		var resource: Resource = load(icon_path)
		if resource is Texture2D:
			var texture: Texture2D = resource
			return texture
	var fallback: Texture2D = load("res://icon.svg")
	return fallback


func _on_close_pressed() -> void:
	_set_open(false)


func _on_menu_opened() -> void:
	_menu_count += 1


func _on_menu_closed() -> void:
	_menu_count = max(0, _menu_count - 1)
