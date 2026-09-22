#!/usr/bin/env python3
"""Generate the attack-variety cells: per-character SIGNATURE SPECIAL frames
(special1 windup, special2 release — matching what the special actually does
in-game) plus a third in-between frame for light and heavy chains.

Appended to sheets by extend_sheet.py; originals never touched.

Usage: FAL_KEY=... python3 gen_attackposes.py <out_root>
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

HERE = pathlib.Path(__file__).resolve().parent
OUT = pathlib.Path(sys.argv[1])

IDENTITY = {
 "executioner": "purple hood, curved demon horns, orange scarf, orange glowing eyes and a long sword",
 "mizu":        "purple domed hood, long ragged cloak, glowing white eyes and a long wooden bo staff",
 "shin":        "teal-green hood with trailing headband tails, glowing cyan eyes and a metal shuriken throwing star",
 "tsubasa":     "wild black and red flame hair, glowing red eyes, a red scarf and dual crossed katanas",
 "ember":       "lime-green hood, black cape, glowing green eyes and metal claws on both fists",
 "kael":        "golden-yellow hood, black body armor, glowing yellow eyes and two swords",
}

# signature special per character = what the move DOES in executeAttack
SPECIALS = {
 "executioner": (
    "Repose winding up an enormous two-handed overhead strike: the long sword raised high "
    "behind the head with both hands, body leaning back, gathering power.",
    "Repose slamming the long sword down INTO the ground in front: blade low and buried forward, "
    "body fully committed forward over the front leg, impact stance."),
 "mizu": (
    "Repose spinning the long wooden bo staff overhead: staff horizontal above the head mid-whirl, "
    "one arm raised holding it, cloak swirling around the body.",
    "Repose sweeping the bo staff in a wide low arc: staff fully extended out in front, deep forward "
    "lunge, the sweep finishing across the body."),
 "shin": (
    "Repose winding up a shuriken throw: throwing arm cocked back behind the head holding the "
    "shuriken, other arm aiming straight forward, weight on the back foot.",
    "Repose the instant after hurling the shuriken: throwing arm fully extended forward with fingers "
    "open on release, body leaning hard into the throw, back leg kicked up behind."),
 "tsubasa": (
    "Repose crossing both katanas in front of the chest in an X-shaped guard: blades crossed, "
    "elbows tucked, braced defensive counter stance.",
    "Repose slashing outward with BOTH katanas at once in a wide scissor cut: both arms fully "
    "extended out to the sides, torso twisted, blades apart at the end of the cut."),
 "ember": (
    "Repose leaning low ready to pounce: both metal claws raised up beside the face, elbows bent, "
    "feral hunting stance, weight forward on the toes.",
    "Repose lunging forward raking both metal claws ahead: both arms thrust straight forward, body "
    "stretched near-horizontal in the lunge, one leg driving off the ground."),
 "kael": (
    "Repose with both swords drawn back on opposite sides: arms spread wide apart, one blade high "
    "and one low, ready to scissor together.",
    "Repose mid double-slash: both swords sweeping across each other in front of the body, arms "
    "crossing, twin cutting arcs."),
}

LIGHT3 = ("Repose the follow-through of a fast slash: weapon arm swung fully ACROSS the body to the "
          "opposite side, torso twisted with the cut, front foot planted, cut finished.")
HEAVY3 = ("Repose recovering after a massive downward swing: weapon held low and trailing behind the "
          "body, torso rising back upright, slightly off balance from the force.")

def valid(p):
    try:
        m = ImageStat.Stat(Image.open(p).convert("L")).mean[0] / 255.0
        return 0.2 < m < 0.97
    except Exception:
        return False

def gen(name, pose, frag, url, suf):
    dest = OUT / name / f"{pose}.png"
    dest.parent.mkdir(parents=True, exist_ok=True)
    for attempt in range(5):
        r = fal_client.subscribe("fal-ai/flux-pro/kontext", arguments={
            "prompt": frag + suf, "image_url": url, "output_format": "png",
            "guidance_scale": 4.2, "safety_tolerance": "6"}, with_logs=False)
        subprocess.run(["curl", "-sSL", "-o", str(dest), r["images"][0]["url"]], check=True)
        if valid(dest):
            return f"OK   {name}/{pose} (try {attempt+1})"
    return f"FAIL {name}/{pose}"

jobs = []
for name, ident in IDENTITY.items():
    url = fal_client.upload_file(str(HERE / "base" / f"{name}.png"))
    suf = (f" Keep the exact same character identity: {ident}. The character faces LEFT. Bold black "
           "outlines, flat cel shading, full body, single character, centered, plain solid pure white "
           "background, no text, no extra characters.")
    sp1, sp2 = SPECIALS[name]
    jobs += [(name, "special1", sp1, url, suf), (name, "special2", sp2, url, suf),
             (name, "light3", LIGHT3, url, suf), (name, "heavy3", HEAVY3, url, suf)]

with cf.ThreadPoolExecutor(max_workers=6) as ex:
    for line in ex.map(lambda j: gen(*j), jobs):
        print(line, flush=True)
print("ALL DONE")
