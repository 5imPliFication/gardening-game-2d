extends Node

const PLAYER_SPEED: float = 200.0
const TILE_SIZE: int = 32

const PHASE_SECONDS: float = 240.0
const PHASE_NAMES: Array[String] = ["Morning", "Afternoon", "Evening", "Midnight"]
const WARNING_SECONDS: Array[int] = [60, 20]
const START_DAY: int = 1

const PASS_OUT_ITEM_LOSS_CHANCE: float = 0.67
const PASS_OUT_FINE_RATE: float = 0.10
const PASS_OUT_MIN_FINE: int = 10
