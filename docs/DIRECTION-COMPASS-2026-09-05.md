# Directional compass — SHODO-EDITION :9101

Owner request: all nine fighters should face the opponent appropriately, run forward instead of backward, and cling/jump in the correct wall direction. Standing approval covers the fixes; no sprite pixels were regenerated or edited.

## Behavior

- Idle, crouch, guard and attack input facing remain opponent-relative. Running artwork follows actual travel direction; both directions play the stride forward instead of reversing the animation.
- Cling poses grip the wall. Ordinary attacks on a wall face out into the arena, matching their hitboxes. Contact and release keep the transitional cling frame covered, while grounded frames never use the wall mirror.
- A wall jump cancels a dash into the wall. A real quick-release/re-grip sequence previously left dashTimer active; movement then overwrote the outward jump impulse with 800px/s into the wall and immediately reattached. Both sides, all nine reproduced it; the jump now wins.
- Replay tape stores the actual displayed mirror separately from combat facing. Echoes preserve the visual direction without changing their attack-facing data.

## Authored frame directions

Live captures plus raw full-row inspection found right-facing artwork in rows the renderer assumed faced left. Added 69 per-cell mirror flags across six manifests:

| Fighter | Corrected cells |
|---|---|
| Ember | 8 run cells |
| Kael | 8 run, 8 idle/recovery, 6 jump, 4 crouch, 2 guard, wall cling and wall jump (30) |
| Mokurai | 8 run, 7 directional jump beats, 4 crouch, 8 guard and wall cling (28) |
| Mizu | Wall jump (1) |
| Shin | Wall jump (1) |
| Exile | Wall jump (1) |

Executioner, Tsubasa and Oni required the shared facing changes but no per-cell metadata changes. Mokurai's final frontal jump-settle cell was left alone. Sprite PNGs, frame coordinates, scale, weapons and baked effects are unchanged. SHEET_V is bumped with the manifests.

## Verification

`OUT=media/compass-check node tools/check_direction_compass.mjs` runs all nine in fresh local matches with real DOM key events and live animation frames. It tests both sides: idle, crouch, guard, running toward/away, stop, opponent crossing sides, wall contact, Heavy on the wall, release while attacking, plain release, rapid re-grip and wall jump. It observes the real Canvas transform, not a copied engine expression. Raw-art orientation fixtures reflect the inspected rows; the first numeric-only probe missed reversed drawings, which the enlarged visual inspection caught.

The check also walks every run-cycle phase in both directions and verifies that replay tape preserves visual versus combat facing. `python3 tools/check_wall_mirror.py` delegates to this check, replacing the obsolete single-fighter test that required wall attacks to share the cling mirror.

Final result: 882 captured direction samples and 216 filmstrips across all nine fighters, zero direction failures.

Additional checks: all 648 directional input probes pass; jump-commitment and wall-escape regression passes. No attack damage, timing constants, recovery windows or jump-strength constants changed. The wall-jump dash cancellation is an explicit movement bug fix.

Evidence: `media/direction-review-20260905/`. Each fighter has trace.json and consecutive strips for both sides under `final/`; raw row boards document the metadata decisions. `before/` preserves the original captures, and `after/` preserves the rapid re-grip wall-jump failure. This reviews the named movement/facing paths, not every directional combat drawing in the entire sprite atlas.
