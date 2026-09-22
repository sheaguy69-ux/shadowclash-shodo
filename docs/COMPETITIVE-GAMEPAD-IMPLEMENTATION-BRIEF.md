# Shadow Clash — Competitive Gamepad and Gameplay Improvement Brief

**Review baseline:** SHODO-EDITION, branch `shodo-edition`, commit `95d455e`, `SHEET_V = 685`  
**Prepared:** 2026-09-02  
**Audience:** Anthony, Claude Code, and any developer implementing the next gameplay pass  
**Status:** Review and implementation instructions. This document does not approve new canon, generated art, spending, or a gameplay rewrite.

## 1. Executive decision

Shadow Clash already has a substantial combat system. It does not need more mechanics before it needs cleaner access to the mechanics already present.

The next implementation should be split into small, testable passes:

1. Complete gamepad combat parity, especially the missing Medium input.
2. Make the menus usable without touching a keyboard or mouse.
3. Improve competitive readability and create a stable 1v1 ruleset.
4. Add training measurements before changing global balance.
5. Finish the existing story/cutscene route only after normal players can enter it.

Do not combine these into one large rewrite. The keyboard input funnel already handles attack timing, hitstop buffering, throws, stance actions, rolls, variable jump height, and P2 seat rules. Gamepad support should continue to translate controller actions into that existing path.

## 2. Current-state review

### What is already strong

- Four attack strengths are implemented: Light, Medium, Heavy, and Special.
- The combat system includes hit-confirm cancels, block/chip, throws, Kawarimi, chakra management, rolls, Shunshin movement, wall interactions, pogo attacks, stagger/free escape, weapon clashes, blade locks, knockdowns, launches, and character-specific kits.
- Gamepad polling already supports two standard-mapped controllers, D-pad movement, left-stick movement, a `0.4` dead zone, press/release edges, disconnect release, guard, throw macros, stance, and pause.
- All input methods are intended to enter combat through `pressCombat()` and `fireCombatKey()`. This is the correct architecture and should remain the single source of combat-input behavior.
- The cutscene overlay, typewriter, advance, skip, simulation freeze, and fight handoff are already implemented.

### Highest-impact problems found

| Priority | Finding | Player impact | Required response |
| --- | --- | --- | --- |
| P0 | Gamepad has no Medium action in `PAD_KEYS` or `PAD_BUTTONS`. | Controller players cannot use the complete combo hierarchy. | Add Medium without creating a new attack path. |
| P0 | Touch, mouse, and hand-control paths also omit Medium. | Different devices expose different movesets. | Fix after the controller patch; do not bury gamepad work in that larger change. |
| P0 | Gamepad controls combat but does not provide complete controller-only menu navigation. | A player still needs a mouse/keyboard to configure and start many matches. | Add a focused menu-navigation pass after combat parity. |
| P0 | The permanent controls sidebar narrows the arena, and fighters read small against the background. | Spacing, startup, and punish distance are harder to judge. | Hide the sidebar during a match and tighten the 1v1 presentation. |
| P0 | Ordinary hits can trigger a very large white/invert wash. | Impact is strong, but moment-to-moment information is obscured. | Reserve full-screen treatment for major events. |
| P1 | The simulation uses variable `requestAnimationFrame` delta time. | Local play works, but deterministic replay, rollback, and reliable frame analysis are not ready. | Move to fixed 60 Hz simulation only when replay/online work begins. |
| P1 | Training lacks input history, frame advantage, hitbox display, and configurable defense/wakeup behavior. | Balance decisions depend on feel instead of repeatable evidence. | Add a small competitive training HUD before broad balance changes. |
| P1 | Story code exists, but there is no normal `data-mode="story"` selection button. | The implemented cutscenes are not reachable through the ordinary UI. | Wire a Story entry before producing more scenes. |
| P1 | README still describes six fighters and a three-attack layout. | Players and implementers receive stale instructions. | Update it with the controller patch. |

## 3. Recommended standard controller layout

This layout places all four attacks on the four face buttons and keeps defense on the shoulders. Physical positions are authoritative because Xbox, PlayStation, and Nintendo labels differ.

