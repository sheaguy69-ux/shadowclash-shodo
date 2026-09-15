# TSUBASA — walk · launched hurt · second jump

Part of `SHODO-WALK-LAUNCH-NINJAJUMP-BRIEF-2026-09-15`. Read `README.md`, `BOARD-SPEC.md`
and `PROMPTS.md` §0–§1 first — the canon table and the eight hard rules are there and they
are not repeated per fighter.

**Sheet:** cell `301x332`, aspect **0.91**, `footY 312`, scale `0.3663`, `cols 511`.
**Reference:** `refs/tsubasa-refs.png` (idle, current jump, current air-hurt, landing) and
`refs/ROSTER-true-scale.png` for how tall this fighter is against the others.

⛔ **The refs are cut from the live sheet and some cells still carry drawn ground** — a pale
scuff or a contact smear under the boots. Match the BODY off them, never the floor.

---

## Row A — `walk1..8`

**Intent.** The player should feel him CLOSING — a low, level, blade-quiet glide from a man already inside his own counter range, so that breaking into the run reads as him dropping the pretence. The row exists to be the one locomotion state where his upper body tells you NOTHING.

**Beats**

1. BEAT 1 — CONTACT, stride open. Three-quarter view facing screen-left. Lead (left) foot planted flat well forward, rear foot flat behind with the heel just breaking off the floor. Both knees bent, hips LOW and LEVEL. Torso vertical with almost no lean. Both arms hanging straight and dead still at his sides, both tantō in his idle carriage — reverse grip, blade hanging down and outward at about 45 degrees, tip near knee height. Chin level, the single white eye forward. Both scarf tails floating out behind at shoulder height.
2. BEAT 2 — LOW POINT. Rear foot skims forward with the sole grazing the floor and the toe never clearing it; the lead knee takes all the weight and bends deeper; the head drops to its lowest point of the cycle, about 4-5 source px below beat 1. Hips stay level — no hip roll, no shoulder dip. Arms and blades unchanged and motionless: the knives do not swing with the legs. Scarf tails sagging, beginning to fall behind him.
3. BEAT 3 — PASSING. Feet together directly under the hips, ankles almost touching, both soles on the floor. Body at mid-height, torso vertical, shoulders square. Arms still dead; only the lead wrist has rolled a few degrees as the body follows through, so the blade ANGLE changes without the arm moving. Scarf tails at their lowest, draped straight back.
4. BEAT 4 — HIGH POINT / REACH. The passing foot slides out ahead, toe leading, sole still skimming the floor; the support leg straightens to its tallest and the head reaches its highest point of the cycle, about 4-5 source px above beat 1. Shoulders stay level — the rise never reaches the arms. Both blades still hanging in the idle carriage. Scarf tails lifting again and trailing straight back.
5. BEAT 5 — CONTACT, MIRRORED. The travelling foot lands flat well forward, stride fully open — a mirror of beat 1 with the opposite leg leading; the other foot flat behind, heel breaking. The ARMS DO NOT SWAP DUTY: both still hang dead at his sides in the same carriage, and only the hip turn changes which blade reads nearer the camera. Torso vertical, chin level, hips low. Scarf tails out behind at shoulder height.
6. BEAT 6 — LOW POINT, MIRRORED. Exactly beat 2 with the legs swapped: the new rear foot skims forward with the sole grazing the floor, the lead knee deepens, the head at its lowest. Hips level, arms and blades still, no telegraph anywhere in the upper body. Scarf tails sagging back.
7. BEAT 7 — PASSING, MIRRORED. Feet together under the hips, ankles close, both soles down, body at mid-height, torso vertical. Blades quiet; the trailing wrist rolls slightly as the body passes over the support foot. Scarf tails at their lowest, draped back.
8. BEAT 8 — HIGH POINT / REACH, MIRRORED, AND THE WIND BACK INTO BEAT 1. The pushing foot extends forward and low with the sole skimming, support leg tall, head at its highest — and the lead shoulder has already begun turning back toward the beat-1 angle so the loop closes with no pop. Blades unchanged. Scarf tails lifted and streaming straight back.

