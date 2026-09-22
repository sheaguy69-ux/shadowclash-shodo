#!/usr/bin/env python3
"""Generate registered candidate frames from an approved character seed via Seedance 2 i2v."""

import argparse
import hashlib
import json
import os
import re
import subprocess
import sys
from pathlib import Path


DEFAULT_ENV = Path("/Users/anthonyguy/WILDCOMIKS.2.0/.env.local")
from fal_models import MOTION_MODEL, MOTION_MODEL_KLING, i2v_clip

DEFAULT_MODEL = MOTION_MODEL   # Seedance 2 (owner order Jul 29) — see fal_models.py

# Camera lock beats render quality for sprite work: any camera drift breaks size
# registration (<=0.5% wobble is a hard gate) and a shrinking character silently
# fakes a growing weapon. Only the Kling v3 family exposes negative_prompt, so it
# is the only one that can be told NOT to move. Use it for locomotion + attack arcs.
MODEL_CHOICES = {"seedance": MOTION_MODEL, "kling": MOTION_MODEL_KLING}


def resolve_model(name):
    try:
        return MODEL_CHOICES[name]
    except KeyError:
        raise SystemExit("--model must be one of %s" % ", ".join(sorted(MODEL_CHOICES)))


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--character", required=True)
    parser.add_argument("--seed", type=Path, required=True)
    parser.add_argument("--out-dir", type=Path, required=True)
    parser.add_argument("--action", required=True)
    parser.add_argument("--identity", required=True, help="character identity/weapon constraints for the whole clip")
    parser.add_argument("--fps", type=int, default=24)
    parser.add_argument("--duration", choices=("4","5","6","7","8","9","10"), default="5")
    parser.add_argument("--resolution", choices=("480p","720p","1080p","4k"), default="1080p")
    parser.add_argument("--aspect-ratio", default="16:9")
    parser.add_argument("--env-file", type=Path, default=DEFAULT_ENV)
    parser.add_argument("--model", choices=sorted(MODEL_CHOICES), default="seedance",
                        help="kling = camera-lock (negative_prompt); use for locomotion/arcs")
    parser.add_argument("--baked-smear", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--self-test", action="store_true")
    return parser.parse_args()


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def save_json(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n")
    temporary.replace(path)


def load_key(path):
    if os.environ.get("FAL_KEY"):
        return os.environ["FAL_KEY"]
    if path.exists():
        match = re.search(r'^FAL_KEY=["\']?([^"\'\n]+)', path.read_text(), re.MULTILINE)
        if match:
            return match.group(1).strip()
    raise RuntimeError(f"FAL_KEY not found in environment or {path}")


def build_prompt(action, baked_smear, identity):
    smear = ""
    if baked_smear:
        smear = (
            " At the strike moment, bake a broad tapered blade-sweep smear into the character art: three or four "
            "translucent ghosted exposures of the same single weapon along its exact arc. The exposures are motion "
            "art, never extra weapons, and resolve back to the solid weapon after impact."
        )
    return (
        f"2D side-scroller fighting-game sprite action: {action}. Show a complete readable anticipation, strike, "
        f"impact, follow-through, and return-to-ready cycle.{smear} Keep the exact same character identity as the reference for the entire clip: "
        f"{identity}. The weapon set never changes, disappears, "
        "duplicates, bends, or leaves the canvas. Keep the complete fighter and any weapons inside frame. "
        "Hold a strict left-facing side profile; never rotate front-facing or three-quarter. Feet stay registered to "
        "one ground line except when the named action requires a jump. Locked static camera: no pan, zoom, orbit, "
        "crop, or shake. Character center and scale stay fixed. Plain pure white background, no cast shadow, no "
        "ground splash, no floor effects, no text. "
        # The palette comes from `identity` above and NOTHING else. This line used to
        # hardcode "deep-purple cel shading" for every fighter, which contradicts any
        # identity that forbids purple — Ember's lock says "FORBIDDEN: ... purple" — and
        # asking a model for purple on a green character is the likeliest source of the
        # magenta ground-splash contamination cleaned out of his jump cells at SHEET_V 293.
        "Bold black outlines, deep cel shading in the character's OWN palette named above and no other hues, "
        "smooth registered 2D sprite animation."
    )


def source_state(args, prompt):
    return {
        "action": args.action,
        "aspect_ratio": args.aspect_ratio,
        "baked_smear": args.baked_smear,
        "character": args.character,
        "duration": args.duration,
        "fps": args.fps,
        # the RESOLVED model, so the checkpoint records what actually rendered the
        # frames — a stale "seedance" here on a Kling clip makes the provenance lie
        "model": resolve_model(args.model),
        "prompt_sha256": hashlib.sha256(prompt.encode()).hexdigest(),
        "seed_sha256": digest(args.seed),
    }


def sources_changed(checkpoint, current):
    return bool(checkpoint) and any(checkpoint.get(key) != value for key, value in current.items())


def extract_frames(video, frames_dir, fps):
    frames_dir.mkdir(parents=True, exist_ok=True)
    subprocess.run([
        "ffmpeg", "-y", "-i", str(video), "-vf", f"fps={fps}",
        str(frames_dir / "f_%03d.png"),
    ], check=True, capture_output=True)
    frames = sorted(frames_dir.glob("f_*.png"))
    if not frames:
        raise RuntimeError("ffmpeg extracted zero frames")
    return frames


def build_filmstrip(video, destination):
    subprocess.run([
        "ffmpeg", "-y", "-i", str(video), "-vf", "fps=4,scale=240:-1,tile=5x4",
        "-frames:v", "1", str(destination),
    ], check=True, capture_output=True)


def run(args):
    if not args.seed.is_file():
        raise FileNotFoundError(args.seed)
    if args.fps <= 0:
        raise ValueError("fps must be positive")
    prompt = build_prompt(args.action, args.baked_smear, args.identity)
    state = source_state(args, prompt)
    plan = {
        "character": args.character,
        "seed": str(args.seed),
        "out_dir": str(args.out_dir),
        **state,
    }
    print(json.dumps(plan, indent=2))
    if args.dry_run:
        print("DRY_RUN_OK")
        return

    args.out_dir.mkdir(parents=True, exist_ok=True)
    checkpoint_path = args.out_dir / "checkpoint.json"
    checkpoint = json.loads(checkpoint_path.read_text()) if checkpoint_path.exists() else {}
    if sources_changed(checkpoint, state):
        raise RuntimeError(f"checkpoint inputs changed; use a new output directory: {args.out_dir}")
    checkpoint.update({"character": args.character, "seed": str(args.seed.resolve()), **state})
    video = args.out_dir / "clip.mp4"
    if not video.is_file() or video.stat().st_size == 0:
        result_url = checkpoint.get("result_url")
        if result_url:
            print(f"RESUME_URL {result_url}", flush=True)
        else:
            os.environ["FAL_KEY"] = load_key(args.env_file)
            import fal_client

            checkpoint["status"] = "submitting"
            save_json(checkpoint_path, checkpoint)
            # Route through i2v_clip(): the Seedance and Kling families take DIFFERENT
            # argument names (image_url vs start_image_url, resolution vs none), and
            # only Kling accepts negative_prompt/cfg_scale — the one way to FORBID
            # camera motion instead of politely asking. fal_models says do not
            # hand-roll these shapes, so we don't.
            result = i2v_clip(
                fal_client, prompt, args.seed,
                duration=args.duration,
                resolution=args.resolution,
                aspect_ratio=args.aspect_ratio,
                model=resolve_model(args.model),
            )
            result_url = result["video"]["url"]
            checkpoint.update({"result_url": result_url, "status": "result_ready"})
            save_json(checkpoint_path, checkpoint)
            print(f"RESULT_URL {result_url}", flush=True)
        subprocess.run([
            "curl", "--fail", "--silent", "--show-error", "--location",
            "--output", str(video), result_url,
        ], check=True)
        checkpoint.update({
            "result_url": result_url,
            "status": "downloaded",
            "video_bytes": video.stat().st_size,
            "video_sha256": digest(video),
        })
        save_json(checkpoint_path, checkpoint)
    else:
        print(f"SKIP_VIDEO {video}", flush=True)
        checkpoint.update({
            "video_bytes": video.stat().st_size,
            "video_sha256": digest(video),
        })

    frames = extract_frames(video, args.out_dir / "frames", args.fps)
    filmstrip = args.out_dir / "filmstrip-4fps.png"
    build_filmstrip(video, filmstrip)
    checkpoint.update({
        "filmstrip": str(filmstrip),
        "frame_count": len(frames),
        "frames_dir": str(args.out_dir / "frames"),
        "status": "complete",
    })
    save_json(checkpoint_path, checkpoint)
    print(f"DONE {args.character} {len(frames)} frames -> {args.out_dir}")


def self_test():
    plain = build_prompt("run in place", False, "test identity, one katana")
    smear = build_prompt("heavy horizontal slash", True, "test identity, one katana")
    assert "ghosted exposures" not in plain
    assert "three or four translucent ghosted exposures" in smear
    assert "test identity, one katana" in smear and "test identity, one katana" in plain
    assert "horned" not in plain
    assert not sources_changed({}, {"model": "a"})
    assert not sources_changed({"model": "a"}, {"model": "a"})
    assert sources_changed({"model": "a"}, {"model": "b"})
    print("SELF_TEST_OK")


def main():
    args = parse_args()
    if args.self_test:
        self_test()
        return
    run(args)


if __name__ == "__main__":
    try:
        main()
    except (FileNotFoundError, RuntimeError, ValueError, subprocess.CalledProcessError) as error:
        sys.exit(f"ERROR: {error}")
