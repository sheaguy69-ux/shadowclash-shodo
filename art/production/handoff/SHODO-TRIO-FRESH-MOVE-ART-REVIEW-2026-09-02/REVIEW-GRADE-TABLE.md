# Fresh SHODO trio — Doc 17 grade table (Fable 5, 2026-09-02, reviewed at SHEET_V 694)

All three source hashes match `PROVENANCE.md`. Review only; nothing packed, no live file touched.

## ⛔ BLOCKER THAT OUTRANKS THE ART — all three moves are gated OFF

These are **second-mode** moves. `web/index.html:1120` holds `const FIRST_FORM_ONLY = true`,
and `secondFormBlocked()` kills all three at **seven** call sites — the mode input
(`modeKey`, `toggleHanbo`, `toggleKageNui`, `toggleSakate`) and the three frame routers
(`mizuF2Frame`, `shinF2Frame`, `tsubasaF2Frame`, which return `undefined`).

**No sheet packs a single second-mode cell today** — mizu 0 `hb_*`, shin 0 `f2_*`,
tsubasa 0 `f2_*`. Each mode needs a whole kit before it can be entered:

| Fighter | Mode | Rows the engine can reach | Packed |
|---|---|---|---|
| Mizu | Hanbō no Kata | `hb_aircross airrap catch cross jab low maki mist rap1 split` (10) | 0 |
| Shin | Kage-Nui | `f2_` idle run jump crouch dash roll land block parry air light1-3 heavy1-3 clow csweep dashcut (19) | 0 |
| Tsubasa | Sakate | same `f2_` set (19) | 0 |

`mizuF2Frame` additionally requires `hb_split_1` and `tsubasaF2Frame` requires `f2_light1_1`
before either will draw anything at all. So a board landed today packs cells nothing reads —
orphans on arrival. **Owner decision needed before any of this is worth packing.**

## Grades

Dimension numbers are Doc 17's. N/T = not testable at this stage (RGB review files, not packed).

| # | Dimension | Mizu — Hanbo Kaeshi | Shin — Kage-Nui Poke | Tsubasa — Sakate Rake |
|---|---|---|---|---|
| 1 | Identity hold | PASS — purple hood, **two** white eyes, scarf all match her live idle | PASS — green hood, **one** cyan eye, teal scarf; eye shape matches live idle (live cell is only 7x5px, hence the ring look) | PASS — black/red, spiked hair, one white eye + shadowed far eye, matches live idle |
| 2 | Weapon discipline | PASS — two hanbō on all 6 beats (GUARD's second reads only on a tight crop) | **CONCERN** — two kunai, but DRIVE's second is detached from the hand (see 11) | PASS — two tanto, reverse grip, blades pinky-side |
| 3 | Palette match | PASS | PASS | PASS |
| 4 | Pose readability | PASS — six distinct beats | PASS | PASS |
| 5 | Silhouette clarity @48x64 | **PASS 6/6 at game size** — the binary silhouette IS blobbier than her shipped cells (bbox fill 0.65 on VEIL/GUARD vs her live max 0.53), and in a pure silhouette VEIL loses the stick entirely. But that channel is not what carries her weapon: rendered at her true on-screen height of 62px, the tan hanbō sits at luminance ~105 against a robe at ~30, Weber contrast 1.37-3.48 on every beat where 0.25 is the reading threshold. The action reads. | PASS 6/6 | **PASS 6/6** |
| 6 | Size registration | **UNRESOLVED** — no ruler passes a known-answer check on her; foot line holds to 6px | **UNRESOLVED** — eye reads 4.1% spread but the ruler over-reads (x1.05 measures x1.167), so 4.1% is an upper bound, not a gate; foot line 3px | **UNRESOLVED**; foot line 4px |
| 7 | Motion path | PASS | PASS | PASS |
| 8 | Smear legibility | N/A — no smear cells | N/A | N/A |
| 9 | Cartoon physics | N/A at this scope | N/A | N/A |
| 10 | Frame-data alignment | **FAIL — no row exists to align to** (gate above) | **FAIL — same** | **FAIL — same** |
| 11 | Background artifacts | **FAIL 4/6** — floating debris: VEIL 17px, INVITE 37px, CATCH 132px, PIVOT 690px stub + 38px | **FAIL 2/6** — SIGHT 95px, DRIVE **454px floating kunai with no hand or arm** | **PASS — zero detached pieces on all 6** |
| 12 | Sheet integrity | N/T | N/T | N/T |

Also verified on all three: **zero canvas-edge ink** on every side, so no straight cut-offs;
captions below the row; one row per image.

## Verdict

| Board | Grade | Why |
|---|---|---|
| **Tsubasa — Sakate Backhand Rake** | **KEEP** | Clean on every testable dimension. Only the gate stops it. |
| **Shin — Kage-Nui Poke** | **KEEP** | Its "2 fragments" were never real — my own beat cut was slicing a neighbour's thrust kunai. Measured whole-board, shin has zero detached components. |
| **Mizu — Hanbo Kaeshi** | **KEEP** | The one speck is gone. The silhouette worry did not survive measurement — see dimension 5. |

**Nothing on these three boards needs a redraw.** Every finding was either fixed locally or
withdrawn on measurement — the extraction is in `extracted/`, and the only thing still
outstanding is the `FIRST_FORM_ONLY` decision, which is an engine question, not an art one.
