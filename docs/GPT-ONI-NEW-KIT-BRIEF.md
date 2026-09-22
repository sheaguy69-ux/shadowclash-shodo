# GPT BRIEF — ONI, THE FOUNDER: the art still owed, drawn at the RIGHT BODY MASS

**Written 2026-08-13 (Fable 5), measured live against the shipped roster at SHEET_V 486.**
Hand this file to GPT together with the reference images named in §6.

There are two jobs in here and the second one is the important one:

1. Draw the handful of cells Oni still owes (§4) — it is a short list, not a redraw.
2. **Draw him with MASS.** Every page from here on has to carry his build, because
   the engine cannot fake it. See §2 — this is the part that is currently wrong.

---

## 1. WHO HE IS — the identity lock (do not deviate)

> Chibi warrior, strict side profile, **FACING LEFT**. A **WHITE SKULL MASK** with
> **three claw-scratch gouges** across it and **RED glowing eyes**. **Two dark horns.**
> A **BLACK HOOD** over a **tattered black mantle**; **ash-gray worn plate** at the
> chest, bracers, knees and boots. **Cloth wrappings on BOTH hands and forearms.**
> **RIGHT HAND CLAW ONLY** — five long dark-gunmetal blades. **THE LEFT HAND IS
> WRAPPED, WITH NO CLAW.** **Two swords carried crossed on his back.**
> Palette: **black, ash gray, white mask, red eyes and FX** — and nothing else.

**Never:** a mane, a bone pelt, any purple, a claw on both hands, extra limbs.
(An older redesign had the mane and purple. It is deleted canon — if a reference
image shows it, that image is the wrong one.)

---

## 2. ⛔ BODY MASS — the thing to fix, with numbers

Oni is **the founder who towers over the cast**. Right now he is TALL but THIN, and
that reads as lanky rather than powerful. These are measured drawn sizes of every
fighter's idle, on screen, in the live game today:

| fighter | drawn height | drawn width | width ÷ height |
|---|---|---|---|
| **ONI** | **85.8 px** | **62.1 px** | **0.72 ← lowest on the roster** |
| Ember | 69.3 | 65.3 | 0.94 |
| Shin | 66.6 | 61.8 | 0.93 |
| Mizu | 62.4 | 67.6 | 1.08 |
| Exile | 72.3 | 68.1 | 0.94 |
| Tsubasa | 69.6 | 66.4 | 0.95 |
| Kael | 70.0 | 57.5 | 0.82 |
| Mokurai | 69.5 | 55.1 | 0.79 |
| Executioner | 70.4 | 86.4 | 1.23 |

**His height is already right — do not make him taller.** He leads the cast by
~13px (+19% over the next tallest) and that is the canon "he towers".

**His WIDTH is the problem.** He is the narrowest body relative to his height of
anyone in the game, including the two slender ninja. The width above was measured
while the engine was still stretching him 1.2× horizontally — he measured thinnest
*with the cheat on*. **That cheat is now deleted** (SHEET_V 488: the `thicken` knob
is out of the engine and every manifest, on the owner's ruling that no fighter gets
a warping x-stretch), so he draws at his true width today and reads narrower still.
**The mass can only come from the drawing.** There is no longer any code path that
can fake it.

### The precise defect: SHOULDER SPAN, not head size

Measuring every idle in head-widths (the only unit that survives a scale change)
settles what is actually wrong with him:

| fighter | heads tall | **shoulders, in head-widths** |
|---|---|---|
| Executioner | 3.03 | **2.48** |
| Mizu | 3.06 | 2.41 |
| Exile | 3.04 | 2.20 |
| Ember | 3.04 | 2.04 |
| Tsubasa | 3.06 | 2.00 |
| Shin | 2.37 | 1.93 |
| Mokurai | 2.81 | 1.87 |
| **ONI** | **3.08** | **1.69 ← second-narrowest** |
| Kael | 3.05 | 1.51 (the slim duelist) |

**His head-to-body proportion is CORRECT** — 3.08 heads tall against a cast median
of 3.04, so he is properly chibi and the head does not need touching. (I expected
this to be the fault and it is not; the measurement says otherwise.)

**The fault is entirely in the shoulders.** He spans 1.69 head-widths where the
heavy bodies span 2.2–2.5. He is built like the slim duelist and asked to read like
the founder.

