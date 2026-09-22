#!/usr/bin/env python3
"""True-canon statics + attacks generator (18:10 OWNER CANON RESET, Claude 23:05 dispatch).

K3 lane ONLY: true-color STATICS + ATTACKS wave-2 fighters (mokurai/exile).
Run cycles are NOT generated here (Claude's i2v lane, owner A/B pending).

- Identity: media/polished-candidates/<char>/identity-true.txt (REQUIRED —
  states where the accent color is ALLOWED and where FORBIDDEN).
- Ref image: media/polished-candidates/true-refs/<char>-true-ref.png ONLY
  (old corrected-refs are DEAD).
- Output: media/polished-candidates/<char>/truecolor-raw/<cell>.png
  Claude gates these raws, then packs. This script never touches web/.

Usage:
    python3 tools/sprites/gen_truecolor.py <character> [--group statics|attacks|all]
        [--only cell1,cell2] [--force] [--seed-base N] [--budget-usd 8.00]
"""
import argparse, json, os, re, subprocess, sys, time, pathlib

COST_PER_GEN = 0.04

ATTACK_POSES = {
    "attack_body1": "TSUKI thrust attack: weapon arm driving STRAIGHT FORWARD toward the enemy, weapon at FULL EXTENSION pointing at the target, back leg pushing off, hips rotated into the thrust, body lunging forward — the weapon visibly reaches toward the enemy",
    "attack_body2": "KESAGIRI diagonal cut: blade sweeping diagonally from shoulder to opposite hip, torso twisting, weapon arm at FULL EXTENSION through the cut, weight shifting to the front foot, the blade's arc clearly crossing the space in front of the body",
    "attack_body3": "KIRIOROSHI overhead chop: weapon raised high then chopped straight down at FULL EXTENSION, body dropping into the strike, follow-through toward the ground",
    "attack_body4": "spinning cut: body rotating through a full turn, weapon arm fully extended in a wide circular arc around the body, one leg pivoting, the weapon sweeping the whole circle",
    "attack_body5": "YOKOGIRI low horizontal sweep: body crouched low, weapon sweeping horizontally at ground height at FULL EXTENSION, opposite arm out for balance",
    "attack_body6": "finishing thrust: weapon at MAXIMUM forward extension toward the enemy, arm locked straight, body stretched into the lunge, back leg trailing — the longest possible reach",
    "heavy_i1": "heavy wind-up: weapon pulled far back behind the body, torso twisted in deep anticipation, fully coiled — the clear tell before the big hit",
    "heavy_i2": "heavy overhead slam: weapon swinging down at FULL EXTENSION with the whole body behind it, body dropping, full commitment — the blade visibly descending through the target",
    "heavy_i3": "KIRI-AGE rising cut: weapon sweeping UPWARD at full extension from low to high, body extending tall, back leg pushing — the blade visibly climbing through the enemy",
    "heavy_i4": "heavy spinning whirlwind: body rotating with the weapon fully outstretched, momentum carrying the spin, the weapon sweeping a wide full circle",
    "heavy_i5": "heavy finishing slam: weapon chopped down at FULL EXTENSION to the ground line, body bent forward over the strike, follow-through to the floor",
}

