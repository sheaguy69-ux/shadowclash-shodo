# MOKURAI — walk · launched hurt · second jump

Part of `SHODO-WALK-LAUNCH-NINJAJUMP-BRIEF-2026-09-15`. Read `README.md`, `BOARD-SPEC.md`
and `PROMPTS.md` §0–§1 first — the canon table and the eight hard rules are there and they
are not repeated per fighter.

**Sheet:** cell `300x248`, aspect **1.21**, `footY 218`, scale `0.4808`, `cols 410`.
**Reference:** `refs/mokurai-refs.png` (idle, current jump, current air-hurt, landing) and
`refs/ROSTER-true-scale.png` for how tall this fighter is against the others.

⛔ **The refs are cut from the live sheet and some cells still carry drawn ground** — a pale
scuff or a contact smear under the boots. Match the BODY off them, never the floor.

---

## Row A — `walk1..8`

**Intent.** The player should feel the floor get heavier under him - a stone-masked monk closing distance at a temple-flagstone pace, palm still raised, eyes still shut, the long mala down his back swinging like a bell-rope, absolutely unhurried while everyone else sprints.

**Beats**

1. BEAT 1 - PASS, NEAR LEG PLANTED: the camera-side leg flat on the floor carrying all the weight, the far leg lifted just clear and swinging through beside the standing ankle, shins almost crossed; hips level and square over the standing foot; spine vertical; the near shoulder rolled BACK; left forearm up with the open palm out at chin height (abhaya, exactly as xidle cells 207-212 carry it); right hand a loose fist at the hip; sash tails swung BACK off centre; the long back mala hanging forward against the hip.
2. BEAT 2 - REACH, NEAR LEG LEADING: the near leg extending forward into a long wide step, knee barely bent, the open-toe sandal sole angled to plant FLAT (no heel strike); far leg straight behind, its heel beginning to peel; body upright and centred between the feet - he covers ground by stepping wide, never by leaning; raised palm unmoved; sash tails swinging back to vertical; back mala at the front of its swing, standing a little clear of the hip; hakama hem swept back off the leading shin.
3. BEAT 3 - WIDEST SPLIT, NEAR LEG IN FRONT: both soles flat, legs at maximum spread, front shin vertical, back leg straight with the whole back sole still down (a monk does not push off the toe); weight dead centre; the fully-rendered near leg is the one LEADING, its gold ankle rings catching light, the far leg one value darker behind it; shoulders square; raised palm at chin height; sash tails swung FORWARD; the shoulder scarf pulled back behind him; back mala starting to swing rearward.
4. BEAT 4 - TRANSFER OFF THE NEAR LEG: weight rolling onto the front foot, the back sole peeling off the floor FLAT, whole sole at once (lifting, not pushing); back knee starting to fold; torso vertical, a fraction of hip rotation only; near shoulder beginning to come forward; palm unmoved; sash tails falling back toward centre; back mala at the back of its swing, clear of the body outline.
5. BEAT 5 - PASS, FAR LEG PLANTED (the opposite of beat 1, not its mirror): the far leg flat and carrying the weight, the near leg lifted clear and swinging through beside it - so the darker, simpler far leg is now the pillar and the detailed near leg is the one in motion, which is what separates this cell from beat 1 in silhouette; the near shoulder rolled FORWARD; hips level; raised palm still out at chin height, it does NOT drop or pump; sash tails swung FORWARD; back mala hanging back against the hip.
6. BEAT 6 - REACH, FAR LEG LEADING: the far leg extending into the long wide step, sole angling to plant flat, drawn one value darker as it crosses in front of the near leg; near leg straight behind, fully rendered, heel peeling; body upright and centred; raised palm unmoved; sash tails swinging toward vertical; back mala at the front of its swing again.
7. BEAT 7 - WIDEST SPLIT, FAR LEG IN FRONT: both soles flat, legs at maximum spread, weight dead centre - the same geometry as beat 3 with the leading and trailing legs swapped, so the darker leg leads and the detailed near leg trails; sash tails swung BACK; the scarf still lagging a beat behind the legs and only now beginning to swing forward; back mala swinging rearward.
8. BEAT 8 - TRANSFER AND HAND-OFF: weight rolling onto the front foot, back sole peeling off flat, back knee folding - geometrically one step short of beat 1 so the loop closes with no jump; head level, mask level, eyes closed; shoulders square; sash tails and back mala returning toward vertical; the raised palm exactly where beat 1 will take it.

