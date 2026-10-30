extends CanvasLayer

@onready var next_burst_label: Label = $Window/NextBurstLabel
@onready var customer_list: VBoxContainer = $Window/CustomerList
@onready var status_label: Label = $Window/StatusLabel
@onready var close_button: Button = $Window/CloseButton

var _menu_count: int = 0
var _seconds_until_burst: float = 0.0
var _next_customer_id: int = 0
var _customers: Array = []
var _customer_item_ids: Array[String] = []
var _rng: RandomNumberGenerator = RandomNumberGenerator.new()


func _ready() -> void:
	visible = false
	_rng.randomize()
	_build_customer_item_ids()
	EventBus.shop_requested.connect(_on_shop_requested)
	EventBus.inventory_changed.connect(_refresh)
	EventBus.midnight_reached.connect(_on_midnight_reached)
	EventBus.menu_opened.connect(_on_menu_opened)
	EventBus.menu_closed.connect(_on_menu_closed)
	close_button.pressed.connect(_on_close_pressed)
	_refresh()


func _process(delta: float) -> void:
	if not visible:
		return

	_seconds_until_burst -= delta
	if _seconds_until_burst <= 0.0:
		_spawn_burst()
		_schedule_next_burst()
	next_burst_label.text = "Next burst: %ds" % ceili(_seconds_until_burst)


func _unhandled_input(event: InputEvent) -> void:
	if visible and event.is_action_pressed("cancel"):
		_set_open(false)
		get_viewport().set_input_as_handled()


func _set_open(should_open: bool) -> void:
	if visible == should_open:
		return
	if should_open and (_menu_count > 0 or GameClock.current_phase_name() == "Midnight"):
		return

	visible = should_open
	if should_open:
		status_label.text = "Shop open - the clock is running"
		_spawn_burst()
		_schedule_next_burst()
		EventBus.menu_opened.emit()
		EventBus.shop_opened.emit()
	else:
		_customers.clear()
		_refresh()
		EventBus.shop_closed.emit()
		EventBus.menu_closed.emit()


func _exit_tree() -> void:
	if visible:
		EventBus.shop_closed.emit()
		EventBus.menu_closed.emit()


func _build_customer_item_ids() -> void:
	_customer_item_ids.clear()
	for id_variant in GameData.items:
		var item_id: String = str(id_variant)
		var item: Dictionary = GameData.get_item(item_id)
		if str(item.get("type", "")) == "potion" and int(item.get("base_price", 0)) > 0:
			_customer_item_ids.append(item_id)


func _spawn_burst() -> void:
	_customers.clear()
	var min_customers: int = int(GameData.customers.get("min_customers", 0))
	var max_customers: int = int(GameData.customers.get("max_customers", 0))
	var min_multiplier: float = float(GameData.customers.get("price_multiplier_min", 0.0))
	var max_multiplier: float = float(GameData.customers.get("price_multiplier_max", 0.0))
	if _customer_item_ids.is_empty() or min_customers <= 0 or max_customers < min_customers:
		_refresh()
		return
	if min_multiplier <= 0.0 or max_multiplier < min_multiplier:
		_refresh()
		return

	var customer_count: int = _rng.randi_range(min_customers, max_customers)
	for _index in customer_count:
		var item_id: String = _customer_item_ids[_rng.randi_range(0, _customer_item_ids.size() - 1)]
		var item: Dictionary = GameData.get_item(item_id)
		var base_price: int = int(item.get("base_price", 0))
		var minimum_payment: int = ceili(base_price * min_multiplier)
		var maximum_payment: int = floori(base_price * max_multiplier)
		_customers.append({
			"id": _next_customer_id,
			"item": item_id,
			"payment": _rng.randi_range(minimum_payment, maximum_payment),
		})
		_next_customer_id += 1

	status_label.text = "A new customer burst arrived"
	_refresh()


func _schedule_next_burst() -> void:
	var minimum: float = float(GameData.customers.get("burst_min_seconds", 0.0))
	var maximum: float = float(GameData.customers.get("burst_max_seconds", 0.0))
	if minimum <= 0.0 or maximum < minimum:
		_seconds_until_burst = INF
		return
	_seconds_until_burst = _rng.randf_range(minimum, maximum)


func _refresh() -> void:
	for child in customer_list.get_children():
		customer_list.remove_child(child)
		child.queue_free()

	if _customers.is_empty():
		var empty_label: Label = Label.new()
		empty_label.text = "No customers waiting"
		customer_list.add_child(empty_label)
		return

	for customer_variant in _customers:
		var customer: Dictionary = customer_variant
		customer_list.add_child(_make_customer_row(customer))


func _make_customer_row(customer: Dictionary) -> HBoxContainer:
	var row: HBoxContainer = HBoxContainer.new()
	var item_id: String = str(customer.get("item", ""))
	var item: Dictionary = GameData.get_item(item_id)

	var request: Label = Label.new()
	request.custom_minimum_size = Vector2(330, 32)
	request.text = "Wants %s - pays %dg" % [
		str(item.get("name", item_id)), int(customer.get("payment", 0))
	]
	row.add_child(request)

	var button: Button = Button.new()
	button.text = "Serve"
	button.disabled = GameState.get_item_count(item_id) <= 0
	button.pressed.connect(_on_serve_pressed.bind(int(customer.get("id", -1))))
	row.add_child(button)
	return row


func _on_shop_requested() -> void:
	_set_open(true)


func _on_serve_pressed(customer_id: int) -> void:
	for index in _customers.size():
		var customer: Dictionary = _customers[index]
		if int(customer.get("id", -1)) != customer_id:
			continue

		var item_id: String = str(customer.get("item", ""))
		var payment: int = int(customer.get("payment", 0))
		if GameState.sell_to_customer(item_id, payment):
			var item: Dictionary = GameData.get_item(item_id)
			status_label.text = "Served %s for %dg" % [str(item.get("name", item_id)), payment]
			_customers.remove_at(index)
		else:
			status_label.text = "You do not have that item"
		_refresh()
		return


func _on_close_pressed() -> void:
	_set_open(false)


func _on_midnight_reached() -> void:
	if visible:
		_set_open(false)


func _on_menu_opened() -> void:
	_menu_count += 1


func _on_menu_closed() -> void:
	_menu_count = max(0, _menu_count - 1)
