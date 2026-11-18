"""Original, grid-drawn pixel art. Run with Python 3 and Pillow >= 9.1."""

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parent
P = {
    "ink": "#28253d", "deep": "#39334f", "purple": "#66517c",
    "lilac": "#a183bb", "lavender": "#d5b5dd", "cream": "#fff0cf",
    "wood": "#735063", "bark": "#a87378", "tan": "#d6a17e",
    "skin": "#f1c49d", "blush": "#db8d93", "hair": "#69434f",
    "teal_dark": "#294c55", "teal": "#397b78", "mint": "#70b698",
    "light": "#b9dfac", "gold": "#e8ad62", "yellow": "#ffe39b",
    "orange": "#bd6a62", "blue": "#6799b6", "ice": "#b9e7df",
    "pink": "#e9a5c1",
}
SPRITES: dict[str, Image.Image] = {}


class Pixel:
    def __init__(self):
        self.im = Image.new("RGBA", (32, 32))
        self.d = ImageDraw.Draw(self.im)

    def rect(self, box, color):
        self.d.rectangle(box, fill=P.get(color, color))

    def poly(self, points, color, outline=None):
        self.d.polygon(points, fill=P.get(color, color),
                       outline=P.get(outline, outline))

    def ellipse(self, box, color, outline=None):
        self.d.ellipse(box, fill=P.get(color, color),
                       outline=P.get(outline, outline))

    def line(self, points, color, width=1):
        self.d.line(points, fill=P.get(color, color), width=width)

    def save(self, name):
        dest = ROOT / "sprites" / f"{name}.png"
        dest.parent.mkdir(parents=True, exist_ok=True)
        self.im.save(dest)
        SPRITES[name] = self.im
        return self.im


def leaf(s, x, y, side=1, color="mint"):
    s.poly([(x, y), (x + 6 * side, y - 5), (x + 7 * side, y - 2),
            (x + 5 * side, y + 1), (x + side, y + 2)], color, "teal_dark")
    s.line([(x + side, y), (x + 5 * side, y - 2)], "light")


def sparkle(s, x, y, color="cream"):
    s.line([(x - 1, y), (x + 1, y)], color)
    s.line([(x, y - 1), (x, y + 1)], color)


def gardener(direction, step=0):
    s = Pixel()
    bob = -1 if step else 0
    # Boots, short overalls, and a large readable satchel.
    s.rect((11, 23, 20, 27), "ink")
    s.rect((12, 23, 15, 26), "purple")
    s.rect((17, 23, 19, 26), "purple")
    for x, lift in ((11, int(step == 1)), (17, int(step == 2))):
        s.rect((x, 27 - lift, x + 4, 29 - lift), "ink")
        s.rect((x + 1, 27 - lift, x + 3, 27 - lift), "wood")
    s.poly([(11, 17 + bob), (20, 17 + bob), (22, 23 + bob),
            (19, 25 + bob), (12, 25 + bob), (9, 23 + bob)], "teal", "ink")
    s.rect((12, 19 + bob, 19, 23 + bob), "mint")
    s.rect((13, 20 + bob, 18, 24 + bob), "teal")
    s.rect((14, 22 + bob, 17, 23 + bob), "teal_dark")
    s.rect((9, 19 + bob, 11, 23 + bob), "ink")
    s.rect((10, 20 + bob, 11, 22 + bob), "skin")
    s.rect((20, 19 + bob, 22, 23 + bob), "ink")
    s.rect((20, 20 + bob, 21, 22 + bob), "skin")
    s.ellipse((10, 8 + bob, 21, 19 + bob), "hair", "ink")
    if direction != "up":
        s.rect((12, 12 + bob, 20, 16 + bob), "skin")
        s.rect((13, 17 + bob, 19, 17 + bob), "tan")
        if direction == "down":
            s.rect((13, 13 + bob, 13, 14 + bob), "ink")
            s.rect((18, 13 + bob, 18, 14 + bob), "ink")
            s.rect((12, 15 + bob, 13, 15 + bob), "blush")
            s.rect((19, 15 + bob, 20, 15 + bob), "blush")
            s.rect((15, 16 + bob, 16, 16 + bob), "hair")
        else:
            s.rect((19, 13 + bob, 19, 14 + bob), "ink")
            s.rect((20, 14 + bob, 21, 15 + bob), "skin")
            s.rect((17, 15 + bob, 18, 15 + bob), "blush")
            s.rect((11, 12 + bob, 13, 16 + bob), "hair")
    else:
        s.rect((12, 12 + bob, 19, 16 + bob), "hair")
        s.line([(12, 13 + bob), (14, 14 + bob), (18, 14 + bob)], "wood")
    # Wide floppy field hat, viewed slightly from above.
    s.poly([(7, 8 + bob), (10, 7 + bob), (11, 4 + bob), (13, 2 + bob),
            (19, 2 + bob), (21, 4 + bob), (22, 7 + bob), (25, 9 + bob),
            (24, 11 + bob), (20, 12 + bob), (10, 11 + bob), (6, 10 + bob)],
           "purple", "ink")
    s.poly([(12, 5 + bob), (14, 3 + bob), (18, 3 + bob), (20, 5 + bob),
            (20, 7 + bob), (11, 7 + bob)], "lilac")
    s.line([(10, 8 + bob), (15, 9 + bob), (21, 8 + bob)], "mint", 2)
    s.line([(8, 10 + bob), (15, 11 + bob), (23, 10 + bob)], "deep")
    s.rect((20, 6 + bob, 21, 8 + bob), "gold")
    s.rect((21, 5 + bob, 22, 6 + bob), "light")
    if direction == "up":
        s.rect((12, 18 + bob, 19, 24 + bob), "ink")
        s.rect((13, 18 + bob, 18, 23 + bob), "bark")
        s.rect((13, 18 + bob, 18, 20 + bob), "tan")
        s.rect((15, 20 + bob, 16, 21 + bob), "gold")
    else:
        s.line([(12, 18 + bob), (20, 24 + bob)], "wood", 2)
        s.rect((20, 22 + bob, 24, 26 + bob), "ink")
        s.rect((21, 22 + bob, 23, 25 + bob), "bark")
        s.rect((21, 22 + bob, 23, 23 + bob), "gold")
    if direction == "left":
        s.im = s.im.transpose(Image.Transpose.FLIP_LEFT_RIGHT)
    return s.save(f"player/{direction}_{('idle', 'walk_1', 'walk_2')[step]}")


