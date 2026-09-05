# ShadowClash — move inputs, hitboxes, effects, and THE FRAME LAW

**Read this before you touch a single cell, a single row, or a single hitbox.**

| | |
|---|---|
| Tree | `/Users/anthonyguy/SHADOWCLASH.1.0*2/SHODO-EDITION` (served on **:9101**) |
| SHEET_V | measured at **709**, re-measured at **711**, ported and re-measured at **714** |
| HEAD | `3317a1b art(714): the twelve directional rows were never missing` |
| Written | 2026-09-05 |
| Engine | one file — `web/index.html`, 20,284 lines |
| Sheets | `web/assets/sprites/<fighter>.png` + `<fighter>.json` |

**Nothing below is quoted from a design doc.** Every move table in §5 was produced at SHEET_V 714 by
pressing the input on a real `Player` object in a real headless match and reading back
what actually drew and what hitbox actually spawned:

```bash
PORT=9101 node tools/moveset_probe.mjs > moveset709.json
```

That is the ruler. This codebase has repeatedly had **art and action disagree** — a
staff rush that drew while a mist vanish ran; two fighters whose Heavy drew their IDLE
(fixed at 709). A move list assembled from key names would have reported every one of
those as fine. If you change routing, re-run the probe and diff it. Do not trust the
prose — including this prose — over the probe.

### If you read nothing else

1. There are **four** attack strengths, not three — Light `F`/`I`, **Medium `J`/`U`**,
   Heavy `G`/`O`, Special `H`/`P`. Medium is on every sheet and every pad.
2. Direction is captured **at the press**, priority **down > up > fwd/back**, and
   `fwd`/`back` are relative to `facing`, not the screen.
3. A hitbox tuple is `[w, h, dmg, delay, push, {opts}]` — the 4th slot is **delay**.
   Its flags decide the damage, the knockdown, **and which impact FX plays**.
4. **Never cut a frame, and never cut the VFX that comes with it.** §6 names the eight
   places in this pipeline that eat art. Grow the cell; never shrink the fighter.
   Erase negative space only. `art-loss = 0` + halo-ring, measured, or the frame is
   not used.
5. Verify against the tree that is actually served — `curl 127.0.0.1:9101/whoami` —
   and re-run the probe after any routing change.

### Contents

| § | |
|---|---|
| 1 | The input surface — keys, pad, touch, the direction law |
| 2 | What happens between the press and the move |
| 3 | The hitbox contract — every flag, every global modifier, the Medium tier |
| 4 | `DIR_MOVES` / `DIR_SPECIALS` — verbatim numbers |
| 5 | **The nine fighters** — packed rows + measured 30-input tables |
| 6 | **THE FRAME LAW** — do not cut frames, do not cut VFX |
| 7 | What the probe flagged, and where each one landed |
| 8 | Reproduce everything here |


---

## 1. The input surface

Four attack strengths, not three. This is the single most common thing to get wrong.

| action | P1 key | P2 key | pad (standard mapping) | touch |
|---|---|---|---|---|
| **Light** | `F` | `I` | face **0 / South** | `btn-t-p*-light` |
| **Medium** | `J` | `U` | face **2 / West** | `btn-t-p*-medium` |
| **Heavy** | `G` | `O` | face **3 / North** | `btn-t-p*-heavy` |
| **Special** | `H` | `P` | face **1 / East** | `btn-t-p*-special` |
| Block / Kawarimi | `C` | `M` | both shoulders | `btn-t-p*-poof` |
| Stance (Mode 2) | `V` | `K` | `stance` | — |
| Move | `WASD` | arrows | d-pad + left stick | on-screen pad |

- Mouse: LMB → Light (`KeyF`), RMB → Heavy (`KeyG`), wheel → Special (`KeyH`).
- **Throw** = Light + Heavy inside **90 ms** → `executeThrow()`.
- **Bunshin** = Block held + Special.
- **Reprisal / shadow slip** are checked on Heavy *before* the attack fires.
- Pad buttons are addressed by **index, not label** — Nintendo prints A/B and X/Y
  mirrored, so the legend must say South/West/North/East or it lies on half the pads.
- The pad path *synthesizes the keyboard's own keydown/keyup*. There is no second
  input implementation, and no `isTrusted` check anywhere. Fix input once, in the
  keyboard handler, and the pad and touch inherit it.

### The direction law

```js
function heldDir(p) {
    if (p.isDownPressed()) return 'down';
    if (p.isUpPressed())   return 'up';
    const ax = p.getInputAxis();
    return ax === p.facing ? 'fwd' : ax === -p.facing ? 'back' : null;
}
```

Priority is **down > up > fwd/back**, and neutral returns `null` so a table lookup can
never fire on an undirected press. The direction is **captured at the press** into
`this.attackDir` — a draw branch that calls `heldDir()` again reads the stick as it is
NOW, which is a different answer, and that has been a bug here before.

`fwd`/`back` are relative to **`facing`**, not to the screen. A move that is
world-oriented (wall, ledge, chain anchor) must not mirror by `facing`.

**So the real input space per fighter is 2 grounds/airs × 5 directions × 4 buttons = 40
inputs, plus stance variants.** The probe covers 30 of them (Light/Heavy/Special);
Medium is deliberately uniform and is documented in §3.

---

## 2. What happens between the press and the move

`executeAttack(type, dir)` — `web/index.html:5060`. In order:

1. **Hard refusals:** blade lock, `sayaLock`, an in-progress roll or its recovery tail.
2. **Tag mode** locks a player to one button for the round.
3. `pressDir = dir ?? heldDir(this)`, then `this.attackDir = pressDir`,
   `this.attackAir = !this.isGrounded`.
4. **Buffer:** if in recovery > 0.05 s and nothing has connected, the press is stored
   as `bufferedAttack` with a **0.133 s TTL** and returns. It replays automatically.
5. **Cancel windows** (`chainComboTier`, `inWin` = connected within **0.166 s**):
   - Heavy/Medium cancel out of tier 1 only.
   - Special cancels out of tier < 3.
   - Light chains into Light only while grounded, inside `stringT`, and only while
     `stringStep + 1 < lightBeats(this).length`.
6. **Stance kits** are caught here, *ahead of the type dispatch* (Mizu hanbō, Shin
   Kage-Nui, Tsubasa sakate, Executioner chūdan) — one place owns a whole kit instead
   of threading nine special cases through two else-if chains.
7. **Command overrides:** dash attacks, Exile's iai window, Oni's `HHHLHHLL` dial,
   Oni's Down+Special smoke (twice a round), wall-throw, anchor release.
8. **Table dispatch:** `DIR_MOVES[spec.id + ':' + heldDir()]` / `DIR_SPECIALS[...]`.
9. Everything else falls to the generic tier.

A move that "doesn't come out" is almost always **branch order**, not a missing row.

---

## 3. The hitbox contract

```js
spawnHitbox(w, h, dmg, dur, push, opts = {})   // web/index.html:7104
```

In the `DIR_MOVES` tables the same five numbers appear as a tuple:
`[w, h, dmg, delay, push, {opts}]` — note **the 4th slot there is `delay`, not `dur`**.

### Every `opts` flag, and what it actually does to the box

| flag | effect |
|---|---|
| `delay` | seconds before the box goes live — the **strike frame gate**. Damage starts when the blade visibly swings, not at t=0 of the windup cell. |
| `tier` | `ATTACK_LIGHT/MEDIUM/HEAVY/SPECIAL` or `'KICK'`. Drives stagger accounting (`KICK` builds only 5) and `hasuji`. Also **suppresses the pogo hijack**. |
| `low` | box drops to `height - h - 2` — sweeps skim the floor. |
| `up` | box centres above the head (`oy = -sh`) — anti-air poke. |
| `down` | box rides **under the feet**, caller's width centred — the meteor plunge. |
| `behind` | box flips to the back arc — heel turns, and both-sides landing slams. |
| `gap: n` | box **starts n px away from the body** — a chain at full extension has a dead zone under it, and that dead zone is the counterplay. |
| `trip` | knocks the victim off their feet. |
| `launch` + `launchVy` | pops the victim up at that vy (negative is up). |
| `spike` | drives an **airborne** victim DOWN. Never put `spike` on a rising arc. |
| `wallsplat` | victim sticks to the wall. |
| `unblockable` | goes through guard. |
| `mat` | `'steel'` / `'chain'` / `'flesh'` for **this box**, overriding the fighter's weapon. |
| `canClash` | explicit override; otherwise a box clashes when its material isn't flesh and the tier isn't `KICK`. |
| `echo` | a shadow replay — **never recorded to the tape**, or it compounds back to full damage. |
| `projectile` handling | separate systems (`proj`, `smokeFields`); the probe counts them separately. |

Two more things the box does on its own:

- **Corner reach-back.** A plain front box reaches **8 px back into the attacker's own
  span**, because a cornered victim gets clamped *inside* the attacker and strict AABB
  fails at identical x. Variant boxes (`behind`/`down`/`up`/`gap`) keep their authored
  geometry — the gap dead zone especially IS the design.
- **Pogo hijack.** Airborne + Down held, with no `behind`/`low`/`launch`/`tier`, turns
  any box into a straight-down stomp under the feet. Command moves carry `tier`
  precisely so they cannot be grabbed by it.

### Global modifiers — these rewrite frame data for everyone

They live inside `spawnHitbox`, once, not at the 24 call sites that author a box,
because reach/damage/startup are properties of **how the weapon is held**:

| stance / resource | who | effect |
|---|---|---|
| **Chūdan** | Executioner | Heavy & Special only: `w ×1.18`, `dmg ×1.28`. Lights untouched — the stance is for landing a big one, not mashing. He gives up his guard for it. |
| **Muki-kamae** | roster (V+Up) | `dmg ×1.25`, **unblockable**, `delay ×MUKI_STARTUP`. |
| **Saya-kamae** (gyaku-te) | roster (V+Down) | `w ×0.82`, faster startup. A reverse blade is shorter and quicker. |
| **Kage-Nui** | Shin | `dmg ×2.0` on every box he throws. The wire's own latch/slice damage is dealt *outside* `spawnHitbox` and is **not** doubled. |
| **Karma** | Mokurai | next Heavy/Special adds all stored karma, spends it whole, gold spark tell. |
| **Enlightened** | Mokurai | Specials bloom `w ×1.3, h ×1.3`. |
| **Dread ≥ 3** | Executioner | next Special: `w ×1.4, h ×1.2, dmg ×1.5`, 0.5 s armor, dread reset. |
| **The Crack** | Mokurai | every box lands `CRACK_FEINT` late and a feint tell fires where the hit *would* have been. One line covers the whole kit — nothing is exempt. |
| **Story toll** | P1, story mode | `dmg ×storyToll.dmgMul`. |

