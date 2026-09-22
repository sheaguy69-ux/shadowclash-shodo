# ONI — FRAMES NEEDED

What a playable Oni still owes, measured against what the ENGINE actually reads and what
every shipped fighter actually supplies — not against a wish list.

**Method.** The required set was derived, not invented: every `F.<key>` the engine reads
in `web/index.html`, intersected with the manifests of all eight shipped fighters
(`web/assets/sprites/*.json`). A key that all eight carry is genuinely required; a key
only one carries is that fighter's private business.

Roster sizes for scale — executioner 328 cells, mokurai 259, shin 257, ember 252,
kael 247, tsubasa 200, mizu 188, exile 143. **Exile at 143 is the proof a fighter ships
well short of the biggest sheet.** Oni does not need 328 cells to be playable.

Sources for everything below: `RECOVERY/oni-founder/boards-aug9/` (25 files). Move names
are the owner's own captions — see `ONI-NEW-KIT-AUG9.md` for the kit itself.

---

## 1. THE FLOOR — 42 cells every fighter has

If a key here is missing, the engine draws the wrong pose or nothing.

| Group | Keys | Count | Covered by | Status |
|---|---|---|---|---|
| Idle | `idle`, `idle2` | 2 | states r1 idle | ✅ have |
| Run cycle | `run_clean1..8` | 8 | states r1 (run start/loop/accel/loop) + `board-run-dash-burst` (6) | ⚠️ **10 poses exist, need 8 CLEAN LOOPING** — see §4 |
| Jump / air | `jump`, `jump1`, `jump2`, `fall`, `fall2`, `air1..3` | 8 | states r3 + `board-basic-jump` + mobility r1 | ✅ have |
| Light chain | `light1..5` | 5 | moveset r1/r2 (jab, kicks, sweeps) | ✅ have |
| Heavy chain | `heavy_i1..5` | 5 | moveset r3 (claw strikes) | ✅ have |
| Special | `special1`, `special2` | 2 | specials r1 (energy gather/charge/burst) | ✅ have |
| Block | `block`, `block2` | 2 | `board-guard-impact` (6 poses) | ✅ have |
| Hurt | `hurt`, `hurt2`, `hurt3` | 3 | states r4 (light hit, air tumble ×2) | ✅ have |
| Crouch / roll | `kneel`, `roll` | 2 | states r2 (dodge roll), moveset r2 (deep crouch) | ✅ have |
| Wall | `wallslide` | 1 | states r2 wall cling ×2 | ✅ have — wall slab stripped |
| Kicks | `kheel`, `kpush`, `kstomp`, `ksweep` | 4 | moveset r1/r2 (axe kick, sweeps, low kick) | ✅ have |

**Floor verdict: covered.** Every one of the 42 has delivered art behind it. Oni can be
made playable from what already exists on disk.

---

## 2. THE DIRECTIONAL FAMILIES — what a full-depth fighter adds

Six-frame families that 6+ of the 8 fighters carry. These are the difference between
"playable" and "as deep as the rest of the cast."

| Family | Keys | Count | Delivered? |
|---|---|---|---|
| Fwd / back air | `afwd1..6`, `aback1..6` | 12 | ⚠️ partial — moveset r4 has fwd-air, back-air, up-air, cross-up, dive (5 of the beats) |
| Heavy directional | `hfwd1..6`, `hback1..6`, `hup1..6`, `hdown1..6` | 24 | ⚠️ partial — moveset r3 covers up (rising claw) and down (ground slam) |
| Special directional | `sfwd1..6`, `sback1..6`, `sup1..6`, `sdown1..6` | 24 | ⚠️ partial — specials sheet covers fwd dash, backstep, spiral ascent, stomp |
| Body attack | `attack_body1..6` | 6 | ⚠️ moveset r4 air lunge |
| Extra jump | `ajump1`, `ajump3..5` | 4 | ✅ mobility r1/r2 |

**Directional verdict: the MOVES exist, the 6-BEAT COVERAGE does not.** His sheets give
1–2 poses per direction where the engine's families want six. This is the single biggest
gap, and it is the difference between a fighter who works and one who feels finished.

---

## 3. WHAT HE HAS THAT NOBODY ELSE DOES

Delivered, kit-defining, and needing engine work rather than art:

- **Razor-wire command grabs** — 4 sequences × 6 (`MASTER-WIRE-GRABS-4x6`). Setup → bind →
  weapon conversion → finish → reset. ⚠️ **Every frame contains a grey dummy opponent**,
  so these are reference, not sprites, until his half is separated (an edit, not a redraw).
- **Mid-air smoke bomb** — max 2 per round (his rule), needs a per-round counter.
- **Wall cling on foot claws** — the pose exists; slab already stripped.
- **Second jump / somersault, backflip, front cartwheel, dodge roll** — all delivered as
  full 6–8 pose boards. The cartwheel is a **light attack**, not pure evasion.

---

## 4. THE ACTUAL SHOPPING LIST

Ordered by what unblocks the most. Nothing here is a redesign — it is coverage.

### A. Owed as ART (only a redraw can supply it)
1. **A clean 8-frame RUN LOOP that cycles.** Ten run/dash poses exist across the states
   sheet and the run board, but they are a dash *burst*, not a loop that closes on itself.
   A run that does not cycle reads as a limp. **Highest value single item.**
2. **The ambiguous-claw frames — 5 cells, named.** These read with talon mass on BOTH
   sides, i.e. the claw is unclear or a bare fist is drawn where it belongs. Mirroring
   cannot add a claw that was never drawn, so these are the only art the handedness
   problem actually costs:

   | Cell | thin-mass L / R |
   |---|---|
   | `r1_1_crouch_stance` | 150 / 167 |
   | `r1_5_prone_recover` | 211 / 168 |
   | `r1_7_axe_kick` | 276 / 228 |
   | `r3_3_claw_thrust1` | 449 / 411 |
   | `r3_7_rising_slash2` | 595 / 702 |

   Five frames out of thirty-two. The other 27 are already correct or corrected by
   mirroring, at no cost.
3. **6-beat fills for the directional families** (§2), if he wants Oni at full cast depth.
   Not needed to ship him playable.

### B. Owed as EDITS (already on disk, no spend)
4. **Strip the dummy from the wire sheet** — same technique that removed the wall slab.
5. **Re-cut row 4 of the moveset matrix.** `r4_4_air_lunge2` came out as a 74×133 fragment
   of pure speed lines: the cut boundary sliced a figure. The claw detector caught it.
6. **Split FX off the remaining attack cells** so arcs can be timed to the active window.

### C. Owed as a RULING (free, but only he can give it)
7. Nothing blocking. The mirror finding is **closed** — normalising to the reference
   (claw on the viewer's left = his right hand) satisfies the checklist, so
   `ctx.scale(-p.facing, 1)` is now a manifest flag rather than a canon violation.

---

## 5. WHAT IS NOT NEEDED

Guardrails, so this list does not grow on its own:

- **Not 328 cells.** Exile ships at 143. Match her, not the Executioner.
- **No idle-breath cycle beyond `idle`/`idle2`** — the engine's bob supplies the motion.
- **No per-mode anything.** The four-mode boss system is dead; one kit.
- **No new design work.** `Oni-Identity-True-Lock.md` is final — third redesign and the
  last. Anything that would change how he LOOKS is out of scope by owner ruling.
