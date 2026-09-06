# Oni, Shin wall contact and airborne hurt repairs — 2026-09-06

SHODO-EDITION only, `http://localhost:9101/`, SHEET_V729.

## Result

- Removed Oni's old canvas shadow glow. The approved four-beat Shodo ink artwork is his only new aura, animated on the combat clock and registered to the actual pose, including airborne recoils. No procedural steam lines remain.
- Replaced 66 old Oni cell references and the rejected four-frame run route. The atlas appends67 unique cells (601→668), preserving every original RGBA pixel. The run uses the owner's two approved alternating contacts; it is intentionally a two-drawing loop, not a claimed eight-drawing cycle.
- Restored complete Oni bodies/capes in crouch, jump, received-hit, knives, dive, sword, claw, staff and special families. Intact original source pixels were recut first; source-amputated margins received narrow built-in imagegen edits. Uniform source scale preserves the existing model. Repaired cells do not inherit obsolete erasure masks.
- Separated Oni’s forward air-heavy artwork from the grounded Severance row. The air attack receives its own four airborne sword beats; ground neutral and forward heavies keep their original routes. Its contact drawing begins at the existing42% startup point and spans the unchanged active window.
- Added rising/apex/falling airborne hurt routing for all nine fighters. Released hit/throw victims use received-hit drawings ahead of stale stance/move/floor-recovery flags. Held throws retain paired art; grounded reactions stay grounded.
- Corrected authored-facing flags on Kael161/162, Mokurai180/181/183, Exile183, and the restored Oni hurt cells. Live landing review also corrected Kael18 and Exile345.
- Shin's wall grip now anchors to the drawn hand/boot contact instead of a painted wall stroke; removed that stroke via the existing frameClear mechanism and replaced the unsuitable pole/walljump drawing with his current jump pose.
- Fixed the shared bounds cache: unnamed Oni, Exile and Mokurai sheets previously collided at the same cell index. Cache identity now uses the sprite image source. Wall state now resolves after the current physics contact, removing the first-contact frame of wrongly anchored jump art.

No damage, gameplay startup/active/recovery, movement speed, jump impulse or hitbox values changed. Only the new air-heavy drawing exposure was aligned to its existing hit window.

## Validation

- All nine direction/wall checks:882 consecutive samples, zero failures.
- Air hurt:216 rendered cases,108 held-throw cases,36 grounded routes,465 consecutive hit-to-landing frames, and cold/warm bounds-cache isolation passed.
- Focused Kael/Exile landing correction:48 air cases and96 live frames passed; both source direction and final drawing transforms reviewed.
- Shin:30 consecutive wall contact/kick samples passed, including the first physics contact on both walls. Hand gap−1.21px and supporting boot+1.81px.
- Oni repaired attacks:22 real attack routes and1,030 consecutive samples inspected in both directions. An additional98 knife-conversion samples covered every active knife cell with zero direction errors. The grounded-art leak discovered here was isolated to forward air Heavy and received its own correction.
- Final dedicated air-heavy regression:6 actual Heavy routes,292 consecutive frames passed. All four air poses and both grounded rows are reachable; contact666 covers the existing active window in both facings; no legacy floor drawings appear airborne.
- Oni aura:24 consecutive frames; moving ink, frozen-clock stability, Oni-only routing, actual airborne registration, and absence of old canvas glow passed.
- Blade-lock regression:150 assertions passed. All nine sprite manifests and atlases remain whole and consistent. Engine syntax and whitespace checks passed.

The checks cover the repaired sequences and shared routing; they do not claim every attack of every fighter has received a new full visual review.

## Evidence and reproducible checks

- `tools/check_air_hurt.py`; `media/air-hurt-20260906/QC.md`, `final/`, and the focused landing rerun.
- `tools/check_shin_wall_contact.py`; `media/shin-wallcling-20260906/final/`.
- `tools/check_oni_air_heavy.py`; `media/oni-aura-cutoff-20260906/air-heavy-final/`, plus the wider `live-attacks/` review.
- `tools/check_oni_aura.py`; `media/oni-aura-cutoff-20260906/live/aura.gif` and `checks.json`.
- `tools/check_direction_compass.mjs`; `media/oni-aura-cutoff-20260906/compass/`.
- `media/oni-aura-cutoff-20260906/pack.json`: exact old→new mappings, candidate hashes, and original-prefix integrity.
- `media/oni-cutoff-20260906/QC.md`, `late/`, `hfwd/`, `ajump/`: source registration, per-cell review, generation provenance and native before/after boards.
- `media/oni-aura-cutoff-20260906/run/`: owner-approved contacts and consistent-scale registration.

Intentional attack dash/dissolve exposures252/467 remain attack artwork; neither is used for airborne hurt. Same-role clean recoveries replace source-amputated equivalents333/357/360/480;329 uses the already-complete sword extension592.
