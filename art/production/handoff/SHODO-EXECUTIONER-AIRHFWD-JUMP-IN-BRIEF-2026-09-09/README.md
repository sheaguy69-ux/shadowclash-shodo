# THE EXECUTIONER — AIR FORWARD HEAVY (`airhfwd1..8`) — art brief

Written 2026-09-09 by Fable 5 (Claude Code) against SHODO-EDITION at `SHEET_V 773`,
branch `shodo-edition`, served on `:9101`.
Audience: the image-generation lane (GPT / the owner's own still-generator).

**Nothing here has been generated. No paid API was called and none is proposed.**

---

## 1. Where the Executioner actually stands

Measured on 773 — all 40 of his inputs driven, three parking spots, fresh match per press —
then **re-driven every frame and through the real key funnel**, which overturned part of the
first reading. The corrected numbers:

| | distinct moves | repeats |
|---|---|---|
| ground | **15 / 20** | 5 |
| air | **7 / 20** measured · **10 / 20** once the probe is parked correctly | 13 / 10 |

**Correction, 2026-09-09.** The first pass of this brief said his air Special was one move
across all five directions and his air Heavy one move across four. Both were partly the
ruler's fault. The sweep parks an airborne fighter at `p.vy = -40`, and two of his moves are
latched behind `this.vy < -180`:

- **air Up+Heavy is GYAKU KESA** (`60/110/26/0.16/120/launch`, cells `xrise`/`xkiriage`) — a real, distinct rising cut. A live W-then-J press reaches it. The probe never armed the latch.
- **air Up+Special is SKY CLEAVE** (`56/155/20/0.13/140/launch+up`) — also real, also missed.

So the honest air picture is **four** air Specials collapsing, not five, and **three** air
Heavies, not four.

| air column | what actually happens |
|---|---|
| **Special** | neutral / fwd / back / down are the SAME move (box `96/50/28/0.16/195`) and all draw `aneu`, his air-**Light** row. **up** is SKY CLEAVE — its own move, but it draws `aneu` too, because `xskycleave` is not packed. |
| **Medium** | all five directions are the same move, all draw `aneu` — airborne Medium deliberately falls through to the Light path, because his `medium1..8` boards are STANDING boards |
| **Heavy** | neutral / fwd / back are the same move (box `80/40/27/0.07/162`); only **neutral** draws its own art (`hneu1..8`), because `hfwd`/`hback` are not packed. **up** is Gyaku Kesa and **down** is the meteor — both real moves of their own. |
| Light | two real moves: the poke (neutral/fwd/back/down) and the `up+L` launcher |

**And his ground is not clean either — that was the bigger miss.** The sweep samples six
frames per move, which returned different subsets for different durations and hid two art
collisions. Re-driven every frame, and confirmed a second way through
`PORT=9101 node tools/drive_real_input.mjs --name executioner`:

- **`xjodan1..6` is drawn by THREE different heavies** — neutral (80/40), back (190/52 quick-draw), down (110/20 low+trip) — because `xnukiuchi`, `xiai`, `kneel`, `xsuso` and `xlow` are all absent from his manifest, so every command heavy falls through to `heavyCells` (`web/index.html:11811`).
- **`xtsuki1..3` (cells 329, 296, 297) is drawn by FIVE grounded moves** — fwd+H (the legitimate owner), down+S HARAI OTOSHI, up+S SKY CLEAVE, and both authored forward moves (SHADOW_SLICE, SMOKE_STRIKE) that name those cells outright.

None of that is this row's job. It is written into §5 so it is on the record.

---

## 2. Why this row lands with zero engine work

`web/index.html:13239` already reads the key:

```js
const forward = F.airhfwd1 !== undefined ? 'airhfwd' : 'hfwd';
const c = dirCells(p, F, { fwd: forward, back: 'hback', up: 'hup',
                           down: 'hdown', neutral: 'hneu' });
const track = forward === 'airhfwd' && p.attackDir === 'fwd' ? 'airheavy' : 'heavy';
```

He has `hneu` packed and nothing else, so `dirCells` returns null for forward and the
picker falls through to the generic air row. Pack eight cells under `airhfwd1..8` and his
jump-in draws its own animation immediately. Art owed, not routing owed — the engine's own
`SHEET_V 714` note already said so.

⛔ **Honest scope:** this changes what the move LOOKS like, not what it DOES. Forward,
back and up air Heavy share one hitbox today. If the owner wants the jump-in to also *hit*
differently from the back and up heavies, that is frame data on top of this art, and it is
his call — this brief does not assume it.

---

## 3. The move

**The Executioner — air forward + Heavy — "Falling Verdict".**

He carries **one long ōdachi**. His grounded Heavy family (`xjodan`) is the overhead
sentence delivered standing; `hneu1..8` (`refs/02`) is that same weight thrown straight
down while airborne — draw from the back, raise overhead, one committed downward cut with
a single orange brush crescent, then recovery.

This row is that cut **thrown forward and down out of a rising jump** instead of straight
below him. He is the oldest and heaviest fighter on the roster and the slowest runner
(speed 3.5) — the jump-in should read as *weight arriving*, not as a nimble dive. Big
overhead gather, one falling diagonal, long settle.

See `refs/05` — Oni's packed `airhfwd` is the only precedent in the game for this pose
family: body tilted forward over the leading knee, blade sweeping down-forward, cloth
trailing up and behind.

---

## 4. Scale contract — measured, not estimated

Every number below came off his CURRENT cells on the served 773 sheet.

| | |
|---|---|
| cell size | **388 × 496** (`frameW` 388, `frameH` 496) |
| ground line | **`footY` = 488** — the red line in every `refs/` strip |
| body ruler | **ink-area √ = 148** on his idle (`idle` 148.9, `idle2` 148.1, `xidle1` 149.1) |
| the same ruler on his air and heavy rows | `aneu1` 142.4, `aneu2` 146.0, `aneu6` 140.7, `hneu1` 144.1, `hneu6` 152.8 |
| working band | **140 – 153**, measured on the BODY with the blade and brush FX excluded |
| on screen | his idle stands **125 px** tall — he is the TALLEST fighter and must stay first by a visible margin |

**ONE uniform scale across all eight cells, anchored on his idle.** Never normalise each
cell's bounding box to the same height — a rotating, extended body genuinely changes its
box, and matching those boxes scales the extended beat about 2× against the compact one
and produces size boil.

⛔ **Do NOT use foot clearance as the airborne test on this sheet.** His cells are packed
foot-anchored: `idle`, `aneu1`, `hneu1` and even `ajump3` all measure a 3 px gap between
the lowest ink and the foot line, because his air poses trail a leg down. On this fighter
the airborne read comes from the POSE — trailing rear leg, no planted foot, no floor
contact art of any kind — not from a number. (Kael's sheet behaves differently; do not
carry a rule across fighters.)

---

## 5. What this row does NOT fix — the rest of his ledger

Listed so it is on the record, not so it ships in this prompt. **One row per prompt.**
Full roster context: `docs/MOVE-COVERAGE-773.md`.

| owed | kind | note |
|---|---|---|
| `xnukiuchi1..6` | art, engine already wired | the IAI QUICK-DRAW (back+H). Branch at `index.html:13151` is written and waiting. Frees `xjodan` from one of its three tenants. |
| `xsuso1..6` | art, engine already wired | SUSO-GIRI, the low sweep (down+H). Branch at `13169`. Frees `xjodan` from the third. |
| `xharai1..6` | art, engine already wired | HARAI OTOSHI (down+S). Branch at `11902`. The engine's own comment at `8258-8261` says it is borrowing until this lands. |
| `xskycleave1..6` | art, engine already wired | SKY CLEAVE. **One row fixes both the grounded and the airborne form** — `13357` sits above the generic air-row branch at `13525`. |
| `hback1..8`, `hup1..8` | art, engine already wired | same `dirCells` map as this row; stops back and up air Heavy drawing `aneu` |
| `hdown1..6` / `dive1..6` | art, engine already wired | METEOR BREAK — a 900 ms, three-hitbox move currently holding ONE cell per phase, and his standing **idle cell** for the last 14 frames of it |
| `kheel1..8`, `adown1..8` | art, engine already wired | absent on his sheet (`kheel` is absent on all nine) |
| air Special × fwd / back / down | **engine first, then art** | three of the four are one move. There is no directional air-Special dispatch, and `sfwd`/`sback`/`sdown` cannot draw airborne anyway — `index.html:13306` gates that map behind `p.isGrounded \|\| !airAttackCells(F)`, and he has an `aneu` row. Needs an owner decision before any art. |
| ground Medium × 5 directions | **engine first, roster-wide** | `index.html:6937` fires one hitbox for MEDIUM and never reads direction, on all nine. Not an Executioner problem. |
| SHEATH CHARGE / `xsheath1..6` | **neither — it is dead code** | the move at `8519` is unreachable: grounded fwd+Special is intercepted at `5842` by the authored SMOKE_STRIKE, and the only escape (`!this.gyakute`) needs a stance that `FIRST_FORM_ONLY = true` blocks. Cells 201-206 are packed art that draws nowhere. `docs/EXECUTIONER-MOVELIST.md:37` still lists it as live. **Owner call — do not delete anything.** |
| `gnd back+H == back+S` | **by design, not owed** | the owner's documented redirect; the in-game move list says *"Back+H also works"*. Leave it. |

---

## 6. Provenance discipline

Two handoffs were rejected on 2026-09-02 for one reason: an old, dead animation was used
as a choreography reference. New paint, dead poses. See
`docs/GPT-HANDOFF-REFERENCE-DISCIPLINE-2026-09-02.md`.

- **Draw only from the five strips in `refs/`.** They are cut from the sheet the game is
  serving right now — not an archive, not a board, not a recovered lineage.
- Do not open `RECOVERY/`, do not use any pre-August frame, do not use a comic panel or a
  Story Bible illustration for body construction.
- A source demoted for identity is not thereby trustworthy about motion.

---

## 7. How it lands after approval

1. Owner sees the montage and the filled-in `GRADE-TABLE.md`. Nothing packs before that.
2. Append-only onto `web/assets/sprites/executioner.png`. He is `cols 351` today, so the
   new cells are **351–358** and `cols` becomes **359**. Originals stay byte-identical, and
   the appender must set `cols = pngWidth / frameW` or the game refuses to load the sheet.
3. Add `airhfwd1..8` to `frames` in `web/assets/sprites/executioner.json`. Nothing else.
4. Bump `SHEET_V` in `web/index.html` in the **same commit** as the sprite change.
5. Verify by watching it — consecutive live-loop frames of his airborne forward Heavy, both
   facings. `python3 tools/audit_move_coverage.py --ids 0` must show his air count rise
   from 9/20, and `node tools/check_dir_moves.mjs` must stay green.
