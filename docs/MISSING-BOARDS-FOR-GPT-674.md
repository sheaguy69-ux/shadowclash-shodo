# Boards still owed — hand this to the generator (SHEET_V 674)

Every row below has a LIVE engine route that currently falls back to another row's art.
Everything else in the game draws a production board. Boards marked **approve** already
exist in `art/production/<fighter>/` as a `-review` take — they need Anthony's approval
(rename/copy to `-approved-review`) or a regeneration, not a new design.

## Format for every new board (the house spec)

- ONE row of 8 frames, equal-width cards, ~1900–2000px wide total, on washi/parchment.
- Side profile, **figure faces LEFT**, same figure scale as that fighter's idle board
  (match head size to the idle board, not the canvas).
- Feet on one consistent ground line; grounded poses never float.
- NO drawn card borders needed, NO drawn walls, floors, or props that the stage already
  provides. FX (slashes, bursts, trails) belong to the move and are welcome.
- Cel beats, not a cross-fade: each frame is a distinct pose in reading order
  (anticipation → action → contact → follow-through → recover).

## Oni — Spectral Founder

1. **Air light attack** (neutral air, staff or spear-hand swipe mid-air) — air Lights
   currently draw his grounded iai-fang row.
2. **Wall-cling + needle-throw REDRAW with NO drawn wall** — the current approved board
   bakes the wall stroke into every card; it had to be machine-erased and edges remain.
   Same beats: cling hold → reach → three-needle toss → settle. Transparent behind him.

## Executioner

3. **Crouch** (8f: sink → held low guard breathing) — he has NO crouch art at all; he
   currently "ducks" in his idle pose.
4. **Air heavy** (falling overhead katana strike) — air Heavies draw the grounded
   gallows-crescent.

## Exile

5. **Crouch** — approve `exile-shodo-kusarigama-crouch-8f-v1-review` or regen.
6. **Airborne hit reaction / thrown tumble** (8f loose tumble, chain flailing).
7. **Air light** (aerial sickle slash).
8. **Launcher** — approve `exile-shodo-gallows-hook-rising-reap-launcher-8f-v1-review`.
9. **Back-special** — approve `grave-chain-reversal-parry-counter` or
   `gravehound-chain-pursuit` (pick which is her back+Special; both are -review).

## Kael

10. **Down-air cleave** — approve `kael-shodo-falling-star-cleave-down-air-8f-v1-review`.
11. **Neutral air special** — approve `kael-shodo-sky-fang-cross-neutral-air-8f-v2-arm-corrected-review`.

## Tsubasa

12. **Fwd heavy rush** (the `rgrush` route: dashing twin-knife pierce, 8f).
13. **Down+Light low sweep** (fast ankle cut).
14. **Dive cut** (down air special — her canon plunging cut; engine route exists).
15. **Air throw** (up special route reads it; grab-and-drop mid-air, 8f).

## Ember

16. **Blade-trap parry** (the `eparry` route: hunch guard → catch flash → X-shred →
    recover; engine has a dedicated 5-beat read).

## Mizu

17. **Neutral HEAVY bo swing** — her biggest gap: every Heavy currently draws the light
    thrust row. One committed two-handed bo strike, 8f.
18. **Rising staff anti-air** (`ristaff`, up+Heavy route).
19. **Low staff drive** (`bolow`, down+Heavy route).
20. **Vaulting staff slam** (`gsup` row, up+Special — pole-vault over, drive down).
21. **Airborne hit reaction / thrown tumble.**

## Mokurai

22. **Bell-ringer** (`mbell`, up+Heavy: both fists swing skyward).
23. **Palm blast** (`mblast`, back+Heavy: braced rear palm shove).
24. **Airborne hit reaction / thrown tumble.**
25. **Wall cling** (`mwall`: catch + slide, bare-handed).

## Shin (all four exist as -review takes — approve or regen)

26. **Neutral heavy** — `shin-shodo-stone-splitting-palm-heavy-8f-v1-review`.
27. **Launcher** — `shin-shodo-bamboo-splitter-rising-knee-launcher-8f-v2-one-eye-corrected-review`.
28. **Parry stance** — `shin-shodo-shadow-thread-reversal-parry-counter-8f-v2-frame4-restored-review`.
29. **Super** — `shin-shodo-silent-canopy-falling-star-burial-super-8f-v1-review`.

## Parked for a routing decision (art exists, engine has no slot)

- Ember `war-wraith-rake-standing-medium`, Mokurai `golden-temple-bell-elbow-standing-medium`,
  Exile `grave-chain-knuckle-standing-medium`, Tsubasa `scarlet-shear-standing-medium` —
  the engine has no "standing medium" tier; say where these should land.
- Guard-break boards (exec/kael/tsubasa/ember/shin/oni) — no guard-break reaction route.
- Mokurai boss specials + boss super, everyone's defeat-KO / intro / taunt / victory —
  no engine routes yet.
