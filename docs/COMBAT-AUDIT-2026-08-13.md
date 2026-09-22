# Whole-game combat audit — movement, physics, hitboxes (2026-08-13)

Owner order: *"the thorough review and check on the movements and physics and hitbox of the
whole game"*, then *"apply appropriate fixes"*, then *"fix everything I need to be fixed …
do another sweep double check your work"*.

Six dimensions swept: hitbox↔animation timing, hitbox geometry, frame data, physics, the
state machine, and hurtbox/collision. Every finding below was re-derived from the code by
hand before anything changed, and **every fix was verified against the running engine** —
driven at a fixed 60fps through `updateGame`/`drawScene` with real key state — not by
reading the source back.

---

## Shipped — thirteen fixes

| # | Bug | Impact | Commit |
|---|---|---|---|
| 1 | Hitbox timers aged once per **foe**, not per frame | In 2v2 every startup and active window HALVED; snapped back mid-match when an enemy was KO'd | `a286c7d` |
| 2 | Roll cancelled into a dash kept the roll's **i-frames** | Free invulnerable 800px/s traversal, whole cast | `552001c` |
| 3 | Attacker **paid** on geometric overlap, before the hit could be negated | Dodging fed the attacker's meter | `f6be228` |
| 4 | A box still in **windup** popped decoys | Kawarimi logs and bunshin clones died to a swing that had not started | in `49fdb12` |
| 5 | Oni's smoke read `v.health` (no such property) | Guard never fired; cloud kept hitting a fighter at 0 HP | in `49fdb12` |
| 6 | Human **P2 had no dash and no dodge roll** in tag / teams / brawl | One side played three modes with no movement options | `21db887` |
| 7 | `executeKick` ignored **RECOVERY_TAX** | The Executioner is listed exempt and was taxed anyway — sweep 0.45s instead of 0.30s | in `2294f45` |
| 8 | Mokurai's **PRAYER ORBIT** hit after its own animation ended | Third contact at 1.31× the anim; box also outlived its recovery | in `2294f45` |
| 9 | **Dive boxes were all 30px** — `opts.down` discarded the caller's width | Call sites pass 46/46/48/60; only body-width was ever used | `d19768a` |
| 10 | An **interrupted vault leaked a 2.0s lease** | ~1.25s of dead lockout on top of hitstun, for a slam never performed | `d19768a` |
| 11 | Executioner's **authored tracks never applied** to the live art | Burst hits landed on the wind-up (cells 1,2,2) instead of one cut each | `4a3f494` |
| 12 | The **KICK tier had zero startup** | Box live on the press frame — the only tier exempt from the strike-frame gate | `4a3f494` |
| 13 | A speed buff could shorten recovery **under its own hitbox** | Champion/tag-heat made attacks safe behind a live box | `4a3f494` |

### 1 — hitbox timers per foe (`a286c7d`)
`processHitboxes(attacker, defender, dt)` owns the decay of `h.delay` (startup) and
`h.duration` (active). 1v1 calls it once per attacker. Brawl calls it **once per living
enemy**, so both ticked twice per frame in a 2v2. Ember's launcher is authored at 233ms
*specifically* because the framing audit called a 6f version "a jab-speed surprise" — it
came out in ~117ms. Fixed with an `advance` flag, true only on the frame's first look.
Measured: 14f startup / 19f total with one foe **and** with two (was 7f / 10f).
Check: `tools/check_hitbox_tick.mjs`.

### 2 — roll-cancel i-frames (`552001c`)
`executeShunshin` guarded the roll's *tail* (`rollRecover`) but not the roll.
`handleMovement` resolves grapple → dash → roll, so a mid-roll dash froze `rollTimer`, and
`rollIFrames()` derives the intangible window **from that frozen clock**. Measured before
the fix: `rollTimer` pinned at 0.18 and `rollIFrames()` true for all 10 dash frames.
Contradicts the move's own law ("No i-frames: the body crosses the space and can be
clipped"). Fixed by hoisting the `rollTimer > 0 || rollRecover > 0` pair `executeJump`
already uses; `executeGrapple` got the same sibling treatment the throw path had.
Check: `tools/check_roll_cancel.mjs`.

