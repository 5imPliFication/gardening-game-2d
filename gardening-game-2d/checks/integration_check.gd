extends Node
## Run in the documented /media/simpi/program-files/opencode-temp sandbox; never writes real player saves.

var checks: int = 0
var root: Window:
	get:
		return get_tree().root
var current_scene: Node:
	get:
		return get_tree().current_scene
	set(value):
		get_tree().current_scene = value


func _ready() -> void:
	get_tree().current_scene = null
	_run.call_deferred()


func quit(code: int = 0) -> void:
	get_tree().quit(code)


func _run() -> void:
	if not _expect(OS.get_user_data_dir().begins_with("/media/simpi/program-files/opencode-temp/"), "Use an isolated XDG_DATA_HOME under /media/simpi/program-files/opencode-temp"):
		return
	for value: Variant in GameData.interface_data["save_slots"]:
		var slot: Dictionary = value
		for suffix: String in ["", ".bak", ".tmp"]:
			DirAccess.remove_absolute(ProjectSettings.globalize_path(str(slot["path"]) + suffix))
	if not _check_resources():
		return
	var start: Node = await _mount("res://ui/start_screen.tscn")
	if not _expect(start.name == "StartScreen" and not GameClock.is_running, "Start screen pauses the clock and waits for input"):
		return
	await _capture("start_screen")
	start.call("_begin")
	await _settle()
	var menu: Control = current_scene as Control
	if not _expect(menu.name == "MainMenu" and bool(menu.get("continue_button").disabled), "Empty saves disable Continue"):
		return
	await _capture("main_menu")
	menu.call("_show_settings")
	if not _expect(bool(menu.get("settings").visible), "Settings opens from the main menu"):
		return
	var settings_panel: SettingsPanel = menu.get("settings")
	var settings_column: VBoxContainer = settings_panel.get_node("Margins/Content")
	(settings_column.get_child(1).get_node("MasterVolume") as HSlider).value = 37
	var resolution_choice: OptionButton = settings_column.get_node("Resolution")
	resolution_choice.select(0)
	resolution_choice.item_selected.emit(0)
	UserSettings.values.clear()
	UserSettings.load_and_apply()
	if not _expect(is_equal_approx(float(UserSettings.values["master_volume"]), 0.37), "Settings persist across reload"):
		return
	if not _expect(is_equal_approx(db_to_linear(AudioServer.get_bus_volume_db(0)), 0.37), "Master volume is applied to the audio bus"):
		return
	if DisplayServer.get_name() != "headless" and not _expect(root.size == UserSettings.resolution_size(), "Window resolution setting resizes the actual window"):
		return
	await _capture("settings")
	menu.call("_show_main")
	(menu.get("appearance") as OptionButton).select(1)
	menu.call("_new_game")
	await _settle()
	if not _expect(GameState.current_map_id == "town_square" and GameState.appearance == "male", "New Game starts chosen adventurer in Town Square"):
		return
	var player: CharacterBody2D = current_scene.get_node("Player")
	var visual: PlayerVisual = player.get_node("Body")
	if not _expect(visual.sprite_frames.resource_path.contains("/male/recolored"), "Unequipped male animation is selected"):
		return
	Input.action_press("move_right")
	var initial: Vector2 = player.position
	await _physics_steps(5)
	if not _expect(player.position.x > initial.x and visual.animation == &"walk_right_down", "Movement drives the correct walking animation"):
		return
	await _press("open_map")
	var map_ui: CanvasLayer = current_scene.get_node("HUD/MapUI")
	if not _expect((map_ui.get_node("WorldWindow") as Control).visible, "M opens the global map"):
		return
	initial = player.position
	var seconds: float = GameClock.seconds_into_phase
	await _physics_steps(5)
	if not _expect(player.position == initial and is_equal_approx(seconds, GameClock.seconds_into_phase), "Global map pauses movement and time"):
		return
	await _press("open_inventory")
	if not _expect(not (current_scene.get_node("InventoryPanel") as CanvasLayer).visible, "Other menus cannot open over the map"):
		return
	await _capture("global_map")
	await _press("open_map")
	Input.action_release("move_right")
	await _physics_steps(2)
	await _capture("town_square")
	await _press("cancel")
	var pause: CanvasLayer = current_scene.get_node("HUD/PauseMenu")
	if not _expect(bool(pause.get("overlay").visible), "Esc opens Pause when no other menu is active"):
		return
	await _capture("pause")
	pause.call("_show_save")
	var browser: SaveLoadPanel = pause.get("saves")
	browser.call("_activate", "user://slot_1.json")
	if not _expect(bool(SaveManager.inspect_slot("user://slot_1.json")["valid"]), "Save screen creates a valid manual slot"):
		return
	await _capture("save_screen")
	pause.call("_show_main")
	await _press("cancel")
	await _interact_at(Vector2(896, 464))
	if not _expect(GameState.current_map_id == "bubble_street" and current_scene.get_node("Player").position == Vector2(128, 432), "Town exit arrives at Bubble Street's matching entrance"):
		return
	if not _expect(current_scene.has_node("PlayerShop") and bool(current_scene.get_node("PlayerShop").get("pending_structure")), "Player shop is marked as pending on Bubble Street"):
		return
	await _capture("bubble_street")
	await _interact_at(Vector2(520, 288))
	if not _expect(GameState.current_map_id == "home", "Pending shop opens the temporary playable interior"):
		return
	await _interact_at(Vector2(200, 472))
	var home_menu: CanvasLayer = current_scene.get_node("HomeMenu")
	if not _expect(home_menu.visible, "Home menu station remains usable with new art/collisions"):
		return
	var appearance: OptionButton = home_menu.get_node("Window/AppearanceChoice")
	appearance.select(0)
	appearance.item_selected.emit(0)
	var upgrade: Dictionary = GameState.get_next_upgrade("lantern")
	GameState.gold = int(upgrade["cost"])
	if not _expect(GameState.purchase_upgrade("lantern"), "Lantern purchase succeeds"):
		return
	player = current_scene.get_node("Player")
	visual = player.get_node("Body")
	if not _expect(GameState.appearance == "female" and visual.sprite_frames.resource_path.contains("/female/lantern"), "Appearance and upgrade signals switch to equipped female frames"):
		return
	home_menu.call("_on_save_pressed")
	home_menu.call("_set_open", false)
	var saved_position: Vector2 = player.position
	if not _expect(SaveManager.save_game(), "Repeated automatic save retains backup"):
		return
	var invalid: FileAccess = FileAccess.open("user://save.json", FileAccess.WRITE)
	invalid.store_string("broken primary for backup recovery check")
	invalid.close()
	if not _expect(bool(SaveManager.inspect_slot("user://save.json").get("backup", false)), "Save browser recognizes a valid backup"):
		return
	await _press("cancel")
	pause = current_scene.get_node("HUD/PauseMenu")
	pause.call("_show_load")
	browser = pause.get("saves")
	await _capture("load_screen")
	browser.call("_activate", "user://save.json")
	await _settle()
	player = current_scene.get_node("Player")
	if not _expect(GameState.current_map_id == "home" and player.position == saved_position and GameState.appearance == "female", "Load restores backed-up area, exact position, appearance and equipment"):
		return
	if not _expect(SaveManager.save_game(), "Recovered primary can be saved again"):
		return
	player.position = Vector2(480, 400)
	await _settle()
	await _capture("home")
	await _interact_at(Vector2(320, 328))
	if not _expect((current_scene.get_node("CraftingPanel") as CanvasLayer).visible, "Cauldron interaction still opens crafting"):
		return
	current_scene.get_node("CraftingPanel").call("_set_open", false)
	await _interact_at(Vector2(480, 512))
	if not _expect(GameState.current_map_id == "bubble_street", "Shop exit returns outside to Bubble Street"):
		return
	await _interact_at(Vector2(1184, 464))
	if not _expect(GameState.current_map_id == "forest" and current_scene.get_node("Player").position == Vector2(520, 240), "Bubble Street connects to Forest with an arrival spawn"):
		return
	player = current_scene.get_node("Player")
	var plant: Area2D = (load("res://scenes/plant.tscn") as PackedScene).instantiate()
	plant.set("item_id", "dew_herb")
	plant.position = Vector2(340, 360)
	current_scene.add_child(plant)
	if not _expect((plant.get_node("Body") as AnimatedSprite2D).is_playing(), "Forage pickups use animated plant sprites"):
		return
	var previous_count: int = GameState.get_item_count("dew_herb")
	player.position = plant.position
	await _physics_steps(4)
	if not _expect(GameState.get_item_count("dew_herb") == previous_count + 1, "Animated plants remain collectible"):
		return
	player.position = Vector2(400, 210)
	Input.action_press("move_up")
	await _physics_steps(18)
	Input.action_release("move_up")
	if not _expect(player.position.y >= 189, "Player feet collide with tree trunks"):
		return
	for marker: Node2D in current_scene.get_node("Spawner/SpawnMarkers").get_children():
		if not _expect(_point_is_clear(marker.global_position + Vector2(0, -4)), "Forage marker remains reachable: " + str(marker.name)):
			return
	if not _expect(_point_is_clear(Vector2(1072, 432)) and not _point_is_clear(Vector2(1040, 432)), "Wood bridge is traversable and adjacent pond water blocks movement"):
		return
	player.position = Vector2(520, 240)
	await _settle()
	await _capture("forest")
	await _interact_at(Vector2(760, 208))
	if not _expect(GameState.current_map_id == "cave_a_1", "Owned lantern unlocks cave entry"):
		return
	var environment_names: Dictionary = {}
	for depth: int in range(1, 5):
		if depth > 1:
			GameState.lantern_tier = depth - 1
			GameState.enter_cave("cave_a", depth, "arrival")
			await _mount("res://scenes/cave_depth.tscn")
		var environment: Node = current_scene.get_node("Environment").get_child(0)
		environment_names[environment.scene_file_path] = true
		if not _expect(GameState.current_map_id == "cave_a_%d" % depth, "Cave map identifies its current depth"):
			return
		if depth > 1 and not _expect((current_scene.get_node("Ladder") as Area2D).visible, "Persistent ladder is visible on reached cave depths"):
			return
		await _capture("cave_%d" % depth)
	if not _expect(environment_names.size() == 4, "Each cave depth loads a different environment"):
		return
	if not _expect(SaveManager.save_to_path("user://slot_3.json") and SaveManager.load_slot("user://slot_3.json"), "Cave save/load validates location and depth together"):
		return
	SaveManager.resume_game()
	await _settle()
	if not _expect(GameState.current_map_id == "cave_a_4", "Cave save resumes at the correct depth"):
		return
	var legacy: Dictionary = SaveManager.call("_build_save_data")
	legacy.erase("appearance")
	legacy.erase("location")
	if not _expect(bool(SaveManager.call("_validate_save_data", legacy)), "Older version-1 saves remain valid"):
		return
	var malformed: Dictionary = legacy.duplicate(true)
	malformed["location"] = {"id": "cave_a_4", "position": [300, 360]}
	malformed["current_cave"] = []
	if not _expect(not bool(SaveManager.call("_validate_save_data", malformed)), "Malformed cave locations are rejected without mutating state"):
		return
	GameState.last_recovery = {"reason": "pass_out", "lost_items": {}, "fine": 0}
	if not _expect(SaveManager.save_game("clinic") and SaveManager.load_game(), "Automatic recovery save points to Clinic instead of the pass-out area"):
		return
	SaveManager.resume_game()
	await _settle()
	if not _expect(GameState.current_map_id == "clinic" and (current_scene.get_node("RecoveryPanel") as CanvasLayer).visible, "Clinic recovery message opens after loading a pass-out save"):
		return
	await _press("cancel")
	if not _expect(not (current_scene.get_node("RecoveryPanel") as CanvasLayer).visible, "Recovery message closes without opening Pause underneath"):
		return
	await _capture("clinic")
	await _interact_at(Vector2(480, 512))
	if not _expect(GameState.current_map_id == "town_square" and current_scene.get_node("Player").position == Vector2(256, 284), "Clinic returns to its marked Town Square plot"):
		return
	await _press("cancel")
	pause = current_scene.get_node("HUD/PauseMenu")
	pause.call("_leave")
	await _settle()
	if not _expect(current_scene.name == "MainMenu" and not GameClock.is_running, "Save & Main Menu returns to a stopped-clock menu"):
		return
	current_scene.call("_continue_game")
	await _settle()
	if not _expect(GameState.current_map_id == "town_square", "Continue chooses the newest saved game"):
		return
	print("PASS: %d gameplay/UI assertions; start/main/pause/settings/save/load; maps and connected areas; appearance, lantern, animation, collision, pickup, legacy and backup saves." % checks)
	quit(0)


