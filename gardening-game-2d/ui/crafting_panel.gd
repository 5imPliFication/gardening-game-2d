extends CanvasLayer

@onready var cauldron_label: Label = $Window/CauldronLabel
@onready var recipe_list: VBoxContainer = $Window/RecipeList
@onready var status_label: Label = $Window/StatusLabel
@onready var close_button: Button = $Window/CloseButton

var _menu_count: int = 0


func _ready() -> void:
	visible = false
	EventBus.crafting_requested.connect(_on_crafting_requested)
	EventBus.inventory_changed.connect(_refresh)
	EventBus.menu_opened.connect(_on_menu_opened)
	EventBus.menu_closed.connect(_on_menu_closed)
	close_button.pressed.connect(_on_close_pressed)
	_refresh()


func _unhandled_input(event: InputEvent) -> void:
	if visible and event.is_action_pressed("cancel"):
		_set_open(false)
		get_viewport().set_input_as_handled()


func _set_open(should_open: bool) -> void:
	if visible == should_open:
		return
	if should_open and _menu_count > 0:
		return

	visible = should_open
	if should_open:
		status_label.text = ""
		_refresh()
		EventBus.menu_opened.emit()
	else:
		EventBus.menu_closed.emit()


func _exit_tree() -> void:
	if visible:
		EventBus.menu_closed.emit()


func _refresh() -> void:
	cauldron_label.text = "Cauldron Tier %d" % GameState.get_cauldron_level()
	for child in recipe_list.get_children():
		recipe_list.remove_child(child)
		child.queue_free()

	for id_variant in GameData.recipes:
		var recipe_id: String = str(id_variant)
		var recipe: Dictionary = GameData.get_recipe(recipe_id)
		recipe_list.add_child(_make_recipe_row(recipe_id, recipe))


func _make_recipe_row(recipe_id: String, recipe: Dictionary) -> HBoxContainer:
	var row: HBoxContainer = HBoxContainer.new()
	var description: Label = Label.new()
	description.custom_minimum_size = Vector2(310, 42)
	description.text = _recipe_description(recipe_id, recipe)
	row.add_child(description)

	var button: Button = Button.new()
	button.text = "Craft"
	button.disabled = not GameState.can_craft(recipe_id)
	button.pressed.connect(_on_craft_pressed.bind(recipe_id))
	row.add_child(button)
	return row


func _recipe_description(recipe_id: String, recipe: Dictionary) -> String:
	var output: Dictionary = recipe.get("output", {})
	var output_id: String = str(output.get("item", recipe_id))
	var output_item: Dictionary = GameData.get_item(output_id)
	var output_name: String = str(output_item.get("name", output_id))
	var output_count: int = int(output.get("count", 0))
	var ingredient_names: PackedStringArray = []

	var inputs: Array = recipe.get("inputs", [])
	for input_variant in inputs:
		if input_variant is Dictionary:
			var input: Dictionary = input_variant
			var item_id: String = str(input.get("item", ""))
			var item: Dictionary = GameData.get_item(item_id)
			ingredient_names.append("%s x%d" % [
				str(item.get("name", item_id)), int(input.get("count", 0))
			])

	return "%s x%d\n%s" % [output_name, output_count, " + ".join(ingredient_names)]


func _on_crafting_requested() -> void:
	_set_open(true)


func _on_craft_pressed(recipe_id: String) -> void:
	if GameState.craft(recipe_id):
		var recipe: Dictionary = GameData.get_recipe(recipe_id)
		var output: Dictionary = recipe.get("output", {})
		var output_id: String = str(output.get("item", recipe_id))
		var item: Dictionary = GameData.get_item(output_id)
		status_label.text = "Crafted %s" % str(item.get("name", output_id))
	else:
		status_label.text = "Missing ingredients or cauldron tier"
	_refresh()


func _on_close_pressed() -> void:
	_set_open(false)


func _on_menu_opened() -> void:
	_menu_count += 1


func _on_menu_closed() -> void:
	_menu_count = max(0, _menu_count - 1)
