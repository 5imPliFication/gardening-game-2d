"""Original seamless 32px terrain art, topology, engine data and review maps."""

import json
import random
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parent
REPO = ROOT.parent.parent
GAME = REPO / "gardening-game-2d" / "assets" / "tilesets" / "woodland"
SIZE = 32
N, NE, E, SE, S, SW, W, NW = (1 << i for i in range(8))
OFFSETS = ((0, -1, N), (1, -1, NE), (1, 0, E), (1, 1, SE),
           (0, 1, S), (-1, 1, SW), (-1, 0, W), (-1, -1, NW))
MATERIALS = {
    "grass": ["#426656", "#395c4d", "#4a705b", "#6b9970", "#304c41"],
    "dirt": ["#967463", "#896555", "#a5826b", "#bc987d", "#71584f"],
    "stone": ["#7d7d87", "#686c78", "#90919a", "#aaa7ad", "#555b67"],
    "gravel": ["#777b77", "#656e69", "#92988a", "#adb09b", "#525f5b"],
    "sand": ["#c7b18a", "#b89e7d", "#d6bf94", "#e6d1a8", "#9c896d"],
    "water": ["#417e8a", "#366d80", "#55949c", "#87bcb9", "#305c73"],
    "wood": ["#977665", "#816357", "#ac8971", "#c3a080", "#665250"],
    "concrete": ["#96958f", "#868783", "#a5a39a", "#bbb4a6", "#737b78"],
}
GRASS_COUNTS = (0, 1, 2, 3, 0, 2, 1, 3, 0, 2, 3, 1)
PAIRS = (("grass", "dirt"), ("grass", "water"), ("gravel", "stone"),
         ("grass", "gravel"), ("grass", "sand"), ("sand", "water"),
         ("dirt", "gravel"), ("dirt", "stone"), ("stone", "wood"),
         ("concrete", "grass"), ("concrete", "wood"), ("sand", "gravel"))
TILES = []
IMAGES = {}
BASES = {}
SHAPES = {}
MAPS = []


def normalized(mask):
    for diagonal, a, b in ((NE, N, E), (SE, E, S), (SW, S, W), (NW, W, N)):
        if not (mask & a and mask & b):
            mask &= ~diagonal
    return mask


MASKS = sorted({normalized(mask) for mask in range(256)})


def save(image, relative):
    path = ROOT / relative
    path.parent.mkdir(parents=True, exist_ok=True)
    image.save(path)


def rgb(color):
    return tuple(bytes.fromhex(color[1:]))


def seam_locked(image, reference):
    # A 3px common edge collar keeps any pair of texture variants compatible.
    for box in ((0, 0, 32, 3), (0, 29, 32, 32), (0, 0, 3, 32), (29, 0, 32, 32)):
        image.paste(reference.crop(box), box[:2])


def shared_texture(material):
    palette = MATERIALS[material]
    image = Image.new("RGBA", (32, 32), palette[0])
    d = ImageDraw.Draw(image)
    rng = random.Random(819 + list(MATERIALS).index(material))
    # Quiet, low-contrast grain. No full-tile border is drawn.
    for _ in range(46):
        x, y = rng.randrange(32), rng.randrange(32)
        d.point((x, y), fill=palette[1 if rng.random() < 0.5 else 2])
    if material == "stone":
        for row in range(-1, 3):
            for col in range(-1, 3):
                x, y = col * 16 + (row % 2) * 8, row * 16
                d.rounded_rectangle((x + 1, y + 1, x + 15, y + 14), radius=3, fill=palette[0], outline=palette[4])
                d.line((x + 4, y + 2, x + 11, y + 2), fill=palette[2])
    elif material == "wood":
        for row in range(2):
            y = row * 16
            d.line((0, y, 31, y), fill=palette[4])
            d.line((0, y + 1, 31, y + 1), fill=palette[2])
            x = (row % 2) * 16
            d.line((x, y + 1, x, y + 15), fill=palette[4])
            d.line((4, y + 8, 12, y + 8), fill=palette[1])
            d.line((18, y + 11, 27, y + 11), fill=palette[2])
    elif material == "water":
        d.line((0, 10, 4, 10), fill=palette[2])
        d.line((26, 10, 31, 10), fill=palette[2])
        d.line((12, 0, 15, 0), fill=palette[1])
    # Opposite border samples are exact matches, including all four corners.
    image.paste(image.crop((0, 0, 1, 32)), (31, 0))
    image.paste(image.crop((0, 0, 32, 1)), (0, 31))
    return image


