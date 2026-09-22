> ⛔ **SUPERSEDED IN PART — see [`../../CLEAN-SLATE-AUG21.md`](../../CLEAN-SLATE-AUG21.md).**
> Owner ruling Aug 21: **every frame before today is invalid** and the whole roster is being
> redrawn. The `×0.851` / `×0.636` "pack-ready" downscales below were computed against the
> OLD cell geometry, which is being replaced — **do not pack those files.** The live target is
> the 4K minimum (Kael 260px). The measurements and canon findings on this page still hold.

# AUG 21 BATCH — Kael's correction + 12 Executioner katana strips

Archived, not packed. SHEET_V stays 575.

## ✅ `kael-CORRECTED-long-short-8f.png` — the correction landed

Owner: *"kael correction."* The flag it answers: his earlier idle strip drew a single sword
out and a second sheathed, **both reading full-length**, where canon is **one long + one
short**.

**Fixed, and confirmed by eye on the frames where both blades clear the body** (beats 1 and
8): one long gently-curved katana reaching well past his stance, and a distinctly shorter
blade held high. Measured short/long ratio on those beats is **0.38–0.49**. Treat the exact
number as indicative rather than precise — the blade detector splits a sword at the hand
guard, so per-beat lengths are noisy; the *canon* call was made by looking, not by the
metric.

| check | result |
|---|---|
| beats | 8 |
| body height | 201px |
| background corner | 253 — fuzz-42 lifts it |
| edge contact | none |
| **vs his current cell** (idle body 171px) | **×0.851 → `kael-CORRECTED-PACKREADY.png`** |
| vs the 4K minimum (260px) | 0.77× — under, if the sheet is ever rebuilt bigger |

`kael-CORRECTED-PACKREADY.png` is the same strip at his current cell scale, one uniform
factor across all eight beats (§2 law 2), ready to pack.

## The 12 Executioner katana strips — the layout lesson landed

These came back as **full-width 2172×724 strips instead of a board**, and it shows: body
heights **196–267px** against ~111px on the boards. Same generator, same character — fewer
frames per image is the whole difference.

Still open on them:

- **⛔ Three have ink touching the frame edge** — an automatic REDO under §3's no-straight-
  cutoffs rule. `70a20…` RIGHT 12px on beat 8, `8d639…` RIGHT 12px on beat 8, `e238b…` LEFT
  6px on beat 1 and RIGHT 4px on beat 8. Small, and it looks like a blade tip rather than
  body, but it is a cut. Re-render those three with more margin.
- **`executioner-katana-BOARD-1535.png` is still a board** (1535×1024, bodies ~97px, 0.36× of
  his 270px target). Reference only — not packable.
- **They are still purple/red and horned.** Horns are correct (owner ruling: horns are his).
  The palette is the open question — he ships purple + orange with a yellow eye, and today's
  gold batch was a third variant.
- **They are not named yet.** Each is a technique from the katana board (four kamae, four
  slashes) but the mapping needs a look before they are keyed.

---

## Later Aug 21 — two more Kael assets

### ✅ `kael-twinblade-string-8f.png` — the first asset on the roster to clear the 4K bar

An 8-beat twin-blade attack string, numbered, with gold slash arcs. **Long and short blade
both drawn and clearly different** on beats 1, 3, 5 and 8 — the correction holds here too.

| check | result |
|---|---|
| size / beats | 2170×725, 8 |
| background corner | 253 |
| edge contact | **none** |
| body heights | `[250, 315, 238, 284, 305, 255, 374, 241]` |
| median body | **269px** |
| footY drift | 6px |
| **vs the 4K minimum (260px)** | **1.03× — PASSES.** First Kael asset that does. |
| vs his current cell (171px) | ×0.636 → `kael-twinblade-PACKREADY.png` |

The 48% height spread is **pose and FX, not boil** — beat 7 is the double-arc climax and its
ink box is inflated by the FX, not by a bigger fighter (footY holds within 6px across all
eight). Per §2 law 2 it takes ONE uniform scale for the whole string, which is what the
pack-ready file does.

### `kael-TACHI-SEIHO-1-3-board.png` — named techniques, and the layout trend is improving

