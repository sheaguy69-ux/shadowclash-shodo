# EVERYTHING STILL OWED — full-roster corrections list

Re-measured 2026-08-23 against the shipped sheets at SHEET_V 619 — not remembered.
Every item below was verified this day against pixels, jsons, engine greps, or the
ledgers; nothing is carried forward on trust. This replaces the Aug-21 version of
this file: Ember's first form has since been DELIVERED in full, Shin's sheet moved
to 520x370, and the Executioner was rebuilt onto the 271px standard (commits
7b0293d / 8255112 / a45f333). Split by who acts.

---

## STYLE SOURCE PER FIGHTER — which "new look" each brief means

The doc is measured off what is PACKED at 619. For exec, shin, ember-GK and
mizu's kit that IS the new style. Two fighters' new looks are delivered but not
yet packed — their briefs must reference the strips, not the sheet:

| fighter | authoritative style for new art | packed yet? |
|---|---|---|
| executioner | the packed 271px sheet itself (+ `RECOVERY/new-style-actionsets-aug20/EXECUTIONER-add-horns-spec.png`) | YES |
| shin | packed board-look sheet (grey scale-mail, green hood, single eye) | YES |
| ember | packed `gk_*` rows — all-ash; green form DELETED, never reference it | YES |
| mizu | `media/polished-candidates/mizu/boards-aug22/` kit (hb_* packed from it) | kit YES, idle NO |
| kael | `RECOVERY/new-style-actionsets-aug20/actionset-kael.png` — **NOT packed**; packed idle is the older look; gated on the 2nd-blade ruling (Part 2E) | NO |
| tsubasa | `RECOVERY/new-style-actionsets-aug20/actionset-tsubasa.png` — **NOT packed** | NO |
| mokurai / exile | current sheets are canon — no newer style exists | — |
| oni | `RECOVERY/oni-founder/ONI-BIBLE-FINAL.png` (skull mask FINAL) | benched |

When a not-yet-packed new look packs, that fighter's idle ink changes and the
scale re-solves against the Part 4 table.

---

## PART 1 — ART TO GENERATE (your outside generator)

### 1. Ember, GHOST KILLER form — 7 rows, 40 beats (was 29 rows; 22 landed)

Everything else in his two forms is on the sheet with its own drawn cells —
measured key-by-key, cell-sharing checked. These seven still fall back to
first-form art when the form is active:

| row | input | beats | strip px |
|---|---|---|---|
| `gk_ahfwd` | air forward + Heavy | **6** | **2172 x 724** |
| `gk_ahup` | air up + Heavy | **6** | **2172 x 724** |
| `gk_asfwd` | air forward + Special | **6** | **2172 x 724** |
| `gk_sup` | up + Special | **6** | **2172 x 724** |
| `gk_asup` | air up + Special | **6** | **2172 x 724** |
| `gk_fall` | state — fall | **4** | **1448 x 724** |
| `gk_roll` | state — roll | **6** | **2172 x 724** |

Reference: the packed `gk_*` rows on `web/assets/sprites/ember.png`.
⚠ The canon master ref `emberidle.gif` was NOT FOUND anywhere on this machine
(mdfind + find across the repo, Downloads, Desktop). If it lives on another
device, restore it before any first-form brief cites it.

### 2. Mokurai — three washed kick cells + green-face batch

Measured per-cell (mean ink saturation; script kept in the session scratchpad):

- **Washed (grey-pink, dull-mustard) batch is only THREE single cells** —
  `ksweep`=41, `kpush`=42, `kheel`=43, sat 0.32-0.36 vs idle 0.51. His bell/snare
  rows (btoll, snarew, gravel, dbell, scut, meats, crefl, blash…) measured VIVID
  and their body scale is right (head-width ruler) — do not redraw those.
  → Redraw the three kicks: one beat each, vivid colorway.
- **Green skin contamination** — cells 0-27 (`mstrike` `mthrow` `mpalm` `mhammer`
  `mbell` `mblast`, 8-9% green ink) and 35-40 (`bair1-3` `bksweep` `bkfront`
  `bkheel`, 6-10%): green-tinted faces, visually confirmed.
  → Regenerate those rows, or approve a local hue-fix pass on the faces.

