# EMBER — walk · launched hurt · second jump

Part of `SHODO-WALK-LAUNCH-NINJAJUMP-BRIEF-2026-09-15`. Read `README.md`, `BOARD-SPEC.md`
and `PROMPTS.md` §0–§1 first — the canon table and the eight hard rules are there and they
are not repeated per fighter.

**Sheet:** cell `340x390`, aspect **0.87**, `footY 369`, scale `0.3414`, `cols 517`.
**Reference:** `refs/ember-refs.png` (idle, current jump, current air-hurt, landing) and
`refs/ROSTER-true-scale.png` for how tall this fighter is against the others.

⛔ **The refs are cut from the live sheet and some cells still carry drawn ground** — a pale
scuff or a contact smear under the boots. Match the BODY off them, never the floor.

---

## Row A — `walk1..8`

**Intent.** The player should feel a predator closing distance on purpose - unhurried, head-low, hooks already at ankle height, arriving in range without ever standing up straight.

**Beats**

1. BEAT 1 - LEAD CONTACT. Front boot flat on the line, whole weight over it; rear boot behind with heel lifted and only the toe down. Hips low and level at exactly the feral-idle height (cell 505), knees bent out. Hood thrust forward at shoulder height, single pale eye aimed forward-down. Lead claw-hand hangs low and forward, its three blade tips raking at ankle height and hanging BELOW the boot soles. Rear cuff cocked at chest height, its three blades angled down and back. Scarf tails settled, hanging back. Sash tails vertical.
2. BEAT 2 - REAR FOOT PEELS. Rear boot leaves the floor, knee folding up and forward under the hip, toe pointed down. Body lifts about 3px, no more - the hood must NOT bob. Lead claw-hand swings back toward the hip, the three blades trailing behind the wrist. Rear cuff drifts forward a little, blades still down. Spine stays in the prowl curve, chest low, shoulders ahead of the hips. Scarf tails begin to lift.
3. BEAT 3 - PASS. Rear leg passes the standing leg, boot at mid-shin, toe still down. Body at the top of its small rise (about +5px from beat 1) - the highest beat, and still lower than a standing pose. Lead arm back at the hip; rear arm reaching forward, cuff arriving at waist height, three blades levelling out ahead. Hood level, eye tracking straight down the line. Scarf tails drift forward off the shoulder.
4. BEAT 4 - REACH, NO CONTACT. Rear boot reaches ahead and hangs a few px above the floor, toe searching, KNEE STILL BENT - no straight-leg lock anywhere in this row. Body sinking back toward beat-1 height. That forward hand is now the lead: three blades dropping toward ankle height. Trailing boot rolling onto its toe behind. Hood pushes forward a few px further than beat 3, eye down.
5. BEAT 5 - OPPOSITE CONTACT. Beat 1's pose on the other leg - NOT a flipped frame: body, hood and eye still face left, the near and far legs simply swap. Reaching boot lands toe-first then flat, weight transferring onto it; the other boot is now the rear one with its heel peeling. Hips back to idle height. New lead claw low and forward, three tips at ankle height and below the soles; new rear cuff cocked at the chest. Hood at shoulder height, eye forward-down. Scarf tails swing back and settle.
6. BEAT 6 - OPPOSITE PEEL. Beat 2 on the other leg, same facing. New rear boot leaves the floor, knee folding up under the hip, toe down. Small 3px lift. New lead claw-hand swings back to the hip, three blades trailing. Rear cuff drifts forward. Prowl curve held, hood dead level.
7. BEAT 7 - OPPOSITE PASS. Beat 3 on the other leg, same facing. Passing boot at mid-shin, body at the top of the rise. Lead arm at the hip, rear arm reaching forward with the cuff at waist height. Hood level, eye down the line. Scarf tails forward.
8. BEAT 8 - OPPOSITE REACH, ALREADY WRAPPING. Beat 4 on the other leg, same facing, but already committing back into beat 1: hips squaring up, reaching boot a few px above the floor with the knee bent, lead claw dropping to ankle height, hood level and forward. Read this beat and beat 1 side by side - the hips, hood height and lead-claw height must be within a couple of px of each other so the cycle wraps without a snap.

