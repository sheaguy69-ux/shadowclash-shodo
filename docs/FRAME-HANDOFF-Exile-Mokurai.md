# FRAME HANDOFF — EXILE + MOKURAI

**For the agent generating the missing frames. Everything needed is in this file plus the
four PNGs in `docs/frame-handoff/`. Do not read anything else in the second brain for
identity — §3 supersedes it, and §0 says why.**

Status: written 2026-08-05 against SHEET_V 346, from a measured audit of the live game
(`tools/audit_move_coverage.py --ids 6,8`), not from documentation.

---

## §0 — STOP. TWO RULINGS BEFORE ANY SPEND

Both are the owner's. Generating before they land wastes money and produces frames that
must be thrown away.

### RULING 1 — Mokurai's sheet holds THREE different characters

Open `docs/frame-handoff/mokurai-identity-board.png`. His 94 cells split into three
incompatible designs:

| Cells | Family | Head |
|---|---|---|
| 44–50 | `canon_*` (the 7 original statics) | **Grey cracked stone**, ruby jewel flush on the forehead, gold eyes, no ear band |
| 51–58 | `brun*` (run cycle) | **Grey stone**, ruby at the temple, plain human ear, blank/closed eye |
| 59–93 | `b*` (everything else — light, heavy, special, jump, air, block, hurt, crouch, kicks, idle) | **GREEN / JADE face** under a grey stone skullcap, gold temple band with the ruby set into it, gold ear-guard |

This is not lighting. It is a different skin colour and a different headpiece.

**It is visible in play right now.** His ground heavy draws cells 64–68 (green). His *air*
heavy falls through to cell 49 (grey stone). Press heavy on the ground, then in the air,
and the fighter changes race mid-combo.

**Owner must pick ONE family.** Everything else gets regenerated to match, and this
handoff's §5 work list assumes the answer.

- Pick **green (`b*`)** → 7 canon cells to redo. Cheapest, and it keeps the side-profile
  family that already carries the whole moveset.
- Pick **grey stone (`canon_*`)** → ~43 cells to redo. Expensive, but the grey stone head
  is what the private roster and the Story Bible describe.

**Recommendation: green (`b*`).** Six times less work, and the `b*` cells are the only
ones in strict side profile — the house medium. The `canon_*` cells are front and 3/4,
which is why they read as a different character even before the colour.

### RULING 2 — Exile's identity lock in the second brain is dead canon

`ShadowClash-Second-Brain/Kunoichi-Identity-True-Lock.md` describes a **hooded, faceless
ninja with white glowing eyes under the hood**. The shipped sheet is **unhooded, with a
huge black-and-silver mane and a cloth eye-wrap over one eye**. They are not the same
character. The lock also still uses her old name, Kunoichi.

The shipped sheet is what renders, and the roster entry calls her "One-eyed exile", so the
sheet is treated as truth here and §3 carries the corrected string. **Do not open that
lock file.** If the owner rules the other way, this whole handoff is void and she needs a
full redraw, not new frames.

---

## §1 — THE LAWS THAT GET FRAMES REJECTED

### Medium
**2D CEL ILLUSTRATION. NOT PIXEL ART.** Clean high-contrast vector-ish look, heavy black
outlines, readable silhouette, controlled dark palette. Roster cells measure ~3900 unique
colours. **PixelLab is the wrong tool — do not use it, do not pack from it** (raw PixelLab
output measures 44 colours).

### Models — import from `tools/sprites/fal_models.py`, never hardcode
| Job | Constant | Endpoint |
|---|---|---|
| Motion / multi-frame | `MOTION_MODEL` | `bytedance/seedance-2.0/image-to-video` — **no `fal-ai/` prefix** |
| Motion, camera-lock critical | `MOTION_MODEL_KLING` | `fal-ai/kling-video/v3/4k/image-to-video` |
| Stills / repose | `STILL_MODEL` | `fal-ai/nano-banana-pro/edit` — takes `image_urls[]`, not `image_url` |

Use `i2v_clip()` and `still_edit()` from that module; they normalise the differing argument
shapes. Audio is forced off. Retired and forbidden: Kling v2.1, flux-pro/kontext.

**Camera lock decides the model, not render quality.** Seedance 2 has no camera parameter
at all and broke lock on both sprite clips it was tried on (measured: character height
+46.96% start-to-end on a Seedance clip vs −2.80% on Kling). Any drift destroys size
registration, which is a hard reject. **All locomotion and all attack arcs → Kling**, whose
`negative_prompt` can FORBID camera motion rather than merely not request it. Use
`NEG_CAMERA` from the same module.

