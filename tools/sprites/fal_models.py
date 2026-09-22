#!/usr/bin/env python3
"""THE ONE PLACE the generator models are named (owner order, Jul 29 2026).

Owner: "the motion generator I want y'all to use is Seedance 2 which is a way
better quality, and use nano banana pro" — so:

  MOTION (i2v clips — the frame source for registered multi-frame animation)
      bytedance/seedance-2.0/image-to-video
  STILLS (repose / identity-locked edits)
      fal-ai/nano-banana-pro/edit

Two gotchas that cost real money if missed:
  1. Seedance 2's endpoint id has NO "fal-ai/" prefix. "fal-ai/bytedance/..."
     is the OLD Seedance 1.x family and will silently give you worse frames.
  2. generate_audio defaults to TRUE. Sprite clips are silent — always pass
     False; audio is wasted spend and a bigger download.

Seedance 2 capabilities i2v_clip() uses:
  - resolution up to 4k -> more pixels per sprite cell
  - end_image_url -> pin the last frame to the first for a PERFECT loop, which
    is what a walk/run cycle wants (no more hunting a clean stride window)

CAMERA LOCK — pick the model by this, not by render quality (owner, Jul 29:
"Kling if you using make you use the recent best model"):
  Seedance 2 exposes NO camera controls, and it BROKE camera lock on both sprite
  clips despite the prompt saying "locked-off static camera, no zoom, no pan, no
  dolly" verbatim — one clip rotated the swing into the lens, the other dollied
  back (the character's head shrank 650px -> 270px, which silently faked a
  "growing" club in the swell metric).
  KLING V3 4K exposes negative_prompt + cfg_scale + shot_type, so camera motion
  can be FORBIDDEN rather than merely requested. For sprite work camera lock beats
  render quality — a drifting camera destroys size registration, which is a hard
  reject. Use MOTION_MODEL_KLING for anything where the character must stay the
  same size in every frame (all locomotion + all attack arcs).

  MEASURED Jul 30 2026 — the Seedance camera detour, so nobody spends on it twice.
  Same standing pose, first frames vs last frames of a 121-frame clip:
      Kling v3 4k                              1356px -> 1318px   -2.80%
      Seedance 1.0 pro, camera_fixed=True       641px ->  942px  +46.96%
  Two things that were tried and did NOT work:
    · Seedance 2.0 has NO camera field at all (fal OpenAPI schema, 9 params:
      prompt, image_url, end_image_url, resolution, aspect_ratio, duration,
      generate_audio, bitrate_mode, end_user_id). A "Camera: [shot], [lens],
      [movement]." first line is prompt text and does not bind.
    · Seedance 1.0 pro/lite DO expose `camera_fixed: bool` — a real parameter —
      and it still pushed in across the whole clip. It is not a lock.
  Mechanism worth knowing: the push-in was WORST from a lowseat/padded seed with
  the character small in an empty frame. The model reframes to FILL empty space,
  so padding ATTRACTS the zoom rather than absorbing it. If a Seedance clip is
  ever unavoidable, the drift settles late — the only window inside the 0.5% gate
  on that test clip was the last 21 frames — so harvest the TAIL, not the middle.
  Kling at -2.80% is still over the 0.5% gate: MEASURE every clip's start-vs-end
  standing height before packing, and per-frame-correct the scale if it drifted.

API SHAPES DIFFER — i2v_clip() normalises them, do not hand-roll:
  Seedance 2   -> image_url,       resolution,      generate_audio (default TRUE)
  Kling v3     -> start_image_url, NO resolution,   generate_audio (default TRUE)
  Kling o3     -> image_url,       NO resolution,   generate_audio (default False)
"""

MOTION_MODEL = "bytedance/seedance-2.0/image-to-video"
MOTION_MODEL_FAST = "bytedance/seedance-2.0/fast/image-to-video"
# multi-reference variant: takes image_urls[] instead of one image_url — better
# identity lock when a single seed frame isn't holding the character.
MOTION_MODEL_REF = "bytedance/seedance-2.0/reference-to-video"

# BEST Kling as of Jul 29 2026 (owner: if using Kling, use the most recent best).
# v2.1 — what this repo used to call — is THREE generations behind. v3 4k is the
# top i2v tier and the only family here exposing negative_prompt/cfg_scale, i.e.
# the only one that can be told NOT to move the camera.
MOTION_MODEL_KLING = "fal-ai/kling-video/v3/4k/image-to-video"
MOTION_MODEL_KLING_PRO = "fal-ai/kling-video/v3/pro/image-to-video"

# Camera motion is the #1 sprite-clip killer: any drift breaks size registration
# (<=0.5% wobble) and a shrinking character fakes a growing weapon. Forbid it.
NEG_CAMERA = ("camera movement, camera zoom, zoom in, zoom out, camera pan, camera dolly, "
              "dolly in, dolly out, camera orbit, camera shake, changing camera distance, "
              "character changing size, character turning toward camera, front view, "
              "three-quarter view, rotating to face the viewer, background, ground shadow, "
              "blur, distort, low quality")
STILL_MODEL = "fal-ai/nano-banana-pro/edit"