**Packing:** every beat is a stance, so the default beat-1 anchor is correct. `--dry` first.

**Prompt**

```text
Draw ONE sprite row of the ShadowClash fighter TSUBASA walking.

8 frames in one horizontal row, evenly spaced, identical camera, identical character scale in every frame, full body with both feet visible in every frame, plain flat background, no ground line, no cast shadow, no floor bar, no drawn floor of any kind, no motion-blur smear across the frame edge. In every frame the lowest ink on the page is the sole of his lower boot and nothing sits below it. Every frame's whole figure — both blade tips and both scarf tails included — sits inside its frame with transparent margin; nothing ends in a straight cut at an edge.

STYLE: sumi-e / shodō ink-brush styling — heavy, uneven black brush outlines with real pressure variation, ink pooling, ragged dry-brush breakup and tapered ends, over flat controlled cel shading. No pixel art, no 3D, no painterly rendering, no photographic lighting. Side-on 2D fighting-game view, three-quarter angle facing LEFT with the torso turned slightly toward the camera.

CHARACTER — EXACT, NO DEVIATION: Tsubasa, he/him. A chibi ninja about 2.5 head-heights tall counting his hair spikes, compact build, short limbs, broad simple hands, chunky boots. NO HOOD and NO COWL — wild spiky BLACK hair swept back with bright RED flame-shaped streaks through it. A black cloth mask over nose and mouth with a single thin RED slash across the bridge. At this three-quarter angle only ONE eye reads: a single large solid WHITE almond eye (#ffffff), no iris, no pupil, no markings inside it. Gi, trousers, sleeves, gloves and boots all BLACK, modelled in dark grey brush, with RED trim — a red sash knotted at the waist with hanging ties, red banding at both forearms, red strapping across the chest, red cross-lacing at both shins and on the boots. A RED scarf (#ef4444) knotted at his neck with TWO separate long trailing tails. He carries EXACTLY TWO small tantō — short silver steel blades with small dark guards and TAN CORD-WRAPPED handles — ONE IN EACH FIST, both in REVERSE (icepick) grip: the blade exits the little-finger side of the fist and hangs DOWN AND OUTWARD at about 45 degrees with the tip near knee height. Both knives are visible and gripped in every single frame.

THE MOVEMENT — this is a WALK, not a run, and it must not be mistakable for one. A low gliding suri-ashi advance: the soles SKIM the floor and never clear it, hips low and LEVEL, the head rising and falling only about 4-5 source px across the whole cycle, and the ARMS COMPLETELY STILL — both blades hang in his idle carriage at his sides for all eight frames and never swing with the legs. A counter-fighter gives nothing away: the legs do all the work and the upper body says nothing. At full contact the feet open to about three-quarters of his standing height — wide and low, but never so wide that a blade tip or a scarf tail leaves the frame. It is a true loopable cycle of two strides: frame 8 must flow straight back into frame 1.

THE 8 BEATS IN ORDER:
1. Contact, stride fully open — lead foot flat well forward, rear foot flat behind with the heel breaking, both knees bent, hips low, torso vertical, both arms hanging dead with the blades down-and-outward at knee height, chin level, scarf tails out behind at shoulder height.
2. Low point — rear foot skims forward with the sole grazing the floor, lead knee deepest, head at its lowest, hips level, arms and blades unchanged, scarf tails sagging back.
3. Passing — feet together directly under the hips, ankles almost touching, both soles down, body at mid-height, torso vertical, arms still, only the lead wrist rolled a few degrees, scarf tails at their lowest.
4. High point — the passing foot slides out ahead toe-first with the sole skimming, support leg tallest, head at its highest, shoulders level, blades unchanged, scarf tails lifting and trailing straight back.
5. Contact mirrored — the travelling foot lands flat well forward with the opposite leg leading, the other foot flat behind; the arms do NOT swap duty, both still hang dead in the same carriage, torso vertical, scarf tails out behind.
6. Low point mirrored — new rear foot skims forward, lead knee deepens, head at its lowest, hips level, arms and blades still.
7. Passing mirrored — feet together under the hips, both soles down, torso vertical, mid-height, blades quiet, scarf tails lowest.
8. High point mirrored and winding back — pushing foot extends forward with the sole skimming, support leg tall, head highest, the lead shoulder already turning back toward frame 1's angle so the cycle loops seamlessly, scarf tails lifted and streaming back.

NEVER: a hood, a cowl, long or tied-back hair, a katana or any long sword, a third knife, an empty hand, a forward sabre grip, two visible eyes, a coloured iris or a pupil, arms swinging with the legs, either foot lifted clear of the floor, a deep forward sprint lean, white speed-streak brush marks on the limbs, purple, orange, or gold costume accents (the tan cord on the knife handles is correct and stays), a second character, captions, frame numbers, panel borders, or any drawn floor, scuff, dust or debris.
```

