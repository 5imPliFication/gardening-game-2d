"""Export approved art into res:// and author playable-scene environment data."""

import importlib.util
import json
import random
import shutil
import sys
from pathlib import Path

from PIL import Image, ImageDraw


ROOT = Path(__file__).resolve().parent
sys.dont_write_bytecode = True
GAME = ROOT.parent / "gardening-game-2d"
ASSETS = GAME / "assets"
SPEC = importlib.util.spec_from_file_location("terrain_art", ROOT / "woodland-tileset/generate_tileset.py")
TERRAIN = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(TERRAIN)
MANIFEST = json.loads((ROOT / "woodland-tileset/manifest.json").read_text())
INTERIORS = {(r["material"], r["variant"]): r["atlas_coords"] for r in MANIFEST["tiles"] if r["kind"] == "interior"}
EDGES = {(r["material"], r["mask"], r["variant"]): r["atlas_coords"] for r in MANIFEST["tiles"] if r["kind"] == "terrain"}
PROP_COORDS = {r["name"]: r["atlas_coords"] for r in MANIFEST["tiles"] if r["kind"] == "decoration"}
DIRECTIONS = ("down", "left_down", "left_up", "up", "right_up", "right_down")


def copy(source, target):
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(source, target)


def export_animations():
    visuals = {"default_appearance": "female", "characters": {}, "animations": {},
               "world_bounds": {"forest": [1280, 736], "home": [960, 640], "clinic": [960, 640], "cave": [4512, 736],
                                "town_square": [960, 640], "bubble_street": [1280, 736]},
               "environments": {name: f"res://assets/world/{name}_environment.tscn" for name in
                                ("forest", "home", "clinic", "town_square", "bubble_street", "cave_moss", "cave_slate", "cave_amber", "cave_moon")}}
    for gender in ("female", "male"):
        visuals["characters"][gender] = {}
        for variant in ("recolored", "lantern"):
            output = ASSETS / "characters" / gender / variant
            animations = []
            for state, fps in (("idle", 6.25), ("walk", 10.0)):
                for direction in DIRECTIONS:
                    name = f"{state}_{direction}"
                    target = output / f"{name}.png"
                    copy(ROOT / "adventurers-spooky-cute/32x32" / gender / variant / f"{name}.png", target)
                    animations.append({"name": name, "texture": "res://" + target.relative_to(GAME).as_posix(),
                                       "frames": 8, "fps": fps, "size": [32, 32]})
            resource = f"res://assets/characters/{gender}/{variant}.tres"
            visuals["characters"][gender][variant] = resource
            visuals["animations"][resource] = animations
    visuals["plants"] = {}
    for plant in ("dew_herb", "sun_plant", "moon_mushroom", "midnight_bloom"):
        target = ASSETS / "environment/plants" / f"{plant}.png"
        copy(ROOT / "spooky-cute-keyframes/sheets/plants" / f"{plant}.png", target)
        resource = f"res://assets/environment/plants/{plant}.tres"
        visuals["plants"][plant] = resource
        visuals["animations"][resource] = [{"name": "idle", "texture": "res://" + target.relative_to(GAME).as_posix(),
                                              "frames": 8, "fps": 6.25, "size": [32, 32]}]
    visuals["trees"] = {}
    for tree in ("witchwood", "moon_pine", "lavender_willow", "silver_birch"):
        target = ASSETS / "environment/trees" / f"{tree}.png"
        copy(ROOT / "spooky-cute-keyframes/sheets/environment/trees" / f"{tree}.png", target)
        resource = f"res://assets/environment/trees/{tree}.tres"
        visuals["trees"][tree] = resource
        visuals["animations"][resource] = [{"name": "idle", "texture": "res://" + target.relative_to(GAME).as_posix(),
                                              "frames": 8, "fps": 6.25, "size": [32, 32]}]
    for resource, animations in visuals["animations"].items():
        write_frames(GAME / resource.removeprefix("res://"), animations)
    (GAME / "data/visuals.json").write_text(json.dumps(visuals, indent=2) + "\n")
    for name in ("dew_herb", "sun_plant", "moon_mushroom", "midnight_bloom"):
        copy(ROOT / "spooky-cute-keyframes/sprites/plants" / f"{name}.png", ASSETS / "items" / f"{name}.png")
    for name in ("bottle", "water", "sugar", "dew_potion", "sun_potion", "moon_potion"):
        copy(ROOT / "spooky-cute-starter/sprites/items" / f"{name}.png", ASSETS / "items" / f"{name}.png")