def texture(material, variant):
    reference = shared_texture(material)
    image = reference.copy()
    d = ImageDraw.Draw(image)
    p = MATERIALS[material]
    rng = random.Random(1439 + list(MATERIALS).index(material) * 619 + variant * 137)
    if material == "grass":
        for _ in range(12 + variant % 5):
            x, y = rng.randrange(4, 27), rng.randrange(5, 27)
            d.line((x, y, x + 1, y - 1), fill=p[1 if rng.random() < 0.5 else 2])
        for _ in range(GRASS_COUNTS[variant % 12]):
            x, y = rng.randrange(6, 26), rng.randrange(8, 26)
            d.line([(x - 2, y - 2), (x - 1, y), (x + 1, y), (x + 2, y - 3)], fill=p[3])
            d.line((x, y, x, y - 4), fill=p[2])
    elif material == "dirt":
        for _ in range(6 + variant % 5):
            x, y = rng.randrange(4, 27), rng.randrange(4, 27)
            d.line((x, y, x + rng.randrange(1, 3), y), fill=rng.choice(p[1:3]))
        for _ in range(variant % 4):
            x, y = rng.randrange(6, 25), rng.randrange(6, 25)
            d.ellipse((x, y, x + 2, y + 1), fill=p[4])
            d.point((x, y), fill=p[3])
    elif material == "stone":
        if variant % 3:
            x, y = rng.randrange(6, 22), rng.randrange(6, 23)
            d.line([(x, y), (x + 2, y + 2), (x + 1, y + 4)], fill=p[4])
        for _ in range(3 + variant % 3):
            x, y = rng.randrange(5, 26), rng.randrange(5, 26)
            d.line((x, y, x + 2, y), fill=p[2])
    elif material == "gravel":
        for _ in range(12 + variant % 5):
            x, y = rng.randrange(4, 26), rng.randrange(4, 26)
            w = rng.choice((1, 2, 2, 3))
            d.polygon([(x, y + 1), (x + 1, y), (x + w, y + 1), (x + w, y + 2), (x + 1, y + 3)], fill=rng.choice(p[1:4]))
            d.point((x + 1, y), fill=p[3])
    elif material == "sand":
        for _ in range(3 + variant % 5):
            x, y = rng.randrange(5, 24), rng.randrange(5, 27)
            d.line([(x, y), (x + 2, y - 1), (x + 5, y - 1)], fill=p[1])
            if variant % 3:
                d.line((x + 1, y + 1, x + 3, y + 1), fill=p[2])
    elif material == "water":
        for _ in range(2 + variant % 4):
            x, y = rng.randrange(5, 23), rng.randrange(5, 26)
            d.line([(x, y), (x + 2, y - 1), (x + 5, y - 1), (x + 6, y)], fill=p[2])
            d.line((x + 2, y, x + 4, y), fill=p[3] if variant % 3 else p[1])
    elif material == "wood":
        for _ in range(2 + variant % 4):
            x, y = rng.randrange(5, 22), rng.choice((6, 10, 21, 25))
            d.line([(x, y), (x + 3, y - 1), (x + 7, y)], fill=p[1])
        if variant % 3 == 1:
            x, y = rng.randrange(7, 22), rng.choice((7, 23))
            d.ellipse((x, y - 1, x + 3, y + 1), outline=p[4])
    else:
        for _ in range(5 + variant % 5):
            x, y = rng.randrange(5, 27), rng.randrange(5, 27)
            d.point((x, y), fill=rng.choice(p[1:4]))
        if variant % 3 == 1:
            x, y = rng.randrange(8, 22), rng.randrange(8, 20)
            d.line([(x, y), (x - 1, y + 3), (x + 1, y + 5), (x, y + 7)], fill=p[1])
            d.point((x + 2, y + 5), fill=p[2])
    seam_locked(image, reference)
    return image


