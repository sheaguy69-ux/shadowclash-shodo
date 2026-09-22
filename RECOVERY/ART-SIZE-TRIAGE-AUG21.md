# ART SIZE TRIAGE — measured, and every wrong call I made corrected

**Aug 21 2026.** Re-measured against the archive as it stands, not as it stood when this file
was first written. **103 unique delivered files: 65 clear the bar, 8 are inside 12%, 30 fall short — but four of
those are duplicates and nine are stance boards with no engine row, so the real job is 17.**

Judged on the **worst row**, not the file. Every row of a board becomes its own animation, so a
board ships only if *every* row ships.

## ⛔ EVERYTHING I GOT WRONG, AND WHAT IT IS NOW

| I said | It is actually | how it was caught |
|---|---|---|
| Kael's special tier is **0.50×** | **0.72×** | I took the median across mixed poses; a crouch is short because it is a crouch. `scale` anchors on the upright beat. |
| **"The wide take proves rows-per-image is the variable"** | measured off a **Shin worklist board** misfiled as Kael | opened the file and looked at it |
| `takeA-edgecut` has a **cut figure** | **sword tip and FX arc** on the border; no body is cut | cropped the contact and looked |
| Score a board by its **tallest** beat | must be its **shortest** — 39/11/27 became 38/7/32 | a 0.93× board had a 0.60× row inside it |
| A row is figures if it holds **≥2 runs** | kills a real band whose beats touch — Migi-Waki read 29px | measured it |
| **Ink density** separates text from figures | runs backwards: display type 0.58-0.64, figures 0.25-0.38 | measured it on three boards |
| The short sword's tsuka is **289px** against a 294px blade | **126px**, ratio 0.43 | measured instead of eyeballing |
| **`fall` is a two-cell ceiling**, "a long drop shows one picture" | seven of nine descend on **`ajump5/6`** of a banded six-cell arc; `fall`/`fall2` serves only Exile and Mokurai | drove it live — a grafted `fall1..N` row changed nothing |
| Kael's kit is **17 attack slots** | **21 rows** — `afwd`/`aback` are live rows the spec never counted, plus `aup`/`adown` | read the manifest against the engine |
| **~20 images of real work** | **~24**, then the whole thing moved as art landed | recount |

Two more that never reached a document because they were caught first: a **crimson mask that
also eats his gold** (deep orange passes every redness test — a global red→white shredded the
spark and nibbled his hood trim), and the same leak making the obvious after-check lie — a
crimson count on the finished strip returns ~2000px *per beat*, evenly across all six, mean
colour (177, 96, 3), which is gold with the blue channel at 3.

**The pattern in all of them:** the static reading looked right and the measurement or the live
drive disagreed. The `fall` row passed a 22-assertion static check and was still dead code.

## What actually changed under the numbers

Kael's whole attack kit was redrawn one move per image while this file sat still. Twenty-one
rows now clear his 260px floor, so the boards this document used to list as owed —
`kael-LIGHT-tier-4rows`, `kael-AIR-tier-3rows`, both `kael-SPECIAL-tier-5rows` takes and
`kael-MISSING-light-air-5rows` — are **superseded, not owed**, and are excluded from the counts
above rather than being counted as debt.

## Resizing still does not rescue an undersized body

Unchanged and still measured. Contour rise 2.84px native → +13% at 0.95× → +33% at 0.82× →
double at 0.56×. **0.88× is where it stops mattering**, and pre-upscaling makes it worse: the
packer resamples to target anyway, so an upscale now just adds a second one.

## The two causes, still

**TOO MANY ROWS** — the board already fills its canvas; the rows divide it. → one move per image.
**FIGURE FLOATS** — already one row, and the fighter is small inside a big white frame. → same
canvas, fill it.

*The fighter must stand at least 45% of the image height, and never under 270 pixels tall.*

## Before you send it: four files come off the list, nine should wait

**Nothing here can be rescaled.** Upscaling is measured-fake and pre-upscaling is worse than
leaving it alone. But four of the thirty do not need drawing at all — another file already
carries the same content, and for two of them the *cut* version is the one to keep:

| drop | covered by | why |
|---|---|---|
{tbl}

Judged on normalised correlation of the whole page. Three more pairs correlate at **0.72–0.79**
and are **NOT** duplicates — they are the same fighter in similar stances on the same layout
(`3-GEDAN`↔`1-CHUDAN`, `5-MIGI-WAKI`↔`4-HIDARI-WAKI`, and a layout coincidence between
`hooded-gold-DISARM-staff` and `shin-run`). Collapsing those would lose real content.

Within the `gk-board` family only pass 1 and pass 2 are the same page (0.998). **Passes 3, 4
and 5 are genuinely different poses** (0.31–0.63 against each other) — four files, three
distinct boards.

**Nine more are the stance boards below.** They map to no engine row, so redrawing them buys
nothing until the mechanic is decided.

**That leaves 17 images of real work**, not 30.

## REDRAW — 21 files

