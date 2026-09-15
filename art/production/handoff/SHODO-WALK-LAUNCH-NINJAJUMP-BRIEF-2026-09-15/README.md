# THREE ROWS — the walk, the launched hurt, and the ninja jump

Art brief for the outside image lane (GPT / the owner's own still-generator).

Written 2026-09-15 by Claude Code against **SHODO-EDITION**, `SHEET_V 837`, HEAD `e64e1b1`,
served on `:9101`.

**Nothing in this folder was generated. No paid API was called and none is proposed.**
Every image in `refs/` was cut from the sheets already in the tree.

---

## 0. The ask

> *"Help create me a handoff to give to GPT describing the walk frames and launched hurt
> pose and also add a ninja jump to add more dynamic to the jumps."*

Three new eight-cell rows, per fighter, across eight fighters. **24 boards** if the whole
roster ships. This brief says exactly what each one is, why it is owed, what it must not do,
and what the engine will do with it the day it lands.

Read in this order:

| file | what it is |
|---|---|
| **README.md** | this — the case for each row and the order of work |
| **PROMPTS.md** | the paste-ready prompt text, per fighter, per row |
| **BOARD-SPEC.md** | the delivery contract — file shape and the eight hard rules |
| **ENGINE-CONTRACT.md** | what code has to change before each row can draw |
| **MEASUREMENTS.md** | every number in here, and the command that produced it |
| `refs/ROSTER-true-scale.png` | all eight fighters at true in-game size on one floor line |
| `refs/<fighter>-refs.png` | that fighter's idle, current jump, current air-hurt, landing |
| `refs/PROOF-airhurt-is-the-grab-pose.png` | the evidence behind row B |

---

## 1. At a glance

| row | key | cells | engine work | what it replaces |
|---|---|---|---|---|
| **A — walk** | `walk1..8` | 8 | **none** | nothing — the run, at half speed |
| **B — launched hurt** | `airhurt1..8` | 8 | **one line** | a 3-cell row that is the *throw-grab pose* |
| **C — the second jump** | `njump1..8` | 8 | 2 lines + a 5-line block | a procedural 360° rotation of the standing flight cell |

---

## 2. Why row A — the walk

The `WALK` tier is **already built and already wired**. It is gated purely on the `walk1`
key existing: pack the row, the tier turns on, nothing to change. It runs at half the
fighter's own run speed and is paced **flat** — an even cadence, because a stroll does not
slam the way a sprint does.

**But one push lasts 8 frames and shows only about three consecutive cells** — and
**`animPhase` is never reset**, so each push resumes the cycle where the last one stopped.
Driven live: push 1 showed beats 5·6·7, push 2 showed 1·2·3, push 3 showed 5·6.

> ⛔ **All eight beats are reachable, and which three you see changes every push. So every
> beat must be equally strong.** The player sees a random three-beat window of a loop — a
> cycle with two hero poses and six in-betweens will stutter whenever a push lands on the
> in-betweens.

*(An earlier draft of this brief said only beats 1–3 are ever seen and told the generator to
front-load them. That was wrong, it was caught by the verification pass, and it is corrected
in `MEASUREMENTS.md` §1.)*

A full cycle in one push needs `WALK_TIME` between **0.514s** (Shin, Exile) and **1.029s**
(Mokurai) — so one roster-wide constant cannot serve everybody.

Also from the same code: `footDust`, body lean and travel-facing are **`STATE.RUN`-only**, so
the walk row **plays forward while backpedalling**. Upright, weight-centred, no strong lean.

### What the owner has to rule on

| | `WALK_TIME` | the feel |
|---|---|---|
| leave it | `0.15` | a lean-out. Three beats ship |
| show the cycle | `~0.57` | a real walk that breaks into a run after half a second |
| make it a stance | gate on stick deflection, not a timer | a held walk, like a traditional fighter |

All three are one line. **Not my call.**

---

## 3. Why row B — the launched hurt. This is the one that matters

`airhurt1..3` is the only airborne hurt art in the game. On **all eight fighters**, its cells
are the same cells as `grabbed3..5` — the drawings made for being **held in a throw**.

```
executioner  airhurt1=300=grabbed3   mizu     airhurt1=151=grabbed3
shin         airhurt1=295=grabbed3   tsubasa  airhurt1=363=grabbed3
ember        airhurt1=233=grabbed3   kael     airhurt1=161=grabbed3
mokurai      airhurt1=180=grabbed3   exile    airhurt1=179=grabbed3
```

See `refs/PROOF-airhurt-is-the-grab-pose.png`.

Tsubasa and Kael are worse still — two of their three bands point at the **same** cell. Swept
across the entire vertical-velocity range on the live sim, Tsubasa draws **two distinct
cells** for the whole of being airborne and hit.

So when a launcher pops someone **92 to 192 pixels** into the air — roughly four body-heights
for Ember's — the victim plays back a pose drawn for a man being *held by someone who is no
longer touching him*. That is the whole reason a juggle reads as a flinch. It is not a
flinch. It is the wrong drawing.

This row is a single continuous arc across eight beats: the pop, the apex, the fall. The one
row in the game where the fighter's silhouette should look **broken rather than composed** —
at the apex there is no muscle tone, no guard, no intent. A rag, not a pose. Weapons stay in
hand but hang loose.

Engine cost: **one line**, and it degrades cleanly, so rows can land one fighter at a time
while the rest stay on three cells.

---

## 4. Why row C — the second jump

> **Owner ruling, Sep 15 2026, given while this brief was being written:**
> *"I want to come to the jump make the extra flip make that a second jump, which I want them
> to jump and roll into a ball in air."*
> *"...change that second jump into a more athletic flexible jump with a curl into a ball,
> maybe people have a different type of jump."*

That ruling made this the **cheapest** of the three rows, not the most expensive — because the
mechanic already exists and somebody already left the door open for the art.

**Every fighter already has a double jump.** `jumpsLeft = 2`, refreshed on landing and on wall
contact. Press jump again in the air and it fires.

**And the second jump already has a flip — as a procedural canvas rotation.** `FLIP_TIME = 0.45`,
commented *"visual only"*, and the renderer spins **whatever cell the vertical-velocity band
already picked** through a full 360°. There is no tuck and no curl anywhere: a standing flight
drawing is rotated end over end, which is why it reads as a cardboard cut-out turning rather
than a body tumbling.

Grepped all eight manifests for `spin|flip|somer|tuck|cart|twirl|corkscrew|vault` —
**nothing airborne and rotational is drawn anywhere on any sheet.** The only rotational rows
in the game are ground rolls, Kael's `kspin` (an attack) and Mizu's `staffspin` (a directional
move).

**The switch-off is already built, and already used.** The same procedural spin is disabled
for the ground roll on every fighter who has drawn roll art — `drawnRoll`, and all eight do,
so the air-jump flip is the **last place the procedural spin still runs**. The flip's own
exemption flag is right there beside it, wired to a constant:

```js
const oniDrawnFlip = false;
  || (false)   // Oni — cell 50 is a drawn tuck
```

Somebody built the door for this row and never got the art. This brief walks through it.

**It is also where the roster gets its variety.** "Maybe people have a different type of jump"
is the right instinct and it is the whole design of §4 in `PROMPTS.md`: Tsubasa gets the
tightest ball on the roster, Shin the fastest, Ember a feral one that snaps open claws-first,
Kael a schooled somersault that curls *around* his own blades, Mizu a pivot around her staff
because she cannot ball up over two metres of bo, Mokurai a serene seated lotus tuck, Exile a
curl the chain wraps itself around — and the **Executioner does not tuck at all**. He pikes.
The oldest, tallest, slowest man on the roster in heavy robes does not somersault, and making
him do it would be a lie about the character.

⛔ **One place this row can surprise someone.** `flipTimer` has a second caller —
`finishGrapple()` sets it for Exile's chain swing-around. With a drawn row she plays the curl
there too. Bonus or bug is **the owner's call**; the narrow fix is in `ENGINE-CONTRACT.md`.

### How it has to be produced

A rotation is exactly where independent stills fall apart — the volume drifts, the weapon
gains or loses a blade at 180°, and the packer applies **one scale to the whole board**, so a
size drift between beats ships as a fighter who changes size mid-tumble.

The owner's own instinct is the fix: **block the motion first, then style it.** A crude 3D
blockout locks the volume and the silhouette at every angle by construction; the motion pass
adds the ink; then pull eight keyframes at even **angle** intervals, not even time.
`PROMPTS.md` §5 has the four steps. Row B benefits from the same treatment for the same reason.

## 5. Order of work, and the pilot

**Pilot: Tsubasa `airhurt1..8`.** One board, one fighter.

It is the right first shot on every axis — his sheet is the most worked-on in the tree, his
air-hurt is the joint-worst on the roster (two distinct cells), he is the fighter the owner
is actively playing, and the payoff is visible **every single time anybody gets launched**.
It also proves the whole pipeline end to end — generate → key → pack → one-line engine change
→ driven live — on one row before 23 more are commissioned.

Then:

1. **`airhurt1..8` for the rest** — highest payoff per board, lowest engine cost.
2. **`walk1..8`** — zero engine work, but hold until the `WALK_TIME` ruling so the art is
   drawn to the right window.
3. **`njump1..8`** — the most per-fighter design thought, but the least engine work. Start
   with **Mokurai** (3 distinct flight poses today) and the **Executioner** (4), who have the
   most to gain, before the fighters who already have six.

---

## 6. Not in scope — logged, not fixed

`python3 tools/check_ninja_jumps.py` currently reports failures that have nothing to do with
this brief:

```
Executioner ['grounded jump does not land']
Mizu        ['grounded jump does not land']
Ember       ['unreviewed/ground art in flight map', 'grounded jump does not land']
Kael        ['grounded jump does not land']
Shin [] · Tsubasa [] · Mokurai [] · Exile []
```

Ember's is almost certainly the check's own stale hard-coded cell list — his cells were
renumbered at 806/835/836/837. The four landing assertions are worth their own look.

Also standing, unrelated: the 215 orphan cells on Tsubasa's sheet (~7.2 MB, blocked on seven
hard-coded engine cell literals), and `cfang1..4` packed and unreferenced.
