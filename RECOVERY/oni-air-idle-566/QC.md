# Oni air-idle correction — SHEET_V 566

## Owner selection

- Visual reference: `/Users/anthonyguy/Desktop/Screenshot 2026-08-19 at 10.32.42 AM.png`
- The selected tuck is already packed at full source quality as Oni `aback2`, cell 390, from the owner's corrected eight-frame Back+Light board.
- `airidle` aliases that existing cell. No pixels were duplicated or modified.

## Routing correction

- Airborne attack recovery now settles through `idleFrame(p, F)`, choosing a sheet-provided `airidle` instead of grounded `idle`.
- An airborne state that clears to `IDLE` cannot enter Oni's `stand1..6` ground loop.
- Oni's non-attacking apex band (`-120 <= vy < 120`) uses cell 390. Authored launch, directional acrobatics, fall, attacks, and grounded idle remain intact.
- The normal `drawSprite -> drawShodoFrame` path renders the cell; no raw-draw bypass was added.

## Verification

- `python3 tools/check_oni_air_idle.py --url http://127.0.0.1:9101/index.html`
  - neutral apex = 390
  - airborne `IDLE` = 390
  - airborne Light/Heavy/Special recovery settle = 390
  - grounded idle remains `stand1`/cell 0 at phase 0
  - authored launch remains a jump cell
  - shared Shodo call receives cell 390
- Real-input capture (`live-v3/log.txt`): air cells include 390, five air-idle samples, zero airborne ground-idle-cell-0 samples, Back+Light remains `attackDir: back`, and the page reports no errors.
- `check_oni_aerial_back_turn.py`: pass in both midair turn directions.
- `check_oni_shadow_dash.py`: all eight dash cells route; 5,712 Shodo contour pixels and 342 red-FX edge-ink pixels measured.
- `check_oni_moves6.py`: all six Oni move boards still route, including Back+Light 389..396 in order.
- `check_it_actually_plays.py`: full Executioner-vs-Oni match lands hits, reaches KO, advances the round, and throws no page errors.

## Evidence

- Focused live still: `live-air-idle.png`
- Full live capture and log: `live-v3/`
