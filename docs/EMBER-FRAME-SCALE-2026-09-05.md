# Ember frame scale — SHODO-EDITION :9101

Anthony requested: “PLEASE FIX AND SCALE ALL EMBER FRAMES.” His standing instruction authorizes the review and fixes without repeated approval requests.

Reviewed all **140 distinct active cells / 146 frame keys**. Applied **108 uniform XY display-scale corrections**, **17 planted-foot anchor corrections**, and removed disconnected card-guide remnants from **six cells** at render time. `SHEET_V 716`. The PNG, frame indices, mirror map, timing, hitboxes, and other fighters' scale metadata are unchanged.

The small grab/kick/hurt/air families and oversized newer directional-heavy heads were compared visually with Ember's idle and crouch, in raw full-cell plates and the real outlined renderer. One multiplier is used across each authored family, including its aliases. Crouching, tucking, turning and airborne poses retain their shapes. The total ink/effect bounding box was audited for clipping, **not used as a body-size ruler**. Factors are visual calibration; the tests do not establish subpixel anatomical uniformity across independently drawn source art.

`drawSprite` reads the optional `frameScale` map. Stored afterimages and clones use their own cell's scale, even when the live fighter is drawing another row; the white hit flash uses the same geometry and cleaned source silhouette. The existing `footAdj` map aligns inspected planted soles. Lifted/airborne beats keep their authored lift.

The `frameClear` rectangles are explicit visual findings: hurt3's dashed vertical guide, medium5's detached vertical card edge, and bottom card marks under four standing Special beats. The body and attack effects remain outside these rectangles. These are not an automatic component-removal heuristic. Sprite bytes remain unchanged, and the shared Shodō renderer still owns all outlines.

Verification:

- `python3 tools/check_ember_scale.py`: all 140 cells render at the intended uniform scale and anchor with nonempty, unclipped output; copies and hit flash pass. Pixel comparison preserves every pixel outside the six cells' declared cleanup rectangles.
- The same check captures 36 consecutive animation callbacks for each forward/down/back Heavy: every cell in all three six-frame rows appears. The input is dispatched on the first captured callback; stage setup completes before capture. Cold first-draw hitches can skip a short exposure if capture starts late; this test does not claim guaranteed FPS.
- `NAME=Ember OUT=media/ember-scale-20260905/live node tools/capture_roster_transitions.mjs --check-landing`: four tier scenarios, 24 transition strips / 192 frames, no routing failures or JavaScript errors. Inspected run-to-idle, ground recovery and aerial landing strips. No new gameplay routing change.
- `node tools/drive_real_input.mjs --all`: 648 input probes pass. Its 57 shared-animation groups are informational.
- `node tools/check_shodo_render_cache.mjs`: 78 reference pixel comparisons pass; zero filtered draws on warm repetition; cache remains bounded at 64 cells.
- PNG SHA-256, original frame map and mirror map match the saved baseline; `git diff --check` passes.

Evidence: `media/ember-scale-20260905/`. `comparison.png` shows representative before/after poses, `before-1..7.png` and `after-1..7.png` cover every active cell, `cell-review.csv` records the scope of the per-cell review, and the live traces/strips retain the sampled motion. This is a sizing/alignment correction using existing art, not a redraw or a claim that every authored effect/contact frame has received a new art-production signoff.

The previously requested 20% faster action clock was saved separately as `9661310` before this art pass.
