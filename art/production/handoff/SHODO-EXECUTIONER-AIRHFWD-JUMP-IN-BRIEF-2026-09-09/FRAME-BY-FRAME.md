# THE EXECUTIONER — "Falling Verdict" — `airhfwd1..8` — the eight beats

One row. Eight cells. One image, eight figures in a single horizontal line, evenly spaced,
each figure fully inside its own cell with clear space around it.

---

## The scale contract — measured off his current sheet

| | |
|---|---|
| cell | **388 × 496** px |
| ground line | **`footY` = 488** — the red line in every `refs/` strip |
| body ruler | **ink-area √ = 148** on his idle · working band **140 – 153**, blade and brush FX excluded |
| on screen | idle stands **125 px** — he is the TALLEST fighter and stays first by a visible margin |

**ONE uniform scale across all eight cells, anchored on his idle.** Never normalise each
cell's bounding box to a common height; a rotating, extended body genuinely changes its box
and matching those boxes causes size boil.

⛔ **Foot clearance is NOT the airborne test on this sheet.** His cells pack foot-anchored —
`idle`, `aneu1`, `hneu1` and `ajump3` all sit 3 px off the foot line, because his air poses
trail a leg down. The airborne read here is the POSE: trailing rear leg, no planted foot,
and no floor contact art of any kind.

**A pose that will not fit is not a reason to shrink him.** Say so and the cell height
grows. The body never shrinks and the pose is never cropped.

---

## The eight beats

He enters from a rising jump (`refs/03`) and leaves into his fall. Beat 1 must read as a
believable next drawing after `ajump3`, and beat 8 must hand to `ajump5`/`fall` with no
jump-cut. Design the eight as one continuous motion — the ōdachi tip, the ochre rope ends
and the sash each trace one smooth curve through the row.

He is the heaviest fighter and the slowest runner in the game. This reads as **weight
arriving**, not as a nimble dive. Gather big, fall committed, settle long.

**1. GATHER.** Airborne, still rising. The ōdachi is hauled back and up over his rear
shoulder in both hands, elbows high, the blade nearly vertical. Horned helm turned toward
the target below-forward. Rope ends and sash stream UP and BEHIND — he is still travelling
upward, so the cloth lags below-behind, not above.

**2. WIND.** Shoulders rotate into the swing; the blade reaches its furthest point back and
its highest point in the whole row. His leading knee begins to open toward the target.
Nothing has left him yet — no trail, no crescent.

**3. TIP-OVER.** His mass crosses the leading knee and he starts to fall. The ōdachi breaks
from the top of its arc and begins down. The FIRST faint ghosted blade exposure appears,
trailing the tip.

**4. CUT — the contact beat.** The committed downward-forward diagonal, both hands still on
the hilt, blade leading on one clean line. Body tilted forward over the leading knee, rear
leg extended back and trailing, helm low behind the guard. Three to four ghosted exposures
behind the tip trace the arc he just cut, and ONE orange brush crescent rides the blade —
the same single-crescent treatment as `hneu5` (`refs/02`, cell 310), not a second one.
**This is the frame the game hits on**: it must read as a contact frame in isolation, at
48 × 64 px, with no limb merged into the torso.

**5. FOLLOW.** The blade finishes past the low point, tip now below and in front of him.
Body rotated furthest forward, both arms extended down the line of the cut. The ghost
exposures thin to one. The rope ends snap FORWARD past his shoulder — that reversal is what
sells the weight landing.

**6. HANG.** The swing is spent. He is falling, blade wide and low, shoulders starting back
over his hips. The orange crescent is gone; only the figure is left.

**7. RECOVER.** Knees gather under him, the ōdachi is hauled back in toward his centre,
guard reforming across his body. Cloth settles from its forward snap back down behind him.

**8. READY.** Compact falling guard, blade in, body upright, braced to land. This drawing
sits beside `ajump5` (`refs/03`) and must read as the same fighter one beat later — same
helm size, same shoulder width, same blade length, same scale.

---

## NEVER — the Executioner's specific failure modes

- **NEVER two swords, and never a dagger.** He carries **ONE long ōdachi**, both hands on it
  through beats 1–5. Count it in every cell.
- **NEVER lose the horns or the amber eyes.** Two horns on the helm, glowing amber/orange
  featureless eyes, every cell.
- **NEVER re-colour him.** Charcoal/near-black armour and cloth, ochre-orange rope wraps and
  sash, amber eyes, and the single orange brush crescent on beat 4 only. No purple, no teal,
  no green, no white core.
- **NEVER a ground pose in the air.** No planted foot, no dust, no crater, no shadow puddle,
  no floor line. The rear leg trails; it does not stand.
- **NEVER make him small or nimble.** He is the tallest and heaviest. No compact acrobat
  tuck, no spin, no flip. "Chibi-like" means the construction already in `refs/04`, not a
  smaller body with a bigger head and not adult proportions with long ankles — Anthony
  rejected both extremes on 2026-09-06.
- **NEVER a horizontal swing.** That is his `aneu` row (`refs/01`), which is exactly what
  this row exists to stop drawing. The read is one descending diagonal.
- **NEVER two crescents, and never a white core.** One orange brush crescent, on beat 4,
  matching `hneu5`.
- **NEVER smooth vector or airbrush finish.** Heavy uneven calligraphic contours, real
  pressure variation, bristle edges, controlled ink-wash shading — the Shodo treatment in
  every `refs/` strip. Not dense granular etched texture either; that was the 2026-09-07
  correction on Oni.
- **NEVER a camera move.** Same framing, same distance, pure side profile, facing LEFT.
  Every sprite in this game is authored facing left and the engine mirrors it.
- **NEVER a background.** Flat white, no gradient, no ground plane, no speed-line backdrop,
  no panel border, no caption text inside the cell.
- **NEVER shrink or crop to fit.** Grow the canvas and say so.
- **NEVER take choreography from an archived row.** Only the five strips in `refs/`.

---

## Held exposures vs new drawings

All eight are **new drawings**. Do not deliver six drawings with two repeats. If a beat
genuinely cannot be drawn distinctly, name it and say why rather than padding the row.

The orange crescent on beat 4 is a **drawn effect inside the cell**, same treatment as
`hneu5`. It is part of the drawing, not a runtime overlay, and must not cross the cell edge.

---

## Delivery

- One PNG, eight figures, one row, flat white background.
- Source resolution comfortably above the 388 × 496 cell so the downscale is clean.
- **Do not deliver pre-keyed RGBA** — the packer keys once, and keying on the way in keys
  twice and punches holes in the ink.
- Plus the filled-in `GRADE-TABLE.md`. No cell packs without a grade.
