extends CanvasLayer

@onready var message_label: Label = $Window/MessageLabel
@onready var continue_button: Button = $Window/ContinueButton


func _ready() -> void:
	visible = true
	continue_button.pressed.connect(_close)
	_refresh_message()
	EventBus.menu_opened.emit()


func _unhandled_input(event: InputEvent) -> void:
	if visible and event.is_action_pressed("cancel"):
		_close()
		get_viewport().set_input_as_handled()


func _exit_tree() -> void:
	if visible:
		EventBus.menu_closed.emit()


func _refresh_message() -> void:
	var recovery: Dictionary = GameState.last_recovery
	if str(recovery.get("reason", "")) != "pass_out":
		message_label.text = "A new morning begins."
		return

	var lost_names: PackedStringArray = []
	var lost_items: Dictionary = recovery.get("lost_items", {})
	for id_variant in lost_items:
		var item_id: String = str(id_variant)
		var item: Dictionary = GameData.get_item(item_id)
		lost_names.append("%s x%d" % [
			str(item.get("name", item_id)), int(lost_items[id_variant])
		])
	var lost_text: String = "Nothing" if lost_names.is_empty() else ", ".join(lost_names)
	message_label.text = "You passed out and woke in the Clinic.\nLost: %s\nClinic fee: %dg" % [
		lost_text, int(recovery.get("fine", 0))
	]
	if GameState.last_save_failed:
		message_label.text += "\nWarning: automatic save failed."
		GameState.last_save_failed = false


func _close() -> void:
	if not visible:
		return
	visible = false
	EventBus.menu_closed.emit()
