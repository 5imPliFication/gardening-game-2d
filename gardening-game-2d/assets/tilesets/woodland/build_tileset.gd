extends SceneTree
## Offline art-resource builder. Run explicitly with --headless --script.

const DIRECTORY: String = "res://assets/tilesets/woodland/"
const PEERS: Array[Dictionary] = [
	{"bit": 1, "peer": TileSet.CELL_NEIGHBOR_TOP_SIDE},
	{"bit": 2, "peer": TileSet.CELL_NEIGHBOR_TOP_RIGHT_CORNER},
	{"bit": 4, "peer": TileSet.CELL_NEIGHBOR_RIGHT_SIDE},
	{"bit": 8, "peer": TileSet.CELL_NEIGHBOR_BOTTOM_RIGHT_CORNER},
	{"bit": 16, "peer": TileSet.CELL_NEIGHBOR_BOTTOM_SIDE},
	{"bit": 32, "peer": TileSet.CELL_NEIGHBOR_BOTTOM_LEFT_CORNER},
	{"bit": 64, "peer": TileSet.CELL_NEIGHBOR_LEFT_SIDE},
	{"bit": 128, "peer": TileSet.CELL_NEIGHBOR_TOP_LEFT_CORNER},
]


func _initialize() -> void:
	_build.call_deferred()


func _build() -> void:
	var parsed: Variant = JSON.parse_string(FileAccess.get_file_as_string(DIRECTORY + "terrain_manifest.json"))
	if not parsed is Dictionary:
		push_error("Could not load woodland terrain manifest.")
		quit(1)
		return
	var manifest: Dictionary = parsed
	var tile_size: int = int(manifest["tile_size"])
	var tile_set: TileSet = TileSet.new()
	tile_set.resource_name = "Witchwood — 32px Connected Terrains"
	tile_set.tile_size = Vector2i(tile_size, tile_size)
	var materials: Array = manifest["materials"]
	for index: int in range(materials.size()):
		var material: String = str(materials[index])
		tile_set.add_terrain_set()
		tile_set.set_terrain_set_mode(index, TileSet.TERRAIN_MODE_MATCH_CORNERS_AND_SIDES)
		tile_set.add_terrain(index)
		tile_set.set_terrain_name(index, 0, material.capitalize())
		var colors: Array = manifest["palette_hex"][material]
		tile_set.set_terrain_color(index, 0, Color(str(colors[0])))
	var atlas: TileSetAtlasSource = TileSetAtlasSource.new()
	atlas.resource_name = "Terrain variations and woodland props"
	atlas.texture = load(DIRECTORY + "terrain_atlas.png") as Texture2D
	if atlas.texture == null:
		push_error("Import terrain_atlas.png in the editor before running this builder.")
		quit(1)
		return
	atlas.texture_region_size = tile_set.tile_size
	atlas.use_texture_padding = true
	tile_set.add_source(atlas, 0)
	var records: Array = manifest["tiles"]
	for value: Variant in records:
		var record: Dictionary = value
		var coordinate: Vector2i = _coords(record["atlas_coords"])
		atlas.create_tile(coordinate)
		var data: TileData = atlas.get_tile_data(coordinate, 0)
		if record["kind"] == "decoration":
			continue
		data.terrain_set = int(record["terrain_set"])
		data.terrain = 0
		data.probability = float(record["probability"])
		var mask: int = int(record["mask"])
		for peer: Dictionary in PEERS:
			data.set_terrain_peering_bit(int(peer["peer"]), 0 if mask & int(peer["bit"]) else -1)
	var error: Error = ResourceSaver.save(tile_set, DIRECTORY + "woodland_tileset.tres")
	if error != OK:
		push_error("Could not save woodland TileSet: %s" % error_string(error))
		quit(1)
		return
	for value: Variant in manifest["maps"]:
		var map_data: Dictionary = value
		if not _save_map(tile_set, map_data, tile_size):
			quit(1)
			return
	print("BUILT: woodland_tileset.tres, %d terrain brushes, %d tiles, woodland_example.tscn." % [materials.size(), records.size()])
	quit(0)


func _coords(value: Array) -> Vector2i:
	return Vector2i(int(value[0]), int(value[1]))


func _save_map(tile_set: TileSet, map_data: Dictionary, tile_size: int) -> bool:
	var scene_root: Node2D = Node2D.new()
	scene_root.name = str(map_data["name"])
	scene_root.texture_filter = CanvasItem.TEXTURE_FILTER_NEAREST
	var layer_index: int = 0
	for value: Variant in map_data["layers"]:
		var layer_data: Dictionary = value
		var layer: TileMapLayer = TileMapLayer.new()
		layer.name = "%02d_%s" % [layer_index, str(layer_data["material"]).capitalize()]
		layer.tile_set = tile_set
		scene_root.add_child(layer)
		layer.owner = scene_root
		for cell_value: Variant in layer_data["cells"]:
			var cell: Dictionary = cell_value
			layer.set_cell(_coords(cell["cell"]), 0, _coords(cell["atlas_coords"]))
		layer_index += 1
	var decorations: TileMapLayer = TileMapLayer.new()
	decorations.name = "Decorations"
	decorations.tile_set = tile_set
	scene_root.add_child(decorations)
	decorations.owner = scene_root
	for cell_value: Variant in map_data["decorations"]:
		var cell: Dictionary = cell_value
		decorations.set_cell(_coords(cell["cell"]), 0, _coords(cell["atlas_coords"]))
	var camera: Camera2D = Camera2D.new()
	camera.name = "OverviewCamera"
	var dimensions: Vector2i = _coords(map_data["size"])
	camera.position = Vector2(dimensions) * float(tile_size) * 0.5
	camera.zoom = Vector2.ONE * float(map_data["camera_zoom"])
	scene_root.add_child(camera)
	camera.owner = scene_root
	var packed: PackedScene = PackedScene.new()
	var error: Error = packed.pack(scene_root)
	if error == OK:
		error = ResourceSaver.save(packed, DIRECTORY + "woodland_example.tscn")
	scene_root.free()
	if error != OK:
		push_error("Could not save woodland example: %s" % error_string(error))
	return error == OK
