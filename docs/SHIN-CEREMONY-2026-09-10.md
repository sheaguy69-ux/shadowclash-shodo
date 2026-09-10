# Shin's six rows, and the three states that play them

**Sep 10 2026 · SHODO-EDITION · `shodo-edition` · SHEET_V 782 → 783 · reviewed on `localhost:9101`**

Owner review page (frames + GIFs at game cadence):
<https://claude.ai/code/artifact/10606725-9392-4f56-a7cb-fb3e6fadca7b>

Source: `~/Desktop/shin` — 34 boards, dropped by the owner.

---

## 0. What actually went in

Six boards, **48 cells appended at 393–440**, `cols` 393 → 441. Every one of the 393
pre-existing cells is byte-identical (measured, 0 diff px — not the packer's own assertion,
an independent read against a copy taken before the first pack).

| key | board | status |
|---|---|---|
| `taunt1..8` | single-shuriken-fingertip-taunt-8f-v1 | **LIVE, zero engine work** |
| `adown1..8` | flying-crescent-kick-air-offense-8f-v1 | **LIVE, zero engine work** |
| `intro1..8` | round-start-intro-8f-v1 | LIVE — new state |
| `win1..8` | palm-fist-salute-victory-8f-v1 | LIVE — new state |
| `ko1..8` | defeat-ko-8f-v1 | LIVE — new state |
| `wcling1..8` | wall-cling-jump-locomotion-8f-v1 | **PACKED, NOT WIRED** — see §4 |

Two of the six needed no engine work at all. `tauntCells` has read `taunt1..N` since 782 and
`executeTaunt` refuses a fighter without the row — Shin is now the second fighter in the game
who can taunt. `adown1..N` lands on the air-Down picker that has been art-gated since 675;
before today Shin's air Down+attack drew the borrowed neutral air row.

## 1. ⛔ THE `-review` FOLDERS ARE NOT ART — read this before touching that drop again

Half the folders in `~/Desktop/shin` end in `-review`, and the obvious reading — that those
are the keyed deliverables and the plain folders are raw — **is backwards**.

| | mode | size | transparent |
|---|---|---|---|
| plain folder | **RGBA** | 416×416 | **~80 %** |
| `-review` folder | RGB, no alpha channel at all | 268×733 | 0 % |

The `-review` PNGs are **screenshots of the transparency checkerboard** — 82 % of their pixels
are near-white and the checker is baked into the image. Packing one keys the whole rectangle
as ink. `pack_keyed_board.py` reported every beat of one at an identical 145 800 px, which is
what that failure looks like from the outside.

**The plain folders are the art.** All six rows above packed from those.

The one board with no plain folder and no alpha is
`silent-star-recall-wire-shuriken-special-8f-v1` — genuinely RGB on white, 300×486, nine files
(the ninth is a QC contact sheet, excluded by the `frame-*.png` glob). It needs the
white-composite path, not this one. It is also the `gsfwd` trap — see §4.

## 2. The rulers, and which one was obeyed

`eye_scale.py` **refuses Shin**, in its own words: *"eye ruler NOT validated — idle spread
6.5 %; disc size follows the row (`run_clean` 1.149 at area 1.178, `sneu` 1.392 at 1.357, 2/8).
Use the ink-area ruler and look."* So the eye is logged, not obeyed — the same verdict the
Executioner's eye earns on other sheets, reached here by the tool rather than by assertion.

`check_row_scale.py` does not apply: it grades a multi-row source spreadsheet for a second row
drawn small, and these boards are one row per image.

**The ruler is ink area**, anchored on each board's ready-guard beat against the packed idle's
10 207 px, one scale per board. Measured on the written cells:

