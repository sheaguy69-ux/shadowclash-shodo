# HANDOFF — EXILE AND MOKURAI, the old-art replacement

**2026-08-07 (Opus 5).** Last commit in this lane: SHEET_V **393**.
Local only. Nothing pushed, nothing deployed.

---

## STATE

| fighter | cells | frameW | frameH | footY | drawing old art? |
|---|---|---|---|---|---|
| exile | 151 | 480 | 368 | 280 | **no — zero of the original 43** |
| mokurai | 258 | 300 | 248 | 218 | **no — full sweep draws 208-257** |

Both fighters are on a single art generation everywhere the engine can reach,
which is the thing that was wrong with them: two generations were live at once
and moves changed style mid-kit. **There is no drawing gap left on either.**

## WHAT LANDED, IN ORDER

| SHEET_V | what |
|---|---|
| 364 | Exile run cycle, 8 cells |
| 365 | Mokurai run cycle, 4 cells |
| 367 | Exile run — facing and scale fixed (was sprinting backwards, at 74%) |
| 369 | Exile grapple, the owner's corrected page |
| 373-377 | Exile pages 1, 2, 3, 4, 6, 7, 8 — 34 cells, sheet re-framed to 480x368 |
| 383 | Exile E5 + Mokurai M1-M6 — 35 cells. **Exile finished.** |
| 389 | Mokurai meditation channel + forward air game wired |
| 391 | Mokurai back-turned air elbow (242/243) — the M2 page's missing panel |
| 392 | Mokurai light chain (244-248) and special chain (249-253) |
| 393 | Mokurai idle cycle (254-257). **Both fighters finished.** |

## VERIFIED, AND HOW

Everything below was probed in a real browser (`tools/watch_game.py`, real rAF,
real key events), asserting the **drawn cell index** — not a state flag.

- Meditation channel: cells `[237,238,239,240,241]` across 119 frames, maxMed 1.98.
- Airborne forward light → `217, 218`. Airborne down light → `221`.
- Mokurai jump arc → `212, 213, 214` by vertical-speed band.
- Exile: idle, run, light, heavy, special, throw, block, hurt, crouch, roll, wall
  cling and the five jump bands all draw new cells.
- Sheet integrity, both fighters: original cells byte-identical, no cell clipped
  at any frame edge, manifest `cols` matches sheet width.

## STILL OPEN — owner's call, not assigned

1. **Exile's far-leg shading on the run.** Her page was four poses drawn twice,
   so left/right alternation is carried by value — frames 1-4 shade the trailing
   leg dark, 5-8 the leading one. Whether that reads at 93x105 on a moving
   sprite is a look-at-it call. If it doesn't land, say so and it comes out; the
   run works without it.
2. **Mokurai's run is four poses, not eight.** A true eight needs four more
   *distinct* phases, not four more drawings of the same four.
3. **Exile's ~38 orphan cells** (the retired originals plus the superseded run at
   86-93). They cost sheet width, not correctness. Compacting is a rewrite of
   every index — worth doing once, at the end.

## THE FOUR RULES THAT COST TIME ON EVERY PAGE

1. **Draw the fighter FACING LEFT.** `drawSprite` does `ctx.scale(-p.facing, 1)`,
   so right-facing art renders backwards the moment they move at the opponent.
   This bit Exile, Mokurai and Oni in three separate commits. **No measurement
   catches it** — foot line, scale and clipping all pass. Only the screen does.
2. **No baked ground shadow.** The engine draws its own.
3. **No second character in the frame.** The engine draws the opponent. The first
   grapple page drew the victim inside her silhouette; four of ten panels went back.
4. **Leave real white gutters between drawings.** Overlapping FX arcs made the
   specials page unsplittable by every component method.

## THE TOOLS

- `tools/sprites/cut_page.py` — a delivered layout page → loose transparent PNGs.
  Segments figures, not a grid: rules come off as rows/columns at >85% ink before
  the flood, panels are the complement of the rules via a recursive X-Y cut,
  captions drop below the figure's foot line.
- `tools/sprites/contact_sheet.py` — labelled contact sheet, every cell with its
  slot names, orphans flagged.
- `tools/watch_game.py --script <json>` — CDP-driven Chrome, real rAF. The only
  way to verify what is actually drawn.

**Scale is solved by iteration against that fighter's own live idle**, measured
with the same erosion kernel at both ends. Mixing kernel scales across source
and cell is what made Exile's run 74% size.

## IDENTITY STRINGS — paste into any new page

**EXILE** — Chibi ninja, roughly 3 heads tall, strict side profile, FACING LEFT.
A huge windswept BLACK MANE with silver-white streaks streaming behind her. A TAN
CLOTH EYE-WRAP over one eye with dark-red kanji brushed on it. A BLACK CLOTH MASK
over nose and mouth. Pale skin, one visible eye. BLACK and charcoal ninja garb —
wrapped sleeves, layered skirt panels over black trousers. A DEEP PURPLE SCARF at
the neck and two long purple sash tails off the waist. TAN BANDAGE WRAPS on
forearms, hands, shins and ankles. In one hand a KAMA SICKLE (silver curved blade,
dark wrapped handle). In the other a CHAIN with a round SMOOTH IRON WEIGHT BALL,
links clearly readable.

**MOKURAI** — Chibi monk, roughly 3 heads tall, strict side profile, FACING LEFT.
A cracked STONE-GREY bald head with a glowing pale-yellow eye and a RED GEM set in
the forehead. BARE HANDS wrapped in dark prayer BEADS at both wrists, and a bead
necklace. NO WEAPON — no staff, no blade. A sleeveless ORANGE-GOLD monk vest over
a dark under-robe, dark trousers, gold ankle wraps and worn sandals. A long RED
SCARF streaming behind him. Scarf, sash and beads lag behind the body.

## TO LOOK AT IT

```bash
python3 tools/serve.py
```

Port 9100. It sends `Cache-Control: no-store` — a plain `http.server` sends none,
pins stale sprite PNGs and fakes regressions.