**Pitfalls for this fighter**

- THE WALK WILL COME BACK AS HIS RUN, AND THE OLD BRIEF DESCRIBED THAT RUN WRONG. Measured from the sheet, run_clean1..8 (cells 230-237) is NOT a deep sprint lean with the arms swept back behind the hips: the torso is near-vertical, the arms swing forward and back with the legs, both blades are driven down-and-FORWARD, both feet leave the floor on beats 2/4/8, and white dry-brush speed slashes are baked onto the limbs. That means the walk cannot be separated from the run by posture or stride. The only three differentiators the art can carry are: soles that never clear the floor, arms that never swing, and no speed slashes. If the board comes back with arm swing, it is a duplicate of a packed row.
- STRIDE LENGTH IS NOT THE DIFFERENTIATOR, AND CANNOT BE. Measured: moveSpeed = 350 x (9/6) = 525 px/s (web/index.html:4751 with stats.speed 9 at :1473); walk vx = 525 x WALK_FRAC 0.5 = 262.5 px/s (:2934, :4905). animPhase runs at min(3, 262.5/150) x 8 cells = 14 cells/s (:4644-4645, cell count from :4640-4642), so one 8-beat cycle is 0.571s and covers 150 world px = 75 px per step = ~205 source px at scale 0.3663. The RUN at 525 px/s clocks min(3, 3.5) x 8 = 24 cells/s, a 0.333s cycle, 175 world px, 87.5 per step = ~239 source px. Walk and run steps are only 17% apart. Worse, the packed run row draws only 133-144 source px of TOTAL ink width (cells 230-237), so it already skates. Draw the widest low stride that fits the 301px cell with both blade tips and both scarf tails inside; the residual skate is an engine property no drawing fixes.
- WEAPON COUNT AND GRIP. Exactly TWO tantō, one per fist, in all 8 frames. RECOVERY/MOVE-LISTS.md:158 — "exactly TWO short silver knives, never full swords, never a hood"; :159 locks BLADES=2; tsubasa.json declares martial_art_discipline "Tantōjutsu (Reverse-Grip)". And the grip is drawn, not described: on the idle (cell 59) each blade hangs DOWN AND OUTWARD from the fist at roughly 45 degrees with the tip near knee height. It does NOT lie back along the forearm — an earlier brief said it did, and that phrasing produces the wrong silhouette.
- HANDLE COLOUR — the handles are TAN CORD WRAP with a small dark guard, verified on cells 53-60. A blanket "no gold or yellow anywhere" rule strips the correct wrap and is the reason it has been drawn dark red before. Ban gold as a COSTUME accent (that is the Story Bible's comic-only line, shadowclash-story-bible.md:286, and Kael's colour); keep the tan on the knives.
- HOOD — he is the ONLY unhooded member of the roster and generators re-hood him by reflex (owner corrective 2026-07-17, Second Brain '11 - Art Implementation Instructions.md':42). The superseded reference sheet showed a HOODED Tsubasa with TWO KATANAS; if any of that leaks in, the board is dead.
- EYE — ONE visible eye, not two. The whole packed sheet is a three-quarter view with the far eye hidden in the hair sweep; idle, run, roll, jflight and divecut all read a single eye. It is blank glowing WHITE: web/index.html:1469 sets colors { primary: "#ef4444", eye: "#ffffff", tunic: "#374151", scarf: "#ef4444" }. Draw it SOLID white, not near-white — the keyer ate his near-white eyes once and 24 cells across mizu/tsubasa/ember had to be refilled (docs/CLAUDE-CHARACTER-ATTACK-FRAME-VFX-BRIEF-2026-09-05.md:18). Do NOT import the Story Bible's comic canon of hazel-red irises with round black pupils (shadowclash-story-bible.md:286).
- #374151 IS THE UI SWATCH, NOT THE INK. The drawn gi, sleeves, gloves and boots are BLACK with dark grey brush modelling and red trim. Quoting the hex at a generator produces a slate-blue-grey costume that does not match a single packed cell.
- A DRAWN GROUND BAR — his own sheet already carries this exact defect: roll_3 (cell 240) and roll_6 (cell 243) have a horizontal grey floor line plus kicked-debris spikes baked into the cell, verified by eye. Every ground shadow in the game was deleted at 798. The packer welds the board's lowest ink to the floor line, so a floor bar, a scuff, a dust puff or a contact smear makes him hover — the row cannot be packed.
- SCALE DRIFT — measure the HEAD, never total ink height and never bbox height (bbox height is banned: wide strides and a flying scarf both inflate it, and the VFX brief bans total ink area at docs/CLAUDE-CHARACTER-ATTACK-FRAME-VFX-BRIEF-2026-09-05.md:14). The reference is `idle` = CELL 59, not 55: ink y120-y310 = 190 source px in a 301x332 frame, head ~75 px, i.e. ~2.5 head-heights. (Cell 55 is xidle3, a different row.) Every one of the 8 beats must carry the same head height.
- FOOT-ANCHOR. This is a GROUNDED row and it packs foot-anchored to footY 312 (tsubasa.json). A board whose sole height wanders between beats packs with a 3-5px bob.
- CUT-OFF SCARF OR BLADE — a tail or a blade tip ending in a straight edge at the cell boundary. VFX brief :15 and :17: frame the union with transparent margin, and nothing ends in an accidental hard cut. He has TWO scarf tails, not one — both must be whole.
- ONE ROW PER PROMPT, ONE BOARD. A second row in the same image changes the body size.
- ENGINE ASK (the row is nearly invisible without it): the WALK tier is art-gated on `walk1` (web/index.html:4903) and NO sheet in the game has it, so this board lights the state up for the first time. But WALK_TIME is 0.15s (:2933) and at 14 cells/s only ~2.1 cells advance before the state flips to RUN — beats 1-3 and nothing else would ever be seen. Raise WALK_TIME to ~0.57s to let one full 8-beat cycle play. Draw all 8 as a true loop regardless.


