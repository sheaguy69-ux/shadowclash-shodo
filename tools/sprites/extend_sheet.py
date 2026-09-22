#!/usr/bin/env python3
"""Append add-on pose cells to an EXISTING sprite sheet without touching the
original cells. The original sheet pixels are copied byte-identical; new
frames are keyed, trimmed, scaled to match the sheet's character size, and
bottom-aligned into new cells on the right. JSON manifest gains the new
frame indices (cols grows).

Scaling: the new raw frames come from the same Kontext base at the same
canvas scale, so we scale them by (idle-cell content height / base-image
content height) — the same effective factor the original pack applied.

Usage: python3 extend_sheet.py <name> <newframes_dir> <base_png> <sheets_dir> pose1 pose2 ...
"""
import sys, json, pathlib, subprocess, tempfile
from PIL import Image

name, fdir, base_png, adir = sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4]
poses = sys.argv[5:]

sheet_path = pathlib.Path(adir) / f"{name}.png"
json_path = pathlib.Path(adir) / f"{name}.json"
man = json.loads(json_path.read_text())
sheet = Image.open(sheet_path).convert("RGBA")
cellW, cellH, cols, pad = man["frameW"], man["frameH"], man["cols"], man["frameH"] - man["footY"]

def keyed_trimmed(src):
    """white -> transparent + trim, same recipe as pack_sheet.py.
    FUZZ env raises the key tolerance (42 kills the i2v soft drop-shadow)."""
    import os as _os
    fuzz = _os.environ.get("FUZZ", "25")
    with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as t:
        dst = t.name
    subprocess.run(["magick", src, "-alpha", "set",
                    "-bordercolor", "white", "-border", "1",
                    "-fuzz", f"{fuzz}%", "-fill", "none", "-floodfill", "+0+0", "white",
                    "-shave", "1x1", "-trim", "+repage", dst], check=True)
    return Image.open(dst).convert("RGBA")

# effective scale: idle cell content height vs raw base content height
idle_cell = sheet.crop((man["frames"]["idle"] * cellW, 0, (man["frames"]["idle"] + 1) * cellW, cellH))
idle_h = idle_cell.getbbox()[3] - idle_cell.getbbox()[1]
base_h = keyed_trimmed(base_png).height
k = idle_h / base_h

# Optional: MATCH_HEIGHT=<cellname> uniform-scales every new cell so its content
# height equals that reference cell's — kills the ~8-10% "boil" you get when
# independent generations don't size-match (critical for run cycles).
import os
match_cell = os.environ.get("MATCH_HEIGHT")
target_h = None
# MATCH_HEIGHT_PX: numeric target height — same per-cell matching, but the
# caller picks the number (e.g. shrunk a few % so wide lunge frames clear the
# cell-box clamp instead of getting shortened by it).
if os.environ.get("MATCH_HEIGHT_PX"):
    target_h = int(os.environ["MATCH_HEIGHT_PX"])
elif match_cell and match_cell in man["frames"]:
    _ref = sheet.crop((man["frames"][match_cell] * cellW, 0, (man["frames"][match_cell] + 1) * cellW, cellH))
    _bb = _ref.getbbox()
    if _bb:
        target_h = _bb[3] - _bb[1]

# Optional: FIXED_SCALE=<float> applies ONE scale to every new cell — for
# frame sets from a single i2v clip where pose heights legitimately differ
# (attack windup vs full extension). Per-cell MATCH_HEIGHT would flatten
# those differences; the clip's own registration is the size guarantee.
fixed_scale = float(os.environ["FIXED_SCALE"]) if os.environ.get("FIXED_SCALE") else None

new_frames = []
for pose in poses:
    f = keyed_trimmed(f"{fdir}/{pose}.png")
    scale = fixed_scale if fixed_scale else (target_h / f.height) if target_h else k
    f = f.resize((max(1, round(f.width * scale)), max(1, round(f.height * scale))), Image.LANCZOS)
    # a cell is a hard box: clamp anything that scaled past it (wide sprint poses)
    if f.width > cellW - 2 or f.height > cellH - pad - 2:
        s = min((cellW - 2) / f.width, (cellH - pad - 2) / f.height)
        f = f.resize((max(1, round(f.width * s)), max(1, round(f.height * s))), Image.LANCZOS)
    new_frames.append((pose, f))

out = Image.new("RGBA", (cellW * (cols + len(poses)), cellH), (0, 0, 0, 0))
out.paste(sheet, (0, 0))
for i, (pose, f) in enumerate(new_frames):
    x = (cols + i) * cellW + (cellW - f.width) // 2
    y = cellH - pad - f.height
    out.paste(f, (x, y), f)
    man["frames"][pose] = cols + i

man["cols"] = cols + len(poses)
out.save(sheet_path, optimize=True)
json_path.write_text(json.dumps(man))
print(f"extended {name}: +{len(poses)} cells -> {man['cols']} cols  (scale k={k:.3f})")
