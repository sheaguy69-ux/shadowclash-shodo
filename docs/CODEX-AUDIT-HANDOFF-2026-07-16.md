# Codex 11-Commit Sprite Audit Handoff — 2026-07-16

Scope: commits `6f5bacf` through `45f2f7c`, approved repairs already on `main`, current GitHub implementation through `origin/main@55cdcaa`, and cumulative repair `466c96b` on `docs/codex-audit-handoff`.

## Commit 1 — 6f5bacf — Refine ninja movement and slash effects

Status: FIXED

Changed:
- `web/index.html`: input-axis cleanup, original-art routing flag, two-cell run routing, run cadence, slash-arc rendering.
- `tools/sprites/generated_run8/*.png`: six generation references; not loaded by the game.

Checks:
- SHEET_V: `4 → 4`; correct because no loaded sheet changed.
- PNG/JSON dimensions: no runtime PNG/JSON changes.
- frame-index integrity: cumulative six-sheet check passes.
- untouched-cell comparison: not applicable.
- timing constants: no damage/startup/active/recovery/hitbox constant changed; visual slash easing changed.
- gameplay behavior: shared run cadence used a six-cell rate while original routing could display two cells.
- art/weapon identity: no runtime character art changed.
- public/private boundary: unchanged.
- runtime test: all routed states and four modes pass cumulatively.
- console/network: zero cumulative errors.

Evidence:
- `git show --stat 6f5bacf`
- `python3 tools/audit_sprite_commits.py media/audit-static-2026-07-16.json`
- `node tools/audit_runtime.mjs media/audit-runtime-2026-07-16`

Defects:
- Medium: run animation phase and selected cell count could disagree on fallback sheets.
- Root cause: run length was derived in multiple places with different priority rules.
- Affected: `web/index.html` run phase/frame selection.

Repair:
- branch: `fix/audit-2026-07-16`
- repair commit: `068404c`
- exact fix: one `runCells()` helper now owns both frame selection and cadence.
- verification after repair: 2/4/6-cell selection regression, browser runtime, zero console errors.

Remaining risk:
- None for the audited behavior.

## Commit 2 — 830ac00 — Integrate clean ninja sprint frames

Status: FIXED

Changed:
- Appended `run_clean1..4` to all six runtime sheets and manifests (`40 → 44` columns).
- Added `tools/sprites/pack_generated_run4.py`.
- Routed original-art run to the four clean sprint cells.

Checks:
- SHEET_V: `4 → 5`; pass.
- PNG/JSON dimensions: all six pass `width = frameW × cols`, `height = frameH`.
- frame-index integrity: all indices in range and unique.
- untouched-cell comparison: exact RGBA `0/40` per fighter; visible-pixel-equivalent `40/40` per fighter; all changes were RGB under `alpha=0`.
- timing constants: no combat timing changed; run display length changed from two to four approved cells.
- gameplay behavior: movement speed/collision unchanged.
- art/weapon identity: new run cells retain each public fighter identity; owner accepted the resulting sheets as the new baseline.
- public/private boundary: unchanged.
- runtime test: all six sheets load and route `RUN` to valid cell 40 cumulatively.
- console/network: zero cumulative errors.

Evidence:
- decoded RGBA differences: Ember `29,873`, Executioner `27,037`, Kael `17,259`, Mizu `16,139`, Shin `20,876`, Tsubasa `22,282`; visible changed pixels: `0` for all.
- contact sheets: `media/audit-contact-sheets-2026-07-16/830ac00-<fighter>.png`.
- JSON: `media/audit-static-2026-07-16.json`.

Defects:
- High discipline failure: the packer recreated and saved the whole canvas, changing hidden RGB in every original cell despite the byte-preservation claim.
- Root cause: fresh transparent canvas plus alpha-composite plus whole-file save.
- Affected: first 40 cells in all six sheets.