**Packing:** every beat is a stance, so the default beat-1 anchor is correct. `--dry` first.

**Prompt**

```text
8-frame sprite sheet, sumi-e / ink-brush shodo styling, side-on 2D fighting-game view, character FACING LEFT in every frame.

CHARACTER - EMBER (fixed canon, identical in all 8 frames):
Male chibi / super-deformed ninja, about 3 to 3.5 heads tall - big head, short thick limbs, wide low stance. He wears a DEEP SMOOTH POINTED COWL in soft-washed ash grey, tapering to a long point that sweeps back off the crown - no facets, no ridges, no horn - edged along its opening with a pale bone-coloured rim band. Inside the hood opening is a SOLID BLACK VOID - NO FACE. No second eye, no mouth, no nose, no chin, no skin. The ONLY feature is ONE pale, closed, leaf/teardrop-shaped eye floating in that void. A pale wrapped bandage encircles his neck and crosses his chest diagonally; a knotted pale sash at the waist with two short hanging tails. From the nape springs a fan of ragged, torn, flame-shaped banner-tails (his scarf), each with a split jagged tip. Both forearms are stacked SEGMENTED RING VAMBRACES ending in a heavy studded, riveted knuckle-cuff. From EACH cuff spring THREE long curved ivory blades - tekko-kagi hooks. THREE PER HAND, SIX TOTAL - never four, never five. He carries NO sword, NO tanto, NO staff, NO kama. Heavy short boots.
MONOCHROME INK ONLY: sumi black through warm ash grey on warm off-white washi paper, with bone-white highlights on the blades, the hood rim and the wrappings. No colour anywhere.

SHEET RULES: 8 frames in one horizontal row, evenly spaced, identical camera, identical character scale in every frame, full body with both feet visible in every frame, plain flat background. NO ground line, NO floor bar, NO cast shadow, no dust, no scuff marks, no drag streaks, no speed lines, no motion-blur smear across a frame edge, no frame numbers or captions. Nothing at all may be drawn below his lowest body ink.

THE ACTION - A STALK, NOT A STRIDE. This is a WALK cycle at half his run speed. He does NOT stand up to walk. He stays in his low four-square predator prowl the whole way: hips low, knees bent out, chest low, shoulders ahead of the hips, hood thrust forward at shoulder height, lead claw-hand hanging down and forward with the blade tips at ankle height. Feet are placed toe-first and quiet, like a cat. Two steps across the 8 frames, contact on frames 1 and 5. Frame 8 must flow straight back into frame 1 as a true seamless loop. The step reaches a normal walking length - roughly four fifths of a full sprint stride - not a mincing shuffle.
THE SECOND STEP IS NOT A MIRRORED IMAGE. Frames 5-8 are frames 1-4 with the LEGS AND ARMS SWAPPED - the near leg becomes the far leg - while the body, hood and eye still face LEFT exactly as in frames 1-4. Do not flip any frame horizontally.

THE 8 BEATS IN ORDER:
1. Front boot planted flat, full weight over it; rear boot behind on its toe with the heel lifted. Hips at the lowest prowl height. Lead claw low and forward, three blades raking at ankle height and hanging below the soles; rear cuff cocked at the chest, blades down-back. Hood forward, eye forward-down.
2. Rear boot peels off the floor, knee folding up and forward under the hip, toe pointed down. Body rises a hair. Lead claw-hand swings back to the hip, blades trailing. Hood stays dead level - no head bob.
3. Rear leg passes the standing leg, boot at mid-shin, toe down. Top of the small rise, still lower than a standing pose. Lead arm at the hip, rear arm reaching forward with the cuff at waist height. Scarf tails drift forward.
4. Rear boot reaches out ahead and hovers just above the floor, toe searching, knee still bent - never a straight locked leg. Body starting to sink. That forward hand becomes the lead, its three blades dropping toward ankle height. Hood pushes a little further forward.
5. Frame 1 on the opposite leg, same facing: the reaching boot lands toe-first then flat, weight transferring; the other boot is now behind with its heel lifting. Hips back to prowl height. New lead claw low and forward at ankle height.
6. Frame 2 on the opposite leg: new rear boot peels off the floor, knee folding up under the hip. Lead claw swings back to the hip.
7. Frame 3 on the opposite leg: passing boot at mid-shin, top of the rise, rear arm reaching forward at waist height.
8. Frame 4 on the opposite leg, already swinging back into frame 1: hips squaring, reaching boot just above the floor with a bent knee, lead claw dropping to ankle height, hood level and forward. Frame 8 and frame 1 must share the same hip height, hood height and lead-claw height so the loop wraps invisibly.
```

