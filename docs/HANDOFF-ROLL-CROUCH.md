# ART HANDOFF — GROUND DODGE ROLL + CROUCH, FRAME BY FRAME

> ## ✅ FILLED AND SHIPPED — `SHEET_V 487`, 2026-08-13
>
> All 68 images came back and all 68 are in the sheets. **Everybody crouches and
> everybody rolls on the ground.** Measured in the live game, not eyeballed:
>
> * every one of the 68 cells has its lowest ink row **exactly on `footY`** — zero float,
>   zero clipped edges
> * the deep crouch beat lands at **65–70 % of each fighter's own standing height** (the
>   engine's own `CROUCH_H` is 0.68), against the 86.6–107.5 % this document opened with
> * the ball beat of the roll lands at **51–62 %**, against `ROLL_TUCK` 0.62
> * the render's fallback spin is **off** for every drawn roll — checked by reading the
>   live `drawImage` matrix mid-roll, not by reading the code
>
> Strips and GIFs of the shipped render: `media/roll-crouch-2026-08-13/`.
> Re-provable any time with `python3 tools/check_roll_crouch.py`.
>
> Kept as written below, because it is the spec the art was measured against.

**For the outside still-generator. Paste this whole file. Attach the reference PNGs it names.**
Everything here is measured off the shipped sheets on 2026-08-12 at `SHEET_V 485`.
Return images only — packing, keying and wiring happen in the repo.

---

## 0. WHY THIS EXISTS

The dodge roll had no roll art. Six fighters held **one standing picture** for the whole
0.28 s dodge while the engine spun that picture 360° in the air — a floaty windmill, not a
roll. The engine side is fixed (it now curls the body and welds the lowest pixel to the
floor), but a rotated standing drawing is still a rotated standing drawing. **The ceiling is
art.**

Same story on the crouch: measured against each fighter's own standing height, the "crouch"
cell is 95–107 % of standing. **Two fighters are literally TALLER crouching than standing.**

| fighter | crouch height vs its own standing | verdict |
|---|---|---|
| Kael | **107.5 %** | taller than standing |
| Mizu | **103.2 %** | taller than standing |
| Tsubasa | 97.9 % | not a crouch |
| Shin | 97.4 % | not a crouch |
| Ember | 96.1 % | not a crouch |
| Executioner | 95.1 % | not a crouch |
| Exile | 94.8 % | a forward lean, head stays up |
| Mokurai | 86.6 % | shallow |
| **Oni** | **53.3 %** | ✅ a real crouch — the only one |

---

## 1. THE MEDIUM — READ THIS BEFORE ANYTHING ELSE

**Clean high-contrast 2D CEL ILLUSTRATION / vector look. THIS IS NOT PIXEL ART.**

- Heavy black outlines, flat controlled shading, readable silhouette.
- Chibi fighting-game proportions — big head, short limbs, exactly as the reference shows.
- Glowing featureless angled eyes (no pupils, no iris) on everyone except Mokurai (stone
  mask, slit eyes) and Oni (white skull mask, red eyes).
- Roster cells measure **4 700 – 12 000 unique colours**. Anything that comes back with a
  few dozen flat colours is pixel art and is rejected on sight.

**⛔ Do not use a pixel-art generator or a pixel-art style preset. Ever.**

---

## 2. HARD RULES — ANY ONE OF THESE FAILS THE CELL

1. **PURE SIDE PROFILE, FACING LEFT.** Every cell in this game is authored facing left and
   mirrored in code. A three-quarter or front-facing frame is unusable.
2. **THE LOWEST PART OF THE BODY SITS ON THE GROUND LINE IN EVERY SINGLE FRAME.**
   This is the whole point of the job. In a roll the contact point travels — feet, then hip,
   then shoulder, then back, then feet again — but *something* is touching the floor in
   every beat. **No frame is airborne. No frame hovers. No jump, no leap, no somersault
   through the air.**
3. **SAME BODY MASS ACROSS THE SET.** Generate the six roll beats as ONE sequence from ONE
   reference so the character does not change size. The measurable check is **head diameter
   constant within ±2 %** across the set (body height changes on purpose; head size must
   not).
4. **NO BACKGROUND.** Transparent PNG. If transparency is impossible, a **flat solid
   `#FF00FF` magenta** field — no gradient, no vignette, no texture.
5. **NO BAKED GROUND SHADOW, no floor, no dust, no speed lines, no motion blur, no
   afterimages, no second character, no UI, no border, no text, no watermark.**
   Effects are drawn by the engine.
