# EXECUTIONER REDO — frame + moveset spec (owner sheets, Aug 2 2026)

Source: owner's four reference sheets — MOVE REPLACEMENT GUIDE, normals spread (6 rows),
specials spread (6 rows), CHUDAN second-stance spread (6 rows). All rows are **6 cells**.

**Owner's design order:** he is a **TANK at MID SPEED** with **lightning-fast attacks and
reaction speed**. → **Movement speed and the run cycle are UNTOUCHED.** Everything that
gets faster is swing, startup and recovery. Nothing that gets faster is locomotion.

⛔ Two new assets incoming in the owner's next message. **No generation, no packing, no
`SHEET_V` bump until they land and the montage is approved.**

---

## 1. THE SPEED PROBLEM — why he currently feels slow (measured, not felt)

His sluggishness is **not** `SLICE_SPEED`. It is `speedScale`:

```
speedScale = curSpeed / 6 = 3.5 / 6 = 0.583
recoveryTimer = <base> / speedScale        // ← DIVIDES. 0.583 means ×1.71
```

Every recovery he owns is inflated 71% because he is the slowest body in the roster. That
is a *movement* stat taxing his *reaction* time — exactly the thing the owner says should
not happen.

| Move | Base | Today (÷0.583) | Tank-fast target |
|---|---|---|---|
| Neutral light | 0.25 | 0.43 | **0.25** |
| Neutral heavy | 0.45 | **0.77** | **0.45** |
| Drive Stab / Chudan Tsuki | 0.42 | 0.72 | **0.42** |
| Iai / Nukiuchi | 0.52 | **0.89** | **0.52** |
| Kiriage (Up+G) | 0.46 | 0.79 | **0.46** |
| Suso Giri | 0.44 | 0.76 | **0.44** |
| The Thrust (H) | 0.60 | **1.03** | **0.60** |

**Fix — one line, one fighter:** exempt him from the speed tax.

```js
// TANK AT MID SPEED, LIGHTNING REACTIONS (owner, Aug 2 2026). Movement stays 3.5 —
// his walk, dash and run cycle are untouched. But recovery is REACTION time, not
// locomotion, and dividing it by a movement stat taxed the wrong thing.
const RECOVERY_TAX = { 0: 1 };   // Executioner pays no speed tax on recovery
const recScale = RECOVERY_TAX[this.spec.id] ?? speedScale;
```

Then every `/ speedScale` on a recovery line becomes `/ recScale`. That single change is
~41% off every recovery he has and costs zero art.

Plus:
- `SLICE_SPEED[0]` **0.75 → 0.62** — swings and their hitbox delays get another 17% faster.
- `spec.stats.defense` **6 → 8** — he is billed as the tank and currently sits mid.
- `spec.stats.speed` **3.5 — UNCHANGED.** Run cycle untouched, per owner.

## 2. MOVE REPLACEMENT MAP (from the owner's guide sheet)

| Input | Was | Becomes | Action | Cell keys needed (6 ea.) |
|---|---|---|---|---|
| `F` | Neutral Light | **NUKITSUKE LIGHT CUT** | REPLACE | `xnuki1..6` |
| `G` | Neutral Heavy (overhead) | **JODAN KIRI OTOSHI** | REPLACE | `xjodan1..6` |
| `Fwd+G` | Drive Stab | **CHUDAN TSUKI** | REWORK | `xtsuki1..6` (repack) |
| `Back+G` | Iai Quick-Draw | **NUKIUCHI DRAW CUT** | REWORK | `xnukiuchi1..6` |
| `Up+G` | Gyaku Kesa | **KIRIAGE RISING CUT** | REPLACE | `xkiriage1..6` |
| `Down+G` | Suso-Giri | **SUSO GIRI** (stronger reanim) | REWORK | `xsuso1..6` |
| `H` | The Thrust | **ARMORED BATTLE TSUKI** | REWORK | `xbtsuki1..6` |
| `Fwd+H` | Sheath Charge | **SHEATH CHARGE** (stronger) | REWORK | `xsheath1..6` |
| `Up+H` | Sky Cleave | **SKY CLEAVE / KIRIOROSHI** | REWORK | `xsky1..6` |
| `Down+H` | Gravewave | **HARAI OTOSHI** (grounded real cut) | REPLACE | `xharai1..6` |
| Chudan `F` | Four Fast Slices | Four Fast Slices (reanim) | REWORK | `xcslice1..6` |
| Chudan `G` | Three Thrusts | Three Thrusts (reanim) | REWORK | `xcthrust1..6` |

