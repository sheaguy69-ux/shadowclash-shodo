# Shodo frame continuity — owner correction, 2026-09-06

Every new character frame stays in the game's established Shodo art style. Before generating, study that fighter's CURRENT approved idle, run, jump and recovery frames together. Match their existing body proportions, hood/head size, limbs, costume, weapon and inkwork. “Chibi-like” does not authorize a smaller body, enlarged baby head, stubby redesign or adult proportions with long ankles. Anthony rejected both extremes in the September 6 jump concepts.

Use heavy, uneven calligraphic black contours, pressure variation, bristle edges and controlled ink-wash shading as visible in the approved game art. Preserve each fighter's own palette and silhouette. Comic-specific faces, pupils and body ratios do not replace the game's masked characters.

The new sequence must connect to the current pose entering it and the pose following it. Design adjacent limb, weapon and scarf positions as one continuous motion, not six independent illustrations. Keep one body scale across the sequence, calibrated against that fighter's existing frames; a tuck changes the pose envelope, not the head or limb lengths. Never normalize each rotating bounding box to the same height. Keep ground contact art out of flight.

Inspect source and runtime-size contact sheets, all twelve QC dimensions, both facing directions and consecutive live-loop transitions before calling frames integrated. Use the existing shared drawShodoFrame renderer for the body and all copies. No extra runtime stretching or duplicate style renderer.

References read: the Second Brain's `05 - Animation and Art Bible.md`, `17 - Sprite Animation Director Prompt.md`, fighter sections of `shadowclash-story-bible.md`, and this repo's `GPT-HANDOFF-REFERENCE-DISCIPLINE-2026-09-02.md` and `superpowers/specs/2026-08-31-shodo-roster-motion.md`. Current owner instructions supersede stale proportions, weapon counts and approval gates in those documents. Ember now has three main blades on each gauntlet and no thumb blade.

## Owner clarification —2026-09-07: preserve design, correct finish

Anthony loves Oni’s wall-projectile design and poses but requires the finish to stay true to Japanese Shodo and the rest of the game. Preserve the approved design; favor pressure-varied brush contours and controlled ink-wash shapes over dense granular/etched surface detail. This is a finish correction, not permission to redesign proportions or equipment.

## Owner correction —2026-09-08: Mokurai's legs

Anthony rejected the replacement run396–403 because its legs were too skinny. Preserve his original short, substantial legs and full gathered charcoal trousers: broad thighs, rounded knees and calf fabric, heavy folds, wide cuffs and brass ankle wraps, and original bare-foot size. Correcting leg exchange does not authorize narrow jogger-like calves or longer shins. Compare the entire lower-body construction with original run281–288 at equal head size; matching only the mask/head cannot establish character proportion consistency.

## Owner clarification —2026-09-09: readable weapons

Anthony permits removing heavy dark weapon outlines because they obscure the weapons. Blades and other weapons may use lighter or omitted dark contours so their shape and material remain readable at gameplay size; do not add the character's thick contour over a thin weapon. This weapon-specific direction supersedes older blanket outline requirements. Preserve the established Shodo ink treatment on the character's body. Judge weapon readability in consecutive native-size frames, including the blade and its motion trail together.

## Owner corrections —2026-09-11: contrasting effects and no cast shadows

Motion trails and action special effects must contrast with the fighter's costume. Use white and pale yellow accents, preserving the character's approved palette and Shodo finish. This specific owner correction supersedes older prohibitions on recoloring attack effects. Inspect baked sprite effects as well as runtime effects.

Remove all character cast/contact shadows, on the ground and in the air. Preserve Claude's deletion of the shared contact ellipse; never restore it from an older art candidate. New airborne drawings contain no underfoot shadow or ground marks. Landing impact bursts are action effects and use the contrasting palette. These corrections do not change combat timing or collision geometry.
