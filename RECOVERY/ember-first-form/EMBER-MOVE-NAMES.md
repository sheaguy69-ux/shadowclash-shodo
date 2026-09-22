# EMBER — every input, its name, and what it does

Names and descriptions are canon where a source says so; the cell counts and the
ash/green status are measured live off `ember.png` every time this is regenerated
(`python3 tools/make_move_names.py`). **Source** is the honest part:

| tag | meaning |
|---|---|
| `board` | a delivered board or moveset file names this move |
| `engine` | the engine names it, usually straight from an owner ruling |
| `spec` | the Wolverine claw-combo spec or the identity lock |
| **`PROPOSED`** | nobody has named it — this is a working name from what the row does, and it is yours to overrule |

**Weapon:** Tekkō-kagi — **three** parallel silver blades per hand, never four.  
**Stats:** Speed 8 · Power 7 · **Reach 3, the shortest in the game** · Defense 8.  
**He/him.** Brawler / rushdown: he has to be inside your guard to exist.


## GROUND — Light

| input | row | cells | look | name | what it does |
|---|---|---|---|---|---|
| neutral + Light | `elight` | 6 | **ASH ✅** | **Horizontal Crescent Tear** — *Mawa-shi Rip*<br>`board` | Wide horizontal hooking slash driven by hip rotation — throat, neck or ribcage. 180ms, box 20x30 for 9. His fastest button and the start of his chain. The packed ash row draws exactly this: guard, chamber, the arc, follow-through with debris, recovery, settle. |
| forward + Light | `kpush` | 7 | **ASH ✅** | **Shoving Front Kick**<br>`engine` | The teep. Shove + WALL-SPLAT, and it PUNTS a kawarimi log into whoever it slides into. 165ms, 46x28 for 5. Unarmed tier: costs no chakra, works while winded, builds only 5 stagger so it does not feed the opponent's free-escape flag. |
| back + Light | `kheel` | 1 | green 44% | **Reverse Heel Kick**<br>`engine` | Hits BEHIND him — the read against this game's three cross-up moves. 145ms, 44x30 for 7. ⛔ ONE DRAWN CELL for the whole move. The kick tier reads `kheel1..N` as a ROW already (it landed with Kael's redraw), so six beats play the moment they are packed. |
| down + Light | `ksweep` | 7 | **ASH ✅** | **Low Trip Sweep**<br>`engine` | Low and it TRIPS. 165ms, 52x16 for 7. ⛔ ONE DRAWN CELL for the whole move. Same as the heel: `ksweep1..N` is read as a row already, so this is pure art. |
| up + Light | `elight` | 6 | **ASH ✅** | **— no move of its own —**<br>`engine` | ⛔ Grounded, this replays neutral Light exactly: same 20x30 box, same 9 damage, same six cells. But Up is the JUMP key, so in real play the jump lifts him first and the input becomes the AIR up-light below. The collision only bites in the frames before he leaves the floor. Measured both ways. |

## GROUND — Heavy

| input | row | cells | look | name | what it does |
|---|---|---|---|---|---|
| neutral + Heavy | `eheavy` | 4 | green 59% | **Cross-Body Double Rake** — *Juji Tsume*<br>`board + spec` | Lead claw slashes inward, rear claw rips back across in a fast X. The spec's frame 7 is "BOTH claws raking inward simultaneously (crossing X — SIX streaks)" at exposure 160 HELD, so the held X is canon, not a stall. The board draws six beats; the sheet holds four. |
| forward + Heavy | `clawrend` | 6 | green 56% | **Leaping Pounce Strike** — *Tobi Tora Geki*<br>`board` | Forward lunging DOUBLE-hand thrust, both clawed hands into chest or throat from a low spring-loaded stance. 380ms, carries him +200, TWO boxes 44x44 for 8 at 0.09 and 0.19 — the second is the one that sends. |
| back + Heavy | `eretreat` | 6 | green 60% | **Blindspot Flank Slash** — *Usiro Tsume Geki*<br>`board` | Quick pivot step to the OUTSIDE, then an outward backhand tear across flank or temple. 340ms, travels -170 (he leaves as he cuts), box 48x42 for 10. |
| down + Heavy | `lowrake` | 6 | **ASH ✅** | **Downward Tiger Rake** — *Tora Tsume Tensho*<br>`owner` | CANON — owner, Aug 21 2026: "ok the cool u can canon it". Explosive downward diagonal swipe using body weight, hooking as it tears. Shuko technique 1. In the engine: 360ms, LOW and it TRIPS, box 62x20 for 11, and it carries him +60 along the floor. |
| up + Heavy | `upatk` · `elaunch` | 6 / 0 | **ASH ✅** / never drawn | **Rising Underbelly Gouge** — *Soko Tora Asobi*<br>`board` | Upward low-to-high scoop into the midsection or the underside of the jaw — a feline gouge from BENEATH the guard. This is his LAUNCHER: 25x76 for 21 with launch, it rises nearly in place and starts the juggle. `upatk` and `elaunch` are two names for one row. |

