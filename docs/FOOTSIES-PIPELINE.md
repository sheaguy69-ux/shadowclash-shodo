# High-pace footsies and animation expansion

This is the project workflow requested by Anthony on September 7, 2026. The first implemented requests are Executioner's **forward+Light Shadow Slice** and **forward+Special Smoke-Bomb Shadow Strike**.

## Runtime contract

The `footsies-data` JSON block in `web/index.html` is the source of truth. The existing attack dispatcher, collision loop, damage resolver and shared Shodo renderer consume it directly. There is no second fighting engine or separate character renderer.

| Input | Frames: startup / active / recovery | Clean-hit cancel frames | Base damage | Hitstun |
|---|---|---|---|---|
| Executioner forward+Light | 2 / 2 / 5 | 3, 4, 5 | 28 | 14 frames |
| Executioner forward+Special | 6 / 3 / 7 | 8, 9, 10 | 55 | 22 frames |

Cancel destinations are smoke dash, Special and jump. Existing stamina costs and availability checks apply. These two moves specifically require a **clean hit**; a blocked hit does not grant their hit-only cancel. Other moves retain their existing hit/block chain rules. Smoke Strike has 12 frames of blockstun and no body/hurtbox on frames 3–4. Frames 5–7 carry its horizontal impulse. A nearby opponent permits one crossing; a distant opponent can make it whiff, and arena walls constrain the exit.

Frames are **60 Hz game-time units**. The existing 1.2 combat tempo accelerates playback, and the existing cinematic hitstop crawl remains. The runtime still integrates variable deltas; this work does not claim a fixed-step migration. A nine-frame move is 150 ms of game time, or 125 ms without hitstop at the current tempo. Damage values are base damage; existing health, defense and combo scaling remain. See `FOOTSIES-PHYSICS.md` for gravity conversion, preserved jump reach, friction, weight and DI.

Author rectangles use center-feet origin, x forward and y up, with y specifying the rectangle's bottom. Runtime rectangles use top-left origin, x right and y down. Box scale is anchored once to the current approved Executioner ready pose's drawn height; using the smaller movement collider made the first candidate's boxes sit at his ankles and was rejected. The approved crescent FX is drawn only during active frames into the same world rectangle as the disjoint, so the requested reach is visible without stretching the character. Source `disjoint_offset` is retained as design metadata: the actual authored rectangle determines contact, without adding a second invisible reach offset.

## Agent 1: implementation and frame direction

1. Read the current ledger, continuity rules, source manifest and actual state/animation routes. Trace callers before changing timing or collisions. Use graph discovery when available; source search is the fallback.
2. Study the current ready, attack, movement and recovery poses together at runtime scale and in both directions. Preserve identity, limb proportions, weapon count, source facing, foot pivots and the shared Shodo renderer.
3. Identify the neutral purpose: fast poke, low sweep, anti-air launcher or spacing pushback. Keep heavy whiffs punishable. Suggest a distinct move only when it improves that purpose; do not silently replace unrelated inputs.
4. Supply **every** frame index. The supplied Slice omitted 6–9; Smoke Strike omitted 11, 12, 14 and 15. These are now explicit recovery exposures. Extra anticipation must fit the approved startup budget; adding a drawing is not permission to add input lag.
5. Reuse suitable approved art first. Distinguish a held source drawing, a new exposure, a new drawing and a requested visual effect. Current implementations reuse approved compression, ready, sword-cut and recovery poses; they do not claim newly drawn hand signs, pellets or body smears. Squash/stretch belongs in authored poses; preserve the owner's rigid Shodo/no-warp rule and Shin crouch exception.
6. Run the data validator, runtime physics check and frame capture. Submit the exact JSON, both-facing contact sheets, consecutive scene filmstrips and source references to Agent 2.

## Agent 2: independent review and repeat gate

Audit contact eligibility against the actual collision loop, not merely a queued hitbox's presence. Inspect red strike rectangles and green body rectangles, including null hurtboxes during vanish. Compare the active blade's direction, scale and registration with the reference cells. Check exact startup/active/recovery boundaries, clean hit versus block versus whiff, cancellation, interruption, reset and wall cases.

