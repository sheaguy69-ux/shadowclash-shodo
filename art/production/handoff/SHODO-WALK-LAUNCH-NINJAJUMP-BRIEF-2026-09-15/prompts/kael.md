# KAEL — walk · launched hurt · second jump

Part of `SHODO-WALK-LAUNCH-NINJAJUMP-BRIEF-2026-09-15`. Read `README.md`, `BOARD-SPEC.md`
and `PROMPTS.md` §0–§1 first — the canon table and the eight hard rules are there and they
are not repeated per fighter.

**Sheet:** cell `300x320`, aspect **0.94**, `footY 312`, scale `0.4046`, `cols 345`.
**Reference:** `refs/kael-refs.png` (idle, current jump, current air-hurt, landing) and
`refs/ROSTER-true-scale.png` for how tall this fighter is against the others.

⛔ **The refs are cut from the live sheet and some cells still carry drawn ground** — a pale
scuff or a contact smear under the boots. Match the BODY off them, never the floor.

---

## Row A — `walk1..8`

**Intent.** He is closing the gap on purpose, not sprinting — the youngest of the six strolling into range with the near hand resting on the katana tsuka the whole way: unhurried, level, balanced, one beat from the draw.

**Beats**

1. CONTACT A. NEAR (camera-side) boot heel strikes forward, far boot toeing off behind. Legs at their widest of the cycle, but about half the split of his run cells (6-13). Torso stacked upright over the hips, no lean. Hood level and at its LOW point, gold band horizontal, amber eye forward. Near hand ON the katana tsuka at the sash, elbow tucked. Far arm at its FORWARD extreme, reaching slightly across the chest. Scarf tails hanging, only the tips lifting. Both saya still and parallel through the sash.
2. DOWN A. Weight collapses onto the bent NEAR knee — body at its LOWEST of the cycle (drop about 5 src px). Far leg straight behind, far heel peeled off the floor. Hood dips with the hips, cowl peak nodding forward a little. Near hand still on the tsuka. Far arm swinging back through, hand passing the hip. The long katana saya tips up a few degrees behind him as the hips sink.
3. PASSING A. The FAR leg swings through under the body — knee up, shin hanging, toe down — and because it is the far leg it reads one value LIGHTER and partly behind the near leg. Near leg straight and vertical, carrying him. Hips level, mid height, torso perfectly upright. Far arm vertical but the hand sits BEHIND the hip, palm turned back, still travelling rearward. Near hand on the tsuka. Scarf tails dead straight down. Both saya level.
4. UP A. Near leg pushed to full extension, near heel rising — body at its HIGHEST of the cycle. Far leg reaching forward, shin opening out, heel about to lead. Hood lifts with the rise, gold band level. Far arm at its BACK extreme, elbow soft. Near hand lifts a few pixels clear of the tsuka. Scarf tails float slightly upward on the rise. Both saya swing forward a touch.
5. CONTACT B. FAR boot heel strikes forward, the near boot now toeing off behind — opposite-leg mirror of beat 1, and the forward boot is the lighter-value one. Far arm at its BACK extreme (the opposite of beat 1). Near hand back on the tsuka, thumb riding the tsuba. Hood at its LOW point. The long katana saya swings out behind him a little further than on beat 1, the short wakizashi staying tucked closer. Torso upright, shoulders square, eye forward.
6. DOWN B. Lowest point again, now on the FAR leg — far knee absorbing, near heel peeling. Hood dips. Far arm swinging forward through, hand passing the hip. Near hand on the tsuka. Scarf tails swing slightly forward from the drop. Saya tip up behind.
7. PASSING B. The NEAR leg swings through under the body — knee up, toe hanging — drawn at FULL value and clearly in front of the far support leg, the reverse read of beat 3. Far leg straight and vertical. Hips level, mid height, torso vertical. Far arm vertical but the hand sits AHEAD of the hip, palm turned forward, still travelling forward. Near hand on the tsuka. Scarf tails still drifting forward from the drop, not yet settled. Saya level.
8. UP B. Highest point again, far heel lifted, near leg opening out forward, hood at its peak with the gold band level. Far arm at its FORWARD extreme. Near hand has settled back onto the tsuka — the exact position beat 1 falls out of. Scarf tails lifted. This frame must flow straight back into beat 1 with no snap in leg spacing, arm phase or hood height.

**Packing:** every beat is a stance, so the default beat-1 anchor is correct. `--dry` first.

**Prompt**

