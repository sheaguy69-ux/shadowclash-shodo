# Move coverage — all nine, measured Sep 9 2026 (SHEET_V 773, `shodo-edition`)

Supersedes `MOVE-COVERAGE-AUDIT.md` (Aug 2, six fighters, SHEET_V 342). Nothing in the tree
was edited to produce this: read-only, from `web/index.html`, the nine files under
`web/assets/sprites/`, `tools/audit_move_coverage.py`, and the three-position matrix at
`media/audit/move-coverage/matrix.json` (x = 140 / 400 / 760, nine fighters, 40 slots each).

Every input: **2 states × 5 directions × 4 buttons = 40 each, 360 total.**

```
python3 tools/audit_move_coverage.py --ids 0,1,2,3,4,5,6,7,8
PORT=9101 node tools/drive_real_input.mjs --name <fighter>
```

---

## 0. The headline, corrected

The first pass of this scan published numbers that were soft in one direction and hard in
the other. Both errors have one cause each, and both are named here so the old numbers stop
circulating.

| | first pass | corrected | why |
|---|---|---|---|
| dead inputs | 0 / 360 | **0 / 360** | stands |
| STATIC rows | 2 | **2 by the tool's rule; ≥5 one-cell holds in fact** | the rule needs `dur ≥ 250` **and** exactly one cell for the whole move (`tools/audit_move_coverage.py:225`) |
| redundant inputs | 94 | **131 / 360** | the sweep put `cells` inside its ECHO key, so frame-sampling jitter split single moves into fake distinct ones |
| ground distinct | 145 / 180 | **139 / 180** (135 reachable by a real press) | same cause |
| air distinct | 90 / 180 | **81 / 180 as measured, 90 / 180 honestly** | the probe parks airborne at `p.vy = -40` (`audit_move_coverage.py:96`); nine Up moves gate on `vy < -180` |
| SHARED-ART rows | 31 | **31 + at least 14 more** | the grouper needs equal cell tuples; subset and offset collisions slip through |

**229 of 360 inputs are a move of their own. 131 are a second button on a move that already
exists.** Nine further collapses are probe artifacts and are excluded from that 131.

---

## 1. Five cross-fighter patterns — one decision each, not nine bugs

**PATTERN 1 — the MEDIUM tier reads no direction at all. 72 of the 131 redundant inputs (55 %).**
`_executeAttack`, `web/index.html:6937-6949`: one hitbox, no direction test, all nine fighters,
ground and air. The word in the source is "yet". **No owner ruling exists on this.**

**PATTERN 2 — directional dispatch stops at the ground. 36 slots.**
- Heavy: the whole directional table is refused off the ground — `} else if (this.isGrounded && DIR_MOVES[...])` at **7550**. The only airborne directional Heavy in the method is the meteor at 7619. **22 slots.**
- Special: every per-id direction branch inside `triggerSpecialAction` (8071) is `&& this.isGrounded` — id 0 at 8242 / 8519, id 2 at 8435 / 8454, id 4 at 8639 / 8657, id 5 at 8692 / 8768 / 9056. **14 slots.**

Mokurai (id 6) is the only exception: real airborne directional branches at **6271-6304**
(air Heavy neutral + up, air Light fwd + down, air fwd Special). All three of their art rows —
`mstrike`, `mdive`, `mairf` — are absent from `mokurai.json`.
Precedent for the fix is already in-tree: `DIR_SPECIALS` (2687-2703) carries an `air:` field
per entry; `DIR_MOVES` (2590) does not.

**PATTERN 3 — grounded Up+Heavy is unpressable for four fighters. 4 fully-specced moves.**
`DIR_MOVES` carries a `:up` entry for id 1 (`ristaff`), id 2 (`ghup`), id 3 (`ristwin`),
id 8 (`ghup`). The jump-priority latch
`type === ATTACK_HEAVY && pressUp && (this.isGrounded || this.vy < -180)` exists only at
**6232** (Ember), **6249** (id 7), **6254** (id 6), **6260** (id 0). The two sets are exactly
complementary. Up is the jump key, so by the time Heavy arrives the fighter is airborne and
7550 refuses.
Measured through the real key funnel (`PORT=9101 node tools/drive_real_input.mjs`): mizu /
shin / tsubasa / oni return `gnd=n` on every Up row and draw `aneu`. **Exile is the passing
control** (`upreach <- up+Heavy`).
This sweep cannot see it — it calls `executeAttack` directly with `isGrounded` forced true,
so all four count as distinct ground moves in the 139.
Fix: ONE branch beside 6260 keyed on `DIR_MOVES[this.spec.id + ':up']` existing.

