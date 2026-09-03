# Roster frame audit — what is actually wrong in the shipped sheets

Run 2026-09-02 against SHODO-EDITION at `SHEET_V 694`. Every LIVE cell of all nine
fighters was rendered POST runtime keyer, laid out by animation row, and inspected
frame against frame. Every defect claimed was re-checked by a second pass; only
survivors are listed. **74 defects, 17 of them blockers, on all nine fighters.**

The owner spotted this before the tooling did. That is the headline.

## Totals

| Kind | Count |
|---|---|
| cut-off | 29 |
| erased-part | 14 |
| fragment-floating | 13 |
| size-pop | 5 |
| other | 4 |
| destroyed | 4 |
| wrong-art | 3 |
| blank | 2 |

| Fighter | Defects | Blockers |
|---|---|---|
| oni | 24 | 4 |
| mokurai | 15 | 5 |
| ember | 7 | 0 |
| executioner | 7 | 3 |
| kael | 7 | 1 |
| exile | 5 | 2 |
| mizu | 3 | 2 |
| shin | 3 | 0 |
| tsubasa | 3 | 0 |

## Per fighter

### oni — 24

- **cell 252** `knives` — destroyed _(blocker)_  
  No character at all. The frame holds a shredded dark-brown wedge of horizontal streaks with no mask, no head, no torso, no legs. Both neighbours (332 and 253) show a complete masked figure at the same scale.
- **cell 400** `run_clean` — cut-off _(blocker)_  
  The front of the body ends in a dead-straight vertical line running ~70% of the sprite's height (26 of 37 content rows start at the identical x). The white oni mask and face are gone entirely - only 1 pixel above lum 150 remains versus 3-7 in cells 394-398, which all show a full white mask with the red eye. What's left reads as a dark slab of hood/hair plus a trailing leg.
- **cell 401** `run_clean` — cut-off _(blocker)_  
  Same flat vertical wall as 400 - 24 of 32 content rows begin at the exact same x. No white mask anywhere (1 bright pixel), no head shape; the frame reads as hair/cloak spray plus one leg. Neighbours 394-398 in this row all carry a full mask.
- **cell 329** `wslice` — wrong-art _(blocker)_  
  This cell holds a large brown-and-gold longbow with a nocked arrow drawn across the chest and a bright gold burst at the grip, spanning nearly the full frame height. The other seven frames in the row (232-236, 238, 239) are the same armored oni swinging a short straight blade with no bow and no glow anywhere. The cell number is also out of sequence with its neighbours. Confirmed visually at 8x on all eight frames side by side.
- **cell 407** `ajump` — erased-part _(notable)_  
  The white horned mask is missing. The head is a dark hood covered by a red/brown spray fan, with only a faint pale sliver left. Frames 402-406 all show a clear pale mask with horns in the same head position; 407 has essentially none of it.
- **cell 430** `glfwd` — fragment-floating _(notable)_  
  A thin dark-grey 1px vertical line at the left of the character runs unbroken from well above the head to below the feet (72 rows, single column). It is detached from the body, hands and weapon. Every other frame in the row starts 20+ rows lower; only 430's content reaches that high.
- **cell 470** `gsback` — wrong-art _(notable)_  
  Two faces in one frame. The fighter's own small white horned mask sits at the left, and a second, much larger white horned skull-face with its own dark eye socket is drawn fused into the burst to its right. No other gsback cell has a second face.
- **cell 433** `hfwd` — fragment-floating _(notable)_  
  A detached dark chunk that reads as a shin and boot sits at the lower right, separated from the real right foot by a clear grey gap, and its own right side ends on a flat straight edge.
- **cell 434** `hfwd` — cut-off _(notable)_  
  The left silhouette is one dead-straight vertical wall from the top of the head to the foot. The white mask is chopped in half on that same column, and shoulder, arm and leg all terminate on it. Hard edge: full-strength ink against pure background, no rim.
- **cell 438** `hfwd` — cut-off _(notable)_  
  Flat vertical pixel wall down the left of the figure, 20 of 36 body rows. The front arm, torso edge and the ground shadow all stop dead on the same column instead of tapering.
