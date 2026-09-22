# WHAT IS MISSING — the drawing gaps, measured

**2026-08-07 (Opus 5), at SHEET_V 393.** Measured off the shipped sheets and
confirmed by **live sweeps** — the game driven in a real browser, asserting the
cell index actually drawn, not the manifest.

**Read that distinction before trusting any count.** These sheets carry hundreds
of *dead alias* names — `light1`, `hurt2`, `jump` — that no branch reads for that
fighter. Counting names in the manifest says Mokurai's cell 50 does 11 jobs; it
does 3. Only a live sweep tells the truth, and everything below comes from one.

---

## THE STATE OF THE TWO REDRAWN FIGHTERS

| fighter | cells | still drawing old art? |
|---|---|---|
| exile | 151 | **no.** Live sweep draws 66-145 — all redraw. Done. |
| mokurai | 258 | **no.** Full sweep draws 208-257, nothing below. Done. |

---

# THERE IS NO DRAWING GAP LEFT

M9 (idle) landed at SHEET_V 393 and was the last of it. A full live sweep of
Mokurai — idle, run, light chain, heavy chain, special, crouch, roll, block, the
meditation channel, the jump arc, air forward, air down — draws cells **208-257
and nothing below 208**. Exile's sweep draws 66-145, all redraw.

Both fighters are one generation everywhere the engine reaches.

The pages that got them there: Exile 1-8 + E5; Mokurai M1-M6, then M3 (light),
M4 (special), M9 (idle) and the back-turned air elbow.

# THE FOUR RULES — every page has to obey these

1. **⛔ DRAW HIM FACING LEFT.** `drawSprite` does `ctx.scale(-p.facing, 1)`, so
   right-facing art renders **backwards** the moment he moves at the opponent.
   This bit Exile, Mokurai and Oni in three separate commits. **No measurement
   catches it** — foot line, scale and clipping all pass. Only the screen does.
2. **No baked ground shadow.** The engine draws its own. A baked ellipse has to
   be keyed out and it touches a shoe often enough to survive the key. (The old
   green cells have one — that is part of why they read as foreign.)
3. **No second character in the frame.** The engine draws the opponent as its own
   player. The first grapple page drew the victim inside the attacker's
   silhouette and four of ten panels went back.
4. **Leave real white gutters between drawings.** Overlapping FX arcs made one
   page unsplittable by every component method and it had to be cut by hand.

## Page format that packs cleanly

One move per page. Drawings in a row (or two rows), each in its own panel with a
caption naming the slot. **White background.** Four or five across is ideal.
That is exactly what pages 1-8 and M1-M6 were.

## Identity string — paste into every Mokurai page

> Chibi monk, roughly 3 heads tall, strict side profile, FACING LEFT. A cracked
> STONE-GREY bald head with a glowing pale-yellow eye and a RED GEM set in the
> forehead. BARE HANDS wrapped in dark prayer BEADS at both wrists, and a bead
> necklace. NO WEAPON — no staff, no blade. A sleeveless ORANGE-GOLD monk vest
> over a dark under-robe, dark trousers, gold ankle wraps and worn sandals. A
> long RED SCARF streaming behind him. Scarf, sash and beads lag behind the body.

**Match the M1-M6 and M3/M4 pages, not the old green cells.** The reference is
the M5 heavy chain and the M3 light chain — NOT his current idle, which is the
drawing being replaced.

---

# THINGS THAT ARE NOT GAPS — do not "fix" these

- **Exile's ~43 orphan cells.** The retired originals plus the superseded run at
  86-93. Append-only sheets keep them; they cost width, not correctness.
  Compacting is a rewrite of every index — worth doing once, at the end.
- **Mokurai's `run_clean1-8` all pointing at cell 50.** Those names are read only
  inside a branch gated to Shin (`id === 5`). Dead aliases.
- **Exile's `air1/air2/air3` sharing one cell.** One air pose is the intent.
- **`mroll3` and `mroll4` sharing a cell.** A four-beat roll off three drawings.

---

# STILL OPEN — the owner's judgement, not a drawing gap

1. **Exile's far-leg shading on the run.** Her page was four poses drawn twice,
   so the left/right alternation is carried by value — frames 1-4 shade the
   trailing leg dark, 5-8 the leading one. Whether that reads at 93x105 on a
   moving sprite is a look-at-it call. If it doesn't land it comes out; the run
   works without it.
2. **Mokurai's run is four poses, not eight.** His page was row 1 mirrored. A
   true eight needs four more *distinct* phases, not four more drawings of the
   same four.
