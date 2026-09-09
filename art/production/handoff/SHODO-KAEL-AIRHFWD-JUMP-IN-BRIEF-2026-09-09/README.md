# KAEL — AIR FORWARD HEAVY (`airhfwd1..8`) — art brief for the outside generator

Written 2026-09-09 by Fable 5 (Claude Code) against SHODO-EDITION at `SHEET_V 773`,
HEAD `bba7c4c`, branch `shodo-edition`, served on `:9101`.
Audience: the image-generation lane (GPT / the owner's own still-generator).

**Nothing in this folder has been generated. This is a brief and a set of measured
references cut from the CURRENT sheet.** No paid API was called and none is proposed.

---

## 1. Why this row and not another

A full roster sweep on 773 drove every input — 9 fighters × 5 directions × 4 buttons
(L/M/H/S) × grounded and airborne, at three parking spots, with a fresh match before every
single press. Reproduce it with:

```bash
SHADOWCLASH_URL=http://localhost:9101/index.html python3 tools/audit_move_coverage.py
```

It found **zero dead inputs** and **94 redundant inputs of 360**. The redundancy is not
spread evenly — it is concentrated in the air, and one missing family explains most of it:

| air-directional attack row | fighters that have it packed |
|---|---|
| `airhfwd` (air forward Heavy) | **1 of 9** — Oni only, and only 4 cells |
| `hback` (back Heavy) | 0 of 9 |
| `hup` (up Heavy) | 1 of 9 — Oni |
| `hfwd` (ground forward Heavy) | 1 of 9 — Oni |

Everyone else's air Heavy in every direction falls through to the generic air-Light row
(`aneu` / `bair` / `kxcut`), which is why the sweep reports `air fwd+H == back+H == up+H`
on the Executioner and Shin and `neutral+H == fwd+H == back+H == up+H` on Mizu, Tsubasa,
Ember, Kael and Exile.

**The engine already reads this key.** `web/index.html:13239`:

```js
const forward = F.airhfwd1 !== undefined ? 'airhfwd' : 'hfwd';
const c = dirCells(p, F, { fwd: forward, back: 'hback', up: 'hup',
                           down: 'hdown', neutral: 'hneu' });
const track = forward === 'airhfwd' && p.attackDir === 'fwd' ? 'airheavy' : 'heavy';
```

So this row is **art owed, not routing owed** — the engine's own note at `SHEET_V 714`
says exactly that: *"The fighters still showing aneu on fwd/back/up have no hfwd/hback/hup
packed either — also art owed, listed rather than faked."* Pack eight cells under
`airhfwd1..8` and they are live on Kael's jump-in with **zero engine changes**.

Kael is first because his air column is the joint-worst on the roster (**8 distinct moves
of 20**), and because his own sheet already carries the two rows this one has to sit
between at one scale: `kxcut` (air Light) and `ajump` (the jump arc).

---

## 2. The move

**Kael — air forward + Heavy — "Diving Twin Fang".**

Kael is Niten Ichi-ryū: **one long katana and one short wakizashi**, and the game's rule
for him is that the short blade parries while the long blade cuts, together. His grounded
Heavy (`kdual`) is the two-blade committed swing on the floor. This row is its airborne
sibling: a jump-in, thrown forward and DOWN out of a rising jump.

Neutral air Light (`kxcut`) is a horizontal X in front of him. This must not look like it.
The read on screen is a **descending diagonal**, committed, both blades stacked on one line
so the silhouette reads as a single falling wedge. See `refs/05` — Oni's packed `airhfwd`
is the only precedent in the game for this pose family, and it is the shape to match:
body tilted forward over the front knee, blade sweeping down-forward, cloak trailing up
and behind.

---

## 3. What ships back

Eight cells, one image, one row, in Kael's existing Shodo treatment.

- `FRAME-BY-FRAME.md` — the eight numbered beats, the scale contract, and the NEVER list.
  This is the generation brief. Read it before drawing anything.
- `frames.json` — the runtime frame data (timing, vectors, red strike rectangles, green
  body rectangles) so the row can be wired the moment the art is approved.
- `refs/` — five strips cut from the CURRENT 773 sheet at source resolution, each with
  Kael's `footY 312` drawn as a red line.
- `GRADE-TABLE.md` — the binding 12-dimension inspection. **No cell packs without a grade.**
  Fill it in and send it back WITH the contact sheet; a batch above 30% REDO/REJECT does
  not ship, it changes method.

---

## 4. Provenance discipline — the rule that got two packages thrown out

Two handoffs were rejected by Anthony on 2026-09-02 for one reason: **an old, dead
animation was used as a choreography reference.** New paint, dead poses. See
`docs/GPT-HANDOFF-REFERENCE-DISCIPLINE-2026-09-02.md`.

For this row:

- **Draw only from the five strips in `refs/`.** They are cut from the sheet the game is
  serving right now, not from an archive, not from a board, not from a recovered lineage.
- Do **not** open `RECOVERY/`, do not use any pre-August frame, and do not use a comic
  panel or a Story Bible illustration for body construction.
- If a reference is wrong about who Kael is, it is not right about how he moves either.
  A source demoted for identity cannot be promoted for choreography.

---

## 5. How it lands after approval (for the packing lane, not the generator)

1. Owner sees the montage and the 12-dimension grade table. **Nothing packs before that**
   — never change on-screen art without showing the frames first.
2. Pack append-only onto `web/assets/sprites/kael.png`. Kael is `cols 311` today, so the
   eight new cells are **311–318** and `cols` becomes **319**. Every original cell stays
   byte-identical; the appender must set `cols = pngWidth / frameW` or the game refuses
   to load the sheet.
3. Add `airhfwd1..8` to `frames` in `web/assets/sprites/kael.json`. No other key changes.
4. Bump `SHEET_V` in `web/index.html` in the **same commit** as the sprite change, or the
   cached png/json mismatch renders an invisible ninja.
5. Verify by WATCHING it: capture consecutive live-loop frames of Kael's forward+Heavy in
   the air, both facings. Cel animation cuts, it never cross-fades; a static assert cannot
   see a ghost. `python3 tools/audit_move_coverage.py --ids 5` must show Kael's air
   distinct count rise from 8/20, and `node tools/check_dir_moves.mjs` must stay green.

---

## 6. What this brief does NOT authorize

- No paid generation. The owner drives the generator himself (ruling, 2026-08-11).
- No redesign. Proportions, hood, scarf, sash, blade count and palette are fixed by
  `refs/03` and the NEVER list.
- No second row. `hback`, `hup` and Mokurai's `mstrike` are owed too and are listed in the
  coverage report, but one row per prompt — body size tracks rows-per-image.
- No engine change. If this row needs one, the brief is wrong; say so instead of packing.
