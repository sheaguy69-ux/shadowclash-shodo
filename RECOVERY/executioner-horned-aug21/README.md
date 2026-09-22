# EXECUTIONER — horned, Aug 21 2026

**The horns landed.** This is the re-render asked for in
`../new-style-actionsets-aug20/EXECUTIONER-add-horns-spec.png`. Ten strips.
Archived, not packed. SHEET_V stays 575.

Purple hood, two horns, red scarf, **yellow eyes**, ONE long katana. The yellow eye matches
his shipped art — the red-eyed take on the earlier technique board is superseded by this.

## Measured

| file | beats | body px | vs 270 (4K) | → current cell | foot drift | edge |
|---|---:|---:|---:|---:|---:|---|
| `exec-horned-1` | 8 | 215 | 0.80× | ×0.82 | 1px | ⛔ **RIGHT, body** |
| `exec-horned-2` | 8 | 235 | 0.87× | ×0.75 | 4px | clean |
| `exec-horned-3` | 8 | 214 | 0.79× | ×0.83 | 1px | ⛔ **RIGHT, body** |
| `exec-horned-4` | 8 | 210 | 0.78× | ×0.84 | 1px | clean |
| `exec-horned-5` | 6 | 203 | 0.75× | ×0.87 | 2px | clean |
| `exec-horned-6` | 6 | 267 | **0.99×** | ×0.66 | 0px | clean |
| `exec-horned-7` | 6 | 252 | 0.93× | ×0.70 | 0px | clean |
| `exec-horned-8` | 6 | 261 | 0.97× | ×0.68 | 19px | clean |
| `exec-horned-9` | 6 | 252 | 0.93× | ×0.70 | 1px | clean |
| `exec-horned-parry-8f` | 8 | 227 | 0.84× | ×0.78 | 8px | ⛔ **both sides, blade tips** |

All backgrounds key at fuzz-42 (darkest corner 251–253). **Facing LEFT throughout** — correct,
the engine mirrors for the right-facing fighter. **One katana in every beat** — his lock holds.

## ⛔ Three strips have ink cut at the image border

`exec-horned-1` and `exec-horned-3` lose 12px of **body/scarf** off the right edge — a figure
is sliced, which is an automatic REDO under the no-straight-cutoffs rule. `exec-horned-parry-8f`
clips **blade tips** on both sides (6px left, 4px right) — less severe, but still a cut.

The fix is framing, not redrawing: the same poses with margin around every figure. Everything
else in those strips is fine.

## Scale

Against his **current** cell (300×412, canonical idle body 177px) every strip is oversized and
takes a **downscale of ×0.66–×0.87** — one uniform factor per strip, never per-cell flattening.
Against a future 4K-ready sheet (270px body) they sit at 0.75–0.99×, so they are close but not
quite there; `exec-horned-6` at 0.99× is effectively on target and is the best scale reference
in the batch.

## ⛔ CORRECTION — his palette never went gold. The gold sightings were KAEL.

An earlier note flagged "the Executioner's palette moved three times in one day —
purple+orange, then RED eyes, then GOLD." That was wrong, and the gold half of it was a
misattribution. Measured accent colours:

| art | accent RGB | who |
|---|---|---|
| `exec-horned-1..9` | **164,12,3** — red | Executioner |
| `exec-horned-10` | **184,100,18** — orange | Executioner |
| the "gold" strips | 188,126,20 · 188,125,32 · 194,136,27 | **KAEL** — and one of them labels itself so |

So his real palette question is much narrower than reported: **red scarf or orange scarf.**
His shipped art is purple + orange, and `exec-horned-10` matches it. Yellow eyes are settled
across every strip in this batch.

**It still needs one ruling, because these two cannot share a sheet** — a row of red-scarf
cells next to a row of orange-scarf cells reads as two different fighters.

## `exec-horned-10` is the best frame reference in the whole batch

8 beats, median body **266px = 0.99×** the 4K target, **1px** of foot drift, background keys
clean. Its only fault is **11px of ink off the RIGHT edge** — the same framing slip as strips
1 and 3. Fix the framing and this is the size and quality every other strip should be held to.

## Not his — moved out

