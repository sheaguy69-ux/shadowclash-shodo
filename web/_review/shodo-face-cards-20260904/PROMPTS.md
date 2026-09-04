# SHODO face-card generation — 2026-09-04

Status: Anthony approved the portraits and requested a commit, then corrected Exile's missing eye wrap. Eight approved portraits are installed locally on :9101. Exile's original two-eye portrait is REJECTED; `exile-eye-wrap-v2.png` is a new review-only correction awaiting approval. No Exile portrait has been installed.

All nine are newly generated with the built-in image generator, not cropped from old art. Existing approved art was used as identity reference only. Final cards are intentionally opaque, warm ivory-backed UI images, NOT transparent sprites. Never feed these through a sprite keyer, atlas packer, background flood-fill, or drawShodoFrame. The first Executioner/Mizu/Shin outputs had baked checkerboards and are rejected; final revisions replace that background. Integration updates the shared UI portrait helper and adds both fight-HUD portraits, including tag swaps. No combat, atlas, SHEET_V, or public roster-gate changes. No deployment.

Verification: `node tools/check_portraits.mjs` checks byte-identical approved/local/server images, both HUD updates, and inline JavaScript syntax. Selection and Tsubasa-vs-Oni fight HUD were visually checked in the running :9101 game.

## kael

Identity reference: /Users/anthonyguy/SHADOWCLASH.1.0*2/art/production/kael/idle-v2/frame-01.png

Generated original: /Users/anthonyguy/.codex/generated_images/01a060c4-5fe0-7622-a916-27296479a681/exec-b5c632f1-5282-4278-a4bb-95ab1a294382.png

### Generation prompt

Create ONE BRAND-NEW head-and-shoulders character portrait for ShadowClash's character-select card and small fight HUD face icon. The attached image is ONLY an authoritative CHARACTER IDENTITY reference, not output to crop, trace, or reuse. Draw an entirely new composition. Preserve this fighter's exact established costume, head shape, face/mask type, accent colors and stylized semi-chibi character identity.

ART DIRECTION: very heavy traditional Japanese SHODO / sumi-e calligraphic ink painting. Thick, expressive, messy BLACK brush strokes with dramatic pressure variation, rough split-bristle edges, ink pooling, ragged dry-brush breakup and sharp tapered ends. This must unmistakably read as handmade brush painting, not clean digital anime outlines, not 3D, not photorealism. Broad black shapes, controlled colored ink washes only in the fighter's established accent colors. Cinematic restrained lighting, crisp readable facial landmarks, strong character presence.

COMPOSITION: square 1024x1024. Exactly ONE fighter, no panels or extra poses. Tight bust portrait from upper chest up, head centered, mild three-quarter turn toward viewer-left with readable face; entire hood/hair/horns visible within 8% safe margins. Face large enough to read as a 64px HUD icon. Shoulders and scarf terminate in natural tapered dry-brush strokes INSIDE the canvas, never a straight crop. No hands in this bust. No flying weapons. Distinct silhouette, deliberate negative space.

DELIVERY: Intentionally OPAQUE full square UI card image with uniform warm ivory background #eee7d8, absolutely NO checkerboard, no transparency simulation, no grid, no gradient, no border or rectangle frame, no writing, captions, signature, stamp, seal or logo. Paint the bust directly on the ivory field. Generous margin around entire bust; shoulder and scarf brushstrokes fade/taper onto the ivory before reaching edges. All actual white character details remain white.

KAEL: the attached black-hooded fighter with ochre-GOLD hood trim, ochre-gold scarf and black cloth gi, NOT red. The reference is identity-only. Correct current canon eyes are HAZEL-YELLOW, luminous almond shapes set flat in his black void face, no human face, no nose/mouth/skin. Do not introduce horns. Youngest fighter, hopeful questioning resolve with vulnerability beneath determination, head lifted a touch, shoulders straight and open. Recompose him into a fresh viewer-left three-quarter frontal bust instead of the profile in the reference. Hood recognizable with a soft pointed top. Thick uneven ink outlines, golden scarf rendered with two broad powerful brush sweeps. Weapons cropped out, not redesigned.

