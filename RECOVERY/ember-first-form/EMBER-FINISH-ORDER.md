# EMBER — THE FINISH ORDER

Everything still owed, numbered in the order it should be drawn. **One row per
strip** — body size tracks how many rows share one image on every delivery measured,
so a strip that carries two rows comes back at half the size. The number on each
line is the number on its card in `row-cards/`.

**Every strip: 2172 x 724 px, flat WHITE background, beats left to right, body 260px
minimum crown-to-heel, drawn FACING LEFT, no ground shadow and no background.**

**13 strips, 77 beats — and 6 of the 13 already have their pose
drawn on a board.** Those 6 are a RE-CUT at strip size, not new art: the boards
return 148-214px bodies and the bar is 260px, so the pose is right and only the size
is wrong. **7 strips are genuinely new.**

## THE SIZE, measured — not a guess

Measured across every full-width strip delivered so far — all 2172 x 724, six beats:
median beat pitch **357px**, bodies **174-612px**. So the pitch is ~362px per beat
and the height is fixed:

| beats | strip size | note |
|---|---|---|
| 2 | **724 x 724** | |
| 3 | **1086 x 724** | |
| 4 | **1448 x 724** | |
| 5 | **1810 x 724** | |
| 6 | **2172 x 724** | the proven one, and what every delivery so far has used |
| 8 | **2896 x 724** | |

**Body 260px minimum, crown to heel.** That is the floor, not the target — bigger is
free because it gets scaled DOWN into the cell, and smaller cannot be rescued. One
delivered strip already missed it (`gldown` came back 174-265px, because a crouch
compresses; the answer is to draw the crouch BIGGER, not to accept the row).

**It gets scaled into a 340 x 377 cell, footY 369, to a 202px in-cell body** — so a 260px delivery is downscaled ~0.78x and a 400px one ~0.51x. Never upscale.


Wave order is by what he gains per strip, not by tier.


## WAVE 1 — one frame, or no frame at all

Each of these is a whole move drawn as a single still, or not drawn at all. Five strips buys back five moves, which is the best return on the sheet.

| # | row | move | beats | strip px | pose already drawn? |
|---|---|---|---|---|---|
| 01 | `kheel` | Reverse Heel Kick | **6** | **2172 x 724** | no — nothing drawn for this row |
| 02 | `epounce` | Wall Pounce | **6** | **2172 x 724** | no — nothing drawn for this row |
| 03 | `ko` | KO / death | **6** | **2172 x 724** | no — nothing drawn for this row |


## WAVE 2 — cannot fight without it

Everything he does between attacks. These play constantly, so this is the most visible green left on him.

| # | row | move | beats | strip px | pose already drawn? |
|---|---|---|---|---|---|
| 04 | `wallslide` | Wall cling | **6** | **2172 x 724** | no — nothing drawn for this row |


## WAVE 3 — the directional matrix

His air Heavy and air Special columns. Every slot is already wired; only the art is green.

| # | row | move | beats | strip px | pose already drawn? |
|---|---|---|---|---|---|
| 05 | `sback` | Grave Hook Evisceration | **6** | **2172 x 724** | ✅ YES — movesets/ms2-grave-hook-evisceration.png<br>**RE-CUT at strip size**, not re-invented |


## WAVE 4 — air normals and the last kick

| # | row | move | beats | strip px | pose already drawn? |
|---|---|---|---|---|---|
| 06 | `aback` | Reverse Air Rake | **6** | **2172 x 724** | no — nothing drawn for this row |


## WAVE 5 — his named claw kit

The moves with names on a board or in the engine.

