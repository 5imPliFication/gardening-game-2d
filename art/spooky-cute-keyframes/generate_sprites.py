"""Native-grid key poses. No raster shifting, warping or interpolation."""

import importlib.util
import json
import sys
from pathlib import Path

from PIL import Image, ImageDraw


ROOT = Path(__file__).resolve().parent
sys.dont_write_bytecode = True
SPEC = importlib.util.spec_from_file_location(
    "previous_art", ROOT.parent / "spooky-cute-expanded" / "generate_sprites.py"
)
OLD = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(OLD)
OLD.ROOT = ROOT
P, Pixel = OLD.P, OLD.Pixel
DIRECTIONS = ("down", "left", "right", "up")
ANIMATIONS = {}
STATIC = {}
TIMING = {"walk": 100, "idle": 400, "rest": 500, "foliage": 160}

# Explicit eight-pose skeletons: contact, down, passing, up, then opposite leg.
# Each pair contains a knee and ankle for the left/far and right/near leg.
FRONT_GAIT = (
    (((12, 25), (12, 28)), ((19, 24), (19, 25))),
    (((12, 26), (12, 28)), ((19, 25), (20, 26))),
    (((13, 25), (13, 28)), ((20, 24), (20, 25))),
    (((13, 24), (13, 27)), ((19, 25), (19, 27))),
    (((12, 24), (12, 25)), ((19, 25), (19, 28))),
    (((12, 25), (11, 26)), ((19, 26), (19, 28))),
    (((11, 24), (11, 25)), ((18, 25), (18, 28))),
    (((12, 25), (12, 27)), ((18, 24), (18, 27))),
)
SIDE_GAIT = (
    (((13, 25), (10, 27)), ((18, 25), (21, 28))),
    (((13, 24), (11, 26)), ((18, 26), (20, 28))),
    (((17, 24), (18, 25)), ((16, 26), (16, 28))),
    (((19, 24), (22, 27)), ((13, 25), (12, 27))),
    (((20, 25), (23, 28)), ((12, 25), (9, 27))),
    (((20, 26), (22, 28)), ((12, 24), (10, 26))),
    (((18, 26), (18, 28)), ((15, 24), (16, 25))),
    (((15, 25), (14, 27)), ((18, 24), (20, 27))),
)
BOB = (0, 1, 0, -1, 0, 1, 0, -1)
SIDE_HANDS = (
    ((22, 22), (10, 24)), ((21, 23), (12, 24)),
    ((19, 24), (15, 24)), ((16, 24), (19, 23)),
    ((13, 24), (23, 22)), ((14, 24), (22, 23)),
    ((16, 24), (19, 24)), ((19, 23), (14, 24)),
)
FRONT_HANDS = (
    ((8, 22), (22, 25)), ((8, 23), (22, 24)),
    ((9, 24), (21, 23)), ((9, 25), (22, 22)),
    ((8, 25), (22, 22)), ((8, 24), (22, 23)),
    ((9, 23), (21, 24)), ((8, 22), (21, 25)),
)


def arm(s, points):
    s.line(points, "ink", 3)
    s.line(points[:2], "mint", 2)
    s.line(points[1:], "teal", 2)
    x, y = points[-1]
    s.rect((x, y, x + 1, y + 1), "skin")


