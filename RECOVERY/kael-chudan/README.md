# KAEL — CHŪDAN-NO-KAMAE (V), his second form

Owner boards, Aug 21 2026, eight strips at 2172×724 — the one-row-per-image layout.
Packed with the twenty-one form-1 attack rows at **SHEET_V 576**
(`tools/sprites/pack_kael_576.py`), 167 cells, atlas 217 → 384.

| board | key | beats | where it fires |
|---|---|---:|---|
| Setting the guard | `xcentry` | 6 | 0.30 s on the V press, then it settles |
| Stance idle | `idle_chudan` + `idle_chudan2` | 2 | held, breathing |
| Chūdan Slices | `xcslice` | 6 | Light, neutral |
| Chūdan Multi-Thrust | `xcthrust` | 6 | Heavy, neutral |
| Chūdan Tsuki | `xctsuki` | 6 | Heavy, forward |
| Chūdan Sheath Charge | `xcfwdh` | 6 | Special, forward |
| Chūdan Sky Cleave | `xcuph` | 6 | Special, up |
| Chūdan Harai | `xcdownh` | 6 | Special, down |

Every direction he did NOT draw falls through to Form 1. Driven live: chudan Fwd+Light
comes back as `kpush`, his form-1 push kick, which is the design and not a gap.

## The keys collide with the Executioner's, and that is fine

A manifest is per fighter, so `xcslice` on kael.png and `xcslice` on executioner.png are
two different pictures. Nothing of his changes and nothing is shared.

What could NOT be shared is the **draw path**. Every `xc*` branch in the engine is gated
`spec.id === 0` *and* on a flag only the Executioner's own triggers set — `stabAnim`,
`sheathAnim`, `skyAnim`, `lowCutAnim`. Kael would have toggled into a stance that drew
nothing at all. `kaelChudanFrame()` reads the captured input DIRECTION instead, which is
exactly what these boards are labelled by, and it is filed with the other second-form
routers (Shin's Kage-Nui, Tsubasa's Sakate) — above the state switch, below the KO row.

## The V toggle needed no wiring

`modeKey()`'s bare-V fall-through already gates on the sheet carrying an `idle_chudan`
cell rather than on a fighter id. **Packing the cell IS the wiring.**

He also picks up the stance's roster-wide trade: **×1.28 damage, ×1.18 reach, and NO
GUARD while it is held.** That is the deal the stance has always carried
(`spawnHitbox`, and the guard branch is unreachable while it is set) — not something
added for him. Owner call if Kael should get different numbers from the Executioner.

## Proof

- `proof/kael-576-contact.png` — all 167 packed cells, 29 rows
- `proof/kael-chudan-stance.gif` — the guard being set, then held
- `proof/kael-chudan-moves.gif` — the six stance moves
- `proof/kael-form1-*.gif` — the twenty-one form-1 rows
- `proof/gate.png` — in-game, form 1 beside chudan. Feet at GROUND_Y 712 in both.

Measured, not eyeballed: form-1 idle **171px** body, chudan idle **170px**, every new
row's ready beat **170–171px**. 0.4% variance, so there is no size boil between the
forms or against the art already on the sheet.

`node tools/check_kael_576.mjs` (static) · `node tools/drive_kael_576.mjs` (live input).
