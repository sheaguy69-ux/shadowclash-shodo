# Roster footsies independent QA — September 7, 2026

Status: **PASS — all eight scoped fighters score 7/10 after rejection, repair and fresh runtime review.** Agent 2 directly inspected consecutive native-render filmstrips. Scores describe the scoped runtime sequences, not every move or the whole game.

## Baseline rejection

Evidence: `media/roster-footsies-20260907/baseline/` (right-facing whiffs, 48 consecutive game-time samples each), plus `qa/baseline-mizu-forward-light/` (24 samples). Raw baseline image labels can mislabel the last startup boundary as RECOVERY; phase should follow actual collision eligibility. This labeling fault is separate from the observed artwork/collision mismatch.

| Fighter | Score | Exact observed rejection and required repair |
|---|---:|---|
| Mizu | 5/10 | Forward Light: F5 red region below raised knee; F6–7 below extended foot; F8–12 remains active through leg retraction and ready75. Synchronize contact drawing with active interval and place strike at foot. Ready75 F11–20 green top follows staff tip instead of head. |
| Shin | 5/10 | Forward Light: contact246 plays F3 during startup; F5–12 active instead shows retract247/248/249 and ready350. Red rectangle stays at ankles. Put existing contact drawing into active window and align to foot. |
| Tsubasa | 5/10 | Forward Heavy: F10–18 knives/strike are at chest height while red region is at feet; F19–20 retracted179 is still active. Match active exposure and knife height. |
| Ember | 5/10 | Neutral Light: F6 extended claws269 are at chest height while red is at knee; F7–9 retract270/271 stays active. Green on crouch302 excludes much of the forward body/head. Match strike height and pose body extent. |
| Kael | 5/10 | Forward Heavy: F9 windup204 active; F10–18 sword/arcs205/207 at chest/head but red at lower body; F19–22 recoil305 and ready209 still active. Synchronize existing contact exposures with active windows. |
| Mokurai | 5/10 | Forward Special: F6–14 strike red at knees despite chest-height palms; F35–36 ready332 still active. Respect real multihit gaps (F15–16 and F26), synchronize each palm contact. |
| Exile | 6/10 | Neutral Light: F6–8 arc325 is mostly above red strike region; F9 returning326 remains active. Raise geometry to actual sickle arc and synchronize active hold. |
| Oni | 4/10 | Forward Heavy: F10–17 active on coil654/655 with low red region; actual extension657/658 appears only F27–39 recovery. Retiming existing contact drawings is required; simply moving the rectangle cannot fix this sequence. |

No replacement artwork is required to fix these baseline findings: existing contact poses are present. New held exposures must be identified as holds, not new drawings. Preserve actual move identities and committed heavy whiff recovery.

## Reference and scope

Reviewed current ledger, `docs/FOOTSIES-PIPELINE.md`, `docs/SHODO-FRAME-CONTINUITY.md`, the Second Brain Sprite Animation Director Prompt and 2D anatomy/frame staging skill. Newer consistent body-scale/no-warp rules supersede the old pose-bbox height-flattening recipe. Current approved Shodo frames are the style reference. No PNG or manifest edits were made by QA.

The earlier user-facing claim that Oni still lacked six run drawings and Shin still needed the two leg corrections was stale. Build746 already includes Oni660/687/688/689/661/690/691/692 and Shin277/278/381/280/382/282/283/284, with its own independent7/10 review. This task must verify these current rows, not revert or redundantly regenerate them. Exile/Shin wall finish748 and Oni wall747 remain separate existing work.

The 12 review dimensions are identity, weapon discipline, palette, pose readability, small silhouette, body-scale registration, motion path, smear legibility, authored anticipation/settle, frame-data alignment, edge artifacts and sheet integrity. Baseline failures are primarily frame-data alignment and pose-relative collision placement; pre-existing approved artwork is not being advertised as newly redrawn or perfect.

## Contact drawings supplied to Agent 1

These targets come from actual current-render contact sheets, not a generic midpoint assumption. A rotating attack can require several contact poses and changing strike bounds.

