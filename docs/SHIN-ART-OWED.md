# SHIN — EVERYTHING STILL OWED

Rewritten 21 Aug 2026 against **`SHEET_V 571`**. Sheet is `shin.png` / `shin.json`:
**520 × 370 px cells, 449 of them, footY 330, import scale 0.3431.** Next free cell: **449**.

---

## WHERE HE STANDS

| | rows | status |
|---|---|---|
| **FIRST MODE** | 42 | ✅ **DONE — 100 % board look, zero old-design cells reachable** |
| **SECOND MODE (Kage-Nui)** | 9 of 19 | ⚠️ attack rows only, and drawn on the OLD body |

First mode is finished. Everything below is second mode, plus five first-mode
*capabilities* the engine supports that he has no art for at all.

---

# ⛔ SECOND MODE — 10 ROWS / 62 CELLS MISSING

Tsubasa is the only other fighter with a second form, and hers is complete: **18 rows.**
Shin has **9** — the attacks and nothing else. Second mode currently borrows first mode's
idle, run, jump, crouch, roll and block, which is why he changes body the instant he
attacks in the stance.

| row | cells | what it is |
|---|---|---|
| `f2_idle` | **6** | the kunai stance at rest — a breathing loop, blades held |
| `f2_run` | **8** | running with the kunai out |
| `f2_jump` | **6** | vy-banded: launch / rise / apex / descend / fast-fall |
| `f2_crouch` | **6** | ducking in the stance — sink, deeper, hold that breathes |
| `f2_roll` | **6** | the shoulder roll, blades kept clear of the floor |
| `f2_block` | **6** | guard with the kunai crossed — raise, hold, impact |
| `f2_land` | **6** | the touchdown beat out of a jump |
| `f2_parry` | **6** | the catch — a reverse blade is held to catch, that is the whole point |
| `f2_dash` | **6** | the dash in stance |
| `f2_dashcut` | **6** | the dash that cuts on the way through |
| **TOTAL** | **62** | |

**No engine work is blocking these** — `shinF2Frame` currently only answers for light and
heavy. I extend it to read these rows the day they land; that is my job, not yours.

## ⛔ AND THE 9 ROWS HE ALREADY HAS ARE ON THE OLD BODY

Measured off the sheet:

| | saturation | grey scale-mail |
|---|---|---|
| board look (canon, all of first mode) | **0.803** | **5.9 %** |
| the nine locked `f2_` rows | 0.548 | 2.1 % |

That is the pre-armour body — same numbers as the old first-mode art I just retired. So
even once the 10 rows above land, **if they are drawn on the armoured body they will not
match the nine attack rows he already has.**

Three ways to close it, your call:

1. **Redraw the nine on the armoured body — 54 cells.** Total for second mode: **116 cells.**
   The only fully consistent answer.
2. **Draw the 10 new rows on the OLD body to match the nine.** Total: **62 cells.** Second
   mode becomes deliberately a different-looking Shin — which is defensible, it is a
   different stance with a different weapon.
3. **Draw the 10 on the armoured body and accept the mix** — 62 cells, and he changes build
   between his stance and his attacks.

**Option 2 is the least work and it is coherent.** Option 1 is the most work and the most
correct. I would not pick this for you.

---

# FIRST MODE — FINISHED, BUT FIVE CAPABILITIES HAVE NO ART

These are not broken — the engine falls back cleanly on all of them. They are things the
engine can already do that Shin cannot, because only Oni ever got the art drawn.

| row | cells | what it unlocks |
|---|---|---|
| `walljump` | **1–2** | the wall KICK-OFF. He has the cling; the push off the wall falls back to his jump pose |
| `blockhit` | **1** | upgrades his 2-beat guard to the 3-beat one (raise → hold → impact) |
| `grab` | **6–10** | **his own throw.** He can be thrown (`grabbed` is drawn) but has no animation for throwing someone |
| `getup` | **2** | wake-up from a knockdown |
| `slide` | **2–4** | a sliding move |

`grab` is the one I would actually draw. Every fighter throws, and right now his throw has
no picture of its own.

---

# THE SPEC — follow it exactly, it is not stylistic

Every rule below exists because breaking it cost a redraw.

**PAGE**
- **One MOVE per page.** ⛔ This is the rule that cost the most. A seven-row page forced every
  figure down to ~110 px and those six rows had to be **upscaled 74 %** — they are visibly
  bulkier and softer than everything else on the sheet, permanently.
- Page **2000–2200 px wide**, one horizontal row.
- Background **pure white `#FFFFFF`**. No panel boxes, no borders, no drop shadows.
- A title across the top is fine and is removed automatically — it must not touch a figure.
- **⛔ NO FRAME NUMBERS, NO CAPTIONS UNDER THE FIGURES.** They fall inside the cut and key
  onto the sheet as floating glyphs.

**THE FIGURES**
- **Each figure 300–450 px tall.** Everything comes in as a DOWNSCALE. Your standalone idle
  page was 305 px and needed no upscaling at all — that page is the quality bar.
- **A real white gutter of at least 40 px**, and nothing crosses it — not a fist, not a
  smear, not a spark. ⛔ On the SOKUYAKU KEN board the impact burst was drawn IN the gutter
  and the two legs touched through it.
- **⛔ ONE CHARACTER SIZE ACROSS THE ROW.** Head-to-heel constant, changing only because the
  pose crouches or extends.

**THE VIEW**
- Facing **LEFT** (right is fine too — a mirror is free — just say which).
- Clean 2D cel illustration: heavy black outlines, flat controlled shading. **Not pixel art.**
- **⛔ NO GROUND SHADOW, NO FLOOR LINE.** It keys as a grey streak welded under his feet and
  cannot be removed without cutting into the boots. The engine draws its own shadow.

**BEATS** — **wind-up → commit → CONTACT → follow-through → recovery → settle.** The CONTACT
beat is mandatory; missing contact beats killed three redraws.

---

# WHO HE IS

**FIRST MODE.** Lean, low-slung, in a signature **low coiled crouch**. Dark green hood and
tattered skirt over **GREY GUNMETAL SCALE-MAIL** — sleeves, shoulder plate, knee and shin
plates. Deep **teal scarf**. **Wrapped fists — first mode is UNARMED.** **ICE-CYAN glowing
eyes**, featureless and angled, in a black faceless hood; **one eye in pure side profile is
correct and canon.** One four-point wire shuriken stowed on the hip.

**SECOND MODE (KAGE-NUI).** Same fighter, **kunai in both hands** — leaf-shaped black iron
blade with a **ring pommel** (one move hooks a guard with it, so it must read the same in
every frame). Gold/tan bandage wraps on forearms and shins.

**⛔ NEVER:** purple, orange. No sword, katana, staff or claws. No standing-tall posture.

**SCALE ANCHOR (measured):** his standing guard is **193 px** tall inside the cell.

---

# ON DELIVERY

Each page is cut, keyed at fuzz 42 %, registered against the 193 px band and appended from
cell **449** — append-only, existing cells byte-identical. Every row ships with a montage and
a GIF at game cadence before the sheet is touched.

⛔ **Wire against KEY NAMES, never cell numbers.** The sheet has been re-indexed once and the
frame has grown twice; the second-mode rows moved from 204–257 to **197–250**. Any document
quoting cell integers is already stale.
