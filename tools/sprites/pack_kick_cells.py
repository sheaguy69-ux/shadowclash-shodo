#!/usr/bin/env python3
"""Pack the four kick cells (ksweep/kpush/kheel/kstomp) into a ninja's sheet
from MIXED sources: i2v video frames (registered, need the seed-anchored
uniform scale — same math as pack_attack5.py) and/or Kontext stills (same
canvas scale as the base, default k path). FUZZ=42 everywhere: both sources
carry soft ground shadows.

Usage: python3 pack_kick_cells.py <name> <kickvid_dir> <kontext_dir> \
         ksweep=vid:37 kpush=kx kheel=vid:88:flop kstomp=skip
  vid:N[:flop] -> frame f_NNN.png from <kickvid_dir>/frames (flop = mirror a
                  right-facing frame to the sheet's authored LEFT)
  kx           -> <kontext_dir>/<pose>.png
  skip         -> cell not added (the game falls back to existing cells)
"""
import sys, subprocess, tempfile, pathlib, os, json
from PIL import Image

name, vdir, kdir = sys.argv[1], sys.argv[2], sys.argv[3]
spec = dict(a.split('=', 1) for a in sys.argv[4:])
HERE = pathlib.Path(__file__).resolve().parent
REPO = HERE.parent.parent
SHEETS = REPO / "web" / "assets" / "sprites"

def key(src, dst, flop=False):
    extra = ["-flop"] if flop else []
    subprocess.run(["magick", str(src), *extra, "-alpha", "set", "-bordercolor", "white", "-border", "1",
                    "-fuzz", "42%", "-fill", "none", "-floodfill", "+0+0", "white",
                    "-shave", "1x1", "-trim", "+repage", str(dst)], check=True)

vid = {p: (s.split(':')[1], s.endswith(':flop')) for p, s in spec.items() if s.startswith('vid:')}
kx = [p for p, s in spec.items() if s == 'kx']

# --- i2v cells: one uniform scale anchored through the seed (pack_attack5 math) ---
if vid:
    man = json.loads((SHEETS / f"{name}.json").read_text())
    sheet = Image.open(SHEETS / f"{name}.png").convert("RGBA")
    cw, ch = man["frameW"], man["frameH"]
    idle = sheet.crop((man["frames"]["idle"] * cw, 0, (man["frames"]["idle"] + 1) * cw, ch))
    idle_h = idle.getbbox()[3] - idle.getbbox()[1]
    tmp = pathlib.Path(tempfile.mkdtemp())
    key(HERE / "base" / f"{name}.png", tmp / "_base.png")
    key(f"{vdir}/seed.png", tmp / "_seed.png")
    key(f"{vdir}/frames/f_001.png", tmp / "_f1.png")
    scale = (Image.open(tmp / "_seed.png").height * (idle_h / Image.open(tmp / "_base.png").height)) \
            / Image.open(tmp / "_f1.png").height
    pad = man["frameH"] - man["footY"]
    for pose, (fr, flop) in vid.items():
        key(f"{vdir}/frames/f_{int(fr):03d}.png", tmp / f"{pose}.png", flop)
    # uniform shrink if any frame would overflow its cell box
    sizes = [Image.open(tmp / f"{p}.png").size for p in vid]
    fit = min([(cw - 2) / (w * scale) for w, h in sizes] + [(ch - pad - 2) / (h * scale) for w, h in sizes] + [1.0])
    if fit < 1.0:
        print(f"[{name}] i2v kick cells shrink to fit: {fit*100:.1f}%")
    env = dict(os.environ, FIXED_SCALE=str(scale * fit), FUZZ="42")
    subprocess.run([sys.executable, str(HERE / "extend_sheet.py"), name, str(tmp),
                    str(HERE / "base" / f"{name}.png"), str(SHEETS), *vid.keys()], check=True, env=env)

# --- Kontext cells: base-canvas scale, default k path ---
if kx:
    tmp2 = pathlib.Path(tempfile.mkdtemp())
    for pose in kx:
        subprocess.run(["cp", f"{kdir}/{pose}.png", str(tmp2 / f"{pose}.png")], check=True)
    env = dict(os.environ, FUZZ="42")
    subprocess.run([sys.executable, str(HERE / "extend_sheet.py"), name, str(tmp2),
                    str(HERE / "base" / f"{name}.png"), str(SHEETS), *kx], check=True, env=env)

print(f"packed {name}: i2v={list(vid.keys())} kontext={kx} skipped={[p for p,s in spec.items() if s=='skip']}")
