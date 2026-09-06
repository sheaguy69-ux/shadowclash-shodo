# Blade-lock update — September 6, 2026

Target: SHODO-EDITION on `localhost:9101`, sprite cache revision 728.

## Combat behavior

Blade locks now clear the attacks that created them, track their exact partner, and cancel both sides on damage or reset. A stun update cannot prematurely release a fighter. Resolution preserves knockouts and turns both fighters toward each other after the winning cross-through. At either wall, the pair moves together far enough to keep its colliders and complete lock sprites inside the arena.

Attack taps feed the lock through the shared keyboard, mouse, touch and controller input path before throw-pair handling. The HUD displays pressure and remaining time. CPU effort varies independently within a bounded range so equal-tier watch opponents can win, lose or tie. Wooden binds retain their distinct sound treatment.

The existing duration (1.15 seconds), minimum hold (0.3 seconds), six-press lead, damage, push and clash cooldown remain unchanged. The mechanics and art are committed separately.

## Active art

All poses use the existing `drawSprite()` / `drawShodoFrame()` renderer. Entries are catch, settle, held A, held B, win, recoil. Repeated indices deliberately hold a stable brace where no suitable intermediate drawing exists.

| Fighter | Active cells | Contact reach, world pixels |
|---|---|---:|
| Executioner | 246, 269, 246, 269, 270, 249 | 14 |
| Mizu | 17, 17, 17, 17, 11, 19 | 21 |
| Ember | 156, 157, 157, 157, 160, 161 | 30 |
| Exile | 339, 339, 339, 339, 336, 343 | 37 |
| Oni | 514, 510, 513, 510, 509, 517 | 30 |
| Kael | 307, 309, 309, 309, 219, 17 | 47 |
| Tsubasa | 361, 362, 361, 362, 359, 360 | 30 |

Kael adds four cells from the existing Shodo lock source; only 307 and 309 are active. Cell 308 has an extra blade and is excluded; 310 does not reach the common contact area. The original 307-cell RGBA prefix is unchanged. Kael's right-authored recoil cell 17 now has its correct mirror flag.

Tsubasa adds six cells from two built-in imagegen edits matched to current Shodo construction. High guards 361–362 meet near 98 pixels above the floor; 359–360 supply win/recoil. Lower guards 357–358 remain unused. The original 357-cell RGBA prefix is unchanged. Registration uses a uniform source scale and horizontal placement; no per-pose body deformation or vertical stretching was added.

The other five fighters reuse current compatible weapon poses. Shin and Mokurai retain their existing unarmed eligibility; no fictitious blade poses were assigned. This pass does not replace the separate Oni run cycle.

## Validation

- `node tools/blade_lock_check.mjs`: 150 assertions passed, including input routing, interruption/reset, CPU timestep behavior, outcomes and knockout handling.
- `python3 tools/check_sheets_whole.py --worktree`: all nine sheets whole and consistent.
- `OUT=media/blade-lock-20260906/final-watch python3 tools/check_blade_lock_live.py`: 248 native draw samples, all 21 weapon-user pairings, both facings, all six pose phases, and 70 wall pixel checks; zero failures.
- Consecutive live animation entered through actual attack hitboxes and `processWeaponClash`, advanced its poses without drifting, then resolved. Thirty-two watch-mode CPU contests produced 10 P1 wins, 12 P2 wins and 10 ties. This sample checks varied outcomes, not a statistical balance claim.
- Independent visual review found weapon contact, consistent grounded scale, correct facing, and no active extra blades or clipping across the 21 pairings.

Local review artifacts: `media/blade-lock-20260906/final-watch/{board,pairs,consecutive}.png`, `checks.json`, `final/art-review.md`, `kael/native-final.png`, `tsubasa/raised-native-review.png`, and the per-fighter QC/registration records. Generation specifications and provenance are saved in `media/blade-lock-20260906/generation-specifications.md`; final cell mapping is in `phase-sources.json`.

Concurrent AudioSys/blade-spark edits and deletions in the held Ember review directory belong to separate work and are excluded from these commits.
