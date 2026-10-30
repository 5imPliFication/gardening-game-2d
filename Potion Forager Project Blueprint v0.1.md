# Potion Forager: Project Blueprint v0.1

*Working title. Vertical-slice blueprint for the build agents. Godot 4.x, GDScript, 32x32 tiles, 2D top-down.*

## 1. Pitch and pillars

A cozy top-down game in a magical world. The player forages magical plants and fungi in a forest and its caves, crafts potions and ingredients at home, and sells them from a shop. Long-term goals: earn money, max out gear, unlock the biggest shop, and fill the Botanary (a collection log of every plant).

Pillars:

- **Chill with teeth.** Penalties are inconvenience, never ruin. Warnings are loud and early.
- **The clock is the main resource.** Only foraging and an open shop spend it.
- **Every upgrade opens something:** a place, a recipe, or a kind of item. No pure stat bumps.
- **Data-driven.** Items, recipes, prices, spawns, upgrades and cave depths live in JSON, not code.
- **Art-agnostic.** Every sprite is a swappable file referenced by path.

## 2. Scope

**In the vertical slice:** one forest map, 4 phase-based spawn tables, 5 plants plus 1 midnight bloom, 3 recipes, inventory, crafting, shop counter with simple customers, sleep and midnight pass-out, ONE cave with 4 depths, lantern tiers, bag upgrade, Botanary list, save/load.

**Not until the slice is fun with friends:** story and NPC dialogue, garden pots and seeds, caves B and C, plant growth over days, stay-awake buff, shop decorations, real 2D lighting, lantern fuel, sound polish.

## 3. Rules for the build agents

1. Godot 4.x only, typed GDScript. Use `@onready`, `@export`, and `signal.connect()`. No Godot 3 syntax.
2. No art. Use `ColorRect` and the default icon. Item icons load from an `icon` path in data, with a placeholder fallback if the file is missing.
3. No gameplay numbers in code. Read them from JSON through the `GameData` autoload. Time constants live in one config file.
4. Systems communicate through signals on an `EventBus` autoload, not direct node references.
5. Every milestone in section 8 must run before the next one starts. Do not build ahead.
6. Keep `CREDITS.txt` updated whenever an external asset is added.
7. One responsibility per script. Keep scripts small.

## 4. Project setup

- Viewport 640x360, stretch mode `canvas_items`, scale mode integer, default texture filter Nearest.
- Tile size 32x32. Player speed 120 px/s (config constant).
- Input actions: `move_left`, `move_right`, `move_up`, `move_down`, `interact`, `open_inventory`, `open_botanary`, `cancel`.
- Folders: `res://autoload`, `res://scenes`, `res://scripts`, `res://ui`, `res://data`, `res://assets`.

## 5. Architecture

**Autoloads**

- `EventBus`: all shared signals.
- `Config`: constants (phase length, speed, loss rate, fine rules).
- `GameData`: loads and serves JSON (items, recipes, spawns, upgrades, caves).
- `GameClock`: day, phase, time. Ticks only when told to.
- `GameState`: gold, inventory, upgrade tiers, flags, Botanary discoveries, cave progress.
- `SaveManager`: saves and loads `GameState` and clock to `user://save.json` with a `version` field.

**Scenes**

- `Player` (`CharacterBody2D`), `Forest`, `CaveDepth` (one reusable scene), `Home` (shop, sell bin, crafting station, bed), `Clinic`.
- UI: `HUD` (clock, phase, gold), `InventoryPanel`, `CraftingPanel`, `ShopPanel`, `BotanaryPanel`, `LadderMenu`, `WarningBanner`.

## 6. Systems

### 6.1 Clock and phases

- `PHASE_SECONDS = 240`. Active phases: Morning, Afternoon, Evening (12 minutes of clock). Midnight begins at the 12 minute mark.
- The clock ticks only while the player is in the forest or a cave with no menu open, or while the shop is open. It is paused in menus, crafting, and at home otherwise.
- Signals: `phase_changed(phase)`, `day_started(day)`, `time_warning(seconds_left)` at 60s and 20s before midnight, `midnight_reached`.
- Warning: banner text plus a screen tint ramp plus a bell placeholder. The banner must be readable in caves.
- A day ends by sleeping in the bed (allowed at any time, remaining time is skipped) or by pass-out.
- Player flag `can_stay_up_past_midnight` exists from day one and is always false in the slice. If true, the midnight phase (240s) plays instead of the pass-out.

