# Animation smoothness — SHODO-EDITION :9101

The shared Shodo renderer now caches up to 64 outlined cells instead of recomputing four drop shadows for every fighter draw. All existing character callers inherit this. No sprite assets, combat timing, routing or SHEET_V changed in this performance pass.

## Measurement

Isolated headless Chrome, software rendering, Kael/Mizu idle, 180 live animation frames per sample. These are local samples, not a hardware FPS guarantee or combat endurance benchmark.

| Metric | Before | After |
|---|---:|---:|
| Scene draw mean | 11.984 ms | 1.999 ms |
| Scene draw p95 | 12.1 ms | 0.3 ms |
| Animation frame interval p95 | 33.3 ms | 16.7 ms |
| Maximum scene draw | 161.2 ms | 259.4 ms |

Cold first-use hitches remain; this change primarily reduces repeated work. Capture source and raw measurements are in `media/kael-smoothness-review-20260905/profiling/`.

## Verification

- `node tools/check_shodo_render_cache.mjs`: 78 pixel comparisons across nine fighters, representative poses, mirroring and fractional transforms match a clean pre-cache renderer. Twelve repeated warm draws perform zero filtered draws. Cache remains bounded at 64 entries.
- The visual oracle resets its scratch canvas per case: the old shared canvas leaked faint stale bottom-edge pixels after differently sized draws. Fresh per-cell canvases also remove this residue. This is not a claim of identity with that unintended residue.
- `node tools/drive_real_input.mjs --all`: 648 input probes passed, no dead inputs or errors. Shared-animation groupings remain informational.
- Node syntax and `git diff --check` passed.

## Kael landing — proposed, awaiting image approval

Real DOM key events through the running game produced four consecutive transition strips: idle/run, run/idle, ground heavy/recovery and late airborne heavy/landing. The late air heavy swaps from X-cut cells 293/294 to grounded cells 198/199 on touchdown while about 280 ms recovery remains.

The review-only candidate changes the X-cut routing guard from `!p.isGrounded` to `(p.attackAir || !p.isGrounded)`. Its next cells are 295/296, continuing the same attack at identical timing. The candidate exists only in an isolated capture browser; the gameplay source has not adopted that routing change. Existing authored cells and full weapons/effects are preserved; no cells were generated, resized or packed.

Compare at `http://localhost:9101/_review/kael-smoothness-20260905/`. Full traces and four strips per version are in `media/kael-smoothness-review-20260905/{current,candidate}/`. Reproduce with `OUT=media/kael-check node tools/capture_kael_transitions.mjs`; add `--candidate` for the isolated proposal. This captures the real sprite renderer in an isolated view, not the entire stage or procedural effects.

AGENTS.md rule 3 requires owner image approval before changing visible animation. No other air/landing routing changes are included.
