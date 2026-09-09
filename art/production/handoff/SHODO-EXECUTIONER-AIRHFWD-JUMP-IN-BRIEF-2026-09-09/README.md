# THE EXECUTIONER — AIR FORWARD HEAVY (`airhfwd1..8`) — art brief

Written 2026-09-09 by Fable 5 (Claude Code) against SHODO-EDITION at `SHEET_V 773`,
branch `shodo-edition`, served on `:9101`.
Audience: the image-generation lane (GPT / the owner's own still-generator).

**Nothing here has been generated. No paid API was called and none is proposed.**

---

## 1. Where the Executioner actually stands

Measured on 773 — all 40 of his inputs driven, three parking spots, fresh match per press:

| | distinct moves | repeats |
|---|---|---|
| ground | **16 / 20** | 4 |
| air | **9 / 20** | 11 |

He is the joint-thinnest fighter in the air on the roster. His eleven air repeats are not
eleven separate bugs — they are three columns collapsing:

| air column | what actually happens |
|---|---|
| **Special** | all five directions are the SAME move (box `96/50/28/0.16/195`) and all five draw `aneu`, his air-**Light** row |
| **Medium** | all five directions are the same move, all draw `aneu` (airborne Medium deliberately falls through to Light art — his `medium1..8` boards are standing boards) |
| **Heavy** | neutral / fwd / back / up are the same move (box `80/40/27/0.07/162`). Only **neutral** draws its own art (`hneu1..8`); fwd, back and up fall to `aneu` because `hfwd` / `hback` / `hup` are not packed. `down` is the meteor and is genuinely its own move. |
| Light | two real moves: the poke (neutral/fwd/back/down) and the `up+L` launcher |

**This row fixes exactly one of those**: the forward air Heavy — the jump-in, the button
every offensive sequence opens with. The rest is listed in §5 so nothing here pretends to
be the whole fix.

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

| owed | kind | note |
|---|---|---|
| `hback1..8`, `hup1..8` | art, engine already wired | same `dirCells` map; makes back and up air Heavy stop drawing `aneu` |
| air Special × 5 directions | **engine first, then art** | all five are one move today. There is no directional air-Special dispatch, and `sfwd`/`sback`/`sup`/`sdown` cannot draw airborne anyway — `web/index.html:13306` gates that map behind `p.isGrounded \|\| !airAttackCells(F)`, and he has an `aneu` row. Needs a design decision from the owner before any art. |
| ground Medium × 5 directions | **engine first, roster-wide** | `web/index.html:6937` fires one hitbox for MEDIUM and never reads direction, on all nine fighters. Not an Executioner problem. |
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
