class_name PlayerVisual
extends AnimatedSprite2D
## Animation/equipment presentation for one player; resources are data-driven.

var facing: String = "down"
var walking: bool = false


func _ready() -> void:
	EventBus.upgrades_changed.connect(_refresh_equipment)
	EventBus.appearance_changed.connect(_refresh_equipment)
	_refresh_equipment()


func update_motion(intent: Vector2, displacement: Vector2) -> void:
	if not intent.is_zero_approx():
		if is_zero_approx(intent.x):
			facing = "up" if intent.y < 0.0 else "down"
		else:
			facing = "left" if intent.x < 0.0 else "right"
			facing += "_up" if intent.y < 0.0 else "_down"
	walking = not displacement.is_zero_approx()
	_play_state()


func _refresh_equipment() -> void:
	var characters: Dictionary = GameData.visuals.get("characters", {})
	var model: Dictionary = characters.get(GameState.appearance, {})
	var variant: String = "lantern" if GameState.get_lantern_level() > 0 else "recolored"
	var path: String = str(model.get(variant, ""))
	if path.is_empty() or not ResourceLoader.exists(path):
		push_error("PlayerVisual: missing character frames %s" % path)
		return
	var previous_frame: int = frame
	var previous_progress: float = frame_progress
	sprite_frames = load(path) as SpriteFrames
	_play_state()
	if sprite_frames != null and sprite_frames.has_animation(animation):
		set_frame_and_progress(previous_frame % sprite_frames.get_frame_count(animation), previous_progress)


func _play_state() -> void:
	var next_animation: StringName = StringName(("walk_" if walking else "idle_") + facing)
	if sprite_frames != null and sprite_frames.has_animation(next_animation):
		if animation != next_animation or not is_playing():
			play(next_animation)
