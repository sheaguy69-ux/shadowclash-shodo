# EMBER — the directional Light / Heavy / Special matrix

**Status Aug 21 2026, SHEET_V 578: the mode gate is IN (`emberF2Frame`) and `gk_air1..6` is
packed — press V and his neutral air Light draws the wrapped beats, drop it and Form 1 comes
straight back. The four DIRECTIONAL rows are still owed: their art is delivered as two takes
each and picking between them is the owner's call — see `TAKE-A-vs-B.png`. His FIRST form is a
separate and larger job; 24 of its 232 cells landed in SHEET_V 577 and the other 208 are still
the deleted green version — see `SPEC-first-form.md`.**

**Measured, not read off the manifest:** `tools/drive_real_input.mjs --name ember` presses all
15 combos through `fireCombatKey` — the same funnel a keyboard uses. 30 presses, **no dead
inputs**, one collision.

## Heavy and Special are DONE

All ten slots exist with six cells each: `hneu hfwd hback hdown hup` · `sneu sfwd sback sdown sup`.
Nothing owed — in the killer form. The first form owes the same six rows in its own look.

## Light was the whole gap — four rows, and this is what each drew before

| slot | drew | problem |
|---|---|---|
| Light neutral | `elight`, 5 cells | fine |
| **Light up** | `elight` — *the same row* | duplicate of neutral, no art of its own |
| **Light fwd** | `kpush` kick, 3 cells | generic kick, not a claw move |
| **Light back** | `kheel` kick, **1 cell** | single frame |
| **Light down** | `ksweep` kick, **1 cell** | single frame |

## ⛔ THE ROWS ARE `gk_*`, NOT `gl*` — SHIPPED Aug 21, SHEET_V 578

`emberF2Frame` is in, and the first wrapped row with it: `glneu-air` is packed as
`gk_air1..6` (cells 256-261). Toggle V and his neutral air Light draws all six wrapped
beats; toggle it off and `air1..3` comes straight back. Everything else — his forward air
light, his ground light, his meteor — falls through the router untouched.

**Packing these as bare `glfwd`/`glback`/`gldown`/`glup`/`glneu` would have been wrong
twice, and the second one is the expensive one.** That family is ungated in two places:

1. `dirCells(p, F, { fwd:'glfwd', back:'glback', down:'gldown', up:'glup', neutral:'glneu' })`
   has **no fighter-id gate**, so the wrapped face would draw in his FIRST form, with
   nobody pressing V.
2. `drewDirLight(dir)` reads `{ fwd:'glfwd', back:'glback', down:'gldown' }` to decide
   whether a press becomes a **KICK** — a drawn row bypasses `executeKick` entirely. So
   packing those three names would have **silently deleted his push, heel and sweep**,
   with their wallsplat, their behind box and their low+trip.

A `gk_` prefix is invisible to both, which is what lets a mode gate exist at all. Verified
live in killer mode after the change: fwd+L `kpush1..3` KICK/46x28+wallsplat, back+L
`kheel` KICK/44x30+behind, down+L `ksweep` KICK/52x16+low — all three still fire.

### The four directional rows are still owed, and the pick is the owner's

Each comes as **two takes**. Cut, flopped, scaled and registered side by side in
`TAKE-A-vs-B.png`; no take clips the 377px cell, so this is a pose call, not a fit call.

| row | takeA scale | takeB scale |
|---|---|---|
| `gk_fwd` | 0.7002 | 0.7362 |
| `gk_back` | 0.6780 | 0.6732 |
| `gk_down` | 0.7074 | 0.7872 |
| `gk_up` | 0.6601 | 0.7619 |

Once picked: `python3 tools/sprites/pack_ember_gk.py --row <fwd|back|down|up> --src <strip>`,
then extend `emberF2Frame` to answer the grounded directional Lights the same way it
answers `gk_air`.

⛔ **The strips face RIGHT.** Every sprite in this game is authored facing LEFT and mirrored
by the engine. The packer flops each **cell** after the cut — flopping the strip whole
reverses the beat order.

⛔ **Scale is the ink-area median**, not height and not the eye. `eye_scale.py` is the house
tool and cannot be used on this form: his face is wrapped and he has no eye. A hood-width
ruler was tried and is junk on airborne poses (88px to 234px across one row, because a
horizontal body puts shoulders and claws in the top band).

## His own Shuko techniques already cover all four

From `technique-boards/` — the descriptions are the board's own words:

| slot | key | technique | why it fits |
|---|---|---|---|
| Light **up** | `glup1..6` | **4. Rising Underbelly Gouge** (*Soko Tora Asobi*) | "upward low-to-high scoop… a feline upward gouge **from beneath the guard**" |
| Light **fwd** | `glfwd1..6` | **2. Leaping Pounce Strike** (*Tobi Tora Geki*) | "**forward lunging** double-hand thrust… momentum from a low spring-loaded stance" |
| Light **back** | `glback1..6` | **6. Blindspot Flank Slash** (*Usiro Tsume Geki*) | "quick **pivot step to the outside**, then an outward backhand tearing motion" |
| Light **down** | `gldown1..6` | **1. Downward Tiger Rake** (*Tora Tsume Tensho*) | "explosive **downward** diagonal claw swipe using body weight" |

Spare, and worth keeping for the neutral light chain rather than a direction:
**3. Horizontal Crescent Tear** (*Mawa-shi Rip*) and **5. Cross-Body Double Rake** (*Juji Tsume*).

**Six beats per technique is exactly right** — every directional row on his sheet is 6 cells.