## tsubasa

Identity reference: /Users/anthonyguy/SHADOWCLASH.1.0*2/art/production/tsubasa/idle-v4/frame-01.png

Generated original: /Users/anthonyguy/.codex/generated_images/01a060c4-5fe0-7622-a916-27296479a681/exec-62f96013-e4b4-4cc0-a4dc-c4b882b80699.png

### Generation prompt

Create ONE BRAND-NEW head-and-shoulders character portrait for ShadowClash's character-select card and small fight HUD face icon. The attached image is ONLY an authoritative CHARACTER IDENTITY reference, not output to crop, trace, or reuse. Draw an entirely new composition. Preserve this fighter's exact established costume, head shape, face/mask type, accent colors and stylized semi-chibi character identity.

ART DIRECTION: very heavy traditional Japanese SHODO / sumi-e calligraphic ink painting. Thick, expressive, messy BLACK brush strokes with dramatic pressure variation, rough split-bristle edges, ink pooling, ragged dry-brush breakup and sharp tapered ends. This must unmistakably read as handmade brush painting, not clean digital anime outlines, not 3D, not photorealism. Broad black shapes, controlled colored ink washes only in the fighter's established accent colors. Cinematic restrained lighting, crisp readable facial landmarks, strong character presence.

COMPOSITION: square 1024x1024. Exactly ONE fighter, no panels or extra poses. Tight bust portrait from upper chest up, head centered, mild three-quarter turn toward viewer-left with readable face; entire hood/hair/horns visible within 8% safe margins. Face large enough to read as a 64px HUD icon. Shoulders and scarf terminate in natural tapered dry-brush strokes INSIDE the canvas, never a straight crop. No hands in this bust. No flying weapons. Distinct silhouette, deliberate negative space.

DELIVERY: Intentionally OPAQUE full square UI card image with uniform warm ivory background #eee7d8, absolutely NO checkerboard, no transparency simulation, no grid, no gradient, no border or rectangle frame, no writing, captions, signature, stamp, seal or logo. Paint the bust directly on the ivory field. Generous margin around entire bust; shoulder and scarf brushstrokes fade/taper onto the ivory before reaching edges. All actual white character details remain white.

TSUBASA: exact reference identity: no hood; tall swept-back spiky BLACK hair with fine RED streak accents near the roots/front, smooth black ninja lower-face MASK and dark upper face with flat WHITE luminous eyes, black gi with red seam lines and a deep red scarf. No human nose, no new skin face, no iris, no horns, no goggles. Precise, intensely composed swordsman, silent protector; gaze level, still focused dignity, chin slightly tucked, shoulders relaxed rather than aggressive. This is a new tight bust composition, not enlarging an old sprite. Hair built from huge expressive dry-brush black strokes and a restrained vermilion accent, scarf in heavy red calligraphic strokes. Do not draw knives or hands; the portrait crop doesn't alter his established twin tantō.

## executioner

Identity reference: /Users/anthonyguy/SHADOWCLASH.1.0*2/art/production/executioner/executioner-shodo-iaijutsu-idle-8f-v7-safe-cell-layout-approved-review.png

Generated original: /Users/anthonyguy/.codex/generated_images/01a060c4-5fe0-7622-a916-27296479a681/exec-90341571-385b-41a9-a986-26a3213409b3.png

### Generation prompt

Create ONE BRAND-NEW head-and-shoulders character portrait for ShadowClash's character-select card and small fight HUD face icon. The attached image is ONLY an authoritative CHARACTER IDENTITY reference, not output to crop, trace, or reuse. Draw an entirely new composition. Preserve this fighter's exact established costume, head shape, face/mask type, accent colors and stylized semi-chibi character identity.

ART DIRECTION: very heavy traditional Japanese SHODO / sumi-e calligraphic ink painting. Thick, expressive, messy BLACK brush strokes with dramatic pressure variation, rough split-bristle edges, ink pooling, ragged dry-brush breakup and sharp tapered ends. This must unmistakably read as handmade brush painting, not clean digital anime outlines, not 3D, not photorealism. Broad black shapes, controlled colored ink washes only in the fighter's established accent colors. Cinematic restrained lighting, crisp readable facial landmarks, strong character presence.

