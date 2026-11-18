# Witchwood — redrawn keyframe collection (current)

The current revision uses **eight separately drawn poses for walking and environment animation**, and four poses for slower idle/rest loops. Each pose is drawn directly onto a fresh 32×32 canvas. Leaf and petal contours, bent knees/elbows, dress hems, ponytails, and branches are specified per pose. No raster rows or columns are shifted, and there is no image warping or motion interpolation.

The spooky-cute palette, four-direction views, four tree variants, four forageables, and six rock/stone variants carry forward. The character designs and walking cycle have been redrawn.

## Updated characters

- **Female:** twin chestnut ponytails with prominent lilac ribbons, a headband, puff sleeves, a teal pinafore dress with a scalloped lilac hem, a pale apron, waist bow, lavender tights, and boots.
- **Male:** exposed tousled chestnut hair with a swept quiff, teal field vest, mint shirt, lilac neckerchief, belted trousers, and boots.

The hats have been replaced by visible hairstyles so the differences read at native size. Both characters retain the shared plum, teal, lilac, and warm-brown color family. Ponytails and bags have delayed follow-through during walking.

## Review the motion

- [Walking GIF](previews/characters_walk.gif) — both characters, four directions.
- [Standing idle GIF](previews/characters_idle.gif) — breathing and blinking.
- [Seated rest GIF](previews/characters_rest.gif) — relaxed arm/chest poses.
- [Woodland GIF](previews/environment_animated.gif) — foliage drawings and rune glow.
- [Character designs](characters_preview.png) — both characters in all four directions.
- [Character pose breakdown](character_frames.png) — down-facing walking, idle, and seated-rest drawings.
- [Walk breakdown](previews/walk_frames.png) — every walking frame in every direction.
- [Woodland pose breakdown](environment_frames.png) — all eight drawings for every tree and plant.
- [Environment contact sheet](environment_preview.png) — includes all six rocks/stones.

Review GIFs include labels, dark backgrounds, and a frame-progress indicator. The actual sprite PNGs are transparent and have none of those review aids.

## Simple, consistent timing

Every frame in a given loop has the **same duration**. Playback is deliberately low-frame-rate:

| Animation | Drawings | Time per frame | Playback rate | Loop duration |
| --- | ---: | ---: | ---: | ---: |
| Walking | 8 | 100 ms | 10 fps | 0.8 s |
| Standing idle | 4 | 400 ms | 2.5 fps | 1.6 s |
| Seated rest | 4 | 500 ms | 2 fps | 2 s |
| Trees and plants | 8 | 160 ms | 6.25 fps | 1.28 s |
| Rune glow | 8 | 160 ms | 6.25 fps | 1.28 s |

Walk order: left contact → left down → left passing → left up → right contact → right down → right passing → right up. Knees bend during the passing poses; supporting legs reach the ground; arms counter-swing; the torso lowers on weight transfer and rises before the next contact. Side-view legs are drawn far-first for readable overlap.

Foliage has dedicated approach and recovery drawings around the right and left bends, keeping the pixel-art silhouettes while reducing the abrupt changes of the previous four-frame cycle. Ordinary rocks remain static; rune animation changes the marking brightness, repeating some brightness levels as the glow rises and falls.

The animation rate is independent of the game's movement/render frame rate. When these are integrated, player movement can remain continuous while the sprite changes only on its animation beat.

## Sprite layout

Every individual frame is **32×32 RGBA**, with binary transparency and no antialiasing. Direction order is **down, left, right, up**. Left-facing poses mirror the right-facing drawings, including accessories.

- Character frames: `sprites/player/{male|female}/{walk|idle|rest}/{direction}/00.png` onward. Walking ends at `07.png`; idle/rest end at `03.png`.
- Character directional strips: `sheets/player/{gender}/{state}/{direction}.png` — walking **256×32**, idle/rest **128×32**.
- Combined character sheets: `sheets/player/{gender}/{state}_4dir.png` — walking **256×128**, idle/rest **128×128**; four direction rows in each.
- Trees: `sprites/environment/trees/{variant}/00.png` through `07.png`.
- Plants: `sprites/plants/{plant}/00.png` through `07.png`.
- Static plant icons: `sprites/plants/{plant}.png`.
- Rocks and stones: `sprites/environment/rocks/{variant}.png`.
- Rune glow: `sprites/environment/rocks/rune_glow/00.png` through `07.png`.
- Each environment loop also has an eight-cell **256×32** strip under `sheets/` with the corresponding category path.

The nominal animation anchor is `(16, 29)`; plant roots and lower tree trunks remain identical between frames. Resting is seated; sit-down/get-up transitions are not included in this review set.

**Totals:** 33 loops (17 eight-frame and 16 four-frame), 200 animation frames, 10 static sprites, **210 individual PNGs**, 33 animation strips, and 6 combined character sheets.

[`manifest.json`](manifest.json), version **4**, lists every individual sprite and strip, ordered pose names, frame durations, anchors, and looping metadata. All paths are relative to this folder. Read each animation's frame count from the manifest: this revision intentionally mixes eight-frame walking/environment and four-frame idle/rest loops.

## Editable source and regeneration

Requires Python 3 and Pillow >=9.1:

```sh
python3 art/spooky-cute-keyframes/generate_sprites.py
```

Keep the sibling `spooky-cute-expanded/` and `spooky-cute-starter/` generator sources in place. This generator reuses their palette, basic drawing/preview helpers, and still rock designs. Their character-animation and foliage-displacement routines are not used, and earlier artwork is not regenerated.

The generator verifies distinct source drawings and multiple redrawn silhouettes after normalizing their positions (except the intentionally color-only rune glow), fixed plant/tree ground pixels, consistent per-loop timings, image dimensions/transparency, manifest coverage, every sheet cell, GIF frame counts, and actual GIF frame durations. Idle/rest can include internal gestures without changing the outer silhouette.

This is a review collection of artwork. Timing metadata is for asset playback; it does not change gameplay data.

## Credits

Original project artwork created with OpenAI's coding assistant using explicit pixel-grid drawing instructions. No third-party art was added. Pillow generates the images; review text uses the system DejaVu Sans font when available, without bundling the font.
