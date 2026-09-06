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

## Further source recovery — SHEET_V722

Appended101 reviewed cells across six fighters: Mokurai32, Oni36, Exile16, Executioner11, Tsubasa4, Kael2. Recovers cut heads, limbs, weapons and crouch/landing silhouettes from the original art. Kael's two hood repairs replace only709/714 missing cloth pixels from the aligned original sources; all pixels outside those masks are unchanged. Current pose order and source-family scale are retained. Original atlas prefixes are RGBA-identical.

Pre-pack grades, hashes, selected beats and mappings: `media/roster-sweep-20260906/more/{QC722.md,qc722.json,packed722.json}`. Rejected panel-border and source-clipped candidates are excluded. Remaining source cuts still need repair; this is an interim checkpoint.

Live review found right-authored attack families with missing mirror metadata: Mokurai palm Light, Exile shoulder throw, Tsubasa forward normal and Oni forward spearhand. Corrected the entire active family, including unreplaced sibling cells, and added independent fixtures. Mokurai guard's test fixture also now recognizes its eight appended right-authored cells.

Checks: nine-sheet geometry,882 compass samples plus32 ground-family mirror fixtures,36 wall-visibility cases,Exile9,006 picker cases and five real jump arcs. Four fighters pass all four attack tiers/96 live transitions in `live722-final/`; additional real directional-input captures cover Oni/Tsubasa forward Light and Kael forward Heavy/down Special. No combat timing, damage, physics, shared Shodo rendering or visible CPU-browser changes.

## Selected attack-edge repairs — SHEET_V723

Appended26 graded cells: Exile4, Mokurai8, Oni13, Shin1; original decoded atlas prefixes unchanged. Source recovery restores complete wire/katana/chain edges. Built-in imagegen restores two Oni spearhand rear legs, Shin's clipped wire-release leg, and Mokurai's medium-row border cleanup. Current head/body scale and shared Shodo rendering retained. Pre-pack review, hashes, exact mappings and prompts: `media/roster-sweep-20260906/more/{QC723.md,qc723.json,packed723.json,prompts723.json}`.

Corrected independently viewed authoring directions across related families. Shin's source mixes left-authored ready/settle220/221/227 with right-authored release222/378/224–226; live review caught and corrected that distinction. Oni's eight planted spearhand poses use measured existing footAdj metadata; no scale or combat timing changes.

Verification: nine-sheet geometry,882 compass samples plus explicit authored-direction fixtures,36 wall visibility cases,96 live transitions across four fighters. Both normal and alternate-mode input sweeps drive648 presses each with no dead inputs/errors. Additional real forward-input filmstrips cover Shin/Oni/Exile; Oni wire binds and three follow-up paths captured with controlled bind setup and actual key events. The old wire driver has five stale expected-family assertions (including neutral conversion now explicitly slice); its actual bind/damage checks pass. Exile forward Special legitimately enters grapple JUMP, outside the generic capture's attack-state expectation; the consecutive strip shows a complete visible body.

Full sweep continues. Anthony specifically rejected the run poses for repeating the same leading leg. New Exile/Oni alternating-stride studies are review-only and not part of723. Earlier run cleanup/cadence checks did not establish correct leg alternation; do not treat those checks as proof of natural gait.
