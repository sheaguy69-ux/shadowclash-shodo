# ONI — THE NEW KIT (owner delivery, Aug 9 2026)

Everything here is transcribed from the owner's own boards in
`RECOVERY/oni-founder/boards-aug9/`. His captions are the state names — where a name
appears in this file it is his word, not an invention. Design canon lives in
`Oni-Identity-True-Lock.md`; this file is the KIT.

**Nothing is packed yet.** No `web/assets/sprites/oni.*` exists and `SHEET_V` is
untouched. Frames go to the owner before the sheet is touched.

---

## 1. THE SOURCES

| File | What it is | Cells |
|---|---|---|
| `MASTER-MOVESET-MATRIX-v2.png` | **the moveset — pack from this** (v1 = same matrix, earlier render) | 32 |
| `MASTER-STATES-CLEAN-alt.png` | the states, **NO captions — prefer this** | 7/8/8/7 = **30** |
| `MASTER-STATES-4x8.png` | the states, red-numeral captions — **the naming reference**, and the only copy of the 2 poses `-alt` lacks | 8x4 = **32** |
| `MASTER-STATES-CLEAN.png` | ⛔ **NOT states, NOT clean** — the captioned SPECIALS board | 8 / 9 / 9 |
| `MASTER-STATES-v2-grouped.png` = `MASTER-SPECIALS-3row.png` | byte-identical duplicates (md5 `e988a749…`), both the bracket-grouped 4-row MOBILITY board | — |
| `MASTER-WIRE-GRABS-4x6.png` | four razor-wire grab sequences | 24 |
| `MASTER-FRAMEDATA-aerials-labelled.png` | **startup / active / recovery per aerial** | 4 x 8 |
| `board-*.png` (9) | one move each, 6 poses, larger | 54 |

⛔ `MASTER-STATES-CLEAN.png` IS THE ONE THAT BIT US, AND ITS NAME IS THE WHOLE TRAP.
`CLEAN` and `CLEAN-alt` are two different boards, not two renders of one, and only
`-alt` is caption-free — so they get one row each above, and a table that pairs them
sends the cutter at a caption board. The base file is ROW 1
NEUTRAL / FORWARD / BACK SPECIALS, ROW 2 UP / DOWN SPECIALS & COMMAND GRAB, ROW 3
SPECIAL IMPACT & RECOVERY STATES — a different move set at a different cell count,
with a white-on-black caption pill over every panel and a 1-2px divider rule between
them. Cutting it *because the table called it the clean one* is how `dash1`/`dash2`/
`dash3` came to carry '5. FORWARD DASH MID', '6. BACKSTEP PREP' and '8. RECOVERY' as
art. That row is the ROOT CAUSE of §7.3 and is why this table is now measured, not
described.

⛔ AND THE TWO STATES BOARDS DO NOT SHARE A GRID — MATCH BY POSE, NEVER BY INDEX.
Measured Aug 11 by segmenting each row, one box per figure with no merges: `-alt` runs
7 / 8 / 8 / 7 = 30 figures, the captioned board runs 8 per row = 32. So `-alt` row 1 is
idle x3, run x3 and a SINGLE forward dash lunge, where the captioned row 1 is
`1 IDLE · 2 RUN START · 3 RUN LOOP · 4 ACCELERATION · 5 RUN LOOP · 6 DASH START ·
7 DASH BURST · 8 DASH END`. Taking "`-alt` cell 6" as DASH START lands on a run. Cut
`-alt` where the pose exists, and fall back to the captioned board only for the two it
is missing, de-captioning as `tools/sprites/recut_oni_dash.py` does on the other lane.

⛔ Filenames were corrected on Aug 9 after an audit: two archives had been named for
what they were assumed to be rather than what they showed. That audit did not catch
these. So do NOT trust the table over the file — open the board, read its own captions,
and believe the pixels. Every row above was re-measured on Aug 11 2026.

---

## 2. FRAME DATA — the owner's own phase split

