extends CanvasLayer

@onready var gold_label: Label = $Window/GoldLabel
@onready var upgrade_list: VBoxContainer = $Window/UpgradeList
@onready var status_label: Label = $Window/StatusLabel
@onready var close_button: Button = $Window/CloseButton

var _menu_count: int = 0


func _ready() -> void:
	visible = false
	EventBus.upgrade_requested.connect(_on_upgrade_requested)
	EventBus.upgrades_changed.connect(_refresh)
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
	for child in upgrade_list.get_children():
		upgrade_list.remove_child(child)
		child.queue_free()
	for line_variant in GameData.upgrades:
		var line: String = str(line_variant)
		upgrade_list.add_child(_make_upgrade_row(line))


func _make_upgrade_row(line: String) -> HBoxContainer:
	var row: HBoxContainer = HBoxContainer.new()
	row.set_meta("line", line)
	var current_effect: int = GameState.get_upgrade_effect(line)
	var next_upgrade: Dictionary = GameState.get_next_upgrade(line)

	var description: Label = Label.new()
	description.custom_minimum_size = Vector2(300, 42)
	if next_upgrade.is_empty():
		description.text = "%s\n%s" % [line.capitalize(), _effect_text(line, current_effect)]
	else:
		description.text = "%s\n%s -> %d" % [
			line.capitalize(), _effect_text(line, current_effect), int(next_upgrade.get("effect", 0))
		]
	row.add_child(description)

	var button: Button = Button.new()
	if next_upgrade.is_empty():
		button.text = "MAX"
		button.disabled = true
	else:
		button.text = "Buy %dg" % int(next_upgrade.get("cost", 0))
		button.disabled = not GameState.can_purchase_upgrade(line)
		button.pressed.connect(_on_buy_pressed.bind(line))
	row.add_child(button)
	return row


func _effect_text(line: String, effect: int) -> String:
	if line == "bag":
		return "Capacity %d" % effect
	if line == "lantern":
		return "Cave depth %d" % effect
	if line == "cauldron":
		return "Recipe tier %d" % effect
	return "Level %d" % effect


func _on_upgrade_requested() -> void:
	_set_open(true)


func _on_buy_pressed(line: String) -> void:
	var next_upgrade: Dictionary = GameState.get_next_upgrade(line)
	if GameState.purchase_upgrade(line):
		status_label.text = "%s upgraded to level %d" % [
			line.capitalize(), int(next_upgrade.get("effect", 0))
		]
	else:
		status_label.text = "Not enough gold"
	_refresh()


func _on_gold_changed(_total_gold: int) -> void:
	_refresh()


func _on_close_pressed() -> void:
	_set_open(false)


func _on_menu_opened() -> void:
	_menu_count += 1


func _on_menu_closed() -> void:
	_menu_count = max(0, _menu_count - 1)