**Packing:** every beat is a stance, so the default beat-1 anchor is correct. `--dry` first.

**Prompt**

```text
Sumi-e / ink-brush shodo character sheet, side-on 2D fighting-game view, 8 frames in one horizontal row, evenly spaced, identical camera, identical character scale in every frame, full body with both feet visible in every frame, plain flat background, no ground line, no cast shadow, no floor bar, no scuff or dust under the feet, no motion-blur smear across the frame edge.

CHARACTER (exact canon - do not invent or substitute): MOKURAI, male, a stone-masked Buddhist monk. He carries NO WEAPON OF ANY KIND - no staff, no bo, no walking stick, no blade, no chain, no fan. His only gear is prayer beads. He has NO HOOD and NO HAIR: a bare bald dome, warm bone-tan (body #c09860, highlight #e1bb85), and the front of the face from the hairline down is a carved GREY STONE PLATE (mid #908878, shade #807868, light #a8a090, highlight never brighter than #d8d0c1 - no pure white anywhere on the stone). The tan skull stays visible ABOVE and BEHIND the plate with a clear seam between them; the plate is a face, not a covering helmet. A small red oval jewel sits high on the centre of the stone forehead. His EYES ARE CLOSED in every frame - serene lids, thin dark lash lines, a faint closed-mouth smile, no pupils, no whites, no glow, never red. A long gold double-ring ear ornament hangs from an elongated Buddha earlobe on the visible ear.

BEADS (three separate pieces, all three in every frame): a fine gold bead cord high on the throat; a strand of large matte-black wooden mala beads resting on the chest; and a LONG black mala strand hanging down his BACK to hip-height, ending in one larger bead. Both wrists carry stacked gold bands, and the right wrist adds a black bead wrap that carries over the back of the fist. Matte black wood, never gold or jade.

CLOTHING: a sleeveless saffron/ochre wrap (#b89058-#c09860) crossed at the chest OVER a charcoal-black long-sleeved under-layer - his arms are covered in black to the wrist, only the hands are bare tan. A vermilion sash (#782810 into #401808) knotted at the waist with two long ragged tails hanging down the FRONT CENTRE to the knee, and a matching ragged vermilion scarf trailing off the back of the right shoulder. Baggy charcoal-black hakama gathered at the ankles. FOOTWEAR: dark charcoal open-toe foot-wraps with an instep strap, the bare tan toes exposed at the front, and two or three stacked GOLD ankle rings above them. Not bare feet, not boots, not tabi. No purple, no violet, no magenta anywhere. No gold glow, halo, aura or energy of any kind - the game draws those, not the art.

HE FACES LEFT in all 8 frames. He is WALKING, not running: slow, level, deliberate, a monk crossing temple flagstones. His spine stays vertical - he covers ground with a long WIDE step, never by leaning forward. He plants each sole FLAT, whole foot at once, no heel strike and no toe push-off. His raised left arm never pumps: the open palm stays out in front at chin height through the whole cycle. The right hand stays a loose fist at the hip. His head stays level within a hair across all 8 frames; any small rise comes from the standing leg straightening with the sole still on the floor, never from lifting the whole body. The cycle loops: frame 8 flows straight back into frame 1.

EVERY FRAME MUST BE A DIFFERENT PICTURE. Frames 1-4 are led by the CAMERA-SIDE leg, frames 5-8 by the FAR leg, and the far leg is always drawn one value darker with simplified toes and a dimmer ankle ring, so the two halves of the cycle never pack as the same cell. The sash tails and the long back mala are the second separator: they swing on OPPOSITE phases from each other and both lag the legs by one beat.

THE 8 BEATS IN ORDER:
1. Near leg flat and bearing all weight, far leg lifted and swinging through beside the standing ankle, shins almost crossed; near shoulder back; palm up at chin height; fist at the hip; sash tails swung back; back mala forward against the hip.
2. Near leg reaching forward into a long wide step, knee barely bent, sole angled to land flat; far leg straight behind, heel peeling; body upright and centred; sash tails vertical; back mala standing clear at the front of its swing; hem swept off the leading shin.
3. Widest split, near leg IN FRONT: both soles flat, legs at maximum spread, front shin vertical, whole back sole still down, weight dead centre; sash tails swung forward, scarf pulled back behind him; back mala swinging rearward.
4. Weight transferring onto the front foot; the back sole lifting flat off the floor all at once; back knee folding; torso vertical; near shoulder coming forward; sash tails falling to centre; back mala at the back of its swing.
5. Far leg flat and bearing all weight, near leg lifted and swinging through - the darker leg is now the pillar and the detailed one is in motion; near shoulder forward; palm still up at chin height; sash tails swung forward; back mala hanging back against the hip.
6. Far leg reaching into the long wide step, crossing in front of the near leg, drawn darker; near leg straight behind; body upright; sash tails toward vertical; back mala forward again.
7. Widest split, far leg IN FRONT: legs at maximum spread, both soles flat, weight dead centre, the darker leg leading and the detailed leg trailing; sash tails swung back; scarf only now beginning to swing forward; back mala rearward.
8. Weight rolling onto the front foot, back sole peeling off flat, back knee folding - one step short of frame 1 so the loop closes seamlessly; head level, mask level, eyes closed; sash tails and back mala returning to vertical.
```

