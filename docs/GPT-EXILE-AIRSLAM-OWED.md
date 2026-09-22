# GPT PAGE OWED — EXILE'S AIR SLAM (one row, 6 poses)

**Status Aug 11 2026:** her air Down+Heavy currently draws **repurposed grapple frames**
(cells 119 → 121 → 122, her `xgrap` page). It animates, so the move is no longer frozen —
but they are three frames of a chain *grapple* that happen to fall in roughly the right
shape, not a slam. This page replaces them.

**This is the ONLY art owed.** Everything else that looked like an art gap was measured and
is not one — see the last section before you commission anything more.

---

## 1. THE MOVE

**SKY DOWN-SMASH** — her airborne Down+Heavy. She stops dead in the air, hauls the iron
weight ball overhead, and drives it straight down into the floor with her whole body
following it. The engine already runs it as a three-stage meteor:

| stage | engine | duration | the frame that draws |
|---|---|---|---|
| hang | `slamPhase 1` | 150ms | `hdown2` |
| plunge | `slamPhase 2` | 2.5× gravity, ~315ms | `hdown3` |
| landing tax | `SLAM_LAG` | 380ms | `hdown4`+ |

So **`hdown2` and `hdown3` carry the move.** They are the two that must read at a glance.
The other four dress the entry and the recovery.

## 2. THE SIX BEATS

Deliver **one row, left to right, 6 poses:**

1. **`hdown1` — CATCH.** Still rising or at apex. She snaps upright in the air, chain
   whipping up, ball just starting to climb past her head.
2. **`hdown2` — HANG.** ⛔ *Money frame 1.* Dead stop at the top. Body coiled and compact,
   knees drawn up, ball held **overhead at full chain extension**, both hands on the chain.
   This is the beat the whole move hangs on — it must read as a held breath.
3. **`hdown3` — PLUNGE.** ⛔ *Money frame 2.* Committed straight down. Body stretched
   vertical, legs trailing **above** her, arms driving the ball **below** her — the ball is
   the lowest thing in the frame and leads the fall. Motion streaks vertical.
4. **`hdown4` — IMPACT.** Ball strikes the floor. Crimson/violet burst at the point of
   contact, chain slack and snapping, her body compressed over it.
5. **`hdown5` — RECOIL.** Landed in a deep crouch, one knee down, ball settled, mane still
   falling.
6. **`hdown6` — RECOVER.** Rising back to her guard, chain gathering.

## 3. IDENTITY STRING — paste verbatim into the prompt

> Chibi ninja, roughly 3 heads tall, strict side profile. NO HOOD. A huge windswept BLACK
> MANE with silver-white streaks, long and streaming behind her. A TAN CLOTH EYE-WRAP
> covering one eye with dark-red kanji brushed on it. A BLACK CLOTH MASK over nose and
> mouth; the one visible eye is pale and hard under a heavy dark brow. Pale skin. BLACK and
> charcoal ninja garb — wrapped sleeves, layered skirt panels over black trousers. A DEEP
> PURPLE SCARF at the neck and two long purple sash tails off the waist. TAN BANDAGE WRAPS
> on forearms, hands, shins and ankles. In one hand a KAMA SICKLE (silver curved blade, dark
> wrapped handle, red-brown grip). In the other a CHAIN with a round SMOOTH IRON WEIGHT
> BALL, links clearly readable.

**Palette:** garb near-black `#1c1626` (highlight `#322646`) · scarf + sash `#6d28d9`
(accent `#8b5cf6`) · visible eye `#f2f4f6` · eye-wrap warm tan, kanji dark red · bandage
wraps warm tan — *a real secondary colour, not a detail* · sickle blade `#9aa2ac`.

**Her feet are TAN BANDAGE-WRAPPED with a dark toe cap.** Not boots. A black gold-strapped
boot was grafted on once and rejected on sight.

## 4. HARD RULES — these are QC gates, not taste

- **NO ground shadow, no floor line, no horizon.** Nothing under the feet unless it is
  impact FX. The engine draws her shadow; a baked one doubles it.
- **NO text, numbers, captions, labels, panel borders, grid lines or cell boxes.**
  Deliver a bare page. *(Oni's dash shipped with the board's captions baked into the art
  because a labelled page was cut instead of a clean one.)*
- **Facing LEFT.** Every sheet in this game is authored facing left and the engine flips
  the whole sprite by `ctx.scale(-facing, 1)`. A right-facing page has to be mirrored, and
  mirroring is how her chain ended up on the wrong side once already.
- **Plain white background**, poses evenly spaced on one row, generous margin, and **no FX
  bridging two poses** — a red arc that spans a gap fuses neighbours and defeats the cutter.
- **Continuity in every frame:** the mane, the eye-wrap, the purple scarf and sash, the
  tan wraps, the kama AND the chain-and-ball. She holds both weapons at all times.
- The ball is **round, smooth and iron.** Not spiked, not a flail head.

## 5. GEOMETRY

Draw large; the pipeline scales. For reference, her cell is **480 × 368 with `footY` 280**
and she renders at **scale 0.4667**, so her standing body is ~148 sheet px.

⛔ **The plunge frame is TALLER than the idle** — she is stretched vertical with the ball
below her. That is correct and expected. Do **not** shrink the pose to fit; the frame box
grows, the body never shrinks. Frames 2 and 5 are shorter (compact coil, deep crouch); that
size difference is the move and must survive into the sheet, so this row is packed on **ONE
uniform scale**, not per-cell height matching.

## 6. WHAT IS *NOT* OWED — do not commission these

Measured Aug 11 2026, so nobody spends art budget twice:

- **Mokurai's air slam — SOLVED, no art needed.** Built from three cells already on his
  sheet: 214 coil → 221 plunge → 235 impact.
- **Mizu's 7 dead Specials — CODE, not art.** She already carries every family:
  `sneu`, `sfwd`, `sback`, `sdown`, `sup`, `gsfwd`, `gsdown`. The art is packed and drawing;
  the moves spawn no hitboxes.
- **Oni's 9 dead Specials — MOSTLY CODE.** He carries `gsfwd`, `gsback`, `gsdown`, `sdown`,
  `sup`. The dispatch chain simply has no branch for his id, so all ten of his Special
  inputs fall out the far end untouched. **Optional second page if you want his air
  specials complete: `sneu`, `sfwd`, `sback` are the three families he lacks (6 poses
  each).** Everything else of his is a wiring job.
- **Her idle feet — DONE** at SHEET_V 458.

## 7. WHEN IT COMES BACK

Deliver the bare page as PNG. Then:

```bash
python3 tools/sprites/cut_strip.py <page.png> <outdir> --n 6
```

`cut_strip.py`, **not** `cut_page.py` — the latter segments by connected components and her
chain bridges neighbours into one blob. Then append with `extend_sheet.py` using **one**
`FIXED_SCALE` solved against her idle body height, repoint `hdown1`..`hdown6`, and bump
`SHEET_V` in the same commit.

⛔ **Define all six or none.** `dirCells` gates on `hdown1` and then returns a fixed
six-slot array — defining `hdown1` without `hdown4/5/6` hands the blitter `undefined` and
draws **cell 0**. That is why only `hdown2/3/4` are defined today.

Verify with `python3 tools/audit_move_coverage.py` (STATIC must stay 0 of 180) and
`python3 tools/audit_frame_hygiene.py` (catches baked captions and borders).