Target palette (quantized off his vivid idle, cell 204): outline `#130906`,
robe shadow `#421c12`, stone skin `#87807a` / `#554e4b` / `#c8bdad`, robe
orange `#cf7213`, scarf red `#9d1503` (merged robe/scarf `#ac3005`).
Bare hands, bead-wrapped fists, NO staff.

### 3. Shin, form 1 — `gsback` Wire Retreat, 6 beats (2172 x 724)

Deleted as fake at SHEET_V 611 (crouch/idle cells stuttering over a wire
retreat); confirmed still absent from shin.json (247 keys). Real move — back +
Special in form 1 — with no art on any tree. Grey scale-mail board look, green
hood, single eye (canon — never "fix" the eye count).

### 4. Blade-lock cells — whole roster, none exist

Engine is WIRED and waiting: `web/index.html:10944` `STATE.BLADE_LOCK` reads
`lock1..N` (up to 12; "Pack lock1..4 and it plays four"), last two cells = win /
lose per the ledger. Key-scan of all nine jsons: ZERO lock keys anywhere. One
lock row per blade fighter (exec, kael, tsubasa, exile, shin form-2 at minimum)
unlocks the whole feature — 4-6 beats each, straining sword-clash pose, last two
beats the win shove and the lose stagger.

### 5. Mizu — new-look idle board (the anchor row)

Her mode-2 HANBŌ kit is fully packed now (132 `hb_*` keys live), but `idle` and
`idle2` both alias ONE stand-in cell (col 0), and her own boards-aug22 REVIEW.md
lists "idle (the anchor row)" as missing. Every scale ruling anchors on idle —
this is the highest-leverage single board on the list. Purple hood, long bo
staff, 6 beats.

---

## PART 2 — DECISIONS ONLY YOU CAN MAKE (no drawing needed)

### A. Executioner grown-frame sheet adoption (one swap)

His sheet here is one size now (271px standard) but `glup6` — the overhead-thrust
peak — holds beat 5's drawing because the true peak needs the 490px-tall frame
fable-5's 645 grew. Say "adopt" and fable-5's executioner sheet (byte-superset,
the one you reviewed on :9100) replaces this one whole and lands the real peak.
My session permissions refused that copy twice — your swap or your grant.

### B. Remaining drift rows — RECOVERED still loses these 5

From the judged plates (they live in **fable-5's** tree:
`~/shadowclash-fable-5/RECOVERY/tree-drift-aug23/`). Most of the review's
14-key losing list was already resolved here by 618/619 (block, hurt, xcslice,
xparry, xiai, xnukiuchi, gldown, idle_chudan, exec idle). Still open:

| row | defect here | fix |
|---|---|---|
| oni `lunge` | six copies of the standing idle | adopt fable-5's row (benched, when unbenched) |
| oni `aback` | "aerial" whose feet never leave the floor | adopt fable-5's row |
| oni `dash` | listed losing, no defect line recorded | adopt fable-5's row |
| ember `gk_wallslide` | fable-5's is right; ours needs the baked wall keyed out | import fable-5's instead of re-keying |
| exec `xcentry` cells 14-15 | two pre-standard cells left in a six-cell row | import fable-5's two cells |

Say "adopt those" and they land append-only like 619 did.

### C. Contested rows my 619 already answered — confirm or reverse

`glfwd` (was sword-jab art in a push-KICK slot; fable-5's real kick art is now
keyed) and `xctsuki` (came inside the 271px batch). The drift review had left
both for you. One json edit reverses either — old cells still on the sheet.
`xkiriage` was never verified by the review; it measured on-standard here.

### D. Which tree is THE tree

:9100 serves **shadowclash-fable-5** (645+); this sweep's fixes live on
**SHADOWCLASH-RECOVERED** (619). Art is key-converged but the ENGINES diverge
~2411 lines — wiring that exists on one tree dies with the other. Pick the
survivor; the other drains into it and dies.

### E. Kael's second blade

Canon (your Jul-16 ruling): ONE SHORT + ONE LONG — the both-blades-long lineup
was rejected. The Aug-20 new-look idle reads its second blade as full-length.
Still open in the ledger. Bless the new read or order the short blade back.

