#!/usr/bin/env python3
"""Generate resumable polished sprite candidates from identity and pose references."""

import argparse
import hashlib
import json
import os
import re
import subprocess
import sys
import tempfile
from pathlib import Path

from PIL import Image, ImageOps, ImageStat


DEFAULT_MODEL = "fal-ai/flux-pro/kontext/multi"
DEFAULT_ENV = Path("/Users/anthonyguy/WILDCOMIKS.2.0/.env.local")
SUPPORTED_MODELS = (
    "fal-ai/flux-pro/kontext/multi",
    "fal-ai/nano-banana/edit",
    "fal-ai/flux/dev/image-to-image",
)
SMEAR_FRAME_SOURCES = {
    "heavy_i_smear": "heavy_i3",
    "special_smear": "special2",
}
SMEAR_FRAME_AFTER = {
    "heavy_i_smear": "heavy_i2",
    "special_smear": "special1",
}


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--character", required=True)
    parser.add_argument("--identity-ref", type=Path, required=True)
    parser.add_argument("--identity-description", required=True)
    parser.add_argument("--sheet", type=Path)
    parser.add_argument("--manifest", type=Path)
    parser.add_argument("--frames", help="Comma-separated frame names; defaults to every manifest frame")
    parser.add_argument("--out-root", type=Path, default=Path("media/polished-candidates"))
    parser.add_argument("--env-file", type=Path, default=DEFAULT_ENV)
    parser.add_argument("--seed", type=int, default=17072026)
    parser.add_argument("--model", choices=SUPPORTED_MODELS, default=DEFAULT_MODEL)
    parser.add_argument("--strength", type=float, default=0.45)
    parser.add_argument("--max-attempts", type=int, default=3)
    parser.add_argument("--force", action="store_true")
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


def load_manifest(path):
    value = json.loads(path.read_text())
    required = {"frameW", "frameH", "cols", "frames"}
    missing = required - value.keys()
    if missing:
        raise ValueError(f"manifest missing: {', '.join(sorted(missing))}")
    return value


def select_frames(manifest, requested):
    names = requested.split(",") if requested else list(manifest["frames"])
    names = [name.strip() for name in names if name.strip()]
    available = set(manifest["frames"]) | {
        name for name, source in SMEAR_FRAME_SOURCES.items() if source in manifest["frames"]
    }
    unknown = [name for name in names if name not in available]
    if unknown:
        raise ValueError(f"unknown frames: {', '.join(unknown)}")
    if not requested:
        for name, after in SMEAR_FRAME_AFTER.items():
            if name in available and after in names:
                names.insert(names.index(after) + 1, name)
    return names


def frame_source(name):
    return SMEAR_FRAME_SOURCES.get(name, name)


def extract_guides(sheet_path, manifest, names, guide_dir):
    sheet = Image.open(sheet_path).convert("RGBA")
    frame_width = int(manifest["frameW"])
    frame_height = int(manifest["frameH"])
    expected = (frame_width * int(manifest["cols"]), frame_height)
    if sheet.size != expected:
        raise ValueError(f"sheet size {sheet.size} does not match manifest {expected}")
    guide_dir.mkdir(parents=True, exist_ok=True)
    outputs = {}
    for name in names:
        index = int(manifest["frames"][frame_source(name)])
        destination = guide_dir / f"{name}.png"
        sheet.crop((index * frame_width, 0, (index + 1) * frame_width, frame_height)).save(destination)
        outputs[name] = destination
    return outputs