Repair:
- branch: `fix/audit-2026-07-16`
- repair commit: `068404c`
- exact fix: packers now open the existing PNG and append via canvas extension without re-encoding the original region; owner accepted current sheets as the new byte baseline.
- verification after repair: synthetic hidden-RGB regression fails before and passes after; no sprite bytes changed by the repair.

Remaining risk:
- Historical exact bytes before `830ac00` were not restored by owner decision; current baseline is authoritative.

## Commit 3 — 8ca9ff9 — Lengthen matches without weakening impacts

Status: FIXED

Changed:
- `MAX_HP 100 → 150`, `ROUND_TIME 60 → 90`, new `HEALTH_DAMAGE_SCALE = 0.88`.
- Applied health scalar to strikes, throws, armor chip, and relevant damage paths.

Checks:
- SHEET_V: `5 → 5`; no sprite change.
- PNG/JSON dimensions: unaffected; cumulative pass.
- frame-index integrity: unaffected; cumulative pass.
- untouched-cell comparison: not applicable.
- timing constants: round length changed intentionally; hitstop, stun, knockback, startup, active time, and recovery were not weakened.
- gameplay behavior: cumulative runtime confirms 150 HP, 0.88 health scalar, 90-second timer.
- art/weapon identity: unchanged.
- public/private boundary: unchanged.
- runtime test: Arcade, VS CPU, 2P, and Watch advance the timer and retain 150 HP.
- console/network: zero cumulative errors.

Evidence:
- `git diff 8ca9ff9^ 8ca9ff9 -- web/index.html`
- `media/audit-runtime-2026-07-16/cumulative-runtime.json`.

Defects:
- Medium: the health HUD still used the old 100-point assumption in the resulting commit.
- Root cause: gameplay maximum changed before HUD percentage math was updated.
- Affected: `web/index.html` HUD display only.

Repair:
- branch: original chronological series.
- repair commit: `70d6597`
- exact fix: HUD derives percentages from each player's `maxHp`.
- verification after repair: 150 HP HUD and cumulative runtime pass.

Remaining risk:
- Balance remains owner-approved pending ordinary playtesting, not an audit blocker.

## Commit 4 — 70d6597 — Sharpen sword slices and fix health HUD

Status: PASS

Changed:
- Rebuilt draw-only slash wedge geometry and gradients.
- Corrected health HUD scaling for 150 HP.

Checks:
- SHEET_V: `5 → 5`; no sprite change.
- PNG/JSON dimensions: unaffected; cumulative pass.
- frame-index integrity: unaffected; cumulative pass.
- untouched-cell comparison: not applicable.
- timing constants: no combat timing change.
- gameplay behavior: draw/HUD only.
- art/weapon identity: one tapered path per slash; no extra weapon entity.
- public/private boundary: unchanged.
- runtime test: HUD, impacts, and modes pass cumulatively.
- console/network: zero cumulative errors.

Evidence:
- `git diff 70d6597^ 70d6597 -- web/index.html`
- cumulative screenshot: `media/audit-runtime-2026-07-16/cumulative-runtime.png`.

Defects:
- None.

Repair:
- branch: none.
- repair commit: none.
- exact fix: not required.
- verification after repair: not applicable.

Remaining risk:
- Visual quality remains subject to owner review during later design replacement.

## Commit 5 — 9b31e19 — Align sword streaks with horizontal cuts

Status: PASS

Changed:
- Draw-only `SLASH_ARC` angle/geometry alignment.

Checks:
- SHEET_V: `5 → 5`; no sprite change.
- PNG/JSON dimensions: unaffected; cumulative pass.
- frame-index integrity: unaffected; cumulative pass.
- untouched-cell comparison: not applicable.
- timing constants: unchanged.
- gameplay behavior: no hitbox, damage, movement, or recovery change.
- art/weapon identity: streak follows the actual cut path; no three-blade effect added.
- public/private boundary: unchanged.
- runtime test: slash rendering executes in cumulative fights.
- console/network: zero cumulative errors.