### 6.2 Forest and spawning

- Each phase has a spawn table (item id, weight, max count). Tables are rebuilt on `phase_changed`. Plants are `Area2D` pickups placed on random valid spawn markers.
- Morning: dew herbs. Afternoon: sun plants. Evening: mushrooms. These are placeholders for the 5 slice plants.
- **Midnight bloom:** one special plant spawns in the last 60 seconds of Evening and despawns at midnight. It is the only source of that plant.
- Cave spawns do not depend on phase. They depend on depth only.

### 6.3 Inventory

- Stackable items, capacity counted in total units (bag capacity), not slots.
- Full bag blocks pickup and shows a message. No auto-discard.
- Inventory UI is a simple grid or list built from `Control` nodes.

### 6.4 Crafting

- Done at the crafting station at home. Costs no clock time.
- Recipe: input items and counts, output item and count. Recipes may require a cauldron tier.
- Slice: 3 recipes, all visible from the start.

### 6.5 Shop and customers

- **Sell bin** (always available, no clock): buys any sellable item at 70% of base price.
- **Open shop** (clock runs): customers arrive in bursts, one burst every 45 to 75 seconds of open time, 1 to 3 customers each. Each wants one specific item and pays 100% to 130% of base price.
- Customers who are not served simply leave. No reputation penalty in the slice.
- The shop auto-closes at midnight.
- Shop sells only non-magical bases (bottles, water, sugar) and, in v2, common seeds. Magical ingredients are never sold by the shop.

### 6.6 Midnight, pass-out, sleep

- At `midnight_reached` with `can_stay_up_past_midnight` false, the player passes out wherever they stand.
- **Item loss:** roll every unit of carried items separately. Each unit has a 67% chance of being lost. Rolling per unit, not per stack.
- **Fine:** `min(gold, max(10, round(gold * 0.10)))`. Never more than the player has.
- The player wakes in the Clinic at Morning of the next day, with a short message showing what was lost.
- Sleeping in bed starts the next day with no loss and no fine.
- Hidden caves, ladders, and Botanary progress are never lost.

### 6.7 Caves

- Slice: one cave (Cave A) with 4 depths. Caves B and C are added later as data rows, using the same scene.
- **One reusable `CaveDepth` scene.** Each depth is a data row: required lantern tier, spawn table, hole candidate markers, art theme. Do not hand-build 12 separate maps.
- Required lantern tier by depth: 1, 2, 3, 4 (so the lantern has 4 tiers, all in JSON).
- **Travel time:** about 1 minute per depth. Design the walking distance between a depth's arrival point and its hole at about 30 seconds of walking (`120 px/s x 30s = 3600 px`, about 110 tiles). The rest of the minute is gathering and searching.
- **Hidden hole:** each depth has one hole to the next depth. It uses a floor sprite nearly identical to the normal floor. Its position is chosen once per save from 3 or 4 candidate markers and stored in the save. It does not change daily.
- **Descending:** interact with the hole. If `lantern_tier` is below the next depth's requirement, show: too dark to go on. Otherwise descend.
- **Ladder:** on arrival at depth 2, 3 or 4 a ladder is generated at the arrival point. It persists across days and is saved. Interacting opens `LadderMenu` with three choices: **Go up 1 depth**, **Get out of cave**, **Cancel**.
- Going up 1 depth places the player at the hole of the depth above. They then walk to that depth's ladder to continue up.
- Once a hole is found it stays marked in the save. The player still walks to it each day.
- Cave spawns reset on `day_started`.

### 6.8 Upgrades

Four gear lines, all in one JSON file with `tiers`, `cost`, `effect`:

