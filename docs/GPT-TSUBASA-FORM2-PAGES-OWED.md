# TSUBASA — FORM 2 (SAKATE, the Founder's Grip) — 8 pages owed

Written Aug 9 2026 against the packed sheet. Tsubasa's sheet is `tsubasa.png` /
`tsubasa.json`: **301 × 320 px cells, 190 of them in one row, footY 312, import
scale 0.3608.** The next free cell is **190**.

**What Form 2 is:** he flips both tantō to **reverse (icepick) grip** and fights
the discipline as the founder wrote it. This is canon three times over —
`tsubasa.json` names his discipline *"Tantōjutsu (Reverse-Grip)"*, Oni's identity
lock carries Tsubasa's fragment as *twin reverse-grip tantō at the sash*, and the
Story Bible gives him the creed the mechanic is built on: *one exact cut,
delivered a heartbeat after the enemy commits.* Form 1 is his own way (forward
grip, the alternating rush). Form 2 is the inheritance — the school Kael was
handed, fought by the student who was better.

**Two rows come off his own sheet for free** (verified by eye, Aug 9):

- `rgrush1-6` (cells 88-93) — **already reverse grip.** This row is the Form 2
  dash attack as-is, and its ready beats are the Form 2 stance idle. **It is also
  the grip reference for every page below** — match those daggers, those handles,
  that fist.
- `divecut1-6` (cells 76-81) — the air dive already drives both blades tip-down.
  It is the Form 2 air heavy as-is.

**Form 2 also gets its own locomotion** (owner ruling, Aug 10): a full
reverse-grip movement set, pages 9-16 below, routed per-stance the way Oni's
modes route theirs. Until those pages land, neutral holds the `rgrush` ready
beat.

---

# ⛔ THE SPEC — follow this exactly, it is not stylistic

Identical to the Shin Form 2 spec; every rule exists because breaking it cost a
redraw or a page.

**PAGE**
- **One MOVE per page. Do not stack several moves on one page.**
- Page **2000-2200 px wide**, one horizontal row.
- Background **pure white `#FFFFFF`**. No panel boxes, no borders, no framing
  rectangles around the figures, no drop shadows, no paper texture.
- A title across the very top is fine and will be removed automatically — **but
  it must not touch or overlap any figure**, and it must sit entirely in the top
  fifth of the page.
- **⛔ NO FRAME NUMBERS.** No "1 2 3 4 5 6" under or over the figures, no
  captions, no labels, no arrows. Numbers sitting below a figure fall inside its
  cut and key onto the sheet as floating glyphs.

**THE SIX FIGURES**
- **Exactly six**, left to right, in beat order.
- **Each figure 380-450 px tall.** This is the single most important number.
  Art comes in at roughly 0.4-0.7x and every correction on the way in is a
  DOWNSCALE — nothing is ever interpolated up, so a figure drawn small is
  unusable and the page has to be redrawn.
- **⛔ SIZE ERRS OVER, NEVER UNDER.** If a figure cannot land inside 380-450 px,
  draw it BIGGER, never smaller — oversized art downscales clean, undersized
  art is a dead page. When in doubt between two sizes, take the larger one.
  (Attempt 1 died at ~150 px figures.)
- **A real white gutter of at least 40 px between neighbours**, and nothing may
  cross it — not a blade, not a motion smear, not a spark. Each figure's effects
  belong to that figure alone.
- **Keep the whole pose inside its own space**, including clear air past the
  blade tip. Nothing may run to the page edge.
- **⛔ ONE CHARACTER SIZE ACROSS ALL SIX.** Head-to-heel height stays the same in
  every beat, changing only because the pose crouches or extends.

**THE VIEW**
- **⛔ STRICT SIDE PROFILE, facing RIGHT, all six beats.** One eye visible, the
  chest edge-on to camera — never squared. A beat showing BOTH eyes or the full
  chest is a 3/4 or frontal pose and is a reject; it cannot enter a side-profile
  fighter. (Attempt 1 failed this on nearly every figure.)
