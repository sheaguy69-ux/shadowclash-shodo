# SHODO-EDITION frame + facing + scale audit loop — state
# OWNER RULING Sep 1: this loop audits the SHODO-EDITION tree on :9101 (the GPT shodo
# frames). :9100 / SHADOWCLASH-RECOVERED is OUT OF SCOPE — never started, never touched.
# Canon heights = Story Bible (check_shodo_roster): oni 87.5 > mokurai 75.0 > exec 72.5 >
# exile 72.3 > kael 70.0 > tsubasa 69.6 > ember 69.3 > shin 66.6 > mizu 62.4 (x1.75 display).
# Checks per fighter: negspace / facing / wall / scale / functionality. READ-ONLY.

| fighter     | negspace | facing | wall | scale | functionality |
|-------------|----------|--------|------|-------|---------------|
| ember       | PASS 3px stray, 0 pockets, 0 captions | PASS (48,51,133,161 eyeballed LEFT) | PASS signs -1/+1 @x54/x816, 0 flips | PASS 69.3=canon, ink 201, scale .34138 | FAIL: neutral/up LIGHT draws idle (no light row; roster+probe agree); medium cells 166-168 baked border stroke h279 |
| executioner | PASS 23px stray, 0 pockets; cell 46 caption band = UNREFERENCED orphan | PASS (12 suspects eyeballed LEFT; 109=crescent FX) | PASS -1/+1 @x54/x816, 0 flips | PASS 72.5=canon, ink 270, scale .26654 | PASS w/ notes: 4 empty old-kit descriptors=dead code; heavy/light heuristic contradicted by live probes; runtime asserts all pass, 20 known 404s (portraits) |
| exile       | PASS 0 stray, 0 pockets, 0 captions | PASS art; FAIL cells 129-130 baked WALL stroke | PASS signs -1/+1 (engine); art FAIL see facing | PASS 72.3=canon, ink 162, scale .44085 | FAIL: medium cells 220-222 baked border fragments; up+Special = no hitbox + no unique art (design gap, owner call); 'fall' heuristic false (xjump arc live) |
| kael        | PASS 0 stray, 0 pockets; cell 166 caption = UNREF orphan | PASS (19 suspects eyeballed LEFT; wall 135-136 CLEAN, medium 183-190 CLEAN) | PASS -1/+1 @x54/x816 | PASS 70.0=canon, ink 171, scale .40462 | FAIL: neutral+Special (15dmg) and fwd+Special (18dmg) draw IDLE — kspin/ktrav rows have no art, no boards exist (2 signals: dead-row probe + moveset drew=empty) |
| mizu        | PASS 1px stray, 0 pockets, 0 captions | PASS (2 suspects eyeballed LEFT; wall 101-102 CLEAN, medium 157-164 CLEAN) | PASS -1/+1 @x54/x816 | PASS 62.4=canon, ink 162, scale .37818 | PASS: bo_thrust_sweep descriptor=dead code; heavy_i/ristaff/bolow/gsup all live since 675 (probe-verified) |
| mokurai     | FAIL: cell 147 (mpalm2, LIVE) pale ground plate under feet | PASS (0 suspects; mwall 186-193 CLEAN, medium 194-201 CLEAN) | PASS -1/+1 @x54/x816 | PASS 75.0=canon, ink 156, scale .48077 | PASS: 1 old-kit descriptor = dead code |
| oni         | PASS 0 stray/567 prot; pocket cell 109 = UNREF orphan | PASS (12 suspects eyeballed LEFT) | PASS -1/+1 @x54/x816; wall-row stroke stubs ~1px at cell scale, GPT redraw queued | PASS 87.5=canon, ink 155, scale .55732 | PASS w/ cosmetic: cells 159+174 (LIVE ghup8/sup8, special7) carry 1-2px detached ink flecks 60-68px above the body (invisible at game scale) |
| shin        | FAIL: idle row cells 78-80,83-85 full-width GROUND BAR (152px) baked under feet | PASS poses LEFT; FAIL wall 110-111 vertical stroke | PASS -1/+1 @x54/x816 | PASS 66.6=canon, ink 191, scale .34508 | PASS: taijutsu descriptor dead code; heavy heuristic false (hneu1-8 live, filmed 158-165); sneu2 cell 183 fleck = cosmetic |
| tsubasa     | FAIL: light row 8-15 baked grey ground MOUND (1000-1700px foot band, all 8 beats); medium 207/209/210 figure CLIPPED flat at x~212 + box fragment in 209; orphan 106 caption (unref) | PASS all LEFT (10 suspects eyeballed) | PASS -1/+1 @x54/x816; wall cells 93-94 clean | MINOR: idle ink 190 x .3625 = 68.9 vs canon 69.6 (0.4 under ember - ordering slip) | PASS: 3 empty descriptors = old-kit dead code |