---

## Row B — `airhurt1..8` — the launched hurt arc

**Intent.** The player should feel that he has been switched off — for these eight frames the most precise body in the roster has no say in where it goes. It is the exact inverse of his jump row, where he stays composed through the whole arc.

**Beats**

1. BEAT 1 — THE POP (rising hardest). Both feet torn off the floor and still trailing BELOW him, soles pointing back and down, toes dragging. Spine hyperextended backwards, chest thrown up and out, shoulders behind the hips. Head snapped back hard, chin up, throat exposed, the hair spikes flung back flat by the speed. Both arms flung wide and back, elbows soft, and the two arms at clearly DIFFERENT angles. Both tantō still gripped but the wrists broken loose so the blades point down and back at odd, unmatched angles. Both red scarf tails whipped straight DOWN beneath him.
2. BEAT 2 — RISING HARD. The arch straightens into a long stretched line tilted back off vertical; hips lead the rise, legs trail loose and apart with the knees unlocked and the ankles flopping — one leg noticeably longer and lower than the other. Head still back but lolling to one side. Both arms now above and behind the head, forearms limp; the two blades cross each other ACCIDENTALLY, not in any guard. Scarf streaming down and back beneath him.
3. BEAT 3 — RISE SLOWING. The stretched line starts to fold: the chest caves in, the shoulders roll up around the ears, the head drops toward the sternum WITHOUT tucking — the neck has given way, it has not curled. Knees float up and drift apart, one clearly higher than the other. Arms hang above him with the blades dangling point-down out of slack fists at two different angles. Scarf collapsing, one tail curling in on itself while the other still trails.
4. BEAT 4 — APEX, THE RAG (weightless). NO muscle tone anywhere in the body. He hangs almost HORIZONTALLY, spine curved into a shallow C. The neck is given up entirely: the head hangs BELOW the shoulder line with the face turned toward the floor, and the hair spikes are flung out away from the direction of travel instead of sitting where they sit at rest. Both shoulders are shrugged up around the head by the dead weight of the arms; both arms hang straight down beneath him and both blades point at the floor from fully broken wrists, hanging at DIFFERENT angles. One leg trails out long, the other knee drifts up — the legs must not mirror. Feet limp, toes pointing nowhere. One scarf tail folded slack across his own body, the other hanging free. Cover the head and the silhouette must not tell you which way he is facing: a dropped puppet, not a pose.
5. BEAT 5 — THE TIP OVER. Weight begins to fall; the torso folds forward over the hips and the head swings down past the knees. The arms now begin to TRAIL UPWARD relative to the body as the body drops away from them — the blades still point down but the elbows have risen above the shoulder line, one higher than the other. Legs open out behind him at uneven angles, soles turned up. Scarf tails starting to lift.
6. BEAT 6 — FALLING. Head clearly lower than the hips, body curled forward over the middle with the back rounded. Both arms fully trailing above him, elbows above the head, the two blades hanging point-down from dead fists. Knees loosely drawn up but not together, feet trailing above and behind at different heights. Scarf tails streaming straight UP.
7. BEAT 7 — FALLING HARD. The curl loosens under speed: the body stretches out head-down and slightly head-first, every limb trailing upward and fanned at a different angle — arms above, legs above and apart, everything lagging behind the falling hips. The head is the lowest point of the body, the face slack, the single white eye still open and blank. Scarf tails whipped straight up above him and fluttering.
8. BEAT 8 — FALLING HARDEST, NEAR THE FLOOR AND STILL NOT IN CONTROL. The body has rotated so the hips are now lowest and the shoulders lag behind; one shoulder drops, one hip leads, and the near leg has swung down under him BY ACCIDENT rather than intent — toe down but the ankle limp and the knee unlocked. The far leg still trails above. Arms still above him, both blades still hanging. The head hangs back off the shoulders. Scarf tails straight up. This beat must NOT read as a landing: no bracing, no tuck, no guard, no planted foot.

