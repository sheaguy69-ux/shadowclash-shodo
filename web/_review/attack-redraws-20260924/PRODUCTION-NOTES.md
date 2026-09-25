# Attack redraws — first art pass

## Source and scope

The images in this gallery are exact owner-selected key-pose studies, not packed cells. Built-in image editor model identity was not verified; do not call these GPT Image 2.5 outputs. No paid external API was used. Source art stays unchanged.

| New study | Current route to replace after full animation review | Required next drawings |
| --- | --- | --- |
| Executioner heavy, `executioner-heavy-three-keys-approved.png` | `xjodan1..6` live; source cells `xjodan7/8` exist but are not played | Breakdown between raised blade and contact; measured blade-tip arc; recovery to approved idle; preserve exact long sword length and one shoulder pad |
| Executioner shoulder bump, `executioner-shoulder-bump-three-keys-approved.png` | `xbump1..8`, Dash + Light, 320 ms move | Pad-first impact construction, foot support and travel spacing, recovery; sheathed sword throughout; both facings |
| Kael long/short contact, `kael-niten-contact-white-eyes-approved.png` | `kcross1..8`; positions 2/3 and 6/7 currently reuse source cells | Preserve the owner-approved normal white eye area with dark pupil; distinct anticipation, independent long/short blade breakdowns, separate tip tracks, long-sword reach, short-sword cover, follow-through and recovery |

Kael's grounded light `kdual1..8` is the next separate redraw: the **short blade** leads that light action. The current brief and source strips are in `../sword-swing-motion-20260924/`. Anthony approved Kael's one-long/one-short contact-pose direction and the exact white-eye correction image. The earlier amber-eye image is retained only as edit provenance and is not the current character look.

## Continuity gates before installation

1. Draw missing breakdowns and in-betweens. A storyboard with three poses is not a continuous animation.
2. Register pelvis, planted foot, hood, shoulder pad, waist armor and sword hands against neighboring drawings. Keep intentional body compression and reach.
3. Trace the actual blade tips; show clean substantial white tails behind the moving long blade, rather than letting FX substitute for sword travel. For Kael, trace each blade separately and prevent intersections.
4. Inspect at actual sprite size and normal playback speed, left and mirrored right, including center and wall positions. Repair popping, foot slide, blade length drift, and incorrect pad-side contact.
5. Present the complete strips and playback to Anthony before any sprite-sheet or combat change. Existing hitboxes and attack timing remain untouched in this pass.

`frame_breakdown.json` contains staging intent for the displayed keys, not a claim that production frames or animation timing have been authored.
