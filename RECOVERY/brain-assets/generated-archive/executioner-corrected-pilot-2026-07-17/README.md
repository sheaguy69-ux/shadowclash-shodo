# Executioner Corrected-Art Pilot — Review Handoff

Date: 2026-07-17

Status: **REJECTED FOR RUNTIME PACKING**

## Locked owner source

- Corrected six-character lineup: `original-six-owner-corrected-lineup.png`
- Isolated identity input: `executioner-owner-corrected-ref.png`
- Tsubasa remains hoodless with visible spiky black/red hair and exactly two small knives.
- Kael remains equipped with two equal-length long swords.

## Pilot result

The corrected Executioner reference produced a readable horned dark-purple identity and energetic full-body motion. The Kling clip did not satisfy production constraints:

- camera-facing angle drifts instead of holding a stable fighting-game profile;
- sword length and on-canvas continuity vary between frames;
- several transition frames smear or temporarily duplicate the blade;
- body scale and silhouette shift enough to create sprite jitter.

The filmstrips and source clip are retained as review evidence only. No generated frame was packed into `web/assets/sprites/executioner.png`; the manifest and `SHEET_V` were not changed.

## Next production action

Use a structure-controlled frame-by-frame or pose-conditioned pipeline that preserves the existing runtime silhouette and weapon path. Require a clean five-frame contact sheet and live-motion review before any sheet packing.