- Clean 2D cel illustration: heavy black outlines, flat controlled shading,
  readable silhouette. **Not pixel art.**
- **⛔ NO GROUND SHADOW, NO FLOOR LINE, NO CONTACT SHADOW.** Not a soft ellipse,
  not a horizontal rule, not a scuff. It keys as a gray streak welded under his
  feet and cannot be removed without cutting into the boots. The engine draws its
  own shadow.

**SIX REAL BEATS — this is where pages actually fail**
Not six near-copies of one pose. The row must read as a move:
**wind-up → commit → CONTACT → follow-through → recovery → settle.**
The contact beat — the frame where the blade reaches the target — is mandatory
in every row below; rows missing it jump from wind-up to recovery on screen and
have to be redrawn.

---

# WHO HE IS — identical in every beat

Compact chibi build, upright and exact — he is the precisionist of the six, and
his poses are economical, never wild. **Unhooded spiky black hair with red
streaks** (the hair is the silhouette — a hood appearing = regen). **Black mask
over the lower face; white glowing angled eyes**, featureless — no other facial
feature reads. **Red scarf**, black outfit with **dark-red trim**, red sash, red
forearm and shin wraps.

**THE WEAPON — both forms:** exactly **TWO short silver tantō**, one per hand,
matching the daggers in `rgrush1-6` (cells 88-93) — same blade length, same
handles, same fists. **In Form 2 every grip is REVERSE (icepick): blade emerges
from the bottom of the fist, tip down or trailing.** A forward-grip fist on any
Form 2 page is a reject — the grip IS the mode tell.

**⛔ NEVER DRAW:** a third blade, or an empty hand — BOTH hands work; the off
hand chambers live at the ribs, never dangling (alternation law). No katana, no
long sword, no wire, no shuriken. No hood. Red stays hair streaks, scarf, sash,
wraps and trim only — a red torso or red sleeves is an accent flood, regen.

**SCALE ANCHOR (measured, not guessed):** his idle body measures **193 px tall**
inside the 301 × 320 cell. Every page is cut and rescaled to land the new poses
in the same band. Draw the figures at the 380-450 px page size and the pipeline
handles the rest — just keep the six consistent with each other.

---

# THE EIGHT PAGES

## LIGHT CHAIN — reverse-grip rakes (fast, short, exact)

### 1. `f2_light1_backhand_rake` — Backhand Rake
The lead hand whips a **backhand rake across the chest line**, blade trailing
the fist. Fastest thing in the stance, so the wind-up is a twitch, not a cocked
arm. Beats: minimal coil, blade low → the backhand fires → **edge through the
chest line, contact** → wrist carries past → the arm folds back in → settled
ready, both tips down.

### 2. `f2_light2_inward_rip` — Inward Rip
The other hand answers: a **short inward rip on the opposite diagonal**, high to
low. Beats: off-hand chambers at the ribs → the rip starts → **edge through the
ribs line, contact** → blade finishes low across the body → re-chamber → settle.

### 3. `f2_light3_scissor` — Scissor Cut
His signature, the cut Oni's Mode II borrows: **both blades scissor closed in
the same instant**, crossing at the enemy's collar height. Beats: both arms
open wide, tips down → the scissor drives → **blades crossing at the target
line, contact — the money frame** → fully crossed, X held → arms uncross →
settle.

## HEAVY CHAIN — the committed cuts

### 4. `f2_heavy1_turning_slash` — Turning Slash
The whole body pivots through a **wide reverse-grip arc**, rear shoulder coming
all the way around. His longest Form 2 reach — still shorter than any sword.
Beats: blade wound behind the shoulder, torso coiled → the pivot launches →
**edge through the target arc, contact** → arm at full sweep past him → the
body unwinds → settle.

### 5. `f2_heavy2_double_drive` — Double Drive
Both blades **driven down together** into collarbone height, body dropping
behind them. The guard-chipper. Beats: both blades raised over the shoulders,
tips down → the drive commits → **both points at collar height, contact** → a
hair of recoil through the arms → blades pull free → settle.