Recorded to the kage tape **raw, at the very top**, before any of this — the echo's
respawn runs the same function, so recording a modified box applies every multiplier twice.

### The Medium tier (added Sep 1 2026)

One self-contained block, `web/index.html:6237`, ahead of the type dispatch:

```js
attackAnim.dur = 560;  recoveryTimer = 0.34 / speedScale;  vx = facing * 40 (grounded)
spawnHitbox(76, 44, 13 * pow, 0.12, 130, { delay: 0.16, tier: ATTACK_MEDIUM })
```

- Draws `medium1..N` on every sheet that packs the row (**all nine do**).
- Numbers sit between the generic Light (`8*pow`, ~400 ms, 0.06 delay) and Heavy
  (`18*pow`, ~730 ms, 0.14+).
- **No chain, no cancel, no direction variants yet.** All five directions play the same
  Medium. If you add directional Mediums, they go in a `DIR_MEDIUMS` table next to the
  other two, not as else-ifs.

Because it has no direction variants, the probe skips it, which is why `medium` shows
as "not reached" for all nine fighters in §6. **That is a probe blind spot, not a dead
row.** `medium1..8` is live on every fighter.

---

## 4. The two directional tables — verbatim numbers

`DIR_MOVES` (`web/index.html:2015`) is the Heavy-tier directional table.
`DIR_SPECIALS` (`:2129`) is the Special-tier one. Entry shape:

```
'<spec.id>:<dir>': { art, dur, rec, vx, vy, vyAir, air, box: [[w,h,dmg,delay,push,{opts}]], track }
```

`track` is **only read when `track.length === cellCount`**; otherwise it is discarded in
silence and the move falls to linear exposure. Three of Oni's four entries had their
tracks deleted at 709 for exactly this reason — the art grew to 20/10/8 cells and the
6-stop tracks had been dead weight their whole life. **If you grow a row, re-author its
track at full length or delete it.** A track that silently does nothing reads as
authored emphasis that no frame ever obeys.

| input | art row | dur | box `[w,h,dmg,delay,push]` | flags |
|---|---|---|---|---|
| Mizu fwd | `bothrust` | 380 | `165,26,12,0.11,150` | — |
| Mizu down | `bolow` | 360 | `140,20,10,0.12,120` | `low, trip` |
| Mizu up | `ristaff` | 380 | `44,130,12,0.12,110` | `up, launch -380` |
| Mizu back | `staffspin` | 400 | `110,46,11,0.14,190` | vx −130 |
| Shin fwd | `ghfwd` | 420 | 3 boxes: elbow `46,44,5,0.08,50` · knee `44,40,5,0.16,60` · palm `52,46,7,0.26,150` | vx 140 |
| Shin down | `ghdown` | 340 | `76,20,9,0.10,90` | `low, trip` |
| Shin up | `ghup` | 380 | `40,96,11,0.11,100` | `up, launch -360`, vy −300 |
| Shin back | `ghback` | 400 | `120,24,8,0.16,110` | vx −220. **No `mat:'steel'`** — ura-shutō is a bare knife-hand. |
| Tsubasa fwd | `rgrush` | 380 | `54,40,7,0.08,50` + `54,40,7,0.18,140` | vx 180 |
| Tsubasa down | `lowtanto` | 340 | `70,20,10,0.10,90` | `low, trip` |
| Tsubasa up | `ristwin` | 380 | `42,120,12,0.11,110` | `up, launch -390` |
| Tsubasa back | `eflick` | 400 | `66,40,11,0.20,150` | vx −180 |
| Ember fwd | `clawrend` | 380 | `44,44,8,0.09,50` + `44,44,8,0.19,150` | vx 200 |
| Ember down | `lowrake` | 360 | `62,20,11,0.10,90` | `low, trip` |
| Ember back | `eretreat` | 340 | `48,42,10,0.10,120` | vx −170 |
| Ember **up** | — | — | — | **not in this table** — his launcher has owned Up+Heavy since 332 |
| Oni fwd | `ghfwd` | 850 | `158,30,13,0.12,165` | no track (20 cells) |
| Oni down | `ghdown` | 800 | `145,20,10,0.12,120` | `low, trip`; no track |
| Oni up | `ghup` | 800 | `48,128,12,0.12,115` | `up, launch -380`; keeps its 6-stop track |
| Oni back | `ghback` | 800 | `96,44,11,0.12,150` | no track (10 cells) |
| **Special:** Shin up | `srisaa` | 420 | `44,150,14,0.14,120` | `up, launch -400`, vy −280 |
| **Special:** Tsubasa down | `divecut` | 460 | `60,72,16,**0.34**,170` | `spike, down`, vx 190, vy −300, **vyAir 620** |
| **Special:** Tsubasa up | `airthrow` | 440 | `36,160,13,0.16,110` | `up` |

⚠️ **Negative vy is UP in this engine** (`this.y += this.vy * dt`). Dive Cut shipped once
with its box at 0.20 s — a move named DIVE CUT on a *rising* arc carrying `spike`, whose
contract drives the victim downward, firing while its owner climbed. The box now sits at
0.34 s, past the 0.27 s apex.

Oni's four ground heavies **must** come through this table. There is no ground-heavy
`dirCells` family: `gl*` is ground LIGHT, `gs*` is ground SPECIAL, and `h*`/`s*` are the
AIR families (those `dirCells` calls sit inside `if (p.attackAir)`). Packing his grounded
rows as `hfwd`/`hback`/`hup` drew them 36 frames each in the AIR and zero on the ground —
his standing thrust played mid-jump. The keys are `gh*`, their own family.

---

## 5. The nine fighters

Each table is **measured**, one real press each, at SHEET_V 714. `cells` = how many
distinct cells that input actually plays. `boxes` = hitboxes spawned. `dmg` = raw
recorded damage, BEFORE the global modifiers in §3.


> **Pronoun canon — never infer from a name or a silhouette.**
> **he/him:** Executioner, Shin, Tsubasa, Ember, Kael, Mokurai, Oni.
> **she/her:** Mizu, Exile.
> This binds UI strings, ending cards, commit messages and `SHEET_V` entries, not just
> prose. Anyone not listed: open the Story Bible first.



### Executioner — `spec.id 0`

**Long Sword · Heavy / Berserk · spd 3.5 · pow 9 · reach 8 · def 8 · Special costs 25 chakra**

Sheet `executioner.png` / `executioner.json` — **388 × 496**, footY **488**, scale **0.2665**, **330 cells**, 165 named keys.

**What this fighter does that nobody else does**