**PATTERN 4 — alias rows: named rows with ZERO cells of their own. 7 of 9 sheets.**
Counted per row family: how many of its cell indices are used by no other family. A row
scoring zero is not art, it is a pointer — and because `mirror` / `frameClear` / `frameScale`
are keyed by cell index, the render is byte-identical.

| fighter | row | slots | actually is |
|---|---|---|---|
| Shin | `ghfwd` `ghback` `ghup` `ghdown` | 6 each | `light`+`kpush`+`hneu` / `hneu` / `srisaa` / `ksweep` — all four grounded directional heavies |
| Mizu | `bothrust` (7), `staffspin` (7) | fwd+H, back+H | strict subset of `medium`; 5-of-6 of `heavy_i` plus `medium5` |
| Tsubasa | `eflick` (6) | back+H | stitched from `ksweep` + `aneu` |
| Exile | `glback` ≡ `gsback` (8) | back+L, back+S | the identical eight cells 264,210,265,212,213,266,215,216 |
| Oni | `ghup` ≡ `gsup` ≡ `sup`; `hneu` ≡ `hup` | up+H, up+S, air n+H, air up+H | one row each |
| Kael | `xparry` ≡ `kscis` (6) | back+H, up+H, back+S, down+H | four moves, one row |
| Mokurai | `mblast` ≡ `special` (8); `mpalm`/`kpush` ⊂ `light` | back+H; all four ground lights | one row each |

Any inventory that counts manifest keys reports these as packed art. They are the same pixels.
`sneu` ≡ `special` (Shin) and `xrise` ≡ `xkiriage` (Executioner) are the benign case: one row
deliberately carrying two names for one move.

**PATTERN 5 — the generic air row answers everything airborne.**
`airAttackCells` (11624) returns the first of `aneu` / `bair` / `kxcut`, and every air picker
ends there. Verified by walking all nine manifests:

| key | present on | consequence |
|---|---|---|
| `kheel` | **nobody** | back+Light borrows `ksweep`/`kpush`/`xksweep` via the loop at 12674, all nine |
| `afwd` / `aback` | **nobody** | the branch at 12861 is dead code roster-wide, and `aback` is gated on `F.afwd1` so it can never ship alone |
| `hback` `hdown` `sfwd` `sback` `sdown` `kstomp` `attack_body` | **nobody** | every branch reading them is unreachable |
| `hfwd` `hup` `airhfwd` `dive` `glfwd` `sup` | **Oni only** | |
| `adown` | **Kael only** | |
| `hneu` | Executioner, Shin, Oni | |
| `gsdown` | **nobody**; `gsup` Mizu / Mokurai / Oni; `gsfwd` Tsubasa / Exile / Oni; `gsback` Shin / Exile / Oni | the comment at 13325-13327 claiming Oni is the only `gsup` owner is **FALSE** |

The sharpest instance: **METEOR BREAK (air Down+Heavy) is unartworked on 8 of 9.** It is a
real distinct move on every fighter — 900 ms, three hitboxes
(`30/34/x/1.2/60/down+spike` plus two `78/26/x/0.14/190` shockwaves), `7619` → `startSlam` at
`7807`. Its art branch (13070-13085) wants `dive1..6` (Oni only), then `hdown2`/`hdown3`
(nobody), then falls to `airPose` — ONE held cell per phase. Measured on the Executioner every
frame: `aneu1 ×7, aneu4 ×12, aneu8 ×18, idle (cell 71) ×14` — the last 14 frames are his
**standing idle cell, in mid-air, over the landing.**

---

## 2. The two STATIC rows have different causes — one is a bug