From `MASTER-FRAMEDATA-aerials.png`. Frames numbered 1-8; the phase bars above them
are his. **This is the timing spec — do not approximate it from the art.**

| Sequence | Category | Startup | Active | Recovery |
|---|---|---|---|---|
| Basic Jump & Landing | Acrobatic Locomotion / Neutral | 1-2 | 3-6 | 7-8 |
| Second Jump Mid-Air Somersault | Special Mobility / Neutral | 1-2 | 3-6 | 7-8 |
| Backflip & Front Cartwheel | Acrobatic Evasion / **Light Attack** | 1-2 | 3-6 | 7-8 |
| Mid-Air Smoke Bomb | Air Down Special / Stage Coverage | 1-2 | 3-6 | 7-8 |

⛔ **BALANCE RULE, owner-stated:** the mid-air smoke bomb is **max 2 per round**.
That is a cap on the move, not a cooldown — it needs a per-round counter, not a timer.

Note that Backflip & Front Cartwheel is categorised as a **light attack**, not pure
evasion: the cartwheel's claw arc is an active hitbox.

---

## 3. STATES (`MASTER-STATES-4x8`, 4 x 8)

| Row | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 |
|---|---|---|---|---|---|---|---|---|
| **Idle & locomotion** | idle | run start | run loop | acceleration | run loop | dash start | dash burst | dash end |
| **Wall & dodge** | wall cling | wall cling (still) | wall jump leap | dodge roll start | dodge roll | dodge roll end | recovery | stand |
| **Jumping & acrobatics** | jump takeoff | jump rise | peak | fall | backflip evasion | backflip land | cartwheel fwd | recovery land |
| **Hurt & knockdown** | light hit | air tumble | air tumble | ground slide | ground slide end | get-up start | get-up | recovery stand |

Owner's note on the wall row: *"the wall-cling uses foot claws to let ONI stay
perfectly still on the wall."* His grip is clawed feet, not a hand hold — the cling
pose must not be re-posed into a hand grab.

---

## 4. THE MOVESET & ATTACK MATRIX (`MASTER-MOVESET-MATRIX-v2`, 4 x 8)

⛔ **This is the moveset. The owner issued it as an explicit spec on Aug 9 and ordered
every non-complying frame removed.** The earlier attacks sheet — jab / palm strike /
front kick / roundhouse / spin kick / back kick / side kick — was a DIFFERENT moveset
and is deleted. Do not reintroduce it or cite it as precedent.

| Row | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 |
|---|---|---|---|---|---|---|---|---|
| **Crouching, sliding & rising kicks** | crouch stance | ground brace | sweep stretch | sweep stretch | prone recover | low guard | axe kick | rising crescent |
| **Low sweeps, dashes & rising punches** | deep crouch | hands down | slide sweep | slide sweep | knee guard | fists cocked | leap punch | rising upper |
| **Claw strikes & ground impacts** | claws out | claws out | claw thrust | claw thrust | ground slam | rising slash | rising slash | rising arc |
| **Aerial kicks, lunges & dive slams** | air kick | air kick | air lunge | air lunge | dive prep | dive prep | dive bomb | dive impact |

Two renders of this same matrix exist (`-v1`, `-v2`); v2 is the cut source.

**HARD RULES he set on this sheet** — these are QC gates, checkable, not taste:
no ground shadow, no floor line, no horizon, nothing under the feet unless it is
impact FX; no numbers, labels or text; no grid lines, cell boxes or dividers; every
effect — speed lines, energy arcs, ground bursts — is vibrant CRIMSON. Continuity of
the horned white mask, the two back-mounted katanas, the hood and the claw gauntlet is
required in every frame. *Checked on all 32 cut cells: zero ground-shadow violations.*

⚠ **ONE DISCREPANCY, unresolved, flagged rather than decided.** The spec's prose says
"dual metal claws" and "slamming both claw gauntlets down". The DELIVERED ART does not
show that — it still shows ONE clawed hand and one wrapped hand, clearest in the crouch
stance where the raised fist is bare cloth wrapping. `Oni-Identity-True-Lock.md` also
says right hand only. Art and identity lock agree, so the single claw stands and the
prose is read as loose wording. If the owner actually wants BOTH hands clawed it is a
redraw — and it would incidentally kill the mirror finding, since a symmetric claw
survives `ctx.scale(-p.facing, 1)` unharmed.