COMPOSITION: square 1024x1024. Exactly ONE fighter, no panels or extra poses. Tight bust portrait from upper chest up, head centered, mild three-quarter turn toward viewer-left with readable face; entire hood/hair/horns visible within 8% safe margins. Face large enough to read as a 64px HUD icon. Shoulders and scarf terminate in natural tapered dry-brush strokes INSIDE the canvas, never a straight crop. No hands in this bust. No flying weapons. Distinct silhouette, deliberate negative space.

DELIVERY: real transparent PNG alpha around the bust. No white or beige paper background, NO checkerboard painted into pixels, no card rectangle, NO BORDER, no frame, no text, captions, seals, signatures, logos, ground shadows or environment. Keep actual white eyes and mask opaque.

FIGHTER EXECUTIONER: follow the attached horned dark-purple hood/helmet shape, black void face, small angular gold-amber eyes and rust-orange scarf. NO human facial features, no mouth, no nose, no flesh. Two curved dark horns as in reference. Emotional direction: an old disciplined executioner carrying guilt; chin lowered, gaze unflinching, weary restraint rather than snarling rage. Heavy squared shoulders slightly turned, orange scarf one decisive asymmetrical calligraphic sweep. Match his actual design; do not borrow Oni's white mask.

### Final correction prompt

Edit this newly painted ShadowClash executioner portrait. Preserve the fighter design, exact colors, face, pose and thick expressive SHODO ink brushwork. FIX ONLY DELIVERY AND MARGINS: replace EVERY checkerboard square with one uniform warm ivory paper-color background #eee7d8. This is an intentionally OPAQUE portrait card, not a transparent sprite. The background must be completely continuous, solid color, NO pattern, NO checker, NO grid, NO box, NO border or lettering, NO card outline. Do not remove any of the fighter's white eyes or dark ink. Fit the full portrait inside the square with generous 7% warm ivory margin on all four sides, including the tips of horns, scarf and lower shoulder brushstrokes. Taper the strokes before they hit the canvas edge. The figure is painted directly onto the unframed ivory field. One image, one bust, no text.

## mizu

Identity reference: /Users/anthonyguy/SHADOWCLASH.1.0*2/art/production/mizu/mizu-shodo-bo-idle-8f-v2-review.png

Generated original: /Users/anthonyguy/.codex/generated_images/01a060c4-5fe0-7622-a916-27296479a681/exec-c0b98266-6d55-4f3a-95b7-54aff98ceec0.png

### Generation prompt

Create ONE BRAND-NEW head-and-shoulders character portrait for ShadowClash's character-select card and small fight HUD face icon. The attached image is ONLY an authoritative CHARACTER IDENTITY reference, not output to crop, trace, or reuse. Draw an entirely new composition. Preserve this fighter's exact established costume, head shape, face/mask type, accent colors and stylized semi-chibi character identity.

ART DIRECTION: very heavy traditional Japanese SHODO / sumi-e calligraphic ink painting. Thick, expressive, messy BLACK brush strokes with dramatic pressure variation, rough split-bristle edges, ink pooling, ragged dry-brush breakup and sharp tapered ends. This must unmistakably read as handmade brush painting, not clean digital anime outlines, not 3D, not photorealism. Broad black shapes, controlled colored ink washes only in the fighter's established accent colors. Cinematic restrained lighting, crisp readable facial landmarks, strong character presence.

COMPOSITION: square 1024x1024. Exactly ONE fighter, no panels or extra poses. Tight bust portrait from upper chest up, head centered, mild three-quarter turn toward viewer-left with readable face; entire hood/hair/horns visible within 8% safe margins. Face large enough to read as a 64px HUD icon. Shoulders and scarf terminate in natural tapered dry-brush strokes INSIDE the canvas, never a straight crop. No hands in this bust. No flying weapons. Distinct silhouette, deliberate negative space.

