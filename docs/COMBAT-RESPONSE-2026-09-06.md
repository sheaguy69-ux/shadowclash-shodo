# Combat response — September 6, 2026

Local SHODO-EDITION/:9101 upgrade, requested by Anthony. An attack pressed during the final 133 ms of simulation-time recovery (about 111 ms at the existing 1.2x tempo) now survives stun, roll recovery and stance-lock recovery. Commitments are retained. Earlier presses expire; retrying no longer refreshes the deadline indefinitely.

The queued press carries the complete stick snapshot, including diagonals, through normal, command and special dispatch. Releasing the stick cannot substitute a different move. A rejected/buffered attack no longer clears Executioner's current thrust latch. Grab, vanish, throw and blade-lock exclusions remain. New damage still clears old queued offense.

Validation: `python3 tools/check_combat_buffer.py` reproduces 357 failures before the change and passes after: 324 released-direction commands, 54 recovery/expiry cases, nine stale-press cases, one thrust-continuity case. These use DOM attack events and the real actor update, with controlled recovery gates. `drive_real_input.mjs --all` passes 648 cases in each of normal and MODE2; `check_jump_commit.mjs` passes 36 commitments and 36 escapes; combat-tempo check passes. Three actual consecutive rAF captures show Executioner, Mizu and Ember finishing Heavy and starting a queued down+Medium. Evidence: `media/combat-buffer-20260906/`.

This changes input acceptance, not damage, combo hierarchy, attack durations, sprite art or simulation speed. It does not claim improved rendering FPS. Approved Ember idle integration and the subsequently requested athletic jump-art pass are separate work.
