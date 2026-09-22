# Footsies pipeline: independent Agent 2 audit

Scope: Executioner's owner-selected grounded Forward + Light, `ninja_shadow_slice`, grounded Forward + Special, `smoke_bomb_shadow_strike`, and the frame JSON / visual QA workflow. Review is not a pass for every pre-existing roster animation.

## Reference inspection

Current Executioner source cells 262–267 (`xnuki1`–`xnuki6`) provide ready, coil, draw, arc, arm extension, and follow-through poses. Reviewed the actual sheet against its 388×496 cell geometry, footY 488, and manifest scale. Cell 265's prominent arc sits behind the left-facing body; cell 266 has an extended arm but the live view does not show a useful forward sword. The final revision therefore uses `xtsuki1/2/3` (329/296/297) for chamber, actual sword contact and recovery, retaining the existing source-facing flags. Added exposures are not newly drawn in-betweens.

Final nine exposures: **263, 329, 296, 296, 297, 297, 263, 262, 262**. Smoke uses **262, 211, hidden, hidden, 263, 329, 296, 296, 296, 297, 297, 263, 262, 262, 262, 262**. Requested visual annotations remain distinguishable from what the existing drawing actually depicts.

## Required acceptance checks

- Actual runtime phase boundaries: startup 1–2, active 3–4, recovery 5–9; no startup/recovery collision.
- One clean damage event, exact documented damage/stun/vector units, and correctly mirrored collision rectangles.
- Hit-only smoke-dash, special, and jump cancels on original move frames 3–5; no permission from a whiff or blocked strike.
- Cancellation/interruption clears scheduled hitboxes and effects. Existing alternate attack routes remain intact.
- Export derives source cell, world boxes, timing, velocity and contacts from the actual runtime. A 60 Hz sample is not proof of a fixed-step engine.
- Consecutive live-loop frames show the active red rectangle over the strike, green hull over the body, consistent body scale/feet, and a readable recovery without adding startup delay.

## Legacy animation scope

The reviewed approved-source run boards remain separate work: Oni 660/661 provide only opposite contacts (missing down, passing, and up drawings on both legs); Shin 277–284 contains a diving cell 279, tucked cell 281 at the opposite-contact position, and crouched 284→277 seam. Neither receives a new fluidity pass from this pipeline implementation. Existing Shin held crouch remains subject to the owner's explicit no-squish ruling.

## Final result

**7/10 — PASS for the two implemented moves and their export/audit workflow.** This supersedes the rejected iterations below. The pasted specification's 9.7 rating was not treated as evidence.

The final batch captured 12 cases: two moves × both facings × hit, block and whiff, totaling **180 consecutive simulation/render samples**. Every case used source SHA256 `ddc61bd552c90eb33f3aef328fc50ead3116eac03aa41029ab9b32d3a0f3f20f`. Source changes during two earlier attempts correctly rejected those captures rather than mixing evidence. Independent checks confirmed all authored frame indices, exact active windows, free movement at frame 10/17, one contact on each hit/block case, no contact on whiffs, and absent smoke hurtboxes only on frames 3–4.

Representative native-size scene and collision films were visually inspected in both directions, including blocked Light, Smoke hit/cross-up and Smoke whiff. The approved crescent effect now spans the supplied disjoint red rectangle on active frames only. Body drawing scale stays fixed, stance compression comes from the drawing, and the attacker no longer leaves recovery afterimages. The smoke sequence disappears on 3–4 and reappears before contact. Its clear pause/strike/recovery transitions earn a pass, without claiming newly drawn hand signs or physically perfect limb silhouettes.

| Measured contact against Mizu | Light | Smoke special |
|---|---:|---:|
| First contact frame | 3 | 7 |
| Base damage / actual HP loss | 28 / 20.188 | 55 / 39.655 |
| Hitstun | 14/60 game-seconds | 22/60 game-seconds |
| Unmodified grounded target vector | ±350, 0 px/game-second | ∓500, −400 px/game-second after cross-up |
| Block result | Existing chip/guard behavior | 12/60 game-seconds blockstun |

Existing defense/health scaling accounts for actual HP loss; raw damage values are not a promise of flat HP loss. Export contact vectors are recorded immediately inside `takeDamage`, before subsequent movement/friction changes. Direct game-time sampling bypasses cinematic hitstop crawl and is not proof of a fixed-step runtime.

Evidence: `media/footsies/qa-final/{light,special}-{left,right}-{hit,block,whiff}/` contains `frame_breakdown.json`, `filmstrip.png` (red collision / green hurt hull), and `scene-filmstrip.png` (actual game FX and rendering). The reusable capture command is `python3 tools/export_footsies_frames.py --move special --frames 18 --scenario hit --out media/footsies/recheck`.

Remaining limitations keep the score below 9: the smoke burst is a small floor puff rather than a body-covering cloud; no literal hand-sign/pellet drawing was added; recovery hulls of 70/80 author units intentionally extend above the unchanged ready art; generic roster hurtboxes remain simplified legacy rectangles. These limitations are explicit and do not receive a roster-wide accuracy or art-expansion pass.

## Rejection / resubmission log

Initial exporter implementation: **6/10, rejected**. It sampled 1.2 authored frames per output row and omitted the initial frame, so the requested nine-frame sequence could not be audited faithfully; pressed Slash instead of the real P2 guard KeyM; used the legacy hull rather than the frame-aware hull; and treated every zero-delay box as active even on frame-gated startup/recovery. These are timing/box-reporting defects, not additional authored sprite drawings.

Required corrections were implemented in the exporter: input-entry frame plus one game-time frame per sample, actual nullable `hurtbox()`, explicit contract phase and collision eligibility, aged real guard input, per-contact damage/stun/vector records, unchanged-source hash check, and separate actual-scene and collision-overlay filmstrips.

First live move submission: **6/10, rejected**. Both authored green hulls sat at the ankles because 65 author units were scaled to the legacy 48-pixel collider instead of the roughly 126-pixel displayed ready body. Active cell 266 did not show an exposed forward sword. Light retained an extra recovery sample at frame 10, special at frame 17. Smoke recovery retained multiple speed afterimages. Exact corrections requested: fixed ready-cell scale for authored boxes, sword contact cell 296 / chamber 329 / recovery 297, clock-based expiration at 9/16 frames, and no residual speed ghosts for these authored sequences.

Second live submission: body hulls, actual sword pose and frame-10 release improved, but **6/10, rejected for remaining phantom reach**. `qa-light-right-whiff-v2/filmstrip.png` active frames 3–4 showed a roughly 97-pixel-wide red rectangle extending approximately 66 pixels beyond the visible sword arc. Requested correction: adapt collision bounds to the measured strike or provide a reviewed strike effect reaching the specified disjoint boundary; do not enlarge/distort the character to fill a collision box.

Final resubmission retained the specified reach and filled it with the existing approved crescent effect, positioned by the same world rectangle as collision. The frame-7–9 Smoke effect follows its changing widths and facing. No sprite sheet or character scale was altered to fill the gap. The final evidence above resolves the rejection and earns **7/10 PASS**.
