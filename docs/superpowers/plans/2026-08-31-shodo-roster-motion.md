# Shodō Roster Scale and Motion Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Deliver a standalone first-form game whose nine fighters use only scale-correct, smoothly routed Shodō frames.

**Architecture:** Keep approved board files immutable, append review-approved normalized cells to the runtime atlases, and then use the existing clean exporter for the final zero-orphan compaction. One new roster gate owns Story Bible heights and core-route requirements; existing zero-legacy and live-routing tools retain their current responsibilities.

**Tech Stack:** Python 3 + Pillow/NumPy/SciPy sprite tools, Node.js static gates, single-file Canvas game runtime, local `tools/serve.py` review server.

**Spec:** `docs/superpowers/specs/2026-08-31-shodo-roster-motion.md`

## Global Constraints

- Work only in the independent `SHODO-EDITION` repository.
- Never overwrite `art/shodo-source` or introduce a legacy/second-form playable-character cell.
- Keep one uniform fighter scale and one shared sequence scale; foot-anchor grounded frames.
- Show montage strips and grade tables before changing runtime art.
- Do not use paid generation. Reuse approved eight-frame boards before considering built-in generation.
- Serve the final standalone game on `:9101`; `:9102` remains the approved-art gallery.

---

### Task 1: Story Bible roster gate

**Files:**
- Create: `tools/check_shodo_roster.py`
- Test: `tools/check_shodo_roster.py`

**Interfaces:**
- Consumes: `web/assets/sprites/<fighter>.json` and `.png`.
- Produces: exit code `0` only when neutral heights, core aliases, cell bounds, and first-form alias rules pass.

- [x] **Step 1: Write the failing gate**

Define the nine exact target heights, preferred neutral aliases, required core-route alias groups, and prohibited prefixes. Measure `screen_height = (footY - alpha_top) * scale` from the neutral cell.

- [x] **Step 2: Run it to verify the current export fails**

Run: `python3 tools/check_shodo_roster.py`

Expected: FAIL for undersized neutral poses and missing Executioner/Mokurai/Oni core aliases.

- [x] **Step 3: Keep failure output actionable**

Print one line per fighter with measured height, target height, selected neutral key, and missing route groups.

- [x] **Step 4: Re-run the existing clean-atlas gate**

Run: `node tools/check_zero_legacy.mjs --strict`

Expected: PASS, proving the new gate exposes coverage/scale defects that the geometry gate intentionally does not cover.

### Task 2: Immutable review-strip builder

**Files:**
- Create: `tools/sprites/build_shodo_core_review.py`
- Create: `media/shodo-core-review/` outputs (gitignored)

**Interfaces:**
- Consumes: approved boards under `art/shodo-source`, current manifests, and canon targets from Task 1.
- Produces: one contact sheet and one JSON grade/measurement report per fighter without touching `web/assets/sprites`.

- [x] **Step 1: Write a `--self-test` for scale and footing math**

Use two synthetic RGBA cells to assert that one shared scale preserves their relative pose height and places the grounded reference at `footY`.

- [x] **Step 2: Run the self-test and verify it fails before implementation**

Run: `python3 tools/sprites/build_shodo_core_review.py --self-test`

Expected: FAIL until the shared-scale/foot-anchor functions exist.

- [x] **Step 3: Implement the smallest review builder**

Reuse the existing keying/cropping conventions from `pack_shodo_row.py`; select the already approved idle/run/block/hurt/jump/dodge/knockdown boards. Build versioned preview cells at the internal neutral height implied by `target_height / manifest.scale`.

- [x] **Step 4: Generate review evidence**

Run: `python3 tools/sprites/build_shodo_core_review.py`

Expected: nine strips plus a report containing source paths, hashes, alpha bounds, scale, foot position, and 48x64 silhouette previews.

- [x] **Step 5: Present the strips for owner approval**

Do not modify runtime atlases in this task.

### Task 3: Pack approved core rows

**Files:**
- Modify: `tools/sprites/pack_shodo_row.py`
- Modify: `tools/sprites/pack_shodo_air.py`
- Modify after visual approval: `web/assets/sprites/<fighter>.png`
- Modify after visual approval: `web/assets/sprites/<fighter>.json`
- Modify with sheet changes: `web/index.html`