### 6. `f2_heavy3_answer` — THE ANSWER (counter-KIME)
The creed made visible: **one step in, one exact cut** — a single reverse-grip
draw straight across the throat line, the other blade chambered and still. This
row is also the marked-punish KIME the engine fires after a Form 2 parry, so
beat four must be readable held on its own. Beats: low and still, reading →
the step-in, sudden → **the one cut, full extension across the throat line,
contact — held, certain** → follow-through, blade past him, body finished →
the return, unhurried → settle. Whiff must read different from hit: the
recovery is a distinct pose, never the wind-up reversed.

## LOW & STANCE

### 7. `f2_crouch_light_hamstring` — Hamstring Rake
A quick **crouched reverse-grip rake at ankle height**. He stays in the crouch
for all six beats. Beats: crouched, blade tucked → the rake begins → **edge at
ankle height, contact** → carry past → re-tuck → settled crouch.

### 8. `f2_parry_mark` — The Read (parry + mark)
The Form 2 parry: **both blades snap into a reverse-grip cross and CATCH** — and
then nothing. No riposte in this animation; the punish is page 6. Beats: ready →
the cross snaps up → **the catch, blades crossed against the incoming line,
contact** → the catch holds, his eyes flare (the mark — a small white flare at
the eyes, nothing else glows) → the blades ease apart, still up → settled ready.

---

# THE LOCOMOTION PAGES (9-16) — owner-approved Aug 10

Same SPEC, same fresh-chat one-page protocol, reverse grip in every beat.
The two archived movement boards (`movement-board-a/b.png`) are **pose
references only** — never a source to trace, never an attachment to GPT.
Two page-specific amendments: the **idle and crouch pages may breathe**
(their six beats differ only by breath rise/fall and scarf drift — the
no-near-duplicates rule is waived for held loops), and the **run page holds
EIGHT figures**, not six (house run cycles are 8-frame), each still ≥350 px
tall.

### 9. `f2_idle` — Stance Ready (loop)
Weight low and coiled, both blades tip-down, off elbows loose. Six breath
beats: settle → sink → bottom → rise → top → return-to-1. Beat 6 must flow
into beat 1.

### 10. `f2_run` — Run Cycle (8 figures, loop)
Full alternating cycle: contact → down → passing → up, each side. Deep
forward lean, blades trailing reverse-grip at his sides, scarf streaming.
Beat 8 flows into beat 1. No dust, no speed streaks crossing gutters.

### 11. `f2_jump` — Jump Arc
Load crouch → launch leaving the ground (stretch) → rising tuck → apex →
falling, legs reaching down → braced pre-land, still airborne. Beats 3-6
fully airborne.

### 12. `f2_crouch` — Crouch Hold (loop)
Drop into the deep crouch by beat 2, then HOLD it — beats 3-6 are the held
crouch breathing, blades ready tip-down. Never stands back up.

### 13. `f2_dash` — Dash
Explosive forward burst: coil → launch lean → full extension at speed →
carried momentum → braking skid → stance. Streak FX stay inside the figure's
own space.

### 14. `f2_roll` — Dodge Roll
Duck → tuck entering the roll → FULL BALL mid-roll (hair and scarf still
readable) → unrolling → rising → ready. Blades stay in hand throughout.

### 15. `f2_land` — Landing
Falling brace → contact squash, knees eating it → deepest absorb → push
back up → nearly upright → settled stance. **No dust, no impact FX** — the
engine draws the landing cushion itself.

### 16. `f2_block` — Block / Guard
Blades snap into a tight low reverse-grip cross braced against the body →
the brace holds through four beats (small shudder allowed) → release back to
ready. Distinct from The Read: this is tight and defensive, no flare, no
catch.

---

# What is NOT asked for

So none of it gets drawn by mistake:

- **A dash attack.** `rgrush1-6` (cells 88-93) is already reverse grip and IS
  the Form 2 dash. Reference it; do not redraw it.