**i2v is the frame source for anything multi-frame.** Frames harvested from ONE clip are
size-registered with each other; independent stills never are. A still editor cannot invent
a pose its reference does not hold — 8 of 8 nano-banana walk attempts returned the standing
stance. For locomotion always i2v, and **measure** the harvested frames rather than
eyeballing them.

### Spend
Pre-authorised — do not ask, report the running total. ~$0.15 per 5s clip. The full list in
§5 is roughly 20 clips plus refires: **budget $10–20**.

---

## §2 — GEOMETRY CONTRACT (hard numbers, do not infer)

| | Exile | Mokurai |
|---|---|---|
| sheet | `web/assets/sprites/exile.png` | `web/assets/sprites/mokurai.png` |
| manifest | `exile.json` | `mokurai.json` |
| `frameW` | **200** | **300** |
| `frameH` | **226** | **226** |
| `footY` | **218** | **218** |
| `cols` now | **43** | **94** |
| `scale` | 0.4667 | 0.4667 |
| sheet px now | 8600 × 226 | 28200 × 226 |

**`frameH` is PER-FIGHTER. Never assume 320.** If a pose does not fit, **grow `frameH`
and `footY`** — never shrink the body, never crop the pose.

### Where new cells go
- **Exile — append only.** New cells start at index 43. Sheet grows 200px per cell.
- **Mokurai — FILL CELLS 0–43 FIRST.** They are fully transparent (verified: alpha maxima
  0 on all 44) and **no slot name points at any of them**. 44 free slots, zero sheet
  growth, and no index can shift because nothing references them. His work list in §5 is
  ~41 cells, so it fits almost exactly. *This writes into cells that already exist, which
  the append-only law technically covers — flag it and take the owner's yes. If he says no,
  append from 94 instead and leave 13,200px of blank sheet.*

### The append-only law
Existing cells stay **byte-identical**. Composite new cells onto the existing PNG; never
re-export the whole sheet from scratch. Verify with a byte compare of the untouched region
before committing.

### Facing
The engine draws with `ctx.scale(-p.facing, 1)` ([web/index.html:8140](../web/index.html)),
so sheet art is mirrored at render time. **Do not reason about this — match the sheet.**
The test: put your new cell beside cell 0 (Exile) or cell 87 (Mokurai). The mane / scarf /
weapon must fall on the **same side**. If it is flipped, flip it back before packing.

---

## §3 — IDENTITY (from the shipped cells — this is the only identity source)

Look at `docs/frame-handoff/<fighter>-identity-board.png` before writing any prompt. The
string below describes what is in those cells; if the two ever disagree, the cells win.

### EXILE — "One-eyed exile. Fastest body and highest jumper."
> Chibi ninja, roughly 3 heads tall, strict side profile. **NO HOOD.** A huge windswept
> **black mane with silver-white streaks**, long and streaming behind her. A **tan cloth
> eye-wrap covering one eye, with dark-red kanji brushed on it**. A **black cloth mask**
> over nose and mouth; the one visible eye is pale and hard, under a heavy dark brow. Pale
> skin. **Black and charcoal ninja garb** — wrapped sleeves, layered skirt panels over
> black trousers. A **deep purple scarf at the neck and two long purple sash tails** off
> the waist. **Tan bandage wraps** on forearms, hands, shins and ankles — a strong
> secondary colour, not a detail. In one hand a **kama sickle**: silver curved blade,
> dark wrapped handle with a red-brown grip. In the other a **chain with a round smooth
> iron weight ball**, dark iron links clearly readable link by link.

**Palette:** garb `#1c1626` · scarf/sash `#6d28d9` accent `#8b5cf6` · eye `#f2f4f6` ·
wraps warm tan · blade silver-grey · chain dark iron.

**THE CHAIN LAWS — she is the only rope-physics fighter and this is where clips fail:**
1. **Thrown = TAUT.** Straight line, every link readable, ball at full extension. Any sag
   on a throw frame = reject.
2. **Hanging or circling = SAG.** Natural catenary. A rigid straight chain at rest reads as
   a rod = reject.
3. **ONE CONTINUOUS OBJECT.** Trace hand → ball on EVERY frame. Broken, vanishing or
   teleporting links = reject that frame. Expect refires; budget for them.
4. **The ball is a round smooth iron weight — never a blade, never spiked.**
5. **The sickle never swaps hands, never duplicates, never vanishes.**

**NEVERs:** never a hood · never a faceless void where her face is · never both eyes
uncovered · never a katana/kunai (her only blade is the curved kama) · never red eyes ·
never gold or red FX (engine FX is pale silver-white) · never a heavy planted read — she
is Speed 10, the fastest body on the roster.

