# SHODO Medium-board generation decision — 2026-09-01

## Understanding

- Produce the five Medium boards specified in `docs/MISSING-BOARDS-FOR-GPT-674.md` at SHEET_V 676: Oni, Executioner, Kael, Shin, and Mizu.
- These are combo-bridge animations for the live Medium tier, not gameplay or balance changes.
- Use only fighter references inside `/Users/anthonyguy/SHADOWCLASH.1.0*2/art/production`.
- Each deliverable is one eight-beat horizontal SHODO review strip: LEFT-facing, idle-matched anatomy scale, stable ground line, distinct cel poses, no painted props, no drawn card borders, and no excessive empty space.
- Generate review art and QC evidence only. Do not change runtime sheets, manifests, routes, timing, damage, or `SHEET_V` before Anthony approves the montage.

## Decision log

- The attached detailed move/beat brief is the accepted design and prompt authority; no alternate move concepts will be invented.
- Regenerate Shin instead of approving `shin-shodo-silent-reed-elbow-standing-medium-8f-v1-review`: it faces right, does not clearly show the rear wire loop, and has baked panel borders.
- Generate all five independently from each fighter's production idle/approved attack references to prevent identity or scale leakage between fighters.
- Grade every output against the 12-point Sprite Animation Director checklist. More than 30% REDO/REJECT stops the batch before owner delivery.

## Assumptions and non-goals

- Performance, reliability, security, and maintenance are unchanged because this pass creates review PNGs only.
- Existing live Medium inputs and combat values remain authoritative.
- Final border removal, true-alpha cutting, append-only atlas packing, `SHEET_V` bump, live filmstrip capture, and routing verification happen only after owner art approval.
