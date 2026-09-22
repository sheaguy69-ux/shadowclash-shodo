# KAEL — REDRAW BOARDS: LIGHT TIER + AIR TIER

Delivered against `../KAEL-ATTACK-FRAME-SPECS.md`. Archived, not packed.

## ✅ The beat counts are exactly right

This is the part that matters most, and it is correct on all seven rows:

| row | slot | beats delivered | beats the engine wants | ✓ |
|---|---|---:|---:|---|
| L1 | neutral Light — Dual Slash Combo | 6 | 6 (`dual` track) | ✅ |
| **L2** | **fwd Light — Push Kick / Teep** | **3** | **3** | ✅ |
| L3 | back Light — Heel Turn | 6 | 6 | ✅ |
| L4 | down Light — Sweep / Ashi-barai | 6 | 6 | ✅ |
| A1 | air Light — Zero-G Cross | 6 | 6 | ✅ |
| A2 | air Heavy — Jumping X-Cut | 6 | 6 (`xcut` track) | ✅ |
| A3 | air Special — Air Spin Finisher | 6 | 6 | ✅ |

**L2 at three beats is deliberate and correct.** The light picker hardcodes
`[F.kpush1, F.kpush2, F.kpush3]`, so a fourth through sixth cell would never be read. Every
other row here has a six-entry timing track, and `attackCellIndex` applies a track **only**
when `track.length === cellCount` — six was a hard number and six is what came back.

**Three of these fill slots that had nothing at all**: `kheel` and `ksweep` held ONE cell
each, and air-neutral Light and air-neutral Special had no row whatsoever. A2 and A3 also mean
his aerial family is complete for the first time.

## Clean on hygiene

Background corner **252–253** on both, so the fuzz-42 keyer lifts them.

**No figure touches a border on either board.** The air board reports ink on columns 0 and
1039, but those are its own **full-width divider rules** — 1040×2 and 1040×3 components at
identical rows on both sides. Worth stating plainly because a naive edge check calls that a
straight-cutoff REDO, and it is not: every fighter sits clear of the frame.

## ⛔ The one problem: they are boards, so they are undersized

| board | rows | figures | median body | vs Kael's 260px |
|---|---:|---:|---:|---:|
| LIGHT tier | 4 | 22 | 155px | **0.60×** |
| AIR tier | 3 | 20 | 167px | **0.64×** |

Same cause as every board before them — 1040×1512 holding three or four rows leaves each
figure ~160px. The fix is the one that has worked every time: **one full-width strip per row,
~2172×724, six beats across.** That layout has returned 250–460px on every delivery, and
Kael's twin-blade string already passed outright at 269px.

So: **the content is right and the container is wrong.** Nothing about the poses, the beat
counts or the blade discipline needs changing — re-issue these same seven rows one per strip.

---

## SPECIAL TIER — all five slots, two takes

S1 neutral **Spinning Finisher** · S2 fwd **Travelling Cross Slash** · S3 back **Niten Parry** ·
S4 up **Skyward Fang** · S5 down **Rising Twin Fang**. Six beats each, 30 frames.

**Content is complete and correct** — five slots, six beats apiece, matching the specs and the
timing tracks (`spin`, `trav`, `fang` are all 6-entry).

| take | size | upright body | vs 260px | border ink |
|---|---|---:|---:|---|
| **B** *(use this one)* | 1041×1511 | 197px | 0.76× | none |
| A | 1024×1536 | 200px | 0.77× | 7px of **sword tip and FX arc** on the right — no body is cut |

Take B for the marginally cleaner page; there is nothing to choose between them on size, and
**neither has a cut figure.** Both are short and both need the same fix.

### Why they are short: five rows on one page, and the page is already full

These boards fill **64–65%** of their canvas with figures. The canvas is not being wasted —
five rows are dividing it five ways, so each fighter gets ~190px of band and lands at ~200px
of body against the 260px he needs.

That is the multi-row failure and it is the one **rows per image** actually explains. It does
not explain the single-row strips, which are short for the opposite reason — see
`RECOVERY/ART-SIZE-TRIAGE-AUG21.md`, which measures both causes across the whole delivery.

**One move per image, six beats, ~2172×724.** Same content, same beat counts, ~2.5× the body.

### ⛔ S5 still needs the `rise` track fixed — it is not an art problem

`krise` holds **six** cells and its `rise` track holds **five** entries, so `attackCellIndex`
refuses the authored timing and falls back to generic exposure. Delivering S5 at six beats is
correct and does **not** fix this on its own. Either add a sixth entry to `rise` or cut `krise`
to five cells — an engine one-liner either way, and the owner's call because it changes the
move's feel.

---

## Aug 21, 06:03 — "KAEL — MISSING LIGHT & AIR ROWS", 5 rows

`kael-MISSING-light-air-5rows.png`, 1086×1448. **Superseded on arrival — do not pack it, and
do not draw from it.** Every one of its five rows already exists on a board delivered earlier
the same day, and every one of those is bigger.

| row | same move already on | earlier | this board |
|---|---|---:|---:|
| ROW 4 `glup` *("replay of neutral light")* | LIGHT tier **L1** | **241px** | 124px |
| ROW 1 `glfwd` push kick / teep | LIGHT tier **L2** | **176px** | 156px |
| ROW 2 `glback` heel turn | LIGHT tier **L3** | **157px** | 148px |
| ROW 3 `gldown` sweep / ashi-barai | LIGHT tier **L4** | **156px** | 136px |
| ROW 5 `aneu` Zero-G Cross | AIR tier **A1** | **205px** | 116px |

Kael needs 260px. Nothing here reaches 0.60×; `aneu` lands at **0.45×**, the smallest figure in
the whole archive. Cause is the documented one — five rows on one 1448px page, 58% filled.

**Mechanically it is clean:** corner 253 so fuzz-42 lifts it, zero edge contact, and it is drawn
**facing LEFT**, which is the shipped convention (Ember's Ghost Killer lights are the odd ones
out there, not this).

### These five rows ARE genuinely missing, and they are zero engine work

`kael.json` carries **none** of `glfwd` / `glback` / `gldown` / `glup` / `aneu` / `glneu` — it has
`kpush` (c11), `kheel` (c94), `ksweep` (c93) and `air1..3` (c3-5) instead. Read off the engine,
not from memory:

- `index.html:11006` — `dirCells(p, F, { fwd:'glfwd', back:'glback', down:'gldown', up:'glup',
  neutral:'glneu' })`. **No fighter gate.**
- `index.html:5071` — the kick fallback yields the moment `kman.frames[drew+'1'] !== undefined`,
  so packing `glfwd1` is what hands Fwd+Light to the drawn row. Up was never mapped to a kick,
  which is why `glup` routes on its own.
- `index.html:11028` — `if (p.attackAir && F.aneu1 !== undefined)`, looping `aneu1..N`. **No
  fighter gate, any beat count.**

So the slots are real and filling them costs no engine work. **The art just has to be bigger.**

### Two things for the owner

1. **`glfwd` is 3 beats on BOTH boards** while every sibling row is 6. Drawn that way twice, so
   it reads as the spec rather than a slip — `dirCells` loops `glfwd1..N` and 3 plays fine.
   Confirm 3 is intended.
2. **Row 4 is captioned "REPLAY OF NEUTRAL LIGHT".** That makes Up+Light the same move as
   neutral Light. It is the exact duplicate that collides on Ember. Either it is intended (plenty
   of fighters do it) or `glup` wants its own up-angled cut.
