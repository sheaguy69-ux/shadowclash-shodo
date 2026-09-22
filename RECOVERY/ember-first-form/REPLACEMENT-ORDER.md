# EMBER — FULL REPLACEMENT ORDER

**Owner, Aug 21 2026: replace all his old frames.** This is the whole job, ordered so
the fighter becomes playable in the new look as early as possible.

**PACKED SO FAR: 7 rows, 34 keys** — measured off the png, not tracked by
hand: a replaced row stops being green (0.0% against the deleted version's 35-69%).
  `elight` `gk_air` `hdown` `idle` `run` `run_clean` `xidle`

**216 manifest keys over 199 unique cells in 48 rows.**

Sheets to hand the generator, one tier at a time:

- `REPLACE-P1.png` — cannot fight without it
- `REPLACE-P2.png` — the 15-slot directional matrix
- `REPLACE-P3.png` — air and kicks
- `REPLACE-P4.png` — his named claw kit

Rebuild the sheets with `tools/make_reference_sheet.py --tier`, and this file with
`tools/make_replacement_order.py`, after every delivery.


## P1 — cannot fight without it (49 cells)

| row | cells | art on disk? |
|---|---|---|
| `xidle` | 6 | ✅ **PACKED** — 0.0% green |
| `idle` | 2 | ✅ **PACKED** — 0.0% green |
| `run_clean` | 6 | ✅ **PACKED** — 0.0% green |
| `run` | 2 | ✅ **PACKED** — 0.0% green |
| `ajump` | 6 | — |
| `fall` | 2 | — |
| `crouch_` | 4 | — |
| `kneel` | 1 | — |
| `block` | 2 | — |
| `hurt` | 3 | — |
| `roll_` | 6 | — |
| `grabbed` | 8 | — |
| `wallslide` | 1 | — |


## P2 — the 15-slot directional matrix (66 cells)

| row | cells | art on disk? |
|---|---|---|
| `elight` | 6 | ✅ **PACKED** — 0.0% green |
| `hneu` | 6 | — |
| `hfwd` | 6 | — |
| `hback` | 6 | — |
| `hdown` | 6 | ✅ **PACKED** — 0.0% green |
| `hup` | 6 | — |
| `sneu` | 6 | **on disk** — movesets/ms3 — Rabid Spiral Flense |
| `sfwd` | 6 | **on disk** — movesets/ms1 — Phantom Maul Rush |
| `sback` | 6 | **on disk** — movesets/ms2 — Grave Hook Evisceration |
| `sdown` | 6 | **on disk** — movesets/ms4 — Carrion Drop Ravage (slot is a reading, not a measurement) |
| `sup` | 6 | — |


## P3 — air and kicks (30 cells)

| row | cells | art on disk? |
|---|---|---|
| `air` | 3 | — |
| `afwd` | 6 | — |
| `aback` | 6 | — |
| `kpush` | 4 | — |
| `kheel` | 1 | — |
| `ksweep` | 1 | — |
| `kstomp` | 1 | — |
| `upatk` | 6 | — |
| `xblkguard` | 1 | — |
| `xblkhit` | 1 | — |


## P4 — his named claw kit (61 cells)

| row | cells | art on disk? |
|---|---|---|
| `ec` | 5 | — |
| `echarge` | 6 | — |
| `eheavy` | 4 | — |
| `ehook` | 6 | — |
| `elaunch` | 6 | — |
| `eretreat` | 6 | — |
| `erip` | 6 | — |
| `clawrend` | 6 | — |
| `lowrake` | 6 | — |
| `espec` | 5 | — |
| `eparry` | 5 | — |


## Delivered, but the engine slot is YOURS to pick

| file | what it shows | candidate slots |
|---|---|---|
| `ember-ghostkiller/lights/gl{fwd,back,down,up}-take{A,B}.png` | the four GHOST KILLER directional lights, TWO TAKES each | the slot is settled (`gk_fwd` `gk_back` `gk_down` `gk_up`) — the TAKE is the owner's pick, see `TAKE-A-vs-B.png` |

## Where it stands

- **34 keys** are PACKED and measure 0.0% green.
- **24 keys** have art drawn on disk, not yet packed.
- **154 keys** still need generating.
- **6 beats** for the one row nothing has ever drawn — `aneu`, his
  neutral AIR light. ⛔ The leap-dive row is NOT it: beat 5 is a ground impact with
  debris, which on a 180ms airborne light draws debris in mid-air. It is a dive and it
  went to `hdown`.

## Two different size targets — do not mix them

His shipped cell is 340x377 with `footY` 369, and his idle carries a **207px** body
in-cell. The **260px** figure is the 4K re-cut minimum, a different and larger target.
So the same file can be "too small" and "the right size" at once:

| art | body | vs the 4K min | vs the cell that ships |
|---|---|---|---|
| `actionset-aug21/idle-6f.png` | 214px | 0.82x | **1.03x — drop-in** |
| `ember-idle-10f.gif` | 313px | **1.20x** | 1.51x |
| `actionset-aug21/run-6f.png` | 161px | 0.62x | 0.78x |
| `movesets/ms4` | 273px | **1.05x** | 1.32x |

Run and attack rows measure short because a lean and a crouch ARE short — pose, not
scale. Their scale gets set at pack time on head geometry, one value per row.

## ⛔ ONE ROW PER PROMPT — the whole-sheet route does not work

The four `REPLACE-P*.png` sheets are a BRIEF for a person to read. Fed to a generator
they come back as a picture OF a sheet: the four returned Aug 21 were 1024x1536 with
**50-64px** figures, a quarter of usable size, and the labels were redrawn wrong
(`htwd` for `hfwd`, `espec1_y` for `espec1_v`, `pparry5` for `eparry5`).

That is not a one-off. Across every Ember delivery, body size tracks how many rows
share one image:

| layout | bodies | vs the 260px 4K min |
|---|---|---|
| **one full-width row** 2172x724 | 285-593px | **1.10-2.28x** |
| one row, the 10-frame idle | 313px | **1.20x** |
| 3-technique board 1448x1086 | 157-197px | 0.60-0.76x |
| 4x6 action board 1491x1055 | 148-214px | 0.57-0.82x |
| whole sheet 1024x1536 | 50-64px | 0.19-0.25x |

**The more rows in one image, the smaller the body. Every time.** So `row-cards/`
holds ONE card per row — 57 of them, named `<tier>-<row>.png`. Each card is one
prompt and expects ONE full-width strip back. Rebuild them with:

```
python3 tools/make_reference_sheet.py --fighter ember --form first --rows \
  --all-tiers --out RECOVERY/ember-first-form/row-cards
```

## The trap that will cost a whole batch if it is missed

The nine light strips came back **facing RIGHT**. Every sprite in this game is authored
**facing LEFT** and mirrored by the engine. The idle master and this action set are both
correct; the generator has to stay that way, or every claw packs on the wrong side.

