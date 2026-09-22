# EMBER — the FIRST form: it is the green version, and it is live

Two questions answered here, both measured off the shipped sheet rather than remembered:
what his first form is still missing, and what of it is the deleted green look.

## ⛔ His first form IS the green version — all 232 cells of it

`web/assets/sprites/ember.png` at SHEET_V 575 is **51.5% green** by opaque ink, and it is not
patchy: **every one of his 57 rows measures 35–69% green. Not a single cell is ash.** The idle
he fights from is 48.0% green; `xidle`, the newer six-beat idle, is 48.1%.

Replacing "the old green version" therefore means the whole first form, not a touch-up. For
scale, the same measurement across all nine shipped sheets:

| sheet | green | | sheet | green |
|---|---|---|---|---|
| **ember** | **51.5%** | | kael | 0.0% |
| **shin** | **46.8%** | | mizu | 0.0% |
| mokurai | 1.4% | | oni | 0.0% |
| executioner | 0.0% | | tsubasa | 0.0% |
| exile | 0.0% | | | |

**Ember and Shin are the only two fighters live in a palette the owner has deleted.** Shin's is
a separate standing ruling — the grey scale-mail board look is canon there — but it is the same
problem and the same fix.

## What the first form is MISSING

Measured with `node tools/drive_real_input.mjs --name ember` — real key presses through
`fireCombatKey`, not a stubbed call. **30 presses, no dead inputs, one collision.**

| slot | has its own row? | what actually draws | cells |
|---|---|---|---|
| Light neutral | **no** | `elight` fallback | 5 |
| Light **up** | **no** | `elight` — *the same row*, this is the collision | 5 |
| Light **fwd** | **no** | `kpush` kick | 4 |
| Light **back** | **no** | `kheel` kick | **1** |
| Light **down** | **no** | `ksweep` kick | **1** |
| **Air** light neutral | **no** | `air1..3` fallback | 3 |
| Heavy ×5 | yes | `hneu hfwd hback hdown hup` | 6 each |
| Special ×5 | yes | `sneu sfwd sback sdown sup` | 6 each |

**Six rows, 36 beats, and his first form is complete** — five ground lights plus the air light.
Heavy and Special owe nothing.

## ⛔ The Ghost Killer rows CANNOT fill these

The nine strips in `lights/` are **killer-form art**: the whole face wrapped, no eye, ash-grey.
The first form is a visibly different fighter — green, hooded, one glowing eye. Packing those
rows as bare `glfwd`/`glback`/`gldown`/`glup` would draw them in **both** forms, so first-form
Ember's face would wrap itself without the player ever pressing V.

### It needs the router this engine already has twice

`ghostKiller` today gates exactly four things — the blind sense in `faceCx`, the disarm, the
toggle, and a tint colour. **Nothing picks art by mode.** But two fighters already do this:

```js
function shinF2Frame(p, F) {
    if (p.spec.id !== 2 || !p.kageNui || F.f2_light1_1 === undefined) return undefined;
    ...
}
```

`tsubasaF2Frame` is the same shape and owns his legs as well as his hands. Both key on
fighter + stance + a sentinel row and return `undefined` so every other draw path is untouched;
drop the stance and Form 1's art comes straight back. Ember's Ghost Killer takes the identical
shape over an `f2_`-prefixed family. **Copying an established pattern, not inventing a
mechanism** — and Oni's `mode2`, the one precedent that was *removed* from this tree, is not it.

## The replacement order, by what a match needs first

Per-row green share is in brackets — every row is a repaint, this is only the sequence.

**P1 — cannot fight without it (55 cells).** `idle` 2 (48%) · `xidle` 6 (48%) · `run` 2 (36%) ·
`run_clean` 8 (44%) · `jump` 3 (43%) · `ajump` 6 (54%) · `fall` 2 (44%) · `crouch_` 4 (62%) ·
`block` 2 (38%) · `hurt` 3 (47%) · `grabbed` 8 (57%) · `roll` 1 (45%) · `roll_` 6 (69%) ·
`kneel` 1 (42%) · `wallslide` 1 (49%)

**P2 — the 15-slot matrix (70 cells).** `elight` 5 · `light` 5 · `hneu hfwd hback hdown hup`
6 each · `sneu sfwd sback sdown sup` 6 each — **plus the six rows above that do not exist yet.**

**P3 — air and kicks (28 cells).** `air` 3 · `afwd` 6 · `aback` 6 · `kpush` 4 · `kheel` 1 ·
`ksweep` 1 · `kstomp` 1 · `upatk` 6