DELIVERY: real transparent PNG alpha around the bust. No white or beige paper background, NO checkerboard painted into pixels, no card rectangle, NO BORDER, no frame, no text, captions, seals, signatures, logos, ground shadows or environment. Keep actual white eyes and mask opaque.

FIGHTER MIZU: follow her deep-violet pointed hood with stitched rim, black featureless face, TWO flat luminous white eyes, purple robe and layered purple scarf. NO human nose/mouth or skin, no bubble eyes. She is the mature strategist: poised, perceptive, composed, slightly withdrawn, gaze thoughtful and measuring. Head gently inclined with calm nearly level gaze. Do not add an eyepatch. Keep all purple costume shapes recognizable. No weapons or hands visible: portrait crop avoids changing her first-form one full wooden bo staff into two sticks.

### Final correction prompt

Edit this newly painted ShadowClash mizu portrait. Preserve the fighter design, exact colors, face, pose and thick expressive SHODO ink brushwork. FIX ONLY DELIVERY AND MARGINS: replace EVERY checkerboard square with one uniform warm ivory paper-color background #eee7d8. This is an intentionally OPAQUE portrait card, not a transparent sprite. The background must be completely continuous, solid color, NO pattern, NO checker, NO grid, NO box, NO border or lettering, NO card outline. Do not remove any of the fighter's white eyes or dark ink. Fit the full portrait inside the square with generous 7% warm ivory margin on all four sides, including the tips of horns, scarf and lower shoulder brushstrokes. Taper the strokes before they hit the canvas edge. The figure is painted directly onto the unframed ivory field. One image, one bust, no text.

## shin

Identity reference: /Users/anthonyguy/SHADOWCLASH.1.0*2/art/production/shin/shin-shodo-idle-owner-model-8f-v6-safe-margin-approved-review.png

Generated original: /Users/anthonyguy/.codex/generated_images/01a060c4-5fe0-7622-a916-27296479a681/exec-b87691b6-67f5-4c66-b36c-0f144870ad53.png

### Generation prompt

Create ONE BRAND-NEW head-and-shoulders character portrait for ShadowClash's character-select card and small fight HUD face icon. The attached image is ONLY an authoritative CHARACTER IDENTITY reference, not output to crop, trace, or reuse. Draw an entirely new composition. Preserve this fighter's exact established costume, head shape, face/mask type, accent colors and stylized semi-chibi character identity.

ART DIRECTION: very heavy traditional Japanese SHODO / sumi-e calligraphic ink painting. Thick, expressive, messy BLACK brush strokes with dramatic pressure variation, rough split-bristle edges, ink pooling, ragged dry-brush breakup and sharp tapered ends. This must unmistakably read as handmade brush painting, not clean digital anime outlines, not 3D, not photorealism. Broad black shapes, controlled colored ink washes only in the fighter's established accent colors. Cinematic restrained lighting, crisp readable facial landmarks, strong character presence.

COMPOSITION: square 1024x1024. Exactly ONE fighter, no panels or extra poses. Tight bust portrait from upper chest up, head centered, mild three-quarter turn toward viewer-left with readable face; entire hood/hair/horns visible within 8% safe margins. Face large enough to read as a 64px HUD icon. Shoulders and scarf terminate in natural tapered dry-brush strokes INSIDE the canvas, never a straight crop. No hands in this bust. No flying weapons. Distinct silhouette, deliberate negative space.

DELIVERY: real transparent PNG alpha around the bust. No white or beige paper background, NO checkerboard painted into pixels, no card rectangle, NO BORDER, no frame, no text, captions, seals, signatures, logos, ground shadows or environment. Keep actual white eyes and mask opaque.

FIGHTER SHIN: olive mottled hood, black featureless face with CYAN eyes, ragged dark TEAL scarf and small authentic chainmail details beneath olive clothing. Eyes are narrow luminous shapes flat/inset INTO the dark face, NEVER spherical protruding goggles or white bubbles. Professional fast mercenary, vigilant and guarded, head subtly cocked as if calculating an escape, one shoulder forward. No mouth/nose/skin invented. His teal scarf dissolves into forceful diagonal dry-brush strokes, keeping hood silhouette exactly his reference. No hands or shuriken in the portrait, do not introduce new weapons.

