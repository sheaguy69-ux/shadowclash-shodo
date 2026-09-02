# Session handoff — 2026-09-02, SHEET_V 690

Tree `SHODO-EDITION` · branch `shodo-edition` · HEAD `ecfc68f` · served on `:9101` ·
**nothing pushed, 12 local commits after `05945ae`.**

---

## Start here

```bash
python3 tools/lane.py start "your name"   # several agents share this tree
python3 tools/lane.py who
python3 tools/serve.py 9101 web
curl -s localhost:9101/whoami             # MUST say SHODO-EDITION before you trust the screen
node tools/check_gamepad_mapping.mjs      # 54 assertions, no browser, no server
node tools/kinetics_check.mjs             # ALL PASS
node tools/check_zero_legacy.mjs          # hard checks pass; orphans are expected
```

`tools/check_story_cutscene.mjs` **cannot run on this machine** — it hardcodes port 9100
(the other edition, never to be touched) and needs a Chrome remote-debugging port that is
dead here. The cutscene path was verified by hand in the Browser pane instead.

## Laws that cost something to learn

1. **Sheets are append-only.** Append the new cell, repoint the key, leave the old cell an
   orphan, strip orphans in a *separate later pass*. Original cells byte-identical.
   `SHEET_V` bumps in the same commit as any `web/assets/sprites/*` change.
2. **File alpha lies** — the engine keys at draw time. Measure through
   `keyer_emu.keyed_cell` or your numbers describe a picture nobody sees.
3. **Sheets are ONE ROW**: cell `c` at `x = c*frameW`. No grid.
4. **Two rulers or none**: ink area vs the fighter's own idle, plus a rigid landmark that
   passed a known-answer check. Never bbox height, never per-cell flattening, one scale per row.
5. **Local commits only**; `LANE_AS="you" git commit` while another lane is open.
6. **No paid generation.** New art comes from the owner's own generator; this repo hands it
   measured references and checks what comes back.

## What landed (12 commits)

| SHEET_V | commit | what |
| --- | --- | --- |
| 684 | `9f6391c` | Exile Chain to the Wall on the engine's LIVE rope; rope roots in the drawn fist via `handAnchor`; kama painted at a bitten wall anchor |
| 685 | `95d455e` | Size campaign: 68 rows / 471 keys rescaled to each fighter's idle, one scale per row, 8 fighters |
| 686 | `447fcb8` | Ember's 7 AREA-derived rows; his eye-derived rows held (his eye validates itself) |
| 687 | `bc909d2` | exec `roll_` x1.226 (pose twin, no canvas growth needed), kael `krise` x1.246, tsubasa `jump1` repointed 25→69 |
| 688 | `341f5dd` | All four wall cells rebuilt: right size, feet on the sheet's foot line, painted wall byte-identical |
| 689 | `2fe2889` | Ember `light` x0.944 — the one held row with a landmark that survived validation |
| 690 | `ecfc68f` | GPT's drawn chain-less board replaced the local erase (which had removed her raised arm on beat 5) |

| pass | commit | what |
| --- | --- | --- |
| A | `eb7af0c` | **Medium had no pad button at all.** All four attacks on the four face buttons BY POSITION: `0 South=Light, 2 West=Medium, 3 North=Heavy, 1 East=Special` |
| — | `ed7b23b` | `tools/check_gamepad_mapping.mjs` — runs the real `pollGamepads` in a `vm` sandbox, no browser/server |
| B | `54e372b` | Legend by physical position (Nintendo mirrors A/B and X/Y), `#pad-status` on select, README six→nine fighters |
| C | `a73cb10` | The pad drives the menus. **The fighter cards are DIVs** — a button-only selector reaches no ninja |
| D | `444fbc9` | MED on both touch clusters; mouse/hand labelled casual |

## Sheet state

2910 cells, **1496 orphans (51%)**, 112.6 MB of PNG.

**The orphans are real art, not blank tail padding** — of 2910 cells only 2 are effectively
empty (both kael orphans), so 1494 orphan cells carry drawn ink. That is exactly why the strip
is the owner's call and not a mechanical cleanup.

**`oni.png` is 231,840 px wide** (shin 176,800). That is past the ~65,535 px dimension limit
for a 2D canvas in Chrome and Safari: these sheets draw fine as an `<img>`, but any future
in-browser tooling that wants to re-key or re-pack has to slice first — it can never blit one
of these through an offscreen canvas in one piece. Decoded, oni alone is ~345 MB of RGBA.

| fighter | cols | live | orphans |
| --- | ---: | ---: | ---: |
| oni | 483 | 217 | 266 |
| mokurai | 347 | 172 | 175 |
| shin | 340 | 141 | 199 |
| tsubasa | 326 | 172 | 154 |
| exile | 322 | 152 | 170 |
| executioner | 320 | 149 | 171 |
| kael | 291 | 155 | 136 |
| ember | 274 | 122 | 152 |
| mizu | 207 | 134 | 73 |

## Open