`extra-a` was delivered with this batch but is **KAEL**, and has been filed at
`../new-style-actionsets-aug20/kael/kael-dualblade-8f.png`. Three independent tells: the accent
measures **RGB 188,126,20 (gold)** where the Executioner's measures **164,12,3 (red)**; the eyes
are gold; there are **no horns**; and he carries **two blades, one long and one short**, which
is Kael's lock and a hard violation of the Executioner's single-long-sword lock.

---

## `exec-GEDAN-no-kamae-8f.png` — owner-named, Aug 21

**Owner's brief, verbatim:** *"Gedan-no-Kamae. Sword tip lowered near the ground. An upward,
sweeping slash to the legs or groin. Functions as an iron shield for the lower body while
baiting the opponent to strike high, leading to an upward deflection-thrust."*

The strip draws exactly that: low guard → tip to the floor → **the bait lands** (a detached
black slash comes in from above on beat 4) → he rises → upward sweep with the purple/orange
arc → the clash burst → blade high → recover.

| check | result |
|---|---|
| beats | **8 figures + 1 detached FX** (the incoming strike — art, not a figure) |
| foot line | **0px drift across all 8** — every figure on the same floor |
| edges | **CLEAN** — nothing touches a border |
| background | corner 253, keys at fuzz-42 |
| accent | **188,100,18 — orange**, matching `exec-horned-10` |
| scale | standing beats 205–261px, median ~234 = **0.87×** the 270px target |

Three beats measure 349–470px because **the sword arc is attached to the body**, so total ink
height lies there (§2 law 7). The standing beats are the scale signal.

### This is his SECOND Gedan take

`../new-style-actionsets-aug20/evening-batch/executioner-gedan-counter-8f.png` is the same
technique — duck under an overhead, rise into a counter-slash. Differences worth a ruling
before either packs:

| | evening-batch take | this take |
|---|---|---|
| accent | 198,150,79 (pale gold-ish) | **188,100,18 (orange)** |
| foot drift | 58px | **0px** |
| scale | 0.93× | 0.87× |
| the bait | a black arrow **annotation** | a drawn black **slash**, in-world |

**This take is the better animation** — dead-level footing and the incoming strike drawn as
real FX rather than a diagram marker. The earlier one is slightly larger. They cannot both
be `gedan`; pick one.

---

## `exec-CHUDAN-no-kamae-board-8f.png` — ⛔ this one collides with shipped code

**Owner's brief, verbatim:** *"Chūdan-no-Kamae. Sword held at center, pointing at the enemy's
throat. Fast, direct thrusting or lunging. Constantly controls the centerline. Any attack made
by the enemy is automatically deflected just by holding your ground."*

The art draws that last line literally: on beats 4–5 an incoming black slash strikes his
extended blade and throws a spark. **He deflects without doing anything.**

### The engine already has chudan, and it does the OPPOSITE

Chūdan is not a new stance here — it is his existing offensive stance on **V**, owner-ordered
Jul 31 2026, and he is the only fighter with the art (`idle_chudan`, `idle_chudan2`).
What it currently does:

| | shipped code | this brief |
|---|---|---|
| damage | `CHUDAN_DMG = 1.28` — +28% on committed swings | — |
| reach | `CHUDAN_REACH = 1.18` — +18% | "fast, direct thrusting or lunging" ✓ |
| **defence** | **`// no guard in chudan, no riposte`** ([index.html:2553]) | **"any attack is automatically deflected"** |

The shipped trade is recorded in the code as **"HITS HARDER, CANNOT BLOCK"**, and the engine
enforces it — `executeReprisal()` refuses outright while `chudan` is set, and the comment two
lines up says the stance exists so that *"giving up the guard to enter it is a real decision."*

**The brief inverts exactly that.** A stance that hits 28% harder, reaches 18% further AND
auto-deflects has no cost at all.

⛔ **This is an owner call and is deliberately not decided here.** Two readings:

1. **Flavour.** The text describes the real budo concept as art direction, and the shipped
   trade stands. Nothing changes; the frames pack as the chudan row.
2. **A spec change.** Chūdan gains an auto-deflect, and something else has to pay for it —
   drop `CHUDAN_DMG` back toward 1.0, or put the deflect on a cooldown the way the reverse
   grip's auto-parry already is (`SAYA_PARRY_CD = 1.6s`, "a property, not a wall").