**Pitfalls for this fighter**

- CANON FIX - THREE CLAWS PER HAND, NOT FOUR. Verified by 12x zoom on BOTH cuffs of packed cell 505: three long curved ivory blades each, six total. web/index.html:11051 entry 835 states the ruling verbatim - 'HE NOW HAS THREE CLAWS PER HAND ON THE IDLE AND FOUR EVERYWHERE ELSE ... the owner asked for both thumb blades removed, and his newest boards are named three-claw-corrected, so three is the live direction'. The old 'four, never shrink to three' note is withdrawn. Drawing four puts the new row out of step with the idle it has to loop into.
- CANON FIX - THE HOOD IS SMOOTH, NOT FACETED. 'Faceted ridged surface with a raised horn-like peak' describes the RUN row (cell 419), a different and older treatment. The idle board this row must match (cell 505) is a soft-washed deep cowl with a long back point and a pale bone rim along the opening. Match 505, not 419.
- STANDING HIM UP. His idle is a 12-beat wrapped feral prowl: xidle1..xidle12 = packed cells 505-516, read whole by rowCells(F,'xidle') at web/index.html:14007 and wrapped one beat per animPhase tick at 3/s (14015-14017, full cycle every 4 s). A walk drawn at standing height pops him ~20px taller the instant a direction is pressed and snaps back on release. Same hip height, same hood height, same eye-line as cell 505.
- FACING RIGHT. The roster is authored FACING LEFT and the engine mirrors toward the opponent (web/index.html:14304 `p.drawMirror = onWall ? p.facing : -drawFacing;` with the ruling at 14306-14312: 'a cell that was drawn facing RIGHT comes out facing AWAY from the opponent for the entire move'). Generators default to facing right. Verified by zoom: on cell 505 the hood opening and the pale eye sit on the LEFT edge of the head. NOTE FOR THE OWNER: the packed run row reads the other way - cell 419's eye is on the RIGHT - and ember.json's `mirror` map (51 entries) covers none of 416-423 or 505-516. Worth his eye before the board is drawn.
- A FACE. Told 'ninja', a generator draws two eyes and a mouth. Ember's hood opening is a solid black void with exactly ONE pale leaf-shaped eye and nothing else. A second eye, a mouth, a visible chin or a bare head kills the identity.
- THE EYE AS AN OPEN NOTCH OR A DRIFTING SHAPE. The eye is a WHITE-DRAWN ENCLOSED POCKET; the packer hunts it by name and guards it with a 7x7 dilation (web/index.html:11051 entry 836 - 'POCKETS=drop cuts every pocket and Ember's EYE is a white-drawn pocket, so that blinds him'). The same class of defect punched Shin's eye into a hole (11190-11192). One closed pale shape, same size, same place in the void, in all 8 frames, never touching the hood rim.
- ENCLOSED NEGATIVE SPACE BECOMES A SOLID INK SLAB. The biggest enclosed page region on the approved idle board is the ~3200px gap between his legs, and the default packer rule recolours an enclosed region to the surrounding ink (web/index.html:11051 entry 836). Keep the gap between his legs open to the frame edge on every beat; outline any genuinely enclosed pocket cleanly.
- DRAWING THE GROUND. Owner ruled DELETE on Sep 15 2026 for the drawn contact on this very board - pale boot scuff, dark claw-drag streaks on beats 5-9, kicked-up dust, 1076-1958px per beat (web/index.html:11051 entry 837), following 798 which deleted every ground shadow in the game. It is near-unremovable on HIM specifically: his ivory claw bodies read exactly like a pale scuff and his drag streaks are as dark as his boots, so stripping them needed a three-signal detector. Zero ground ink.
- CONTACT HOLDS OR AN ACCENTED BEAT. The walk paces FLAT with no hold table - web/index.html:12533-12535, 'a walk is an even cadence, not a run's contact-hold ... this paces flat', `w[Math.floor(p.animPhase) % w.length]`. A beat drawn as a heavier slam just flashes past.
- UNDER-DRAWING THE STEP. Measured: moveSpeed = 350 x 9.5/6 = 554.2 px/s (4751) x WALK_FRAC 0.5 (2934) = 277.1 px/s; animPhase advances at min(3, 277.1/150) x 8 = 14.78 cells/s (4644), so one 8-cell cycle is 0.541 s and covers 150.0 world px, against 184.7 px for the existing 8-cell run row (run_clean1..8 = cells 416-423) at full speed. The walk step must reach about 81% of the run row's step or the feet skate.
- A COMMITTED LUNGING STRIDE THAT MOONWALKS. A grounded fighter always faces the opponent (web/index.html:4909-4911) and WALK is NOT in the travel-facing branch (14301-14303, which tests STATE.RUN only), so holding away plays walk1..8 forward while the body travels backwards. A low stalk with the weight under the hips reads correctly in both directions; a big committed lunge does not.
- EXPECTING THE ENGINE TO ADD LEAN OR DUST. The body-lean spring is gated to STATE.RUN (web/index.html:4658-4659) and footDust fires only on STATE.RUN (4647-4652). WALK gets neither, so the carriage must be drawn in - and no dust may be drawn in.
- SCALE OR VERTICAL DRIFT ACROSS THE ROW. The approved idle packs at scale 0.6186 against ink-area canon 18157 with -0.1..-0.3% deviation over all twelve beats and 1px of boot spread (web/index.html:11051 entry 837). The source board drifted: beats 11-12 were drawn 13 source px higher than beat 1 and every beat had to be re-registered onto beat 1's boot line (entry 836). And his bbox HEIGHT is not a valid ruler - measured on cell 505 the bbox is x66-274 y203-373 because the hood and the claws both leave the body box. QC on ink area, never on bbox height.
- LIFTING THE CLAWS TO SIT THE SOLES LOWEST. His claw tips are the lowest ink in the packed idle - the whole row had to be dropped 5px after packing because --floor-beat welds beat 1's INK bottom (web/index.html:11051 entry 837), and entry 835 records boots landing on row 366 = footY-3 with the forward claw fan hanging to 376. Boots on the line, blades hanging below them.
- DELIVERING IT IN COLOUR. Measured on cell 505 the packed sheet is achromatic - warm greys, no saturated pixels. The canon greens in the roster data (#84cc16 / #3f6212 / #15803d / eye #22c55e, web/index.html:1479) drive the UI and the vector fallback, not the shodo sheet, and the greens are deliberately left out of the prompt above so a generator cannot reach for them. A colour board will not match the twelve idle beats it has to loop into. ONE QUESTION FOR THE OWNER, not a decision to make for him.
- MEASURED CAVEAT - HE HAS NO WALK TIER AT ALL TODAY. There is no `walk*` key anywhere in ember.json (298 frames checked), and the tier is gated on the art: `const walking = this.isGrounded && this.walkT > 0 && wf?.walk1 !== undefined;` (web/index.html:4903). Until walk1 lands he goes straight to full-speed run; landing the row is what switches the feature on. Once it is on, WALK_TIME = 0.15 s (2933) x 14.78 cells/s = 2.22 cells, 9 frames at 60fps and 41.6 px of travel before RUN takes over (4905-4912), so beats 4-8 never draw until the owner raises WALK_TIME. Draw all 8 as a true loop anyway, but put the whole predator read into beats 1-3.


---

## Row B — `airhurt1..8` — the launched hurt arc

**Intent.** The player should feel that Ember has stopped being a fighter for a second - that the hit took him, not that he reacted to it - and want to keep hitting him while he is still up there.

**Beats**

1. BEAT 1 - THE POP (rising hardest, vy about -500). Both boots just torn off the floor, toes still pointing down and trailing below everything. Spine arched violently BACK into a C, chest thrown open to the sky, ribs leading. Hood snapped back off the crown, its point aimed down-and-back, the void open upward, the pale eye riding high in the opening and looking at nothing. Both claw arms flung DOWN and BACK from the shoulders, the heavy cuffs at hip level, all six blades trailing straight down. Scarf tails yanked straight DOWN past the boots. Sash tails straight down.
2. BEAT 2 - STILL RISING HARD (vy about -380). The arch releasing, body straightening, shoulders leading, hips beneath them. Knees just beginning to break. Boots still the lowest ink, ankles loose. Arms still trailing but floating outward now, cuffs rising to waist level, the six blades fanning apart. Hood still back, its point swinging toward horizontal. Scarf tails down and beginning to curl at the tips.
3. BEAT 3 - RISE DECAYING (vy about -220). Body rotating toward horizontal, face-up, one shoulder dropping lower than the other. One knee folds up, the other leg trails straight. Both arms out to the sides, cuffs at shoulder height, blades splayed wide - the cuffs rolled open, no grip tension anywhere. Hood horizontal, void aimed sideways, the eye dead centre and vacant. Scarf tails horizontal.
4. BEAT 4 - FLOAT-UP (vy about -60, nearly weightless). ZERO muscle tone. This is a rag, not a pose. Body near-horizontal and slack, spine in a loose S, head hanging back off the neck a beat BEHIND the torso. Both arms hang straight from the SHOULDER SOCKETS with no elbow angle held, the heavy cuffs the lowest point of each arm, the wrists broken so each cuff hangs at a different angle to its own forearm and the blades dangle and cross. The two legs hang at DIFFERENT angles - one knee up, one trailing - never symmetrical. Scarf tails curl loose in three different directions with no common line; the sash tails cross. NOTHING in this frame is parallel to anything else and no straight line runs through him.
5. BEAT 5 - APEX (vy about +20, the top of the arc). Nothing reads as a pose. Body folded slightly at the waist with the HIPS the highest point; head and boots both hang lower than the hips, and the head hangs lower than the shoulders. Hood tipped fully forward, point down, void aimed at the floor, eye looking straight down. Arms hang vertically from the shoulders, cuffs below the hood line, all six blades pointing at the floor and not aligned with each other. Knees, ankles and wrists all slack at different angles. Scarf and sash float outward and slightly UP, drifting, not streaming. If this frame could be read as an attack, a block or a flip it is wrong.
6. BEAT 6 - FALL BEGINS (vy about +160). Folding forward hard around the middle - the juggle fold, driven by the hit and not by him. Knees driving up toward the chest, boots still ABOVE the hips. Hood down, void to the floor, eye straight down. Arms now trailing ABOVE the shoulders, cuffs level with the hood, the six blades raked up and back. Scarf tails beginning to lift off the back.
7. BEAT 7 - FALLING (vy about +320). Body tipping back toward feet-down, hips dropping under the shoulders. Legs unfolding downward, boots below the hips, toes pointed down, ankles completely loose. Arms still fully trailing above and behind, cuffs above the hood line, all six blades raked upward. The hood is dragged back off the head by the airflow, its rim lifted; the eye still aims down. Scarf tails straight UP.
8. BEAT 8 - FALLING HARD (vy about +500). Near-vertical, boots the lowest ink, legs roughly straight but the knees and ankles slack - NOT braced, NOT reaching for a floor, he is still being juggled. Head down between raised shoulders, hood pressed flat back, void down. Both arms straight up past the ears, cuffs above the hood, all six blades a vertical fan overhead. Scarf tails and sash stretched straight up past the crown. Silhouette reads as a falling arrow.

⛔ **Packing: this row has NO stance beat.** The packer anchors scale on beat 1 by default, and
beat 1 here is the pop — the most extended frame in the row. Anchoring there packs the whole row
too small. Pass `--scale` taken from this fighter's idle, or `--anchor` at the most neutral beat.
The union of an 8-beat arc is also taller than a standing pose, so budget `grow_frame.py --down`
if the dry run prints `REFUSE: scaled window exceeds cell`.

**Prompt**

```text
8-frame sprite sheet, sumi-e / ink-brush shodo styling, side-on 2D fighting-game view, character FACING LEFT in every frame.

CHARACTER - EMBER (fixed canon, identical in all 8 frames):
Male chibi / super-deformed ninja, about 3 to 3.5 heads tall - big head, short thick limbs. He wears a DEEP SMOOTH POINTED COWL in soft-washed ash grey, tapering to a long point that sweeps back off the crown - no facets, no ridges, no horn - edged along its opening with a pale bone-coloured rim band. Inside the hood opening is a SOLID BLACK VOID - NO FACE. No second eye, no mouth, no nose, no chin, no skin. The ONLY feature is ONE pale, closed, leaf/teardrop-shaped eye floating in that void. A pale wrapped bandage encircles his neck and crosses his chest diagonally; a knotted pale sash at the waist with two short hanging tails. From the nape springs a fan of ragged, torn, flame-shaped banner-tails (his scarf), each with a split jagged tip. Both forearms are stacked SEGMENTED RING VAMBRACES ending in a heavy studded, riveted knuckle-cuff. From EACH cuff spring THREE long curved ivory blades - tekko-kagi hooks. THREE PER HAND, SIX TOTAL - never four, never five. He carries NO sword, NO tanto, NO staff, NO kama. Heavy short boots.
MONOCHROME INK ONLY: sumi black through warm ash grey on warm off-white washi paper, with bone-white highlights on the blades, the hood rim and the wrappings. No colour anywhere.

SHEET RULES: 8 frames in one horizontal row, evenly spaced, identical camera, identical character scale in every frame, full body with both feet visible in every frame, plain flat background. NO ground line, NO floor bar, NO cast shadow, no dust, no scuff marks, no speed lines, no motion-blur smear across a frame edge, no frame numbers or captions. Nothing at all may be drawn below his lowest body ink.

THE ACTION - HE IS BEING JUGGLED. One continuous arc of a body that has been launched into the air by an uppercut and has NO control of itself. He is AIRBORNE IN ALL 8 FRAMES - no frame has a sole flat, level and weight-bearing, and no frame is a fighting pose. His silhouette must read BROKEN, not composed: no guard, no bracing, no clenched claws, no defensive chin tuck, nothing symmetrical. The hooks are STRAPPED TO HIS FOREARMS so they never leave his hands, but they hang dead - the heavy studded cuff is the weight and always leads, the three blades always trail and always point AWAY from his body. His scarf tails are the velocity read: yanked DOWN while he rises, floating loose and curled at the top, streaming straight UP while he falls. Frame 1 is rising hardest and frame 8 is falling hardest, and the arc must read correctly strictly in that order.

THE 8 BEATS IN ORDER:
1. THE POP: feet just torn off the floor, toes trailing down; spine arched violently backward into a C, chest open to the sky; hood snapped back, point down-and-back, the void open upward with the pale eye riding high; both arms flung down and back from the shoulders, cuffs at hip level, all six blades trailing down; the scarf tails yanked straight DOWN past his boots.
2. STILL RISING HARD: the arch releasing, body straightening, shoulders leading; knees just beginning to break; arms floating outward, cuffs at waist height, blades fanning apart; hood point swinging toward horizontal; scarf tails still down but curling at the tips.
3. RISE DECAYING: body rotating toward horizontal and face-up, one shoulder dropping lower than the other; one knee folds up, the other leg trails; arms out to the sides, cuffs at shoulder height, blades splayed with the cuffs rolled open; hood horizontal, void sideways, the eye vacant; scarf tails horizontal.
4. FLOAT-UP, NEARLY WEIGHTLESS - A RAG, NOT A POSE. Zero muscle tone. Body near-horizontal and slack, spine a loose S, head hanging back off the neck a beat behind the torso; both arms hang straight from the SHOULDER SOCKETS with no elbow angle held, the heavy cuffs the lowest point of each arm, the wrists broken so each cuff hangs at a different angle to its forearm and the blades dangle and cross; the two legs hang at DIFFERENT angles, one knee up, one trailing, never symmetrical; the scarf tails curl in three different directions with no common line and the sash tails cross. Nothing in this frame is parallel to anything else.
5. APEX: body folded slightly at the waist with the HIPS the highest point; head and boots both hang lower than the hips and the head hangs lower than the shoulders; hood tipped fully forward, point down, void aimed at the floor, eye looking straight down; arms hanging vertically, cuffs below the hood line, all six blades pointing at the floor and not aligned with each other; knees, ankles and wrists slack at different angles; scarf and sash drifting outward and slightly up. If this frame could be read as an attack, a block or a flip, it is wrong.
6. FALL BEGINS: folding forward hard around the middle, knees driving up toward the chest with the boots still ABOVE the hips; hood down, void and eye to the floor; arms now trailing ABOVE the shoulders, cuffs level with the hood, blades raked up and back; scarf tails beginning to lift.
7. FALLING: body tipping back toward feet-down, hips dropping under the shoulders; legs unfolding downward, boots below the hips, toes down, ankles loose; arms still fully trailing above and behind, cuffs above the hood line, blades raked upward; the hood dragged back off the head by the airflow with its rim lifted; scarf tails straight UP.
8. FALLING HARD: near-vertical, boots lowest, legs roughly straight but knees and ankles slack and NOT braced - he is not landing; head down between raised shoulders, hood pressed flat back, void down; both arms straight up past the ears, cuffs above the hood, all six blades a vertical fan overhead; scarf tails and sash stretched straight up past the crown. The whole silhouette reads as a falling arrow.
```

**Pitfalls for this fighter**

- CANON FIX - THREE CLAWS PER HAND, NOT FOUR. Verified by 12x zoom on both cuffs of packed cell 505: three ivory blades each, six total. web/index.html:11051 entry 835: 'HE NOW HAS THREE CLAWS PER HAND ON THE IDLE AND FOUR EVERYWHERE ELSE ... three is the live direction.' The old 'never shrink to three' note is withdrawn.
- CANON FIX - SMOOTH COWL, NOT A FACETED RIDGED HELM WITH A HORN. That description belongs to the older run row (cell 419). Match the approved idle board, cell 505.
- DRAWING A POSE INSTEAD OF A RAG - the single most common failure of a hurt row. No guard, no brace, no clenched claws, no chin tuck, no readable stance, and nothing symmetrical: paired limbs at matching angles is the tell that a generator posed him. Beats 4 and 5 must carry no muscle tone at all - arms hanging from the sockets with no held elbow, broken wrists, the head lagging behind the torso, each scarf tail going its own way.
- PUTTING HIM ON A FLOOR. The three cells this replaces are drawn foot-anchored: measured, airhurt1/2/3 = cells 233/234/235 and all three have their ink bottom on row 366 - which is footY-3 (footY 369), the exact contact row every planted cell of his lands on (web/index.html:11051 entry 835). They are standing-height drawings that the engine only ever shows in mid-air. All 8 new beats are airborne; no sole may be flat, level and weight-bearing.
- DISARMING HIM, OR LETTING THE BLADES POINT INWARD. The tekko-kagi are strapped to his forearms and cannot leave - but they hang dead. The heavy studded cuff is the weight and leads every swing; the three blades trail and always point AWAY from the body. Blades crossing into the torso both read as self-impalement and create an enclosed pocket that packs as a solid slab.
- BREAKING THE ORDER. The engine picks the beat purely off vertical velocity (web/index.html:12310, `const beat = p.vy < -80 ? 1 : p.vy > 100 ? 3 : 2;`). The row must be strictly monotonic from rising-hardest to falling-hardest; a beat drawn out of order flashes the wrong pose mid-juggle.
- MATCHING THE OLD BOARD'S INK QUALITY. Measured: cells 233/234/235 carry 13,460 / 12,546 / 12,673 px of ink against the idle canon of 18,157 px (web/index.html:11051), and ember.json gives all three frameScale 1.14 to sit right - they are visibly a coarser, half-toned board from an earlier pass. The new board must match the 837 feral-idle board's line weight and ink density so it packs at frameScale 1.0.
- FACING RIGHT. Authored canon is FACING LEFT; the engine mirrors toward the opponent (web/index.html:14304, ruling at 14306-14312). Drawn the wrong way this row ships reversed unless 8 `mirror` entries are hand-added to ember.json.
- A FACE, OR A SECOND EYE. One pale leaf-shaped eye in a black void - and in this row it is the ONLY acting he has. Rolling the eye off the line of travel (up on the pop, down on the fall) and letting it go vacant at the apex is the whole performance. Two eyes, a mouth or a bare head kills him.
- THE EYE PACKED AS AN OPEN NOTCH. The eye is a white-drawn ENCLOSED pocket that the keyer finds by name and guards with a 7x7 dilation (web/index.html:11051 entry 836); the same class of defect punched Shin's eye into a hole (11190-11192). One closed pale shape, same size, same place in the void, in all 8 frames, never touching the hood rim.
- ENCLOSED NEGATIVE SPACE. The packer recolours an enclosed page region to the surrounding ink - the ~3200px gap between his legs on the idle board is the reference case (web/index.html:11051 entry 836). In this row the risks are the fold at beat 6 and the arm/torso triangles at beats 3-5. Keep them open to the frame edge where the pose allows.
- DRAWING GROUND FX. Owner ruled DELETE Sep 15 2026 on every drawn contact mark, following 798 which deleted every ground shadow in the game (web/index.html:11051 entry 837). It is also near-unremovable on Ember specifically: his ivory claw bodies read exactly like a pale scuff. No dust, no impact burst, no scuff, no shadow.
- SCALE DRIFT ACROSS THE ROW. Ember's canon is ink area 18,157 px at scale 0.6186 (web/index.html:11051 entry 837) and his bbox HEIGHT lies - measured on cell 505 the bbox runs x66-274 y203-373 because hood and claws both leave the body box, so hood-in-box reads a x1.20 board as x1.04. Identical character scale in all 8 frames, QC'd on ink area.
- DELIVERING IT IN COLOUR. The packed sheet is achromatic (measured on cell 505: warm greys, no saturated pixels). The canon greens at web/index.html:1479 are roster data and vector-fallback paint, not shodo sheet paint, and are deliberately kept out of the prompt so a generator cannot reach for them. Flag the conflict to the owner rather than guessing.
- MEASURED CAVEAT - ONLY 3 BANDS EXIST TODAY. web/index.html:12310 splits airhurt into exactly three: `p.vy < -80 ? 1 : p.vy > 100 ? 3 : 2`. An 8-beat row needs that widened to eight bands, owner-gated; until it is, beats 4-8 never draw. And the beats are SHORT: measured launchVy across the roster runs -300 to -520 (web/index.html:2663, 2677, 2723-2724, 2775, 7054, 7129, 7215, 7546) against GRAVITY 1100 (930/936/1622) = 41-123 px of apex and 0.55-0.95 s of airtime, so each of 8 beats is on screen for 4-7 frames at 60fps. Silhouette first, detail second.


---

## Row C — `njump1..8` — the second jump — Ember — a feral ball, not a gymnastic one

*His idle is a twelve-beat animal prowl. His air jump should look like a cat balling up, not
a gymnast.* Spine-first curl, claws drawn in tight against the chest, then he **snaps open
claws-first**. Predatory, not schooled.

> …A hooded ninja in **achromatic warm greys — no green anywhere**, pale grey eyes, wearing
> **tekkō-kagi claw gauntlets with THREE long parallel silver blades on each hand — claws, never
> swords**, curling into a feral ball in mid-air like an animal.
> Frame 1: spine rounding first, shoulders hunching, head dropping — the curl starts at the back.
> Frame 2: knees driving up outside the elbows, all six claw blades drawn in tight across the chest.
> Frame 3: quarter turn forward, a hunched irregular ball, claws glinting inside the tuck.
> Frame 4: half turn, inverted, body coiled and tense — compressed, not relaxed.
> Frame 5: three-quarter turn, the coil beginning to release, claws leading.
> Frame 6: snapping open claws-first, arms thrown wide, legs still trailing.
> Frame 7: landing shape, claws forward and low, back still arched.
> Frame 8: the low forward prowl stance, both clawed hands leading.


⛔ **Packing: no stance beat here either.** Same `--scale` / `--anchor` rule as Row B, and
the rotation makes the union taller still.
