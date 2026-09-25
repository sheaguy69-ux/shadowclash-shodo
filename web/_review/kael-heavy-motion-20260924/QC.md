# Kael heavy motion study · visual QC

This is the next art process after Anthony approved the Kael contact pose. It is a five-drawing motion preview, with the exact approved contact PNG copied byte-for-byte as frame 3. Frames 1, 2, 4, and 5 are new review drawings. Nothing here has been packed into the playable sprite sheet.

All five files measure 1536 × 1024. A dark-pixel scan gives bottommost pixels at y=923, 924, 921, 874, and 892 respectively. The player temporarily shifts frames 4 and 5 downward by 4.9% and 3.1% of canvas height to make the feet easier to compare. The source drawings themselves are unaltered. This registration difference still needs art correction.

The first windup drawing had a short long-blade; it was redrawn with a longer blade for this preview. The old draft remains as `01-anticipation-shortblade-draft.png` for provenance. The long katana's apparent length and the tip spacing still need a full sequence check. The preview helps locate this and any foot/body pop; it does **not** certify a finished continuous animation. Before installation: redraw for consistent blade dimensions and handedness, add missing in-betweens where the long tip jumps, check the short blade's separate guard path, review at game size and both facings, then show the complete strip to Anthony.

The preview's 330 ms timing matches the game's current nominal neutral-heavy visual duration for Kael (`baseDur=330`, no Kael `SLICE_SPEED` override). Existing contact and recovery behavior were not edited. No sprite-sheet bytes, routes, hitboxes, or SFX were changed.
