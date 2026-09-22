#!/usr/bin/env python3
"""Regenerate + pack all six ninja sprite sheets from their base illustrations.

Run from anywhere; paths are resolved relative to this file:
    base illustrations : tools/sprites/base/<name>.png
    working frames      : tools/sprites/frames/<name>/*.png
    packed output       : web/assets/sprites/<name>.{png,json}

Usage:
    FAL_KEY=... python3 tools/sprites/gen_all.py
    FAL_KEY=... python3 tools/sprites/gen_all.py ember kael   # only these two
"""
import subprocess, sys, pathlib
HERE = pathlib.Path(__file__).resolve().parent
REPO = HERE.parent.parent
BASE = HERE / "base"
FRAMES = HERE / "frames"
ADIR = REPO / "web" / "assets" / "sprites"

# name -> identity phrase fed to Kontext (the character's canonical description)
IDENTITY = {
 "executioner": "purple hood, curved demon horns, orange scarf, orange glowing eyes and a long sword",
 "mizu":        "purple domed hood, long ragged cloak, glowing white eyes and a long wooden bo staff",
 "shin":        "teal-green hood with trailing headband tails, glowing cyan eyes and a metal shuriken throwing star",
 "tsubasa":     "wild black and red flame hair, glowing red eyes, a red scarf and dual crossed katanas",
 "ember":       "lime-green hood, black cape, glowing green eyes and metal claws on both fists",
 "kael":        "golden-yellow hood, black body armor, glowing yellow eyes and two swords",
}

names = sys.argv[1:] or list(IDENTITY)
for name in names:
    print(f"\n===== {name} =====", flush=True)
    subprocess.run([sys.executable, str(HERE / "gen_frames.py"), name,
                    str(BASE / f"{name}.png"), str(FRAMES / name), IDENTITY[name]], check=True)
    subprocess.run([sys.executable, str(HERE / "pack_sheet.py"), name,
                    str(FRAMES / name), str(ADIR)], check=True)
print("\nALL DONE")
