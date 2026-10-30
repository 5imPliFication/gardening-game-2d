extends CanvasLayer

@onready var gold_label: Label = $Window/GoldLabel
@onready var rate_label: Label = $Window/RateLabel
@onready var item_list: VBoxContainer = $Window/ItemScroll/ItemList
@onready var status_label: Label = $Window/StatusLabel
@onready var close_button: Button = $Window/CloseButton

var _menu_count: int = 0


func _ready() -> void:
	visible = false
	EventBus.sell_bin_requested.connect(_on_sell_bin_requested)
	EventBus.inventory_changed.connect(_refresh)
	EventBus.gold_changed.connect(_on_gold_changed)
	EventBus.menu_opened.connect(_on_menu_opened)
	EventBus.menu_closed.connect(_on_menu_closed)
	close_button.pressed.connect(_on_close_pressed)
	_refresh()


func _unhandled_input(event: InputEvent) -> void:
	if visible and event.is_action_pressed("cancel"):
		_set_open(false)
		get_viewport().set_input_as_handled()


func _set_open(should_open: bool) -> void:
	if visible == should_open:
		return
	if should_open and _menu_count > 0:
		return

	visible = should_open
	if should_open:
		status_label.text = ""
		_refresh()
		EventBus.menu_opened.emit()
	else:
		EventBus.menu_closed.emit()


func _exit_tree() -> void:
	if visible:
		EventBus.menu_closed.emit()


func _refresh() -> void:
	gold_label.text = "Gold: %d" % GameState.gold
	var multiplier: float = float(GameData.customers.get("sell_bin_multiplier", 0.0))
	rate_label.text = "%d%% base value" % roundi(multiplier * 100.0)
	for child in item_list.get_children():
		item_list.remove_child(child)
		child.queue_free()

	var sellable_count: int = 0
	for id_variant in GameState.inventory:
		var item_id: String = str(id_variant)
		if GameState.get_sell_price(item_id) <= 0:
			continue
		item_list.add_child(_make_item_row(item_id))
		sellable_count += 1

	if sellable_count == 0:
		var empty_label: Label = Label.new()
		empty_label.text = "Nothing sellable"
		item_list.add_child(empty_label)


func _make_item_row(item_id: String) -> HBoxContainer:
	var row: HBoxContainer = HBoxContainer.new()
	var item: Dictionary = GameData.get_item(item_id)

	var description: Label = Label.new()
	description.custom_minimum_size = Vector2(250, 32)
	description.text = "%s x%d" % [
		str(item.get("name", item_id)), GameState.get_item_count(item_id)
	]
	row.add_child(description)

	var button: Button = Button.new()
	button.text = "Sell 1 (+%dg)" % GameState.get_sell_price(item_id)
	button.pressed.connect(_on_sell_pressed.bind(item_id))
	row.add_child(button)
	return row


func _on_sell_bin_requested() -> void:
	_set_open(true)


func _on_sell_pressed(item_id: String) -> void:
	var item: Dictionary = GameData.get_item(item_id)
	var item_name: String = str(item.get("name", item_id))
	var price: int = GameState.get_sell_price(item_id)
	if GameState.sell_item(item_id):
		status_label.text = "Sold %s for %dg" % [item_name, price]
	else:
		status_label.text = "Could not sell item"
	_refresh()


func _on_close_pressed() -> void:
	_set_open(false)


func _on_gold_changed(total_gold: int) -> void:
	gold_label.text = "Gold: %d" % total_gold


func _on_menu_opened() -> void:
	_menu_count += 1


func _on_menu_closed() -> void:
	_menu_count = max(0, _menu_count - 1)
