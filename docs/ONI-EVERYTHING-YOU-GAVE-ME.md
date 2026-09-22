# ONI — EVERY BOARD YOU GAVE ME, AND WHETHER IT REACHES THE SCREEN

**2026-08-13.** Measured, not read off the source. His whole kit was driven with
real key presses (216 steps) while a 4ms sampler recorded every cell that
actually got drawn. **161 of his 293 packed cells came up. 132 never did.**

---

## THE ANSWER TO "I DON'T SEE HIS OTHER MOVES"

**Your directional LIGHT board is completely unreachable.** `MASTER-LIGHT-DIR-4x6.png`
— four moves, 24 drawn cells — has no way in, because every direction + `F` is
bound to a **single-frame kick pose** instead:

| you press | you get | what's sitting unused |
|---|---|---|
| `Fwd + F` | `kpush` — **1 cell** | `glfwd1-6` (6 cells) |
| `Back + F` | `kheel` — **1 cell** | `glback1-6` (6 cells) |
| `Down + F` | `ksweep` — **1 cell** | `gldown1-6` (6 cells) |
| `Up + F` | nothing, he just jumps | `glup1-6` (6 cells) |
| `Up + G` | his **neutral heavy** (`heavy_i1-5`) | `ghup1-6` (6 cells) |

So four of his six-beat light attacks are being played by three still frames, and
his rising heavy plays the wrong move entirely. That is what "his attacks don't
show up" is.

**I had `Up+G → ghup` in the earlier audit. That was wrong** — it draws
`heavy_i1-5`, measured twice. Corrected here.

---

## CONFIRMED STRANDED — art on the sheet, no way to reach it

| row | cells | board | why |
|---|---|---|---|
| `glfwd` `glback` `glup` `gldown` | 24 | `MASTER-LIGHT-DIR-4x6` | dir+F is bound to 1-frame kicks |
| `ghup` | 6 | `MASTER-HEAVY-DIR-4x6` | Up+G falls through to the neutral heavy |
| `bostrike` `bosweep` | 12 | `CLEAN-BOSTAFF-STRIKE/SWEEP-6` | no input exists |

**42 cells, and not one of them needs redrawing.** They need inputs.

## NOT REACHED IN THE SWEEP — needs confirming one at a time

`lunge` (6) · `cart` (6) · `knives` (6) · `wslice` (3) · `aback` (6) · `sup` (6) ·
`dashatk` (2) · `airkick` (2) · `divekick` (2) · `kstomp` (1)

These may need a situation the sweep never created (a wire bind that connects
first, a specific air state) rather than being dead. Each gets its own probe
before I claim anything about it.

## STATE ART THE SWEEP COULDN'T TEST

`block` · `blockhit` · `guard` · `getup` · `fall` · `slide` · `walljump` ·
`wallslide` · `dash` · `roll` — these need to be hit, knocked down, or put on a
wall. Not evidence of a bug; evidence my sweep didn't cover them.

---

## WHAT IS WORKING (measured this pass)

Neutral `F` (`glneu1-6`) · neutral `G` (`heavy_i1-5`) · **all six specials, every
beat, all connecting** — whip `whip1-6` 15dmg, wire shot `special1-6` 9, Fwd+H
`gsfwd1-6` 28, Up+H `gsup1-6` 16, Down+H `gsdown1-6` 32, Back+H `gsback1-6` 12 ·
air `aneu` `afwd` `adown` · heavies `ghfwd` `ghback` `ghdown` · the run
(`runb1-8`) · roll · smoke · bunshin.

---

## THE SPEED

You were right and it was mine. Fixing the truncated specials, I made the
animation *fit* the shortened attack state — which sped every one of them up.
Backwards. The authored millisecond count **is** the pacing. It now holds the
state open until the art has finished instead, so the moves play at their drawn
speed AND reach their last beat.

---

## THE WHIP — your ruling, BUILT (SHEET_V 493)

> *"It was supposed to bring people in. He sliced them. Or you can make it like
> the red razor sharp wire cut them and he come with a slice."*

Built as you described: **the wire cuts where it lands and ONI travels** — he
covers the gap during the startup and arrives on the contact beat. The bare
re-press after a bind is the short-wire slice (`wslice`); Fwd takes the katana
execution, Back the claw rake, and the two air grabs split on where the victim
is. Verified live at 493 and re-proven inside the second mode by
`tools/check_oni_mode2.mjs`.