**Pitfalls for this fighter**

- A STAFF. The oldest failure on this character and the engine says so in its own roster comment - index.html:1512, 'The bo staff is erased from canon, not set down in it', with weapon set to 'Prayer Beads / Bare Hands' at 1513. A pole in any frame is a reject, including a walking-stick or pilgrim's staff, which a 'monk walking' prompt attracts hardest.
- BARE FEET. The spec this replaces said bare feet; the shipped art does not. LOOKED AT on the master (idle cell 332 at 9x): he wears dark charcoal OPEN-TOE foot-wraps with an instep strap - heel and instep covered, bare tan toes out the front - under two or three stacked gold ankle rings. Draw the wrap, the strap, the exposed toes and the rings in every frame.
- A HOOD, or swallowing the tan skull. Bald dome above and behind, grey stone plate on the face, a visible seam between them. Generators borrow Oni's and Exile's hoods onto any masked fighter, and they also turn the plate into a full helmet.
- LOSING THE BACK MALA. The long black strand hanging down his back to hip-height is his single most distinctive trailing element and the original spec left it out entirely. It is also the cheapest per-beat differentiator in the row - it swings on the opposite phase to the sash tails, so it makes beats 1/5, 2/6, 3/7 and 4/8 into different cells for free.
- BEATS 1/5, 2/6, 3/7 AND 4/8 PACKING AS THE SAME CELL. This is the standard side-on walk-cycle failure and it would waste half the row. The leg swap alone is not enough in a flat side view: the far leg must be one value darker with simplified toes and a dimmer ankle ring, the near shoulder must rotate back on 1-4 and forward on 5-8, and the two cloth pointers must be a beat out of phase with the legs and with each other.
- A DRAWN GROUND BAR, SCUFF OR DUST UNDER THE SOLES. The packer welds the board's lowest ink to the floor line, so drawn ground makes him hover by exactly its own thickness. Measured on his own sheet today (ink in the bottom three rows lying more than 6px outside the ankle span 8-12 rows above): bjump1 cell 289 carries 96px of it, brun7 cell 287 47px, bjump6 cell 294 37px, bjump7 cell 295 30px, and bjump2/bjump8 cells 290/296 carry a bar directly under the soles. His idle 332 and xidle 207-212 are clean - match those, not the jump board.
- MEASURING SCALE ON BBOX HEIGHT. Banned here, and the spec this replaces broke its own rule by calling the hurt row '12-15% oversized' off bbox height. Measured: his live cells run 79px tall (cell 181) to 199px (cell 98) for the same body. The ruler is HEAD WIDTH at the temples - 44-45px on all seven idle/xidle cells (332, 207-212), a 2.3% spread - against a 154px standing ink height in a 300x248 cell. On that ruler the hurt row reads 39-42 and jland reads 45, i.e. the sheet is already consistent and the bbox numbers were pose, not size.
- A PURE-WHITE HIGHLIGHT ON THE STONE. Not because the runtime keys it - it does not; keyedShodoCell at index.html:2199 only floods a cell that is under 70% transparent, and his live cells measure 88-92% transparent, so it never fires on his art. The risk is the PACK-time keyer, which drops min-channel >= 205 and is what ate near-white eyes at sheet 708. Measured ceiling on his head today is #d8d0c1; the only near-white opaque pixels on his whole sheet (308 of them) are gold specular on rings, bracelets and beads. Keep the stone under #d8d0c1 and never draw the closed eyes as white slits.
- OPEN EYES. Every shipped cell has them shut. An 'alert walking monk' reading will open them.
- BAKED GOLD ENERGY - aura, halo, glowing palm, chakra motes. The engine draws his karma glint itself (index.html:4139-4145, gold streaks at #f0c040) and his prayer-halo bloom at 9181-9191, which is flagged 'gold-only FX (identity law)'. Art that includes them double-draws.
- A FORWARD LUNGE OR A FIGHTING LEAN. Measured: draw facing follows velocity ONLY in STATE.RUN (index.html:2413), and grounded movement always auto-faces the opponent (4908-4910), so this exact cycle plays UNREVERSED while he backpedals. A pose that only makes sense advancing plays backwards on every retreat. Upright and wide, never leaned.
- A SHORT SHUFFLING STEP. Measured: animPhase advances dt x min(3, |vx|/150) x cells (index.html:4644-4645) and mokurai has no runAnimScale, so ground covered per cycle is a flat 150 world px regardless of beat count. At sheet scale 0.4808 that is 312 cell px per cycle - about one 154px body height of travel between successive foot plants. A small step will visibly slide.
- DRAWING HIM FACING RIGHT. Default authoring on this sheet is FACING LEFT: mirror = -drawFacing x (mirror[idx] ? -1 : 1) at index.html:2415, so a cell with NO mirror entry is authored facing left. His idle 332 and xidle 207-212 carry no entry and are drawn facing left; his run 281-288 and jump 289-295 are all listed and are drawn facing right (cell 296 is missing its entry, which is why it is worth checking). Drawing this board facing left costs zero mirror entries.
- TREATING THIS AS A LIVE ROW. Measured across all nine sheets: NOT ONE fighter has a walk row, and the walk tier is gated on wf?.walk1 (index.html:4903), so Mokurai would be the first fighter in the game to ever enter STATE.WALK. Two consequences worth flagging to the owner before the board is paid for: the picker is a flat even cadence, w[floor(animPhase) % w.length] at 12535, deliberately not the run's held-contact picker; and WALK_TIME is 0.15s (2933), which at his 145.8 px/s walk and 7.78 cells/s stride clock advances animPhase only 1.17 cells, so exactly two adjacent cells draw per push and animPhase is never reset (3420) so the pair starts on an arbitrary beat. Every adjacent pair must read as a step on its own. Raising WALK_TIME is the lever; draw all 8 as a true loop regardless.


---

## Row B — `airhurt1..8` — the launched hurt arc

**Intent.** The player should feel the composure come off him - the one man in the game who never opens his eyes, thrown up and dropped like a cut bell-rope, with three long-held stills doing all the work and the beads doing all the screaming his stone face cannot.

**Beats**

1. BEAT 1 - RISING (drawn for vy below -80; the engine holds this one still for 0.27-0.44s, the longest single look at any launched pose): both feet torn clean off the floor with the toes still pointed down and trailing behind the hips; spine arched HARD backwards over the hit point, chest thrown open, the stone mask snapped back so the face is aimed at the sky and the throat is exposed; both arms flung up and back behind the head, fists open, fingers loose and splayed with no grip in them; the chest mala lifted clear off the collarbone and standing out in front of the throat; the long back mala, both sash tails and the shoulder scarf all snapping STRAIGHT DOWN in one hard vertical line - that line is the only thing in the frame that is straight, and it is what says 'still going up'.
2. BEAT 2 - APEX, WEIGHTLESS AND COMPLETELY LIMP (drawn for vy between -80 and +100; exactly 0.164s of game time every single time, because the band is a fixed 180 px/s window - this cell is a held still, not a passing frame, and it is the whole point of the row): zero muscle tone anywhere. The torso has rotated past horizontal with the chest turned toward the floor; the heavy stone head hangs BELOW the shoulder line under its own weight, lolled over onto one shoulder, and the stone mask is turned three-quarters away from camera so the closed eyes read as unconscious rather than posed; one shoulder is dropped clearly lower than the other; one arm hangs limp across the chest, the other is still flung out behind with the wrist broken and the fingers open; the legs hang apart with no tension at all, one knee bent and one straight, both ankles slack and the toes pointing nowhere; the chest mala, the wrist wrap and the long back mala all hang in slack open LOOPS in the air, neither up nor down, curling with no direction. Nothing in the silhouette is symmetrical, nothing is braced, no limb is where he would have put it, and there is no line of action through the body at all - it is a dropped bundle, not a pose.
3. BEAT 3 - FALLING (drawn for vy above +100 and held 0.25-0.42s, and it is the cell on screen when he hits the floor): nearly inverted and head-down, the heavy stone mask leading the drop like a plumb-weight; the body folded almost in half around the middle with the spine rounded and the chin driven onto the chest; both knees splayed loose ABOVE him with the feet apart and the ankles completely slack; both arms trailing fully overhead and straight, shoulders at full stretch, hands open and empty; the chest mala streaming off the neck PAST the mask, the wrist wrap whipped straight up and standing clear of the body outline, and the long back mala, both sash tails and the scarf all vertical and pointing UP. The whole silhouette is a dropped weight with a tail, and nothing about it is a pose he chose.

⛔ **Packing: this row has NO stance beat.** The packer anchors scale on beat 1 by default, and
beat 1 here is the pop — the most extended frame in the row. Anchoring there packs the whole row
too small. Pass `--scale` taken from this fighter's idle, or `--anchor` at the most neutral beat.
The union of an 8-beat arc is also taller than a standing pose, so budget `grow_frame.py --down`
if the dry run prints `REFUSE: scaled window exceeds cell`.

**Prompt**

```text
Sumi-e / ink-brush shodo character sheet, side-on 2D fighting-game view, 3 frames in one horizontal row, evenly spaced, identical camera, identical character scale in every frame, full body with both feet visible in every frame, plain flat background, no ground line, no cast shadow, no floor bar, no motion-blur smear across the frame edge.

CHARACTER (exact canon - do not invent or substitute): MOKURAI, male, a stone-masked Buddhist monk. He carries NO WEAPON OF ANY KIND - no staff, no bo, no blade, no chain - and nothing is dropped or falling beside him. His only gear is prayer beads. He has NO HOOD and NO HAIR: a bare bald dome, warm bone-tan (body #c09860, highlight #e1bb85), with the front of the face from the hairline down a carved GREY STONE PLATE (mid #908878, shade #807868, light #a8a090, highlight never brighter than #d8d0c1 - no pure white anywhere on the stone). The tan skull stays visible above and behind the plate, including in the inverted frame. A small red oval jewel sits high on the centre of the stone forehead. His EYES STAY CLOSED in every frame - serene lids, thin dark lash lines, no pupils, no whites, no glow, never red. The mask cannot show pain, so the BODY has to. A long gold double-ring ear ornament hangs from an elongated earlobe on the visible ear.

BEADS (three pieces, all present and all whipping loose in every frame, never snapped, never scattered, never left out): a fine gold bead cord high on the throat; a strand of large matte-black wooden mala beads on the chest; and a LONG black mala strand off his back, hip-length, ending in one larger bead. Both wrists carry stacked gold bands and the right wrist adds a black bead wrap over the back of the fist.

CLOTHING: a sleeveless saffron/ochre wrap (#b89058-#c09860) crossed at the chest over a charcoal-black long-sleeved under-layer - the arms are black to the wrist, only the hands are bare tan. A vermilion sash (#782810 into #401808) knotted at the waist with two long ragged tails, and a matching ragged vermilion scarf off the back of the right shoulder. Baggy charcoal-black hakama gathered at the ankles. FOOTWEAR: dark charcoal open-toe foot-wraps with an instep strap, bare tan toes exposed, two or three stacked GOLD ankle rings above them. Not bare feet, not boots, not tabi. No purple, no violet, no magenta anywhere. No gold glow, halo, aura, energy, impact flash, shock ring, speed lines or dust - the game draws all of that. No blood, no tears in the cloth.

HE FACES LEFT. This is the pose while he is being JUGGLED in mid-air by a launcher. He is NOT in control and NOT fighting. These are three separate STILLS, each held on screen for a third of a second or more, read strictly in order: rising hard, weightless apex, falling head-down. They are not a tumble loop and frame 3 must never read as more airborne than frame 1.

THIS IS THE ONE ROW WHERE HIS SILHOUETTE MUST LOOK BROKEN INSTEAD OF COMPOSED. No braced limbs. No chosen poses. No symmetry. No line of action. After frame 1 there is no muscle tone anywhere in the body - if a hand looks placed, or a leg looks supported, or the two shoulders sit level, the frame is wrong. The trailing cloth and the three bead strands are the arc's pointer: they stream straight DOWN in frame 1, hang in slack open loops in frame 2, and stream straight UP in frame 3.

THE 3 BEATS IN ORDER:
1. RISING HARD: both feet torn off the floor with the toes trailing; spine arched hard backwards over the hit; stone mask snapped back facing the sky, throat open; both arms flung up and back behind the head, hands open and fingers splayed; chest mala lifted clear off the collarbone; every strand of cloth and every bead snapping STRAIGHT DOWN in one hard vertical line.
2. APEX, FULLY LIMP: torso rotated past horizontal, chest toward the floor; the heavy stone head hanging BELOW the shoulder line, lolled onto one shoulder, the mask turned three-quarters away from camera so the closed eyes read as unconscious; one shoulder dropped lower than the other; one arm limp across the chest, the other flung out behind with a broken wrist and open fingers; legs hanging apart with no tension, one knee bent and one straight, ankles slack; all three bead strands hanging in slack open loops in the air, neither up nor down; cloth curling with no direction; nothing symmetrical, nothing braced.
3. FALLING HARD, HEAD-DOWN: nearly inverted, the stone mask leading the drop like a plumb-weight; body folded almost in half, spine rounded, chin on the chest; both knees splayed loose above him, feet apart, ankles slack; both arms trailing straight overhead at full stretch, hands open and empty; the chest mala streaming past the mask, the wrist wrap standing clear of the body outline, and every strand of cloth and bead vertical and pointing UP.
```

**Pitfalls for this fighter**

- EIGHT FRAMES. THE ENGINE READS THREE. This is the correction that matters most and it halves the board. The air-hit picker is `const beat = p.vy < -80 ? 1 : p.vy > 100 ? 3 : 2; return F['airhurt' + beat]` at index.html:12310-12311, and that is the ONLY consumer of the row in the file. All nine sheets carry exactly airhurt1/2/3 and nothing else, so an 8-frame board ships five cells that can never draw. Widening the picker is not a free fix either: it would need matching cells on the other eight fighters or they fall through to an undefined key.
- DRAWING IT AS A POSE - and the middle frame is where it will happen. The three cells are each held for a long time (airhurt1 0.27-0.44s, airhurt2 exactly 0.164s of game time because its band is a fixed 180 px/s window, airhurt3 0.25-0.42s at GRAVITY 1100 across the roster's launchers), so there is nowhere for a bad frame to hide in motion. Frame 2 must have NO muscle tone: if the limbs look placed, or the body is symmetrical, or a hand is braced, or you can draw a line of action through it, the beat is wrong. His closed-eyed stone face cannot emote, so the whole read is the slack neck, the head hanging below the shoulder line, the dropped shoulder and the bead loops.
- BEATS OUT OF ORDER, OR AN ARC THAT LOOPS. The picker bands on the victim's VERTICAL VELOCITY, so frame 1 must be unambiguously more 'rising' than frame 2 and frame 2 more than frame 3, with no exceptions - a cycle that reads as a tumble will flicker between cells every time vy crosses a band edge. Measured reference: launcher velocities across the roster run -200 to -560 px/s with the default at -430 (index.html:10597) and most launchers at -380/-390, giving 66-143px of pop and 0.69-1.02s of airtime.
- REUSING HIS EXISTING TUMBLE. Measured: airhurt1/2/3 point at cells 180, 181 and 183, which are CO-TENANTED as grabbed3/grabbed4/grabbed6, and 183 is also mroll4. Looked at on the master: they are throw-victim art - a curled-up somersault, not a launch - and they are not free to repoint. This must be genuinely new art, not a re-crop of the 178-185 tumble.
- A STAFF, OR ANY DROPPED OBJECT. He has never had one (index.html:1512, 'The bo staff is erased from canon, not set down in it'). A limp airborne figure is exactly where a generator adds a pole falling beside him.
- BARE FEET. Measured off the master: dark charcoal open-toe foot-wraps with an instep strap, bare tan toes exposed, two or three stacked gold ankle rings above. Draw them even on the inverted frame where the feet are at the top.
- THE BEADS DISAPPEARING IN THE INVERTED FRAME. All three strands stay ON him - throat cord, chest mala, back mala - plus the right-wrist wrap, through all three frames. Do not snap them, scatter them as loose beads, or leave them out of frame 3 because they are awkward there; they are the clearest motion cue in the row and the thing that separates rising from falling.
- A DRAWN GROUND BAR, SCUFF OR IMPACT DUST. He is airborne in all three beats, and the packer welds the board's lowest ink to the floor line so any drawn ground makes him hover by its own thickness. His own boards have shipped with ink dashes under the feet before - measured today on cells 289 (96px of lateral floor ink), 287 (47px), 294 (37px) and 295 (30px). Nothing at all beneath him, and no shock ring, speed lines or red flash - the engine owns those.
- SCALE DRIFT, AND MEASURING IT ON THE BBOX. Rotating and folded bodies tempt a generator to resize each panel to fill it. The ruler is HEAD WIDTH at the temples: 44-45px on all seven of his idle/xidle cells (332, 207-212) against a 154px standing ink height in a 300x248 cell. Never bbox height - in this row it legitimately halves, and his existing tumble cells measure 79px to 156px tall for the same body.
- CROPPED HANDS, FEET OR MASK AT THE PANEL EDGE. In frames 1 and 3 the arms and feet reach the top of the frame and the mask the bottom; leave margin so nothing touches an edge. This project has already lost soles to an edge cut on nine cells.
- PURE WHITE ON THE STONE. The pack-time keyer drops min-channel >= 205 and is what ate near-white eyes at sheet 708, so a white highlight becomes a hole punched through his mask exactly where the frame's read lives. Measured ceiling on his head today is #d8d0c1; the only near-white on his sheet is gold specular on rings and beads.
- OPENING HIS EYES BECAUSE HE IS HURT. They stay closed. It is the single most likely 'improvement' a generator makes to a pain frame.
- BOOTS, PURPLE, OR A GOLD AURA. Open-toe wraps with exposed toes and gold ankle rings; no violet anywhere (measured: 5 near-neutral dark-plum pixels out of 936,158 opaque pixels on his whole sheet - he has no purple, that is Exile's colour); no karma glow, the engine draws the gold itself at index.html:4139-4145 and 9181-9191.
- DRAWING HIM FACING RIGHT. Cells with no `mirror` entry are drawn unflipped when he faces LEFT (index.html:2415). His current airhurt cells 180/181/183 are all listed in the mirror map, i.e. drawn facing right; authoring this replacement facing LEFT, like his idle, costs zero new mirror entries.


---

## Row C — `njump1..8` — the second jump — Mokurai — the only serene rotation in the game

*A monk who does not rise for anyone. He still curls — but it is a **seated meditation tuck**,
full lotus, hands together, turning slowly and calmly while everyone else tumbles.*
**Bare hands with prayer beads. Never a staff.**

> …A calm monk with **no hood**, a **gray carved stone mask with a red jewel on the forehead**,
> saffron and ochre robes, maroon scarf, **bare hands with prayer beads wrapped round both
> fists — no weapon, no staff**, drawing up into a seated meditation posture in mid-air and
> rotating slowly.
> Frame 1: feet lifting, legs beginning to fold inward, hands coming together.
> Frame 2: legs crossing into a lotus fold, palms pressed, beads swinging out.
> Frame 3: quarter turn, a serene seated ball, robes settling around him.
> Frame 4: half turn, inverted, still perfectly composed and still seated, beads orbiting.
> Frame 5: three-quarter turn, hands beginning to part.
> Frame 6: legs unfolding downward, beads trailing.
> Frame 7: nearly upright, one foot reaching.
> Frame 8: upright, feet planted, hands open at his sides, beads settling.


⛔ **Packing: no stance beat here either.** Same `--scale` / `--anchor` rule as Row B, and
the rotation makes the union taller still.
