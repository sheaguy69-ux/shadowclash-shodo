# KAEL — locomotion & reaction states

Six takes delivered Aug 21 10:58. **All six are unusable for packing, and the beat counts do
not match what the engine reads.** Archived as pose reference only.

## 1. Size — ten rows on one page

Measured on the figures directly, not on row detection (a 10-row grid with a crouch row half
the height of a standing row defeats the row splitter):

| take | canvas | figures | median body | vs 260 |
|---|---|---:|---:|---:|
| 1 | 1536×1024 | 42 | 106px | **0.41×** |
| 2 | 1536×1024 | 56 | 87px | **0.33×** |
| 3 | 1536×1024 | 42 | 110px | **0.42×** |
| 4 | 1792×878 | 54 | 95px | **0.37×** |
| 5 | 1536×1024 | 57 | 88px | **0.34×** |
| 6 | 1536×1024 | 44 | 106px | **0.41×** |

The tallest single figure across all six is 172px. His attack rows, ordered one move per image,
came back at **284–539px**. Ten rows on a page is the same failure, at its extreme — 42 to 57
figures sharing one canvas.

**Same fix: one row per image, ~2172×724.**

## 2. ⛔ The engine will silently drop most of these beats

Read off `web/index.html`, not assumed. Only two of the eleven rows take any beat count:

| row | what the engine reads | accepts |
|---|---|---|
| `run_clean1..N` | `for (i=1; F['run_clean'+i]...)` | **any count** |
| `grabbed1..N` | `for (i=1; F['grabbed'+i]...)` | **any count** |
| `ajump1..6` | six named keys | exactly 6 |
| `roll_1..6` | six named keys | exactly 6 |
| `crouch_1..4` | four named keys | exactly 4 |
| `ajump1..6` covers the descent too | banded by `jumpBand(vy)` | exactly 6 |
| `hurt` `hurt2` `hurt3` | three named keys | exactly 3 |
| `block` `block2` | two named keys | exactly 2 |
| `fall` `fall2` | fallback for Exile and Mokurai only | exactly 2 |
| **`wallslide`** | **one cell** | **1** |
| **`kneel`** (KO) | **one cell** | **1** |

The takes draw 4–6 beats of wall slide and 4–6 of KO. **Every beat past the first is thrown
away** unless the engine is extended — the same shape of problem as `kheel` and `ksweep`.

## 3. What to order, and what to fix first

Order at the counts above and nothing is wasted. **Two rows got the engine change** (`3f2e...`,
see `tools/check_state_rows.mjs`) — pack them and they play:

- **`wallslide1..N`** — loops on `animPhase`, so it runs until he lets go. Was one static pose
  held through the whole descent on all nine sheets.
- **`ko1..N`** — plays once and HOLDS its last cell. A defeated fighter had no frame of his own
  at all: `hp<=0` set the hitstop, the shake and the camera punch-in, then drew whatever the
  hurt row left on screen. Note this is NOT `kneel` — `kneel` is the landing pose, so the
  board's "KNEEL / KO" row is two different engine things and wants splitting.
**`fall` is NOT a two-cell ceiling** — an earlier note here said it was and that was wrong.
Seven of nine carry `ajump1..6` and descend on `jumpBand`'s beats 5 and 6 of that banded
six-cell arc; `fall`/`fall2` only ever serves Exile and Mokurai, who keep custom arcs. A
`fall1..N` row was written, measured dead on everyone it was meant to help, and deleted.
Driving it live is what caught it — the source reads as though `fall` owns the descent.

Two real gaps found while checking that: **Shin has no `ajump2`** and **Tsubasa has no
`ajump6`**, so both have a hole in their banded jump arc.

`run_clean` and `grabbed` already loop, so a six- or eight-beat run and a six-beat grab work
the moment they are packed — zero engine work.
