#!/usr/bin/env python3
"""Phase-1 audit contact sheets: EVERY cell of every fighter, labeled with its
frame name(s), tiled into readable chunks for frame-by-frame visual review.
Read-only: writes PNGs to the output dir, never touches web/assets."""
import json
import sys
from pathlib import Path

from PIL import Image, ImageDraw

SP = Path(__file__).resolve().parent.parent / "web/assets/sprites"
ROSTER = ["executioner", "mizu", "shin", "tsubasa", "ember", "kael", "mokurai", "exile"]

TILE = 210          # tile box (cell fit inside, bottom-anchored like the engine's footY)
LABEL = 26
COLS_PER_ROW = 6
CELLS_PER_SHEET = 24


def fit(cell, w=TILE, h=TILE, foot_y=218, frame_h=226):
    """Bottom-anchor the foot line like the engine does, so vertical drift is visible."""
    copy = cell.copy()
    copy.thumbnail((w, h - 8), Image.Resampling.LANCZOS)
    canvas = Image.new("RGBA", (w, h), (30, 30, 36, 255))
    # anchor: footY of cell sits on the guide line near the tile bottom in every tile
    scale = copy.height / frame_h
    fy = int(foot_y * scale)
    canvas.alpha_composite(copy, ((w - copy.width) // 2, (h - 8) - fy))
    return canvas


def main(out_dir):
    out_dir.mkdir(parents=True, exist_ok=True)
    for name in ROSTER:
        d = json.load(open(SP / f"{name}.json"))
        sheet = Image.open(SP / f"{name}.png").convert("RGBA")
        fw, fh, cols = d["frameW"], d["frameH"], d["cols"]
        foot_y = d.get("footY", 218)
        names_by_col = {}
        for fname, idx in d["frames"].items():
            if 0 <= idx < cols:
                names_by_col.setdefault(idx, []).append(fname)
        cells = []
        for i in range(cols):
            cell = sheet.crop((i * fw, 0, (i + 1) * fw, fh))
            label = ",".join(names_by_col.get(i, [f"col_{i}"]))
            cells.append((i, label, fit(cell, foot_y=foot_y, frame_h=fh)))
        for chunk_start in range(0, len(cells), CELLS_PER_SHEET):
            chunk = cells[chunk_start:chunk_start + CELLS_PER_SHEET]
            rows = (len(chunk) + COLS_PER_ROW - 1) // COLS_PER_ROW
            img = Image.new("RGBA", (TILE * COLS_PER_ROW, (TILE + LABEL) * rows), (18, 18, 24, 255))
            draw = ImageDraw.Draw(img)
            for n, (idx, label, tile) in enumerate(chunk):
                x = (n % COLS_PER_ROW) * TILE
                y = (n // COLS_PER_ROW) * (TILE + LABEL)
                draw.text((x + 4, y + 6), f"[{idx}] {label[:38]}", fill=(255, 220, 100, 255))
                # foot line guide
                draw.line([(x, y + LABEL + TILE - 8), (x + TILE, y + LABEL + TILE - 8)], fill=(80, 80, 90, 255))
                img.alpha_composite(tile, (x, y + LABEL))
            part = chunk_start // CELLS_PER_SHEET + 1
            out = out_dir / f"{name}-cells-{chunk_start:03d}-{chunk_start + len(chunk) - 1:03d}.png"
            img.convert("RGB").save(out)
            print(f"{name} part {part}: cells {chunk_start}-{chunk_start + len(chunk) - 1} -> {out.name}")


if __name__ == "__main__":
    main(Path(sys.argv[1] if len(sys.argv) == 2 else "media/audit-phase1"))
