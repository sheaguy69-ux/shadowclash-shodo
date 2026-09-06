# Sprite negative-space cleanup — SHODO-EDITION :9101

SHEET_V717 removes reviewed opaque gray/dark/paper pockets between limbs, inside chain/bead loops, and disconnected card/adjacent-cell remnants. Anthony explicitly requested the all-roster cleanup and authorized proceeding without repeated approvals and using audit agents.

All 1,493 active cells were visually inspected. New cleanup covers 250 cells and 239,561 source pixels with nonzero alpha:

| Fighter | Active cells reviewed | Cells cleaned |
| --- | ---: | ---: |
| Executioner | 149 | 29 |
| Mizu | 148 | 7 |
| Shin | 165 | 34 |
| Tsubasa | 178 | 27 |
| Ember | 140 | 17 |
| Kael | 155 | 25 |
| Mokurai | 172 | 7 |
| Exile | 151 | 54 |
| Oni | 235 | 50 |

Precise reviewed pixel masks are stored as merged rectangles in the existing `frameClear` metadata. The shared cached keyer applies them before Shodo outlining for bodies, afterimages, clones and hit flash. No new renderer algorithm or runtime color threshold. Original PNG hashes, frame maps, scales, foot anchors and mirror maps are unchanged. Ember's six previously cleaned guide cells remain, making 256 cells with cleanup metadata overall. Mizu had no confirmed gray leg pockets; its seven fixes remove detached guides.

Validation: `python3 tools/check_sprite_clear.py` checks all 1,493 active cells in the real browser: reviewed pixels clear, every outside pixel remains identical before outlining, and bodies remain nonempty. `--before` reproduces the defect with cleanup disabled inside an isolated browser. All 140 Ember scale/anchor/envelope probes and copy/flash checks pass via `tools/check_ember_scale.py`. Nine Heavy live-input scenarios pass with 54 consecutive eight-tick strips; all-nine recovery strips visually inspected. Exile was captured again after refining three paper pockets. PNG hashes, non-cleanup manifest equality, sheet integrity and diff checks pass.

Evidence is in `media/negative-space-20260906/`: native mask audits `audit-a/`, `audit-b/`, `audit-c/`, `ember/`; browser comparisons `runtime/`; live strips `live/` and final Exile `live-final/`. Exile141/142/175 refined evidence supersedes their initial candidate plates. `applied.json` records per-fighter counts; baseline hashes/manifests are in `baseline/`.

This is background-artifact QC (dimension 11), with geometry/inventory preservation (dimension 12), not new-art approval across all 12 dimensions. Existing clipped bodies, missing hood/face pixels, finger-overlapping wall strips, foot-attached baselines, and ambiguous effect shading remain. Examples: Kael208/284 hood holes; Shin338/339 and Exile312/313 wall contacts; Mokurai237 card edge intertwined with impact rays. Source restoration is required for missing artwork. Attack arcs, dust, cloth and weapons were preserved; tiny uncertain fringe pixels were not broadly keyed away. Full inventories are in the audit reports. No timing changes, paid generation, push, deployment or visible-browser reconfiguration.
