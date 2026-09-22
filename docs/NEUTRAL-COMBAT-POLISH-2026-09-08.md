# Neutral combat polish — 2026-09-08

Local :9101, cache750. Scope: neutral grounded Light, Heavy and Special for all nine fighters.162 sequences cover27 moves × both facings × whiff/hit/block. Final capture is from one unchanged source version. Existing artwork only; no PNG/manifest edits, commit or deployment.

## Implemented

- Executioner neutral Light/Heavy/Special now use the shared collision-synchronized contact-pose renderer. Previously the blade had withdrawn or the fighter was standing still while the hitbox remained live. Contact stays on xnuki4/xjodan4/xtsuki2 and geometry follows that drawing. Authored forward footsies moves retain their own timelines.
- Tsubasa neutral Heavy now chambers using the approved light1 drawing, then extends heavy1 for contact and uses heavy2 for recovery. Previously it began fully extended. Damage and commitment unchanged.
- Shin and Ember neutral Heavy contact now uses hneu6/eheavy6. The generic middle-frame selection had chosen compression/windup art and left the visible impact for recovery.
- Oni Heavy now uses hfwd5/hfwd6 for contact, replacing the overhead-preparation frame previously active at release. Power10, movement9.5 and the faster Heavy commitment are preserved.
- Mokurai and Exile grounded neutral Specials receive4/60 game-seconds of authored hitbox delay, exposing their existing preparation drawings. In the discrete live capture their first active/contact boundary moves fromF1 toF7 due to the resolver’s boundary order. Damage, active durations and total commitment remain unchanged. This small anticipation is not advertised as human-reactable by itself.

## Measured frame advantage

Numbers are defender-ready minus attacker-ready in60 Hz game-time samples, from the actual contact. Positive means the attacker recovers first. Each cell is **on hit / on block**, right-facing close fixture. Cinematic hitstop crawl is bypassed. Most opponents are Executioner; Executioner’s opponent is Mizu, matching the exporter fixture. Therefore this is not a same-defender damage ranking. CSV includes both facings and positions/contact samples are in the full JSON.

| Fighter | Light | Heavy | Special |
|---|---:|---:|---:|
| Executioner | +17 / -7 | +17 / -11 | +10 / -16 |
| Mizu | +16 / -5 | +20 / -2 | utility |
| Shin | +17 / -3 | +18 / +0 | +10 / -6 |
| Tsubasa | +17 / -4 | +21 / -1 | utility |
| Ember | +17 / -4 | +22 / -1 | +7 / -9 |
| Kael | +16 / -5 | +20 / -2 | +13 / -4 |
| Mokurai | +11 / -11 | +10 / -13 | -7 / -25 |
| Exile | +17 / -3 | +20 / +0 | +4 / -13 |
| Oni | +21 / -3 | +28 / +0 | +10 / -4 |

This table preserves the original cache750 snapshot. Mokurai's later palm correction gives +1 to +4 on an uncharged hit and −17 on block; the follow-up matchup report below records the current values and full-Karma results.

Mizu’s mist and Tsubasa’s parry deliberately deal no unprovoked damage. Negative block advantage is a timing opportunity, not proof that a punish reaches through pushback. Positive hit advantage is not automatically a guaranteed combo. No AI/human win-rate conclusion is made.

## What still needs matchup/art work

Neutral artwork closeout completed: seven new eight-drawing rows plus four targeted existing-art replacements. Fresh162sequences/4,922frames, independent review and wall/strike/balance checks pass. See `media/neutral-art-closeout-20260908/REPORT.md`. Remaining matchup work below is separate from art.

- Executioner neutral Special now has eight approved straight-thrust drawings; original343 cells preserved,16 route checks and independent8/10 passed. See `media/executioner-neutral-special-art-20260908/REVIEW.md`.

- Exile neutral Special now has eight approved sickle body drawings, preserving the existing orbit. Original414 cells preserved;20 captures and independent8/10 review passed. See `media/exile-neutral-special-art-20260908/REVIEW.md`.

