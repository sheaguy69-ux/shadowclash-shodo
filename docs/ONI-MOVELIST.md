> Historical SHEET515 design. For the playable SHODO-EDITION kit, see [current Oni moves](ONI-CURRENT-SHODO-MOVES.md). The modes and several inputs below are retired.

# ONI — MOVELIST (Mode 1 & Mode 2)

**Owner ruling source:** Story Bible ("the Founder wrote all six disciplines") +
`Oni-Identity-True-Lock.md` + `RECOVERY/oni-founder/boards-aug9/` + the shipped
`web/assets/sprites/oni.json` (SHEET_V 515). This file is the ONE coherent statement of
his kit — the in-game list and the older handoffs drift, this is the reference.

## The design thesis

Oni is the founder of the clan, and every fighter down in the pit inherited exactly one
fragment of his art. So his own kit expresses **all six** — he is not a specialist, he is
the whole foundation, and each weapon family is a discipline the roster fragmented.

**The six weapons (and whose fragment each is):**

| # | Weapon | Inherited by | How Oni carries it |
|---|---|---|---|
| 1 | Tekko-kagi **claw** (right hand only) | Ember | worn on the right gauntlet — his signature |
| 2 | **Razor wire** (right hand) | Shin | wound at the hip — whip, shot, command grabs |
| 3 | **Twin knives** | Tsubasa | tucked at the sash — flurry + air-grab finish |
| 4 | **Katana** (long blade) | Executioner (the greatsword, retconned to one slim katana) | crossed on the back |
| 5 | **Bo staff** | Mizu | crossed on the back beside the katana |
| 6 | **Bare fists & feet** | the root discipline the six refine | always — his hands are wrapped, his left stays empty |

Two laws bind every move: **the claw is right-hand only** (never mirrored onto the left),
and **he does not draw steel without cause** — the katana and staff stay on his back until
a wire bind or a committed heavy earns the draw.

---

## MODE 1 — THE FOUNDER (base form)

Claw-first pressure, wire for reach and conversion, katana for the committed finish. This
is the form he fights in by default.

### Ground normals

| Input | Move | Art | Weapon | Notes |
|---|---|---|---|---|
| Light (F) | **Knife flurry** | `glneu1-6` | twin knives | six beats, short reach |
| Heavy (G) | **Katana chain** | `heavy_i1-5` | katana | 17 dmg, his neutral punish |
| Fwd + F | **Front cartwheel** | `glfwd1-6` | claw | the cartwheel's claw arc is an ACTIVE hitbox (owner filed it as a light attack, not evasion) |
| Back + F | **Backflip** | `glback1-6` | claw | evasive arc, active claw |
| Down + F | **Low sweep light** | `gldown1-6` | claw | low |
| Up + F | **Rising light** | `glup1-6` | claw | rising |
| Fwd + G | **Bo staff thrust** | `ghfwd1-6` | bo staff | 165px reach — the longest heavy, staff spacing |
| Back + G | **Reversal cut** | `ghback1-6` | katana | short reach, backward displacement |
| Up + G | **Rising launcher** | `ghup1-6` | katana | launches (launchVy −380) |
| Down + G | **Staff low sweep** | `ghdown1-6` | bo staff | 9 dmg, trips (low) |

### Specials (H)

| Input | Move | Art | Weapon | Notes |
|---|---|---|---|---|
| Special (H) | **Razor whip** (close) / **wire shot** (far) | `whip1-6` / `special1-6` | razor wire | 15 dmg close, 9 dmg far projectile — both open the wire bind |
| Fwd + H | **Wire lunge** | `gsfwd1-6` | razor wire | 28 dmg, long lunge |
| Up + H | **Rising wire** | `gsup1-6` | razor wire | 16 dmg, anti-air |
| Down + H | **Ground sweep special** | `gsdown1-6` | razor wire | 32 dmg |
| Back + H | **Back special** | `gsback1-6` | razor wire | 12 dmg |
| Air Down + H | **Smoke bomb** | smoke sheet | — | concealment, **max 2 per round** (owner cap, not a cooldown) |

