# Handoff — frame-by-frame animation fluidity (Codex lane)

**Status:** owner-requested 2026-09-23. Tree `SHODO-EDITION`, branch `shodo-edition`, HEAD `30077de`,
`SHEET_V 869` (line anchors below are from that HEAD and drift; grep the symbol), served on `:9101` (`curl -s localhost:9101/whoami` before you trust anything).
**Rulebook:** `AGENTS.md` (106 lines). Read it first. §0 applies to every step below: show, get
the yes, do it, show what happened. Not a plan for ten — the next one.
**Your skill:** `~/.codex/skills/2d-anatomy-and-frame-staging-expert/SKILL.md` is the owner's own
frame-staging standard (keys → breakdowns → in-betweens, exposure vs spacing, smears, review the
moving sequence at native size, `frame_breakdown.json` per sequence). It is the authoring law for
every row in this handoff; this file only says which rows, in what order, and how they land.

---

## 0. What "stiff" is, measured, and what has already moved

Diagnosis (Sep 11, read off the engine, not the art):

| cause | where it was | state today |
|---|---|---|
| every cell held the same length (run 8 × 41 ms, idle 1 cut / 667 ms, 8-cell attacks 8 equal slices) | `attackCellIndex`, RUN case, IDLE case | **fixed in engine** — `RUN_HOLDS_8` (`web/index.html:13296`), `ATTACK_EXPOSURES_8` (`:12330`), cosine idle breath 3.2 s. Landed in `5a7293c`. |
| zero transition art: turn 0, run-stop 0, jump squat 0, land 1 cell / 80 ms | manifests | **wired, not drawn** — `turn1`, `jsquat1..2`, `land1..3`, `skid1..2` exist on the six but every one ALIASES a taunt / roll / crouch / getup cell. `transitionFrame()` (`:13279`) plays them; `e64e1b1` routes the dash exit through the skid. |
| velocity 0→full→0 in one tick, facing flips in one tick | `handleMovement` | **stays** — footsies law (`docs/FOOTSIES-PHYSICS.md`). The BODY shows the brake/turn; the sim does not slow. Do not touch. |
| squash & stretch | `drawSprite` | **wired, event-scoped** — `hitSquashT` 0.8y / 1.25x on damage (`:15512`), `landSquash`, per-tier `lunge`/`attackStretch` FEEL curves (`:2328`). The August removals were of ALWAYS-ON warps. Never add a deformation that does not return to identity. |
| poses evenly spaced across a move (linear spacing = robotic) | the boards | **open — this is the art work.** Cells bunch at the ends of an action (ease in / ease out), one smear across the fast middle. Nothing in the engine can fake spacing. |
| rows that are two names for one drawing, or six slots on three drawings | manifests | **open — see `ROW-INVENTORY.md`.** A repeat or an alias is a slot that plays nothing new. |

The engine side of "fluid" is done. What is left is drawings and per-row exposure authoring.

---

## 1. Definition of done, per row

A row is done when ALL of these hold, in this order:

