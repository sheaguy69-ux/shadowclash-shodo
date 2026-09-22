# Roster floor audit — 2026-07-25

Every fighter checked for sprites that float off the ground, plus two dead ends recorded so
nobody re-investigates them. Three real bugs found and fixed; everything else was either
correct behaviour or below the visible threshold.

---

## The method (reuse this — it found all three bugs)

1. **In-browser, enumerate which cells each GROUNDED state actually resolves to.** Don't audit
   the sheet blind: most cells are unreachable, and some named sets are dead legacy. Oni's
   `run_clean*` cells still exist but his RUN draws `owalk7-9`, so measuring `run_clean` told
   us nothing.
2. **Measure each cell PER COLUMN**, not per cell:
   - `contact` = the lowest solid pixel in the whole cell
   - `bodyLow` = the lowest solid pixel within the middle 40% of the figure's columns
   - `support%` = share of columns whose lowest pixel is within 3px of `contact`
3. **Flag** `contact < footY-8` (whole frame floats) or
   `bodyLow < footY-12 && support < 30` (only a weapon touches the floor).

**A whole-cell "lowest ink vs footY" check misses the bug.** Oni's `kneel` read **+1px** and
looked fine; per column, only x=96-120 reached the floor and *those columns are the club*. His
boots bottomed out at y=180-207 against footY=218 — he hovered up to **38px**, held up by the
kanabo.

**Convert to screen pixels before calling something broken.** Sheet px x `scale` is what the
player sees: 2px is **0.7-0.9px** on screen for every fighter. Anything at +2 is invisible.

---

## Fixed

| what | detail | commit |
|---|---|---|
| **Oni** crouch | `kneel` hovered up to 38px with only the club touching; also a standing stance, not a crouch. New `ocrouch` cell, feet pinned to footY, club held clear. Also wired to his landing squash. | `3429381` |
| **Executioner** heavy | `heavy_i1 +14, i2 +14, i3 +13` while `i4/i5` sat at `+2` — he bobbed up ~14px mid-swing then dropped. Packing offset; cells shifted down by their own offset (i3 capped at +11, real semi-transparent art reaches y=214). Now 0/0/+2/+2/+2. | `e79c86c` |
| **Ember** run | **0 of 8** frames planted, near-uniform 5-9px hover — he skated the whole cycle. All eight shifted down the SAME 5px to keep the stride's rise and fall. Now 4/8 planted, rest at +3/+4. | `875d3ef` |

Modifying existing cells (Executioner, Ember) always asserted: untouched cells byte-identical,
zero pixels with alpha >= 25 lost, each index carrying exactly one frame name.

---

## Run cycles — planted beats per stride

    Exile        8/8       Oni (owalk)  8/8       Executioner  2/8       Shin  2/8
    Mizu         1/8       Tsubasa      1/8       Kael         1/8
    Ember        0/8  <-- fixed

**Mizu, Tsubasa and Kael were checked and deliberately left alone.** They have real strides with
legitimate flight phases (Mizu `r4 +11`, `r8 +14`; Tsubasa `r3 +13`, `r7 +16`, both legs tucked)
and their contact beats land at **+2 — under one screen pixel.** The `1/8` reading is the `<=2px`
cutoff catching them exactly on the boundary, not floating. Ember was different in kind: 0/8 and
uniform.

---

## Verified as intentional — do not "fix" these

**Executioner special = a full somersault.** Read in order: wind-up `+18` -> launch `+43` ->
inverted `+6` -> apex tucked `+54` -> rotate `+43` -> **lands planted `+2`** -> recover `+15`.

**Kael special = a rising launcher.** Starts planted `+2` -> steps `+4` -> rises `+7/+8` ->
airborne `+19` -> peak `+60` -> descending `+38`.

Also correct: Shin's flying kicks, the airborne beat of several run cycles, Mizu's `special3`
(a teleport — smoke puff, legs tucked), and Ember/Shin/Exile frames flagged at 1-3px only
because a claw, shuriken or kusarigama hangs lower than the torso.

---

## Dead end: the Growing Kanabo cannot go on Oni's aerial heavy

His light (1.0 -> 2.25x straight up) and special (1.45x on contact) both carry the swell; the
heavy does not, and it cannot be composited on. Three isolation routes were tried:

- **Distance** — `grow()` takes the farthest ink from the centroid as the club tip. On these
  poses that is his **dangling foot**, so it stretched his leg.
- **Colour** — his garb and the club are both "void black" (7000+ px each, only ~900 grey px of
  studs). No threshold separates them.
- **By hand** — club axis read off a coordinate grid per cell. This *worked*, and then killed the
  idea outright:

| cell | grip -> tip | tip at 1.6x | headroom above |
|---|---|---|---|
| `oahv1` | (80,92) -> (182,15) | **(243, -31)** | 11px |
| `oahv2` | (82,98) -> (168,12) | **(220, -40)** | 8px |
| `oahv3` | (84,105) -> (150,8) | **(190, -50)** | 5px |
| `oahv4` | (88,96) -> (196,28) | **(261, -13)** | 14px |

The club points up-and-**back** in all four beats, so growing along its own axis drives the tip
13-50px through the top of the cell. **Root cause is the harvest window:** `f1-f17` is the
wind-up half of the swing, which was the only stretch where the clip's camera stayed locked. A
forward-extension beat with room to lengthen only exists in the zoomed section that took five
clips to fight. Adding the swell means re-shooting the move, not compositing.

---

## Also recorded

- **Ember is male (he/him).** Owner canon.
- **Ember's green slashes are a new look, by owner decision** ("I like them frames with the
  slashes the X slash and the three claw"). His shipped claw trails measure silver
  `rgb(193,194,192)` with zero green FX, so his older frames will not match. A procedural
  recolour was attempted and abandoned: the streak glow sits in the same green range as his garb
  (3232 garb px vs 979 mid-band), so no threshold separates them without draining his clothes.
  **Don't retry it.**