| Action | Physical control | Standard Gamepad API index | P1 keyboard event | P2 keyboard event |
| --- | --- | ---: | --- | --- |
| Move / jump / crouch | D-pad or left stick | D-pad `12–15`; axes `0–1` | `WASD` | Arrow keys |
| Light | South face button | `0` | `KeyF` | `KeyI` |
| Medium | West face button | `2` | `KeyJ` | `KeyU` |
| Heavy | North face button | `3` | `KeyG` | `KeyO` |
| Special | East face button | `1` | `KeyH` | `KeyP` |
| Poof / hold Block | Either shoulder | `4` or `5` | `KeyC` | `KeyM` |
| Throw macro | Either trigger | `6` or `7` | Light + Heavy | Light + Heavy |
| Stance / team swap | Back / Share | `8` | `KeyV` | `KeyK` |
| Pause / skip scene | Start / Options | `9` | `Escape` | `Escape` |

Why this layout:

- Light → Medium → Heavy is physically learnable across the face-button cluster.
- Special remains a distinct face action.
- Holding a shoulder for Block is comfortable while pressing attacks or directions.
- Either shoulder and either trigger support different hand preferences without a settings screen.
- It reuses every existing keyboard behavior, including the Light + Heavy throw timing window.

The existing layout currently uses South for Light, West for Heavy, North for Special, and East plus both shoulders for Poof. Therefore the change deliberately keeps Light in place, moves Heavy to North, moves Special to East, introduces Medium on West, and leaves Poof available on both shoulders.

Do not build custom remapping in this first pass. Add remapping when playtests show a real need or when accessibility/platform requirements demand it.

## 4. Claude Code implementation instructions

### Pass A — complete gamepad combat parity

Work primarily in `web/index.html` around `PAD_KEYS`, `PAD_BUTTONS`, `padHeld`, and `pollGamepads()`.

1. Add `medium` to both `PAD_KEYS` entries:
   - P1: `medium: 'KeyJ'`
   - P2: `medium: 'KeyU'`
2. Change `PAD_BUTTONS` to the recommended layout:
   - `0: 'light'`
   - `2: 'medium'`
   - `3: 'heavy'`
   - `1: 'special'`
   - Keep `4` and `5` as `poof`.
   - Keep `6` and `7` as `throw`.
   - Keep `8` as `stance`, `9` as `pause`, and `12–15` as directions.
3. Preserve edge-only dispatch. A held attack must produce one keydown, not an attack every animation frame.
4. Preserve release dispatch. Releasing Block or unplugging a controller must send the matching keyup so no action remains stuck.
5. Preserve `isP2Human()` gating. A second connected pad must never puppet a CPU opponent.
6. Preserve the standard-mapping restriction in this pass. Do not guess layouts for controllers that report a non-standard mapping.
7. Do not call `executeAttack()` directly from gamepad code. The controller must continue through the synthetic keyboard events and the existing `pressCombat()` → `fireCombatKey()` funnel.
8. Do not alter move damage, startup, recovery, cancel rules, hitstop, or chakra costs in this patch.

### Pass B — controller documentation and visible status

1. Update the in-game controller legend to show both keyboard and physical controller positions.
2. Update `README.md` to describe nine fighters, four attacks, and the gamepad layout.
3. Add a small, non-blocking `P1 PAD` / `P2 PAD` connected indicator on the selection or pause screen. Do not place it over the combat canvas.
4. Use physical names such as South/West/North/East and optionally show Xbox/PlayStation examples. Do not label the layout only as A/B/X/Y because Nintendo labels reverse the physical expectation.

### Pass C — controller-only menus

The game is not fully gamepad-ready until a player can launch it, choose a mode, choose fighters/stage, start, pause, rematch, and return to selection without a mouse.

Implement this as a separate pass so combat parity remains easy to review.

1. Reuse the existing native `<button>` elements, `.focus()`, and `.click()`.
2. When a visible screen opens, focus one sensible default:
   - Title: Quick Play.
   - Selection: current mode, then current P1 fighter.
   - Pause: Resume.
   - Results: Rematch or Next Opponent.