**Mokurai air Up+Light, 360 ms on `bair3` — by design.** `airPose` (11651-11655) returns ONE
cell by contract and 12691-12693 routes the up-poke to it. Every fighter does this; Mokurai is
the only one whose speed scale pushes it past 250 ms. The Executioner's is ~250 ms of `aneu3`,
Shin's 236 ms, Kael's 240 ms of `kxcut3`. The STATIC bucket under-counts; it is not wrong.

**Exile ground Down+Heavy, 300 ms on `xheavy5` alone — a defect, with a mechanism.**
`ROSTER_CONTACT_POSES[7]` at `web/index.html:11543` contains `['xheavy1','xheavy5','xheavy5']`.
In `rosterAttackFrame` (11549) that sets `first = last = indexOf(xheavy5) = 4`, so the entire
live window returns `arr[4]`, and the post-contact branch clamps to `arr[4]` too. Compounding
it, the hitbox at **7581** — `spawnHitbox(66, 20, 13*pow, 0.12, 70, { low, trip })` — carries
**no `delay`**, so the strike window is live from frame 0 and there is no pre-contact phase
either. 100 % of the move is one picture, at all three x.
Same shape as Kael's RISING FANG at **8779**. **22 `spawnHitbox` calls roster-wide carry no
startup delay** — the population at risk: 5027, 5028, 5044, 5045, 5067, 5068, 5858, 6170,
7581, 8481, 8497, 8779, 8790, 8800, 8801, 8846, 9086, 9290, 9291, 9363, 9364, 9428.

---

## 3. Per-fighter gaps

Dropped as by-design or probe artifact and **not** listed: every `Neutral+L == Up+L` row except
Exile's; Executioner `Back+H == Back+S`; all air Up+Heavy echoes on ids 0/4/6/7; all air
Up+Special echoes on ids 0/2/3/4/5; every second-form route.

**EXECUTIONER (id 0)** — ground 15/20, air 7/20 measured (10/20 at `vy = -400`)
ART: `xjodan1..6` is drawn by THREE different heavies — neutral (80/40), back (190/52
quick-draw), down (110/20 low+trip) — because `xnukiuchi` (13151), `xiai` (13155), `kneel`
(13157), `xsuso` (13169) and `xlow` (13172) are all absent, so every one of them falls to
`heavyCells` at 11811. `xtsuki1..3` (cells 329, 296, 297) is drawn by **FIVE** grounded moves:
fwd+H (the legitimate owner, 13140), down+S HARAI OTOSHI, up+S SKY CLEAVE, and fwd+L
SHADOW_SLICE and fwd+S SMOKE_STRIKE, whose authored frame lists (5842-5843, `footsies-data`)
name `xtsuki1/2/3` outright. Air fwd/back+H draw `aneu` while neutral+H draws `hneu1..8`
(cells 306-313). Air Down+Heavy unartworked. `kheel`, `adown` absent.
ENGINE: all four non-up airborne Specials land on the unguarded `if (specId === 0)` fallback
at 9093-9107.
DEAD CODE + ORPHANED ART: **SHEATH CHARGE (8519-8534) is unreachable and `xsheath1..6`
(cells 201-206) draws nowhere.** Its input — grounded fwd+Special — is intercepted 2 600 lines
earlier at 5842 by the authored SMOKE_STRIKE; the only escape is `!this.gyakute`, and `gyakute`
is set only in `toggleSaya()` (5386), reachable only through `modeKey()` (3676), whose first
line is `secondFormBlocked()` — which returns `true` unconditionally while
`FIRST_FORM_ONLY = true` (1622). Measured live: a 72-input scan returned
`inputs_reaching_SHEATH_CHARGE: []`. `docs/EXECUTIONER-MOVELIST.md:37` still lists it as live.
Also: a 16th grounded move exists outside the audit's vocabulary — the PUSH KICK on
**up-forward** (`46/28/6/0.12/300/wallsplat`, `kpush1..8`), because `heldDir` resolves
down > up > axis and dodges the `pressDir === 'fwd'` authored gate.

