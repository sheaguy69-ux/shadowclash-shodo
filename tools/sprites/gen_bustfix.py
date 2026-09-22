#!/usr/bin/env python3
"""Pose-collapse-proof generator: NEUTRAL-CELL guide + BUST-CROPPED identity ref.

exp-d 2026-07-18: for characters whose flat silhouettes are illegible (big hair /
cloak mass — tsubasa, ember, kael) the guide is the OLD CELL in flattened grayscale:
pose and limb detail stay readable, old colors/design are neutralized. Bust-cropped
identity ref still supplies face/palette and cannot inject a stance.
Proven in exp-c (2026-07-18): a head-and-shoulders identity image cannot inject
a stance, so the pose guide is the only geometry source. Inline pose check
aborts the run after 2 consecutive frames that clone the set's idle (>0.92
silhouette similarity) — a collapsed batch stops at ~2 frames, not 33.
Usage: gen_bustfix.py <character> <identity_description_file_or_->  (reads frames from model-guides/)
"""
import os, re, sys, pathlib, subprocess, itertools
import numpy as np
from PIL import Image
sys.path.insert(0, str(pathlib.Path(__file__).parent))
from pose_gate import ink, iou

char = sys.argv[1]
IDENTITY = sys.stdin.read().strip() if sys.argv[2] == "-" else pathlib.Path(sys.argv[2]).read_text().strip()
base = pathlib.Path(f"media/polished-candidates/{char}")
env = pathlib.Path("/Users/anthonyguy/WILDCOMIKS.2.0/.env.local")
os.environ["FAL_KEY"] = re.search(r'^FAL_KEY=["\']?([^"\'\n]+)', env.read_text(), re.M).group(1).strip()
import fal_client

import json
from PIL import ImageOps
man = json.loads(pathlib.Path(f"web/assets/sprites/{char}.json").read_text())
sheet = Image.open(f"web/assets/sprites/{char}.png").convert("RGBA")
fw, fh = int(man["frameW"]), int(man["frameH"])
ngdir = base / "neutral-guides"; ngdir.mkdir(exist_ok=True)
def neutral_guide(frame):
    gp = ngdir / f"{frame}.png"
    if gp.exists(): return gp
    idx = int(man["frames"][frame])
    cell = sheet.crop((idx*fw, 0, (idx+1)*fw, fh))
    # largest connected component only — old-cell debris (neighbor bleed, floating
    # shards) otherwise renders as severed heads / bows / blade fragments (kael v3).
    import collections
    a = np.array(cell.getchannel("A"))
    mask = (a > 40).astype(np.uint8)
    lbl = np.zeros_like(mask, dtype=np.int32); cur = 0
    H, W = mask.shape
    for sy in range(H):
        for sx in range(W):
            if mask[sy, sx] and not lbl[sy, sx]:
                cur += 1
                q = collections.deque([(sy, sx)]); lbl[sy, sx] = cur
                while q:
                    y, x = q.popleft()
                    for ny, nx in ((y-1,x),(y+1,x),(y,x-1),(y,x+1)):
                        if 0 <= ny < H and 0 <= nx < W and mask[ny, nx] and not lbl[ny, nx]:
                            lbl[ny, nx] = cur; q.append((ny, nx))
    if cur > 1:
        keep = int(np.argmax(np.bincount(lbl.ravel())[1:])) + 1
        a = np.where(lbl == keep, a, 0).astype("uint8")
        cell.putalpha(Image.fromarray(a))
    b = cell.getbbox(); cell = cell.crop(b)
    g = ImageOps.autocontrast(cell.convert("L")).point(lambda v: 110 + v//3)
    canvas = Image.new("RGB", (880, 1184), "white")
    sc = min(880*0.86/cell.width, 1184*0.86/cell.height)
    size = (round(cell.width*sc), round(cell.height*sc))
    canvas.paste(Image.merge("RGB", (g,)*3).resize(size), ((880-size[0])//2, (1184-size[1])//2),
                 cell.getchannel("A").resize(size))
    canvas.save(gp); return gp

ref = Image.open(f"media/polished-candidates/corrected-refs/final/{char}-owner-corrected-ref.png")
bust_p = base / "bust-ref.png"
ref.crop((0, 0, ref.width, int(ref.height * 0.48))).save(bust_p)
bust_url = fal_client.upload_file(str(bust_p))
out = base / "raw-v2"; out.mkdir(exist_ok=True)
frames = sorted(p.stem for p in (base / "model-guides").glob("*.png"))
# idle FIRST: it is the collapse-check reference — alphabetical order left the
# first 8 frames unchecked (attack_body* < idle). Caught in fault audit 2026-07-18.
if "idle" in frames:
    frames.remove("idle"); frames.insert(0, "idle")
idle_sil, consec = None, 0
for i, frame in enumerate(frames):
    outp = out / f"{frame}.png"
    if outp.exists():
        print(f"SKIP {frame}"); continue
    prompt = (f"EDIT IMAGE #1 IN PLACE for the {frame} animation frame. IMAGE #1 IS THE ONLY GEOMETRY AUTHORITY: "
              "keep its EXACT pose — limb positions, torso lean, weapon arm angles, stride, tilt. Its gray, "
              "washed-out look is deliberately neutralized old art: REPLACE the design completely. IMAGE #2 is a "
              "HEAD-AND-SHOULDERS reference for face, hair, eyes, palette, and materials only — it contains NO "
              f"pose information and must contribute none. The character: {IDENTITY}. "
              "Crisp black outlines, polished cel shading, plain pure white background, no shadow, no text, no border.")
    r = fal_client.subscribe("fal-ai/flux-pro/kontext/multi", arguments={
        "prompt": prompt,
        "image_urls": [fal_client.upload_file(str(neutral_guide(frame))), bust_url],
        "num_images": 1, "output_format": "png", "safety_tolerance": "6",
        "aspect_ratio": "3:4", "seed": int(os.environ.get("SEED_BASE", "44440718")) + i * 100,
        "guidance_scale": 4.5, "enhance_prompt": False,
    }, with_logs=False)
    subprocess.run(["curl", "-fsSL", "-o", str(outp), r["images"][0]["url"]], check=True)
    sil = ink(outp)
    if frame == "idle": idle_sil = sil
    elif idle_sil is not None and not frame.startswith("idle"):
        sim = iou(idle_sil, sil)
        collapsed = sim > 0.92
        consec = consec + 1 if collapsed else 0
        print(f"OK {frame} idleSim={sim:.3f}{' COLLAPSE-WARN' if collapsed else ''}", flush=True)
        if consec >= 2:
            sys.exit(f"ABORT: 2 consecutive pose-collapsed frames at {frame} — stop billing, fix the method")
        continue
    print(f"OK {frame}", flush=True)
print(f"DONE {char} {len(frames)} frames -> {out}")
