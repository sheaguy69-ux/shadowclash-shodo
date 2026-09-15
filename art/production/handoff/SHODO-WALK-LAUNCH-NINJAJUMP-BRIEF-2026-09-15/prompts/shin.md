# SHIN — walk · launched hurt · second jump

Part of `SHODO-WALK-LAUNCH-NINJAJUMP-BRIEF-2026-09-15`. Read `README.md`, `BOARD-SPEC.md`
and `PROMPTS.md` §0–§1 first — the canon table and the eight hard rules are there and they
are not repeated per fighter.

**Sheet:** cell `520x370`, aspect **1.41**, `footY 330`, scale `0.3451`, `cols 447`.
**Reference:** `refs/shin-refs.png` (idle, current jump, current air-hurt, landing) and
`refs/ROSTER-true-scale.png` for how tall this fighter is against the others.

⛔ **The refs are cut from the live sheet and some cells still carry drawn ground** — a pale
scuff or a contact smear under the boots. Match the BODY off them, never the floor.

---

## Row A — `walk1..8`

**Intent.** A decision being withheld — speed 10 deliberately NOT sprinting, creeping forward in his permanent low crouch with the guard already up, so the walk reads as the half-second before a kill. It is literally half a second: the tier is a lean-out before the run, so beats 1-3 are the whole performance.

**Beats**

1. CONTACT (lead leg) — THE BEAT THAT SHIPS. Deep predatory crouch, torso pitched forward about 25 degrees and held LEVEL. Lead boot plants on the ball of the foot ahead of the hips; rear toe still down behind, heel off. Both padded fists up in guard, lead fist at chest, rear fist at hip. Hood aimed dead ahead, spine long and low. The four-point wire shuriken lashed flat on the right hip, cord coiled at the belt. Both scarf tails trailing straight back, horizontal.
2. DOWN — THE BEAT THAT SHIPS. Weight sinks fully onto the lead leg, that knee folding deeper: the lowest beat of the cycle. Rear heel peels high, rear knee starting forward. Shoulders stay at the SAME height as beat 1 — the compression is in the knee and the waist, not the head. Fists unchanged. Scarf tails drop and curl under. Ragged waist flaps settle against the thighs.
3. PASSING — THE BEAT THAT SHIPS, and the last one the game reaches. Rear leg swings through directly under the body, knee up to hip height, shin hanging slack, toe pointed down. Supporting leg straight. Torso still low and level. Small opposed arm swing: trailing fist drifts forward, lead fist drifts back, wrists never above shoulder height, the guard never opens. Scarf tails cross behind the hips.
4. UP. The passing leg reaches forward, toe leading, ankle relaxed. Body at the highest point of the cycle — still a crouch, a hair above beat 2. Hips rotate a few degrees, the far shoulder drops. Scarf tails lift and flare out behind. Shuriken and cord unmoved on the hip.
5. CONTACT (rear leg is now the lead). Mirror of beat 1: the new lead boot plants on the ball ahead of the hips, the old lead toe trails behind heel-up. Fists swap guard slots. Hood dead ahead, torso pitched forward and level at beat 1's height. Scarf tails horizontal again.
6. DOWN. Weight sinks onto the new lead leg, the lowest beat repeated. Rear heel peels. Shoulders hold level. The hood brim dips a couple of pixels as the spine compresses — the head does NOT bob. Waist flaps swing forward one beat behind the leg that just planted.
7. PASSING. The other leg swings through under the body, knee at hip height, shin hanging, toe down. Supporting leg straight. Arm swing opposed the other way, guard still closed. Waist flaps swing across the thighs one beat behind the legs. Scarf tails cross behind the hips the opposite way from beat 3.
8. UP and RETURN. The passing leg reaches forward toe-first, ankle relaxed. Torso, hood angle, hip height and both fists settle back into EXACTLY the beat-1 carriage so the loop closes. Scarf tails and waist flaps caught mid-lift, angled so beat 1's horizontal trail reads as their continuation.

