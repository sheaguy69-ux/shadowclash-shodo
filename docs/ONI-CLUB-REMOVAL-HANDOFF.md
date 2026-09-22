# ONI — "THE FOUNDER" CLUB-REMOVAL HANDOFF (for GPT frame generation)

> Give this file to GPT. It describes what Oni SHOULD look like, what is already
> fixed in code, and exactly which cells need new claw art.

## 1. THE DESIGN IS SETTLED (owner canon, Aug 11 2026)

Oni is **claw + knives + twin back swords**. He does **NOT** have a club / kanabo /
bo staff. The club is the OLD, retired design and must not appear.

Final look:
- **White skull mask**, three claw-scratch gouges across it, **RED eyes**. Two dark horns.
- **Black hood + tattered black mantle**, ash-gray worn plate (chest, bracers, knees, boots).
- **Cloth wrappings on BOTH hands and forearms.**
- **RIGHT HAND CLAW ONLY** — five long dark-gunmetal blades. **LEFT HAND IS WRAPPED, NO CLAW.**
- **Two swords carried crossed on his back.**
- Palette: **black, ash gray, white mask, red eyes/FX.** NO purple, NO mane, NO pelt.
- Authored facing LEFT (the engine mirrors him); claw stays on the RIGHT hand in the art.

His real weapons (from the shipped kit):
- **Light** = knife pokes (small knife).
- **Heavy** = claw swings, with **red arc FX already drawn into the cell**.
- **Specials** = claw pressure into ground slams + a mid-air **smoke bomb** (twice a round).
- **Wire finishers** = katana execution / claw execution / dual knives.

## 2. WHAT IS ALREADY FIXED IN CODE (no frames needed for this)

The **V-key "second mode" that switched him to a staff/club has been REMOVED**.
The `mode2` flag is now always false, so the neutral-light "staff strike"
(`bostrike`) and neutral-heavy "staff sweep" (`bosweep`) are never drawn. The
in-game controls help no longer mentions the staff or second mode.

## 3. CELLS THAT STILL SHOW THE CLUB (these are the frame need)

These frame rows are now dead OR still carry club art. GPT should regenerate them as
**claw** poses to match the design above. (Cell indices are 0-based into oni.png,
480x372 per cell, 317 columns, feet at footY 330.)

| frame row | cells | what it currently shows | what it SHOULD be |
|---|---|---|---|
| bostrike1-6 | 153-158 | staff strike (bo) | claw strike (right-hand claw) |
| bosweep1-6 | 159-164 | staff sweep (bo) | claw sweep (low, trips) |
| sdown1-6 | 67-72 | club overhead slam | claw downward slam |
| aspin1-6 | 189-194 | spinning club | claw spin (if kept) or remove |
| athrow1-6 | 311-316 | club throw (air special) | claw air special or smoke bomb |
| crouch (49) | 49 | club held up-and-back | crouch with claw, no club |
| ghfwd/ghback/ghup/ghdown | 201-224 | ground heavies | verify: claw heavies, no staff |
| heavy_i1-5 | 23-27 | heavy | verify: claw, no club |
| sup1-6 | 93-98 | special up | claw, no club |

> If the owner does NOT want a claw replacement for a given move, the correct action
> is to leave the move routed to an existing claw cell — do NOT leave a club cell
> visible anywhere.

## 4. GENERATION RULES (read before generating)

- **2D cel illustration**, NOT pixel art. Heavy black outlines, readable silhouette,
  dark palette, glowing featureless angled eyes.
- **Feet-anchored** — every grounded cell's soles sit on footY (330); the engine lifts
  airborne sprites itself, so airborne cells also plant feet at footY+1.
- **One uniform scale per move**, anchored on the idle body (154px); do NOT scale each
  beat to a common height (that causes size boil).
- **No baked camera/ground/wall** in the frame; key out the background.
- **Red FX only** where the move is a claw swing — steel-white is off-palette for Oni.
- The sheet is **append-only**: new cells go at the END (cols grow), existing cells are
  never re-encoded.

## 5. WHO NEEDS FRAMES vs CODE (roster-wide)

- **ONI** — needs the club cells above regenerated as claw art. The code is already fixed.
- **Everyone else** — code-only. Their specials and moves resolve to valid existing
  frames; no new art is required. If any move looks wrong it is a routing bug, not a
  missing frame.

## 6. VERIFY

Reload http://localhost:9100 (Cmd/Ctrl+Shift+R) and watch Oni:
1. He must never show a club/staff in any move.
2. Neutral light = knife, neutral heavy = claw (red arcs), specials = claw slams + smoke bomb.
3. Pressing V (P2: K) does nothing — the second mode is gone.
