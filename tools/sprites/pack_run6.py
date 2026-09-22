#!/usr/bin/env python3
"""Key + pack SIX extracted i2v run frames as run6_1..run6_6 — the smoother
6-cell run cycle (engine prefers run6_* over nrun_i*). Same recipe as
pack_i2v_run.py: fuzz 42% corner-floodfill keying (kills bg + the clip's soft
drop-shadow), MATCH_HEIGHT=nrun1 so every cell lands at the proven run height
-> 0% wobble.

Usage: python3 pack_run6.py <name> <frames_dir> <f1> <f2> <f3> <f4> <f5> <f6> [--uniform]
  --uniform: ONE scale for all six instead of per-cell MATCH_HEIGHT — for
  clips whose picks include wide lunge poses that would hit extend_sheet's
  cell-box clamp (the clamp shortens just those frames -> wobble returns).
  The clip's own registration keeps heights equal; the set is sized so the
  widest frame fits with no clamp.
"""
import sys, subprocess, tempfile, pathlib, os, json
from PIL import Image

name, fdir = sys.argv[1], sys.argv[2]
picks = sys.argv[3:9]
uniform = "--uniform" in sys.argv
assert len(picks) == 6, "need exactly 6 frame numbers"
HERE = pathlib.Path(__file__).resolve().parent
REPO = HERE.parent.parent
SHEETS = REPO / "web" / "assets" / "sprites"
tmp = pathlib.Path(tempfile.mkdtemp())

for i, fr in enumerate(picks, 1):
    src = f"{fdir}/f_{int(fr):03d}.png"
    dst = tmp / f"run6_{i}.png"
    subprocess.run(["magick", src, "-alpha", "set", "-bordercolor", "white", "-border", "1",
                    "-fuzz", "42%", "-fill", "none", "-floodfill", "+0+0", "white",
                    "-shave", "1x1", "-trim", "+repage", str(dst)], check=True)

if uniform:
    # per-cell height matching like the default path, but to a REDUCED target:
    # the largest height at which every frame's width still clears the cell box,
    # so the clamp never fires and all six land at exactly the same height.
    man = json.loads((SHEETS / f"{name}.json").read_text())
    sheet = Image.open(SHEETS / f"{name}.png").convert("RGBA")
    cw, chh, pad = man["frameW"], man["frameH"], man["frameH"] - man["footY"]
    ref = sheet.crop((man["frames"]["nrun1"] * cw, 0, (man["frames"]["nrun1"] + 1) * cw, chh))
    bb = ref.getbbox(); target = bb[3] - bb[1]
    sizes = [Image.open(tmp / f"run6_{i}.png").size for i in range(1, 7)]
    fit = int(min([target] + [(cw - 2) * h / w for w, h in sizes] + [chh - pad - 2]))
    print(f"[{name}] height target {fit}px (nrun1={target}px, widest-frame fit)")
    env = dict(os.environ, MATCH_HEIGHT_PX=str(fit))
else:
    env = dict(os.environ, MATCH_HEIGHT="nrun1")
subprocess.run([sys.executable, str(HERE / "extend_sheet.py"), name, str(tmp),
                str(HERE / "base" / f"{name}.png"), str(REPO / "web" / "assets" / "sprites"),
                "run6_1", "run6_2", "run6_3", "run6_4", "run6_5", "run6_6"], check=True, env=env)
print(f"packed {name} run6 from frames {picks}")
