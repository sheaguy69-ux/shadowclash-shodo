# ShadowClash — outstanding art brief (SHODO-EDITION, current at SHEET_V 690)

*Written 2026-09-02. Item 5 (Exile's chain-less row) is DONE — the owner's board landed at
690 as cells 314-321. The four remaining items are 1-4.*

Everything in this file is art I could NOT fix locally. Anything fixable by scaling, erasing,
repointing or growing a cell window is already done in the tree; nothing below is a scale problem.

## House rules for every prompt here
- ONE row per image, left-facing, transparent background, captions BELOW the row (never over the art).
- The whole row at ONE body size: heads, hands and weapons the same size beat to beat. Do not shrink
  the tucked beats.
- No motion blur, no speed lines, no ground shadow, no background, no border, no drop shadow.
- Nothing may end in a straight cut. If an effect leaves the figure, it fades to nothing inside the
  frame; a smear that hits the canvas edge is a reject.
- Match the fighter's existing design exactly (mask, hair, sash, weapon, palette) — these are
  replacement beats inside a live animation, not a redesign.

---

## 1. EXECUTIONER — "rise" row, three beats (highest value)
Row: `xrise1..8` / `xkiriage1..8` (the same eight cells). Live cells: 105-112.
What is wrong: the row was assembled from two different sources, so the beats step in size mid-swing.
Measured against his idle (1.00 = idle size): 105 .88 | 106 .80 | 107 .84 | **108 .94** | 109 .77 |
**110 .73** | 111 .81 | 112 .88. Beat 107→108 jumps 14%, 110→111 climbs 18%. One uniform scale cannot
fix a row whose beats disagree with each other.
**Generate:** the rising-cut sequence as ONE clean row of 8 beats at one body size — sheathed low →
draw → rising diagonal cut → follow-through → recover to stance. Beat 3 of 8 (the cell now numbered
109) currently has NO figure at all, only an effect arc: draw the fighter in it.
Target size: the same body height as his idle stance (his standing beats read 0.88-0.92 of idle by ink
area, which is correct for a crouched draw; the STAND beats at both ends must match idle exactly).

## 2. EXECUTIONER — neutral special, the six middle beats
Row: `special1..8`, live cells 193-200. The two bookends (193, 200) are already correct at idle size
(0.92); the six middle beats (194-199) came from a smaller source and read 0.85. Scaling the row moves
the good bookends 12-15% too big, so the middles have to be redrawn instead.
**Generate:** beats 2-7 of the neutral special at the SAME body size as the row's first and last beat.
Note: this row is currently unreachable in play (his neutral special routes elsewhere), so it is the
lowest priority item in this file — worth doing only if you want the row alive later.

## 3. KAEL — air heavy, last two beats (`kxcut7`, `kxcut8`)
Live cells 73 and 74. These two are old art and are drawn **41% and 49% larger** than kael's idle
(1.41 and 1.49 where 1.00 is idle). The first six beats of the same move read 0.76-1.11. The engine
plays all eight in sequence, so kael visibly inflates on the last two frames of every air heavy.
**Generate:** the final two beats of the air heavy — the crossing slash and the recovery — at kael's
idle body size, matching beats 1-6 of that row (hood, twin blades, gold trim).

## 4. SHIN — getup, the two floor beats
Live cells 241 and 242 (`getup`, `getup2`). The row cannot be fixed with one scale: 241 (lying, with
dust) reads 1.16 of idle and 242 (head down) reads 1.01, and the beat that hands back to idle lands
10% big while another lands 13% small.
**Generate:** a four-beat getup row at ONE size — flat on the floor → pushing up on one arm → rising
crouch → standing, the last beat exactly idle size. Keep the floor dust as a soft cloud that fades out;
it must not end in a hard edge.

## 5. EXILE — "Chain to the Wall", chain-less beats (only if you reject my erase)
I already produced chain-less versions locally by erasing the painted chain, and the engine now draws
the rope itself from her drawn fist, so this is optional. If you want them drawn properly instead:
same eight poses (ready → coil → cast → taut → yank → reel → wall-ready → brace), same prompt as the
approved board, but with NO chain and NO sickle in flight. The gripping fist stays closed and fully
visible in every beat, nothing overlapping it; the coiled chain and iron ball stay at her hip as in her
idle. Same canvas and body size as the approved board.

---

## Not art — for your information
- **Ember** is the only fighter whose size pass is unfinished; his verification fleet is running now.
- **Straight-edge sweep:** I swept every live cell of all nine fighters for hard vertical cut-offs
  (127 candidate edges). Most look like blade edges or the drawn wall stroke, which are legitimate.
  I have not deleted anything — say the word and I will classify them cell by cell and delete the
  effects that genuinely end in a cut.
- **Portraits** still 404 on the select screen; that is art you own, not a size issue.
