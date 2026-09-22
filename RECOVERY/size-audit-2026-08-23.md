# SIZE AUDIT — every fighter, every frame, vs the Story Bible (Aug 23 2026)

**Owner request:** scan every character's frames, list everything sized up incorrectly, referenced to the Story Bible.

**What was measured:** all 9 sheets, every cell, on the live build `:9100` (SHADOWCLASH-RECOVERED @ SHEET_V 619, head edbb2df), cross-checked against shadowclash-fable-5 @ SHEET_V 645. Every number below is on-screen pixels at game scale: `(footY − topInk) × scale`, the same convention the owner's 645 verification used.

**Canon cited (Story Bible, `shadowclash-story-bible.md` lines 160–173 + CLAUDE.md):**
- The Executioner is the OLDEST and TALLEST of the six, *slightly* — a visible ~2–3px margin over #2; Kael is the youngest (the two bracket the cast); Oni is the one who towers; Mizu is shortest. This constrains `scale`, not just prose.
- Aug-2 measured idle baselines: exec 70.4 · kael 70.0 · tsubasa 69.6 · ember 69.3 · shin 66.6 · mizu 62.4.
- Uniform per-fighter scale (Ember recipe / convergence law): every cell of a fighter is drawn at the same scale; a cell whose body differs from the idle by more than pose allows is wrong. Owner's own rule (sheet entry 228): *"Shorter figure AND smaller head means the pack is wrong."*
- Poses that legitimately shrink the *body* (crouch, roll, tuck, kneel, hurt, grabbed, chain-ball wind-up) keep the HEAD at idle size. Cells flagged below have BOTH the body and the head off — that is the owner's "smaller version of them" signature.

**Method notes:** FX auras (ember echarge/espec), blades passing the head zone (exec xsuso6), wide-swing silhouettes (exile xheavy4, oni aback2) were silhouette-checked and excluded where the head stayed at idle size. Airborne cells (floating above the foot line) are pose-expected; grounded cells with feet planted are the ones that count.

---

## 1. ROSTER LEVEL — the six are on canon; two outsiders need a ruling

Served build (RECOVERED @ 619): **exec 71.9 > kael 69.6 ≈ tsubasa 69.6 > ember 68.3 > shin 66.6 > mizu 62.4** — order intact, Exec leads by ~2.3px (canon wants ~2–3px visible margin ✓), Oni towers at 87.5 ✓, Mizu shortest ✓. The Aug-23 619 sweep already fixed this; fable-5 @ 645 still has the eroded margins (exec 71.9 · kael 68.4 · tsubasa 68.2 · ember 67.3).

⚠ **EXILE renders 72.3px — TALLER than the Executioner (71.9).** The Bible law is scoped to "the six," so this is only a violation if the owner intends the Executioner to be the tallest figure in the cast besides Oni. Needs one ruling.
⚠ **MOKURAI 69.5** sits between Kael and Ember — above Tsubasa/Ember/Shin/Mizu. Not one of the six, so no violation, but noteworthy on the roster silhouette.

---

## 2. EXECUTIONER (idle 71.9) — "halving" still lives in xkiriage; glup only fixed on one tree

**CONFIRMED HALF-SIZE (feet planted, standing figure, head shrunk):**

| cells | RECOVERED | fable-5 | read |
|---|---|---|---|
| `xkiriage1-3,8` (rising cut) | 48.7 / 55.4 / 59.4 / 54.8 (0.68–0.83x) | **39.0 / 34.5 / 42.0 / 38.8 (0.48–0.58x)** | LIVE — his rising cut is still two sizes; beats 1–3+8 shrink to ½–⅔, beat 5 balloons to 100px (1.39x) on RECOVERED |
| `xnukiuchi8` (iai draw, beat 8) | 49.2 (0.68x) | 49.2 | LIVE — last draw beat a third short |
| `special2`, `special7` | 52.4 / 51.1 (0.72x) | same | his special row runs ~0.72x idle |
| `xtsuki1-3` (thrust) | 51.6–54.8 (0.72–0.76x) | same | LIVE |
| `xslip1`,`xslip6` (dodge) | 55.4–55.6 (0.77x) | same | LIVE |
| `xcdownh3` | 56.2 (0.78x) | same | LIVE |
| `glfwd1` / `light1` | 54.0 / 54.5 (0.75–0.76x) | same | forward-lean borderline |

**DEAD keys, wrong art only (not visible until wired):** `xgkamae1-4,6,7` (0.42–0.60x standing figures, ink ends 143px above footY → they would float ~38px in the air), `xitto2/3/5` (41–48px), `xgedan1/7` (42–46px).

