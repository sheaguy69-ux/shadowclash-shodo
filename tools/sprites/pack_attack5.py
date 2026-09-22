#!/usr/bin/env python3
"""Key + pack FIVE i2v heavy-attack frames as heavy_i1..heavy_i5.

Unlike the run cycle, attack pose heights legitimately differ (coiled windup
vs full extension), so per-cell MATCH_HEIGHT would flatten the animation.
Instead ONE scale is applied to all five (FIXED_SCALE): the clip's own
frame-to-frame registration is the size guarantee, and the absolute scale is
anchored by mapping the clip's first frame back through the Kontext seed:
  target_h(seed at sheet scale) = trimmed(seed).h * (idle_cell.h / trimmed(base).h)
  FIXED_SCALE = target_h / trimmed(f_001).h
If any scaled frame would overflow its cell box, the whole set shrinks
uniformly (registration is preserved; the % is printed — watch it).

Usage: python3 pack_attack5.py <name> <atk_dir> <f1..f5> [--flop]
  <atk_dir> holds seed.png and frames/f_NNN.png; --flop mirrors right-facing picks.
"""
import sys, subprocess, tempfile, pathlib, os, json
from PIL import Image

name, adir = sys.argv[1], sys.argv[2]
picks = sys.argv[3:8]
flop = "--flop" in sys.argv
assert len(picks) == 5, "need exactly 5 frame numbers"
HERE = pathlib.Path(__file__).resolve().parent
REPO = HERE.parent.parent
SHEETS = REPO / "web" / "assets" / "sprites"
tmp = pathlib.Path(tempfile.mkdtemp())

def key(src, dst, extra=()):
    subprocess.run(["magick", src, *extra, "-alpha", "set", "-bordercolor", "white", "-border", "1",
                    "-fuzz", "42%", "-fill", "none", "-floodfill", "+0+0", "white",
                    "-shave", "1x1", "-trim", "+repage", str(dst)], check=True)

# --- anchor scale: seed -> sheet space, then clip-f001 -> seed ---------------
man = json.loads((SHEETS / f"{name}.json").read_text())
sheet = Image.open(SHEETS / f"{name}.png").convert("RGBA")
cw, ch, pad = man["frameW"], man["frameH"], man["frameH"] - man["footY"]
idle = sheet.crop((man["frames"]["idle"] * cw, 0, (man["frames"]["idle"] + 1) * cw, ch))
idle_h = idle.getbbox()[3] - idle.getbbox()[1]

key(str(HERE / "base" / f"{name}.png"), tmp / "_base.png")
key(f"{adir}/seed.png", tmp / "_seed.png")
key(f"{adir}/frames/f_001.png", tmp / "_f1.png")
base_h = Image.open(tmp / "_base.png").height
seed_h = Image.open(tmp / "_seed.png").height
f1_h = Image.open(tmp / "_f1.png").height
scale = (seed_h * (idle_h / base_h)) / f1_h

# --- key the 5 picks (mirror right-facing sets to the authored LEFT) ---------
extra = ("-flop",) if flop else ()
sizes = []
for i, fr in enumerate(picks, 1):
    dst = tmp / f"heavy_i{i}.png"
    key(f"{adir}/frames/f_{int(fr):03d}.png", dst, extra)
    sizes.append(Image.open(dst).size)

# --- uniform shrink if the tallest/widest scaled frame would overflow --------
fit = min([(cw - 2) / (w * scale) for w, h in sizes] + [(ch - pad - 2) / (h * scale) for w, h in sizes] + [1.0])
if fit < 1.0:
    print(f"[{name}] uniform shrink to fit cell box: {fit*100:.1f}% of anchor scale")
scale *= fit

env = dict(os.environ, FIXED_SCALE=str(scale))
subprocess.run([sys.executable, str(HERE / "extend_sheet.py"), name, str(tmp),
                str(HERE / "base" / f"{name}.png"), str(SHEETS),
                "heavy_i1", "heavy_i2", "heavy_i3", "heavy_i4", "heavy_i5"], check=True, env=env)
print(f"packed {name} heavy_i from frames {picks} (flop={flop}, scale={scale:.4f})")
