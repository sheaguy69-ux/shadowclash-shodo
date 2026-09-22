# ONI + THE ROSTER — EVERY PACKED CELL THAT NEVER REACHES THE SCREEN

**2026-08-13.** Produced by `tools/audit_cell_coverage.py`: every input driven in the
live game, the DRAWN cell recorded every frame, diffed against every cell on the sheet.
Nothing here is read off the source — the source lies, because frame keys are built at
runtime.

## COVERAGE TODAY

| fighter | cells drawn | note |
|---|---|---|
| Oni | 222/293 | **clean — 0 orphan rows** |
| Executioner | 172/298 |  |
| Shin | 179/261 |  |
| Tsubasa | 177/298 |  |
| Mizu | 165/192 |  |
| Ember | 164/224 |  |
| Kael | 158/209 |  |
| Exile | 79/114 | small sheet; her grabs are Tier D |
| Mokurai | 76/212 | lowest on the roster — see Tier D |

⛔ **READ THIS BEFORE ACTING ON THE NUMBERS.** The sweep is calibrated against **Oni**,
who is the only fighter it has been tuned and double-run for. For the other eight this is
a FIRST PASS, and on Oni alone it produced seven separate FALSE orphan reports about art
that was fine — wrong distance, no stamina, keys vs physKeys, dummy in the way, foe never
airborne, up-moves in mid-air, round clock expiring. Every fighter below needs the same
calibration before their numbers are quotable. That is what the tiers are for.

---

## TIER A — DEAD BY ITS OWN NAME. Delete these. (8 rows, 18 cells)

The sheet itself says so. No decision needed.

- **Executioner** — `light1_old` (1), `light2_old` (1), `light3_old` (1), `light4_old` (1), `light5_old` (1), `xcfour_old` (6), `xcthree_old` (6), `xstab2_headless_DO_NOT_USE` (1)

## TIER B — THE ORIGINAL 43-CELL ROWS, SUPERSEDED BY YOUR BOARDS (66 rows, 176 cells)

`kneel` `run` `roll` `jump` `light` `heavy` `heavy_i` `attack_body` `special` — the
pre-board originals, on nearly every fighter. **Confirmed on Oni**: his `light1-5` is dead
because `glneu1-6` off MASTER-LIGHT-DIR replaced it, his `jump1-3` because `ajump1-6` did.
Sheets are append-only, so the originals stay as bytes. Each still needs its successor
named once before it is recorded, but none of these is a bug.

- **Ember** (28 cells) — `attack_body`(6), `heavy`(3), `heavy_i`(5), `jump`(3), `kneel`(1), `light`(5), `roll`(1), `run`(2), `special`(2)
- **Executioner** (37 cells) — `attack_body`(6), `heavy`(3), `heavy_i`(5), `jump`(3), `kneel`(1), `light`(5), `roll`(1), `run`(2), `special`(7), `xlight`(4)
- **Exile** (13 cells) — `heavy_i`(5), `jump`(3), `kneel`(1), `kstomp`(1), `roll`(1), `xcrouch`(1), `xlight`(1)
- **Kael** (33 cells) — `attack_body`(6), `heavy`(3), `heavy_i`(5), `jump`(3), `kneel`(1), `light`(5), `roll`(1), `run`(2), `special`(7)
- **Mizu** (13 cells) — `attack_body`(6), `heavy`(3), `kneel`(1), `roll`(1), `run`(2)
- **Mokurai** (26 cells) — `air`(3), `arake`(2), `bcrouch`(1), `bheel`(2), `kheel`(1), `kneel`(1), `kpush`(1), `kstomp`(1), `ksweep`(1), `light`(5), `mwall`(2), `sit`(3), `spurn`(2), `xcrouch`(1)
- **Shin** (16 cells) — `heavy`(3), `heavy_i`(5), `idle_stance`(1), `jump`(3), `kneel`(1), `roll`(1), `run`(2)
- **Tsubasa** (10 cells) — `heavy`(3), `jump`(3), `kneel`(1), `roll`(1), `run`(2)

