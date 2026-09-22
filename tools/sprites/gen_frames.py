#!/usr/bin/env python3
"""Generate the 12 animation-pose frames for ONE ninja via fal FLUX Kontext.

Each pose is an identity-locked *repose* of the character's base illustration:
Kontext keeps the exact character (colours, hood, eyes, weapon) and only changes
the pose. Frames are validated (solid-black fal failures / blank frames are
rejected and retried) and downloaded with curl.

Usage:
    FAL_KEY=... python3 gen_frames.py <name> <base_png> <out_dir> "<identity phrase>"

Example:
    FAL_KEY=xxx python3 gen_frames.py executioner base/executioner.png frames/executioner \
        "purple hood, curved demon horns, orange scarf, orange glowing eyes and a long sword"

Requires: pip install fal-client pillow ; and `curl` on PATH.
Notes:
  * Kontext holds IDENTITY very well but is CONSERVATIVE about leg/stride
    reposes — the "Repose into ..." wording + guidance_scale 4.0 force bigger
    poses (default 3.5 barely moves the base). See the improvement backlog in
    docs/SPRITE-HANDOFF.md for stronger-pose strategies.
  * fal occasionally returns a solid-black frame; that's why every frame is
    validated (mean luminance in 0.2..0.97) and retried up to 4x.
"""
import os, sys, pathlib, subprocess, re, concurrent.futures as cf
from PIL import Image, ImageStat

def load_fal_key():
    if os.environ.get("FAL_KEY"):
        return os.environ["FAL_KEY"]
    # fallback: a .env.local in CWD or alongside this script
    for p in (pathlib.Path(".env.local"), pathlib.Path(__file__).with_name(".env.local")):
        if p.exists():
            m = re.search(r'FAL_KEY=["\']?([^"\'\n]+)', p.read_text())
            if m:
                return m.group(1).strip()
    sys.exit("FAL_KEY not set (export FAL_KEY=... or put it in .env.local)")

os.environ["FAL_KEY"] = load_fal_key()
import fal_client

name, base_path, out_dir, identity = sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4]
pathlib.Path(out_dir).mkdir(parents=True, exist_ok=True)

SUF = (f" Keep the exact same character identity: {identity}. Bold black outlines, flat cel "
       "shading, full body, single character, centered, plain solid pure white background, "
       "no text, no extra characters.")

# The 12 canonical poses. drawSprite() in web/index.html maps each FSM STATE to
# one or two of these by name — keep the keys stable if you regenerate.
POSES = {
 "idle":   "standing in a calm combat-ready idle stance, feet planted apart, weapon held ready at the side",
 "idle2":  "standing combat-ready, weight shifted onto one leg, chest raised mid-breath, weapon held ready",
 "run1":   "Repose into a running stride: front knee lifted and bent forward, back leg extended behind, body leaning forward, weapon trailing. Running action pose.",
 "run2":   "Repose into a running stride with the OPPOSITE legs: back leg driving forward with knee up, other leg extended back, arms swinging, leaning forward. Running action pose.",
 "jump":   "Repose leaping high into the air, BOTH knees tucked up toward the chest, both feet off the ground, weapon raised. Dynamic airborne jump, no ground shadow.",
 "fall":   "Repose descending from a jump, legs spread wide downward ready to land, arms out for balance. Airborne falling pose, no ground shadow.",
 "light1": "Repose winding up a quick attack, weapon drawn back beside the body, front foot stepping forward, coiled to strike.",
 "light2": "Repose into a fast forward attack lunge, weapon arm fully extended thrusting the weapon straight out to the side, front leg deep in a forward lunge.",
 "heavy1": "Repose winding up a heavy attack, weapon raised high overhead with both arms, body coiled back, ready to strike down.",
 "heavy2": "Repose the follow-through of a heavy overhead strike, weapon swung all the way DOWN and forward to low, body bent forward from the swing.",
 "block":  "Repose into a defensive guard, crouched low, arms and weapon raised across the body to shield and block.",
 "hurt":   "Repose staggering backward from a hard hit, torso arched back, head thrown back, arms flung outward, off balance and reeling.",
 "wallslide": "Repose into a wall-slide: body upright and vertical, knees bent with both feet tucked back beneath the hips, one arm reaching back behind the body bracing against a surface behind them, the other arm forward for balance, scarf and clothes blown UPWARD as if sliding downward. IMPORTANT: do not draw any wall, surface or object — only the character.",
}

url = fal_client.upload_file(base_path)
print(f"[{name}] base uploaded", file=sys.stderr)

def valid(path):
    try:
        m = ImageStat.Stat(Image.open(path).convert("L")).mean[0] / 255.0
        return 0.2 < m < 0.97   # reject solid-black fal failures and blank frames
    except Exception:
        return False

def one(item):
    pose, frag = item
    dest = f"{out_dir}/{pose}.png"
    for attempt in range(4):
        r = fal_client.subscribe("fal-ai/flux-pro/kontext", arguments={
            "prompt": frag + SUF, "image_url": url, "output_format": "png",
            "guidance_scale": 4.0, "safety_tolerance": "6",
        }, with_logs=False)
        subprocess.run(["curl", "-sSL", "-o", dest, r["images"][0]["url"]], check=True)
        if valid(dest):
            return f"OK   {pose}  (try {attempt+1})"
    return f"FAIL {pose}  (still invalid after 4 tries)"

with cf.ThreadPoolExecutor(max_workers=6) as ex:
    for line in ex.map(one, POSES.items()):
        print(line, flush=True)
print(f"[{name}] DONE")