Evidence:
- `git diff 9b31e19^ 9b31e19 -- web/index.html`.

Defects:
- None.

Repair:
- branch: none.
- repair commit: none.
- exact fix: not required.
- verification after repair: not applicable.

Remaining risk:
- Human filmstrip judgment remains the final art gate, already exercised before later routing merge.

## Commit 6 — 296ac3c — Time universal weapon streaks to contact

Status: FIXED

Changed:
- Added one deferred `pendingSlash`, released on hit contact or scheduled whiff contact.

Checks:
- SHEET_V: `5 → 5`; no sprite change.
- PNG/JSON dimensions: unaffected; cumulative pass.
- frame-index integrity: unaffected; cumulative pass.
- untouched-cell comparison: not applicable.
- timing constants: visual delays light `0.045`, heavy `0.075`, special `0.09`; combat frame data unchanged.
- gameplay behavior: hitstop freezes the released streak at contact.
- art/weapon identity: one streak per attack path.
- public/private boundary: unchanged.
- runtime test: attack/contact paths and clashes pass cumulatively.
- console/network: zero cumulative errors.

Evidence:
- `git diff 296ac3c^ 296ac3c -- web/index.html`
- `media/audit-runtime-2026-07-16/cumulative-runtime.json`.

Defects:
- High: an interrupted attacker could retain `pendingSlash`, then emit a phantom streak while stunned.
- Root cause: interruption transitions and parry did not clear the deferred visual.
- Affected: `takeDamage` actual-stun transition and parry attacker-stun path.

Repair:
- branch: `fix/audit-2026-07-16`
- repair commit: `068404c`
- exact fix: clear only on actual interruption immediately before `STUNNED`, plus clear the attacker on parry; invulnerability, substitution, block, and armor paths retain valid attacks.
- verification after repair: runtime match to KO, static branch review, zero console errors.

Remaining risk:
- None for interruption-scoped streak lifetime.

## Commit 7 — 864162e — Add full-body attacks and Shin flying kick

Status: OWNER-DECISION

Changed:
- Appended six `attack_body` cells to Executioner, Mizu, Tsubasa (`44 → 50`).
- Appended six `attack_body` plus six `flying_kick` cells to Shin (`44 → 56`).
- Routed approved full-body attacks and changed Shin neutral special to flying kick.

Checks:
- SHEET_V: `5 → 6`; pass.
- PNG/JSON dimensions: all four sheets pass.
- frame-index integrity: all indices in range and unique.
- untouched-cell comparison: exact `44/44` and visible `44/44` for each changed fighter.
- timing constants: normal attack frame/recovery constants preserved; Shin flying kick adds its intended rush hitbox.
- gameplay behavior: Shin neutral special is flying kick; Forward+Special still creates exactly one wire projectile.
- art/weapon identity: Shin remains hands/feet-first with one explicit wire tool.
- public/private boundary: unchanged.
- runtime test: both Shin special paths pass; all appended routes valid.
- console/network: zero cumulative errors.

Evidence:
- contact sheets: `media/audit-contact-sheets-2026-07-16/864162e-<fighter>.png`.
- cumulative runtime field: `shinIdentity: true`.

Defects:
- Owner-decision: neutral-special identity changed from tracking shuriken to flying kick.
- Root cause: deliberate moveset redesign, not an accidental code defect.
- Affected: Shin special action and sprite route.

Repair:
- branch: none.
- repair commit: none.
- exact fix: owner ruled to keep flying kick while retaining Forward+Special wire shuriken.
- verification after repair: automated neutral/forward special assertions and runtime sheet route.

Remaining risk:
- Resolved owner decision; no technical blocker.

## Commit 8 — 44b1c04 — Complete full-body attack frames for roster

Status: FIXED

Changed:
- Appended six `attack_body` cells to Ember and Kael (`44 → 50`).

