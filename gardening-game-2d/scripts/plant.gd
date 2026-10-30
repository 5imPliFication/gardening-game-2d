extends Area2D

@export var item_id: String = ""
@export var spawn_id: String = ""

@onready var body_rect: ColorRect = $Body


func _ready() -> void:
	if item_id == "":
		queue_free()
		return

	body_rect.color = _placeholder_color()
	body_entered.connect(_on_body_entered)


func _on_body_entered(body: Node2D) -> void:
	if not body.is_in_group("player"):
		return

	if GameState.add_item(item_id, 1):
		if spawn_id != "":
			EventBus.plant_collected.emit(spawn_id, item_id)
		queue_free()


func _placeholder_color() -> Color:
	var hue: float = float(abs(item_id.hash()) % 360) / 360.0
	return Color.from_hsv(hue, 0.65, 0.95)