| Fighter | Current approved contact aliases |
|---|---|
| Mizu | `light4–6` staff poke; `kpush5` foot extension; `bothrust4/5` staff extension; `bolow5` low staff contact; Special progresses overhead `special3` to low `special5/7`. |
| Shin | `light4` punch; `kpush2` extended kick (the second drawing, not midpoint); forward Heavy starts `ghfwd3` punch and later kick. |
| Tsubasa | `light7` forward knife contact (corrected after source-grid inspection; the earlier `light5/6` recommendation was inadequate); `kpush4` horizontal knives; `rgrush4/5/6` extension/impact/follow-through. |
| Ember | `light4`, `kpush4`, `clawrend4`; `espec4` extension to `espec6` flare. |
| Kael | `kdual4` overhead sword arc; `kcyc4` horizontal to `kcyc6` full circle; `ktrav5/6/7` spread/cross/low follow-through. |
| Mokurai | `light4`, `kpush4`, `mpalm3` palm extension; `mpalm4` impact; `bspec4` is the most extended palm in the short block-derived special row. |
| Exile | `light4` sickle arc; `xkpush5` currently a single held push; `xheavy5` overhead crescent; `gsfwd6` forward chain contact. Baseline forward Special red incorrectly extends behind the visible forward chain. |
| Oni | `light4/5`, `glfwd4/5`; forward Heavy `ghfwd5/6` extension/impact. |

Shin/Oni forward Special projectile routes and Tsubasa forward Special dash should retain their distinct lifecycle; absence of a melee rectangle alone is not a failed projectile/dash move.

## Hurtbox candidate rejection

Fresh `qa/ember-hull-candidate/filmstrip.png` shows the proposed median-body centering moves green toward the crouched body, but still clips the upper hood throughout standing attack F1–11 by roughly20 world pixels and excludes the front half of the head. Crouch302 F12–16 also has much of the head outside the narrow green rectangle. Score remains5/10 for this candidate. Require standing head reference instead of low idle cap and enough width/offset to include the head; excluding long claws/scarf tips is acceptable, excluding the visible head is not.

Fresh `qa/ember-hull-candidate2/filmstrip.png` after the dense-head/upper-body-width repair passes **7/10 for the scoped Ember body hull only**: F1–11 standing hood and trunk now fit; F12–16 crouch302 head/trunk are represented. Small contour protrusions, trailing foot and claw tips remain outside the bounded body rectangle. This is not an attack pass: red geometry and contact exposure timing were still pending in that capture, and both-facing all-fighter validation must follow the final shared change.

Fresh `qa/shin-phase-candidate/filmstrip.png` verifies the exposure repair for forward Light: F1–4 anticipation245; F5–12 holds actual extended kick246 while the strike is active; F13 withdraws248 before movement. The original active-on-retraction defect is removed. **7/10 for this scoped phase repair**, with ordinary held cel animation rather than a newly drawn transition. Red strike placement was still below the foot in that intermediate capture, so the overall move remained rejected pending geometry.

## Combined candidate rejection and corrections

`qa/final-candidate/` contains128 sequences at one unchanged game source:64 core attacks plus both-facing run/jump/crouch/guard for eight fighters. Its jump subset was rejected as harness evidence: the zero-delta boundary update landed the fighter at unchanged takeoff coordinates before any displacement, producing JUMP/zero-velocity then IDLE. The exporter was corrected to capture the jump-entry boundary before that zero-delta update, and actual negative launch velocity/rise assertions were required. Left-facing spawn context was also corrected to mirror the arena position, preventing Exile's left Special from selecting a nearby-wall grapple while the right selected an open-space attack.

The combined candidate exposed residual scan failures, not new art defects: Mizu Heavy's long melee rectangle had been mistakenly exempted as a travelling attack; Mizu113 included a back-staff tip in a foot region; Ember150 and Oni527/528/584 included a front leg underneath the attacking hand. Manually inspected current source contact regions were supplied for these exact cells (`qa/*-strike-landmarks.png`). Kael207/236 and Mizu168/170/172 needed body landmarks to prevent baked weapon arcs becoming green hurt regions (`qa/*-source-landmarks.png`).

Tsubasa neutral Light contact was corrected to the clearly extended forward knife `light7`/246 after source-grid inspection. The earlier native-size recommendation of `light5/6` was insufficient; those poses do not provide as clear a forward knife contact. Kael `kdual5` was removed from the active span because its sword retracts behind the neck. Shin Heavy preserves the original punch/kick/punch identity with261→246→261 contact windows instead of holding one punch throughout.