| # | row | move | beats | strip px | pose already drawn? |
|---|---|---|---|---|---|
| 07 | `espec` | Rabid Spiral Flense | **5** | **1810 x 724** | ✅ YES — movesets/ms3-rabid-spiral-flense.png<br>**RE-CUT at strip size**, not re-invented |
| 08 | `echarge` | Phantom Maul Rush / Shred Charge | **6** | **2172 x 724** | ✅ YES — movesets/ms1-phantom-maul-rush.png<br>**RE-CUT at strip size**, not re-invented |
| 09 | `eheavy` | Cross-Body Double Rake — *Juji Tsume* | **6** | **2172 x 724** | ✅ YES — shuko-techniques-4-6.png  (technique 5, Juji Tsume)<br>**RE-CUT at strip size**, not re-invented |
| 10 | `ehook` | Ceiling Hook | **6** | **2172 x 724** | no — nothing drawn for this row |
| 11 | `eretreat` | Blindspot Flank Slash — *Usiro Tsume Geki* | **6** | **2172 x 724** | ✅ YES — shuko-techniques-4-6.png  (technique 6, Usiro Tsume Geki)<br>**RE-CUT at strip size**, not re-invented |
| 12 | `erip` | Ground Rip | **6** | **2172 x 724** | no — nothing drawn for this row |
| 13 | `clawrend` | Leaping Pounce Strike — *Tobi Tora Geki* | **6** | **2172 x 724** | ✅ YES — shuko-techniques-1-3.png  (technique 2, Tobi Tora Geki)<br>**RE-CUT at strip size**, not re-invented |


## WAVE LAST — the blade trap

Owner's call: everything else ships first, and the other fighters' parry frame counts are parked with it.

| # | row | move | beats | strip px | pose already drawn? |
|---|---|---|---|---|---|


## What each one is

**01 · `kheel` — Reverse Heel Kick**  
*back + Light* · source `engine`  
Hits BEHIND him — the read against this game's three cross-up moves. 145ms, 44x30 for 7. ⛔ ONE DRAWN CELL for the whole move. The kick tier reads `kheel1..N` as a ROW already (it landed with Kael's redraw), so six beats play the moment they are packed.

**02 · `epounce` — Wall Pounce**  
*Special on a wall* · source `engine`  
Armored claw dive off the cling — the wall is a threat angle, not a retreat. He kicks off and crosses the screen: vx 520 AWAY from the wall, vy 300 downward, 0.3s of hyper armor, box 42x34 for 13. Six beats: the cling, the coil against the wall, the kick-off, the airborne claw-first dive, the landing, the rise. Until Aug 21 2026 it had no row at all and played `sneu1..6`, his air NEUTRAL special, measured live.

**03 · `ko` — KO / death**  
*state* · source `engine`  
the engine reads `ko1..N` ungated and HOLDS the last cell — Kael is the only fighter in the roster who owns the row. Ember has none, so his death draws the hurt stagger

**04 · `wallslide` — Wall cling**  
*state* · source `engine`  
the claws in the wall — his identity move, and the launch point for Wall Pounce

**05 · `sback` — Grave Hook Evisceration**  
*air back + Special* · source `board`  
Slips to the flank, hooks the body line, drags it open, carves back.

**06 · `aback` — Reverse Air Rake**  
*air back + Light* · source `PROPOSED`  
His back air normal — the cross-up tool.

**07 · `espec` — Rabid Spiral Flense**  
*neutral + Special* · source `board`  
Coiled hunch, low scrape, full-body spiral, second tearing follow-through. In the engine it is his fast ARMORED claw dash: 0.3s of hyper armor, vx 500, box 35x30 for 14 with 5 frames of startup so a whiff is a read. `ec` draws through `espec`.

**08 · `echarge` — Phantom Maul Rush / Shred Charge**  
*forward + Special* · source `board + engine`  
Rabid forward burst from a low stalking crouch — lead claw rake, rear claw crash, finishing tear. A low ARMORED run-in that ends in a double-claw cross-tear: 420ms, armor 0.30, vx 300, boxes 52x46 for 9 at 0.16 and 58x50 for 13 at 0.26. The tear lands at the END of the travel, which is what separates it from the neutral dash.

**09 · `eheavy` — Cross-Body Double Rake — *Juji Tsume***  
*neutral + Heavy* · source `board + spec`  
Lead claw slashes inward, rear claw rips back across in a fast X. The spec's frame 7 is "BOTH claws raking inward simultaneously (crossing X — SIX streaks)" at exposure 160 HELD, so the held X is canon, not a stall. The board draws six beats; the sheet holds four.

**10 · `ehook` — Ceiling Hook**  
*up + Special* · source `engine`  
Claws hooked overhead as both feet leave together. 460ms, vy -360 — unlike the Up+Heavy launcher this COMMITS his body upward, and it is his answer to someone already above him. Box 46x120 for 15, launches at -380.

**11 · `eretreat` — Blindspot Flank Slash — *Usiro Tsume Geki***  
*back + Heavy* · source `board`  
Quick pivot step to the OUTSIDE, then an outward backhand tear across flank or temple. 340ms, travels -170 (he leaves as he cuts), box 48x42 for 10.

