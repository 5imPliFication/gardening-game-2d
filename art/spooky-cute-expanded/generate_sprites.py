"""Expanded original 32px art. Python 3 + Pillow >=9.1; see README.md."""

import importlib.util
import json
import math
import sys
from pathlib import Path

from PIL import Image, ImageDraw


ROOT = Path(__file__).resolve().parent
# Reuse the editable first-draft palette, drawing tools, and plant designs.
# Redirect its output to this collection; the first draft is never rewritten.
sys.dont_write_bytecode = True
SPEC = importlib.util.spec_from_file_location(
    "starter_art", ROOT.parent / "spooky-cute-starter" / "generate_sprites.py"
)
BASE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(BASE)
BASE.ROOT = ROOT
P = BASE.P
Pixel = BASE.Pixel
DIRECTIONS = ("down", "left", "right", "up")
ANIMATIONS = {}
STATIC = {}


def save_frame(image, name):
    target = ROOT / "sprites" / f"{name}.png"
    target.parent.mkdir(parents=True, exist_ok=True)
    image.save(target)
    return f"sprites/{name}.png"


def animation(name, frames, durations):
    paths = [save_frame(frame, f"{name}/{i:02}") for i, frame in enumerate(frames)]
    sheet = Image.new("RGBA", (32 * len(frames), 32))
    for i, frame in enumerate(frames):
        sheet.paste(frame, (i * 32, 0))
    path = ROOT / "sheets" / f"{name}.png"
    path.parent.mkdir(parents=True, exist_ok=True)
    sheet.save(path)
    ANIMATIONS[name] = {
        "frames": paths, "durations_ms": durations, "loop": True,
        "sheet": path.relative_to(ROOT).as_posix(), "frame_size": [32, 32],
        "anchor_px": [16, 29],
    }


def shift_shape(s, points, color, outline, dx, dy):
    s.poly([(x + dx, y + dy) for x, y in points], color, outline)