⛔ **Packing: this row has NO stance beat.** The packer anchors scale on beat 1 by default, and
beat 1 here is the pop — the most extended frame in the row. Anchoring there packs the whole row
too small. Pass `--scale` taken from this fighter's idle, or `--anchor` at the most neutral beat.
The union of an 8-beat arc is also taller than a standing pose, so budget `grow_frame.py --down`
if the dry run prints `REFUSE: scaled window exceeds cell`.

**Prompt**

```text
Draw ONE sprite row of the ShadowClash fighter TSUBASA being LAUNCHED and juggled — the airborne hurt arc.

8 frames in one horizontal row, evenly spaced, identical camera, identical character scale in every frame, full body with both feet visible in every frame, plain flat background, no ground line, no cast shadow, no floor bar, no drawn floor of any kind, no motion-blur smear across the frame edge. Every frame's whole figure — both blade tips and both scarf tails included — sits inside its frame with transparent margin; nothing ends in a straight cut at an edge.

STYLE: sumi-e / shodō ink-brush styling — heavy, uneven black brush outlines with real pressure variation, ink pooling, ragged dry-brush breakup and tapered ends, over flat controlled cel shading. No pixel art, no 3D, no painterly rendering. Side-on 2D fighting-game view, three-quarter angle facing LEFT with the torso turned slightly toward the camera.

CHARACTER — EXACT, NO DEVIATION: Tsubasa, he/him. A chibi ninja about 2.5 head-heights tall counting his hair spikes, compact build, short limbs. NO HOOD and NO COWL — wild spiky BLACK hair with bright RED flame-shaped streaks. A black cloth mask over nose and mouth with a single thin RED slash across the bridge. At this three-quarter angle only ONE eye reads: a single large solid WHITE almond eye (#ffffff), no iris, no pupil, and it stays OPEN and blank through all 8 frames. Gi, trousers, sleeves, gloves and boots all BLACK, modelled in dark grey brush, with RED trim — a red sash at the waist, red banding at both forearms, red strapping across the chest, red cross-lacing at both shins and on the boots. A RED scarf (#ef4444) at his neck with TWO separate long trailing tails. He carries EXACTLY TWO small tantō — short silver steel blades with small dark guards and TAN CORD-WRAPPED handles — ONE IN EACH FIST. He is NOT disarmed: both knives stay gripped in every frame in REVERSE (icepick) grip, blade out of the little-finger side, but the wrists are SLACK so the blades hang at odd angles instead of being held in any guard.

THE MOVEMENT: he has been hit by a launcher and popped into the air. This is the ONE row where his silhouette must look BROKEN rather than composed — there is no fighting stance anywhere in it. One continuous arc across the 8 frames, read in strict order from RISING HARDEST to FALLING HARDEST: the pop (feet torn off the floor, spine arching back, head snapping), then the apex (utterly limp, weightless, no muscle tone — a rag, not a pose), then the fall (folding forward with every limb and the scarf trailing ABOVE him). SYMMETRY READS AS CONTROL AND HE HAS NONE: in no frame may the two arms mirror each other, the two legs mirror each other, or the two scarf tails do the same thing. The scarf is the compass for which way he is moving — it hangs straight DOWN while he rises, goes slack and folded at the apex, and streams straight UP while he falls. Never repeat a pose; every frame is a different point on one arc.

THE 8 BEATS IN ORDER:
1. The pop, rising hardest — both feet torn off the floor and trailing below, spine hyperextended backwards, chest thrown up, head snapped back with the chin up and throat exposed, hair flung back, both arms flung wide and back at different angles, both blades pointing down and back unmatched, scarf tails whipped straight DOWN.
2. Rising hard — the arch straightens into a long line tilted back, hips leading, legs trailing loose and uneven with unlocked knees and flopping ankles, head still back but lolling to one side, both arms above and behind the head with limp forearms, the two blades crossing accidentally, scarf streaming down and back.
3. Rise slowing — the chest caves, shoulders roll up around the ears, the head drops toward the sternum because the neck has given way, not because he tucked; knees float up and drift apart at different heights, arms hang above him with the blades dangling point-down from slack fists at two different angles, scarf collapsing with one tail curling and the other trailing.
4. Apex, the rag — hanging almost horizontally with no muscle tone anywhere, spine in a shallow C, the neck fully given up so the head hangs BELOW the shoulder line with the face toward the floor and the hair spikes flung out away from the direction of travel, both shoulders shrugged up around the head by the dead weight of the arms, both arms hanging straight down with both blades pointing at the floor from broken wrists at different angles, one leg trailing long and the other knee drifting up, feet limp, one scarf tail folded slack across his own body and the other hanging free. Cover the head and you must not be able to tell which way he faces. A dropped puppet, not a pose.
5. The tip over — the torso folds forward over the hips, the head swings down past the knees, the arms begin to trail UPWARD relative to the body with the elbows rising above the shoulder line at uneven heights while the blades still point down, legs opening out behind at uneven angles with the soles turned up, scarf tails starting to lift.
6. Falling — head clearly lower than the hips, the body curled forward with a rounded back, both arms fully trailing above him with the elbows above the head, both blades hanging point-down from dead fists, knees loosely drawn up but not together, feet trailing above and behind at different heights, scarf tails streaming straight UP.
7. Falling hard — the curl loosens under speed, the body stretched head-down and slightly head-first, all four limbs trailing upward and fanned at different angles, the head the lowest point of the body, the face slack and the white eye still open, scarf tails whipped straight up and fluttering.
8. Falling hardest — the hips are now lowest and the shoulders lag, one shoulder dropped and one hip leading, the near leg swung down under him by accident with the toe down but the ankle limp and the knee unlocked, the far leg still trailing above, arms still above with both blades hanging, the head hanging back off the shoulders, scarf tails straight up. NOT a landing: no bracing, no tuck, no guard, no planted foot.

NEVER: a hood, a cowl, long or tied-back hair, a katana or any long sword, a third knife, an empty hand, a forward sabre grip, a composed fighting stance, a defensive guard, a braced landing pose, a symmetrical pose of any kind, a deliberate tuck, a closed or expressive eye, two visible eyes, a coloured iris or a pupil, purple, orange, or gold costume accents (the tan cord on the knife handles is correct and stays), a second character, captions, frame numbers, panel borders, or any drawn floor, dust, impact burst or debris.
```

