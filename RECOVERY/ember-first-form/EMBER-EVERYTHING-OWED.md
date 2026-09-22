# EMBER — EVERYTHING STILL OWED, BOTH FORMS

**Measured Aug 22 2026 at SHEET_V 592**, off `ember.png` / `ember.json` and the live
engine — not read off any earlier list. Every number here is reproducible:

```
python3 tools/make_finish_order.py     # regenerates the Form 1 queue from the sheet
node    tools/check_ember_keys.mjs     # every key read, every read row art-or-queued
node    tools/drive_real_input.mjs --name ember   # all 15 presses, both modes
node    tools/check_ember_air_matrix.mjs
node    tools/check_state_rows.mjs
```

---

## THE ANSWER: NO. Neither form is complete.

| | rows with art | still the deleted GREEN look | never drawn | owed |
|---|---|---|---|---|
| **FORM 1** (base) | 33 of 46 | 11 rows / 53 columns | 2 rows | **13 strips · 77 beats** |
| **FORM 2** (Ghost Killer) | **1** of ~15 | — | ~14 rows | **13 rows already DRAWN and unpacked, + 15 rows never drawn** |

**Form 1 is 86% done and the last 14% is 13 drawings.**
**Form 2 is one row.** `gk_air` is the only wrapped art on his sheet; press V and every
other button in the game still draws his first-form face. Shin's second form is 9 rows /
54 cells. Tsubasa's is 18 rows / 110 cells. Ember's is **1 row / 6 cells**.

The honest unit is the **COLUMN, not the key**: 216 columns, 215 live, **158 ash / 57
green**. Counting keys inflated it, because `ec` was `espec` seen twice.

---

# FORM 1 — 13 STRIPS, 77 BEATS

**Every strip: flat WHITE background, beats left to right, body 260px minimum crown-to-heel,
drawn FACING LEFT, no ground shadow, no background.** 362px of width per beat.

## The 7 that are genuinely new art

| # | row | move | beats | strip px | why it is owed |
|---|---|---|---|---|---|
| 01 | `kheel` | **Reverse Heel Kick** | 6 | 2172 x 724 | ONE cell for the whole move. Hits BEHIND him — the answer to this game's three cross-ups. |
| 02 | `epounce` | **Wall Pounce** | 6 | 2172 x 724 | ⛔ **ZERO cells.** Armored claw dive off the wall cling. Plays `sneu1..6` today — a different move entirely. |
| 03 | `ko` | **KO / death** | 6 | 2172 x 724 | ⛔ **ZERO cells.** Kael is the only fighter in the roster who owns this row. Ember dies playing the hurt stagger. |
| 04 | `wallslide` | **Wall cling** | 6 | 2172 x 724 | ONE cell. His identity move and the launch point for 02. The engine LOOPS `wallslide1..N`. |
| 06 | `aback` | **Reverse Air Rake** | 6 | 2172 x 724 | his back-air, the cross-up tool |
| 10 | `ehook` | **Ceiling Hook** | 6 | 2172 x 724 | up+Special, 460ms, vy -360 — his answer to someone already above him |
| 12 | `erip` | **Ground Rip** | 6 | 2172 x 724 | down+Special, LOW and TRIPS — how the shortest reach in the game (3) beats a high guard |

## The 6 that are a RE-CUT, not new art — the pose is already drawn

The boards return 148–214px bodies and the bar is 260px. **The pose is right; only the
size is wrong.** Redraw at strip size from the file named.

| # | row | move | beats | the pose is here |
|---|---|---|---|---|
| 05 | `sback` | Grave Hook Evisceration | 6 | `movesets/ms2-grave-hook-evisceration.png` |
| 07 | `espec` | Rabid Spiral Flense | **5** | `movesets/ms3-rabid-spiral-flense.png` |
| 08 | `echarge` | Phantom Maul Rush | 6 | `movesets/ms1-phantom-maul-rush.png` |
| 09 | `eheavy` | Cross-Body Double Rake — *Juji Tsume* | 6 | `shuko-techniques-4-6.png` (technique 5) |
| 11 | `eretreat` | Blindspot Flank Slash — *Usiro Tsume Geki* | 6 | `shuko-techniques-4-6.png` (technique 6) |
| 13 | `clawrend` | Leaping Pounce Strike — *Tobi Tora Geki* | 6 | `shuko-techniques-1-3.png` (technique 2) |