- **cell 90** `hurt` — fragment-floating _(notable)_  
  A detached vertical sliver floats left of the body, separated by clear grey background, running from mid-height to the ground. It has real structure (pale rod on top, red cloth mid, a dark boot shape at the base), so it is leftover art, not spray. Cells 88 and 89 have nothing there.
- **cell 367** `kdraw` — cut-off _(notable)_  
  The right side of the body is boxed flat: blade arm, cape and rear leg all terminate on one vertical column for 23 of 43 body rows, down to the ground shadow.
- **cell 332** `knives` — cut-off _(notable)_  
  The left silhouette is a flat vertical slice for 35 of 45 body rows, from shoulder through hip. Part of the whole-row clip: every knives cell is cropped to the same x range, but this is the cell where the slice eats the most body.
- **cell 452** `ksweep` — cut-off _(notable)_  
  The cape/back on the right is a dead-straight vertical line from mid-height to the ground, 22 of 35 body rows. Hardest cut on the sheet: median ink 174 immediately inside the column, 3 (pure background) immediately outside.
- **cell 399** `run_clean` — erased-part _(notable)_  
  The oni mask is chopped down to a thin white vertical sliver at the same cut line that flattens 400 and 401; the face behind it is dark and gone. 13 of 35 rows share one left-edge x, roughly double the 6-9 of the clean cells. 394-398 each show the full white mask with the red eye.
- **cell 469** `gsback` — cut-off _(minor)_  
  Left edge runs dead straight for 31 of 45 body rows with a hard ink-to-background step (147 inside, 3 outside). Real, but not cell-specific: unflagged 468 and 471 sit on the same column, so the whole gsback row is cropped, not this frame alone.
- **cell 253** `knives` — cut-off _(minor)_  
  Straight vertical slice down the left of the body, 31 of 44 rows, and the trailing side ends flat too. Silhouette reads as a rectangle. The claim of a 28-row right cut is overstated; the right run measures 7.
- **cell 254** `knives` — cut-off _(minor)_  
  The right side of the body ends on a straight vertical line for 26 of 44 rows, giving a squared-off trailing edge. The left run is only 11 rows, so the 'boxed on BOTH sides' framing overstates the left.
- **cell 249** `knives` — cut-off _(minor)_  
  Flat vertical wall down the left of the body, 22 of 66 rows (32 rows sit exactly on the clip column). Same whole-row horizontal crop; the thrown star above is intact.
- **cell 250** `knives` — cut-off _(minor)_  
  The back/cape on the left ends on a straight vertical line, 26 of 46 body rows, chopped flat with no taper.
- **cell 248** `knives` — cut-off _(minor)_  
  The cape on the right ends on a straight vertical column, 22 rows, and the left edge is flat on the same row-wide clip. Mild compared with 332.
- **cell 333** `knives` — cut-off _(minor)_  
  Left and right silhouette both sit on the row's clip columns; the trailing cape ends flat for 17 rows. Weakest of the knives set - the claimed '14-38 of 45' right cut measures 17.
- **cell 453** `ksweep` — cut-off _(minor)_  
  The cape on the right is a straight vertical cut from shoulder to ground, 17 of 35 rows. The two chunks floating to the left are small, dark and sit on a diagonal - they read as kicked-up sweep debris, not torn body art, so the fragment half of the claim does not hold.
- **cell 329** `wslice` — other _(minor)_  
  The figure floats above the row's ground line. Its body art bottoms out at y=99 in the cell (only the bow tip reaches y=100), while all seven other frames in the row bottom out at y=103. That is a 4px lift, and it is visible in the strip as this figure's feet sitting higher than every neighbour's.

### mokurai — 15

- **cell 142** `kpush` — wrong-art _(blocker)_  
  The frame carries baked-in board furniture: a hard straight dark vertical line running the full height of the cell down the left side of the figure, plus a straight horizontal line with a rounded corner near the bottom. The figure is also drawn noticeably larger and with heavier, darker outlines than the rest of the row - its art box measures 103 px tall against 70-81 px for 305-312, and it reaches the very top of the cell while every other kpush frame has 22-33 px of stage above the head. None of 305-312 carry any ruled lines.
