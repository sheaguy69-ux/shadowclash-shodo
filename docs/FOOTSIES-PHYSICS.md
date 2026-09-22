# Footsies physics and authored moves — 2026-09-07

Executioner's base Forward+Light is **Shadow Slice**, and base Forward+Special is **Smoke-Bomb Shadow Strike**. The runtime reads both move definitions from the embedded `footsies-data` JSON in `web/index.html`. Reverse-grip commands keep their existing kit.

## Exact timing convention

Frames mean **60 Hz game time**, not wall-clock/render frames. The existing `COMBAT_TEMPO = 1.2` remains active; the existing cinematic hitstop slows gameplay clocks to its crawl rate. A nine-frame move lasts 0.150 game seconds / 0.125 wall seconds without hitstop. A sixteen-frame move lasts 0.266667 game seconds / 0.222222 wall seconds. This is the existing seconds-based engine; it has not been migrated to fixed-step simulation. The exporter samples `updateGame(1 / (60 * COMBAT_TEMPO))` to expose every authored frame.

| Move | Startup / active / recovery | Clean-hit cancel frames | Base damage | Hitstun |
|---|---|---|---|---|
| Shadow Slice | 2 / 2 / 5 | 3, 4, 5 | 28 | 14 game frames |
| Smoke-Bomb Shadow Strike | 6 / 3 / 7 | 8, 9, 10 | 55 | 22 game frames |

Both allow jump, Shunshin dash and Special during their clean-hit windows. A block or whiff does **not** unlock these authored cancels. Ordinary existing Light → Medium/Heavy → Special confirms still allow immediate cancels on hit **or block**. Smoke Strike has 12 game frames of blockstun; frames 3–4 have no hurtbox and are invulnerable. It books one nearby crossing, reappears, and drives forward on frames 5–7; distant targets can whiff and arena boundaries clamp travel. Every active window deals at most one hit per victim through the existing shared collision path.

Damage numbers are **base combat damage**, not promises of identical HP loss against every character. Defender defense, combo scaling, Exile's fragility, stance damage taken and the existing `HEALTH_DAMAGE_SCALE = 0.70` still apply. Against unmodified Kael at the start of a combo, 28 base damage removes 19.6 HP and 55 removes 38.5 HP. The authored attacks bypass attacker power/reach/hasuji inflation; unrelated attacks retain their existing balance.

## Shared physics

- The author's up-positive gravity `-22` maps to screen-down `+2200 px/game-second²` at 100 pixels per velocity/gravity unit. The same conversion maps Slice's base hit velocity to `(350, 0)` and Smoke Strike's to `(500, -400)`, mirrored by facing. Smoke's self-drive is `1600 px/game-second` during frames 5–7.
- Doubling the old 1100 gravity without adjusting takeoff halved jumping height and broke ceiling/wall routes. Normal and wall takeoffs therefore use `oldLift * sqrt(GRAVITY / 1100) + (GRAVITY - 1100) / 120`; the final term compensates the half-step height loss of the existing semi-implicit integration. Jump rankings and prior reach remain, with shorter flight time. At 60 Hz game-time sampling, ordinary peak rise is about 144.7 px, Exile 182.1 px and Oni 175.9 px.
- Neutral grounded movement already starts and stops instantly. Shunshin now permits grounded release/reverse braking after a three-frame minimum burst; holding the direction preserves full traversal. Air dashes and rolls remain committed, and Shunshin grants no invulnerability.
- Grounded knockback and attack/recovery drift retain `0.92 ** (dt * 60)` velocity. This is frame-rate-aware exponential drag. Guard skid retains its existing distinct drag; neutral ground control remains an immediate stop.
- Weight affects launched/air-hit velocities, followed by one input-dependent rotation at impact, bounded by 18 degrees. DI preserves launch speed and does not repeatedly accelerate the victim during hitstun. Grounded ordinary pushback and low sweep trips retain their original forces.
- Neutral aerial Light cancels on touchdown. Generic hard-drop landing no longer adds control lockout. Directional dives, Heavy, Meteor Break, Bell Toll and other committed attack/knockdown recovery retain their own punish windows.

| Fighter | Relative launch weight |
|---|---:|
| Executioner | 1.30 |
| Mizu | 1.00 |
| Shin | 0.85 |
| Tsubasa | 0.95 |
| Ember | 1.10 |
| Kael | 1.00 |
| Mokurai | 1.25 |
| Exile | 0.80 |
| Oni | 0.90 |

These are gameplay tuning values, not new character lore or physical measurements. Authored target velocities describe the base before applicable weight and DI.

## Checks

`python3 tools/check_footsies_physics.py` exercises both moves' frame boundaries, null-hurtbox invulnerability, damage/contact and cancel windows, real keyboard Smoke Strike near/far/both-facing/wall routes, ordinary hit/block chains, all-nine movement stops/microdash brakes, launch weight/DI, landing commitment and jump ranking.

`python3 tools/check_jump_input.py` retains the existing 72 keyboard/touch cases, 72 arcs, 90 wall cases, 40 training resets and ceiling/jump-budget coverage. Only its two literal old impulse expectations were adapted to the new derived takeoff constants; no trajectory thresholds were relaxed.

Visual approval and exact per-frame collision overlays belong to the separate Agent 2 audit. Existing authored cells are exposed through the shared Shodo renderer; this physics pass creates no new sprite drawings.