| ratio | has | needs | rows | fill | cause | file |
|---:|---:|---:|---:|---:|---|---|
| 0.31× | 84 | 270 | 5 | 56% | TOO MANY ROWS | `executioner-katana-BOARD-1535.png` |
| 0.31× | 84 | 270 | 5 | 56% | TOO MANY ROWS | `executioner-long-katana-8rows.png` |
| 0.49× | 127 | 260 | 3 | 42% | TOO MANY ROWS | `horned-gold-technique-board.png` |
| 0.57× | 147 | 260 | 4 | 67% | TOO MANY ROWS | `gk-board-24f-pass4.png` |
| 0.58× | 157 | 270 | 2 | 37% | TOO MANY ROWS | `exec-URONAME5-metsubushi-8f.png` |
| 0.59× | 154 | 260 | 4 | 72% | TOO MANY ROWS | `gk-board-24f-pass5.png` |
| 0.61× | 159 | 260 | 2 | 33% | TOO MANY ROWS | `gk-board-12f-pass3.png` |
| 0.61× | 159 | 260 | 4 | 72% | TOO MANY ROWS | `gk-board-24f-pass2.png` |
| 0.62× | 160 | 260 | 4 | 72% | TOO MANY ROWS | `gk-board-24f-pass1.png` |
| 0.69× | 185 | 270 | 4 | 78% | TOO MANY ROWS | `exec-DEFENSE-EVASION-board-4x8-NOGREY.png` |
| 0.69× | 185 | 270 | 4 | 78% | TOO MANY ROWS | `exec-DEFENSE-EVASION-board-4x8.png` |
| 0.72× | 195 | 270 | 1 | 22% | FIGURE FLOATS | `exec-URONAME2-tsuki-8f.png` |
| 0.74× | 199 | 270 | 1 | 26% | FIGURE FLOATS | `exec-GLFWD-kirikomi-8f.png` |
| 0.77× | 192 | 250 | 4 | 86% | TOO MANY ROWS | `shin-taijutsu-4rows.png` |
| 0.79× | 214 | 270 | 1 | 31% | FIGURE FLOATS | `exec-horned-5.png` *(dup)* |
| 0.80× | 208 | 260 | 1 | 29% | FIGURE FLOATS | `hooded-gold-DISARM-staff-8f.png` |
| 0.80× | 217 | 270 | 1 | 21% | FIGURE FLOATS | `exec-GLDOWN-sune-giri-8f.png` |
| 0.81× | 218 | 270 | 1 | 31% | FIGURE FLOATS | `exec-horned-1.png` *(dup)* |
| 0.83× | 216 | 260 | 1 | 34% | FIGURE FLOATS | `kael-CORRECTED-long-short-8f.png` *(dup)* |
| 0.85× | 212 | 250 | 1 | 27% | FIGURE FLOATS | `shin-run-8f.png` |
| 0.88× | 237 | 270 | 1 | 34% | FIGURE FLOATS | `exec-horned-2.png` *(dup)* |

## KEEP — 8 files, do not redraw

| ratio | body / needs | file |
|---:|---|---|
| 0.89× | 240 / 270 | `executioner-katana-7c280c24d2da800bee551fd6f4410694.png` |
| 0.91× | 247 / 270 | `exec-horned-3.png` |
| 0.93× | 251 / 270 | `exec-horned-9.png` |
| 0.94× | 253 / 270 | `exec-horned-7.png` |
| 0.96× | 249 / 260 | `horned-gold-dualsword-alt-8f.png` |
| 0.96× | 260 / 270 | `exec-URONAME3-nukiuchi-8f.png` |
| 0.97× | 252 / 260 | `gldown-takeB.png` |
| 0.97× | 262 / 270 | `exec-GLBACK-hiki-giri-8f.png` |

## Stance boards — short, but nothing reads them

These are Kael's Nitō/Kodachi/Tachi Seihō guard boards. They are undersized **and** they map to
no manifest row and no engine branch — he has `block` (2 cells) and nothing resembling a
five-stance system. Either they are style reference, or they are a mechanic that has not been
built. Not counted as owed art until that is settled.

| ratio | has | file |
|---:|---:|---|
| 0.72× | 186 | `kael-KODACHI-SEIHO-4-6.png` |
| 0.73× | 191 | `kael-TACHI-SEIHO-1-3-board.png` |
| 0.77× | 200 | `3-GEDAN-low-water-8f.png` |
| 0.77× | 201 | `5-MIGI-WAKI-right-void-8f.png` |
| 0.80× | 209 | `4-HIDARI-WAKI-left-wind-8f.png` |
| 0.81× | 210 | `1-CHUDAN-middle-earth-8f.png` |
| 0.81× | 219 | `exec-CHUDAN-no-kamae-board-8f-NOENEMY.png` |
| 0.81× | 219 | `exec-CHUDAN-no-kamae-board-8f.png` |
| 0.85× | 222 | `kael-KODACHI-SEIHO-1-3.png` |
