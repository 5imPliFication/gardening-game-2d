"""Palette adaptation and belt-lantern variants of the user-supplied packs."""

import hashlib
import json
from pathlib import Path

from PIL import Image, ImageChops, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parent
SOURCES = {
    "female": ROOT.parent / "The Female Adventurer - Free",
    "male": ROOT.parent / "The Male adventurer - Free",
}
CELL = (48, 64)
CROP = (8, 14, 40, 46)  # Fixed ground anchor: source (24, 43) -> (16, 29).
ROW_ORDER = ("down", "left_down", "left_up", "up", "right_up", "right_down")
STATES = ("Idle", "Walk", "Dash", "Death")
TIMINGS = {"Idle": 160, "Walk": 100, "Dash": 80, "Death": 140}
# Keep the source shading ramps; adjust their hues rather than quantizing art.
PALETTE = {
    "#000000": "#211e2c", "#120317": "#211929", "#220728": "#2b2135",
    "#230726": "#302337", "#310d35": "#392a45", "#3b122f": "#412b3c",
    "#43153b": "#4b3348", "#4e1a3f": "#57394d", "#511c3a": "#5b3c4a",
    "#571748": "#5d3c59", "#6e2749": "#75475f", "#7b3155": "#80546c",
    "#913c51": "#956577", "#95426a": "#9d687e", "#8c3c62": "#94627a",
    "#8c4b63": "#996d7e", "#c16a7d": "#c58089", "#e5959f": "#e8aaa5",
    "#3c295e": "#4b3a64", "#2c1d48": "#392d50", "#1d1133": "#2b223d",
    "#22153a": "#302640", "#140a26": "#241c32", "#160d25": "#281f35",
    "#32214d": "#40324f", "#32417f": "#355e6c", "#3c548f": "#477c80",
    "#283070": "#2d4b5c", "#1a1b41": "#293745", "#22306a": "#2d4859",
    "#771313": "#78546f", "#771212": "#76516c", "#ac3232": "#a7789c",
    "#480f0f": "#50384e", "#2a6957": "#39786e", "#3b804d": "#5b9b7b",
    "#3e7d8d": "#57948e", "#5078a1": "#769da8",
    "#222028": "#2c2936", "#343336": "#3e3a48", "#404040": "#494551",
    "#3d3d3d": "#46424e", "#595959": "#615a6b", "#676767": "#6d6577",
    "#737373": "#7b7283", "#8f8f8f": "#97909f", "#aeaeae": "#b4adb9",
    "#a27242": "#ad865e", "#9c8c9c": "#a698ac", "#f2e9f2": "#f4e9df",
}
SHIRT_COLORS = {
    "female": {(42, 105, 87), (59, 128, 77)},
    "male": {(50, 65, 127), (60, 84, 143), (40, 48, 112)},
}
COLORS = {"ink": "#302739", "metal": "#846275", "brass": "#d4a26b",
          "glass": "#e9ba76", "flame": "#fff0c2", "strap": "#7b5964"}
MAP = {tuple(bytes.fromhex(a[1:])): tuple(bytes.fromhex(b[1:])) for a, b in PALETTE.items()}
RECORDS = []
STRIPS = {}
HASHES = {}


def save(image, relative):
    path = ROOT / relative
    path.parent.mkdir(parents=True, exist_ok=True)
    image.save(path)
    return relative.as_posix()


def recolor(source):
    output = source.copy()
    output.putdata([MAP.get((r, g, b), (r, g, b)) + (a,) if a else (r, g, b, a)
                    for r, g, b, a in source.getdata()])
    return output


def direction_from(path):
    stem = path.stem.lower()
    for direction in sorted(ROW_ORDER, key=len, reverse=True):
        if stem.endswith("_" + direction):
            return direction
    return None


def shirt_bounds(frame, gender):
    points = [(x, y) for y in range(64) for x in range(48)
              if frame.getpixel((x, y))[3] and frame.getpixel((x, y))[:3] in SHIRT_COLORS[gender]]
    if points:
        return min(x for x, _ in points), min(y for _, y in points), max(x for x, _ in points) + 1, max(y for _, y in points) + 1
    return None