| row | ink area vs idle | foot gap | resample loss |
|---|---|---|---|
| taunt | 1.01–1.50× | 2 px | 0.1–0.6 % |
| intro | 1.07–1.59× | 3 px | 0.0–0.5 % |
| win | 0.85–1.10× | 3 px | 0.0–0.3 % |
| ko | 0.60–1.17× | 3–8 px | 0.0–0.4 % |
| wcling | 0.78–1.66× | 3–107 px | 0.1–0.5 % |
| adown | 0.87–1.66× | 2–39 px | 0.1–0.7 % |

The wide gaps and areas are the rows that leave the floor and the beats carrying FX — wcling's
107 px is him up the wall, adown's 39 px is the kick airborne, and the >1.4× areas are the
shuriken halo, the scarf flourish and the crescent arc. The shared window is placed once per
board, so a beat that leaves the ground stays off it.

`gate_fragments` is clean at 441 cells except `wcling6`/`wcling7`, which it flags as floating
91–108 px above footY. That is the wall kick-off and it is correct; it is named here so the
next reader does not re-open it.

## 3. The engine — one shared path, three moments

`ceremonyFrame(p, F)`, filed beside `tauntFrame` and above the state switch. Three rows, one
mechanism, and no new STATE anywhere: the fighter is standing or down exactly as before, and
only the drawing differs. That is the taunt's design note applied again, for the same reason —
a new STATE would need a branch in every switch that already handles IDLE, and each one would
be a place for the pose to behave unlike standing.

- `intro1..N` rides `roundIntroTimer`, plays across the ROUND N beat and **holds its last cell
  through FIGHT!**, so he opens on the guard the board ends in, not a half-rise.
- `win1..N` / `ko1..N` ride a new per-player `ceremony` field, set by `beginCeremony(w)` from
  `endRound`'s own winner variable. `endRound` has three mode branches — brawl, tag, 1v1 —
  that each `return` on their own, so each one calls it.
- **A draw salutes nobody**, and the KO pose is earned by `hp <= 0`, so a time-over loser is
  still standing and keeps his stance.
- **The KO row is grounded-only.** Its last beats are a body lying on the floor; drawn while the
  loser is still falling that is a ground frame in the air, which is the defect the 707 air
  sweep exists to kill. Airborne, `airhurt` still wins.

**ART OR NOTHING**, the taunt's rule. A sheet without the row draws what it drew before, so the
other six fighters cost nothing — and **Tsubasa's `intro`/`win`/`ko`/`wcling` wake up for free.**
They were packed at 781 and filed, verbatim, as *"art waiting on an engine state, not orphan
debris — one JSON edit each the day the state exists."* The state exists now, and it took no
JSON edit: the keys were already right.

### The one that bit

The intro first went in with a grounded check, on the reasoning that a ceremony pose is a
standing pose. **`updateGame` is gated on `roundIntroTimer <= 0`** — no physics runs during the
intro, every fighter sits at spawn with `isGrounded` still false, and the row drew `xidle1` for
all 90 frames. Measured in the running game, not reasoned about.

The same guard, in its first form, had also shadowed Shin's and Tsubasa's **airborne held
poses** — `check_air_held_poses` failed 6 of 24 with `NOT AN AIR CELL #402`, which is `intro2`.
That is the whole value of a branch that sits above the state switch being gated: it sees
everything.

Both directions are now asserted in `tools/check_ceremony.mjs`: the win and KO poses must test
the ground, and the intro arm must **not** — a `isGrounded` in the intro arm fails the gate.

## 4. Owner-gated — nothing below was touched

**`wcling1..8` is packed and deliberately not wired.** Beats 2–5 have the **wall painted into
the art** (a black vertical streak behind him). That is the same defect that got a drawn
walljump cell rejected on Aug 16 — *"it contained the gray wall"* — so the cells are on the
sheet and the key is one JSON edit away the day you rule on it.

