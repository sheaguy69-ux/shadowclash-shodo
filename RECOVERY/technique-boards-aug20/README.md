# TECHNIQUE BOARDS — Aug 20 2026

Two labelled technique sheets from the owner's generator. **Archived, not packed.**
No sheet, no manifest key, SHEET_V stays 575.

These are a different kind of delivery from the 2172×724 action strips: each row is a
*named* technique with a written description, laid out as a reference document rather than
as production frames. That distinction decides what can be done with them — see the
resolution section.

---

## `executioner-long-katana-8rows.png` — 1536×1024, 8 rows, 56 frames

**This is the EXECUTIONER.** He was archived as `actionset-UNIDENTIFIED-horned-red-eye-dagger`
in `../new-style-actionsets-aug20/`; this board identifies him on three independent counts:

1. The board's title is **LONG KATANA**, and his `weapon:` is **Long Sword** — he is the
   only one-long-blade fighter on the roster.
2. Row 2 is **Chūdan-no-Kamae**, and the Executioner is the **only fighter in the game with
   `idle_chudan` art** (`idle_chudan`, `idle_chudan2` — nobody else has the key).
3. The horned hood matches his shipped silhouette.

Rename the action-set file once the owner confirms.

| # | row | frames | what it is |
|---|---|---|---|
| 1 | Ichi-no-Kamae | 6 | sword low and behind the hip — hides the blade's length, baits the swing |
| 2 | **Chūdan-no-Kamae** | 6 | centre stance, point at the throat — **the engine already has this** |
| 3 | Gedan-no-Kamae | 6 | point low at the ground, invites an overhead, answers rising |
| 4 | Kasumi-no-Kamae | 6 | "mist stance" — blade across the face, hides the attack angle |
| 5 | Horizontal Slash | 8 | level cut to the midsection |
| 6 | Diagonal Slash | 8 | high-to-low cut |
| 7 | Upward Slash | 8 | rising cut, launcher |
| 8 | Thrust (Choku-to) | 8 | straight pierce |

### The vocabulary is already the engine's vocabulary

This board is not proposing a new system. `modeKey()` already dispatches **four stance slots**
off the V key and two of them are *kamae by name*: **MUKI-KAMAE** (Up+V, the formless
attacking guard) and **SAYA-KAMAE** (Down+V, the grip switch). Chūdan is the Executioner's
existing offensive stance, owner-ordered Jul 31 2026, with art already on his sheet. So the
four kamae here map onto machinery that exists — this is art for a system already built,
which is the cheapest kind of delivery there is.

## `shin-taijutsu-4rows.png` — 1448×1086, 4 rows, 24 frames

**Shin**, unarmed — which matches his `weapon:` exactly: *Hand-to-Hand / Wire Tool*.

| # | row | frames |
|---|---|---|
| 1 | Light Punch Chain | 6 |
| 2 | Kick Combo | 6 |
| 3 | Body Rush Taijutsu | 6 |
| 4 | Flying Kick Special | 6 |

---

## ⛔ RESOLUTION — one of these is production art and one is a reference sheet

Measured body height (crown-to-sole, weapons excluded) against what each fighter needs to
avoid upscaling at 4K fullscreen (`docs/ART-REGEN-HANDOFF.md` §1):

| board | body height | needs | ratio | verdict |
|---|---|---|---|---|
| Executioner katana | **91–125px** (median 111) | 270px | **0.41×** | would need a **2.4× upscale** — this is a **design reference, not packable art** |
| Shin taijutsu | **155–208px** (median 196) | 250px | **0.78×** | needs a **1.28× upscale** — borderline, usable |

The difference is layout, not skill: 56 frames crammed into 1536px leaves each Executioner
about 111px of body, while the full-width strips he sent earlier (2172×724, one row of six)
carry **250–460px**. **Any technique from the katana board that is actually wanted in the
game has to come back as its own full-width strip.** The board stays as the reference the
strips get generated against — which is exactly what it is good at, since it names and
describes all eight techniques.

### Shin's 0.78× is not a coincidence

His run strip measured **0.79×** the idle on four independent proxies, and this board lands
at **0.78×**. The same offset twice, from two separate deliveries, means his non-idle art is
**systematically** drawn small — so one uniform correction of about **×1.28** covers his
whole non-idle output rather than needing a per-batch measurement. Per §2 law 2 and law 4
that correction is applied here at pack time, anchored on **head geometry**, as ONE uniform
scale per sequence — never per-cell MATCH_HEIGHT, and never by regenerating for size.

## Open owner call — the Executioner's palette moved

He ships **purple + orange with a yellow eye**. His new-look idle strip came back
**yellow-eyed**. This board is **purple/black + red with RED eyes**. Red eyes are Oni's tell
(white skull mask, three gouges), so two fighters converging on red is worth a decision
before 56 frames are generated against it.
