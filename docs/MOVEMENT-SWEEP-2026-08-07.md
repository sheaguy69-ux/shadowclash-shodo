# Roster movement sweep — 2026-08-07

Owner order: *"I don't want to see no character lifting/floating off the surface of the
ground on no stage. every character should be level and grounded to the surface"* and
*"any character facing backward, correct it."*

Two defects. **The grounding half is fixed and verified. The facing half is measured and
reported but NOT applied** — it changes how art reads, and AGENTS.md 3 says the owner sees
the frames first.

---

## 1. GROUNDING — fixed (SHEET_V 385, commits `044d7d2` + `62529a7`)

### The cause was the engine, not the art

Which is why it showed on *every* stage. `drawSprite` applied two whole-body transforms
that both carried the planted foot with them, while the contact shadow stayed nailed to
`GROUND_Y + 2`.

**a) `bob` — a whole-sprite TRANSLATE.** Idle sway and the stride bounce lifted the entire
sprite, boots included. Measured peak float, in SCREEN px:

| | run | idle |
|---|---|---|
| Mizu | **6.5** | 0.7 |
| Ember | **5.2** | **2.2** |
| Shin | **5.1** | 1.8 |
| Tsubasa | **4.0** | 1.6 |
| Kael | **3.2** | 1.4 |
| Executioner | **2.4** | 0.8 |

And **no fighter's run cycle ever reached 0** — across the whole stride, Mizu's *closest*
approach to the floor was 1.2px and Shin's was 2.1px. They never touched down at all.

Now a **feet-anchored vertical stretch**: same head amplitude, but `y = 0` *is* the sole
line, so a scale about that origin cannot move the boots. The bounce survives; the float
cannot. (Idle also no longer *sinks* — the old `±sway` spent half of every breath below
the floor.)

**b) `rotate(lean)` — pivoted about the feet anchor.** At a full sprint `targetLean`
reaches 0.35 rad (~20°, and the underdamped spring overshoots past it), which swings the
trailing foot ~4px into the air and drives the leading foot the same distance *through*
the floor. Neither level nor grounded.

Now a **shear**: `x' = x + lean*y`. The head displaces by essentially the same amount
(0.35 vs sin 0.343) and the feet stay planted **and level**. It also drops the `-p.facing`
term the rotate carried, which was inverted — running LEFT, the old rotate tilted the body
*backward*, away from the direction of travel.