### Final correction prompt

Edit this newly painted ShadowClash shin portrait. Preserve the fighter design, exact colors, face, pose and thick expressive SHODO ink brushwork. FIX ONLY DELIVERY AND MARGINS: replace EVERY checkerboard square with one uniform warm ivory paper-color background #eee7d8. This is an intentionally OPAQUE portrait card, not a transparent sprite. The background must be completely continuous, solid color, NO pattern, NO checker, NO grid, NO box, NO border or lettering, NO card outline. Do not remove any of the fighter's white eyes or dark ink. Fit the full portrait inside the square with generous 7% warm ivory margin on all four sides, including the tips of horns, scarf and lower shoulder brushstrokes. Taper the strokes before they hit the canvas edge. The figure is painted directly onto the unframed ivory field. One image, one bust, no text.

## ember

Identity reference: /Users/anthonyguy/SHADOWCLASH.1.0*2/art/production/ember/idle-v3/frame-01.png

Generated original: /Users/anthonyguy/.codex/generated_images/01a060c4-5fe0-7622-a916-27296479a681/exec-a2fd174d-a60b-4fb5-b2e1-e3c979c22151.png

### Generation prompt

Create ONE BRAND-NEW head-and-shoulders character portrait for ShadowClash's character-select card and small fight HUD face icon. The attached image is ONLY an authoritative CHARACTER IDENTITY reference, not output to crop, trace, or reuse. Draw an entirely new composition. Preserve this fighter's exact established costume, head shape, face/mask type, accent colors and stylized semi-chibi character identity.

ART DIRECTION: very heavy traditional Japanese SHODO / sumi-e calligraphic ink painting. Thick, expressive, messy BLACK brush strokes with dramatic pressure variation, rough split-bristle edges, ink pooling, ragged dry-brush breakup and sharp tapered ends. This must unmistakably read as handmade brush painting, not clean digital anime outlines, not 3D, not photorealism. Broad black shapes, controlled colored ink washes only in the fighter's established accent colors. Cinematic restrained lighting, crisp readable facial landmarks, strong character presence.

COMPOSITION: square 1024x1024. Exactly ONE fighter, no panels or extra poses. Tight bust portrait from upper chest up, head centered, mild three-quarter turn toward viewer-left with readable face; entire hood/hair/horns visible within 8% safe margins. Face large enough to read as a 64px HUD icon. Shoulders and scarf terminate in natural tapered dry-brush strokes INSIDE the canvas, never a straight crop. No hands in this bust. No flying weapons. Distinct silhouette, deliberate negative space.

DELIVERY: Intentionally OPAQUE full square UI card image with uniform warm ivory background #eee7d8, absolutely NO checkerboard, no transparency simulation, no grid, no gradient, no border or rectangle frame, no writing, captions, signature, stamp, seal or logo. Paint the bust directly on the ivory field. Generous margin around entire bust; shoulder and scarf brushstrokes fade/taper onto the ivory before reaching edges. All actual white character details remain white.

EMBER, MALE: exact reference grey/charcoal hood with scalloped pointed silhouette and STITCHED hood rim, featureless black face and flat glowing WHITE eyes; layered dark grey scarf and black/grey cloth garb. Monochrome black, charcoal, ash, white ONLY: no invented fire, orange or green hood. No horns, no human nose/mouth/skin, no big bubble eyes. Defiant prodigy/outcast, feral confidence without a beast face; head leaned slightly forward, narrowed hunting gaze, diagonal energy through the neck and shoulder, entirely human ninja anatomy beneath hood. Thickest violent dry-brush strokes in hood, intense controlled black ink ragging in scarf and shoulders, but face crisp. Claws and hands cropped out rather than invented.

## mokurai

Identity reference: /Users/anthonyguy/SHADOWCLASH.1.0*2/art/production/mokurai/mokurai-shodo-locked-model-360-8v-v4-frontal-buddha-mask-strong-shodo-review.png

Generated original: /Users/anthonyguy/.codex/generated_images/01a060c4-5fe0-7622-a916-27296479a681/exec-5717763f-9f31-48af-bee5-da288044d2b4.png