6. **WEAPON DISCIPLINE** — the weapon is held or stowed correctly in every beat, never
   dropped, never duplicated, never changed. It rolls with the body; it does not float.
7. **NO COSTUME DRIFT.** Hood, scarf, mask, belt, wraps, colours identical to the identity
   reference in every beat.
8. **CROP:** full body, nothing clipped by the canvas edge — not a toe, not a scarf tail,
   not a blade tip.

---

## 3. WHAT A GROUND ROLL IS (and what the last attempt got wrong)

A dodge roll is a **shoulder roll along the floor.** The body curls into a ball, the ball
turns over once, the fighter comes back up. The centre of the body never rises above a
crouch. **It is not a flip, not an aerial, not a cartwheel, not a dive.**

**Attach as reference:** `refs/TARGET-ground-roll.png`
The two on the left are Oni's roll (tight ball, then the uncurl). The four in the middle are
Mokurai's (duck → ball → rise). **The tight ball in the middle of that plate is the pose
this whole job is aimed at.** Match that reading.

**Attach as reference:** `refs/WRONG-1.png` and `refs/WRONG-2.png`
Each group of three is one fighter: idle, current "crouch", current "roll". Every one of
those crouch and roll cells is a standing pose. **That is what we are replacing.**

### The six beats — `<fighter>_roll_1..6`

| # | beat | pose | height target |
|---|---|---|---|
| 1 | **DUCK IN** | Knees break hard, chest drops toward the leading knee, leading arm reaching for the floor ahead. Both feet still down. Weight already falling forward. | 78 % of standing |
| 2 | **SHOULDER PLANT** | Leading shoulder and upper back take the floor. Hips rising over the shoulder. Chin tucked to chest. Knees folding in. The head is LOW and forward. | 64 % |
| 3 | **THE BALL** | Fully curled, INVERTED — hips and feet up and over, back on the floor, knees pressed to chest, arms wrapped in. A compact round silhouette. This is the frame the whole move is judged on. | 60 % |
| 4 | **UNCURL** | Rolling out onto the hips/backside, feet swinging down and forward to catch the ground, body opening from the ball. | 66 % |
| 5 | **RISE** | Feet planted, deep low crouch, one hand may still brush the floor, head coming up, weight going forward. | 72 % |
| 6 | **BACK TO STANCE** | Rising out of the crouch into the fighting guard, weapon back on line, not yet fully upright. | 92 % |

Beats 1 and 6 have the feet on the floor. Beats 2–5 have the shoulder / back / hip / feet on
it. **At no point does the whole body leave the ground.**

### The four beats — `<fighter>_crouch_1..4`

A crouch is a **sink in place**, not a step and not a lunge. Feet stay where they are. The
head comes DOWN. Guard stays up.

| # | beat | pose | height target |
|---|---|---|---|
| 1 | **KNEES BREAK** | Weight drops, knees bend, torso still fairly upright, guard held. | 88 % of standing |
| 2 | **SINK** | Hips drop between the heels, back angles forward, elbows tucking in. | 76 % |
| 3 | **THE HOLD** | Deep fighting crouch — thighs near horizontal, head low, guard tight, weapon ready. **This is the pose that is on screen 90 % of the time.** | **68 %** |
| 4 | **BREATH** | The same crouch a hair higher and a hair wider, so the held pose is alive instead of frozen. | 70 % |

68 % is not an arbitrary number — it is the exact squash the engine already applies to any
sheet with no crouch cell (`ctx.scale(1.1, 0.68)`). The art is being made to match what the
game already assumes.

---

## 4. PER-FIGHTER SPEC

`H` = the fighter's measured standing height in sheet pixels. Every target below is `H` × the
percentage in §3. **Work at any resolution you like — I rescale on the way in — but keep the
six/four beats of one fighter at ONE consistent scale.**

Attach the fighter's own `refs/IDENTITY-<name>.png` with its prompt. That file is the
identity lock: costume, palette and proportion all come from it.

---

### EXECUTIONER — `H = 185 px` · **the OLDEST and TALLEST of the six**
**Deep-purple horned hood — TWO long horns sweeping back off the head, orange on the inner
edge.** Purple gi and wraps, **orange scarf and orange sash**, black armour panels, glowing
**gold/amber** angled eyes in a black face-opening. Palette: `#0c0c0c` black · `#3c2454`
indigo · `#242454` blue-violet · `#84240c` burnt orange.
**Weapon: ONE long sword (odachi) — one blade only, never two, never a dagger.**
Roll: `144 · 118 · 111 · 122 · 133 · 170` px · Crouch: `163 · 141 · 126 · 130` px
*Heavy fighter: the roll is a POWER roll — slower, wider, the cloak swings with the turn.*

