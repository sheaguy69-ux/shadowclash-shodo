# Claude Code handoff — production SHODO art only

Anthony's current and controlling instruction is: **use only the art under `/Users/anthonyguy/SHADOWCLASH.1.0*2/art/production`; no old frames and no other art source.**

## Sole art authority

```text
/Users/anthonyguy/SHADOWCLASH.1.0*2/art/production
```

Every image opened, copied, keyed, scaled, packed, or routed must resolve inside that directory. Do not source art from another ShadowClash worktree, an existing gameplay atlas, `RECOVERY`, Downloads, generated candidates outside this tree, or the retired Oni 670 handoff.

`/Users/anthonyguy/SHADOWCLASH.1.0*2/art/gen_preview.py` is a preview/index generator. Its docstring and `PACKED_HINTS` are navigation hints from an earlier packing pass, not Anthony's instruction and not an approval database. In particular, substring matches can identify multiple versions. Never use that heuristic to choose between takes.

## What is packed for the handoff

- `SHODO-PRODUCTION-ART-ONLY.tar`: byte-for-byte archive of the complete `art/production` directory.
- `FRAME-INVENTORY.csv`: SHA-256, dimensions, alpha mode, size, and canonical absolute path for every PNG in the source directory.
- `PRODUCTION-SOURCE-INDEX.txt`: row/frame counts by fighter plus the production board paths that explicitly carry the `approved-review` label.

The canonical directory above remains the source of truth. The tar is a transport copy, not a second editable art library.

Archive verification:

- `SHODO-PRODUCTION-ART-ONLY.tar` — SHA-256 `f777cc049102b27d71e0cb8c31a0900d9e1497dc90aec0f440ee48686f1c5797`
- Source inventory — 5,372 PNG files

## Target worktree

```text
/Users/anthonyguy/SHADOWCLASH.1.0*2/SHODO-EDITION
```

Server `http://127.0.0.1:9101/` is isolated to this worktree. `SHEET_V=672` is the production-only safety baseline. The earlier 97-cell Oni import from two other worktrees has been removed; its scripts, evidence, and handoff package were moved to Trash. Oni currently uses an eight-cell fallback rebuilt directly from the production `spectral-founder-locked-model-360-8v-v4-back-mounted-weapons` row, keyed to true alpha so its parchment card cannot render. No forbidden art is live while the full production rows are implemented.

## Implementation rules

1. Rebuild and route from production frame rows only. Never preserve an old runtime cell merely because an alias already points to it.
2. Use all authored beats in a selected row in their documented reading order. Do not replace an eight-frame row with two repeated cells or idle aliases.
3. Remove connected parchment, gray, white, or black card backgrounds to true alpha. No visible rectangle or background card may survive in game.
4. Keep one shared scale for the whole animation row. Never normalize each beat independently; crouches, rolls, jumps, contacts, smears, and follow-throughs are supposed to change pose height.
5. Grounded frames are foot-anchored to each manifest's `footY`. Preserve authored aerial lift only through the existing gameplay route; do not double-count height in both art and physics.
6. Cel animation cuts between frames. No cross-fades, body stretching, or procedural replacement art.
7. Use the shared `keyedShodoCell()` → `drawShodoFrame()` rendering boundary. Do not introduce a raw body-sprite `drawImage` path.
8. Do not change hitboxes, damage, move duration, physics, or input timing as part of this art implementation.
9. Do not regenerate art. If a move lacks a production row, report the missing row instead of filling it from an old sheet.

## Story Bible display heights

The edition's shared display multiplier is 1.75. These are the required neutral heights after that multiplier:

| Fighter | Base | In-game |
|---|---:|---:|
| Oni | 87.5 px | 153.1 px |
| Mokurai | 75.0 px | 131.2 px |
| Executioner | 72.5 px | 126.9 px |
| Exile | 72.3 px | 126.5 px |
| Kael | 70.0 px | 122.5 px |
| Tsubasa | 69.6 px | 121.8 px |
| Ember | 69.3 px | 121.3 px |
| Shin | 66.6 px | 116.5 px |
| Mizu | 62.4 px | 109.2 px |

## Required checks before Anthony reviews

```sh
cd '/Users/anthonyguy/SHADOWCLASH.1.0*2/SHODO-EDITION'
python3 tools/check_shodo_roster.py
node tools/check_zero_legacy.mjs
node tools/check_first_form_gate.mjs
python3 tools/sprites/key_sheet_cells.py selftest
```

Also film consecutive live frames from the real input path for every newly routed row and visually inspect them at `:9101`. Static alias checks alone do not prove smooth movement, correct scale, stable footing, or removal of visible frame boxes.
