#!/usr/bin/env python3
"""Generate the 3 ADD-ON pose frames (ninja sprint x2 + tucked roll) for one ninja.

Same pipeline rules as gen_frames.py: identity-locked Kontext reposes of the
base illustration, luminance-validated (solid-black fal failures rejected),
curl downloads. These frames are APPENDED to the existing sheets by
extend_sheet.py — the original 13 cells are never touched.

Usage:
    FAL_KEY=... python3 gen_newposes.py <name> <base_png> <out_dir> "<identity phrase>"
"""
import os, sys, pathlib, subprocess, re, concurrent.futures as cf
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

name, base_path, out_dir, identity = sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4]
pathlib.Path(out_dir).mkdir(parents=True, exist_ok=True)

SUF = (f" Keep the exact same character identity: {identity}. The character faces LEFT. "
       "Bold black outlines, flat cel shading, full body, single character, centered, "
       "plain solid pure white background, no text, no extra characters.")

# the traditional anime ninja sprint the owner asked for + a real tuck for the roll
POSES = {
 "nrun1": ("Repose into a full-sprint NINJA RUN: torso pitched far forward almost horizontal, "
           "head low and forward, BOTH arms swept straight back behind the torso, front knee "
           "driving forward, back leg extended far behind, running very low to the ground. "
           "Classic anime ninja sprint action pose."),
 "nrun2": ("Repose into a full-sprint NINJA RUN mid-stride with the OPPOSITE legs: torso pitched "
           "far forward almost horizontal, head low, BOTH arms swept straight back behind the "
           "torso, back knee now driving forward, other leg extended far behind, very low to the "
           "ground. Classic anime ninja sprint action pose."),
 "roll":  ("Repose into a tight tucked somersault: knees pulled up against the chest, body curled "
           "forward into a compact tuck, head tucked down toward the knees, arms wrapped around "
           "the legs, both feet off the ground. Compact airborne tuck pose."),
}

url = fal_client.upload_file(base_path)
print(f"[{name}] base uploaded", file=sys.stderr)

def valid(path):
    try:
        m = ImageStat.Stat(Image.open(path).convert("L")).mean[0] / 255.0
        return 0.2 < m < 0.97
    except Exception:
        return False

def one(item):
    pose, frag = item
    dest = f"{out_dir}/{pose}.png"
    for attempt in range(5):
        # guidance 4.2: these are the biggest reposes in the set — force them
        r = fal_client.subscribe("fal-ai/flux-pro/kontext", arguments={
            "prompt": frag + SUF, "image_url": url, "output_format": "png",
            "guidance_scale": 4.2, "safety_tolerance": "6",
        }, with_logs=False)
        print(f"[{name}] {pose} RESULT_URL: {r['images'][0]['url']}", file=sys.stderr)
        subprocess.run(["curl", "-sSL", "-o", dest, r["images"][0]["url"]], check=True)
        if valid(dest):
            return f"OK   {pose}  (try {attempt+1})"
    return f"FAIL {pose}  (still invalid after 5 tries)"

with cf.ThreadPoolExecutor(max_workers=3) as ex:
    for line in ex.map(one, POSES.items()):
        print(line, flush=True)
print(f"[{name}] DONE")