**MIZU (id 1)** — ground 16/20, air 11/20
ENGINE: grounded Up+Heavy `ristaff` (8 packed cells 209,210,211,177,178,179,212,213) cannot be
reached by a real press — Pattern 3.
ART: four different grounded Specials (mist / Reed Pierce 96/30 / REED WITHDRAW 125/42 / LOW
REED 132/34) all draw `special1..8`; `gsfwd`/`gsback`/`gsdown`/`mback` all absent. Five
different air Specials all draw `aneu1..8`. Air fwd/back/up Heavy → `aneu`.
⚠ **`bothrust` and `staffspin` may cost ZERO new art.** Cells 214-220 on `mizu.png` are seven
drawn staff-THRUST beats and 221-227 are seven drawn SPIN beats (drawn purple arc on 224); all
fourteen carry `mirror` entries, 214-220 carry `frameScale` 0.9, and **nothing in the manifest
points at any of them**. `bothrust` has exactly 7 slots; `staffspin` has exactly 7. Twenty
cells are unreferenced on this sheet (172, 184, 185, 186, 192, 204, 214-227). NOT VERIFIED
that 214-227 were authored for these rows — one owner look settles it before anyone
commissions anything.
⚠ Her back+Light is drawn **mirrored**: `reverseHeel` (2343-2350) flips `drawFacing` whenever
no `kheel` row exists. The moment `kheel` lands, that compensation goes false and the new art
must face forward on its own — roster-wide.

**SHIN (id 2)** — ground 15/20, air 7/20
ART: all four directional ground heavies are alias rows (Pattern 4) — fwd+H draws
`light`+`kpush`+`hneu`, back+H draws `hneu` (the same pictures as neutral+H *and* air
neutral+H), down+H draws `ksweep` (same as back+L and down+L), up+H draws `srisaa` (same as
up+S). `gsfwd`/`gsdown` absent, so WIRE SHURIKEN and SHURIKEN FAN both draw `special1..8`.
Air Down+Heavy unartworked. `kheel`, `adown` absent.
⚠ **TRAP, measured:** packing `gsfwd1` CHANGES THE MOVE. The branch at **6531-6536** is gated
on `SPRITES.shin.frames.gsfwd1 !== undefined`; injecting the row in memory turned fwd+Special
from the wire shuriken (1 projectile, 320 ms) into the SHURIKEN VOLLEY (3 projectiles, 220 ms).
Commission `gsfwd` as the volley, or decouple that gate first. `gsdown` is safe and additive.
BY DESIGN: ground neutral+S == back+S is now an art-only alias — the vanish MOVED to Kage-Nui
fwd+Special (8386-8402), and Kage-Nui is gated off.

**TSUBASA (id 3)** — ground 16/20, air 8/20
ART: back+H `eflick` has zero cells of its own (Pattern 4). back+L and down+L both draw
`ksweep`. Air Down+Heavy unartworked. `kheel`, `adown` and every `h*` absent → air
fwd/back/up Heavy draw `aneu`.
ENGINE: grounded Up+Heavy `ristwin` unreachable (Pattern 3); air fwd/back Special have no branch.
PROBE ARTIFACT: air Up+Special is `airthrow` (`DIR_SPECIALS 3:up`, `air: false`, admitted at
8747 on `vy < -180`) — its 4-way air-S echo is really 3-way. Air Down+Special `divecut` is
correctly `air: true` and draws its own row.

**EMBER (id 4)** — ground 16/20, air 7/20
ART: **fwd+Special SHRED CHARGE** (two boxes, 52/46 + 58/50) draws `espec1..8`, the same row as
his neutral Special — `echarge` (13371) absent. **up+Special CEILING HOOK** (46/120/15, launch)
draws `aneu1..7` — `ehook` (13377) absent. fwd+L and back+L both draw `kpush` (no `ksweep`, no
`kheel`, so push and heel share). Air Down+Heavy unartworked. `adown` and every `h*` absent.
Clean and NOT owed: `clawrend` (fwd+H), `lowrake` (down+H), `eheavy` (up+H), `eretreat`
(back+H), `erip` (down+S) all have their own rows.

