# Oni and Shin running — build746

**Build750 follow-up:** Anthony rejected Oni's intermediate gait. Six corrected supported/passing/reaching drawings now replace687–692 in the active row: **660,695,696,697,661,698,699,700**. Approved660/661 and Shin's row remain unchanged. Both-facing native review passes7/10; see [current report](../media/oni-run-refine-20260907/REPORT.md). The build746 material below is historical. Concurrent balance work changed Oni's current speed to554.1667; his animation cadence remains2.4cycles/game-second.

Anthony approved adding six transitions to Oni's two approved contacts. For Shin,
he explicitly likes the existing run and requested replacing only the dive and
both-knees-tucked poses with ordinary running steps.

| Fighter | Final eight-drawing order | Change |
|---|---|---|
| Oni | 660,687,688,689,661,690,691,692 | Six new compression, passing and push-off drawings; original opposite-leg contacts remain at slots1/5. |
| Shin | 277,278,381,280,382,282,283,284 | New supported leg-exchange and extended-stride drawings replace279/281; six original drawings remain unchanged. |

These are distinct drawings, not duplicated exposures. The travel-based animation
clock is unchanged: at525worldpixels/game-second, Oni runs2.4fullcycles/game-second
and Shin3.0. The existing1.2combattempo remains. All character art uses the shared
`drawShodoFrame` renderer, with uniform scale and no new body warping.

Sources were generated with the built-in imagegen tool from the actual approved
running references. No external paid API was used. Generated green/magenta mattes
were removed during sprite extraction. Oni uses one0.3465head/armor scale across
the six additions; Shin uses one0.18hood scale across both replacements. Pose
envelopes were not flattened to equal height. Every original atlas pixel and all
non-running manifest mappings are preserved. Shin's build745 crouch remains.

## Review and reproduction

Final production checks pass:400 real-input samples across both fighters/facings,
nine roster run collectors, nine whole sheets, exact eight-new-cell pixel matches,
and unchanged old atlas prefixes. Speed, travel, stopping and normalized cadence
match the saved baseline.

Independent review rejected Oni's first passing poses and caught two clipped boot
tips in extraction. The revised actual-rendered loops pass7/10 in both directions.
Accepted limits: Oni's second half-stride rises more than the first; Shin's new knee
and wrap details have slightly higher contrast, and the six retained poses keep
their existing stylized gait. This is a scoped improvement, not a whole-roster redraw.

- [Independent review and twelve-dimension grades](../media/run-expansion-20260907/qa/FINAL-REVIEW.md)
- [Exact packed mappings and preserved atlas hashes](../media/run-expansion-20260907/packed.json)
- [Oni final generation prompt](../media/run-expansion-20260907/oni/prompt-v2.txt) and [initial prompt](../media/run-expansion-20260907/oni/prompt-v1.txt)
- [Shin references, prompts and preparation](../media/run-expansion-20260907/shin/HANDOFF.md)
- [Oni eight-pose direction data](../media/run-expansion-20260907/oni/frame-direction.json)
- [Shin eight-pose direction data](../media/run-expansion-20260907/shin/frame_breakdown.json)

The runtime evidence lives in `media/oni-shin-runs-20260907/`. Its per-exposure JSON
records actual cells, positions, velocity, hitboxes/hurtboxes and renderer transforms;
held exposures remain explicit. Before/after checks use real movement input and
compare travel, facing, loop cadence and stopping. They also hash the two preserved
Oni contacts and six preserved Shin drawings.

```sh
python3 tools/check_oni_shin_runs.py --baseline media/oni-shin-runs-20260907/before/runtime.json --out media/oni-shin-runs-20260907/after/runtime.json
node tools/check_run_cells.mjs
python3 tools/check_sheets_whole.py --worktree
```

Only the two sprite sheets/manifests and the cache version changed in production
for this task. Concurrent footsies/clash changes were preserved. Local`:9101`only;
no commit, staging, push or deployment.