### MIZU — `H = 156 px` · **she/her**
Bright purple hood and robe over a darker purple gi, lighter violet sash and wraps, one big
glowing **white** angled eye showing in profile, no visible mouth. Palette: `#6c3c84` violet
· `#3c2454` deep purple · `#0c0c0c` black.
**Weapon: ONE long bo staff.** It is held across the body and rolls WITH her — tucked
diagonally against the curled torso in beats 2–4, never dropped, never sticking through her.
Roll: `122 · 100 · 94 · 103 · 112 · 144` px · Crouch: `137 · 119 · 106 · 109` px

### SHIN — `H = 194 px`
Dark green hooded gi with a **teal/cyan scarf**, big glowing white angled eyes, wrapped
hands. Palette: `#24543c` green · `#0c2424` deep teal · `#0c240c` dark green.
**Weapon: NONE in hand — hand-to-hand.** A shuriken/wire tool may show at the belt.
Roll: `151 · 124 · 116 · 128 · 140 · 178` px · Crouch: `171 · 147 · 132 · 136` px
*Low-stance specialist: his crouch should be the deepest and most predatory of the six.*

### TSUBASA — `H = 193 px` · **RED accent (never gold)**
**No hood** — spiky black hair with **red streaks**. Black gi, **red scarf, red sash and red
arm-wraps**, black face-mask over the mouth, glowing **white** angled eyes. Palette:
`#0c0c0c` black · `#242424` charcoal · `#540c0c`/`#6c0c0c` deep red.
**Weapon: TWO SMALL KNIVES (tantō). Two. Never katanas, never a hood.**
Roll: `151 · 124 · 116 · 127 · 139 · 178` px · Crouch: `170 · 147 · 131 · 135` px
*Form 1 only. His reverse-grip Form 2 already has its own drawn roll and crouch.*

### EMBER — `H = 207 px` · **he/him**
Green hooded gi, **lime/olive green**, long green scarf trailing behind, glowing white angled
eyes. Palette: `#3c6c24` lime · `#243c0c` olive · `#0c240c` deep green.
**Weapon: TEKKO-KAGI CLAWS ONLY — clawed gauntlets on both hands. NEVER a sword.**
Roll: `161 · 132 · 124 · 137 · 149 · 190` px · Crouch: `182 · 157 · 141 · 145` px
*His existing roll cell is already a low prone claw-dive — see the middle of `WRONG-2.png`.
That reading is right; it just needs the other five beats around it.*

### KAEL — `H = 174 px` · **GOLD accent · the YOUNGEST of the six**
Black hood and gi with **gold/amber trim, a gold sash and gold arm-wraps**, black face-mask,
glowing **gold** angled eyes. Palette: `#0c0c0c` black · `#3c3c3c` grey · `#b48424` gold ·
`#543c0c` bronze.
**Weapon: ONE LONG SWORD AND ONE SHORT SWORD (daishō) — both visible, both correct
lengths. Two blades, different sizes.** The long blade may be sheathed on the back during
the ball beats so it does not pass through the body.
Roll: `136 · 111 · 104 · 115 · 125 · 160` px · Crouch: `153 · 132 · 118 · 122` px

---

### CROUCH ONLY — these two already have a drawn roll

**MOKURAI — `H = 149 px` · he/him · "The Sage of Nothingness"**
Bald grey **cracked-stone head**, a **RED gem set in the brow** and one glowing **gold** eye,
no hood. **Orange-gold robe with a long RED scarf** and red sash, brown/black lower robe and
boots, dark **prayer beads** around the neck and wound round both fists.
**BARE HANDS. He has NO staff and never did.**
Crouch: `131 · 113 · 101 · 104` px

**EXILE — `H = 155 px` · she/her · ONE-EYED**
Huge spiked **black hair with a white streak**, a **white bandage wrap across one eye** (the
other eye visible, scarred), black face-mask over the mouth, black outfit with a **purple
scarf and purple accents**, gold-brown boots and wraps.
**Weapon: KUSARIGAMA — a sickle in one hand and an iron chain-and-ball. The chain lies
along the floor; it does not float.**
Crouch: `136 · 118 · 105 · 108` px
*Her current "crouch" is a forward lunge — her head stays at standing height. She needs a
real sink.*

