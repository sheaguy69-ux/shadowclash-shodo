# Approved feature set — LOCAL BUILD ONLY (`python3 tools/serve.py`, :9100)

**Owner ruling, Aug 8 2026: none of this ships to the public demo.** It lands in the
local tree only. No push, no merge, no deploy — the Vercel demo stays where it is.

Scrapped and gone: **Kawarimi Transference** (the proposed position-swap variant).

> ⚠️ **This is NOT the shipped `Kawarimi (Poof)` substitution.** That one is live and
> load-bearing — `C` / `M`, ~40 call sites in `web/index.html`
> (`kawarimiWindow`, `freeKawarimiTimer`, `executeKawarimi()`, `STATE.SUBSTITUTION`,
> the LOG decoy, grabs-beat-poofs). It is untouched. Only the *Transference* proposal
> is dropped. Confirm if you meant something else.

---

## What the engine already has (build ON these, don't rebuild)

Audited `web/index.html` (14,631 lines) before writing any rules:

| # | Approved feature | Engine status | Real gap |
|---|---|---|---|
| 1 | Polish Suite | **Hit-stop + shake SHIPPED** — `hitstopRemaining`, `hitstopEase`, `hitstopQueue` (inputs buffered through the freeze), `screenShakeAmount` | shake has no *direction*; no speed-lines; no landing cushion |
| 2 | Surface Dynamics | **`STATE.WALL_CLING` + `wallDir` + `wallJumpLock` SHIPPED.** `anchorTimer` / `releaseAnchor()` = weapon bitten into a wall | wall-*run* (horizontal), ceiling latch, stage wire traps |
| 3 | Hasuji edge alignment | none | whole feature — but it is one timing window on `spawnHitbox` |
| 4 | Kage-Kami shadow echo | partial — see `docs/PHASE4-SHADOW-DESIGN.md` | path recording + replay |
| 5 | Kiai clash / blade struggle | none | whole feature |
| 6 | Shadow-Weave Anchor | `anchorTimer` + `stars` already model an anchored line | swap + combo extension |
| 7 | Muki-Kamae offense | none | stance flag + defense suppression |
| 8 | Saya-Kamae grip switch | none | stance flag + the 7f switch lock |
| 9–11 | **Kage-Nui shadow thread** | **~70% SHIPPED** — see below | the persistent tether only |

### Kage-Nui is mostly already written

`web/index.html:2816` resolves a shared `kind: 'wire'` projectile with three flags:

- **`snare`** — drag + stagger, guard is a real answer (`stunTimer > 0` gate)
- **`reel`** — the harder yank: `880px/s`, `0.55s` stagger (vs `560` / `0.45`)
- **`reverse`** — pulls the *caster* through the mark (Mokurai)

Live users today: Shin's wire (`460px/s` yank into throw range), Mokurai's
bead snare (:4974).

**So the only genuinely new mechanic in items 9–11 is the 4-second persistent tether
and its retreat-punishment trigger.** Everything else — the fire, the travel, the
drag, the guard rule, the stagger — is the existing shared wire machinery.

---

## ⛔ Blocker before any of 9–11 can be implemented as written

**The engine has no motion-input parser.** Verified: zero hits for qcf/623/236/
input-history/direction-buffer/double-tap. Input is direct `keys[...]` polling with
directional modifiers only (`up + heavy`, `down + special`, hold-vs-tap on Poof).

`Down, Back + Special` therefore does not exist and cannot be typed today. Two ways out:

- **(a) Lazy — recommended.** Bind Kage-Nui to `Back + Special` (a modifier the engine
  already reads), matching how every other move in this file is keyed. Zero new systems.
- **(b) Build a ~30-line direction-history ring buffer** (`{dir, t}`, 250ms window) and
  gain real motion inputs for the whole roster.

Pick one before item 9 starts. I default to **(a)** unless you say otherwise.

---

## Engine rules — Kage-Nui persistent tether (the one new system)

One shared tether object; the two fighters are parameters, not two implementations.

```js
// on Player: this.tether = { target, t, owner:'shin' } | null
const TETHER_DUR   = 4.0;    // s, both fighters
const TETHER_RADIUS = 0.70;  // × arena width — the leash
```

**Attach** — on wire impact, when the firing move carries `tether: true`:
set `this.tether = { target: opponent, t: TETHER_DUR }`. Reuse the existing
`proj.snare` impact branch at :2816; do not add a second impact path.

**Tick** — in the same loop that decays `anchorTimer` / `kawarimiWindow` (:2714):
`t -= dt`; drop at `t <= 0`, on `stunTimer > 0` of the owner, or on KO.

**Retreat punishment** — fires only on a *retreat*, never on neutral movement:
- distance exceeds `TETHER_RADIUS × arenaW`, **or**
- target backdashes / air-dashes away (sign of `vx` opposes the owner) while airborne

| | Shin — snapback |
|---|---|
| startup | 10f |
| result | 12f staggered crumple in front of him |
| reuse | existing `snare` numbers (`560` / `0.45`) |
| air OK | yes |
| recoil | re-press = zip to target (mirror `proj.reverse`, which already moves the caster) |

**Guard rule is inherited, not re-decided:** a blocked tether pull does nothing, same
`stunTimer > 0` gate that already protects blockers from the reel. Do not special-case it.

**Test:** one assert — fire tether, teleport target past the radius, assert the owner's
snapback fired exactly once and that a *blocking* target is not moved.

---

## Order I'd build in

1. **Item 1 remainder** (directional shake, speed lines, landing cushion) — smallest diff,
   touches only the two globals that already exist, improves every other feature's feel.
2. **Items 9–11 tether** — 70% built, one new object.
3. **Item 8 grip switch** — self-contained stance flag + switch lock.
4. Items 3, 5, 7 — self-contained, no dependencies.
5. Items 2, 4, 6 — largest, and 4 needs the Phase-4 shadow work landed first.

Nothing above is implemented yet. Say go on a number and I'll build it.