- **cell 142** `kpush` — erased-part _(blocker)_  
  A big flat cream/bone wedge - unshaded, hard-edged - sits where the near leg and foot should be. The dark rear thigh terminates in a flat edge against the top of that wedge, and no shin or boot is drawn on that side. Only the far leg's gold boot survives. Every other kpush frame shows two complete legs and two booted feet.
- **cell 315** `mthrow` — fragment-floating _(blocker)_  
  A whole detached lower leg — dark trouser plus a gold sandal, drawn with the same ink outline as the body — floats at the lower right, separated from the figure by about 10px of empty grey stage. The character already stands on two of his own feet at the bottom-left and bottom-centre, so this is a third orphan leg hanging in mid-air. It is solid body art, not the gold streak FX that sweeps overhead in the same frame.
- **cell 254** `special` — cut-off _(blocker)_  
  The back of the figure is sliced off along a dead-straight vertical line: tan shoulder, dark tunic and red sash all terminate at the same column with no ink outline and no rounding. Measured, the leftmost lit pixel sits at x=46-47 for 38 consecutive rows; every undamaged cell on the sheet has a wandering contour with a max flat run of 7-25 rows. Only one leg remains below.
- **cell 255** `special` — cut-off _(blocker)_  
  Same flat vertical slice down the back — the head is still rounded but from just under it down past the sash the shoulder, tunic and red sash tassel all end on one column (x=55-56 for 47 consecutive rows, vs a 7-25 row baseline elsewhere). The rear leg is gone with it; the body reads as half a character standing on a single sandal.
- **cell 237** `bair` — cut-off _(notable)_  
  The gold impact burst does not fade out - it terminates against straight ruled lines. A hard dark vertical line sits at the left of the FX (column 780, rows 106-117, uniform dark grey), a pale vertical line at the right (column 830, rows 91-110, with another straight pale run at column 829 rows 46-66 climbing past the head), and the burst stops dead on a flat bottom edge at row 124 with clean stage grey immediately below. These read as baked-in board panel borders, not art.
- **cell 237** `bair` — erased-part _(notable)_  
  The body ends at mid-thigh - the gold-wrapped thigh terminates in a pale rounded blob and the impact burst occupies everything below it. No shin, no ankle, no foot anywhere in the frame. The neighbouring air frames 236 and 238 both show a full leg with a boot.
- **cell 239** `bair` — other _(notable)_  
  Three separate gold-wrapped shins each ending in a foot at the bottom of the landing crouch: a pale-toed boot at far left, a bare foot with splayed toes at centre, and a boot at right, all on the ground line. Both arms are accounted for elsewhere in the pose - left arm raised up-left, right arm across the chest - so none of the three is a planted hand. The comparable landing crouch in bjump 295 has exactly two feet.
- **cell 310** `kpush` — fragment-floating _(notable)_  
  A pale thin vertical ruled line with straight parallel sides floats to the left of the body - column 1071, an unbroken 35 px run - separated from the figure by two clear columns of stage grey (the body starts at column 1074) and running down past the ground shadow. It is uniform-width ruled line, not effect spray or dust. No other kpush frame has it.
- **cell 175** `mblast` — erased-part _(notable)_  
  The forward extended hand is a hollow outline only. The gold wrist cuff is solid, then the hand becomes a 1px brown hook with grey stage showing straight through where the palm and fingers should be. Cell 174 in the same row, same arm, has a fully filled tan hand.
- **cell 259** `mhurt` — fragment-floating _(notable)_  
  Two detached, ink-outlined pieces float to the right of the outstretched hand with a clear grey gap: a skin-toned crescent the colour of his fingers, and below it a dark-red chunk the colour of the sash tassel. Both are solid drawn art with outlines, unlike the soft gold spark FX used elsewhere on the sheet; the black prayer-bead string nearby is separate from them.
