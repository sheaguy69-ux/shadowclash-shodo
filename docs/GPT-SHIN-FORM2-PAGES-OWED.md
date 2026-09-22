# SHIN — FORM 2 (KAGE-NUI) MELEE KIT — 9 pages owed

Written Aug 8 2026 against the packed sheet. Shin's sheet is `shin.png` /
`shin.json`: **300 × 320 px cells, 204 of them, footY 312, import scale 0.3431.**
The next free cell is **204**.

The Form-2 *wire* move is already live in the engine and needs no art — the
shuriken, the taut tether and the razor-slice streaks are drawn procedurally.
**What is owed is the MELEE kit**: in Form 2 Shin drops bare-handed taijutsu and
fights with kunai. Nine moves, nine pages, six beats each.

He already owns `kunaidash1-6` (cells 98-103) — real kunai-in-hand poses. **Look
at those first.** They are the reference for how the kunai reads in his hand, and
the new pages must match that weapon, that grip, and that character size.

---

# ⛔ THE SPEC — follow this exactly, it is not stylistic

Every rule below exists because breaking it cost a redraw or a page.

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
- **A real white gutter of at least 40 px between neighbours**, and nothing may
  cross it — not a kunai, not a motion smear, not a spark. Each figure's effects
  belong to that figure alone.
- **Keep the whole pose inside its own space**, including clear air past the
  kunai tip. Nothing may run to the page edge.
- **⛔ ONE CHARACTER SIZE ACROSS ALL SIX.** Head-to-heel height stays the same in
  every beat, changing only because the pose crouches or extends.

**THE VIEW**
- Facing **RIGHT** in all six beats. Never facing left.
- Clean 2D cel illustration: heavy black outlines, flat controlled shading,
  readable silhouette. **Not pixel art.**
- **⛔ NO GROUND SHADOW, NO FLOOR LINE, NO CONTACT SHADOW.** Not a soft ellipse,
  not a horizontal rule, not a scuff. It keys as a gray streak welded under his
  feet and cannot be removed without cutting into the boots. The engine draws its
  own shadow.

**SIX REAL BEATS — this is where pages actually fail**
Not six near-copies of one pose. The row must read as a move:
**wind-up → commit → CONTACT → follow-through → recovery → settle.**
The last three rows that had to be redrawn were each missing the CONTACT beat —
the frame where the weapon reaches the target — so on screen the move jumped from
wind-up straight to recovery. **The contact beat is mandatory in every row below.**

---

# WHO HE IS — identical in every beat

Lean, low-slung, fast. **Dark green / teal wraps**, teal scarf, bound forearms
and shins. **ICE-CYAN glowing eyes**, featureless and angled — no other facial
feature reads. He fights out of a signature **low coiled crouch**, lower than the
rest of the roster; keep that low centre of gravity even in the extended beats.

**⛔ NEVER DRAW:** orange, purple, or gold anywhere on the body. No sword, no
katana, no staff, no claws — **kunai only** in Form 2. No hood-and-cape silhouette;
he is wraps and scarf.

**THE WEAPON — Form 2 only:** the **kunai**, a leaf-shaped black iron blade with a
**ring pommel**. Match the ones in cells 98-103. Where a move calls for two, he
holds one in each hand in a reverse-and-forward pair. The ring pommel matters —
one move below hooks a guard with it, so it must be visible and drawn the same
in every page.

**SCALE ANCHOR (measured, not guessed):** his idle body measures **194 px tall**
inside the 300 × 320 cell. Every page is cut and rescaled to land the new poses in
the same band. Draw the figures at the 380-450 px page size and the pipeline
handles the rest — just keep the six consistent with each other.

---

# THE NINE PAGES

## LIGHT CHAIN — kunai quick-slashes

### 1. `f2_light1_poke` — Poke
A rapid, low-telegraph **linear jab** with the kunai tip, aimed at throat height.
Fastest thing he owns (4-frame startup), so the wind-up is **tiny** — a twitch of
the shoulder, not a cocked arm. Beats: minimal coil → arm fires → **tip at full
extension, contact** → the hand starts back → retract → settled low stance.