Exile Special required actual scene review: its separate live chain really travels behind the body, so simply mapping both old broad boxes onto the front baked chain would be wrong. The revised solution retains the forward artwork contact and follows the actual simulated ball for the backward threat, gating that backward box while the tip is in front. Actual scene filmstrips, not isolated body drawings, are required for the final Exile score.


## Final independent verdict

All eight fighters pass **7/10** for neutral Light, forward Light, forward Heavy and forward Special in both facings, plus the reviewed run/jump/crouch/guard body registration. Existing distinct weapons, silhouettes and move identities remain recognizable. Startup/contact/recovery now match collision exposure; red regions follow the relevant strike, and green regions follow the bounded body core rather than the surrounding weapon effects. Held drawings are exposure changes, not newly authored intermediate art.

| Fighter | Final score | Verified improvement and remaining limit |
|---|---:|---|
| Mizu | 7/10 PASS | Foot/staff strike regions and overhead/low special body landmarks corrected. The bounded leading strike region does not trace every decorative trail pixel. |
| Shin | 7/10 PASS | Extended kick stays active; Heavy preserves punch/kick/punch. Held contacts and the existing approved stylized run remain. |
| Tsubasa | 7/10 PASS | Forward knife contact246 replaces inadequate neutral-contact choice; rush contacts align. Source intermediates remain limited. |
| Ember | 7/10 PASS | Standing/crouched head and trunk represented; claw/fist red region no longer includes the lower leg. Small appendage tips remain outside the core hull. |
| Kael | 7/10 PASS | Retracted kdual5 removed from active exposure; overhead sword effects excluded from body hull. Decorative full-circle effects are not wholly damaging. |
| Mokurai | 7/10 PASS | Palm height and distinct multihit gaps align; launch head containment repaired. Short block-derived Special art still repeats held contacts. |
| Exile | 7/10 PASS | Push staged with existing ready/contact art; forward chain artwork and rear simulated ball have separate correct threat regions. Existing baked chain plus live simulation coexist; the entire rope is not a damaging box. |
| Oni | 7/10 PASS | Heavy extension occurs during active frames, claw regions exclude the leg, approved eight-drawing gait retained. Horns/aura/scarf are outside the bounded body core; contacts use holds. |

Final evidence is `media/roster-footsies-20260907/final/`: 832 completed captures, 26,768 game-time samples, zero truncations, 128 confirmed hit/block cases and 192 Special scene filmstrips. Browser-load/end source remained `ab13a93e0e02…`. Automated coverage of all 832 cases does **not** mean every alternate move was independently visually graded. The visual pass covers the 64 core attack sequences and sampled movement evidence described above, including consecutive strips and mirrored context; Exile's actual scene strips were essential to evaluate the rear orbit ball.

The final jump-only rejection concerned legacy launch stretch (`scale(.9,1.1)`) moving the rendered head outside the uniform body hull. Root removed that launch transform without changing source drawings. Fresh `jump-final/` contains 16 captures / 1,440 samples at unchanged source `48c1275f1a9c…`; 296 rising samples have x scale = y scale = approved runtime source scale, and all 16 negative-velocity/rise assertions pass. Native launch/apex/landing comparisons now represent the head and trunk consistently, including Mokurai. Existing landing/contact deformation is unchanged and limits a claim of globally uniform rendering.

Across the 12 dimensions, this is a scoped frame-data/geometry and registration pass. Identity, weapon discipline, palette, pose readability, silhouette, motion path and existing smear/readability were compared to current approved source poses. Existing anticipation/settle drawings were retimed and held; no new source drawings were required. PNG edges and sheet integrity were preserved by leaving art/manifest files untouched, not certified by a new production-art audit. Small contour exclusions and economical holds keep the score at 7 rather than 9–10. This verdict does not certify the whole game's balance, every special route, input-latency measurement or production-perfect animation.

Visible receipt: `media/roster-footsies-20260907/qa/roster-preview.png`, with exact selected sample/cell/source provenance beside it. The collage uses native runtime pixels at 1:1; it is a compact illustration, while the consecutive filmstrips and frame JSON carry the timing evidence.


## Owner approval

2026-09-07 21:10: Anthony explicitly approved the presented remaining-eight roster implementation and reviewed frames ("approve"). The scoped QA assessment and limitations above remain unchanged.
