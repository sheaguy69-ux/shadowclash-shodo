#!/usr/bin/env python3
"""Generate explicit running-cycle frames with detailed pose prompts.

The neutral-guide + bust-ref approach collapses to standing poses for run cycles.
This script uses explicit per-frame pose descriptions to force leg alternation.

Usage:
    python3 tools/sprites/gen_run_frames.py <character> [--frames 4] [--seed 55550718]
"""
import argparse, os, re, subprocess, sys, pathlib
import numpy as np
from PIL import Image

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("character")
    parser.add_argument("--frames", type=int, default=8)
    parser.add_argument("--seed", type=int, default=55550718)
    parser.add_argument("--identity-file", default=None)
    parser.add_argument("--ref", default=None, help="reference image (default: TRUE canon ref from vault)")
    args = parser.parse_args()

    char = args.character
    base = pathlib.Path(f"media/polished-candidates/{char}")
    env = pathlib.Path("/Users/anthonyguy/WILDCOMIKS.2.0/.env.local")
    os.environ["FAL_KEY"] = re.search(r'^FAL_KEY=["\']?([^"\'\n]+)', env.read_text(), re.M).group(1).strip()
    import fal_client

    # OWNER CANON RESET 18:10 — reference is the TRUE colorful lineup crop, full body.
    ref_path = pathlib.Path(args.ref) if args.ref else pathlib.Path(
        f"/Users/anthonyguy/OB-LOCAL_BRAIN/ShadowClash-Second-Brain/assets/{char}-true-ref.png")
    ref_url = fal_client.upload_file(str(ref_path))

    if args.identity_file:
        identity = pathlib.Path(args.identity_file).read_text().strip()
    else:
        identity = f"ShadowClash {char} fighter, consistent with the reference design"

    out = base / "run-frames"
    out.mkdir(exist_ok=True)

    # 8-phase Richard Williams run cycle (owner ANIMATION SPEC: 8 frames @12fps,
    # contact/down/pass/up on BOTH legs). Order is the loop order.
    pose_prompts = [
        "RUN PHASE 1 of 8, CONTACT left: left foot planted forward heel-first, right leg trailing bent behind, body leaning forward, right arm swung forward left arm back",
        "RUN PHASE 2 of 8, DOWN left (recoil): weight fully on bent left leg, body at its LOWEST point, head dipped, right foot lifting off ground behind, arms mid-swing",
        "RUN PHASE 3 of 8, PASSING left: right leg swinging under and past the body with knee bent, left leg pushing back, body upright, arms passing at sides",
        "RUN PHASE 4 of 8, UP left (push-off): left toes pushing off ground, body at its HIGHEST point rising, right knee driving up and forward, left arm swung forward",
        "RUN PHASE 5 of 8, CONTACT right: right foot planted forward heel-first, left leg trailing bent behind, body leaning forward, left arm swung forward right arm back",
        "RUN PHASE 6 of 8, DOWN right (recoil): weight fully on bent right leg, body at its LOWEST point, head dipped, left foot lifting off ground behind, arms mid-swing",
        "RUN PHASE 7 of 8, PASSING right: left leg swinging under and past the body with knee bent, right leg pushing back, body upright, arms passing at sides",
        "RUN PHASE 8 of 8, UP right (push-off): right toes pushing off ground, body at its HIGHEST point rising, left knee driving up and forward, right arm swung forward",
    ]

    for i in range(args.frames):
        pose = pose_prompts[i % len(pose_prompts)]
        out_path = out / f"run_clean{i+1}.png"
        prompt = (
            f"Generate a {char} running animation frame. {pose}. "
            f"The character: {identity}. "
            "Crisp black outlines, polished cel shading, plain pure white background, no shadow, no text, no border. "
            "Side profile view, facing right. Full body visible with margin on all sides."
        )
        print(f"Generating {out_path.name}: {pose[:60]}...")
        r = fal_client.subscribe("fal-ai/flux-pro/kontext/multi", arguments={
            "prompt": prompt,
            "image_urls": [ref_url],
            "num_images": 1, "output_format": "png", "safety_tolerance": "6",
            "aspect_ratio": "3:4", "seed": args.seed + i * 100,
            "guidance_scale": 4.5, "enhance_prompt": False,
        }, with_logs=False)
        subprocess.run(["curl", "-fsSL", "-o", str(out_path), r["images"][0]["url"]], check=True)
        print(f"OK {out_path.name}")

    print(f"DONE {char} {args.frames} run frames -> {out}")


if __name__ == "__main__":
    main()