### MOKURAI — "the Sage of Nothingness", bare hands
*Assumes RULING 1 resolves to green (`b*`). If it resolves to grey, swap the head
description for cell 50's and regenerate the other 43 instead.*

> Chibi monk, roughly 3 heads tall, strict side profile. Bald head: a **green-jade face**
> under a **grey cracked-stone skullcap**, a **gold band across the temple with a round
> ruby set into it**, a gold ear-guard, and a **glowing gold eye**. A **saffron / ochre-gold
> robe** with gold trim and a dark meander pattern at the hem, over **dark brown baggy
> trousers**. A **deep red scarf at the neck streaming back**, and a **red sash knotted at
> the waist**. **Dark wooden prayer-bead strands wrapped around both wrists and hanging at
> the chest.** Pale green-white hands and bare feet in low green-grey sandals.

**Palette:** robe `#d98e2b` / `#f0c040` trim · scarf and sash `#7a2230` · trousers dark
brown · eye gold `#f0c040` · beads dark wood · skin jade green.

**NEVERs:** **NEVER a bo staff — he has none and never did** (owner ruling, Aug 5 2026;
the staff is erased from canon, not set down). Never a demon mask. Never a weapon of any
kind — bare hands and bead-wrapped fists only. Never the grey stone head from cells 44–50
in the same sequence as green cells. **Never circular / orbiting wording in a prompt** —
"halo", "360 orbit", "spinning disc" is what unwound his beads into a swinging flail and
cost a whole clip. His gold FX is the engine's; do not bake it into cells.

---

## §4 — THE PIPELINE (already built — reuse, do not rebuild)

```
1. SEED     one still, character LOW in frame with space above
2. GENERATE i2v clip  (tools/sprites/gen_attack_i2v.py · gen_run_i2v.py · gen_registered_i2v.py)
3. EXTRACT  ffmpeg at 12 or 24 fps, then pick the side-profile window
            (clips drift front-facing — harvest where the profile holds)
4. KEY      magick fuzz 42% corner floodfill  → keep largest connected component
            → purge sub-visible alpha LAST.   42, not 25: the drop shadow needs it
5. MEASURE  start-vs-end standing height. >0.5% wobble = fix the scale or refire
6. PACK     pack_attack5.py / pack_i2v_run.py / extend_sheet.py
7. GATE     montage strip + GIF at game fps to the owner BEFORE the sheet is touched
```

**⛔ NEITHER FIGHTER HAS SEED FRAMES.** `media/polished-candidates/` has folders for
ember, executioner, kael, mizu, oni, shin, tsubasa — **and nothing for exile or mokurai**.
Their seeds must be built first: upscale the chosen sheet cell with `STILL_MODEL`
(`still_edit`, resolution 2K) into a clean full-res still, then use THAT as the i2v seed.

Seed cell to upscale: **Exile → cell 0** (idle). **Mokurai → cell 87** (`bidle1`, the
side-profile family).

**Scale law for any sequence:** ONE uniform scale for the whole sequence, anchored on an
upright frame measured against the idle's body height. **NOT per-cell MATCH_HEIGHT** on a
jump or a lunge — it scales the compact apex ~2× against the stretched launch and causes
size boil. (Per-cell MATCH_HEIGHT is correct for flat ground sequences only.)

**Prompt shape**, per the recipe that works:
- Six **numbered beats**, one per frame the sequence needs.
- An explicit **NEVER list** for that fighter's failure mode (§3).
- The literal phrases *"stays on the SAME SPOT"*, *"pure side profile"*, *"both legs
  readable at every frame"*.
- **2500-character cap** including the script's ~900-char wrapper → your `--action` +
  `--identity` must total **≤ ~1600 characters**. Over = HTTP 422.

**fal downloads use `curl`, not python** — the proxy breaks urllib SSL. `FAL_KEY` lives in
the WildComiks `.env.local`.

---

## §5 — THE WORK LIST

Every row was measured in the live game, not read off the source. "Draws now" is the actual
cell the engine puts on screen for that input today.

Priority: **T1** = the move draws a pose that is not an attack · **T2** = two different
moves share one picture · **T3** = polish.

### EXILE — 43 cells, all real art, no blanks. Her problem is collisions.

