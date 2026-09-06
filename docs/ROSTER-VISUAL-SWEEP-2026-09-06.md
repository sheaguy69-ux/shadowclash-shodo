# Roster visual sweep — September 6, 2026

Owner requested a full sweep on SHODO-EDITION/:9101, particularly Mizu attack size, all nine run cycles, Oni's restrained gray aura, clipped Oni/Exile artwork, and Exile disappearing at walls. Standing owner authorization covers reviewing and fixing the roster without repeated approval. Current Shodo proportions remain authoritative.

## First correction — SHEET_V720

- Shared `drawSprite` registers the visible wall-facing edge of the selected cell against the fighter's physical contact edge. It works for both arena edges and interior stage walls. Exile's wall ink occupies raw x28–129 inside a480px cell; centering the padded cell had put her completely offscreen. Shin had the same complete disappearance; six other fighters were partially cut by the viewport.
- Mizu: uniform XY calibration for eight existing move families, 50 cells total: block/hurt1.22, grab1.10, grabbed1.20, special1.25, gsup1.15, aneu1.10, bothrust0.90. Body/head reviewed against current idle, not normalized by weapon-inclusive bounding-box height. Bothrust214–220 and staffspin221–227 are right-authored and now receive the manifest mirror correction. Shared body/copy/flash scaling remains in use.
- Oni's body receives a restrained9px ash-gray Canvas shadow around the shared Shodo silhouette. It does not change source pixels or hit-flash rendering.

Checks: `OUT=media/roster-sweep-20260906/run-before python3 tools/check_roster_visuals.py` passes36 outer/interior visibility cases and18 consecutive real DOM-key/rAF runs. Baseline Exile and Shin had0% visible wall ink; current all-nine outer cases exceed98%. `OUT=media/roster-sweep-20260906/compass720 node tools/check_direction_compass.mjs` passes882 direction samples including real wall contact, attacks, release and wall kicks. The live run traces reach all eight stride cells in both directions with no skipped cells.

This is an interim correction, not a claim that the art sweep is finished. Current run cadence and source clipping remain under review. `media/roster-sweep-20260906/` contains before/after boards, manifests and original source reconstructions. None of the experimental source extractions or generated cleanup boards has been packed at720. Some experimental masks erase highlights, retain paper pockets or detach weapons; those are rejected until corrected.

Mizu follow-up: four attack-tier live captures (24 transitions) pass in `mizu-live720/`. Ground-special launch/recovery, heavy launch and airborne Light transition strips inspected; calibrated heads remain near the current idle/jump size. Nine-sheet geometry guard and `git diff --check` pass.

## Original-art recovery — SHEET_V721

Appended46 Oni and55 Exile cells. Original502/322-cell RGBA prefixes are unchanged. Repointed every alias of each restored pose, preserving source direction and uniform source scale. Oni idle/guard/hurt/getup/light/low sweep/run and Exile light/heavy/guard/hurt/jump/getup/slide/low sweep/run are restored from reconstructed sources; Exile run uses the inspected built-in background-cleanup candidates. No animation timing changed. Per-cell registration, source mappings, rejected candidates and12-dimension review are in media/roster-sweep-20260906/{packed721.json,qc721.json,QC721.md}.

36 wall visibility cases,18 real run loops and9 sheet geometry checks pass. Both repaired live run strips reviewed: complete bodies throughout, full Exile sickle/chain/weight, original shared Shodo contour. Exile passes9,006 independent picker cases and five real jump arcs after updating the inspected flight-cell fixture. More clipped attacks across the roster remain under repair; this is not the end of the full sweep.