def prepare_model_guides(guides, destination_dir, canvas_size=(880, 1184)):
    destination_dir.mkdir(parents=True, exist_ok=True)
    outputs = {}
    for name, source_path in guides.items():
        source = Image.open(source_path).convert("RGBA")
        bounds = source.getbbox()
        if not bounds:
            raise ValueError(f"empty guide: {name}")
        source = source.crop(bounds)
        alpha = source.getchannel("A")
        # owner 2026-07-18: guides are SILHOUETTES ONLY — old-design interior detail
        # (capes, garments, weapons) was bleeding into every generation. Pose transfers, appearance cannot.
        # 2026-07-18b: keep ONLY the largest connected component — old cells carry detached
        # debris (neighbor-cell bleed) whose silhouette the model renders as floating shuriken.
        import numpy as np
        import collections
        mask = (np.array(alpha) > 40).astype(np.uint8)
        lbl = np.zeros_like(mask, dtype=np.int32); cur = 0
        H, W = mask.shape
        for sy in range(H):
            for sx in range(W):
                if mask[sy, sx] and not lbl[sy, sx]:
                    cur += 1
                    q = collections.deque([(sy, sx)]); lbl[sy, sx] = cur
                    while q:
                        y, x = q.popleft()
                        for ny, nx in ((y-1,x),(y+1,x),(y,x-1),(y,x+1)):
                            if 0 <= ny < H and 0 <= nx < W and mask[ny, nx] and not lbl[ny, nx]:
                                lbl[ny, nx] = cur; q.append((ny, nx))
        if cur > 1:
            sizes = np.bincount(lbl.ravel())[1:]
            keep = int(np.argmax(sizes)) + 1
            alpha = Image.fromarray(np.where(lbl == keep, np.array(alpha), 0).astype("uint8"))
        black = Image.new("L", source.size, 0)
        source = Image.merge("RGBA", (black, black, black, alpha))
        scale = min((canvas_size[0] * 0.86) / source.width, (canvas_size[1] * 0.86) / source.height)
        size = (max(1, round(source.width * scale)), max(1, round(source.height * scale)))
        source = source.resize(size, Image.Resampling.NEAREST)
        canvas = Image.new("RGBA", canvas_size, "white")
        position = ((canvas_size[0] - size[0]) // 2, (canvas_size[1] - size[1]) // 2)
        canvas.alpha_composite(source, position)
        destination = destination_dir / f"{name}.png"
        canvas.convert("RGB").save(destination)
        outputs[name] = destination
    return outputs


def load_key(path):
    if os.environ.get("FAL_KEY"):
        return os.environ["FAL_KEY"]
    if path.exists():
        match = re.search(r'^FAL_KEY=["\']?([^"\'\n]+)', path.read_text(), re.MULTILINE)
        if match:
            return match.group(1).strip()
    raise RuntimeError(f"FAL_KEY not found in environment or {path}")


def inspect_image(path, expected_size=None):
    with Image.open(path) as image:
        size = image.size
        mean = ImageStat.Stat(image.convert("L")).mean[0] / 255.0
    valid = 0.2 < mean < 0.995 and (expected_size is None or size == expected_size)
    return valid, size, mean


def prompt_for(frame, description, model):
    smear = (
        " This is a motion-blur smear frame: keep the body mid-swing and render the single moving blade as a "
        "swept tapered arc of 3-4 ghosted blade positions, extreme action smear, cel-animation smear technique. "
        "The ghosted positions are exposures of the same one blade, not extra weapons. This baked-in blade arc is "
        "the sole intentional exception to the frozen blade geometry; it is drawn into the sprite, not a separate effect."
        if frame in SMEAR_FRAME_SOURCES else ""
    )
    if model == "fal-ai/flux/dev/image-to-image":
        return (
            f"Polish this exact {frame} fighting-game sprite in place. Keep the complete source pose geometry, "
            "facing direction, torso angle, hands, legs, weapon angle and path, character scale, center placement, "
            "and foot baseline unchanged. Preserve the action silhouette. The source colors were deliberately "
            "neutralized and are not costume colors. Replace them fully while upgrading the character design to "
            f"{description}. Preserve the exact weapon count stated in that description. Keep exactly one fighter "
            "with every weapon fully visible. Crisp black outlines, refined cel shading, readable full body, plain "
            f"pure white background, no shadow, no text, no border, no scenery.{smear}"
        )
    return (
        f"EDIT IMAGE #1 IN PLACE for the {frame} animation frame. IMAGE #1 IS THE ONLY GEOMETRY AUTHORITY. "
        "IMAGE #2 IS ONLY THE IDENTITY, PALETTE, AND MATERIAL REFERENCE. If the images conflict, geometry from #1 "
        "always wins. Never copy or drift toward #2's pose. Keep #1's pose geometry EXACTLY unchanged: "
        "same facing direction, torso angle, hand positions, leg positions, airborne/crouched state, weapon angle "
        "and path, action energy, character scale, center placement, and foot baseline. Do not turn #1 into an idle "
        "or standing pose. #1's colors were deliberately neutralized and are not costume colors. Replace them fully "
        "with #2's near-black/deep-shadow palette and character design. #2 is the ONLY identity reference: "
        f"{description}. Transfer #2's exact face, eyes, outfit layers, palette, materials, and character identity "
        "onto #1's unchanged action without transferring #2's stance. Preserve the exact weapon count stated in "
        "the identity description. Exactly ONE fighter; no extra weapon and no detached body parts. "
        "Keep the complete fighter and weapon inside the canvas. Crisp black outlines, polished cel shading, "
        f"highly readable silhouette, plain pure white background, no shadow, no text, no border, no scenery.{smear}"
    )


def model_arguments(model, prompt, image_urls, seed, strength):
    common = {
        "prompt": prompt,
        "image_urls": image_urls,
        "num_images": 1,
        "output_format": "png",
        "safety_tolerance": "6",
        "aspect_ratio": "3:4",
        "seed": seed,
    }
    if model == "fal-ai/flux-pro/kontext/multi":
        common.update({"guidance_scale": 4.0, "enhance_prompt": False})
    elif model == "fal-ai/nano-banana/edit":
        common["limit_generations"] = True
    elif model == "fal-ai/flux/dev/image-to-image":
        return {
            "prompt": prompt,
            "image_url": image_urls[0],
            "strength": strength,
            "num_inference_steps": 40,
            "guidance_scale": 4.0,
            "seed": seed,
            "num_images": 1,
            "enable_safety_checker": True,
            "output_format": "png",
            "acceleration": "none",
        }
    else:
        raise ValueError(f"unsupported model: {model}")
    return common


def completed(entry, output, expected_size):
    if not entry or entry.get("status") != "complete" or not output.exists():
        return False
    valid, size, _ = inspect_image(output, expected_size)
    return valid and list(size) == entry.get("size")


def checkpoint_sources_changed(checkpoint, source_state):
    return bool(checkpoint) and any(checkpoint.get(key) != value for key, value in source_state.items())


def run_generation(args, manifest, names, guides, out_dir):
    os.environ["FAL_KEY"] = load_key(args.env_file)
    import fal_client

    checkpoint_path = out_dir / "checkpoint.json"
    checkpoint = json.loads(checkpoint_path.read_text()) if checkpoint_path.exists() else {}
    source_state = {
        "model": args.model,
        "identity_sha256": digest(args.identity_ref),
        "sheet_sha256": digest(args.sheet),
        "manifest_sha256": digest(args.manifest),
    }
    if checkpoint_sources_changed(checkpoint, source_state):
        checkpoint["frames"] = {}
        checkpoint.pop("output_size", None)
    checkpoint.update({
        "character": args.character,
        "identity_ref": str(args.identity_ref.resolve()),
        "sheet": str(args.sheet.resolve()),
        "manifest": str(args.manifest.resolve()),
        "requested_frames": names,
        **source_state,
    })
    checkpoint.setdefault("frames", {})
    expected_size = tuple(checkpoint["output_size"]) if checkpoint.get("output_size") else None
    identity_url = fal_client.upload_file(str(args.identity_ref))
    raw_dir = out_dir / "raw"
    raw_dir.mkdir(parents=True, exist_ok=True)
    save_json(checkpoint_path, checkpoint)

    for offset, name in enumerate(names):
        output = raw_dir / f"{name}.png"
        existing = checkpoint["frames"].get(name)
        if not args.force and completed(existing, output, expected_size):
            print(f"SKIP {name} checkpoint complete", flush=True)
            continue
        guide_url = fal_client.upload_file(str(guides[name]))
        source = frame_source(name)
        frame_entry = {"status": "running", "index": manifest["frames"][source], "source": source, "attempts": []}
        checkpoint["frames"][name] = frame_entry
        save_json(checkpoint_path, checkpoint)
        for attempt in range(1, args.max_attempts + 1):
            seed = args.seed + int(manifest["frames"][source]) * 100 + attempt
            result = fal_client.subscribe(args.model, arguments=model_arguments(
                args.model,
                prompt_for(name, args.identity_description, args.model),
                [guide_url, identity_url],
                seed,
                args.strength,
            ), with_logs=False)
            result_url = result["images"][0]["url"]
            print(f"RESULT_URL {name} {result_url}", flush=True)
            subprocess.run([
                "curl", "--fail", "--silent", "--show-error", "--location",
                "--output", str(output), result_url,
            ], check=True)
            valid, size, mean = inspect_image(output, expected_size)
            frame_entry["attempts"].append({
                "attempt": attempt,
                "seed": seed,
                "result_url": result_url,
                "size": list(size),
                "mean_luminance": round(mean, 6),
                "valid": valid,
            })
            if expected_size is None and 0.2 < mean < 0.995:
                expected_size = size
                checkpoint["output_size"] = list(size)
                valid = True
                frame_entry["attempts"][-1]["valid"] = True
            if valid:
                frame_entry.update({
                    "status": "complete",
                    "output": str(output),
                    "size": list(size),
                    "mean_luminance": round(mean, 6),
                    "sha256": digest(output),
                })
                save_json(checkpoint_path, checkpoint)
                print(f"OK {name} {size[0]}x{size[1]} mean={mean:.4f}", flush=True)
                break
            save_json(checkpoint_path, checkpoint)
        else:
            frame_entry["status"] = "failed"
            save_json(checkpoint_path, checkpoint)
            raise RuntimeError(f"{name} failed validation after {args.max_attempts} attempts")
    print(f"DONE {args.character} {len(names)} frames -> {out_dir}")


def self_test():
    with tempfile.TemporaryDirectory() as temporary:
        root = Path(temporary)
        manifest = {"frameW": 8, "frameH": 10, "cols": 2, "frames": {"idle": 0, "hurt": 1}}
        sheet = root / "sheet.png"
        Image.new("RGBA", (16, 10), "white").save(sheet)
        guides = extract_guides(sheet, manifest, ["idle", "hurt"], root / "guides")
        assert list(guides) == ["idle", "hurt"]
        assert Image.open(guides["hurt"]).size == (8, 10)
        colored = root / "colored.png"
        Image.new("RGBA", (4, 6), (230, 70, 20, 255)).save(colored)
        prepared = prepare_model_guides({"pose": colored}, root / "prepared", canvas_size=(8, 12))
        red, green, blue = Image.open(prepared["pose"]).getpixel((4, 6))
        assert red == green == blue
        assert select_frames(manifest, "hurt,idle") == ["hurt", "idle"]
        smear_manifest = {**manifest, "frames": {
            **manifest["frames"], "heavy_i2": 0, "heavy_i3": 1, "special1": 0, "special2": 1,
        }}
        assert select_frames(smear_manifest, "heavy_i_smear,special_smear") == ["heavy_i_smear", "special_smear"]
        default_plan = select_frames(smear_manifest, None)
        assert default_plan.index("heavy_i_smear") == default_plan.index("heavy_i2") + 1
        assert default_plan.index("special_smear") == default_plan.index("special1") + 1
        assert frame_source("heavy_i_smear") == "heavy_i3"
        assert "swept tapered arc of 3-4 ghosted blade positions" in prompt_for("special_smear", "fighter", DEFAULT_MODEL)
        source_state = {"model": "model-a", "identity_sha256": "identity-a"}
        assert not checkpoint_sources_changed({}, source_state)
        assert not checkpoint_sources_changed(source_state.copy(), source_state)
        assert checkpoint_sources_changed({"model": "model-a", "identity_sha256": "identity-b"}, source_state)
    print("SELF_TEST_OK")


def main():
    args = parse_args()
    if args.self_test:
        self_test()
        return
    args.sheet = args.sheet or Path(f"web/assets/sprites/{args.character}.png")
    args.manifest = args.manifest or Path(f"web/assets/sprites/{args.character}.json")
    for path in (args.identity_ref, args.sheet, args.manifest):
        if not path.is_file():
            raise FileNotFoundError(path)
    manifest = load_manifest(args.manifest)
    names = select_frames(manifest, args.frames)
    out_dir = args.out_root / args.character
    guides = extract_guides(args.sheet, manifest, names, out_dir / "guides")
    model_guides = prepare_model_guides(guides, out_dir / "model-guides")
    plan = {
        "character": args.character,
        "frames": names,
        "identity_ref": str(args.identity_ref),
        "manifest": str(args.manifest),
        "sheet": str(args.sheet),
        "model": args.model,
        "guide_sources": {name: frame_source(name) for name in names},
    }
    save_json(out_dir / "plan.json", plan)
    print(json.dumps(plan, indent=2))
    if args.dry_run:
        print(f"DRY_RUN_OK {len(names)} guides -> {out_dir / 'guides'}")
        return
    run_generation(args, manifest, names, model_guides, out_dir)


if __name__ == "__main__":
    try:
        main()
    except (RuntimeError, ValueError, FileNotFoundError, subprocess.CalledProcessError) as error:
        sys.exit(f"ERROR: {error}")
