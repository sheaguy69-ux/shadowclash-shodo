# Mizu launched-hurt replacement — approved source

Anthony approved the eight-drawing Shodō appearance study on 2026-09-23 with “approve and next”. The exact reviewed source is `frame-01.png` through `frame-08.png`, shown in `style-review.png` and `sequence-review.png`. The 1254 × 1254 RGBA files are original transparent drawings; the live atlas uses scale-normalized copies. Built-in editor model identity was not available, so this work is not labeled GPT Image 2.5.

The current live idle staff measures about 157 pixels along its long axis in the 300 × 320 atlas cell. Each new drawing is scaled by its measured staff length to a 160-pixel staff, preserving internal anatomy; raw estimated lengths are `[818, 675, 772, 950, 906, 903, 887, 909]` pixels. Crop using the alpha channel, scale, trim alpha again after downsampling, center horizontally, and place the alpha bottom at y=310 in the 300 × 320 cell. Append eight new cells and repoint only `airhurt1..8`; the former borrowed grabbed cells stay untouched. The velocity-based selector reads all eight new keys. Rebuild runtime pages and bump `SHEET_V` in the same change.

The shared tree may contain unrelated in-flight changes. Do not replay packing over a sheet that already contains these cells.