def belt_attachment(frame, gender, direction, state, index, reference):
    side = -1 if direction in ("down", "left_down", "right_down") else 1
    if state in ("Idle", "Walk"):
        # Lock to the original torso's animation beat, not swinging arms,
        # moving hair, or whichever clothing pixels happen to be visible.
        bounds = reference.getbbox()
        if bounds is None:
            return None
        center = (bounds[0] + bounds[2]) // 2
        bob = ((0, 1, 1, 0, 0, 1, 1, 0) if state == "Walk" else
               (0, 1, 0, -1, 0, 1, 0, 0))[index]
        return center + side * 4, 35 + bob, side, 0
    silhouette = frame.getbbox()
    if silhouette is None:
        return None
    clothes = shirt_bounds(frame, gender)
    box = clothes or silhouette
    if box is None:
        return None
    x0, y0, x1, y1 = box
    x = (silhouette[0] + silhouette[2]) // 2 + side * 3
    y = min(y1 - 1, silhouette[3] - 7)
    angle = 0
    if state == "Death" and index >= 6:
        if direction == "down":
            y, angle = y0, 180
        elif direction in ("left_up", "right_up"):
            x = x1 - 1 if direction == "left_up" else x0
            y, angle = (y0 + y1) // 2, 90 if direction == "left_up" else 270
    return x, y, side, angle


def lantern_drawing(index, state):
    image = Image.new("RGBA", (7, 8))
    d = ImageDraw.Draw(image)
    tilt = (0, 0, 1, 1, 0, 0, -1, -1)[index] if state in ("Walk", "Dash") else 0
    # The handle remains under the belt; the body has a one-pixel pendulum.
    d.line([(3, 0), (2, 1), (2, 2)], fill=COLORS["metal"])
    d.line([(3, 0), (4, 1), (4, 2)], fill=COLORS["brass"])
    d.polygon([(1, 2), (5, 2), (5 + tilt, 6), (4 + tilt, 7),
               (2 + tilt, 7), (1 + tilt, 6)], fill=COLORS["ink"])
    d.line([(1, 2), (5, 2)], fill=COLORS["brass"])
    d.polygon([(2, 3), (4, 3), (4 + tilt, 5), (2 + tilt, 5)], fill=COLORS["glass"])
    d.line([(3, 3), (3 + tilt, 5)], fill=COLORS["flame"])
    d.line([(1 + tilt, 6), (5 + tilt, 6)], fill=COLORS["brass"])
    return image


def add_lantern(original, base, gender, direction, state, index, reference):
    layer = Image.new("RGBA", CELL)
    attachment = belt_attachment(original, gender, direction, state, index, reference)
    if attachment is None:
        return base.copy(), layer
    x, y, side, angle = attachment
    lantern = lantern_drawing(index, state)
    if angle:
        lantern = lantern.rotate(angle, expand=True, resample=Image.Resampling.NEAREST)
    left, top = x + side * 2 - 3, y
    if angle == 180:
        top = y - 7
    elif angle in (90, 270):
        left, top = x - lantern.width // 2, y + 1
    layer.alpha_composite(lantern, (left, top))
    # Far-side hip equipment is naturally occluded by the original body.
    if direction in ("left_down", "left_up") and state != "Death":
        layer.putalpha(ImageChops.subtract(layer.getchannel("A"), base.getchannel("A")))
    d = ImageDraw.Draw(layer)
    end = (left + 3, top) if angle == 0 else (x + side * 2, y)
    d.line([(x - side * 3, y - 1), (x, y), end], fill=COLORS["strap"])
    d.point((x, y), fill=COLORS["brass"])
    result = base.copy()
    result.alpha_composite(layer)
    return result, layer