1. `frame_breakdown.json` exists for the sequence (your skill's schema), and every in-between
   in it was placed for arc / weight / near-far order — not the geometric midpoint.
2. No repeated cells inside the row, unless the repeat is a hold that is ALSO authored in the
   row's exposure (§4). `inventory.py` reports zero `Nc/Mu` for that row.
3. Three size tools on the touched fighter, spread ≤ 8 %, ruler named (ink-area median /
   eye span — never bbox height): `tools/sprites/check_row_scale.py` (`selftest` first),
   `tools/sprites/eye_scale.py`, `tools/sprites/gate_fragments.py`.
4. Extraction gates per cell: art-loss = 0 measured in place, halo ring p99 at the stage
   value, one connected component. (`tools/sprites/key_sheet_cells.py selftest` proves the
   keyer; the numbers come from your extraction run.)
5. A filmstrip of CONSECUTIVE live ticks at native size, BOTH facings, centre and at the wall,
   from the real input path — `tools/capture_roster_transitions.mjs` (drives `KeyD`/`KeyA`/
   `KeyW`/`KeyF…` through `KeyboardEvent`, steps `gameLoop(t)` by hand). Stills and numeric
   alignment do not certify motion; report visual defects separately from the numbers.
6. The owner said yes to that filmstrip, and an `APPROVAL.md` sits beside it naming fighter,
   rows, date (AGENTS.md §3.6). Search the ~160 existing approval records BEFORE asking:
   ```bash
   F=ember; { find art media -iname "*approved*" -iname "*$F*"; find media -iname "APPROVAL*" | xargs grep -ril "$F"; } | sort -u
   ```
7. Gates green after the pack: `tools/check_shodo_roster.py`, `check_zero_legacy.mjs`,
   `check_first_form_gate.mjs`, `check_run_cells.mjs`, `check_drawn_speed.mjs`,
   `check_air_art_holds.mjs`, `check_jump_commit.mjs`, `check_air_no_ground.mjs`,
   `check_recovery_floor.mjs`, and `python3 tools/build_runtime_sprites.py --check`.
8. `SHEET_V` bumped in the same commit as the sheet, runtime pack rebuilt
   (`python3 tools/build_runtime_sprites.py` — any manifest edit invalidates
   `sourceManifest` at `:12237` and silently drops the fighter to the raw strip).

"It builds" is not a step on this list.

---

## 2. The clock you are drawing against

Frames are 60 Hz GAME ticks; `COMBAT_TEMPO 1.2` (`:1640`) makes one tick ≈ 13.9 ms of wall
time. Hitstop crawls the sim to 6 % and eases back over `HITSTOP_EASE_T 0.06`. Gravity is
`-16.5` (`:943`, = 1650 px/s²): a plain jump is ~43 wall frames / 0.72 s at a 143 px apex.

| moment | engine constant | what plays | budget |
|---|---|---|---|
| run loop at full speed | `animPhase += dt·min(3,|vx|/150)·cycle` (`:5408`, shared by RUN and WALK) | 8 cells in 333 ms; `RUN_HOLDS_8` holds contacts 53 ms, passes 33 ms | draw the Williams 8: contact / down / pass / up × 2 legs, arms back (ninja sprint) |
| walk | `WALK_CYCLES 1` (`:3329`), art-gated on `walk1` | one full loop then the run; length = cycles / min(3,|vx|/150) | 8-beat true loop, every beat equally strong (animPhase never resets) |
| jump squat | `JUMP_SQUAT 0.05` | `jsquat1` then `jsquat2` in the last half | 2 drawings: half-bend arms back → full compress heels lifting |
| landing | `LAND_T 0.15`, only after a real fall (`landHard`) | `land1..3` one-shot | 3 drawings: impact squash → overshoot taller than idle → idle settle |
| run-stop | `SKID_T 0.10`, facing the run (`skidDir`) | `skid1` first half, `skid2` second | 2 drawings: lean back, front foot planted → upright recover (no dust in the cell; FX are engine draws) |
| turn | `TURN_T 0.07` on a grounded visual-facing flip | `turn1` held | 1 drawing (the picker reads `turn1` only): head leading, square-on front view |
| light / medium / heavy / special | `attackAnim.dur` 160–560 ms; paced off the LIVE hitbox window by `rosterAttackFrame` (`:12486`) when the move has `strikeWindows`, else `ATTACK_EXPOSURES_{5,6,8}` or a per-row `track` | 8 cells | anticipation on twos/threes, the cut on ones or ONE smear, contact and follow-through held, settle to `F.idle` |

Two facts that change how you draw:
- **Attacks with hitboxes are paced by the hitbox, not by a table.** The levers are
  `ROSTER_CONTACT_POSES` (`:12461` — which cells ARE the contact, per fighter id) and the
  hitbox duration. A drawn smear must sit at the cell index the window reaches on the cut.
- **Tracks exist for five fighters, none for Shin, Mokurai or Exile.** `ANIM_TRACKS` (`:12403`)
  holds per-move tracks for Tsubasa, Kael, Executioner, Mizu and Ember; `attackCellIndex`
  (`:12500`) applies one ONLY when its length equals the row's cell count, else the row runs the
  global `ATTACK_EXPOSURES_8`. Check the length before trusting one. Authoring a track per touched
  row is the cheapest fluidity win on the list and needs no art.

---

## 3. Order of work

Each item is one owner-gated step. Ask, land, show, next.

**Owner order, Sep 23:** work through Mizu, Shin, Mokurai, and Exile first.
Tsubasa, Ember, Executioner, and Kael are the final four fighters. Anthony may
redesign the first three and plans a new move set for Kael. Apply this order to every
row category below; wait for the relevant design and move decisions before preparing
the final four. Mizu launched-hurt was the first completed pilot at SHEET_V 871;
Shin is next. Recheck the latest approved
references when each deferred fighter comes up.

**Kael planned move-set direction, Sep 23:** Anthony plans parry-focused unique
mechanics. Light attacks use his short blade; medium attacks use his long blade;
heavy attacks and specials use both blades. Treat this as design direction pending
the complete move set and mechanic definitions, not as authorization to change
combat, attack art, hitboxes, or timing now. Replan Kael's attack rows against
the approved new move set when his deferred turn arrives.

### 3.1 The three rows he already briefed
`art/production/handoff/SHODO-WALK-LAUNCH-NINJAJUMP-BRIEF-2026-09-15/` — `START-HERE.md`,
`PROMPTS.md` (the shared law, incl. the canon table), `prompts/<fighter>.md` (paste-ready per
fighter), `refs/`, `BOARD-SPEC.md`, `ENGINE-CONTRACT.md`, `MEASUREMENTS.md`. Do not re-brief;
generate the missing per-fighter prompt files in the same shape.
- **walk `walk1..8`** — packs and the WALK tier switches on by itself (`3242e26`).
- **launched-hurt** — Mizu now has owner-approved `airhurt1..8` source art in
  `art/shodo-source/mizu/mizu-airhurt-fluidity-v1/`, packed into cells 256–263;
  her selector reads eight measured velocity bands. Other fighters still use
  `airhurt1..3` borrowed from their throw-hold drawings. This row plays on every air hit.
- **second jump `njump1..8`** — curl into a ball; band on `flipTimer`, never `vy`; owner wants it
  from Blender + his motion lane, not stills. Gate in `spinFlip` (`:15558`) with a `drawnFlip`
  the way `drawnRoll` (`:15551`) already kills the procedural roll spin.

### 3.2 Draw the four transitions for real (they are salvage aliases today)
Most-seen first: **land** (every jump) → **turn** (every crossup) → **skid** (every run
release) → **jump squat**. Per fighter, work Mizu, Shin, Mokurai, and Exile before
Tsubasa, Ember, Executioner, and Kael. Mokurai and Exile have NO transition keys yet; wire
them when their turn arrives. Reference for each: that fighter's approved idle board plus the
board that already holds the limb direction (jump-land board for squat/land, run board for
skid). Cell budgets are in §2. Repoint the existing keys; strip the alias only after the new
cell is live (old art leaves in two steps).

### 3.3 Kill the repeats and aliases in the air
From `ROW-INVENTORY.md` (per-slot detail in `DRAW-LIST.md`): `dive` is 6 slots on 3–4 drawings on all eight; `jflight` 6/4–5; `lock` 6/3–4;
`wallthrow` 6/3. Each is a slot that shows nothing. Draw the missing beats (apex hang, the
tuck opening, the plunge stretch) or author the hold in the row's exposure and delete the
duplicate slot — never leave a silent repeat.

### 3.4 Attack rows: spacing, smears, per-row exposure
Start with each fighter's LIGHT (most thrown), then MEDIUM. For each row:
1. Read the live pacing first: which cells the window lands on (`ROSTER_CONTACT_POSES`),
   startup/active/recovery from the move (`docs/FOOTSIES-PHYSICS.md`, `DIR_MOVES` `:3009`).
   Art changes do not authorize combat changes.
2. Re-space, don't add: anticipation cells bunched near the coil, ONE directional smear on the
   cut that bridges the actual hand/weapon path, contact drawn at full extension, follow-through
   overshooting, settle back to the approved model. Eight drawings is a choice, not a quota.
3. Author the exposure: a `track` on the move if it has no hitbox window; otherwise adjust
   `ROSTER_CONTACT_POSES` so the smear cell is the one the window reaches.
4. `frame_breakdown.json` beside the board.

### 3.5 Idle
`xidle` rows exist on everyone (4–12 beats) and the breath is eased. Lowest priority; only if
he asks.

---

## 4. Delivery and packing (what comes back from his generator, and how it lands)

- **One row per prompt, one board per row, ~1900–2000 px wide, figure faces LEFT, feet on one
  ground line, no card borders, no wall/floor/props, no text.** Same head size as that fighter's
  idle board. `BOARD-SPEC.md` in the walk brief is the spec; per-fighter cell aspect is fixed
  (Shin 1.41, Executioner 1.30, Mokurai 1.21, Exile 1.11, Kael/Mizu 0.94, Tsubasa 0.91, Ember 0.87).
- **Slice before packing.** `pack_keyed_board.py` globs `frame-01..08.png`. Always `--dry` first.
  It anchors scale on beat 1's ink area by default — right for a walk, WRONG for any launched or
  airborne row (beat 1 is the pop). Pass `--scale` from the fighter's idle or `--anchor` at the
  most neutral beat. ONE scale per row; never per-cell height flattening on locomotion / jump /
  roll / crouch rows.
- **Pose does not fit? `tools/sprites/grow_frame.py --down`.** Never shrink the fighter, never
  crop the pose. Growing a frame UP also moves `frameClear` / `weaponNoOutline`.
- **Never feed `pack_shodo_row.py` pre-keyed RGBA** — it white-composites and re-keys at
  min-channel ≥ 205 and punches holes. Direct premultiplied append instead.
- Sheets are append-only; originals byte-identical after every pack (`magick compare -metric AE`
  at the sheet's OWN width must read 0). Repoint keys; strip orphans as a separate, named step.
- Cel cuts only. No cross-fades, no runtime interpolation between cells.
- **No paid generation** (AGENTS.md §3.7). New cells come from the generator the owner drives.
  Your deliverable to him per row is: the prompt file, `refs/<fighter>-refs.png`, the cell
  budget, and `frame_breakdown.json` with the target exposures. Your deliverable back to the
  tree is the measured, gated, approved pack.

---

## 5. Canon you will be graded on (the concrete tier — AGENTS.md §2)

Executioner two eyes (front one a small wedge), ONE long sword · Mizu bo (splits to hanbō) ·
Shin ONE eye, wire + shuriken, bare hands · Tsubasa TWO tantō, no hood · Ember THREE claws per
hand, grey with grey eyes · Kael one long + one short sword · Mokurai bare bead-wrapped fists,
no staff · Exile spiked ball, red iris `#B94828`. Sprites are authored facing LEFT and
mirrored, so an asymmetric weapon swaps hands on a turn — that is correct; drawing it on the
wrong hand in a cell is not. Everything else (palette, timing, mechanics) is CURRENT: read it
to know what the game does today, never quote it back at him as a reason not to draw.

---

## 6. Lane protocol (this tree has four agents in one `web/index.html`)

- `python3 tools/lane.py start "Codex Shodo Edition"` (your lane is already open — `who`
  first). `lane.py claim <paths>` for everything you touch. Never `git checkout` a dirty file.
- **Never `git add web/index.html` whole.** `git diff web/index.html` first; if any hunk is not
  yours, stage a reconstructed blob (`git hash-object -w` + `git update-index --cacheinfo`).
  Never chain a status check and a commit in one command. A `SHEET_V` line you did not write
  is someone else's and travels with their sprites.
- Balance changes are their own commit. Art waits for his eye; engine work commits itself.
- Local commits only. Never push, merge, deploy. **Never kill `:9101`.**
- Other lanes' dirty files and commits are not your business — don't audit, correct, or
  message about them. If one genuinely blocks you, say so in one line and carry on.

---

## 7. Files in this folder

- `README.md` — this contract.
- `inventory.py` — re-run after every pack; it prints the row table.
- `ROW-INVENTORY.md` — generated at `SHEET_V 872`: per fighter, missing transition keys, rows
  with repeated cells, rows that alias another row, orphan-cell count, every row's cell count.
- `DRAW-LIST.md` — every drawing owed, per fighter, per row, with IDs, the cells each key borrows
  today, beat-by-beat pose specs and the queue. The checklist to work from.
