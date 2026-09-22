#!/usr/bin/env python3
"""Key white->transparent, trim, normalize (feet-baseline, h-centered), pack a
single-row sprite sheet + JSON manifest for one ninja."""
import sys, subprocess, json, pathlib, shutil
from PIL import Image

name, fdir, adir = sys.argv[1], sys.argv[2], sys.argv[3]
pathlib.Path(adir).mkdir(parents=True, exist_ok=True)
ORDER = ["idle","idle2","run1","run2","jump","fall","light1","light2","heavy1","heavy2","block","hurt","wallslide"]
tmp = pathlib.Path(fdir) / "_t"; tmp.mkdir(exist_ok=True)

frames = []
for pose in ORDER:
    dst = f"{tmp}/{pose}.png"
    subprocess.run(["magick", f"{fdir}/{pose}.png", "-alpha", "set",
                    "-bordercolor", "white", "-border", "1",
                    "-fuzz", "25%", "-fill", "none", "-floodfill", "+0+0", "white",
                    "-shave", "1x1", "-trim", "+repage", dst], check=True)
    frames.append(Image.open(dst).convert("RGBA"))

# uniform downscale so the tallest frame is ~MAXH (keeps relative sizes; ~3-4x the on-screen px)
MAXH = 210.0
maxh = max(f.height for f in frames)
dsf = min(1.0, MAXH / maxh)
if dsf < 1.0:
    frames = [f.resize((max(1, round(f.width * dsf)), max(1, round(f.height * dsf))), Image.LANCZOS) for f in frames]

pad = 8
cellW = max(f.width for f in frames) + pad * 2
cellH = max(f.height for f in frames) + pad * 2
cols = len(ORDER)
sheet = Image.new("RGBA", (cellW * cols, cellH), (0, 0, 0, 0))
for i, f in enumerate(frames):
    x = i * cellW + (cellW - f.width) // 2      # horizontally center on content
    y = cellH - pad - f.height                  # bottom-align: feet baseline = cellH-pad
    sheet.paste(f, (x, y), f)

footY = cellH - pad
TARGET = 70.0                                   # on-canvas standing height (doll ~60)
scale = round(TARGET / frames[ORDER.index("idle")].height, 4)
out = f"{adir}/{name}.png"
sheet.save(out, optimize=True)
if shutil.which("pngquant"):
    subprocess.run(["pngquant", "--force", "--skip-if-larger", "--ext", ".png", "64", out], check=False)
elif shutil.which("magick"):
    subprocess.run(["magick", out, "-strip", "-define", "png:compression-level=9", out], check=False)
json.dump({"name": name, "frameW": cellW, "frameH": cellH, "cols": cols,
           "footY": footY, "scale": scale, "frames": {p: i for i, p in enumerate(ORDER)}},
          open(f"{adir}/{name}.json", "w"))
print(f"packed {name}: sheet {cellW*cols}x{cellH}  cell {cellW}x{cellH}  scale {scale}")