def write_frames(path, animations):
    count = sum(a["frames"] for a in animations)
    lines = [f'[gd_resource type="SpriteFrames" load_steps={count + len(animations) + 1} format=3]', ""]
    for i, animation in enumerate(animations):
        lines.append(f'[ext_resource type="Texture2D" path="{animation["texture"]}" id="tex_{i}"]')
    for i, animation in enumerate(animations):
        for frame in range(animation["frames"]):
            width, height = animation["size"]
            lines += ["", f'[sub_resource type="AtlasTexture" id="frame_{i}_{frame}"]',
                      f'atlas = ExtResource("tex_{i}")', f'region = Rect2({frame * width}, 0, {width}, {height})']
    lines += ["", "[resource]", "animations = ["]
    for i, animation in enumerate(animations):
        frames = ', '.join(f'{{"duration": 1.0, "texture": SubResource("frame_{i}_{j}")}}' for j in range(animation["frames"]))
        lines.append(f'{{"frames": [{frames}], "loop": true, "name": &"{animation["name"]}", "speed": {animation["fps"]}}}' + ("," if i < len(animations) - 1 else ""))
    lines += ["]", ""]
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines))


def station_props():
    colors = {"ink": "#28253d", "wood": "#735063", "bark": "#a87378", "tan": "#d6a17e",
              "plum": "#66517c", "lilac": "#a183bb", "cream": "#fff0cf", "teal": "#397b78",
              "mint": "#70b698", "gold": "#e8ad62", "dark": "#39334f", "stone": "#777987"}
    for name in ("cauldron", "sell_bin", "counter", "bed", "upgrade", "menu", "door", "house", "cave_entrance", "ladder", "hole", "pending_structure", "route_sign"):
        im = Image.new("RGBA", (32, 32))
        d = ImageDraw.Draw(im)
        def rect(box, c):
            d.rectangle(box, fill=colors[c])
        def poly(points, c, outline="ink"):
            d.polygon(points, fill=colors[c], outline=colors[outline])
        if name == "cauldron":
            rect((7, 26, 10, 29), "ink"); rect((22, 26, 25, 29), "ink")
            d.ellipse((5, 10, 27, 28), fill=colors["dark"], outline=colors["ink"])
            d.ellipse((3, 9, 29, 17), fill=colors["plum"], outline=colors["ink"])
            d.ellipse((6, 11, 26, 15), fill=colors["teal"])
            d.line((9, 12, 21, 12), fill=colors["mint"])
            d.ellipse((10, 4, 13, 7), fill=colors["mint"])
            d.ellipse((20, 1, 22, 3), fill=colors["lilac"])
            d.line((23, 5, 19, 14), fill=colors["tan"], width=2)
            d.line((9, 19, 9, 24), fill=colors["plum"], width=2)
        elif name in ("sell_bin", "counter", "upgrade", "menu"):
            poly([(2, 14), (5, 9), (27, 9), (30, 14), (28, 28), (4, 28)], "wood")
            rect((4, 14, 27, 26), "bark"); rect((3, 13, 29, 15), "tan")
            for x in (8, 16, 24):
                d.line((x, 16, x, 26), fill=colors["wood"])
            rect((5, 25, 27, 27), "wood")
            if name == "sell_bin":
                poly([(4, 8), (6, 3), (26, 3), (28, 8)], "tan")
                rect((6, 10, 25, 12), "dark")
                poly([(12, 21), (15, 17), (20, 17), (18, 21)], "mint", "teal")
            elif name == "menu":
                poly([(7, 5), (15, 6), (16, 8), (18, 6), (25, 5), (26, 12), (17, 14), (7, 12)], "cream", "plum")
                d.line((16, 8, 16, 12), fill=colors["plum"])
            elif name == "counter":
                for x, color in ((9, "mint"), (21, "lilac")):
                    rect((x, 3, x + 3, 5), "tan")
                    d.ellipse((x - 2, 6, x + 5, 12), fill=colors[color], outline=colors["ink"])
                    rect((x, 7, x, 9), "cream")
            else:
                rect((8, 4, 14, 11), "gold"); rect((9, 5, 13, 9), "cream")
                d.arc((9, 0, 13, 5), 180, 360, fill=colors["tan"])
                d.line((20, 5, 24, 12), fill=colors["stone"], width=3)
                d.line((18, 5, 23, 3), fill=colors["tan"], width=2)
        elif name == "bed":
            rect((6, 5, 26, 29), "ink"); rect((7, 7, 25, 27), "wood")
            rect((8, 8, 24, 25), "lilac"); rect((9, 8, 23, 13), "cream")
            rect((8, 15, 24, 25), "plum"); rect((10, 16, 22, 17), "lilac")
            poly([(16, 18), (19, 22), (16, 24), (13, 22)], "gold", "lilac")
            rect((5, 4, 27, 7), "tan"); rect((5, 27, 27, 29), "bark")
        elif name in ("door", "house"):
            if name == "house":
                poly([(4, 13), (27, 13), (27, 29), (4, 29)], "tan")
                poly([(1, 14), (15, 1), (18, 1), (30, 14)], "plum")
                d.line([(5, 12), (16, 3), (27, 12)], fill=colors["lilac"])
                rect((23, 2, 26, 9), "wood")
                rect((6, 17, 10, 21), "teal"); rect((7, 18, 9, 20), "gold")
                rect((22, 17, 25, 21), "teal")
            else:
                poly([(7, 29), (7, 10), (12, 5), (20, 5), (25, 10), (25, 29)], "bark")
            poly([(12, 29), (12, 19 if name == "house" else 12), (15, 16 if name == "house" else 9),
                  (19, 18 if name == "house" else 11), (20, 29)], "wood")
            rect((14, 21, 18, 28), "dark"); rect((18, 25, 18, 25), "gold")
            rect((10, 29, 22, 30), "stone")
        elif name == "cave_entrance":
            poly([(1, 27), (3, 15), (8, 7), (15, 3), (24, 8), (29, 19), (31, 29)], "stone")
            poly([(8, 29), (8, 20), (12, 14), (20, 14), (25, 21), (25, 29)], "dark")
            poly([(11, 29), (11, 21), (15, 17), (19, 19), (22, 29)], "ink")
            d.line([(5, 18), (9, 10), (15, 6)], fill=colors["lilac"])
            rect((25, 25, 29, 27), "teal")
        elif name == "ladder":
            d.ellipse((5, 14, 27, 29), fill=colors["ink"])
            d.line((10, 4, 10, 27), fill=colors["tan"], width=3)
            d.line((22, 4, 22, 27), fill=colors["tan"], width=3)
            for y in (7, 13, 19, 25):
                d.line((11, y, 21, y), fill=colors["bark"], width=2)
        elif name == "hole":
            d.ellipse((3, 13, 29, 29), fill=colors["stone"], outline=colors["dark"])
            d.ellipse((6, 16, 26, 27), fill=colors["ink"])
            d.line((8, 15, 23, 15), fill=colors["wood"])
        elif name == "pending_structure":
            for x in range(4, 28, 6):
                rect((x, 4, x + 2, 4), "lilac"); rect((x, 27, x + 2, 27), "lilac")
            for y in range(4, 28, 6):
                rect((4, y, 4, y + 2), "lilac"); rect((27, y, 27, y + 2), "lilac")
            for x, y in ((3, 3), (26, 3), (3, 26), (26, 26)):
                rect((x, y, x + 2, y + 3), "wood"); rect((x, y, x + 2, y), "gold")
            d.line([(13, 12), (13, 11), (18, 11), (19, 12), (19, 14), (16, 16), (16, 18)], fill=colors["cream"], width=2)
            rect((16, 21, 17, 22), "cream")
        else:
            rect((14, 12, 17, 29), "wood")
            poly([(5, 5), (23, 5), (28, 10), (23, 15), (5, 15)], "bark")
            d.line([(10, 10), (22, 10), (19, 7)], fill=colors["cream"])
            d.line([(22, 10), (19, 13)], fill=colors["cream"])
        target = ASSETS / "props" / f"{name}.png"
        target.parent.mkdir(parents=True, exist_ok=True)
        im.save(target)