Reading 2 has a ready-made pattern in the engine, so it is cheap if he wants it. But it is a
balance change to a shipped fighter, not an art note.

### Measured

8 figures, bodies 175–276px, **median 217 = 0.80×** the 270px target · foot drift **3px** ·
edges clean · corner keys fine.

⛔ **86,289 ink pixels of TITLE AND DESCRIPTION TEXT sit above the figures.** Baked-in text
keys as ink like anything else. The eight figures crop out cleanly — they sit on their own
floor line well below the text — but nothing on this image may be packed whole.

---

# ⛔ QC PASS — 13 agents, every one of the 80 beats read at zoom

Two independent adversarial checkers re-read the whole batch and **sustained both hard-lock
findings**. This section corrects three things I reported earlier from contact sheets rather
than per-beat zooms.

## Verdicts

| verdict | strips |
|---|---|
| **PACK** | `e2` (iai draw-cut) · `e6` (idle_waki) · `e7` (idle_chudan) |
| **OWNER-CALL** | `e4` · `e8` — rising diagonal cut (kiriage), clean but restyled |
| **REDO** | `e1` · `e3` · `e5` · `e9` · `extra-a` · `extra-b` |

## ⛔ Corrections to what I said earlier

1. **"One katana in every beat" was WRONG.** `e9` carries a **second bladed shaft** through the
   grip — full silver blade with a hamon and a tapered kissaki continuing to the RIGHT of the
   tsuba across his chest, so there is blade on **both sides of the guard**. Confirmed at 7× on
   all six beats. It is *not* batch-wide: the grips of all 80 beats were checked and only `e9`
   has it.
2. **"Facing LEFT in every beat" was WRONG.** `extra-b` is mixed — beats 4, 5, 6 face RIGHT, and
   beats 3, 7, 8 are three-quarter or dead front. `extra-a` faces RIGHT in all 8.
3. **I never checked GUTTER BLEED.** On `e1`, content crosses **6 of the 7 cell boundaries** —
   blade tips and the beat-5 fire beam overrun into neighbouring cells, so a fixed-pitch cut
   packs a fragment of the adjacent frame into each cell. Outer-edge checks miss this entirely.

## ⛔ Most of the REDOs need NO new art — they already have clean twins

Graded in isolation, six strips looked like six regenerations. Measured against each other:

- **`e2` IS `e1`'s row, uncut** — same motion, per-beat IoU 0.80–0.90. The iai draw-cut is
  already delivered clean.
- **`e7` IS `e9`'s row, without the second blade** — per-beat IoU 0.82–0.87. Chūdan is already
  delivered clean.

So only **`e3`** (beat-8 sword amputated by the canvas) and **`e5`** (beat 4 is **weaponless**,
and blade length swings 144→66px, a 2.2× change on a fixed object) genuinely need new art.
`extra-a` should simply be **dropped** — it is Kael, not him.

## ⛔ Coverage: 11 strips, 5 distinct motions, 3 usable rows out of 81

`executioner.json`'s 335 keys collapse to **81 row families**. This batch supplies five motions,
three of them usable: `idle_waki`, `idle_chudan`, the iai draw-cut, plus a jodan overhead and a
kiriage rising cut. **Chūdan was delivered three times and the iai twice.**

**What the batch contains none of:**

| missing | rows |
|---|---|
| locomotion | `run`, `run_clean1..8`, `erun1..8`, walk |
| airborne | `jump`, `ajump1..6`, `fall`, `air1..3`, `afwd1..6`, `aback1..6` |
| ground states | `crouch_1..4`, `roll_1..6`, `wallslide`, `kneel` |
| defence | `block`, `block2`, `xblkguard`, `xblkhit` |
| reactions | `hurt1..3`, `hdown/hback/hfwd`, `grabbed1..8` |
| directional heavies | `hneu`, `hfwd`, `hback`, `hdown` (only `hup` has candidates) |
| specials | `special1..7`, `sneu/sfwd/sback/sup/sdown1..6` |
| kicks / body | `kpush1..3`, `kstomp`, `ksweep`, `kheel`, `attack_body1..6` |
| light chain | `light1..5`, `xlight1..4` |
| noto | `xsheath1..6` — the batch has exactly **one** sheathed cell, `e2` beat 2 |