**KAEL (id 5)** — ground 16/20, air 7/20 — worst art-per-slot on the roster
ART: **`kscis` ≡ `xparry` is drawn by FOUR moves** — down+H SCISSOR (72/22 + 72/52, the
legitimate owner), back+H LOW PARRY, up+H HIGH PARRY, back+S NITEN CROSS; `klowp` (13570) and
`khigh` (13573) both absent. He has **no kick rows at all** (no `ksweep`, `kpush`, `kheel`), so
fwd/back/down+Light all draw `kdual`, his neutral light row. **18 of his 20 air slots draw
`kxcut1..8`** (he has no `aneu`). Air Down+Heavy unartworked.
The air-forward-heavy handoff is written:
`art/production/handoff/SHODO-KAEL-AIRHFWD-JUMP-IN-BRIEF-2026-09-09/`, `airhfwd1..8` at cells
311-318, frameW 300 / frameH 320 / footY 312 — **live with zero engine change**
(`F.airhfwd1 !== undefined ? 'airhfwd' : 'hfwd'`, 13238).
ENGINE: NITEN CROSS PARRY is strictly dominated by LOW PARRY (costs chakra and stamina,
recovers slower, mechanically identical) — owner call. RISING FANG (8779) is a pinned-window
candidate.

**MOKURAI (id 6)** — ground 15/20, air 12/20 — best air coverage after Oni, because he is the
only fighter with real air direction branches
ART: his three dedicated airborne branches (6271-6304) all draw the wrong row because their art
is absent — `mstrike` (air neutral/up Heavy, 11749 + 13246), `mdive` (air down Light, 12733),
`mairf` (air fwd Special, 12774). back+H draws `mblast` ≡ `special`; fwd+H draws
`light` ≡ `kpush` ≡ `mpalm`; all four ground lights draw that same set. `bksweep` (12588)
absent. Air Down+Heavy → `bair`.
ENGINE: ground neutral+S == up+S (both `88/78/16/0.3/90`, `mpulse`) — his Up+Special has no
move of its own.
Clean: `mhammer` (down+H), `mbell` (up+H), `gsup` all present.

**EXILE (id 7)** — ground 15/20, air 11/20
ART, four written branches with no sheet behind them: `lowslash` (13100, down+H) — falls to
`xheavy`, and is the STATIC; `cwsnap` (13105, back+H COUNTER-WEIGHT SNAP) — draws
`xheavy1/5/3`, the same row as her fwd+H SIDE REACH; `airhurl` / `xair2` (13126 / 13129, air
Heavy 150/34 chain hurl) — draws `aneu`; `upflick` / `upatk3` (12708 / 12710) — **her ground
Up+Light is a genuine anti-air UP-FLICK** (`34/66/6/0.1/60/up`, 6156-6175, jump-priority clause
present, so it IS pressable) and it draws `light4`/`light5`, her standing neutral light. Also
absent: `airpoke` (12735), `xairf` (12799), `xspin` (11927). `glback` ≡ `gsback`, so back+Light
(60/30/7) and back+Special (584/56/14 corridor chain) are the same eight pictures. Air
Down+Heavy → `aneu`.
ENGINE: the pinned strike window (§2). Her Up+Heavy `upreach1..8` is fine — she is the control
that proves Pattern 3.

**ONI (id 8)** — ground 15/20, air 11/20 — the best-arted fighter (`hfwd`, `hup`, `hneu`,
`airhfwd`, `dive`, `glfwd`, `sup`, `gsfwd`, `gsback`, `gsup` all packed)
ART: `ghup` ≡ `gsup` ≡ `sup` — his rising claw Heavy, rising claw Special and air Up+Special
are one row. `hneu` ≡ `hup` — air neutral and air Up Heavy are one row. `athrow` (13511),
`whip` (13515), `airkick` (12693, his air up-poke) absent. `hback`, `hdown` absent. Ground
fwd+L is the generic light wearing `glfwd` art (the `drew` check at 6199-6208 correctly hands
him the direction back from the kick tier) — mechanically an echo of neutral+L, and that is fine.
ENGINE: grounded Up+Heavy `ghup` unreachable (Pattern 3).

---

## 4. Owed ledger — ART

Every row below is read by a picker branch that is **already written**. Zero engine work
unless marked. Ordered by slots unlocked.