### Generation prompt

Create ONE BRAND-NEW head-and-shoulders character portrait for ShadowClash's character-select card and small fight HUD face icon. The attached image is ONLY an authoritative CHARACTER IDENTITY reference, not output to crop, trace, or reuse. Draw an entirely new composition. Preserve this fighter's exact established costume, head shape, face/mask type, accent colors and stylized semi-chibi character identity.

ART DIRECTION: very heavy traditional Japanese SHODO / sumi-e calligraphic ink painting. Thick, expressive, messy BLACK brush strokes with dramatic pressure variation, rough split-bristle edges, ink pooling, ragged dry-brush breakup and sharp tapered ends. This must unmistakably read as handmade brush painting, not clean digital anime outlines, not 3D, not photorealism. Broad black shapes, controlled colored ink washes only in the fighter's established accent colors. Cinematic restrained lighting, crisp readable facial landmarks, strong character presence.

COMPOSITION: square 1024x1024. Exactly ONE fighter, no panels or extra poses. Tight bust portrait from upper chest up, head centered, mild three-quarter turn toward viewer-left with readable face; entire hood/hair/horns visible within 8% safe margins. Face large enough to read as a 64px HUD icon. Shoulders and scarf terminate in natural tapered dry-brush strokes INSIDE the canvas, never a straight crop. No hands in this bust. No flying weapons. Distinct silhouette, deliberate negative space.

DELIVERY: Intentionally OPAQUE full square UI card image with uniform warm ivory background #eee7d8, absolutely NO checkerboard, no transparency simulation, no grid, no gradient, no border or rectangle frame, no writing, captions, signature, stamp, seal or logo. Paint the bust directly on the ivory field. Generous margin around entire bust; shoulder and scarf brushstrokes fade/taper onto the ivory before reaching edges. All actual white character details remain white.

MOKURAI: use the attached approved reference for his exact design. Bald tan scalp, strapped-on cracked GREY STONE BUDDHA FACEPLATE, serene carved facial features with narrow nearly closed eyes, distinct RED OVAL jewel at the forehead; elongated ears with simple gold hoops. NO HOOD, no horns, no human fleshy face replacing the mask. Large BLACK ROUND PRAYER BEADS around neck, muted saffron/ochre sleeveless monk robe over black sleeves and torn rust/maroon scarf. New near-frontal bust with only a very slight viewer-left turn, upright quiet compassionate presence, grave stillness, saintly mercy worn by suffering. Strong heavy calligraphic contours, pale grey stone mask with controlled dry-brush cracks not holes, very slight gold light in eye slits if visible. Retain the serene mask. No arms/hands or attack effects. Do not copy the model sheet paper border or ground.

## exile — rejected original; superseded by eye-wrap correction below

Identity reference: /Users/anthonyguy/SHADOWCLASH.1.0*2/art/production/exile/exile-shodo-locked-model-360-8v-v4-no-eye-patch-semi-chibi-review.png

Generated original: /Users/anthonyguy/.codex/generated_images/01a060c4-5fe0-7622-a916-27296479a681/exec-f66babad-3a6e-4b4a-9b2b-98fe2df7145d.png

### Generation prompt

Create ONE BRAND-NEW head-and-shoulders character portrait for ShadowClash's character-select card and small fight HUD face icon. The attached image is ONLY an authoritative CHARACTER IDENTITY reference, not output to crop, trace, or reuse. Draw an entirely new composition. Preserve this fighter's exact established costume, head shape, face/mask type, accent colors and stylized semi-chibi character identity.

ART DIRECTION: very heavy traditional Japanese SHODO / sumi-e calligraphic ink painting. Thick, expressive, messy BLACK brush strokes with dramatic pressure variation, rough split-bristle edges, ink pooling, ragged dry-brush breakup and sharp tapered ends. This must unmistakably read as handmade brush painting, not clean digital anime outlines, not 3D, not photorealism. Broad black shapes, controlled colored ink washes only in the fighter's established accent colors. Cinematic restrained lighting, crisp readable facial landmarks, strong character presence.