Three named sword techniques at 6 beats each: **1. Sassen** (fingertip / pushing the tip),
**2. Hasso Hidari**, **3. Hasso Migi**. Same shape of document as the Executioner's katana
board — a reference that names what it draws.

| row | figs | median body | vs 260px |
|---|---:|---:|---:|
| 1. Sassen | 6 | 182px | 0.70× |
| 2. Hasso Hidari | 6 | 185px | 0.71× |
| 3. Hasso Migi | 6 | 184px | 0.71× |

**0.71× — still under, but the trend is right.** 18 frames in 1491×1055 gives 184px where the
Executioner's 56-frame boards gave ~111px (0.41×). Fewer frames per image is doing exactly
what was predicted. To pack these, each technique wants its own full-width strip — the same
generator's strips are landing at 269px.

---

## Aug 21 — KAEL, NITEN ICHI-RYŪ KODACHI SEIHO 1–7

Three boards, **7 named techniques × 6 beats = 42 frames.** Archived, not packed.

| # | technique | what the board says it does |
|---|---|---|
| 1 | **SASSO** | enter off-line under an overhead strike, jam the wrists or forearms, counter from inside |
| 2 | **CHUDAN** | compact middle guard, deflect on the centerline, advance into the dead angle for a throat or chest strike |
| 3 | **UKE KIRI** | receive on the short blade or guard, let the enemy blade slide past, counter with an immediate upward or diagonal cut |
| 4 | **MUKE** | soft, open posture invites the attack; yield and let the cut miss, then step inside the recovery to finish |
| 5 | **TSURENAI** | refuse the blade bind, break rhythm and angle, pass the attacking arc, then strike the underarm or torso gap |
| 6 | **TSUKI KIRI** | drive a sharp irimi thrust to the throat or face, then instantly follow with a short clearing cut |
| 7 | **KENSEI** | project overwhelming forward intent to draw the desperate strike, enter inside the heavy blade, trap or deflect near the hilt, then deliver a final decisive centerline strike |

### ⛔ This is a curriculum for a kit the engine has ALREADY coded

`web/index.html:1328` sets `WEAPON_FX[5] = 'cross'` with the comment **"Kael — Niten
Ichi-ryū: short parries while long cuts, together."** The board's title is the engine's own
words. And his packed rows are **already six cells each**, matching the board's beat count
exactly:

| board technique | what already exists |
|---|---|
| 3. **UKE KIRI** | **`xparry1..6`** — this IS his shipped **Niten Parry** (Back+Special, `nitenAnim`, "wakizashi catches, katana answers"). Same move, drawn. |
| 1. **SASSO** | **`khigh1..6`** — his Up+Heavy **high parry** (`highParryAnim`). Same shape: take it high, counter from inside. |
| 2. **CHUDAN** | **`idle_niten1..2`** — his Niten stance, plus `klowp1..6` for the low answer. |
| 6. **TSUKI KIRI** | `kcut` / `ktrav` cover the thrust-and-travel shapes. |
| 7. **KENSEI** | closest is `kspin` (his neutral-Special spinning finisher) — a decisive ender. |
| 4. **MUKE** | **no existing row.** A yield-and-punish has no equivalent on him today. |
| 5. **TSURENAI** | **no existing art — and this is the real gap.** See below. |

### TSURENAI is the blade-lock row he has never had

"Refuse the blade bind" is a **blade lock**, and blade locks are live in the engine
(`LOCK_DUR = 1.15s`, the picker plays `lock1..N` at whatever count is packed). **Kael has
ZERO lock cells** — his only block art is `block` / `block2`. That is shopping-list item 6,
and this board is the first drawn material for it.

### Resolution — the trend holds, and the fix is the same

| board | frames | median body | vs Kael's 260px |
|---|---:|---:|---:|
| Seiho 1–3 | 18 | 178px | 0.68× |
| Seiho 4–6 | 18 | 175px | 0.67× |
| Seiho 7 (Kensei alone) | 6 | **205px** | **0.79×** |

Corner 250–253, **no edge contact on any of the three**. The single-technique board scores
best because it carries the fewest frames — the same relationship seen everywhere else
(56-frame boards 111px → 18-frame 175px → 6-frame 205px → **full-width 8-beat strip 269px,
which passes**). **One full-width strip per technique** and these all clear the bar.