**Every one of the 11 strips is a standing sword pose or a sword swing.** There is not one cell
in the delivery that could serve a reaction, a jump or a step. Locomotion in particular cannot
come from stills at all (the Ember recipe) — that gap will not close from this generator.

## Batch-wide restyle facts — owner-calls, NOT defects

Measured, and consistent across all nine of his strips, so these are style decisions rather
than errors in any one file:

- **Accent hue 0.9–3.8 (RED)** against the shipped sheet's **18.9 (ORANGE)**.
- **ONE large round glowing eye.** The shipped fighter draws **TWO angled eyes** in the identical
  pure-left profile — this is not the single-profile-eye rule, which is **Shin's**, not his.
- **Sword material splits the batch** between strips — worth settling before packing any of them.

---

## `exec-DEFENSE-EVASION-board-4x8.png` — the gap-filler, with two conditions

**This is the row family the QC pass said the batch had none of.** Coverage listed *defence* —
`block`, `block2`, `xblkguard`, `xblkhit` — as supplied by zero strips. This board is four
named defensive techniques, 8 beats each:

| # | technique | owner's description |
|---|---|---|
| 1 | **Uke Nagashi** *(deflecting flow)* | turning the flat of the blade to skim an incoming strike away rather than meeting it |
| 2 | **Itto Giri Crouch** | drops entirely underneath a high downward (jodan) cut |
| 3 | **Taihen Evasion** | steps off the linear path of a thrust, letting their momentum carry them into empty space |
| 4 | **Sword Evasion & Jamming** | closes the gap to get *inside* the swinging arc, taking away their leverage |

### Condition 1 — a second figure was drawn into the board. **CUT — see NOGREY below.**

Beats alternate between HIM and a **grey opponent**. Owner, Aug 21: *"edit out the gray figure
in the image."* Done — `exec-DEFENSE-EVASION-board-4x8-NOGREY.png`.

**The opponent appears exactly 7 times**, measured cell by cell (see the census note below):

| row | technique | opponent beats | note |
|---|---|---|---|
| 1 | Uke Nagashi | **b2, b7** | b7 **shares its cell with him** — his thrust crosses the opponent |
| 2 | Itto Giri Crouch | **b2** | |
| 3 | Taihen Evasion | **b2, b4** | |
| 4 | Sword Evasion & Jamming | **b2, b7** | b7 **shares its cell with him** — the grapple |

Two cells in that list are NOT the opponent and stay:

- **Taihen b6** is HIM, drawn in a desaturated all-purple palette with **the horns present** and
  a purple eye instead of the yellow one. A palette variant, not the grey man.
- **the double cell labelled `5  5` in Sword Evasion** is **two Executioners** — both horned,
  both orange-sashed — clashing blades on the spark. No grey figure in it.

### How the cut was made — `cut_grey.py`, and what it did NOT touch

His orange sash, yellow eyes and purple hood all carry saturation, so for the five beats where
the opponent stands alone a flood of the *achromatic* ink from one seed stops at his own colour
by itself. The two shared cells each needed a rule:

- **Uke b7** — the only bridge between the two bodies is **his own thrusting blade**, drawn on
  top of the opponent. Barrier the blade and the flood cannot cross it *and* the katana
  survives; a vertical cut at the gap column x=1093 does the separation.
- **Jam b7** — body-to-body contact, no thin bridge. Separated on **value** instead: the
  opponent is mid-grey (lum 36–100), he is near-black.

A last pass takes the pale anti-alias rim, which sits at 240–251 against 253–255 paper — above
any sane ink threshold, which is why a first attempt left a visible ghost standing exactly
where the opponent had been.

**Parity, asserted by the script on every run:**

| | |
|---|---|
| pixels changed | 46,336 — **2.95%** of the image |
| changed outside the 7 opponent footprints | **0** *(assert)* |
| beat numbers, rule lines, title, left text column | **byte-identical** |
| chromatic (orange / yellow / purple) pixels changed | **185 of 51,931 = 0.36%** |

