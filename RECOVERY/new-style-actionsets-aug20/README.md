# NEW-STYLE ACTION SETS — Aug 20 2026

Six strips from the owner's generator, same session as the Ghost Killer set but a different
job: these are **base-form action sets** for the roster in the new style, not a second mode.

**Status: ARCHIVED, NOT PACKED.** No sheet, no manifest key, no `SHEET_V` move.

Each strip is 2172×724 and carries six poses in one row — **idle, run, crouch, jump,
guard/ready, attack-with-FX**. That is the P1-core set: a fighter cannot appear in a match
without those.

| file | reads as | why |
|---|---|---|
| `actionset-shin.png` | **Shin** | green hood, teal scarf, cyan eyes, shuriken |
| `actionset-tsubasa.png` | **Tsubasa** | no hood, spiky black hair, twin daggers, red |
| `DELETED-green-form/ember-GREEN-form-DELETED.png` | **⛔ NOT A FORM** | Ember's green look. Owner, Aug 21: *"the form is gone completely."* Never generate against it. |
| `actionset-kael.png` | **Kael** | black + gold, gold eyes, **two katanas drawn**, gold slash FX |
| `actionset-UNIDENTIFIED-red-eye-katana.png` | **the Executioner** | black hood, red scarf, red eye, one long katana — **missing his horns, see below** |
| `actionset-UNIDENTIFIED-horned-red-eye-dagger.png` | **the Executioner** | horned hood, red scarf, red eye — correct as delivered |

## ⛔ BOTH "UNIDENTIFIED" FILES ARE THE EXECUTIONER — and HORNS ARE CANON

**Owner ruling, Aug 20 2026:** *"the one without the horn — add horns to executioner."*

So the horns are his, and the file that lacks them is the one that is wrong:

| file | verdict |
|---|---|
| `actionset-UNIDENTIFIED-horned-red-eye-dagger.png` | **the Executioner, correct.** Horns present. |
| `actionset-UNIDENTIFIED-red-eye-katana.png` | **the Executioner, WRONG — no horns.** Needs them added to all six frames. |

Three independent confirmations back this up: the long-katana technique board is titled
**LONG KATANA** and his `weapon:` is **Long Sword** (he is the roster's only one-long-blade
fighter); that board's row 2 is **Chūdan-no-Kamae**, and he is the **only fighter in the game
with `idle_chudan` art**; and the horned hood matches his shipped silhouette. Rename both
files once the owner confirms the naming.

### The fix is a re-render, not an edit — `EXECUTIONER-add-horns-spec.png`

Adding the horns locally was attempted and **abandoned**: the extracted horn carries a flat
cut edge where it left its own dome, which shows the moment it lands on a differently-curved
hood, and the head angle changes across the six poses so one pasted sprite cannot serve them
all. Compositing produced horns floating beside the head with a visible rectangular seam.

It does not need an edit anyway — **the generator already draws this character with horns**,
in `actionset-UNIDENTIFIED-horned-red-eye-dagger.png`. So the spec sheet pairs the hornless
set with his own horned head and states the whole change in one line:

> Keep: black hood, red scarf, RED eye, one long katana, the poses exactly as drawn.
> Change: two horns on the hood — one larger curving forward, one smaller behind. Nothing else.

### Removing horns is the direction that does not work

Recorded so nobody tries it: the reverse edit — cutting horns OFF the horned art — was
attempted three ways (morphological opening, a fitted dome profile, and a wide grey-closing
at four radii) and all three leave the same two stubs. The horn **base** is only 8–10px, 9–11%
of the 94px dome, so the tips cut cleanly, but the base **flares into the hood below the
silhouette line** where horn and hood are the same near-black with no seam — no colour signal
and no shape signal to cut on. The first attempt also deleted an eye and left a straight cut
across the scarf. **Add horns to the hornless art; never subtract them from the horned art.**

## One canon note on Kael

`actionset-kael.png` shows him with **two drawn blades**, which fixes the thing flagged on
his idle strip — that one had a single sword out and a second sheathed, both reading
full-length, where canon is one long + one short. Check the two blade lengths against each
other on beats 5–6 before packing.

---

## Aug 20, later — two more SHIN strips (idle REDO + his run)

Archived, not packed. Both 6/8 beats, background corner 253, zero edge contact.

| file | frames | verdict |
|---|---|---|
| `shin-idle-6f-REDO.png` | 6 | **Owner approved, Aug 20: "i like it."** Frame 4 drops the head ~28px while his feet hold (4px drift) — he looks down for one beat. That is a DELIBERATE NOD, not a defect, and it is the beat that gives the loop its character. Heights `[252,251,257,225,255,253]`. See the packing note below — this pose must survive to the screen. |
| `shin-run-8f.png` | 8 | **Structurally a real run** — and that matters, because still-generators have historically returned a standing stance for locomotion (8/8 failures on record). Leg spread alternates extended/passing across the cycle: `0.83 0.83 0.97 0.74 1.06 0.63 0.99 0.75`. That is stride, not stance. |

### The run is drawn ~0.79x the idle — fix it here, not by regenerating

Four independent proxies agree, so this is not a pose artefact:

| proxy | idle | run | run/idle |
|---|---|---|---|
| hood width, top 20% | 134.3px | 106.5px | 0.793 |
| hood width, top 25% | 179.7px | 137.1px | 0.763 |
| hood width, top 30% | 186.8px | 156.1px | 0.836 |
| sqrt(ink area) | 38297 | 23455 | 0.783 |
| body height | 248.8px | 199.0px | 0.800 |

This is the **Kael run incident repeating** (his packed run sits at 0.70x idle — "he sprints
at duck height"). Per §2 law 2 and law 4 the answer is ONE uniform upscale for the whole
sequence anchored on **head geometry**, roughly **x1.26**, applied at pack time — never
per-cell MATCH_HEIGHT, and never a regeneration. Size is this repo's job, not the
generator's. After scaling, run bodies land ~236-273px against Shin's 250px 4K minimum.

### ⛔ The nod is APPROVED — so this idle must NOT be height-flattened

Owner, Aug 20 2026, on frame 4's head drop: **"i like it."** That settles it — the beat is
intentional and it ships.

It also decides how the row packs, and the default would destroy it. **MATCH_HEIGHT per-cell
flatten is the house look for grounded loops** (§2 law 1, wobble target 0.0%) — and running
it here would stretch frame 4 by ~12% to match its neighbours, pulling the lowered head back
up and deleting the nod. The row would measure perfect and look wrong.

**Shin's idle is a pose-varying family, so it takes head-anchored scaling, not height
flattening** — which is exactly what §2 law 4 already says: *"A crouch, tuck, or lunge is
SHORTER because of the pose — total ink height across different poses is not a scale signal.
Only same-pose frames compare by height."* Measure his hood, not his silhouette, and let the
28px live.

Same rule, opposite conclusion, one row apart: the idle keeps its height variation because
the variation is the animation; the run gets one uniform upscale because its variation is a
size error. Both are decided on head geometry.