STATIC_POSES = {
    "idle": "COILED combat-ready idle stance: knees bent, hips low, weight on the balls of the feet, weapon held ready, stillness-before-explosion tension, alert, NOT standing straight",
    "idle2": "alternate coiled idle stance: same low ready crouch with weight shifted to the back foot, scarf and cloth swaying, relaxed but alert, NOT standing straight",
    "jump": "leaping upward, knees tucked high, body ascending, scarf trailing downward — her RIGHT hand holds her ONLY curved sickle, her LEFT hand grips the chain with its round smooth iron ball (NO spikes), chain links clearly visible hanging in a curve — exactly ONE blade in the image",
    "fall": "falling downward, legs extended below the body, arms slightly out for balance, scarf and cloth flowing UPWARD",
    "kneel": "kneeling on one knee, other foot planted forward, head up alert, ready to spring",
    "roll": "MID-SOMERSAULT forward roll: body curled into a TIGHT BALL, UPSIDE-DOWN, knees pulled hard to the chest, arms wrapped around the shins, back rounded like a wheel — clearly tumbling, NOT crouching, NOT standing",
    "wallslide": "sliding down an INVISIBLE wall, back arched against empty air as if pressed to a surface, one palm flat against nothing, feet braced, knees bent — NO wall visible, plain pure white background only",
    "block": "defensive guard stance, weapon and forearms raised to block, legs braced wide, hips low, leaning slightly back",
    "hurt": "REELING from an impact: body tilted BACKWARD off balance, one leg kicked forward, arms flung upward, weapon swinging up with the momentum, hood and scarf thrown back — clearly knocked away, NOT braced, NOT planted",
    "light1": "quick snappy jab attack, small fast strike with the lead hand, minimal wind-up",
    "light2": "follow-up strike, reverse swing across the body, torso rotating",
    "light3": "combo finisher, bigger committed swing with full weight behind the strike",
    "ksweep": "low crouched sweep kick, one leg extended along the ground in a circular sweep, hands supporting the body",
    "kpush": "push kick, sole of the foot thrusting forward at chest height, body leaning back for balance",
    "kheel": "heel kick, leg raised high overhead then chopping down with the heel, body stretched tall",
    "kstomp": "powerful stomp, foot driving downward into the ground, body weight dropping onto it",
    "special1": "signature special technique wind-up, coiled anticipation pose, weapon drawn back, energy gathering",
    "special2": "signature special technique release, explosive committed strike, full extension",
    "flying_kick1": "crouched launch pose, coiling down low before the leap, arms pulled back",
    "flying_kick2": "explosive leap upward, body rising, legs tucking under, arms swinging up",
    "flying_kick3": "airborne kick extension, kicking leg extending forward, body going horizontal in midair",
    "flying_kick4": "FULL flying side-kick extension, kicking leg fully extended forward, body horizontal in midair, other leg tucked",
    "flying_kick5": "held kick extension while descending, kicking leg still out, body starting to drop",
    "flying_kick6": "landing recovery, kicking leg coming down, body returning upright, knees absorbing",
}

BASE_STATICS = ["idle", "idle2", "jump", "fall", "kneel", "roll", "wallslide",
                "block", "hurt", "light1", "light2", "light3"]
ATTACKS = ["attack_body1", "attack_body2", "attack_body3", "attack_body4",
           "attack_body5", "attack_body6", "heavy_i1", "heavy_i2", "heavy_i3",
           "heavy_i4", "heavy_i5"]

# Live-cell map per fighter (from web/assets/sprites/<char>.json, live groups only).
LIVE = {
    "mokurai":   {"kicks": ["ksweep", "kpush", "kheel", "kstomp"],
                 "specials": ["special1", "special2"]},
    "exile": {"kicks": ["ksweep", "kpush", "kheel", "kstomp"],
                 "specials": ["special1", "special2"]},
}


def cell_list(char, group):
    statics = BASE_STATICS + LIVE[char]["kicks"] + LIVE[char]["specials"]
    if group == "statics":
        return statics
    if group == "attacks":
        return ATTACKS
    return statics + ATTACKS


def white_blob_suspect(path):
    """Interior near-white components (not touching border) > 1.5% of image area.
    Border-touching white is the background; interior blobs are the known
    seed-family paint defect (Claude 21:55). numpy-only flood fill."""
    import numpy as np
    from PIL import Image
    a = np.array(Image.open(path).convert("RGB"))
    white = (a > 240).all(axis=2)
    h, w = white.shape
    bg = np.zeros_like(white)
    stack = [(y, x) for y in range(h) for x in (0, w - 1) if white[y, x]]
    stack += [(y, x) for y in (0, h - 1) for x in range(w) if white[y, x]]
    while stack:
        y, x = stack.pop()
        if bg[y, x]:
            continue
        bg[y, x] = True
        for dy, dx in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            ny, nx = y + dy, x + dx
            if 0 <= ny < h and 0 <= nx < w and white[ny, nx] and not bg[ny, nx]:
                stack.append((ny, nx))
    interior = white & ~bg
    return interior.sum() > 0.015 * h * w