## 5. SPECIALS (`MASTER-SPECIALS-3row`)

- **Neutral / forward / back** (8): energy gather · energy charge · energy burst ·
  forward dash start · forward dash mid · backstep prep · shadow reposition · recovery.
  He *"gathers cursed energy, releases it in a burst, dashes forward as a phantom, or
  repositions backward in shadow."*
- **Up / down + command grab** (9): spiral ascent start · mid ascent spin · peak ascent ·
  descent start · stomp impact · recovery · command grab init · grab execution · finish.
- **Impact & recovery states** (9): energy peak · follow-through · low recovery ·
  kneel recovery · stand reset · energy fade · vulnerable turn · vulnerable end ·
  stance reset. These are the punish windows — *"risk after commitment."*

## 6. RAZOR WIRE — command grabs (`MASTER-WIRE-GRABS-4x6`)

Every sequence is setup → bind → conversion → finish → reset stance. **Wire is
right-hand only**, per his legend.

| Sequence | 1 | 2 | 3 | 4 | 5 | 6 |
|---|---|---|---|---|---|---|
| Forward wire grab → **katana finish** | launch wire | bind target | reel in | close in | katana draw | katana slash |
| Reverse wire grab → **claw finish** | throw behind | bind target | yank backward | position | claw raise | claw rake |
| Air-to-air wire grab → **dual-knife finish** | air wire launch | snare in air | pull in | close range | knife cross | dual slice |
| Air-to-ground pulley → **short-wire slice** | drop & launch | bind ground target | yank up | slam down | short-wire draw | short-wire slice |

This is a full command-grab system: a successful bind ENABLES a weapon conversion.
It also means his katanas and a pair of knives are drawn weapons, not just back décor.

---

## 6b. THE SECOND MODE — BUILT (owner spec, Aug 13 2026)

The owner specced it: he delivered the four boards (`MASTER-WIRE-GRABS-v2` /
`SPECIAL-DIR` / `AERIAL-DIR` / `HEAVY-DIR`) and said **"implement these move sets to
oni second mode = v input."** That closed the Aug 11 park ("base attacks first, second
mode after, and he specifies it") — base was finished at SHEET_V 489-493, and this was
the specification.

**What shipped** (`web/index.html`, check: `node tools/check_oni_mode2.mjs`):

- **V (P2: K) toggles `mode2`**, grounded only, through the roster's one `modeKey()`
  entry point. No cost, no timer — a stance, like chudan and kage-nui.
- **The four board move sets are his kit in BOTH forms.** The owner drove 489-493 to
  make them work in the base kit; the mode never takes them away.
