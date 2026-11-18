extends Area2D

@export var item_id: String = ""
@export var spawn_id: String = ""

@onready var sprite: AnimatedSprite2D = $Body


func _ready() -> void:
	if item_id == "":
		queue_free()
		return

	var animations: Dictionary = GameData.visuals.get("plants", {})
	var path: String = str(animations.get(item_id, ""))
	if not path.is_empty() and ResourceLoader.exists(path):
		sprite.sprite_frames = load(path) as SpriteFrames
		sprite.play("idle")
	else:
		var item: Dictionary = GameData.get_item(item_id)
		var icon_path: String = str(item.get("icon", "res://icon.svg"))
		var frames: SpriteFrames = SpriteFrames.new()
		frames.add_frame("default", load(icon_path) as Texture2D)
		sprite.sprite_frames = frames
	body_entered.connect(_on_body_entered)


func _on_body_entered(body: Node2D) -> void:
	if not body.is_in_group("player"):
		return

	if GameState.add_item(item_id, 1):
		if spawn_id != "":
			EventBus.plant_collected.emit(spawn_id, item_id)
		queue_free()
