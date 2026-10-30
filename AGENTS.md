# AGENTS.md

## Project layout

- The Godot project is nested in `gardening-game-2d/`, not at the repo root. `res://` maps to `gardening-game-2d/`; always pass `--path gardening-game-2d`.
- `Potion Forager Project Blueprint v0.1.md` (repo root) is the authoritative design spec. Read it before implementing.
- Build order is gated: each milestone in blueprint §8 must be playable before starting the next. Do not build ahead.
- Milestone 1 added the main scene (`res://scenes/forest.tscn`), `Player`/`Tree`/`Forest` scenes, `scripts/player.gd`, and the `EventBus`/`Config` autoloads. Milestone 2 added the `GameClock` autoload and a debug `HUD`. Milestone 3 added the `GameData` autoload and placeholder JSON in `res://data/`. Milestone 4 added inventory, phase spawning, plant pickups, and the inventory panel. Milestone 5 added gold, recipe crafting, the 70% sell bin, `Home`, station interactions, and forest/home transitions. Milestone 6 added the open-shop clock mode and customer bursts. Milestone 7 added sleep, pass-out penalties, the Clinic recovery flow, and Midnight Bloom. Milestone 8 added the reusable cave-depth scene, hidden holes, persistent ladders, lantern gates, and daily cave spawns. Milestone 9 added data-driven bag, lantern, and cauldron purchases. Milestone 10 added Botanary discovery tracking, the Botanary panel, versioned saves, backup recovery, and Home manual save.
- `.godot/` is generated editor cache (gitignored). Never hand-edit it.

## Commands

- Run project: `godot --path gardening-game-2d`
- Open editor: `godot -e --path gardening-game-2d`
- Validate config/imports: `godot --headless --path gardening-game-2d --quit` now exits cleanly.
- Installed engine: Godot 4.7.1 at `/usr/local/bin/godot`.
- No test, lint, formatter, CI, or export preset is configured. Do not invent commands or claim a suite passes.

## Implementation rules (from the blueprint)

- Godot 4 typed GDScript only: `@onready`, `@export`, `signal.connect()`. No Godot 3 syntax.
- Required autoloads: `EventBus`, `Config`, `GameData`, `GameClock`, `GameState`, `SaveManager`.
- Cross-system communication goes through `EventBus` signals, not direct node references.
- No gameplay numbers in code. Items, recipes, spawns, upgrades, caves, and customers load from `res://data/*.json` via `GameData`; time constants live in `Config`.
- One responsibility per script; keep scripts small.
- No art: use `ColorRect` and the default icon. Item icons load from an `icon` path in data with a placeholder fallback for missing files.
- Update `CREDITS.txt` whenever an external asset is added.
- Create the intended folders as needed: `res://autoload`, `res://scenes`, `res://scripts`, `res://ui`, `res://data`, `res://assets`.

## Gotchas

- `project.godot` is configured for a 640x360 viewport, integer scaling, Nearest texture filtering, the Milestone 1 input map, and the `EventBus`/`Config`/`GameClock`/`GameData`/`GameState`/`SaveManager` autoloads.
- `GameData` loads `res://data/items.json`, `recipes.json`, `spawns.json`, `upgrades.json`, `caves.json`, and `customers.json` at startup. Item lookup: `GameData.get_item(id)` returns the item dictionary or `{}`.
- Forest spawn tables are in `GameData.spawns["forest"]`; `Forest/Spawner` rebuilds `Area2D` plants on `phase_changed`. Pickups call `GameState.add_item(id)`.
- Remaining forest spawn records persist in `GameState` for the current day and phase, so visiting Home does not replenish collected plants.
- `GameState` owns `inventory` (item id to unit count) and `bag_tier`; capacity comes from `GameData.upgrades["bag"]["tiers"][bag_tier]["effect"]`.
- `I` opens the inventory, `B` opens the Botanary, and `Esc` closes the active menu. Menus emit `EventBus.menu_opened`/`menu_closed`, which pause `GameClock` and player movement.
- Picking up a `botanary` item adds it to `GameState.discovered_plants` and emits `EventBus.botanary_changed`. `BotanaryPanel` shows hidden entries as silhouettes with hints and discovered entries with names, icons, and lore.
- `E` at the forest `HomeEntrance` loads `res://scenes/home.tscn`. Home pauses the clock; returning to the forest resumes it unless the phase is Midnight.
- At Home, `E` opens the cauldron or sell bin while nearby. All three recipes are visible from the start. Sell-bin prices use `GameData.customers["sell_bin_multiplier"]`.
- `GameState` owns `gold` and `cauldron_tier`; the tier's usable level comes from `GameData.upgrades["cauldron"]["tiers"][cauldron_tier]["effect"]`.
- `E` at the Home shop counter opens the customer shop. The clock runs while it is open, the first burst arrives immediately, later bursts use the configured 45–75 second range, and a new burst replaces unserved customers.
- Customers request potion items and pay the configured 100%–130% base-price range. The shop closes itself on `midnight_reached`.
- `E` at the Home bed starts the next Morning without loss or a fine. Midnight pass-out rolls each carried unit against `Config.PASS_OUT_ITEM_LOSS_CHANCE`, applies the configured fine formula, and wakes the player in `res://scenes/clinic.tscn`.
- Sleep and pass-out save automatically before changing scenes. `GameState.last_recovery` and `resume_location` let a fresh launch reopen Home after sleep or Clinic after pass-out; the Clinic recovery panel reports lost items and gold before allowing movement.
- `E` at the Home menu station opens `HomeMenu`, whose Save button writes the current state manually.
- The Midnight Bloom uses `GameData.spawns["midnight_bloom"]`, appears once after the final-60-second warning threshold is crossed in Evening, persists as collected for that day, and despawns at Midnight.
- `res://scenes/cave_depth.tscn` is reused for all Cave A depths. `GameState.current_cave_id`, `current_cave_depth`, and `cave_entry_mode` configure it before loading.
- `GameState.cave_progress` stores chosen hole markers, found holes, and generated ladders across days. Cave plant records persist within a day and clear on `day_started`.
- `lantern_tier` starts at `-1` (level 0). Home's upgrade station sells lantern tiers 1–4, each opening its matching Cave A depth; the first purchase opens depth 1.
- Upgrade purchases use target-tier costs from `GameData.upgrades`. Bag upgrades refresh capacity immediately. The slice caps cauldron purchases at tier 2, which unlocks Moon Potion.
- Saves go to `user://save.json` and must include a `version` field. `SaveManager` validates saves before mutating state, writes via `.tmp`, retains a `.bak`, and recovers from the backup when the primary is missing or invalid.
- Tile size is 32x32; player speed is 120 px/s (Config constant).
- Files are UTF-8 with LF endings (`.editorconfig`, `.gitattributes`).
