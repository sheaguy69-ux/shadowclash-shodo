# What was measured, and how

Every number below came out of the live engine on `:9101` at `SHEET_V 837`, HEAD `e64e1b1`,
or out of the sheet manifests directly. Nothing here is estimated. Reproduce any of it with
the command given.

---

## 1. The walk tier lives 8 frames and shows 3 cells of 8

The `WALK` state is already built and gated purely on the `walk1` key. But it is a
**lean-out before the run**, not a persistent walk:

```js
const WALK_TIME = 0.15;   // seconds of walk before the push breaks into a run
const WALK_FRAC = 0.5;    // of that fighter's own moveSpeed
```

Measured by faking `walk1..8` onto Tsubasa in memory and driving a held push:

```
0 WALK walkT=0.130 vx=263 phase=20.40 cell A
1 WALK walkT=0.110 vx=263 phase=20.68 cell A
2 WALK walkT=0.090 vx=263 phase=20.96 cell A
3 WALK walkT=0.070 vx=263 phase=21.24 cell B
4 WALK walkT=0.050 vx=263 phase=21.52 cell B
5 WALK walkT=0.030 vx=263 phase=21.80 cell B
6 WALK walkT=0.010 vx=263 phase=22.08 cell C
7 WALK walkT=0.000 vx=263 phase=22.36 cell C
8 RUN  ...
```

- **8 frames in `STATE.WALK`**, held or tapped — identical either way.
- **3 distinct cells reached**, out of 8.
- `animPhase` advances **0.28 per frame** at walk speed.

The arithmetic, from `web/index.html`:

```
walk vx   = 350 * (curSpeed / 6) * WALK_FRAC        // Tsubasa, speed 9  -> 262.5
animPhase += dt * min(3, |vx| / 150) * cycle        // 0.02 * 1.75 * 8   -> 0.28 / frame
frames in WALK = WALK_TIME / dt                     // 0.15 / 0.02       -> 7.5
cells shown    = 7.5 * 0.28                         //                   -> ~2.1, measured 3
```

To show all eight beats, `WALK_TIME` would have to be about **0.57s** — and longer still for
the slower bodies, because their walk `vx` is lower and `animPhase` advances slower.

**Consequence for the art, and it is the single most important line in this brief:**
draw a full 8-beat loopable cycle, but put the character in **beats 1–3**. Those are the
only ones that ship until the owner rules on `WALK_TIME`. A walk whose personality lives in
beat 6 will never be seen.

---

## 2. Air-hit art does not exist. Every fighter is drawing the throw-grab pose

`airhurt1..3` is the only airborne hurt row, and on **all eight fighters** its cells are the
same cells as `grabbed3..5` — the drawings made for being *held in a throw*.

```
executioner  airhurt1=300=grabbed3  airhurt2=301=grabbed4  airhurt3=302=grabbed5
mizu         airhurt1=151=grabbed3  airhurt2=152=grabbed4  airhurt3=153=grabbed5
shin         airhurt1=295=grabbed3  airhurt2=296=grabbed4  airhurt3=297=grabbed5
tsubasa      airhurt1=363=grabbed3  airhurt2=363=grabbed3  airhurt3=294=grabbed5
ember        airhurt1=233=grabbed3  airhurt2=234=grabbed4  airhurt3=235=grabbed5
kael         airhurt1=161=grabbed3  airhurt2=161=grabbed3  airhurt3=162=grabbed4
mokurai      airhurt1=180=grabbed3  airhurt2=181=grabbed4  airhurt3=183=grabbed6
exile        airhurt1=179=grabbed3  airhurt2=180=grabbed4  airhurt3=183=grabbed7
```

See `refs/PROOF-airhurt-is-the-grab-pose.png`. Tsubasa and Kael are worse than the rest —
two of their three bands point at the *same* cell, so they have **two** drawings covering the
whole airborne arc.

Reproduce:

```bash
python3 - <<'PY'
import json, glob, os
for f in sorted(glob.glob('web/assets/sprites/*.json')):
    d = json.load(open(f)); F = d.get('frames', {})
    own = {}
    for k, v in F.items(): own.setdefault(v, []).append(k)
    for i in (1, 2, 3):
        k = f'airhurt{i}'
        if k in F: print(os.path.basename(f), k, F[k], [x for x in own[F[k]] if x.startswith('grabbed')])
PY
```

This is why a juggle reads as a flinch. It is not a flinch — it is a man being *held*,
played back while he is being launched 92 pixels into the air with nobody touching him.

---

## 3. The jump is six vy bands, and half the roster repeats cells inside them

Airborne art is picked by `jumpBand(vy)` into a six-slot map:

```js
const jumpBand = vy => vy < -380 ? 0 : vy < -240 ? 1 : vy < -60 ? 2
    : vy < 100 ? 3 : vy < 270 ? 4 : 5;
```

The six slots may point at the same cell, so the number of **distinct airborne poses** is
lower than six for most of the roster:

| fighter | `jflight` slots → distinct cells |
|---|---|
| tsubasa | 6 → **6** |
| kael | 6 → **6** |
| mizu | 6 → **5** |
| shin | 6 → **5** |
| ember | 6 → **5** |
| executioner | 6 → **4** |
| exile | 6 → **4** |
| **mokurai** | 6 → **3** |

Mokurai crosses an entire jump arc on three drawings. That is the whole of "the jumps look
static".

Reproduce: `python3 tools/check_ninja_jumps.py` (also reports four fighters whose grounded
landing assertion currently fails, and one stale hard-coded allow-list — separate issue,
logged in §6 of the README).

---

## 4. Launch heights, so the hurt row can be drawn to the real arc

Driven live after `2dbbbc6`, a grounded victim at gap 35 against each fighter's Up+Heavy:

| attacker | victim launched | victim damage |
|---|---|---|
| ember | **192 px** | 15.1 |
| mokurai | 107 px | 15.3 |
| executioner | 97 px | 18.4 |
| tsubasa | 92 px | 9.1 |
| mizu | 87 px | 8.4 |
| shin | 63 px | 4.5 |

A victim of Ember's launcher travels roughly **four body-heights** upward. The hurt row has
to survive being looked at for that entire arc.

---

## 5. Sheet geometry, per fighter

The generator does not need these — they are here so the packer's numbers are on the record
and so the brief can state that **one board is packed at one uniform scale**.

| fighter | frameW | frameH | footY | scale | cols |
|---|---|---|---|---|---|
| executioner | 644 | 496 | 488 | 0.2665 | 455 |
| mizu | 300 | 320 | 312 | 0.3782 | 256 |
| shin | 520 | 370 | 330 | 0.3451 | 447 |
| tsubasa | 301 | 332 | 312 | 0.3663 | 511 |
| ember | 340 | 390 | 369 | 0.3414 | 517 |
| kael | 300 | 320 | 312 | 0.4046 | 345 |
| mokurai | 300 | 248 | 218 | 0.4808 | 410 |
| exile | 480 | 432 | 344 | 0.4409 | 426 |

Tsubasa's `frameH` is 332 rather than 320 because `4220886` grew his cell **downward** to
hold a beat whose trailing leg hangs below his own standing foot line. `footY` did not move.
Any of these can be grown the same way if a new row needs the room — it is not a reason to
shrink a pose.
