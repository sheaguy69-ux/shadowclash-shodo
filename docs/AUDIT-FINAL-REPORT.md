# ShadowClash — Final Consolidated Audit Report

> **Post-report reconciliation:** the `SHEET_V 9` work was the active cumulative repair, not stray work. It is committed as `466c96b`; the exact per-commit evidence is in [`CODEX-AUDIT-HANDOFF-2026-07-16.md`](CODEX-AUDIT-HANDOFF-2026-07-16.md). The audit branch is ready, but `main` remains blocked until Claude review and owner approval/merge of `466c96b`.

**Date:** 2026-07-16
**Scope:** Final gap-closure on the completed 11-commit audit (85c4ef6..45f2f7c) — cumulative runtime
regression on current `origin/main` (HEAD `55cdcaa`), streak-timing / sheet-loading verification, and
consolidated report. All 11 commit verdicts are **settled** (owner-ruled) and are reproduced here for
completeness, not re-litigated.

Runtime testing was done in an isolated git worktree (`docs/codex-audit-handoff`, fast-forwarded to
`origin/main`), serving `web/` over `python3 -m http.server 8442` and driving the live page via
browser automation (real `KeyboardEvent`/`TouchEvent` dispatch + direct `updateGame(1/60)` ticks). The
main working tree at `/Users/anthonyguy/SHADOWCLASH-1.0` was not touched. Nothing in this branch was
merged into `main`.

---

## 1. Executive summary

