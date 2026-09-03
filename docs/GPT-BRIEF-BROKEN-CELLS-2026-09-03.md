# GPT brief — the three cells that must be redrawn, and nothing else

Written 2026-09-03 against SHODO-EDITION at `SHEET_V 697`.

A frame-by-frame audit of every live cell on all nine fighters (1413 cells) found **62
damaged cells that actually draw in game**, 12 of them blockers. **Nine of those twelve are
being repaired from approved shodo boards already on disk — do not draw those.** Three have
no source anywhere and are the entire ask here.

⛔ **Do not regenerate anything not listed in section 2.** The owner has said plainly he is
not redoing art that already exists. If you think something else needs drawing, say so
first and wait.

---

## 1. Read this before generating — it is why the last two boards were rejected

Two delivered packages were rejected on 2026-09-02 because **an old animation/choreography
source was used as a generation reference** (their own `PROMPT.md` said so: *"the recovered
old `hb_catch` row for choreography only"*). The rule that replaced it:

1. **Identity reference: exactly ONE approved idle image of that fighter. Nothing else.**
2. **Choreography comes from the words in this brief, not from a picture.** Never open an
   old move board, a recovered animation strip, a packed sprite cell, a rejected candidate,
   or anything under `RECOVERY/` and feed it in.
3. **Declare every reference you used, with its path and SHA-256.** The rejection above was
   only catchable because the prompt file was honest about its inputs.
4. If a beat genuinely cannot be drawn without seeing prior motion, **stop and say so.**

## 1b. Deliver TRUE ALPHA, not a baked checkerboard

Every review board so far has arrived as **RGB with a baked light checkerboard**. That cost
a full day, because **pure-neutral white art is indistinguishable from a white page**:
Mizu's and Tsubasa's eyes measure core luminance 249.0-251.4 and the page measures 251.4.
Every separator that was tried failed — colour, neutrality, flatness, ring brightness, and
re-flooding at a looser threshold. The keyer deleted **both eyes from every beat** before it
was caught, and a later rule deleted **the steel inside Tsubasa's kunai blades**.

- **Send RGBA with a genuine alpha channel.** Then none of that can happen.
- If a baked background is truly unavoidable, **do not use a neutral one** — use a saturated
  colour the art does not contain.
- **Keep the gutters wide enough that no beat's weapon crosses into a neighbour's column.**
  A thrust weapon overlapping the next figure produced two false "floating fragment"
  findings in an earlier review.
- **No card borders, no frame rectangles, no captions inside the figure's box.** A card
  border baked into a cell is already live damage on Mokurai 142, and border lines set the
  bounding box on the Executioner's thrust board, which silently shrinks every figure.
- **No baked ground shadow.** This game draws its own.

---

## 2. THE THREE CELLS

All three are the same failure: **part of the art is missing from an otherwise correct
frame.** The pose, the costume and the framing of the rowmates are right — reproduce the
row's look exactly and put back what is gone.

### 2.1 MIZU — `medium3`, live cell 192 — HER STAFF IS GONE

**Row:** `medium1..8`, cells 190-197. **Cell window 300x320, footY 312, scale 0.3782.**

Every other beat of that row shows her wooden hanbō staff. Beat 3 shows the identical
stance with **no staff at all** — it was erased out of the frame. Measured: her ink bbox is
**114px wide against 136-250px** on the other seven beats; the missing width is the staff.

**Draw:** beat 3 of an eight-beat mid-range staff strike — the beat between a wind-up
(beat 2, staff drawn back across the body) and the extension (beat 4, staff thrust straight
out to the left). Her two hands are on the staff. Same purple layered coat, pointed hood,
purple scarf tails, black void face with **exactly two flat glowing white oval eyes**, black
gloves and boots.

**Size:** her head and body must match beats 1, 2 and 4 exactly. Her idle ink measures
88x161; a standing beat of this row measures roughly 140x149.

### 2.2 MIZU — `heavy_i3`, live cell 184 — HER STAFF IS GONE

**Row:** `heavy_i1..8`, cells 182-189. Same cell window as above.

Same failure, different row. Ink bbox **105px wide against 140-164px** on its rowmates.

**Draw:** beat 3 of an eight-beat heavy staff swing — the loaded beat just before the
committed swing, staff held across the body, both hands on it, weight going forward. Same
identity as 2.1.

**Size:** match beats 2 and 4 of that row (154x151 and 161x151).

### 2.3 KAEL — `krise2`, live cell 284 — HIS LOWER BODY IS MISSING

**Row:** `krise1..8`, cells 283-290. **Cell window 300x320, footY 312, scale 0.4046.**

Beat 2 is **110px tall where its rowmates are 151-195px** — the legs and lower body are not
there. It reads as a torso sitting on nothing.

**Draw:** beat 2 of an eight-beat rising sword launcher — the crouch-and-load beat, knees
bent, blade still low, just before the upward cut of beats 4 and 5. **A full figure standing
on the ground line, both legs drawn.** Kael's identity: dark hooded ninja with **gold** trim
and gold weapon fittings, twin blades — **one long sword and one short sword** — grey scale
armour under the hood.

**Size:** his idle ink measures 93x171. Beat 1 of this row measures 94x151. Beat 2 must
stand at the same body size, in a crouch, with the feet on the same ground line.

---

## 3. House rules for all three

- ONE row per image if you send a row; a single beat is fine as a single image.
- **Left-facing.** Every sprite in this game is authored facing left and mirrored in engine.
- Transparent background, captions BELOW the figure and outside its box, never over it.
- ONE body size across the beats you send: heads, hands and weapons the same size beat to
  beat. A crouch keeps the same head — do not shrink a tucked beat.
- No motion blur, no speed lines, no ground shadow, no background, no border, no panel box.
- Nothing may end in a straight cut. An effect leaving the figure fades to nothing inside
  the frame; a smear touching the canvas edge is a reject. **27 of the 62 live defects in
  this game are cut-offs** — this is the single most common way art arrives broken.
- These are replacement beats inside a live animation, not a redesign. Match the fighter's
  existing shipped cells exactly.
- **Count weapons against the fighter's own shipped cells, not against any document.** A
  handoff README claimed Ember carries three claw blades per hand; he carries four.

## 4. What is NOT being asked of you

Repaired from approved shodo boards already on disk, no generation required:
oni `knives5` (252), oni `wslice6` (329), oni `run_clean7/8` (400, 401), mokurai
`special6/7` (254, 255), mokurai `mthrow3` (315), exile `gsfwd7` (143). Mokurai `kpush`
(142) carries a baked card border but sits behind a key the engine never reads, so it is
invisible in game and is being dropped rather than redrawn.

Already fixed: executioner `xrise5`/`xkiriage5`, executioner `xtsuki1`, exile `xksweep`,
ember `espec1..8`.