⛔ **`espec` is FIVE beats, not six** — the engine hardcodes `[espec1..espec5]`.
⛔ **`eheavy` is the only one that needs an engine line**: it is hardcoded to
`[eheavy1..eheavy4]` and the board draws six. One line, `rowCells(F, 'eheavy')`.

Everything else on this list is **pure art**. `kheel`, `ko`, `epounce` and `wallslide`
are already read as rows — pack them and they play, with no code change at all.

---

# FORM 2 — GHOST KILLER

**What the mode already does, mechanically:** the blind sense in `faceCx`, the DISARM on a
perfect Back+Special catch (0.035s window, takes the attacker's weapon, ends the round on
his last blade), the round reset, the V toggle and the tint. All live, all tested.

**What it LOOKS like: his first form.** `emberF2Frame` answers exactly one input.

| what | rows | cells | state |
|---|---|---|---|
| **PACKED** | `gk_air` | 6 | neutral air Light. The only wrapped art in the game for him. |
| **DRAWN, NOT PACKED** — the four directional Lights | `gk_fwd` `gk_back` `gk_down` `gk_up` | 24 | `lights/`, **two takes each**, needs a pick |
| **DRAWN, NOT PACKED** — the counter kit | 9 strips | 54 | `strips/`, needs slot assignment + 2 rulings |
| **NEVER DRAWN** | ~15 rows | ~90 | see STOP 2 |

## STOP 1 — 78 cells, ZERO generation. This is free art sitting on disk.

### 1a · the four directional Lights — you pick a take, that is the whole decision

Measured side by side in `TAKE-A-vs-B.png`; no take clips the 377px cell, so this is a
pose call, not a fit call.

| row | recommended | why |
|---|---|---|
| `gk_fwd` | **take A** | +23px median body, spread 10.4% vs 17.2% |
| `gk_back` | **take A** | +80px median body, spread 11.8% vs 17.2% |
| `gk_down` | **take A** | +46px median body; its 34px foot drift is the claw digging in |
| `gk_up` | **take B** | +46px median body and 1px foot drift against take-A's 19px |

⛔ **The strips face RIGHT** — every sprite in this game is authored facing LEFT.
`-flop` each **cell** after the cut; flopping the strip whole reverses the beat order.
Then `pack_ember_gk.py --row <fwd|back|down|up>`, plus ~6 lines in `emberF2Frame` so it
answers the grounded directional Lights the way it answers `gk_air`.

⛔ **These must stay `gk_*` and never `gl*`.** `dirCells` has no fighter gate, so `glfwd`
would draw the wrapped face in his FIRST form with nobody pressing V — and `drewDirLight`
reads the same three names to decide whether a press becomes a KICK, so packing them
would **silently delete his push, heel and sweep** along with their wallsplat, behind box
and low+trip.

### 1b · the nine counter strips — PROPOSED slots, yours to overrule

Nothing here is assigned yet. This is the mapping the beats themselves suggest:

| strip | proposed slot | reading |
|---|---|---|
| `gk-CATCH-sword` | **the DISARM** (back+Special) | the mode's whole point — but see ruling 1 |
| `gk-CATCH-dagger-deflect` | the disarm's whiff / deflect variant | spark, tumble, follow-through |
| `gk-CATCH-arm` | grab counter | traps the wrist, holds, strains |
| `gk-COUNTER-punch-to-leg-takedown` | `gk_down` Heavy | block → sweep → grounded takedown |
| `gk-WALLCLIMB-6beat` | `gk` wall cling | see ruling 2 |
| `gk-dash-rush-claw-slash` | `gk` fwd Special (the `echarge` slot) | crouch → lunge → shard burst |
| `gk-claw-thrust` | `gk` neutral Light | guard → wind → thrust → recover |
| `gk-claw-rake-combo` | `gk` neutral Light, second chain step | stance → raise → crouch → rake → sweep |
| `gk-low-crouch-thrust` | `gk` crouch attack | low stance → deep crouch → low thrust |