def character(gender, direction, state, pose):
    s = Pixel()
    female, side = gender == "female", direction in ("left", "right")
    seated, walking = state == "rest", state == "walk"
    bob = BOB[pose] if walking else (0, -1, 0, 0)[pose]
    h = (3 if seated else 0) + bob
    # Far-side hair is behind the arms/dress; near-side hair is added later.
    tail_bend = (0, 0, 1, 1, 0, 0, -1, -1)[pose] if walking else (0, 1, 0, -1)[pose]
    if female:
        for x in ((8,) if side else (7, 22)):
            s.poly([(x, 10 + h), (x + 3, 10 + h), (x + 4, 15 + h),
                    (x + 3 + tail_bend, 20 + h), (x + 1 + tail_bend, 23 + h),
                    (x - 1 + tail_bend, 21 + h), (x, 16 + h)], "hair", "ink")
            s.line([(x + 1, 13 + h), (x + 2, 17 + h), (x + 1 + tail_bend, 20 + h)], "bark")
    if seated:
        s.ellipse((10, 25, 22, 29), "deep", "ink")
        if side:
            s.poly([(11, 24), (17, 24), (21, 26), (25, 27), (25, 29), (19, 29), (14, 27), (10, 27)], "purple", "ink")
            s.line([(15, 25), (19, 26), (21, 28)], "lilac")
            s.rect((22, 28, 25, 29), "wood")
        else:
            for points in ([(10, 24), (14, 24), (14, 28), (11, 29), (8, 28)],
                           [(18, 24), (22, 24), (24, 28), (22, 29), (18, 28)]):
                s.poly(points, "lavender" if female else "purple", "ink")
            s.rect((9, 28, 13, 29), "wood")
            s.rect((19, 28, 23, 29), "wood")
    elif walking:
        for leg, (knee, ankle) in enumerate((SIDE_GAIT if side else FRONT_GAIT)[pose]):
            hip = ((17 if leg == 0 else 14) if side else (12 if leg == 0 else 19), 22 + bob)
            s.line([hip, knee, ankle], "ink", 4)
            s.line([hip, knee, ankle], "lavender" if female else ("deep" if leg == 0 and side else "purple"), 2)
            x, y = ankle
            s.poly([(x - 1, y - 1), (x + 1, y - 1), (x + 3 if side else x + 2, y),
                    (x + 3 if side else x + 2, y + 1), (x - 2, y + 1)], "wood", "ink")
            s.line([(x - 1, y), (x + 1, y)], "bark")
    else:
        s.poly([(11, 23), (15, 23), (15, 29), (10, 29), (10, 27)], "lavender" if female else "purple", "ink")
        s.poly([(17, 23), (20, 23), (21, 27), (21, 29), (17, 29)], "lavender" if female else "purple", "ink")
        s.rect((11, 27, 14, 28), "wood")
        s.rect((18, 27, 20, 28), "wood")
        s.line([(11, 28), (14, 28)], "bark")
        s.line([(18, 28), (20, 28)], "bark")
    # Dress with puff sleeves, fitted bodice, apron, and a scalloped lilac hem.
    if female:
        hems = ((9, 22), (10, 22), (11, 21), (10, 22), (9, 22), (9, 21), (10, 20), (9, 21))
        left, right = hems[pose] if walking else ((10, 21), (9, 22), (10, 22), (10, 21))[pose]
        skirt_y = 24 + (2 if seated else 0)
        s.poly([(12, 17 + h), (19, 17 + h), (19, 20 + h), (right, skirt_y),
                (right - 2, skirt_y + 1), (16, skirt_y), (12, skirt_y + 1), (left, skirt_y), (12, 20 + h)], "teal", "ink")
        s.line([(left + 1, skirt_y), (12, skirt_y), (15, skirt_y - 1), (18, skirt_y), (right - 1, skirt_y)], "lilac")
        s.poly([(13, 18 + h), (18, 18 + h), (18, 20 + h), (19, skirt_y - 1), (13, skirt_y - 1)], "cream")
        s.line([(12, 21 + h), (19, 21 + h)], "purple")
        s.rect((15, 21 + h, 16, 21 + h), "gold")
        s.ellipse((9, 17 + h, 12, 20 + h), "lavender", "purple")
        s.ellipse((19, 17 + h, 22, 20 + h), "lavender", "purple")
    else:
        s.poly([(11, 17 + h), (20, 17 + h), (21, 23 + h), (19, 25 + h), (11, 25 + h), (10, 21 + h)], "teal", "ink")
        s.rect((13, 18 + h, 18, 23 + h), "mint")
        s.poly([(11, 17 + h), (14, 18 + h), (14, 24 + h), (11, 24 + h)], "teal_dark")
        s.poly([(18, 18 + h), (20, 17 + h), (20, 24 + h), (18, 24 + h)], "teal_dark")
        s.rect((12, 24 + h, 19, 24 + h), "wood")
        s.rect((15, 24 + h, 16, 24 + h), "gold")
        s.poly([(12, 17 + h), (19, 17 + h), (17 + tail_bend, 20 + h), (14, 19 + h)], "lilac", "purple")
    if walking:
        hands = (SIDE_HANDS if side else FRONT_HANDS)[pose]
        arms = [((11 if i == 0 else 20, 18 + bob),
                 (((11 if i == 0 else 20) + hand[0]) // 2, 21 + bob), hand) for i, hand in enumerate(hands)]
    elif seated:
        arms = (
            (((11, 22), (10, 25), (13, 26)), ((20, 22), (22, 25), (19, 26))),
            (((11, 22), (10, 24), (14, 25)), ((20, 22), (21, 24), (18, 25))),
            (((11, 22), (11, 24), (14, 25)), ((20, 22), (21, 25), (19, 26))),
            (((11, 22), (10, 25), (13, 26)), ((20, 22), (22, 24), (18, 25))),
        )[pose]
    else:
        arms = (
            (((10, 19), (9, 21), (9, 24)), ((21, 19), (22, 21), (22, 24))),
            (((10, 18), (8, 21), (9, 23)), ((21, 18), (23, 21), (22, 23))),
            (((10, 19), (9, 21), (10, 23)), ((21, 19), (22, 21), (21, 23))),
            (((10, 20), (9, 22), (9, 24)), ((21, 20), (23, 22), (21, 24))),
        )[pose]
    for points in arms:
        arm(s, points)
    s.ellipse((10, 5 + h, 22, 17 + h), "hair", "ink")
    if direction != "up":
        s.ellipse((11, 9 + h, 21, 17 + h), "skin")
        for x in ((19,) if side else (14, 18)):
            if seated or (state == "idle" and pose == 2):
                s.line([(x - 1, 14 + h), (x, 14 + h)], "hair")
            else:
                s.rect((x, 13 + h, x, 14 + h), "ink")
        s.rect((12, 15 + h, 13, 15 + h), "blush")
        s.rect((19, 15 + h, 20, 15 + h), "blush")
        s.rect((16, 16 + h, 17, 16 + h), "hair")
        if side:
            s.rect((20, 14 + h, 21, 15 + h), "skin")
            s.rect((10, 10 + h, 13, 15 + h), "hair")
    else:
        s.line([(12, 13 + h), (15, 14 + h), (19, 13 + h)], "wood")
    # Exposed hairstyles replace the large hats so they read at native size.
    if female:
        s.poly([(10, 10 + h), (10, 6 + h), (13, 3 + h), (18, 3 + h), (21, 5 + h),
                (23, 9 + h), (21, 11 + h), (18, 8 + h), (15, 9 + h), (12, 11 + h)], "hair", "ink")
        s.line([(12, 7 + h), (14, 5 + h), (18, 5 + h), (20, 7 + h)], "bark")
        s.line([(12, 7 + h), (16, 6 + h), (21, 7 + h)], "lilac")
        for x in ((9,) if side else (7, 23)):
            s.poly([(x - 1, 8 + h), (x + 2, 9 + h), (x + 4, 8 + h), (x + 4, 12 + h), (x + 2, 11 + h), (x - 1, 12 + h)], "lilac", "purple")
            s.rect((x + 1, 9 + h, x + 2, 10 + h), "pink")
        if side:
            s.poly([(10, 11 + h), (13, 12 + h), (14, 17 + h), (12 + tail_bend, 22 + h),
                    (9 + tail_bend, 23 + h), (8 + tail_bend, 20 + h), (10, 16 + h)], "hair", "ink")
            s.line([(11, 14 + h), (12, 17 + h), (10 + tail_bend, 21 + h)], "bark")
        if direction == "up":
            s.line([(12, 10 + h), (15, 12 + h), (19, 10 + h)], "bark")
    else:
        s.poly([(9, 10 + h), (10, 6 + h), (9, 4 + h), (13, 5 + h), (16, 2 + h),
                (17, 4 + h), (21, 3 + h), (20, 5 + h), (23, 7 + h), (22, 11 + h),
                (19, 10 + h), (18, 8 + h), (15, 10 + h), (12, 9 + h), (11, 12 + h)], "hair", "ink")
        s.line([(12, 6 + h), (15, 5 + h), (17, 5 + h)], "bark")
        s.line([(16, 7 + h), (19, 6 + h), (21, 7 + h)], "wood")
        if direction == "up":
            s.line([(12, 11 + h), (16, 13 + h), (20, 11 + h)], "wood")
    if direction == "up":
        if female:
            s.poly([(12, 20 + h), (15, 21 + h), (18, 20 + h), (18, 23 + h), (15, 22 + h), (12, 23 + h)], "lilac", "purple")
            s.rect((15, 21 + h, 16, 22 + h), "pink")
        else:
            s.poly([(12, 18 + h), (19, 18 + h), (19, 24 + h), (12, 24 + h)], "bark", "ink")
            s.rect((13, 19 + h, 18, 20 + h), "tan")
            s.rect((15, 21 + h, 16, 22 + h), "gold")
    elif not seated:
        s.line([(12, 19), (22, 24)], "wood")
        bag_pose = (0, 0, 1, 1, 2, 2, 3, 3)[pose] if walking else pose
        bags = ([(22, 22), (25, 22), (25, 26), (22, 26)], [(22, 21), (25, 22), (24, 26), (21, 25)],
                [(21, 22), (24, 21), (25, 25), (22, 26)], [(22, 22), (25, 22), (25, 25), (22, 26)])
        s.poly(bags[bag_pose], "bark", "ink")
        s.line(bags[bag_pose][:2], "tan")
        s.rect((22, 23, 23, 23), "gold")
    return s.im.transpose(Image.Transpose.FLIP_LEFT_RIGHT) if direction == "left" else s.im


def leaf(s, points):
    s.poly(points, "mint", "teal_dark")
    s.line([points[0], points[2]], "light")


def plant(kind, pose):
    s = Pixel()
    # Each stalk, leaf blade and flower silhouette is drawn for this pose.
    stems = (((16, 27), (15, 20), (16, 13)), ((16, 27), (16, 20), (17, 13)),
             ((16, 27), (15, 21), (15, 13)), ((16, 27), (16, 20), (16, 14)),
             ((16, 27), (16, 21), (17, 14)), ((16, 27), (16, 20), (17, 14)),
             ((16, 27), (15, 21), (16, 14)), ((16, 27), (15, 20), (15, 14)))
    blades = (
        ([(15, 23), (8, 18), (8, 22), (12, 25)], [(16, 21), (23, 15), (23, 20), (19, 23)]),
        ([(16, 23), (9, 17), (8, 21), (12, 24)], [(16, 21), (22, 17), (24, 18), (20, 23)]),
        ([(15, 23), (8, 20), (7, 23), (12, 25)], [(16, 21), (21, 14), (23, 18), (20, 22)]),
        ([(16, 23), (9, 19), (8, 23), (13, 25)], [(16, 21), (23, 16), (24, 20), (19, 23)]),
        ([(15, 23), (9, 18), (8, 22), (12, 25)], [(16, 21), (23, 16), (24, 19), (19, 23)]),
        ([(16, 23), (9, 18), (8, 21), (13, 24)], [(16, 21), (23, 17), (24, 19), (20, 23)]),
        ([(15, 23), (8, 19), (7, 23), (12, 25)], [(16, 21), (22, 15), (23, 19), (19, 23)]),
        ([(15, 23), (8, 19), (8, 22), (12, 25)], [(16, 21), (22, 15), (23, 18), (20, 23)]),
    )
    s.line(stems[pose], "teal_dark", 2)
    if kind != "moon_mushroom":
        for points in blades[pose]:
            leaf(s, points)
    if kind == "dew_herb":
        buds = (
            [(16, 15), (13, 11), (14, 6), (17, 3), (19, 7), (19, 11)],
            [(17, 15), (14, 11), (15, 7), (19, 4), (20, 9), (19, 12)],
            [(15, 15), (12, 12), (12, 8), (15, 3), (17, 7), (18, 11)],
            [(16, 16), (13, 12), (14, 8), (16, 4), (19, 8), (19, 12)],
            [(17, 15), (14, 11), (14, 7), (18, 3), (20, 8), (19, 11)],
            [(17, 15), (14, 12), (15, 8), (18, 4), (20, 8), (19, 12)],
            [(16, 16), (13, 12), (13, 7), (16, 3), (18, 7), (18, 12)],
            [(15, 15), (13, 11), (13, 7), (16, 3), (18, 8), (19, 11)],
        )
        leaf(s, buds[pose])
        for x, y in ((10, 21), (21, 18)):
            s.ellipse((x, y, x + 2, y + 2), "blue")
            s.rect((x + (pose % 2), y, x + (pose % 2), y), "ice")
    elif kind == "sun_plant":
        petals = (
            [(12, 3, 19, 12), (7, 7, 16, 14), (17, 7, 25, 14), (10, 12, 17, 19), (16, 12, 23, 19)],
            [(13, 4, 20, 12), (8, 6, 16, 14), (17, 9, 26, 15), (11, 12, 18, 19), (17, 13, 23, 19)],
            [(12, 3, 18, 12), (6, 9, 15, 15), (16, 6, 24, 14), (9, 13, 16, 19), (16, 12, 22, 19)],
            [(12, 4, 19, 12), (8, 8, 16, 15), (17, 8, 24, 15), (10, 13, 17, 20), (16, 13, 23, 20)],
            [(13, 3, 20, 12), (8, 7, 16, 14), (17, 8, 26, 14), (11, 12, 17, 19), (17, 12, 23, 19)],
            [(13, 4, 20, 12), (8, 7, 16, 15), (17, 9, 25, 15), (11, 13, 18, 20), (17, 13, 23, 20)],
            [(12, 4, 18, 12), (7, 9, 16, 15), (16, 7, 24, 14), (10, 13, 17, 20), (16, 12, 22, 19)],
            [(12, 3, 19, 12), (7, 8, 15, 15), (16, 7, 25, 14), (9, 12, 16, 19), (16, 12, 23, 19)],
        )
        for box in petals[pose]:
            s.ellipse(box, "gold", "orange")
        s.ellipse((11, 8, 21, 16), "wood", "ink")
        s.ellipse((13, 9, 19, 12), "orange")
        for x in (14, 18):
            s.rect((x, 12, x, 13), "ink")
        s.rect((16, 15, 17, 15), "gold")
    elif kind == "moon_mushroom":
        stalks = (
            [(13, 16), (20, 16), (20, 24), (23, 27), (20, 28), (11, 28), (10, 26), (13, 23)],
            [(14, 17), (21, 17), (20, 23), (23, 27), (20, 28), (11, 28), (10, 26), (13, 23)],
            [(12, 16), (19, 16), (19, 23), (23, 27), (20, 28), (11, 28), (10, 26), (13, 23)],
            [(13, 17), (20, 17), (20, 23), (23, 27), (20, 28), (11, 28), (10, 26), (13, 23)],
            [(13, 16), (21, 16), (20, 23), (23, 27), (20, 28), (11, 28), (10, 26), (13, 23)],
            [(14, 17), (20, 17), (20, 24), (23, 27), (20, 28), (11, 28), (10, 26), (13, 23)],
            [(12, 17), (20, 17), (19, 24), (23, 27), (20, 28), (11, 28), (10, 26), (13, 23)],
            [(13, 16), (19, 16), (20, 23), (23, 27), (20, 28), (11, 28), (10, 26), (13, 23)],
        )
        caps = (
            [(4, 15), (7, 9), (12, 5), (19, 5), (24, 9), (28, 15), (26, 17), (20, 18), (15, 17), (9, 18), (5, 17)],
            [(5, 14), (8, 9), (13, 6), (20, 6), (25, 11), (28, 17), (24, 19), (18, 18), (12, 17), (6, 17)],
            [(4, 17), (7, 11), (11, 5), (18, 5), (23, 8), (27, 14), (26, 17), (20, 17), (14, 18), (8, 19)],
            [(4, 16), (7, 11), (12, 7), (19, 7), (24, 11), (28, 16), (25, 19), (19, 18), (14, 19), (8, 18)],
            [(4, 15), (7, 9), (13, 5), (20, 6), (24, 10), (28, 16), (25, 18), (19, 18), (14, 17), (8, 18)],
            [(5, 15), (8, 10), (13, 6), (20, 7), (24, 11), (28, 17), (25, 19), (19, 18), (13, 18), (6, 17)],
            [(4, 17), (7, 11), (12, 6), (19, 6), (23, 10), (28, 15), (26, 18), (20, 18), (14, 19), (8, 19)],
            [(4, 16), (7, 10), (12, 5), (18, 5), (23, 9), (28, 15), (26, 17), (20, 17), (14, 18), (8, 18)],
        )
        s.poly(stalks[pose], "lavender", "ink")
        s.line([(15, 21), (15, 25)], "cream", 2)
        s.poly(caps[pose], "purple", "ink")
        s.poly([caps[pose][1], caps[pose][2], caps[pose][3], caps[pose][4], (23, 14), (17, 13), (10, 15), (7, 14)], "lilac")
        s.ellipse((16, 8, 21, 13), "cream")
        s.ellipse((18, 7, 22, 11), "lilac")
        s.ellipse((10, 10, 12, 12), "lavender")
    else:
        flowers = (
            [(16, 4), (19, 10), (25, 8), (22, 14), (26, 18), (20, 19), (16, 23), (12, 19), (6, 18), (10, 14), (7, 8), (13, 10)],
            [(17, 5), (19, 11), (26, 10), (22, 15), (24, 20), (19, 19), (15, 23), (13, 19), (7, 16), (11, 13), (9, 7), (14, 10)],
            [(15, 4), (18, 10), (23, 7), (22, 13), (26, 16), (20, 19), (17, 23), (13, 20), (7, 20), (9, 15), (6, 10), (12, 11)],
            [(16, 6), (19, 11), (24, 9), (22, 15), (25, 19), (20, 20), (16, 22), (12, 20), (7, 18), (10, 15), (8, 9), (13, 11)],
            [(16, 4), (19, 10), (25, 9), (22, 15), (25, 19), (20, 19), (16, 23), (12, 19), (7, 17), (10, 14), (8, 8), (13, 10)],
            [(17, 5), (19, 11), (25, 10), (22, 15), (24, 20), (20, 20), (16, 23), (13, 19), (7, 17), (11, 14), (9, 8), (14, 11)],
            [(16, 5), (19, 11), (24, 8), (22, 14), (26, 18), (20, 20), (17, 23), (12, 20), (7, 19), (10, 15), (7, 10), (13, 11)],
            [(15, 4), (18, 10), (24, 8), (22, 14), (26, 17), (20, 19), (16, 23), (12, 19), (6, 19), (9, 14), (7, 9), (12, 10)],
        )
        s.poly(flowers[pose], "purple", "ink")
        for x, y in flowers[pose][::2]:
            s.line([(16, 15), ((x + 16) // 2, (y + 15) // 2)], "lilac", 2)
        s.ellipse((12, 12, 20, 19), "pink")
        s.ellipse((14, 13, 18, 17), "cream" if pose in (1, 2) else "yellow")
        glints = ((5, 5), (26, 5), (27, 23), (5, 21), (5, 5), (26, 5), (5, 21), (27, 23))
        gx, gy = glints[pose]
        if pose < 4:
            OLD.BASE.sparkle(s, gx, gy, "ice")
        else:
            s.rect((gx, gy, gx, gy), "lavender")
    return s.im


def tree(kind, pose):
    s = Pixel()
    # The trunk/root drawing is identical; branch and foliage shapes are redrawn.
    birch = kind == "silver_birch"
    s.poly([(13, 14), (19, 14), (19, 25), (23, 29), (18, 29),
            (16, 27), (12, 29), (9, 29), (13, 25)], "lavender" if birch else "wood", "ink")
    s.line([(15, 18), (15, 25), (13, 27)], "purple" if birch else "bark", 2)
    if birch:
        s.line([(16, 23), (18, 23)], "purple")
        s.line([(14, 26), (16, 26)], "purple")
    if kind in ("witchwood", "silver_birch"):
        crowns = (
            [(2, 14), (5, 9), (8, 9), (8, 5), (13, 3), (16, 1), (22, 3), (25, 8), (27, 9), (29, 15), (27, 20), (22, 20), (19, 23), (13, 21), (9, 23), (3, 20)],
            [(2, 13), (5, 8), (9, 9), (9, 5), (14, 3), (17, 2), (23, 4), (25, 9), (28, 11), (29, 17), (26, 21), (21, 20), (18, 22), (12, 21), (8, 22), (3, 19)],
            [(2, 16), (4, 11), (7, 9), (7, 6), (12, 3), (15, 1), (21, 2), (25, 7), (27, 8), (29, 14), (28, 19), (23, 21), (20, 22), (14, 22), (10, 21), (4, 21)],
            [(2, 15), (5, 10), (9, 10), (8, 6), (13, 4), (16, 2), (22, 4), (24, 8), (27, 10), (29, 16), (27, 20), (22, 21), (19, 22), (13, 20), (9, 22), (3, 19)],
            [(2, 14), (5, 9), (9, 9), (8, 5), (14, 3), (16, 1), (23, 3), (25, 8), (28, 10), (29, 16), (27, 20), (22, 20), (19, 23), (13, 21), (9, 22), (3, 20)],
            [(2, 14), (5, 9), (9, 10), (9, 6), (14, 4), (17, 2), (23, 4), (25, 9), (28, 11), (29, 16), (26, 21), (21, 21), (18, 22), (12, 21), (8, 22), (3, 19)],
            [(2, 16), (4, 10), (8, 10), (8, 6), (13, 4), (15, 2), (21, 3), (24, 8), (27, 9), (29, 15), (28, 20), (23, 21), (20, 22), (13, 21), (10, 22), (3, 20)],
            [(2, 15), (4, 10), (8, 9), (7, 5), (12, 3), (15, 1), (22, 3), (25, 7), (27, 9), (29, 14), (28, 20), (23, 20), (20, 23), (14, 21), (10, 22), (4, 20)],
        )
        if birch:
            boxes = (
                ((4, 8, 17, 20), (13, 5, 27, 18), (7, 2, 21, 14)),
                ((4, 7, 18, 19), (14, 7, 28, 19), (8, 3, 22, 13)),
                ((3, 10, 16, 21), (12, 4, 26, 17), (6, 2, 20, 15)),
                ((4, 9, 18, 20), (13, 6, 27, 19), (7, 3, 21, 14)),
                ((4, 8, 18, 20), (14, 6, 27, 18), (8, 2, 21, 14)),
                ((4, 8, 18, 19), (14, 7, 27, 19), (8, 3, 22, 14)),
                ((3, 10, 17, 20), (12, 5, 26, 18), (6, 3, 21, 15)),
                ((3, 9, 17, 21), (13, 5, 26, 17), (7, 2, 20, 14)),
            )
            for box in boxes[pose]:
                s.ellipse(box, "teal", "ink")
        else:
            s.poly(crowns[pose], "teal_dark", "ink")
            s.poly([crowns[pose][1], crowns[pose][3], crowns[pose][4], crowns[pose][5], crowns[pose][6], crowns[pose][7], (25, 15), (21, 16), (17, 19), (12, 17), (8, 19), (4, 17)], "teal")
        # Leaf clumps turn/overlap differently in each key drawing.
        clumps = (
            [(6, 11), (10, 9), (10, 6), (15, 5), (17, 3), (21, 5), (21, 8), (17, 10), (13, 10), (9, 14), (5, 14)],
            [(6, 10), (11, 9), (11, 6), (16, 5), (18, 4), (22, 6), (21, 9), (17, 11), (13, 10), (10, 13), (5, 13)],
            [(5, 13), (9, 10), (9, 7), (14, 5), (16, 3), (20, 4), (21, 7), (16, 9), (12, 11), (8, 15), (5, 15)],
            [(6, 12), (10, 10), (10, 7), (15, 6), (17, 4), (21, 6), (20, 9), (16, 10), (13, 11), (10, 14), (6, 14)],
            [(6, 11), (11, 9), (10, 6), (16, 5), (17, 3), (22, 5), (21, 8), (17, 11), (13, 10), (9, 13), (5, 14)],
            [(6, 11), (11, 10), (11, 7), (16, 5), (18, 4), (22, 6), (21, 9), (17, 10), (13, 11), (10, 14), (5, 13)],
            [(5, 12), (10, 10), (9, 7), (15, 6), (16, 4), (21, 5), (20, 8), (16, 10), (12, 11), (9, 15), (5, 14)],
            [(5, 12), (9, 10), (10, 6), (14, 5), (16, 3), (21, 4), (21, 8), (17, 10), (12, 10), (9, 14), (5, 15)],
        )
        s.poly(clumps[pose], "mint")
        s.line([(11, 8), (14, 6), (17, 6)], "light")
        for x, y in (((8, 17), (23, 12)), ((8, 16), (24, 14)), ((7, 18), (22, 11)), ((9, 17), (23, 13)),
                     ((8, 17), (24, 13)), ((9, 16), (24, 14)), ((8, 18), (22, 12)), ((7, 17), (23, 12)))[pose]:
            s.rect((x, y, x + 1, y + 1), "gold" if birch else "lilac")
    elif kind == "moon_pine":
        tips = ((16, 15, 16), (17, 16, 15), (15, 14, 17), (16, 16, 16),
                (17, 15, 16), (17, 16, 16), (15, 15, 17), (16, 14, 16))[pose]
        for level, (top, bottom, left, right) in enumerate(((2, 12, 8, 24), (8, 20, 5, 27), (15, 26, 3, 29))):
            tx = tips[level]
            s.poly([(tx, top), (tx + 3, top + 4), (right - 2, bottom - 4), (right, bottom - 1),
                    (right - 5, bottom), (tx, bottom - 1), (left + 5, bottom), (left, bottom - 1), (left + 3, bottom - 5)], "teal_dark", "ink")
            s.poly([(tx, top + 2), (tx + 3, top + 5), (right - 4, bottom - 3),
                    (tx, bottom - 4), (left + 3, bottom - 2)], "teal")
            s.line([(tx, top + 3), (left + 5, bottom - 4)], "mint")
        s.rect((11, 22, 12, 23), "lilac")
    else:
        s.poly([(3, 11), (5, 6), (11, 3), (19, 2), (25, 6), (28, 11),
                (27, 16), (22, 17), (18, 15), (12, 17), (7, 16)], "purple", "ink")
        s.poly([(5, 11), (7, 7), (12, 5), (19, 4), (24, 8), (26, 12), (22, 14), (17, 12), (12, 15), (7, 13)], "lilac")
        ends = (
            ((4, 12, 4, 22), (8, 11, 7, 24), (12, 13, 13, 21), (21, 12, 22, 21), (26, 12, 26, 24)),
            ((4, 12, 5, 22), (8, 11, 9, 23), (12, 13, 14, 21), (21, 12, 23, 22), (26, 12, 27, 23)),
            ((4, 12, 3, 21), (8, 11, 6, 23), (12, 13, 11, 22), (21, 12, 20, 21), (26, 12, 24, 24)),
            ((4, 12, 4, 23), (8, 11, 8, 24), (12, 13, 12, 21), (21, 12, 21, 22), (26, 12, 26, 23)),
            ((4, 12, 5, 22), (8, 11, 8, 24), (12, 13, 14, 21), (21, 12, 22, 21), (26, 12, 27, 24)),
            ((4, 12, 5, 23), (8, 11, 9, 24), (12, 13, 13, 21), (21, 12, 23, 22), (26, 12, 27, 23)),
            ((4, 12, 3, 23), (8, 11, 7, 24), (12, 13, 11, 22), (21, 12, 20, 22), (26, 12, 25, 23)),
            ((4, 12, 3, 22), (8, 11, 6, 24), (12, 13, 12, 21), (21, 12, 21, 21), (26, 12, 25, 24)),
        )
        for x, y, ex, ey in ends[pose]:
            s.poly([(x - 1, y), (x + 2, y), (ex + 2, ey - 2), (ex, ey), (ex - 1, ey - 1)], "purple", "ink")
            s.line([(x, y), (ex, ey - 2)], "lilac")
            s.rect((ex, ey - 1, ex, ey), "pink")
        s.line([(10, 7), (15, 5), (20, 6)], "lavender")
    return s.im


def save_frame(image, name):
    path = ROOT / "sprites" / f"{name}.png"
    path.parent.mkdir(parents=True, exist_ok=True)
    image.save(path)
    return path.relative_to(ROOT).as_posix()


def animation(name, frames, duration, poses):
    paths = [save_frame(im, f"{name}/{i:02}") for i, im in enumerate(frames)]
    sheet = Image.new("RGBA", (32 * len(frames), 32))
    for i, im in enumerate(frames):
        sheet.paste(im, (i * 32, 0))
    path = ROOT / "sheets" / f"{name}.png"
    path.parent.mkdir(parents=True, exist_ok=True)
    sheet.save(path)
    ANIMATIONS[name] = {"frames": paths, "sheet": path.relative_to(ROOT).as_posix(),
                        "frame_size": [32, 32], "anchor_px": [16, 29], "loop": True,
                        "durations_ms": [duration] * len(frames), "pose_names": poses}


def frames_for(name):
    return [Image.open(ROOT / path).convert("RGBA") for path in ANIMATIONS[name]["frames"]]


def build():
    for gender in ("male", "female"):
        for state in ("walk", "idle", "rest"):
            count = 8 if state == "walk" else 4
            all_dirs = Image.new("RGBA", (32 * count, 128))
            for row, direction in enumerate(DIRECTIONS):
                frames = [character(gender, direction, state, i) for i in range(count)]
                labels = (["left_contact", "left_down", "left_passing", "left_up", "right_contact", "right_down", "right_passing", "right_up"] if state == "walk" else
                          ["relaxed", "inhale", "settle", "exhale"])
                animation(f"player/{gender}/{state}/{direction}", frames, TIMING[state], labels)
                for i, im in enumerate(frames):
                    all_dirs.paste(im, (i * 32, row * 32))
            all_dirs.save(ROOT / "sheets" / "player" / gender / f"{state}_4dir.png")
    for kind in ("witchwood", "moon_pine", "lavender_willow", "silver_birch"):
        animation(f"environment/trees/{kind}", [tree(kind, i) for i in (0, 4, 1, 5, 3, 6, 2, 7)], TIMING["foliage"],
                  ["open", "right_ease_in", "bend_right", "right_ease_out", "settle", "left_ease_in", "bend_left", "left_ease_out"])
    for kind in ("dew_herb", "sun_plant", "moon_mushroom", "midnight_bloom"):
        frames = [plant(kind, i) for i in (0, 4, 1, 5, 3, 6, 2, 7)]
        animation(f"plants/{kind}", frames, TIMING["foliage"], ["open", "right_ease_in", "turn_right", "right_ease_out", "settle", "left_ease_in", "turn_left", "left_ease_out"])
        STATIC[f"plants/{kind}"] = save_frame(frames[0], f"plants/{kind}")
    # Reuse the still rock drawings. A glow is a deliberate color change.
    def rock_animation(name, frames, durations):
        animation(name, frames, TIMING["foliage"], ["dim", "rise_1", "rise_2", "peak", "fall_1", "fall_2", "fall_3", "low"])
    OLD.animation = rock_animation
    OLD.rocks()
    STATIC.update(OLD.STATIC)


def make_previews():
    folder = ROOT / "previews"
    folder.mkdir(parents=True, exist_ok=True)
    # Shared rendering helpers only: previous animation/warping code is unused.
    for state in ("walk", "idle", "rest"):
        frames = []
        count = 8 if state == "walk" else 4
        for pose in range(count):
            canvas = Image.new("RGB", (864, 506), "#191d2b")
            OLD.title(canvas, f"REDRAWN POSES / {state.upper()}",
                      f"{count} separate sprites / {1000 / TIMING[state]:g} fps / Male above, female below")
            for row, gender in enumerate(("male", "female")):
                for col, direction in enumerate(DIRECTIONS):
                    OLD.paste_sprite(canvas, character(gender, direction, state, pose), (35 + col * 207, 112 + row * 193))
            frames.append(canvas)
        OLD.gif(frames, folder / f"characters_{state}.gif", [TIMING[state]] * count)
    contact = Image.new("RGB", (1160, 860), "#191d2b")
    OLD.title(contact, "FORAGERS / NEW STYLES & WALK CYCLE", "Twin ribbon ponytails & pinafore / tousled quiff & field vest / native 32 x 32")
    d = ImageDraw.Draw(contact)
    for row, (gender, state) in enumerate((g, s) for g in ("male", "female") for s in ("walk", "idle", "rest")):
        y = 110 + row * 122
        d.text((25, y + 35), f"{gender.title()} / {state}", font=OLD.BASE.font(14), fill=P["cream"])
        for pose in range(8 if state == "walk" else 4):
            OLD.paste_sprite(contact, character(gender, "down", state, pose), (250 + pose * 110, y), 3)
            d.text((285 + pose * 110, y + 100), f"{pose + 1}", font=OLD.BASE.font(12), fill=P["mint"])
    contact.save(ROOT / "character_frames.png")
    designs = Image.new("RGB", (960, 570), "#191d2b")
    OLD.title(designs, "FORAGERS / CHARACTER DESIGNS", "Shared plum & teal palette / exposed hairstyles / down, left, right, up")
    for row, gender in enumerate(("male", "female")):
        for col, direction in enumerate(DIRECTIONS):
            OLD.paste_sprite(designs, character(gender, direction, "idle", 0), (42 + col * 230, 110 + row * 220), 6)
    designs.save(ROOT / "characters_preview.png")
    gait = Image.new("RGB", (1160, 1090), "#191d2b")
    OLD.title(gait, "WALK / CONTACT, DOWN, PASSING, UP", "Eight source drawings / far leg drawn first / opposed arm swing and secondary hair motion")
    d = ImageDraw.Draw(gait)
    for row, (gender, direction) in enumerate((g, dr) for g in ("male", "female") for dr in DIRECTIONS):
        y = 110 + row * 120
        d.text((22, y + 40), f"{gender.title()} / {direction}", font=OLD.BASE.font(14), fill=P["cream"])
        for pose in range(8):
            OLD.paste_sprite(gait, character(gender, direction, "walk", pose), (250 + pose * 110, y), 3)
    gait.save(folder / "walk_frames.png")
    names = [n for n in ANIMATIONS if not n.startswith("player/") and "rune" not in n]
    names += [n for n in STATIC if n.startswith("environment/rocks/")]
    frames = []
    for pose in range(8):
        canvas = Image.new("RGB", (1120, 790), "#191d2b")
        OLD.title(canvas, "WOODLAND / SOFTER MOTION", "Eight separate leaf, petal and branch drawings / 6.25 fps / fixed roots")
        d = ImageDraw.Draw(canvas)
        for index, name in enumerate(names):
            row, col = (0, index) if index < 4 else ((1, index - 4) if index < 8 else (2, index - 8))
            x, y = 32 + col * 180, 115 + row * 218
            d.rectangle((x, y, x + 127, y + 127), fill="#303549")
            if name in ANIMATIONS:
                image = frames_for(name)[pose]
            elif name.endswith("rune_rock"):
                image = frames_for("environment/rocks/rune_glow")[pose]
            else:
                image = Image.open(ROOT / STATIC[name]).convert("RGBA")
            OLD.paste_sprite(canvas, image, (x, y), 4)
            d.text((x, y + 143), name.split("/")[-1].replace("_", " ").title(), font=OLD.BASE.font(13), fill=P["cream"])
        frames.append(canvas)
    frames[0].save(ROOT / "environment_preview.png")
    OLD.gif(frames, folder / "environment_animated.gif", [TIMING["foliage"]] * 8)
    # Show the actual changing contours side by side, without motion or timing.
    board = Image.new("RGB", (1160, 1100), "#191d2b")
    OLD.title(board, "WOODLAND / POSE BREAKDOWN", "Each column is a fresh 32 x 32 drawing. Roots stay fixed.")
    d = ImageDraw.Draw(board)
    for row, name in enumerate(names[:8]):
        y = 112 + row * 120
        d.text((24, y + 30), name.split("/")[-1].replace("_", " ").title(), font=OLD.BASE.font(14), fill=P["cream"])
        for i, image in enumerate(frames_for(name)):
            OLD.paste_sprite(board, image, (250 + i * 110, y), 3)
    board.save(ROOT / "environment_frames.png")


def verify():
    expected = set(STATIC.values())
    for name, record in ANIMATIONS.items():
        frames = frames_for(name)
        count = 4 if "/idle/" in name or "/rest/" in name else 8
        assert len(frames) == len(record["pose_names"]) == count
        assert len(set(record["durations_ms"])) == 1 and record["durations_ms"][0] >= 100
        assert len({im.tobytes() for im in frames}) >= (4 if name.endswith("rune_glow") else count), f"Duplicate drawings: {name}"
        if not name.endswith("rune_glow"):
            # A translated source retains its normalized silhouette. Each pose
            # must instead have a different contour (not just different colors).
            masks = [im.getchannel("A") for im in frames]
            normalized = [(mask.getbbox()[2] - mask.getbbox()[0], mask.getbbox()[3] - mask.getbbox()[1],
                           mask.crop(mask.getbbox()).tobytes()) for mask in masks]
            # Resting fingers/blinks may change inside the same outer contour.
            assert len(set(normalized)) >= (2 if count == 4 else 6), f"Contour must be redrawn: {name}"
        if name.startswith(("plants/", "environment/trees/")):
            assert len({im.crop((0, 27, 32, 32)).tobytes() for im in frames}) == 1, name
        sheet = Image.open(ROOT / record["sheet"])
        assert sheet.size == (32 * count, 32) and sheet.mode == "RGBA"
        for i, (path, im) in enumerate(zip(record["frames"], frames)):
            expected.add(path)
            assert sheet.crop((i * 32, 0, i * 32 + 32, 32)).tobytes() == im.tobytes(), path
            assert im.crop((0, 30, 32, 32)).getbbox() is None, path
    actual = {p.relative_to(ROOT).as_posix() for p in (ROOT / "sprites").rglob("*.png")}
    assert actual == expected, actual ^ expected
    for path in expected:
        with Image.open(ROOT / path) as im:
            assert im.size == (32, 32) and im.mode == "RGBA", path
            assert set(im.getchannel("A").getdata()) == {0, 255}, path
            assert im.crop((0, 31, 32, 32)).getbbox() is None, path
    for gender in ("male", "female"):
        for state in ("walk", "idle", "rest"):
            sheet = Image.open(ROOT / "sheets" / "player" / gender / f"{state}_4dir.png")
            assert sheet.size == (256 if state == "walk" else 128, 128)
            for row, direction in enumerate(DIRECTIONS):
                for i, im in enumerate(frames_for(f"player/{gender}/{state}/{direction}")):
                    assert sheet.crop((i * 32, row * 32, i * 32 + 32, row * 32 + 32)).tobytes() == im.tobytes()
    for path in (ROOT / "previews").glob("*.gif"):
        with Image.open(path) as im:
            state = path.stem.removeprefix("characters_")
            assert im.n_frames == (4 if state in ("idle", "rest") else 8), path
            expected_ms = TIMING[state] if state in TIMING else TIMING["foliage"]
            for i in range(im.n_frames):
                im.seek(i)
                assert im.info["duration"] == expected_ms, (path, i, im.info["duration"])
    print(f"PASS: {len(ANIMATIONS)} loops, {len(expected)} native 32x32 sprites; redrawn poses, fixed roots, uniform timing, transparency, sheet cells and GIFs verified.")


def main():
    build()
    make_previews()
    manifest = {"version": 4, "technique": "explicit redrawn key poses; no pixel displacement or interpolation",
                "frame_size": [32, 32], "direction_row_order": list(DIRECTIONS),
                "animations": ANIMATIONS, "static_sprites": STATIC}
    (ROOT / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    verify()


if __name__ == "__main__":
    main()