### 3 — paid for a hit that never landed (`f6be228`)
Three payouts were granted on `overlapX && overlapY` before `takeDamage` ruled: the
Skullgirls cancel window, Oni's wire bind, and the Executioner's DREAD. `takeDamage` holds
the one list of "why did that hit pass through me" (grabbed, vanished, invulnerable, roll
i-frames, Enlightened). A swing the defender **rolled through** still opened a cancel and
still stacked DREAD toward the armored 1.5× EXECUTION — a meter its own comment reserves
for a *clean* heavy. Fixed at the single source: `takeDamage` stamps `hitConfirmed` past
that list. **BLOCK is deliberately still paid** — the on-block chain cancel is documented.
Measured: phased-through → dread 0 / no cancel / hp unchanged; blocked → cancel true, chip;
clean → dread 1.

### 6 — P2 movement (`21db887`)
`TAPS` rebuilt `isP2Human()` as a hand-written `'2p' || 'training'` literal. The helper also
returns true for tag, teams and brawl. That block is the only route to **both** the shunshin
dash and the Guard+direction dodge roll. Verified across all seven modes; cpu/watch still
refuse to be puppeted.

### 8 — PRAYER ORBIT (`2294f45`)
The branch never set `attackAnim.dur`, so the orbit inherited the generic 320ms special
while its third box fires at 0.42s. Measured: contact fraction **1.31** — the spin art had
finished and he had settled to his recovery pose while the last hit was still landing. Now
`dur = 560` (last contact 0.42 + its 0.14 active) and recovery floors at 0.59s, because the
box outlived its recovery (0.56 vs 0.514) and the heavy branch forbids that in as many
words. After: contact fraction 0.75, recovery 0.59.

### 9 / 10 — dive width and the vault lease (`d19768a`)
`if (opts.down)` did `sh = h` (honour the caller's height) and `sw = this.width` (throw the
width away) on the same line; its sibling `opts.up` has always centred the caller's width.
Now they match — measured: down and up both yield a 60px box at ox −15.
Mizu's Up+Special books `recoveryTimer = 2.0` as an airborne lease only the landing hook
collapses, and that hook tests `state === ATTACK_SPECIAL`, which getting hit overwrites with
STUNNED. It now cancels on the line that already interrupts a dash/roll for the same reason.
Measured: interrupted → `vaultAnim` false, recovery 2.0 → 0.5, stunned. Controls hold: a
non-vault special keeps its 2.0, an uninterrupted vault keeps its lease until it lands.

---

## Still open

**Nothing.** Every confirmed finding is fixed. The four that were previously parked here
were closed in `4a3f494`, and the fifth turned out not to be a bug at all:

| was parked | outcome |
|---|---|
| Executioner `slices` / `lowcut` track mismatches | **fixed** — `slices6` / `lowcut6`, derived from the moves' own box delays |
| KICK tier zero startup | **fixed** — light-tier FRAME_DATA ratio on the kick's own 140ms |
| Champion / Chain-Frenzy defeats the recovery invariant | **fixed** — one floor at the tail of `executeAttack` |
| CORNER REACH-BACK "overcorrects" | **not a bug** — measured, the boxes never overlap |

### 11 — Executioner tracks (`4a3f494`)
`attackCellIndex` only applies a track when `track.length === count`, so a mismatch falls
through in silence. `slices` is 7 entries (the 7-cell xlight pump) against the live 6-cell
xcslice row; `lowcut` is 5 against the live 6-cell xsuso row. Both live rows were running on
the generic `ATTACK_EXPOSURES_6`.
Measured on FOUR FAST SLICES (320ms, boxes 0.03/0.06/0.09/0.26s): the three burst hits landed
on cells **1, 2, 2** — the wind-up and the first cut twice. `slices6` is derived off those
same box delays and lands them on **2, 3, 4, 6**, one drawn cut each.
`lowcut6` covers both consumers of the xsuso row — suso-giri at 0.289 and harai otoshi at
0.238 — with cell 3 held 0.23–0.50. Both were landing on cell 2, the wind-up.

### 12 — kick startup (`4a3f494`)
All three kicks spawned with no `delay`: the box was live on the press frame, the one tier
exempt from the strike-frame gate. Startup is the light tier's own ratio against the kick's
own 140ms — 0.32 × 140 = 45ms, ~2.7 frames.

