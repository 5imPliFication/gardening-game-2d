# Witchwood Forager — spooky-cute starter art

Original pixel-art draft for **Potion Forager**, created for this project.

## Review

- **`preview.png`** — labeled contact sheet at 5× nearest-neighbor scale.
- **`walk_down_preview.gif`**, **`walk_left_preview.gif`**, **`walk_right_preview.gif`**, **`walk_up_preview.gif`** — enlarged walk-cycle previews.
- **`sprites/`** — individual transparent **32×32 RGBA PNGs**.
- **`player_sheet.png`** — transparent 96×128 sheet, 32×32 cells. Rows: down, left, right, up. Columns: idle, walk 1, walk 2. Suggested cycle: walk 1 → idle → walk 2 → idle, about 0.17 seconds per frame.
- **`atlas.png`** — transparent atlas, eight 32×32 cells per row. Order: player directions down/left/right/up (idle, walk 1, walk 2 each), tree, dew herb, sun plant, moon mushroom, midnight bloom, dew potion, sun potion, moon potion, bottle, water, sugar. Final unused cell is transparent.

## Art direction

Slightly overhead, top-down RPG view; chunky silhouettes; dark plum outlines; muted teal foliage; lilac field hat; warm peach skin; amber and moonlit-pink accents. The gardener carries a little satchel and wears teal overalls. All artwork is drawn directly on the pixel grid, with no antialiasing or downsampled artwork.

The tree fits entirely inside one 32×32 cell. Forageables can serve as both world pickups and item icons. Potions use different bottle silhouettes and label symbols as well as different colors.

## Contents

- 12 gardener frames: four directions, each with an idle and two walk poses.
- 1 witchwood tree.
- 4 forageables matching the current `items.json`: Dew Herb, Sun Plant, Moon Mushroom, Midnight Bloom.
- 3 potions: Dew, Sun, Moon.
- 3 crafting bases: Bottle, Water, Sugar.

**23 individual sprites total.** These are review assets; gameplay scenes and item data have not been wired to them.

## Editing and regeneration

The editable source is `generate_sprites.py`, including the shared hexadecimal palette. Requires Python 3 and Pillow (9.1 or newer):

```sh
python3 art/spooky-cute-starter/generate_sprites.py
```

This regenerates the PNGs and preview GIFs in this folder. Use nearest-neighbor filtering and integer scaling when displaying the sprites.

## Credits

Original artwork created for this project with OpenAI's coding assistant using custom pixel-grid drawing instructions. No downloaded, stock, or third-party sprite assets were used. Pillow is the image-generation tool; the preview labels use the system DejaVu Sans font when available (font files are not bundled).