Checks:
- SHEET_V: `6 → 6`; failed in the original commit.
- PNG/JSON dimensions: both sheets pass.
- frame-index integrity: all indices in range and unique.
- untouched-cell comparison: Ember exact/visible `44/44`; Kael exact/visible `44/44`.
- timing constants: no code or gameplay timing change.
- gameplay behavior: no collision/hitbox change.
- art/weapon identity: Ember retains two claws and no swords; Kael retains short/long sword identity.
- public/private boundary: unchanged.
- runtime test: both sheets load and all states route cumulatively.
- console/network: zero cumulative errors.

Evidence:
- contact sheets: `media/audit-contact-sheets-2026-07-16/44b1c04-{ember,kael}.png`.
- static JSON: `media/audit-static-2026-07-16.json`.

Defects:
- High release-discipline failure: loaded sheet bytes/manifests changed without `SHEET_V` bump.
- Root cause: sprite-only follow-up omitted the cache version.
- Affected: Ember/Kael cache consistency.

Repair:
- branch: `fix/audit-2026-07-16`
- repair commit: `068404c`
- exact fix: `SHEET_V 6 → 7` covering the missed sheet release.
- verification after repair: all six real sheets load with matching dimensions and no fallback.

Remaining risk:
- None after version repair.

## Commit 9 — dce49c3 — Add directional throws and weapon clashes

Status: OWNER-DECISION

Changed:
- Added staged forward/back throws and armed-hitbox weapon clashes.
- `THROW_TIME = 0.38`, `THROW_RELEASE = 0.56`, throw stun `0.68`, clash hitstop `115`, clash recovery floor `0.16`.

Checks:
- SHEET_V: `6 → 6`; no sprite change.
- PNG/JSON dimensions: unaffected; cumulative pass.
- frame-index integrity: unaffected; cumulative pass.
- untouched-cell comparison: not applicable.
- timing constants: intentional throw/clash timing inventory above; unrelated timing unchanged.
- gameplay behavior: back throw crosses and launches behind; only overlapping `canClash` hitboxes clash and both are consumed.
- art/weapon identity: Shin body attacks and command kicks remain non-clashing; armed roster attacks clash.
- public/private boundary: unchanged.
- runtime test: `backThrow: true`, `clash: true`, hitstop `>=115`.
- console/network: zero cumulative errors.

Evidence:
- `git diff dce49c3^ dce49c3 -- web/index.html`
- `media/audit-runtime-2026-07-16/cumulative-runtime.json`.

Defects:
- Owner-decision: deliberate combat-feel expansion (throws/clashes), not a safe audit-only change.
- Root cause: approved feature design.
- Affected: throw and weapon-collision systems.

Repair:
- branch: none.
- repair commit: none.
- exact fix: owner ruled balance changes stay; playtest judges future tuning.
- verification after repair: automated directional throw and eligible-clash assertions.

Remaining risk:
- Balance tuning is an owner/playtest concern, not a correctness blocker.

## Commit 10 — 0d46b0a — Polish character animation and normalize Kael scale

Status: PASS

Changed:
- Added visual attack exposure timing, contact shadow/transform polish, idle cadence adjustment, and Kael render-only scale `0.95`.

Checks:
- SHEET_V: `6 → 6`; no sprite bytes changed.
- PNG/JSON dimensions: unaffected; cumulative pass.
- frame-index integrity: unaffected; cumulative pass.
- untouched-cell comparison: not applicable.
- timing constants: visual exposure array only; gameplay startup/active/recovery unchanged.
- gameplay behavior: Kael collision rectangle, reach, hitboxes, and feet anchor unchanged.
- art/weapon identity: render transform only.
- public/private boundary: unchanged.
- runtime test: Kael loads and routes every state; later owner-approved routing normalized him to `1.0` without gameplay changes.
- console/network: zero cumulative errors.

