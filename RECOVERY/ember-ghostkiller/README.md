# EMBER — SECOND MODE: "GHOST KILLER"

**Owner ruling, Aug 20 2026:** Ember gets a second mode named **Ghost Killer**, and this
is its art. Same shape of thing as Oni's `mode2` (V toggles) and Shin's Form 2.

**Status: ARCHIVED, NOT PACKED.** Nothing here is on a sheet, no manifest key points at it,
`SHEET_V` did not move. Packing needs the owner's motion gate — montage + GIF at game fps +
the Doc-17 grade table — per the packing contract in `docs/ART-REGEN-HANDOFF.md` §5.

## What the mode is

Read off the frames, not from a brief: **Ghost Killer is a counter / disarm kit.** He catches
what comes at him — a thrown sword, a thrown dagger, a punch, a grabbing arm — and answers
with claws. He also climbs walls with them. Every strip is the ash-grey/black claw silhouette
from the new-look Ember, so the mode reads as the same fighter gone cold.

## The strips — `strips/`, 9 files, 2172×724, six beats each

| file | what happens across the six beats |
|---|---|
| `gk-CATCH-sword` | stance → a blade flies in → both claws catch it overhead → he holds it vertical → brings it down → ends **holding the sword** |
| `gk-CATCH-dagger-deflect` | stance → thrown dagger incoming → claws deflect it with a spark → it tumbles away → claw follow-through |
| `gk-CATCH-arm` | stance → claw thrust → an arm comes in → he traps the wrist → holds → strains against it |
| `gk-COUNTER-punch-to-leg-takedown` | stance → a punch comes in → crossed-claw block → sweep → **grounded leg takedown** → recover |
| `gk-WALLCLIMB-6beat` | six beats climbing a stone wall on the claws; **the wall is drawn into the cell** |
| `gk-dash-rush-claw-slash` | crouch → dashing lunge with speed trails → extended claw → shard-burst slash → recover |
| `gk-claw-thrust` | guard → wind-up → straight claw thrust with an impact burst → recover |
| `gk-claw-rake-combo` | stance → claw raised → crouch → forward rake → sweep → recover |
| `gk-low-crouch-thrust` | low stance → step → deep crouch → extended low claw thrust → recover |

## The boards — `boards/`, 5 files

Earlier passes at the same mode as 12- and 24-frame grids (05:04–05:05), kept because they
carry poses the strips don't: landing, run cycle, dash recovery. Not cut, not keyed.

## Measured (see `MEASURED.json` for per-beat numbers)

Split on fixed sixths — the generator lays the six beats out evenly, and a thrown weapon
sitting in a gap defeats gap-detection.

- **Clean on the mechanical checks.** Darkest background corner is RGB **253** on all nine,
  so the fuzz-42 keyer lifts them; **no ink touches any edge**, so there are no straight
  cutoffs to redo.
- **Body height is in range.** Standing beats run **270–320px**, above the 260px minimum
  Ember needs to never upscale at 4K (`docs/ART-REGEN-HANDOFF.md` §1).
- **The stable rows hold one scale**: CATCH-arm 7.6%, claw-rake 8.1%, dagger-deflect 9.2%,
  low-crouch-thrust 9.9%, claw-thrust 13.2% spread.
- **Four rows swing wide and that is POSE, not boil** — CATCH-sword 61% (arms overhead),
  WALLCLIMB 63% (he extends up the wall), dash-rush 44% (FX arc inflates the box),
  COUNTER 37% with 20px foot drift (he genuinely goes to the ground on beat 5).
  Per §2 law 2 these take **ONE uniform scale for the whole sequence** — never per-cell
  MATCH_HEIGHT, which is what makes a compact beat boil against a stretched one.

## ⛔ Two things the owner has to rule on before any of this packs

1. **`gk-CATCH-sword` ends with Ember holding a sword.** His identity lock is *claws ONLY,
   never a sword* (`docs/ART-REGEN-HANDOFF.md` §4). Catching and keeping an opponent's blade
   may be the entire point of a disarm mode — but that is a canon change, not a detail, and
   it is not mine to make. The strip is archived unaltered either way.
2. **`gk-WALLCLIMB-6beat` has the wall drawn into the cell.** World-oriented frames must not
   mirror by `facing` or the wall flips to the wrong side — they need the manifest's per-cell
   `mirror` map. Worth knowing: this is the first real **side-profile grip pose** in the
   project. Shopping-list item 7 says all nine current wall-cling cells are ground stances
   held midair with no grip and no wall, which is why both walls have always looked wrong.
   This solves it for Ember; the other eight still need theirs.

## Provenance

Delivered by the owner's outside generator on 2026-08-20 (05:04–05:20). MD5 of every file
is in `MEASURED.json` against its original `~/Downloads` filename. Deduplicated on content —
the download folder held several byte-identical copies.

The six **base-form** action sets from the same session are NOT part of this mode and live in
`RECOVERY/new-style-actionsets-aug20/`.

---

## Aug 21 2026 — the four directional LIGHT rows, delivered

`lights/` — nine strips, 2172x724, six beats each. Four directions in two takes, plus a
neutral **air** light nobody asked for that fills a fifth empty slot. **ARCHIVED, NOT PACKED.**

Full measurements, take-by-take verdict and the packing constraints are in
`SPEC-directional-lights.md`. The three things that decide whether this art is usable:

- **Size is solved.** Seven of nine clear Ember's 260px 4K minimum outright — the first Ghost
  Killer art to do so. The two `gldown` rows measure short because a crouch *is* short; their
  own standing bookend beats are 265 and 252px.
- **⛔ They are drawn facing RIGHT.** Every shipped sprite in this game is authored facing LEFT
  and mirrored by the engine, and the nine older Ghost Killer strips obey that. These do not.
  `-flop` each one before keying, or the whole row packs with the claws on the wrong side.
- **Killer form 9/9.** Fully wrapped face, no eye, on every beat. Judged on high-zoom head
  crops — the only way this call gets made here.

`python3 tools/measure_strip.py --check RECOVERY/ember-ghostkiller/lights/*.png`
