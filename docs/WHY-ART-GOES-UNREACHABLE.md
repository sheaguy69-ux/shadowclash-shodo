# WHY ART GOES UNREACHABLE — and how to make sure it never does

**2026-08-13.** Every cause below was found by MEASURING this engine, not by reading it.
Most were found on Oni in a single day. If you know these nine, you can look at a board
before it is drawn and say where it will live.

---

## FIRST: YOU DO NOT NEED TO RESET HIS MOVESET

Oni draws **222 of 293** packed cells and has **zero** orphan rows. The 71 that stay dark
are not broken:

- **51 are duplicates your own boards replaced.** His sheet still carries `light1-5`, a
  five-cell attack from before MASTER-LIGHT-DIR existed. `glneu1-6` replaced it. The old
  cells stay because **sheets are append-only** — the originals must remain byte-identical
  so nothing already shipped shifts. They are history, not waste.
- **The rest need a STATE, not a button** — being blocked, knocked down, on a wall. No
  press can create those; the fight does.

A reset would delete finished work and re-open bugs that are closed.

---

## THE NINE WAYS ART GOES DARK

### 1. THE INPUT IS ALREADY TAKEN
The most common, and the one that hid your directional lights. `Fwd/Back/Down + Light` was
hard-bound to the kick tier one layer *above* his art: it fired a one-cell pose and
`return`ed before the code that picks his six-beat rows ever ran. 18 cells, invisible.

**Tell:** two moves that should both exist, sharing one button.
**Prevent:** every new board gets its input named *before* it is drawn.

### 2. A FLAG IS SET THAT NOTHING READS
His razor whip set `whipAnim = true`, spawned its hitbox, dealt damage — and drew the
generic stub, because **no draw branch ever read the flag.** `F.whip` appeared zero times
in the entire file. The move worked; only the picture was missing.

**Tell:** the move does damage but looks like something else.
**Prevent:** a flag and its draw branch are one change, never two.

### 3. THE FALLBACK TRUNCATES
The shared resolver asked "does this sheet have `special7`?" — if yes take seven cells, if
no take **two**. Exact for a 7-row sheet, silently lossy for anything between. Oni has six.
He played 2 of 6 and was the only fighter on the roster it hit.

**Tell:** a move that plays a stubby fraction of what you drew.
**Prevent:** count the rows that exist; never hard-code a length.

### 4. BRANCH ORDER
A branch filed *after* one that already catches the state never runs, no matter how correct
it is. This file has re-taught that lesson at least four times.

**Tell:** correct-looking code that never executes.
**Prevent:** specific before general, always.

### 5. THE STATE IS SHORTER THAN THE ANIMATION
The attack state lives `recoveryTimer` seconds and that is **speed-taxed**; the animation
length was a flat number written as if it weren't. At speed 8 Oni kept 75% of his own
animation, so the last beats were *mathematically* unreachable — on hit and on whiff.
Exile kept 60%.

**Tell:** a move that hard-cuts to idle before it finishes.
**Prevent:** the state stretches to the art. Never the art to the state — squeezing the art
in makes everything play too fast, which is exactly what you caught me doing.

### 6. RANGE OR CONTEXT GATING
His neutral Special is the **whip** inside 132px and the **wire shot** outside it. Both are
correct; a test at one distance sees one of them and calls the other dead.

**Tell:** works sometimes, "broken" other times.
**Prevent:** this is a FEATURE — one button, two moves. See below.

### 7. SUPERSEDED AND ORPHANED AS BYTES
New art is appended and the *name* repoints to it. The old cells stay on the sheet forever.
Correct and unavoidable — but it means "unreached" and "broken" are not the same word.

### 8. NO KEY LEFT
His two bo-staff boards had no input at all — every light, heavy, special and air slot was
spoken for. Twelve cells with nowhere to go.

**Prevent:** the mechanisms below. There is always somewhere.

### 9. A PHYSICAL INPUT COLLISION
`W` is jump. So "hold up and attack" launches him and you get the **air** move. His
grounded up-attacks look dead unless you let the jump finish and press with up still held.
This one fooled me and I published it wrong before catching it.

---

## HOW TO GIVE ANY ART A HOME — the mechanisms this engine already has

Every one of these is already working in the game today. None needs new tech.

| mechanism | how it works | already used by |
|---|---|---|
| **Stance** | a key toggles a mode; light/heavy re-skin until you press it again | **Oni's bo on `V`**, Shin's Kage-Nui, Tsubasa's Sakate, the Executioner's chudan |
| **Stance + direction** | `V` + up/down/back/fwd = **four more slots per fighter** | the four approved stance techniques |
| **Range split** | one button, two moves, chosen by distance | Oni's whip vs wire shot |
| **Context split** | grounded vs airborne, **and the opponent's state too** | Oni's wire conversions: foe grounded → slice, foe airborne → knives |
| **Follow-up window** | a move CONNECTS and opens a window; pressing again inside it is a different move | Oni's whole wire-bind family — 4 conversions off one button |
| **Direction on the follow-up** | the window plus a held direction multiplies again | neutral → slice, fwd → katana, back → claw |
| **Dash / run cancel** | the same button while moving is a different move | Oni's lunge claw, Mokurai's headbutt |
| **Meter gate** | a move that only exists on a full bar | Mokurai's karma, Exile's Champion |
| **Charge / hold** | tap vs hold splits one key in two | `hold C+H` for bunshin |

**Do the arithmetic.** One fighter has 3 buttons × 5 directions × (ground/air) = 30 base
inputs. Add one stance and that doubles. Add a follow-up window with 5 directions and you
have room for 40+ distinct moves on four keys. **You will run out of drawings long before
you run out of inputs.**

---

## WHAT ACTUALLY NEEDS REDRAWING

**For Oni: nothing.** Not one cell. His moves all come out, all connect, and all draw their
own art.

**Roster-wide, genuinely homeless art is 25 cells**, and most of it isn't moves:

| fighter | row | cells | what it really is |
|---|---|---|---|
| Kael | `kcut` | 5 | a real cut sequence with no input — **the only true orphan move on the roster** |
| Ember | `espec1_v`–`espec5_v` | 15 | variant takes of his special; needs a look before wiring |
| Mokurai | `canon_*` | 4 | identity REFERENCE frames, not animation — never meant to play |
| Executioner | `heavy_smear` | 1 | a single smear frame |

And 18 cells the sheet already labels dead (`*_old`, `xstab2_headless_DO_NOT_USE`) that
should simply be deleted.

**The art wishes that remain for Oni are quality, not function:**

1. Five cells where the claw reads on BOTH hands — `r1_1_crouch_stance`,
   `r1_5_prone_recover`, `r1_7_axe_kick`, `r3_3_claw_thrust1`, `r3_7_rising_slash2`.
   His claw is the right hand only.
2. Broader shoulders — he measures 1.69 shoulder-widths-per-head against a 1.9–2.5 cast.
   This can only come from the drawing now: horizontal stretching is outlawed engine-wide.

Prompts for both are ready in `docs/GPT-ONI-BROAD-SHOULDERS-PROMPTS.md`.

---

## THE GUARD THAT STOPS ALL OF THIS RECURRING

```bash
python3 tools/audit_cell_coverage.py --ids 8
```

Drives every input, records what the game actually DREW, diffs it against the sheet, and
**exits non-zero if any packed cell cannot be reached.** Run it whenever a sheet changes or
the frame resolver is touched. It is the reason "unreachable" is now a thing that gets
caught in minutes instead of surviving three sheet versions.
