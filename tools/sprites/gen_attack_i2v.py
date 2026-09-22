#!/usr/bin/env python3
"""i2v heavy-attack pipeline (same second-brain method as gen_run_i2v.py): a
reference pose is animated into a short VIDEO by Seedance 2 i2v, then frames are
extracted. Video frames are REGISTERED (one continuous motion) so the attack
arc reads clean instead of wobbling between independent t2i frames.

Step 1: nano-banana-pro makes a clean full-res SIDE-VIEW attack-windup seed from the base.
Step 2: Seedance 2 i2v (bytedance/seedance-2.0/image-to-video) animates
        it into a 5s locked-camera repeated-attack clip. ~$0.10.
Step 3: ffmpeg dumps frames at 24fps (attacks are fast — finer slices than the
        run cycle's 12); a human picks the clean swing window.

Mirrors src/lib/motion/animate-panel.ts params. curl downloads (fal blocks
python fetch on this proxied machine).

Usage: FAL_KEY=... python3 gen_attack_i2v.py <name> <base_png> <out_dir> "<weapon_action>"
"""
import os, sys, subprocess, pathlib, re
from PIL import Image, ImageStat

def load_fal_key():
    if os.environ.get("FAL_KEY"):
        return os.environ["FAL_KEY"]
    for p in (pathlib.Path(".env.local"), pathlib.Path(__file__).with_name(".env.local")):
        if p.exists():
            m = re.search(r'FAL_KEY=["\']?([^"\'\n]+)', p.read_text())
            if m:
                return m.group(1).strip()
    sys.exit("FAL_KEY not set")

os.environ["FAL_KEY"] = load_fal_key()
import fal_client
from fal_models import still_edit, i2v_clip, MOTION_MODEL, STILL_MODEL

name, base_path, out_dir, weapon_action = sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4]
out = pathlib.Path(out_dir); out.mkdir(parents=True, exist_ok=True)

def valid(p):
    try:
        m = ImageStat.Stat(Image.open(p).convert("L")).mean[0] / 255.0
        return 0.2 < m < 0.97
    except Exception:
        return False

# --- Step 1: side-view attack-windup seed via nano-banana-pro --------------------------
seed = out / "seed.png"
seed_prompt = (
    "Repose into a STRICT SIDE PROFILE coiled attack windup: the character is seen purely from the "
    "SIDE, facing LEFT, in full left-facing profile like a 2D fighting-game attack sprite. Only ONE "
    "side of the body faces the viewer; the face is in profile. "
    # The weapon description MUST reach the seed: Kontext once fused Kael's two
    # swords into one because this prompt said "Weapon raised" — and i2v can
    # never restore a weapon the seed lost. The clip is only as honest as the seed.
    f"The character {weapon_action}. Keep the EXACT same weapon(s) — same count, same size, same type "
    "as the input image; never merge two weapons into one, never invent a new weapon. "
    "Coiled ready to unleash the attack: knees bent, torso wound up. "
    "NOT front-facing, NOT three-quarter view — pure left profile. "
    "Keep the exact same character identity. Bold black outlines, flat cel shading, "
    "full body, single chibi character, centered, plain solid pure white background, no shadow, no text."
)
seed_url = fal_client.upload_file(base_path)
print(f"[{name}] seed: generating side-view attack windup via nano-banana-pro...", file=sys.stderr)
for attempt in range(5):
    r = still_edit(fal_client, seed_prompt, base_path)
    print(f"[{name}] seed URL: {r['images'][0]['url']}", file=sys.stderr)
    subprocess.run(["curl", "-sSL", "-o", str(seed), r["images"][0]["url"]], check=True)
    if valid(seed):
        print(f"[{name}] seed OK (try {attempt+1})", file=sys.stderr)
        break
else:
    sys.exit(f"[{name}] seed generation FAILED")

# --- Step 2: Seedance 2 i2v repeated heavy-attack clip -------------------------------
video_url = fal_client.upload_file(str(seed))
i2v_prompt = (
    f"Side-scroller heavy attack cycle. The character {weapon_action} — repeated full attack swings, "
    "one after another, each swing a complete arc: wind up, slash through, follow through, return to "
    "ready. The character is filmed in STRICT LEFT SIDE PROFILE and STAYS in side profile for the "
    "entire clip — it NEVER rotates, NEVER turns to face the camera, NEVER changes angle. "
    "Only the arms and torso swing the attacks; the feet stay planted on an invisible ground line and "
    "do NOT travel. "
    "LOCKED-OFF STATIC CAMERA, absolutely no camera movement, no zoom, no pan, no dolly, no orbit. "
    "The character stays perfectly centered and the EXACT SAME SIZE in every single frame. "
    "Plain solid pure white background, no shadow. Keep the exact chibi "
    "character identity and the same face in profile, bold black outlines, flat cel shading. "
    "Smooth looping 2D side-view sprite animation."
)
print(f"[{name}] i2v: animating attack cycle via Seedance 2 (~$0.15, ~1-2 min)...", file=sys.stderr)
rv = i2v_clip(fal_client, i2v_prompt, seed, duration="5", resolution="1080p",
              aspect_ratio="9:16", loop=False)   # no loop: a swing must not rewind
vurl = rv["video"]["url"]
print(f"[{name}] VIDEO URL: {vurl}")
mp4 = out / "attack.mp4"
subprocess.run(["curl", "-sSL", "-o", str(mp4), vurl], check=True)
print(f"[{name}] downloaded {mp4} ({mp4.stat().st_size} bytes)")

# --- Step 3: dump a dense strip for the human to pick a clean swing window ------
frames_dir = out / "frames"; frames_dir.mkdir(exist_ok=True)
subprocess.run(["ffmpeg", "-y", "-i", str(mp4), "-vf", "fps=24", str(frames_dir / "f_%03d.png")],
               check=True, capture_output=True)
n = len(list(frames_dir.glob("f_*.png")))
print(f"[{name}] extracted {n} frames at 24fps -> {frames_dir}")