**Packing:** every beat is a stance, so the default beat-1 anchor is correct. `--dry` first.

**Prompt**

```text
ShadowClash fighter SHIN — WALK CYCLE. Sumi-e ink-brush shodo styling, side-on 2D fighting-game view, pure side profile.

CHARACTER — do not redesign, match the locked reference, only the pose changes:
Male ninja, compact chibi proportions, PERMANENT LOW CROUCH — he never stands tall.
- Head: smooth dark moss-green hood, always up, hood mouth open onto a pure BLACK VOID face. No jaw, no nose, no mouth, no skin.
- Eye: exactly ONE large oval glowing pale-cyan eye (about #90C6D1) in that black void. Pure side profile means one eye — never a mirrored pair.
- Scarf: two deep-teal ragged scarf tails off the neck wrap, torn brush-cut ends.
- Armour: dark gunmetal scale-mail head to toe under the clothes — mail sleeves, one shoulder plate, knee and shin plates.
- Clothes: layered ragged green waist flaps over the thighs, green cloth wraps on forearms and shins, loose normal-volume pants (never ballooned), dark boots.
- Hands: wrapped padded fists with small bone-cream knuckle accents. No bare fingers.
- WEAPON: exactly ONE four-point wire shuriken — a single bone-white four-pointed star on a thin dark cord — lashed flat to his right hip with the cord coiled at the belt, and NEVER drawn in this row. NO BLADES OF ANY KIND, EVER: no sword, no dagger, no kunai. Never a second star, never a fanned set.
- Colour is DARK. Roughly 40% of his ink is pure black; the green is deep desaturated moss/olive (#304830 to #607860), never lime. The pale-cyan eye is the brightest thing on the figure. NO PURPLE, no red, no gold.

SHEET FORMAT: 8 frames in ONE horizontal row, evenly spaced, identical camera and IDENTICAL CHARACTER SCALE in every frame. Full body with both feet visible in every frame, nothing touching the frame edge. Plain flat ash-grey background — no ground line, no cast shadow, no floor bar, no dust, no grass, no horizon. No motion blur, no speed lines, no afterimages, no captions, no numbers, no borders.

THIS IS A WALK, NOT A RUN — half speed, even flat cadence, no sprint slam. A low predatory creep on the balls of the feet: he stays in the crouch the whole cycle, shoulders held LEVEL with no head bob, and the guard never opens. BEATS 1-3 CARRY THE WHOLE CHARACTER OF THE WALK — put the personality there. Draw all eight as a true loop anyway; frame 8 must flow back into frame 1.

THE 8 BEATS IN ORDER:
1. CONTACT — deep crouch, torso pitched forward 25 degrees and level; lead boot plants on the ball of the foot ahead of the hips, rear toe down behind with the heel up; lead fist in guard at chest, rear fist at hip; hood dead ahead; shuriken flat on the right hip; both scarf tails trailing straight back, horizontal.
2. DOWN — weight sinks onto the lead leg, knee folding to the lowest point of the cycle; rear heel peels high; shoulders stay at frame 1's height; fists unchanged; scarf tails drop and curl under; waist flaps settle on the thighs.
3. PASSING — rear leg swings through under the body, knee at hip height, shin hanging slack, toe down; supporting leg straight; torso still low and level; small opposed arm swing, wrists never above the shoulders; scarf tails cross behind the hips.
4. UP — the passing leg reaches forward toe-first, ankle relaxed; body at the highest point of the cycle, still a crouch, a hair above frame 2; hips rotate slightly; scarf tails lift and flare out behind.
5. CONTACT, OTHER LEG — mirror of frame 1: new lead boot plants on the ball, old lead toe trails behind heel-up; the fists swap guard slots; hood dead ahead; hips at frame 1's height; scarf tails horizontal again.
6. DOWN — weight sinks onto the new lead leg, lowest point again; rear heel peels; shoulders level; the hood brim dips a couple of pixels as the spine compresses, the head does not bob; waist flaps swing forward one beat behind the planted leg.
7. PASSING — the other leg swings through, knee at hip, shin hanging, toe down; supporting leg straight; arm swing opposed the other way, guard still closed; waist flaps trail the legs by one beat; scarf tails cross behind the hips the opposite way from frame 3.
8. UP AND RETURN — passing leg reaches forward toe-first; torso, hood angle, hip height and both fists settle into exactly the frame-1 carriage so the cycle loops; scarf tails and waist flaps caught mid-lift so frame 1's horizontal trail reads as their continuation.
```

