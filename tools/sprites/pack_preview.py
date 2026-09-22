#!/usr/bin/env python3
"""Pack polished candidate frames into a PREVIEW sheet (replace-in-place).
Local preview only — never merged to main. Keys white-bg candidates (magick
corner floodfill fuzz 42%, house method), scales content to the OLD cell's
content height, anchors bottom-center at the old cell's footprint.
Usage: pack_preview.py <character> <candidates_raw_dir> [--cells name1,name2,...]
"""
import json, pathlib, subprocess, sys, tempfile
from PIL import Image

char = sys.argv[1]
raw = pathlib.Path(sys.argv[2])
cells_arg = None
if "--cells" in sys.argv:
    cells_arg = sys.argv[sys.argv.index("--cells") + 1].split(",")
# --uniform: one scale ratio for the whole character (old idle height / new idle height).
# Per-cell height matching shrinks the fighter when Kontext renders a pose more upright
# than the old cell (shin run_clean2); uniform keeps the new set's internal proportions.
uniform = "--uniform" in sys.argv

sheet_p = pathlib.Path(f"web/assets/sprites/{char}.png")
man_p = pathlib.Path(f"web/assets/sprites/{char}.json")
man = json.loads(man_p.read_text())
fw, fh = int(man["frameW"]), int(man["frameH"])
sheet = Image.open(sheet_p).convert("RGBA")

def key_white(src: pathlib.Path) -> Image.Image:
    with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tf:
        out = tf.name
    # 1px white border wrap so floodfill gets around any drawn frame lines, then shave
    subprocess.run(["magick", str(src), "-bordercolor", "white", "-border", "1",
                    "-fuzz", "42%", "-fill", "none", "-draw", "alpha 0,0 floodfill",
                    "-shave", "1x1", out], check=True)
    img = Image.open(out).convert("RGBA")
    pathlib.Path(out).unlink()
    return img

uniform_ratio = None
if uniform:
    idle_idx = int(man["frames"]["idle"])
    ib = sheet.crop((idle_idx * fw, 0, (idle_idx + 1) * fw, fh)).getbbox()
    ni = key_white(raw / "idle.png")
    nib = ni.getbbox()
    uniform_ratio = (ib[3] - ib[1]) / (nib[3] - nib[1])
    print(f"uniform ratio {uniform_ratio:.4f} (old idle h {ib[3]-ib[1]}, new idle h {nib[3]-nib[1]})")

packed, skipped = [], []
targets = cells_arg or [n for n in man["frames"] if (raw / f"{n}.png").exists()]
for name in targets:
    cand_p = raw / f"{name}.png"
    if not cand_p.exists() or name not in man["frames"]:
        skipped.append(name); continue
    idx = int(man["frames"][name])
    box = (idx * fw, 0, (idx + 1) * fw, fh)
    old_cell = sheet.crop(box)
    ob = old_cell.getbbox()
    if not ob:
        skipped.append(name); continue
    old_h = ob[3] - ob[1]; old_bottom = ob[3]; old_cx = (ob[0] + ob[2]) // 2
    new = key_white(cand_p)
    nb = new.getbbox()
    if not nb:
        skipped.append(name); continue
    new = new.crop(nb)
    scale = uniform_ratio if uniform else old_h / new.height
    nw = max(1, round(new.width * scale))
    if nw > fw:  # clamp width, height follows (house clamp)
        scale = fw / new.width * scale / (old_h / new.height) * (old_h / new.height)
        scale = min(old_h / new.height, fw / new.width)
        nw = max(1, round(new.width * scale))
    nh = max(1, round(new.height * scale))
    new = new.resize((nw, nh), Image.Resampling.LANCZOS)
    blank = Image.new("RGBA", (fw, fh), (0, 0, 0, 0))
    px = min(max(0, old_cx - nw // 2), fw - nw)
    py = max(0, old_bottom - nh)
    blank.paste(new, (px, py), new)
    sheet.paste(blank, (box[0], 0))
    packed.append(name)

sheet.save(sheet_p)
print(f"packed {len(packed)} cells into {sheet_p}: {','.join(packed)}")
if skipped: print(f"skipped: {','.join(skipped)}")