---

## 5. DELIVERY

```
<fighter>_roll_1.png   … _roll_6.png     (6 fighters × 6  = 36 images)
<fighter>_crouch_1.png … _crouch_4.png   (8 fighters × 4  = 32 images)
```

- One pose per file. PNG. Transparent, or flat `#FF00FF`.
- Lowercase fighter names exactly: `executioner mizu shin tsubasa ember kael mokurai exile`.
- **Priority if it has to be split:** ① all six ROLL sets → ② crouch for Kael and Mizu (the
  two who grow when they duck) → ③ the remaining six crouches.

## 6. WHAT HAPPENED TO THEM HERE — `SHEET_V 487`

**Pack:** `tools/sprites/pack_roll_crouch.py` · **Proof:** `tools/check_roll_crouch.py` ·
**Owner review:** `tools/capture_roll_crouch.py` → `media/roll-crouch-2026-08-13/`

1. The returns were already keyed and binary-alpha (0 % REDO on the candidate QC), so the
   only keying left was **purging sub-visible alpha after the rescale**. That one step is
   not optional and it is not cosmetic: LANCZOS hangs ~2 px of alpha-4 fringe under the
   soles, `Image.paste` squares alpha through its own mask (4·4/255 → 0), and the fringe
   therefore measured as body, set the foot anchor, then evaporated in the composite.
   All 68 cells first landed **2–3 px above the floor** — the exact bug this job exists to
   kill, reintroduced by the packer. Purge, then place with numpy, never `paste`.
2. **ONE UNIFORM SCALE PER SEQUENCE** = `median(target ÷ candidate)` over the set, against
   the measured standing heights in §4. Never per-cell MATCH_HEIGHT: body height changing
   across the beats IS the animation, and flattening each cell to its own target scales the
   compact ball against the upright rise and boils the character's size.
   * *Ink area was tried as a second opinion and rejected* — it reads +10…+28 % on all
     fourteen sets, uniformly, because a folded pose simply has less silhouette than a
     standing one. A cross-pose area match would inflate every crouch.
   * *`eye_scale.py` could not be used at all* — on 2K candidate frames its blob filter
     returns 9–20 spans per frame (trim, highlights, weapon glints), not two eyes, and its
     medians disagreed with the height answer by up to 2×. It is built for packed cells.
3. Horizontal anchor differs by sequence, because what must not slide differs. **Crouch**
   pins its foot-band centroid to the idle's — feet do not move when you duck. **Roll** pins
   its ink-bbox centre to the idle's, because the contact point travels (feet → shoulder →
   back → hip → feet) and pinning *that* would shove the body backward the moment the
   shoulder takes the floor.
4. Appended (originals byte-identical, asserted before and after save), `SHEET_V` bumped,
   and wired: `crouch_1..4` sinks off `crouchAt` then breathes on the hold, `roll_1..6`
   paces over `rollTimer`. Two more slots were reading the same wrong cell and inherited the
   fix — the sweep **tumble** drew `F.roll` and now rides beats 2–5, and **landing** drew
   `F.kneel` (a standing pose on six, `canon_guard` on Mokurai, her BLOCK on Exile) and now
   absorbs into `crouch_3`, retiring the `xcrouch`/`bcrouch` landing patches.
5. `roll_1` was added to `drawnRoll` **in the same edit as the picker**. Miss that and the
   drawn roll and the fallback windmill spin on top of each other — the documented Oni bug.
5. On approval: append to the sheets (append-only, existing cells byte-identical), bump
   `SHEET_V`, add `<fighter>_roll_1..6` / `_crouch_1..4` to the frame map, and wire them —
   the roll row replaces the engine's spin the same way Mokurai's and Exile's already do.

## 7. AUTOMATIC REJECT

- Any frame where the body is fully off the ground · a flip, leap or aerial spin
- Pixel art · a three-quarter or front-facing view · a mirrored (right-facing) cell
- Wrong weapon count or type · a dropped weapon · a weapon passing through the body
- Costume or palette drift from `IDENTITY-<name>.png`
- A baked ground shadow, dust, speed lines, motion blur or afterimage
- Any part of the body clipped by the canvas edge
- Head diameter drifting more than ±2 % across a set
- A "crouch" that is not visibly lower than the fighter's own standing pose

---

*Measured and written 2026-08-12 against `SHEET_V 485`. Reference plates in
`docs/roll-fix/refs/`.*
