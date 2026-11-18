extends SceneTree
## Engine-side brush/resource verification; does not load a gameplay scene.

const DIRECTORY: String = "res://assets/tilesets/woodland/"
const NEIGHBORS: Array[Vector2i] = [
	Vector2i(0, -1), Vector2i(1, -1), Vector2i(1, 0), Vector2i(1, 1),
	Vector2i(0, 1), Vector2i(-1, 1), Vector2i(-1, 0), Vector2i(-1, -1),
]
const PEERS: Array[int] = [
	TileSet.CELL_NEIGHBOR_TOP_SIDE, TileSet.CELL_NEIGHBOR_TOP_RIGHT_CORNER,
	TileSet.CELL_NEIGHBOR_RIGHT_SIDE, TileSet.CELL_NEIGHBOR_BOTTOM_RIGHT_CORNER,
	TileSet.CELL_NEIGHBOR_BOTTOM_SIDE, TileSet.CELL_NEIGHBOR_BOTTOM_LEFT_CORNER,
	TileSet.CELL_NEIGHBOR_LEFT_SIDE, TileSet.CELL_NEIGHBOR_TOP_LEFT_CORNER,
]


func _initialize() -> void:
	_verify.call_deferred()


func _verify() -> void:
	var manifest: Dictionary = JSON.parse_string(FileAccess.get_file_as_string(DIRECTORY + "terrain_manifest.json"))
	var tiles: TileSet = load(DIRECTORY + "woodland_tileset.tres") as TileSet
	if not _check(tiles != null, "TileSet loads"):
		return
	if not _check(tiles.tile_size == Vector2i(int(manifest["tile_size"]), int(manifest["tile_size"])), "Native tile size"):
		return
	var materials: Array = manifest["materials"]
	if not _check(tiles.get_terrain_sets_count() == materials.size(), "Terrain set count"):
		return
	var atlas: TileSetAtlasSource = tiles.get_source(0) as TileSetAtlasSource
	if not _check(atlas != null and atlas.get_tiles_count() == manifest["tiles"].size(), "Atlas tile count"):
		return
	for value: Variant in manifest["tiles"]:
		var record: Dictionary = value
		var coord: Array = record["atlas_coords"]
		var data: TileData = atlas.get_tile_data(Vector2i(int(coord[0]), int(coord[1])), 0)
		if record["kind"] == "decoration":
			if not _check(data.terrain_set == -1, "Decoration has no terrain rules"):
				return
			continue
		if not _check(data.terrain_set == int(record["terrain_set"]) and data.terrain == 0, "Material terrain assignment"):
			return
		if not _check(_read_mask(data) == int(record["mask"]), "Saved peering bits"):
			return
	var checks: int = 0
	seed(20261031)
	for material: int in range(materials.size()):
		var layer: TileMapLayer = TileMapLayer.new()
		layer.tile_set = tiles
		root.add_child(layer)
		for value: Variant in manifest["blob_masks"]:
			var expected: int = int(value)
			layer.clear()
			var cells: Array[Vector2i] = [Vector2i.ZERO]
			for index: int in range(NEIGHBORS.size()):
				if expected & (1 << index):
					cells.append(NEIGHBORS[index])
			layer.set_cells_terrain_connect(cells, material, 0, false)
			var center: TileData = layer.get_cell_tile_data(Vector2i.ZERO)
			if not _check(center != null and center.terrain_set == material and center.terrain == 0, "Brush paints requested center"):
				return
			if not _check(_read_mask(center) == expected, "%s brush mask %d became %d" % [str(materials[material]), expected, _read_mask(center)]):
				return
			for cell: Vector2i in cells:
				var painted: TileData = layer.get_cell_tile_data(cell)
				if not _check(painted != null and painted.terrain_set == material and painted.terrain == 0, "Brush preserves all requested cells"):
					return
			checks += 1
		layer.clear()
		var fill_cells: Array[Vector2i] = []
		for y: int in range(12):
			for x: int in range(16):
				fill_cells.append(Vector2i(x, y))
		layer.set_cells_terrain_connect(fill_cells, material, 0, false)
		var chosen_interiors: Dictionary = {}
		for y: int in range(2, 10):
			for x: int in range(2, 14):
				var cell: Vector2i = Vector2i(x, y)
				var data: TileData = layer.get_cell_tile_data(cell)
				if not _check(data != null and _read_mask(data) == 255, "Filled region uses interior topology"):
					return
				chosen_interiors[layer.get_cell_atlas_coords(cell)] = true
		if not _check(chosen_interiors.size() > 1, "Terrain painting selects multiple texture variations"):
			return
		layer.free()
	var scene: PackedScene = load(DIRECTORY + "woodland_example.tscn") as PackedScene
	if not _check(scene != null, "Example scene loads"):
		return
	var example: Node = scene.instantiate()
	if not _check(example.get_child_count() == manifest["maps"][0]["layers"].size() + 2, "Example layer count"):
		return
	example.free()
	print("PASS: Godot resource, all tile peering bits, %d terrain-brush topology cases, 8 varied fill regions, and example scene verified." % checks)
	quit(0)


func _read_mask(data: TileData) -> int:
	var result: int = 0
	for index: int in range(PEERS.size()):
		if data.get_terrain_peering_bit(PEERS[index]) == 0:
			result |= 1 << index
	return result


func _check(condition: bool, message: String) -> bool:
	if not condition:
		push_error("TileSet verification failed: " + message)
		quit(1)
	return condition