def main():
    p = argparse.ArgumentParser()
    p.add_argument("character", choices=sorted(LIVE))
    p.add_argument("--group", choices=["statics", "attacks", "all"], default="all")
    p.add_argument("--only", default=None, help="comma-separated cell names")
    p.add_argument("--force", action="store_true")
    p.add_argument("--seed-base", type=int, default=93300118)
    p.add_argument("--budget-usd", type=float, default=8.00)
    args = p.parse_args()

    char = args.character
    base = pathlib.Path(f"media/polished-candidates/{char}")
    ident_path = base / "identity-true.txt"
    if not ident_path.exists():
        sys.exit(f"ERROR: {ident_path} missing — write the 18:10 identity first")
    identity = ident_path.read_text().strip()

    ref_path = pathlib.Path(f"media/polished-candidates/true-refs/{char}-true-ref.png")
    if not ref_path.exists():
        sys.exit(f"ERROR: true ref missing: {ref_path}")

    env = pathlib.Path("/Users/anthonyguy/WILDCOMIKS.2.0/.env.local")
    os.environ["FAL_KEY"] = re.search(r'^FAL_KEY=["\']?([^"\'\n]+)', env.read_text(), re.M).group(1).strip()
    import fal_client

    out = base / "truecolor-raw"
    out.mkdir(exist_ok=True)
    manifest_path = out / "manifest.json"
    manifest = json.loads(manifest_path.read_text()) if manifest_path.exists() else {}

    cells = args.only.split(",") if args.only else cell_list(char, args.group)
    poses = {**STATIC_POSES, **ATTACK_POSES}

    ref_url = fal_client.upload_file(str(ref_path))
    print(f"ref uploaded: {ref_path.name}")

    done = sum(1 for c in cells if (out / f"{c}.png").exists() and not args.force)
    gens = len(cells) - done
    print(f"{char}: {len(cells)} cells, {done} cached, {gens} to generate (~${gens * COST_PER_GEN:.2f})")

    spend = 0.0
    for i, cell in enumerate(cells):
        out_path = out / f"{cell}.png"
        if out_path.exists() and not args.force:
            continue
        if spend + COST_PER_GEN > args.budget_usd:
            sys.exit(f"BUDGET STOP at ${spend:.2f} — rerun to resume")
        pose = poses.get(cell)
        if not pose:
            sys.exit(f"ERROR: no pose prompt for cell {cell}")
        seed = args.seed_base + i * 137
        prompt = (
            f"Generate a {char} character animation frame for a 2D fighting game. {pose}. "
            f"The character: {identity}. "
            "Crisp black outlines, polished cel shading, plain pure white background, "
            "no shadow, no text, no border. Side profile view, facing right. "
            "Full body visible with margin on all sides."
        )
        print(f"[{cell}] seed {seed} ...", flush=True)
        r = fal_client.subscribe("fal-ai/flux-pro/kontext/multi", arguments={
            "prompt": prompt,
            "image_urls": [ref_url],
            "num_images": 1, "output_format": "png", "safety_tolerance": "6",
            "aspect_ratio": "3:4", "seed": seed,
            "guidance_scale": 4.5, "enhance_prompt": False,
        }, with_logs=False)
        url = r["images"][0]["url"]
        print(f"RESULT_URL {url}", flush=True)  # printed BEFORE download — never lose a paid gen
        subprocess.run(["curl", "-fsSL", "-o", str(out_path), url], check=True)
        spend += COST_PER_GEN
        warn = " WHITE-BLOB-SUSPECT" if white_blob_suspect(out_path) else ""
        print(f"OK {cell} (${spend:.2f}){warn}", flush=True)
        manifest[cell] = {"status": "done", "seed": seed, "url": url,
                          "blob_suspect": bool(warn), "ts": time.time()}
        manifest_path.write_text(json.dumps(manifest, indent=1))

    print(f"DONE {char} group={args.group} spend=${spend:.2f} -> {out}")


if __name__ == "__main__":
    main()
