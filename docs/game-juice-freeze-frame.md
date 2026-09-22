# Freeze Frame / Hitstop — Quality Implementation (Game Juice)

**Source:** [Quality Freeze Frame in Godot 4.4 | Game Juice](https://youtu.be/Jwv9t5zFlqI) —
Mostly Mad Productions, April 2025 (project files on the creator's
[Patreon](https://www.patreon.com/mostlymadproductions)).
Cross-referenced with the [Godot forum hitstop thread](https://forum.godotengine.org/t/how-should-i-implement-hitstop/45146),
the [Godot 4.4 physics interpolation docs](https://docs.godotengine.org/en/4.4/tutorials/physics/interpolation/physics_interpolation_introduction.html),
and the game-feel canon (Jan Willem Nijman's *The Art of Screenshake*, Martin Jonasson &
Petri Purho's *Juice It or Lose It*).

---

## 1. What it is and why it works

**Freeze frame** (a.k.a. **hitstop** / **hit pause**) is a tiny, deliberate pause — usually
30–150 ms — injected at the exact moment of an impact: a sword connecting, an enemy dying, a
heavy landing. Fighting games (Street Fighter, Smash Bros.) have used it since the arcade era.

Why it works, perceptually:

- **It gives weight.** The brain reads the interruption of motion as resistance — the hit
  "connected with something solid."
- **It creates a beat.** Like a comic panel border or a drum hit, the pause punctuates the
  action so the player's eye can register *what just happened* before motion resumes.
- **It buys read time for other juice.** Screen shake, flash, and particles land harder when
  the first few milliseconds of them are shown at a standstill.

The comic-book parallel is worth noting for Wildcomiks: hitstop is literally a **freeze frame
panel** — the game momentarily becomes a comic. Leaning into that (halftone flash, "POW!"
lettering during the freeze) would be strongly on-brand.

### Naive vs. quality

| | Naive | Quality |
| --- | --- | --- |
| Mechanism | `Engine.time_scale = 0` + `await` a normal timer | Near-zero or eased time scale, timer that **ignores** time scale |
| Overlap | Second hit mid-freeze restores time early or double-freezes | Priority/refresh policy: longest or strongest freeze wins |
| Exit | Snaps back to full speed | Optional ramp back (freeze → slow-mo → full speed) |
| Audio | Music stutters/pitches | Music keeps playing; only SFX belong to game time |
| UI | Menus and pause screen freeze too | UI runs on unscaled time |
| Scope | Global always | Global for big beats, per-entity for small ones |

The single most common bug: pausing with a timer that is itself affected by the pause. With
`Engine.time_scale = 0`, a normal `SceneTreeTimer` **never fires** and the game hangs frozen.

---

## 2. Godot 4.4 implementation

### 2.1 The core trick

`Engine.time_scale` multiplies delta for `_process`, `_physics_process`, timers, and tweens —
everything. So the timer that ends the freeze must opt out via `create_timer`'s fourth
argument, `ignore_time_scale`:

```gdscript
# SceneTree.create_timer(time_sec, process_always, process_in_physics, ignore_time_scale)
await get_tree().create_timer(duration, true, false, true).timeout
```

### 2.2 A production-quality autoload

Register as an autoload named `Juice` (Project Settings → Globals). One call site for every
impact in the game keeps tuning centralized.

```gdscript
# juice.gd — autoload singleton
extends Node

## Freeze frame / hitstop manager.
## Usage:  Juice.freeze(0.08)                    - hard stop for 80 ms
##         Juice.freeze(0.15, 0.05)              - 150 ms at 5% speed (dramatic slow-mo)
##         Juice.freeze_frames(4)                - frame-count variant (fighting-game style)

signal freeze_started
signal freeze_ended

const RECOVERY_TIME := 0.10   # ramp back to full speed instead of snapping

var _freeze_end_at := 0.0     # unscaled time when current freeze expires
var _active := false

func freeze(duration: float, scale: float = 0.05) -> void:
    # Overlap policy: a new freeze only extends, never shortens. A weak jab
    # landing during a heavy finisher's freeze must not cut it off early.
    var now := Time.get_ticks_msec() / 1000.0
    _freeze_end_at = maxf(_freeze_end_at, now + duration)
    if _active:
        return
    _active = true
    freeze_started.emit()

    # Never a literal 0: at 0 the world is dead. 0.02-0.10 keeps particles
    # and shake crawling almost imperceptibly - reads as frozen, feels alive.
    Engine.time_scale = clampf(scale, 0.01, 1.0)

    # ignore_time_scale=true (4th arg) or this timer never fires.
    while Time.get_ticks_msec() / 1000.0 < _freeze_end_at:
        var remaining := _freeze_end_at - Time.get_ticks_msec() / 1000.0
        await get_tree().create_timer(remaining, true, false, true).timeout

    # Ease back to full speed - the "quality" part. A snap from 5% to 100%
    # reads as a glitch; a 100 ms ramp reads as the world exhaling.
    var t := create_tween()
    t.tween_property(Engine, "time_scale", 1.0, RECOVERY_TIME) \
        .set_ease(Tween.EASE_OUT).set_trans(Tween.TRANS_QUAD)
    t.set_ignore_time_scale(true)   # the tween itself must not be slowed
    await t.finished

    Engine.time_scale = 1.0
    _active = false
    freeze_ended.emit()

func freeze_frames(frames: int, scale: float = 0.05) -> void:
    # Fighting games tune hitstop in frames, not seconds. At 60 fps:
    # light hit 2-4, medium 5-8, heavy/kill 10-20.
    freeze(frames / 60.0, scale)
```

Call sites:

```gdscript
# In the attack's hit confirmation:
func _on_hitbox_body_entered(body: Node) -> void:
    body.take_damage(damage)
    Juice.freeze_frames(3)              # light hit

func _on_enemy_died() -> void:
    Juice.freeze(0.12, 0.03)            # death: longer, deeper
```

### 2.3 What must ignore the freeze

Anything that should live in *real* time, not *game* time:

- **UI / pause menu** — set `process_mode = PROCESS_MODE_ALWAYS` on the UI layer; note
  `Engine.time_scale` still scales its delta, so drive UI animation from
  `Time.get_ticks_msec()` or unscaled tweens (`set_ignore_time_scale(true)`).
- **Music** — `AudioStreamPlayer` is unaffected by `time_scale` (audio runs on its own
  clock), so music keeps playing naturally. Punch *SFX* should fire **before** the freeze so
  the crack lands on the frozen frame.
- **Camera shake** — start it during the freeze at unscaled time; the shake buzzing over a
  frozen world is the classic one-two punch.

### 2.4 Godot 4.4-specific gotchas

- **Physics interpolation** (promoted in 4.4) interpolates between physics ticks at render
  rate. During a freeze, physics ticks nearly stop while rendering continues — interpolated
  nodes may visibly *creep* toward their next tick position. Usually this is invisible at
  `time_scale = 0.05`; if a node creeps, call `reset_physics_interpolation()` on it when the
  freeze starts.
- **Tweens and timers all scale.** Any tween running during the freeze (e.g. a projectile's
  arc) slows with the world — that's desirable. Tweens that must not (UI, the recovery ramp)
  use `set_ignore_time_scale(true)` (available since 4.2).
- **`await` re-entrancy.** The autoload's while-loop + `_active` flag handles overlapping
  calls without stacking coroutines that each try to restore `time_scale` — the naive
  "await then reset" version has a race where an early freeze's reset kills a later one.

### 2.5 Scoped (per-entity) freeze

Global freezes are for big beats. For small hits in a busy scene, freeze only the two actors:

```gdscript
func micro_freeze(node: Node, duration: float) -> void:
    node.process_mode = Node.PROCESS_MODE_DISABLED
    await get_tree().create_timer(duration, true, false, true).timeout
    node.process_mode = Node.PROCESS_MODE_INHERIT
```

Pair with a one-frame white flash on the sprite (`modulate = Color(10, 10, 10)` with HDR, or
a flash shader) for the full effect.

---

## 3. Web / TypeScript equivalent

If the game ships inside the Wildcomiks app (canvas/WebGL in Next.js), there is no engine
`time_scale` — you own the game loop, so you scale delta yourself. Same design: real-clock
expiry, extend-only overlap, eased recovery.

```ts
// timeScale.ts — the game loop multiplies dt by TimeScale.value
class TimeScaleManager {
  value = 1;                      // multiply your dt by this
  private freezeEndAt = 0;        // real-clock ms
  private recoverFrom = 0;

  freeze(durationMs: number, scale = 0.05) {
    this.freezeEndAt = Math.max(this.freezeEndAt, performance.now() + durationMs);
    this.value = Math.min(this.value, Math.max(scale, 0.01));
  }

  /** Call once per rAF tick with the real timestamp. */
  update(nowMs: number, recoveryMs = 100) {
    if (this.value === 1) return;
    if (nowMs < this.freezeEndAt) { this.recoverFrom = 0; return; }
    if (!this.recoverFrom) this.recoverFrom = nowMs;
    const t = Math.min((nowMs - this.recoverFrom) / recoveryMs, 1);
    this.value = this.value + (1 - this.value) * (1 - (1 - t) * (1 - t)); // ease-out quad
    if (t >= 1) { this.value = 1; this.freezeEndAt = 0; this.recoverFrom = 0; }
  }
}

export const timeScale = new TimeScaleManager();

// game loop
let last = performance.now();
function tick(now: number) {
  timeScale.update(now);
  const dt = ((now - last) / 1000) * timeScale.value;  // scaled game delta
  last = now;
  updateGame(dt);        // all gameplay uses scaled dt
  updateUI(now);         // UI uses the real clock
  render();
  requestAnimationFrame(tick);
}
requestAnimationFrame(tick);

// on hit:
timeScale.freeze(80);          // light
timeScale.freeze(150, 0.03);   // kill shot
```

Browser-specific notes: clamp raw `dt` (tab-switch produces giant deltas that `freeze` can't
mask), and keep audio on the Web Audio clock (`AudioContext.currentTime`), which is unaffected
by your loop — same split as Godot.

---

## 4. Tuning cheat sheet

| Event | Duration | Scale | Extras |
| --- | --- | --- | --- |
| Light hit | 2–4 frames (~35–70 ms) | 0.05–0.1 | small shake |
| Medium hit | 5–8 frames (~85–130 ms) | 0.05 | shake + sprite flash |
| Heavy / kill | 10–20 frames (~170–330 ms) | 0.02–0.05 | shake + flash + zoom punch |
| Parry / perfect dodge | 150–300 ms | 0.05 → slow-mo 0.3 exit | desaturate or vignette |
| Player death | 300–500 ms | 0.02 | hold, then slow ramp |

Rules of thumb from the game-feel canon:

- **Less is more.** If the player can *name* the effect, it's too long. Hitstop should be
  felt, not seen.
- **Never freeze on whiffs.** Hitstop is a reward for connecting; freezing on misses makes
  controls feel laggy.
- **Scale with significance.** Identical freezes on every hit flatten the hierarchy — the
  finisher must freeze longer than the jab.
- **Stack the juice on one beat.** Freeze + shake + flash + sound on the *same* frame reads
  as one powerful event; spread across frames it reads as three weak ones.

---

## 5. Follow-ups for the prep series

Natural next topics in the same series, each pairing with this doc's `Juice` autoload:
screen shake (trauma-based, Squirrel Eiserloh's noise method), sprite flash shaders,
camera zoom punch, squash & stretch, and particle-on-impact. The autoload above is designed
to grow into the one-call game-feel API: `Juice.impact({freeze, shake, flash, zoom})`.