**OVERSIZE:**
- `glup6`: **RECOVERED 76.7 (fine) / fable-5 128.4 (1.79x)** — the 645 re-cut only landed on fable-5; this tree's glup6 is the beat-5 hold until the grown-frame sheet is adopted. `glup7` fable-5 104.3 (1.44x).
- `xsuso3 → xsuso6` spans 48 → 108px in one move (chamber vs blade peak; blade accounts for most — pose).
- `heavy1` 86.9 (1.2x, overhead wind-up — pose).

---

## 3. ONI (idle 87.5) — the air kit is the resize that's left (both trees)

- `airidle` **139.8px on-screen** — body 113px = **1.29x his ground idle** (hover pose cannot explain a 29% bigger body); `aback2/4` ~140px (1.6x incl. hover). On RECOVERED `aback2` is 87.5 = the known idle-copy defect (Opus 5 drift plate).
- `aneu1/4/5`, `afwd4/5`, `aspin4/5` — **48.3px = 0.55x idle** (both trees).
- **His air kit spans 0.55x → 1.6x (a 2.9x range).** The 645 fix flattened his ground run; the air kit was untouched.
- `ghup3` 106.3 (1.21x), `ghup4` **131.9 (1.51x, feet planted)** — ground up-heavy row oversized on both trees.
- `special5`/`sneu5`/`whip5` 63.1 (0.72x).

---

## 4. EMBER (idle ~67–68) — the new gk_ down row is oversized (both trees)

- `gk_asdown2` **118.2 / 119.9px = 1.76x** (feet planted), `gk_adown4` **105.8 / 107.3 = 1.57x**, `gk_adown5` 90.4 / 91.7 = 1.34x.
- These are the "new friends" art — exactly the cells the owner's rule ("if they're too big, re-scale to the proper size") applies to. **The gk down row needs re-scaling to ~1.0x idle.**
- `ehook4` 122.6px but airborne (floats 63px) — leaping hook, pose, OK.
- `echarge5` 88.7 / `espec3` 96.1 — energy aura inflates the measurement; needs a montage before judging.
- Everything else (elight/eheavy/gk run/neutral rows) is size-consistent.

---

## 5. EXILE (idle 72.3) — down-heavy row oversized (both trees)

- `hdown3` **116.7px = 1.61x** (feet planted), `hdown1` 87.3 (1.2x), `xheavy4` 91.5 (1.27x).
- `xgrap8` 113.9px but the chain sinks 27px below the floor line (body normal — pose).
- `heavy_i3/4` 41.1px (0.57x) — chain-ball wind-up crouch with a full-size head = legitimate crouch, cleared.

---

## 6. MIZU (idle 62.4–64.8) — down-special row oversized (both trees)

- `sdown4` **112.0 / 107.9px = 1.73x** (feet planted), `sdown5` 89.6 / 86.3 (1.38x).
- `bolow5` 30.8 (0.48x) — low poke, head normal → pose, cleared. `hb_*` cells are FX techniques — excluded.

---

## 7. Smaller flags (both trees, same numbers)

- **SHIN** — `ghup3` 91.5 (1.37x, head also +23%), `kpush2` 85.9 (1.29x). Otherwise clean (converged art is consistent).
- **TSUBASA** — `sup1` 43.3 (0.63x) — super opening beat a third short (sup4/5 are 72px, normal); `divecut4` 85.1 (1.25x, leap — pose); `grabbed7/8` head +57% wide — victim+attacker share the cell (pose, cleared).
- **MOKURAI** — `dbell5` 27.1 (0.39x — tiny grounded cell, both trees); `dbell4` floats 50px (broken anchor); `bair1` 84.5 (1.22x spin).
- **KAEL** — clean; note `crouch_1` is 68px = full idle height (a real crouch should read ~50px like `crouch_2` at 51.9) — verify it's not a standing placeholder.

---

## 8. Priority order for the correction pass

1. **Ember gk down row** (1.34–1.76x) — re-scale to idle; the owner's "re-scale the too-big ones" order applies directly.
2. **Oni air kit** (0.55x → 1.6x span) — anchor airidle/aback to idle; re-scale aneu/afwd/aspin up.
3. **Executioner xkiriage** (halves on fable-5; 0.68–1.39x span on RECOVERED) — one row, two trees, both wrong. This was the row Opus 5's drift review left "never verified" — now verified broken.
4. **Exile hdown row** (1.2–1.61x) and **Mizu sdown row** (1.38–1.73x).
5. **Oni ghup3/4** (1.21–1.51x) — ground up-heavy.
6. **Roster ruling:** Exile (72.3) taller than the Executioner (71.9); Mokurai (69.5) between Kael and Ember.
7. Small flags: exec xnukiuchi8/special/xtsuki/xslip (0.68–0.77x), tsubasa sup1, shin ghup3/kpush2, mokurai dbell5, kael crouch_1.
8. **fable-5's glup6/7** (128.4/104.3) are fixed on RECOVERED but still oversized on that tree — whichever tree wins, the other's copy should adopt.

— DeepSeek reviewer, 2026-08-24
