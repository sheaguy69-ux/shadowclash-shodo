# Oni baked idle aura cleanup — 2026-09-06

Anthony explicitly requested erasure of the old gray crust in front of his approved animated Shodo aura, then approved the clean cutout. The previous Canvas-glow removal had missed smoke painted into the source sprites.

Installed six alpha-only replacements 668–673 for idle502–507, all eight semantic aliases repointed, SHEET_V735. Removed 5,152 visibly changed haze pixels. Every original RGB byte, body scale, registration, horn silhouette and existing dark Shodo treatment remains. All original668 atlas cells remain byte-identical in decoded RGBA. The new animated aura asset and renderer remain unchanged; gameplay and animation timing remain unchanged.

Built-in imagegen supplied a foreground matte, not replacement character paint. Saved source, prompt/processing account, feature alignment, exact native cutouts and comparison overlays are under `media/oni-gray-removal-20260906/`. The returned image had RGB checkerboard, not true alpha; extracting its silhouette and applying it only to original sprite alpha avoids both checkerboard leakage and character redesign.

| Beat | Cell | Result | Removed haze pixels |
|---|---:|---|---:|
| 1 | 668 | KEEP | 902 |
| 2 | 669 | KEEP | 901 |
| 3 | 670 | KEEP | 926 |
| 4 | 671 | KEEP | 906 |
| 5 | 672 | KEEP | 734 |
| 6 | 673 | KEEP | 783 |

All six candidates pass identity/weapon/palette, pose/silhouette, size/registration, existing motion/smear/physics/timing, background and integrity checks. This is an erasure pass, with no new action poses.

`BROWSER_PORT=9366 OUT=media/oni-gray-removal-20260906/live python3 tools/check_oni_aura.py` passes:120 consecutive captures spanning all six actual idle poses, moving/frozen aura clock, correct air-pose anchor, Oni-only aura routing and no old Canvas glow. Pixel check enforces original RGB preservation, alpha-only deletion and substantial baked-haze removal on every beat. Nine worktree sprite sheets pass `tools/check_sheets_whole.py --worktree`.

Evidence: `approved-native-cleanup.png`, `live/six-beats.png`, `live/aura.gif` and `live/checks.json` in that media directory. User CPU tab was not reloaded; a refresh of :9101 loads735.

Scope: the approved idle loop. Several older guard/attack/recovery families also contain baked smoke and have not received this new matte pass; no claim every Oni action is halo-free. The broad roster review remains separate.

Concurrent AudioSys, sparks, supplied VFX, Executioner/Tsubasa/Mokurai/Exile work and held Ember deletions are excluded from this commit. One authorized quota-reset redemption was attempted after a subagent hit its limit; outcome `noCredit`, available bonuses0, no reset consumed. No paid external API, push or deployment.
