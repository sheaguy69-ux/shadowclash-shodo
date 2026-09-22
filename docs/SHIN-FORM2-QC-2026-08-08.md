# SHIN FORM 2 — nine pages received, all nine packed

Aug 8 2026. All nine pages arrived at 1916 × 821. **All nine are on the sheet**,
cells 204–257, at `SHEET_V` 428. Nothing was sent back for redraw — the two
rows that failed first inspection were repaired locally.

- Sheet rows: `media/pages/shin-form2/PACKED-FROM-SHEET.png` + `REPAIRED-FROM-SHEET.png`
- Motion, cel cuts at game cadence: `media/pages/shin-form2/gif-packed/*.gif`

---

## Grade table — final, measured off the packed sheet

**Size spread is measured by ink AREA, not bounding box.** Area is pose-invariant;
bbox height is not. That distinction is the whole story of this delivery — see
"the measurement that was wrong" below.

| move | cells | beats | contact beat | size spread | scale | verdict |
|---|---|---|---|---|---|---|
| `f2_light1` Light 1 · Poke | 204–209 | 6 | beat 3 | 6.2% | 0.78 ↓ | **PACKED** |
| `f2_light2` Light 2 · Slice | 210–215 | 6 | beat 3 | 7.3% | 0.68 ↓ | **PACKED** |
| `f2_light3` Light 3 · Double Thrust | 216–221 | 6 | beat 3 | 3.6% | 0.75 ↓ | **PACKED** — best row |
| `f2_heavy1` Heavy 1 · Tsuki | 222–227 | 6 | beat 3 | 7.8% | 0.79 ↓ | **PACKED** |
| `f2_heavy2` Heavy 2 · Cross-Slice | 228–233 | 6 | beat 3 | 9.8% | 0.63 ↓ | **PACKED** |
| `f2_clow` Crouch Light · Ankle | 234–239 | 6 | beat 3 | 10.3% | 0.82 ↓ | **PACKED** |
| `f2_csweep` Crouch Heavy · Sweep | 240–245 | 6 | beat 3 | 15.1% | 0.92 ↓ | **PACKED** — the low beat is the spin, not drift |
| `f2_heavy3` Heavy 3 · Disarm Hook | 246–251 | 6 | beat 3 | **1.2%** | 0.75–0.84 ↓ | **PACKED, REPAIRED** |
| `f2_air` Air Heavy · Dive Pierce | 252–257 | 6 | beat 4 | **0.4%** | 0.80–0.92 ↓ | **PACKED, REPAIRED** |

### The twelve dimensions

| # | dimension | result |
|---|---|---|
| 1 | six real beats | ✅ all nine |
| 2 | contact beat present | ✅ all nine — the defect that killed the last three Oni rows did not recur |
| 3 | size consistency | ✅ after repair; the two worst rows now measure 1.2% and 0.4% |
| 4 | facing right | ✅ — the sweep's spin and the dive's rotation both resolve facing right by beat 6 |
| 5 | ground shadow / floor line | ✅ none on any page |
| 6 | frame numbers / captions | ✅ none |
| 7 | background purity | ✅ pure white, keys clean |
| 8 | gutter integrity | ❌ **6 of 9 pages** — worked around, see below |
| 9 | identity | ✅ dark green/teal wraps, ice-cyan eyes, low stance, consistent across all nine |
| 10 | weapon correctness | ✅ after repair — kunai only, the enemy katana is gone |
| 11 | silhouette readability | ✅ heavy outline, reads at size |
| 12 | usable scale | ✅ every cell a net downscale, single resampling |

---

## The measurement that was wrong

My first pass graded size drift by **bounding-box height** and rejected
`air_heavy_dive_pierce` at 43% spread, calling beat 1 "visibly a bigger
character." That reasoning was wrong. The dive is drawn rotated — beat 1 is
upright and beats 3–5 are horizontal — so bbox height measures the *pose*, not
the character.

Re-measured by **ink area**, which is invariant to rotation, the real size
variation was **12.8%** — in the same band as rows that passed. Same for the
hook: 23% on bbox, 11.1% on area.

Both were then normalised to ~0% and packed. **Neither page ever needed a
redraw.** The lesson is the metric: on any row with rotation or an overhead
arm, bbox height will lie, and area is the honest measure.

---

## The two repairs

### `f2_heavy3` — the enemy katana is gone

The page drew a *disarm*: beats 3–5 hooked an opponent's **katana**, held it
overhead and threw it. A second character's weapon inside Shin's cut would have
packed as a sword welded to his hand.

Removed by geometric cut in beats 3 and 4 — the blade sits up-right of the ring
fist in beat 3 and up-left of the raised fist in beat 4, so both separate
cleanly. What survives in beat 4's fist is a short dark grip that reads as his
own kunai handle. The thrown katana in beat 5 was already gone, caught by the
orphan purge.

**This also fixed the design divergence.** The slot is a *launcher* — hook the
guard on the ring pommel and rip upward. With the katana removed that is exactly
what the six beats now show: hook empty air at guard height, rip up, follow
through, settle. Size normalised 11.1% → **1.2%**.

### `f2_air` — the dive holds one size

Normalised by ink area, 12.8% → **0.4%**. The rotation stays; only the
character's size was equalised. Beats 4 and 5 remain close in pose — that is the
one thing local editing cannot fix, and it costs one exposure of a six-beat
move, so it was not worth a redraw.

---

## Gutter bleed — the one thing to change next round

Six of nine pages had FX crossing the 40 px gutter. Cutting by white gutter
therefore **failed outright** on three: `heavy2_cross_slice` segmented as **3**
figures instead of 6, because the cyan slash streaks welded neighbours together.

Two fixes, both local and free:

1. **Cut by clustering ink into six columns** instead of requiring gutters.
   Recovered all three merged pages.
2. **Purge orphan blobs by true nearest-pixel distance** to the silhouette —
   over 10 px away and under 400 px. 85 fragments removed across the sheet. A
   bbox test cannot do this: it reads 0 for both a spark hugging the blade and a
   neighbour's kunai tip 40 px away.

Streaks still have to stay inside the gutter next round. A streak crossing
*through* a body cannot be separated at all.

---

## Not a problem, despite the spec

Figures came in at **181–355 px**, under the 380–450 px the handout asked for.
That rule exists solely to guarantee the import is a downscale. Every cell on
the sheet is one. **No page was redrawn for size.**

---

## State

54 cells at 204–257, append-only — the 204 original cells verified byte-identical
and no original frame key repointed. All 54 land on footY 312. Zero far-detached
debris across all of them.

**The cells are not yet referenced by any move.** Engine wiring for the Form 2
melee kit — the light chain, the heavy chain and the crouch attacks onto his
in-stance buttons — is the next step.
