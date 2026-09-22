#!/usr/bin/env python3
"""Append the approved Executioner hurt rescale without touching older cells."""
import json
import math
from pathlib import Path

import numpy as np
from PIL import Image


ROOT = Path(__file__).resolve().parents[2]
PNG = ROOT / "web/assets/sprites/executioner.png"
JSON = ROOT / "web/assets/sprites/executioner.json"
JOBS = (("hurt", 8, 1.06), ("hurt2", 38, 1.08), ("hurt3", 39, 1.08))


def main():
    man = json.loads(JSON.read_text())
    sheet = Image.open(PNG).convert("RGBA")
    width, height, cols = man["frameW"], man["frameH"], man["cols"]
    assert sheet.size == (width * cols, height)

    keys = [f"x{name}_scaled" for name, _, _ in JOBS]
    base = man["frames"].get(keys[0], cols)
    assert all(man["frames"].get(key, base + i) == base + i for i, key in enumerate(keys))
    new_cols = max(cols, base + len(JOBS))
    out = Image.new("RGBA", (width * new_cols, height), (0, 0, 0, 0))
    out.paste(sheet, (0, 0))

    for offset, (name, source_index, scale) in enumerate(JOBS):
        source = sheet.crop((source_index * width, 0, (source_index + 1) * width, height))
        box = source.getchannel("A").getbbox()
        assert box
        art = source.crop(box)
        art = art.resize(
            (round(art.width * scale), round(art.height * scale)),
            Image.Resampling.LANCZOS,
        )
        pixels = np.array(art)
        pixels[..., 3][pixels[..., 3] < 16] = 0
        art = Image.fromarray(pixels)

        x = math.floor(((box[0] + box[2]) - art.width) / 2)
        y = box[3] - art.height
        index = base + offset
        out.paste(Image.new("RGBA", (width, height)), (index * width, 0))
        out.alpha_composite(art, (index * width + x, y))

        man["frames"].setdefault(f"{name}_old_scale", source_index)
        man["frames"][keys[offset]] = index
        man["frames"][name] = index
        print(f"{name}: cell {source_index} x{scale:.2f} -> cell {index} at ({x},{y})")

    assert out.crop((0, 0, base * width, height)).tobytes() == sheet.crop(
        (0, 0, base * width, height)
    ).tobytes(), "a pre-existing cell changed"
    man["cols"] = new_cols
    out.save(PNG)
    JSON.write_text(json.dumps(man, indent=1) + "\n")
    print(f"cols {cols} -> {new_cols}; all {base} pre-existing cells are pixel-identical")


if __name__ == "__main__":
    main()
