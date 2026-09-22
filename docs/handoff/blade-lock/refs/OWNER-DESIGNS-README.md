# Exile and Oni — canon design, in words, until the owner's sheets are in the repo

Both were pulled from the blade-lock batch because every image of them in this repo is a
**superseded design** (see `../GPT-BLADE-LOCK-HANDOFF.md` §4). The owner has since supplied
the correct design for each. Those two images are **not in the repo yet** — this file holds
their canon in text so nothing is lost and nothing gets guessed at in the meantime.

**Drop the owner's two images here, with these exact names, and the pack picks them up
automatically** (`make_lock_refcards.py` looks for them):

```
docs/handoff/blade-lock/refs/OWNER-exile-run-cycle.png
docs/handoff/blade-lock/refs/OWNER-oni-founder-sheet.png
```

---

## EXILE — she/her

Owner's ruling, Aug 11 2026: *"This is the only true image of exile — if it don't look
like this it's not usable, it should be deleted."*

His reference sheet is **EXILE — LOW SHINOBI RUN CYCLE**, an 8-frame run cycle labelled
Left Contact / Left Down / Passing / Up / Right Contact / Right Down / Passing / Up-Recover,
drawn in ShadowClash chibi style on white.

| | |
|---|---|
| **Hair** | Black, long and swept back, with a **bold WHITE/silver streak** running through it |
| **Face** | **BARE — no headband, no eye covering.** Visible skin |
| **Eyes** | **TWO RED EYES**, both visible |
| **Markings** | **Red slash markings** on the cheek, and a red mark on the forehead |
| **Mask** | Black cloth mask over the nose and mouth only |
| **Outfit** | Black, with **purple/violet scarf tails** streaming behind |
| **Limbs** | **Tan/gold cloth wrappings** on the forearms and the shins; visible skin on the upper arms |
| **Weapon** | **Kusarigama** — a steel **sickle** held in hand, on a **chain** ending in a **spiked ball** |
| **Stance** | Deep, low shinobi lean — body carried well forward and down |

### ⛔ What the repo gets WRONG — do not reproduce any of it

Measured at 4x on `web/assets/sprites/exile.png`, on the idle **and** on
`run_clean1/3/5/7` — every cell has all of these:

- a tan cloth **headband with red kanji on it, covering one eye**
- a single glowing **WHITE** eye, not two red ones
- **muted grey** streaks in the hair where the bold white streak belongs
- **no** red facial markings
- an upright stance instead of the low forward lean

The portrait refs under `RECOVERY/select-portrait-handoff/refs/` are worse — pre-repack,
with baked white manga panels (74.1% and 32.6% near-white pixels).

### For the blade lock

Her **sickle** binds — it hooks an edge and holds it, and that hook is the pose. Her
**chain and spiked ball never bind**; a ball on a rope has no edge to catch. This is
enforced in the engine now: all six of her chain hitboxes carry `mat: 'chain'`.

---

## ONI — "THE FOUNDER" — he/him

Owner, Aug 11 2026: *"This is his only final character design look."* His sheet is a
four-panel design doc: main reference, an asset verification checklist, frame-by-frame
sprite specs (Idle / Startup / Active / Recovery / Attack Pose), and a visual consistency
spec.

| | |
|---|---|
| **Mask** | **WHITE skull mask** with **three claw-scratch gouges** raked across it |
| **Eyes** | **RED**, glowing |
| **Horns** | **Two**, dark brown, curving up from the hood |
| **Head** | Black hood over the mask; black cloth wrapping the lower face |
| **Body** | Black tattered mantle / cloak with a ragged fringe |
| **Armour** | **Ash-gray worn plate** — chest, bracers, knees, boots. Riveted, scratched, battle-worn |
| **Hands** | **Cloth wrappings on BOTH hands and forearms** |
| **Right hand** | **CLAW — five long dark-gunmetal blades.** Sharp, worn metal finish |
| **Left hand** | **WRAPPED, NO CLAW.** This asymmetry is the design |
| **Back** | **TWO swords carried crossed** on his back |
| **Belt** | Black sash, a leather pouch, small sheathed blades |
| **Palette** | Black, ash gray, white mask, **red eyes / red FX** |
| **FX** | The attack pose carries a **red spiral slash arc** |

### Owner's own checklist, verbatim

- Right hand claw only
- Left hand wrapped, no claw
- Hand wrappings present
- **No mirrored claw errors**
- No extra appendages

### ⛔ Two things block his cells — owner rulings, not to be inferred

1. **His animation rule fights the engine.** The rule is *"face right, never flip claw to
   left."* This engine authors every sprite facing right and **mirrors** it for the
   left-facing fighter, which puts the one-handed claw on his **left hand** the instant he
   turns around — the exact mirrored-claw error the checklist forbids. Ways out: a
   per-fighter no-mirror flag **plus a full left-facing cell set** (doubles his frame
   count), accepting the swap when he faces left, or a symmetric claw.
2. **Does the kanabo survive?** The design shows a claw and two back-carried swords and
   **no club**, but the engine still runs the Growing Kanabo Law — `WEAPON_MAT` `'iron'`,
   the `swell` mechanic, `form_1_kanabo` in his spec.

### ⛔ What the repo gets WRONG

`web/assets/sprites/oni.png` is the **pre-redesign** oni. `RECOVERY/oni-redesign/` and its
59 frames are the **white-maned, bone-pelt, PURPLE-accent** lane — a **different
character**, with no mane, no pelt and no purple in the final design. The old standing rule
*"never fix the purple out of new Oni art"* is **deleted**; following it would repaint the
wrong character.

### For the blade lock

His **claw** is metal and binds, like ember's tekkō-kagi — he traps an edge rather than
crossing blades. If the kanabo survives it binds and rings too. His **flesh/fist form must
never bind**, which the per-hitbox `mat` can now express.