### 13 — the recovery floor (`4a3f494`)
The heavy branch floors itself and says why; every other branch wrote `authored / speedScale`,
and `curSpeed` carries CHAIN FRENZY (×1.2) and TAG HEAT (up to ×1.65). One floor now sits at
the tail of `executeAttack`, against the longest box the swing spawned. Boxes whose active
window exceeds the whole animation are skipped — travelling boxes with their own state
machine (the meteor descent lives 1.2s against a 900ms anim, cleared on touchdown).
**The speed-up is kept**; only the unsafe tail is closed. Measured: 1.5× → 0.30 untouched,
1.8× → 0.25 still quicker, 6.0× → clamped to 0.2386 (box + 0.03) where unfloored was 0.075
against a box living to 0.209. Check: `tools/check_recovery_floor.mjs`.

## Rejected after checking — do NOT "fix" these

- **"CORNER REACH-BACK overcorrects — an 8px band lets a both-sides move hit twice."**
  Measured off the real `spawnHitbox`: facing right the front box spans [22, 90] and the
  behind box [−60, 0]; facing left, [−60, 8] and [30, 90]. **They never touch, in either
  facing.** The reach-back does exactly what it documents. Third false confirmation.
- **"Boxes are 3–9× longer than the drawn weapon."** Measured true (Mizu's box 67px vs 12px
  of drawn reach) and **intentional**: the slash FX carries the visual reach — *"two or three
  cells plus one big arc reads as a full swing"* — and box and arc scale off the same
  `reach/6`.
- **"Blade-lock mash is a ReferenceError."** False. `const p2Live = isP2Human()` is declared
  well before its uses. The automated verifier confirmed this one **wrongly**.
- **"Shin's Wire-Step throws a TypeError."** Not reproducible — `this.opponent` and
  `clampLandX` both exist, and executing the branch threw nothing. Also a wrong confirmation.
- **"Bunshin tested before the real body."** Sanctioned by the comment — eating the hit is
  the decoy's job.
- **Fighters render invisible after Mizu's special.** Correct: a mist field hides its own
  owner (`alpha = 0`, `hiddenInSmoke`). Cost me a detour; noting it so nobody "fixes" it.
- **Synthetic keypresses get wiped every frame.** Correct: the attract-demo scrub skips any
  key in `physKeys`, so a real player's input is never touched. Only a *synthetic* key is
  scrubbed. Good defensive code.
- **Crouch hurtbox** — correct. `hurtTopY()` drops the top to 60% on crouch and roll, and
  both the melee overlap and the projectile check read that one definition.
- **Physics integration** — sound. Semi-implicit Euler (velocity before position), `dt`
  clamped both ways in `gameLoop`, terminal velocity capped, asymmetric jump gravity
  documented.
- **Hitbox delays** — swept all 18 moves that set `attackAnim.dur`. Every delay lands between
  0.16 and 0.61 of its animation; nothing fires on frame 1 or after the move ends.

---

## Measured baseline (for the next audit)

    GRAVITY 1100 · TERMINAL_VELOCITY 1000 · jump vy -450 · body 30x48
    GROUND_Y 890 (per-board; BASE_GROUND_Y 890 against BASE_H 1000)
    moveSpeed = 350*(speed/6) · apex 92px (1.92x body) · airtime 0.82s
    Exile jumpScale 1.12 -> apex 115.5px, airtime 0.92s
    DASH 800px/s x 0.15s = 120px · ROLL 430px/s x 0.28s = 120px
    generic light box 40*(reach/6) · heavy 60*(reach/6)

⛔ `GROUND_Y` is **890 and per-board**, not the 440 an older pass recorded. Anything that
hard-codes a floor value is wrong.

Drawn weapon reach beyond the body, screen px (light / heavy): executioner 38/25 ·
exile 32/25 · oni 38/21 · ember 20/12 · kael 16/19 · mokurai 14/16 · mizu 12/11 ·
shin 11/10 · tsubasa 9/12.

## Running the game to check this yourself

The browser pane reports `document.hidden`, so `requestAnimationFrame` never fires there and
a match sits frozen on ROUND 1 under synthetic input. To verify in-pane, drive the loop
directly — `updateGame(1/60)` + `drawScene()` per frame, and add held keys to **both**
`keys` and `physKeys`. For real play, open `http://localhost:9100` in an actual browser
window (`python3 tools/serve.py 9100 web`).

Checks: `tools/check_hitbox_tick.mjs`, `tools/check_roll_cancel.mjs`,
`tools/check_recovery_floor.mjs` (node, no deps).
Sprite tools: `tools/sprites/ground_audit.py`, `tools/sprites/floor_proof.py`.
