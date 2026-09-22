# EMBER — everything he needs: ART and ENGINE

Measured against `web/index.html` and `web/assets/sprites/ember.json` at **SHEET_V 578**
(Aug 21 2026). Nothing here is remembered; every number has a command behind it.

**What changed since the first pass at 575:** two of the three engine defects are fixed and
verified live, and the first 34 keys of his ash look are packed. The counts below are the
current census, not the old one.

---

# PART 1 — ART

## Where the sheet stands

`252 manifest keys over 235 cells in 58 rows.` A row counts as ASH when its mean green
measures under 1%; the deleted green version runs 35-69% per row.

| | rows | keys |
|---|---|---|
| **ash — done** | 7 | **34** |
| still the deleted green | 51 | **218** |

**Ash:** `xidle` `idle` · `run_clean` `run` · `elight` · `hdown` · `gk_air`.

**Still green, all 51 rows:** `aback afwd air ajump attack_body block clawrend crouch_ ec
echarge eheavy ehook elaunch eparry eretreat erip espec espec1_v espec2_v espec3_v espec4_v
espec5_v fall grabbed hback heavy heavy_i hfwd hneu hup hurt jump kheel kneel kpush kstomp
ksweep light lowrake roll roll_ sback sdown sfwd sneu special sup upatk wallslide xblkguard
xblkhit`.

## Still never drawn

`aneu` — his neutral AIR light, six beats, nothing behind it.

⛔ **And the leap-dive row is NOT it.** The first pass named it the obvious candidate. Cutting
it and looking says otherwise: beat 5 is a **ground impact with debris**, which on a 180ms
airborne light would draw debris in mid-air. It is a dive, and the meteor is what you press
to dive — it went to `hdown`, where all six beats are physically coherent and where it also
replaced green.

The four **Ghost Killer directional** rows (`gk_fwd` `gk_back` `gk_down` `gk_up`) are drawn
and waiting on one owner decision: each comes as two takes. See
`RECOVERY/ember-ghostkiller/TAKE-A-vs-B.png` — cut, flopped, scaled and registered side by
side. No take clips the cell, so it is a pose call, not a fit call.

## ⛔ ONE ROW PER PROMPT

Body size tracks how many rows share one image. Measured on every delivery:

| layout | bodies | vs the 260px 4K min |
|---|---|---|
| **one full-width row** 2172x724 | 285-593px | **1.10-2.28x** |
| one row, the 10-frame idle | 313px | **1.20x** |
| 3-technique board 1448x1086 | 157-197px | 0.60-0.76x |
| 4x6 action board 1491x1055 | 148-214px | 0.57-0.82x |
| whole sheet 1024x1536 | 50-64px | 0.19-0.25x |

The four `REPLACE-P*.png` sheets are a brief for a **person**. Fed to a generator they came
back as pictures of sheets with the labels redrawn wrong (`htwd`, `espec1_y`, `pparry5`). Use
`row-cards/` — one card, one prompt, one strip back.

## Two size targets. Do not mix them.

His cell is **340x377**, `footY` **369**, and his idle carries a **207px** body **in-cell**.
The **260px** figure is the 4K re-cut minimum — a different, larger target.

**How the two packs anchored their scale, and why they differ:**

| pack | anchor | scale |
|---|---|---|
| 577, first form (4 rows off ONE board) | the idle's 214px upright vs the 207px in-cell | **0.9673**, one value for all four rows |
| 578, Ghost Killer (`gk_air`) | ink-area median vs his own `hneu` row | **0.7042** |

`eye_scale.py` is the house tool for picking a scale and **cannot be used on the killer
form**: his face is wrapped and he has no eye. A hood-width ruler was tried and is junk on
airborne poses — 88px to 234px across one row, because a horizontal body puts shoulders and
claws in the top band. Ink-area median is `check_row_scale.py`'s documented ruler, and two
independent references agreed on it to 1.2% (0.696 vs `hneu`, 0.688 vs the ash `xidle`).

**Ground rows keep ONE shared ground line; air rows are bottom-aligned per cell.** Measured:
`hneu` sits at y=368 on all six cells, so that is the house convention for an air attack.
Bottom-aligning a ground row per cell would pin a leap's apex to the floor and delete the jump.

---

# PART 2 — ENGINE

## Inputs: nothing is broken

`node tools/drive_real_input.mjs --name ember` — real key presses through `fireCombatKey`:
**30 presses, no dead inputs.**

`python3 tools/audit_move_coverage.py --ids 4` — **Ember 15/15 ground, 15/15 air**, and
nothing of his in the DEAD, STATIC, STANCE or ECHO buckets.

## 1. ✅ FIXED — Ghost Killer had no art gate (SHEET_V 578, `fca4735`)

`ghostKiller` was live at six sites — the blind sense in `faceCx`, the disarm, the round
reset, the V toggle, a tint colour — and **not one picked a cell**. The mode was mechanically
real and visually identical to his base form.