### F. Oni (benched — nothing here blocks the six)

Unbench gate is yours (motion-gate the skull-mask FINAL). Waiting behind it:
the three drift rows above; dir rows `gsfwd`/`gldown`/`glup` — DRAWN in
`RECOVERY/oni-founder/boards-aug9/` (MASTER-LIGHT-DIR / MASTER-SPECIAL-DIR
boards) but never cut, keys don't exist yet; the 18-move placeholder cell; his
idle-vs-kit size solve.

### G. Finished art with no move attached (Aug-21 audit — still true)

Three drawn Ember counters (`gk-CATCH-arm`, `gk-CATCH-dagger-deflect`,
`gk-COUNTER-punch-to-leg-takedown`) and the six-beat rake `air-14.png` — the art
is finished and the MOVE doesn't exist. Give them inputs or they stay archived.

---

## PART 3 — ENGINE WIRING YOU CAN ORDER (agent work, no art)

- **Exec's dedicated deflect rows are dead art**: `xuke1-7` and `xgedan1-8` are
  packed and referenced NOWHERE in the engine (0 grep hits). His only live
  deflects are the tier-agnostic projectile knock-back and IRON GUARD reprisal.
  Order: wire uke/gedan as real deflect visuals, or mark the rows superseded.
- **LIGHT tier has no deflect answer** anywhere (chudan explicitly buys lights
  nothing). Design call first, wiring second.
- **Shin `slowsweep1-6` and `flying_kick1-6`**: packed, zero executable
  references — unreachable. Order: wire or strip. (Also the stale comment at
  index.html:10285 claiming slowsweep is gone — it isn't.)
- **Ember up+Light**: currently a plain light by design (UP never maps to a
  kick), so it shares the `elight` row with neutral. If you want a distinct
  up+Light, it needs BOTH a drawn `glup` row and the input map extended — art
  alone would be dead cells.

---

## PART 4 — DELIVERY SPEC (every strip, no exceptions)

- **724px tall.** Width **362px per beat**: 2 = 724x724 · 3 = 1086x724 ·
  4 = 1448x724 · 5 = 1810x724 · 6 = 2172x724 · 8 = 2896x724
- **Flat WHITE background.** No ground shadow, no scenery, no wall.
- **Beats left to right**, evenly spaced, **ONE ROW PER IMAGE**.
- **Facing LEFT.** Every sprite is authored left and mirrored by the engine.
- **Body 260px minimum, crown to heel** — a floor, not a target.

### Per-fighter cell geometry (current sheets, measured 2026-08-23)

| fighter | cell (WxH) | footY | scale | idle ink | on-screen |
|---|---|---|---|---|---|
| executioner | 300x412 | 404 | 0.2674 | 271 | **72.5** (tallest of the six) |
| kael | 300x320 | 312 | 0.4094 | 171 | 70.0 |
| tsubasa | 301x320 | 312 | 0.3606 | 189 | 69.6 |
| ember | 340x377 | 369 | 0.3397 | 204 | 69.3 |
| shin | 520x370 | 330 | 0.3505 | 190 | 66.6 |
| mizu | 300x320 | 312 | 0.3852 | 162 | 62.4 (smallest) |
| exile | 480x368 | 280 | 0.4667 | 155 | 72.3 |
| mokurai | 300x248 | 218 | 0.4667 | 149 | 69.5 |
| oni | 480x372 | 330 | 0.5684 | 154 | 87.5 (towers; benched) |

Silhouette law: the Executioner stays slightly tallest of the six (~2-3px over
Kael), Oni towers, Kael is the youngest. Any new idle re-solves its fighter's
`scale` against this table.

---

## Fixed this session — do NOT redraw

617: six rescaled to canon order. 618: exec onto the 271px standard, hurt cells
real. 619: exec's last eleven rows at full size, append-only, originals
byte-identical. Ember first form: all 11 rows delivered; GK: 22 of 29 delivered.
Oni run: flat 134px all ten beats, both trees. Mokurai bell/snare rows: vivid
and correctly scaled — cleared by measurement, off the redraw list.