### Command grabs — the razor-wire conversions (the "bind → weapon finish" system)

A successful bind ENABLES a weapon conversion. Each wire lands on a DIFFERENT weapon, which
is how all six stay in rotation mid-match:

| Grab | Finish | Weapon |
|---|---|---|
| Forward wire grab | **katana draw → slash** | katana |
| Reverse wire grab | **claw raise → claw rake** | claw |
| Air-to-air wire grab | **knife cross → dual slice** | twin knives |
| Air-to-ground pulley | **short-wire draw → slice** | razor wire |

### Multi-tap string (tap Light repeatedly)

**Knife flurry → body jab → rising upper** — `glneu` → `punch2` → `punch3`, the third
beat launches. The jab and upper are his **bare-fist** discipline surfacing inside the
string.

### Air & mobility

- **Neutral air light** = the claw whirl (`aneu1-6`), a full spin with the red arc.
- **Air heavies** = the `hfwd/hback/hup/hdown` board rows; **air specials** = `sfwd/sback/sup/sdown`.
- **Run** `runb1-8` · **dash** = the SOLID blur beats (1,2,5,6) · **roll** · **wall cling & jump** (clawed feet, not a hand hold).

---

## MODE 2 — THE FOUNDER'S JUDGEMENT (V toggle; P2: K)

Staff-forward and shadow. Bare `V` toggles it, grounded only. The four board move sets
stay live in BOTH forms — the mode never takes a move away, it only re-faces his neutrals
and his dash.

| Change | Mode 1 | Mode 2 |
|---|---|---|
| Neutral Light (F) | knife flurry (`glneu`) | **staff strike** (`bostrike1-6`) |
| Neutral Heavy (G) | katana chain (`heavy_i`) | **staff sweep** (`bosweep1-6`) |
| Multi-tap string | flurry → **punch2 → punch3** | staff → **kick2 → kick3** (rising crescent, launches) |
| Dash | solid beats 1,2,5,6 | **full shadow-dissolve** (all six `blur1-6`, red-black particulate) — "he does not move fast, he stops being solid" |

Directional normals (`gl*`, `gh*`), specials (`gs*`), the wire grabs, the smoke bomb
and the mobility kit are **identical in both forms**. The mode is a stance, not a separate
character — it changes the two neutral buttons and the dash read, nothing else.

---

## The six weapons in one pass

| Weapon | Where it lives |
|---|---|
| **Claw** | cartwheel, backflip, glup/gldown lights, the air whirl, reverse-grab rake |
| **Razor wire** | whip, fwd/up/down/back specials, all four command grabs |
| **Twin knives** | neutral light flurry, air-grab dual-slice finish |
| **Katana** | neutral heavy chain, up/back heavies, fwd-grab draw-slash finish |
| **Bo staff** | down+G sweep, and BOTH neutrals in Mode 2 |
| **Fists & feet** | the punch string (Mode 1), the kick string (Mode 2) |

## Settled vs still owed

**Settled** (verified, not open):

- **Claw on turn** — accepted: the engine's per-facing mirror swaps his claw hand when he
  turns, exactly like Kael's asymmetric long/short swords. "Never a mirrored claw error"
  is an art QC rule (the claw is drawn on his right hand in every cell), not a render-path
  requirement.
- **Dual claw vs single** — single, settled: his art, `Oni-Identity-True-Lock.md` and every
  prompt doc already read "RIGHT HAND CLAW ONLY · left hand wrapped, no claw". The old spec
  prose ("dual metal claws") was loose wording and is gone.
- **Wire-grab mannequin** — non-issue: measured, every wire conversion cell holds a single
  figure. The clean solo boards were packed, not the reference grab boards with the grey
  dummy.

**Still owed** (art — the owner's GPT draws it):

- **Broader shoulders** — he reads lanky (0.72 width/height vs a 1.9-2.5-shoulder cast).
  Mass must come from the DRAWING; x-stretch is outlawed engine-wide.