3. Outside active combat, use D-pad/stick press edges to move among visible, enabled controls.
4. Use South to activate the focused control and East to go back where a back action already exists.
5. Never fire combat attacks while a menu owns controller input.
6. Add an obvious focus ring with sufficient contrast.
7. Keep selection rules unchanged: CPU modes choose one player fighter; local 2P chooses both seats; team modes keep their existing pair logic.
8. A first version may retain pad index 0 as P1 and index 1 as P2. Add “press a button to join” seat assignment only if disconnect/reconnect tests show unstable indices or public playtests require hot joining.

### Pass D — remaining input parity

After gamepad combat and menu control are green:

1. Add a Medium button to both touch combat clusters.
2. Add `p1_medium: 'KeyJ'` and `p2_medium: 'KeyU'` to `TOUCH_CODE` and bind both buttons through `bindTouch()`.
3. Decide whether mouse and hand tracking are supported competitive inputs. If yes, provide Medium. If no, label them as experimental/casual instead of implying full parity.
4. Do not redesign the entire touch layout during the controller patch.

## 5. Required controller checks

Add one small no-framework check, preferably `tools/check_gamepad_mapping.mjs`, that loads the real page and mocks `navigator.getGamepads()`. It should fail if any mapping or edge behavior regresses.

### Automated acceptance matrix

- P1 South sends one `KeyF` keydown and one keyup.
- P1 West sends one `KeyJ` keydown and one keyup.
- P1 North sends one `KeyG` keydown and one keyup.
- P1 East sends one `KeyH` keydown and one keyup.
- P2 produces `KeyI`, `KeyU`, `KeyO`, and `KeyP` only when `isP2Human()` is true.
- Holding a face button across multiple polls does not repeat keydown.
- Either shoulder holds and releases the correct Poof/Block key.
- Either trigger sends Light and Heavy during the same poll and reaches the existing throw route.
- Axis value `0.39` produces no direction; `0.41` crosses the current dead zone; returning below the threshold releases the direction.
- D-pad and stick do not leave opposite directions stuck.
- Start pauses and resumes once per press.
- Disconnecting during movement or Block releases every held synthetic key.
- A controller press during hitstop still uses the existing queued-input behavior.
- In team modes, the stance button reaches the existing team-swap behavior.
- During a cutscene, an attack button advances and Start/Options follows the existing Escape/skip behavior.

### Manual controller matrix

Test at least one Xbox-layout controller and one PlayStation-layout controller in Chrome. If available, also test Switch Pro or 8BitDo in standard mode.

For each device, verify:

- Title dismissal and menu navigation.
- Quick Play.
- VS CPU.
- Local two-player with two controllers.
- Training mode.
- Pause, rematch, and return to selection.
- Light → Medium → Heavy → Special routes.
- Guard, roll, Kawarimi, throw, stance, and variable jump height.

### Existing gates that must remain green

Run:

```bash
node tools/kinetics_check.mjs
node tools/check_zero_legacy.mjs
node tools/check_story_cutscene.mjs
```

At the review baseline:

- `kinetics_check.mjs`: pass.
- `check_zero_legacy.mjs`: hard checks pass; 1,412 inked append-only orphan cells remain strip candidates. Do not compact sprite sheets during controller work.
- `check_story_cutscene.mjs`: 14 assertions pass.
- `check_shodo_roster.py`: fails Exile, Tsubasa, and Shin. The measurement is pose-sensitive, so investigate the selected neutral cells/checker assumptions before automatically rescaling art.

## 6. Competitive gameplay improvement route

### Phase 1 — input and readability

Ship these before adding new moves:

1. Complete input parity as specified above.
2. Hide the large controls sidebar while a match is active; move help to pause or an optional overlay.
3. Give the combat canvas the available width and tighten the 1v1 camera so fighter silhouettes, spacing, and attack ranges are readable.
4. Reduce the ordinary-hit full-screen wash. Keep the largest effects for parries, supers, Hasuji, round finish, and KO.
5. Add a clear competitive preset: 1v1, timer on, hazards/ring-outs off, consistent stage bounds, and no CPU control.

