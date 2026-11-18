"""Independent checks for connectivity and variation, not just file sizes."""

import itertools
import json
from pathlib import Path

from PIL import Image


ROOT = Path(__file__).resolve().parent
OFFSETS = ((0, -1, 1), (1, -1, 2), (1, 0, 4), (1, 1, 8),
           (0, 1, 16), (-1, 1, 32), (-1, 0, 64), (-1, -1, 128))


def mask_for(cells, x, y):
    mask = sum(bit for dx, dy, bit in OFFSETS if (x + dx, y + dy) in cells)
    for bit, a, b in ((2, 1, 4), (8, 4, 16), (32, 16, 64), (128, 64, 1)):
        if not (mask & a and mask & b):
            mask &= ~bit
    return mask


def main():
    manifest = json.loads((ROOT / "manifest.json").read_text(encoding="utf-8"))
    atlas = Image.open(ROOT / "terrain_atlas.png").convert("RGBA")
    assert atlas.size == tuple(manifest["atlas_size"])
    assert len(manifest["materials"]) == 8 and len(manifest["blob_masks"]) == 47
    occupied = set()
    tiles = {}
    interiors = {}
    for record in manifest["tiles"]:
        coord = tuple(record["atlas_coords"])
        assert coord not in occupied
        occupied.add(coord)
        x, y = coord
        image = atlas.crop((x * 32, y * 32, x * 32 + 32, y * 32 + 32))
        assert image.getbbox() is not None
        assert set(image.getchannel("A").getdata()).issubset({0, 255})
        if record["kind"] == "terrain":
            tiles[record["material"], record["mask"], record["variant"]] = image
        elif record["kind"] == "interior":
            interiors[record["material"], record["variant"]] = image
    for material in manifest["materials"]:
        variants = [interiors[material, i] for i in range(12)]
        assert len({im.tobytes() for im in variants}) == 12, material
        for im in variants:
            assert im.getchannel("A").getextrema() == (255, 255)
            assert im.crop((0, 0, 1, 32)).tobytes() == im.crop((31, 0, 32, 32)).tobytes()
            assert im.crop((0, 0, 32, 1)).tobytes() == im.crop((0, 31, 32, 32)).tobytes()
        for mask in manifest["blob_masks"]:
            group = [tiles[material, mask, i] for i in range(3)]
            assert len({im.tobytes() for im in group}) == 3, (material, mask, "Duplicate texture alternatives")
            assert len({im.getchannel("A").tobytes() for im in group}) == 1
            for im in group[1:]:
                for edge in ((0, 0, 1, 32), (31, 0, 32, 32), (0, 0, 32, 1), (0, 31, 32, 32)):
                    assert im.crop(edge).tobytes() == group[0].crop(edge).tobytes(), (material, mask)
    # Exhaust every possible local arrangement around a connected pair.
    # There are ten unconstrained neighbor cells: 1,024 cases per axis.
    cases = 0
    for vertical in (False, True):
        center_a, center_b = (1, 1), ((1, 2) if vertical else (2, 1))
        width, height = (3, 4) if vertical else (4, 3)
        optional = [(x, y) for y in range(height) for x in range(width) if (x, y) not in (center_a, center_b)]
        for occupancy in itertools.product((False, True), repeat=len(optional)):
            cells = {center_a, center_b} | {pos for pos, present in zip(optional, occupancy) if present}
            a, b = mask_for(cells, *center_a), mask_for(cells, *center_b)
            for material in manifest["materials"]:
                first, second = tiles[material, a, 0], tiles[material, b, 2]
                edge_a = first.crop((0, 31, 32, 32) if vertical else (31, 0, 32, 32))
                edge_b = second.crop((0, 0, 32, 1) if vertical else (0, 0, 1, 32))
                assert edge_a.tobytes() == edge_b.tobytes(), (material, a, b, vertical)
            cases += 1
    grass_records = [r for r in manifest["tiles"] if r["kind"] == "interior" and r["material"] == "grass"]
    assert {r["grass_tufts"] for r in grass_records} == {0, 1, 2, 3}
    for background, foreground in manifest["mixed_pairs"]:
        sheet = Image.open(ROOT / "mixed" / f"{background}__{foreground}.png").convert("RGBA")
        assert sheet.size == (256, 256)
        for index, mask in enumerate(manifest["blob_masks"]):
            expected = interiors[background, 0].copy()
            expected.alpha_composite(tiles[foreground, mask, 0])
            x, y = index % 8 * 32, index // 8 * 32
            assert expected.tobytes() == sheet.crop((x, y, x + 32, y + 32)).tobytes()
    game = ROOT.parent.parent / "gardening-game-2d" / "assets" / "tilesets" / "woodland"
    assert (ROOT / "terrain_atlas.png").read_bytes() == (game / "terrain_atlas.png").read_bytes()
    assert (ROOT / "manifest.json").read_bytes() == (game / "terrain_manifest.json").read_bytes()
    print(f"PASS: {len(occupied)} atlas cells; 47 masks x 3 alternatives x 8 materials; 96 unique interiors; {cases} exhaustive connected-pair configurations ({cases * 8} exact RGBA seam checks); 12 mixed sheets.")


if __name__ == "__main__":
    main()