## TIER C — FORM 2 (22 rows, 134 cells)

Tsubasa's second form is the 8 pages already on the books as owed, and Shin's is partly
built. This is unfinished work, not broken wiring.

- **Shin** (42 cells) — `f2_air_`(6), `f2_clow_`(6), `f2_csweep_`(6), `f2_heavy1_`(6), `f2_heavy3_`(6), `f2_light2_`(6), `f2_light3_`(6)
- **Tsubasa** (92 cells) — `f2_air_`(6), `f2_block_`(6), `f2_clow_`(6), `f2_crouch_`(6), `f2_dash_`(6), `f2_dashcut_`(6), `f2_heavy1_`(6), `f2_heavy3_`(6), `f2_jump_`(6), `f2_land_`(6), `f2_light2_`(6), `f2_light3_`(6), `f2_parry_`(6), `f2_roll_`(6), `f2_run_`(8)

## TIER D — WIRED IN THE ENGINE, NOT REACHED BY THE SWEEP (37 rows, 207 cells)

⚠️ **The largest tier and the least trustworthy.** Every row here IS named by the engine,
so the art has a home — the probe just could not pay for the input. Known causes already
proven on Oni: karma/meter the sweep never builds, long holds, stance chains, and moves
that need the OPPONENT in a particular state.

Two examples that make the point: **Mokurai's** whole kit is karma-gated and stance-driven,
which is why he reads worst on the roster at 76/212 — that is the ruler, not 39 dead moves.
**Exile's `xgrap` (10 cells)** is her air grab, which was wired and verified live at
SHEET_V 390; the sweep simply never gets a foe airborne inside her grab window.

**Nothing in this tier should be touched until the sweep is calibrated per fighter.**

- **Executioner** (69 cells) — `xcdownh`(6), `xcentry`(6), `xcfwdh`(6), `xcthrust`(6), `xcuph`(6), `xcut`(5), `xiai`(5), `xlow`(5), `xreprisal`(6), `xrise`(3), `xsky`(6), `xslip`(6), `xtsuki`(3)
- **Exile** (17 cells) — `xgrap`(10), `xroll`(4), `xthrow`(3)
- **Mokurai** (121 cells) — `blash`(6), `bpray`(6), `bring`(6), `btoll`(3), `cguard`(6), `crack`(6), `crefl`(6), `dbell`(6), `feint`(6), `gravel`(6), `hhalo`(6), `hidle`(6), `hpalm`(6), `lbell`(6), `meats`(6), `mmed`(5), `mthrow`(3), `run_clean`(8), `scut`(6), `snarew`(6), `unmade`(6)

## TIER E — NO REFERENCE ANYWHERE IN THE ENGINE (11 rows, 25 cells)

The Oni-shaped bug: packed art no line of code names. These are the real candidates for
the treatment his directional lights and bo staff just got — **they need INPUTS, not
redraws.**

- **Ember** (15 cells) — `espec1_v`(3), `espec2_v`(3), `espec3_v`(3), `espec4_v`(3), `espec5_v`(3)
- **Executioner** (1 cells) — `heavy_smear`(1)
- **Kael** (5 cells) — `kcut`(5)
- **Mokurai** (4 cells) — `canon_beads`(1), `canon_idle`(1), `canon_kick`(1), `canon_palm`(1)

---

## WHAT I RECOMMEND, IN ORDER

1. **Tier E first** — 25 cells with no code behind them at all. Same job as Oni's, small.
2. **Tier A** — 18 cells the sheet already labels dead. Delete or record them.
3. **Calibrate the sweep per fighter** so Tier D collapses. On Oni that work turned 71
   reported orphans into 0, and every one of those 71 was the tool being wrong.
4. **Tier B** — name each successor once, then record them. Bookkeeping, not repair.
5. **Tier C** — Form 2 is owed art, and it is a scope decision, not a fix.

**Oni is finished.** 222/293 drawn, zero orphan rows, every dead cell accounted for in
`tools/sprites/frame_coverage_allow.json` with a written reason.