def adapt_sheet(source, gender, state, direction):
    base = recolor(source)
    merged = Image.new("RGBA", source.size)
    layers = Image.new("RGBA", source.size)
    for row in range(source.height // 64):
        facing = direction if direction is not None else ROW_ORDER[row]
        reference = source.crop((0, row * 64, 48, (row + 1) * 64))
        for index in range(8):
            box = (index * 48, row * 64, (index + 1) * 48, (row + 1) * 64)
            result, layer = add_lantern(source.crop(box), base.crop(box), gender, facing, state, index, reference)
            merged.paste(result, box[:2])
            layers.paste(layer, box[:2])
    return base, merged, layers


def build():
    for gender, folder in SOURCES.items():
        for path in sorted(folder.rglob("*.png")):
            if path.name == "frame dimensions.png":
                continue
            HASHES[path] = hashlib.sha256(path.read_bytes()).hexdigest()
            relative = path.relative_to(folder)
            with Image.open(path) as raw:
                source = raw.convert("RGBA")
            state = relative.parts[0]
            main_character = len(relative.parts) == 2 and state in STATES
            record = {"source": path.relative_to(ROOT.parent).as_posix(), "gender": gender,
                      "size": list(source.size), "kind": "character" if main_character else "support"}
            if main_character:
                assert source.size in ((384, 64), (384, 384)), (path, source.size)
                direction = direction_from(path)
                base, merged, layers = adapt_sheet(source, gender, state, direction)
                record.update({"state": state.lower(), "direction": direction or "atlas",
                               "columns": 8, "rows": source.height // 64,
                               "source_frame_size": list(CELL), "preview_frame_ms": TIMINGS[state]})
                record["lantern"] = save(merged, Path("native") / gender / "lantern" / relative)
                record["lantern_layer"] = save(layers, Path("native") / gender / "lantern_layers" / relative)
                if direction:
                    STRIPS[gender, state, direction] = (source, base, merged, layers)
            else:
                base = recolor(source)
            record["recolored"] = save(base, Path("native") / gender / "recolored" / relative)
            RECORDS.append(record)
    # Only standing/locomotion frames receive a shared fixed 32px crop.
    for (gender, state, direction), images in STRIPS.items():
        if state not in ("Idle", "Walk"):
            continue
        for variant, source in zip(("original", "recolored", "lantern", "lantern_layers"), images):
            if variant == "original":
                continue
            strip = Image.new("RGBA", (256, 32))
            for index in range(8):
                frame = source.crop((index * 48, 0, index * 48 + 48, 64))
                cropped = frame.crop(CROP)
                # Cropping may remove transparent padding, never visible art.
                assert sum(frame.getchannel("A").getdata()) == sum(cropped.getchannel("A").getdata()), (gender, state, direction, variant, index)
                strip.paste(cropped, (index * 32, 0))
                save(cropped, Path("32x32") / gender / variant / state.lower() / direction / f"{index:02}.png")
            save(strip, Path("32x32") / gender / variant / f"{state.lower()}_{direction}.png")


def font(size):
    path = Path("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf")
    return ImageFont.truetype(str(path), size) if path.exists() else ImageFont.load_default()


def paste(canvas, image, xy, scale=5):
    image = image.resize((image.width * scale, image.height * scale), Image.Resampling.NEAREST)
    canvas.paste(image, xy, image)


def heading(canvas, title, subtitle):
    d = ImageDraw.Draw(canvas)
    d.text((28, 20), title, font=font(27), fill="#fff0cf")
    d.text((30, 60), subtitle, font=font(14), fill="#a4c9b8")


def save_gif(frames, path, duration):
    # One shared palette for every frame prevents preview palette flicker.
    sample = Image.new("RGB", (frames[0].width, sum(f.height for f in frames)))
    y = 0
    for frame in frames:
        sample.paste(frame, (0, y))
        y += frame.height
    palette = sample.quantize(colors=256, dither=Image.Dither.NONE)
    converted = [f.quantize(palette=palette, dither=Image.Dither.NONE) for f in frames]
    converted[0].save(path, save_all=True, append_images=converted[1:], duration=duration,
                      loop=0, disposal=2, optimize=False)


def previews():
    folder = ROOT / "previews"
    folder.mkdir(parents=True, exist_ok=True)
    comparison = Image.new("RGB", (1080, 610), "#191d2b")
    heading(comparison, "ADVENTURERS / COZY WOODLAND PALETTE", "Source artwork / subtly recolored / belt-lantern variant — no pose or outline redesign")
    d = ImageDraw.Draw(comparison)
    for row, gender in enumerate(("female", "male")):
        for col, label in enumerate(("Original", "Recolored", "Waist lantern")):
            x, y = 160 + col * 290, 120 + row * 230
            source = STRIPS[gender, "Idle", "down"][col]
            frame = source.crop((0, 0, 48, 64)).crop(CROP)
            d.rectangle((x, y, x + 159, y + 159), fill="#303549")
            paste(comparison, frame, (x, y))
            d.text((x, y + 174), label, font=font(15), fill="#fff0cf")
        d.text((30, 188 + row * 230), gender.title(), font=font(18), fill="#d5b5dd")
    comparison.save(ROOT / "comparison.png")
    for state in ("Idle", "Walk"):
        frames = []
        for index in range(8):
            canvas = Image.new("RGB", (1120, 570), "#191d2b")
            heading(canvas, f"WAIST LANTERNS / {state.upper()}", "Female above / male below — source direction order retained")
            d = ImageDraw.Draw(canvas)
            for row, gender in enumerate(("female", "male")):
                for col, direction in enumerate(ROW_ORDER):
                    image = STRIPS[gender, state, direction][2]
                    frame = image.crop((index * 48, 0, (index + 1) * 48, 64)).crop(CROP)
                    x, y = 28 + col * 181, 115 + row * 215
                    paste(canvas, frame, (x, y), 5)
                    d.text((x, y + 168), direction.replace("_", " ").title(), font=font(13), fill="#fff0cf")
            d.text((1020, 546), f"{index + 1} / 8", font=font(12), fill="#a4c9b8")
            frames.append(canvas)
        save_gif(frames, folder / f"lantern_{state.lower()}.gif", TIMINGS[state])
        frames[0].save(folder / f"lantern_{state.lower()}.png")
    # Native falling/dash poses are reviewed without a 32px crop.
    for state in ("Dash", "Death"):
        frames = []
        for index in range(8):
            canvas = Image.new("RGB", (1120, 650), "#191d2b")
            heading(canvas, f"NATIVE CELL / {state.upper()}", "48 x 64 cells preserve the source's wider and falling poses")
            for row, gender in enumerate(("female", "male")):
                for col, direction in enumerate(ROW_ORDER):
                    image = STRIPS[gender, state, direction][2]
                    frame = image.crop((index * 48, 0, (index + 1) * 48, 64))
                    paste(canvas, frame, (25 + col * 181, 100 + row * 266), 4)
            ImageDraw.Draw(canvas).text((1020, 626), f"{index + 1} / 8", font=font(12), fill="#a4c9b8")
            frames.append(canvas)
        save_gif(frames, folder / f"lantern_{state.lower()}.gif", TIMINGS[state])


def verify():
    for record in RECORDS:
        with Image.open(ROOT.parent / record["source"]) as raw:
            original = raw.convert("RGBA")
        with Image.open(ROOT / record["recolored"]) as base:
            assert base.size == original.size == tuple(record["size"])
            assert base.mode == "RGBA"
            assert base.getchannel("A").tobytes() == original.getchannel("A").tobytes()
            assert base.tobytes() == recolor(original).tobytes()
        if record["kind"] == "character":
            base = Image.open(ROOT / record["recolored"]).convert("RGBA")
            layer = Image.open(ROOT / record["lantern_layer"]).convert("RGBA")
            merged = Image.open(ROOT / record["lantern"]).convert("RGBA")
            assert base.size == layer.size == merged.size
            assert Image.alpha_composite(base, layer).tobytes() == merged.tobytes()
            assert ImageChops.subtract(base.getchannel("A"), merged.getchannel("A")).getbbox() is None
            assert base.tobytes() != merged.tobytes(), record["source"]
    count = 0
    for path in (ROOT / "32x32").rglob("*.png"):
        with Image.open(path) as im:
            assert im.mode == "RGBA" and im.size in ((32, 32), (256, 32)), path
            count += im.size == (32, 32)
    assert count == 576, count  # 2 genders * 3 variants * 2 states * 6 directions * 8.
    for (gender, state, direction), sources in STRIPS.items():
        if state not in ("Idle", "Walk"):
            continue
        for variant, source in zip(("original", "recolored", "lantern", "lantern_layers"), sources):
            if variant == "original":
                continue
            strip = Image.open(ROOT / "32x32" / gender / variant / f"{state.lower()}_{direction}.png")
            for index in range(8):
                path = ROOT / "32x32" / gender / variant / state.lower() / direction / f"{index:02}.png"
                frame = Image.open(path)
                expected = source.crop((index * 48, 0, (index + 1) * 48, 64)).crop(CROP)
                assert frame.tobytes() == expected.tobytes() == strip.crop((index * 32, 0, (index + 1) * 32, 32)).tobytes()
    for path, before in HASHES.items():
        assert hashlib.sha256(path.read_bytes()).hexdigest() == before, f"Source was modified: {path}"
    for state in STATES:
        with Image.open(ROOT / "previews" / f"lantern_{state.lower()}.gif") as im:
            assert im.n_frames == 8
            for index in range(8):
                im.seek(index)
                assert im.info["duration"] == TIMINGS[state]
    print(f"PASS: {len(RECORDS)} source images adapted; 56 character sheets have lantern variants and layers; {count} aligned 32px frames; source hashes, silhouettes, composites, strip cells and preview timing verified.")


def main():
    build()
    previews()
    manifest = {"version": 1, "source_cell_size": list(CELL), "atlas_row_order": list(ROW_ORDER),
                "game_crop_box": list(CROP), "game_frame_size": [32, 32], "game_anchor_px": [16, 29],
                "source_images": RECORDS, "palette_hex": PALETTE,
                "exports_32px": {"root": "32x32", "states": ["idle", "walk"],
                                  "variants": ["recolored", "lantern", "lantern_layers"],
                                  "columns": 8, "strip_size": [256, 32], "direction_names": list(ROW_ORDER)},
                "timing_note": "Preview timings are suggestions; source PNGs contain no playback durations.",
                "source_note": "Female Walk atlas and individual directional strips have source pixel differences; both are adapted independently, without replacing either."}
    (ROOT / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    verify()


if __name__ == "__main__":
    main()