- **cell 260** `mhurt` — erased-part _(notable)_  
  The head is only a small grey wedge (about 8px) perched on the neck, with the red forehead mark at its tip — no bald tan cranium and no face behind it. Frames 258, 259, 261, 262, 263 and 264 in the same row all show a full round head roughly twice that size with the mask on it.
- **cell 253** `special` — cut-off _(notable)_  
  The back edge of the torso is the same straight vertical cut (x=48 for 47 consecutive rows, far outside the 7-25 row baseline), fills ending with no outline. The rear leg tapers to a point and stops in mid-air roughly 8px above the ground shadow with no foot, while the front leg has a complete gold sandal planted on the shadow line.
- **cell 238** `bair` — fragment-floating _(minor)_  
  A pale grey vertical bar with straight parallel edges sits just to the right of the head - columns 970-971, rows 75-95, so 2 px wide by 21 px tall - detached from the body by a gap of clear stage grey over its upper two-thirds. A ruled-line remnant.
- **cell 234** `bair` — fragment-floating _(minor)_  
  A short pale grey vertical dash with straight parallel edges hangs just off the right of the outstretched hand - columns 390-391, rows 76-88, so 2 px by 13 px - with stage grey between it and the fist below the contact point. Same stray ruled-line remnant as in 238.

### ember — 7

- **cell 207** `grab` — cut-off _(notable)_  
  The art runs off the bottom of the frame: a solid 33px-wide band of ink sits on the very last pixel row, and rows 108-115 are near-full-width ink. Sibling frames 201-208 all stop with 0-4px on that row and clear space below. The lower-right mass is sliced flat by the frame edge.
- **cell 237** `grabbed` — erased-part _(notable)_  
  A flat patch the same value as the empty stage grey sits across the middle of the hood/face, roughly 9px wide x 6px tall, with a hard straight top edge under the lit hood crown. Every other frame in the row (234, 235, 236, 238) has a fully textured hood there. The head silhouette is still closed, so it reads as a blank washed-out chunk of the face rather than a hole all the way through.
- **cell 133** `hurt` — other _(notable)_  
  The whole figure floats. Solid ink ends at row 101 versus rows 113 and 114 in 131 and 132, so the boots hang about 12px above the neighbours' ground line. Body height is the same (45px vs 47 and 43), so it is purely a vertical offset and will pop upward for one frame.
- **cell 147** `kpush` — size-pop _(notable)_  
  The whole kpush row (147-154 plus the leading 151) draws Ember at roughly 65-70% of his idle/xidle size on this same sheet. It is the same hood-and-scarf character, not a compact pose: the hood and the white eye themselves are visibly smaller at 8x zoom, which a bent-knee push stance cannot cause. Measured ink bbox height 34-41 px across the row against 63-64 px for idle 81/82 and xidle 75/79, and ink area 649-843 px against 1410-1507 (area ratio 0.48, linear ~0.69). The row is internally consistent, so nothing pops between kpush frames, but the row sits under-scaled against the rest of the kit.
- **cell 280** `espec` — fragment-floating _(minor)_  
  Two faint detached smudges (about 9px of ink each) sit at rows 112-115, roughly 6 rows below the feet, with clean background between them and the body (body ink stops at row 106). Very low contrast - reads as leftover ground-shadow dust rather than ink.
- **cell 277** `espec` — fragment-floating _(minor)_  
  A faint detached smudge (about 11px of ink) sits at rows 112-115, about 6 rows below the feet, with clean background between it and the body (body ink stops at row 106). Same leftover-dust remnant as 276 and 280, and the darkest of the three.
- **cell 276** `espec` — fragment-floating _(minor)_  
  A faint detached smudge (about 11px of ink) sits at rows 112-115, about 6 rows below the feet, with clean background between it and the body (body ink stops at row 106). Barely above stage grey - only clearly visible when zoomed.

### executioner — 7

- **cell 324** `xkiriage` — blank _(blocker)_  
  The frame contains no character at all - only a large orange/black crescent sword-trail arc and a faint white glint on empty grey. No head, horns, eyes, torso or legs anywhere in the cell. Neighbouring 323 and 325 both show the full Executioner together with their trail, and every other crescent frame on this sheet (xjodan 261, xnuki 265, special 198) draws the arc over the fighter, so this is not an intentional FX-only beat.