COMPOSITION: square 1024x1024. Exactly ONE fighter, no panels or extra poses. Tight bust portrait from upper chest up, head centered, mild three-quarter turn toward viewer-left with readable face; entire hood/hair/horns visible within 8% safe margins. Face large enough to read as a 64px HUD icon. Shoulders and scarf terminate in natural tapered dry-brush strokes INSIDE the canvas, never a straight crop. No hands in this bust. No flying weapons. Distinct silhouette, deliberate negative space.

DELIVERY: Intentionally OPAQUE full square UI card image with uniform warm ivory background #eee7d8, absolutely NO checkerboard, no transparency simulation, no grid, no gradient, no border or rectangle frame, no writing, captions, signature, stamp, seal or logo. Paint the bust directly on the ivory field. Generous margin around entire bust; shoulder and scarf brushstrokes fade/taper onto the ivory before reaching edges. All actual white character details remain white.

EXILE: use the attached latest approved NO-EYEPATCH design. Female ninja with black swept-back hair and ONE broad white streak at the front, tan skin around BOTH clearly visible eyes, black lower-face cloth mask, faded red crest/mark centered on the tan forehead bandage/headband, purple scarf and black sleeveless gi with small restrained antique-gold fastenings. Current Story Bible eyes are RED, not brown: subtle crimson irises with normal human eye anatomy, not luminous void eyes. Keep her exact semi-chibi face shape, no eyepatch, no new armor, no hood, no horns. New cinematic upper-chest portrait, head turned slightly viewer-left but both eyes visible, steady thoughtful patient gaze, cool self-possession with a trace of longing, not a villainous grin. Hair and sash form controlled heavy black and purple calligraphic sweeps; large white streak immediately readable. Shoulders small enough that face/hair dominate. No weapon or hands, no chain crossing her. Fully show entire hair silhouette with margin.

## oni

Identity reference: /Users/anthonyguy/SHADOWCLASH.1.0*2/art/production/oni/oni-shodo-spectral-founder-locked-model-360-8v-v4-back-mounted-weapons-approved-review.png

Generated original: /Users/anthonyguy/.codex/generated_images/01a060c4-5fe0-7622-a916-27296479a681/exec-47e9aac3-6bd4-47a7-b42d-72c18d88ae62.png

### Generation prompt

Create ONE BRAND-NEW head-and-shoulders character portrait for ShadowClash's character-select card and small fight HUD face icon. The attached image is ONLY an authoritative CHARACTER IDENTITY reference, not output to crop, trace, or reuse. Draw an entirely new composition. Preserve this fighter's exact established costume, head shape, face/mask type, accent colors and stylized semi-chibi character identity.

ART DIRECTION: very heavy traditional Japanese SHODO / sumi-e calligraphic ink painting. Thick, expressive, messy BLACK brush strokes with dramatic pressure variation, rough split-bristle edges, ink pooling, ragged dry-brush breakup and sharp tapered ends. This must unmistakably read as handmade brush painting, not clean digital anime outlines, not 3D, not photorealism. Broad black shapes, controlled colored ink washes only in the fighter's established accent colors. Cinematic restrained lighting, crisp readable facial landmarks, strong character presence.

COMPOSITION: square 1024x1024. Exactly ONE fighter, no panels or extra poses. Tight bust portrait from upper chest up, head centered, mild three-quarter turn toward viewer-left with readable face; entire hood/hair/horns visible within 8% safe margins. Face large enough to read as a 64px HUD icon. Shoulders and scarf terminate in natural tapered dry-brush strokes INSIDE the canvas, never a straight crop. No hands in this bust. No flying weapons. Distinct silhouette, deliberate negative space.

DELIVERY: Intentionally OPAQUE full square UI card image with uniform warm ivory background #eee7d8, absolutely NO checkerboard, no transparency simulation, no grid, no gradient, no border or rectangle frame, no writing, captions, signature, stamp, seal or logo. Paint the bust directly on the ivory field. Generous margin around entire bust; shoulder and scarf brushstrokes fade/taper onto the ivory before reaching edges. All actual white character details remain white.