- **Bag:** carry capacity.
- **Lantern:** cave depth access (4 tiers).
- **Cauldron:** recipe tier access (3 tiers).
- **Pot (v2):** garden plots, with one free pot at the start.

Rule: an upgrade that does not open a place, recipe or item type does not get built.

### 6.9 Botanary

- A list of every plant with a `discovered` flag, saved in `GameState`.
- Undiscovered entries show as a silhouette plus a vague hint (for example: blooms only after dark).
- Each entry has a `lore` text field (empty is fine in the slice).
- Discovery happens on first pickup.

### 6.10 Garden (v2, do not build yet)

3 to 4 plots, seeds only drop from foraging (shop sells common seeds only), plants grow in N days, advanced on sleep. No daily watering until playtesters ask for care mechanics.

### 6.11 Save

- Save on sleep and on pass-out. Manual save from the home menu.
- Save file holds: version, day, gold, inventory, upgrade tiers, Botanary flags, cave progress (found holes, hole positions, ladders), and flags.

## 7. Data files

All in `res://data/` as JSON.

- **items.json:** `id`, `name`, `type` (raw, refined, potion, ingredient, base), `base_price`, `icon`, `botanary` (true or false), `hint`, `lore`.
- **recipes.json:** `id`, `inputs` (item id and count), `output` (item id and count), `cauldron_tier`.
- **spawns.json:** per forest phase and per cave depth, a list of `item`, `weight`, `max`.
- **upgrades.json:** per line, a list of tiers with `cost` and `effect`.
- **caves.json:** per cave, per depth: `required_tier`, `spawn_table`, `hole_candidates`.
- **customers.json:** burst timing and price multiplier range.

## 8. Build order

Each milestone must be playable before the next.

1. **Walk:** colored square, camera, colliding trees. *Done when* the player walks and bumps into trees.
2. **Clock:** `GameClock` autoload with a debug HUD showing day, phase, time. *Done when* phases change on time and a warning appears before midnight.
3. **Data:** `GameData` loads all JSON and prints it. *Done when* an item can be looked up by id.
4. **Forage:** phase spawn tables, pickup, bag capacity, inventory panel. *Done when* different plants appear in different phases.
5. **Craft and sell:** crafting panel and sell bin. *Done when* a plant becomes a potion becomes gold.
6. **Shop:** open shop, clock running, customer bursts. *Done when* serving customers earns more than the sell bin.
7. **Midnight:** pass-out, per-unit loss, fine, clinic, bed. *Done when* a full night cycle works and the bloom appears before midnight.
8. **Cave:** `CaveDepth` scene, hidden hole, lantern gate, ladder and menu, persistence. *Done when* a player can descend to depth 4, leave by ladder, and find the ladder next day.
9. **Upgrades:** bag and lantern purchases, cauldron tier 2. *Done when* buying the lantern opens depth 1.
10. **Botanary and save:** collection log, save and load. *Done when* closing and reopening keeps everything.
11. **Export and playtest:** Windows build, send to friends, watch them play.

## 9. Starter numbers (placeholders, tune in JSON)

- Day one income target: 100 to 150 gold.
- Bag: capacity 10, then 15, 22, 30.
- Lantern costs: 120, 400, 1100, 2600.
- Plant base prices: 6 to 15 gold. Potion base prices: 35 to 60 gold. Midnight bloom: 40 gold raw.
- Price new upgrades by days of saving: tier 1 at 1 to 2 days, tier 2 at 4 to 6, tier 3 at 10 or more.

## 10. Open decisions

- **Exit cost:** should Get out of cave be free, or cost a flat amount of clock time (suggested: 15 seconds per depth)? Free removes all cave risk.
- **Pass-out grace:** does the player pass out the instant midnight hits, or after a short 5 to 10 second grace?
- **Hole hint:** consider an optional clue (for example a faint sparkle) if friends cannot find holes.
- **Midnight bloom location:** one fixed spot or one of several random spots.

## 11. Parked

Story and NPCs, quests, garden and pots, caves B and C, plant growth, stay-awake buff and its drowsy penalty, shop size upgrades and decorations, 2D lighting, sound, real art.
