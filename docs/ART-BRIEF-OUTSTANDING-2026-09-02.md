# ShadowClash — what actually needs drawing (SHODO-EDITION, current at SHEET_V 693)

Rewritten 2026-09-02 after a pass that fixed locally everything that could be fixed locally.
**The list went from four items to three, and two of the original four turned out not to need
art at all.** Nothing below is a scale problem — every scale problem in this tree has been
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

## 3. EMBER — the special, or a ruling instead

**Row:** `espec1..8`, cells 190-197.

Honest status: **I cannot measure this row, and I am not certain it is wrong.** Ink area reads
it 1.18 of his idle, but that is the claw spread, not his body — area over-reads exactly this
kind of row. Every rigid landmark fails: his eye reads on 0 of the 8 beats (hidden behind the
claws), and a hood template locks on none of them.

The root cause is worth knowing: **ember's sheet is not one drawing.** His idle, light and
crouch wear a scalloped hood with a stitched rim; his action rows wear a plain mottled dome.
That is why no template that fits one family fits the other.

So this is a choice, not a defect report:
- **If the row looks right to you, it stays.** Nothing measurable says otherwise.
- **If it looks oversized,** it needs redrawing at his idle head size, because there is no
  ruler that could verify a rescale of it.

---

## Removed from this brief, and why

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