Evidence:
- `git diff 0d46b0a^ 0d46b0a -- web/index.html`
- current cumulative route/sheet result in runtime JSON.

Defects:
- None in the audited commit.

Repair:
- branch: none.
- repair commit: none.
- exact fix: not required.
- verification after repair: not applicable.

Remaining risk:
- Proportion judgment belongs to the owner-facing polished-design pass.

## Commit 11 — 45f2f7c — Add private-roster silhouettes to public select

Status: PASS

Changed:
- Added three non-playable locked cards with slot numerals and generic weapon-shape keywords.

Checks:
- SHEET_V: `6 → 6`; no sprite change.
- PNG/JSON dimensions: unaffected; cumulative pass.
- frame-index integrity: unaffected; cumulative pass.
- untouched-cell comparison: not applicable.
- timing constants: unchanged.
- gameplay behavior: public playable roster remains six.
- art/weapon identity: locked cards remain black silhouettes.
- public/private boundary: no private names, portraits, stats, mechanics, playable IDs, or revealing asset filenames in `web/`.
- runtime test: six real playable sheets load; no private fighter is instantiated.
- console/network: zero cumulative errors.

Evidence:
- `rg -n -i 'kunoichi|\boni\b|mokurai|ruby jewel|kanabo|kusarigama' web` returns no matches.
- `LOCKED_ROSTER_SLOTS` and six-entry `NINJA_ROSTER` inspection.

Defects:
- None.

Repair:
- branch: none.
- repair commit: none.
- exact fix: not required.
- verification after repair: not applicable.

Remaining risk:
- Private prototype must remain outside public repository paths.

# Final Output

## Executive summary

- Original result: 5 PASS, 4 FIXED, 2 OWNER-DECISION (both owner-resolved).
- Previously approved repair `068404c` fixed run-cadence ownership, future byte preservation, missed `SHEET_V 7`, and interruption-scoped phantom slashes.
- Cumulative audit found one additional cache defect: owner-directed Tsubasa bytes changed in `04a5ea0` after `SHEET_V 8`. Repair `466c96b` bumps `SHEET_V 9` and removes the favicon 404.
- Exact repaired tree passes all six sheet dimensions/indices, all routed states, all four modes, keyboard, touch, directional throw, weapon clash, Shin identity, 150 HP/0.88/90s, and double KO with zero console/network errors.

## Commit table

| N | Commit | Status |
|---:|---|---|
| 1 | `6f5bacf` | FIXED |
| 2 | `830ac00` | FIXED |
| 3 | `8ca9ff9` | FIXED |
| 4 | `70d6597` | PASS |
| 5 | `9b31e19` | PASS |
| 6 | `296ac3c` | FIXED |
| 7 | `864162e` | OWNER-DECISION — resolved: keep flying kick + wire tool |
| 8 | `44b1c04` | FIXED |
| 9 | `dce49c3` | OWNER-DECISION — resolved: keep throws/clashes/balance |
| 10 | `0d46b0a` | PASS |
| 11 | `45f2f7c` | PASS |

## Repair commits and branches

| Branch | Commit | Repair |
|---|---|---|
| `fix/audit-2026-07-16` | `068404c` | run-cell single source, composite-only packers, `SHEET_V 7`, scoped pending-slash clears |
| `art/wobble-flatten` | `39306e3`, `04a5ea0` | owner-approved live-cell flatten/re-anchor, contact sheets reviewed |
| `docs/codex-audit-handoff` | `466c96b` | `SHEET_V 9`, favicon clean-network fix, reproducible static/runtime/contact-sheet tools |

## SHEET_V history

