# EXECUTIONER — current move list (post tank/speed pass, Aug 2 2026)

> This file was silently deleted twice while being written. It is committed now so it
> stops vanishing. Companion doc: `EXECUTIONER-REDO-SPEC.md` (the *planned* redo).

Spec: id 0 · Long Sword (odachi) · archetype Heavy/Berserk
Stats: **speed 3.5 · power 9 · reach 9 · defense 8** ← defense was 6
`pow = 1.5` · `rate = 1.5` · **`RECOVERY_TAX[0] = 1`** (no speed tax on recovery) ·
**`SLICE_SPEED[0] = 0.62`** (was 0.75) · Special cost 25 stamina.

Damage is post-`pow`. Frames @60fps in brackets.

## 1. NORMALS (free)

| Input | Name | Box w×h | Dmg | Startup | Active | Push | Recovery | Was |
|---|---|---|---|---|---|---|---|---|
| `F` | Neutral light | 60×30 | 12 | 0.036 [2.2f] | 0.05 | 90 | **0.25** | 0.43 |
| `G` | Neutral heavy (overhead) | 90×40 | 27 | 0.086 [5.2f] | 0.07 | 162 | **0.45** | 0.77 |
| `Fwd+G` | **DRIVE STAB** | 150×24 | 21 | 0.09 | 0.12 | 160 | **0.42** | 0.72 |
| `Back+G` / `Back+S` | **IAI QUICK-DRAW** | ≥90×52 | 27 | 0.50 (noto) | 0.14 | 175 | **0.52** | 0.89 |
| `Up+G` | **GYAKU KESA** | 60×110 | 25.5 | 0.09 | 0.16 | 120 | **0.46** | 0.79 |
| `Down+G` | **SUSO-GIRI** | 110×20 | 19.5 | 0.11 | 0.12 | 90 | **0.44** | 0.76 |
| `Down+F` | Sweep kick | 52×16 | 9 | 0 | 0.12 | 40 | 0.51 | — |
| `Fwd+F` | Push kick | 46×28 | 6 | 0 | 0.12 | 300 | 0.55 | — |
| `Back+F` | Heel kick (hits BEHIND) | 44×30 | 9 | 0 | 0.10 | 60 | 0.41 | — |
| air `Down+G` | Meteor Break | body×34 | 24 | = hang | 1.2 | 60 | landing tax | — |
| `F+G` | Throw | — | 12 | — | — | — | — | — |

`Fwd+G` and `Back+G` are both **unblockable** and both free. Kicks still pay the speed tax
(owner said kicks unchanged) — that is the one remaining inconsistency.

## 2. SPECIALS (25 stamina)

| Input | Name | Box w×h | Dmg | Startup | Active | Push | Recovery | Notes |
|---|---|---|---|---|---|---|---|---|
| `H` | **THE THRUST** | 96×50 | 28 | 0.09 | 0.16 | 195 | **0.60** | armor 0.35s, tsuki slide ~84px |
| `Fwd+H` | **SHEATH CHARGE** | 92×58 | 22 | 0.24 | 0.14 | 230 | 0.52 | armor 0.34s, wall-splat |
| `Up+H` | **SKY CLEAVE** | 56×155 | 20 | 0.20 | 0.13 | 140 | 0.50 | launch −430, no armor |
| `Down+H` | **HARAI OTOSHI** | 143×26 | **22** | 0.10 | 0.14 | 150 | 0.48 | **floor-anchored + trip.** Replaced Gravewave |
| `C+H` | Bunshin (30) | — | — | — | — | — | — | counter-double |

⚠️ **He has no ranged tool.** Gravewave was it.

## 2b. THE TWO COUNTERS (20 stamina each) — Executioner only

| Input | Name | Box w×h | Dmg | Startup | Active | Push | Recovery |
|---|---|---|---|---|---|---|---|
| `Guard+G` | **SHADOW SLIP REVERSAL** | 128×46 | 26 | 0.24 | 0.14 | 190 | **0.30** hit read / **0.40** missed read |
| `G` after a block | **IRON GUARD REPRISAL** | 113×50 | 30 | **0.06** | 0.14 | 210 | 0.44 |