def tree():
    s = Pixel()
    s.poly([(13, 17), (20, 17), (20, 25), (24, 29), (19, 29),
            (17, 27), (13, 29), (9, 29), (13, 25)], "wood", "ink")
    s.line([(15, 19), (15, 25), (13, 27)], "bark", 2)
    s.line([(19, 21), (18, 25), (20, 27)], "deep")
    s.poly([(3, 11), (5, 8), (7, 8), (7, 5), (11, 3), (14, 3),
            (16, 1), (21, 2), (24, 5), (26, 6), (27, 10), (30, 13),
            (29, 18), (26, 20), (22, 20), (20, 23), (15, 22),
            (12, 23), (8, 21), (4, 21), (1, 17), (1, 14)], "teal_dark", "ink")
    s.poly([(3, 12), (6, 9), (9, 9), (9, 6), (14, 5), (17, 3),
            (21, 4), (23, 7), (25, 8), (25, 11), (28, 14),
            (25, 17), (20, 16), (17, 19), (12, 17), (8, 19), (4, 17)], "teal")
    s.poly([(5, 11), (10, 10), (10, 7), (15, 6), (17, 4), (21, 5),
            (22, 8), (18, 9), (17, 12), (12, 11), (9, 14), (5, 14)], "mint")
    s.line([(11, 8), (14, 7), (16, 7)], "light")
    s.line([(4, 17), (8, 19), (12, 17)], "teal_dark")
    s.line([(19, 17), (22, 19), (26, 17)], "teal_dark")
    for x, y in ((7, 15), (22, 11), (18, 18)):
        s.rect((x, y, x + 1, y + 1), "lilac")
        s.rect((x, y, x, y), "pink")
    s.save("environment/witchwood_tree")