func _check_resources() -> bool:
	for character: Variant in GameData.visuals["characters"].values():
		for path: Variant in character.values():
			var frames: SpriteFrames = load(str(path)) as SpriteFrames
			if not _expect(frames != null and frames.get_animation_names().size() == 12, "Character has all six idle and walking directions"):
				return false
			for animation: StringName in frames.get_animation_names():
				if not _expect(frames.get_frame_count(animation) == 8 and frames.get_frame_texture(animation, 0).get_size() == Vector2(32, 32), "Character frames stay native 32px with eight poses"):
					return false
	for item: Variant in GameData.items.values():
		var texture: Texture2D = load(str(item["icon"])) as Texture2D
		if not _expect(texture != null and texture.get_size() == Vector2(32, 32), "Item icon loads as a 32px texture"):
			return false
	return true


func _mount(path: String) -> Node:
	if current_scene != null:
		current_scene.queue_free()
		current_scene = null
		await get_tree().process_frame
		await get_tree().process_frame
	var node: Node = (load(path) as PackedScene).instantiate()
	root.add_child(node)
	current_scene = node
	await _settle()
	return node


func _settle() -> void:
	await get_tree().process_frame
	await get_tree().process_frame
	await _physics_steps(3)


func _physics_steps(count: int) -> void:
	for _index: int in range(count):
		await get_tree().physics_frame