**`gsfwd` is a trap, and it is a mechanics change, so it is yours.** `web/index.html:6407` gates
Shin's forward+Special on `SPRITES.shin.frames.gsfwd1 !== undefined`. Packing that key does not
give the move art — **it changes the move**, from the wire shuriken (1 projectile, 320 ms) into
the SHURIKEN VOLLEY (3 stars, 220 ms). The board is named *silent-star-recall-**wire**-shuriken*,
i.e. it is art for the move he has, not for the volley. Decoupling that gate is one line and
provably behaviour-preserving today (the key is absent, so the branch does not fire), but it is
a mechanics edit and it is not mine to make.

**Ten boards are new art for rows that already have art**, so repointing them changes what you
see and none were packed: `straight-punch-light` (`light`), `low-sweep` (`ksweep`),
`silent-reed-elbow-standing-medium` (`medium`), `stone-splitting-palm-heavy` (`hneu`),
`empty-hand-guard-block` (`block`), `hit-medium` (`hurt`), `grab-shoulder-throw` (`grab`),
`knockdown-recovery` (`getup`), `low-shadow-dodge-dash` (`roll_`),
`shadow-thread-reversal-parry-counter` (`sparry`).

**Seven idle boards, one live idle** — `idle-8f-v1`, `-authoritative-design-v4`,
`-owner-model-v5`, `-owner-model-v6-safe-margin`, `-reference-design-v3`, and two
`-stand-to-predatory-crouch`. Pick one.

**Already on the sheet, as orphans.** A silhouette-IoU sweep of all 34 boards against all 393
cells resolves `jump-land-8f-v3` at 0.97, `run-8f-v1` at 0.94, `idle-8f-v1` at 0.91 and
`knockdown-recovery-8f-v1` at 0.90 — frame for frame, in order — and the cells they land on are
almost all **unreferenced**. Shin's sheet carried **256 orphan cells of 393** before this pass.
That is a repoint job, not an art job, and it is a separate decision from the ten above.

## 5. Verified

Driven in the running game at `localhost:9101` (`/whoami` confirms this tree, `sheet_v` 783),
through the real entry points — `resetRound()`, `player1.executeTaunt()`, `endRound()` — and
read back through `spriteFrameIndex`, the picker the renderer itself calls:

| moment | how | result |
|---|---|---|
| intro | `resetRound()`, 95 frames | **8/8 beats**, `intro1..intro8` in order, then normal art |
| win | real `endRound()`, p2 at 0 hp | **8/8 beats** on the winner |
| ko | real `endRound()`, p2 at 0 hp | **8/8 beats** on the loser |
| taunt | `executeTaunt()` → **true** (was `false`) | **8/8 beats** through `tauntFrame` |
| adown | air Down latched, attack clock walked | **8/8 beats** through the full picker |

`executeTaunt` returning `true` is itself the assertion: that method refuses any fighter whose
sheet has no taunt row, and it refused Shin yesterday.

The live taunt run showed `taunt1`/`taunt2` on screen and then stopped, because the CPU driving
P1 in this build pressed a direction — that is 782's documented *"cancels into anything on the
first real input"*, not a fault, and it is why the full row was walked through the picker
directly.

Gates: `check_ceremony.mjs` (new) · `check_taunt.mjs` — now reports **3 sheets** carry taunt art
· `check_air_held_poses.mjs` — back to **24/24** after the intro fix · `check_first_form_gate`
· `check_zero_legacy` · `gate_fragments`.

`check_shodo_roster.py` and `check_dir_moves.mjs` **crash, and not because of this work**:
`web/assets/sprites/oni.json` and `oni.png` are deleted in the working tree (`D` in
`git status`). That predates this session and is someone else's in-flight state — flagged, not
touched.

## 6. Not done

No paid generation, no push, no deploy. The `web/assets/sprites/shin.*` pair was already dirty
when this session opened — someone had taken `cols` 379 → 393, added `flying_kick1..8` and
`wallthrow1..6` and dropped `xidle5`/`xidle6`. Those 14 cells are underneath these 48 and
cannot be separated in one commit; see the commit message for how that was handled.