**P4 — his named claw kit (77 cells).** `ec` 5 · `echarge` 6 · `eheavy` 4 · `ehook` 6 ·
`elaunch` 6 · `eparry` 5 · `eretreat` 6 · `erip` 6 · `espec` 5 · `clawrend` 6 · `lowrake` 6 ·
`attack_body` 6 · `heavy` 3 · `heavy_i` 5 · `special` 2

Plus 17 uncategorised cells in 7 rows (`espec1_v`…`espec5_v`, `xblkguard`, `xblkhit`).

**232 cells to replace outright, and 36 beats that were never drawn at all.**

## The green — and the OLIVE nobody had measured

Swept all 66 archived files under `RECOVERY/` for green ink. The only Ember file carrying the
bright green is `new-style-actionsets-aug20/DELETED-green-form/ember-GREEN-form-DELETED.png`
at 45.7%, already parked as deleted.

**But his two Shuko technique boards are OLIVE, and that changes what can be used as
reference.** A first pass scored them 0.49% and 0.15% and called it trace warmth on the wrap.
That pass measured the whole file at `sat>0.22` — which counts the white page and drops a
desaturated drab entirely. Measured on the figures only at `sat>0.08`, the boards carry
**8.3% olive ink** (hue 60-170) against **0.2%** on `glfwd-takeA` and **0.1%** on
`gk-claw-thrust`. A 40x gap, and plain to see side by side.

So there is **no clean ash reference for the first form on disk.** The boards are the only art
that draws his open face; the Ghost Killer strips are the only art with the right palette.

## The first form's own art — `RECOVERY/ember-first-form/`

**Identity master: `ember-idle-10f.gif`** (owner, Aug 21: *"way better art"*). 10 distinct
frames, 313px body at 0.3% spread, foot pinned to y=328 on every frame, corner 245, zero edge
contact, **already facing LEFT**. At **1.20x** the 260px minimum it is the only Ember asset that
packs with no upscale. Palette measured off it — 76% pure neutral, zero saturation:
`#0a0a0a #1f1f1f #353535 #4a4a4a #5f5f5f #747474`, one cool accent `#5f5f74` on the scarf.

**⛔ FILE BY FACE, NOT BY CAPTION.** Open face (hood shadow, one glowing eye) = first form.
Wrapped face (bandages, no eye) = Ghost Killer. Owner ruling Aug 21: four boards captioned
*"GHOST KILLER / MOVESET 1-4"* are drawn open-faced and **the captions are the mistake — they
are first form.** The two Shuko technique boards moved on the same rule.

**Ten six-beat sequences of first-form art are on disk** — six Shuko techniques and four named
movesets, 60 frames. They cover five of the six never-drawn rows (`glneu glfwd glback gldown
glup`) and four of the five special slots. Full mapping in that directory's README.

## ⛔ THE FULL REPLACEMENT IS ORDERED — `RECOVERY/ember-first-form/`

Owner, Aug 21 2026: **replace all his old frames.** `REPLACEMENT-ORDER.md` is the tracker and
`REPLACE-P1..P4.png` are the sheets, generated from the manifest so their counts cannot drift
from it. **32 of 247 keys already have first-form art; 215 still need generating**, plus 36
beats for six rows that never existed (five of those covered by the Shuko boards, leaving only
`aneu` and `sup` uncovered).

## The earlier two P1 reference sheets

- `P1-REFERENCE-first-form.png` — **two look sources on purpose**: palette from the Ghost Killer
  strips, face from the Shuko boards. Handing a generator the boards alone rebuilds a khaki Ember.
- `P1-REFERENCE-ghost-killer.png` — one source; all four crops are approved art.

Both carry the same 55 P1 poses cropped from the shipped sheet and **desaturated on purpose** —
they are pose reference, and green source art for an ash character bleeds the old palette back
in. Each footer carries the delivery specs: 2172x724 per row, flat white background, ink off the
edge, 260px minimum body, **drawn facing LEFT**, one scale per row.

Rebuild either with `python3 tools/make_reference_sheet.py --fighter ember --form first|killer`.

The green files that did turn up are Shin's (`actionset-shin` 50.7%, `shin-idle-6f-REDO` 38.5%,
`shin-run-8f` 36.7%, `shin-taijutsu-4rows` 25.8%) and one Executioner board — his separate
ruling, not Ember's.