def plants():
    s = Pixel()
    s.line([(15, 27), (16, 13)], "teal_dark", 2)
    leaf(s, 15, 23, -1)
    leaf(s, 16, 19, 1)
    leaf(s, 16, 15, -1)
    s.poly([(16, 14), (13, 10), (14, 6), (17, 3), (19, 7), (19, 11)], "mint", "teal_dark")
    s.line([(16, 11), (17, 6)], "light")
    for x, y in ((10, 20), (21, 15), (13, 10)):
        s.ellipse((x, y, x + 2, y + 3), "blue")
        s.rect((x, y, x, y), "ice")
    s.save("plants/dew_herb")

    s = Pixel()
    s.line([(16, 27), (16, 14)], "teal_dark", 2)
    leaf(s, 15, 24, -1)
    leaf(s, 16, 21)
    for box in ((12, 3, 19, 12), (7, 7, 16, 14), (16, 7, 25, 14),
                (10, 12, 17, 19), (16, 12, 23, 19)):
        s.ellipse(box, "gold", "orange")
    s.ellipse((11, 7, 21, 16), "wood", "ink")
    s.ellipse((13, 8, 20, 13), "orange")
    s.rect((14, 11, 14, 12), "ink")
    s.rect((18, 11, 18, 12), "ink")
    s.rect((16, 14, 17, 14), "gold")
    s.line([(13, 5), (16, 4), (18, 6)], "yellow")
    s.save("plants/sun_plant")

    s = Pixel()
    s.poly([(13, 16), (20, 16), (20, 23), (23, 26), (20, 28),
            (11, 28), (10, 26), (13, 23)], "lavender", "ink")
    s.rect((14, 20, 16, 25), "cream")
    s.rect((19, 21, 19, 24), "lilac")
    s.ellipse((5, 12, 27, 20), "deep", "ink")
    s.poly([(4, 15), (6, 11), (8, 8), (12, 5), (19, 5), (23, 8),
            (25, 11), (28, 15), (26, 17), (20, 18), (15, 17),
            (9, 18), (5, 17)], "purple", "ink")
    s.poly([(7, 12), (10, 8), (14, 6), (19, 6), (23, 10),
            (24, 13), (19, 14), (14, 13), (9, 15), (6, 15)], "lilac")
    s.ellipse((10, 9, 13, 11), "lavender")
    s.rect((22, 13, 24, 14), "pink")
    s.ellipse((16, 7, 21, 12), "cream")
    s.ellipse((18, 6, 22, 10), "lilac")
    s.save("plants/moon_mushroom")

    s = Pixel()
    s.line([(15, 28), (16, 16)], "purple", 2)
    leaf(s, 15, 25, -1, "lilac")
    leaf(s, 16, 23, 1, "purple")
    s.poly([(16, 4), (19, 9), (25, 8), (23, 14), (26, 18),
            (20, 20), (16, 24), (12, 20), (6, 18), (9, 14),
            (7, 8), (13, 9)], "purple", "ink")
    s.poly([(16, 7), (18, 12), (22, 10), (20, 15), (23, 17),
            (18, 18), (16, 21), (14, 18), (9, 17), (12, 15),
            (10, 10), (14, 12)], "lilac")
    s.ellipse((12, 12, 20, 19), "pink")
    s.ellipse((14, 13, 18, 17), "cream")
    sparkle(s, 5, 6, "ice")
    sparkle(s, 26, 4, "lavender")
    s.rect((27, 23, 27, 23), "ice")
    s.save("plants/midnight_bloom")


def bottle(name, dark=None, light=None, shape="round", emblem=None):
    s = Pixel()
    if shape == "round":
        body = [(12, 10), (20, 10), (21, 14), (25, 17), (26, 22),
                (24, 27), (21, 29), (11, 29), (8, 27), (6, 22), (7, 17), (11, 14)]
    elif shape == "square":
        body = [(12, 10), (20, 10), (20, 13), (25, 16), (25, 27),
                (23, 29), (9, 29), (7, 27), (7, 16), (12, 13)]
    else:
        body = [(12, 10), (20, 10), (20, 14), (26, 23), (26, 27),
                (23, 29), (9, 29), (6, 27), (6, 23), (12, 14)]
    s.poly(body, "blue", "ink")
    s.poly([(13, 12), (18, 12), (18, 16), (22, 18), (22, 25),
            (20, 27), (11, 27), (9, 24), (10, 18), (13, 16)], "teal_dark")
    if dark:
        s.poly([(10, 20), (14, 19), (18, 20), (22, 19), (23, 23),
                (21, 27), (11, 27), (9, 24)], dark)
        s.line([(10, 20), (14, 20), (18, 21), (22, 20)], light)
    s.line([(10, 18), (9, 21), (10, 24)], "ice")
    s.rect((13, 12, 13, 14), "ice")
    s.rect((23, 23, 23, 25), "ice")
    s.rect((11, 8, 21, 11), "ink")
    s.rect((12, 9, 20, 10), "ice")
    s.rect((12, 3, 20, 8), "ink")
    s.rect((13, 4, 19, 7), "bark")
    s.rect((13, 4, 18, 4), "tan")
    s.rect((17, 6, 18, 7), "wood")
    if emblem:
        s.rect((13, 22, 19, 26), "cream")
        if emblem == "leaf":
            s.poly([(14, 25), (15, 23), (18, 23), (17, 25)], "teal")
        elif emblem == "sun":
            s.rect((15, 23, 17, 25), "orange")
            s.rect((16, 22, 16, 26), "gold")
        else:
            s.ellipse((14, 22, 18, 26), "purple")
            s.rect((17, 22, 19, 24), "cream")
    s.save(f"items/{name}")


