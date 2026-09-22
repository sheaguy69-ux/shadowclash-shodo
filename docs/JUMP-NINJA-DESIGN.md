# Jump arcs → ninja movements — design brief (brainstorming-skill format)

**STATUS: design only, nothing implemented.** Owner order (Jul 28): "improvement
to the jumping frames more like ninja movements." Reference: his own training
folder, `ref_08` (chibi ninja jump/flip strip), frame-analyzed.

## Understanding summary

- **What:** re-read the six's jump arcs (launch → apex → fall → landing) in
  classic ninja-jump vocabulary.
- **Why:** today's apex is ONE static cell held through the top of the arc; a
  ninja jump is a *rotation* — the flip is the signature.
- **Who:** the six (original roster). Mokurai, Exile keep their custom
  arcs (Mokurai's bjump set) — out of scope unless
  owner says otherwise.
- **The vocabulary (from ref_08):** elongated diagonal launch drive → tuck-in
  → open-limbed spin through the apex → inversion at true apex → open-out
  into descent → absorbed landing. Five beats; the game's current arc has
  launch/apex/fall/fall2/kneel — the middle three are where it falls short.
- **Explicit non-goals:** no physics changes (gravity, velocity, jump height
  stay as owner-tuned), no new art spend unless owner picks it, no changes to
  the landing kneel.

## Assumptions (marked)

1. "Ninja movements" means the ref_08 vocabulary above (his own reference).
2. $0-first is preferred; art spend only if the $0 version reads flat in motion.
3. Scope = the original six; wave-2 fighters untouched.

## Approaches

### A. APEX SPIN SEQUENCE — physics-mapped rotation, $0 (RECOMMENDED)
The apex vy-band stops holding one cell and instead plays a 3-beat rotation
mapped to vertical velocity — no timers, pure physics:
- vy ∈ [-260, -40): tuck-in (curl into the spin)
- vy ∈ [-40, +40): inversion (the true apex flip moment)
- vy ∈ [+40, +430): open-out, then existing fall/fall2

Cells come from each fighter's own sheet (verified to exist, same family):
- Executioner [jump2=60, air2=47, fall2=61]
- Mizu [air2=47, fall2=51, air1=46]
- Shin [air2=53, fall2=60, air1=52]
- Tsubasa [jump2=53, air2=47, fall2=54]
- Ember [44, air2=38, air1=37]
- Kael [jump2=53, air2=47, fall2=54]

Engine: one branch in the JUMP case of spriteFrameIndex; falls back to the
static jump2 if a cell is missing. Risk: cell-sharing between apex and
air-attack frames (accepted practice — manifests already dupe elsewhere).
Launch (jump1) and landing (kneel) already read right.

### B. GENERATED SPIN STRIPS (~$0.40-1.20)
3 true spin-angle cells per fighter (nano-banana stills off each idle, ~18
stills ≈ $0.36, or Seedance clips). Best fidelity to ref_08, but costs money,
needs the owner's art gate, and takes a pack/verify cycle per fighter.

### C. PROCEDURAL ROTATION ($0)
ctx.rotate the sprite through the apex. Zero art, but rotating a cel sprite
reads blurry/cheap against the game's crisp flat-cel look. Not recommended.

## Decision log

1. **Apex = rotation, not a held cell** — the whole point of the reference;
   chosen over "better static poses" (a better photo is still a photo).
2. **Physics-mapped beats (vy bands), not timers** — no new state to desync;
   rotation speed tracks the jump for free. Alternative (per-jump timer)
   rejected as more machinery for the same read.
3. **Own-sheet cells first (A), generated art only if A fails in motion (B)** —
   the tumble/flip cells already exist on every sheet; spending before seeing
   them in motion violates YAGNI.
4. **C rejected** — procedural rotation fights the art style.

## NFR

- Performance: same draw count (cell selection only).
- Reliability: vy-band logic untouched; static fallback if any cell missing.
- Maintenance: one engine branch + this doc + SHEET_V entry.
- Verification: harness jump-arc cell traces per fighter (the same rig used
  for the 238 repairs), then owner motion check before commit.

## Decision needed

Owner picks: **A** (recommended, $0, now) / **B** (art spend, higher
fidelity) / **C** (rejected). A goes through the standard gate: harness
verification → owner motion check → commit.