| Point | Version | Result |
|---|---:|---|
| `6f5bacf` | 4 | no runtime sheet change |
| `830ac00` | 5 | correct bump for six appended run groups |
| `864162e` | 6 | correct bump for appended full-body groups |
| `44b1c04` | 6 | defect: Ember/Kael bytes changed without bump |
| `068404c` | 7 | repaired missed `44b1c04` release |
| `39306e3` | 8 | correct bump for wobble flatten |
| `04a5ea0` | 8 | defect: Tsubasa bytes changed without bump |
| `466c96b` | 9 | repaired current cache release |

## Byte-comparison totals

| Fighter | `830ac00` exact / visible | Later append exact | Visible changed pixels in claimed-untouched cells |
|---|---:|---:|---:|
| Executioner | 0/40 exact; 40/40 visible | 44/44 | 0 |
| Mizu | 0/40 exact; 40/40 visible | 44/44 | 0 |
| Shin | 0/40 exact; 40/40 visible | 44/44 | 0 |
| Tsubasa | 0/40 exact; 40/40 visible | 44/44 | 0 |
| Ember | 0/40 exact; 40/40 visible | 44/44 | 0 |
| Kael | 0/40 exact; 40/40 visible | 44/44 | 0 |

Decoded-cell total: `264/504` exact because `830ac00` normalized hidden RGB; `504/504` visually identical. Owner accepted the post-`830ac00` sheets as the new exact baseline; subsequent append commits preserve that baseline `264/264` exactly.

## Timing constants before/after

| System | Before | After | Decision |
|---|---:|---:|---|
| Max HP | 100 | 150 | keep |
| Health damage scalar | 1.0 implicit | 0.88 | keep |
| Round timer | 60s | 90s | keep |
| Throw staging | immediate/0.30 recovery | `THROW_TIME 0.38`, release 0.56 | keep |
| Throw victim stun | prior direct throw behavior | 0.68s | keep |
| Clash hitstop | none | 115ms | keep |
| Clash recovery floor | none | 0.16s | keep |
| Slash release | immediate visual | 45/75/90ms light/heavy/special or hit contact | fixed interruption cleanup |

Unchanged: gravity, ordinary hitbox geometry for visual-only commits, ordinary startup/active/recovery, base hitstop outside intentional throw/clash work, and collision rectangles.

## Public/private leakage report

- Public playable roster: six.
- Locked slots: three black, non-playable silhouettes.
- Private names/mechanics/assets in `web/`: zero detected.
- Private runtime snapshot remains in the owner-only Second Brain, outside public asset paths.

## Runtime regression matrix

| Area | Result |
|---|---|
| Six real sheets | PASS — ready, correct width/height, no fallback |
| All named routed states | PASS — valid in-range frame for all six |
| Arcade | PASS |
| VS CPU | PASS |
| Two Players | PASS |
| Watch | PASS |
| Keyboard combat path | PASS |
| Touch combat path | PASS |
| Directional back throw | PASS |
| Eligible weapon clash | PASS |
| Shin flying kick + wire tool | PASS |
| 150 HP / 0.88 scalar / 90s | PASS |
| Double KO | PASS |
| Console/network | PASS — zero errors |

Machine evidence: `media/audit-runtime-2026-07-16/cumulative-runtime.json` and `cumulative-runtime.png`. Prior owner/Claude runtime gates also completed full fights to KO across all six fighters; the current automated matrix covers every mode and audited mechanic deterministically.

## Contact sheets

- Original commit groups: `media/audit-contact-sheets-2026-07-16/{830ac00,864162e,44b1c04}-*.png`.
- Owner-approved repair groups: `media/audit-contact-sheets-2026-07-16/{39306e3,04a5ea0}-*.png`.
- Reproduce: `python3 tools/audit_contact_sheets.py media/audit-contact-sheets-2026-07-16`.

## Recommendation

**BLOCKED** only on Claude review and owner approval/merge of `466c96b` from `docs/codex-audit-handoff`. After that one cache-discipline repair lands, the gate recommendation becomes **READY FOR ORIGINAL-SIX ART INTEGRATION**. Do not merge this branch into `main` without the owner command.
