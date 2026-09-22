#!/usr/bin/env python3
"""Pack an 8-phase run cycle (run_clean1-8) with ONE shared transform.
Replaces run_clean1-4 cells in place, appends run_clean5-8.
All 8 scale to the same content height (registered — no per-frame size
normalization noise); UP/airborne phases (4,8) get a 4px lift.
ponytail: head-bob comes from the engine's phase-locked bounce, not baked offsets.

Usage: pack_run8.py <name> <frames_dir>
"""
import sys, os, json, pathlib, subprocess, tempfile
from PIL import Image

name, fdir = sys.argv[1], sys.argv[2]
REPO = pathlib.Path(__file__).resolve().parent.parent.parent
adir = REPO / "web" / "assets" / "sprites"
man = json.loads((adir / f"{name}.json").read_text())
sheet = Image.open(adir / f"{name}.png").convert("RGBA")
cellW, cellH, pad = man["frameW"], man["frameH"], man["frameH"] - man["footY"]

def keyed_trimmed(src):
    with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as t: dst = t.name
    subprocess.run(["magick", src, "-alpha", "set", "-bordercolor", "white", "-border", "1",
                    "-fuzz", os.environ.get("FUZZ", "42") + "%", "-fill", "none", "-floodfill", "+0+0", "white",
                    "-shave", "1x1", "-trim", "+repage", dst], check=True)
    return Image.open(dst).convert("RGBA")

# size anchor: existing run_clean1 cell content height keeps game scale identical
rc1 = sheet.crop((man["frames"]["run_clean1"] * cellW, 0, (man["frames"]["run_clean1"] + 1) * cellW, cellH))
bb = rc1.getbbox(); target_h = bb[3] - bb[1]

frames = []
for i in range(1, 9):
    f = keyed_trimmed(f"{fdir}/run_clean{i}.png")
    s = target_h / f.height
    f = f.resize((max(1, round(f.width * s)), target_h), Image.LANCZOS)
    if f.width > cellW - 2:
        s2 = (cellW - 2) / f.width
        f = f.resize((cellW - 2, max(1, round(f.height * s2))), Image.LANCZOS)
    frames.append(f)

need_append = sum(1 for i in range(5, 9) if f"run_clean{i}" not in man["frames"])
out = Image.new("RGBA", (cellW * (man["cols"] + need_append), cellH), (0, 0, 0, 0))
out.paste(sheet, (0, 0))
col_next = man["cols"]
for i, f in enumerate(frames, 1):
    key = f"run_clean{i}"
    if key in man["frames"]:
        col = man["frames"][key]
    else:
        col = col_next; col_next += 1; man["frames"][key] = col
    # clear the cell, then paste bottom-centered; airborne UP phases lift 4px
    out.paste(Image.new("RGBA", (cellW, cellH), (0, 0, 0, 0)), (col * cellW, 0))
    lift = 4 if i in (4, 8) else 0
    out.paste(f, (col * cellW + (cellW - f.width) // 2, cellH - pad - f.height - lift), f)

man["cols"] = col_next
out.save(adir / f"{name}.png", optimize=True)
(adir / f"{name}.json").write_text(json.dumps(man))
print(f"packed {name} run_clean1-8, cols={man['cols']}, target_h={target_h}")
