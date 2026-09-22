# Owner-directed roster balance — 2026-09-07

Implemented locally in SHODO-EDITION on :9101. No commit, push or deployment. The concurrent Oni gait/art pass moved the shared cache version from749 to750; these changes concern combat values only.

## Roster values

| Fighter | Speed /10 | Power /10 | Defense /10 |
|---|---:|---:|---:|
| Executioner | 3.5 | 9 | 8 |
| Mizu | 7.5 | 6 | 5 |
| Shin | 9 | 4 | 4 |
| Tsubasa | 8 | 6.5 | 7 |
| Ember | 8 | 7 | 8 |
| Kael | 7.5 | 6 | 6 |
| Mokurai | 5 | 7 | 8 |
| Exile | 10 | 5 | 3 |
| Oni | 9.5 | 10 | 6 |

Speed order is Exile > Oni > Shin > Tsubasa = Ember > Kael = Mizu > Mokurai > Executioner. These are base movement ratings; move-specific recovery, lunges and specials retain their individual properties. Oni now has the highest base power and stronger neutral Light/Medium/Heavy damage than Executioner. Executioner remains strongest among the original six and the slowest runner. Conditional finishers and utility specials are not required to have the same damage ordering as basic attacks.

## Changes

- Removed Oni’s obsolete2.2× swing-duration multiplier. Neutral Heavy commitment dropped from44 to20 sampled60 Hz game ticks, with the existing attack poses/contact still present. His measured movement is554.17 px/game-second, between Exile583.33 and Shin525.
- Medium attack animation/startup now follows the existing recovery-speed divisor. Exile/Oni/Shin neutral Medium commitments are21/22/23 ticks instead of all34. Existing active-window/recovery floors remain.
- Tsubasa speed7→8 and power6→6.5; Kael speed6→7.5; Mizu speed6→7.5 and power5→6.
- Ember keeps speed8/power7; shared hitbox creation scales Light/kicks by0.8 and Medium by0.9. Heavy and Special retain their current damage so his kit has lighter pressure and stronger commitments.
- Shared health conversion now applies defense, Exile fragility and stance damage modifiers to normal hits, guarded chip, armor and throws. Exile’s total base factor is exactly1.25, replacing1.09×1.25. A20-raw normal hit costs17.5 HP instead of19.075; a12-raw throw costs10.5 HP. Champion’s inactive-mode formula retains defense1.09.
- Ordinary guard gets4/6/9/12 game-frame blockstun for Light/Medium/Heavy/Special, with authored blockstun overriding defaults. Guard spends25% of incoming raw damage as stamina; it cannot absorb the next hit at zero stamina. Defense now affects chip. Existing exhaustion, chip fractions, knockback, parries, throw rules, combo scaling and armor stagger immunity remain.
- Shin’s neutral flying kick limits its initial lunge at close spacing so he does not pass the opponent before its active window. It still connects at70/140 px and now connects at20 px.

## Verification

- `python3 tools/check_roster_balance.py`: strict movement/power ranking; all-nine normal/armor/throw/guard damage; exhausted guard; invulnerability; combo scaling; dormant stance consistency;54 Shin kick cases (nine defenders, both facings, three gaps). PASS.
- Existing combat-tempo checks:9 movement/clock cases,36 attack recoveries and long-frame cap. PASS.
- Existing combat-buffer checks:324 released-direction presses,54 recovery gates,9 expirations and thrust continuity. PASS.
- Existing attack-route checks:40 routes×65 simulation samples, both directions, approved contact frames present. PASS. Oni neutral-heavy contact strip inspected.
- Repeated audit capture:1,080 attack configurations (648 base plus432 forced diagnostics),120 defense samples,108 neutral collision trials and106 supplemental checks; no attack/defense/contact runtime errors. Forced modes remain diagnostics only because FIRST_FORM_ONLY still gates their input.

Evidence: `media/combat-balance-fix-20260907/` contains before snapshot, JSON traces, test logs and focused regression output. The original audit remains under `media/combat-balance-audit-20260907/`. This is verified local tuning, not a claim of tournament balance or exhaustive matchup/combo coverage.