def character(gender, direction, state, frame):
    s = Pixel()
    female = gender == "female"
    side = direction in ("left", "right")
    walking = state == "walk"
    resting = state == "rest"
    phase = frame * math.tau / 8
    stride = round(math.sin(phase) * 2) if walking else 0
    bob = (-1 if frame in (1, 2, 5, 6) else 0) if walking else (-1 if frame in (1, 2, 3) else 0)
    sway = round(math.sin(phase - 0.8)) if walking else ({5: 1, 6: -1}.get(frame, 0))
    dy = bob + (3 if resting else 0)
    # Rest is a seated loop, with feet forward and elbows on knees.
    if resting:
        s.ellipse((9, 24, 23, 29), "deep", "ink")
        if side:
            s.poly([(13, 24), (19, 24), (24, 26), (26, 28), (24, 29),
                    (18, 28), (12, 27)], "purple", "ink")
            s.line([(17, 25), (21, 26), (22, 28)], "lilac")
            s.rect((23, 27, 26, 28), "wood")
            s.rect((22, 26, 24, 26), "bark")
        elif direction == "up":
            s.poly([(10, 23), (14, 24), (13, 28), (9, 28), (8, 26)], "purple", "ink")
            s.poly([(18, 24), (21, 23), (24, 26), (22, 28), (18, 28)], "purple", "ink")
            s.rect((9, 26, 11, 27), "wood")
            s.rect((21, 26, 23, 27), "wood")
        else:
            s.poly([(10, 24), (14, 24), (14, 28), (10, 29), (8, 28)], "purple", "ink")
            s.poly([(18, 24), (22, 24), (24, 28), (23, 29), (18, 28)], "purple", "ink")
            s.rect((9, 28, 13, 29), "wood")
            s.rect((19, 28, 23, 29), "wood")
    else:
        # Feet travel in opposing arcs rather than just changing length.
        for leg in range(2):
            sign = 1 if leg == 0 else -1
            lift = max(0, round(math.cos(phase + leg * math.pi) * 2)) if walking else 0
            x = (12 if leg == 0 else 17) + (stride * sign if side else 0)
            y = min(27, 27 + (0 if side else stride * sign // 2) - lift)
            s.poly([(x, 22 + bob), (x + 3, 22 + bob), (x + 3, y),
                    (x + 4, y + 1), (x + 4, y + 2), (x - 1, y + 2), (x - 1, y)],
                   "purple", "ink")
            s.rect((x, y, x + 3, y + 1), "wood")
            s.rect((x, y, x + 2, y), "bark")
    # Female: flared teal field coat. Male: cropped vest and overalls.
    torso = [(12, 17), (19, 17), (21, 20), (22 if female else 20, 25),
             (9 if female else 11, 25), (10, 20)]
    shift_shape(s, torso, "teal", "ink", 0, dy)
    s.rect((12, 19 + dy, 19, 22 + dy), "mint")
    if female:
        s.poly([(13, 18 + dy), (18, 18 + dy), (17, 21 + dy), (14, 21 + dy)], "cream")
        s.rect((11, 23 + dy, 20, 23 + dy), "purple")
        s.rect((15, 23 + dy, 16, 23 + dy), "gold")
        s.line([(12, 24 + dy), (12, 25 + dy)], "mint")
        s.line([(19, 24 + dy), (20, 25 + dy)], "teal_dark")
    else:
        s.rect((13, 19 + dy, 18, 24 + dy), "teal_dark")
        s.rect((14, 20 + dy, 17, 23 + dy), "teal")
        s.rect((13, 19 + dy, 13, 20 + dy), "gold")
        s.rect((18, 19 + dy, 18, 20 + dy), "gold")
    # Arm swing counterbalances the legs, with an occasional idle hat touch.
    for left in (True, False):
        arm = (-stride if left else stride) if walking else 0
        ax = (8 if left else 20) + (arm if side else 0)
        ay = 19 + dy + (arm // 2 if not side else 0)
        if resting:
            ax, ay = (10 if left else 19), 23 + bob
        s.poly([(ax + 1, ay), (ax + 3, ay), (ax + 3, ay + 4),
                (ax + 1, ay + 5), (ax, ay + 3)], "mint", "ink")
        s.rect((ax + 1, ay + 3, ax + 2, ay + 4), "skin")
    # Head is layered over the shoulders, leaving a visible neck scarf.
    s.poly([(12, 17 + dy), (19, 17 + dy), (17 + sway, 20 + dy),
            (15, 19 + dy), (12, 19 + dy)], "lilac", "purple")
    s.ellipse((10, 9 + dy, 21, 18 + dy), "hair", "ink")
    if female:
        braid_x = 20 + sway
        for n in range(4):
            x = braid_x + (n % 2)
            s.ellipse((x, 14 + dy + n * 2, x + 3, 17 + dy + n * 2), "hair", "ink")
            s.rect((x + 1, 15 + dy + n * 2, x + 2, 15 + dy + n * 2), "bark")
        s.rect((braid_x + 1, 22 + dy, braid_x + 3, 23 + dy), "gold")
    if direction != "up":
        s.rect((12, 12 + dy, 20, 16 + dy), "skin")
        s.rect((13, 17 + dy, 18, 17 + dy), "tan")
        s.rect((11, 12 + dy, 12, 14 + dy), "hair")
        s.rect((13, 11 + dy, 15, 12 + dy), "hair")
        blink = (not walking and frame == 3) or (resting and frame not in (0, 7))
        eyes = (14, 18) if not side else (19,)
        look = -1 if state == "idle" and frame in (5, 6) and not side else 0
        for x in eyes:
            if blink:
                s.line([(x - 1 + look, 14 + dy), (x + look, 14 + dy)], "hair")
            else:
                s.rect((x + look, 13 + dy, x + look, 14 + dy), "ink")
        s.rect((12, 15 + dy, 13, 15 + dy), "blush")
        s.rect((19, 15 + dy, 20, 15 + dy), "blush")
        s.rect((16, 16 + dy, 17, 16 + dy), "hair")
        if side:
            s.rect((20, 14 + dy, 21, 15 + dy), "skin")
            s.rect((11, 12 + dy, 13, 16 + dy), "hair")
    else:
        s.rect((12, 12 + dy, 20, 16 + dy), "hair")
        s.line([(12, 13 + dy), (15, 14 + dy), (19, 13 + dy)], "wood")
    # Same lavender/teal palette; very different hat silhouettes.
    hx = sway
    if female:
        shift_shape(s, [(6, 9), (9, 7), (11, 4), (14, 2), (19, 3), (22, 7),
                        (25, 8), (26, 10), (23, 12), (11, 12), (6, 11)], "purple", "ink", hx, dy)
        shift_shape(s, [(11, 7), (12, 5), (15, 3), (18, 4), (20, 7)], "lilac", None, hx, dy)
        s.line([(10 + hx, 8 + dy), (16 + hx, 9 + dy), (21 + hx, 8 + dy)], "mint", 2)
        s.line([(8 + hx, 10 + dy), (15 + hx, 11 + dy), (24 + hx, 10 + dy)], "deep")
        s.rect((21 + hx, 6 + dy, 22 + hx, 8 + dy), "cream")
        s.rect((20 + hx, 7 + dy, 23 + hx, 7 + dy), "pink")
        s.rect((21 + hx, 7 + dy, 21 + hx, 7 + dy), "gold")
    else:
        shift_shape(s, [(10, 9), (10, 6), (12, 3), (18, 3), (21, 6), (22, 9),
                        (24, 10), (23, 12), (13, 11)], "purple", "ink", hx, dy)
        shift_shape(s, [(12, 7), (13, 4), (17, 4), (20, 7)], "lilac", None, hx, dy)
        s.line([(11 + hx, 9 + dy), (20 + hx, 9 + dy)], "mint", 2)
        s.line([(15 + hx, 11 + dy), (23 + hx, 11 + dy)], "deep")
        s.line([(18 + hx, 6 + dy), (20 + hx, 4 + dy), (22 + hx, 4 + dy)], "light")
        s.rect((19 + hx, 7 + dy, 20 + hx, 8 + dy), "gold")
    if direction == "up":
        s.rect((12, 18 + dy, 19, 24 + dy), "ink")
        s.rect((13, 19 + dy, 18, 23 + dy), "bark")
        s.rect((13, 19 + dy, 18, 20 + dy), "tan")
        s.rect((15, 21 + dy, 16, 22 + dy), "gold")
    elif not resting:
        s.line([(12, 19 + dy), (21, 24 + dy)], "wood")
        bx = 21 + (sway if walking else 0)
        s.rect((bx, 22 + dy, bx + 4, 26 + dy), "ink")
        s.rect((bx + 1, 23 + dy, bx + 3, 25 + dy), "bark")
        s.rect((bx + 1, 22 + dy, bx + 3, 23 + dy), "tan")
        s.rect((bx + 2, 24 + dy, bx + 2, 24 + dy), "gold")
    if state == "idle" and frame in (5, 6) and direction != "up":
        s.line([(9, 21 + dy), (8, 17 + dy), (10, 12 + dy)], "ink", 3)
        s.line([(9, 20 + dy), (9, 17 + dy)], "mint", 2)
        s.rect((9, 12 + dy, 11, 14 + dy), "skin")
    if direction == "left":
        s.im = s.im.transpose(Image.Transpose.FLIP_LEFT_RIGHT)
    return s.im


def characters():
    timings = {
        "walk": [100] * 8,
        "idle": [650, 250, 300, 130, 650, 220, 300, 650],
        "rest": [650, 350, 350, 150, 650, 350, 350, 650],
    }
    for gender in ("male", "female"):
        for state, durations in timings.items():
            directional_sheet = Image.new("RGBA", (256, 128))
            for row, direction in enumerate(DIRECTIONS):
                frames = [character(gender, direction, state, i) for i in range(8)]
                animation(f"player/{gender}/{state}/{direction}", frames, durations)
                for i, frame in enumerate(frames):
                    directional_sheet.paste(frame, (i * 32, row * 32))
            directional_sheet.save(ROOT / "sheets" / "player" / gender / f"{state}_4dir.png")


def tree_variant(kind):
    if kind == "witchwood":
        BASE.tree()
        return BASE.SPRITES["environment/witchwood_tree"]
    s = Pixel()
    s.poly([(13, 15), (19, 15), (19, 25), (22, 29), (18, 29),
            (16, 27), (13, 29), (10, 29), (13, 25)], "wood", "ink")
    s.line([(15, 18), (15, 25), (13, 27)], "bark", 2)
    if kind == "moon_pine":
        s.poly([(16, 1), (20, 6), (20, 8), (24, 12), (22, 13),
                (27, 19), (25, 20), (29, 24), (23, 26), (17, 25),
                (10, 26), (3, 24), (7, 20), (5, 19), (10, 13),
                (8, 12), (12, 8), (12, 6)], "teal_dark", "ink")
        for x, y, w in ((13, 5, 5), (10, 11, 11), (7, 18, 18)):
            s.poly([(16, y - 2), (x + w, y + 3), (16, y + 2), (x, y + 4)], "teal")
            s.line([(16, y - 1), (x + 2, y + 2)], "mint")
        s.rect((19, 18, 20, 19), "lilac")
        s.rect((11, 22, 12, 23), "lavender")
    elif kind == "lavender_willow":
        s.poly([(3, 10), (5, 6), (11, 3), (19, 2), (25, 6), (28, 10),
                (28, 21), (25, 24), (23, 17), (22, 22), (19, 21),
                (17, 16), (14, 22), (11, 20), (9, 17), (7, 24), (3, 22)], "purple", "ink")
        s.poly([(5, 11), (7, 7), (12, 5), (19, 4), (24, 7), (26, 11),
                (23, 14), (19, 12), (15, 15), (11, 13), (7, 16)], "lilac")
        s.line([(9, 8), (14, 6), (19, 6)], "lavender")
        for x, y in ((5, 14), (8, 12), (12, 14), (20, 13), (25, 12)):
            s.line([(x, y), (x, y + 6)], "lilac")
            s.rect((x, y + 5, x, y + 6), "pink")
        s.line([(14, 23), (14, 26)], "bark")
    else:
        s.poly([(13, 12), (18, 12), (19, 26), (22, 29), (17, 28),
                (12, 29), (14, 25)], "lavender", "ink")
        for x, y in ((14, 20), (16, 23), (15, 26)):
            s.line([(x, y), (x + 2, y)], "purple")
        for box in ((4, 8, 17, 20), (13, 5, 27, 18), (7, 2, 21, 14)):
            s.ellipse(box, "teal", "ink")
        s.poly([(7, 8), (11, 4), (17, 3), (20, 6), (17, 9), (13, 8), (11, 12), (6, 13)], "mint")
        s.line([(11, 6), (15, 5)], "light")
        s.ellipse((20, 9, 25, 13), "mint")
        s.rect((8, 15, 9, 16), "gold")
        s.rect((22, 14, 23, 15), "gold")
    return s.im


def sway_image(source, amount, anchor_y, canopy_end=None):
    """Integer-only row displacement; the grounded base remains stationary."""
    dest = Image.new("RGBA", (32, 32))
    for y in range(32):
        movable = canopy_end is None or y <= canopy_end
        dx = round(amount * max(0, (anchor_y - y) / anchor_y)) if movable else 0
        dest.paste(source.crop((0, y, 32, y + 1)), (dx, y))
    return dest


def environment():
    for kind in ("witchwood", "moon_pine", "lavender_willow", "silver_birch"):
        source = tree_variant(kind)
        frames = []
        for i, amount in enumerate((0, 0.8, 1.4, 0.8, 0, -0.8, -1.4, -0.8)):
            frame = sway_image(source, amount, 26, canopy_end=24 if kind == "moon_pine" else 22)
            # A few moving leaf-tip accents sell the breeze without moving roots.
            if i in (2, 6):
                d = ImageDraw.Draw(frame)
                x = 19 if i == 2 else 10
                d.point((x, 8), fill=P["lavender" if kind == "lavender_willow" else "light"])
            frames.append(frame)
        animation(f"environment/trees/{kind}", frames, [200] * 8)
    STATIC["environment/witchwood_tree"] = "sprites/environment/witchwood_tree.png"
    BASE.plants()
    for name in ("dew_herb", "sun_plant", "moon_mushroom", "midnight_bloom"):
        STATIC[f"plants/{name}"] = f"sprites/plants/{name}.png"
        source = BASE.SPRITES[f"plants/{name}"]
        if name == "midnight_bloom":
            # Sparkles animate separately from the flower's rooted sway.
            source = source.copy()
            d = ImageDraw.Draw(source)
            for box in ((3, 4, 7, 8), (24, 2, 28, 6), (27, 23, 27, 23)):
                d.rectangle(box, fill=(0, 0, 0, 0))
        frames = []
        for i, amount in enumerate((0, 1, 1.5, 1, 0, -1, -1.5, -1)):
            frame = sway_image(source, amount, 28)
            d = ImageDraw.Draw(frame)
            if name == "midnight_bloom":
                d.ellipse((14, 13, 18, 17), fill=P["cream" if i in (1, 2, 3, 6) else "yellow"])
                x, y = ((5, 6), (26, 4), (27, 23), (5, 21))[i // 2]
                if i % 2:
                    d.line((x - 1, y, x + 1, y), fill=P["ice"])
                    d.line((x, y - 1, x, y + 1), fill=P["ice"])
                else:
                    d.point((x, y), fill=P["lavender"])
            elif name == "dew_herb":
                d.point(((10, 21) if i < 4 else (22, 15)), fill=P["cream" if i % 2 else "ice"])
            elif name == "sun_plant" and i in (3, 4):
                # Little sleepy blink on the sunny flower.
                for x in (14, 18):
                    dx = round(amount * (28 - 11) / 28)
                    d.point((x + dx, 11), fill=P["orange"])
            elif name == "moon_mushroom":
                d.point((11 + round(amount / 2), 9), fill=P["cream" if i in (2, 6) else "lavender"])
            frames.append(frame)
        animation(f"plants/{name}", frames, [180] * 8)


def rocks():
    for kind in ("boulder", "mossy_boulder", "rune_rock", "flat_stone", "pebble_cluster", "small_stone"):
        s = Pixel()
        if kind in ("boulder", "mossy_boulder", "rune_rock"):
            s.poly([(4, 19), (7, 11), (13, 7), (22, 9), (27, 16),
                    (28, 24), (24, 28), (9, 28), (3, 24)], "purple", "ink")
            s.poly([(5, 19), (9, 12), (14, 9), (21, 10), (23, 16),
                    (18, 20), (10, 21)], "lilac")
            s.line([(10, 13), (14, 11), (19, 12)], "lavender")
            s.poly([(19, 21), (25, 17), (26, 23), (23, 26), (10, 26), (8, 24)], "deep")
            s.line([(20, 13), (18, 17), (20, 19)], "purple")
            if kind == "mossy_boulder":
                s.poly([(7, 14), (10, 10), (15, 8), (22, 10), (23, 13),
                        (19, 14), (17, 17), (13, 15), (11, 19), (6, 19)], "teal_dark")
                s.poly([(9, 13), (14, 10), (20, 11), (19, 13), (16, 14), (12, 13), (9, 16)], "mint")
                s.rect((13, 11, 16, 11), "light")
                s.rect((8, 22, 10, 23), "teal")
                s.rect((23, 23, 24, 24), "mint")
            elif kind == "rune_rock":
                s.line([(14, 15), (18, 12), (21, 15), (17, 20), (14, 17), (20, 17)], "ice")
                s.rect((17, 22, 18, 23), "mint")
        elif kind == "flat_stone":
            s.poly([(5, 20), (12, 16), (23, 17), (28, 22), (25, 27), (11, 28), (4, 25)], "purple", "ink")
            s.poly([(6, 21), (12, 18), (22, 19), (25, 22), (21, 24), (10, 24)], "lilac")
            s.line([(10, 21), (14, 19), (19, 20)], "lavender")
            s.line([(17, 24), (20, 22), (23, 22)], "purple")
        elif kind == "pebble_cluster":
            for x, y, w in ((5, 20, 7), (15, 16, 10), (18, 25, 6)):
                s.poly([(x, y + 2), (x + 2, y), (x + w - 2, y),
                        (x + w, y + 3), (x + w - 1, y + 5), (x + 1, y + 5)], "purple", "ink")
                s.line([(x + 2, y + 1), (x + w - 2, y + 1), (x + w - 1, y + 2)], "lavender")
                s.line([(x + 2, y + 2), (x + w - 3, y + 2)], "lilac")
        else:
            s.poly([(10, 22), (13, 18), (19, 18), (23, 23), (21, 27), (12, 28), (9, 25)], "purple", "ink")
            s.poly([(12, 22), (14, 20), (18, 20), (21, 23), (16, 24)], "lilac")
            s.line([(14, 21), (17, 20)], "lavender")
        STATIC[f"environment/rocks/{kind}"] = save_frame(s.im, f"environment/rocks/{kind}")
        if kind == "rune_rock":
            frames = []
            for i in range(8):
                frame = s.im.copy()
                pixels = frame.load()
                for y in range(32):
                    for x in range(32):
                        if pixels[x, y][:3] == tuple(bytes.fromhex(P["ice"][1:])):
                            pixels[x, y] = tuple(bytes.fromhex(P[("teal", "mint", "ice", "cream", "ice", "mint", "teal", "teal_dark")[i]][1:])) + (255,)
                if i in (2, 3, 4):
                    d = ImageDraw.Draw(frame)
                    d.point((24, 9 - (i % 2)), fill=P["ice"])
                frames.append(frame)
            animation("environment/rocks/rune_glow", frames, [220] * 8)


def get_frames(name):
    return [Image.open(ROOT / p).convert("RGBA") for p in ANIMATIONS[name]["frames"]]


def paste_sprite(canvas, image, xy, scale=5):
    enlarged = image.resize((32 * scale, 32 * scale), Image.Resampling.NEAREST)
    canvas.paste(enlarged, xy, enlarged)


def title(canvas, heading, subheading):
    d = ImageDraw.Draw(canvas)
    d.text((32, 22), heading, font=BASE.font(29), fill=P["cream"])
    d.text((34, 65), subheading, font=BASE.font(15), fill=P["mint"])


def gif(frames, path, durations):
    # A shared palette prevents color flickering between review frames.
    for index, frame in enumerate(frames):
        d = ImageDraw.Draw(frame)
        for tick in range(len(frames)):
            x, y = frame.width - 108 + tick * 11, frame.height - 16
            d.rectangle((x, y, x + 6, y + 3), fill=P["mint" if tick == index else "deep"])
    palette_source = Image.new("RGB", (len(P) + 2, 1))
    palette_source.putdata([tuple(bytes.fromhex(c[1:])) for c in P.values()] + [(25, 29, 43), (48, 53, 73)])
    palette = palette_source.quantize(colors=256)
    indexed = [im.convert("RGB").quantize(palette=palette, dither=Image.Dither.NONE) for im in frames]
    indexed[0].save(path, save_all=True, append_images=indexed[1:], duration=durations,
                    loop=0, optimize=False, disposal=2)


def previews():
    folder = ROOT / "previews"
    folder.mkdir(parents=True, exist_ok=True)
    still = Image.new("RGB", (1120, 1050), "#191d2b")
    title(still, "WITCHWOOD / CHARACTER COLLECTION", "Male & female foragers  /  matching palette, distinct silhouettes  /  32 x 32 originals")
    d = ImageDraw.Draw(still)
    for row, gender in enumerate(("male", "female")):
        y = 110 + row * 250
        d.text((34, y), f"{gender.upper()} / FIELD CAP & OVERALLS" if gender == "male" else "FEMALE / FLOWER HAT, BRAID & FIELD COAT", font=BASE.font(16), fill=P["lavender"])
        for col, direction in enumerate(DIRECTIONS):
            x = 40 + col * 210
            d.rectangle((x, y + 30, x + 159, y + 189), fill="#303549")
            paste_sprite(still, character(gender, direction, "idle", 0), (x, y + 30))
            d.text((x, y + 200), direction.title(), font=BASE.font(14), fill=P["cream"])
    d.text((34, 620), "MOTION STUDIES / WALK  ·  STANDING IDLE  ·  SEATED REST", font=BASE.font(16), fill=P["lavender"])
    for col, state in enumerate(("walk", "idle", "rest")):
        x = 40 + col * 350
        paste_sprite(still, character("male", "down", state, 2), (x, 663), 4)
        paste_sprite(still, character("female", "down", state, 2), (x + 145, 663), 4)
        d.text((x, 807), state.title(), font=BASE.font(16), fill=P["cream"])
        desc = {"walk": "8 frames / stride, swing & bounce", "idle": "8 frames / breathe, blink & hat touch", "rest": "8 frames / sit, relax & close eyes"}[state]
        d.text((x, 836), desc, font=BASE.font(13), fill=P["mint"])
    d.text((34, 940), "See the GIF previews for motion. PNG originals have transparent backgrounds.", font=BASE.font(16), fill=P["cream"])
    d.text((34, 978), "Directions: down / left / right / up. Walking and idle share a fixed ground anchor.", font=BASE.font(14), fill=P["mint"])
    still.save(ROOT / "characters_preview.png")

    for state in ("walk", "idle", "rest"):
        frames = []
        for i in range(8):
            canvas = Image.new("RGB", (864, 506), "#191d2b")
            title(canvas, f"FORAGERS / {state.upper()}", "Male (top)  /  Female (bottom)  /  Down, left, right, up")
            for row, gender in enumerate(("male", "female")):
                for col, direction in enumerate(DIRECTIONS):
                    paste_sprite(canvas, character(gender, direction, state, i), (35 + col * 207, 112 + row * 193))
            frames.append(canvas)
        gif(frames, folder / f"characters_{state}.gif", ANIMATIONS[f"player/male/{state}/down"]["durations_ms"])

    names = [f"environment/trees/{kind}" for kind in ("witchwood", "moon_pine", "lavender_willow", "silver_birch")]
    names += [f"plants/{kind}" for kind in ("dew_herb", "sun_plant", "moon_mushroom", "midnight_bloom")]
    names += [name for name in STATIC if name.startswith("environment/rocks/")]
    frames = []
    for i in range(8):
        canvas = Image.new("RGB", (1120, 790), "#191d2b")
        title(canvas, "WITCHWOOD / LIVING WOODLAND", "4 swaying trees  /  4 animated forageables  /  6 rocks & stones (rune rock glows)")
        d = ImageDraw.Draw(canvas)
        for index, name in enumerate(names):
            if index < 4:
                row, col = 0, index
            elif index < 8:
                row, col = 1, index - 4
            else:
                row, col = 2, index - 8
            x, y = 32 + col * 180, 115 + row * 218
            d.rectangle((x, y, x + 127, y + 127), fill="#303549")
            if name in ANIMATIONS:
                image = get_frames(name)[i]
            elif name.endswith("rune_rock"):
                image = get_frames("environment/rocks/rune_glow")[i]
            else:
                image = Image.open(ROOT / STATIC[name]).convert("RGBA")
            paste_sprite(canvas, image, (x, y), 4)
            label = name.split("/")[-1].replace("_", " ").title()
            d.text((x, y + 143), label, font=BASE.font(13), fill=P["cream"])
        frames.append(canvas)
    frames[0].save(ROOT / "environment_preview.png")
    gif(frames, folder / "environment_animated.gif", [200] * 8)

    # Expose every pose for easy onion-skin / motion-arc review.
    breakdown = Image.new("RGB", (1000, 860), "#191d2b")
    title(breakdown, "FORAGERS / FRAME BREAKDOWN", "Eight source frames per loop  /  walking, standing idle, seated rest")
    d = ImageDraw.Draw(breakdown)
    for row, (gender, state) in enumerate((g, s) for g in ("male", "female") for s in ("walk", "idle", "rest")):
        y = 113 + row * 122
        d.text((20, y + 31), gender.title(), font=BASE.font(12), fill=P["cream"])
        d.text((20, y + 51), state.title(), font=BASE.font(12), fill=P["mint"])
        for i in range(8):
            paste_sprite(breakdown, character(gender, "down", state, i), (112 + i * 110, y), 3)
            d.text((147 + i * 110, y + 100), f"{i:02}", font=BASE.font(11), fill=P["lilac"])
    breakdown.save(folder / "character_frames.png")


def verify():
    """Check delivered files and metadata, including every sheet cell."""
    expected = set()
    for name, record in ANIMATIONS.items():
        assert len(record["frames"]) == len(record["durations_ms"]) == 8, name
        assert all(ms > 0 for ms in record["durations_ms"])
        frames = get_frames(name)
        assert len({frame.tobytes() for frame in frames}) >= 4, f"Insufficient movement: {name}"
        if name.startswith(("environment/trees/", "plants/")):
            roots = [frame.crop((0, 27, 32, 32)).tobytes() for frame in frames]
            assert len(set(roots)) == 1, f"Ground anchor moves: {name}"
        sheet = Image.open(ROOT / record["sheet"])
        assert sheet.size == (256, 32) and sheet.mode == "RGBA"
        for i, (path, image) in enumerate(zip(record["frames"], frames)):
            expected.add(path)
            assert image.size == (32, 32), path
            assert set(image.getchannel("A").getdata()) == {0, 255}, path
            assert image.getbbox() is not None, path
            assert image.crop((0, 30, 32, 32)).getbbox() is None, f"Feet clipped: {path}"
            assert sheet.crop((i * 32, 0, i * 32 + 32, 32)).tobytes() == image.tobytes(), path
    for path in STATIC.values():
        expected.add(path)
        image = Image.open(ROOT / path)
        assert image.size == (32, 32) and image.mode == "RGBA", path
        assert set(image.getchannel("A").getdata()) == {0, 255}, path
    actual = {p.relative_to(ROOT).as_posix() for p in (ROOT / "sprites").rglob("*.png")}
    assert actual == expected, f"Sprite/manifest mismatch: {actual ^ expected}"
    for gender in ("male", "female"):
        for state in ("walk", "idle", "rest"):
            sheet = Image.open(ROOT / "sheets" / "player" / gender / f"{state}_4dir.png")
            assert sheet.size == (256, 128)
            for row, direction in enumerate(DIRECTIONS):
                for i, frame in enumerate(get_frames(f"player/{gender}/{state}/{direction}")):
                    assert sheet.crop((i * 32, row * 32, i * 32 + 32, row * 32 + 32)).tobytes() == frame.tobytes()
    for path in (ROOT / "previews").glob("*.gif"):
        with Image.open(path) as image:
            assert image.n_frames == 8, (path, image.n_frames)
    print(f"PASS: {len(ANIMATIONS)} eight-frame loops; {len(expected)} manifest-listed 32x32 PNGs; transparency, grounded bounds, sheet cells and GIF frame counts verified.")


def main():
    characters()
    environment()
    rocks()
    previews()
    manifest = {
        "title": "Witchwood Forager — Expanded Review Art", "version": 2,
        "frame_size": [32, 32], "direction_row_order": list(DIRECTIONS),
        "animations": ANIMATIONS, "static_sprites": STATIC,
        "notes": "Review assets. Timings are art playback suggestions, not gameplay constants.",
    }
    (ROOT / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    verify()


if __name__ == "__main__":
    main()
