# Adventurers — woodland recolor & waist-lantern variants

Adaptations of the user-supplied **The Female Adventurer - Free** and **The Male adventurer - Free** packs. Original animation drawings, pixel positions, proportions, and shading details are retained. The original folders are the editable inputs and are not overwritten.

## Review

- [Original / recolored / waist-lantern comparison](comparison.png)
- [Walking with lanterns](previews/lantern_walk.gif)
- [Idle with lanterns](previews/lantern_idle.gif)
- [Dash with lanterns, native cells](previews/lantern_dash.gif)
- [Falling/death with lanterns, native cells](previews/lantern_death.gif)

Female is above male in the animated previews. Backgrounds and labels appear only in review images.

## Palette changes

Small, explicit shading-ramp substitutions bring the assets toward the game's spooky-cute woodland colors:

- Black outlines become deep plum-black.
- Green clothing shifts toward muted woodland teal.
- The male character's blue clothing and red scarf become subdued teal and dusty lilac.
- Magenta hair/shadows shift toward softer plum-brown tones; the male hair retains its purple character.
- Skin highlights become slightly warmer, with less saturated pink shadows.
- Gray details gain a restrained lilac tint; bright cloth stays warm and pale.

This is a palette adaptation, not an animation redraw. Transparent pixels retain their original RGBA values, and recolored images have exactly the source alpha channel. [`manifest.json`](manifest.json) records every hexadecimal substitution.

## Waist lantern

The alternate variant adds a small **amber-glass lantern with a pale warm flame, brass trim, and a leather belt strap**. It is attached to the character's right hip, with facing-dependent positioning and far-side body occlusion. The attachment follows the torso's animation beat; walking/dashing introduces a restrained one-pixel swing of the lantern body below its fixed handle.

Falling/death poses have separate attachment rules for inverted and horizontal frames. The flame is drawn into the sprite; no game lighting is configured by these assets.

Each character animation is available as:

1. **`recolored`** — palette-only character.
2. **`lantern`** — palette-adjusted character with lantern already composited.
3. **`lantern_layers`** — transparent, aligned accessory/strap layer, useful for equipment toggles. It already includes the appropriate body occlusion for its matching frame.

## Native source-compatible sheets

The imported packs use **48×64 cells**, eight frames per direction. Outputs preserve the original sheet filenames, dimensions, frame positions, and capitalization:

```text
native/female/recolored/Idle/Idle_Down.png
native/female/lantern/Idle/Idle_Down.png
native/female/lantern_layers/Idle/Idle_Down.png
native/male/recolored/Walk/walk_down.png
native/male/lantern/Walk/walk_down.png
native/male/lantern_layers/Walk/walk_down.png
```

- Directional strips: **384×64** (8 columns).
- Combined state atlases: **384×384** (8 columns × 6 rows).
- States: **Idle, Walk, Dash, Death**.
- Atlas rows, as labeled in the original packs: **down, left_down, left_up, up, right_up, right_down**.
- Dust and shadow support images are recolored under each character's `recolored/` folder; they do not receive lanterns. Both character variants can use these support files.
- The instructional `frame dimensions.png` images remain in the source folders.

The female Walk combined atlas differs at the pixel level from its separate directional strips in the supplied pack. Both are adapted independently, preserving their respective original drawings. The 32×32 outputs below use the separate directional strips.

## Aligned 32×32 game exports

Idle and walking fit losslessly into a fixed **32×32 crop**, without resizing, resampling, or per-frame recentering:

- Crop within each native cell: **`(8, 14)` through `(40, 46)`**, right/bottom exclusive.
- Source ground reference `(24, 43)` maps to **`(16, 29)`**.
- All original visible pixels and all visible lantern/strap pixels are retained.
- Individual frames: `32x32/{female|male}/{variant}/{idle|walk}/{direction}/00.png` through `07.png`.
- Eight-frame strips: `32x32/{female|male}/{variant}/{idle|walk}_{direction}.png`, **256×32**.

For example:

```text
32x32/female/recolored/walk/down/00.png
32x32/female/lantern/walk/down/00.png
32x32/female/lantern_layers/walk/down/00.png
32x32/male/lantern/walk_down.png
```

Dash and falling/death retain native cells: their movement extends beyond the shared 32×32 crop, so a fixed crop would cut off artwork. In Godot, native and cropped sprites can share a ground reference by offsetting their textures relative to the anchors above. Use nearest-neighbor filtering and integer scale.

There are **87 recolored source images**, plus **56 lantern character sheets**, **56 accessory-layer sheets**, **576 individual 32×32 frames** (including layers), and **72 cropped animation strips**.

## Playback metadata

Source PNG files have no embedded animation speed. Preview timings are suggestions, not changes to the original animation artwork:

| State | Time per frame | Preview rate | Frames |
| --- | ---: | ---: | ---: |
| Idle | 160 ms | 6.25 fps | 8 |
| Walk | 100 ms | 10 fps | 8 |
| Dash | 80 ms | 12.5 fps | 8 |
| Death | 140 ms | approximately 7.14 fps | 8 |

Death GIFs loop for review; the animation should normally play once in-game. `manifest.json` lists native outputs, original files, direction metadata, crop and anchor coordinates, 32px export conventions, and palette substitutions.

## Regeneration and verification

Requires Python 3 and Pillow. From the repository root:

```sh
python3 art/adventurers-spooky-cute/adapt_sprites.py
```

The generator reads the two supplied folders and writes only this adaptation folder. It verifies source hashes remain unchanged, native dimensions and palette-only alpha masks match the originals, accessory layers reproduce their composited variants, original silhouettes are not erased by the lantern, 32px crops preserve all visible pixels, individual frames match strip cells, and preview frame counts/timings are correct.

These are review/export assets. Gameplay scenes and item data are not wired to these sheets.

## Credits

Original character artwork: the user-supplied **The Female Adventurer - Free** and **The Male adventurer - Free** packs. The supplied folders do not identify the original artist/publisher or include a source URL; no author name is guessed here.

Palette adaptations, lantern/strap drawings, compositing, and exports were made for this project with OpenAI's coding assistant. See the repository-root [`CREDITS.txt`](../../CREDITS.txt). Pillow handles image processing; preview text uses system DejaVu Sans when available, without bundling font files.