**12 · `erip` — Ground Rip**  
*down + Special* · source `engine`  
Both claw sets driven INTO the floor and torn forward. 440ms, LOW and it TRIPS, box 84x22 for 14, and the tear carries him along the ground. Deliberately NO armor — a low that also eats trades is a button, not a read. This is how the shortest-reach fighter in the game (reach 3) gets through a high guard.

**13 · `clawrend` — Leaping Pounce Strike — *Tobi Tora Geki***  
*forward + Heavy* · source `board`  
Forward lunging DOUBLE-hand thrust, both clawed hands into chest or throat from a low spring-loaded stance. 380ms, carries him +200, TWO boxes 44x44 for 8 at 0.09 and 0.19 — the second is the one that sends.


## Not on the list, and why

| row | why |
|---|---|
| `adown` | ✅ already ash — packed and measured 0.0% green |
| `afwd` | ✅ already ash — packed and measured 0.0% green |
| `ajump` | ✅ already ash — packed and measured 0.0% green |
| `aneu` | ✅ already ash — packed and measured 0.0% green |
| `block` | ✅ already ash — packed and measured 0.0% green |
| `crouch_` | ✅ already ash — packed and measured 0.0% green |
| `elight` | ✅ already ash — packed and measured 0.0% green |
| `eparry` | ✅ already ash — packed and measured 0.0% green |
| `fall` | ✅ already ash — packed and measured 0.0% green |
| `gk_air` | ✅ already ash — packed and measured 0.0% green |
| `grabbed` | ✅ already ash — packed and measured 0.0% green |
| `hback` | ✅ already ash — packed and measured 0.0% green |
| `hdown` | ✅ already ash — packed and measured 0.0% green |
| `hfwd` | ✅ already ash — packed and measured 0.0% green |
| `hneu` | ✅ already ash — packed and measured 0.0% green |
| `hup` | ✅ already ash — packed and measured 0.0% green |
| `hurt` | ✅ already ash — packed and measured 0.0% green |
| `idle` | ✅ already ash — packed and measured 0.0% green |
| `kneel` | ✅ already ash — packed and measured 0.0% green |
| `kpush` | ✅ already ash — packed and measured 0.0% green |
| `ksweep` | ✅ already ash — packed and measured 0.0% green |
| `lowrake` | ✅ already ash — packed and measured 0.0% green |
| `roll` | ✅ already ash — packed and measured 0.0% green |
| `roll_` | ✅ already ash — packed and measured 0.0% green |
| `run` | ✅ already ash — packed and measured 0.0% green |
| `run_clean` | ✅ already ash — packed and measured 0.0% green |
| `sdown` | ✅ already ash — packed and measured 0.0% green |
| `sfwd` | ✅ already ash — packed and measured 0.0% green |
| `sneu` | ✅ already ash — packed and measured 0.0% green |
| `sup` | ✅ already ash — packed and measured 0.0% green |
| `upatk` | ✅ already ash — packed and measured 0.0% green |
| `xblkguard` | ✅ already ash — packed and measured 0.0% green |
| `xidle` | ✅ already ash — packed and measured 0.0% green |
| `kstomp` | draws through `adown`, so one strip covers both |
| `light` | ⛔ DELETED at SHEET_V 580 — heavyCells returns eheavy above it. Never needs redrawing. |
| `heavy` | ⛔ DELETED at SHEET_V 580 — specialCells is never called for him. Never needs redrawing. |
| `heavy_i` | ⛔ DELETED at SHEET_V 580 — its one reader is gated to the Executioner. Never needs redrawing. |
| `attack_body` | ⛔ DELETED at SHEET_V 580 — the Ember branch returns before `body` is read. Never needs redrawing. |
| `special` | ⛔ DELETED at SHEET_V 580 — specialCells is never called for him. Never needs redrawing. |
| `espec1_v … espec5_v` | ⛔ DELETED at SHEET_V 580 — zero references anywhere in the engine. Never needs redrawing. |
| `jump` | KEPT on the sheet but NOT queued — never drawn — his jump plays `ajump1..6`. Kept only as the `F.roll ?? F.jump` fallback. |
| `roll` | KEPT on the sheet but NOT queued — never drawn — his dodge plays `roll_1..6`. Kept as a fallback. |