- **RECOVERY_TAX = 1** — he is the only fighter who pays NO speed tax on recovery. He keeps speed 3.5 (walk/dash/run untouched, owner's order) but his reactions are lightning. `SLICE_SPEED = 0.62` makes the swing itself fast.
- **Chūdan stance** rewrites his normals: LIGHT becomes one fast poke, HEAVY becomes a four-thrust flurry. He cannot really block in it. Every command variant (Fwd+Heavy drive stab, Back+Heavy iai, Up+Heavy gyaku-kesa, all three kicks) keeps its own slot.
- **Back+Special is redirected to Heavy** at `executeAttack` — grounded, axis = −facing, no up/down. That is why Back+H and Back+S read identically in the table. Owner's redirect, by design.
- **Dread:** three landed heavies arm the next Special — `w ×1.4, h ×1.2, dmg ×1.5`, 0.5 s armor, orange spark tell.
- His `hneu` and `special` rows are packed but were not reached by any of the 30 probe inputs — stance/condition gated, not dead.


**Every packed row**

`ajump`×6, `aneu`×8, `block`×1, `blockhit`×1, `crouch_`×8, `fall`×1, `getup`×4, `grab`×8, `grabbed`×8, `guard`×8, `hneu`×8, `hurt`×2, `idle`×1, `jump`×2, `kpush`×8, `ksweep`×8, `medium`×8, `roll_`×6, `run_clean`×8, `special`×8, `walljump`×1, `wallslide`×1, `xidle`×6, `xjodan`×8, `xkiriage`×8, `xnuki`×6, `xrise`×8, `xsheath`×6, `xtsuki`×3


**Measured move table — 30 inputs, SHEET_V 714**

| where | tier | dir | draws | cells | dmg | dur ms | boxes | proj | field |
|---|---|---|---|---|---|---|---|---|---|
| ground | Light | neutral | `xnuki` | 6 | 12 | 112 | 1 | 0 | 0 |
| ground | Light | fwd | `kpush` | 8 | 6 | 165 | 1 | 0 | 0 |
| ground | Light | back | `ksweep` | 8 | 9 | 145 | 1 | 0 | 0 |
| ground | Light | down | `ksweep` | 8 | 9 | 165 | 1 | 0 | 0 |
| ground | Light | up | `xnuki` | 6 | 12 | 112 | 1 | 0 | 0 |
| ground | Heavy | neutral | `xjodan` | 6 | 27 | 205 | 1 | 0 | 0 |
| ground | Heavy | fwd | `xtsuki` | 3 | 21 | 320 | 1 | 0 | 0 |
| ground | Heavy | back | `xjodan` | 6 | 27 | 640 | 1 | 0 | 0 |
| ground | Heavy | down | `xjodan` | 6 | 19.5 | 380 | 1 | 0 | 0 |
| ground | Heavy | up | `xrise`+`xkiriage` | 6 | 25.5 | 360 | 1 | 0 | 0 |
| ground | Special | neutral | `xtsuki` | 3 | 28 | 250 | 1 | 0 | 0 |
| ground | Special | fwd | `xsheath` | 6 | 22 | 460 | 1 | 0 | 0 |
| ground | Special | back | `xjodan` | 6 | 27 | 640 | 1 | 0 | 0 |
| ground | Special | down | `xtsuki` | 3 | 22 | 420 | 1 | 0 | 0 |
| ground | Special | up | `xtsuki` | 3 | 20 | 480 | 1 | 0 | 0 |
| air | Light | neutral | `aneu` | 8 | 12 | 112 | 1 | 0 | 0 |
| air | Light | fwd | `aneu` | 8 | 12 | 112 | 1 | 0 | 0 |
| air | Light | back | `aneu` | 8 | 12 | 112 | 1 | 0 | 0 |
| air | Light | down | `aneu` | 8 | 12 | 112 | 1 | 0 | 0 |
| air | Light | up | `aneu` | 1 | 10.5 | 112 | 1 | 0 | 0 |
| air | Heavy | neutral | `hneu` | 8 | 27 | 205 | 1 | 0 | 0 |
| air | Heavy | fwd | `aneu` | 8 | 27 | 205 | 1 | 0 | 0 |
| air | Heavy | back | `aneu` | 8 | 27 | 205 | 1 | 0 | 0 |
| air | Heavy | down | `aneu` | 1 | 24 | 900 | 1 | 0 | 0 |
| air | Heavy | up | `aneu` | 8 | 27 | 205 | 1 | 0 | 0 |
| air | Special | neutral | `aneu` | 8 | 28 | 250 | 1 | 0 | 0 |
| air | Special | fwd | `aneu` | 8 | 28 | 250 | 1 | 0 | 0 |
| air | Special | back | `aneu` | 8 | 28 | 250 | 1 | 0 | 0 |
| air | Special | down | `aneu` | 8 | 28 | 250 | 1 | 0 | 0 |
| air | Special | up | `aneu` | 8 | 28 | 250 | 1 | 0 | 0 |

**Rows the 30 presses never reached:** `medium`, `special`.
`medium` is the probe's blind spot (§3); the rest are stance- or condition-gated.
**Two independent signals before you call any row dead.**


### Mizu — `spec.id 1`

**Long Bo Staff · Zoning / Support · spd 6 · pow 5 · reach 10 · def 5 · Special costs 30 chakra**

Sheet `mizu.png` / `mizu.json` — **300 × 320**, footY **312**, scale **0.3782**, **228 cells**, 154 named keys.

**What this fighter does that nobody else does**

- Longest reach in the game (10). Her whole kit is spacing — that is why all four of her directions are in `DIR_MOVES` with genuinely different geometry (165 px thrust, 140 px low sweep, 130 px tall anti-air, 110 px spin).
- **Mode 2 — Hanbō no Kata (`V`)**: the bo splits into twin hanbō. Caught ahead of the type dispatch. Hanbō Light fwd = `62,26,6, delay .09, 90`; hanbō neutral Light = `52,32,5,.08,70`; hanbō Heavy = `70,40,12*pow,.12,120` with **`unblockable`** at 0.26 s delay.
- Her staff is **wood** — `weaponMat` is not metal, so her boxes carry **no `hasuji`** and clash differently from a blade.
- Drops circular mist fields (`smokeFields`) — a field, not a hitbox; the probe counts these in the `field` column.


**Every packed row**

`ajump`×6, `aneu`×8, `block`×1, `bolow`×8, `bothrust`×7, `fall`×1, `getup`×4, `grab`×8, `grabbed`×8, `gsup`×6, `heavy_i`×8, `hurt`×2, `idle`×1, `jump`×2, `kpush`×8, `ksweep`×8, `light`×8, `medium`×8, `ristaff`×8, `roll_`×6, `run_clean`×8, `special`×8, `staffspin`×7, `walljump`×1, `wallslide`×1, `xidle`×6


**Measured move table — 30 inputs, SHEET_V 714**

| where | tier | dir | draws | cells | dmg | dur ms | boxes | proj | field |
|---|---|---|---|---|---|---|---|---|---|
| ground | Light | neutral | `light` | 8 | 6.7 | 180 | 1 | 0 | 0 |
| ground | Light | fwd | `kpush` | 8 | 3.3 | 165 | 1 | 0 | 0 |
| ground | Light | back | `ksweep` | 8 | 5 | 145 | 1 | 0 | 0 |
| ground | Light | down | `ksweep` | 8 | 5 | 165 | 1 | 0 | 0 |
| ground | Light | up | `light` | 8 | 6.7 | 180 | 1 | 0 | 0 |
| ground | Heavy | neutral | `heavy_i` | 8 | 15 | 330 | 1 | 0 | 0 |
| ground | Heavy | fwd | `bothrust` | 7 | 10 | 380 | 1 | 0 | 0 |
| ground | Heavy | back | `staffspin` | 7 | 9.2 | 400 | 1 | 0 | 0 |
| ground | Heavy | down | `bolow` | 8 | 8.3 | 360 | 1 | 0 | 0 |
| ground | Heavy | up | `ristaff` | 8 | 10 | 380 | 1 | 0 | 0 |
| ground | Special | neutral | `special` | 8 | 0 | 320 | 0 | 0 | 1 |
| ground | Special | fwd | `special` | 8 | 12 | 320 | 1 | 0 | 0 |
| ground | Special | back | `special` | 8 | 12 | 420 | 1 | 0 | 0 |
| ground | Special | down | `special` | 8 | 12 | 400 | 1 | 0 | 0 |
| ground | Special | up | `gsup` | 6 | 0 | 180 | 0 | 0 | 0 |
| air | Light | neutral | `aneu` | 8 | 6.7 | 180 | 1 | 0 | 0 |
| air | Light | fwd | `aneu` | 8 | 6.7 | 180 | 1 | 0 | 0 |
| air | Light | back | `aneu` | 8 | 6.7 | 180 | 1 | 0 | 0 |
| air | Light | down | `aneu` | 8 | 6.7 | 180 | 1 | 0 | 0 |
| air | Light | up | `aneu` | 1 | 5.8 | 206 | 1 | 0 | 0 |
| air | Heavy | neutral | `aneu` | 8 | 15 | 330 | 1 | 0 | 0 |
| air | Heavy | fwd | `aneu` | 8 | 15 | 330 | 1 | 0 | 0 |
| air | Heavy | back | `aneu` | 8 | 15 | 330 | 1 | 0 | 0 |
| air | Heavy | down | `aneu` | 1 | 13.3 | 900 | 1 | 0 | 0 |
| air | Heavy | up | `aneu` | 8 | 15 | 330 | 1 | 0 | 0 |
| air | Special | neutral | `aneu` | 8 | 0 | 320 | 0 | 0 | 1 |
| air | Special | fwd | `aneu` | 8 | 12 | 380 | 1 | 0 | 0 |
| air | Special | back | `aneu` | 8 | 12 | 400 | 1 | 0 | 0 |
| air | Special | down | `aneu` | 8 | 13 | 420 | 1 | 0 | 0 |
| air | Special | up | `aneu` | 8 | 12 | 400 | 1 | 0 | 0 |

**Rows the 30 presses never reached:** `medium`.
`medium` is the probe's blind spot (§3); the rest are stance- or condition-gated.
**Two independent signals before you call any row dead.**


### Shin — `spec.id 2`

**Hand-to-Hand / Wire Tool · Speed / Assassin · spd 9 · pow 4 · reach 7 · def 4 · Special costs 15 chakra**

Sheet `shin.png` / `shin.json` — **520 × 370**, footY **330**, scale **0.3451**, **378 cells**, 170 named keys.

**What this fighter does that nobody else does**

- Cheapest Special in the roster (15 chakra); fastest body tied with Oni.
- **Fwd+Heavy is a three-box move** — elbow (0.08 s) → knee (0.16 s) → palm (0.26 s). If you retime this row, those three delays ARE the animation.
- **Material is `'mail'`, not flesh** — Story Bible chainmail lets his strikes trade with blades. His trades ring the DULL clash, never the katana edge. Do NOT give a bare knife-hand `mat:'steel'`; the back heavy (ura-shutō) had steel carried over from the old kunai art and it rang an empty hand like a sword.
- **Mode 2 — Kage-Nui (`V`)**: shuriken and razor wires, `dmg ×2.0` on every `spawnHitbox`. The wire's own latch/slice damage sits outside `spawnHitbox` with its own constants and is NOT doubled. `f2Step` counts his three-hit Form-2 light string because `chainComboTier` only knows light→heavy→special.
- **Air Light is deliberately excluded from Form 2** — the owner's Form-2 table lists exactly one airborne family (Air Heavy, the Dive-Pierce). It used to fall through and run the grounded jab, box and all, in mid-air.
- **His single eye is CANON** — never flag his eye count, and never measure face defects off keyed cells.


**Every packed row**

`ajump`×6, `aneu`×8, `block`×1, `fall`×1, `getup`×3, `ghback`×6, `ghdown`×6, `ghfwd`×6, `ghup`×6, `grab`×8, `grabbed`×8, `gsback`×8, `hneu`×8, `hurt`×2, `idle`×1, `jump`×2, `kpush`×5, `ksweep`×8, `light`×8, `medium`×8, `roll_`×6, `run_clean`×8, `sneu`×8, `sparry`×8, `special`×8, `srisaa`×8, `walljump`×1, `wallslide`×1, `xidle`×6


**Measured move table — 30 inputs, SHEET_V 714**

| where | tier | dir | draws | cells | dmg | dur ms | boxes | proj | field |
|---|---|---|---|---|---|---|---|---|---|
| ground | Light | neutral | `light` | 8 | 5.3 | 180 | 1 | 0 | 0 |
| ground | Light | fwd | `kpush` | 5 | 2.7 | 165 | 1 | 0 | 0 |
| ground | Light | back | `ksweep` | 8 | 4 | 145 | 1 | 0 | 0 |
| ground | Light | down | `ksweep` | 8 | 4 | 165 | 1 | 0 | 0 |
| ground | Light | up | `light` | 8 | 5.3 | 180 | 1 | 0 | 0 |
| ground | Heavy | neutral | `hneu` | 8 | 12 | 330 | 1 | 0 | 0 |
| ground | Heavy | fwd | `ghfwd` | 6 | 11.3 | 420 | 3 | 0 | 0 |
| ground | Heavy | back | `ghback` | 6 | 5.3 | 400 | 1 | 0 | 0 |
| ground | Heavy | down | `ghdown` | 6 | 6 | 340 | 1 | 0 | 0 |
| ground | Heavy | up | `ghup` | 6 | 7.3 | 380 | 1 | 0 | 0 |
| ground | Special | neutral | `special` | 8 | 13 | 320 | 1 | 0 | 0 |
| ground | Special | fwd | `special` | 8 | 0 | 320 | 0 | 1 | 0 |
| ground | Special | back | `gsback` | 8 | 13 | 320 | 1 | 0 | 0 |
| ground | Special | down | `special` | 8 | 0 | 300 | 0 | 3 | 0 |
| ground | Special | up | `srisaa` | 8 | 14 | 420 | 1 | 0 | 0 |
| air | Light | neutral | `aneu` | 8 | 5.3 | 180 | 1 | 0 | 0 |
| air | Light | fwd | `aneu` | 8 | 5.3 | 180 | 1 | 0 | 0 |
| air | Light | back | `aneu` | 8 | 5.3 | 180 | 1 | 0 | 0 |
| air | Light | down | `aneu` | 8 | 5.3 | 180 | 1 | 0 | 0 |
| air | Light | up | `aneu` | 1 | 4.7 | 206 | 1 | 0 | 0 |
| air | Heavy | neutral | `hneu` | 8 | 12 | 330 | 1 | 0 | 0 |
| air | Heavy | fwd | `aneu` | 8 | 12 | 330 | 1 | 0 | 0 |
| air | Heavy | back | `aneu` | 8 | 12 | 330 | 1 | 0 | 0 |
| air | Heavy | down | `aneu` | 1 | 10.7 | 900 | 1 | 0 | 0 |
| air | Heavy | up | `aneu` | 8 | 12 | 330 | 1 | 0 | 0 |
| air | Special | neutral | `aneu` | 8 | 13 | 320 | 1 | 0 | 0 |
| air | Special | fwd | `aneu` | 8 | 13 | 320 | 1 | 0 | 0 |
| air | Special | back | `aneu` | 8 | 13 | 320 | 1 | 0 | 0 |
| air | Special | down | `aneu` | 8 | 13 | 320 | 1 | 0 | 0 |
| air | Special | up | `aneu` | 8 | 13 | 320 | 1 | 0 | 0 |

**Rows the 30 presses never reached:** `medium`, `sneu`, `sparry`.
`medium` is the probe's blind spot (§3); the rest are stance- or condition-gated.
**Two independent signals before you call any row dead.**


### Tsubasa — `spec.id 3`

**Twin Daggers (Tantō) · Precision / Counter · spd 7 · pow 6 · reach 6 · def 7 · Special costs 20 chakra**

Sheet `tsubasa.png` / `tsubasa.json` — **301 × 320**, footY **312**, scale **0.3663**, **347 cells**, 184 named keys.

**What this fighter does that nobody else does**

- **Neutral / Back / Up + Special are all his strict 0.133 s parry** — a mechanics decision, not an art gap. `sneu`/`sback`/`sup` are packed and draw the moment those directions stop parrying.
- **Dive Cut (Down+Special)** is the roster's only `spike` + `down` pair: `vy −300` hop, box at **0.34 s** on the way down, `vyAir 620` so an airborne input drives him DOWN instead of turning a descent into a second climb.
- **Air Throw (Up+Special)** is a 160 px-tall `up` box with `air: false` — it plants him.
- **Mode 2 — Sakate (`V`)**: both tantō reversed. Dash+Light in sakate plays `rgrush` as a dash attack: `62,40,12*pow,.12,170`.


**Every packed row**

`airthrow`×8, `ajump`×6, `aneu`×8, `block`×1, `crouch_`×4, `divecut`×8, `eflick`×6, `fall`×1, `getup`×4, `grab`×8, `grabbed`×8, `gsfwd`×8, `heavy`×2, `hurt`×2, `idle`×1, `jump`×2, `kpush`×8, `ksweep`×8, `light`×8, `lowtanto`×8, `medium`×8, `rgrush`×8, `ristwin`×8, `roll_`×8, `run_clean`×8, `sneu`×8, `special`×8, `walljump`×1, `wallslide`×4, `xidle`×6


**Measured move table — 30 inputs, SHEET_V 714**

| where | tier | dir | draws | cells | dmg | dur ms | boxes | proj | field |
|---|---|---|---|---|---|---|---|---|---|
| ground | Light | neutral | `light` | 8 | 8 | 180 | 1 | 0 | 0 |
| ground | Light | fwd | `kpush` | 8 | 4 | 165 | 1 | 0 | 0 |
| ground | Light | back | `ksweep` | 8 | 6 | 145 | 1 | 0 | 0 |
| ground | Light | down | `ksweep` | 8 | 6 | 165 | 1 | 0 | 0 |
| ground | Light | up | `light` | 8 | 8 | 180 | 1 | 0 | 0 |
| ground | Heavy | neutral | `heavy` | 2 | 18 | 330 | 1 | 0 | 0 |
| ground | Heavy | fwd | `rgrush` | 8 | 14 | 380 | 2 | 0 | 0 |
| ground | Heavy | back | `eflick` | 6 | 11 | 400 | 1 | 0 | 0 |
| ground | Heavy | down | `lowtanto` | 8 | 10 | 340 | 1 | 0 | 0 |
| ground | Heavy | up | `ristwin` | 8 | 12 | 380 | 1 | 0 | 0 |
| ground | Special | neutral | `special` | 2 | 0 | 320 | 0 | 0 | 0 |
| ground | Special | fwd | `gsfwd` | 8 | 12 | 320 | 1 | 0 | 0 |
| ground | Special | back | `special` | 8 | 10 | 450 | 4 | 0 | 0 |
| ground | Special | down | `divecut` | 8 | 16 | 460 | 1 | 0 | 0 |
| ground | Special | up | `airthrow` | 8 | 13 | 440 | 1 | 0 | 0 |
| air | Light | neutral | `aneu` | 8 | 8 | 180 | 1 | 0 | 0 |
| air | Light | fwd | `aneu` | 8 | 8 | 180 | 1 | 0 | 0 |
| air | Light | back | `aneu` | 8 | 8 | 180 | 1 | 0 | 0 |
| air | Light | down | `aneu` | 8 | 8 | 180 | 1 | 0 | 0 |
| air | Light | up | `aneu` | 1 | 7 | 206 | 1 | 0 | 0 |
| air | Heavy | neutral | `aneu` | 8 | 18 | 330 | 1 | 0 | 0 |
| air | Heavy | fwd | `aneu` | 8 | 18 | 330 | 1 | 0 | 0 |
| air | Heavy | back | `aneu` | 8 | 18 | 330 | 1 | 0 | 0 |
| air | Heavy | down | `aneu` | 1 | 16 | 900 | 1 | 0 | 0 |
| air | Heavy | up | `aneu` | 8 | 18 | 330 | 1 | 0 | 0 |
| air | Special | neutral | `aneu` | 8 | 13 | 320 | 1 | 0 | 0 |
| air | Special | fwd | `aneu` | 8 | 13 | 320 | 1 | 0 | 0 |
| air | Special | back | `aneu` | 8 | 13 | 320 | 1 | 0 | 0 |
| air | Special | down | `divecut` | 8 | 16 | 460 | 1 | 0 | 0 |
| air | Special | up | `aneu` | 8 | 13 | 320 | 1 | 0 | 0 |

**Rows the 30 presses never reached:** `medium`, `sneu`.
`medium` is the probe's blind spot (§3); the rest are stance- or condition-gated.
**Two independent signals before you call any row dead.**


### Ember — `spec.id 4`

**Tekko-Kagi Claws · Brawler / Rushdown · spd 8 · pow 7 · reach 3 · def 8 · Special costs 25 chakra**

Sheet `ember.png` / `ember.json` — **340 × 377**, footY **369**, scale **0.3414**, **302 cells**, 146 named keys.

**What this fighter does that nobody else does**

- **Reach 3 — the shortest arms in the game.** Every box he owns is small on purpose (44–62 px). Do not 'fix' that by widening; his design is that he has to be inside you.
- **Up+Heavy is his launcher and is NOT in `DIR_MOVES`** — it has owned that input since 332 via `upAtkPending`. Adding a `'4:up'` entry would steal it.
- Fwd+Heavy is a **two-box lunge** (0.09 s and 0.19 s) with vx 200.
- **Claw count is canon-locked at FOUR blades per hand** (owner ruling). The handoff README that says three is stale; the sheet wins. Never shrink a hand to three.
- **He has no valid scale ruler** — hood-in-box reads ×1.20 as ×1.04. Prove the PACK, never the board.
- **Sheet geometry is non-standard: 340 × 377, footY 369.** Never assume 300×320 for him.


**Every packed row**

`ajump`×6, `aneu`×8, `block`×1, `clawrend`×6, `crouch_`×4, `eheavy`×8, `eparry`×8, `eretreat`×6, `erip`×6, `espec`×8, `fall`×1, `getup`×4, `grab`×8, `grabbed`×8, `hurt`×2, `idle`×1, `jump`×2, `kpush`×8, `light`×8, `lowrake`×6, `medium`×8, `roll_`×6, `run_clean`×8, `walljump`×1, `wallslide`×1, `xidle`×6


**Measured move table — 30 inputs, SHEET_V 714**

| where | tier | dir | draws | cells | dmg | dur ms | boxes | proj | field |
|---|---|---|---|---|---|---|---|---|---|
| ground | Light | neutral | `light` | 8 | 9.3 | 180 | 1 | 0 | 0 |
| ground | Light | fwd | `kpush` | 8 | 4.7 | 165 | 1 | 0 | 0 |
| ground | Light | back | `kpush` | 8 | 7 | 145 | 1 | 0 | 0 |
| ground | Light | down | `kpush` | 8 | 7 | 165 | 1 | 0 | 0 |
| ground | Light | up | `light` | 8 | 9.3 | 180 | 1 | 0 | 0 |
| ground | Heavy | neutral | `eheavy` | 8 | 21 | 330 | 1 | 0 | 0 |
| ground | Heavy | fwd | `clawrend` | 6 | 18.7 | 380 | 2 | 0 | 0 |
| ground | Heavy | back | `eretreat` | 6 | 11.7 | 340 | 1 | 0 | 0 |
| ground | Heavy | down | `lowrake` | 6 | 12.8 | 360 | 1 | 0 | 0 |
| ground | Heavy | up | `eheavy` | 8 | 21 | 380 | 1 | 0 | 0 |
| ground | Special | neutral | `espec` | 8 | 14 | 320 | 1 | 0 | 0 |
| ground | Special | fwd | `espec` | 8 | 22 | 420 | 2 | 0 | 0 |
| ground | Special | back | `eparry` | 1 | 0 | 320 | 0 | 0 | 0 |
| ground | Special | down | `erip` | 6 | 14 | 440 | 1 | 0 | 0 |
| ground | Special | up | `espec` | 8 | 15 | 460 | 1 | 0 | 0 |
| air | Light | neutral | `aneu` | 8 | 9.3 | 180 | 1 | 0 | 0 |
| air | Light | fwd | `aneu` | 8 | 9.3 | 180 | 1 | 0 | 0 |
| air | Light | back | `aneu` | 8 | 9.3 | 180 | 1 | 0 | 0 |
| air | Light | down | `aneu` | 8 | 9.3 | 180 | 1 | 0 | 0 |
| air | Light | up | `aneu` | 1 | 8.2 | 206 | 1 | 0 | 0 |
| air | Heavy | neutral | `aneu` | 8 | 21 | 330 | 1 | 0 | 0 |
| air | Heavy | fwd | `aneu` | 8 | 21 | 330 | 1 | 0 | 0 |
| air | Heavy | back | `aneu` | 8 | 21 | 330 | 1 | 0 | 0 |
| air | Heavy | down | `aneu` | 1 | 18.7 | 900 | 1 | 0 | 0 |
| air | Heavy | up | `aneu` | 8 | 21 | 330 | 1 | 0 | 0 |
| air | Special | neutral | `aneu` | 8 | 14 | 320 | 1 | 0 | 0 |
| air | Special | fwd | `aneu` | 8 | 14 | 320 | 1 | 0 | 0 |
| air | Special | back | `aneu` | 8 | 14 | 320 | 1 | 0 | 0 |
| air | Special | down | `aneu` | 8 | 14 | 320 | 1 | 0 | 0 |
| air | Special | up | `aneu` | 8 | 14 | 320 | 1 | 0 | 0 |

**Rows the 30 presses never reached:** `medium`.
`medium` is the probe's blind spot (§3); the rest are stance- or condition-gated.
**Two independent signals before you call any row dead.**


### Kael — `spec.id 5`

**Katana & Wakizashi · Starter / All-Round · spd 6 · pow 6 · reach 6 · def 6 · Special costs 25 chakra**

Sheet `kael.png` / `kael.json` — **300 × 320**, footY **312**, scale **0.4046**, **299 cells**, 161 named keys.

**What this fighter does that nobody else does**

- The reference fighter — every stat is 6, `renderScale: 1.0`. If a shared mechanic feels wrong, test it on Kael first.
- **One long sword + one short sword** (owner ruling + `kael.json` `weapon_type`). Doc 17's 'two equal long swords' is WRONG and is not authority.
- His kit is bespoke `k*` rows, not the shared families: `kdual` (Light), `kcross` (Heavy neutral), `kcyc` (Twin Cyclone, fwd Heavy), `kscis` (Scissor, down Heavy), `krise` (Rising Twin), `kspin` (Special), `ktrav` (travel), `kfang` (Skyward), `kxcut` (**air** X-Cut), `xparry` (Niten parry).
- **`kxcut` is his air family.** He is deliberately excluded from the generic `!isGrounded` air branch by `F.kxcut1 !== undefined`. Branch order matters — `kxcut` once ate his `hfwd`/`hback`/`hup` and measured 0/6 cells.
- He has **no kick art at all** — no `kpush`, no `ksweep`, no `kheel`. Three of his four directional Lights therefore route to `kdual` (measured `kdual3→5→7`). A known ART gap, not a routing bug.


**Every packed row**

`adown`×8, `ajump`×6, `block`×1, `crouch_`×4, `getup`×4, `grab`×8, `grabbed`×7, `hurt`×2, `idle`×1, `kcross`×8, `kcyc`×8, `kdual`×8, `kfang`×8, `krise`×8, `kscis`×8, `kspin`×8, `ktrav`×8, `kxcut`×8, `medium`×8, `roll_`×6, `run_clean`×8, `sneu`×8, `walljump`×1, `wallslide`×1, `xidle`×6, `xparry`×6


**Measured move table — 30 inputs, SHEET_V 714**

| where | tier | dir | draws | cells | dmg | dur ms | boxes | proj | field |
|---|---|---|---|---|---|---|---|---|---|
| ground | Light | neutral | `kdual` | 8 | 8 | 180 | 1 | 0 | 0 |
| ground | Light | fwd | `kdual` | 8 | 4 | 165 | 1 | 0 | 0 |
| ground | Light | back | `kdual` | 8 | 6 | 145 | 1 | 0 | 0 |
| ground | Light | down | `kdual` | 8 | 6 | 165 | 1 | 0 | 0 |
| ground | Light | up | `kdual` | 8 | 8 | 180 | 1 | 0 | 0 |
| ground | Heavy | neutral | `kcross` | 8 | 18 | 330 | 1 | 0 | 0 |
| ground | Heavy | fwd | `kcyc` | 8 | 21 | 380 | 2 | 0 | 0 |
| ground | Heavy | back | `kscis`+`xparry` | 6 | 0 | 330 | 0 | 0 | 0 |
| ground | Heavy | down | `kscis`+`xparry` | 8 | 20 | 400 | 2 | 0 | 0 |
| ground | Heavy | up | `kscis`+`xparry` | 6 | 0 | 330 | 0 | 0 | 0 |
| ground | Special | neutral | `kspin` | 8 | 15 | 520 | 1 | 0 | 0 |
| ground | Special | fwd | `ktrav` | 8 | 18 | 440 | 1 | 0 | 0 |
| ground | Special | back | `kscis`+`xparry` | 6 | 0 | 320 | 0 | 0 | 0 |
| ground | Special | down | `krise` | 5 | 12 | 520 | 1 | 0 | 0 |
| ground | Special | up | `kfang` | 8 | 16 | 440 | 1 | 0 | 0 |
| air | Light | neutral | `kxcut` | 8 | 8 | 180 | 1 | 0 | 0 |
| air | Light | fwd | `kxcut` | 8 | 8 | 180 | 1 | 0 | 0 |
| air | Light | back | `kxcut` | 8 | 8 | 180 | 1 | 0 | 0 |
| air | Light | down | `adown` | 8 | 8 | 180 | 1 | 0 | 0 |
| air | Light | up | `kxcut` | 1 | 7 | 206 | 1 | 0 | 0 |
| air | Heavy | neutral | `kxcut` | 8 | 18 | 330 | 1 | 0 | 0 |
| air | Heavy | fwd | `kxcut` | 8 | 18 | 330 | 1 | 0 | 0 |
| air | Heavy | back | `kxcut` | 8 | 18 | 330 | 1 | 0 | 0 |
| air | Heavy | down | `kxcut` | 1 | 16 | 900 | 1 | 0 | 0 |
| air | Heavy | up | `kxcut` | 8 | 18 | 330 | 1 | 0 | 0 |
| air | Special | neutral | `kxcut` | 6 | 15 | 520 | 1 | 0 | 0 |
| air | Special | fwd | `kxcut` | 6 | 15 | 520 | 1 | 0 | 0 |
| air | Special | back | `kxcut` | 6 | 15 | 520 | 1 | 0 | 0 |
| air | Special | down | `kxcut` | 6 | 15 | 520 | 1 | 0 | 0 |
| air | Special | up | `kxcut` | 6 | 15 | 520 | 1 | 0 | 0 |

**Rows the 30 presses never reached:** `medium`, `sneu`.
`medium` is the probe's blind spot (§3); the rest are stance- or condition-gated.
**Two independent signals before you call any row dead.**


### Mokurai — `spec.id 6`

**Prayer Beads / Bare Hands · Sage of Nothingness / Area · spd 5 · pow 7 · reach 8 · def 8 · Special costs 25 chakra**

Sheet `mokurai.png` / `mokurai.json` — **300 × 248**, footY **218**, scale **0.4808**, **347 cells**, 172 named keys.

**What this fighter does that nobody else does**

- **BARE HANDS. NO STAFF, and there never was one** — owner ruling Aug 5 2026. Every shipped cell is bead-wrapped fists. A staff in a candidate frame means the frame is wrong.
- **Flesh material — his boxes never clash.** An empty hand has no steel to meet a blade (owner ruling Aug 2). One material predicate, no id list.
- **Karma**: absorbed force is stored and paid whole on the next Heavy or Special (`dmg += karma`, gold spark). **Enlightened** blooms his Specials `×1.3` in both axes.
- **The Crack**: six seconds of feint rhythm — *every* box lands `CRACK_FEINT` late and a false tell fires at the original timing. Applied inside `spawnHitbox`, so nothing in his kit is exempt and nothing has to remember to be.
- **Air kit is its own block** (`spec.id === 6 && attackAir`): air Heavy neutral/up = `60*(reach/6), 40, 18*pow`; air Light fwd/down = `40*(reach/6), 30, 8*pow`; air Special fwd = `72,46,13,.13,130`.
- Dash+Light = headbutt: `44,30,10*pow,.12,300`, `tier:'KICK'`, **`wallsplat`**, 0.25 s armor.
- **He is TALLER than Exile** (owner, Sep 1) — keep that through any exile re-ruling.
- **Sheet geometry: 300 × 248, footY 218.** The `b*`/`m*` families (`bair`, `bheavy`, `bjump`, `brun`, `bspec`, `mbell`, `mblast`, `mhammer`, `mpalm`, `mroll`, `mwall`) are his alone.


**Every packed row**

`bair`×8, `bheavy`×5, `bjump`×8, `block`×1, `brun`×8, `bspec`×5, `crouch_`×4, `getup`×7, `grabbed`×8, `gsup`×8, `hurt`×1, `idle`×1, `kpush`×8, `light`×8, `mbell`×8, `mblast`×8, `mblock`×7, `medium`×8, `mhammer`×5, `mhurt`×7, `mpalm`×5, `mroll`×8, `mthrow`×3, `mwall`×8, `special`×8, `upatk`×8, `xidle`×6


**Measured move table — 30 inputs, SHEET_V 714**

| where | tier | dir | draws | cells | dmg | dur ms | boxes | proj | field |
|---|---|---|---|---|---|---|---|---|---|
| ground | Light | neutral | `light` | 8 | 9.3 | 180 | 1 | 0 | 0 |
| ground | Light | fwd | `kpush` | 8 | 4.7 | 165 | 1 | 0 | 0 |
| ground | Light | back | `kpush` | 8 | 7 | 145 | 1 | 0 | 0 |
| ground | Light | down | `kpush` | 8 | 7 | 165 | 1 | 0 | 0 |
| ground | Light | up | `light` | 8 | 9.3 | 180 | 1 | 0 | 0 |
| ground | Heavy | neutral | `bheavy` | 5 | 21 | 330 | 1 | 0 | 0 |
| ground | Heavy | fwd | `mpalm` | 5 | 15.2 | 330 | 1 | 0 | 0 |
| ground | Heavy | back | `mblast` | 8 | 0 | 340 | 0 | 1 | 0 |
| ground | Heavy | down | `mhammer` | 5 | 16.3 | 330 | 1 | 0 | 0 |
| ground | Heavy | up | `mbell` | 8 | 18.7 | 380 | 1 | 0 | 0 |
| ground | Special | neutral | `bspec` | 5 | 16 | 320 | 1 | 0 | 0 |
| ground | Special | fwd | `bspec` | 5 | 27 | 560 | 3 | 0 | 0 |
| ground | Special | back | `special` | 2 | 0 | 320 | 0 | 0 | 0 |
| ground | Special | down | `bspec` | 5 | 28 | 320 | 2 | 0 | 0 |
| ground | Special | up | `gsup` | 8 | 0 | 320 | 0 | 1 | 0 |
| air | Light | neutral | `bair` | 8 | 9.3 | 180 | 1 | 0 | 0 |
| air | Light | fwd | `bair` | 8 | 9.3 | 200 | 1 | 0 | 0 |
| air | Light | back | `bair` | 8 | 9.3 | 180 | 1 | 0 | 0 |
| air | Light | down | `bair` | 8 | 9.3 | 200 | 1 | 0 | 0 |
| air | Light | up | `bair` | 1 | 8.2 | 206 | 1 | 0 | 0 |
| air | Heavy | neutral | `bair` | 8 | 21 | 330 | 1 | 0 | 0 |
| air | Heavy | fwd | `bair` | 8 | 21 | 330 | 1 | 0 | 0 |
| air | Heavy | back | `bair` | 8 | 21 | 330 | 1 | 0 | 0 |
| air | Heavy | down | `bair` | 1 | 18.7 | 900 | 1 | 0 | 0 |
| air | Heavy | up | `bair` | 8 | 21 | 330 | 1 | 0 | 0 |
| air | Special | neutral | `bair` | 8 | 16 | 320 | 1 | 0 | 0 |
| air | Special | fwd | `bair` | 8 | 13 | 380 | 1 | 0 | 0 |
| air | Special | back | `bair` | 8 | 13 | 380 | 1 | 0 | 0 |
| air | Special | down | `bair` | 8 | 12 | 320 | 1 | 0 | 0 |
| air | Special | up | `bair` | 8 | 10 | 320 | 1 | 0 | 0 |

**Rows the 30 presses never reached:** `medium`, `upatk`.
`medium` is the probe's blind spot (§3); the rest are stance- or condition-gated.
**Two independent signals before you call any row dead.**


### Exile — `spec.id 7`

**Kusarigama · Speed / Agility · spd 10 · pow 5 · reach 9 · def 3 · Special costs 20 chakra**

Sheet `exile.png` / `exile.json` — **480 × 432**, footY **344**, scale **0.4409**, **322 cells**, 167 named keys.

**What this fighter does that nobody else does**

- **Fastest body (10) and highest jumper (`jumpScale 1.12`)** — owner directive: a clear edge, not an outlier. Lowest defense in the roster (3).
- **`gap` is her flag.** The counter-weight snap starts a set distance from the body, so it covers a band of space and deliberately misses anything closer. That dead zone IS the counterplay — never 'fix' it away.
- **Iaijutsu quick-draw**: Light inside `iaiWindow`, or Light during a dash, calls `executeIaijutsu()` — reads as a teleport.
- **Up+Light** (grounded or `vy < -180`) is her own 160 ms up-attack: `34,66,7*pow,.1,60`.
- **Chain anchor (`V`+Fwd → `weaveAnchor`)**: the kusarigama bites a side wall within `ANCHOR_RANGE 210` and holds her `ANCHOR_TIME 1.5 s` with `ANCHOR_STARS 3` (`STAR_CD 0.14`, `STAR_SPEED 560`). A **firing position**, bounded by a hard timer and finite stars, not by chakra — deliberately NOT the wall-cling contract, so it can never become a camp spot. Light with 0 stars releases the anchor.
- **`V` = `enterChampion()`** for her, checked before every other per-fighter stance branch.
- `xanchor`/`xgrap` are only reachable through the anchor and grapple systems. **`xanchor` is chain-less on the live rope and `handAnchor` is in CELL px** (owner ruling @684).
- **Sheet geometry in THIS tree: 480 × 432, footY 344.** The sprite README's 200×226 line is stale — read the manifest, every time.


**Every packed row**

`aneu`×8, `block`×1, `crouch_`×8, `getup`×4, `glback`×8, `grabbed`×8, `gsback`×8, `gsfwd`×8, `guard`×8, `idle`×1, `light`×8, `medium`×8, `run_clean`×8, `slide`×4, `special`×8, `upreach`×8, `walljump`×1, `wallslide`×1, `xanchor`×8, `xgrap`×10, `xheavy`×5, `xhurt`×3, `xidle`×6, `xjump`×6, `xkpush`×8, `xksweep`×8


**Measured move table — 30 inputs, SHEET_V 714**

| where | tier | dir | draws | cells | dmg | dur ms | boxes | proj | field |
|---|---|---|---|---|---|---|---|---|---|
| ground | Light | neutral | `light` | 3 | 6.7 | 180 | 1 | 0 | 0 |
| ground | Light | fwd | `xkpush` | 1 | 3.3 | 165 | 1 | 0 | 0 |
| ground | Light | back | `gsback`+`glback` | 8 | 6.7 | 180 | 1 | 0 | 0 |
| ground | Light | down | `slide`+`xksweep` | 1 | 5 | 165 | 1 | 0 | 0 |
| ground | Light | up | `light` | 3 | 5.8 | 160 | 1 | 0 | 0 |
| ground | Heavy | neutral | `xheavy` | 5 | 15 | 330 | 1 | 0 | 0 |
| ground | Heavy | fwd | `xheavy` | 4 | 12.5 | 340 | 1 | 0 | 0 |
| ground | Heavy | back | `xheavy` | 4 | 11.7 | 300 | 1 | 0 | 0 |
| ground | Heavy | down | `xheavy` | 5 | 10.8 | 300 | 1 | 0 | 0 |
| ground | Heavy | up | `upreach` | 8 | 13.3 | 420 | 1 | 0 | 0 |
| ground | Special | neutral | `special` | 8 | 30 | 520 | 2 | 0 | 0 |
| ground | Special | fwd | `gsfwd` | 8 | 30 | 520 | 2 | 0 | 0 |
| ground | Special | back | `gsback`+`glback` | 8 | 14.2 | 260 | 1 | 0 | 0 |
| ground | Special | down | `special` | 8 | 10 | 320 | 1 | 0 | 0 |
| ground | Special | up | `special` | 8 | 0 | 320 | 0 | 0 | 0 |
| air | Light | neutral | `aneu` | 8 | 6.7 | 180 | 1 | 0 | 0 |
| air | Light | fwd | `aneu` | 8 | 6.7 | 180 | 1 | 0 | 0 |
| air | Light | back | `aneu` | 8 | 6.7 | 180 | 1 | 0 | 0 |
| air | Light | down | `aneu` | 8 | 6.7 | 180 | 1 | 0 | 0 |
| air | Light | up | `aneu` | 1 | 5.8 | 206 | 1 | 0 | 0 |
| air | Heavy | neutral | `aneu` | 8 | 11.7 | 320 | 1 | 0 | 0 |
| air | Heavy | fwd | `aneu` | 8 | 11.7 | 320 | 1 | 0 | 0 |
| air | Heavy | back | `aneu` | 8 | 11.7 | 320 | 1 | 0 | 0 |
| air | Heavy | down | `aneu` | 1 | 13.3 | 900 | 1 | 0 | 0 |
| air | Heavy | up | `aneu` | 8 | 11.7 | 320 | 1 | 0 | 0 |
| air | Special | neutral | `aneu` | 8 | 30 | 520 | 2 | 0 | 0 |
| air | Special | fwd | `aneu` | 8 | 13 | 420 | 1 | 0 | 0 |
| air | Special | back | `aneu` | 8 | 13 | 400 | 1 | 0 | 0 |
| air | Special | down | `aneu` | 8 | 14 | 400 | 1 | 0 | 0 |
| air | Special | up | `aneu` | 8 | 0 | 320 | 0 | 0 | 0 |

**Rows the 30 presses never reached:** `medium`, `xanchor`, `xgrap`.
`medium` is the probe's blind spot (§3); the rest are stance- or condition-gated.
**Two independent signals before you call any row dead.**


### Oni — `spec.id 8`

**Tekko-Kagi Claw · Acrobat / Rushdown · spd 9 · pow 8 · reach 6 · def 6 · Special costs 25 chakra**

Sheet `oni.png` / `oni.json` — **480 × 372**, footY **330**, scale **0.5573**, **502 cells**, 267 named keys.

**What this fighter does that nobody else does**

- **THE FOUNDER.** White demon mask, hood, horns, one clawed hand + two back swords. `jumpScale 1.10`, `runAnimScale 0.8` so each stride pose reads.
- **His second mode (staff/club) is DELETED** — owner ruling. `bostrike`/`bosweep`/`sdown`/`aspin` club cells are never drawn; `mode2` stays false the whole match. The four directional move-sets still fire in the base kit.
- **`HHHLHHLL` hand-seal dial** — 8 Light/Heavy presses with < 0.7 s gaps fires `handseal`: `130,46,18*pow,.32,320`, `launch -380`, `tier: ATTACK_HEAVY`, 650 ms.
- **Down+Special = mid-air smoke bomb, TWICE a round** (`smokeUsed`). Radius 240, 4.0 s field. The third press falls back to `'neutral'`.
- **Razor-wire bind** (`WIRE_BIND_TIME 0.55 s`) converts his next Special. `WHIP_RANGE 132`, `WIRE_SHOT_RANGE 230`, `PHANTOM_RANGE 92` — three NAMED ranges, because the arming site and the `wire1..3` draw ramp must read the SAME number or a three-cell animation quietly desyncs from its window.
- His `attackAnim.dur` is multiplied **×2.2** — his art is slower on purpose.
- **HIS ART ALREADY CARRIES HIS TRAIL, so he gets no engine trail.** His cells measure up to 560× more ink than the others (`gsdown` 4504, `light` 2828, `hneu` 1968). Laying a steel W01/W02 on top double-draws the motion.
- **23 of his beats are SUBSTITUTIONS, not restorations** (703): their source boards are not on disk, so each gutted beat borrows the nearest healthy beat in its own row. `glfwd` is down to 4 distinct poses, `gsback`/`sneu`/`wclaw` to 5, and `wire` collapses to one held pose across all 3 beats. The damaged cells stay on the sheet as orphans and are **NOT deleted** — the day their real boards turn up, one pointer each puts them back.
- **Biggest sheet: 484 cells, 480 × 372, footY 330, scale 0.5573.**


**Every packed row**

`ajump`×6, `aneu`×8, `block`×1, `blockhit`×1, `crouch_`×4, `dive`×6, `fall`×1, `getup`×4, `ghback`×10, `ghdown`×8, `ghfwd`×8, `ghup`×8, `glfwd`×8, `grab`×8, `grabbed`×8, `gsback`×8, `gsfwd`×8, `gsup`×6, `guard`×8, `hfwd`×8, `hneu`×8, `hup`×8, `hurt`×2, `idle`×1, `jump`×2, `kdraw`×8, `knives`×8, `ksweep`×8, `light`×8, `medium`×8, `roll_`×6, `run_clean`×8, `sneu`×8, `special`×8, `stand`×6, `sup`×8, `walljump`×1, `wallneedle`×8, `wallslide`×1, `wclaw`×8, `wire`×3, `wslice`×8


**Measured move table — 30 inputs, SHEET_V 714**

| where | tier | dir | draws | cells | dmg | dur ms | boxes | proj | field |
|---|---|---|---|---|---|---|---|---|---|
| ground | Light | neutral | `light` | 8 | 10.7 | 396 | 1 | 0 | 0 |
| ground | Light | fwd | `glfwd` | 8 | 10.7 | 396 | 1 | 0 | 0 |
| ground | Light | back | `ksweep` | 8 | 8 | 145 | 1 | 0 | 0 |
| ground | Light | down | `ksweep` | 8 | 8 | 165 | 1 | 0 | 0 |
| ground | Light | up | `light` | 8 | 10.7 | 396 | 1 | 0 | 0 |
| ground | Heavy | neutral | `hfwd` | 8 | 24 | 726 | 1 | 0 | 0 |
| ground | Heavy | fwd | `ghfwd` | 8 | 17.3 | 850 | 1 | 0 | 0 |
| ground | Heavy | back | `ghback` | 10 | 14.7 | 800 | 1 | 0 | 0 |
| ground | Heavy | down | `ghdown` | 8 | 13.3 | 800 | 1 | 0 | 0 |
| ground | Heavy | up | `ghup`+`gsup`+`sup` | 8 | 16 | 800 | 1 | 0 | 0 |
| ground | Special | neutral | `special` | 8 | 9 | 460 | 1 | 0 | 0 |
| ground | Special | fwd | `gsfwd` | 8 | 28 | 260 | 1 | 0 | 0 |
| ground | Special | back | `gsback` | 8 | 8 | 440 | 1 | 0 | 0 |
| ground | Special | down | `special` | 8 | 0 | 300 | 0 | 0 | 1 |
| ground | Special | up | `ghup`+`gsup`+`sup` | 6 | 16 | 440 | 1 | 0 | 0 |
| air | Light | neutral | `aneu` | 8 | 10.7 | 594 | 1 | 0 | 0 |
| air | Light | fwd | `aneu` | 8 | 10.7 | 396 | 1 | 0 | 0 |
| air | Light | back | `aneu` | 8 | 10.7 | 396 | 1 | 0 | 0 |
| air | Light | down | `aneu` | 8 | 10.7 | 396 | 1 | 0 | 0 |
| air | Light | up | `aneu` | 1 | 9.3 | 396 | 1 | 0 | 0 |
| air | Heavy | neutral | `hup`+`hneu` | 8 | 24 | 726 | 1 | 0 | 0 |
| air | Heavy | fwd | `hfwd` | 8 | 24 | 726 | 1 | 0 | 0 |
| air | Heavy | back | `aneu` | 8 | 24 | 726 | 1 | 0 | 0 |
| air | Heavy | down | `dive` | 1 | 21.3 | 900 | 1 | 0 | 0 |
| air | Heavy | up | `hup`+`hneu` | 8 | 24 | 726 | 1 | 0 | 0 |
| air | Special | neutral | `aneu` | 8 | 42.7 | 704 | 2 | 0 | 0 |
| air | Special | fwd | `aneu` | 8 | 20 | 400 | 1 | 0 | 0 |
| air | Special | back | `aneu` | 8 | 0 | 360 | 0 | 0 | 0 |
| air | Special | down | `aneu` | 8 | 0 | 300 | 0 | 0 | 1 |
| air | Special | up | `aneu` | 8 | 14 | 380 | 1 | 0 | 0 |

**Rows the 30 presses never reached:** `kdraw`, `knives`, `medium`, `sneu`, `wallneedle`, `wclaw`, `wire`, `wslice`.
`medium` is the probe's blind spot (§3); the rest are stance- or condition-gated.
**Two independent signals before you call any row dead.**

---

## 6. THE FRAME LAW — do not cut a single frame, and do not cut the VFX either

This is the owner's standing order and it outranks every convenience in the pipeline:

> **Never cut out any of the frames — including the VFX that comes with an attack.
> Be conscious enough not to cut them off.**

A frame is the pose **plus** whatever the attack draws around it: the arc, the slam
burst, the speed streak, the smoke, the chain, the ink splash, the sparks. If any of it
leaves the cell, the frame is damaged, whether a human clipped it or a script did.

Three owner rulings this rests on, all already paid for in this repo:

1. **Erase only negative space — never the ink.** `art-loss = 0`, measured in place, or
   the frame is not used.
2. **No straight cutoffs.** If a cut FX has to go, **delete it entirely** — never fade
   it, never soften it, and never touch the body to hide the seam.
3. **Fix the ROW, not canon.** Overshoot in one row means shortening a joint *in that
   row*. Never move canon, never rescale the fighter.

### 6.1 The eight places a frame or its VFX actually gets eaten

Every one of these has already destroyed art in this tree. Know them by name.

| # | mechanism | what it eats | the correct move |
|---|---|---|---|
| 1 | **`extend_sheet.py` clamping** | Anything larger than the cell box is silently **shrunk**. A wide claw pose or a long trail is exactly what overflows. | **Grow the cell, never shrink the fighter.** Ember 300→340, Executioner 320→327 were done for precisely this. Bump `frameW`/`frameH` in the JSON and re-pack. |
| 2 | **The `components == 1` gate** | A detached VFX blob reads as "a surviving drop shadow or FX fragment", and largest-connected-component keying **deletes it**. | That gate is a **body** gate. A detached blob that is *drawn FX* is kept — lift it with `split_fx.py`, do not drop the component. |
| 3 | **Fuzz keying (`FUZZ=42`)** | Translucent FX — mist, smoke, glow, speed streaks, spark falloff — is low-alpha, which is exactly what a fuzz key removes. | Key the **source** frame, inspect the FX region at 4×, and prove `art-loss = 0` on the FX region separately from the body. |
| 4 | **White / near-white keying** (`key_white.py`, `key_edge.py`) | Ink splash, bone-light, white-hot spark cores — and, historically, **eyes**. The keyer ate near-white eyes on 24 cells across Mizu / Tsubasa / Ember (708), and Shin's eye was left as a **hole** in his idle row (706). | Keep every enclosed pocket. Drop a pocket only by name (`--drop-pocket`). Solve the rim; never ramp it. |
| 5 | **The RUNTIME keyer `keyedShodoCell()`** (`web/index.html:1678`) | The engine keys **at draw time**, so **file alpha lies**. Its only guard against flooding drawn art is `clear < sw*sh*0.70 && edgeInk > perimeter*0.30`. A cell whose FX fills the frame can trip that and get flooded — it already ate 35 cells of Oni's and Mokurai's near-black armour down to 0.33–0.60 solidity. | **Emulate `keyedShodoCell` first** (`tools/sprites/keyer_emu.py`) for every sprite QC. Measuring the file instead of the keyed draw is measuring the wrong image. |
| 6 | **Debris scrubbers** (`purge_debris.py`, `scrub_artifacts.py`, `detect_floaters.py`) | They treat small detached ink as debris. **VFX motes are small detached ink.** | Run them with the FX region excluded, and diff the pixel count you removed against what you intended to remove. 420 debris pixels were erased at 699 — negative space only, and that was the whole point. |
| 7 | **`gate_fragments.py`** | Nothing on its own — it **shortlists, it does not judge**. A tucked jump is honestly short and honestly floating. | Never wire it to an automatic delete. A human looks at the montage. |
| 8 | **`strip_orphans.py`** | Unreferenced cells. At 700 it removed 1,527 cells; at 702 **all 1,527 were put back — the strip was never approved.** | Old art leaves in **two steps**: pack the replacement, repoint the key, and only then strip the orphan — **and only when the owner has approved that strip.** |

### 6.2 The two numeric gates — a contact sheet HIDES damage

Never sign off a cut, key, or repack on a contact sheet. Both of these must be measured:

1. **`art-loss = 0`, measured in place.** Same canvas, same coordinates, before vs
   after. Not a re-crop, not a re-scale, not eyeballed on a montage.
2. **Halo-ring check.** A key that "worked" but left a rim, or that shaved a
   one-pixel edge off every stroke, fails here even when the loss count looks small.

If either gate is not measured, the frame is not used. That is the whole rule.

### 6.3 Who owns which VFX — this is why the effects differ per attack

**The engine owns 26 drawn FX crops**, packed from the owner's own sheets into the
appended bottom row of the FX atlas at y 946 (`FX_RECTS` / `FX_DEF`,
`web/index.html:2313`):

- `M01–M10` — movement dust
- `W01–W08` — weapon marks, including the **W01 thin / W02 broad single-sword trails**
  the owner reopened (they ship, SHEET_V 499)
- `H01–H08` — hand and body impacts

Plus `FX_SMOKE` (an 8-beat strip on its own loader), `FX_STRIKE` (512 × 192, the
quick-draw slash + star burst that fires when a clash winner's cut lands through the
bind) and the procedural `createSparks`.

**Which impact FX fires is chosen off the hitbox itself** (`web/index.html:10056`):

```
launch          -> H04        trip            -> H06
diving kick     -> H07        kick            -> H05
dmg >= 10       -> H03        dmg >= 6        -> H02        else H01
```

**So changing a box's flags changes the effect that plays.** Add `launch` to a move and
its impact art changes from H03 to H04. Retime `delay` and the FX moves with it. That is
the "different hitboxes, different effects" relationship in one line — the FX is not
decoration bolted on afterwards, it is a read of the box.

FX are **world-space** and age on game `dt`, so hitstop's 6% crawl freezes them with the
slashes for free. Floor-locked crops anchor bottom-centre; everything else anchors dead
centre, straight from `anchors.jsonl`.

**FX are sized against the REAL bodies**, not the spec's imaginary ones. Measured drawn
body heights, canvas px: Executioner 70.4 · Mizu 62.0 · Shin 66.2 · Tsubasa 69.3 ·
Ember 69.0 · Kael 70.0 · Mokurai 69.5 · Exile 72.3 · **Oni 85.8**. The original spec
assumed 130–155 px and every crop was ~2× too big — the heavy trail alone measured 106 px
against a 70 px body. One factor, `70/142 = 0.493`, applied once, fixed the whole table.
**Do not re-derive FX sizes from a doc. Measure the body.**

**The art owns exactly one fighter's trails: Oni's.** His cells already carry the motion
(`gsdown` 4504 ink, `light` 2828, `hneu` 1968 — up to 560× the others), so he is excluded
from W01/W02 or the motion double-draws. For everyone else: **a sprite cell holds one
fighter. Contact FX belongs to the engine (`processWeaponClash`), never to the art.**

And the deleted thing, so nobody rebuilds it: the **procedural crescent** — `bladeSegment`
scan, `sampleBladeTrail`, `drawBladeTrails` and the parametric arc fallback — is what the
owner killed on Aug 13 2026. Sword trails are **drawn crops** now. Git holds the old code;
leave it there.

### 6.4 Before you ship any cell

- [ ] Read the fighter's `identity-true.txt` **before** packing, not after. Ember shipped
      the wrong claw count across three commits because that file was read too late.
- [ ] Emulate `keyedShodoCell` and QC the **keyed draw**, not the file.
- [ ] `art-loss = 0`, measured in place. Halo-ring measured. Both, or the frame is out.
- [ ] Edge alpha `0` on sides and top; bottom row exactly on `footY`.
- [ ] `components == 1` **for the body** — a detached blob that is drawn FX gets lifted
      with `split_fx.py`, not deleted.
- [ ] No off-palette colour. (A generator once invented 43 purple pixels on Kael, whose
      palette is black and gold.)
- [ ] **Never colour-correct a packed cell by tolerance.** A 300 px cell has no colour
      headroom; one attempt matched 1,852 px of legitimate armour and flattened it to
      black. Fix the source and re-pack.
- [ ] **All three size tools, every test**: `check_row_scale.py` + `eye_scale.py` +
      `gate_fragments.py`. Report the **spread %**, name the ruler you used, and **never
      use bbox height** — a long weapon changing angle moves the bbox without the body
      moving. Scale small rows **UP** and oversized rows **DOWN**; there is no
      "never shrink" rule any more.
- [ ] **Append-only.** New cells appended, names repointed in the JSON, old cells kept
      addressable (`*_old`, `*_v309`). A revert is then a JSON edit, not a regeneration.
- [ ] Byte-verify the pre-existing region: `magick compare -metric AE` must return **0**,
      cropped at the sheet's **own** width. (A check run at the wrong width once reported
      36,320 phantom diffs.)