def sugar():
    s = Pixel()
    s.poly([(10, 11), (8, 5), (14, 6), (17, 4), (23, 5), (21, 11),
            (24, 17), (26, 25), (23, 28), (9, 28), (6, 25), (8, 17)], "tan", "ink")
    s.poly([(11, 12), (19, 12), (22, 18), (23, 25), (20, 26),
            (10, 26), (9, 23)], "cream")
    s.line([(10, 10), (20, 10)], "wood", 2)
    s.line([(12, 7), (14, 9)], "bark")
    s.poly([(12, 19), (16, 17), (20, 19), (20, 23), (16, 25), (12, 23)], "lavender", "purple")
    s.poly([(13, 19), (16, 18), (19, 19), (16, 21)], "cream")
    s.line([(16, 21), (16, 24)], "purple")
    s.save("items/sugar")


def font(size):
    path = Path("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf")
    return ImageFont.truetype(str(path), size) if path.exists() else ImageFont.load_default()


def previews():
    groups = [
        ("THE FORAGER / FOUR DIRECTIONS", [f"player/{d}_idle" for d in ("down", "left", "right", "up")]),
        ("WITCHWOOD / TREE & FORAGE", ["environment/witchwood_tree"] + [f"plants/{n}" for n in ("dew_herb", "sun_plant", "moon_mushroom", "midnight_bloom")]),
        ("APOTHECARY / POTIONS & BASES", [f"items/{n}" for n in ("dew_potion", "sun_potion", "moon_potion", "bottle", "water", "sugar")]),
    ]
    sheet = Image.new("RGB", (1200, 920), "#191d2b")
    d = ImageDraw.Draw(sheet)
    d.text((38, 24), "WITCHWOOD FORAGER", font=font(32), fill=P["cream"])
    d.text((40, 69), "Spooky-cute starter sprites  /  32 x 32 px  /  original pixel art", font=font(16), fill=P["mint"])
    for row, (title, names) in enumerate(groups):
        y = 122 + row * 254
        d.text((40, y), title, font=font(16), fill=P["lavender"])
        for col, name in enumerate(names):
            x = 40 + col * 190
            for cy in range(8):
                for cx in range(8):
                    color = "#303549" if (cx + cy) % 2 else "#353b50"
                    d.rectangle((x + cx * 20, y + 33 + cy * 20,
                                 x + cx * 20 + 19, y + 52 + cy * 20), fill=color)
            sheet.paste(SPRITES[name].resize((160, 160), Image.Resampling.NEAREST), (x, y + 33), SPRITES[name].resize((160, 160), Image.Resampling.NEAREST))
            label = name.split("/")[-1].replace("_idle", "").replace("_", " ").title()
            d.text((x, y + 203), label, font=font(14), fill=P["cream"])
    d.text((40, 897), "Preview at 5x nearest-neighbor  |  Transparent PNG originals in sprites/", font=font(13), fill=P["mint"])
    sheet.save(ROOT / "preview.png")

    # Native-resolution atlas: cells never include labels or padding.
    names = list(SPRITES)
    atlas = Image.new("RGBA", (8 * 32, ((len(names) + 7) // 8) * 32))
    for i, name in enumerate(names):
        atlas.paste(SPRITES[name], ((i % 8) * 32, (i // 8) * 32))
    atlas.save(ROOT / "atlas.png")

    for direction in ("down", "left", "right", "up"):
        frames = [SPRITES[f"player/{direction}_{frame}"] for frame in ("walk_1", "idle", "walk_2", "idle")]
        # Dark background is only used for the review GIF, not the PNGs.
        animated = []
        for frame in frames:
            bg = Image.new("RGBA", (32, 32), "#303549")
            bg.alpha_composite(frame)
            animated.append(bg.convert("RGB").resize((256, 256), Image.Resampling.NEAREST))
        animated[0].save(ROOT / f"walk_{direction}_preview.gif", save_all=True,
                         append_images=animated[1:], duration=170, loop=0)

    walk = Image.new("RGBA", (96, 128))
    for row, direction in enumerate(("down", "left", "right", "up")):
        for col, frame in enumerate(("idle", "walk_1", "walk_2")):
            walk.paste(SPRITES[f"player/{direction}_{frame}"], (col * 32, row * 32))
    walk.save(ROOT / "player_sheet.png")


def main():
    for direction in ("down", "left", "right", "up"):
        for step in range(3):
            gardener(direction, step)
    tree()
    plants()
    bottle("dew_potion", "teal", "light", emblem="leaf")
    bottle("sun_potion", "orange", "yellow", shape="square", emblem="sun")
    bottle("moon_potion", "purple", "pink", shape="triangle", emblem="moon")
    bottle("bottle")
    bottle("water", "blue", "ice")
    sugar()
    previews()
    print(f"Created {len(SPRITES)} original 32x32 sprites, atlas, player sheet, and previews in {ROOT}")


if __name__ == "__main__":
    main()
