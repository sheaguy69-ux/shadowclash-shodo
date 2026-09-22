# THE EXECUTIONER — everything still owed to finish him

Aug 21 2026. Built by measuring his manifest against what the engine actually draws
(driven live through the real `executeAttack` and frame picker), then subtracting
everything delivered today. Under the CLEAN-SLATE ruling every pre-today frame is
invalid, so this is the full regeneration order, not a gap list.

**Format for every line below: ONE ROW OF 8 (or the stated beat count), captions
underneath, captions kept to THREE lines.** That layout has now returned 1.12–1.64×
of target ten times running. A grid returns 0.50–0.59×. See the layout series in the
archive README.

**Target: 300px+ of drawn body.** His 4K minimum is 270px; generate above it for margin.
**Face LEFT** if the generator will do it — everything so far has come back facing right
and needs a `-flop` before keying.

---

## ✅ DONE — delivered today, passes, nothing to reorder

| board | covers |
|---|---|
| URONAME 1 **Kiriage** | `xkiriage` — Up+Heavy, Gyaku Kesa |
| URONAME 2 **Tsuki** | `xctsuki` / `xtsuki` — Fwd+Heavy, Drive Stab |
| URONAME 3 **Nukiuchi** | `xnukiuchi` — Back+Heavy, Iai Quick-Draw |
| URONAME 4 **Gedan Deception** | NEW move — the second deflect |
| URONAME 5 **Metsubushi** | NEW mechanic — blinding powder |
| `glfwd` **Kirikomi** · `glback` **Hiki-giri** · `glup` **Age-tsuki** | the light tier |
| CHŪDAN STANCE SHEET | **the index** — owner ruling "yes keep", not cut for cells |

## ✅ FIXED — both, in the tree, nothing to redraw

| item | what was wrong | what it is now |
|---|---|---|
| `gldown` **Sune-giri** beat 8 | his katana ran off the right frame edge | **`exec-GLDOWN-sune-giri-8f-FIXED.png`** — beat 8 is the same drawing as beat 1 (89.3% IoU at dx 1262), so the missing 12 columns of tip were lifted from beat 1 rather than invented; canvas grown to 1484 with 24px of paper past the point. Every original pixel byte-identical. `fix_gldown_b8.py` |
| `aneu` **Kesa-giri** beats 7–8 | a grounded landing on an airborne row | **`exec-ANEU-kesa-giri-6f+LAND2-FIXED.png`** — the row splits where the art splits: **1–6 → `aneu1..6`**, **7–8 → `aland1`/`aland2`**, a landing tail the engine now draws only once he touches down. Nothing is discarded, and it is the first drawn air-attack landing recovery any fighter has. `fix_aneu_split.py` |

---

# THE ORDER — 40 strips, ~233 cells

## A · CHŪDAN STANCE — 8 strips, 44 cells
The stance sheet is the reference to hand the generator; these are the cuttable rows.

| strip | beats | move |
|---|---|---|
| `idle_chudan` | 2 | the stance idle |
| `xcentry` | 6 | setting the guard |
| `xcslice` | 6 | Chūdan Slices — Light neutral |
| `xcthrust` | 6 | Chūdan Multi-Thrust — Heavy neutral |
| `xctsuki` | 6 | Chūdan Tsuki — Heavy forward *(may be cuttable from URONAME 2)* |
| `xcfwdh` | 6 | Chūdan Sheath Charge — Special forward |
| `xcuph` | 6 | Chūdan Sky Cleave — Special up |
| `xcdownh` | 6 | Chūdan Harai — Special down |

## B · HIS NAMED GROUND MOVES — 9 strips, 54 cells

| strip | beats | move | input |
|---|---|---|---|
| `xnuki` | 6 | **Nukitsuke** light cut | Light, neutral |
| `xjodan` | 6 | the overhead | Heavy, neutral |
| `xsuso` | 6 | **Suso-Giri** | Heavy, down |
| `xbtsuki` | 6 | the thrust | Special, neutral |
| `xsheath` | 6 | **Sheath Charge** | Special, forward |
| `xskycleave` | 6 | **Sky Cleave** | Special, up |
| `xharai` | 6 | **Harai Otoshi** | Special, down |
| `xslip` | 6 | **Shadow Slip** reversal | Guard + Heavy |
| `xreprisal` | 6 | **Iron Guard Reprisal** | Heavy right after a block |

## C · THE AIR KIT — 16 strips, 85 cells

| strip | beats | |
|---|---|---|
| `hneu` `hfwd` `hback` `hup` `hdown` | 6 each | air HEAVY, all five directions |
| `sneu` `sfwd` `sback` `sup` `sdown` | 6 each | air SPECIAL, all five directions |
| `afwd` `aback` | 6 each | air LIGHT forward / back |
| `ajump` | 6 | the jump arc |
| `jump` 2 · `fall` 2 · `air` 3 | | takeoff, descent, the shared aerial |

## D · LOCOMOTION & STATES — 6 strips, 22 cells
`idle` 2 · `run_clean` 8 · `crouch_` 4 · `roll_` 6 · `wallslide` 1 · `kneel` 1

## E · REACTIONS — 3 strips, 17 cells
`hurt` 3 · `grabbed` 8 · `attack_body` 6

## F · DEFENCE — 3 cells
`block` 2 · `xblkguard` 1 · `xblkhit` 1
*(`xblkhit` is packed today and named by nothing — wire it or drop it.)*

## G · `kstomp` — 1 cell
The air-down stomp. **`kpush`, `kheel` and `ksweep` are NOT reordered** — the new
`glfwd` / `glback` / `gldown` rows take those inputs, so his kick poses are retired.

## H · ⛔ BLADE LOCK — 6 cells, and NOBODY IN THE ROSTER HAS THEM
`lock1 … lock6`. The engine is built and waiting: cells **1–2** are the catch and the
settle (played once), the middle **loops as the strain**, and **the last two are always
WIN and LOSE**. With none packed it holds ONE static guard cell — deliberately, so the
gap stays visible. This is a shipped signature mechanic currently drawing a still frame.

## I · `idle_waki` — 2 cells, OWNER CALL
A **third** stance idle (waki-gamae) is packed on his sheet and named by nothing.
Wire it as a real stance or drop it.

---

# ⛔ THREE DECISIONS THAT GATE WORK

1. **What does BLINDED do?** Metsubushi's art is in hand but nothing in the engine
   blinds. Lose the sprite? Lose aim? Stagger? Guaranteed follow-up?
2. **ONE eye or TWO?** Every new board draws one; the shipped fighter draws two angled.
   Whichever loses is a repaint of the other set.
The `glback` question is **settled and built**: it does **not** keep `behind`. His own
board puts the clash spark in FRONT of him on beat 5 — Hiki-giri cuts forward while the
body withdraws — and Oni's glback is a backflip arc. A box spawned behind a fighter whose
blade is in front of him is the frame-physics mistake. `behind` stays with the heel kick,
which is still what the other seven fighters get.

The kick properties are no longer owed either. A drawn row now inherits what the kick it
replaced carried — `gldown` → `low` + `trip`, `glfwd` → `wallsplat` + `puntLogs()` — off one
shared derivation (`drewDirLight`). That was not a future problem: **Oni draws glfwd today
and his shove had silently stopped splatting and stopped punting logs.** Measured live on
:9100, 9 fighters x 3 directions. `tools/check_dir_light_props.mjs`.
