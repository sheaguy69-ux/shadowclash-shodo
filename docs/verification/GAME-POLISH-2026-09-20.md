# Game polish — September 20, 2026

This pass targets the local Shodō edition on port 9101, based on commit `84518b5` (SHEET_V 846). The task's older home-directory path had moved into iCloud Drive. Existing uncommitted work was preserved.

## Changes

- Package the existing fighter cells into small, lossless runtime PNG pages. The original sheets and manifests remain unchanged. Each runtime cell retains its source coordinates; the existing Shodō contour, keying, frame selection, attack timing and combat geometry still apply.
- Load the derived pages only when their sheet version and complete source manifest match. Missing, invalid or stale pages fall back to the existing width-checked original atlas loader.
- Pause active matches on focus loss or tab hiding, with explicit Resume required. Title demos and cutscenes keep their existing behavior.
- Clear held/queued inputs and short input chords at pause boundaries. Keyboard/touch releases cannot alter a paused jump. Old touch gestures, mouse targets and controller menu presses cannot become attacks or jumps after Resume.
- Keep the pause dialog within the viewport, including portrait phones and short landscape screens.

## Rebuilding runtime pages

After approved source-art changes, run:

```sh
python3 tools/build_runtime_sprites.py
python3 tools/build_runtime_sprites.py --check
```

The packer verifies every cell's alpha and every nontransparent RGBA pixel against its original and checks the source PNG/JSON hashes before and after. Source RGB hidden beneath zero alpha is omitted from the derived pages; Canvas cannot display it. Each page has transparent padding and stays at or below 2048 pixels per side. Page names include the original source hash. The index records SHEET_V; changing that version disables old pages until rebuilt.

The original art files remain the authority. These runtime assets are reproducible packaging, not new or redrawn artwork.

## Validation evidence

Detailed results and frame strips are in `media/game-polish-20260920/` (local, ignored by Git).

- Full source reconstruction: 3,446 cells across eight active fighters and 28 runtime pages; alpha and visible pixels identical; original files unchanged.
- Decoded sheet area: 2,222,502,288 bytes → 389,048,836 bytes, an 82.5% reduction. This is image-surface size, not a claim about total browser memory.
- Sprite download bytes: 146,976,725 → 130,154,793 (11.4% smaller).
- Targeted pause/input checks: 32 pass, including keyboard, touch, mouse, synthetic webcam callback, gamepad edges and three viewport sizes. Physical controllers/cameras and real phones were not used.
- Existing gamepad mapping suite: 54 assertions pass.
- Independent browser pixel oracle: 3,831 raw cells, 3,831 keyed cells and 332 outlined samples match the original renderer exactly, including both facings and source metadata offsets. Counts include legacy-height variants of Ember cells.
- Deterministic combat replay: eight fighters × 240 real game-loop frames = 1,920 identical combat snapshots before/after; no browser exceptions.
- Six mirrored fractional raw-projectile compatibility fixtures also match. The legacy raw wire row is absent from current sheets; when present in a future sheet, it retains the native original-image sampling path.
- Integrated Ember/Executioner sustained desktop probe: 7.1 → 60.0 FPS; 15 recurring long tasks → zero in the 12-second measurement window. The final frozen-source rerun sustained 59.92 FPS with zero long tasks and a 0.73 ms mean scene draw. Kael/Mizu also sustained 60 FPS. Startup stalls remain: the final 8-second warmup had three initialization tasks of 102, 55 and 71 ms.
- Fresh boot: all eight fighters use the 28 runtime pages, with no original fighter-strip downloads and no failed sprite resources.
- Runtime fallback checks pass for missing index entries, mismatched metadata, missing pages, stale versions, invalid geometry and out-of-bounds cells. Expected injected 404s and the existing optional, unbundled music slot are recorded separately; no JavaScript exceptions or unhandled rejections occurred.
- The older `polish_suite_check.mjs` still reports nine failures involving obsolete landing-cushion constants/expectations. Its complete output is identical against the saved pre-change source and this build; those are pre-existing failures, not a passing suite.

Final render/combat evidence: `media/game-polish-20260920/runtime-verified/result.json` and matching before/after filmstrips. Pause results: `pause-final.json`. Performance: `performance.json` and `performance.md`. Loader fallback evidence: `runtime-fallbacks.json`. Desktop headless measurements do not establish performance on every phone or browser.

No public deployment, merge, image generation, paid API request or combat rebalance is part of this pass.

Verified installed HTML SHA-256: `a9f801ff0672ab6f3f0828781cdcc8cf866e03589c3f32cd2ae028bfe00050b6`.