Those 185 are arc-root pixels where a purple trail met the deleted blade. **The purple arcs,
the speed lines and the clash spark all stay** — the order was the grey *figure*, and the arcs
are FX that also spill into his own cells (Uke b3 wears one).

**The one real loss, stated plainly:** in Uke b7 the last ~22px of his blade existed only as a
faint highlight painted *over* the opponent's chest — it had no art of its own. It goes with
him, and the blade is re-tapered to a point at the body edge rather than left blunt. His katana
in that beat is ~22px shorter than delivered. Nothing else of his changed.

Review sheet: `exec-DEFENSE-EVASION-nogrey-BEFORE-AFTER.png`.

*Why the census took a detour:* three attempts at classifying the 32 cells automatically all
disagreed with what opening the cells showed — the figures are **not** on an even 8-column
pitch, so any grid-based census is wrong. The table above was built by detecting the figures
(connected components + a warm-pixel test), not by assuming the grid.

### ⛔ Condition 2 — board resolution, again

Figure heights **80–169px, median 134 = 0.50×** the 270px he needs. It wants **×2.0**, which is
the same layout failure as the katana board (0.41×) and the Kael Tachi Seiho board (0.74×).
Four rows of eight inside 1517×1037 leaves each figure ~134px; his full-width strips carry
250–270px.

**As reference this board is excellent** — it names four techniques and shows the exchange,
which a single-figure strip cannot. As production art it is half the size it needs to be.
The techniques wanted in the game come back as their own full-width strips, one row of eight,
**him only, no grey opponent**.

---

## `exec-CHUDAN-no-kamae-board-8f.png` — ⛔ there is NO grey figure on this board

Asked to "do the same thing" here, and the honest answer is that the thing isn't there:
**all 8 beats are the Executioner alone.** Measured — every one of the eight figure components
carries **1,400–2,200 orange pixels**; not one is the grey man.

What IS foreign to him is **the enemy's incoming cut** — a black ink-brush slash falling in
from above on **beats 4 and 5**, meeting his blade on beat 5 in the parry spark. That is what
`exec-CHUDAN-no-kamae-board-8f-NOENEMY.png` removes, and only that. The original is untouched
and stays the reference for the deflect FX.

**The spark is HIS and it stays** — it is the deflection landing, and with the incoming blade
gone beats 4–5 read as *chūdan held, spark on the blade*: exactly the auto-deflect pose.

| | |
|---|---|
| removed | 7,372 px = **3.85%** of the board's ink |
| changed outside the two slash footprints | **0** *(assert)* |
| **orange pixels changed** | **0 of 15,148** *(assert)* |
| ink lost per figure | 7 figures **0**; the 8th loses 2,413 px, which is the slash merged into its component |

Two rules the script had to learn, both worth keeping for the next board:

- **the brush throws a trail of splatter dots** that the flood can't reach — they are their own
  tiny components. Sweeping every small grey component inside the slash footprint gets them…
- …**but the spark's black spikes are small grey components too.** Sweeping blind ate the spark
  (178 orange pixels moved). The sweep now skips anything within 35px of orange.

Script: `cut_chudan_enemy.py`. Review sheet: `exec-CHUDAN-noenemy-BEFORE-AFTER.png`.

### This board's text is the source of the deflect perk

> *"Constantly controls the centerline. **Any attack made by the enemy is automatically
> deflected just by holding your ground.**"*


---

## URONAME 1–5 — five 8-beat boards, Aug 21. **The first of his boards that are BIG ENOUGH.**

| # | board | beats | median body | vs his 270px | spread | verdict |
|---|---|---|---|---|---|---|
| 1 | `exec-URONAME1-kiriage-8f.png` — **Kiriage**, upward cut | 8 | **346px** | **1.28×** | 47% *(pose, not boil)* | **PASS** |
| 2 | `exec-URONAME2-tsuki-8f.png` — **Tsuki**, the thrust / lunge | 8 | **317px** | **1.17×** | 15% | **PASS** |
| 3 | `exec-URONAME3-nukiuchi-8f.png` — **Nukiuchi**, draw-and-cut | 8 | **386px** | **1.43×** | **9%** | **PASS — best of the batch** |
| 4 | `exec-URONAME4-gedan-deception-8f.png` — **Gedan Deception**, low bait to lunge | 8 | **361px** | **1.34×** | 25% | **PASS — and NEW** |
| 5 | `exec-URONAME5-metsubushi-8f.png` — **Metsubushi**, blinding powder + strike | 8 | **383px** | **1.42×** | 18% | **PASS, one condition** |

