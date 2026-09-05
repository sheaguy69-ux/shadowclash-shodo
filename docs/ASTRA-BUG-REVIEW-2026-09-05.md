# Shodō bug review — 2026-09-05

Target: SHODO-EDITION on :9101, starting commit `114b7c0`, SHEET_V 714.
Scope: input ownership, focus loss, attack startup/clashes, and a roster smoke run.

## Fixed

- **Spectators could control CPU fighters.** The existing combat-key gate missed keyboard/touch dashes and direct mouse/webcam movement. Watched teams/brawl also omitted P1 from CPU classification, letting attack buttons through and denying P1 its CPU blade-lock mash clock. Reused the existing ownership checks at these input boundaries. Mouse/webcam steering no longer overrides CPU steering. Human P1 and P2 training/touch controls remain available. The live reproducer initially found **26 unauthorized actions**.
- **Weapon clashes fired during startup.** `processWeaponClash` ran before `processHitboxes`, but never checked either hitbox's delay. Overlapping windup boxes immediately consumed both attacks and entered a lock. Both participants must now be active. Three startup combinations failed before the fix; active/active remains valid. No damage, startup duration or balance constants changed.
- **Focus loss left the physical-key registry held.** Blur cleared `keys` but not `physKeys`; watch-mode cleanup could then preserve CPU residue as supposed human input. The shared blur/tab-hide release now clears both registries.

## Verification

- `PORT=9101 node tools/check_seat_gate.mjs`: **169 cases, no ownership leaks or errors**. Includes fresh fighters per button, real keyboard/touch event listeners, mouse/webcam callbacks, CPU steering, human P2 touch guard and blur cleanup.
- `node tools/blade_lock_check.mjs`: **88 passed, zero failed**, testing the actual extracted game function.
- `node tools/drive_real_input.mjs --all`: **648 attack inputs, no dead inputs or errors**.
- `PORT=9101 node tools/check_jump_commit.mjs`: **36/36 attack commitments and 36/36 escape routes passed**.
- Actual :9101 browser: a delayed hitbox returned `clashed=false`; after activation, `clashed=true` and both lock timers were 1.15s.
- Nine short CPU matchups covering the roster: no captured JavaScript exceptions, finite positions and damage observed. Sampled screenshots were inspected with the game fitted in view. Capture ran below the requested rate, so this is a gameplay smoke check, **not consecutive-frame animation approval or a full-match endurance test**.
- JavaScript test syntax and `git diff --check` passed.

Evidence: `media/astra-bug-review-20260905/` (local review artifacts).

## Open review findings — not a clean bill for the whole game

- The older `audit_runtime.mjs` stops at its assumption that every weapon clash produces at least 115ms hitstop. A grounded bind now returns before that recoil path; the new targeted test verifies the actual bind. Later assertions in that old audit were not reached.
- `check_air_art_holds.mjs` still reports **19 air-to-land art transitions** (9 Medium, 9 Special, Kael Heavy). Commit `440b3ae` explicitly documents four Special transitions as intentional. The remainder needs fresh-input and visual validation; this check reuses fighter state and manually changes the floor flag. No animation routing was changed on the strength of these counts.
- The handoff's size-fix revert, missing/borrowed artwork, orphan stripping, publication exclusions and canonical-tree choices remain unchanged. No sprite bytes, manifests, art approval states, SHEET_V, push, merge or deployment changed.
