# Kael heavy · eight-frame sprite preparation

Scope assumed from the active Kael heavy-attack review. This is an eight-drawing replacement candidate for `kcross1..8`, not a redraw of Kael's entire 345-cell character atlas. A scope clarification has been sent to Anthony.

Frames 01, 02, 04, 06 and 07 are transparent derivatives of the five approved model-matched study poses (`../kael-heavy-model-match-20260925/APPROVAL.md`). Frames 03 (mid cut), 05 (overtravel) and 08 (settle) are newly generated connectors and have not received separate visual approval. The five approved opaque originals remain unchanged. Built-in image editor model identity is unverified; do not label these as GPT Image 2.5.

All eight candidate sources are RGBA 1536 × 1024. The current game sheet is 300 × 320 per cell, `footY=312`, `cols=345`. A dry pack with the existing `tools/sprites/pack_keyed_board.py`, uniform scale 0.245 and floor beat 1, fit all eight: union window 294 × 184 within 300 × 320; no empty or clipped cell. Expected appended indices 345–352. The dry run wrote no game sheet or manifest.

At that shared scale, source foot bottoms relative to the desired baseline measured +0, +8, −3, +5, +0, +1, +3, −2 pixels. The review player applies opposite display-only offsets of 0, −8, +3, −5, 0, −1, −3, +2 pixels. Production packing must register the cells themselves before a live swap; display offsets do not solve it. Inspect head/body size stability, especially frames 2 and 7, the long-blade tip route, and the gap from settle back to current idle. The player uses the current 330 ms total, but eight sampled drawings are not proof of perfect frame-to-frame motion.

No live atlas, sprite JSON, `SHEET_V`, combat timing, hitboxes or SFX was changed in this preparation pass. An eight-frame montage/playback is available at `index.html` for the art gate before installation.