Body = hood crown (horns included) to the lowest ink in that figure's own columns, so a
raised blade is never counted as head. Spread is pose variation across an 8-beat technique,
which §2 law 4 says is **not** a scale signal — only same-pose frames compare by height, and
the tightest board here (Nukiuchi, 9%) is the one whose beats hold one stance.

**This is the layout finally working.** Every earlier board failed on size — the katana board
0.41×, Kael's Tachi Seihō 0.74×, the Defence & Evasion board 0.50×. Those were 4 rows of 8
inside one frame. These are **ONE row of 8 with the captions underneath**, and the figures get
the whole height: 1.17–1.43× of target instead of half of it. **Nothing here needs upscaling.**

### Batch-wide, measured

- **Accent hue 19.3–22.2° — ORANGE.** The shipped sheet is 18.9°. These match what ships, so
  the RED-vs-ORANGE question the Aug-21 strips opened (they measured 0.9–3.8° RED) **does not
  apply to this batch** — it is the same orange, and these can share a sheet with the roster.
- **ONE eye.** A single yellow flame in pure profile on all five boards. The shipped fighter
  draws **TWO angled eyes**. Still the owner's call, now standing on five more boards.
- **Horns on every beat**, purple hood, one long blade. Canon holds.
- **Background 252–253 corner** → fuzz-42 lifts it. **Edge contact: 0px** on four boards,
  **2px** on Tsuki. Clean.
- ⛔ **All five face RIGHT.** Every sprite in this game is authored facing **LEFT** and mirrored
  by `ctx.scale(-p.facing,1)`. **`-flop` before keying**, exactly as the Ghost Killer strips needed.

### What they actually add — three are REDRAWS, two are new

| board | maps to | new? |
|---|---|---|
| **Kiriage** | `xkiriage1-6` — his **Up+Heavy**, Gyaku Kesa | redraw, 6 → **8 beats** |
| **Tsuki** | `xtsuki1-3` / `xctsuki1-6` — his **Fwd+Heavy** Drive Stab + the chūdan thrust | redraw, → **8 beats** |
| **Nukiuchi** | `xnukiuchi1-6` — his **Back+Heavy** Iai Quick-Draw | redraw, 6 → **8 beats** |
| **Gedan Deception** | nothing | ⛔ **NEW** |
| **Metsubushi** | nothing | ⛔ **NEW — and a new MECHANIC** |

`dirCells` and the moveArt branch both collect `1..N`, not a fixed six, so an 8-beat row plays
whole with no engine change — the three redraws are a straight upgrade the moment they pack.

### ⛔ Gedan Deception is the SECOND deflect move

The deflect perk shipped (`1e6b2ca`) scoped to chūdan because chūdan was the only stance whose
canon text says it deflects, and the commit named **Gedan-no-Kamae** as one of the two waiting
on art. **This is that art.** Its beat 5 — *"upward/forward counter-thrust launches from the low
guard"* — is drawn with the orange clash spark, which is the deflect landing. When it packs,
`deflectsBlades` takes one more clause and the perk covers the gedan line too.

### ⛔ Metsubushi is a mechanic, not a move — and it needs a ruling

Blinding powder. Nothing in this engine blinds. Before it can be built the owner has to say what
"blinded" DOES: does the victim lose their sprite, lose their aim, take a stagger, eat guaranteed
damage on the follow-up cut, or just get a screen effect? Two of the eight beats are the powder
and the cloud, one is the cut through it, so the art assumes the blind is a real state.

**The cloud, measured:** the main mass is **11,434px** and spans **1.4 cell widths** — beat 4's
dust bleeds into beat 5's column, and a second 2,422px mass sits over beat 5. It also **covers
his body** on beat 4, so that cell cannot be cut as a fighter cell without separating the dust.

**It separates cleanly.** The dust is **tan** — saturation 20–90, luminance 125–225 — and his
accent is **saturated orange** (sat >110). 14,667 tan px against 5,721 of his orange, and the
two bands do not overlap. Same colour-separation that took the grey opponent off the defence board.

