class_name WorldMapCanvas
extends Control
## Schematic world routes or a pixel overview of the current location.

signal location_selected(id: String)

@export var global_view: bool = false
var selected_id: String = ""
var _texture: Texture2D
var _definition: Dictionary = {}


func _ready() -> void:
	texture_filter = CanvasItem.TEXTURE_FILTER_NEAREST
	EventBus.location_changed.connect(_on_location_changed)
	EventBus.player_position_changed.connect(_on_position_changed)
	EventBus.upgrades_changed.connect(queue_redraw)
	EventBus.cave_progress_changed.connect(queue_redraw)
	_on_location_changed(GameState.current_map_id)


func _on_location_changed(id: String) -> void:
	_definition = GameData.maps.get("locations", {}).get(id, {})
	var path: String = str(_definition.get("overview", ""))
	_texture = load(path) as Texture2D if not path.is_empty() else null
	queue_redraw()


func _on_position_changed(_position: Vector2) -> void:
	if not global_view:
		queue_redraw()


func _draw() -> void:
	if global_view:
		_draw_world()
	else:
		_draw_local()


func _draw_local() -> void:
	draw_rect(Rect2(Vector2.ZERO, size), Color("202631"))
	var dimensions: Array = _definition.get("size", [])
	if _texture == null or dimensions.size() != 2:
		return
	var world_size: Vector2 = Vector2(float(dimensions[0]), float(dimensions[1]))
	var scale_value: float = minf((size.x - 8) / world_size.x, (size.y - 8) / world_size.y)
	var map_size: Vector2 = world_size * scale_value
	var origin: Vector2 = (size - map_size) * 0.5
	var bounds: Rect2 = Rect2(origin, map_size)
	draw_texture_rect(_texture, bounds, false)
	draw_rect(bounds, Color("829d91"), false)
	for value: Variant in _definition.get("markers", []):
		var marker: Dictionary = value
		var point: Array = marker["position"]
		var position_value: Vector2 = origin + Vector2(float(point[0]), float(point[1])) * scale_value
		var kind: String = str(marker.get("kind", "exit"))
		if kind == "pending":
			var extent: Array = marker.get("size", [112, 80])
			var rectangle: Vector2 = Vector2(float(extent[0]), float(extent[1])) * scale_value
			draw_rect(Rect2(position_value - rectangle * 0.5, rectangle), Color("bba0d1"), false)
		elif kind == "ladder":
			if GameState.has_cave_ladder(str(_definition.get("cave_id", "")), int(_definition.get("depth", 0))):
				draw_rect(Rect2(position_value - Vector2.ONE * 2, Vector2.ONE * 4), Color("e8ad62"))
		else:
			draw_circle(position_value, 2.0, Color("b9dfac") if kind == "exit" else Color("d5b5dd"))
	_draw_found_hole(origin, scale_value)
	var player: Vector2 = origin + GameState.map_player_position.clamp(Vector2.ZERO, world_size) * scale_value
	draw_circle(player, 3, Color("28253d"))
	draw_circle(player, 2, Color("fff0cf"))


func _draw_found_hole(origin: Vector2, scale_value: float) -> void:
	var cave_id: String = str(_definition.get("cave_id", ""))
	var depth: int = int(_definition.get("depth", 0))
	if cave_id.is_empty() or not GameState.is_cave_hole_found(cave_id, depth):
		return
	var progress: Dictionary = GameState.cave_progress.get(cave_id, {})
	var marker_name: String = str(progress.get("hole_positions", {}).get(str(depth), ""))
	var points: Dictionary = _definition.get("hole_positions", {})
	if points.has(marker_name):
		var point: Array = points[marker_name]
		draw_circle(origin + Vector2(float(point[0]), float(point[1])) * scale_value, 2, Color("e9a5c1"))


func _world_point(definition: Dictionary) -> Vector2:
	var point: Array = definition["world_position"]
	return Vector2(float(point[0]), float(point[1])) * (size - Vector2(24, 40)) + Vector2(12, 10)


func _draw_world() -> void:
	draw_rect(Rect2(Vector2.ZERO, size), Color("202631"))
	var locations: Dictionary = GameData.maps.get("locations", {})
	var font: Font = ThemeDB.fallback_font
	for value: Variant in GameData.maps.get("connections", []):
		var edge: Array = value
		if locations.has(edge[0]) and locations.has(edge[1]):
			draw_line(_world_point(locations[edge[0]]), _world_point(locations[edge[1]]), Color("718d82"), 2)
	var current: Dictionary = locations.get(GameState.current_map_id, {})
	var current_world_id: String = str(current.get("world_parent", GameState.current_map_id))
	for key: Variant in locations:
		var definition: Dictionary = locations[key]
		if not definition.has("world_position"):
			continue
		var point: Vector2 = _world_point(definition)
		var locked: bool = GameState.get_lantern_level() < int(definition.get("required_lantern", 0))
		var color: Color = Color("665b75") if locked else Color("70b698")
		if str(key) == selected_id:
			draw_circle(point, 11, Color("d5b5dd"), false, 1)
		draw_circle(point, 7, color)
		if str(key) == current_world_id:
			draw_circle(point - Vector2(0, 12), 3, Color("fff0cf"))
		var title: String = str(definition["name"])
		if definition.has("depth"):
			title = "%d. %s" % [int(definition["depth"]), title]
		var offset: Vector2 = Vector2(-64, 20)
		if definition.has("depth"):
			offset = Vector2(-128, 4)
			draw_string(font, point + Vector2(12, 4), "L%d" % int(definition["required_lantern"]), HORIZONTAL_ALIGNMENT_LEFT, 32, 10, Color("e8ad62"))
		draw_string(font, point + offset, title, HORIZONTAL_ALIGNMENT_CENTER, 138, 11, Color("b6b2bc") if locked else Color("fff0cf"))


func _gui_input(event: InputEvent) -> void:
	if not global_view or not event is InputEventMouseButton:
		return
	var mouse: InputEventMouseButton = event
	if mouse.button_index != MOUSE_BUTTON_LEFT or not mouse.pressed:
		return
	var locations: Dictionary = GameData.maps.get("locations", {})
	for key: Variant in locations:
		var definition: Dictionary = locations[key]
		if definition.has("world_position") and mouse.position.distance_to(_world_point(definition)) <= 14:
			selected_id = str(key)
			location_selected.emit(selected_id)
			queue_redraw()
			accept_event()
			return