```text
Sprite animation board, sumi-e / ink-brush shodo styling, side-on 2D fighting-game view. EXACTLY 8 FRAMES IN ONE HORIZONTAL ROW, evenly spaced, left to right. Identical camera and IDENTICAL CHARACTER SCALE in every frame. Full body in every frame with BOTH FEET VISIBLE and clear of the frame edge. Plain flat empty background. NO ground line, NO floor bar, NO cast shadow, NO contact scuff, NO dust, NO dark smear under the boots — the lowest ink in every frame must be the boot sole itself. No motion blur, no speed lines, no smear across the frame edge. All 8 frames face the SAME direction: LEFT.

CHARACTER (exact — do not reinterpret): Kael, the youngest of six ninja swordsmen, drawn in stylised chibi proportion — the hood is about a third of his total height, the torso compact, the legs short and thick.
HOOD: deep charcoal-black, worn UP in every frame, a tall cowl with a pointed peak. A thick GOLD BAND edges the hood opening. That band is the ONLY gold on the hood — the cowl itself stays charcoal, never gold, never pulled down.
FACE: the opening is pure black shadow holding ONE amber eye — a TALL almond, taller than it is wide, glowing the same saturated gold as the scarf. Nothing else inside: no second eye, no mouth, no nose, no hair, no skin.
BODY: black tunic, black sleeves, black trousers, black boots. Gold scarf knotted at the throat with TWO ragged tails. Wide gold sash at the waist with a knot and a short hanging tail. Two gold bands on each forearm bracer, gold bands on each boot cuff.
SWORDS: exactly TWO, BOTH SHEATHED, both thrust through the gold sash at the hip with the hilts forward and the black scabbards trailing behind. One LONG katana, one SHORT wakizashi. Gold hilt fittings, gold scabbard end caps. THE LENGTH DIFFERENCE MUST BE OBVIOUS AT A GLANCE IN EVERY FRAME — draw the long scabbard trailing clearly further back than the short one. Never one sword, never two of the same length, never a drawn blade, never a third weapon.
Palette: charcoal black and gold/amber only. No purple, no red, no green, no blue.

ACTION — a slow, loopable 8-beat WALK cycle. A stroll at half his running speed, not a run. Even flat cadence, no frame held longer than another. Torso upright with no forward lean, hood level, scarf tails HANGING and drifting rather than streaming. Head bobs only slightly: highest on frames 4 and 8, lowest on frames 1, 2, 5 and 6. Both boot soles sit on the same invisible floor height in every frame.
THE NEAR HAND NEVER LEAVES THE KATANA HILT. It rests on the tsuka at the sash for the whole cycle — that is the character. Only the FAR arm swings, and it swings opposite the near leg.
OPPOSITE LEGS, NOT A REPEAT: frames 1-4 lead with the NEAR (camera-side) leg, frames 5-8 lead with the FAR leg. Draw the far leg and far arm one value lighter than the near ones so the swap reads at a glance.

Frame 1 — CONTACT A: near boot heel strikes forward, far boot toeing off behind, legs at their widest but a modest stroll split; torso upright; hood level and low; near hand on the katana hilt; far arm at its FORWARD extreme.
Frame 2 — DOWN A: weight collapses onto the bent near knee, body at its lowest; far leg straight, far heel peeling; hood dips; far arm swinging back past the hip; the long scabbard tips up behind him.
Frame 3 — PASSING A: the FAR leg swings through under the body, knee up and toe hanging, drawn lighter and partly behind the near leg; near leg straight and vertical; hips level, body mid height, torso upright; far arm vertical with the hand BEHIND the hip, palm back; scarf tails hanging dead straight.
Frame 4 — UP A: near leg fully extended with the heel rising, body at its highest; far leg reaching forward, shin opening; hood lifts, gold band level; far arm at its BACK extreme; near hand lifts just off the hilt.
Frame 5 — CONTACT B, OPPOSITE LEG: the FAR boot heel strikes forward, the near boot now toeing off behind — the lighter-value leg is the one in front; far arm at its BACK extreme; near hand back on the hilt; hood low again; the long katana scabbard swings a little wider behind him.
Frame 6 — DOWN B: lowest point on the far leg, far knee absorbing, near heel peeling; hood dips; far arm swinging forward past the hip.
Frame 7 — PASSING B: the NEAR leg swings through under the body, knee up, drawn at FULL value and clearly in front of the far support leg; hips level, mid height, torso vertical; far arm vertical with the hand AHEAD of the hip, palm forward; scarf tails still drifting forward.
Frame 8 — UP B: highest point again, far heel lifted, near leg opening forward, hood at its peak with the gold band level, far arm at its FORWARD extreme, near hand settled back on the hilt — this frame must flow seamlessly back into frame 1 as a perfect loop.
```

**Pitfalls for this fighter**