Definition of success: two players can sit down with controllers, start a match, understand what hit them, and complete a rematch without touching another device.

### Phase 2 — training evidence

Add only the tools needed to answer balance questions:

- Input history.
- Current move and cancel tier.
- Damage and combo count.
- Frame advantage or actionable-time difference.
- Dummy settings: always block, block after first hit, no block, and wake-up action.
- Optional hitbox/hurtbox display.

Record a compact playtest summary rather than building a full analytics service:

- Average round duration.
- Openings required to win a round.
- Damage per opening.
- Chakra spent and regained.
- Kawarimi/roll escape success.
- Character and stage used.

For the requested faster pace, aim initially for an average round of roughly 25–40 seconds and about 3–5 meaningful openings. Current global values are `MAX_HP = 150` and `HEALTH_DAMAGE_SCALE = 0.70`, reflecting an earlier owner request for longer fights. Do not silently reverse that decision. Test a separate faster preset by changing one dial at a time—for example, keep 150 HP and compare a damage scale around `0.82` against the current `0.70`. Do not lower HP and raise damage simultaneously because the result will not identify which change helped.

### Phase 3 — deterministic foundation, only when required

Do not port or rewrite the game merely to clean up the large HTML file. The current browser build is the playable source of truth.

When replay, frame-perfect tooling, or online rollback becomes an approved goal:

1. Run gameplay simulation at a fixed 60 Hz step.
2. Seed gameplay randomness.
3. Separate deterministic combat state/update code from DOM rendering and audio.
4. Record inputs per simulation tick and prove a replay reaches the same final state.

That is the point to extract a combat module. Doing it before those requirements exist creates migration risk without improving the current match.

## 7. Story and cutscene recommendation

Use the existing data-driven cutscene system. Do not begin with rendered MP4 cinematics.

The next story pass should:

1. Add a visible Story mode entry.
2. Confirm the intended boss-door order. The code currently contains only Exile and Mokurai in `BOSS_TAIL`; Oni is not included.
3. Add the missing rival-intro and epilogue data only after Anthony approves the prose.
4. Correct stale ending descriptions against current canon before recording voice or producing final art.
5. Keep advance, skip, controller input, and simulation freeze working.
6. Add one to three approved stills per important chapter only when the playable story flow is complete.

Recommended responsibility split:

- Claude Code: draft dialogue and continuity against the approved Story Bible.
- Codex: repository integration, live browser verification, state-machine wiring, and regression checks.
- Anthony: final canon, dialogue, boss order, art, and spending approval.

If only one coding agent is used for cutscene implementation, choose the agent that will run and visually verify the current repository build. The largest risk is integration and reachability, not writing more dialogue.

## 8. Definition of done for the gamepad milestone

The gamepad milestone is complete only when all of the following are true:

- Medium is available to both controller seats.
- Every attack reaches the existing input funnel.
- No held-button repeat or stuck-key regression exists.
- Two standard controllers can complete a local match.
- CPU opponents cannot be puppeted by pad 2.
- Menus, pause, results, rematch, and return are controller-operable.
- The visible controller legend and README match the shipped mapping.
- The new gamepad check and existing gameplay gates pass.
- Combat balance and sprite sheets are unchanged by the controller patch.

## 9. Copy-paste task for Claude Code

> Implement the gamepad milestone in `SHODO-EDITION` using `docs/COMPETITIVE-GAMEPAD-IMPLEMENTATION-BRIEF.md` as the specification. First complete Pass A and its no-framework gamepad mapping check. Preserve the existing synthetic-keyboard architecture and route every controller action through `pressCombat()` and `fireCombatKey()`; do not call combat actions directly. Use the specified four-face-button layout, keep Poof/Block on both shoulders, Throw on both triggers, stance on Back/Share, and pause on Start/Options. Then update the in-game legend and README. Keep controller-only menu navigation as a separate reviewable pass. Do not change damage, frame timing, sprite sheets, canon, cutscene prose, or unrelated systems. Run the specified gates and report exact results and any pre-existing failures.