- **An air heavy.** `divecut1-6` (cells 76-81) already dives blades-down and IS
  the Form 2 air heavy. Reference it; do not redraw it.
- **A crouch heavy.** Form 1's low tantō row (`lowtanto1-6`) stays the crouch
  heavy in both forms for now; if the stance needs its own later, the useful
  thing is to say so — not to pre-draw it.
- **Any Form 1 row.** The forward-grip chains, the pass-through slash, the
  Tanto Flurry and the parry stance come straight back when the stance drops.
- **A katana, or anything of Kael's.** The stolen-daishō idea was considered and
  parked — Form 2 is his own two knives, held the way the founder held them.

---

# Engine notes (for whoever wires it — not for GPT)

- **Entry:** `modeKey()` dispatch, `spec.id === 3` → `toggleSakate()`, copied
  from Shin's `toggleKageNui` shape. V is currently DEAD for Tsubasa — the
  chudan fall-through gates on an `idle_chudan` cell his sheet does not have
  (verified) — so the binding takes nothing away.
- **The mechanic — the read:** in Form 2 his parry does not riposte. A caught
  hit sets a mark on the attacker (~1.5 s, one use). His next hit on a marked
  opponent is the counter-KIME: plays `f2_heavy3_answer`'s KIME beat, bonus
  damage, and the hasuji edge lands **true** unconditionally (the `74e8bf5`
  window, forced). You commit, he answers.
- **The trade:** Form 2 startup faster across the board, reach shorter —
  reverse-grip tantō is the shortest steel in the game. Form 1 stays the safe
  rush; Form 2 must get close and must read.
- **Stance visuals:** attack reuse stays — dash attack = `rgrush` row, air
  heavy = `divecut` row, crouch heavy = `lowtanto` row. Locomotion routes
  per-stance once pages 9-16 land (`f2_idle/run/jump/crouch/dash/roll/land/
  block`), Oni-mode style: an art lookup on the stance flag, no second state
  machine. Until then neutral holds `rgrush1`.

---

# On delivery

Each page is cut, keyed at fuzz 42%, scaled against the 193 px idle body band
and appended to the sheet from cell 190 — **append-only, existing cells stay
byte-identical.** Every row ships with a 12-dimension grade table and a montage
for sign-off before anything is packed. Rows arrive one move per page; a page
with two moves on it cannot be cut.

---

# ATTEMPT 1 — Aug 9 2026: three 8-move boards. Design boards, not pages.

Archived in `RECOVERY/tsubasa-form2-handoff/gpt-delivered/board-{1,2,3}.png`.
Beautiful and useful — the choreography is now pickable — but **zero of the 144
figures can pack**, measured, for four structural reasons:

1. **3/4-front facing everywhere.** Both eyes and the squared chest visible on
   nearly every figure; the game needs strict side profile. Automatic reject
   (Doc 17). This is why THE VIEW above now spells out the one-eye rule.
2. **Figures too small.** Median body height 147-152 px against the 193 px
   band → every cell would be a ~1.3x UPSCALE (worst 1.79x). The pipeline is
   downscale-only; Shin's pages worked because figures were 380-450 px.
   Eight moves on one 1536-wide board cannot physically hold the size.
3. **Grid furniture.** Panel borders, titles, input labels, and beat captions
   under every figure — all of it falls inside the cuts.
4. **Ground shadows** under most figures; the engine draws its own.

**Choreography grades** (V1/V2/V3 = boards 1/2/3; V2 has the cleanest grip
discipline and identity overall — feed it back as the pose reference):

