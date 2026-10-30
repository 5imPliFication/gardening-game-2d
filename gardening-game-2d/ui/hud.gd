extends CanvasLayer

@onready var day_label: Label = $DayLabel
@onready var phase_label: Label = $PhaseLabel
@onready var time_label: Label = $TimeLabel
@onready var gold_label: Label = $GoldLabel
@onready var warning_label: Label = $WarningLabel
@onready var message_label: Label = $MessageLabel
@onready var tint: ColorRect = $Tint

var _message_seconds: float = 0.0


func _ready() -> void:
	EventBus.day_started.connect(_on_day_started)
	EventBus.phase_changed.connect(_on_phase_changed)
	EventBus.time_warning.connect(_on_time_warning)
	EventBus.midnight_reached.connect(_on_midnight_reached)
	EventBus.item_collected.connect(_on_item_collected)
	EventBus.inventory_full.connect(_on_inventory_full)
	EventBus.item_crafted.connect(_on_item_crafted)
	EventBus.item_sold.connect(_on_item_sold)
	EventBus.gold_changed.connect(_on_gold_changed)
	EventBus.message_requested.connect(_show_message)
	_update_labels()
	if GameState.last_save_failed:
		_show_message("Warning: automatic save failed.")
		if GameState.resume_location != "clinic":
			GameState.last_save_failed = false


func _process(delta: float) -> void:
	_update_labels()
	_update_tint()
	_update_message(delta)


func _update_labels() -> void:
	day_label.text = "Day %d" % GameClock.day
	phase_label.text = GameClock.current_phase_name()
	gold_label.text = "Gold: %d" % GameState.gold

	var total_seconds: float = GameClock.phase_index * Config.PHASE_SECONDS
	total_seconds += GameClock.seconds_into_phase
	var elapsed: int = int(total_seconds)
	var minutes: int = elapsed / 60
	var seconds: int = elapsed % 60
	time_label.text = "%02d:%02d" % [minutes, seconds]


func _update_tint() -> void:
	if GameClock.current_phase_name() != "Evening":
		tint.modulate.a = 0.0
		return

	var seconds_left: float = Config.PHASE_SECONDS - GameClock.seconds_into_phase
	var t: float = clampf(1.0 - (seconds_left / 60.0), 0.0, 1.0)
	tint.modulate.a = t * 0.4


func _update_message(delta: float) -> void:
	if _message_seconds <= 0.0:
		return

	_message_seconds -= delta
	if _message_seconds <= 0.0:
		message_label.visible = false


func _show_message(text: String) -> void:
	message_label.text = text
	message_label.visible = true
	_message_seconds = 2.0


func _on_day_started(day: int) -> void:
	day_label.text = "Day %d" % day


func _on_phase_changed(phase: String) -> void:
	phase_label.text = phase
	warning_label.visible = false


func _on_time_warning(seconds_left: int) -> void:
	warning_label.text = "Midnight in %d seconds!" % seconds_left
	warning_label.visible = true


func _on_midnight_reached() -> void:
	warning_label.text = "MIDNIGHT"
	warning_label.visible = true


func _on_item_collected(item_id: String, count: int) -> void:
	var item: Dictionary = GameData.get_item(item_id)
	var item_name: String = str(item.get("name", item_id))
	_show_message("Picked up %s x%d" % [item_name, count])


func _on_inventory_full(item_id: String) -> void:
	var item: Dictionary = GameData.get_item(item_id)
	var item_name: String = str(item.get("name", item_id))
	_show_message("Bag full: no room for %s" % item_name)


func _on_item_crafted(_recipe_id: String, item_id: String, count: int) -> void:
	var item: Dictionary = GameData.get_item(item_id)
	var item_name: String = str(item.get("name", item_id))
	_show_message("Crafted %s x%d" % [item_name, count])


func _on_item_sold(item_id: String, count: int, gold_earned: int) -> void:
	var item: Dictionary = GameData.get_item(item_id)
	var item_name: String = str(item.get("name", item_id))
	_show_message("Sold %s x%d for %dg" % [item_name, count, gold_earned])


func _on_gold_changed(total_gold: int) -> void:
	gold_label.text = "Gold: %d" % total_gold