### ⛔ None of these five is a directional LIGHT

His Heavy and Special tiers already measure **complete, 10/10 each**, in both stances. His LIGHT
tier is **2/10** — only neutral is his; Fwd / Back / Down all play the roster's shared UNARMED
KICKS (`kpush` 3 cells, `kheel` **one**, `ksweep` **one**) and Up+Light just replays the neutral.
These boards are three more Heavies and two new techniques. **The five rows still owed are
`glfwd`, `glback`, `gldown`, `glup` and `aneu`** — art only, the engine already routes all five.

---

## THE LIGHT TIER — all five rows delivered, Aug 21. **The gap is closed.**

Named as proposed and titled with the row key, which is exactly what the pipeline needs.

| row | technique | median body | vs 270px | edge | verdict |
|---|---|---|---|---|---|
| `glfwd` | **Kirikomi** 斬り込み — the cutting-in | **353px** | **1.31×** | 0 | **PASS** |
| `glback` | **Hiki-giri** 引き斬り — the drawing cut | **402px** | **1.49×** | 0 | **PASS** |
| `gldown` | **Sune-giri** 脛斬り — the shin cut | **302px** | **1.12×** | 0 (fixed) | **PASS** |
| `glup` | **Age-tsuki** 上げ突き — the rising thrust | **375px** | **1.39×** | 0 | **PASS** |
| `aneu` | **Kesa-giri** 袈裟斬り — the collarbone cut | **442px** | **1.64×** | 0 | **PASS, 6 + 2** |

Accent hue **18.4–20.3° = ORANGE** on all five, against the shipped sheet's 18.9. Horns, hood,
one long blade, one eye — the batch canon holds. Corner 252–253, fuzz-42 lifts it.

### ✅ `gldown` beat 8 — the amputated blade, reconstructed

