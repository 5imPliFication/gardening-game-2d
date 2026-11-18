# Witchwood — connected 32×32 terrain tileset

Original pixel-art ground tiles for Potion Forager, using muted woodland greens, warm earth, plum-gray stone, and moonlit teal water. Every tile is **32×32**, drawn on the native grid with hard pixel edges.

## Look at the set

- **[Surface variations](previews/surface_variations.png):** 12 distinct interior tiles for each of eight surfaces.
- **[Blended surfaces](previews/mixed_surfaces.png):** 12 background/foreground combinations.
- **[Terrain-only example map](previews/terrain_map.png):** joins are visible without decorations.
- **[Decorated woodland example](previews/woodland_map.png):** paths, pond, bridge, courtyard, and cabin floor.
- **[Connection guide](previews/connection_guide.png):** all 47 connection shapes.
- **[Master atlas](terrain_atlas.png):** native-resolution, transparent PNG.

The enlarged review sheets include labels. Actual atlas tiles have **no spacing, labels, or padding**; the Godot atlas uses 32×32 regions starting at `(0, 0)`.

## Contents

| Surface | Character | Variation examples |
| --- | --- | --- |
| Grass | Muted forest-green floor | Bare, sparse, and denser patches; zero, one, two, or three grass tufts |
| Dirt | Warm worn earth | Fine soil grain, little stones, scattered chips |
| Stone | Staggered stone paving | Uncracked stones, chips, fine cracks, highlight changes |
| Gravel | Loose, uneven small pebbles | Different pebble sizes, positions, density, and colors |
| Sand | Warm pale sand | Quiet areas, small wind-ripple marks, scattered grain |
| Water | Cool teal surface | Different ripple clusters and small highlights |
| Wood | Joined horizontal planks | Grain lines, knots, and worn marks; staggered end joints |
| Concrete | Subdued weathered gray | Plain grain, fine cracks, small chips |

Each surface includes:

- **47 topology shapes**, covering isolated patches, ends, straight runs, turns, T-junctions, crosses, external corners, internal corners, and solid interiors.
- **Three texture alternatives for every shape**, sharing exactly the same connecting edges.
- **12 interior variations**, with matching boundaries so they can be freely mixed.

There are **1,224 terrain atlas entries**: `8 × (47 × 3 + 12)`. An additional **14 original project prop tiles** provide four trees, six rocks/stones, and four forageables for map dressing. Total: **1,238 occupied atlas cells**. The prop drawings come from the earlier project-created woodland collection.

These are still tiles. Water ripples are texture variations, not animation frames. No collision or navigation is assigned; the TileSet handles artwork and terrain connections.

## Ready-made mixed surfaces

The [`mixed/`](mixed/) folder includes **12 opaque, precomposed PNG sheets**:

- Grass + Dirt
- Grass + Water
- Gravel + Stone
- Grass + Gravel
- Grass + Sand
- Sand + Water
- Dirt + Gravel
- Dirt + Stone
- Stone + Wood
- Concrete + Grass
- Concrete + Wood
- Sand + Gravel

Filenames use **`background__foreground.png`**. For example, `grass__dirt.png` is a dirt edge/path shape over grass. Each 256×256 sheet has eight columns, 47 connection shapes in manifest order, then 12 foreground interior alternatives: **59 populated cells**, five transparent unused cells.

The Godot brushes use the transparent terrain shapes rather than these flattened sheets. That lets the same foreground brush blend over any of the other seven surfaces, including combinations beyond this ready-made list. The mixed sheets are useful for manual placement or other map editors.

## Start building maps in Godot

The usable Godot resource is already generated at:

**`res://assets/tilesets/woodland/woodland_tileset.tres`**

Open **`res://assets/tilesets/woodland/woodland_example.tscn`** to see an editable example. It contains ordinary `TileMapLayer` nodes and an overview camera. Zoom to 100% in the editor when judging pixel detail; the camera intentionally fits the whole example map when run.

### Painting workflow

1. Create/select a `TileMapLayer` and assign `woodland_tileset.tres` to its **Tile Set** property. The resource already defines tile size and terrain peering bits.
2. Make the ground layer first. Choose **Grass** in the TileMap editor's **Terrains** tab and fill an area larger than your intended playable/viewed region. Interiors automatically choose among the weighted texture variations.
3. Add a `TileMapLayer` above it for paths, using the same TileSet. Choose **Dirt** and the terrain **Connect** painting mode. Paint connected cells; the brush supplies edges, turns, inner corners, and ends.
4. Add further layers for different foreground surfaces. For a pond, paint **Sand** over grass, then **Water** over the sand. Put **Wood** above water for a bridge. For a courtyard, paint **Gravel**, then **Stone** above it.
5. Keep each distinct terrain region on its own layer when it overlaps another material. A material brush connects its own cells; transparent edge pixels reveal the surface below. In code, use `set_cells_terrain_connect(cells, terrain_set_index, 0, false)` so empty space participates in border selection.
6. Add a decoration layer above the terrain and place the prop tiles from the **Tiles** tab if desired.

