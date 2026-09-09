# KAEL — "Diving Twin Fang" — `airhfwd1..8` — the eight beats

One row. Eight cells. One image, eight figures in a single horizontal line, evenly spaced,
each figure fully inside its own cell with clear space around it.

---

## The scale contract — measured, not estimated

Every number below was measured off Kael's CURRENT cells on the served 773 sheet.

| | |
|---|---|
| cell size | **300 × 320** px (`frameW` 300, `frameH` 320) |
| ground line | **`footY` = 312** — drawn as the red line in every `refs/` strip |
| body ruler | **ink-area √ = 96** on his idle (`idle` 95.9, `idle2` 95.8, `xidle1` 96.2) |
| the same ruler on his air row | `kxcut1` **101.4**, `kxcut8` **100.3**, `ajump5` **96.2** |
| on screen | his idle stands **120 px** tall in the game |

**ONE uniform scale across all eight cells, anchored on his idle.** Do not normalise each
cell's bounding box to the same height — a rotating, tucked, extended body genuinely
changes its box, and matching those boxes scales the extended beat about 2× against the
compact one and produces size boil. The body's ink-area √, measured with the blade and any
brush FX excluded, stays in the band **94–102** on every one of the eight cells.

**He is in the air.** His grounded cells sit with 1–8 px between the lowest ink and the
foot line. His one true airborne beat, `ajump3`, sits **32 px** clear of it. Every cell in
this row must clear the foot line the way `ajump3` does — beats 1–6 by 30 px or more.
Ground contact art does not belong in flight: no dust, no crater, no shadow puddle, no
planted foot, no floor line.

**A pose that will not fit is not a reason to shrink him.** If a beat runs out of room,
say so and the cell height grows; the body never shrinks and the pose is never cropped.

---

## The eight beats

He enters out of a rising jump (`refs/02`, `ajump1..6`) and leaves into his fall. Beats 1
and 8 are the joins: beat 1 must read as a believable next drawing after `ajump3`, and beat
8 must hand off to `ajump5`/`fall` without a jump-cut. Design the eight as one continuous
motion, not eight separate illustrations — the scarf, the cloak hem and both blade tips
each trace one smooth curve through the row.

**1. GATHER.** Airborne, knees drawn up, body still rising. Both blades pulled back and
high on his rear side, wrists cocked, the long katana above the short wakizashi. Hood
forward, eyes toward the target. Scarf and cloak hem stream UP and BEHIND him — he is still
travelling upward, so the cloth lags below-behind, not above.

**2. WIND.** Shoulders rotate into the swing; the front knee starts to open toward the
target. Both blades reach their furthest point back and up. This is the highest the tips go
in the whole row. Nothing has left him yet — no ink trail, no crescent.

**3. TIP-OVER.** His mass crosses over the front knee and he begins to fall forward. The
blades break from the top of their arc and start down. The FIRST ghosted blade exposure
appears here, faint, trailing the tips.

**4. CUT — the contact beat.** The committed downward-forward diagonal. Both blades stacked
on ONE line, long katana leading, short wakizashi a hand's width behind and inside it, so
the silhouette reads as a single falling wedge and not as a scissor. Body tilted forward
over the leading knee, rear leg extended back, hood down over the eyes. Three to four
ghosted blade exposures behind the tips trace the arc he just cut. **This is the frame the
game hits on** — it must read as an attack contact frame in isolation, at 48 × 64 px, with
no limb merging into the torso.

**5. FOLLOW.** The blades finish past the low point, tips now below and in front of his
feet. His body has rotated furthest forward. The ghost exposures thin out to one. Scarf
snaps forward past his shoulder — the cloth reverses direction here, and that reversal is
what sells the impact.

**6. HANG.** The swing is spent. He is falling, blades wide and low, body beginning to
right itself. Shoulders come back over his hips. The gold brush marks are gone; only the
figure is left.

**7. RECOVER.** Knees come up under him, both blades draw back in toward his centre,
guard reforming. Cloth settles from its forward snap back down behind him.

**8. READY.** Compact falling guard, both blades in, body upright, ready to land. This
drawing has to sit beside `ajump5` (`refs/02`, cell 303) and look like the same fighter one
beat later — same hood size, same shoulder width, same blade lengths, same scale.

---

## NEVER — Kael's specific failure modes

- **NEVER two long swords, and never two short.** He carries **one long katana and one short
  wakizashi**, always both, always visibly different lengths. Count them in every cell.
- **NEVER a horizontal X.** That is `kxcut`, his air Light (`refs/01`), and this row exists
  to not be it. The read is one descending diagonal.
- **NEVER a ground pose in the air.** No planted feet, no dust, no floor contact, no shadow
  under him, no crater. Compare against `ajump3`'s 32 px foot clearance.
- **NEVER re-colour him.** Charcoal/near-black hood and cloak, gold-ochre scarf, sash and
  wraps, pale mask slit. No purple, no teal, no saturated green, no new accent.
- **NEVER a bigger head or a stubbier body.** "Chibi-like" means the construction already in
  `refs/03`, not a smaller body with a baby head, and not adult proportions with long
  ankles. Anthony rejected both extremes on 2026-09-06.
- **NEVER smooth vector or airbrush finish.** Heavy uneven calligraphic contours with real
  pressure variation, bristle edges, controlled ink-wash shading — the Shodo treatment
  visible in every strip in `refs/`. Not granular etched texture either; that was the
  2026-09-07 correction on Oni.
- **NEVER a camera move.** Same framing, same distance, pure side profile, facing LEFT.
  Every sprite in this game is authored facing left and the engine mirrors it.
- **NEVER a background.** Flat white, keyed out on delivery, no gradient, no ground plane,
  no speed-line backdrop, no panel border, no caption text inside the cell.
- **NEVER shrink or crop to fit.** Grow the canvas and say so.
- **NEVER copy choreography from an archived row.** Only the five strips in `refs/`.

---

## Held exposures vs new drawings

All eight are **new drawings**. None of them is a held exposure of another, and the row must
not be delivered as six drawings with two repeats. If a beat genuinely cannot be drawn
distinctly, say which one and why — do not pad the row.

The gold brush crescents on beats 3–5 are **drawn effects inside the cell**, the same
treatment as `kxcut4` (`refs/01`, cell 294). They are part of the drawing, not a runtime
overlay, and they must not extend past the cell edge.

---

## Delivery

- One PNG, eight figures, one row, flat white background.
- Source resolution comfortably above the 300 × 320 cell so the down-scale is clean;
  do not deliver pre-keyed RGBA — the packer keys once, and keying on the way in keys twice
  and punches holes in the ink.
- Plus the filled-in `GRADE-TABLE.md`.