func _press(action: String) -> void:
	var event: InputEventAction = InputEventAction.new()
	event.action = action
	event.pressed = true
	Input.parse_input_event(event)
	await get_tree().process_frame
	event = InputEventAction.new()
	event.action = action
	event.pressed = false
	Input.parse_input_event(event)
	await get_tree().process_frame


func _interact_at(position_value: Vector2) -> void:
	var player: CharacterBody2D = current_scene.get_node("Player")
	player.position = position_value
	await _physics_steps(4)
	await _press("interact")
	await _settle()


func _point_is_clear(point: Vector2) -> bool:
	var query: PhysicsPointQueryParameters2D = PhysicsPointQueryParameters2D.new()
	query.position = point
	query.collide_with_areas = false
	query.collision_mask = 1
	return (current_scene as Node2D).get_world_2d().direct_space_state.intersect_point(query).is_empty()


func _capture(name_value: String) -> void:
	if not OS.get_cmdline_user_args().has("--capture") or DisplayServer.get_name() == "headless":
		return
	await RenderingServer.frame_post_draw
	var image: Image = root.get_texture().get_image()
	var directory: String = ProjectSettings.globalize_path("res://").path_join("../art/gameplay-previews").simplify_path()
	DirAccess.make_dir_recursive_absolute(directory)
	image.save_png(directory.path_join(name_value + ".png"))


func _expect(condition: bool, message: String) -> bool:
	checks += 1
	if not condition:
		push_error("Integration check failed: " + message)
		quit(1)
	return condition
