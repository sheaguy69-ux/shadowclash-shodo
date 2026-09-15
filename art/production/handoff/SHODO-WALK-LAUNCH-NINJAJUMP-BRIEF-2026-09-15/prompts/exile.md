# EXILE — walk · launched hurt · second jump

Part of `SHODO-WALK-LAUNCH-NINJAJUMP-BRIEF-2026-09-15`. Read `README.md`, `BOARD-SPEC.md`
and `PROMPTS.md` §0–§1 first — the canon table and the eight hard rules are there and they
are not repeated per fighter.

**Sheet:** cell `480x432`, aspect **1.11**, `footY 344`, scale `0.4409`, `cols 426`.
**Reference:** `refs/exile-refs.png` (idle, current jump, current air-hurt, landing) and
`refs/ROSTER-true-scale.png` for how tall this fighter is against the others.

⛔ **The refs are cut from the live sheet and some cells still carry drawn ground** — a pale
scuff or a contact smear under the boots. Match the BODY off them, never the floor.

---

## Row A — `walk1..8`

**Intent.** She is in no hurry and she is still the fastest body in the game — THE TOLL, the first door, crossing her own ground: chain slack, spiked ball swinging at her heel, arriving before you noticed she had started.

**Beats**

1. CONTACT (lead foot). Lead leg plants heel-first directly under the pelvis, rear leg fully extended behind with the toe still down. Torso UPRIGHT, only a 3-4 degree forward lean (nothing like the run's deep pitch), head level, mane settled and hanging behind — no bob. Lead hand carries the kama low at hip height, the long blade curving forward and down. Rear hand holds the chain; the chain sags DOWN-AND-FORWARD across the front of her thighs to the spiked ball, which hangs at its REARMOST point, ankle height, just clear of the floor behind the rear ankle.
2. DOWN. Weight sinks onto the lead leg: lead knee bends about 20 degrees, hips drop, rear heel peels off the ground, rear toe drags a beat. Kama hand drops with the hips, blade still forward. Chain sag at its deepest. Ball has swung forward to under the rear knee and is rising slightly. One plum sash tail lifts with the sink.
3. PASSING. Rear leg swings through directly beneath the pelvis, knee up, shin vertical, boot just clearing the floor. Support (lead) leg straight, hips at their lowest of the cycle. Torso still upright, head still level. Ball is directly under her hips at the bottom of its swing — the closest it comes to the floor in the whole row, and still clear of it.
4. UP. Support leg pushes to full extension, hips at their highest, the swinging foot reaches forward heel-first with the leg almost straight. Kama hand at its highest carry. Ball out at its FORWARD extreme past the front thigh at KNEE height, chain pulled nearly straight but never taut. Mane lifts a few strands off her back.
5. CONTACT (opposite foot) — legs mirrored from beat 1 only: the other foot plants heel-first under the pelvis, the kama-side leg now extended behind, toe down. ARMS DO NOT SWAP — the kama stays in the same hand it has held all row, still low and forward. The chain now crosses the other way, DOWN-AND-BACK behind her hips, and stays on that diagonal for beats 5-8. Ball just past its forward extreme, fallen back and RISEN to hip height. Torso back to the 3-4 degree lean, head level.
6. DOWN (opposite). Weight sinks onto the new support leg, knee bends about 20 degrees, hips drop, the kama-side heel peels off behind. Ball travelling rearward under the front knee, chain sagging deep and skimming close to her calves. Both plum sash tails settle. Head still level — no vertical head bob beyond 2-3px across the whole cycle.
7. PASSING (opposite). Kama-side leg swings through under the pelvis, knee up, shin vertical, boot clearing the floor. Support leg straight, hips lowest. Ball is now BEHIND her at rear-ankle height and still travelling back toward its rearmost point; chain at full sag behind her legs. Mane just beginning to settle back from the previous swing.
8. UP (opposite) — the loop seam. Support leg at full extension, hips highest, the kama-side foot reaching forward heel-first, the heel exactly one short step behind where beat 1 plants it. Kama hand at its highest carry. Ball arrived back at its REARMOST extreme so it sits precisely where beat 1 shows it, chain sag matching beat 1. Body already back to the 3-4 degree lean so beat 8 flows into beat 1 with no pop.

**Packing:** every beat is a stance, so the default beat-1 anchor is correct. `--dry` first.

**Prompt**

```text
Character: EXILE, a female shinobi from a 2D fighting game. Chibi fighting-game proportions (large head, compact body, short limbs), side-on 2D fighting-game view, facing SCREEN-LEFT in all eight frames. Sumi-e / ink-brush shodo styling: inked black brush linework with hand-painted colour accents — NOT flat greyscale monochrome, NOT cel-shaded vector.

CANON, exact, do not change: she is UNHOODED — no hood, no cowl, no headband over the hair. Huge windswept BLACK feathered mane with broad bone-white / silver streaks and pale flecks through it. A TAN / CREAM cloth wrap covers ONE eye — the forward, screen-left one (her anatomical right) — with a DARK-RED brushed kanji painted on the wrap. The other eye is visible and RED: iris #B94828, black pupil, white sclera, thin gold liner. Black cloth mask over nose and mouth. Near-black quilted shinobi garb with gold and brass studs, rings and trim, gold-trimmed segmented bracers, tan wraps at the shins, gold-trimmed black boots, tan skin. Neck scarf wound under the mask and TWO trailing sash tails, all in VERY DARK DESATURATED PLUM (#3A2D47) — almost black: never bright violet, never magenta, never neon purple.

WEAPON, exact: ONE kusarigama. That is ONE kama — a short wood-and-brass handle with a gold ring pommel and ONE LONG steel crescent sickle blade set at right angles at its head — carried in her LEAD (forward, screen-left) hand in all eight frames; it NEVER swaps hands. Her REAR hand holds the chain. ONE fine steel chain, one continuous unbroken line at the same link gauge in every frame, running from the ring pommel across her body to ONE iron morningstar ball with about eight short radial spikes. No second sickle, no sword, no smooth ball, no chain in each hand. In this row the chain HANGS in a sagging curve — it never goes taut. The ball is a weight, never a blade, is drawn complete and inside the frame in all eight, and never touches the floor.

FORMAT: 8 frames, evenly spaced, in ONE horizontal row, read left to right. Identical camera and IDENTICAL CHARACTER SCALE IN EVERY FRAME — head and mane exactly the same size in all eight. Full body with both feet visible and complete in every frame. Plain flat background. NO ground line, NO floor bar, NO cast shadow, NO scuff, dust or grey smudge under the boots, no motion-blur smear across a frame edge. No panel borders, no captions, no numbers, no frame dividers, no page-white patches sealed between the legs or inside the chain curve.

THIS IS A WALK CYCLE at half a run's travel: an even, unhurried, loopable 8-beat stride, torso UPRIGHT with only a 3-4 degree forward lean, head level with almost no bob, mane settled behind her rather than streaming. Frame 8 flows straight back into frame 1. The legs cycle TWICE across the eight; the spiked ball swings ONCE — so the ball sits somewhere different in every frame, and that is what keeps the mirrored beats from repeating. The ARMS NEVER SWAP: the kama stays in the lead hand throughout and only rises and falls with the hips.

THE 8 BEATS, in order:
1. CONTACT: lead foot plants heel-first under the pelvis, rear leg extended behind, toe down; kama low at hip height, blade forward; chain sagging DOWN-AND-FORWARD across the front of her thighs; ball at its REARMOST, ankle height, behind the rear ankle.
2. DOWN: weight sinks onto the lead leg, knee bent about 20 degrees, hips low, rear heel peeling off; kama hand drops with the hips; chain sag at its deepest; ball swung forward to under the rear knee, rising slightly.
3. PASSING: rear leg swings through directly under the pelvis, knee up, shin vertical, boot just clearing the floor; support leg straight, hips lowest, head level; ball directly under her hips at the bottom of its swing — closest to the floor of the whole row, still clear of it.
4. UP: support leg at full extension, hips highest, front foot reaching forward heel-first; kama hand at its highest; ball out at its FORWARD extreme past the front thigh at KNEE height, chain pulled nearly straight but not taut.
5. CONTACT, OPPOSITE FOOT: the legs mirror beat 1 — the other foot plants heel-first, the kama-side leg now extended behind. THE ARMS DO NOT SWAP: kama still low and forward in the same hand. The chain now crosses the other way, DOWN-AND-BACK behind her hips, and stays on that diagonal through beat 8. Ball just past the forward extreme, fallen back and RISEN to hip height.
6. DOWN, opposite: weight sinks onto the new support leg, knee bent, hips low, kama-side heel peeling off behind; ball travelling rearward under the front knee, chain sagging deep and skimming her calves.
7. PASSING, opposite: kama-side leg swings through under the pelvis, knee up, shin vertical; support leg straight, hips lowest; ball now BEHIND her at rear-ankle height and still going back, chain at full sag behind her legs.
8. UP, opposite — the loop seam: support leg at full extension, hips highest, kama-side foot reaching forward heel-first, its heel one short step behind where frame 1 plants it; ball arrived back at its REARMOST, exactly where frame 1 shows it; chain sag and torso lean match frame 1 so the cycle loops with no pop.
```

**Pitfalls for this fighter**

- HOOD. The single most common failure on this character. She is UNHOODED — huge black mane with bone-white streaks. No hood, no cowl, no forehead bandana replacing the eye-wrap.
- THE EYE-WRAP BECOMES SOMETHING ELSE. It is a tan/cream cloth band over ONE eye carrying a dark-red brushed kanji — not a forehead bandage, not a leather eyepatch, not two uncovered eyes. Her own packed idle (cell 244) is the reference.
- WRONG IRIS COLOUR, from two directions at once. Her packed sheet still draws an AMBER/gold iris (looked at and measured on cell 244), and the engine's roster card still lists eye "#f2f4f6" (pale) at web/index.html:1531. Both are outgoing. The iris is RED #B94828.
- BRIGHT PURPLE. The roster card at web/index.html:1531 carries primary #8b5cf6 and scarf #6d28d9. The packed art does not: the sash median measures (45,36,56) = #2D2438 on cell 244, a near-black plum. A generator handed the card paints her neon. (Her RUN row is the warning — cells 401-408 drift the sash to pink/magenta, hue 300-345.)
- ARM SWAP. A real walk swings both arms — hers cannot. The kama never leaves its hand. Only the LEGS mirror at beat 5. Boards routinely hand the sickle to the other fist at the mirror beat.
- FOUR BEATS DRAWN TWICE. With the arms locked and the legs mirroring, beats 1-4 and 5-8 pack as near-identical cells unless the ball separates them. The ball's position is the whole job: rearmost / under the rear knee / under the hips / forward extreme at knee height / forward-falling at hip height / under the front knee / behind at ankle height / rearmost. Eight different places, and the chain flips diagonal at beat 5. Beats 3 and 7 are the pair that collapses first — they are identical bodies, so the ball MUST be under her hips in 3 and behind her ankle in 7.
- BORROWING THE RUN POSTURE. Her run row (cells 401-408) is a deep forward pitch with the mane streaming horizontally. Drawn at that lean, the walk will not hand back to xidle when the 0.15s tier expires. Upright, head level, mane settled.
- SCALE DRIFT, and her sheet already has it: run_clean median ink area measures 8,467px against xidle's 10,342px, 18% smaller. Anchor every frame of this board to the IDLE's head-and-mane size, never the run's.
- GROUND BAR / GROUND CONTACT. Her own idle carries a faint grey boot scuff, and cell 62 (xidle6) ships a thick black L-shaped border baked along the bottom and right edge plus a large unerased cream page-slab behind the body (ink 14,308px against 10,156-10,523px on the other five idle beats). Do not repeat either. And the spiked ball must CLEAR the floor in all 8 — a ball resting on an implied floor is a ground bar by another name.
- SIX BEATS INSTEAD OF EIGHT. Her idle row is 6 cells and her boards often arrive at 6. The walk row is collected walk1..N (web/index.html:12522) and drawn flat (12535); eight is what the cycle needs.
- MEASURED ENGINE CAVEAT to hand up with the board: STATE.WALK is real and art-gated purely on walk1 (web/index.html:4903, state set 4912), and NO sheet in this tree has a walk row today — verified across all EIGHT fighter JSONs in web/assets/sprites (there is no oni.json here) — so this is the first. But at WALK_TIME 0.15 (web/index.html:2933) and WALK_FRAC 0.5 (2934), Exile's moveSpeed of 350*10/6 = 583.3px/s (4751) gives a walk vx of 291.7, an animPhase rate of min(3, 291.7/150) = 1.944 x 8 cells = 15.55 phase/s (4644-4645), and 0.15s x 15.55 = 2.33 phase — only cells 1, 2 and 3 ever draw. Ask the owner to raise WALK_TIME to about 0.51s to show all eight. Draw the full loopable 8 regardless.


---

## Row B — `airhurt1..8` — the launched hurt arc

**Intent.** The most fragile body in the game coming apart in mid-air — the beat where the player stops seeing a fighter and sees a weight on the end of a chain. She is being MOVED; she is not moving.

**Beats**

1. THE POP. Both boots torn off the floor and still pointing down, soles a body-thickness clear of where she stood, knees snapping straight. Spine arched hard BACKWARD over the hit, chin up, head snapped back so the mask points at the ceiling. Both arms flung out and behind her. The kama hangs UPSIDE DOWN from a limp lead hand, held only by the very end of the handle. Chain still slack at her hip and the spiked ball is the only thing still down at floor level — it has not been lifted yet.
2. RISING HARD. The body is a backward C: hips are the highest ink in the frame, head trails below and behind them, mane blown straight DOWN. Both arms trail above her head, elbows slack and at different angles. The chain snaps taut for this one beat as the ball is finally ripped off the floor and follows her up, a full body-length behind and below.
3. RISE SLOWING. The arch releasing into slack — torso rolling from arched to boneless, one shoulder dropping far lower than the other, knees breaking loose and drifting apart at two different angles, no symmetry left anywhere. Head lolling sideways off the spine line. The ball has caught up and is level with her boots; the chain goes soft.
4. APEX, FIRST BEAT — a rag, not a pose. Nothing in the body is holding itself. Fingers open and splayed, both wrists bent back limp, the kama hooked on one finger and about to fall. Arms floating above and behind wherever the rise left them, at two different angles. Legs hanging unequal — one knee half-bent, one nearly straight, both feet trailing toes-down with no ankle tone. Head tipped fully back off the neck line, chin past the shoulder, jaw slack under the mask so the cloth tents loose. Mane fanned into a weightless halo. Chain drifting in a lazy S, ball hanging almost motionless beside her hip. No two limbs parallel, nothing clenched, zero muscle tone in the whole silhouette.
5. APEX, SECOND BEAT. The same dead body rotated 20-25 degrees head-down-forward under its own weight, because nothing is stopping it: one arm has slid across her chest, one boot has drifted above the other. The mane and both sash tails are still finishing beat 4's motion — they arrive LATE, a beat behind the body. The ball begins to sink below her BEFORE she does; the chain leads her down.
6. THE FALL BEGINS. Folding at the waist, chest collapsing toward the knees, head dropping below hip height, both arms trailing straight UP above her now, kama hanging blade-down over her head from slack fingers. Chain paying out upward; the ball is above her and still falling slower than she is.
7. FALLING. An OPEN forward jackknife — head low, hips high, both arms and the mane streaming straight up, both boots the highest ink in the frame, legs apart and at unequal angles. The chain is a long near-vertical line with the ball at the very TOP of the frame, a full body-length above her.
8. FALLING HARD — the last beat before she hits. The fold TIGHTENS into a compact head-down tumble: chin driven into the chest, knees dragged up and crossing, arms above and now crossing each other, the kama swinging on the very ends of her limp fingers, mane straight up. The ball has whipped PAST her and is now BELOW her, so the chain reads as a whipping S with the weight leading her into the floor. Nothing in the silhouette is composed.

⛔ **Packing: this row has NO stance beat.** The packer anchors scale on beat 1 by default, and
beat 1 here is the pop — the most extended frame in the row. Anchoring there packs the whole row
too small. Pass `--scale` taken from this fighter's idle, or `--anchor` at the most neutral beat.
The union of an 8-beat arc is also taller than a standing pose, so budget `grow_frame.py --down`
if the dry run prints `REFUSE: scaled window exceeds cell`.

**Prompt**

```text
Character: EXILE, a female shinobi from a 2D fighting game. Chibi fighting-game proportions (large head, compact body, short limbs), side-on 2D fighting-game view, facing SCREEN-LEFT in all eight frames — one facing only, no frame mirrored. Sumi-e / ink-brush shodo styling: inked black brush linework with hand-painted colour accents — NOT flat greyscale monochrome, NOT cel-shaded vector.

CANON, exact, do not change: she is UNHOODED — no hood, no cowl, no headband over the hair. Huge windswept BLACK feathered mane with broad bone-white / silver streaks and pale flecks through it. A TAN / CREAM cloth wrap covers ONE eye — the forward, screen-left one — with a DARK-RED brushed kanji painted on the wrap. The other eye is visible and RED: iris #B94828, black pupil, white sclera, thin gold liner. Black cloth mask over nose and mouth. Near-black quilted shinobi garb with gold and brass studs, rings and trim, gold-trimmed segmented bracers, tan shin wraps, gold-trimmed black boots, tan skin. Neck scarf and TWO trailing sash tails in VERY DARK DESATURATED PLUM (#3A2D47) — almost black: never bright violet, never magenta, never neon purple.

WEAPON, exact: ONE kusarigama, and she is NOT disarmed — she keeps it through the whole row, but everything hangs LOOSE. ONE kama: a short wood-and-brass handle with a gold ring pommel and ONE LONG steel crescent sickle blade at right angles at its head, in the SAME hand in all eight frames, held only by slack open fingers. ONE fine steel chain, one continuous unbroken line at the same link gauge in every frame, running from the kama to ONE iron morningstar ball with about eight short radial spikes. No second sickle, no sword, no smooth ball. The ball is dead weight: it LAGS a beat behind every change of direction, and it is drawn complete and inside the frame in all eight.

FORMAT: 8 frames, evenly spaced, in ONE horizontal row, read left to right. Identical camera and IDENTICAL CHARACTER SCALE IN EVERY FRAME — head and mane exactly the same size in all eight. Full body with both feet visible and complete in every frame, clear of the frame edge. Plain flat background. NO ground line, NO floor bar, NO cast shadow, NO dust, scuff, impact spray or debris at any frame's bottom edge, no motion-blur smear across a frame edge. No panel borders, no captions, no numbers, no frame dividers, no page-white patches sealed between the limbs or inside the chain curve.

THIS IS A LAUNCHED JUGGLE ARC, not a flinch: one continuous arc read left to right, from rising hard, through a weightless apex, to falling hard. She is NOT in control at any point — she is being moved, she is not moving. This is the one row where her silhouette must look BROKEN rather than composed: no braced legs, no clenched fists, no matching limb angles, no fighting stance anywhere in the eight.

THE 8 BEATS, in order:
1. THE POP: both boots torn off the floor and still pointing down, knees snapping straight, spine arched hard BACKWARD, chin up and head snapped back, both arms flung out behind, kama hanging upside down from the end of the handle in limp fingers, chain slack, the spiked ball still at the bottom — the only thing not yet lifted.
2. RISING HARD: the body a backward C, hips the highest ink, head trailing below and behind them, mane blown straight DOWN, both arms trailing above the head with elbows slack at different angles; the chain snaps taut for this one beat as the ball is ripped off the floor and follows her up a body-length below.
3. RISE SLOWING: the arch releasing, torso going boneless, one shoulder dropped far lower than the other, knees loose at two different angles, head lolling sideways off the spine line; the ball catches up level with her boots and the chain goes soft.
4. APEX ONE — a rag, not a pose: fingers open and splayed, both wrists bent back limp, the kama hooked on one finger about to fall; arms floating above and behind at two different angles; legs unequal, one knee half-bent, one nearly straight, both feet trailing toes-down with no ankle tone; head tipped fully back off the neck line, chin past the shoulder, jaw slack under the mask so the cloth tents loose; mane fanned into a weightless halo; chain in a lazy S, ball hanging almost motionless beside her. No two limbs parallel, nothing clenched, zero muscle tone.
5. APEX TWO: the same dead body rotated 20-25 degrees head-down-forward under its own weight, one arm slid across her chest, one boot drifted above the other; the mane and both sash tails are still finishing beat 4's motion, arriving a beat LATE; the ball begins to sink below her before she does.
6. THE FALL BEGINS: folding at the waist, chest collapsing toward the knees, head dropping below the hips, both arms trailing straight UP, kama hanging blade-down above her head, chain paying out upward, the ball above her and falling slower than she is.
7. FALLING: an OPEN forward jackknife, head low and hips high, both arms and the mane streaming straight up, both boots the highest ink in the frame, legs apart at unequal angles; the chain a long near-vertical line with the ball at the very TOP of the frame a body-length above her.
8. FALLING HARD: the fold TIGHTENS into a compact head-down tumble — chin driven into the chest, knees dragged up and crossing, arms above and crossing each other, the kama swinging on the ends of limp fingers, mane straight up; the ball has whipped PAST her and is now BELOW her, so the chain reads as a whipping S with the weight leading her into the floor.
```

**Pitfalls for this fighter**

- DRAWING A POSE INSTEAD OF A BODY. This is the failure her sheet already shipped: airhurt1/2/3 are not drawn art at all — they point at cells 179/180/183, which are grabbed3/grabbed4/grabbed7 out of her THROW row. She currently reads as a grab victim being carried, not a juggled body. A composed mid-air 'flinch' repeats it exactly.
- APEX WITH MUSCLE TONE. Beats 4 and 5 are the ones boards always get wrong — they draw a controlled, symmetrical air pose. The test for beat 4: no two limbs parallel, no clenched fist, no braced leg, no tucked chin, both wrists bent back, fingers splayed, the head off the neck line, and the kama hooked on ONE finger. If you could hold the drawing, it is wrong. And beat 5 needs the late hair: the mane and sash a beat behind the body is the single cheapest thing that sells dead weight.
- BEATS THAT DON'T READ IN ORDER. The engine bands this row on the victim's vertical velocity (web/index.html:12310), so beat 1 must be unmistakably RISING and beat 8 unmistakably FALLING. Interchangeable or mirror-symmetrical beats destroy the read.
- BEATS 7 AND 8 PACKING THE SAME. Both are head-down falls. They separate on two things only: 7 is an OPEN jackknife with the ball at the TOP of the frame; 8 is a TIGHT crossed tumble with the ball already BELOW her. Draw that difference or one of the two is a wasted cell.
- MIRRORED BEATS. Today's third beat is cell 183, which is flagged "183": true in the mirror map of exile.json, so the engine flips her facing mid-juggle. Draw all eight one facing, screen-left, no exceptions.
- DISARMING HER — or the opposite, gripping properly. She keeps the kama and the ball, but the kama must hang from slack open fingers and the ball must LAG a beat behind every direction change. That lag is the single thing that sells weightlessness across eight frames; a ball that tracks her body kills the row.
- THE CHAIN BREAKING ITS OWN LAW. One continuous unbroken line, same link gauge every frame. Taut ONLY on beat 2 (the ball ripped off the floor) and beat 8 (whipping past her). Slack or drifting everywhere else. It must never knot, loop through a limb, or vanish behind the body.
- GROUND CONTACT IN AN AIR ROW. There is none — any drawn dust, scuff, impact spray or debris at a frame's bottom edge is a ground bar. Her own sheet already ships this defect on cell 350, which carries a drawn black impact spray at the kama tip inside a FLIGHT cell.
- HOOD, WRONG IRIS, BRIGHT PURPLE — the three standing traps: no hood ever; the iris is RED #B94828 (her packed sheet still draws amber, and the roster card at web/index.html:1531 still lists eye "#f2f4f6"); the sash is a near-black plum, measured (45,36,56) on cell 244, not the card's #8b5cf6/#6d28d9.
- SCALE DRIFT AND CROPPED FEET. The body rotates through this row and boards drift bigger on the extended beats. Identical character scale in all eight, anchored to the idle's head-and-mane size (xidle median ink 10,342px; her run row already sits 18% under it at 8,467px), and both boots complete and clear of the frame edge on every beat — her packed cells run ink-bottom 334-345 against footY 344.
- MEASURED ENGINE CAVEAT to hand up with the board: the picker reads only THREE beats today — const beat = p.vy < -80 ? 1 : p.vy > 100 ? 3 : 2 (web/index.html:12310) — so an 8-cell row draws cells 1, 2 and 3 only until that band is widened to 8. And the real launch range is smaller than a generic brief assumes: launchVy measures -200 (web/index.html:9024) to -560 (7676) with a -430 default (10597), and at GRAVITY 1100px/s^2 (930, 936, 1622) that is an 18px / 84px / 143px apex. Pitch the arc at a typical -380 to -560 pop.


---

## Row C — `njump1..8` — the second jump — Exile — the chain does the curling

*A long chain and a spiked ball are the problem and the answer.* She curls, and the **chain
wraps around her** through the rotation while the spiked ball orbits outside the tuck. Her
mane is half the silhouette.

> …An unhooded kunoichi with a **huge black-and-silver mane**, a **tan cloth wrap over one
> eye with dark-red kanji on it**, one visible red eye, holding a **long-bladed kusarigama on
> a long chain with a SPIKED iron ball on the other end**, curling into a ball in mid-air
> while the chain wraps around her and the spiked ball orbits outside.
> Frame 1: feet leaving, chain slack and beginning to loop, ball swinging wide.
> Frame 2: knees drawn up, sickle held close, the first wrap of chain crossing her back.
> Frame 3: quarter turn, tight ball, chain wrapping, ball flung out at the end of its arc.
> Frame 4: half turn, inverted, mane fanned wide, chain looped around the tuck, ball at full extension.
> Frame 5: three-quarter turn, chain beginning to unwind, ball swinging back in.
> Frame 6: legs dropping, sickle coming out to lead, chain paying out.
> Frame 7: nearly upright, ball landing back in her free hand or trailing low.
> Frame 8: upright, sickle forward, chain hanging in a slack loop, mane settling.

---


⛔ **Packing: no stance beat here either.** Same `--scale` / `--anchor` rule as Row B, and
the rotation makes the union taller still.