| T | Input / slot | Draws now | Needed | Cells | The beats |
|---|---|---|---|---|---|
| **1** | **Down+G** low kama slash | cell 29 — her **CROUCH** | its own low armed cut | 4 | drop to a knee → kama sweeps low along the floor → full extension at ankle height → recover to guard |
| **1** | **air G** (all 4 dirs) | cell 30 only, 320ms on one frame | airborne chain hurl | 4 | body turns in air → ball released down-forward → chain snaps taut at full reach → slack, drawn back |
| **1** | **Up+G** UP REACH (420ms) | cell 21, **shared with Up+F** | plant + chain straight up | 5 | plant both feet, weight down → ball whipped overhead → chain **vertical and taut**, ball at ceiling → ball falls, chain sags → catch, settle |
| **2** | **Up+F** up-flick (160ms) | cell 21 | short fast poke, no launch | 3 | quick chamber → sickle flicks straight up above the head → snap back to guard |
| **2** | **Back+G** COUNTER-WEIGHT SNAP | cell 20, **shared with Fwd+G** | the lean-back gap hitbox | 5 | weight shifts onto the back foot → torso leans hard away → ball snaps out at mid-range → held at extension → hauled back across the body |
| **2** | **air Down+F** | cell 22, shared with Sky Down-Smash | its own air-down poke | 2 | knees tuck, sickle points down → short downward stab |
| **2** | **light chain beats 3, 4, 5** | all cell 19 | three distinct beats | 3 | cross-cut → rising cut → spinning finisher, each a separate contact |
| **3** | **IDLE** | cell 0 only — a **single static frame** | breathing cycle | 3 | settle → inhale, chain sways out → exhale, chain sways back *(cell 0 becomes beat 1 of 4)* |
| **3** | **RUN** | 4 real cells aliased to 8 | true 8-phase Williams cycle | 4 | the four missing phases: contact, down, pass, up on the opposite leg |
| **3** | **ROLL** | cell 14 — her **jump apex** | a real tumble | 4 | duck and commit → tuck, shoulder down → inverted mid-roll → rise out low |
| **3** | **JUMP ARC** | 4 cells | 6-cell acrobatic arc (`ajump1..6`) | 6 | crouch launch → rise → tuck → apex inversion → open out, legs reach down → two-foot absorbing landing |

**Exile total: 43 new cells** → sheet grows to 86 cols (17,200px). T1 alone is 13 cells.

> **Exile jump note:** she is the **highest jumper in the roster** (`jumpScale 1.12`) and
> the only fighter without an acrobatic arc — the six originals all have `ajump1..6`. Her
> jump is the most-seen animation she owns and it is 4 static cells. Follow the EMBER
> RECIPE exactly for it: Kling, `negative_prompt` forbidding camera motion and ground
> shadow, six numbered beats, ONE uniform scale, grow `frameH` if the pose does not fit.

**Free, code-only — no art, do these regardless:**
- `hurt` / `hurt2` / `hurt3` in `exile.json` all point at cell 2, which is also
  `run_clean2`. The draw already uses `xhurt1..3`, so these three names are dead. Repoint
  or delete them.
- Stale comment at [web/index.html:7157](../web/index.html) claims her kicks borrow slide
  cells. They do not any more — 40/41/42 are real kick art.

### MOKURAI — 94 cells, **44 of them blank**. His problem is missing art.

*Every row assumes RULING 1 = green (`b*`). New cells go into blanks 0–43.*

| T | Input / slot | Draws now | Needed | Cells | The beats |
|---|---|---|---|---|---|
| **1** | **air G** (all 4 dirs) | cells 49, 47, 50 = his **block pose, jump pose, idle** | an airborne strike | 5 | both fists gathered at the chest mid-air → drive down and forward → contact at full extension → follow-through → recover, feet reaching for the floor |
| **1** | **THROW** | `[cell 49, cell 47]` = **block pose + jump pose** | a real grab | 3 | reach and seize → haul the body across the hip → release with the whole torso |
| **1** | **Fwd+G** | replays neutral heavy | a stepping strike of its own | 5 | step in behind the lead shoulder → elbow drives through → palm lands at full reach → hold → settle |
| **1** | **Down+G** | replays neutral heavy | a low answer | 5 | drop the hips → downward hammer-fist to the floor → impact, dust at the knuckles → hold → rise |
| **1** | **air Down+F** and **Meteor Break** | cell 47 — his jump/fall | a dive | 3 | tuck at the apex → both fists driven straight down → landing compression |
| **2** | **Up+G** BELL RINGER (380ms) | cell 44, **shared with Back+G** | planted anti-air | 5 | feet plant, weight sinks → palm chambers at the hip → driven straight at the sky → held at full extension → arm falls, settle |
| **2** | **Back+G** BUDDHIST PALM (340ms) | cell 44 | the blast, his own | 5 | both palms gather at the chest → weight rocks back → single palm thrust forward → held, arm locked → recover |
| **2** | **air F** fwd / back | no directional variation at all | two directional air lights | 4 | fwd: diving punch ahead · back: reverse elbow behind |
| **3** | **ROLL** | cell 47 | a real tumble | 4 | duck → tuck, shoulder down → inverted → rise low |
| **3** | **WALLSLIDE** | cell 49 — his block | a cling | 2 | palms and feet flat to the wall → sliding, robe dragging up |