### ⛔ Two rulings only you can make, and both block packing

1. **`gk-CATCH-sword` ends with Ember HOLDING a sword.** His identity lock is *claws only,
   never a sword*. Catching and keeping an opponent's blade may be the entire point of a
   disarm mode — but that is a canon change, not a detail. The strip is archived unaltered
   either way.
2. **`gk-WALLCLIMB-6beat` has the wall drawn INTO the cell.** A world-oriented frame must
   not mirror by `facing` or the wall flips to the wrong side — it needs a per-cell `mirror`
   map. Worth knowing: it is the first real **side-profile grip pose** in this project. All
   nine current wall-cling cells across the whole roster are ground stances held midair with
   no grip and no wall, which is why both walls have always looked wrong. This fixes Ember's.

## STOP 2 — what "a real second form" costs, if you want it

Not defects. The router was **built** to fall through to Form 1 for anything undrawn, and
that is why the mode ships at all. These are the stopping points, and the choice is yours:

| stop | what the mode owns | rows | beats | precedent |
|---|---|---|---|---|
| **today** | one air Light | 1 | 6 | — |
| **STOP 1** | + 4 ground Lights + the counter kit | 14 | 84 | *free — art is on disk* |
| **STOP 2** | + neutral Light, 5 Heavies, 5 Specials, 4 air directionals | 29 | 174 | **Shin** owns 9 rows |
| **STOP 3** | + idle, run, jump, fall, crouch, block, hurt, roll, land | 38 | 228 | **Tsubasa's Sakate** owns 18 — "the mode owns its legs" |

**Recommendation: STOP 1 now**, because it is already paid for, and then only the
**neutral ground Light** and the **Back+Special disarm** on top — those two are what make
the mode read as a mode when you press V. The heavies and specials falling through to
Form 1 is a defensible look; a mode whose signature move draws the first form is not.

---

## THE ENGINE WORK — three items, and none of it is hard

| # | what | size |
|---|---|---|
| 1 | `eheavy` hardcoded `[eheavy1..4]` → `rowCells(F, 'eheavy')` so a 6-beat strip plays | **1 line** |
| 2 | `emberF2Frame` answers grounded directional Lights the way it answers `gk_air` | **~6 lines** |
| 3 | per-cell `mirror` map, only if the wallclimb strip is packed | small, and it is owed roster-wide anyway |

Everything else on both lists is art. `kheel`, `ksweep`, `kpush`, `ko`, `epounce`,
`wallslide`, `aback`, `sback` and the whole `gk_` family are already read as rows.

---

## NOT OWED — so nobody asks for these again

| row | why |
|---|---|
| `air1..3` | **DEAD.** Every reader is shadowed by a row he now owns; 15/15 air presses driven off the floor reach something else. Deleted SHEET_V 591. |
| `ec1..5` · `elaunch1..6` · `xblkhit` | **DELETED SHEET_V 592.** Never aliases — the engine reads *neither* name. `ec` was `espec`'s own columns under a second name, `elaunch` was `upatk`'s. |
| `kstomp` | live engine name, **unreachable on his sheet**: the kick tier only falls here when `F['k'+kind]` is undefined and he has all three. |
| `jump` `jump1` `jump2` | behind `F.roll ?? F.jump`, and `F.roll` is defined for him. Kept as the fallback (SHEET_V 591). |
| `roll` | his dodge draws `roll_1..6`. Kept as the fallback. |
| `light` `heavy` `heavy_i` `special` `attack_body` `espec*_v` | deleted SHEET_V 580 — zero readers. |
| `getup` / `getup2` | **nobody in the roster has these**, Oni included. Ember lying on the floor after a throw is a roster-wide gap, not his. |

⛔ **`kheel`, `kpush` and `ksweep` have no literal reference in the engine either — and all
three are LIVE.** They are built at runtime by `rowCells(F, 'k' + p.kickKind)`. That is why
`check_ember_keys.mjs` treats a name with no literal hit as a *candidate* and makes a human
name the lookup, instead of deleting it. Automating that scan would have deleted his kicks.