**Pitfalls for this fighter**

- THE CHARACTER LIVES IN BEATS 4-8 AND IS NEVER SEEN. New, and it outranks everything else here. WALK_TIME is 0.15s (web/index.html:2933) — 7.5 frames in STATE.WALK before the push breaks into a run. Shin's walk vx is 350*(10/6)*0.5 = 292 px/s (:4751, :4905, WALK_FRAC :2934), so animPhase advances 0.311 per frame (:4644-4645) and the row shows about 2.3 cells of 8. Beats 1-3 are the only ones that ship until the owner rules on WALK_TIME. Draw the loopable eight; front-load the first three.
- HE STANDS UP. The single most likely failure. Canon is a PERMANENT LOW CROUCH — his xidle cells 346-349 measure 134/161/183/161 px of ink in a 370px cell (measured on web/assets/sprites/shin.png). A generator handed the word 'walk' draws an upright pedestrian stroll. Restate the crouch in any re-roll.
- HEAD BOB, OR RUN CADENCE. The picker paces this row FLAT — w[floor(animPhase) % w.length], no contact holds (web/index.html:12535) — so any vertical head travel becomes an even-tempo pogo. A sprint slams; a stroll does not. Shoulders level across all 8.
- A BLADE APPEARS. Canon is hand-to-hand plus ONE four-point wire shuriken. The repo itself will push a blade at you: shin.json still declares weapon_type 'Unarmed & Shuriken / Kunai' and carries a kunai_dash_cancel animation, and the engine once rang his empty hand as steel from old kunai art (docs/MOVE-INPUTS-HITBOXES-AND-FRAME-LAW-709.md:415). No katana on the back, no kunai in the hands, ever.
- THE SHURIKEN IS DRAWN, MULTIPLIED OR FANNED. In the walk it stays STOWED FLAT ON THE RIGHT HIP, cord coiled. shin.json has a shuriken_fan animation and boards drift toward two or three stars; the fan is a MOVE, not his carriage. One star, four points, on the hip.
- A SECOND EYE, OR A 'CORRECTED' FACE. One eye in pure side profile is canon and eye count is NOT a QC dimension for Shin (docs/MOVE-INPUTS-HITBOXES-AND-FRAME-LAW-709.md:419) — never flag it, and never let a re-roll symmetrise the face or open a jaw inside the hood.
- SCALE DRIFT BETWEEN FRAMES. The packer applies ONE scale to the whole board, so a per-frame zoom ships as a fighter who changes size mid-stride. His run row already carries the defect: the two repaired cells 381 and 382 measure 51 and 40 px of cyan against 10-18 px on the other six cells of run_clean — repainted at a different weight. Height differences between beats must be POSE, never camera.
- FEET OR TOES CROPPED. Packed Shin cells bottom out at ink y 324-327 against footY 330 — the soles sit right on the pack anchor, so a board that crops the boots yields a fighter floating above the floor. Both boots fully inside the frame with clearance below.
- A GROUND BAR, SHADOW, SCUFF OR DUST TUFT. The packer welds the board's lowest ink to the floor line, so painted ground BECOMES the feet and he hovers. Every drawn ground shadow was deleted at SHEET_V 798, and the owner ruled 'delete' again on a drawn boot scuff and kicked-up dust on Sep 15 2026 (web/index.html:11051).
- SCARF AND EYE BLEEDING INTO ONE COLOUR. The eye is about 30 px of core colour in a 370px cell (measured, mean #90C6D1). Keep the scarf DARK teal and the eye PALE and clearly brighter, or it disappears at game scale.
- TWO ROWS, OR CAPTIONS UNDER THE FRAMES. One horizontal row of 8 only — a 2-row layout halves the drawn body and the packer reads rows-per-image; captions and numbers get sliced into the cells.
- BEAT 8 DOES NOT MEET BEAT 1. The picker loops modulo the row length with no blend, so a mismatched beat 8 is a visible hitch every cycle. Torso pitch, hip height, hood angle and both fists on beat 8 must be the beat-1 carriage.


---

## Row B — `airhurt1..8` — the launched hurt arc

**Intent.** The instant he stops being a fighter and becomes an object: the hit TOOK him, no part of the pose was chosen, and speed 10 has no speed left to spend. The row exists because today he is drawn braced and composed while being juggled.

**Beats**

1. POP — torso about 20 degrees back off vertical, rising hardest. Both boots torn off the floor and still pointing down and back, soles visible, legs trailing under him. Spine snapped into a violent backward arch. Hood whipped back so the black void and the cyan eye face UP and away. Both arms thrown forward and up in front of the chest, elbows locked, fists open and useless. The shuriken jarred off the belt and swinging out below the hip on a taut cord — attached, never released. Scarf tails and ragged waist flaps ripped straight DOWN by the rise.
2. TIPPING — about 55 degrees back, still rising hard. The arch breaks: one shoulder drops and leads, the hips rotate under him, the legs SCISSOR — one knee snapping up, the other boot still trailing low. Arms lag behind the shoulders now. Scarf tails and hem still streaming straight down, hem snapping. Shuriken flung out wide on a slackening cord.
3. HORIZONTAL — about 90 degrees, rise slowing. Muscle tone is gone. Arms trail behind and above him like rope from the shoulder sockets. The head lolls sideways, the hood brim off the line of the spine, the eye pointed at nothing. One leg straight, the other half-folded — the legs stop matching and never match again. Scarf tails slackening off vertical.
4. PAST HORIZONTAL — about 120 degrees, head now lower than the hips, nearing apex. Shoulders sag toward the ears, arms hang from them with soft elbows and limp hands. The spine unfolds out of the arch and goes slack, the belly open. Knees half bent and passive, feet dangling at two different heights. Waist flaps and scarf tails settle up and out, no longer combed by airspeed. The shuriken drifts slack on its cord.
5. APEX — THE RAG, about 140 degrees. The weightless frame. NO muscle tone anywhere, no pose, no silhouette a stance could be read out of. The spine sags in a loose forward fold over nothing. The hood has flopped fully across the face so the cyan eye is buried and barely a glint. Both arms hang PAST the head, fully extended by their own weight, hands open, fingers apart. The legs hang at two different angles and two different heights, toes down, knees at different bends. Scarf tails and waist flaps float outward in no direction at all. The star dangles below him on a fully slack cord. If any part of this frame looks aimed, braced, curled or guarded, it is wrong — every joint is being carried, none is being held.
6. FALL BEGINS — about 160 degrees. The hips lead downward and the torso folds forward over them at the waist. Arms and head still above the hips, trailing the drop. The hood flops fully forward. Knees rise toward the chest passively as the hips outrun them. Scarf tails and waist flaps start to lift. The shuriken cord goes taut upward.
7. JACK-KNIFED — about 175 degrees, falling. Head and chest down and forward, legs whipping up and back behind him, boots above the shoulder line. Arms trail straight up above the head, fully extended by the drop, hands open. Both scarf tails and the shuriken cord stream UP past the boots. Nothing braced — a tumble, not a dive.
8. DEAD WEIGHT — past 180, a steep head-low diagonal, falling hardest. The body stretched long and rolled slightly so the shoulders lead, hood and void face lowest, boots highest and behind. Arms trailing straight overhead, limp. Legs unmatched and passive, one trailing higher than the other. Scarf tails, waist flaps and the shuriken all streaming up above him on taut lines. A body being dropped, not a purposeful head-first dive.

⛔ **Packing: this row has NO stance beat.** The packer anchors scale on beat 1 by default, and
beat 1 here is the pop — the most extended frame in the row. Anchoring there packs the whole row
too small. Pass `--scale` taken from this fighter's idle, or `--anchor` at the most neutral beat.
The union of an 8-beat arc is also taller than a standing pose, so budget `grow_frame.py --down`
if the dry run prints `REFUSE: scaled window exceeds cell`.

**Prompt**

```text
ShadowClash fighter SHIN — LAUNCHED / AIR-HURT ARC (being juggled). Sumi-e ink-brush shodo styling, side-on 2D fighting-game view, pure side profile.

CHARACTER — do not redesign, match the locked reference, only the pose changes:
Male ninja, compact chibi proportions.
- Head: smooth dark moss-green hood, always up, hood mouth open onto a pure BLACK VOID face. No jaw, no nose, no mouth, no skin.
- Eye: exactly ONE large oval glowing pale-cyan eye (about #90C6D1) in that black void. Pure side profile means one eye — never a mirrored pair.
- Scarf: two deep-teal ragged scarf tails off the neck wrap, torn brush-cut ends.
- Armour: dark gunmetal scale-mail head to toe under the clothes — mail sleeves, one shoulder plate, knee and shin plates.
- Clothes: layered ragged green waist flaps over the thighs, green cloth wraps on forearms and shins, loose normal-volume pants, dark boots.
- Hands: wrapped padded fists with small bone-cream knuckle accents; in this row the hands are OPEN and limp, never fists.
- WEAPON: exactly ONE four-point wire shuriken — a single bone-white four-pointed star on a thin dark cord. He is NOT disarmed: it stays attached the whole row, jarred off the hip and swinging loose on its cord. NO BLADES OF ANY KIND, EVER: no sword, no dagger, no kunai. Never a second star.
- Colour is DARK. Roughly 40% of his ink is pure black; the green is deep desaturated moss/olive (#304830 to #607860), never lime. The pale-cyan eye is the brightest thing on the figure. NO PURPLE, no red, no gold.

SHEET FORMAT: 8 frames in ONE horizontal row, evenly spaced, identical camera and IDENTICAL CHARACTER SCALE in every frame. Full body with both feet visible in every frame, nothing touching the frame edge. Plain flat ash-grey background — no ground line, no cast shadow, no floor bar, no horizon. No motion blur, no speed lines, no afterimages, no captions, no numbers, no borders.

THIS IS ONE CONTINUOUS ARC OF A JUGGLED BODY, READ STRICTLY IN ORDER from rising hardest (frame 1) to falling hardest (frame 8). He is NOT in control. THE BODY TIPS FURTHER OVER THE LAUNCH EVERY SINGLE FRAME — about 20, 55, 90, 120, 140, 160, 175 and past 180 degrees off vertical — so no two frames sit at the same angle. From frame 3 on he has NO muscle tone: the limbs hang from their joints, the legs stop matching each other, and the cloth is what tells you which way he is moving. This is the one row where the silhouette must look BROKEN rather than composed — no guard, no stance, no aim, no readable intent.

THE 8 BEATS IN ORDER:
1. POP, about 20 degrees back, rising hardest — both boots torn off the floor still pointing down and back, soles showing, legs trailing under him; spine snapped into a violent backward arch; hood whipped back so the black void and the cyan eye face UP; both arms thrown forward and up, elbows locked, hands open; the shuriken jarred off the belt and swinging below the hip on a taut cord; scarf tails and ragged waist flaps ripped straight DOWN.
2. TIPPING, about 55 degrees, still rising hard — the arch breaks, one shoulder drops and leads, the hips rotate under him, the legs SCISSOR: one knee snapping up, the other boot still trailing low; arms lagging behind the shoulders; scarf tails and hem still streaming straight down; the star flung out wide on a slackening cord.
3. HORIZONTAL, about 90 degrees, rise slowing — tone gone; arms trail behind and above like rope from the shoulder sockets; the head lolls sideways, the hood brim off the line of the spine, the eye pointed at nothing; one leg straight, the other half-folded — the legs stop matching; scarf tails slacken off vertical.
4. PAST HORIZONTAL, about 120 degrees, head lower than the hips, nearing apex — shoulders sag toward the ears, arms hang with soft elbows and limp hands; the spine unfolds out of the arch and goes slack; knees half bent and passive, feet dangling at two different heights; waist flaps and scarf tails settle up and out, no longer combed by airspeed; the shuriken drifts slack.
5. APEX, THE RAG, about 140 degrees — weightless, NO muscle tone anywhere, no pose at all; the spine sags in a loose forward fold over nothing; the hood has flopped fully across the face so the cyan eye is buried and barely a glint; both arms hang PAST the head, fully extended by their own weight, hands open and fingers apart; the legs hang at two different angles and two different heights, toes down, knees at different bends; scarf tails and waist flaps float outward in no direction; the star dangles on a fully slack cord. If any part of this frame looks aimed, braced, curled or guarded, it is wrong.
6. FALL BEGINS, about 160 degrees — the hips lead downward and the torso folds forward over them at the waist; arms and head still above the hips, trailing the drop; the hood flops fully forward; the knees rise toward the chest passively; scarf tails and waist flaps start to lift; the shuriken cord goes taut upward.
7. JACK-KNIFED, about 175 degrees, falling — head and chest down and forward, legs whipping up and back, boots above the shoulder line; arms trailing straight up above the head, fully extended by the drop, hands open; both scarf tails and the shuriken cord stream UP past the boots; nothing braced — a tumble, not a dive.
8. DEAD WEIGHT, past 180, falling hardest — the body stretched long on a steep head-low diagonal, rolled so the shoulders lead, hood and void face lowest, boots highest and behind; arms trailing straight overhead and limp; legs unmatched and passive, one trailing higher; scarf tails, waist flaps and the shuriken all streaming up above him on taut lines. A body being dropped, not a purposeful head-first dive.
```

**Pitfalls for this fighter**

- HE STAYS COMPOSED. This is the exact defect the row exists to kill. Shin's airhurt1..3 are cells 295/296/297, which ARE grabbed3/grabbed4/grabbed5 — drawings made for being HELD IN A THROW (verified in web/assets/sprites/shin.json; every fighter on the sheet has the same bug). Today he plays a man being held while nobody is touching him. A re-roll that hands him a tidy curled 'hurt pose' has reproduced the bug.
- THE APEX STILL HAS TONE. The second half of the same failure. Beat 5 must have no held joint anywhere: arms past the head under their own weight, hood over the face, legs at two different angles, cloth hanging in no direction. A stills generator quietly gives the victim his posture back at the apex — check beat 5 first on every board that comes off the lane.
- BEATS AT THE SAME ANGLE. Eight variations of one airborne pose is a wasted board. The tilt is the read: 20 / 55 / 90 / 120 / 140 / 160 / 175 / past-180. No two frames share one.
- AMBIGUOUS DIRECTION. The engine picks this row off the victim's vertical velocity — today a hard-coded 3-way band, vy < -80 / -80..100 / > 100 (web/index.html:12310), which widens across the row when the art lands — so CLOTH is the only cue separating rising from falling. Scarf tails and waist flaps point DOWN on beats 1-3 and UP on beats 6-8. Neutral cloth is unreadable in both directions.
- THE EARLY BEATS ARE THE MOVE. Measured against a -390 launcher with 0.5s of hitstun, the first beat covers roughly 0 to 0.28s — more than half the launch — and victims are launched 63 to 192 px on the live sim. Every beat is worth looking at on its own, but a launched pose that only becomes interesting at beat 6 is wasted.
- HE IS DISARMED. The star never leaves him. A generator reading 'limp' will drop it out of frame or draw it flying away like a thrown projectile with an impact burst — it is on a CORD, attached, swinging. Never released, never duplicated, never fanned.
- A BLADE APPEARS. Canon is hand-to-hand plus ONE four-point wire shuriken. shin.json still declares weapon_type 'Unarmed & Shuriken / Kunai' and carries a kunai_dash_cancel animation; ignore both. No katana on the back, no kunai in the hands.
- THE LEGS STAY SYMMETRICAL. Matching legs read as a chosen pose. From beat 3 on they must sit at different angles AND different heights — that asymmetry is most of what sells 'not in control'.
- A SECOND EYE, OR A 'CORRECTED' FACE. One eye in pure side profile is canon and eye count is NOT a QC dimension for Shin (docs/MOVE-INPUTS-HITBOXES-AND-FRAME-LAW-709.md:419). Beats 5 and 6 bury the eye behind the flopped hood ON PURPOSE — that is correct, not a defect to fix.
- SCALE DRIFT BETWEEN FRAMES. Inverted and stretched poses are exactly where a generator rescales to fill the frame, and the packer applies ONE scale to the whole board. His packed flight cells already spread 158 px of ink (cell 304, tucked) to 196 px (cell 305, inverted) — that is POSE. Hold one camera and let the pose do the stretching.
- FEET OR TOES CROPPED. Beats 1, 7 and 8 put the boots near a frame edge; nothing may touch the canvas edge. A cropped sole anchors a footless body at the pack.
- A GROUND BAR, SHADOW OR IMPACT FX. He is airborne — no floor in shot, no shadow ellipse, no horizon. No hit sparks, stars or pain lines either: the engine owns impact FX and the owner deleted the procedural trails.
- PURPLE, RED OR GOLD. Purple belongs to the Executioner and Mizu; red is Tsubasa and Exile; gold is Kael. Shin is black ink with dark moss-green and deep teal, and one pale-cyan eye.
- TWO ROWS, OR CAPTIONS UNDER THE FRAMES. One horizontal row of 8 — a 2-row layout halves the drawn body and the packer reads rows-per-image; captions and numbers get sliced into the cells.


---

## Row C — `njump1..8` — the second jump — Shin — the fastest, the lowest, barely a ball at all

*Speed 10. His revolution is the quickest on the roster and he unwinds into his own low stance.*
Backward tuck, arms wrapped round the shins, chainmail bunching at the joints.
**No blades in any frame** — bare hands, and **one eye**.

> …A compact ninja in **full chainmail head to toe** under a dark-green hood with a deep-teal
> scarf, **pale-cyan single eye**, **no weapons at all, bare hands**, performing a very fast
> tight backward tuck in mid-air.
> Frame 1: feet snapping up behind him, spine beginning to round backward.
> Frame 2: arms clamping round the shins, head tucking to the knees, chainmail bunching.
> Frame 3: quarter turn backward, a hard compact ball, scarf trailing forward.
> Frame 4: half turn, inverted, the smallest and fastest point of the tumble.
> Frame 5: three-quarter turn, grip on the shins releasing.
> Frame 6: legs whipping down and forward, arms out for balance.
> Frame 7: nearly upright, weight already dropping into a crouch.
> Frame 8: his low fighting stance, knees deep, hands open and empty.


⛔ **Packing: no stance beat here either.** Same `--scale` / `--anchor` rule as Row B, and
the rotation makes the union taller still.
