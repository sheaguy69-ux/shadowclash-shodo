# K3 MANDATORY ANIMATION & PHYSICS PROTOCOL

**Source:** owner directive, 2026-07-29 (verbatim, pasted to K3 in session).
**Scope:** ALL sprite frame arrays / animation work for any Shinobi character,
from this date forward. Reviewers (Fabel) may hold frame work to this.

> When generating, calculating, or updating sprite frame arrays and animations
> for any Shinobi character, you MUST adhere to real-world martial arts
> physics and classic 2D animation mechanics:

## 1. ANATOMICAL KINETIC CHAIN

- Striking moves must show momentum origin (feet/hips) before limb extension.
- Weapons (Bō, Katana, Tekkō-kagi) must follow arc trajectories with proper
  weight leading the swing.

## 2. NON-LINEAR TIMING (WEIGHT & IMPACT)

- NEVER use evenly spaced linear timing.
- Follow the 4-Phase Rule:
  - **Phase 1 — Wind-up / Telegraph:** low velocity, 2–3 frames
  - **Phase 2 — Action / Thrust:** high velocity, 1 frame
  - **Phase 3 — Hit-Stop / Extension:** freeze / impact frame
  - **Phase 4 — Follow-through / Recoil:** easing recovery, 2–4 frames

## 3. DISCIPLINE ACCURACY

- **Shin (Taijutsu):** grounded footwork, crisp snaps.
- **Kael (Niten Ichi-ryū):** asymmetrical posture (short blade guarding, long
  blade attacking).
- **Tsubasa (Tantōjutsu):** low stance, reverse-grip wrist tilts.
- **Executor (Iaijutsu):** deep knee bends, instant unsheathing snap.
- **Ember (Tekkō-kagi):** feral crouch, wide claw arcs.
- **Mizu (Bōjutsu):** pole-vault leverage, two-handed staff rotation.
  (owner's roster script says "Miza"; engine key is `mizu`)

---

## K3 implementation notes (how this maps onto the existing engine)

- Phase 3 hit-stop is already an engine law: impact holds land at
  ~0.245–0.585 of the swing's exposure (the "exposure law" used in the
  heavy-attack audits). New frame arrays keep that — the freeze frame sits
  inside that band, never at uniform spacing.
- Phases 1/4 frame counts are expressed through the JSON frame arrays +
  per-move `frameRate`/`speed` fields: wind-up and recovery get the repeated /
  longer-exposed cells, the action frame gets exactly one.
- Chibi jump rules (owner, earlier session) still govern aerials and stack
  with this protocol: takeoff squash (vy < -380), tight-ball tuck on
  rotations, apex pose-hold (widened -75..75 band), bouncy 2/3-point landing.
- The bujutsu metadata pass (SHEET_V 266) wrote `weapon_type` /
  `martial_art_discipline` / `discipline_notes` into the six manifests as
  inert metadata. Its `animations` frame arrays are illustrative only — the
  engine reads none of that block. Any REAL technique build (Iai quick-draw,
  blade-trap parry, vaulting staff slam, etc.) is engine work and must be
  sequenced per this protocol, then harness-verified before the owner's
  motion gate.