- [ ] Bump `SHEET_V` in `web/index.html` in the **same commit** as any sprite change.
- [ ] Preview/pack parity: previews render **from the final packed cells**. If a preview
      and the pack disagree, that is one question to the owner, not a guess.
- [ ] Never feed `pack_shodo_row` pre-keyed RGBA.

---


---

## 7. What the probe flagged, and where each one landed

Straight out of the probe run that produced §5. **Reported, not repaired.** Confirm
each against a second signal before touching it, and never delete a row to make a
symptom go away — the sweep reports what it REACHED, nothing more.

### 7.1 Directional Heavies whose art row was not on the sheet — CLOSED at 714

Twelve of the twenty-two rows. All twelve turned out to be packed on
`SHADOWCLASH-RECOVERED` and were ported; see §7.4 for what landed and what still needs
the owner's eye. Kept here because the *shape* of the bug is worth recognising again:
**the move ran perfectly and only the art fell back**, so nothing in the hitbox, the vx or
the recovery looked wrong, and no test failed. `check_dir_moves` is the gate that catches
it — it asserts every named art row exists.

### 7.2 Inputs that play ONE cell — a held pose, not an animation

**FIXED at 711 for the airborne ones.** See §7.4.

| input | draws | cells |
|---|---|---|
| Executioner · air Light up | `fall+ajump` | 1 |
| Executioner · air Heavy down | `fall+ajump` | 1 |
| Mizu · air Light up | `light` | 1 |
| Mizu · air Heavy down | `fall+ajump` | 1 |
| Shin · air Light up | `light` | 1 |
| Shin · air Heavy down | `fall+ajump` | 1 |
| Tsubasa · air Light up | `light` | 1 |
| Tsubasa · air Heavy down | `fall+ajump` | 1 |
| Ember · ground Special back | `eparry` | 1 |
| Ember · air Light up | `light` | 1 |
| Ember · air Heavy down | `fall+ajump` | 1 |
| Kael · air Light up | `ajump` | 1 |
| Kael · air Heavy down | `ajump` | 1 |
| Mokurai · air Light up | `upatk` | 1 |
| Mokurai · air Heavy down | `bjump` | 1 |
| Exile · ground Light fwd | `xkpush` | 1 |
| Exile · ground Light down | `slide+xksweep` | 1 |
| Exile · air Light up | `light` | 1 |
| Exile · air Heavy down | `xjump` | 1 |
| Oni · air Light up | `light` | 1 |
| Oni · air Heavy down | `dive` | 1 |

