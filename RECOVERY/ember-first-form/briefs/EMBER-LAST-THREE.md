# EMBER — THE LAST THREE STRIPS

Everything he owes, and nothing else. Generated from the shipped sheet — every
number below was measured, not remembered.

## The spec, identical for all three

- **2172 x 724 px**, six beats left to right, evenly spaced.
- **Flat WHITE background.** No ground shadow, no scenery, no floor line — the engine draws its own.
- **FACING LEFT.** Every sprite in this game is authored left and mirrored by the engine.
- **Body 260px minimum**, crown to heel. A floor, not a target: it is scaled DOWN into a
  340 x 377 cell (footY 369), so bigger is free and smaller cannot be rescued.
- **ONE ROW PER IMAGE.** Body size tracks rows-per-image on every delivery measured —
  a strip carrying two rows comes back at half the size.

## The look — measured off his packed idle, not described

| | |
|---|---|
| palette | `#000000` `#101010` `#202020` `#303030` `#404040` `#505050` `#606060` |
| saturation | **97% of his ink is pure neutral.** Zero pixels above sat 40. No green, no olive, no colour cast. |
| face | hood shadow with ONE glowing pale eye in profile (two in three-quarter). Open face — this is FIRST form, not Ghost Killer. |
| weapon | Tekkō-kagi — **three** parallel silver blades per hand, never four. Worn, never held. |
| build | chibi, heavy black outlines, readable silhouette, controlled dark palette |
| in-cell size | his idle body packs at **202px**; his tallest shipped beat (`upatk4`) is **366px** |


## `ehook` — Ceiling Hook

**up + Special** · **2172 x 724**

*His answer to someone already above him. Both claw sets hook overhead and he goes up with them — this is not a poke, he leaves the floor entirely.*

**In the engine:** 460ms · vy -360 (it COMMITS his body upward, unlike the Up+Heavy launcher) · box 46x120 for 15 · launches the victim at -380

**Reference plate:** `briefs/REF-ehook.png` — his idle, then `upatk1`, `upatk3`, `upatk4`, `upatk6`, cut from the shipped sheet at 2x. Match THAT figure.

| beat | what it shows |
|---|---|
| **1** | Low coiled crouch, both claws drawn down and back past his hips, weight loading. Feet flat, still on the floor. |
| **2** | Explosive extension begins — knees straighten, both claws start the sweep up the centre line, hood snapping back. |
| **3** | Both feet LEAVE TOGETHER. Claws pass his chest, elbows tight, the two sets converging into one line. |
| **4** | THE HOOK. Fully extended overhead, both claw sets hooked and pointing back down behind the hands, body stretched vertical, scarf streaming straight down. Tallest beat of the row. |
| **5** | Apex tip-over — the arms open outward, wrists relax, he starts to fall. |
| **6** | Two-foot absorbing landing, knees bent deep, claws down at his sides. Back on the floor. |

**NEVER:**
- NEVER draw him still standing at beat 4 — this move leaves the ground and the row is the proof
- NEVER a one-arm reach: both claw sets go up, this is not the Up+Heavy scoop
- NEVER ground debris while he is airborne (beats 3-5)

## `erip` — Ground Rip

**down + Special** · **2172 x 724**

*How the shortest-reach fighter in the game gets through a high guard. Both claw sets go INTO the floor and tear forward, and the floor comes with them.*

**In the engine:** 440ms · LOW and it TRIPS · box 84x22 for 14 · the tear carries him forward along the ground · deliberately NO armor — a low that also eats trades is a button, not a read

**Reference plate:** `briefs/REF-erip.png` — his idle, then `lowrake1`, `lowrake3`, `lowrake4`, `lowrake6`, cut from the shipped sheet at 2x. Match THAT figure.

| beat | what it shows |
|---|---|
| **1** | Drop to a deep low stance, both claws raised high above the shoulder, points turned down at the floor. |
| **2** | The plunge — both claw sets driven straight DOWN into the ground, buried past the knuckles, impact burst at the point of entry. |
| **3** | Anchored. Weight forward over the buried hands, shoulders low, the first stone lifting. |
| **4** | THE TEAR. He drags forward, both claws ploughing a furrow — a long low spray of broken ground running AHEAD of him, wide and flat, not a vertical plume. |
| **5** | Follow-through, claws breaking free of the floor at the far end of the furrow, debris still hanging. |
| **6** | Rise out of the low stance to a forward-leaning guard, claws trailing dirt. |

**NEVER:**
- NEVER a vertical shockwave — the box is 84 WIDE by 22 TALL, the FX must read low and long
- NEVER leave the ground: every beat keeps at least one foot down
- NEVER a one-handed dig — both claw sets enter the floor

## `kheel` — Reverse Heel Kick

**back + Light** · **2172 x 724**

*The read against this game's three cross-up moves. Someone crossed over behind him and he does not turn around — the heel goes back to meet them.*

**In the engine:** 145ms · box 44x30 for 7 · the box spawns BEHIND him · unarmed tier: costs no chakra, works while winded

**Reference plate:** `briefs/REF-kheel.png` — his idle, then `ksweep1`, `kpush1`, `kpush3`, cut from the shipped sheet at 2x. Match THAT figure.

| beat | what it shows |
|---|---|
| **1** | Guard stance, weight shifting onto the front foot, hips beginning to turn away from the camera. |
| **2** | Rear leg unloads, knee lifting and folding back, torso leaning FORWARD to counterweight it. |
| **3** | THE HEEL. Rear leg fires straight out BEHIND him, sole and heel leading, leg locked, body a hard diagonal. His head stays facing forward — he is not looking at what he hits. |
| **4** | Impact frame — the same extension held, a short flat burst at the heel. |
| **5** | The leg folds back in, knee first, torso righting. |
| **6** | Foot returns to the floor, back to guard. |

**NEVER:**
- NEVER turn him around — the whole move is that he does NOT face the target
- NEVER a claw strike: this is his UNARMED tier, the leg does all of it
- NEVER a high roundhouse arc — the heel travels straight back, not around

---

## When they come back

Drop the three PNGs in `RECOVERY/ember-first-form/` and they pack with the existing
tooling — `cut_strip` cuts them, the row is scaled by its own standing beat against
the packed idle (202px), and the ground rows share one ground line so a
beat that leaves the floor keeps its lift. `ehook` is the only one of the three that
leaves the ground, and its beats 3-5 must not be flattened onto the floor line.