- **cell 324** `xrise` — blank _(blocker)_  
  Confirmed. Cell 324 holds only the orange/black crescent slash arc on empty grey stage — no fighter at all. Measured inside the cell (x 506-590, y 22-139 in the sheet): 0 pixels of the purple armour colour and 1 stray yellow-ish pixel, versus 75-115 purple pixels in every other xrise frame (320-323, 325-327), each of which shows the full horned Executioner. Not a compact pose and not an occlusion — there is simply no body, head, or mask anywhere in the frame.
- **cell 295** `xtsuki` — size-pop _(blocker)_  
  Confirmed, and it reads as wrong art rather than a pose. Placed at identical scale next to 320, 323, 296 and 297, cell 295 is a tall adult-proportioned samurai — small head, long torso, long legs — while every other frame on the sheet is the chibi ~3-head-tall build with an oversized horned helmet. The head is roughly 0.6-0.65x the width of its rowmates' while the figure fills the same cell height, so the difference is body proportion, not an extended weapon or a crouch.
- **cell 127** `guard` — erased-part _(notable)_  
  The katana is gone outside the body outline: no hilt, no pommel, no blade, no scabbard. Only a ~10px pale diagonal sliver survives across the belly where the sword crossed the torso. Content bbox is 35px wide vs 56px for cell 128, the near-identical standing guard beside it, which shows the pommel at the left hip and a long blade running down-right past the leg. Cells 245/246/247/248/269 all carry a visible sword too.
- **cell 268** `kpush` — erased-part _(notable)_  
  The sword is gone. At high zoom the left hip carries only a short dark stub tipped with a single gold pommel pixel that stops dead - no blade continues off it and none crosses the body, which is in an arms-folded pose. Frames 97, 238, 239, 240, 241, 103 and 104 all show a full grey blade, and in 240/241 that blade extends left at chest/waist height, precisely the region that is bare grey in 268.
- **cell 295** `xtsuki` — erased-part _(notable)_  
  Confirmed visible, though it is a facet of the wrong-proportion rendition above. In 295 the helmet is a small smooth cap with nothing above it but the raised gauntlets and sword hilt; no horns anywhere. Occlusion is ruled out by cell 323, which has the sword raised over the head in the same way and still shows both purple horns clearly. 296 and 297 both show large paired horns, as do 320-322 and 325-327.
- **cell 268** `kpush` — fragment-floating _(minor)_  
  A small orange-cored blob with white flecks floats to the LEFT of the chest, separated from the nearest ink by a clear band of clean panel grey (roughly 10-12 px). It is not a spray or dust trail belonging to the move: the fighter faces right (eyes right, sash tails streaming left), so a push impact spark would sit in front of him, not behind, and no other frame in the row carries anything like it. The figure is also shifted hard to the right of the cell while 97/238/239/240/241/103/104 are centred, which is what opens the gap.

### kael — 7

- **cell 284** `krise` — erased-part _(blocker)_  
  The hood/head is a hollow outline only - a dark ring with the mid-grey stage showing straight through the interior. No face fill, no lit eye. At 14x zoom the interior pixels read as the exact stage colour. Cells 283 and 285-290 in the same row all have a solid filled hood with a gold-lit eye.
- **cell 208** `kcyc` — erased-part _(notable)_  
  The hood/head is a hollow ring: a thin dark outline arc with plain stage grey showing straight through the interior where the solid dark hood and face should be. Cells 203, 206 and 209 in the same row all have a solid shaded helmet with a visible masked face. Only the head is affected - the rest of the body is normally filled (54.7% ink fill vs 55.0% in 209), and its shorter ink block (31px vs 44px) is just the compact recovery crouch after the 207 spin, not damage.
- **cell 233** `medium` — cut-off _(notable)_  
  A solid dark-brown wedge is baked into the cell, filling the whole gap between the legs from the crotch down and ending in a hard straight horizontal line at boot level, wider than the feet. Cell 186 at the same crop shows clean grey stage between the legs.