def layer(material, cells, rng, tint=None, full=False):
    output = {"material": material, "cells": []}
    if tint:
        output["tint"] = tint
    for x, y in sorted(cells):
        mask = 255 if full else TERRAIN.cell_mask(cells, x, y)
        if mask == 255:
            coord = INTERIORS[material, rng.randrange(12)]
        else:
            coord = EDGES[material, mask, rng.randrange(3)]
        output["cells"].append({"cell": [x, y], "atlas_coords": coord})
    return output


def world_layouts():
    rng = random.Random(20261031)
    worlds = {}
    for name, width, height, base in (("forest", 40, 23, "grass"), ("home", 30, 20, "concrete"),
                                      ("clinic", 30, 20, "concrete"), ("town_square", 30, 20, "grass"),
                                      ("bubble_street", 40, 23, "grass"), ("cave_moss", 141, 23, "grass"),
                                      ("cave_slate", 141, 23, "stone"), ("cave_amber", 141, 23, "sand"),
                                      ("cave_moon", 141, 23, "concrete")):
        cells = TERRAIN.rectangle(0, 0, width - 1, height - 1)
        theme_tint = {"cave_moss": "#8aa98c", "cave_slate": "#869daf", "cave_amber": "#c49d82", "cave_moon": "#9783b2"}.get(name)
        layers = [layer(base, cells, rng, theme_tint, full=True)]
        world = {"size": [width * 32, height * 32], "layers": layers, "props": [], "trees": [], "water": []}
        if name == "forest":
            route = TERRAIN.trail([(3, 15), (10, 5), (16, 5), (23, 5), (29, 8), (33, 13), (36, 17)], 1.15, width, height)
            route |= TERRAIN.trail([(10, 5), (10, 19), (29, 19)], 0.9, width, height)
            layers.append(layer("dirt", route, rng))
            sand = TERRAIN.ellipse(33, 13, 4.6, 3, width, height)
            water = TERRAIN.ellipse(33, 13, 3.5, 2, width, height)
            bridge = TERRAIN.rectangle(33, 10, 33, 16)
            layers += [layer("sand", sand, rng), layer("water", water, rng), layer("wood", bridge, rng)]
            layers.append(layer("stone", TERRAIN.rectangle(15, 5, 17, 7), rng))
            world["water"] = [list(cell) for cell in sorted(water - bridge)]
            protected = [(320, 180), (520, 180), (760, 180), (520, 240), (760, 240), (400, 180), (240, 180), (320, 100), (320, 260)]
            protected += [(80, 80), (180, 60), (460, 80), (580, 60), (760, 100), (900, 80), (1080, 120),
                          (80, 200), (180, 320), (460, 320), (580, 200), (860, 300), (1040, 320), (100, 420),
                          (260, 480), (400, 460), (560, 420), (760, 520), (980, 560), (1160, 480),
                          (160, 620), (360, 640), (520, 620), (1000, 660)]
            for y in range(64, height * 32 - 32, 64):
                for x in range(64, width * 32 - 32, 64):
                    if rng.random() > 0.28 or any((x - px) ** 2 + (y - py) ** 2 < 64 ** 2 for px, py in protected):
                        continue
                    if (x // 32, y // 32) in route | sand:
                        continue
                    world["trees"].append({"position": [x, y], "variant": rng.choice(("witchwood", "moon_pine", "lavender_willow", "silver_birch"))})
                    protected.append((x, y))
            for x, y in ((660, 430), (1080, 600), (650, 100), (1120, 260)):
                world["props"].append({"atlas_coords": PROP_COORDS["mossy_boulder"], "position": [x, y]})
        elif name in ("home", "clinic"):
            if name == "home":
                layers.append(layer("wood", TERRAIN.rectangle(1, 2, 28, 18), rng))
                layers.append(layer("stone", TERRAIN.rectangle(8, 7, 11, 10), rng))
            else:
                layers.append(layer("stone", TERRAIN.rectangle(1, 2, 28, 18), rng))
                layers.append(layer("wood", TERRAIN.rectangle(12, 10, 17, 15), rng))
                for x in (288, 672):
                    world["props"].append({"texture": "res://assets/props/bed.png", "position": [x, 320], "scale": 2})
        elif name in ("town_square", "bubble_street"):
            if name == "town_square":
                layers.append(layer("gravel", TERRAIN.rectangle(6, 7, 23, 17), rng))
                layers.append(layer("stone", TERRAIN.rectangle(8, 8, 21, 16), rng))
                road = TERRAIN.trail([(15, 13), (28, 13)], 1.5, width, height)
                plots = [(8, 7), (22, 7), (15, 10)]
            else:
                road = TERRAIN.trail([(2, 13), (37, 13)], 1.5, width, height)
                plots = [(8, 8), (16, 8), (25, 8)]
            layers.append(layer("dirt", road, rng))
            for x, y in plots:
                layers.append(layer("concrete", TERRAIN.rectangle(x - 2, y - 1, x + 1, y + 1), rng))
            for x, y in ((96, 96), (width * 32 - 96, 96), (96, height * 32 - 64), (width * 32 - 96, height * 32 - 64)):
                world["trees"].append({"position": [x, y], "variant": "silver_birch" if name == "town_square" else "witchwood"})
        else:
            if name == "cave_moss":
                path = TERRAIN.rectangle(6, 5, 134, 17)
                layers.append(layer("dirt", path, rng, "#8d9b88"))
            elif name == "cave_slate":
                path = TERRAIN.trail([(8, 11), (32, 7), (60, 14), (88, 7), (130, 11)], 5, width, height)
                layers.append(layer("gravel", path, rng, "#99acc2"))
            elif name == "cave_amber":
                path = TERRAIN.trail([(8, 11), (30, 14), (64, 7), (96, 14), (130, 11)], 5, width, height)
                layers.append(layer("dirt", path, rng, "#d0ad88"))
            else:
                path = TERRAIN.rectangle(6, 5, 134, 17)
                layers.append(layer("stone", path, rng, "#a897c5"))
                pools = TERRAIN.rectangle(20, 2, 45, 3) | TERRAIN.rectangle(75, 19, 108, 20)
                layers.append(layer("water", pools, rng, "#a292c4"))
                world["water"] = [list(cell) for cell in sorted(pools)]
            for x in range(512, 4400, 384):
                for y in (96, 672):
                    rock = {"cave_moss": "mossy_boulder", "cave_slate": "boulder", "cave_amber": "rune_rock", "cave_moon": "rune_rock"}[name]
                    world["props"].append({"atlas_coords": PROP_COORDS[rock], "position": [x, y], "tint": theme_tint})
        worlds[name] = world
    (GAME / "data/world_art.json").write_text(json.dumps(worlds, indent=2) + "\n")
    export_maps(worlds)
    backdrop = Image.open(ROOT / "woodland-tileset/previews/woodland_map.png").convert("RGBA")
    target = ASSETS / "menu/background.png"
    target.parent.mkdir(parents=True, exist_ok=True)
    backdrop.crop((720, 72, 1360, 432)).save(target)


def export_maps(worlds):
    locations = {}
    for name, world in worlds.items():
        overview = Image.new("RGB", (world["size"][0] // 32, world["size"][1] // 32))
        for definition in world["layers"]:
            color = tuple(bytes.fromhex(TERRAIN.MATERIALS[definition["material"]][0][1:]))
            if definition.get("tint"):
                tint = bytes.fromhex(definition["tint"][1:])
                color = tuple(round(c * (0.5 + t / 510)) for c, t in zip(color, tint))
            for record in definition["cells"]:
                overview.putpixel(tuple(record["cell"]), color)
        target = ASSETS / "maps" / f"{name}.png"
        target.parent.mkdir(parents=True, exist_ok=True)
        overview.save(target)
        locations[name] = {"name": name.replace("_", " ").title(), "size": world["size"],
                           "overview": "res://" + target.relative_to(GAME).as_posix(),
                           "environment": f"res://assets/world/{name}_environment.tscn", "markers": [], "spawns": {}, "structures": [], "exits": []}
    locations["forest"].update({"scene": "res://scenes/forest.tscn", "name": "Forest", "world_position": [0.60, 0.25],
                                "description": "Forage among trees and follow the trail to the caves.",
                                "spawns": {"street_gate": [520, 240], "cave_gate": [760, 240]},
                                "markers": [{"position": [520, 180], "kind": "exit"}, {"position": [760, 180], "kind": "cave"}]})
    locations["town_square"].update({"scene": "res://scenes/town_square.tscn", "name": "Town Square", "world_position": [0.10, 0.25],
                                     "description": "The town's starting plaza. Clinic and civic buildings are pending structures.", "spawns": {"street_gate": [832, 432], "clinic_door": [256, 284]}})
    locations["bubble_street"].update({"scene": "res://scenes/bubble_street.tscn", "name": "Bubble Street", "world_position": [0.35, 0.25],
                                      "description": "The player's shop is here. Marked plots stand in for future buildings.",
                                      "spawns": {"town_gate": [128, 432], "forest_gate": [1120, 432], "shop_door": [520, 316]}})
    locations["town_square"]["structures"] = [
        {"name": "Clinic", "position": [256, 224], "target_scene": "res://scenes/clinic.tscn"},
        {"name": "Town Hall", "position": [704, 224]}, {"name": "Fountain", "position": [480, 320]}]
    locations["bubble_street"]["structures"] = [
        {"name": "Player Shop", "position": [520, 256], "target_scene": "res://scenes/home.tscn"},
        {"name": "Apothecary", "position": [800, 256]}, {"name": "Cottage", "position": [256, 256]}]
    locations["town_square"]["exits"] = [{"name": "Bubble Street", "position": [896, 432], "target_scene": "res://scenes/bubble_street.tscn", "target_spawn": "town_gate"}]
    locations["bubble_street"]["exits"] = [
        {"name": "Town Square", "position": [64, 432], "target_scene": "res://scenes/town_square.tscn", "target_spawn": "street_gate"},
        {"name": "Forest", "position": [1184, 432], "target_scene": "res://scenes/forest.tscn", "target_spawn": "street_gate"}]
    for name in ("town_square", "bubble_street"):
        for structure in locations[name]["structures"]:
            locations[name]["markers"].append({"position": structure["position"], "kind": "pending", "name": structure["name"], "size": [112, 80]})
        for exit_record in locations[name]["exits"]:
            locations[name]["markers"].append({"position": exit_record["position"], "kind": "exit"})
    locations["home"].update({"name": "Player Shop", "world_parent": "bubble_street", "scene": "res://scenes/home.tscn", "description": "Temporary shop interior: craft, sell, sleep, save and change appearance."})
    locations["clinic"].update({"name": "Clinic", "world_parent": "town_square", "scene": "res://scenes/clinic.tscn", "description": "Temporary recovery interior on Town Square."})
    for resumable in ("town_square", "bubble_street", "forest", "home", "clinic"):
        locations[resumable]["resume_allowed"] = True
        locations[resumable]["default_spawn"] = [480, 432] if resumable in ("town_square", "bubble_street") else ([320, 180] if resumable == "forest" else [480, 400])
    themes = ("cave_moss", "cave_slate", "cave_amber", "cave_moon")
    titles = ("Moss Hollow", "Slate Gallery", "Amber Grotto", "Moon Chamber")
    candidates = (((3900, 220), (4000, 360), (4100, 500)), ((3920, 500), (4020, 240), (4120, 380)),
                  ((3940, 260), (4040, 480), (4140, 340)), ((3960, 440), (4060, 220), (4160, 500)))
    for depth, (theme, title) in enumerate(zip(themes, titles), 1):
        definition = locations.pop(theme)
        definition.update({"name": title, "scene": "res://scenes/cave_depth.tscn", "required_lantern": depth,
                           "world_position": [0.86, 0.12 + (depth - 1) * 0.23], "cave_id": "cave_a", "depth": depth,
                           "description": f"Cave A, depth {depth}. {title}: a distinct {theme.removeprefix('cave_')} environment. Requires lantern level {depth}.",
                           "hole_positions": {f"hole_{depth}_{letter}": list(pos) for letter, pos in zip("abc", candidates[depth - 1])},
                           "markers": [{"position": [300, 360], "kind": "exit" if depth == 1 else "ladder"}]})
        locations[f"cave_a_{depth}"] = definition
    connections = [["town_square", "bubble_street"], ["bubble_street", "forest"], ["forest", "cave_a_1"],
                   ["cave_a_1", "cave_a_2"], ["cave_a_2", "cave_a_3"], ["cave_a_3", "cave_a_4"]]
    (GAME / "data/maps.json").write_text(json.dumps({"locations": locations, "connections": connections}, indent=2) + "\n")


if __name__ == "__main__":
    export_animations()
    station_props()
    world_layouts()
    print("Exported gameplay sprites, nine distinct terrain layouts, map overviews, and menu background.")
