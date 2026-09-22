# Oni throwing-arm motion — Claude handoff

Current owner direction: animate Oni's **body throwing motion**, not projectile travel. This supersedes the earlier `oni-projectile-motion-keyframe` sequence for this request.

## Assets

- `frames/oni-throwing-arm-01.png` through `06.png`
- Six 512×512 frames on exact `#FFFFFF`
- Contact-sheet order: 3×2, left-to-right, top row then bottom row
- No projectile is drawn in any frame

## Playback

| Frame | Body beat | Exposure |
|---|---|---:|
| 01 | Right throwing arm pulled far back | 70 ms |
| 02 | Maximum coil; elbow begins leading | 60 ms |
| 03 | Shoulder and forearm accelerate forward | 50 ms |
| 04 | Forward/downward release | 50 ms |
| 05 | Full follow-through | 70 ms |
| 06 | Arm and shoulders recover | 80 ms |

## Placement rules

1. Play 01→06 once in about 380 ms.
2. Use every complete 512×512 cell at the same origin. Registration is based on Oni's mask/torso, not the changing arm bounds.
3. Do not trim or recenter individual frames.
4. These are character-motion frames only. Do not interpret the red hand arcs as projectiles.
5. Projectiles, hitboxes, damage, range, meter, and move state are outside this art handoff and must not be changed from it.
6. Key out only the exact white background during import; preserve the white mask and pale wraps.
