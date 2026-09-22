# Shodo functionality sweep — September 7, 2026

Local build 744 on `http://localhost:9101/`, in `/Users/anthonyguy/SHADOWCLASH.1.0*2/SHODO-EDITION`. Three subagents separately handled attack direction, Oni commands, and jump/wall behavior. Root integrated their fixes and ran roster-wide controls, combat, CPU and sprite checks.

The recovered game on `:9100` was read only. Existing Shodo drawings, proportions, aura and sound/VFX work were preserved. No sprite PNG changed; this pass corrects routing, metadata, mechanics and instructions. Changes are local and uncommitted alongside the pre-existing worktree changes.

## Repairs

### Attack and movement direction

Corrected 122 source-facing flags across seven manifests. The audit compared drawings with actual active hitboxes and both combat facings, rather than treating every turned head in a spin as an error.

| Fighter | Corrected source frames | Additional result |
|---|---:|---|
| Executioner | 2 | Heavy/air contact direction; rear fallback corrected |
| Mizu | 23 | Special, forward Light and aerial row; rear fallback corrected |
| Shin | 0 | Rear fallback corrected; run/wall direction checks passed |
| Tsubasa | 11 | Medium and Heavy contact cells; rear fallback corrected |
| Ember | 36 | Medium, forward Light/Heavy, air row and ground rip; rear fallback corrected |
| Kael | 32 | Light, Heavy, forward Heavy and air row; rear fallback corrected |
| Mokurai | 0 | Rear fallback corrected; run/wall direction checks passed |
| Exile | 10 | Medium and forward-hitting weapon contact cells |
| Oni | 8 | Air Heavy source row; rear fallback and grounded reverse-wire drawing corrected |

Eight fighters' rear heel attack reused a forward-facing sweep drawing. The renderer now directs that fallback toward its actual rear hitbox, without changing combat facing or globally flipping the shared art. Exile's Back+Light is a separate forward-hitting weapon route; its contact source was corrected separately. Oni's rear wire uses the same narrow correction; bound-wire finishers are excluded so they still face their target.

Intentional windups, wheel kicks, vertical strikes and circular follow-throughs were retained after contact-side review. Runs still face travel, including retreat; attacks retain opponent-relative input direction. Wall clings face the wall, and wall attacks/kicks face away from it.

### Jumps and walls

The old game and previous Shodo build had essentially the same raw jump lift. Larger Shodo character drawings and the faster 1.2 combat clock made those arcs look proportionately shorter. The measured repair raises normal lift 450→570 and wall lift 430→550 while preserving each fighter's jump multiplier and combat tempo.

| Full jump | Before | After |
|---|---:|---:|
| Standard jump height | 88.7 px | 142.7 px |
| Oni jump height | 106.9 px | 172.9 px |
| Exile jump height | 111.1 px | 179.6 px |
| Standard wall-kick rise | 80.2 px | 132.7 px |

Holding a direction now carries the fighter farther during the longer arc. Releasing horizontal input still stops ordinary air travel, as it did in the recovered game. Exile remains the highest jumper.

Two shared input bugs were repaired: releasing Jump before the first physics tick now produces a short hop, and touch release/cancel/sliding off Up now cuts ascent like the keyboard. Holding the same Up touch does not repeatedly cut the jump. Double-jump limits, ceiling release and wall-kick commitment remain enforced.

### Oni

- Removed the obsolete hidden handseal sequence that fired an unrelated launcher without matching art.
- Early Special branches now use the existing 25-chakra affordability, winded and spending rules. Smoke remains free for its first two uses, and paid wire follow-ups are not charged twice.
- A third smoke input now becomes a coherent neutral Special; it no longer draws neutral art while secretly executing the retired ground stomp. The fallback requires 25 chakra.
- Wire contact now follows the 0.10 s approach. Grounded finishers no longer stop short at long range; air finishers no longer coast past the target. Travel ends at a bounded destination and cancels on interruption or reset.
- Removed the extra slowdown intended for a retired 16-frame air-Light row. The current eight-frame neutral and forward rows both take 396 ms.
- Replaced obsolete in-game instructions. Medium is listed; Player 2 sees the correct keys. First-form-only help hides unavailable V/K mode instructions. Shin's wall projectile is correctly labeled shuriken; Exile's is kunai.

The complete input reference is [Oni — current Shodo moves](ONI-CURRENT-SHODO-MOVES.md). New art titles do not imply unimplemented rush, counter, super or independent mastery-mode commands. Those distinctions are explicit in the reference.

### Training reset

R now clears pending inputs, active attacks, dash/roll, wall/grapple motion, projectiles and delayed air-throw damage. It restores two jumps and a coherent grounded state. In abyss training, both fighters reset onto actual starter platforms. Existing fighter objects, round-use caps, gauges and ongoing mode timers are retained.

## Verification and limits

- 648 real attack presses across all nine fighters, versus and training: no dead inputs or runtime errors. Shared art routes were recorded rather than misrepresented as unique drawings.
- 882 consecutive direction snapshots across all nine: run toward/away, stop, cross-up, crouch, guard, both walls, wall release/attack/kick.
- 78 targeted attack-direction cases and 1,064 reviewed render samples, plus both-facing wire-conversion exclusion checks: no wrong-side contacts after correction.
- 324 buffered directional attacks,54 recovery gates, nine expired-input cases and active-thrust continuity.
- 72 keyboard/touch cases,72 jump arcs,90 wall scenarios and 40 actual training-reset cases; ceiling escapes and jump-budget checks.
- 347 focused Oni command checks: resource boundaries, smoke, near/far conversions, moving targets, walls, interruptions and reset.
- 54 gamepad mapping, press/release, dead-zone and CPU-seat assertions.
- 248 blade-lock render samples across 21 armed pairs, wall bounds, live phase progression and CPU outcomes.
-Six wall-projectile scenarios: both walls for Shin, Exile and Oni, including direction, hand origin, ammo, cooldown and landing refill.
-Nine CPU matchups after gameplay repairs:4,320 sampled ticks, all dealing damage, finite positions/resources and no captured runtime errors.
-All nine sheets passed whole-sheet checks. Original PNG hashes are unchanged; manifest differences are exactly the 122 reviewed facing flags.

This certifies the exercised current first-form roster routes and regression scenarios. It does not claim exhaustive proof of every possible input sequence, matchup, archived sprite or disabled second form. Some current moves intentionally reuse approved art; this pass did not invent replacement drawings or new movesets.

Evidence: `media/functionality-audit-20260907/` (roster checks, CPU films, baseline snapshots), `media/functionality-scan-20260907/` (attack contact films, source-orientation maps and Oni results), and `media/jump-functionality-20260907/checks.json`. Focused reusable checks: `tools/check_jump_input.py`, `tools/check_oni_commands.py`, `tools/check_combat_buffer.py`, `tools/check_direction_compass.mjs`.