> **Before any strip pass, compute the REACHABILITY set, not the key set.** An independent
> check found the 1496 figure *understates* the dead cells: some cells have a key pointing at
> them that the engine can still never reach. `shin` `kpush4..kpush8` (cells 245-249) are keyed
> but dead — he has no `kpush1..3` and no bare `kpush`, so the kick resolver's loop breaks at
> n=1 and he falls through to the interim leg pose. `exile.json`'s own `single_cell_names`
> records the same for her collapsed legacy names (hurt/air/block/special), superseded by her
> x-rows. Conversely, two gap patterns look like defects and are NOT: mokurai's `mblock2..8`
> and `mhurt2..8` have no beat 1 by design (index.html starts those loops at i=2), and every
> fighter's "missing 1" on idle/block/hurt/fall/getup is just the convention that the bare
> name IS beat 1.

**Owner's eye**
- **Ember's six held rows** — `grab` 201-208, `kpush` 147-154, `aneu` 99-106, `wallslide` 107,
  `hurt` 131-133, `espec` 190-197, all still on their ORIGINAL cells. Nine landmarks were
  tested; only the hood-cap vertical scale survives, and it does not lock on these six because
  **ember's sheet is not one drawing** (idle/light/crouch = scalloped hood with a stitched rim;
  these rows = plain mottled dome). Only ink area remains, which cannot separate "drawn small"
  from "compact pose". **Do not scale them off the area column.**
- **Orphan strip** — mechanical and verifiable, but some orphans are deliberately reserved art
  (e.g. ember's ghost-pounce cells). He must name what stays first. Ember alone is now 152 of
  274 cells unreferenced (55%), including the 57 superseded by 686/689.
- **127 straight cut-offs** on live cells (≥20px, only 1 is the legitimate wall stroke).
  Not classified, nothing deleted. Sweep code in the session scratchpad; trivially re-runnable.

**Needs new art** (brief written, in the 680 handoff folder)
- exec rise row beats at cells 108/110 (and 109, which has NO figure)
- exec special mid beats 194-199 (bookends 193/200 are already canon)
- kael `kxcut7`/`kxcut8` (cells 73/74), drawn ~1.41x and ~1.49x his idle
- shin getup cells 241/242

**Unblocked engineering**
- Later phases of `docs/COMPETITIVE-GAMEPAD-IMPLEMENTATION-BRIEF.md`: hide the controls
  sidebar during a match, reduce the ordinary-hit screen wash, fixed 60Hz sim, training HUD,
  Story entry button (the cutscenes exist and are unreachable from the menus).
- **Kael's packed idle measures the same as ember's** though canon orders kael above him.
  Kael is the one off his label.
- Portraits 404 on the select screen.

## Methods worth keeping

- **Ink area reads POSE as well as size.** An untouched crouch/tuck row reads 0.77-0.91 of a
  standing idle; a row full of FX/claw sweeps reads ABOVE its true size (ember `light`: area
  said 15.8% big, the validated landmark said 5.9%). Correcting either to 1.00 is wrong.
- **Isolate a painted wall by INTERSECTING the two wall cells** — her pose differs between
  them, the painted wall does not. Then scale the figure alone and write the stroke back.
  Two earlier attempts each broke one law from opposite directions.
- **Carry the keyer disarm** (the faint alpha pixel at the cell border). Dropping it cost 55%
  of an exile cell with no error anywhere.
- **Say WHICH RULER every number came from.** They disagree, legitimately, by ~5 points.
  Ember's `crouch_` reads **0.926 by the hood-vertical landmark** but **0.875 by ink area**;
  his `light` read 1.059 by the landmark and 1.148 by area. The 689 commit message quotes the
  0.926 without naming the ruler — do not re-quote it as an area number.
  Related: bbox HEIGHT is banned as a row-scaling ruler, but the cross-fighter canon table
  (oni 87.5 > mokurai 75.0 > … > mizu 62.4 world px) IS a height table, because ink area is a
  silhouette-mass measure and is not comparable BETWEEN fighters. Height across fighters, area
  and a landmark within one.
- **The runtime keyer is a NO-OP on ember's packed sheet** — every cell was already keyed at
  pack time, so file alpha and post-keyer ink agree there. Emulate it anyway to know that, and
  do NOT generalize it to the other eight.
- **Validate a ruler on known answers before citing it.** Ember's eye (5.4% idle spread vs a
  3% gate) and a face-blob measure (21.7% within-row spread) both looked fine and both failed.
- **Check an erase by LOOKING at every beat.** A pixel count called the chain erase clean;
  zooming showed a whole raised arm gone on beat 5 and chain stubs on 6-8.

## Scripts

`tools/sprites/session-2026-09-02/`

| file | what |
| --- | --- |
| `land_sizefix.py` | central append-and-repoint driver: dedupes identical candidates to one new cell, repoints keys that shared an old cell together, asserts the original prefix byte-identical |
| `land_ember.py` | the same for ember's judge-approved rows |
| `grow_canvas.py` | grow `frameW`/`frameH`+`footY` without moving the art (both growths this session turned out unnecessary — measure a rigid landmark before growing) |
| `wall_rebuild.py` | the intersect-the-two-cells wall method |
| `pack_board.py` | pack an owner-supplied board into a fighter's cell window, pose-matched to the cells it replaces |

Everything else lived in a session scratchpad that will be deleted. Nothing there is
irreplaceable: every replaced cell is still on its sheet as an orphan, so any before/after is
regenerable from git history.
