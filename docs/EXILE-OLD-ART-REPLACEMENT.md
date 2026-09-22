# EXILE — the old art that still ships, and what has to be drawn to finish her

**Written 2026-08-06 (Opus 5) at SHEET_V 369, measured off the shipped sheet
`web/assets/sprites/exile.png` (102 cells · 300x226 · footY 218 · scale 0.4667).**

Owner: *"replace all her old frames with the new ones, get them so they all be
coherent and consistent."*

## The split is exactly at cell 43

| | cells | look | face patch (measured) |
|---|---|---|---|
| **OLD** | 0-42 | small figure, muddy dark palette, no readable face | 5-138px |
| **NEW** | 43-101 | bigger read, tan eye-wrap, gold bandages, purple sash | 250-560px |

Cells 0-42 are the original sheet carried in from the SHEET_V 228 recovery
snapshot. Cells 43-101 are the pages the owner delivered this session. Two
drawing generations sitting on one sheet — that is the whole inconsistency.

## What was fixed for free at 369

Only **two** animations actually drew from both generations, and both are now
all-new:

1. **The light chain** drew cells 17, 18, 66, 6, 17 — four old, one new — so the
   button she presses most changed art style mid-combo. Now `[light3, light4,
   light5]` = 66/67/68 (reach → overhead → strike). Three beats of one style.
2. **`F.idle`** still pointed at cell 0. Her in-game idle has been the xbreath
   cycle since 357, but `F.idle`/`F.idle2` are what her **bunshin clone** draws
   and the roster-wide last-resort fallback — so the old drawing was still
   reachable in play. `idle` → 69, `idle2` → 70. (The character-select cards are
   painted portraits, not sheet cells — checked, unaffected.)

That is the end of what editing can do. **Everything below needs drawing.**

## What still needs drawing — ONE page

SHEET_V 376 landed pages 1, 2, 3, 6, 7 and 8 (28 figures, cells 108-135); 377
landed page 4, her chain spin (10 figures, cells 136-145). A live sweep of every
state she has — idle, run, light, heavy, special, throw, block, hurt, crouch,
roll, wall cling and the jump arc across five vertical speeds — now draws **two**
old-generation cells and no others:

| cell | slot |
|---|---|
| 27 | `slide4` |
| 29 | `kneel xcrouch` |

### PAGE 5 — slides and crouch (5 cells) — the last one owed
| cell | slot | pose |
|---|---|---|
| 24 | `slide1` | drop into the slide, legs extended |
| 25 | `slide2` | mid-slide, dust at the feet |
| 26 | `slide3` | slide tail |
| 27 | `slide4` | rise out of it |
| 29 | `kneel xcrouch` | low guard / crouch |

(24, 25 and 26 no longer draw — the engine reaches slide4 and the crouch only —
but all five belong to the same move and want drawing together.)

## Identity string for the page

Paste verbatim; it is the shipped-sheet lock and it matches cells 43-145:

> Chibi ninja, roughly 3 heads tall, strict side profile, FACING LEFT. NO HOOD.
> A huge windswept BLACK MANE with silver-white streaks streaming behind her. A
> TAN CLOTH EYE-WRAP over one eye with dark-red kanji brushed on it. A BLACK
> CLOTH MASK over nose and mouth. Pale skin, one visible eye. BLACK and charcoal
> ninja garb — wrapped sleeves, layered skirt panels over black trousers. A DEEP
> PURPLE SCARF at the neck and two long purple sash tails off the waist. TAN
> BANDAGE WRAPS on forearms, hands, shins and ankles. In one hand a KAMA SICKLE
> (silver curved blade, dark wrapped handle). In the other a CHAIN with a round
> SMOOTH IRON WEIGHT BALL, links clearly readable.

### Four things that cost real time on the pages so far

1. **Draw her facing LEFT.** `drawSprite` does `ctx.scale(-p.facing, 1)`, so a
   cell drawn facing right renders backwards the moment she moves at the
   opponent. Every page has arrived facing right and been flipped on the way in.
2. **No baked ground shadow.** The engine draws its own.
3. **No second character in the frame.** The first grapple page drew the opponent
   inside her silhouette; the engine draws them as their own Player, so it
   doubled up.
4. **Leave real gaps between drawings.** Overlapping FX arcs are what made page 4
   unsplittable by every component method — it had to be cut on a dark-column
   profile instead.

## Orphans — art on the sheet nothing can draw

38 cells as of 377: **0-5, 8-16, 19, 21-23, 28, 30-33, 37-42, 86-93**. Almost all
of it is the original 43 the redraw retired, plus the superseded run cycle at
86-93. They cost sheet width, not correctness.