- THE WHOLE HOOD COMES BACK GOLD. Only the BAND around the hood opening is gold; the cowl is charcoal-black (fighter spec web/index.html:1495 — tunic #1f2937, primary/eye #eab308, scarf #facc15, and the drawn cell agrees). Briefs that say 'gold hood' mean that band. A solid gold cowl is a hard fail.
- ONLY ONE SWORD COMES BACK. Canon is one long katana AND one short wakizashi, both sheathed and stacked at the hip (see jflight cell 301), so at chibi scale a generator routinely merges them into a single scabbard. Count two scabbards and two hilts in all 8 frames or reject the board.
- THE TWO BLADES COME BACK THE SAME LENGTH. The length difference is law and is already only marginally readable on the live sheet — the two saya in 299-304 nearly stack. In a walk the long saya must visibly trail further behind him than the short one on every contact beat.
- A BLADE GETS DRAWN. Every movement and reaction row on his sheet carries both swords SHEATHED (xidle 103-108, run_clean 6-13, jflight 299-304). Drawn steel belongs only to his attack boards. No bare blade, no gold crescent trail, no speed lines.
- HOOD DOWN OR A FACE APPEARS. The hood is UP in every cell of his sheet. Boards come back with hair, a jaw, or two eyes. He has ONE amber eye disc in black hood shadow and nothing else.
- THE GOLD BAND ON THE HOOD OPENING GOES MISSING OR THINS. xidle, run and jflight all carry a thick gold band edging the opening; the kspin board (245-252) thinned it to a hairline. Match xidle 103.
- THE EYE COMES BACK WHITE. Measured: kspin 245-248 draw the eye near-white instead of amber, and the runtime keyer eats near-white eyes. The eye must be saturated amber, the same value as the scarf.
- THE EYE COMES BACK WIDE AND SQUAT. It is a TALL almond. Measured on the live sheet: 7 wide x 12 tall src px on xidle 103; 6x11 on 104; 6x10 on 106 and 108; 7x9 on jflight 301. Hold it 6-8 px wide and 9-12 tall — never wider than tall.
- IT READS AS A RUN, NOT A WALK. His run cells 6-13 are a wide, hard-leaning sprint with the scarf STREAMING horizontally. NOTE — the hood is NOT swept back in his run; it stays up and level there too, so hood position is not the tell. The walk differs by three things only: upright torso with no lean, HANGING scarf, and about half the stride width. If frames 1 and 5 look like his run contacts, it is wrong.
- 8 FRAMES THAT ARE REALLY 4. Frames 5-8 must lead with the OPPOSITE leg and the opposite far-arm extreme, not be frames 1-4 shifted in x. Check the leading boot changes at frame 5.
- FRAMES 3 AND 7 PACK AS THE SAME CELL — the wasted-frame risk in every side-view walk, because at passing both legs stack. They are separated on purpose: on 3 the FAR leg passes (lighter value, partly hidden) with the far hand BEHIND the hip; on 7 the NEAR leg passes (full value, clearly in front) with the far hand AHEAD of the hip. If those two cells are interchangeable, the board is 7 frames and a duplicate.
- SCALE DRIFT BETWEEN FRAMES. Measured ruler: xidle 103-108 hold an ink height of 170-171 src px with a 1px spread, top at y=139-140, in a 300x320 cell with footY 312. Every walk cell must hold that ink height, and the head may bob only 4-6px between the low beats (1,2,5,6) and the high beats (4,8). Secondary ruler is the amber eye at 6-8 px wide.
- DO NOT COPY THE FOOT LINE OFF xidle. Measured: xidle 103's ink bottom is y=309, but the lowest 3-4 rows are a DRAWN CONTACT SMEAR, not boot — at y=306-307 the ink spans x=126-187 against the boots' own x=135-181 at y=305. The real sole line is y≈305-306. Weld the new soles there with nothing below them.
- A GROUND BAR, SCUFF OR CAST SHADOW IS DRAWN IN — and his own reference rows are the source of the infection. Measured: xidle 103-108, run_clean 6-13, grabbed 163-165 and kdual 222/236 ALL carry a drawn contact smear under the boots. 798 deleted every ground shadow in the game and 837 stripped the drawn ground off the Ember feral idle. If ground arrives on this board it must be REGENERATED, not cut — 798's cut pass took the feet off 9 cells doing exactly that.
- FEET CROPPED BY THE CELL EDGE. Both soles inside the frame with clearance below.
- PURPLE. Purple belongs to the Executioner. Kael is charcoal black and gold/amber only.
- FACING DRIFT WITHIN THE ROW. Deliver all 8 frames facing the SAME direction, and LEFT-facing. A cell absent from kael.json's `mirror` map draws unflipped when facing left (web/index.html:2415); jflight 299-304 are left-facing and carry no mirror entry, while xidle 103-108 and run_clean 6-13 are right-facing and all DO carry entries. Left-facing means the pack adds zero mirror entries.
- PALE HALO RING ON THE KEYED CELLS. Measured ruler — rim = opaque pixels (alpha>=8) touching a transparent pixel. Clean cells: 103 mean rim luminance 45.3, 299 = 10.7, 6 = 39.3, 161 = 34.1, 222 = 42.4, all with 0.0% of rim pixels above luminance 190. Failed cells: kspin 245 = 171.4 mean / 45.2% above 190, 246 = 179.4 / 54.3%, 247 = 177.5 / 56.6%, 248 = 183.2 / 62.6%; kdual 236 = 155.1 / 42.6%. The new board must key with art-loss=0 and 0% rim above 190, both measured, before it packs.
- ENGINE CAVEAT TO HAND TO THE OWNER WITH THE BOARD — the row will not be seen as drawn. No `walk*` key exists on ANY of the eight sheets, so Kael would be the first fighter ever to enter STATE.WALK (gated on `walk1` at web/index.html:4903; picker is flat with no contact holds at 12535). But WALK_TIME is 0.15s and WALK_FRAC 0.5 (2933-2934), and Kael's moveSpeed is 350*(8/6)=466.7 (4751), so his walk vx is 233.3 and animPhase advances min(3, 233.3/150) * 8 = 12.4 cells/s (4644-4645): 0.15s buys 1.87 cells — 2-3 distinct cells before he breaks into a run. Raise WALK_TIME to >=0.65 to see one full 8-cell cycle. Draw all 8 as a true loop regardless.


---

## Row B — `airhurt1..8` — the launched hurt arc

**Intent.** The instant he gets caught he stops being a swordsman — a light kid tossed off his feet, all control gone, the hood and the two scabbards flailing while he does nothing about it.

**Beats**

1. POP, rising hardest. Feet torn off the floor, both boots still pointing down with the toes trailing behind. Spine arched backward into a hard C, chest thrown open, hips leading upward. Hood snapped BACK so the opening tilts at the sky and the amber eye is a narrow sliver behind the gold band. Both arms flung out and BEHIND the shoulder line, hands open, fingers splayed — no fists anywhere in this row. Scarf tails whipping straight DOWN beneath him. Both sheathed saya swung out low and behind, the long katana scabbard nearly vertical.
2. RISING. Still arched but the arch is releasing. Knees break at two clearly different angles. One arm folds limp across the chest, the other still trailing behind and above the shoulder. Hood begins to slide back off the crown, cowl peak pointing down-behind. Both scabbards swinging up toward horizontal, the long one clearly outrunning the short one. Head lolling.
3. RISING, SLOWING. Body tipping out of the arch toward horizontal, shoulders now behind the hips, face rolling upward. Legs fully loose — one knee bent, one straight, ankles slack. BOTH arms now overhead, trailing under the direction of travel, hands open. Scarf tails horizontal. Nothing braced, nothing symmetric.
4. APEX ENTRY — the torso has arrived, the limbs have NOT. Body near horizontal and face-up, still drifting up a few pixels. The arms and boots are still LAGGING down-behind from the rise, only beginning to fall through vertical; the head is still whipping back past the shoulders. Hood fallen back off the crown so the cowl droops empty behind the head. Both scabbards laid loosely across the body, crossing at two different lengths.
5. APEX — THE RAG BEAT. Zero velocity, zero muscle tone. Everything has caught up and gone slack: all four limbs now hang straight toward the floor at FOUR different angles, elbows and knees each bent a different amount, no two joints matching. Hands open, fingers loosely curled at different angles, thumbs untucked. Shoulders rolled forward and down toward the floor, belly slack, spine neutral — neither arched nor folded. Head hanging so far back the hood opening points at the ceiling and the amber eye is barely a sliver behind the gold band. The whole body tilted a few degrees off horizontal so NO line in the silhouette is level or vertical. The two saya have swung to wherever gravity left them, crossing the body untidily. Scarf tails floating outward with no direction. He must read as a dropped doll, not a pose.
6. FALL BEGINS. Hips drop first and the body starts folding forward around the belly. Head still trailing above and behind the chest. Arms lifting above the head as gravity takes the heavier mass. Knees drifting up toward the chest. Hood starting to flap up off the shoulders. Scarf tails turning to point upward. Scabbards trailing above the hips.
7. FALLING. Clearly folded forward, chest coming over the knees, back rounded. Both arms streaming straight up above and behind, hands open, as if being pulled by the wrists. Hood flapping up and back off the head, gold band tilted. Scarf tails near-vertical. Both saya trailing above the hips, the long one higher.
8. FALLING HARD. Tightly folded, head dropped below the shoulder line, hood collapsed forward over the crown, eye barely visible. Both arms fully extended straight up behind, hands open. Knees up under the chest, both boots trailing ABOVE the hips. Scarf tails and both scabbards streaming vertically upward. The whole silhouette reads as a falling comma with everything trailing above it.

⛔ **Packing: this row has NO stance beat.** The packer anchors scale on beat 1 by default, and
beat 1 here is the pop — the most extended frame in the row. Anchoring there packs the whole row
too small. Pass `--scale` taken from this fighter's idle, or `--anchor` at the most neutral beat.
The union of an 8-beat arc is also taller than a standing pose, so budget `grow_frame.py --down`
if the dry run prints `REFUSE: scaled window exceeds cell`.

**Prompt**

```text
Sprite animation board, sumi-e / ink-brush shodo styling, side-on 2D fighting-game view. EXACTLY 8 FRAMES IN ONE HORIZONTAL ROW, evenly spaced, left to right. Identical camera and IDENTICAL CHARACTER SCALE in every frame. Full body in every frame with BOTH FEET VISIBLE and clear of the frame edge. Plain flat empty background. He is AIRBORNE in all 8 frames: NO ground line, NO floor bar, NO cast shadow, NO contact scuff, NO dust. No motion blur, no speed lines, no impact flash, no star, no burst, no blood — the engine draws impact FX itself. All 8 frames face the SAME direction: LEFT.

CHARACTER (exact — do not reinterpret): Kael, the youngest of six ninja swordsmen, drawn in stylised chibi proportion — the hood is about a third of his total height, the torso compact, the legs short and thick.
HOOD: deep charcoal-black, a tall cowl with a pointed peak. A thick GOLD BAND edges the hood opening. That band is the ONLY gold on the hood — the cowl itself stays charcoal, never gold.
FACE: the opening is pure black shadow holding ONE amber eye — a TALL almond, taller than it is wide, glowing the same saturated gold as the scarf. Nothing else inside: no second eye, no mouth, no nose, no hair, no skin. The hood may slide back off the crown, but the head underneath stays pure black shadow.
BODY: black tunic, sleeves, trousers, boots. Gold scarf knotted at the throat with TWO ragged tails. Wide gold sash at the waist. Two gold bands on each forearm bracer, gold bands on each boot cuff.
SWORDS: exactly TWO, BOTH SHEATHED, both staying through the gold sash for all 8 frames — one LONG katana, one SHORT wakizashi, gold hilt fittings and gold scabbard end caps. THE LENGTH DIFFERENCE MUST BE OBVIOUS AT A GLANCE IN EVERY FRAME. He is NOT disarmed: the scabbards swing and flail loose with the body, but no blade is ever drawn, dropped, or flying free, and neither scabbard may be deleted to make room for a tumbling pose.
Palette: charcoal black and gold/amber only. No purple, no red, no green, no blue.

ACTION — ONE CONTINUOUS LAUNCHED-AND-JUGGLED ARC, read strictly in order from rising hardest (frame 1) to falling hardest (frame 8). He has been hit by an uppercut launcher and is completely out of control. This is the ONE row where his silhouette must look BROKEN rather than composed: no fighting stance, no braced limb, no clenched fist anywhere, no symmetry, no line of action he would have chosen. Limbs trail OPPOSITE the direction of travel. The scarf tails and the two scabbards are the wind-vane: they point DOWN while he rises (frames 1-3) and UP while he falls (frames 6-8).

Frame 1 — THE POP, rising hardest: feet torn off the floor with the toes still trailing down, spine arched hard backward, chest open, hips leading up, hood snapped back so the opening tilts at the sky and the amber eye is a sliver, both arms flung out and behind the shoulders with hands open and fingers splayed, scarf tails whipping straight down, both scabbards swung out low and behind.
Frame 2 — RISING: arch releasing, knees breaking at two clearly different angles, one arm folding limp across the chest and the other still trailing behind, hood sliding back off the crown, scabbards swinging up toward horizontal with the long one outrunning the short one.
Frame 3 — RISING AND SLOWING: body tipping out of the arch toward horizontal, shoulders behind the hips, head lolling face-up, legs loose with one knee bent and one straight, BOTH arms overhead and trailing, scarf tails horizontal.
Frame 4 — APEX ENTRY, the torso has arrived and the limbs have not: body near horizontal and face-up, still drifting up; arms and boots still LAGGING down-behind from the rise, only beginning to swing through vertical; head still whipping back past the shoulders; hood fallen back and drooping empty; both scabbards laid loosely across the body at two different lengths.
Frame 5 — APEX, THE RAG BEAT: weightless, draped, ZERO muscle tone. All four limbs now hang straight toward the floor at four DIFFERENT angles, elbows and knees each bent a different amount, no two joints matching. Hands open, fingers loosely curled at different angles. Shoulders rolled forward and down, belly slack, spine neutral. Head hanging back so the hood opening points at the ceiling and the amber eye is barely a sliver. The whole body tilted a few degrees off horizontal so no line in the silhouette is level or vertical. The two scabbards crossing the body untidily wherever gravity left them, scarf tails floating with no direction. A dropped doll, not a pose.
Frame 6 — THE FALL BEGINS: hips drop first, body folding forward around the belly, head still trailing above and behind, arms lifting above the head, knees drifting toward the chest, scarf tails turning upward.
Frame 7 — FALLING: clearly folded forward, chest over the knees, back rounded, both arms streaming straight up above and behind with open hands as if pulled by the wrists, hood flapping up off the head, scarf tails near-vertical, both scabbards trailing above the hips.
Frame 8 — FALLING HARDEST: tightly folded, head dropped below the shoulders, hood collapsed forward over the crown, both arms fully extended straight up behind, knees up under the chest with both boots trailing ABOVE the hips, scarf tails and both scabbards streaming straight up — a falling comma with everything trailing above it.
```

**Pitfalls for this fighter**

- THE CURRENT ROW IS THE WARNING. kael.json maps airhurt1 -> cell 161, airhurt2 -> cell 161 (the SAME cell) and airhurt3 -> cell 162, and both are borrowed from the grabbed row (grabbed3 and grabbed4). Rendered, 161 is a doubled-over crouch with BOTH BOOTS PLANTED and 162 is a standing compression — two GROUNDED flinches standing in for a juggle. Any new beat with planted feet, a braced knee or a stance repeats the exact defect.
- A POSE INSTEAD OF A RAG. Frames 4 and 5 are where boards fail: the generator gives a heroic mid-air pose with tension in the arms. FALSIFIABLE TEST for frame 5 — mirror it and tilt it 30 degrees; if it still reads as a pose a fighter would choose to hold, it is wrong. Nothing parallel, nothing mirrored, no two joints at the same angle, no closed hand anywhere in the row.
- FRAMES 4 AND 5 PACK AS THE SAME CELL. They are separated on purpose: on 4 the torso has arrived but the limbs are still LAGGING down-behind from the rise and the head is still whipping back; on 5 everything has caught up and hangs floorward, and the body is tilted off-axis. If the two cells are interchangeable, the apex is one frame and the other is wasted.
- LIMBS TRAILING THE WRONG WAY. Arms, scarf and scabbards must trail DOWN in frames 1-3 (he is rising) and UP in frames 6-8 (he is falling). A board that keeps them down all the way through reads as one static flinch and destroys the vy ordering the picker bands on.
- HE GETS DISARMED. Both swords stay SHEATHED through the sash and swing loose. Boards come back with a sword flying out of frame, a blade drawn, or the scabbards deleted entirely because the artist could not fit them on a tumbling body.
- ONE SWORD, OR TWO OF THE SAME LENGTH. Count two scabbards of visibly different length in all 8 frames.
- THE WHOLE HOOD COMES BACK GOLD. Only the band around the hood opening is gold (web/index.html:1495 — tunic #1f2937, primary/eye #eab308, scarf #facc15). The cowl is charcoal-black.
- HOOD DOWN OR A FACE APPEARS. A launched character is exactly where a generator decides to show pain on a face. The hood may slide back off the crown (frames 4-7) but the head underneath stays pure black shadow with ONE amber eye — never hair, never a jaw, never a second eye, never a mouth.
- THE EYE COMES BACK WHITE, OR WIDE AND SQUAT. Keep it saturated amber, the same value as the scarf — the runtime keyer eats near-white eyes (kspin 245-248 did exactly this). And it is a TALL almond: measured 7 wide x 12 tall src px on xidle 103, 6x11 on 104, 6x10 on 106 and 108, 7x9 on jflight 301.
- SCALE DRIFT. Airborne cells are NOT foot-anchored — measured, his jflight ink bottoms sit at y=280, 283, 296, 304, 305 and 311 in a 300x320 cell with footY 312 — so the ruler here is the EYE, not the ink height or the bbox. Hold the amber eye at 6-8 px wide and 9-12 tall in every frame, and hold the hood crown the same size frame to frame.
- A GROUND BAR, SCUFF LINE OR CAST SHADOW. He is airborne for all 8 frames; no floor contact anywhere. His own sheet is the infection source — measured, xidle 103-108, run_clean 6-13, grabbed 163-165 and kdual 222/236 all carry a drawn contact smear under the boots. If ground arrives, REGENERATE the board, do not cut it (798's cut pass took the feet off 9 cells).
- FEET CROPPED BY THE CELL EDGE, especially on frame 1 (toes trailing low) and frame 8 (boots trailing high). Both boots visible and inside the frame every time.
- PURPLE, RED OR GREEN IMPACT FX. No hit-flash, no star, no burst, no blood. Grabbed cell 160 on the live sheet carries a baked gold impact burst on the chest — this row must carry NONE; the engine draws impact FX itself.
- FACING DRIFT WITHIN THE ROW. All 8 frames face the same way, LEFT, to match jflight 299-304, which carry no `mirror` entry in kael.json (web/index.html:2415) — that way the pack adds none.
- DO NOT STRIP CELLS 161/162 WHEN THE NEW ROW PACKS. They are still grabbed3 and grabbed4. Repointing airhurt1..8 to new cells must leave 161/162 in place, or the grabbed row breaks. Two-step law: pack the replacement, repoint the key, and only strip a cell once nothing else points at it.
- ENGINE NOTE FOR THE OWNER: airhurt is banded on vertical velocity in THREE bands today — `p.vy < -80 ? 1 : p.vy > 100 ? 3 : 2` at web/index.html:12310-12311 — so an 8-beat row needs that line re-banded or frames 4-8 never draw. Suggested 8 bands, rising to falling: vy < -420, -420..-300, -300..-180, -180..-60, -60..60, 60..180, 180..320, > 320.
- PALE HALO RING. Measured ruler — rim = opaque pixels (alpha>=8) touching a transparent pixel. Clean cells: 103 mean rim luminance 45.3, 299 = 10.7, 6 = 39.3, 161 = 34.1, all with 0.0% of rim pixels above luminance 190. Failed: kspin 245 = 171.4 / 45.2%, 246 = 179.4 / 54.3%, 247 = 177.5 / 56.6%, 248 = 183.2 / 62.6%. The new board must key with art-loss=0 and 0% rim above 190, both measured, before it packs.


---

## Row C — `njump1..8` — the second jump — Kael — the schooled somersault, and he curls around his own blades

*The last student of a real school. His is the only textbook-correct rotation — and the only
one with the problem of two drawn blades.* **You do not curl onto your own edges**: both
swords are held out and away from the tuck through the whole revolution.

> …A young ninja in black with a **gold-amber hood**, gold scarf and sash, glowing amber eyes,
> holding **one LONG katana in one hand and one clearly SHORTER wakizashi in the other — the
> length difference obvious at a glance**, performing a disciplined forward somersault in mid-air.
> Frame 1: feet leaving, knees rising, both blades sweeping outward away from the body.
> Frame 2: knees to chest in a clean tuck, both swords held out wide, clear of the legs.
> Frame 3: quarter turn forward, textbook ball, blades extended on either side like outriggers.
> Frame 4: half turn, fully inverted, hood and gold scarf trailing a full circle, blades still clear.
> Frame 5: three-quarter turn, tuck opening, blades beginning to draw back in.
> Frame 6: legs extending down, both swords returning toward a guard.
> Frame 7: nearly upright, long blade high and short blade low.
> Frame 8: upright landing stance, long katana high, wakizashi across the body.


⛔ **Packing: no stance beat here either.** Same `--scale` / `--anchor` rule as Row B, and
the rotation makes the union taller still.

---

## Row D — `run_clean1..8` — THE RUN, REPLACED

> **Owner, Sep 15 2026:** *"yeah let's give him a more epic serious run cycle."*

**Zero engine work.** The run picker reads `run_clean1..8` and already paces them on
`RUN_HOLDS_8`. Pack eight cells, repoint, done.

### What is actually wrong with the current one — measured, not opinion

**His eight-beat run is a four-beat cycle drawn twice.** Ink area per beat:

```
beats 1-4   8752  7646  7996  7656
beats 5-8   8782  7623  7991  7614
difference  0.3%  0.3%  0.1%  0.5%
```

Beat 5 *is* beat 1. Beat 6 *is* beat 2. He has **four distinct poses**, so the left-lead and
the right-lead stride are the same drawing, and a run that does not alternate its lead leg
reads as a loop rather than as travel. That is the single biggest reason it looks small.

Second: he is **hunched and compact** — 119–137px wide by 124–146px tall in a 300×320 cell,
head down, shoulders rolled forward. It reads as scurrying. His head swings 21px on screen,
which is fine; the problem is posture and stride length, not bounce.

Third: **both blades are inert.** A two-sword fighter is running with his swords parked. They
never lead, never trail, never counterweight.

**What is already right and must survive:** beats **4 and 8 are genuine flight** — both feet
clear, knees tucked, 31px up. That is the two-stride structure and it is correct. Do not plant
them.

### The beats that actually carry the animation

`RUN_HOLDS_8` gives the cycle uneven exposure — beats **1, 4, 5 and 8** hold longest:

| beat | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 |
|---|---|---|---|---|---|---|---|---|
| share of cycle | **16%** | 10% | 10% | **14%** | **16%** | 10% | 10% | **14%** |

So the two **contacts** (1, 5) and the two **leaps** (4, 8) are 60% of the screen time between
them. Put the drama there. Beats 2, 3, 6, 7 are the passing frames and can be quieter.

### Intent

He is the last student of a school that no longer exists, and the youngest of the six. His run
should read as **trained**, not eager — a swordsman covering ground with economy and intent,
long low strides, blades carried like he knows exactly where both of them are. Serious, not
heroic; no cape-flare, no showboating. Grounded weight on the contacts, real extension in the air.

### Beats — EIGHT DISTINCT POSES, alternating lead

1. **LEFT CONTACT (held, 16%).** Left boot strikes flat and takes the full load, knee stacked
   over it, back straight and pitched forward about 15°. Long katana carried low and back in
   the right hand, tip trailing near the ankle. Short wakizashi tucked across the chest, blade
   flat. Hood settled back off the face, amber eye visible. Gold sash snapped forward past the hip.
2. **LEFT DOWN (10%).** Weight sinking through the left leg, knee flexing deepest in the cycle,
   right leg swinging through low and close. Torso drops with it. Both blades hold their line —
   the long one steady, no swing. Sash falling back to vertical.
3. **LEFT PASS (10%).** Left leg driving straight, right knee coming forward and high, body
   rising. Long katana beginning to sweep forward with the drive. Hood starting to lift off the
   shoulders.
4. **LEFT LEAP — FULL EXTENSION (held, 14%).** **Both feet clear.** Front leg reaching far
   forward and nearly straight, rear leg fully extended behind — the widest stride in the cycle,
   a real split, not a tuck. Body long and level, not balled. Long katana swept back and up
   behind him in a straight line with the rear leg; short blade forward across the chest. Hood
   and sash streaming straight back. **This is the money frame.**
5. **RIGHT CONTACT (held, 16%).** The mirror of beat 1 in *stride*, but **not the same drawing**
   — this is the other lead, so the arms swap: long katana now forward-low in front of the body,
   short blade drawn back at the hip. Right boot lands flat, left arm counterweights forward.
   The silhouette must be plainly different from beat 1 at a glance.
6. **RIGHT DOWN (10%).** Weight sinking through the right leg, left leg swinging through. Long
   katana held low and forward, tip just off the floor. Shoulders squarer to camera than beat 2.
7. **RIGHT PASS (10%).** Right leg driving, left knee high, rising. Long blade drawing back
   toward the hip in preparation. Hood lifting.
8. **RIGHT LEAP — FULL EXTENSION (held, 14%).** Both feet clear again, opposite legs to beat 4,
   and the blades opposite too: long katana thrown *forward* and level this time, short blade
   trailing back. Same airtime and same stride width as beat 4 so the cycle is even, different
   arms so it is not beat 4 again. Lands back into beat 1 with no jump.

**Packing:** beat 1 is a full-weight contact stance, so the default beat-1 anchor is correct.
`--dry` first — the leaps are the tallest beats and the union may want `grow_frame.py --down`.

### Prompt

```text
Sumi-e / ink-brush shodo character sheet, side-on 2D fighting-game view. 8 frames in one
horizontal row, evenly spaced, identical camera, identical character scale in every frame,
full body with both feet visible in every frame, plain flat background, no ground line, no
cast shadow, no floor bar, no dust, no speed lines running off the frame edge.

CHARACTER, exact, no deviation: KAEL, male. A compact chibi ninja roughly 2.5 head-heights
tall. Black body, black tunic and black trousers. A GOLD-AMBER HOOD and a long GOLD scarf,
with a gold sash knotted at the waist and gold wrist and ankle wraps. One glowing AMBER eye
visible inside the hood shadow. He carries TWO SWORDS AND THEY ARE DIFFERENT LENGTHS: ONE LONG
KATANA and ONE CLEARLY SHORTER WAKIZASHI, roughly half its length — the difference must be
obvious at a glance in every single frame. Never two equal blades. No purple anywhere.

A DISCIPLINED, SERIOUS RUN — a trained swordsman covering ground with economy and intent.
Long low strides, real extension, body pitched slightly forward, head up and level. Not
eager, not comic, not scurrying, no cape-flare, no showboating.

EIGHT DISTINCT POSES. Frames 5-8 are the OPPOSITE lead leg AND the opposite arm carriage to
frames 1-4 — swap which hand leads and which blade is forward, so frame 5 is plainly a
different drawing from frame 1 and not a copy.

Frame 1: LEFT FOOT CONTACT. Left boot flat, taking full weight, knee stacked over it, spine
straight and pitched forward. Long katana low and BACK in the trailing hand, tip near the
ankle; short wakizashi tucked flat across the chest. Gold sash snapped forward past the hip.
Frame 2: weight sinking through the left leg, deepest knee bend of the cycle, right leg
swinging through low and close, torso dropping. Both blades steady, no swing.
Frame 3: left leg driving straight, right knee coming forward and high, body rising, long
katana beginning to sweep forward.
Frame 4: THE LEAP. Both feet completely off the ground. Front leg reaching far forward almost
straight, rear leg fully extended behind — the widest split of the cycle, body LONG and level,
never balled or tucked. Long katana swept back and up in one straight line with the rear leg;
short blade forward across the chest. Hood and scarf streaming straight back.
Frame 5: RIGHT FOOT CONTACT, and the arms have SWAPPED. Long katana now FORWARD and low in
front of the body, short wakizashi drawn back at the hip, left arm counterweighting forward.
Right boot flat and loaded. Clearly a different silhouette from frame 1.
Frame 6: weight sinking through the right leg, left leg swinging through, long katana low and
forward with the tip just off the floor, shoulders squarer to camera.
Frame 7: right leg driving, left knee high, body rising, long blade drawing back toward the hip.
Frame 8: THE SECOND LEAP. Both feet clear again, opposite legs to frame 4, and the blades
opposite too — long katana thrown FORWARD and level, short blade trailing back. Same airtime
and same stride width as frame 4. Flows straight back into frame 1.
```

### Pitfalls for this row

- **Two equal blades.** The commonest Kael failure. The wakizashi must read as roughly half the
  katana in every frame, including both leaps where the arms are extended.
- **Frames 5–8 coming back as copies of 1–4.** That is the exact defect being replaced. If the
  ink areas of 1 and 5 land within 1% of each other, reject the board.
- **Tucking the leaps.** Beats 4 and 8 are a long extended split, not a ball — the ball belongs
  to Row C, the second jump, and the two must not look alike.
- **Planting the leaps.** Both feet clear on 4 and 8, 30px up. Do not let a toe touch.
- **A drawn ground smear** under the contact beats. The packer welds the lowest ink to the floor
  line — a smear becomes the feet.
- **Purple.** Forbidden on Kael; gold and amber only.
- Hood swallowing the face on every frame — the amber eye should read on at least the contacts.