This layered setup is important: grass and dirt painted with different terrain sets onto the **same** layer do not form a two-material Godot terrain solver. The resource intentionally has one terrain per set, using empty/transparent space at the border, so brushes remain reusable over all backgrounds.

### Terrain set indices

| Set | Terrain name | Terrain index within set |
| ---: | --- | ---: |
| 0 | Grass | 0 |
| 1 | Dirt | 0 |
| 2 | Stone | 0 |
| 3 | Gravel | 0 |
| 4 | Sand | 0 |
| 5 | Water | 0 |
| 6 | Wood | 0 |
| 7 | Concrete | 0 |

All sets use **Match Corners and Sides**. Godot probabilities favor quieter/bare grass variations to keep the ground from becoming uniformly busy. The example uses explicitly chosen variations so it is deterministic.

## Layout and connectivity details

- Master atlas: **1536×864** pixels, **48 columns × 27 rows** of 32×32 cells.
- Top section (tile rows 0–23): eight material blocks. Each block is 12×12 cells, with three runs of 47 connection shapes and three unused cells.
- Tile rows 24–25: the 96 full interior variations, ordered by material and then variation 0–11.
- Tile row 26, columns 0–13: decoration tiles. Other cells on this row are unused.
- Individual material sheets under [`surfaces/`](surfaces/) are **384×416**: the 12×12 topology block followed by a bottom row of 12 full interiors.

The manifest supplies exact atlas coordinates for every populated tile. Connection masks use **N=1, NE=2, E=4, SE=8, S=16, SW=32, W=64, NW=128**. Diagonal bits are relevant only when their two adjacent cardinal neighbors are present, giving the standard **47 blob shapes**. Mask 0 is an isolated patch; mask 255 is a filled interior.

Natural surfaces use rounded, lightly irregular contours; wood/concrete use tighter, cleaner bevels. A common texture-edge collar allows different interior patterns to meet without a color jump. Edge shading is calculated from the terrain silhouette and does not outline connected tile-cell boundaries.

## Files and regeneration

### Art/export folder

```text
art/woodland-tileset/
  terrain_atlas.png
  manifest.json
  surfaces/                 # 8 material PNGs
  mixed/                    # 12 precomposed pair sheets
  previews/                 # labeled sheets and example maps
  generate_tileset.py       # editable artwork, palettes and example layout
  verify_tileset.py         # independent pixel/topology checks
```

### Godot project folder

```text
gardening-game-2d/assets/tilesets/woodland/
  terrain_atlas.png
  terrain_manifest.json
  woodland_tileset.tres
  woodland_example.tscn
  build_tileset.gd
  verify_tileset.gd
```

Requires Python 3, Pillow, and Godot 4.7. Run from the repository root:

```sh
python3 art/woodland-tileset/generate_tileset.py
python3 art/woodland-tileset/verify_tileset.py
godot --headless --editor --path gardening-game-2d --quit
godot --headless --path gardening-game-2d --script res://assets/tilesets/woodland/build_tileset.gd
godot --headless --path gardening-game-2d --script res://assets/tilesets/woodland/verify_tileset.gd
```

The Python generator reuses the 14 earlier original prop PNGs from `art/spooky-cute-keyframes/sprites/`; keep those source files available for regeneration. The exported PNGs and `.tres` are ready to use without running the generators.

## Verification performed

- All 47 masks and all three shape alternatives exist for each surface.
- All 96 interior variants are visually distinct, with opaque, matching perimeter pixels.
- Shape alternatives keep identical silhouettes and boundary samples.
- **2,048 exhaustive connected-pair arrangements**, covering horizontal and vertical connections, pass **16,384 exact RGBA seam comparisons** across all eight surfaces.
- Every precomposed mixed tile matches its documented background/foreground composition.
- Godot loads all 1,238 atlas cells with correct terrain peering bits.
- All **376 Godot brush cases** (47 shapes × 8 materials) choose the expected center topology and retain every requested painted cell.
- Eight filled-region checks confirm that Godot actually selects multiple interior texture variations when painting each surface.
- The editable example scene loads successfully.

## Credits

Original terrain artwork and generation instructions created for this project with OpenAI's coding assistant. The 14 prop tiles reuse earlier original project artwork. No downloaded terrain pack or third-party character asset is included in this tileset or its example. Pillow handles image creation; preview labels use system DejaVu Sans when available, without bundling font files. See the repository-root `CREDITS.txt`.
