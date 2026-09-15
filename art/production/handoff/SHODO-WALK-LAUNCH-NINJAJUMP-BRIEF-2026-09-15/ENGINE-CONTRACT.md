# The engine contract — what each row needs before it can draw

Three rows, three very different amounts of engine work. This file says exactly how much,
so nobody generates art that cannot be seen.

**All engine work listed here is mine (Claude), not the generator's.** It is written down so
the owner can see the cost before art is commissioned, and so the art is drawn to what the
engine will actually do with it.

---

## `walk1..8` — ZERO engine work

The tier is already built and already reads the row:

```js
// handleMovement — the state is gated purely on the key existing
const wf = SPRITES[this.spec.name.toLowerCase()]?.frames;
const walking = this.isGrounded && this.walkT > 0 && wf?.walk1 !== undefined;
...
if (this.isGrounded) this.state = walking ? STATE.WALK : STATE.RUN;
```

```js
// the picker — reads the row length, falls back to the run row, paces FLAT
case STATE.WALK: {
    if (!p.isGrounded) return neutralFrame(p, F, F.idle);
    const w = [];
    for (let i = 1; F['walk' + i] !== undefined; i++) w.push(F['walk' + i]);
    if (!w.length) { /* falls back to the run */ }
    // A walk is an even cadence, not a run's contact-hold: a sprint SLAMS, strolling does not.
    return w[Math.floor(p.animPhase) % w.length];
}
```

Pack the eight cells, the tier is live. Nothing to change.

**The one open question is `WALK_TIME`, and it is the owner's ruling, not a bug.**
At `0.15` the walk lasts 8 frames and shows 3 of 8 cells (measured — `MEASUREMENTS.md` §1).
Three options, all one line:

| | `WALK_TIME` | what the player gets |
|---|---|---|
| leave it | `0.15` | a lean-out. Beats 1–3 ship, 4–8 are insurance |
| show the cycle | `~0.57` | a real walk that breaks into a run after half a second |
| make it a stance | gate on stick deflection instead of a timer | a held walk, like a traditional fighter |

Until he rules: **the art must front-load its character into beats 1–3.**

---

## `airhurt4..8` — ONE LINE

The row exists but the band is hard-capped at three. Proven by sweeping the entire vertical
velocity range on the live sim with five fake cells appended:

```
swept vy -800 .. +800, STATE.STUNNED, airborne
distinct cells drawn : 2
airhurt4..8          : NEVER DREW
```

Because of this:

```js
// the airborne hurt picker — a hard-coded three-way split
if (!p.isGrounded && !p.grabbedBy && F.airhurt1 !== undefined
    && (p.state === STATE.STUNNED || p.state === STATE.THROWN)) {
    const beat = p.vy < -80 ? 1 : p.vy > 100 ? 3 : 2;
    return F['airhurt' + beat] ?? F.airhurt1;
}
```

The change, once the art lands — band across the row instead of across a literal 3, using
`rowCells`, which is the same function the idle row already uses:

```js
if (!p.isGrounded && !p.grabbedBy && F.airhurt1 !== undefined
    && (p.state === STATE.STUNNED || p.state === STATE.THROWN)) {
    const ah = rowCells(F, 'airhurt');
    // vy runs about -430 (a hard launch) to +700 (terminal). Map that span onto the row so
    // beat 1 is the pop and the last beat is the hard fall; a 3-cell sheet is unchanged.
    const u = Math.min(0.999, Math.max(0, (p.vy + 430) / 1130));
    return ah[Math.floor(u * ah.length)] ?? F.airhurt1;
}
```

⛔ **This must stay backward-compatible.** Four fighters may still be on three cells while
the others have eight; the expression above degrades to the current behaviour on a 3-cell
row, so rows can land one fighter at a time.

⛔ **`grabbed3..5` must stop being the same cells.** Today `airhurt1..3` *are* `grabbed3..5`
on all eight fighters. Once a real `airhurt` row is packed, the `grabbed` keys keep pointing
at the old cells — the throw art is still correct for a throw — and the old cells become
shared, not orphaned. Nothing is deleted.

---

## `njump1..8` — THE SECOND JUMP. Two lines of gate, one band

**Owner ruling, Sep 15 2026, mid-brief:**
> *"I want to come to the jump make the extra flip make that a second jump, which I want
> them to jump and roll into a ball in air."*
> *"...change that second jump into a more athletic flexible jump with a curl into a ball,
> maybe people have a different type of jump."*

This turned out to be the cheapest of the three rows, because **the mechanic already exists
and the engine was built expecting exactly this art.**

### What is already there

- **Every fighter already has a double jump.** `this.jumpsLeft = 2` (`:3188`), refreshed on
  landing (`:4985`) and on wall contact (`:5128`, `:9733`), gated at `:5993`, decremented at
  `:6018`. Nothing to add.
- **The second jump already has a flip** — and it is a **procedural canvas rotation**, not a
  drawing:

```js
if (!fromGround) this.flipTimer = FLIP_TIME;   // air jump = backflip flair   :6016
const FLIP_TIME = 0.45;                        // "visual only"               :2991
...
const spinFlip = p.flipTimer > 0 && !oniDrawnFlip && !spinRoll;              // :14414
const th = prog * Math.PI * 2 * -1;   // a full 360, backwards
ctx.rotate(th);                                                              // :14438
```

The engine spins **whatever cell `jumpBand` already picked** through a full circle. There is
no tuck, no curl, no change of pose — a standing flight drawing is rotated end over end.

- **Nothing airborne and rotational is drawn anywhere on any sheet.** Grepped all eight
  manifests for `spin|flip|somer|tuck|cart|twirl|corkscrew|vault`: the only rotational rows
  are ground rolls (`roll_1..6/8`, `mroll`, `slide`), Kael's `kspin` (a special attack), and
  Mizu's `staffspin` (a directional move). The 0.45s procedural spin is the **only** air
  rotation in the game.

### And the switch-off already has a precedent — and a placeholder

The procedural **roll** spin is already disabled for every fighter who has drawn roll art:

```js
const drawnRoll = (p.spec.id === 7 && MF.slide1 !== undefined)
               || (p.spec.id === 6 && MF.mroll1 !== undefined)
               || MF.roll_1 !== undefined || ...;                            // :14406-14412
const spinRoll = p.rollTimer > 0 && !drawnRoll;
```

All eight fighters have a drawn roll, so **the procedural spin is already off for rolls
everywhere. The air-jump flip is the last place it still runs.**

And the flip's own exemption flag exists — wired to a constant:

```js
const oniDrawnFlip = false;                                                  // :14405
  || (false)   // Oni — cell 50 is a drawn tuck                              // :14409
```

Somebody built the door for this row and never got the art. This is walking through it.

### The change

**1 — switch off the procedural spin for a fighter who has the drawing** (`:14405`, `:14414`),
exactly as `drawnRoll` does:

```js
const drawnFlip = MF.njump1 !== undefined;
...
const spinFlip = p.flipTimer > 0 && !drawnFlip && !spinRoll;
```

**2 — draw the row on the flip's own clock**, above the `jflight` band in `case STATE.JUMP`
(`:12581`):

```js
// THE SECOND JUMP IS A ROTATION, so it rides its own 0.45s clock, not the vy bands.
// vy would be wrong here: a curl is a fixed-length tumble, and banding it on velocity
// would stall mid-rotation at the apex and snap through it on the way down.
const nj = rowCells(F, 'njump');
if (nj.length && p.flipTimer > 0) {
    const prog = 1 - p.flipTimer / FLIP_TIME;              // 0 -> 1 across the tumble
    return nj[Math.min(nj.length - 1, Math.floor(prog * nj.length))];
}
```

That is it. Two lines and a five-line block, and a fighter without the row is bit-for-bit
unchanged.

⛔ **Band on `flipTimer`, never on `vy`.** The first jump is a ballistic arc and vy is the
honest clock for it. The second jump is a **fixed-length tumble** — 0.45s regardless of where
the arc has got to — and banding a rotation on velocity would hold one beat through the apex
and skip three on the way down. This is why `njump` is a separate key from `jflight` rather
than more slots on it.

⛔ **`flipTimer` has a second caller.** `finishGrapple()` sets it at `:9296` ("the swing-around
spin") for Exile's chain arrival. With a drawn `njump` row she would play the curl on that
swing-around too. Either that reads as a bonus or it does not — **it is an owner call, and it
is the one place this row can surprise someone.** The narrow fix if he dislikes it is to gate
the draw on `p.jumpsLeft === 0` as well, which is true on an air jump and false on the grapple.

### "Maybe people have a different type of jump"

Supported, and half-built already: `p.jumpDir` is captured at takeoff (`'fwd'` / `'back'` /
`null`, `:6007-6008`) — and has **zero readers in this tree**. Five assignments, no consumers.
A forward curl and a backward curl could be separate rows off the key that is already being
set, with no new state at all. **Not proposed for round one** — one curl per fighter first.

### Also found, not fixed

- `hitSquashT` is set at `:10562` ("impact squash: 0.8y / 1.25x") and ticked at `:4154`, and
  is **read nowhere**. The documented impact squash does not happen.
- Coming out of a launch there is **one frame of a grounded idle cell drawn in mid-air**: on
  the tick `stunTimer` hits 0, `:4499` sets `STATE.IDLE` and returns before `handleMovement`,
  and the switch's `default:` (`:13930`) has no `isGrounded` guard — unlike `case STATE.WALK`,
  which does. The 707 defect, one frame wide, still open.
- The `walljump` comment at `:12341-12345` says the cell "is out of the manifest" — **7 of 8
  sheets carry it**. Stale comment describing a state that no longer exists.
- `tools/check_air_hurt.py` and `tools/check_ninja_jumps.py` both still assume a **9-fighter**
  roster and name `oni`; this tree has 8 and no `oni.json`.