- **In the mode, his NEUTRAL light/heavy are the staff** (`bostrike`/`bosweep`, the
  clean solo renders of his board's staff heavies). Neutral ONLY — a directional press
  draws its own board row. The earlier bo-stance stub drew the staff over every
  direction, which fired `ghfwd`'s box under `bosweep`'s picture; that mismatch is dead.
- **The dash dissolve is the mode's** (his Aug 11 look, verbatim: *"he does not move
  fast, he stops being solid"*): in base form the dash keeps the SOLID beats of the
  blur row (1, 2, 5, 6); the mode plays all six, including the red-black particulate
  beats 3-4. Same row, zero new art, and the mode has a mid-match tell.

Geometry note for this tree: the blur row is `blur1..6` = cells **273-278**;
`bostrike1..6` / `bosweep1..6` = cells **153-164**. (The old "cell 156 = shadowblur /
153-155 = dash keys" numbers were the `lane/fable-5-oni-rebuild` pack, not this one.)
The contaminated caption cells 10-12 (`dash1-3`) remain unreferenced.

## 7. OPEN — needs an owner ruling before packing

**DONE — these were edits on his own frames, not redraws (`tools/sprites/`):**
- the stone slab is off both `wall_cling` cells, claw and foot claws intact (`strip_wall.py`)
- FX lift into a registered `__fx` layer that composites back exactly, his red eyes
  protected, arcs taken whole including their pale cores (`split_fx.py`)
- enclosed page-white pockets keyed out, split from his white MASK on tint (`cut_strip.py`)

**STILL OPEN:**
0. ⛔ **HIS WHOLE SPECIAL TIER IS ART WITH NO ACTION — owner ruling needed.** Measured
   live, not inferred: `triggerSpecialAction` has no `specId === 8` branch at all, so
   pressing Special as Oni spends chakra, burns 0.45s of recovery and spawns **no hitbox**.
   The art is already packed and already wired to the draw switch — `special1..6` (neutral),
   `gsfwd/gsback/gsdown` (grounded directions), `sup` (air up) — so all of it *draws* a move
   that does nothing. §5 above is his own board's description of what those frames are:
   energy gather → burst, forward phantom dash, backward shadow reposition, spiral ascent →
   stomp, plus the wire command grabs of §6. **Nobody specs these but him**, the same ruling
   §6b makes about the second mode.
   The ONE Special of his that works is the **air Down smoke bomb**, which resolves at press
   time in `executeAttack` and never needed the dispatcher.
   ⚠ A missing `SPECIAL_COST[8]` made this worse than dormant and is now FIXED: the
   affordability gate read `stamina < undefined` (false, so it never refused) and then
   `stamina -= undefined` wrote **NaN**, which loses every later comparison — one press
   bricked his chakra for the round (no dash, no roll, no smoke bomb, and `Math.min(100, NaN)`
   could never heal it). The CPU brain also carries `spc: 0` in `CPU_PERSONA[8]`, which is
   what keeps it from rolling for a Special that cannot hit; **raise it the day the tier is
   specced.**
1. **The dummy target.** Every wire-grab frame includes a grey mannequin opponent.
   Those read as sequence references, not packable sprites. Same technique as the wall
   would strip it — say the word and it is an edit, not a redraw.
2. **Dual claw or single?** See §4: his spec's prose says both hands, his art says one.
3. **✅ DONE — `dash1`/`dash2`/`dash3` no longer carry caption text.** Fixed on this
   branch at `12771e6` (SHEET_V 469), which packed clean cells **153-155** off
   `CLEAN-DASHBLUR-6.png` and repointed the three keys at them. Flat-top now reads
   **4.9% / 10.2% / 4.1%**; the worst cell on the whole sheet is `sup1` at 53.1%.
   Fixed independently on `lane/opus5-oni-frames` at SHEET_V 465 by re-cutting the
   ORIGINAL panels in place (`tools/sprites/recut_oni_dash.py`).
   ⛔ **HE NEVER RENDERED THE TEXT — the cells were dirty AND invisible.** `dash1`
     appears nowhere in `web/index.html` outside the SHEET_V notes; the engine reaches
     cells by literal `F.<key>` reads plus `dirCells`' 18 directional stems, and `dash`
     is in neither set — verified on BOTH branches. Driven as well as read: six real
     `executeShunshin` dashes drew cells 0-8, 40, 41, 42 and 67, never the dash cells.
     A latent defect, which is the argument for fixing it cheaply rather than for having
     left it. Reachability and cleanliness are independent; `audit_frame_hygiene.py`
     exists because a cell can fail one and pass the other.
   ⛔ **AND `CLEAN-DASHBLUR-6.png` IS NOT WHERE THE CONTAMINATION CAME FROM.** It is a
     good board and this branch cut the replacement beats from it, but it never explained
     the bug. The contamination came from **`MASTER-STATES-CLEAN.png` row 1, panels
     5 / 6 / 8** — FORWARD DASH MID, BACKSTEP PREP, RECOVERY. Identified three ways that
     agree: the pill text reads back literally once un-mirrored, the silhouettes match
     panels 6 and 8 at IoU 0.91 / 0.78, and his white mask measures the same 0.78-0.80
     ratio in all three. The cut landed on the wrong BOARD, not merely the wrong grid,
     and §1's table is why — that row is the ROOT CAUSE.
   ⛔ **STILL DIRTY: cells 10, 11 and 12 are UNREFERENCED BUT STILL IN THE PNG**, and
   still measure 100% / 100% / 96.7%. `12771e6` appended rather than overwrote, which is
   correct under append-only, but it means the caption art still ships in the file.
   `audit_frame_hygiene.py` now sweeps every cell in the sheet, not only the ones
   `frames{}` points at, and names these three as a WARNING — it used to walk
   `sorted(used)` and so reported "zero contaminated" while they sat there. Left as a
   warning because orphans are legitimate under append-only; blank them in a pass that
   says so if the dead weight is worth a commit.
   ⛔ **GEOMETRY IS PER-BRANCH — CHECK IT, DO NOT ASSUME.** This branch is
   **420x300, footY 268**. The `lane/opus5-oni-frames` tree moved to 480x372 / footY 330
   around SHEET_V 463. A cut placed for one does not drop into the other.

## 8. THE CLAW HAND — solved by mirroring, no redraw

The generator could not hold the claw on one hand. Measured across the 32-cell matrix:
claw LEFT in 16 cells, RIGHT in 10, ambiguous in 5. That is the owner's complaint,
quantified.

**Two findings decide what to do about it.**

*It barely matters in play.* The roster renders ~70px tall. At that size the claw is
3-6 pixels — a dark smudge whose handedness is not readable. Rendered at 70 / 140 /
280px side by side, it only becomes legible around 2x game size. So gameplay can carry
the inconsistency; the select portrait and any close-up cannot.

*And it is free to fix anyway.* He is symmetric in everything else — hood, horns, mask,
the two X-crossed katanas, the armour all read identically flipped (checked by eye on
four cells). So MIRRORING a cell moves the claw to the other hand and changes nothing a
viewer can name. `tools/sprites/normalize_claw.py` finds the claw as the thin mass left
after eroding the body core, scores it either side of the centroid, and flips the
outliers: **10 flipped, 16 already correct, 5 ambiguous — 31 of 32 normalised, zero art.**

⛔ **THE TARGET SIDE IS SET BY THE REFERENCE, NOT BY THE MAJORITY — this is the trap.**
Mirroring swaps ANATOMY: a mirrored figure holds the claw in the other hand, which is
precisely what his checklist forbids ("no mirrored claw errors — never on left hand").
So "make every cell match the majority" is wrong; the majority can be wrong. The main
reference is front-facing with the claw on the **viewer's LEFT**, which is **his RIGHT
hand**, and that is the target. Normalising to the viewer's right instead would have put
the claw on his LEFT hand in all 32 cells and failed checklist items 1, 2 and 4 at once.
`normalize_claw.py` defaults to `--side L` for that reason.

⛔ This also disarms **the mirror finding**. `ctx.scale(-p.facing, 1)` flips the whole
sprite on a side change; once every cell is normalised, the per-cell `mirror` map pins
handedness in either facing. The finding stops being a redraw and becomes a manifest flag.

The one cell reported with NO claw, `r4_4_air_lunge2`, turned out not to be a missing
claw at all — it is a 74x133 fragment of pure speed lines, i.e. a bad CUT boundary on
row 4. The detector caught a cutting bug, which is worth keeping.
4. ⛔ **THE MIRROR FINDING — still unresolved and now load-bearing.** His reference
   locks *"right hand = metallic claw gauntlet, left hand = wrapped cloth"* and
   *"face right, never flip claw to left."* The engine mirrors every fighter with
   `ctx.scale(-p.facing, 1)` on each side change, so packed as drawn, his claw lands on
   his LEFT hand every time he turns — failing the owner's own checklist item 4 by
   itself. Options: accept the flip, author a second facing, or split the claw into an
   overlay. Costs art either way, so it is his call.