## Findings log
- Sep1 ember: (1) NO NEUTRAL-LIGHT ART — ground neutral+Light and up+Light draw idle
  (probe `drew`=∅, audit_roster INVISIBLE RISK "light"). fwd/back/down lights draw the
  jump-alias cells. Candidate board exists unlabeled: ember-shodo-ghost-pounce-slash v1/v2.
  (2) medium row beats 4-6 (cells 166-168) carry a baked full-height border stroke
  (ink h=279 vs ~200 body; sheet_fixer +38% flags). Needs stroke-kill + repack from the
  approved war-wraith board. (3) engine animations.claw_rend descriptor: empty frames.
  (4) audit_runtime.mjs crashed on Chrome tmp cleanup (ENOTEMPTY) — infra flake, retry.
- Sep1 executioner: sheet_fixer +flags cells 19-50 ALL unreferenced legacy orphans
  (strip-pass fodder), incl. cell 46 caption band. audit_runtime needed 4 tool repairs
  (committed) — six-sheet invariant, timer window, watch-mode key ownership, rm race.
  audit_roster INVISIBLE-RISK heavy/light = heuristic (exec routes via xnuki/xjodan,
  proven drawing by 674/675 probes). Portraits 404 x20 confirmed again at runtime gate.
- Sep1 exile: wallslide/walljump cells 129-130 SHIP THE WALL STROKE (wall_kill missed
  her board's beats 3/6). Medium beats 4-6 (cells 220-222) carry card-frame fragments —
  SAME CLASS as ember medium 166-168: the standing-medium boards have mid-board frames
  the median-band detector missed. Check tsubasa 205-212 + mokurai 194-201 mediums in
  their iterations. up+Special spawns NO hitbox and draws the neutral special row
  (audit_specials '--' + probe agree) — empty kit slot, owner decision.
- Sep1 kael: neutral-special spinning finisher (kspin) and fwd-special travelling cross
  (ktrav) fire hitboxes but draw idle — NO boards exist for either. GPT-list candidates.
  His wall + medium rows are CLEAN (handoff ready-frames, no strokes/fragments). 7 empty
  old-kit descriptors + 5 INVISIBLE-RISK heuristics = noise (kdual/kcross/kxcut live).
- Sep1 mokurai: mpalm2 (cell 147, LIVE — his fwd-heavy bridge-hammer beat 2) stands on a
  pale ground-shadow PLATE that survived keying. Needs plate-kill + repack of that beat.
  mwall + medium rows clean. Facing zero suspects (symmetric monk). Fixer +flags 8-13 =
  six identical legacy cells, refs checked below.
- Sep1 oni: pocket cell 109 unreferenced orphan. Cells 159/174 LIVE but the detached
  bands are 1-2px flecks (sub-pixel on screen) — cosmetic, clean in the next repack of
  those boards. Old jump cells 105-111 unreferenced. All other +flags are FX-tall rows
  (staff/eclipse verticals, authored). Wall-row GPT no-wall redraw already queued.
- Sep1 shin: IDLE ROW (668-era story-bible strip) ships a full-width ground BAR in 6 of
  8 cells (78,79,80,83,84,85 — bottom band = full 152px body width at footY). His most
  visible frames. Needs bar-strip + repack from idle-owner-model v6 board. Wall cells
  110-111 keep the vertical wall stroke (same class as exile). Medium 190-197 clean.
- Sep1 tsubasa (FINAL fighter): whole LIGHT row (cells 8-15) ships the board's grey
  ground mound under her feet (loose-grey foot-band 1000-1700px vs ~0 on idle) — her
  most-used attack. Medium beats 3/5/6 (cells 207/209/210) are CLIPPED: flat vertical
  alpha cut at x~212 mid-cell (ready-cell crop boundary), 209 also carries a stray box
  fragment. Wall cells clean, facing clean, scale 68.9 vs 69.6 canon (minor — drops her
  below ember, breaking canon order). Orphan cell 106 unreferenced caption. AUDIT COMPLETE 9/9.

## FIX PASS (Sep 1, owner-approved "Yes, continue") — lands as SHEET_V 678
- shin: idle row repacked from idle-owner-model v6 board (198-205; old cells shipped a
  solid black card SLAB, not a thin bar); wall 206-207 stroke-erased.
- tsubasa: light 213-220 mound-stripped; medium REBUILT whole-board 221-228 (artist drew
  lunges CROSSING card borders — any card-sliced take clips; extract connected components
  off the keyed full board instead); scale 0.3625->0.3663 (canon order restored).
- exile: wall 225-226; medium4-6 227-229 (welded 3-side card frame + beige dust).
- ember: LIGHT ROW LIVE 174-179 (ghost-pounce-slash v2 frames 3-8, flipped to house LEFT,
  scale 0.61 ruler-median); medium 1+8 rebuilt from war-wraith v1-approved (180-181);
  medium 4-6 cleaned (171-173). OPEN: medium7 (169) ~35% over row scale (pre-existing);
  idle grey rock between boots left (inseparable from boots, possibly authored).
- mokurai: mpalm REBUILT 202-206 from bridge-hammer v1-approved (old row carried card
  frame + parchment mound and FLOATED ~60px — pack had anchored on the card corner).
- kael kspin/ktrav briefs -> docs/MISSING-BOARDS-FOR-GPT-674.md (GPT owed).
- Lesson: pack_shodo_row white-composites + re-keys — NEVER feed it pre-keyed RGBA
  (holes + resurrection of sub-205 bg); direct premult append instead (scratchpad
  append_rgba_row.py pattern).
