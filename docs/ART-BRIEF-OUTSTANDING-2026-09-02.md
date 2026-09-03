# ShadowClash — what actually needs drawing (SHODO-EDITION, current at SHEET_V 694)

Rewritten 2026-09-02 after a pass that fixed locally everything that could be fixed locally.
**Two items left.** The list started at four; two of those turned out not to need art at all,
and Ember's special was drawn and landed at 694. Nothing below is a scale problem — every scale problem in this tree has been
measured and corrected in place.

## House rules for every prompt here

- ONE row per image, left-facing, transparent background, captions BELOW the row.
- The whole row at ONE body size: heads, hands and weapons the same size beat to beat. Do not
  shrink the tucked beats — a tuck keeps the same head.
- No motion blur, no speed lines, no ground shadow, no background, no border.
- Nothing may end in a straight cut. An effect that leaves the figure fades to nothing inside
  the frame; a smear that hits the canvas edge is a reject.
- Match the fighter's existing design exactly. These are replacement beats inside a live
  animation, not a redesign.

---

## 0. ⛔ BLOCKED — the approved beat-5 frame does not fit his cell (owner decision open)

Item 1 below was DRAWN and owner-approved: package
`art/production/handoff/SHODO-EXECUTIONER-XRISE-BEAT5-V2-APPROVED-READY-2026-09-02`,
all six hashes verified. Integration is blocked on a geometry decision, not on art.

**At any fighter-correct scale the frame overflows his 300x412 cell window.**

| scale | frame becomes | fits 300x412? |
|---|---|---|
| 0.669 | 395 x 507 | no — and the fighter reads bigger than beats 4 and 6 |
| 0.600 | 355 x 455 | no |
| 0.550 | 325 x 417 | no |
| 0.507 | 300 x 384 | yes, but he reads ~20% small against the row |

Not trimmable: the ink extent is identical at every alpha threshold from 8 to 128, and
**15.5% of the ink falls outside a 300px-wide window**. The cause is that the approved
crescent is about **1.5x the crescent it replaces** (live cell 324 is 250x344).

**Scale could not be pinned by any single ruler.** Five were tried and three failed a
known-answer or known-equal check outright: horns (66% spread on cells that are the same
size), hood band (50%), hood mass (62%). Template matching failed too — live 323 against
live 325 peaks at ncc 0.41, not 1.0, because the poses differ. His EYE, the one ruler
validated elsewhere in this roster, is invalid ON THIS FRAME: the approved art draws a
single eye 21x19 where his live cells carry an 11x12 teardrop plus a small front wedge,
so the eye is proportionally larger and matching it oversizes the head. A visual scale
sweep and the template median agree on roughly **0.55-0.60**.

**Three ways forward, owner's call:**

1. **Grow his cell window** to ~440x560. Follows the handoff contract ("grow the
   transparent cell window rather than shrinking the fighter") and is in-family — shin is
   already 520 wide, exile 480. Costs a re-layout of all 328 cells, and `frameW` feeds the
   crack aura radius (`fw * S * 0.62`, index.html:13317) which would swell ~47% — a visible
   change to a different feature, against contract item 6's "preserve gameplay exactly".
2. **Send beat 5 back with the crescent sized to the row.** Drops into the existing window
   with no engine change. The fighter in the approved art is fine; only the arc is oversized.
3. Shrink to fit — not recommended, he reads ~20% small.

Nothing has been written to the sheet.

## 1. EXECUTIONER — one beat of the rise row has no fighter in it

**Row:** `xrise1..8` / `xkiriage1..8` (one set of eight cells, two names). Live cells 320-327.
**The beat:** number 5 of 8 — currently cell 324.

That cell is a **pure effect crescent with no figure at all.** Not a small figure, not a
partial one: one stray 4px pixel and an orange-black arc. Everything else in the row was
rebuilt at 693 and the row now holds one size to 1.3%, so this is the only gap left in it.

**Generate:** beat 5 of the rising diagonal cut — the fighter at the top of the swing, blade
carried through, at the same body size as the beats either side of it. The arc that is already
there is the shape the cut should follow.

*Note: beats 7 and 8 of this row are runtime orphans — the engine takes a branch that reads
only keys 1-6, so the live move is six beats. Draw beat 5 and the move is whole.*

## 2. SHIN — the getup, four beats, redrawn as one row

**Cells:** 241, 242 (lying, head-down) and 120, 121 (rising crouch, nearly standing).

This is a mixed-source row and it is the one row in the roster where **no ruler locks.** His
eye is not a ruler on him (idle spread 6.5% against a 3% gate), a hood measure reads 10.7% on
his own idle, and on the prone and rising beats no head template locks at all — peaks 0.53 to
0.74 where 0.85 is the threshold. So the row cannot be corrected by measurement and it cannot
be verified after the fact either. It has to be drawn as one row.

**Generate:** a four-beat getup at ONE size — flat on the floor → pushing up on one arm →
rising crouch → standing, with the last beat exactly his idle size. Keep the floor dust as a
soft cloud that fades out; it must not end in a hard edge.

---

## Removed from this brief, and why

- **Ember's special** — DRAWN AND LANDED at 694. The owner approved a regenerated eight-beat
  board; it packed at one shared scale (0.7759, row spread 0.40% in height — integer-pixel
  quantisation, not pop) as cells 274-281. Landing it uncovered that `specialCells()` returned
  a frame instead of a cell list for Ember alone, so **his special had been drawing his idle
  and none of this row's art would ever have appeared.** Fixed in the same commit. The old
  cells 190-197 are now orphans awaiting the strip pass.

- **Kael's air heavy last two beats** — FIXED at 691. They were drawn 35-45% oversized while
  the six jump beats were 25% undersized; all eight now match his idle head, measured on hood
  mass (validated on his idle at 2.7% against a 3% gate).
- **Executioner's rise row, beats 4 and 6** — FIXED at 693 along with the rest of the row.
  Beat 4's eye was unreadable only because its front wedge is lost to the turned head; its
  rear eye alone was validated as a ruler and placed it.
- **Executioner's special middle beats** — NOT A DEFECT. The premise was wrong. All eight
  beats come from one board at one pack scale (0.8950, row spread 0.00%), and the row sits
  0.6% off his idle, inside the ruler's own noise. Ink area lied because the source board
  carries a painted ground shadow. Nothing to draw.
