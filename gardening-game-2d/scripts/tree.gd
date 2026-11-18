extends StaticBody2D

@export_enum("witchwood", "moon_pine", "lavender_willow", "silver_birch") var variant: String = "witchwood"

@onready var sprite: AnimatedSprite2D = $Body


func _ready() -> void:
	var variants: Dictionary = GameData.visuals.get("trees", {})
	var path: String = str(variants.get(variant, ""))
	if not path.is_empty() and ResourceLoader.exists(path):
		sprite.sprite_frames = load(path) as SpriteFrames
		sprite.play("idle")