ONI: authoritative identity is the attached approved V4 reference, NOT any straw hat or old human redesign. White angular horned demon MASK with its exact black-and-red ornamental slash markings, two tall curved pale ivory horns, narrow glowing RED EYES in dark sockets, black tattered hood and layered black gunmetal shoulder armor, desaturated torn burgundy/rust mantle from the attached design. Face is a solid ceramic/ivory mask, not human or flesh, not a skull, no skeletal exposed teeth redesign. Back-mounted katana and bo may be omitted by this tight face-card crop, do not invent hand weapons. New nearly frontal, slightly viewer-left bust: silent ancient absolute certainty, chin level, monumental calm threat, NOT snarling or shouting. Two eye embers supply the strongest accent; keep weathered grey-white mask crisp inside heavy black dry-brush hood and armor. Tall horns entirely inside generous safe margin. No hands, no extra horns.

## Exile right-eye correction — 2026-09-04, approval pending

Anthony's latest correction overrides the v4 no-eye-patch reference mistakenly used above. Her anatomical RIGHT eye (viewer-left in this portrait) must be fully covered; only her left eye is visible. The approved v5 art shows warm ivory/tan cloth with a red brush marking. Its exact Japanese wording/meaning and the missing-eye backstory were not verified; do not invent them. The current Story Bible wording conflicts with the older identity lock and v5 visuals on the eye wrap, so follow the owner's explicit correction.

Authoritative visual reference: /Users/anthonyguy/SHADOWCLASH.1.0*2/art/production/exile/exile-shodo-locked-model-360-8v-v5-correct-right-eye-patch-review.png

Cross-check: /Users/anthonyguy/SHADOWCLASH.1.0*2/art/production/exile/exile-shodo-kusarigama-idle-8f-v5-safe-margin-approved-review.png

Identity lock: /Users/anthonyguy/OB-LOCAL_BRAIN/ShadowClash-Second-Brain/Exile-Identity-True-Lock.md

Generated original: /Users/anthonyguy/.codex/generated_images/01a060c4-5fe0-7622-a916-27296479a681/exec-87fc72ee-b27e-4df1-974a-a506a9ae84ff.png

Review copy: exile-eye-wrap-v2.png. Not installed until Anthony approves this revision. No change to her combat frames.

### Correction prompt

Use case: precise-object-edit.
Input 1 is the EDIT TARGET: the newly approved heavy-SHODO Exile bust portrait on ivory.
Input 2 is the AUTHORITATIVE EYE-WRAP REFERENCE: her approved v5 turnaround with the correct RIGHT-EYE CLOTH PATCH.

Change ONLY the missing cloth eye-wrap on the portrait in input 1. Preserve its exact portrait composition, bold messy black calligraphic brushwork, face shape, huge black hair with ONE white streak, black lower-face mask, purple scarf, clothing, same pose, same background and square format.
The owner correction: Exile has only ONE visible eye. Cover HER ANATOMICAL RIGHT EYE — the SMALLER EYE ON THE VIEWER'S LEFT in input 1 — completely with opaque cloth. Leave her anatomical LEFT eye, the LARGE EYE ON THE VIEWER'S RIGHT, visible and unchanged. Never cover both eyes, never swap sides, never make an uncovered second eye.
Match the broad diagonal, softly triangular cloth eye-wrap on the first two views of input 2: from the forehead down across the right eye to upper cheek, wraps around the side of her head. This is actual fabric with visible edges, slight creases and a soft aged warm ivory/tan with faint blush cast, NOT a black pirate patch, NOT glasses, NOT a strip just across the forehead. The eye beneath it must not remain visible.
Move the existing red forehead marking onto this eye-covering cloth to match the red brush-sigil shown in input 2. Preserve that reference's mark as a visual emblem, not invented new kanji or arbitrary Japanese writing. No duplicate mark remaining on exposed skin. The reference mark is the intended guide.
Do NOT change any other artwork. Keep the existing intentional opaque ivory card backdrop; no checkerboard, no transparency simulation, no frame, no border, no captions, no extra writing. One portrait.