**Target: shoulders ~2.4 head-widths — a full head-width broader than he is now**,
putting him with the Executioner instead of with Kael. Concretely:

- **Shoulders and chest plate broad** — the widest point of the body, well outside
  the hips, spanning about 2.4 of his own head-widths. He should look like he could
  not fit through a doorway square-on.
- **Thick upper arms and forearms**, with the cloth wraps adding bulk, not hugging.
- **Heavy thighs and boots**; a wide, planted stance with the feet well apart.
- **The mantle hangs with weight** — a heavy fall that adds volume at the flanks,
  not a thin cape stuck to his back.
- **Keep the head/mask the size it already is.** Mass comes from the BODY. Do not
  make him a bigger chibi; make him a *heavier* one.

**One caveat on the table, so nobody chases a wrong number:** these widths are the
INK extents of the whole cell, so a fighter holding a weapon out wide measures wider
than his body really is — the Executioner's 86.4 includes his extended katana, and
Mizu's 67.6 includes her staff. That does not rescue Oni: his own claw and the two
swords on his back are counted in his 62.1 too, and he is *still* last. The body
underneath is narrower than the number suggests, which makes the gap worse, not
better.

Use the side-by-side at `docs/frame-handoff/oni-mass/oni-mass-comparison.png` —
Oni, the Executioner and Kael scaled to the SAME height so the widths compare
honestly. Oni should read as the heaviest **body** of the three while staying the
tallest. If a drawing of Oni could be swapped for a drawing of Kael by scaling it
up, it is wrong.

---

## 3. THE FOUR PAGE RULES (each has cost a redo)

1. **Draw him FACING LEFT.** The engine mirrors toward the opponent; art drawn
   facing right plays backwards for the whole move, and no measurement catches it.
2. **No baked ground shadow.** The engine draws its own.
3. **No second character in the frame** — no dummy, no victim, no opponent. The
   engine draws the other fighter. (A dummy on an earlier board had to be erased
   cell by cell.)
4. **Real white gutters between figures.** The splitter cuts on them. No captions
   under the figures, no frame numbers, no panel rules, no red numerals — a caption
   board once got cut as art and shipped the words "5. FORWARD DASH MID" as a sprite.

**Page format that packs cleanly:** one MOVE per page, ~2000×620 or larger, figures
**350–450px tall**, six figures left-to-right in beat order, white background.
Every correction is a downscale — art that arrives too small cannot be used.

---

## 4. WHAT IS OWED — the whole list

### PRIORITY 1 — five ambiguous-claw cells, redrawn
These read with talon mass on BOTH sides, so the viewer cannot tell which hand is
clawed. Mirroring cannot add a claw that was never drawn. **Right hand clawed, left
hand wrapped and empty**, unmistakably, in each:

| cell | pose |
|---|---|
| `r1_1_crouch_stance` | crouched ready stance |
| `r1_5_prone_recover` | rising off the floor |
| `r1_7_axe_kick` | axe kick |
| `r3_3_claw_thrust1` | claw thrust, beat 1 |
| `r3_7_rising_slash2` | rising slash, beat 2 |

### PRIORITY 2 — directional 6-beat fills (only for full depth)
Not needed to ship him playable. Exile ships at 143 cells; match her, not the
Executioner's 328. **Do not draw an idle-breath cycle** — the engine's bob supplies it.

---

## 5. WHAT NOT TO SEND

- Mini-figures. An earlier 20-move sheet arrived with figures 66–108px against a
  ~107px packed body: packing it meant upscaling, and nothing gets upscaled.
- Caption boards, numbered panels, or grouped bracket layouts.
- Any figure sharing a panel with a dummy or an opponent.
- Anything with the deleted mane / pelt / purple design.

## 6. REFERENCES TO SEND WITH THIS FILE

- `RECOVERY/oni-founder/ONI-BIBLE-FINAL.png` — the design master.
- `RECOVERY/oni-founder/boards-aug9/MASTER-STATES-CLEAN-alt.png` — his states, no captions.
- A crop of the **Executioner's idle** as the mass yardstick (§2).
- Any recent packed Oni cell as the current-look reference — and the note that his
  build is to get **heavier**, not taller.
