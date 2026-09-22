#!/usr/bin/env python3
"""Animate storyboard panels into trailer shots with Seedance 2.

The storyboard panel IS the seed, so the model moves the art that already exists
instead of inventing a character — that is the whole anti-drift strategy here.

Prompt shape is the owner's 4-block anti-drift architecture: SUBJECT+ANCHOR,
MOTION, CAMERA, ENVIRONMENT+STYLE — each isolated, subject frozen first.

Usage:
  python3 tools/trailer/anim_panels.py test          # one shot, ~$1.52
  python3 tools/trailer/anim_panels.py all           # the rest
"""
import os, sys, json, subprocess
from pathlib import Path

SCR = Path("/private/tmp/claude-501/-Users-anthonyguy-SHADOWCLASH-RECOVERED"
           "/ca56c915-b305-4845-a1ac-6d66942b0b2d/scratchpad")
PAN, CLIPS = SCR / "panels", SCR / "clips"
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "sprites"))

for line in (Path.home() / ".env.local").read_text().splitlines():
    if line.startswith("FAL_KEY="):
        os.environ["FAL_KEY"] = line.split("=", 1)[1].strip().strip('"').strip("'")

import fal_client
from fal_models import i2v_clip

STYLE = ("2D cel-shaded illustration, heavy black outlines, flat controlled dark palette, "
         "glowing featureless angled eyes, painterly torchlit background, film grain. "
         "Exactly the art style of the source image.")
CAMERA = ("CAMERA: locked-off, tripod stable, fixed focal length. The camera does not move, "
          "zoom, pan, dolly or orbit. Framing identical in the first and last frame.")

# (panel, seconds, motion). Panels the storyboard already groups into one action
# are animated as ONE shot — fewer generations, fewer seams, less spend.
SHOTS = [
    ("p01", "5", "Torch flames flicker and banners ripple in the wind. Ash drifts down through the air. The small hooded figure walks slowly forward. Everything else is still."),
    ("p02", "5", "The gold-hooded ninja walks forward into frame, scarf trailing behind him. His glowing eyes hold steady."),
    ("p04", "5", "The gold-hooded ninja settles into a cross-blade stance, both swords crossed in front of him. His scarf lifts and settles. He breathes once. He does not attack."),
    ("p05", "5", "The purple-hooded figure stands motionless at the top of the stone steps, greatsword point-down. Only his orange scarf moves in the wind. He does not react to anything."),
    ("p06", "5", "Extreme close-up on the horned purple hood. The glowing orange eyes flicker and dim, then brighten. Faint purple dread-smoke curls upward behind him. He does not turn."),
    ("p07", "5", "The gold ninja spins, both blades sweeping a fast golden arc trail around his body. Sparks fly off the blades."),
    ("p10", "5", "The purple-hooded figure slips smoothly backward and to the side, blade held low, purple after-images trailing his motion. He returns to centre."),
    ("p12", "5", "Blades clash — a hot orange spark burst flares at the point of contact, then fades. The purple-hooded figure holds his guard, unmoved."),
    ("p15", "5", "The gold ninja launches upward, both blades rising in a bright golden crescent arc. Motion trails follow the blades."),
    ("p16", "5", "Only drifting purple shadow and smoke. The figure has already gone. Empty dark space, faint embers floating."),
    ("p18", "5", "The gold ninja lands hard and off balance, momentum carrying him forward, scarf whipping. He is exposed."),
    ("p22", "5", "One blinding flash of steel bursts from the sheath, orange sparks exploding outward, the horned figure's eyes flaring bright. Fast and final."),
]

def prompt_for(motion):
    return (f"SUBJECT AND ANCHOR: keep the character in the source image exactly as drawn — "
            f"same colours, same hood, same horns, same number of blades, same proportions. "
            f"Do not redesign, do not add or remove anything.\n"
            f"MOTION: {motion}\n{CAMERA}\nENVIRONMENT AND STYLE: {STYLE}")

def run(shots):
    CLIPS.mkdir(parents=True, exist_ok=True)
    total = 0.0
    for pid, dur, motion in shots:
        out = CLIPS / f"{pid}.mp4"
        if out.exists():
            print(f"skip {pid} (already have it)"); continue
        print(f"→ {pid} ...", flush=True)
        r = i2v_clip(fal_client, prompt_for(motion), PAN / f"{pid}.png",
                     duration=dur, resolution="1080p", aspect_ratio="16:9")
        url = r["video"]["url"]
        print("   ", url)
        subprocess.run(["curl", "-sL", "-o", str(out), url], check=True)   # proxy breaks urllib
        total += 1.52
        print(f"   saved {out.name}  running total ${total:.2f}")
    print(f"\nSPEND THIS RUN: ${total:.2f}")

if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else "test"
    run(SHOTS[:1] if mode == "test" else SHOTS)
