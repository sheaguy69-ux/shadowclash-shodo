# Roster combat body registration — 2026-09-07

`combatPose(p)` reads the current sprite resolver directly, independent of rendering. It registers source pixels using the existing uniform scale, renderScale, frameScale, footAdj, per-cell mirror and frameOffsetX. Run direction, reverse heel/wire and wall contact registration follow the renderer. The movement pushbox remains unchanged.

Legacy hurtboxes now cover the drawn body instead of the 48px movement box. A cached dense-ink head row rejects narrow staff tips above the head; median occupied x and 3–97% upper-body quantiles locate off-centre hoods/trunks without using the full weapon/scarf bounding box. Current pose head height is allowed above a low idle pose: the first implementation incorrectly capped Ember standing attacks to his crouched idle, and QA rejected it. Mizu idle75's reference hood begins at source y173 rather than staff-tip y149. Shin's canonical reference uses standing xidle1 rather than low ready idle.

`hurtbox()`, `hurtTopY()`, melee contact sparks and projectile impacts share the same geometry. Projectile circle–AABB contact uses radius4 (floor wave8); the existing wave grounded/roll restriction remains. Authored Executioner Footsies boxes and null vanish frames bypass legacy fitting unchanged. Damage invulnerability is still resolved by takeDamage.

## Verification

- `python3 tools/check_roster_hurtboxes.py`: nine fighters × two facings × five states; finite body bounds, sole registration, projectile head/tangent/outside/diagonal and above-crouch checks; Executioner null vanish on frames3/4. JSON: `media/roster-hurtboxes/checks.json`.
- `DEBUG_PORT=9393 python3 tools/check_footsies_physics.py`: existing authored-move/cancel/physics regression.
- Independent Ember hurtbox review: first candidate rejected5/10 for head clipping; second candidate passes7/10, including standing attack and low idle. Final whole-roster visual report is owned by the independent QA pass.

## Limits

This is a body-core AABB approximation, not a per-limb pixel mask. Extreme extended limbs, disconnected FX and thin weapon blades are deliberately outside the body hull. Tracked attack lunges and the legacy launch stretch are disabled so release/launch bodies keep uniform source registration. Existing landing and impact squash transforms are not included in this source registration. Those transforms can create minor contour differences. The generic crouch renderer target is honored for its fallback cells; authored crouch/roll poses keep their actual head height rather than a blanket percentage of an unrelated idle. Existing radius-targeted special abilities keep their declared range mechanics.

No artwork or damage/startup/recovery/cancel parameter is changed by this subtask. Actual contact reach and which visible regions can hit are deliberately changed; this is a gameplay calibration, not merely a debug overlay.

## Contact strike geometry

`refreshStrikeGeometry(p,h)` resolves tracked, active melee boxes before collision and weapon clash. It stamps the active pose window before reading the sprite, including the final active simulation tick. Source alpha in the intended front/back, low, up or down sector locates the visible tip; the contact rectangle extends from the near strike region to that tip with a two-world-pixel contour allowance. Geometry is cached per source cell/direction and transformed through `combatPose`. Authored Footsies frames, echo/gap attacks, explicit iaijutsu corridor and live simulated chains keep their dedicated geometry. The capture exporter invokes the identical eligible resolver before collecting collision probes.

Independent Shin forward-Light right-facing review passes7/10: active F5–12 red covers extended foot and impact cell246; F13 recovery has no red. The dense-head approximation was also rejected on Kael/Mizu overhead baked arcs. QA supplied explicit source head/core landmarks for Kael207/236 and Mizu168/170/172; these now override automatic body fitting and preserve foot corrections. Additional arc-heavy poses may need equivalent landmarks.

The runnable hurtbox check also exercises8fighters ×2facings ×4ground attack requests, checks actual fitted cells and unchanged damage/duration, and verifies the final-active stamp. These are geometry checks, not a replacement for the final full-roster visual score.

Final candidate QA rejected the width-based exemption: Mizu's165px staff poke is ordinary melee. The exemption is now an explicit corridor flag only on Exile's existing full-arena iaijutsu call. Mizu source113 uses reviewed foot-only region155,229–202,253 (excluding the raised staff); source193 uses staff25,217–139,237. Ember source150 uses claw186,280–228,301 (excluding the aligned forward leg). These overrides follow the same source-to-world facing transform and two-pixel contact allowance.

Exile HELI SPIN keeps two distinct attacks: the source394 front chain region and the existing simulated iron ball behind. The rear hitbox follows `chain.pts.at(-1)` at the same8.2px outer radius drawn by `Player._paint`. It becomes inactive while the ball is in front or absent. Melee, clash and exporter eligibility all honor that flag, while its normal lifetime still expires. Both-facing checks put a victim inside the inactive box and verify no damage, then verify expiration. Oni527/528/584 use QA claw-only regions rather than a vertical union of hands and aligned legs.