**Interfaces:**
- Consumes: approved review cells/report from Task 2.
- Produces: appended, foot-anchored runtime cells and complete core aliases.

- [x] **Step 1: Add a failing bootstrap-scale check**

Exercise packing against a manifest without `idle`; require an explicit internal target height instead of falling back to cell `0`.

- [x] **Step 2: Add the minimal explicit-target option**

Allow `TARGET_H=<pixels>` for the first neutral row. Keep the existing idle-derived path unchanged for later rows.

- [x] **Step 3: Pack neutral rows first**

Append approved neutral boards and map `idle`/`idle2`, `xidle1..6`, or `stand1..6` according to each fighter's runtime router.

- [ ] **Step 4: Pack remaining missing core rows**

Append and route approved run, block, hurt, jump/fall, dodge/roll, crouch, wall, and knockdown/recovery boards. Use aerial packing only for art whose vertical lift is supplied by world physics.

- [x] **Step 5: Bump `SHEET_V` once with the complete approved batch**

No timing, combat, hitbox, or physics changes.

- [x] **Step 6: Run static gates**

Run: `python3 tools/check_shodo_roster.py`

Run: `node tools/check_zero_legacy.mjs`

Expected: roster gate PASS; append-only gate may report only the superseded Shodō cells as strip candidates.

### Task 4: Targeted motion continuity pass

**Files:**
- Modify only if required: `art/shodo-source/<fighter>/<new-versioned-board>/`
- Create: `media/shodo-motion-review/` outputs (gitignored)

**Interfaces:**
- Consumes: packed runtime route filmstrips.
- Produces: either a proof that existing approved eight-frame boards cover motion, or owner-reviewed versioned in-between frames for specific failed transitions.

- [ ] **Step 1: Capture consecutive route filmstrips**

Test idle-to-run-to-idle, grounded light/heavy/special, jump/air/land, block/hurt, dodge/roll, and knockdown/recovery for all nine fighters.

- [ ] **Step 2: Grade continuity**

Reject identity/weapon mutation, foot drift, body-scale wobble over 0.5%, motion jumps over 30% without a readable smear, missing anticipation/contact/recovery, clipping, or blank/dead frames.

- [ ] **Step 3: Reuse another approved beat where possible**

Prefer reordering or selecting an existing approved beat over creating art.

- [ ] **Step 4: Generate only proven gaps**

If a sequence still fails, use built-in image generation with the exact adjacent approved frames as references. Write a new versioned board; never overwrite an approved source.

- [ ] **Step 5: Present generated strips and grade tables**

Do not pack generated cells before Anthony approves the images.

### Task 5: Clean compaction and live launch

**Files:**
- Modify: `tools/sprites/export_shodo_only.py`
- Modify: `docs/SHODO-EXPORT-MANIFEST.json`
- Modify: `web/assets/sprites/*.png`
- Modify: `web/assets/sprites/*.json`

**Interfaces:**
- Consumes: approved routed cells from Tasks 3-4.
- Produces: deterministic zero-orphan atlases and provenance receipt.

- [ ] **Step 1: Make the clean exporter select approved routed cells by provenance rather than a numeric baseline**

Reject missing required aliases and preserve exact RGBA bytes for retained cells.

- [ ] **Step 2: Export the final clean atlases**

Run the exporter against the approved packing source and retain only first-form routed cells.

- [ ] **Step 3: Run all static checks**

Run: `python3 tools/check_shodo_roster.py`

Run: `node tools/check_zero_legacy.mjs --strict`

Run: `node tools/check_first_form_gate.mjs`

Expected: all PASS with zero orphan, blank, fallback, or prohibited cells.

- [x] **Step 4: Rebind the dedicated game server**

Stop the current mixed-tree process on `:9101`, then run `python3 tools/serve.py 9101 web` from this repository.

- [x] **Step 5: Verify server identity and watch the game**

Run: `curl -s http://127.0.0.1:9101/whoami`

Expected: tree is `SHODO-EDITION`, branch is `shodo-edition`, and the reported sheet version matches the changed game.

- [ ] **Step 6: Open the verified Shodō game and capture final roster filmstrips**

The final evidence must show all nine fighters at canon relative scale with no legacy frame visible.
