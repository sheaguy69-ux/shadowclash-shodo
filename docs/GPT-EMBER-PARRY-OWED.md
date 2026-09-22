# GPT PAGE OWED — EMBER'S BLADE-TRAP PARRY (one row, 5 poses)

**Status Aug 12 2026:** his Back+Special parry draws `block2` — **his guard cell**. It is
the only parry on the roster with no art of its own, and the only one held on a single
picture: Tsubasa's draws 2 cells, Mokurai's 2, Kael's 4. So the move that is supposed to
*catch a blade* currently looks exactly like standing still and blocking.

His discipline in his own spec is **Tekkōkagijutsu / Shukōjutsu — "close-quarters claw
slashes, blade trapping, and aggressive beast-style grappling."** The trap is his identity
and it is the one thing he cannot show.

---

## 1. THE MOVE

**BLADE-TRAP PARRY** — Back + Special, grounded. The engine's own words:

> *Tekkōkagijutsu: the crossed iron claws CATCH the incoming blade — a caught swing eats
> the X-shred counter. Whiff = 0.5s of honest recovery.*

| stage | engine | timing |
|---|---|---|
| the trap is open | `PARRY_STANCE` | held |
| catch window | `parryFlashTimer` | **0.15s** — a hair wider than Tsubasa's strict 0.133 |
| whiff | `recoveryTimer` | 0.5s, fully punishable |
| on a catch | X-shred counter | resolved in `takeDamage` |

**It is a TRAP, not a block.** He is not absorbing the hit — he is inviting the swing,
scissoring the two claw racks shut on the blade, and answering. That distinction is the
whole page.

## 2. THE FIVE BEATS

Deliver **one row, left to right, 5 poses.** Five is his house row length — `light1..5`,
`espec1..5` — so a 5-row drops in beside his existing work.

1. **`eparry1` — OPEN THE TRAP.** Weight back, both clawed hands held wide and low, palms
   turned out, the two racks *apart*. Deliberately inviting. This must not read as a guard:
   his guard is claws crossed tight in front of the face, and this is the opposite shape.
2. **`eparry2` — SET.** Claws drawn in and angled toward each other, elbows tucked, eyes
   locked forward. The jaws of the trap about to close.
3. **`eparry3` — THE CATCH.** ⛔ *Money frame.* The two claw racks **scissor shut on an
   incoming blade**, the blade pinched at an angle between them, a hard white-gold spark
   at the bite point. His whole frame braced against it. Draw the caught blade as a bare
   steel edge — it belongs to whoever swung it, so give it no hilt, no owner, no colour of
   its own.
4. **`eparry4` — THE X-SHRED.** Both claws rip outward across the body in a wide X, the
   counter. Twin three-line tear trails in his green.
5. **`eparry5` — RECOVER.** Settling back toward his stance, claws dropping, scarf still
   carrying the motion.

## 3. IDENTITY — derived from the SHIPPED SHEET, `web/assets/sprites/ember.png`

There is no separate lock file for him; the sheet is the source of truth. Paste this:

> Chibi ninja, roughly 3 heads tall, strict side profile. A DEEP GREEN POINTED HOOD with a
> long drape down the back. Under the hood the face is a BLACK VOID — no skin, no mouth,
> no nose — carrying only TWO GLOWING PALE-GREEN ANGLED EYES, featureless, no pupils. A
> bright green SCARF trailing behind the neck. Layered dark-green tunic over darker green
> trousers, olive and lime highlights, a brown leather belt with a plain buckle, wrapped
> shins. On BOTH hands a TEKKŌ-KAGI: three long silver claw blades per hand mounted on a
> dark grey riveted knuckle plate. He is heavy-set and low-slung, not lithe.

**Palette:** primary/highlight lime `#84cc16` · eye glow `#22c55e` · tunic `#3f6212` ·
scarf `#15803d` · claw blades bright silver on a dark gunmetal plate.

⛔ **He is HE/HIM.** Roster canon, and the engine's own comments use it.

## 4. HARD RULES — QC gates, not taste

- **NO ground shadow, no floor line, no horizon.** The engine draws his shadow.
- **NO text, captions, labels, panel borders, grid lines or cell boxes.** A bare page.
  *(Oni's dash shipped with a labelled board's caption text baked into the art.)*
- **Facing LEFT.** Every sheet here is authored facing left; the engine flips the whole
  sprite. A right-facing page has to be mirrored, and mirroring is its own bug.
- **Plain white background**, evenly spaced on one row, generous margin, and **no FX
  bridging two poses** — a spark or tear-trail spanning a gap fuses neighbours and defeats
  the cutter.
- **Six claw blades in every frame** — three per hand, both hands, all five poses. The
  hood, the void face and the two green eyes are continuity in every frame.
- The eyes are **flat glowing shapes**. No pupils, no iris, no highlight dot.

## 5. GEOMETRY

Draw large; the pipeline scales. His cell is **340 × 377 with `footY` 369**, he renders at
**scale 0.3349**, and his standing body is **207 sheet px** — the reference to solve the
uniform scale against.

The catch and the X-shred are **wider** than his idle (arms out); `eparry1` is wide too.
That is correct. The frame box is 340 wide against a 195px idle, so there is room — but
pack the row on **ONE uniform scale**, never per-cell height matching, or the wide frames
get shrunk against the narrow ones and he changes size mid-parry.

## 6. OPTIONAL SECOND PAGE — ONI'S AIR SPECIALS

Only if you want it; **it is not blocking anything.**

Oni is missing three air-special families: **`sneu`, `sfwd`, `sback`** (6 poses each). He
already carries `sdown` and `sup`, and `gsfwd`/`gsback`/`gsdown` on the ground.

⛔ **His nine dead Special inputs are a CODE gap, not an art gap.** The neutral-special
dispatch chain has no branch for his id at all, so every one of his ten Special inputs
falls out the far end untouched — the art he already has does not fire either. Commission
these only if the moves are going to be written; art alone changes nothing for him.

His geometry: **420 × 300, `footY` 268, scale 0.4667.** Identity canon is
`Oni-Identity-True-Lock.md` and `RECOVERY/oni-founder/ONI-BIBLE-FINAL.png` — ragged black
hood, WHITE demon mask with three claw gouges and two RED slit eyes, two horns, ash-cloth
wrappings on both forearms, dark gunmetal armour, two katanas crossed on his back, and a
four-bladed tekko-kagi on his RIGHT HAND ONLY. Red `#D71302` is the ONLY hot colour.

## 7. WHEN IT COMES BACK

```bash
python3 tools/sprites/cut_strip.py <page.png> <outdir> --n 5
```

`cut_strip.py`, **not** `cut_page.py` — the latter segments by connected components and
claw FX bridges neighbours into one blob. Then `extend_sheet.py` with a single
`FIXED_SCALE` solved as **207 ÷ (his upright pose on the page)**, append, and bump
`SHEET_V` in the same commit.

Wire `eparry1..2` to `PARRY_STANCE` (banded on `parryFlashTimer`, the way Exile's tumble
bands on `tumbleT`); `eparry3..5` are the catch and counter and need their own draw hook
off the `takeDamage` parry result.

Verify: `python3 tools/audit_move_coverage.py` — **STANCE must go 1 of 180 → 0** — and
`python3 tools/audit_frame_hygiene.py` for baked captions, borders and neighbour bleed.
Last page delivered had a 4px sliver of one pose bled into the next; the tool caught it.