**Pitfalls for this fighter**

- THE GENERATOR WILL DRAW A COMPOSED POSE — and that is exactly the defect being replaced, verified by eye on the sheet. His current 3-beat flinch is airhurt1 = cell 363, airhurt2 = cell 363 (the SAME drawing twice) and airhurt3 = cell 294. Cell 363 is a tidy hunched curl with both blades still in a readable downward guard; cell 294 is nearly upright with the blades hanging in his normal carriage. Only TWO distinct pictures exist today for three beats, and neither reads as hurt. If any frame of the new row carries a readable stance, it has failed.
- THE APEX IS THE WHOLE ROW AND IT IS THE FRAME MOST OFTEN DRAWN WRONG. "Chin on chest" is a TUCK, which is a controlled shape — the correct read is a neck that has given way, so the head hangs BELOW the shoulder line. Two hard tests for beat 4: (a) no two paired parts may match — arms, legs, blade angles, and the two scarf tails must each be doing different things; (b) mask the head and the silhouette must not reveal which way he is facing.
- HAIR AT THE APEX — say "flung back by the motion", never "drooping". His hair is drawn as stiff black spikes with red streaks; "drooping" gets read as soft long hair and breaks the identity silhouette that Second Brain '11 - Art Implementation Instructions.md':42 locks.
- WEAPON COUNT — exactly TWO tantō, one per fist, in all 8 frames, even limp. RECOVERY/MOVE-LISTS.md:158-159 lock "exactly TWO short silver knives, never full swords, never a hood" and BLADES=2. A limp hand is not an excuse to drop a knife, and a rag pose is not an excuse to grow a third.
- GRIP — reverse (icepick) grip, blade out of the little-finger side, tan cord handle. Slack wrists change the blade ANGLE, not the grip. Generators flip to a forward sabre grip whenever the hand goes loose.
- HOOD — the only unhooded fighter on the roster; the superseded reference showed him hooded with two katanas (Second Brain '11 - Art Implementation Instructions.md':42). A flying-hair hurt pose is where a hood gets reintroduced most often.
- EYE — ONE visible eye, blank glowing WHITE (web/index.html:1469, eye: "#ffffff"); the packed sheet is a three-quarter view and the far eye is inside the hair sweep in every row. Do not close it, do not add expression lines, and draw it SOLID white — the keyer previously ate his near-white eyes and 24 cells needed refilling (docs/CLAUDE-CHARACTER-ATTACK-FRAME-VFX-BRIEF-2026-09-05.md:18). NOT the Story Bible's comic-only hazel-red irises with round black pupils (shadowclash-story-bible.md:286).
- SHADOW OR GROUND ANYWHERE — this is an airborne row; there is no floor in any frame. His roll row already ships the failure (cells 240 and 243 carry a drawn horizontal grey floor line plus debris spikes, verified by eye), and every ground shadow in the game was deleted at 798. The packer welds the lowest ink to the floor line.
- SCALE DRIFT — measure the HEAD only, never bbox height and never total ink area (banned at docs/CLAUDE-CHARACTER-ATTACK-FRAME-VFX-BRIEF-2026-09-05.md:14): a hyperextended beat 1 and a flung-open beat 7 both blow up a bbox and make a correctly sized body look wrong. Reference is `idle` = CELL 59 (not 55): ink y120-y310 = 190 source px in a 301x332 frame, head ~75 px, ~2.5 head-heights.
- BEAT ORDER MUST BE PHYSICALLY READABLE. The engine bands this row on the victim's vertical velocity (web/index.html:12310, currently `p.vy < -80 ? 1 : p.vy > 100 ? 3 : 2`), so the beats are selected by how fast he is going up or down, not by a timer. If beat 5 reads as more "rising" than beat 3, the row plays out of order in the game. The scarf is the reader's compass: down while rising, slack at the apex, up while falling.
- DO NOT PACK BY REPOINTING THE EXISTING CELLS. Cell 363 is also grabbed3 and grabbed4; cell 294 is also grabbed5. Overwriting either cell silently rewrites his grab-tumble row. Append the 8 new cells and repoint only airhurt1..airhurt8. The sheet is 511 columns with cell 510 already in use, so it has to grow.
- CUT-OFF LIMBS OR SCARF at the frame edge — beats 1, 7 and 8 have the widest limb fan. Frame the union with transparent margin rather than cropping a hand, a boot, a blade tip or either scarf tail (VFX brief :15, :17). He has TWO tails and both must be whole.
- PALETTE — black with dark grey brush modelling, red #ef4444 trim, silver steel, tan cord on the handles, one white eye. #374151 in web/index.html:1469 is the UI card swatch, not the ink: quoting it produces a slate-blue-grey costume that matches no packed cell. No purple, no orange, no gold costume accents. No hit-flash, spark or impact VFX baked into the cells — that is the attacker's art.
- ONE ROW PER PROMPT, ONE BOARD — a second row in the same image changes the body size.
- ENGINE ASK: the branch at web/index.html:12308-12311 picks from only THREE bands. An 8-beat row needs eight. For the roster's measured launch range (launchVy -200 at :9024 up to -560 at :7676, GRAVITY 1100 from the engine_settings at :930/:936 via :1622) an equal-time recut on a typical -430 pop is vy <= -322, -322..-215, -215..-107, -107..0, 0..+107, +107..+215, +215..+322, > +322 — eight beats of about 98ms each. Without that recut, five of the eight drawings are unreachable.


