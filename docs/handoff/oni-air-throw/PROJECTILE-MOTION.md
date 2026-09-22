# Oni projectile-motion keyframe — Claude handoff

Current owner direction: duplicate the supplied airborne Oni key cel and animate the projectile travel. This replaces the standing/staff-volley direction for this art request; do not combine the two concepts.

## Assets

- `frames/oni-projectile-motion-01.png` through `06.png`
- Every frame is 512×512 on exact `#FFFFFF`.
- Contact-sheet order is 3×2, left-to-right, top row then bottom row.
- `keyframe-reference.png` is the owner-supplied source reference.

## Playback

| Frame | Visual beat | Exposure |
|---|---|---:|
| 01 | Projectiles gathered at the throwing claw | 50 ms |
| 02 | Release; blades clear the hand | 50 ms |
| 03 | Early staggered flight | 50 ms |
| 04 | Mid-flight | 60 ms |
| 05 | Late flight with longest streaks | 70 ms |
| 06 | Compact projectile impact | 100 ms |

## Placement rules

1. Use each complete 512×512 frame at the same origin. The airborne fighter is deliberately held in one registered position.
2. Do **not** trim, center, or anchor from the changing projectile bounds; that will make Oni slide.
3. The fighter and projectiles are already composited together. Do not stack another Oni cel or additional projectile sprites over them.
4. Frames 01→06 play once in about 380 ms. Frame 06 does not loop.
5. The frame-06 impact burst is authored visual timing only. Do not change damage, range, hitboxes, meter cost, or move state from this art handoff.
6. Key out only the exact white background during import. Preserve the pale mask and wrap highlights.