The pattern is roster-wide: **air Light + Up** and **air Heavy + Down**. The count of
one-cell holds is unchanged at 711 and that is correct — the fix was never about the
count. Both are *supposed* to hold one cell (an up-poke and a committed plunge). What
was wrong was WHICH cell. See §7.4.

### 7.3 Inputs with no box, no projectile and no field

| input | draws |
|---|---|
| Mizu · ground Special up | `gsup` |
| Tsubasa · ground Special neutral | `special` |
| Ember · ground Special back | `eparry` |
| Kael · ground Heavy back | `kscis+xparry` |
| Kael · ground Heavy up | `kscis+xparry` |
| Kael · ground Special back | `kscis+xparry` |
| Mokurai · ground Special back | `special` |
| Exile · ground Special up | `special` |
| Exile · air Special up | `aneu` |
| Oni · air Special back | `aneu` |

A genuinely free slot **or** a move whose entire effect is a state change the probe
does not count — a parry, a stance, a teleport, a counter arm. Tsubasa's neutral
Special is his 0.133 s parry and is *supposed* to be empty here. Kael's three
`kscis+xparry` entries are his Niten parry. Check before you fill one in.


---

### 7.4 What 711 and 714 changed

**FIXED — the two held airborne cells were planted stances.**

The air up-poke and the meteor's hang and plunge are the only two things in the game that
**hold one cell** instead of playing a row, which is exactly why the 707 air sweep never
reached them: it walked rows. Their `??` chains ended on `light3` (six fighters), `upatk3`
(Mokurai, a kneeling pose), `ajump4` (Kael, Executioner) and `fall2` — and `fall`, `fall2`
and `ajump4` are the SAME cell on five sheets. Rendered through the runtime keyer and
looked at, every one of them is a **planted standing stance**. Up+Light in the sky drew a
man standing on the floor, and so did every meteor plunge but Oni's.

