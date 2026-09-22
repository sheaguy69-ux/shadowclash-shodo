# Oni shadow dash QC — SHEET_V 564

Source: built-in ImageGen concept approved for integration on 2026-08-19.
Source SHA-256: `31b6685479c9c84020a97c433eacf5325712f8cac1266c8822fc536ca4f1fb72`.

All eight beats are `KEEP-CROP`: the authored pose/smoke/red-speed content is kept,
with only corner-connected white-page keying, one uniform `0.74` scale, cell centering,
and `footY: 330` registration. The entire cel—including smoke and red speed FX—renders
through the shared `drawShodoFrame()` path; no Shodo pixels are baked into the PNG.

| Beat | Motion role | Identity | Weapon | Palette | Pose | 48x64 | Size | Path | Smear | Physics | Timing | Background | Integrity | Grade |
|---:|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | launch | PASS | PASS | PASS | PASS | PASS | PASS | PASS | PASS | PASS | PASS | PASS | PASS | KEEP-CROP |
| 2 | reach | PASS | PASS | PASS | PASS | PASS | PASS | PASS | PASS | PASS | PASS | PASS | PASS | KEEP-CROP |
| 3 | acceleration | PASS | PASS | PASS | PASS | PASS | PASS | PASS | PASS | PASS | PASS | PASS | PASS | KEEP-CROP |
| 4 | dissolve-in | PASS | PASS | PASS | PASS | PASS | PASS | PASS | PASS | PASS | PASS | PASS | PASS | KEEP-CROP |
| 5 | full shadow | PASS | PASS | PASS | PASS | PASS | PASS | PASS | PASS | PASS | PASS | PASS | PASS | KEEP-CROP |
| 6 | emerge | PASS | PASS | PASS | PASS | PASS | PASS | PASS | PASS | PASS | PASS | PASS | PASS | KEEP-CROP |
| 7 | brake | PASS | PASS | PASS | PASS | PASS | PASS | PASS | PASS | PASS | PASS | PASS | PASS | KEEP-CROP |
| 8 | recovery | PASS | PASS | PASS | PASS | PASS | PASS | PASS | PASS | PASS | PASS | PASS | PASS | KEEP-CROP |

Packed bounds are 244–269 px wide and 124–164 px tall. Every beat is strictly
inside the 480×372 cell, and every lower bound is exactly `footY: 330`. Cells
0–380 are verified pixel-identical after the append; active dash cells are 381–388.
