# Witchwood Forager — expanded character & woodland art

Second review collection for Potion Forager. All individual frames are original **32×32 transparent RGBA PNGs**, using the first draft's plum, teal, lavender, and amber palette. Artwork is drawn at native resolution with hard pixel edges. The source and first draft live alongside each other in `art/`.

## Start here

| Preview | Contents |
| --- | --- |
| [`characters_preview.png`](characters_preview.png) | Male/female designs, all directions, and animation-state examples |
| [`previews/characters_walk.gif`](previews/characters_walk.gif) | Both characters walking in four directions |
| [`previews/characters_idle.gif`](previews/characters_idle.gif) | Standing breathing, blinking, looking around, and touching the hat |
| [`previews/characters_rest.gif`](previews/characters_rest.gif) | Seated rest with closed eyes, breathing, and slight hat movement |
| [`previews/character_frames.png`](previews/character_frames.png) | Every down-facing animation frame, arranged for pose review |
| [`environment_preview.png`](environment_preview.png) | All trees, plants, rocks, and stones |
| [`previews/environment_animated.gif`](previews/environment_animated.gif) | Swaying foliage, twinkling plants, and the pulsing rune rock |

Preview backgrounds, text, and frame-progress marks are review aids and are not part of the transparent sprite images. The environmental GIF uses a shared 200ms demo beat; exact suggested per-asset timings are in the manifest.

## Characters

**Male:** cropped hair, short field cap with a leaf pin, scarf, vest/overalls, and satchel.

**Female:** long braid, broad flower-trimmed hat, flared field coat with a belt, scarf, and satchel.

Both have the same scale, skin/hair color family, shared clothing palette, and matching animation timing. Their silhouettes and outfit construction differ, rather than relying on a recolor.

Each character has **four directions** (down, left, right, up) and three **eight-frame looping states**:

| State | Motion | Frame durations in milliseconds |
| --- | --- | --- |
| `walk` | Opposing leg arcs, arm counter-swing, body bounce, secondary hat/braid/bag movement | 100 × 8 (10 fps) |
| `idle` | Standing breath, blink, glance, occasional hat touch | 650, 250, 300, 130, 650, 220, 300, 650 |
| `rest` | Seated break, relaxed knees, breathing, closed eyes | 650, 350, 350, 150, 650, 350, 350, 650 |

Resting is a **separate seated state**; idle is standing. These loops do not include stand-to-sit or sit-to-stand transitions. Up-facing views naturally hide facial gestures. Left/right artwork is mirrored, including accessories.

There are **192 character frames** in total. All frames use a consistent 32×32 canvas with a nominal ground anchor at `(16, 29)`; lifted feet intentionally move inside the cell during a stride.

### Files and sheets

- Individual frames: `sprites/player/{male|female}/{walk|idle|rest}/{direction}/00.png` through `07.png`.
- Directional strips: `sheets/player/{gender}/{state}/{direction}.png` — **256×32**, eight cells in playback order.
- All-direction sheets: `sheets/player/{gender}/{state}_4dir.png` — **256×128**, eight columns and four direction rows: **down, left, right, up**.

## Woodland collection

### Four trees — eight frames each

- **Witchwood:** rounded teal canopy and pink-lilac buds.
- **Moon Pine:** layered evergreen silhouette with pale moonlit tips.
- **Lavender Willow:** hanging purple foliage and pink leaf ends.
- **Silver Birch:** clustered teal crown, pale trunk, dark bark markings.

Canopies sway gently on a **1.6-second loop**; roots and lower trunks stay fixed. All trees fit within a single 32×32 frame.

### Four forageables — eight frames each

- **Dew Herb:** gentle sway and moving dew glints.
- **Sun Plant:** stem/flower sway with a little blink.
- **Moon Mushroom:** cap sway and a subtle highlight twinkle.
- **Midnight Bloom:** petal sway, pulsing center, and changing sparkles.

Plant loop duration: **1.44 seconds**. Root bases stay fixed. Static plant PNGs are included for inventory icons.

### Six rocks and stones

- Boulder
- Mossy Boulder
- Rune Rock, plus a separate eight-frame **1.76-second glow loop**
- Flat Stone
- Pebble Cluster
- Small Stone

Ordinary rocks remain static. The rune animates its markings rather than moving the rock.

### Files

- Animated tree frames: `sprites/environment/trees/{variant}/00.png` through `07.png`.
- Animated plant frames: `sprites/plants/{plant}/00.png` through `07.png`.
- Rock stills: `sprites/environment/rocks/{variant}.png`.
- Rune animation: `sprites/environment/rocks/rune_glow/00.png` through `07.png`.
- Each environment animation also has an eight-cell strip under `sheets/`, using the same relative category path.

## Manifest and totals

[`manifest.json`](manifest.json) lists every individual sprite and every animation strip with ordered frame paths, frame size, anchor, loop flag, and per-frame durations. Paths are relative to this folder.

- **33 eight-frame loops:** 24 character loops + 4 trees + 4 plants + 1 rune rock.
- **264 animated frames**, plus **11 stills** (6 rocks, 4 plant icons, 1 original tree pose).
- **275 individual transparent 32×32 PNGs**.
- **33 directional/environment strips** and **6 combined character sheets**.

Animation times are art playback suggestions. The art remains a review collection; the game's scene and item configuration is unchanged.

## Regeneration and checks

Requires Python 3 and Pillow >=9.1. Keep the sibling first-draft generator in place: this generator imports its palette, pixel drawing helpers, and plant designs without rewriting the first draft.

```sh
python3 art/spooky-cute-expanded/generate_sprites.py
```

The command regenerates the collection and verifies:

- Every manifest-listed sprite exists and is 32×32 RGBA with binary transparency.
- The manifest covers all generated individual sprite PNGs.
- Each animation has eight frames and valid timing data, with at least four distinct visual poses.
- Source images match every cell of their animation strips and combined character sheets.
- Animated sprites have no occupied pixels below their intended ground bounds.
- All four animated review GIFs contain eight frames.

Use nearest-neighbor filtering and integer display scales.

## Credits

Original artwork created for this project with OpenAI's coding assistant using custom pixel-grid drawings. No third-party art, stock sprites, or downloaded asset packs were added. Pillow generates the images; preview labels use the system DejaVu Sans font when available. Font files are not bundled.
