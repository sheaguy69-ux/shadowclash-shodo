# Oni authoritative aerial Back+Light — SHEET_V 565 QC

Owner ruling: `/Users/anthonyguy/Desktop/Codex Image Aug 19, 2026, 10_30_23 AM.png`
is the correct frame-by-frame sequence. Reading order is top-left through top-right,
then bottom-left through bottom-right. SHA-256:
`7fdc7b3708be8e462a49f1ad284973f63ab1d356cb11e169aad1cf2e2de5eb7f`.

Sequence: crouch/load → launch → reach → chamber → horizontal rear heel strike
(KIME) → retract → drop → landing settle.

All cells are graded `KEEP-CROP`: the owner-supplied drawings are unchanged; only
measured row cuts, corner-connected white-page keying, uniform scaling, and atlas
placement were applied.

| Beat | Identity | Weapon | Palette | Pose | 48×64 | Registration | Path | Smear | Physics | Frame data | Background | Integrity | Grade |
|---:|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | PASS | PASS | PASS | PASS | PASS | PASS | PASS | N/A | PASS | PASS | PASS | PASS | KEEP-CROP |
| 2 | PASS | PASS | PASS | PASS | PASS | PASS | PASS | N/A | PASS | PASS | PASS | PASS | KEEP-CROP |
| 3 | PASS | PASS | PASS | PASS | PASS | PASS | PASS | N/A | PASS | PASS | PASS | PASS | KEEP-CROP |
| 4 | PASS | PASS | PASS | PASS | PASS | PASS | PASS | N/A | PASS | PASS | PASS | PASS | KEEP-CROP |
| 5 | PASS | PASS | PASS | PASS | PASS | PASS | PASS | PASS | PASS | PASS | PASS | PASS | KEEP-CROP |
| 6 | PASS | PASS | PASS | PASS | PASS | PASS | PASS | N/A | PASS | PASS | PASS | PASS | KEEP-CROP |
| 7 | PASS | PASS | PASS | PASS | PASS | PASS | PASS | N/A | PASS | PASS | PASS | PASS | KEEP-CROP |
| 8 | PASS | PASS | PASS | PASS | PASS | PASS | PASS | N/A | PASS | PASS | PASS | PASS | KEEP-CROP |

Measured notes:

- One uniform scale: `0.67`. The packed mask component is 28–31px wide against
  the live idle's 29px, so Oni's physical size holds while the authored poses vary.
- Source ground lines are preserved independently per row (top `y=407`, bottom
  `y=372`); the airborne lift is not flattened onto `footY`.
- All eight packed alpha bounds have transparent padding on every cell edge;
  measured edge-alpha count is zero for every cell.
- Beat 5's white/red heel smear is authored source art and remains intact. No
  extra Shodō is baked into the PNG; all eight cells inherit the permanent shared
  `drawShodoFrame()` path through `drawSprite()`.
- Combat timing, damage, recovery, and the existing behind/steel hitbox are
  intentionally unchanged. This correction replaces only the visual sequence.
- Cells 389–396 are append-only. Decoded pixels for cells 0–388 are asserted
  identical before and after packing; the previous seven-cell route remains under
  `aback_v564_1..7` aliases.
