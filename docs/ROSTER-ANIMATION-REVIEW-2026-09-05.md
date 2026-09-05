# All-nine animation review — SHODO-EDITION :9101

Anthony authorized the full roster pass and explicitly waived repeated image approval. No sprite assets, weapons, baked effects, exposure tracks or combat timing changed.

## Repairs

Four rendering guards repair 14 observed landing snaps:

- Medium checks the press-time airborne latch as well as the live floor flag. All nine fighters finish their airborne animation instead of switching to medium1..N on touchdown.
- Executioner's two Chudan Light branches respect that latch too: airborne Medium falls through the Light renderer, so the stance must not steal its remaining animation after the first fix.
- Generic airborne Specials keep their existing air row through recovery. This fixes Executioner, Mizu, Ember, Mokurai and Exile.
- Shin, Tsubasa, Kael and Oni retain their documented sneu landing phases. That earlier branch is unchanged. Three are observed active at touchdown here; Shin's sampled Special finishes before landing.

| Fighter | Medium landing | Special landing |
|---|---|---|
| Executioner | Fixed, including Chudan fallback | Fixed |
| Mizu | Fixed | Fixed |
| Shin | Fixed | Intentional route preserved |
| Tsubasa | Fixed | Intentional phase preserved |
| Ember | Fixed | Fixed |
| Kael | Fixed | Intentional phase preserved |
| Mokurai | Fixed | Fixed |
| Exile | Fixed | Fixed |
| Oni | Fixed | Intentional phase preserved |

Kael's earlier Heavy landing repair remains in place. Run starts/stops and grounded recoveries were visually inspected for all nine; no additional routing defect was established in those captures.

## Verification

`node tools/capture_roster_transitions.mjs --check-landing` exercises nine fighters × four strengths through real DOM key events and the live animation loop. Each fresh match captures idle/run, run/idle, ground attack startup/recovery, airborne startup and touchdown. Each strip contains eight consecutive ticks, using the real sprite renderer in an isolated view. These are not OS keyboard tests or a complete audit of every directional move and artwork cell.

Before and after: 36 scenarios, 216 strips and 1,728 captured transition frames each. The targeted comparison finds 14 faulty landing cases before and zero after. All 36 after scenarios pass without captured JavaScript errors. Tsubasa's grounded neutral Special is a parry; the capture records PARRY_STANCE rather than falsely requiring ATTACK_SPECIAL. Light attacks in this trajectory finish before touchdown, so the continuity assertion targets Medium and generic Specials that actually straddle landing.

Executioner's Chudan Medium regression fails before and passes after; all four Chudan strengths then pass the capture. Reproduce with `CHUDAN=1 NAME=executioner AIR_FRAME=171 OUT=media/chudan-check node tools/capture_roster_transitions.mjs --check-landing`. NAME and TIER narrow a capture; OUT separates evidence.

`node tools/drive_real_input.mjs --all`: 648 directional/input probes pass; MODE2=1 repeats all 648 successfully (1,296 total). The older `check_air_art_holds.mjs` exits 1 for exactly the four documented intentional Special landing transitions; its blanket verdict remains unsuitable as a zero-failure gate. The new live-loop regression distinguishes those phases. Node syntax and diff checks pass.

Evidence: `media/roster-animation-review-20260905/{before,after}/<fighter>/<tier>/`, each with trace.json and six filmstrips. `comparison.json` lists the 14 before failures. `inspection/` contains all-nine locomotion and ground-recovery review boards. Chudan evidence is in `chudan-before/` and `chudan-after/`.

This is a routing and transition review: no new cell generation, resizing, packing, keying or claims of new artwork QC approval. Existing drawings provide the poses and effects. The earlier renderer cache still reduces repeated work; cold first-use hitches remain outside this repair.