def shape(material, mask):
    alpha = Image.new("L", (32, 32))
    hard = material in ("wood", "concrete")
    radius = 3 if hard else 6
    profile = ((3,) * 16 if hard else (6, 6, 6, 6, 5, 5, 6, 7, 7, 6, 6, 5, 5, 6, 6, 6))
    # Four quarter drawings implement the complete 47-blob vocabulary.
    quarters = ((False, False, N, W, NW), (True, False, N, E, NE),
                (True, True, S, E, SE), (False, True, S, W, SW))
    for flip_x, flip_y, vertical, horizontal, diagonal in quarters:
        a, b, corner = bool(mask & vertical), bool(mask & horizontal), bool(mask & diagonal)
        for v in range(16):
            for u in range(16):
                if a and b:
                    inside = corner or u * u + v * v >= radius * radius
                elif a:
                    inside = u >= profile[v]
                elif b:
                    inside = v >= profile[u]
                else:
                    inside = u >= profile[v] and v >= profile[u]
                    # Rounded external corners; square boards have small bevels.
                    round_r = 1 if hard else 5
                    center = radius + round_r
                    if u < center and v < center:
                        inside = inside and (u - center) ** 2 + (v - center) ** 2 <= round_r ** 2
                if inside:
                    alpha.putpixel((31 - u if flip_x else u, 31 - v if flip_y else v), 255)
    return alpha


def terrain_tile(material, mask, variant):
    image = texture(material, variant)
    alpha = SHAPES[material, mask]
    pixels = image.load()
    p = MATERIALS[material]
    def outside(px, py):
        clamped_x = max(0, min(31, px))
        clamped_y = max(0, min(31, py))
        return not alpha.getpixel((clamped_x, clamped_y))
    # Edge-clamped alpha avoids painting a false rim on tile-cell seams.
    for y in range(32):
        for x in range(32):
            if not alpha.getpixel((x, y)):
                pixels[x, y] = (0, 0, 0, 0)
                continue
            rim = any(outside(x + dx, y + dy) for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)))
            if rim:
                pixels[x, y] = rgb(p[3] if material == "water" else p[4]) + (255,)
            elif any(outside(x + dx, y + dy) for dx, dy in ((2, 0), (-2, 0), (0, 2), (0, -2))):
                pixels[x, y] = rgb(p[2]) + (255,)
    return image


