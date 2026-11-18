extends "res://scripts/scene_exit.gd"
## A marked construction plot or a route sign, with optional temporary interior.

@export var title: String = "Pending structure"
@export var pending_structure: bool = true


func _ready() -> void:
	var body: Sprite2D = $Body
	var label: Label = $Title
	if pending_structure:
		body.texture = load("res://assets/props/pending_structure.png") as Texture2D
		body.scale = Vector2(3, 2)
		body.z_index = -2
		label.text = title + "\nPending structure"
	else:
		body.texture = load("res://assets/props/route_sign.png") as Texture2D
		body.scale = Vector2(2, 2)
		body.position.y = -26
		label.text = title
	super._ready()
	prompt.text = "Pending structure" if target_scene.is_empty() else "E: " + title