## ⛔ ALL FOUR ROWS ARE DRAWN — delivered Aug 21 2026

`RECOVERY/ember-ghostkiller/lights/` — nine strips, all 2172x724, **six beats each**.
Four directions in two takes, plus a neutral **air** light that was not asked for and fills a
slot nothing else covers.

| file | row | corner | edge | body heights (px) | spread | foot drift | median vs 260px |
|---|---|---|---|---|---|---|---|
| `glfwd-takeA.png`  | Light fwd  | 253 | none | 346 385 353 345 349 372 | 10.4% | 2px  | 351 = **1.35x** |
| `glfwd-takeB.png`  | Light fwd  | 253 | none | 298 360 327 333 328 320 | 17.2% | 0px  | 328 = **1.26x** |
| `glback-takeA.png` | Light back | 253 | none | 365 414 414 393 395 394 | 11.8% | 1px  | 395 = **1.52x** |
| `glback-takeB.png` | Light back | 253 | none | 322 300 308 344 285 322 | 17.2% | 4px  | 315 = **1.21x** |
| `glup-takeA.png`   | Light up   | 253 | none | 293 293 363 472 493 291 | 41.0% | 19px | 328 = **1.26x** |
| `glup-takeB.png`   | Light up   | 252 | none | 294 314 431 522 593 316 | 50.4% | 1px  | 374 = **1.44x** |
| `gldown-takeA.png` | Light down | 253 | none | 265 238 232 245 196 233 | 26.0% | 34px | 236 = 0.91x |
| `gldown-takeB.png` | Light down | 253 | none | 252 196 182 183 174 212 | 31.0% | 13px | 190 = 0.73x |
| `glneu-air.png`    | air light  | 253 | none | 310 284 274 277 309 214 | 31.0% | 88px | 281 = **1.08x** |

`python3 tools/measure_strip.py --check RECOVERY/ember-ghostkiller/lights/*.png` — all nine green.

**Size is solved.** The full-width layout did what it did for Kael: seven of nine clear Ember's
260px 4K minimum outright, the first Ghost Killer art to do so. The two `gldown` rows measure
short because a **crouch is short** — their own standing bookend beats are 265 and 252px, and
per the repo's scale law total ink height across different poses is not a scale signal. They
take one uniform scale set against the idle at pack time.

## ⛔ THEY ARE DRAWN FACING RIGHT — flop before packing

Every shipped ShadowClash sprite is authored **facing LEFT** and mirrored by the engine
(`ctx.scale(-p.facing,1)`). The nine archived Ghost Killer strips obey that. **These nine do
not** — hood and face sit on the right, mantle trails left, claws drive right. Confirmed by
looking at an archived beat beside a new one, not by a metric: a hood-centroid test was tried
first and called the plainly-left-facing `gk-claw-thrust` "mixed", because the hood spreads
backward over the shoulders and its centroid carries no facing signal.

`magick <in> -flop <out>` per strip, before keying. Costs nothing; skipping it packs the whole
row mirrored and every claw lands on the wrong side.

## Killer form: 9/9 pass

The face is fully wrapped on every beat of every strip — no eye. Checked on high-zoom head
crops, which is the only way this call gets made (two automated wrapped-vs-eyed classifiers
were built and both were unsound). At low zoom the highlight on the wrap reads as an amber
glint; at high zoom it is bandage, not eye.

## Which take to pack

take-A is bigger and tighter on three of four rows; take-B wins `glup` on both counts.

| row | take | why |
|---|---|---|
| `glfwd`  | **A** | +23px median body, spread 10.4% vs 17.2% |
| `glback` | **A** | +80px median body, spread 11.8% vs 17.2% |
| `gldown` | **A** | +46px median body; its 34px foot drift is the claw digging in, not a floating body |
| `glup`   | **B** | +46px median body and 1px foot drift against take-A's 19px |

Owner overrides this — both takes are archived, nothing is deleted.

## The neutral air row is a FIFTH free slot — `aneu`

Read off `ember.json`, not assumed. Ember today has **no `gl*` row at all** (so all four
directional lights really are empty) and **no `aneu` row**, which means his neutral air light
falls back to `air1..3` — three cells. The picker's air branch is as generic as the ground one:

```
if (p.attackAir && F.aneu1 !== undefined) { ... }   // no fighter-id gate
```

So `glneu-air` packs as `aneu1..6` and upgrades a 3-cell fallback to a purpose-drawn six-beat
row. Zero engine work, same as the other four. His `afwd1..6` and `aback1..6` are already drawn,
so with this row his aerial light family is complete too.

## Cell geometry, for whoever packs this

`ember.json`: `frameW` **340**, `frameH` **377**, `footY` **369**, `scale` **0.3349**, 232 cols.
His idle cell (`idle2`) carries a **207px** body in-cell.

The per-row uniform scale is **not derived here**. Body height cannot set it — these poses
differ, and the repo's own law says total ink height across different poses is not a scale
signal — and both automated head proxies tried on these strips were unsound (a whole-row hood
measure is contaminated by the outstretched arm of a lunging beat; a beat-1-only retry
re-admitted caption ink inside the figure's column). It gets set by eye against the idle head at
pack time, ONE scale for the whole row, anchored at the foot.

## Still owed

Nothing for the directional matrix — it is drawn end to end. What remains is packing work,
gated on the owner: flop all nine, key at fuzz 42, pick a take per row, set one scale per row,
append to the sheet and bump `SHEET_V` in the same commit.