## GROUND — Special

| input | row | cells | look | name | what it does |
|---|---|---|---|---|---|
| neutral + Special | `espec` · `ec` | 5 / 0 | green 25% / never drawn | **Rabid Spiral Flense**<br>`board` | Coiled hunch, low scrape, full-body spiral, second tearing follow-through. In the engine it is his fast ARMORED claw dash: 0.3s of hyper armor, vx 500, box 35x30 for 14 with 5 frames of startup so a whiff is a read. `ec` draws through `espec`. |
| forward + Special | `echarge` | 6 | green 43% | **Phantom Maul Rush / Shred Charge**<br>`board + engine` | Rabid forward burst from a low stalking crouch — lead claw rake, rear claw crash, finishing tear. A low ARMORED run-in that ends in a double-claw cross-tear: 420ms, armor 0.30, vx 300, boxes 52x46 for 9 at 0.16 and 58x50 for 13 at 0.26. The tear lands at the END of the travel, which is what separates it from the neutral dash. |
| back + Special | `eparry` | 5 | **ASH ✅** | **Blade-Trap Parry** — *Tekkokagijutsu*<br>`engine + owner` | The crossed iron claws CATCH an incoming blade and answer with the X-shred. Whiff is 0.5s of honest recovery. In GHOST KILLER this same input becomes the DISARM — it takes the attacker's weapon inside a 0.035s window. It is the only parry in the roster that draws just ONE of its cells; Tsubasa's draws 2, Mokurai's 2, Kael's 4. |
| down + Special | `erip` | 6 | green 46% | **Ground Rip**<br>`engine` | Both claw sets driven INTO the floor and torn forward. 440ms, LOW and it TRIPS, box 84x22 for 14, and the tear carries him along the ground. Deliberately NO armor — a low that also eats trades is a button, not a read. This is how the shortest-reach fighter in the game (reach 3) gets through a high guard. |
| up + Special | `ehook` | 6 | green 39% | **Ceiling Hook**<br>`engine` | Claws hooked overhead as both feet leave together. 460ms, vy -360 — unlike the Up+Heavy launcher this COMMITS his body upward, and it is his answer to someone already above him. Box 46x120 for 15, launches at -380. |
| Special on a wall | `epounce` | 0 | never drawn | **Wall Pounce**<br>`engine` | Armored claw dive off the cling — the wall is a threat angle, not a retreat. He kicks off and crosses the screen: vx 520 AWAY from the wall, vy 300 downward, 0.3s of hyper armor, box 42x34 for 13. Six beats: the cling, the coil against the wall, the kick-off, the airborne claw-first dive, the landing, the rise. Until Aug 21 2026 it had no row at all and played `sneu1..6`, his air NEUTRAL special, measured live. |

## AIR — Light

| input | row | cells | look | name | what it does |
|---|---|---|---|---|---|
| air neutral + Light | `aneu` | 6 | **ASH ✅** | **Airborne Cross Rake**<br>`PROPOSED` | Six beats of a claw rake that stays AIRBORNE start to finish: no crouch, no launch, no landing, no ground debris. |
| air neutral + Light (fallback) | `air` | 0 | never drawn | **Generic Air Normal**<br>`engine` | ⛔ DEAD, NOT OWED. Three cells the whole early roster shares, and nothing on his sheet reaches them any more: `aneu1..6` wins the Light tier, `hneu` the Heavy, `sneu` the Special, and `ajump1..6` returns before the apex-spin line that read air1/air2. Verified by driving all 15 air presses. Never draw it — delete it. |
| air forward + Light | `afwd` | 6 | **ASH ✅** | **Diving Claw Rake**<br>`PROPOSED` | His forward air normal. |
| air back + Light | `aback` | 6 | green 64% | **Reverse Air Rake**<br>`PROPOSED` | His back air normal — the cross-up tool. |
| air up + Light | `upatk` · `elaunch` | 6 / 0 | **ASH ✅** / never drawn | **Rising Underbelly Gouge (air)** — *Soko Tora Asobi*<br>`board` | The same drawn row as the ground launcher, played from the air. |
| air down + Light | `adown` · `kstomp` | 6 / 1 | **ASH ✅** / green 55% | **Dive Stomp**<br>`engine` | Six beats of a claws-down stomp. `adown1..N` outranks the old shared `kstomp` cell, ungated, so the drawn row plays with no code change at all. |

## AIR — Heavy