| # | move | verdict | note for the redraw |
|---|---|---|---|
| 1 | Backhand Rake | **APPROVED** (V2 base) | beats 4-6 pad toward idle on all three — draw the doc's distinct recovery beats |
| 2 | Inward Rip | **APPROVED** (V2 base) | V1 slips to forward grip in beats 5-6 — reverse grip every beat |
| 3 | Scissor Cut | **APPROVED** (V2 base) | the X money-frame works; open the arms WIDE in the wind-up |
| 4 | Turning Slash | **REDO** | the pivot became an FX ring around a static frontal body; the BODY must rotate through the cut — legs cross, shoulder leads, blade path visible |
| 5 | Double Drive | **APPROVED** (V2 base) | keep both blades readable THROUGH the contact burst — if the burst hides the steel, shrink the burst |
| 6 | The Answer | **APPROVED** (V2 base) | contact pierce + crescent follow-through both read; keep beat 4 readable standalone (it doubles as the punish KIME) |
| 7 | Hamstring Rake | **REDO** | he stands up in every variant — the crouch must HOLD for all six beats; keep the ankle-height arc |
| 8 | The Read | **REDO — wrong move drawn** | a feint-into-cut was drawn and its beat 3 has no contact at all. The page owed is the PARRY: reverse-grip crossed CATCH → the catch holds, eyes flare (the mark) → blades ease apart. No riposte in this row — the punish is page 6 |

# ATTEMPT 2 — Aug 10 2026: the board again, smaller. The CHAT is the problem.

Asked for page 1 only; received another 8-panel board at 1122 × 1402 — figures
measure 131-180 px (median ~154, still under the 193 band), most rows hold five
or fewer separable figures (neighbours touch — gutter violations), titles and
panel borders again, and two NEW identity breaks: **blades drifted to
short-sword/katana length** in Double Drive and The Read, and a **white chest
emblem** appeared. One real improvement: heads are now mostly true profile,
single eye. Verdict: unusable, same size/format kills.

**Diagnosis:** the chat session is anchored to its own board format — every
generation inherits the poster layout from the images before it. Iterating in
that chat will keep producing boards. **The fix is a FRESH chat per page**:
attach ONLY the real game idle (`media/polished-candidates/tsubasa/truecolor-raw/idle.png`)
as identity reference — never a board, it re-anchors the format — and paste the
one-page prompt with the beat script in text.

**The ask back to GPT:** eight pages, ONE move per page, per THE SPEC above —
2000-2200 px wide, six figures 380-450 px (**err BIG, never small — over the
size the pipeline downscales clean; under it the page is dead**), strict side
profile facing right, white background, no text below the title fifth, no
ground shadow. Moves
1/2/3/5/6 redraw their V2 row at full size with the notes above; 4/7/8 redraw
from the beat scripts in THE EIGHT PAGES. The input labels on the boards
("FORWARD + SPECIAL" etc.) are GPT's invention — the kit's real wiring lives in
the Engine notes and does not appear on art.

# LOCOMOTION DELIVERED — Aug 10 2026: pages 9-16 in one drop, 8/8 PASS

The fresh-chat protocol held for the whole movement set. Eight single-move
pages (2172 × 724; run 2222 × 707), strict side profile, single eye on every
beat, no ground shadow, no dust on the landing. Figures 313-506 px — idle ~500
(the over-never-under law obeyed), run 313-321 (under the stated 350 floor but
still a pure 0.556 downscale to cell scale — MINOR, waived). Originals
archived in `RECOVERY/tsubasa-form2-handoff/gpt-delivered/loco/`; cut + keyed
cells staged local in `media/pages/tsubasa-form2-loco/` (50 figures: run has
eight, the rest six).

**Scale law used:** ONE uniform scale per row (Ember recipe), cross-row
calibrated by INK AREA — idle pinned to the 193 px Form 1 body, every other
row scaled so its median ink matches idle's at cell scale. Sanity: crouch's
standing beat lands 193 exactly, block guards 191, roll's stance beats 188/187.

