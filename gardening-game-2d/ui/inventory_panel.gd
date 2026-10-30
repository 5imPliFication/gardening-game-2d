extends CanvasLayer

@onready var item_list: VBoxContainer = $Window/ItemList
@onready var capacity_label: Label = $Window/CapacityLabel

var _menu_count: int = 0


func _ready() -> void:
	visible = false
	EventBus.inventory_changed.connect(_refresh)
	EventBus.menu_opened.connect(_on_menu_opened)
	EventBus.menu_closed.connect(_on_menu_closed)
	_refresh()


func _unhandled_input(event: InputEvent) -> void:
	if event.is_action_pressed("open_inventory"):
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


func _on_menu_opened() -> void:
	_menu_count += 1


func _on_menu_closed() -> void:
	_menu_count = max(0, _menu_count - 1)


func _refresh() -> void:
	capacity_label.text = "Bag: %d / %d" % [
		GameState.get_total_item_count(), GameState.get_bag_capacity()
	]

	for child in item_list.get_children():
		item_list.remove_child(child)
		child.queue_free()

	if GameState.inventory.is_empty():
		var empty_label: Label = Label.new()
		empty_label.text = "Empty"
		item_list.add_child(empty_label)
		return

	for id_variant in GameState.inventory:
		var item_id: String = str(id_variant)
		var item: Dictionary = GameData.get_item(item_id)
		item_list.add_child(_make_row(item_id, item))


func _make_row(item_id: String, item: Dictionary) -> HBoxContainer:
	var row: HBoxContainer = HBoxContainer.new()

	var icon: TextureRect = TextureRect.new()
	icon.custom_minimum_size = Vector2(16, 16)
	icon.expand_mode = TextureRect.EXPAND_IGNORE_SIZE
	icon.stretch_mode = TextureRect.STRETCH_KEEP_ASPECT_CENTERED
	icon.texture = _load_icon(item)
	row.add_child(icon)

	var label: Label = Label.new()
	label.text = "%s x%d" % [
		str(item.get("name", item_id)), GameState.get_item_count(item_id)
	]
	row.add_child(label)
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