**Mokurai total: 41 new cells** → fits in the 44 blanks with 3 to spare, **sheet does not
grow at all**. T1 alone is 21 cells.

**Free, code-only:**
- Cells **91, 92, 93** (`ksweep`/`kpush`/`kheel`) are finished kick art the engine can
  never reach — the Mokurai branch at [web/index.html:7144](../web/index.html) returns
  `bksweep`/`bkfront`/`bkheel` first for all three kicks. Repoint or delete.
- If RULING 1 = green, the seven `canon_*` cells (44–50) become the wrong character and
  need regenerating; that is **not** in the 41 above. Add 7.

---

## §6 — QC GATE. NO CELL PACKS WITHOUT A GRADE.

Grade **every** cell on all 12 dimensions and ship the table with the contact sheet. The
five that kill the most frames on these two fighters:

| # | Dimension | Pass criteria |
|---|---|---|
| 1 | **IDENTITY HOLD** | Matches the §3 string and the identity board exactly. Any feature from a dead design = automatic fail (Exile: a hood. Mokurai: a staff, or the wrong head family). |
| 2 | **WEAPON DISCIPLINE** | Exile: ONE kama + ONE chain + ONE ball, sickle never swaps hands. Mokurai: **bare hands, zero weapons.** |
| 4 | **POSE READABILITY** | Does it read as its move in isolation? "Collapsed toward idle" = FAIL. This is the failure that produced every T1 row above. |
| 5 | **SILHOUETTE CLARITY** | Downscale to 48×64. Still readable? Limbs must not merge into the torso. |
| 6 | **SIZE REGISTRATION** | Target **0.0% wobble**, max **±0.5%** against the sequence median. Above that = reject, not a patch. |

Plus 3 PALETTE MATCH · 7 MOTION PATH · 8 SMEAR LEGIBILITY · 9 CARTOON PHYSICS ·
10 FRAME DATA ALIGNMENT · 11–12 per `17 - Sprite Animation Director Prompt.md`.

**>30% REDO/REJECT on a batch → do not ship the montage. Propose a method change instead.**

### Deliver back, per batch
1. Labelled **contact sheet** of the new cells.
2. **GIF at the real game fps** — cel cuts, never cross-fades. A static assert cannot see a
   ghost, and the owner rules on motion, not on stills.
3. The **12-dimension grade table**.
4. **Measured** start-vs-end height numbers for every i2v sequence.
5. Running **spend total**.

Nothing touches `web/assets/sprites/*` until the owner says yes to the GIF.

---

## §7 — DEFINITION OF DONE

- [ ] Ruling 1 (Mokurai's family) and Ruling 2 (Exile's identity) both signed off
- [ ] Seed stills built for both fighters — neither has one today
- [ ] All **T1** rows shipped: no input draws a block pose, an idle, or a jump frame
- [ ] All **T2** rows shipped: no two inputs share one cell
- [ ] `python3 tools/audit_move_coverage.py --ids 6,8` shows **15/15 ground and 15/15 air**
      distinct, with the `+Special` collapse understood as this branch's neutral-Special
      pin rather than a hole
- [ ] `python3 tools/check_moves.py` passes
- [ ] Sheets appended (or blanks filled) with **existing cells byte-identical**
- [ ] `SHEET_V` bumped in the **same commit** as the sprite change, with the chain entry
- [ ] Owner has seen the GIFs

### Where things stand today (measured, SHEET_V 346)

| | ground distinct | air distinct |
|---|---|---|
| Mokurai | 8/15 | 6/15 |
| Exile | 11/15 | 8/15 |
| the six originals | 10–13/15 | 15/15 |

Both benched fighters are passable on the ground and **starved in the air** — and Exile is
the highest jumper in the game.

---

## FILES IN THIS HANDOFF

| File | What it is |
|---|---|
| `docs/frame-handoff/exile-identity-board.png` | 12 key Exile cells, labelled. **The identity source.** |
| `docs/frame-handoff/mokurai-identity-board.png` | 12 key Mokurai cells — shows the three-family split in Ruling 1 |
| `docs/frame-handoff/exile-sheet-contact.png` | All 43 cells, each labelled with every slot pointing at it |
| `docs/frame-handoff/mokurai-sheet-contact.png` | All 94 cells; the 44 blanks are marked ORPHAN in yellow |