**KEEP UNCHANGED (owner):** Down+F sweep · Fwd+F push · Back+F heel · air Down+G Meteor
Break · Throw · Bunshin · **Dread mechanic**.

## 3. NEW — CHUDAN GETS ITS OWN SPECIALS

The second-stance sheet adds **four rows the engine does not have today**. Currently
`chudan` only rewrites neutral `F` and `G`; every command input falls through to the
standing version with a `×1.28/×1.18` multiplier. The sheet says otherwise:

| Row | Input | New in-stance move | Engine status |
|---|---|---|---|
| 1 | `V` toggle | **CHUDAN ENTRY — No Kamae / Guard Set** | ⚠️ NEW — today the toggle is instant with no anim |
| 2 | Chudan `F` | Four Fast Slices | exists, reanimate |
| 3 | Chudan `G` | Three Thrusts | exists, reanimate |
| 4 | Chudan `Fwd+H` | **EXECUTION SHEATH CHARGE** | ⚠️ NEW branch |
| 5 | Chudan `Up+H` | **SKY CLEAVE / KIRIOROSHI** (stance version) | ⚠️ NEW branch |
| 6 | Chudan `Down+H` | **HARAI OTOSHI** (stance version) | ⚠️ NEW branch |

Owner's own note on the sheet: *"Gravewave is not part of this second-stance spreadsheet."*

**Entry anim needs a gate.** A 6-cell CHUDAN ENTRY means the toggle is no longer free — it
becomes a committed ~0.3s action. That is a real balance change (today you can toggle in
a gap). Recommended: entry cells play, and the last 0.25s of the entry is a **parry
window** — the blade being set IS the block, once. That gives the stance an entry reward
and pays for the new commitment in the same beat.

## 4. NEW FRAME DATA — tank body, lightning steel

`pow = 1.5`, `rate = 1.5`. Damage shown post-`pow`. Startups assume `SLICE_SPEED 0.62`.

### Normals

| Input | Move | Box w×h | Dmg | Startup | Active | Push | Recovery | Change |
|---|---|---|---|---|---|---|---|---|
| `F` | Nukitsuke Light Cut | 60×30 | 12 | **0.036** [2f] | 0.05 | 90 | **0.25** | −42% rec |
| `G` | Jodan Kiri Otoshi | 90×40 | 27 | **0.086** [5f] | 0.07 | 162 | **0.45** | −42% rec, **+armor 0.15s** |
| `Fwd+G` | Chudan Tsuki | 150×24 | 21 | 0.09 | 0.12 | 160 | **0.42** | unblockable → **guard-crush** (see §5) |
| `Back+G` | Nukiuchi Draw Cut | ≥90×52 | 27 | 0.50 (noto) | 0.14 | 175 | **0.52** hit / **0.72** whiff | whiff penalty is new |
| `Up+G` | Kiriage Rising Cut | 60×110 | 25.5 | 0.09 | 0.16 | 120 | **0.46** | launch −400 unchanged |
| `Down+G` | Suso Giri | 110×20 | 19.5 | 0.11 | 0.12 | 90 | **0.44** | low + trip unchanged |

### Specials (25 stamina)

| Input | Move | Box w×h | Dmg | Startup | Active | Push | Recovery | Change |
|---|---|---|---|---|---|---|---|---|
| `H` | Armored Battle Tsuki | 96×50 | 28 | 0.09 | 0.16 | 195 | **0.60** | armor **0.35 → 0.45s** (the name says armored) |
| `Fwd+H` | Sheath Charge | 92×58 | **24** | 0.24 | 0.14 | 230 | 0.52 | +2 dmg, armor 0.34s, wall-splat |
| `Up+H` | Sky Cleave / Kirioroshi | **62×165** | 20 | 0.20 | 0.13 | 140 | 0.50 | taller column so it beats what Kiriage loses to |
| `Down+H` | **HARAI OTOSHI** | **135×26** | **22** | 0.10 | 0.14 | 150 | 0.48 | ⛔ **projectile DELETED** — real grounded cut, low + trip |

### Chudan (`×1.28 dmg / ×1.18 reach` on heavy+special tiers, block disabled)

