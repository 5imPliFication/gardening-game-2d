extends SceneTree
## Bake data-authored ground, props and boundaries into editable environment scenes.

const TILE_SET_PATH: String = "res://assets/tilesets/woodland/woodland_tileset.tres"
const OUTPUT: String = "res://assets/world/"


func _initialize() -> void:
	_build.call_deferred()


func _build() -> void:
	var layouts: Dictionary = JSON.parse_string(FileAccess.get_file_as_string("res://data/world_art.json"))
	var tiles: TileSet = load(TILE_SET_PATH) as TileSet
	DirAccess.make_dir_recursive_absolute(OUTPUT)
	for key: Variant in layouts:
		var layout: Dictionary = layouts[key]
		var scene_root: Node2D = Node2D.new()
		scene_root.name = str(key).capitalize() + "Environment"
		scene_root.y_sort_enabled = true
		scene_root.texture_filter = CanvasItem.TEXTURE_FILTER_NEAREST
		var layer_index: int = 0
		for value: Variant in layout["layers"]:
			var definition: Dictionary = value
			var layer: TileMapLayer = TileMapLayer.new()
			layer.name = "%02d_%s" % [layer_index, str(definition["material"]).capitalize()]
			layer.tile_set = tiles
			layer.z_index = -10 + layer_index
			if definition.has("tint"):
				layer.modulate = Color(str(definition["tint"]))
			scene_root.add_child(layer)
			layer.owner = scene_root
			for cell_value: Variant in definition["cells"]:
				var cell: Dictionary = cell_value
				layer.set_cell(_coords(cell["cell"]), 0, _coords(cell["atlas_coords"]))
			layer_index += 1
		for value: Variant in layout["trees"]:
			var definition: Dictionary = value
			var tree: Node2D = (load("res://scenes/tree.tscn") as PackedScene).instantiate()
			tree.position = Vector2(_coords(definition["position"]))
			tree.set("variant", str(definition["variant"]))
			tree.name = "Tree_" + str(definition["variant"])
			scene_root.add_child(tree, true)
			tree.owner = scene_root
		for value: Variant in layout["props"]:
			_add_prop(scene_root, tiles, value)
		var size: Vector2i = _coords(layout["size"])
		_add_solid(scene_root, "WestBoundary", Vector2(-16, size.y * 0.5), Vector2(32, size.y + 64))
		_add_solid(scene_root, "EastBoundary", Vector2(size.x + 16, size.y * 0.5), Vector2(32, size.y + 64))
		_add_solid(scene_root, "NorthBoundary", Vector2(size.x * 0.5, -16), Vector2(size.x, 32))
		_add_solid(scene_root, "SouthBoundary", Vector2(size.x * 0.5, size.y + 16), Vector2(size.x, 32))
		for value: Variant in layout["water"]:
			var cell: Vector2i = _coords(value)
			_add_solid(scene_root, "Water", Vector2(cell * tiles.tile_size) + Vector2(tiles.tile_size) * 0.5, Vector2(24, 24))
		var packed: PackedScene = PackedScene.new()
		var error: Error = packed.pack(scene_root)
		if error == OK:
			error = ResourceSaver.save(packed, OUTPUT + str(key) + "_environment.tscn")
		scene_root.free()
		if error != OK:
			push_error("Could not build environment %s: %s" % [str(key), error_string(error)])
			quit(1)
			return
	print("BUILT: %d editable gameplay environments, including distinct cave themes." % layouts.size())
	quit(0)


func _coords(value: Array) -> Vector2i:
	return Vector2i(int(value[0]), int(value[1]))


func _add_solid(scene_root: Node2D, node_name: String, position: Vector2, dimensions: Vector2) -> StaticBody2D:
	var body: StaticBody2D = StaticBody2D.new()
	body.name = node_name
	body.position = position
	scene_root.add_child(body, true)
	body.owner = scene_root
	var shape: CollisionShape2D = CollisionShape2D.new()
	var rectangle: RectangleShape2D = RectangleShape2D.new()
	rectangle.size = dimensions
	shape.shape = rectangle
	body.add_child(shape)
	shape.owner = scene_root
	return body


func _add_prop(scene_root: Node2D, tiles: TileSet, definition: Dictionary) -> void:
	var is_bed: bool = definition.has("texture")
	var body: StaticBody2D = _add_solid(scene_root, "Prop", Vector2(_coords(definition["position"])), Vector2(36, 40) if is_bed else Vector2(18, 8))
	var collision: CollisionShape2D = body.get_child(0) as CollisionShape2D
	collision.position.y = -22 if is_bed else -4
	var sprite: Sprite2D = Sprite2D.new()
	if is_bed:
		sprite.texture = load(str(definition["texture"])) as Texture2D
	else:
		var atlas: TileSetAtlasSource = tiles.get_source(0) as TileSetAtlasSource
		var texture: AtlasTexture = AtlasTexture.new()
		texture.atlas = atlas.texture
		texture.region = Rect2(Vector2(_coords(definition["atlas_coords"]) * tiles.tile_size), Vector2(tiles.tile_size))
		sprite.texture = texture
	var sprite_scale: float = float(definition.get("scale", 1))
	sprite.scale = Vector2.ONE * sprite_scale
	if definition.has("tint"):
		sprite.modulate = Color(str(definition["tint"]))
	sprite.position.y = -13 * sprite_scale
	body.add_child(sprite)
	sprite.owner = scene_root