| # | frame key | cells | fighters owed | slots | picker site |
|---|---|---|---|---|---|
| 1 | `kheel1..8` | 8 | **all 9** | 9 | 12653 — ⚠ landing it turns off the `reverseHeel` mirror at 2343 |
| 2 | `hdown1..6` (or `dive1..6`) | 6 | all but Oni (8) | 8 | 13077 / 13070 — the METEOR, a 900 ms 3-hitbox move currently held on one cell |
| 3 | `adown1..8` | 8 | all but Kael (8) | 8 | 12753 |
| 4 | `hfwd1..8` | 8 | all but Oni (8) | 8 (appearance only) | 13238-13240 — ⚠ mechanics need E3 |
| 5 | `hback1..8` | 8 | **all 9** | 9 (appearance only) | 13239 — ⚠ same |
| 6 | `hneu1..8` | 8 | Mizu, Tsubasa, Ember, Kael, Mokurai, Exile | 6 | 13240 |
| 7 | `gsdown1..8` | 8 | Executioner (`xharai`), Mizu, Shin | 3 | 13329 |
| 8 | `gsfwd` / `gsback` | 6-8 | Mizu (or `mback1..6`), Shin (`gsfwd` ⚠ 6531 changes the move) | 3 | 13329 |
| 9 | `xnukiuchi1..6`, `xsuso1..6`, `xharai1..6`, `xskycleave1..6` | 6 each | Executioner | 4 — `xskycleave` fixes grounded **and** airborne from one row (13357 sits above 13525) | 13151 / 13169 / 11902 / 13357 |
| 10 | `klowp1..6`, `khigh1..6` | 6 each | Kael | 2 (breaks a 4-move collision) | 13570 / 13573 |
| 11 | `mstrike1..8`, `mdive1..8`, `mairf1..8` | 8 each | Mokurai | 3 (his own branches already dispatch) | 11749+13246 / 12733 / 12774 |
| 12 | `echarge1..8`, `ehook1..8` | 8 each | Ember | 2 | 13371 / 13377 |
| 13 | `lowslash1..4`, `cwsnap1..5`, `airhurl1..4`, `upflick1..N` | 4/5/4/N | Exile | 4 | 13100 / 13105 / 13126 / 12708 |
| 14 | `airhfwd1..8` | 8 | Kael (cells 311-318), Executioner (cells 351-358) | 2 — **both briefs written**, zero engine change | 13238 |
| 15 | real cells for `ghfwd`/`ghback`/`ghup`/`ghdown` | 6 each = 24 | Shin | 4 | already routed; today they are pointers |
| 16 | real cells for `eflick` | 6 | Tsubasa | 1 | already routed |
| 17 | real cells for `bothrust` (7) / `staffspin` (7) | 0 if the orphans at 214-227 are theirs | Mizu | 2 | manifest repoint only |
| 18 | real cells for `glback` (8) | 8 | Exile | 1 (splits back+L from back+S) | already routed |
| 19 | real cells for `ghup`/`gsup`/`sup`, `hup` | 8 | Oni | 2 | already routed |
| 20 | `sfwd` / `sback` / `sdown` | 6-8 | anyone | 14 | 13307 — **BLOCKED on E7**; must be drawn genuinely airborne |
| 21 | `afwd1..8` + `aback1..8` | 8 each | all 9 | 0 mechanically | 12861 — ⚠ `aback` alone is dead art (branch gated on `F.afwd1`), and they are not distinct moves until E2 lands |
| 22 | `athrow`, `whip`, `airkick`, `bksweep`, `xairf`, `airpoke`, `xspin` | — | Oni ×3, Mokurai ×1, Exile ×3 | outside the 5×4 grid | branch written, row absent |