---

## Row C — `njump1..8` — the second jump — Tsubasa — the tightest ball on the roster

*Precision as a religion. The smallest, cleanest revolution — no wasted arc.*

> 8 frames in one horizontal row, evenly spaced, identical camera and identical character
> scale in every frame. Full body, both feet visible, nothing touching the frame edge. Plain
> flat background, no ground line, no cast shadow, no floor bar. Side-on 2D fighting-game
> view, sumi-e ink-brush shodō styling on ash grey.
> A lean young ninja, **no hood**, spiky black hair with red streaks, black and dark-red
> outfit with a long red scarf, holding **exactly two small tantō knives in reverse grip**,
> performing a tight forward somersault in mid-air.
> Frame 1: feet leaving, knees starting up, chin tucking, scarf snapping straight down.
> Frame 2: knees to chest, arms drawing in, both knives crossed flat over the shins.
> Frame 3: a tight compact ball, body a quarter turn forward, scarf beginning to whip round.
> Frame 4: half turn, fully inverted, ball as small as it gets, scarf a red ring around him.
> Frame 5: three-quarter turn, the ball just starting to open, knees releasing.
> Frame 6: legs extending downward, arms opening, knives coming back to guard.
> Frame 7: nearly upright, legs reaching for the ground, body still angled forward.
> Frame 8: upright, knees soft, both knives in reverse-grip guard, scarf settling.


⛔ **Packing: no stance beat here either.** Same `--scale` / `--anchor` rule as Row B, and
the rotation makes the union taller still.