⛔ **The alpha cannot tell you this.** Every cell is packed foot-anchored, so "lowest ink
versus `footY`" reads 3–5 px for all eighteen and calls an idle and a jump the same thing.
The verdict came from rendering them. This is why `eye_scale` is invalid on packed cells
and why bbox height is banned as a ruler — the same trap, one function along.

| input | 709 drew | 711 draws |
|---|---|---|
| air Light + Up · six fighters | `light3` *(a ground light)* | air row beat 3 |
| air Light + Up · Kael, Executioner | `ajump4` / `fall2` | `kxcut3` / `aneu3` |
| air Light + Up · Mokurai | `upatk3` *(kneeling)* | `bair3` |
| meteor hang · eight fighters | `fall2` / `ajump4` / `bjump4` / `xjump4` | air row beat 1 |
| meteor plunge · eight fighters | `fall2` / `ajump4` / `bjump4` / `xjump4` | air row beat 4 |
| meteor · Oni | `dive1` / `dive3` | unchanged — his drawn dive row wins |

Still **one committed pose per phase** — that part of the meteor's design is untouched.
Only which cell. One shared helper, `airPose(F, beat)`, next to `airAttackCells`; a
`ponytail:` comment marks the one shared beat per use as the deliberate simplification and
names the upgrade path (a per-fighter beat map) if the owner wants specific poses.