`emberF2Frame` is now the third router of the `shinF2Frame` shape: fighter + stance + a
sentinel row, `undefined` otherwise.

⛔ **And the specced fix was a trap.** `SPEC-directional-lights.md` said to pack the killer
strips as bare `glfwd`/`glback`/`gldown`/`glup`/`glneu` and called it zero engine work,
because that picker has no fighter gate. That is exactly what makes it wrong twice: the
wrapped face draws in his FIRST form with nobody pressing V, **and** `drewDirLight()` reads
those same three names to decide whether a press becomes a KICK — a drawn row bypasses
`executeKick` — so it would have silently deleted his push, heel and sweep. The rows are
`gk_*`, invisible to both.

Verified live: air neutral L with the mode OFF draws `air1..3`; ON draws `gk_air1..6`; air
fwd L, ground L and the meteor all fall through untouched; and in killer mode fwd+L still
fires `kpush` with wallsplat, back+L `kheel` with behind, down+L `ksweep` with low.

## 2. ✅ FIXED — the meteor drew two of six cells, for SEVEN fighters (`775c34f`)

Not an Ember bug — a roster bug his audit surfaced. METEOR BREAK is the whole roster's air
Down+Heavy. Oni alone has a drawn `dive1..6` row and the six-phase map; everyone else was on
`p.slamPhase === 1 ? F.hdown2 : F.hdown3` — a beat early on the hang, a beat early on the
plunge, **nothing at all for the floor**.

The rows were always there. Cropping `hdown1..6` on all nine sheets and looking: 1 tuck,
2 commit, 3 plunge with speed streaks, **4 an explosion at the feet** (purple on executioner
and mizu, gold on kael, dark on exile, red on tsubasa, a ground scuff on ember), 5 the landed
crouch, 6 the rise. So the fix is the row NAME, not the map.

Measured on Ember, hand-stepping `gameLoop`:

```
before   hdown2 > hdown3
after    hdown1 f1 > hdown2 f5 > hdown3 f9 > hdown4 f21 > hdown5 f34 > hdown6 f40
```

**28 drawn cells across the roster** that never reached the screen now do. Tsubasa's
`divecut1..6` is his Down+Special dive CUT and is a different move — he is one of the seven
that gain, not one of the untouched. Mokurai's three-cell row keeps the old line.

## 3. STILL OPEN — one input collision, and it is smaller than first reported

Grounded, `up+Light` replays `neutral+Light` exactly — measured with the jump suppressed:
same six `elight` cells, same 20x30 box, same 9 damage, `upAtkAnim` false.

**But Up is the JUMP key.** Driven with real key events and no suppression, W lifts him and
the input lands as an **air** up-Light, which draws `upatk1..6` and is a move of its own. So
the collision only exists in the frames before he leaves the floor, and the first write-up —
"neutral+Light and up+Light both draw elight" — was true of a state a player can barely
reach. A drawn ground up-light row still separates them with no code change; it is just not
the defect it looked like.

## 15 cells nothing can reach

`espec1_v307` … `espec5_v310` — version-tagged variants that no code path names and no string
concatenation builds. They look like deliberate history rather than junk, so they are
reported, not deleted.

**Three rows draw only through an alias**, which is fine but worth knowing: `ec` draws as
`espec`, `elaunch` as `upatk`, `xblkhit` as `block`.

---

# PART 3 — corrections to earlier claims

**`h*` and `s*` are the AIR families, not ground heavy and special.** Both `dirCells` calls
sit inside `if (p.attackAir)`. So "Heavy x5 and Special x5 are complete" was true of his
**air** matrix. His **ground** directional heavies come from the `'4:*'` table — `4:fwd`
`clawrend`, `4:down` `lowrake`, `4:back` `eretreat`; Up+G is his launcher. Ground specials
are flag-gated: `shredAnim`→`echarge`, `ripAnim`→`erip`, `hookAnim`→`ehook`.

**`kheel` and `ksweep` are NOT orphans.** They are reached by `F['k' + p.kickKind]`, built
from a string. The same scan's first version also called `xidle`, `crouch_`, `roll_`,
`elight` and `eparry` dead — a regex that required the row name *not* be followed by an
alphanumeric, when every real reference is `xidle1`.

**"air.down+H draws hdown2 for 900ms" was one sample short of the truth.** It drew hdown2
AND hdown3; the probe samples every sixth frame and the move ends when he lands. The defect
was real and bigger than reported — four cells missing, not five — and the 900ms is the
meteor's own `attackAnim.dur`, which spans the hang and the plunge and is nulled at impact.

**The leap-dive row was called a candidate for `aneu`.** It is a dive. See PART 1.

---

## Runnable checks

```
node tools/check_meteor_row.mjs                              # the six-beat meteor map
python3 tools/sprites/pack_ember_actionset.py --verify       # the 577 first-form pack
python3 tools/sprites/pack_ember_gk.py --verify              # the 578 killer gate
```