- Mokurai neutral Special now has eight approved palm drawings in local759. Original388 cells preserved;16 route captures and independent8/10 review passed. See `media/mokurai-neutral-special-art-20260908/REVIEW.md`.
- Resolved: Mokurai's calm neutral Special recovery is now 0.60s after actual reach tests proved every fighter could jab-punish an uncharged clean hit. Final 1,728 cases give +1 to +4 on uncharged hit, +9 to +15 at full Karma, and −17 on block. No tested clean-hit punishment remains; blocked palms stay punishable. Startup/damage/active time and other moves are unchanged. See `media/mokurai-palm-matchups-20260908/REPORT.md`.
- Resolved in local build752: Shin’s approved compact flying-kick art now supplies eight dedicated neutral Special drawings. Original385 cells preserved;16 route captures,54 kick matchup checks and independent8/10 neutral visual review passed. See `media/shin-flying-kick-art-20260908/REVIEW.md` for evidence and limitations.
- Tsubasa neutral Heavy now has eight approved drawings in local build754, preserving timing and damage. See media/tsubasa-neutral-heavy-art-20260908/REVIEW.md. Oni’s neutral Special now has eight approved Cursed Burst drawings in local755, with corrected rear coverage/hand geometry/outward push; front damage and timing preserved. See media/oni-neutral-special-art-20260908/REVIEW.md.
- This pass does not cover all directional/air/wall attacks, every matchup, counter activation, combo/cancel routes or network play.

## Validation and review

- `python3 tools/check_neutral_combat.py`:162 sequences, expected contact poses, preparation, successful offensive hit/block contact and full readiness capture. PASS.
- Existing roster-balance regression: hierarchy, defense paths, guard, combos and54 Shin kick matchup/spacing checks. PASS.
- Existing combat-buffer regression:324 released-direction presses,54 recovery gates and9 expirations. PASS.
- Existing footsies regression: both authored moves/25 frames/both facings; hit/block/cancels;8 Smoke near/far/wall routes; nine-roster physics. PASS.
- Reviewed contact montages for all27 right-facing moves and mirrored corrected examples. Full consecutive frame strips, per-frame transforms/boxes, source hashes and scene strips are saved. These are held-source-pose corrections, not a claim of new animation drawings or independent full-art approval.

Final capture: 4,922 sampled frames. Evidence folder: `media/roster-footsies-20260907/neutral-final-20260908/`. Baseline: sibling `neutral-20260908/`. Frame table: `media/neutral-combat-pass-20260908/frame-advantage.csv`. Replay: `python3 media/neutral-combat-pass-20260908/capture.py`, then the check above.

## Corrected contact strips

Executioner heavy
![Executioner heavy](</Users/anthonyguy/SHADOWCLASH.1.0*2/SHODO-EDITION/media/roster-footsies-20260907/neutral-final-20260908/0-ground-neutral-heavy-R-whiff/contact-montage.png>)

Tsubasa heavy
![Tsubasa heavy](</Users/anthonyguy/SHADOWCLASH.1.0*2/SHODO-EDITION/media/roster-footsies-20260907/neutral-final-20260908/3-ground-neutral-heavy-R-whiff/contact-montage.png>)

Shin heavy
![Shin heavy](</Users/anthonyguy/SHADOWCLASH.1.0*2/SHODO-EDITION/media/roster-footsies-20260907/neutral-final-20260908/2-ground-neutral-heavy-R-whiff/contact-montage.png>)

Ember heavy
![Ember heavy](</Users/anthonyguy/SHADOWCLASH.1.0*2/SHODO-EDITION/media/roster-footsies-20260907/neutral-final-20260908/4-ground-neutral-heavy-R-whiff/contact-montage.png>)

Oni heavy
![Oni heavy](</Users/anthonyguy/SHADOWCLASH.1.0*2/SHODO-EDITION/media/roster-footsies-20260907/neutral-final-20260908/8-ground-neutral-heavy-R-whiff/contact-montage.png>)

Mokurai special
![Mokurai special](</Users/anthonyguy/SHADOWCLASH.1.0*2/SHODO-EDITION/media/roster-footsies-20260907/neutral-final-20260908/6-ground-neutral-special-R-whiff/contact-montage.png>)

Exile special
![Exile special](</Users/anthonyguy/SHADOWCLASH.1.0*2/SHODO-EDITION/media/roster-footsies-20260907/neutral-final-20260908/7-ground-neutral-special-R-whiff/contact-montage.png>)