Gated by **`tools/check_air_held_poses.mjs`** — 27 assertions, all nine fighters, each held
cell asserted to be a member of `airAttackCells()` or of a drawn dive row. Driven through
`executeAttack`, not hand-set: `spriteFrameIndex` returns `xidle` for a Player that is not
actually mid-move, so a synthetic `slamPhase` proves nothing.

Five more rows moved in the same window from the co-tenant lane's audit — Executioner and
Shin air Heavy neutral now reach `hneu`, Oni reaches `hfwd`/`hup`. **22 of the 270 inputs
changed between 709 and 711.**

**DONE at 714 — the 12 rows were ported.**

Every one of the twelve missing `DIR_MOVES` art rows was packed on
`SHADOWCLASH-RECOVERED`, so this was a port of already-approved art, not a generation.
**80 cells appended across five sheets**, raw pixels (the engine keys at draw time, so
keying on the way in keys twice), pre-existing region `AE=0` on all five.

| fighter | rows | how | reads against the SHODO look |
|---|---|---|---|
| Mizu | `bothrust`, `staffspin` | verbatim | same character, same ink — clean |
| Tsubasa | `eflick` | verbatim | clean |
| Ember | `clawrend`, `lowrake`, `eretreat` | verbatim | fine at game scale |
| Oni | `ghback`, `ghdown` | verbatim | fine at game scale; checked against the Aug 9 bible before packing — white mask, red slits, two horns, swords on the back, no purple, no mane. Current founder design, not the purged one. |
| Shin | `ghfwd`, `ghback`, `ghdown`, `ghup` | **×0.72** | ⚠ **colour break** — his RECOVERED art is a saturated green ninja against SHODO's mossy eroded one, and that reads at any size |