Both faults were already on record **against Oni alone** ("he stood floating on top of the
surface", "running off the ground, tilted, folding") and had been patched for him only.
This is the same fix for the rest of the roster.

### Per-cell art corrections

New `footAdj` / `mirror` maps in the manifests, read by `drawSprite`. **Data, not pixels** —
sheets stay append-only, not one art byte moves, and every entry is reversible.

| fighter | cell | fix | why |
|---|---|---|---|
| executioner | `attack_body3` [31] | +19 sheet px | the THROW animation, hovering **7.2** screen px |
| executioner | `attack_body4` [32] | +26 sheet px | same throw, hovering **9.9** screen px |
| mizu | `special2` [15] | +7 sheet px | rooted parry/special stance popping **2.8px** against a planted `special1` |
| mokurai | cells 0–34 | mirrored | see below |

### Verified in the live engine, not by reading the source

Instrumented `drawImage` in the running game and swept both players through idle plus the
full 8-frame run cycle: **foot anchor = 440 = `GROUND_Y` on all 32 samples**, **rotation
component 0 on all 32**, `scaleY` 1.0 → 1.0625 (the bounce, feet-anchored).

### Rejected after measuring — do NOT "fix" these

- **Shin's `flying_kick1..6`** looked like five hovering beats of a grounded special. It is
  not: `index.html:5615` does `isGrounded = false; vy = -185`. His neutral Special **is an
  airborne rush**. A correction was applied and then **reverted** — planting those cells
  would have dragged an airborne pose to the floor.
- **executioner `attack_body1`/`attack_body6`** (2.28px) — inside the contact shadow's own
  vertical extent (semi-minor ≈ 4px), so no visible gap. Ember `special2` (2.01px) dropped
  for the same reason.
- **executioner `xharai5`** [179] — 16+ silhouette columns sit within 1.2px of the floor;
  it is feet contact, not a lone sword tip.
- **Run-stride flight frames** (Mizu `run_clean4/8`, Tsubasa, Kael) — a real run leaves the
  ground between footfalls. Confirmed intentional by the Jul 25 audit; left alone.
- **Dead cells** — mizu `run1/run2/heavy1/heavy2/heavy3` etc. measure badly but are
  unreachable, so they cannot hover on screen.

---

## 2. FACING — reported, NOT applied (except Mokurai)

Every sheet is authored **facing LEFT**; `drawSprite` mirrors toward the opponent. A cell
packed facing RIGHT therefore plays **turned away from the opponent for the whole move** —
this is the "facing backward" in the order.

### Shipped: Mokurai cells 0–34 — one packing error, not 25 defects

The 41-frame GPT page added in `030cf45` was packed **unmirrored as a block**: ear LEFT,
third-eye ruby RIGHT, scarf trailing LEFT — the exact mirror of `canon_idle[50]`,
`bidle1[87]` and `blight1[59]`, which all put ear RIGHT, ruby LEFT, scarf RIGHT. Flipping
the block restores canon; verified against the canon cells side by side. `mwall`/`roll`
cells are outside the block and untouched.

This one shipped because **canon proves the intended orientation**. The rest below has no
such reference, so it is your call.

### Needs your ruling

| fighter | cells | what |
|---|---|---|
| **tsubasa** | 46 | the largest block |
| **executioner** | 35 | the whole directional set — `afwd/hfwd/hup/hdown/sfwd/sback/sdown/sup`. `aback` and `sneu` are correct and excluded |
| **oni** | 12 | includes the brand-new mode-III board (`m3_snap_cut`, `m3_overhead_cleave`, …) from SHEET_V 381 |
| **ember** | 8 | `attack_body1..6` + `kpush`/`kheel` |
| **kael** | 4 | 3 are SHOWS_BACK (a flip will not fix those — they need dropping or re-pointing) |
| **shin** | 2 | `special2`, `kpush1` |
| **mizu** | 1 | `staffspin3` — back to camera |
| **exile** | 0 | clean, both audits |

Review sheets, top row = as packed, bottom row = flipped:
`<scratch>/review/<fighter>-facing-review.png`.

**Honest caveat.** The automated adversarial verification of the *executioner* facing list
is unreliable — I had written mirror flags into `executioner.json` while those verifiers
were running, and `floor_proof.py` honours that flag, so several of them judged cells I had
already flipped and reported "already correct". The flags were reverted; the verdicts were
discarded. My own read at 4× full-body (face position + scarf side) says the block IS
mirrored, and both a dark-cowl-centroid and an orange-scarf-centroid classifier separate
the two groups — but neither classifier was clean enough to drive 35 cells on its own, so
nothing shipped. **Not verified — you must confirm.**

Applying a ruling is one command per fighter, e.g.:

```bash
python3 tools/sprites/apply_cellfix.py executioner --mirror 241 242 243 245 253
```

⛔ **A family must flip whole.** Half a family flips the character back and forth mid-move,
which is worse than the bug.

---

## Tools added

- `tools/sprites/ground_audit.py` — every cell's contact line, body line and support%
  against `footY`, in sheet and screen px. Per-COLUMN, per the Jul 25 method: a whole-cell
  "lowest ink" check misses a fighter propped up on a weapon.
- `tools/sprites/floor_proof.py` — renders cells exactly as `drawSprite` anchors them,
  against the floor line and the real contact shadow. Honours `footAdj`/`mirror`, so it
  shows what the engine draws rather than the raw packing.
- `tools/sprites/apply_cellfix.py` — writes the measured `footAdj` / `mirror` maps.