| Input | Move | Hits | Per-hit | Timing | Recovery |
|---|---|---|---|---|---|
| `V` | **Chudan Entry** | — | — | 6 cells ~0.30s | parry window last 0.25s |
| `F` | Four Fast Slices | 4 | 6 / 6 / 6 / 9 | 0.03 / 0.06 / 0.09 / 0.26 | **0.32** |
| `G` | Three Thrusts | 3 | 9.6 / 9.6 / 19.2 | 0.04 / 0.10 / 0.17 | **0.36** |
| `Fwd+H` | Execution Sheath Charge | 1 | 30.7 | 0.24 | 0.52 |
| `Up+H` | Sky Cleave / Kirioroshi | 1 | 25.6 | 0.20 | 0.50 |
| `Down+H` | Harai Otoshi | 1 | 28.2 | 0.10 | 0.48 |

## 5. TWO BALANCE CALLS THIS REDO FORCES

1. **He loses his only ranged tool.** Gravewave was his answer to a zoner camping full
   screen; Harai Otoshi is a 135px grounded cut. With no projectile and mid speed, a
   patient Mizu or Shin can hold him out all round. **Recommendation:** Harai Otoshi's
   *swoosh* extends a short travelling floor-crack ~90px past the blade — visually the
   same cut, mechanically he keeps a whiff-punishing pressure tool. Cheap, no new art.
2. **Two free unblockables (Fwd+G, Back+G) survive this redo.** With his recoveries cut
   ~41% they get considerably stronger. **Recommendation:** Chudan Tsuki (Fwd+G) becomes a
   **guard-crush** (chip + heavy blockstun + pushback) and Nukiuchi keeps the sole
   unblockable — it already pays with the 0.50s noto delay.

## 5b. TWO NEW COUNTER SPECIALS (owner sheet, Aug 2 2026)

Both 6 cells. Owner's notes: *"special counter tools … preserve his heavy / precise sword
identity … can build or spend Dread."* Neither needs a new key — both ride inputs that are
free today, which is why they cost nothing to add.

### SHADOW SLIP REVERSAL — *evasive slip backward, then instant counter punish*

| | |
|---|---|
| **Input** | `Guard + G` (free chord — Guard+H is Bunshin, Guard+Special is the roster's clone) |
| **Cost** | 20 stamina |
| **Phase 1** (cells 1–3) | backward slip ~110px, **i-frames 0.18s**, no hitbox |
| **Phase 2** (cells 4–6) | fires **only if something whiffed through the slip** — 120×46, **26 dmg**, delay 0.08, active 0.14, push 190 |
| **Whiff** | slip plays, no counter, 0.40s recovery — a read you lost, not a free retreat |
| **Dread** | builds on connect AND spends at 3 — the Execution rule fires on any special-tier box (measured: 26 -> 39 dmg). An earlier draft said "builds only"; that was wrong. |
| **Cells** | `xslip1..6` |

Why this input: he is mid-speed with no non-attacking approach or escape. A backward
i-frame slip is the defensive tool a tank at 3.5 speed is actually missing, and gating the
counter on "something whiffed" stops it being a panic button.

### IRON GUARD REPRISAL — *block, absorb the force, riposte*

| | |
|---|---|
| **Input** | `G` **during blockstun** — i.e. you just successfully blocked. Contextual, no new key |
| **Cost** | 20 stamina |
| **Window** | 0.22s from the block connecting |
| **Riposte** | 105×50, **30 dmg**, delay 0.06 (near-instant — the block WAS the wind-up), active 0.14, push 210, **armor 0.25s** |
| **Recovery** | 0.44 |
| **Dread** | builds on connect AND spends at 3 — measured 30 -> 45 dmg, 113 -> 155 wide, armor 0.5s, dread reset to 0 |
| **Cells** | `xreprisal1..6` |

Why this input: it is literally what the sheet describes — *"successful block triggers a
counterattack follow-up."* It also repays the thing chudan took away: standing guard is
worth something again, which makes the choice to enter chudan (and give guard up) an
actual decision instead of a free upgrade.

⚠️ **Interaction to watch:** neither counter works in chudan, because chudan has no block
and Shadow Slip's chord uses the guard key. That is correct — stance is offence, these are
defence — but it should be said out loud in the training move list.

## 6. ORDER OF WORK

1. ⏸ **WAIT** — owner's two new assets (next message).
2. Code-only pass (zero art risk, zero spend): `RECOVERY_TAX`, `SLICE_SPEED` 0.62,
   `defense` 8, neutral-`G` armor, Harai Otoshi replacing the wave, the three new chudan
   branches, chudan entry anim gate.
3. Art pass: 13 rows × 6 cells against the owner's sheets. Ember recipe for anything with
   locomotion. Montage strip + GIF at game fps to the owner **before** the sheet is touched.
4. `SHEET_V` bump in the SAME commit as any `web/assets/sprites/*` change.

**Running spend this saga: $5.08. Nothing new spent on this doc.**