Score the **observed result**, never the intended prompt: 9–10 excellent; 7–8 pass with named minor limitations; 1–6 reject. A score below 7 requires exact offending frame numbers, missing/extraneous exposures, vector/box errors and source-reference mismatches. Agent 1 repairs those findings and resubmits fresh evidence. Agent 2 then reruns and regrades. Automated checks do not assign a visual score. The supplied Smoke Strike's claimed 9.7 score is not evidence.

The Executioner review history is in `FOOTSIES-QA-2026-09-07.md`. The subsequent eight-fighter pass is documented in `ROSTER-FOOTSIES-QA-2026-09-07.md`; its independent scores are scoped to the observed sequences. The separate build746 run task added six Oni gait breakdowns and replaced only Shin's dive/tuck poses while preserving his other six drawings; see `ONI-SHIN-RUN-2026-09-07.md`.

## Remaining eight fighters

The September7 roster expansion keeps each existing kit and source drawing. `floorCommitment` records each committed melee window; `rosterAttackFrame` places reviewed release drawings inside actual contact intervals, including their last eligible simulation sample, then plays recovery. Shin's forward Heavy keeps elbow/knee/palm staging; Exile's formerly single-frame forward Light now uses existing anticipation and recovery drawings. Basic grounded Lights cap nominal startup at two game frames (three startup samples in the current collision loop); kicks retain their existing short startup and heavy whiff commitments remain.

Shared `combatPose` registers the current body independently of rendering. Strike fitting uses the same source-to-world transform; explicit source landmarks resolve ambiguous weapons, feet and baked slash effects. Executioner's authored rectangles bypass this fitting. The movement pushbox is unchanged. Directional source-tip AABBs are an approximation, not per-pixel collision or a claim that every extended limb is a hurt region. Existing projectile, counter, travel and corridor mechanics keep their own lifecycles.

`tools/audit_roster_footsies.py` exports all eight fighters: 640 grounded/airborne directional attack cases, 64 movement cases and128 hit/block cases. Each sequence has consecutive frame JSON and native-scale filmstrips. Facing-left spawn positions mirror the right-facing wall distance; otherwise Exile's left command correctly selects a nearby-wall grapple and cannot be compared with her far-wall strike. Runtime source hashes identify the exact tested build. Use `tools/check_roster_strikes.py` for the64 core contact-pose checks and `tools/check_roster_hurtboxes.py` for shared body/strike geometry checks. A full matrix is broad mechanical evidence; visual approval is separately recorded by Agent2.

## Reproduce

Run from this Shodo repository with its server on port 9101. Every browser tool verifies `/whoami` and opens an isolated headless browser.

```sh
python3 tools/check_footsies_data.py
python3 tools/check_footsies_physics.py
python3 tools/export_footsies_frames.py --fighter 0 --move light --direction forward --facing 1 --frames 12 --out media/footsies/slice-right
python3 tools/export_footsies_frames.py --fighter 0 --move special --direction forward --facing -1 --scenario hit --frames 20 --out media/footsies/smoke-left
```

Repeat captures with both facings and `--scenario whiff`, `hit` and `block`. The exporter also supports existing light/medium/heavy/special, run and jump sequences. Each output contains `frame_breakdown.json`, `filmstrip.png` with geometry and `scene-filmstrip.png` from the real scene renderer. JSON records source hashes, source cells/aliases, every exposure, simulation timing, velocity, acceleration/impulse changes, actual collision probes and contact outcomes. It explicitly labels its 60 Hz game-time sampling and bypass of cinematic hitstop crawl; it is not a claim that normal display FPS is fixed.


Final roster mechanical evidence: `media/roster-footsies-20260907/final/summary.json` records832 complete sequences /26,768 consecutive samples (104 cases per fighter), including128 hit/block setups with damage,16 real-jump assertions and zero truncated attack/projectile lifecycles. The other28 no-offense attack cases are conditional/counter/utility whiffs, not assumed failures. Native source remained unchanged throughout the final capture. Agent2 visual approval remains a separate, scoped judgment in the roster QA report.

The final jump review removed the legacy 10% launch stretch: it drew heads above the source-registered hurtboxes. The approved launch drawings now stay at their uniform source scale. Post-correction both-facing jump evidence is in `media/roster-footsies-20260907/jump-final/`; the832-case capture remains the prior broad mechanical record, with this rendering-only delta documented separately.
