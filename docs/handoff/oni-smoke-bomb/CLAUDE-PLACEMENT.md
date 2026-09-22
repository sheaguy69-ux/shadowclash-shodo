# Oni Smoke Bomb — Claude placement handoff

Purpose: visually sell Oni's existing smoke-bomb field: a floor-anchored charcoal concealment cloud whose existing damage tick can be blocked or dodged. This is an art handoff only; do not change gameplay.

## Assets

- `frames/oni-smoke-bomb-01.png` through `08.png`
- Every frame is 512×512 with an exact `#FFFFFF` background.
- Shared pivot in every frame: **(256, 440)**, measured from the top-left.
- Contact sheet order is 4×2, left-to-right, top row then bottom row.

## Frame use

| Frame | Use |
|---|---|
| 01 | Bomb contacts the floor; smallest anticipation beat. |
| 02 | Shell ruptures into the first sharp smoke burst. |
| 03 | Fast vertical and lateral eruption. |
| 04 | Rapid expansion into concealment. |
| 05 | Stable full cloud; use as the persistent hold frame. |
| 06 | Red inner "bite" flash; briefly show on the existing 0.45 s smoke damage tick, then return to 05. Do not create a new gameplay tick. |
| 07 | Field breaks into separated curls when its duration ends. |
| 08 | Final low wisps; remove the visual after this frame. |

## Placement and timing

1. Trigger frame 01 when the existing `kind: 'smokebomb'` field is created.
2. Play 01→05 once in about 0.35 s: **80, 60, 50, 60, 100 ms**.
3. Hold frame 05 for the existing field lifetime. Flash frame 06 for about **90 ms** whenever the existing smoke tick fires, then return to 05.
4. When the field expires, play 07 for **100 ms**, then 08 for **140 ms**, then remove the sprite.
5. Place the shared pivot **(256, 440)** at **(field.x, GROUND_Y)**. Do not recenter individual frames.
6. Use one constant scale for the whole sequence. Size it so frame 05's cloud width equals `field.radius * 2` (currently 480 px). Never fit each frame separately.
7. Draw on the current smoke-screen layer after fighters, so the cloud visibly conceals them. Keep existing slashes above it.

## Guardrails

- Reuse the existing smoke field. Do not add another field, hitbox, blind, timer, or counter.
- Do not change the current 240 radius, 4.0 s lifetime, 0.45 s tick, or two-use-per-round cap.
- White is only the crop/key background; convert it to transparency during asset import.
- Keep the smoke charcoal. The tiny red lines belong only to frame 06 and signal Oni's existing damage tick.
