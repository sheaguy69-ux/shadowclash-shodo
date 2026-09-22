#!/usr/bin/env python3
"""Generate explicit running-cycle pose guides for ShadowClash fighters.

A proper run cycle has 4 key poses per stride (contact, passing, push-off, airborne)
with legs alternating. These guides use explicit joint coordinates so the model
has an unambiguous pose to follow.

Usage:
    python3 tools/sprites/make_run_guides.py <character> [--frames 4]
"""
import argparse
import os
from PIL import Image, ImageDraw

CANVAS = (880, 1184)


def draw_figure(draw, cx, hip_y, lean, dy, joints):
    """Draw a stick figure from explicit joint coordinates."""
    # joints: head, neck, hip, l_knee, l_foot, r_knee, r_foot, l_elbow, l_hand, r_elbow, r_hand
    # all relative to hip at (cx, hip_y)

    # Body
    hip = (cx + lean, hip_y + dy)
    neck = (hip[0] + lean * 0.5, hip[1] - 200)
    head = (neck[0] + lean * 0.2, neck[1] - 100)

    # Draw torso
    draw.line([hip, neck], fill=(0, 0, 0), width=20)
    draw.ellipse([head[0]-90, head[1]-90, head[0]+90, head[1]+90], fill=(0, 0, 0))

    # Left leg: hip -> l_knee -> l_foot
    l_knee = (hip[0] + joints["l_knee"][0], hip[1] + joints["l_knee"][1])
    l_foot = (hip[0] + joints["l_foot"][0], hip[1] + joints["l_foot"][1])
    draw.line([hip, l_knee], fill=(0, 0, 0), width=16)
    draw.line([l_knee, l_foot], fill=(0, 0, 0), width=16)

    # Right leg
    r_knee = (hip[0] + joints["r_knee"][0], hip[1] + joints["r_knee"][1])
    r_foot = (hip[0] + joints["r_foot"][0], hip[1] + joints["r_foot"][1])
    draw.line([hip, r_knee], fill=(0, 0, 0), width=16)
    draw.line([r_knee, r_foot], fill=(0, 0, 0), width=16)

    # Left arm: neck -> l_elbow -> l_hand
    l_elbow = (neck[0] + joints["l_elbow"][0], neck[1] + joints["l_elbow"][1])
    l_hand = (neck[0] + joints["l_hand"][0], neck[1] + joints["l_hand"][1])
    draw.line([neck, l_elbow], fill=(0, 0, 0), width=12)
    draw.line([l_elbow, l_hand], fill=(0, 0, 0), width=12)

    # Right arm
    r_elbow = (neck[0] + joints["r_elbow"][0], neck[1] + joints["r_elbow"][1])
    r_hand = (neck[0] + joints["r_hand"][0], neck[1] + joints["r_hand"][1])
    draw.line([neck, r_elbow], fill=(0, 0, 0), width=12)
    draw.line([r_elbow, r_hand], fill=(0, 0, 0), width=12)


# Each pose: lean, dy, and joint offsets relative to hip
POSES = [
    # 1. LEFT CONTACT: left leg forward extended, right leg back bent, body leaning forward
    {
        "lean": 30, "dy": 0,
        "l_knee": (60, 80), "l_foot": (100, 160),
        "r_knee": (-50, 100), "r_foot": (-80, 40),
        "l_elbow": (40, 60), "l_hand": (70, 100),
        "r_elbow": (-30, 80), "r_hand": (-60, 120),
    },
    # 2. PASSING: left leg under body bent, right leg lifting forward, body upright
    {
        "lean": 15, "dy": -30,
        "l_knee": (20, 100), "l_foot": (30, 160),
        "r_knee": (-20, 60), "r_foot": (-40, -20),
        "l_elbow": (20, 70), "l_hand": (40, 110),
        "r_elbow": (-10, 60), "r_hand": (-20, 100),
    },
    # 3. RIGHT CONTACT: right leg forward extended, left leg back bent, body leaning forward
    {
        "lean": 30, "dy": 0,
        "l_knee": (-50, 100), "l_foot": (-80, 40),
        "r_knee": (60, 80), "r_foot": (100, 160),
        "l_elbow": (-30, 80), "l_hand": (-60, 120),
        "r_elbow": (40, 60), "r_hand": (70, 100),
    },
    # 4. PASSING: right leg under body bent, left leg lifting forward, body upright
    {
        "lean": 15, "dy": -30,
        "l_knee": (-20, 60), "l_foot": (-40, -20),
        "r_knee": (20, 100), "r_foot": (30, 160),
        "l_elbow": (-10, 60), "l_hand": (-20, 100),
        "r_elbow": (20, 70), "r_hand": (40, 110),
    },
]


def make_guide(out_path, pose):
    img = Image.new("RGB", CANVAS, (255, 255, 255))
    draw = ImageDraw.Draw(img)
    draw_figure(draw, CANVAS[0]//2, 700, pose["lean"], pose["dy"], pose)
    img.save(out_path)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("character")
    parser.add_argument("--frames", type=int, default=4)
    parser.add_argument("--out", default=None)
    args = parser.parse_args()

    out_dir = args.out or f"media/polished-candidates/{args.character}/run-guides"
    os.makedirs(out_dir, exist_ok=True)
    for i in range(args.frames):
        path = os.path.join(out_dir, f"run_clean{i + 1}.png")
        make_guide(path, POSES[i % len(POSES)])
        print(f"Wrote {path}")


if __name__ == "__main__":
    main()
