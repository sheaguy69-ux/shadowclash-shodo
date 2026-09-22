# Shodō Roster Scale and Motion Specification

## Goal

Ship an isolated first-form edition in which every playable character uses only approved Shodō cells, renders at the Story Bible silhouette hierarchy, and moves without missing-frame fallbacks or blank/dead cells.

## Current defects

- Port `9101` still serves the mixed packing tree, not this standalone edition.
- The clean export contains 500 non-empty, non-legacy cells, but its baseline filter removed required core aliases.
- Executioner, Mokurai, and Oni have no neutral Shodō alias in the clean manifests, so the runtime can fall back to unrelated cell `0`.
- Existing upright Shodō cells render below canon; Shin's current exported idle is the largest error.
- Approved eight-frame source boards already exist under `art/shodo-source`, so new generation is not justified unless motion review finds a transition that those boards cannot supply.

## Canon screen heights

| Fighter | Height |
|---|---:|
| Oni | 87.5 px |
| Mokurai | 75.0 px |
| Executioner | 72.5 px |
| Exile | 72.3 px |
| Kael | 70.0 px |
| Tsubasa | 69.6 px |
| Ember | 69.3 px |
| Shin | 66.6 px |
| Mizu | 62.4 px |

Mokurai must stand 2.7 px above Exile. Executioner remains the visibly tallest of the original six. Oni is the only towering boss silhouette.

## Packing and motion rules

- Preserve `art/shodo-source` byte-for-byte. Generated runtime atlases may only receive appended cells until the final clean export.
- Use one uniform scale for each fighter and one shared crop/scale within each animation sequence. Never normalize individual attack beats independently.
- Anchor grounded cells at `footY`. Preserve intentional airborne lift and crouched/compressed poses.
- A fixed transparent canvas margin is allowed for stable feet and uncropped attacks. No routed cell may be blank, clipped, or contain a tiny figure lost in avoidable transparent space.
- Use the approved eight-frame boards before generating anything. A move must read as anticipation, acceleration, contact/smear, follow-through, and recovery; add in-betweens only when an approved board cannot satisfy that sequence.
- Cel animation cuts directly between frames. No cross-fades, runtime body stretching, or per-fighter rendering fork.
- First form only: no `f2_`, `hb`, or `gk` playable-character aliases or cells.

## Delivery sequence

1. Add a failing roster gate for canon height and required core routes.
2. Build scale-correct review strips from approved source boards without changing runtime atlases.
3. Present the strips and grade table to Anthony.
4. After image approval, append and repoint the selected cells, then compact to a fresh zero-orphan atlas.
5. Verify static gates, route probes, and consecutive live filmstrips.
6. Rebind `9101` from the mixed packing tree to this standalone Shodō edition and verify `/whoami` before opening the game.

## Acceptance criteria

- Nine fighters match the canon heights within 0.5 px on their neutral reference cell.
- Every fighter has intentional Shodō idle, run, block, hurt, jump/fall, dodge/roll, and knockdown/recovery coverage where the engine requests it.
- `node tools/check_zero_legacy.mjs --strict` passes with zero orphan and zero blank cells.
- The roster gate reports no cell-0 fallback, prohibited second-form alias, clipping, or scale-order inversion.
- Live filmstrips show stable feet, stable identity/weapon, and complete anticipation-to-recovery motion.
- `http://127.0.0.1:9101/whoami` identifies this repository before review.