# retired — kept named so a grep for them lands on this comment instead of nothing
_RETIRED = {
    "fal-ai/kling-video/v2.1/standard/image-to-video": "-> MOTION_MODEL_KLING (v2.1 is 3 gens old)",
    "fal-ai/flux-pro/kontext": "-> STILL_MODEL",
    "fal-ai/flux-pro/kontext/multi": "-> STILL_MODEL (image_urls takes a list)",
}


def still_edit(fal_client, prompt, image_paths, resolution="2K", **kw):
    """Identity-locked repose/edit. Returns the result dict (images[0].url).

    image_paths: one path or a list — nano-banana-pro always takes image_urls[].
    resolution 2K by default: sprite cells get downscaled into the sheet, so the
    extra pixels survive as edge quality instead of being invented by the packer.
    """
    if isinstance(image_paths, (str, bytes)) or hasattr(image_paths, "__fspath__"):
        image_paths = [image_paths]
    urls = [fal_client.upload_file(str(p)) for p in image_paths]
    args = {"prompt": prompt, "image_urls": urls, "resolution": resolution,
            "output_format": "png", "safety_tolerance": "6"}
    args.update(kw)
    return fal_client.subscribe(STILL_MODEL, arguments=args, with_logs=False)


def i2v_clip(fal_client, prompt, image_path, duration="5", resolution="1080p",
             aspect_ratio="9:16", loop=False, fast=False, model=None,
             cfg_scale=0.85, **kw):
    """Animate one still into a clip. Returns the result dict (video.url).

    model: None -> MOTION_MODEL (Seedance 2, the owner's default). Pass
    MOTION_MODEL_KLING for camera-lock-critical work — see the CAMERA LOCK note
    in the module docstring. The two families take DIFFERENT argument names; this
    function normalises them so callers never have to care.

    loop=True pins the final frame back to the start image so a cycle closes on
    itself — use it for walk/run, never for a one-shot attack (it would rewind
    the swing). generate_audio is forced off on every family: silent sprites.
    """
    model = model or (MOTION_MODEL_FAST if fast else MOTION_MODEL)
    url = fal_client.upload_file(str(image_path))
    is_kling = "kling" in model
    args = {"prompt": prompt, "duration": duration, "generate_audio": False}
    # v3 Kling wants start_image_url; Seedance and Kling o3 want image_url
    args["start_image_url" if "kling-video/v3" in model else "image_url"] = url
    if is_kling:
        # the whole reason to reach for Kling: camera motion can be FORBIDDEN
        args["negative_prompt"] = kw.pop("negative_prompt", NEG_CAMERA)
        args["cfg_scale"] = cfg_scale        # raised over the 0.5 default: obey the prompt
        args["shot_type"] = kw.pop("shot_type", "customize")   # never let it pick shots
    else:
        args["resolution"] = resolution
        args["aspect_ratio"] = aspect_ratio
        args["bitrate_mode"] = "high"
    if loop:
        args["end_image_url"] = url
    args.update(kw)
    return fal_client.subscribe(model, arguments=args, with_logs=False)


if __name__ == "__main__":
    # self-check: the ids must not carry the wrong prefix, and loop must pin the tail
    assert not MOTION_MODEL.startswith("fal-ai/"), "Seedance 2 takes no fal-ai/ prefix"
    assert "seedance-2.0" in MOTION_MODEL and STILL_MODEL.endswith("nano-banana-pro/edit")

    class _Fake:
        def upload_file(self, p): return f"url://{p}"
        def subscribe(self, model, arguments, with_logs=False):
            return {"_model": model, "_args": arguments}

    f = _Fake()
    r = i2v_clip(f, "walk", "/tmp/a.png", loop=True)
    assert r["_model"] == MOTION_MODEL
    assert r["_args"]["end_image_url"] == r["_args"]["image_url"], "loop must pin the tail frame"
    assert r["_args"]["generate_audio"] is False, "sprite clips are silent"
    assert i2v_clip(f, "x", "/tmp/a.png")["_args"].get("end_image_url") is None
    assert i2v_clip(f, "x", "/tmp/a.png", fast=True)["_model"] == MOTION_MODEL_FAST
    # Kling path: different arg name, camera forbidden, audio still off
    kr = i2v_clip(f, "swing", "/tmp/a.png", model=MOTION_MODEL_KLING)
    assert kr["_model"] == MOTION_MODEL_KLING
    assert "start_image_url" in kr["_args"] and "image_url" not in kr["_args"], \
        "Kling v3 takes start_image_url, not image_url"
    assert "resolution" not in kr["_args"], "Kling v3 has no resolution param"
    assert kr["_args"]["generate_audio"] is False
    assert "camera zoom" in kr["_args"]["negative_prompt"] and kr["_args"]["cfg_scale"] > 0.5
    assert i2v_clip(f, "x", "/tmp/a.png")["_args"].get("negative_prompt") is None, \
        "Seedance has no negative_prompt — do not send one"
    s = still_edit(f, "pose", "/tmp/b.png")
    assert s["_model"] == STILL_MODEL and s["_args"]["image_urls"] == ["url:///tmp/b.png"]
    assert still_edit(f, "p", ["/tmp/b.png", "/tmp/c.png"])["_args"]["image_urls"] == \
        ["url:///tmp/b.png", "url:///tmp/c.png"]
    print("fal_models self-check PASS:", MOTION_MODEL, "|", STILL_MODEL)
