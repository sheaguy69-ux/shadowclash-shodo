#!/usr/bin/env python3
"""Completion-clip method (owner's law): an ACCEPTED raw static is frame 1,
Seedance 2 i2v completes the motion. No still-edit seed step — the start pose is canon.

Usage: gen_complete_clip.py <start_png> <out_dir> "<i2v_prompt>"
Writes <out_dir>/clip.mp4 + <out_dir>/frames/f_NNN.png (24fps). ~$0.10.
"""
import os, sys, subprocess, pathlib, re

start, out_dir, prompt = sys.argv[1], pathlib.Path(sys.argv[2]), sys.argv[3]
if not os.environ.get("FAL_KEY"):
    env = pathlib.Path("/Users/anthonyguy/WILDCOMIKS.2.0/.env.local")
    os.environ["FAL_KEY"] = re.search(r'FAL_KEY=["\']?([^"\'\n]+)', env.read_text()).group(1).strip()
import fal_client
from fal_models import i2v_clip

out_dir.mkdir(parents=True, exist_ok=True)
print(f"[{out_dir.name}] Seedance 2 i2v (~$0.15, ~1-3 min)...", file=sys.stderr)
rv = i2v_clip(fal_client, prompt, start, duration="5", resolution="1080p", aspect_ratio="9:16")
mp4 = out_dir / "clip.mp4"
subprocess.run(["curl", "-sSL", "-o", str(mp4), rv["video"]["url"]], check=True)
frames = out_dir / "frames"; frames.mkdir(exist_ok=True)
subprocess.run(["ffmpeg", "-y", "-i", str(mp4), "-vf", "fps=24", str(frames / "f_%03d.png")],
               check=True, capture_output=True)
print(f"[{out_dir.name}] {mp4.stat().st_size} bytes, {len(list(frames.glob('f_*.png')))} frames")