**Scale: only Shin, and only because his rulers agree.** On `idle2`/`xidle1` his three
independent measures land together (√area 0.70/0.74, bbox width 0.67/0.78, bbox height
0.74/0.71). For Mizu, Tsubasa, Ember and Oni the same three **conflict** — height says
~1.0 while width says 0.60–0.81, because bbox width is contaminated by weapon angle and
area by pose, and the eye ruler is unvalidated on every fighter but the Executioner.
Resampling on a guess throws away pixels you cannot get back, so those four are verbatim.

**Shin's colour was NOT corrected**, deliberately: colour-correcting a packed cell is
banned here — a 300 px cell has no colour headroom, and the one attempt flattened 1,852 px
of legitimate armour to black. The fix is the owner's generator redrawing those four rows
in the shodo treatment, not a homemade approximation. Reverting any row is a JSON edit;
the cells stay addressable.

**And the dead tracks went with it.** `check_dir_moves` reported 11 silent failures —
eleven entries still carrying six-stop timing from when those rows were six cells, so the
tracks had been discarded in silence for their whole life. Deleting them is a proven no-op
(the probe returns byte-identical rows before and after). The 709 note claiming `8:up`
keeps its track was stale; `ghup` is eight cells now. **`check_dir_moves` is GREEN for the
first time: 22 moves, every track matches its cell count, every art row exists, every
launcher carries an impulse.**

**709 → 714: 34 of 270 inputs draw something different** — 22 air, 12 rows.
`gate_fragments` CLEAN on all five ported sheets; `check_air_held_poses` 27/27.

Frames for every row: https://claude.ai/code/artifact/5cb6642d-a73a-4b55-99f3-00387768d38d

---

## 8. Reproduce everything in this document

```bash
python3 tools/serve.py 9101 web            # if :9101 is not already up
curl -s 127.0.0.1:9101/whoami              # confirm tree + SHEET_V before trusting anything
PORT=9101 node tools/moveset_probe.mjs          # all nine fighters, 30 inputs each
PORT=9101 node tools/check_air_held_poses.mjs   # the 27 held-pose assertions
node tools/movelist.mjs --name oni         # one fighter, verbose
node tools/check_dir_moves.mjs             # DIR_MOVES / DIR_SPECIALS routing
node tools/check_air_no_ground.mjs         # no ground frame plays in the air
node tools/check_kick_rows.mjs             # kick-tier routing
python3 tools/audit_move_coverage.py       # dead-input census
python3 tools/sprites/gate_fragments.py    # fragment shortlist, all nine
python3 tools/sprites/check_row_scale.py   # per-row scale spread
python3 tools/sprites/eye_scale.py         # eye ruler
```

**Verify on the tree that is actually being served.** `/whoami` first, every time — this
project has four builds and `:9100` is a *different* tree at a *different* SHEET_V.

If the probe output changes and you did not intend it to change, you broke routing.
