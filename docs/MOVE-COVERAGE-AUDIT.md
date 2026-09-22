# Move coverage — the six originals, measured Aug 2 2026 (SHEET_V 342)

Every input the six can press: **2 states × 5 directions × 3 buttons = 30 each, 180 total.**
Reproduce with `python3 tools/serve.py &` then `python3 tools/audit_move_coverage.py`.

| | distinct moves |
|---|---|
| **ground** | **84 / 90** |
| **air** | **88 / 90** (38 before this pass began, 48 at 339, 65 at 340, 83 at 341) |

**No dead buttons.** All 180 inputs do something.

| fighter | ground | air |
|---|---|---|
| Executioner | 13/15 | **15/15** |
| Mizu | **15/15** | **15/15** |
| Shin | 14/15 | **15/15** |
| Tsubasa | 14/15 | 13/15 |
| Ember | 14/15 | **15/15** |
| Kael | 14/15 | **15/15** |

**Five of the six are complete in the air**; Mizu is complete everywhere.

## Every remaining shared input, and why

| | | |
|---|---|---|
| all six, ground | `Neutral+Light == Up+Light` | **by design** — Up on the ground is jump; no fighter has an anti-air Light |
| Executioner, ground | `Back+Heavy == Back+Special` | **by design** — the owner's redirect at `web/index.html` :3316; the move list says *"Back+H also works"* |
| Tsubasa, air | `Neutral+S == Back+S == Up+S` | all three are his **strict 0.133 parry** (:5002). His `sneu`/`sback`/`sup` cells are packed and draw the moment those directions stop parrying — a mechanics decision, not an art gap |

## Nothing is open

The three sheets rejected on identity were **edited into canon, not redrawn** (owner
ruling): nano-banana removed the Executioner's second sword on all 66 frames, a geometric
warp gave Kael his wakizashi on all 48 (`tools/sprites/fix_kael_wakizashi_341.py`), and
Ember's teal scarf and cyan eyes became his own green on all 54 — 43 of those paid for,
and **the last 11 done locally for free** by `tools/sprites/recolor_ember_scarf.py`, whose
transform is measured off the paid frames rather than invented.

### The one thing that could not be fixed: Ember's claw count

His shipped cells carry **three** blades per gauntlet (checked at 4x on idle, air1 and
light1). The Aug 2 move sheet is **mixed** — some hands drawn with three, some with four;
`hfwd_1` alone has four on the rear hand and three on the front. Four routes were tried
on Aug 2 and every one failed, so this is recorded rather than left as a live to-do:

| attempt | result |
|---|---|
| nano-banana, bundled prompt (scarf + eyes + claws) | did the two colour changes, ignored the count |
| nano-banana, single-purpose prompt — the exact 332 wording that fixed this before | count **unchanged** on both test frames |
| nano-banana, with his shipped idle as a second reference image | returned the **reference's standing pose**, destroying the frame |
| geometric removal, the method that gave Kael his wakizashi | cannot count reliably — adjacent blades in a fan TOUCH, so two come back as one blob (only 14 of 54 frames reported a four-blade hand against what the eye sees), and erasing a detected blade leaves its black **outline** behind as a ghost |

The lesson, which is now three-for-three: **a still editor will not change a MEASUREMENT
or a COUNT it does not consider wrong.** Kael's blade length needed geometry; a length is
measurable on one blob and a count is not, which is why the same trick does not transfer.

Getting this right needs the rows redrawn with "THREE blades per gauntlet" in the prompt,
or hand editing in an image editor. It is cosmetic and internally consistent as it stands.

## How this is measured, and the rulers that lied

The ruler is a wrapper on `spawnHitbox` plus a **diff of every scalar on the player**
before and after the press. Five earlier rulers each produced a confident wrong answer:

1. **Polling the live `hitboxes` array** misses a box that spawns and expires between two
   frames. It called Tsubasa's forward Special dead; it does 8 damage.
2. **Damage against a parked opponent** measures *positions*, not moves. It claimed
   **86 dead inputs of 180**.
3. **A hand-written list of parry flags** claimed **7 dead inputs**; every one was a real
   move. The honest count is 0.
4. **Releasing the direction before sampling** — the game rebuilds `keys` every frame, so
   a wired, working move sampled as an echo of neutral.
5. **Reading the direction at DRAW time instead of press time** — the same bug in the
   engine: Shin's vanish flips his facing mid-move, and an air Down+Heavy lands before it
   draws. `executeAttack` captures `attackDir`/`attackAir` once, at the press.

And the recurring branch-order trap, bitten FOUR times now (334, 339, 340, 341): a shared
branch catches a whole class (`id <= 5 && !isGrounded`, Kael's `kxcut`), and anything
filed after it never draws, no matter how correct its cells are.

A hitbox is one way a move can be real, not the only one. Each input gets a fresh fighter
via `startNewGame()` — sharing one lets a move's lingering lock read as a row of missing
moves.