His katana on the final beat ran off the right edge of the board: 8px of ink in the last
column at y668–675, the tip simply gone. **Beat 8 is the same drawing as beat 1** — "Return
to ready guard" against "Low ready guard", 89.3% IoU on the ink mask at dx 1262, and 477
fewer pixels, which is exactly what the canvas cut. So the tip was not invented: the 12
missing columns were lifted from beat 1 (dy solved on the blade's own columns, +2, not the
body's 0) and the canvas grown to 1484 with 24px of paper past the new point. Every original
pixel is byte-identical; the paper fill is tiled from a block of the board's own grain proven
>= 252, because the strip beside the old edge carries the figure's 247–252 halo and printed a
ghost. **`exec-GLDOWN-sune-giri-8f-FIXED.png`, `fix_gldown_b8.py`.**

### ✅ `aneu` beats 7–8 are GROUNDED — so they are a LANDING TAIL, not air beats

Beat 7 lands him in a low recovery and beat 8 stands him back to ready. No edit makes either
airborne. So the row splits where the art splits:

    beats 1-6  ->  aneu1..aneu6     the airborne Kesa-giri
    beats 7-8  ->  aland1, aland2   drawn only once he touches down

An air light deliberately keeps its own row after landing (`attackAir` is captured at press
time), which is precisely why the last two beats would otherwise kneel him in mid-air at 75%
of the swing. The engine now tests `aland1` ahead of `aneu1` and gates it on `isGrounded` —
inert for every sheet without the row. **Nothing is discarded, and it is the first drawn
air-attack landing recovery any fighter in this game has.**
**`exec-ANEU-kesa-giri-6f+LAND2-FIXED.png`, `fix_aneu_split.py`.**

### ✅ The properties the kicks carried — a drawn row now inherits them

Filling these rows makes the engine skip `executeKick`, so the move becomes an ordinary Light
and everything the kick carried went with it. **That was already live, not a future problem:
Oni draws `glfwd` today and his shove had stopped wall-splatting and stopped punting logs.**

| row | property | now |
|---|---|---|
| `glfwd` | `wallsplat` + `puntLogs()` | **carried** — it is a step-in that shoves |
| `gldown` | `low` + `trip` | **carried** — the art is explicitly a cut *under the guard* |
| `glback` | `behind: true` | **NOT carried, and that is the answer.** His board puts the clash spark in FRONT of him on beat 5 — Hiki-giri cuts forward while the body withdraws — and Oni's glback is a backflip arc. A box behind a fighter whose blade is in front of him is the frame-physics mistake. `behind` stays with the heel kick, which is still what the other seven get. |

One shared derivation (`drewDirLight`) feeds both the gate that skips the kick and the hitbox
that has to carry what the kick would have. The old Oni-only `lowL` was dead code — a fighter
with no `gldown` row never reaches that line, because `executeKick` returns above it.
Measured live on :9100 through the real `executeAttack`, 9 fighters x 3 directions.
**`tools/check_dir_light_props.mjs`.**

---

## HIS SECOND STANCE — CHŪDAN-NO-KAMAE (**V**)

| row | cells | what it is | slot |
|---|---|---|---|
| `idle_chudan` | 2 | the stance idle | V held |
| `xcentry` | 6 | setting the guard | the V press |
| `xcslice` | 6 | **Chūdan Slices** — four fast cuts | Light, neutral |
| `xcthrust` | 6 | **Chūdan Multi-Thrust** | Heavy, neutral |
| `xctsuki` | 6 | **Chūdan Tsuki** | Heavy, forward |
| `xcfwdh` | 6 | **Chūdan Sheath Charge** | Special, forward |
| `xcuph` | 6 | **Chūdan Sky Cleave** | Special, up |
| `xcdownh` | 6 | **Chūdan Harai** | Special, down |

**44 cells, eight rows.** Legacy and unreferenced: `xcfour_old` (6), `xcthree_old` (6).

**Chūdan slots that fall back to his BASE art** — they play, they just are not stance-specific:
Heavy back → `xnukiuchi` · Heavy up → `xkiriage` · Heavy down → `xsuso` · Special neutral →
`xbtsuki` · Special back → `xnukiuchi` *(re-routed to the Iai on purpose)*.

The four directional Lights are **stance-blind** — the `gl*` rows above serve both stances, so
chūdan needs no second set unless the owner wants one.

---

## `exec-CHUDAN-STANCE-SHEET-8rows-44cells.png` — the whole second stance, one image

**Structurally perfect.** Eight rows, every one labelled with its **engine key** and its slot,
beat numbers on every cell, and the counts match the manifest exactly:

`idle_chudan` 2 · `xcentry` 6 · `xcslice` 6 · `xcthrust` 6 · `xctsuki` 6 · `xcfwdh` 6 ·
`xcuph` 6 · `xcdownh` 6 — **44 cells.** Corner 253, **edge contact 0px**, accent hue **20.6° =
orange**. Nothing to fix in what it says.

### ⛔ But it cannot be cut — it is the SAME SIZE as the sheet it would replace

| | median body |
|---|---|
| this stance sheet | **158px = 0.59×** of his 270px target |
| the chūdan cells **already packed** at SHEET_V 575 | **147–187px** |

Two independent measurements agreeing: the new art is **no bigger than what already ships**.
Under the CLEAN-SLATE ruling the whole point of a restyle is to land at the 4K minimum, and this
lands where the old sheet already was. It would be a look upgrade at **zero** resolution gain,
and would still need **×1.71** to reach target.

### The layout series — rows-per-image is the only variable that matters

| layout | body | vs target |
|---|---|---|
| **one row of 8, 3-line captions** *(URONAME + the light boards)* | **302–442px** | **1.12–1.64×** |
| one row of 8, 5-line captions *(Kael Nitō Seihō)* | 194–268px | 0.75–1.03× |
| **8 rows × 6** *(this sheet)* | **158px** | **0.59×** |
| 4 rows × 8 *(Defence & Evasion)* | 134px | 0.50× |

Monotonic, and it extends the CLEAN-SLATE finding already on file (56-frame boards ~111px,
18-frame 175–184px, 6-frame 205px, full-width strips 250–460px).

### ✅ OWNER RULING, Aug 21 2026 — *"yes keep"*

**This sheet is KEPT as the stance INDEX.** It is the reference image handed to the generator:
it names every row by its engine key, every slot, and every beat. It is **not** cut for cells.

The eight rows come back as **eight separate one-row strips**, three-line captions — the format
that has now passed ten times running.