| input | row | cells | look | name | what it does |
|---|---|---|---|---|---|
| air neutral + Heavy | `hneu` | 6 | **ASH ✅** | **Hanging Cross Tear**<br>`PROPOSED` |  |
| air forward + Heavy | `hfwd` | 6 | **ASH ✅** | **Both-Claws X-Rake Ahead**<br>`spec` |  |
| air back + Heavy | `hback` | 6 | **ASH ✅** | **Both-Claws Reverse Rake**<br>`spec` |  |
| air up + Heavy | `hup` | 6 | **ASH ✅** | **Rising Double Claw-Swipe**<br>`spec` |  |
| air down + Heavy | `hdown` | 6 | **ASH ✅** | **METEOR BREAK**<br>`engine` | The roster-wide dive slam, and his is drawn as one: tuck, commit, plunge with speed streaks, ground scuff at the feet, landed crouch, rise. Anti-grav hang telegraph, then a 2.5x-gravity plunge that SPIKES an airborne victim into a ground bounce, then a landing shockwave on BOTH sides and a real recovery tax. |

## AIR — Special

| input | row | cells | look | name | what it does |
|---|---|---|---|---|---|
| air neutral + Special | `sneu` | 6 | **ASH ✅** | **Spiral Flense (air)**<br>`PROPOSED` |  |
| air forward + Special | `sfwd` | 6 | **ASH ✅** | **Claw-First Dive Charge**<br>`spec` |  |
| air back + Special | `sback` | 6 | green 50% | **Grave Hook Evisceration**<br>`board` | Slips to the flank, hooks the body line, drags it open, carves back. |
| air down + Special | `sdown` | 6 | **ASH ✅** | **Carrion Drop Ravage**<br>`board` | Compresses low, explodes upward, dives with BOTH claws, mauling descent, hunter's crouch. The engine's own description is "downward shred, both claws below the feet". |
| air up + Special | `sup` | 6 | **ASH ✅** | **Rising Claw Hook**<br>`spec` | A single long upward tear. |

## GHOST KILLER (second form, V)

| input | row | cells | look | name | what it does |
|---|---|---|---|---|---|
| V | `—` | — | — | **GHOST KILLER**<br>`owner` | His second form. Whole face WRAPPED, no eye. Counter/disarm kit: catches a thrown sword, deflects a thrown dagger, traps a grabbing arm, blocks a punch into a grounded leg takedown, climbs walls on the claws. Back+Special becomes the DISARM. |
| air neutral + Light | `gk_air` | 6 | **ASH ✅** | **Ghost Killer — Neutral Air Light**<br>`board` | PACKED. |
| forward + Light | `gk_fwd` | 0 | never drawn | **Leaping Pounce Strike** — *Tobi Tora Geki*<br>`board` | Forward lunging double-hand thrust from a low spring-loaded stance. TWO TAKES delivered. |
| back + Light | `gk_back` | 0 | never drawn | **Blindspot Flank Slash** — *Usiro Tsume Geki*<br>`board` | Pivot step to the outside, outward backhand tear across flank or temple. TWO TAKES delivered. |
| down + Light | `gk_down` | 0 | never drawn | **Low Tearing Scrape**<br>`PROPOSED` | TWO TAKES delivered. |
| up + Light | `gk_up` | 0 | never drawn | **Rising Underbelly Gouge** — *Soko Tora Asobi*<br>`board` | Upward low-to-high scoop from beneath the guard. TWO TAKES delivered. |

## States (not attacks, but they all still need art)

| rows | cells | look | name | what it is |
|---|---|---|---|---|
| `xidle` · `idle` | 6 / 2 | **ASH ✅** / **ASH ✅** | **Stalking Idle** | the standing breath cycle — six beats, ping-ponged 1-6-2 so the loop cannot snap at the seam |
| `run_clean` · `run` | 6 / 2 | **ASH ✅** / **ASH ✅** | **Run** | the forward run — six beats, one stride cycle every 267ms |
| `jump` · `ajump` · `fall` | 3 / 6 / 2 | green 40% / **ASH ✅** / **ASH ✅** | **Jump / air / fall** | his jump is a FULL BACKFLIP: crouch, both feet leave together, tuck, full back rotation, legs reach down, two-foot landing |
| `crouch_` · `kneel` | 4 / 1 | **ASH ✅** / **ASH ✅** | **Crouch** | four crouch beats plus the kneel |
| `block` · `xblkguard` | 2 / 1 | **ASH ✅** / **ASH ✅** | **Guard** | the crossed-claw block and the guard hold — `xblkguard` is also the static cell the blade lock holds |
| `hurt` | 3 | **ASH ✅** | **Hurt** | three stagger beats paced over the stun window |
| `roll_` · `roll` | 6 / 1 | **ASH ✅** / **ASH ✅** | **Dodge roll** | six beats — everyone in the roster has a DRAWN roll, never the fallback spin |
| `grabbed` | 8 | **ASH ✅** | **Grabbed** | eight beats of being held and thrown |
| `wallslide` | 1 | green 44% | **Wall cling** | the claws in the wall — his identity move, and the launch point for Wall Pounce |
| `ko` | 0 | never drawn | **KO / death** | the engine reads `ko1..N` ungated and HOLDS the last cell — Kael is the only fighter in the roster who owns the row. Ember has none, so his death draws the hurt stagger |