def build_art():
    atlas = Image.new("RGBA", (1536, 864))
    for material_index, material in enumerate(MATERIALS):
        block_x, block_y = (material_index % 4) * 12, (material_index // 4) * 12
        sheet = Image.new("RGBA", (384, 416))
        for mask in MASKS:
            SHAPES[material, mask] = shape(material, mask)
        for variant in range(3):
            for index, mask in enumerate(MASKS):
                slot = variant * 47 + index
                coord = (block_x + slot % 12, block_y + slot // 12)
                image = terrain_tile(material, mask, variant)
                IMAGES[material, mask, variant] = image
                atlas.paste(image, (coord[0] * 32, coord[1] * 32))
                sheet.paste(image, ((slot % 12) * 32, (slot // 12) * 32))
                TILES.append({"material": material, "terrain_set": material_index, "mask": mask,
                              "variant": variant, "atlas_coords": list(coord), "kind": "terrain",
                              "probability": 0.3 if mask == 255 else 1.0})
        for variant in range(12):
            slot = material_index * 12 + variant
            coord = (slot % 48, 24 + slot // 48)
            image = texture(material, variant)
            BASES[material, variant] = image
            atlas.paste(image, (coord[0] * 32, coord[1] * 32))
            sheet.paste(image, (variant * 32, 384))
            record = {"material": material, "terrain_set": material_index, "mask": 255,
                      "variant": variant, "atlas_coords": list(coord), "kind": "interior",
                      "probability": 3.0 if material == "grass" and GRASS_COUNTS[variant] == 0 else 1.0}
            if material == "grass":
                record["grass_tufts"] = GRASS_COUNTS[variant]
            TILES.append(record)
        save(sheet, Path("surfaces") / f"{material}.png")
    # Reuse only original project-created prop drawings, not imported characters.
    props_root = ROOT.parent / "spooky-cute-keyframes" / "sprites"
    props = [(f"tree_{name}", props_root / "environment" / "trees" / name / "00.png")
             for name in ("witchwood", "moon_pine", "lavender_willow", "silver_birch")]
    props += [(name, props_root / "environment" / "rocks" / f"{name}.png")
              for name in ("boulder", "mossy_boulder", "rune_rock", "flat_stone", "pebble_cluster", "small_stone")]
    props += [(name, props_root / "plants" / f"{name}.png")
              for name in ("dew_herb", "sun_plant", "moon_mushroom", "midnight_bloom")]
    for index, (name, path) in enumerate(props):
        with Image.open(path) as raw:
            image = raw.convert("RGBA")
        coord = ((96 + index) % 48, 24 + (96 + index) // 48)
        atlas.paste(image, (coord[0] * 32, coord[1] * 32))
        TILES.append({"name": name, "kind": "decoration", "atlas_coords": list(coord)})
        IMAGES[name] = image
    save(atlas, Path("terrain_atlas.png"))
    GAME.mkdir(parents=True, exist_ok=True)
    atlas.save(GAME / "terrain_atlas.png")
    for background, foreground in PAIRS:
        sheet = Image.new("RGBA", (256, 256))
        entries = []
        for index, mask in enumerate(MASKS):
            image = BASES[background, 0].copy()
            image.alpha_composite(IMAGES[foreground, mask, 0])
            coord = (index % 8, index // 8)
            sheet.paste(image, (coord[0] * 32, coord[1] * 32))
            entries.append({"atlas_coords": list(coord), "mask": mask})
        for variant in range(12):
            index = 47 + variant
            sheet.paste(BASES[foreground, variant], ((index % 8) * 32, (index // 8) * 32))
        save(sheet, Path("mixed") / f"{background}__{foreground}.png")


def cell_mask(cells, x, y):
    return normalized(sum(bit for dx, dy, bit in OFFSETS if (x + dx, y + dy) in cells))


def render_layer(canvas, material, cells, rng):
    records = {(r["mask"], r["variant"]): r for r in TILES if r.get("material") == material and r["kind"] == "terrain"}
    interiors = [r for r in TILES if r.get("material") == material and r["kind"] == "interior"]
    output = []
    for x, y in sorted(cells):
        mask = cell_mask(cells, x, y)
        variant = rng.randrange(12 if mask == 255 else 3)
        image = BASES[material, variant] if mask == 255 else IMAGES[material, mask, variant]
        record = interiors[variant] if mask == 255 else records[mask, variant]
        canvas.alpha_composite(image, (x * 32, y * 32))
        output.append({"cell": [x, y], "atlas_coords": record["atlas_coords"]})
    return {"material": material, "cells": output}


def ellipse(cx, cy, rx, ry, width, height):
    return {(x, y) for y in range(height) for x in range(width)
            if ((x - cx) / rx) ** 2 + ((y - cy) / ry) ** 2 <= 1}


def rectangle(x0, y0, x1, y1):
    return {(x, y) for y in range(y0, y1 + 1) for x in range(x0, x1 + 1)}


def trail(points, radius, width, height):
    cells = set()
    for (ax, ay), (bx, by) in zip(points, points[1:]):
        steps = max(abs(bx - ax), abs(by - ay)) * 4
        for i in range(steps + 1):
            t = i / max(steps, 1)
            cells |= ellipse(ax + (bx - ax) * t, ay + (by - ay) * t, radius, radius, width, height)
    return cells


def example_map():
    width, height = 48, 28
    canvas = Image.new("RGBA", (width * 32, height * 32))
    rng = random.Random(52569)
    layers = []
    # Full-coverage floor is a normal tile layer, not a bordered terrain patch.
    full = []
    for y in range(height):
        for x in range(width):
            v = rng.randrange(12)
            canvas.paste(BASES["grass", v], (x * 32, y * 32))
            rec = next(r for r in TILES if r.get("material") == "grass" and r["kind"] == "interior" and r["variant"] == v)
            full.append({"cell": [x, y], "atlas_coords": rec["atlas_coords"]})
    layers.append({"material": "grass", "cells": full})
    path = trail([(0, 16), (9, 16), (16, 13), (24, 13), (31, 16), (39, 16), (47, 20)], 1.35, width, height)
    path |= trail([(18, 13), (18, 9)], 1.1, width, height)
    specs = [("dirt", path), ("gravel", rectangle(13, 2, 23, 10)),
             ("stone", rectangle(15, 4, 21, 8)),
             ("sand", ellipse(35, 7, 10, 5.8, width, height)),
             ("water", ellipse(35, 7, 8.2, 4.1, width, height)),
             ("wood", rectangle(34, 2, 35, 13)),
             ("concrete", rectangle(5, 20, 13, 25)),
             ("wood", rectangle(6, 21, 12, 24)),
             ("sand", ellipse(43, 24, 3.5, 2, width, height))]
    reserved = set()
    for material, cells in specs:
        layers.append(render_layer(canvas, material, cells, rng))
        reserved |= cells
    terrain_only = canvas.copy()
    save(terrain_only, Path("previews") / "terrain_map.png")
    props = []
    for x, y in sorted(rectangle(0, 0, width - 1, height - 1) - reserved):
        if rng.random() < 0.065 and 1 <= x < width - 1 and 1 <= y < height - 1:
            name = rng.choice(("tree_witchwood", "tree_moon_pine", "tree_silver_birch", "mossy_boulder", "moon_mushroom", "dew_herb"))
            canvas.alpha_composite(IMAGES[name], (x * 32, y * 32))
            record = next(r for r in TILES if r.get("name") == name)
            props.append({"cell": [x, y], "atlas_coords": record["atlas_coords"]})
    save(canvas, Path("previews") / "woodland_map.png")
    MAPS.append({"name": "WoodlandExample", "size": [width, height], "layers": layers,
                 "decorations": props, "camera_zoom": 0.4})


def font(size):
    path = Path("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf")
    return ImageFont.truetype(str(path), size) if path.exists() else ImageFont.load_default()


def contact_sheets():
    board = Image.new("RGB", (1320, 840), "#191d2b")
    d = ImageDraw.Draw(board)
    d.text((28, 20), "WITCHWOOD / EIGHT CONNECTED SURFACES", font=font(27), fill="#fff0cf")
    d.text((30, 62), "32 x 32 tiles / 12 interior variations per surface / matching edges across every variation", font=font(15), fill="#a4c9b8")
    for row, material in enumerate(MATERIALS):
        y = 111 + row * 88
        d.text((28, y + 23), material.title(), font=font(18), fill="#d5b5dd")
        for variant in range(12):
            tile = BASES[material, variant].resize((64, 64), Image.Resampling.NEAREST)
            board.paste(tile, (190 + variant * 91, y))
            label = str(variant + 1)
            if material == "grass":
                label += f" ({GRASS_COUNTS[variant]} tufts)"
            d.text((190 + variant * 91, y + 67), label, font=font(10), fill="#b4c6bb")
    save(board, Path("previews") / "surface_variations.png")
    combos = Image.new("RGB", (1200, 1020), "#191d2b")
    d = ImageDraw.Draw(combos)
    d.text((28, 18), "MIX & MATCH / SHORELINES, PATHS & FLOORS", font=font(25), fill="#fff0cf")
    for index, (background, foreground) in enumerate(PAIRS):
        x, y = 28 + (index % 3) * 395, 80 + (index // 3) * 232
        preview = Image.new("RGBA", (320, 160))
        rng = random.Random(index + 37)
        for gy in range(5):
            for gx in range(10):
                preview.paste(BASES[background, rng.randrange(12)], (gx * 32, gy * 32))
        cells = trail([(0, 3), (3, 3), (5, 1), (9, 1)], 1, 10, 5)
        render_layer(preview, foreground, cells, rng)
        combos.paste(preview, (x, y))
        d.text((x, y + 174), f"{background.title()} + {foreground.title()}", font=font(15), fill="#fff0cf")
    save(combos, Path("previews") / "mixed_surfaces.png")
    guide = Image.new("RGB", (900, 940), "#191d2b")
    d = ImageDraw.Draw(guide)
    d.text((24, 18), "47 CONNECTION SHAPES / DIRT OVER GRASS", font=font(24), fill="#fff0cf")
    for index, mask in enumerate(MASKS):
        x, y = 26 + index % 8 * 109, 72 + index // 8 * 142
        image = BASES["grass", 0].copy()
        image.alpha_composite(IMAGES["dirt", mask, 0])
        guide.paste(image.resize((96, 96), Image.Resampling.NEAREST), (x, y))
        d.text((x, y + 102), f"mask {mask:03}", font=font(12), fill="#a4c9b8")
    save(guide, Path("previews") / "connection_guide.png")


def export_manifest():
    manifest = {"version": 1, "tile_size": 32, "atlas_size": [1536, 864],
                "atlas_columns": 48, "materials": list(MATERIALS), "palette_hex": MATERIALS,
                "bit_order": {"N": N, "NE": NE, "E": E, "SE": SE, "S": S, "SW": SW, "W": W, "NW": NW},
                "blob_masks": MASKS, "tiles": TILES, "mixed_pairs": [list(p) for p in PAIRS],
                "mixed_layout": {"columns": 8, "connection_tiles": 47, "interior_variants": 12},
                "maps": MAPS}
    text = json.dumps(manifest, indent=2) + "\n"
    (ROOT / "manifest.json").write_text(text, encoding="utf-8")
    (GAME / "terrain_manifest.json").write_text(text, encoding="utf-8")


def main():
    assert len(MASKS) == 47
    build_art()
    example_map()
    contact_sheets()
    export_manifest()
    print(f"Created {len(TILES)} atlas tiles, 8 terrain brushes, 96 interior variants, and 12 precomposed combination sheets.")


if __name__ == "__main__":
    main()
