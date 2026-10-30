extends Node

var items: Dictionary = {}
var recipes: Dictionary = {}
var spawns: Dictionary = {}
var upgrades: Dictionary = {}
var caves: Dictionary = {}
var customers: Dictionary = {}


func _ready() -> void:
	items = _load_indexed("res://data/items.json")
	recipes = _load_indexed("res://data/recipes.json")
	spawns = _load_dictionary("res://data/spawns.json")
	upgrades = _load_dictionary("res://data/upgrades.json")
	caves = _load_dictionary("res://data/caves.json")
	customers = _load_dictionary("res://data/customers.json")

	print("GameData loaded: items=%d recipes=%d spawns=%d upgrades=%d caves=%d customers=%d" % [
		items.size(), recipes.size(), spawns.size(), upgrades.size(), caves.size(), customers.size()
	])


func get_item(id: String) -> Dictionary:
	if items.has(id):
		var item: Dictionary = items[id]
		return item
	return {}


func get_recipe(id: String) -> Dictionary:
	if recipes.has(id):
		var recipe: Dictionary = recipes[id]
		return recipe
	return {}


func get_cave_depth(cave_id: String, depth: int) -> Dictionary:
	var cave: Dictionary = caves.get(cave_id, {})
	var depths: Array = cave.get("depths", [])
	for depth_variant in depths:
		if depth_variant is Dictionary:
			var row: Dictionary = depth_variant
			if int(row.get("depth", 0)) == depth:
				return row
	return {}


func _load_indexed(path: String) -> Dictionary:
	var result: Dictionary = {}
	var data: Variant = _read_json(path)
	if data is Array:
		var entries: Array = data
		for entry in entries:
			if entry is Dictionary:
				var row: Dictionary = entry
				if row.has("id"):
					var id: String = str(row["id"])
					result[id] = row
	return result


func _load_dictionary(path: String) -> Dictionary:
	var data: Variant = _read_json(path)
	if data is Dictionary:
		var result: Dictionary = data
		return result
	return {}


func _read_json(path: String) -> Variant:
	if not FileAccess.file_exists(path):
		push_error("GameData: missing file %s" % path)
		return null

	var file: FileAccess = FileAccess.open(path, FileAccess.READ)
	if file == null:
		push_error("GameData: unable to open %s" % path)
		return null

	var text: String = file.get_as_text()
	file.close()

	var parsed: Variant = JSON.parse_string(text)
	if parsed == null:
		push_error("GameData: invalid JSON in %s" % path)
	return parsed