- **cell 234** `medium` — cut-off _(notable)_  
  Same baked-in dark-brown ground wedge filling the leg gap, flat straight bottom edge running wider than the boots. The middle cells of the row (184-188) are clean.
- **cell 235** `medium` — cut-off _(notable)_  
  Same baked-in dark-brown ground wedge between the legs with a hard straight bottom edge extending past the boots; middle cells of the row have transparent grey between the legs.
- **cell 269** `sneu` — cut-off _(notable)_  
  Dark slab baked between and under the boots, flat-topped triangle with a dead-straight horizontal bottom edge wider than the feet. Sampled at RGB ~(24,23,18) vs boot ~(49,48,46) - far darker and harder-edged than cell 270's real soft drop shadow (~98,100,102). Cells 270 and 272 are clean.
- **cell 276** `sneu` — cut-off _(notable)_  
  Same dark-brown ground slab between the legs with a flat straight bottom edge running wider than the boots, unlike the clean mid-row cells 270-275.

### exile — 5

- **cell 143** `gsfwd` — size-pop _(blocker)_  
  The whole character is drawn at a smaller scale than the rest of the row. Head-crown width measured 5 rows below the top of the hair is 11px here vs 17px on both 252 and 253 (~0.65x), and the face patch is about half the area. Body ink is ~28px tall vs ~46-48px on the standing frames. Top-of-head-aligned crops show the head is plainly the smallest in the row - a forward lunge lowers the body but cannot shrink the skull and hair mass.
- **cell 149** `xksweep` — destroyed _(blocker)_  
  The ninja is shredded: only the spiky head and a bit of face survive; the torso and legs break up into scattered dark/gold specks with holes through them, plus a line of loose chips trailing left along the ground. Measured at ink threshold 30 it is 211 px in 11 disconnected pieces (largest piece 149 px), while every other frame in the row (145,146,147,148,272,273,151,152) is 431-711 px in only 1-4 pieces with a main body of 423-709 px. Not a low sweep pose - a crouch would still be one solid mass.
- **cell 141** `gsfwd` — size-pop _(notable)_  
  Head/hair mass is visibly undersized against the row: crown width 13px vs 17px on 252 and 253, and 15px on 140 in the same row. Body ink ~38px vs ~46-48px. The pose is an upright planted thrust with a dust puff at the feet, not a crouch, so the shortfall reads as scale, not compression. Side by side with 253 at matched head-top alignment the head and shoulders are about three quarters the size.
- **cell 142** `gsfwd` — size-pop _(notable)_  
  Same undersized character as 141 and measures identically: crown width 13px vs 17px on 252/253, body ink ~38px vs ~46-48px. Standing thrust with the same foot dust, so the smaller head and torso are a scale difference rather than a lower pose.
- **cell 82** `xheavy` — fragment-floating _(notable)_  
  A thin dark vertical sliver floats at the lower left, clearly separated from the body by empty grey stage. Component analysis: body occupies x50-75, the fragment is 13 px at x46-47 y74-83 with a 2 px bit at x46 y69-70 (about 2 px wide, 15 px tall), columns 48-49 empty between them. It is not the kusarigama chain (sickle and handle are up top-left, ribbon is on the right, no chain drawn across the gap) and not ground dust (vertical, off the contact line). Frames 81/83/84 have only 1-2 px specks; 85's extras are a 6 px ground puff and single pixels.

### mizu — 3

- **cell 184** `heavy_i` — erased-part _(blocker)_  
  The hanbo staff is entirely absent and so are both arms and hands — the figure stands in the wide attack stance with a bare torso, sash streamers, robe and legs only. A single 2-3px tan sliver sits at the mid-right of the torso as the last remnant. Neighbouring frames 182, 183 and 185 all show clearly drawn gripping arms holding the full staff.