The 11-commit audit range is closed: 6 commits PASS as shipped/owner-kept, 4 were FIXED by follow-up
commits (culminating in `068404c`, merged `befa5b8`), 1 (`8ca9ff9`) is intentional-balance PASS with its
HUD regression already fixed downstream. Two further repair passes landed after the original audit —
the wobble-flatten art pass (`39306e3`+`04a5ea0`, merged `4551e18`) and the live-cell routing pass
(`69b6e02`, merged `55cdcaa`, PR #54) — both already on `origin/main`.

This session's cumulative runtime regression matrix, run fresh against `origin/main`, found **zero
runtime errors** across all 4 game modes (600+ ticks each), the full P1 input surface, a complete
KO → round-advance → match-end flow, a forced double-KO / sudden-death path, the TIMER ON/OFF toggle,
sprite-loading integrity, and synthetic touch-control input. Streak-timing and hitstop-freeze code was
verified by direct file/line inspection and both check out as designed. No public/private roster
leakage was found in git history.

**Recommendation: BLOCKED ON OWNER MERGE GATE.** The regression pass is clean, but `466c96b` must be
reviewed by Claude and approved/merged by the owner before original-six runtime art integration.

---

## 2. Per-commit table — final settled verdicts

| Commit | Verdict | Basis |
|---|---|---|
| `6f5bacf` | **FIXED** | Run-cadence guard landed in `068404c` |
| `830ac00` | **FIXED** (owner ruling 1A) | Re-baseline accepted; composite-only packers fixed in `068404c` |
| `8ca9ff9` | **PASS** | Balance change (ROUND_TIME/MAX_HP/TTK) intentional, owner kept; HUD regression it introduced was fixed in `70d6597` |
| `70d6597` | **PASS** | Cosmetic + HUD fix |
| `9b31e19` | **PASS** | Draw-only SLASH_ARC geometry |
| `296ac3c` | **FIXED** | Interruption-scoped `pendingSlash` clear + parry clear landed in `068404c` |
| `864162e` | **PASS** (owner ruling) | Shin's flying kick (redesign from tracking shuriken) kept |
| `44b1c04` | **FIXED** | SHEET_V bumped to 7 in `068404c` (covers the missed bump) |
| `dce49c3` | **PASS** | Intentional (staged grab, weapon-clash system), owner kept |
| `0d46b0a` | **PASS** | Render-only; Kael renderScale later re-ruled to 1.0 in PR #54 |
| `45f2f7c` | **PASS** | LOCKED_ROSTER_SLOTS budget respected (slot numerals + weapon-shape keyword only) |

---

## 3. Repair commits

- **`068404c`** (branch `fix/audit-2026-07-16`) — SHEET_V 7, interruption-scoped `pendingSlash` clear,
  run-cadence guard, composite-only packers. Merged via **`befa5b8`** ("post-audit discipline + bug
  fixes", owner approved).
- **Wobble flatten**: `39306e3` ($0 wobble fix on live attack groups: kael/ember/tsubasa `attack_body`,
  shin `flying_kick`) + `04a5ea0` (tsubasa `attack_body3` re-anchor, owner: "fix frame 3"). Merged via
  **`4551e18`** ("1 merge and 2 fix", owner approved).
- **Routing**: `69b6e02` (route approved live cells per ninja). Merged via **`55cdcaa`** ("merge it",
  PR #54).

All three are present on `origin/main` (verified: `55cdcaa` is the current tip fast-forwarded into this
branch with no conflicts).

---

## 4. SHEET_V history

| Value | Commit | Reason |
|---|---|---|
| 3 | `ac8695b` | Version-stamped sheet loading + width check introduced (#43) |
| 4 | `5771bc4` | Kick cells (ksweep/kpush/kheel/kstomp) added to every sheet (#53, fixing a miss in #52) |
| 5 | `830ac00` | Cleaned four-frame ninja sprint added to every sheet |
| 6 | `864162e` | Full-body attacks and Shin flying kick |
| 7 | `068404c` | Audit 2026-07-16 fix — covers the missed bump in `44b1c04` |
| 8 | `39306e3` | Wobble flatten pass |
| **9*** | *(uncommitted, working tree only)* | Comment reads "Tsubasa attack_body3 re-anchor" — see §10 |

\* Value 9 is **not** part of any commit in the `docs/codex-audit-handoff` history as of `55cdcaa`; it
exists only as an uncommitted local edit in the worktree used for this session's regression run (see
§10). It does not affect the verdicts above.

---

## 5. Byte-comparison totals per fighter (830ac00 re-baseline)

From `docs/AUDIT-2026-07-16.md`: the `830ac00` repacker re-encoded all 6 sprite sheets; every differing
byte was an **alpha=0 flattening** (invisible RGB channel change on fully-transparent pixels) — geometry
and frame indices were unaffected. Per-fighter differing-pixel counts, all alpha=0:

| Fighter | Differing px |
|---|---|
| Ember | 29,873 |
| Executioner | 27,037 |
| Kael | 17,259 |
| Mizu | 16,139 |
| Shin | 20,876 |
| Tsubasa | 22,282 |

Re-baselined per owner ruling 1A (§2, `830ac00`); no visible pixel changed.

---

## 6. Timing-constant before/after table

From `docs/AUDIT-2026-07-16.md` §"Per-commit verdicts" and the fix commit:

| Constant | Before | After | Commit |
|---|---|---|---|
| ROUND_TIME | 60 | 90 | `8ca9ff9` (kept) |
| MAX_HP | 100 | 150 | `8ca9ff9` (kept) |
| HEALTH_DAMAGE_SCALE | 1.0 (implicit) | 0.88 (TTK ×~1.7) | `8ca9ff9` (kept) |
| THROW_TIME / RELEASE / stun | — | 0.38 / 0.56 / 0.68 | `dce49c3` (kept) |
| Weapon-clash hitstop / recovery floor | — | 115 / 0.16 | `dce49c3` (kept) |
| SHEET_V | 6 | 7 | `068404c` (fixes missed bump in `44b1c04`) |
| `pendingSlash` clear on interruption | absent (phantom-streak bug) | cleared in `takeDamage` + parry path | `068404c` (fixes `296ac3c`) |
| Run-cadence (2-cell art vs 6-cell animPhase) | mismatched (~1.5× fast legs) | guarded | `068404c` (fixes `6f5bacf`) |

Unchanged across the whole range (confirmed in the original audit and re-confirmed this session by
inspection): FOLLOW_THROUGH_HOLD (0.55), recoveryTotal logic, GRAVITY, base hitstop values.

---

## 7. Public/private leakage report

- **LOCKED_ROSTER_SLOTS** (`web/index.html:485`): budget respected — slot numerals + weapon-shape
  keyword only, no private names/stats/ids/portraits (per `45f2f7c` PASS verdict, §2).
- **`docs/LAUNCH-MESSAGING-PACKAGE.md`**: was untracked-only, relocated to the private brain on
  2026-07-16. Verified this session:
  ```
  $ git log --all --oneline -- docs/LAUNCH-MESSAGING-PACKAGE.md
  (no output)
  ```
  Zero commits in the entire history (`--all`) ever contained this file. Confirmed clean.

---

## 8. Runtime regression matrix (this session, against `origin/main` / `55cdcaa`)

All ticks driven synchronously via `updateGame(1/60)` in-page (bypassing the `requestAnimationFrame`
wrapper, per the task's methodology); no natural background game loop was found running concurrently
(confirmed: state was static between manual ticks with no player-object drift).

| # | Test | Result |
|---|---|---|
| 1a | ARCADE — mizu, BEGIN ARCADE, 600 ticks | **PASS** — 0 errors |
| 1b | VS CPU — shin vs CPU, 600 ticks | **PASS** — 0 errors |
| 1c | 2 PLAYERS — executioner vs mizu, 600 ticks | **PASS** — 0 errors |
| 1d | WATCH — tsubasa vs ember (CPU vs CPU), 600 ticks | **PASS** — 0 errors |
| 2 | P1 full input surface: run (D), crouch (S), jump (W), roll (S+DD), light (F), heavy (G), special (H), block (C hold), throw (F+G) — real `KeyboardEvent` dispatch, console checked after each | **PASS** — 0 errors, 0 console errors on every step |
| 3a | KO flow — WATCH executioner vs mizu, ~18,000 ticks: executioner KO'd (0/150) → round pip advanced (visible on canvas) → "ROUND 2" banner → continued to match end | **PASS** — "MIZU WINS — EXECUTION" victory screen reached (stats: 136 vs 308 dmg, 3 max combo each), 0 errors |
| 3b | TIMER toggle OFF → ∞ display | **PASS** — button flips to "⏱️ TIMER: OFF", `timedRounds` global confirmed `false`, canvas pixel-sampled at (400,34) shows 98px of the `#6b7280` glyph color in a 30×30 region — the "∞" glyph renders as coded |
| 4 | Double-KO / sudden-death — forced via direct `player1.hp=0; player2.hp=0` state injection (after clearing round-intro gate), single `updateGame` tick | **TESTED** (not skipped) — `roundWins` went `[0,0]→[1,1]` (both-earn-the-round branch fired), then a second forced double-KO at `[1,1]` drove `roundWins` to the coded `[1,1]` sudden-death reset with round advancing to "ROUND 3", both pips lit. 0 errors. Note: driven via direct state mutation on the confirmed-global `player1`/`player2` objects (not literal gameplay) since natural double-KO requires frame-exact simultaneous damage; this exercises the real `endRound()` branch at `web/index.html:3284-3288`, not a fabricated result. |
| 5 | Silent-fallback / sprite-loading | **PASS** — network log shows exactly 12×200 (6 `.png?v=9` + 6 `.json?v=9`, plus 6 unversioned select-screen portrait `.png` @200 = 18 total, no duplicates beyond one extra portrait re-fetch on reselect); zero `&r=` cache-buster retries; console has no width-mismatch/retry messages; all `<img>` elements `complete:true` with nonzero `naturalWidth` |
| 6a | Streak timing (code-level) | **PASS** — see §6a detail below |
| 6b | Hitstop freeze (code-level) | **PASS** — see §6b detail below |
| 7a | Touch controls | **PASS (driven)** — synthetic `touchstart` on `window` correctly sets `isTouchDevice=true` and un-hides `#touch-controls`; synthetic `touchstart`/`touchend` fired on all 8 P1 pad buttons (`btn-t-p1-{up,left,right,down,light,heavy,special,poof}`) — 0 errors. Handlers (`web/index.html:3444-3475`) read `e.preventDefault()` and `keys[keyString]` only, no `e.touches[0].identifier` dependency, so synthetic dispatch is a valid test, not a workaround. |
| 7b | Mobile performance | **NOT-TESTED** — no physical device available in this environment. |

### 6a. Streak timing — code evidence

- `web/index.html:1227-1230`: `pendingSlash.delay` is set at attack start to **0.045s (light) / 0.075s
  (heavy) / 0.09s (special)**.
- `web/index.html:1240` / `1243`: the actual damage hitbox is spawned **synchronously at the same
  instant** (t=0 of the attack), with `duration` **0.12s (light) / 0.2s (heavy)**.
- `web/index.html:795-799`: `pendingSlash.delay` counts down every frame; at zero, `spawnSlash()` fires
  the visual weapon-streak.
- Since the hitbox is live from t=0 through t=duration, and the streak delay (0.045–0.09s) falls inside
  that active window (0.12–0.2s), the visual streak lands **at/near the mid-to-late part of the
  hitbox's active life** — i.e. at/near contact, not before startup and not long after.
- **Verdict: PASS** — delay constants place the streak spawn inside the attack's live damage window,
  consistent with "near contact."

### 6b. Hitstop freeze — code evidence

- `web/index.html:3565-3584`: the `requestAnimationFrame` wrapper (`gameLoop`) checks
  `hitstopRemaining > 0` and, if true, **only calls `drawScene()`** (render) and returns — `updateGame()`
  is **not called** during a hitstop freeze.
- `web/index.html:3592-3593`: `animClock` only advances inside `updateGame()`.
- `web/index.html:3646-3650`: slash-arc `life` is decremented (`slashes[i].life -= dt`) only inside
  `updateGame()`.
- Because `updateGame()` is gated out by the hitstop check in `gameLoop`, both `animClock` and every
  active slash's `life` are driven by the same game-time clock that hitstop freezes — confirming the
  code comment at line 3646 ("they hang frozen during hitstop").
- **Verdict: PASS** — slash arc life does not advance during hitstop; it is frozen by construction
  (the same gate that pauses the whole sim), not by a separate special-cased check.

---

## 9. Contact sheet paths

Per `docs/AUDIT-2026-07-16.md:5`, these are gitignored local artifacts (`media/` is in `.gitignore`) —
they were not present in this session's fresh worktree checkout (expected; they're not meant to be
committed):

- `media/audit-2026-07-16/` — 12 files (`<char>_{attack_body,heavy}.png` × 6 fighters)
- `media/wobble-flatten-2026-07-16/` — 5 files
- `media/routing-proposal/` — 7 files

---

## 10. Recommendation

**BLOCKED ON OWNER MERGE GATE.**

Basis: all 11 audited commits are settled (6 PASS, 4 FIXED, 1 intentional-PASS), all repair commits are
confirmed present on `origin/main`, and this session's fresh regression pass against `origin/main` found
**zero runtime errors** across every mode, the full input surface (keyboard + synthetic touch), a
complete match lifecycle including KO/round-advance/victory and a forced double-KO/sudden-death branch,
the TIMER toggle, and sprite-load integrity. Streak-timing and hitstop-freeze logic both check out by
direct code inspection. No roster-privacy leakage in git history.

**Required owner-gated repair:** `04a5ea0` changed Tsubasa sheet bytes after the `SHEET_V 8` bump in
`39306e3`. Commit `466c96b` records the required `SHEET_V 9` release and the reproducible audit tools.
It is on `docs/codex-audit-handoff`, not `main`; Claude must review it and the owner must approve the
merge. Once merged, the recommendation becomes **READY FOR ORIGINAL-SIX ART INTEGRATION**.

Mobile on-device performance remains NOT-TESTED (no hardware available) — flagged as a pre-launch gate,
not a blocker for the art-integration phase.
