# Oni clean airborne idle — SHEET_V 567

## Owner ruling

Remove the dirt beneath Oni's airborne-idle pose. Keep the authoritative eight-frame airborne Back+Light sequence unchanged.

## Implementation

- `aback2` remains source cell **390**, including its authored launch dirt.
- `airidle` now routes to appended cell **397**.
- Cell 397 keeps the largest connected alpha component from cell 390 byte-for-byte and clears only the disconnected debris underneath.
- Cleanup removed **866 alpha pixels across 12 disconnected components**. Oni's character pixels, placement, colors, silhouette, and transparent edge padding are unchanged.
- Atlas cells 0–396 remain decoded-pixel identical; the manifest grows from 397 to 398 columns.
- Ground idle is still excluded from Oni's airborne idle/recovery routes.

## Art-edit decision

A built-in precise-object image edit was tested with the instruction to remove only the detached dirt/dust below Oni while preserving the exact character, pose, silhouette, colors, placement, and transparent background. It redrew/upscaled the character, so it was rejected and never packed. The shipped frame uses deterministic connected-alpha cleanup instead.

## Verification

- `python3 tools/sprites/pack_oni_air_idle_567.py` — reproducible; confirms 866 removed pixels/12 debris components.
- `python3 tools/check_oni_air_idle.py --url http://127.0.0.1:9101/index.html` — clean cell 397 is used for neutral apex, airborne idle, and Light/Heavy/Special recovery; launch and grounded idle remain authored; Shodō routing is retained.
- `python3 tools/check_oni_aerial_back_light.py` — authoritative eight-frame cells 389–396 remain exact.
- `python3 tools/check_oni_aerial_back_turn.py --url http://127.0.0.1:9101/index.html` — airborne Back remains Back after either midair facing turn.
- `python3 tools/check_oni_shadow_dash.py --url http://127.0.0.1:9101/index.html` — dash cells 381–388 and red/black Shodō FX remain live.
- `python3 tools/check_oni_moves6.py --url http://127.0.0.1:9101/index.html` — all Oni move-board routes pass.
- `python3 tools/check_it_actually_plays.py --url http://127.0.0.1:9101/index.html --out RECOVERY/oni-air-idle-567/full-fight` — real input lands hits, reaches KO, advances the round, and throws no page errors.
- `git diff --check` — clean.
- `/whoami` — exact tree, branch `lane/codex-shin-mode-2`, commit `bb686fc`, `SHEET_V 567`, PID 93824.

## Evidence

- `source-vs-clean.png` — source cell 390 beside clean cell 397.
- `airidle-cell390-original.png` — unchanged attack source.
- `airidle-cell397-clean.png` — packed dirt-free idle.
- `live-air-idle-clean.png` — live port-9101 frame showing the clean pose in the air.
- `live/` — real-input Back-to-idle trace and screenshots; reports five air-idle samples, zero ground-idle leaks, and no page errors.
- `full-fight/` — full fight harness artifacts.

Status: verified locally; uncommitted, unmerged, and undeployed.