- **cell 192** `medium` — erased-part _(blocker)_  
  The bo staff is entirely absent: both gloved hands are visible and empty and no wooden shaft appears anywhere in the frame, while cells 190, 191, 193, 194, 195, 196 and 197 all hold the staff across the body (measured 0 wood-coloured pixels in 192 vs 26-59 in every other cell of the row). The same frame also shows a flat dark eye slot with no white eye highlights (0 near-white pixels vs 5-10 in all seven neighbours). Hood, scarf, torso and legs are intact and the same size as the neighbouring cells, so only the overlay detail was wiped.
- **cell 204** `aneu` — other _(minor)_  
  The staff is drawn about 40% too short, not cut. Measured at matched figure scale (white-eye ruler 5px, same as 201/202/203) the staff spans 32px versus 45/48/54/57/57/58/69/78px in the other seven frames of the row, so it reads as a stub next to its siblings. However both ends carry the same dark drawn end-cap with anti-aliasing as 203's end — there is no raw chop, no hard clipped edge, and nothing is clipped at a cell boundary. The originally claimed 'hard flat vertical cut' is not present; this is a length/proportion inconsistency in a mid-spin airborne tuck.

### shin — 3

- **cell 311** `roll_` — destroyed _(notable)_  
  Only the green hood plate and the blue eye are readable at the right; the entire left side of the sprite is ragged black spike-streaks with teal scarf and green cloth fragments smeared into them, no torso, arms or legs. Cells 309, 310, 312 and 313 in the same row all draw a complete tucked body with distinct limbs and scarf, and none of them has streaks, so this is a single-frame baked motion smear, not the roll's FX.
- **cell 327** `sneu` — destroyed _(notable)_  
  Above the hood the body becomes a featureless olive taper, measured y735-763, 5 to 12 px wide, striated and narrowing to a point, about one hood-length long. That is limb width, not the 1-2 px thin dark katana line this sheet draws in 326 and 289, so it is not an extended weapon. Cell 326 keeps a fully readable upside-down body with two feet. Note the legs and one foot BELOW the hood in 327 are still readable, so only the region above the hood is lost.
- **cell 288** `sparry` — cut-off _(minor)_  
  The cell frame runs y850-967. The incoming weapon enters from the lower left, passes through the parry spark, turns upward at x=765 and rises to y=880 where it stops with a flat blunt end, 30 px below the frame top and touching no frame edge, with no tip and no taper. Cell 289 in the same row draws its blade tapering to a fading point, so the blunt stop is anomalous.

### tsubasa — 3

- **cell 293** `grabbed` — cut-off _(notable)_  
  Back of the head/hood is sliced flat. 22 consecutive scanlines (y62-83) hold the identical right edge x=78, then a second flat wall runs down the back/arm at x=71 for y85-90. The spiky hair fan that 290, 291, 292, 294, 295 and 297 all show is replaced by a smooth blunt vertical edge. 42% of ink-bearing scanlines on the wall vs 0.05-0.30 for the rest of the row. Not explainable by the leaning pose -- the silhouette edge itself is a straight column.
- **cell 251** `gsfwd` — cut-off _(notable)_  
  Right side is cropped on a dead-straight vertical column at cell x=81. Head/hood top-right, shoulder, torso, blade tip, hip and the ground streak all terminate flush on that same column, while the LEFT side of the head keeps its spiky hair fan. Longest flat run 15 scanlines (y82-96), plus y59-67, y73-78, y106-108 at the identical x; 57% of all ink-bearing scanlines sit on the wall vs 0.02-0.30 for every other cell in the row. NOTE: the first inspector's supporting detail is wrong -- the right arm and the blade ARE present (the horizontal slash with the red edge), so this is not a destroyed frame. Downgraded blocker -> notable: real hard crop, but the figure still reads whole.
- **cell 250** `gsfwd` — cut-off _(notable)_  
  The whole field of motion streaks trailing right is chopped on one straight vertical column at cell x=84. Independent red, white and black streaks -- which fan out at different angles and lengths -- all stop dead on the identical column instead of tapering. 20 consecutive scanlines (y86-105) plus a second run y109-113 at the same x; 67% of ink-bearing scanlines sit on the wall, the highest in the row (siblings 0.02-0.30). Reads as a hard crop, not a drawn taper.
