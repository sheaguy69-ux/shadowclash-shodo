# KAEL — the LIGHT and AIR rows, one move per image

Aug 21 2026, 07:46. Seven strips, **2172×724, one row each** — the layout the size triage
asked for. **All seven clear his 260px minimum**, the first Kael attack art to do so.

| row | move | upright body | vs 260 | fill | beats |
|---|---|---:|---:|---:|---:|
| `L1` | Dual Slash Combo | 364px | **1.40×** | 53% | 6 |
| `L2` | Push Kick / Teep | 467px | **1.80×** | 65% | 3 |
| `L3` | Heel Turn | 438px | **1.68×** | 61% | 6 |
| `L4` | Sweep / Ashi-Barai | 358px | **1.38×** | 52% | 6 |
| `A1` | Zero-G Cross | 309px | **1.19×** | 46% | 6 |
| `A2` | Jumping X-Cut | 447px | **1.72×** | 63% | 6 |
| `A3` | Air Spin Finisher | 284px | **1.09×** | 42% | 6 |

Mechanically clean on all seven: darkest corner **253** so the fuzz-42 keyer lifts them,
**zero edge contact**, and drawn **facing LEFT**, which is the shipped convention.

Beat counts are counted off the strips by eye. The automatic split merges touching pairs — a
blade or an FX arc crossing a gap — which changes nothing about the measured body heights but
does make a run count read low. Do not read a low run count as a missing beat here.

## SPECIAL tier — 08:35, captioned with the Japanese names

| row | move | | upright | vs 260 | fill |
|---|---|---|---:|---:|---:|
| `S1` | Spinning Finisher | Kaiten-giri 回転斬り | 375px | **1.44×** | 52% |
| `S2` | Travelling Cross Slash | Fumikomi-giri 踏み込み斬り | 291px | **1.12×** | 42% |
| `S3` | Niten Parry | Jūmonji-dome 十文字止め | 340px | **1.31×** | 50% |
| `S4` | Skyward Fang | Kiriage 切り上げ | 539px | **2.07×** | 75% |
| `S5` | Rising Twin Fang | Gyaku-kesa 逆袈裟 | 420px | **1.62×** | 60% |

Corner 253, zero edge contact, facing LEFT on all five. **His whole Light, Special and Air
kit now clears 260px — twelve of his seventeen attack slots.**

### S3 beat 4 — the opponent's sword is CUT (owner, Aug 21)

The strip arrived with an attacker's crimson blade drawn into his crossed guard. Packed as-is
every Niten Parry would summon a phantom red sword whoever he was actually fighting — the same
defect the owner ruled on for the Executioner's defence board, where the grey opponent was cut.

**Cut by `tools/cut_red_blade.py`.** 3431px removed, **988px of spark preserved** — the flash is
his own contact FX and stays. Changes are confined to beat 4; the other five beats are
byte-identical, and the row still measures 340px upright with a 253 corner and no edge contact.
`kael-S3-niten-parry-AS-DELIVERED.png` keeps the original.

What made it safe rather than a repaint: the corridor the blade occupied held **1353px of red
against 69px of orange**, so the rays mostly stopped at its edge instead of running under it.
Almost nothing needed reconstructing.

⛔ **The crimson mask overlaps his own gold.** Deep orange satisfies every redness test, so a
global `red -> white` shredded the spark rays and nibbled the gold on his hood. The spark is
exempted explicitly at every stage. This also makes the obvious after-check lie: a crimson
count on the finished strip returns ~2000px *per beat*, evenly across all six, mean colour
(177, 96, 3) — his gold, blue channel at 3. The blade was (235, 146, 139). Judge it on the
distribution and the colour, never the raw count.

## HEAVY tier — 10:31, the last five slots

| row | move | | upright | vs 260 |
|---|---|---|---:|---:|
| `H1` | Cross Slash | Jūmonji-giri 十文字斬り | 325px | **1.25×** |
| `H2` | Twin Cyclone | Kuruma-giri 車斬り | 373px | **1.43×** |
| `H3` | Low Parry | Gedan-barai 下段払い | 295px | **1.13×** |
| `H4` | High Parry | Ukenagashi 受け流し | 396px | **1.52×** |
| `H5` | Low-High Scissor | Hasami-giri 鋏斬り | 372px | **1.43×** |

## The four AIR direction rows — same batch

| row | | upright | vs 260 |
|---|---|---:|---:|
| `afwd` | Forward Air Slash | 371px | **1.43×** |
| `aback` | Backward Air Slash | 342px | **1.32×** |
| `aup` | Upward Air Light | 440px | **1.69×** |
| `adown` | Downward Air Light | 302px | **1.16×** |

`afwd` and `aback` are live engine rows the 17-slot spec never counted — his aerial game is five
rows, not three. `aup` and `adown` are the two the engine gained in `2d56093`.

**⛔ The board calls it `aup`; three manifests already call it `upatk`.** The engine now reads
`aup1..N` first and falls back to `upatk1..N`, so the owner's naming and Ember's existing
`upatk1..6` both work and neither needs a repack. Verified live: Ember still returns
[79-84], Exile still returns its lone [81], Oni's own `airkick` row still wins over both.

## HIS ATTACK KIT IS COMPLETE — 21 rows, every one over 260px

Seventeen spec slots plus the four air directions. Nothing in the attack kit is owed.

## What these supersede

`../redraw-boards/kael-LIGHT-tier-4rows.png`, `kael-AIR-tier-3rows.png` and both
`kael-SPECIAL-tier-5rows-take*.png`. Same content, four
and three rows to a page, 156–241px — every row short. **Superseded, do not draw from them.**
Same for `kael-MISSING-light-air-5rows.png`, which was already superseded on arrival.

## Where they go, and what it costs

Zero engine work for six of the seven. `index.html:11006` routes all four ground directions
through `dirCells` with no fighter gate — pack L1→`glneu`, L2→`glfwd`, L3→`glback`,
L4→`gldown` and the kick fallback yields. `:11028` takes A1 as `aneu1..6` ungated. A3 packs as
`sneu`, which is already in the draw map.

A2 (air Heavy) is the one that does not have a waiting ungated key.

## Still owed on his kit

Nothing. What remains for his first form is **outside** the attack kit: locomotion and
reactions — run, jump, fall, crouch, roll, block, hurt, kneel/KO, wall slide, grabbed. 29 rows,
122 cells, all still the pre-clean-slate art. Only the idle has been redrawn.