NOT owed, checked: every `xc*` (Executioner chudan), `crack` / `feint` / `lbell` / `blash` /
`hhalo` / `crefl` / `btoll` / `gravel` / `hpalm` (Mokurai's second form), `attack_body` (absent
on all nine — the `fanAnim` hook at 13429 and Tsubasa's at 13469 are dead roster-wide). All
gated by `FIRST_FORM_ONLY = true` at 1622.

---

## 5. Owed ledger — ENGINE

| # | branch | site | unlocks |
|---|---|---|---|
| E1 | direction cases in the MEDIUM block | `_executeAttack`, **6937-6949** | **72 slots** |
| E2 | airborne fwd/back in the Light tier | `_executeAttack`, beside 7205 / 7222 | **18 slots** |
| E3 | air-permitting directional Heavy | lift the `isGrounded &&` at **7550** with an `air:` flag per `DIR_MOVES` entry (precedent: `DIR_SPECIALS` 2687), or per-id branches beside the meteor at 7619 | **22 slots** |
| E4 | airborne directional Specials | `triggerSpecialAction` (8071) — every per-id direction branch is `isGrounded`-gated (8242, 8435, 8454, 8519, 8639, 8657, 8692, 8768, 9056) | **14 slots** |
| E5 | Up+Heavy jump-priority latch for ids 1/2/3/8 | one branch beside **6260**, keyed on `DIR_MOVES[id + ':up']` | 4 unpressable moves (`ristaff`, `ghup`, `ristwin`, `ghup`) |
| E6 | un-pin the strike window | `ROSTER_CONTACT_POSES[7]` at **11543** (begin == end) and/or a `delay:` on the hitbox at **7581**; same for Kael at **8779** | 2 measured STATIC/near-static; 22 no-delay hitboxes at risk |
| E7 | relax the air-Special art guard | **13306** `p.attackAir && (p.isGrounded \|\| !airAttackCells(F))` — any fighter with an air row can never draw `sfwd`/`sback`/`sdown` | prerequisite for ART item 20 |
| E8 | harness rot | `tools/audit_move_coverage.py:327` asserts `vanishTimer` on Shin's `gnd.back.S`; the vanish moved to Kage-Nui and Kage-Nui is gated off, so the run **aborts before the MEDIUM guard at :331 ever executes**. `:320` also skips every assertion on a partial `--ids` run | the tool's own self-check |

---

## 6. By design — not owed, do not re-audit next month

1. **Ground Up+Light == Neutral+Light on 8 of 9.** Up on the ground is jump. The two differ only in that neutral walks the string beat (7245-7247), which is why `stringT` splits them in the fingerprint. **EXILE IS THE EXCEPTION** — hers is a real UP-FLICK (`34/66/6/0.1/60/up`, 6156-6175) and it owes art.
2. **Executioner Back+Heavy == Back+Special.** Deliberate input rewrite at **5994-5996** under a 19-line owner quote.
3. **Every second-form route.** `FIRST_FORM_ONLY = true` (1622): the Executioner's chudan, Shin's Kage-Nui (and with it his Back+Special vanish), Mokurai's cracked kit, `gyakute` / SHEATH CHARGE. No art owed while the flag stands.
4. **The air up-poke holding one cell.** `airPose` returns one cell by contract (11651-11655).
5. **Oni's fwd+Light keeping the direction from the kick tier** (the `drew` check at 6199-6208).
6. **`sneu` ≡ `special` (Shin), `xrise` ≡ `xkiriage` (Executioner)** — one row, two names, one move.
7. **Air Medium borrowing the air row.** 12557-12561 deliberately drops an airborne Medium through to the Light path, because the four approved medium boards are STANDING boards.

⚠ **Not on this list, contrary to two classifiers: the MEDIUM tier being direction-blind.**
No owner ruling exists. The word in the source is "yet".

---

## 7. What this scan did NOT cover

- **It drove `executeAttack` directly, not the key funnel.** It proves what a move ASKS FOR, never that a press reaches it. `tools/drive_real_input.mjs` is the other ruler, and it is the only thing that caught Pattern 3.
- **Five directions only.** Diagonals are outside the vocabulary: up-forward, up-back, down-forward and down-back are folded into up/down by `heldDir` (2706-2711) before the grid sees them. The Executioner's PUSH KICK lives on up-forward and is invisible to this scan.
- **No throws, grabs, dash attacks, wall moves, wall proximity, second forms or multi-hit strings.** One press per input with `chainComboTier` reset, so beats 2+ of every LIGHT_STRING, every cancel route and every chain link are unmeasured. Oni's whole wire-bind conversion family never fires.
- **No live opponent, no round clock, no mist on the floor.** `startNewGame()` runs before every input, so Mizu's MIST SILHOUETTES (8325, needs a live `smokeField` she is standing in) is structurally unreachable and always falls through to LOW REED. Parries, counters and reprisals that need an incoming attack are equally invisible.
- **Three parking spots only.** Range-gated moves (Exile's wall grapple 60-520 px, her chain anchor at 210 px) can fall through at the wrong x and read as duplicates.
- **The fingerprint cannot see startup.** The probe wraps `spawnHitbox` naming arg 4 `delay`, but the real signature at **7834** is `(w, h, dmg, dur, push, opts)` — arg 4 is the box LIFETIME, and every numeric opt (`delay`, `launchVy`, `tier`, `mat`) is discarded. Two moves differing only in startup, launch velocity or material read as one echo.
- **Nothing was rendered.** Every art claim here is a manifest/index claim plus what the picker returns. No pixels were compared.
- **The tool is flaky and its output file is shared.** `audit_move_coverage.py` writes to one un-namespaced `matrix.json`; concurrent runs clobber each other. Cross-fighter contamination reproduced at x = 170 and x = 620, and `watch_game.py` crashed outright at x = 650. **Read the "measured at x=N: <count> fighters" line on every run** — a `--ids 1` run printing "2 fighters" is poisoned.

---

## 8. NOT VERIFIED — the owner must confirm

- Air Up+Heavy at `vy < -400` was re-driven and measured distinct **for the Executioner only**. Ember, Mokurai and Exile share the byte-identical latch condition (6232 / 6249 / 6254), so their echoes are called artifacts on a code reading, not a measurement. Same for Tsubasa's, Ember's and Kael's air Up+Special (8747 / 8673 / 8707).
- Mizu's orphan cells 214-227 matching `bothrust` and `staffspin` slot-for-slot is a strong circumstantial case (7 slots each, row-scale boundary at 220, correct subject) with **no packing note anywhere in the tree**. One owner look before anyone commissions or repoints.
- The exact reason Exile's `gnd.down.H` shows only `xheavy5` is read from `rosterAttackFrame` and the missing `delay`. The pinning mechanism is verified in source and the 3-sample-per-x measurement is in the matrix; the frame-by-frame confirmation is not done.
- `web/index.html` carries two directly contradictory comments about air-heavy branch order (13215 "THE AIR ROW GOES FIRST" vs 13230 "THE DIRECTIONAL MAP RUNS FIRST"). The code implements the second. Whether `hneu` is planted ground art that should not draw in the air is an **art judgement nobody has settled** — ink-vs-`footY` reads 2-5 px on every cell of both rows, so that ruler cannot separate them. Needs the runtime keyer and an owner ruling.
- Two false comments found in passing, do not propagate: **8568-8577** claims Mizu draws six six-cell Special rows (`gsdown`/`sneu`/`sfwd`/`sback`/`sdown`/`sup`) — all six are absent from her sheet. **13325-13327** claims Oni is the only fighter with `gsup` packed — Mizu and Mokurai have it too.

---

## 9. Independently re-verified before publication

Re-read from source and the manifests by hand, not taken on the scan's word:

- The Pattern 5 presence table above — every cell of it, by walking all nine manifests.
- `xnukiuchi1` / `xiai1` / `kneel` / `xsuso1` / `xlow1` / `xharai1` / `xskycleave1` / `xbtsuki1` / `xslip1` / `xreprisal1` absent from `executioner.json`; `xjodan1..6` = cells 81-86; `xtsuki1..3` = 329, 296, 297; `xsheath1..6` = 201-206; `xrise1` and `xkiriage1` both = cell 320.
- The `heavyCells` id-0 fallback at 11811-11813 and the `specialCells` id-0 tail at 11920 — the two fall-throughs that cause the `xjodan` and `xtsuki` collisions.
- The SHEATH CHARGE chain end to end: 5842 intercept → `gyakute` set only at 5386 → `toggleSaya` reachable only through `modeKey` 3676 → `secondFormBlocked` returns `true` unconditionally under `FIRST_FORM_ONLY = true` (1622). `xsheath` is read only at 13343-13350, behind `sheathAnim`, which only the unreachable branch sets.
