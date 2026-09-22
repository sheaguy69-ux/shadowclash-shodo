#!/usr/bin/env python3
"""Generate a stage backdrop image for the arena (text-to-image, no reference).

Usage: gen_stage.py <out_png> "<prompt>" [aspect]
Shared house rules are appended to every prompt: no characters, no text, NO NEON.
"""
import os, re, sys, subprocess, pathlib

out, prompt = pathlib.Path(sys.argv[1]), sys.argv[2]
aspect = sys.argv[3] if len(sys.argv) > 3 else "16:9"

if not os.environ.get("FAL_KEY"):
    env = pathlib.Path("/Users/anthonyguy/WILDCOMIKS.2.0/.env.local")
    os.environ["FAL_KEY"] = re.search(r'FAL_KEY=["\']?([^"\'\n]+)', env.read_text()).group(1).strip()
import fal_client

HOUSE = (" Painted cel-shaded 2D game art, clean flat illustration, horizontal side-view composition, "
         "empty arena backdrop. NO characters, NO people, NO creatures, NO text, NO watermark, NO UI. "
         "NO NEON, no cyberpunk glow, no magenta or cyan light — warm natural light only.")

out.parent.mkdir(parents=True, exist_ok=True)
print(f"[stage] generating {out.name}...", file=sys.stderr)
r = fal_client.subscribe("fal-ai/flux-pro/v1.1", arguments={
    "prompt": prompt + HOUSE,
    "aspect_ratio": aspect, "num_images": 1, "output_format": "png",
    "safety_tolerance": "6", "enable_safety_checker": False,
}, with_logs=False)
subprocess.run(["curl", "-fsSL", "-o", str(out), r["images"][0]["url"]], check=True)
print(f"[stage] {out} ({out.stat().st_size} bytes)")