| page | row verdict | measured |
|---|---|---|
| 9 idle | **PASS** | bodyH 190-193, ink spread 3.2% — a true breath loop |
| 10 run | **PASS** | 8 beats, REAL leg alternation (contact/recoil/passing both sides), bodyH 174-179 |
| 11 jump | **PASS** | crouch 163 → launch 185 → apex 172 → fall; engine supplies the arc |
| 12 crouch | **PASS** | settle 193 → hold 144-145, matches the lowtanto deep-crouch band (148) |
| 13 dash | **PASS** | deep lean 134-155, blades trailing |
| 14 roll | **PASS** | full inversion, bodyH 188→89→187; 52% ink spread is tuck occlusion, not size boil |
| 15 land | **PASS** | airborne 173 → squash 124 → recover 188, NO dust as specced |
| 16 block | **PASS** | spark on beat 3 is NOT a spec kill — see ruling |

**Block ruling:** the engine's `STATE.BLOCKING` draws `F.block` as the guard
hold and `F.block2` only while `blockPushTimer > 0` — a dedicated
impact-reaction cell. Beat 3's gold spark IS that cell: route clean beats as
the `f2_block` hold and the spark beat as `f2_block2`, and the flare only ever
shows the instant a hit lands on guard. No FX surgery, no redraw.

**Unpacked.** Nothing on the sheet moves until the owner OKs the montage —
same gate as attack rows 1-8, which also remain QC-PASSED and UNPACKED.

# CORRECTION — Aug 12 2026: TWO rows are owed, not one, and "full resolution" was wrong

A claim was made that only a Form 2 air attack was still owed and that
everything else on the owner's 9-row board was "already covered at full
resolution". The owner challenged it. Measured, it is wrong on two counts and
unproven on a third.

**1. TWO of the nine board rows run on borrowed Form 1 art, not one.**

| board row | draws | status |
|---|---|---|
| DASH ATTACK | `rgrush` 88-93 | **Form 1, borrowed** (reverse grip, but not Form 2's own row) |
| AIR ATTACK | `divecut` 76-81 | **Form 1, borrowed** |
| IDLE · RUN · JUMP · CROUCH · CROUCH ATTACK · DODGE ROLL · BLOCK/GUARD | 238-243 · 244-251 · 252-257 · 258-263 · 226-231 · 270-275 · 282-287 | Form 2's own |

`rgrush` was wired as the dash cut in this same session and then left out of the
tally an hour later. One row was named; two are borrowed.

**2. The borrowed rows are NOT scale-matched to Form 2.** Never measured before
the claim; measured now, as median ink per row:

| row | bodyH | median ink | vs Form 2 idle |
|---|---|---|---|
| FORM 1 idle | 192-193 | 19017 | 1.55x |
| **rgrush** (dash cut) | 178-183 | **16438** | **1.34x** |
| **divecut** (air heavy) | 156-222 | **17317** | **1.41x** |
| Form 2 idle | 190-193 | 12247 | 1.00x |
| Form 2 rows (all 16) | — | 12197-14981 | 1.00-1.22x |

Form 1 and Form 2 are drawn at the same HEIGHT but different MASS — Form 1
carries 1.55x the ink at an identical 193px body. Height-anchoring cannot
equalise that, which is why the Form 2 set is internally consistent (12.2k-15.0k
ink, feet pinned at y=311) while the two borrowed rows sit well above it. He
visibly BULKS UP on the dash cut and the dive cut, and divecut's body peaks at
222px against Form 2's 193px ceiling. Rescaling them is not available: both are
shared with Form 1 and the sheet is append-only, so fixing the pop means Form 2
cells of their own.

**3. UNVERIFIED — does Form 2 keep the METEOR BREAK (air Down+Heavy)?** Form 1
fires it: 3 hitboxes (16 + 9 + 9, the plunge and its two-sided landing
shockwave), measured through the real input path. A matching clean Form 2 run
was never obtained — the harness kept losing either the jump edge-trigger or the
V toggle, and two earlier "results" were traced to leaked `slamPhase` and to
over-resetting fields. **Not claimed either way.** Owner check, two seconds:
jump, hold Down, press Heavy, in each form, and see whether the plunge fires.

**Pages now owed: TWO** — `f2_air` and `f2_dash_attack`, both at the working
spec (2000-2200px, six figures 380-450px, fresh chat, idle.png attached).
