#!/usr/bin/env python3
"""Generate a character-select BUST portrait (assets/ninjas/<name>.png).

Matches the existing six: head-and-shoulders chibi, bold black outlines,
flat cel shading, plain white background, ~791x851. The select screen falls
back to a procedural doll head when this file is missing.

Usage: gen_portrait.py <name> "<identity sentence>"
"""
import os, re, sys, subprocess, pathlib
from PIL import Image

name, identity = sys.argv[1], sys.argv[2]
REPO = pathlib.Path(__file__).resolve().parent.parent.parent
out = REPO / "web" / "assets" / "ninjas" / f"{name}.png"

if not os.environ.get("FAL_KEY"):
    env = pathlib.Path("/Users/anthonyguy/WILDCOMIKS.2.0/.env.local")
    os.environ["FAL_KEY"] = re.search(r'FAL_KEY=["\']?([^"\'\n]+)', env.read_text()).group(1).strip()
import fal_client

HOUSE = (" Chibi character BUST PORTRAIT — head and shoulders only, large head, "
         "facing the viewer at a three-quarter angle, centered, cropped at the chest. "
         "Bold black outlines, flat cel shading, plain solid pure white background. "
         "ONE character only, no weapons raised, no text, no watermark, no border, no UI. "
         "NO NEON, no cyberpunk glow, no magenta or cyan light.")

out.parent.mkdir(parents=True, exist_ok=True)
print(f"[portrait] {name}...", file=sys.stderr)
r = fal_client.subscribe("fal-ai/flux-pro/v1.1", arguments={
    "prompt": identity + HOUSE,
    "aspect_ratio": "1:1", "num_images": 1, "output_format": "png",
    "safety_tolerance": "6", "enable_safety_checker": False,
}, with_logs=False)
subprocess.run(["curl", "-fsSL", "-o", str(out), r["images"][0]["url"]], check=True)
# match the existing portraits' canvas so the select-card layout stays identical
Image.open(out).convert("RGB").resize((791, 851), Image.LANCZOS).save(out)
print(f"[portrait] {out} ({out.stat().st_size} bytes)")