- **Shadow Slip** always gives the slip: `vx −300`, **i-frames 0.18s**, no crescent. The
  **counter only spawns if the opponent was in an attacking state on the press** — slip
  into nothing and you get the slip, no box, and 0.40s to think about it.
- **Iron Guard Reprisal** is armed only by `blockedAt`, stamped in the BLOCKING branch of
  `takeDamage` — it cannot be pressed without a block having actually connected. Window
  **0.22s**, one riposte per block, **armor 0.25s**, startup 0.06 because the block *was*
  the wind-up. Refused in chudan (no guard in stance).
- **Dread — corrected Aug 2 2026.** An earlier draft of this file said slip *builds* and
  reprisal *spends*. **Both do both.** The Execution rule in `spawnHitbox` fires on any
  **special-tier** box, so at dread 3 either counter comes out as the Execution. Measured:
  slip **26 → 39 dmg** (128 → 176 wide), reprisal **30 → 45 dmg** (113 → 155 wide), both
  armored 0.5s, both reset dread to 0. This is consistent with his whole special kit; the
  reprisal is just the one you *aim* to spend it with, because its 0.06 startup makes it
  the hardest to whiff.
- ⛔ **Wiring order matters:** `executeReprisal` is tested BEFORE `executeShadowSlip` on the
  heavy key. You are still holding guard during blockstun, so the reverse order would eat
  every riposte. `check_moves.py` asserts the order and it is mutation-tested.

## 3. CHUDAN — second stance (`V` / `K`)

Toggle, grounded only. **Cannot block in stance.** `×1.28 dmg / ×1.18 reach` on every
**heavy- and special-tier** box — which is 9 of his 12 attacking inputs, not just the two
rewritten normals. **Not** boosted: lights, kicks, throw.

| Input | Move | Hits | Per-hit | Timing | Recovery |
|---|---|---|---|---|---|
| `F` | Four Fast Slices (72×32) | 4 | 6 / 6 / 6 / 9 | 0.03 / 0.06 / 0.09 / 0.26 | **0.32** |
| `G` | Three Thrusts (106×22) | 3 | 9.6 / 9.6 / 19.2 | 0.04 / 0.10 / 0.17 | **0.36** |

Standing moves in stance: Fwd+G 177×24·26.9 · Back+G ≥106×52·34.6 · Up+G 71×110·32.6 ·
Down+G 130×20·25.0 · `H` 113×50·35.8 · Fwd+H 109×58·28.2 · Up+H 66×155·25.6 ·
Down+H 159×26·28.2.

## 4. DREAD → THE EXECUTION

0→3. **+1** per clean landed heavy/special (blocked doesn't count). **−1** per clean hit
taken. At 3 the next **special** is ×1.4 w, ×1.2 h, **×1.5 dmg**, armor 0.5s, then resets.

**Ceiling — THE THRUST · chudan · dread 3 = 158×60 box, 53.8 damage, armored.** Over a
third of a 150 HP bar on one button.

## 5. SPRITE SHEET FACTS (do not re-derive)

- `executioner.json` **`cols = 121`** as of `c174bbd`. Any new art appends at **index 121+**.
- `xstab1_old` (53) / `xstab3_old` (55) are retired keys, PNG byte-identical.
- **`xstab2_headless_DO_NOT_USE` (cell 54) is a TOMBSTONE, not a to-do.** It is a headless
  fragment — torso and arms, no head, no legs, floating 81px off the floor. It reads like
  unfinished work and it is not. **Do not "fix" cell 54. Do not repack it. Do not wire it.**
- **The block cells are NOT scaled wrong — owner ruling, keep them.** `block`/`xblkguard`
  (102) and `block2`/`xblkhit` (103) look short next to the idle, but measured: horn span
  86px vs idle's 82, body 149px vs idle's 184. Same head, shorter body = a chibi-er
  drawing, not a shrink. Scaling up to match height inflates the head ~24% and looks worse.
  **Do not "fix" the block scale.** Cells 10 and 58 are the sheet's only unreferenced cells
  and are old-lineage — not usable as guard art.
- Harai Otoshi currently **borrows `xlow1..5`** (104–108, the Suso-Giri cells) as a marked
  placeholder until `xharai1..6` are packed.
