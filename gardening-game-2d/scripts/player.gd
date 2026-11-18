extends CharacterBody2D

@onready var speed: float = Config.PLAYER_SPEED
@onready var visual: PlayerVisual = $Body
@onready var camera: Camera2D = $Camera2D

@export_enum("forest", "home", "clinic", "cave") var world_art: String = "forest"

var _menu_count: int = 0


func _ready() -> void:
	EventBus.menu_opened.connect(_on_menu_opened)
	EventBus.menu_closed.connect(_on_menu_closed)
	EventBus.location_changed.connect(_on_location_changed)
	EventBus.player_spawn_requested.connect(_on_spawn_requested)
	var bounds: Array = GameData.visuals.get("world_bounds", {}).get(world_art, [])
	if bounds.size() == 2:
		camera.limit_left = 0
		camera.limit_top = 0
		camera.limit_right = int(bounds[0])
		camera.limit_bottom = int(bounds[1])
	_publish_position()


func _physics_process(_delta: float) -> void:
	if not GameState.map_player_position.is_equal_approx(global_position):
		_publish_position()
	if _menu_count > 0:
		velocity = Vector2.ZERO
		move_and_slide()
		visual.update_motion(Vector2.ZERO, Vector2.ZERO)
		return

	var direction: Vector2 = Input.get_vector("move_left", "move_right", "move_up", "move_down")
	velocity = direction * speed
	move_and_slide()
	visual.update_motion(direction, get_position_delta())
	if not GameState.map_player_position.is_equal_approx(global_position):
		_publish_position()


func _on_location_changed(id: String) -> void:
	var definition: Dictionary = GameData.maps.get("locations", {}).get(id, {})
	var bounds: Array = definition.get("size", [])
	if bounds.size() == 2:
		camera.limit_right = int(bounds[0])
		camera.limit_bottom = int(bounds[1])
	_publish_position()


func _on_spawn_requested(position_value: Vector2) -> void:
	global_position = position_value
	camera.reset_smoothing()
	_publish_position()


func _publish_position() -> void:
	GameState.map_player_position = global_position
	EventBus.player_position_changed.emit(global_position)


func _on_menu_opened() -> void:
	_menu_count += 1


func _on_menu_closed() -> void:
	_menu_count = max(0, _menu_count - 1)
