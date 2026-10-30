extends Node

var day: int = Config.START_DAY
var phase_index: int = 0
var seconds_into_phase: float = 0.0
var is_running: bool = true

var _warned_seconds: Array[int] = []
var _menu_pause_count: int = 0
var _shop_open: bool = false


func _ready() -> void:
	EventBus.menu_opened.connect(_on_menu_opened)
	EventBus.menu_closed.connect(_on_menu_closed)
	EventBus.shop_opened.connect(_on_shop_opened)
	EventBus.shop_closed.connect(_on_shop_closed)
	EventBus.day_started.emit(day)
	EventBus.phase_changed.emit(current_phase_name())


func _process(delta: float) -> void:
	if not is_running or (_menu_pause_count > 0 and not _shop_open):
		return

	seconds_into_phase += delta

	if seconds_into_phase >= Config.PHASE_SECONDS:
		seconds_into_phase -= Config.PHASE_SECONDS
		_advance_phase()

	_check_warnings()


func current_phase_name() -> String:
	return Config.PHASE_NAMES[phase_index]


func start_next_day() -> void:
	day += 1
	phase_index = 0
	seconds_into_phase = 0.0
	is_running = false
	_shop_open = false
	_menu_pause_count = 0
	_warned_seconds.clear()
	EventBus.day_started.emit(day)
	EventBus.phase_changed.emit(current_phase_name())


func restore_state(saved_day: int, saved_phase: int, saved_seconds: float) -> void:
	day = maxi(Config.START_DAY, saved_day)
	phase_index = clampi(saved_phase, 0, Config.PHASE_NAMES.size() - 1)
	seconds_into_phase = clampf(saved_seconds, 0.0, Config.PHASE_SECONDS)
	is_running = false
	_shop_open = false
	_menu_pause_count = 0
	_warned_seconds.clear()
	EventBus.day_started.emit(day)
	EventBus.phase_changed.emit(current_phase_name())


func _advance_phase() -> void:
	phase_index += 1

	if phase_index >= Config.PHASE_NAMES.size():
		phase_index = 0
		day += 1
		EventBus.day_started.emit(day)

	var phase_name: String = current_phase_name()
	EventBus.phase_changed.emit(phase_name)
	_warned_seconds.clear()

	if phase_name == "Midnight":
		EventBus.midnight_reached.emit()
		if not GameState.can_stay_up_past_midnight:
			is_running = false


func _check_warnings() -> void:
	if current_phase_name() != "Evening":
		return

	var seconds_left: float = Config.PHASE_SECONDS - seconds_into_phase

	for warning in Config.WARNING_SECONDS:
		if seconds_left <= float(warning) and not _warned_seconds.has(warning):
			EventBus.time_warning.emit(warning)
			_warned_seconds.append(warning)


func _on_menu_opened() -> void:
	_menu_pause_count += 1


func _on_menu_closed() -> void:
	_menu_pause_count = max(0, _menu_pause_count - 1)


func _on_shop_opened() -> void:
	_shop_open = true
	is_running = current_phase_name() != "Midnight"


func _on_shop_closed() -> void:
	_shop_open = false
	is_running = false