### 2. `f2_light2_slice` — Rising Slice
A **diagonal upward slice** cutting across the chest, low to high. Beats: blade
drops to his hip → the cut starts → **mid-arc contact across the chest line** →
blade continues past the shoulder → wrist rolls over → settle.

### 3. `f2_light3_double_thrust` — Double Thrust
A rapid **dual-hand forward thrust**, both kunai driving in together. This one
chips through a guard, so it must read as *committed* — both arms out, hips square
behind it. Beats: both blades chamber at the ribs → drive → **both tips at full
extension, contact** → a hair of recoil → arms draw back → settle.

## HEAVY CHAIN — rending blade thrusts

### 4. `f2_heavy1_tsuki` — Tsuki Poke
A deep **lunging forward thrust** with maximum horizontal reach — the longest
thing in the kit. Beats: deep coil back over the rear leg → the lunge launches →
**front foot planted, arm and blade at absolute full extension, contact** →
holds the extension a beat → weight recovers back → settle.
*Keep the whole lunge inside the figure's gutter — this is the page most likely to
cross into its neighbour.*

### 5. `f2_heavy2_cross_slice` — Cross-Slice
A **wide horizontal cross-slice with two kunai**, arms scissoring open. Beats:
both blades wound across the body → the sweep opens → **both blades through the
target line, contact** → arms fully crossed open at the far side → they gather
back in → settle.

### 6. `f2_heavy3_disarm_hook` — Disarming Hook / Launcher
He catches the opponent's guard on the **ring pommel**, hooks it, and **rips
upward** to launch them. The ring must be clearly the thing doing the work.
Beats: kunai turned pommel-forward, low → the hook reaches in and catches →
**tension, the hook bites and starts to lift — contact** → the rip drives up →
arm finishes overhead, body opened → settle.

## LOW & AERIAL

### 7. `f2_crouch_light_ankle` — Low Ankle Poke
A quick **crouching tip-stab at the opponent's feet**. He stays in a deep crouch
for all six beats. Beats: crouched, blade tucked → stab begins → **tip at ankle
height, contact** → withdraw → re-tuck → settled crouch.

### 8. `f2_crouch_heavy_sweep` — Sweeping Slice
A low **360° rotational sweep** with the kunai edge, spinning on the supporting
hand and knee. Beats: crouch coils, blade back → rotation starts, body turning →
**blade through the low arc, contact** → rotation carries past → the spin unwinds
→ settled crouch, facing right again.
*He must be facing RIGHT again by beat six even though the body rotates through.*

### 9. `f2_air_heavy_dive_pierce` — Dive-Pierce
**Airborne, all six beats — no ground contact anywhere on this page.** A steep
**45° downward lunge** driving the kunai point toward the floor. Beats: airborne
gather, knees up, blade raised → the body angles over into the 45° line → the dive
committed, arm locked, point leading → **point at the bottom of the line, contact**
→ the dive carries through, legs trailing → braced to land, still airborne.

---

# What is NOT asked for

So none of it gets drawn by mistake:

- **The nine Kage-Nui wire panels** (Cast, Release, Direct Latch, Bound State,
  Retreat Trigger, Razor Slice, Snapback Crumple, Reel-In Zip, Kunai Extension).
  The move is live and its visuals are **procedural** — the wire, the tether and
  the slice streaks are drawn by the engine. It reuses his existing cells. **No
  art is owed for it.**
- **`kunaidash1-6` (cells 98-103).** Already correct, already kunai. Reference
  them; do not redraw them.
- **Any Form 1 row.** His bare-handed taijutsu, the shuriken fan, Wire-Step and
  the flying kick are untouched and come straight back when the stance drops.
- **An idle or run for Form 2.** He reads as the same fighter in both forms; the
  kunai in hand is the tell. If that turns out not to be enough on screen, the
  useful thing is to say so — not to pre-draw a second idle.

---

# On delivery

Each page is cut, keyed at fuzz 42%, scaled against the 194 px idle body band and
appended to the sheet from cell 204 — **append-only, existing cells stay
byte-identical.** Every row ships with a 12-dimension grade table and a montage
for sign-off before anything is packed. Rows arrive one move per page; a page
with two moves on it cannot be cut.
