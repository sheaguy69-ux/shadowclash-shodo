#!/usr/bin/env python3
"""Generate explicit attack animation frames with detailed pose prompts.

Attack frames must show dynamic motion — lunge, slash, recoil — not standing poses.
This script uses per-frame pose descriptions to force variety.

Usage:
    python3 tools/sprites/gen_attack_frames.py <character> [--seed 55550718]
"""
import argparse, os, re, subprocess, sys, pathlib
from PIL import Image

ATTACK_POSES = {
    "attack_body1": "lunging forward stab with lead weapon arm extended, back leg pushing off, body leaning into the strike",
    "attack_body2": "wide horizontal slash with weapon arm sweeping across the body, torso twisting, weight shifting to front foot",
    "attack_body3": "overhead downward strike with weapon arm raised high then chopping down, body dropping slightly, follow-through",
    "attack_body4": "spinning attack with body rotating, weapon arm extended in a circular arc, one leg pivoting",
    "attack_body5": "low sweeping attack with body crouched, weapon arm near the ground, opposite arm for balance",
    "attack_body6": "finishing thrust with weapon arm fully extended forward, body stretched, back leg trailing, maximum reach",
    "heavy_i1": "heavy wind-up with weapon pulled back behind the body, torso twisted, anticipation pose",
    "heavy_i2": "heavy overhead strike with weapon arm swinging down, body dropping, full commitment",
    "heavy_i3": "heavy rising uppercut-style slash with weapon arm sweeping upward, body extending, back leg pushing",
    "heavy_i4": "heavy spinning whirlwind attack with body rotating, weapon arm outstretched, momentum",
    "heavy_i5": "heavy finishing slam with weapon arm chopping down, body bent forward, follow-through to the ground",
}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("character")
    parser.add_argument("--seed", type=int, default=55550718)
    parser.add_argument("--identity-file", default=None)
    parser.add_argument("--frames", default=None, help="comma-separated frame names")
    args = parser.parse_args()

    char = args.character
    base = pathlib.Path(f"media/polished-candidates/{char}")
    env = pathlib.Path("/Users/anthonyguy/WILDCOMIKS.2.0/.env.local")
    os.environ["FAL_KEY"] = re.search(r'^FAL_KEY=["\']?([^"\'\n]+)', env.read_text(), re.M).group(1).strip()
    import fal_client

    ref_path = base / "bust-ref.png"
    if not ref_path.exists():
        ref = Image.open(f"media/polished-candidates/corrected-refs/final/{char}-owner-corrected-ref.png")
        ref.crop((0, 0, ref.width, int(ref.height * 0.48))).save(ref_path)
    ref_url = fal_client.upload_file(str(ref_path))

    if args.identity_file:
        identity = pathlib.Path(args.identity_file).read_text().strip()
    else:
        identity = f"ShadowClash {char} fighter, consistent with the reference design"

    out = base / "attack-frames"
    out.mkdir(exist_ok=True)

    if args.frames:
        frame_list = args.frames.split(",")
    else:
        frame_list = sorted(ATTACK_POSES.keys())

    for i, frame in enumerate(frame_list):
        pose = ATTACK_POSES.get(frame, f"dynamic attack pose for {frame}")
        out_path = out / f"{frame}.png"
        prompt = (
            f"Generate a {char} attack animation frame. {pose}. "
            f"The character: {identity}. "
            "Crisp black outlines, polished cel shading, plain pure white background, no shadow, no text, no border. "
            "Side profile view, facing right. Full body visible with margin on all sides."
        )
        print(f"Generating {frame}: {pose[:60]}...")
        r = fal_client.subscribe("fal-ai/flux-pro/kontext/multi", arguments={
            "prompt": prompt,
            "image_urls": [ref_url],
            "num_images": 1, "output_format": "png", "safety_tolerance": "6",
            "aspect_ratio": "3:4", "seed": args.seed + i * 100,
            "guidance_scale": 4.5, "enhance_prompt": False,
        }, with_logs=False)
        subprocess.run(["curl", "-fsSL", "-o", str(out_path), r["images"][0]["url"]], check=True)
        print(f"OK {frame}")

    print(f"DONE {char} {len(frame_list)} attack frames -> {out}")


if __name__ == "__main__":
    main()
