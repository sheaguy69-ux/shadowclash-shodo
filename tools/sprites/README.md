# Sprite pipeline

How animation cells get made, checked and packed into `web/assets/sprites/`.

Read this before generating anything. Most of it is written from failures that cost
real money.

---

## 1. Models

Model IDs live in **one** file: [`fal_models.py`](fal_models.py). Import them; never
hardcode an ID.

| Role | Constant | Notes |
|---|---|---|
| Motion (i2v clips) | `MOTION_MODEL` | Seedance 2. The ID has **no** `fal-ai/` prefix — that prefix selects the old 1.x family and silently returns worse frames. |
| Stills / repose / prop edits | `STILL_MODEL` | nano-banana-pro. Takes `image_urls[]`, a **list**. |
| Fallback motion | `MOTION_MODEL_KLING` | Holds framing better than Seedance, with drift of its own. |

`i2v_clip()` forces `generate_audio=False` — sprites are silent, and audio is wasted
spend on a bigger download.

**A still editor cannot invent a pose.** It returns the reference's stance however you
word the prompt, so locomotion and attacks must come from i2v. What it *can* do is
change a garment, prop or weapon while holding a pose — see §7.

---

## 2. Prompt architecture

Four isolated blocks, never one paragraph:

```
[SUBJECT + ANCHOR] → [MOTION / ACTION] → [CAMERA] → [ENVIRONMENT & STYLE]
```

- **Subject** anchors literally to `[Image 1]` and states **limb count, weapon count
  and weapon size** as hard constraints. Locking the camera does not lock anatomy.
- **Copy the character description verbatim** between prompts. "ninja with a blue
  belt" vs "blue-belted ninja" is enough licence to redesign him.
- **Camera** uses closed verbs — `locked-off tripod shot`, `fixed wide lens, zero
  zoom`. Never `dynamic camera` or `cinematic movement`.
- Clips beyond ~4s need **timeline prompting** (`[0s-1s] … [1s-2s] …`), or the poses
  collapse into one held frame.

### Camera lock is an input-side problem

Measured on one subject, 121 frames per run:

| Approach | Frames fully edge-clean |
|---|---|
| Camera paragraph mid-prompt | 40 / 121 |
| Verbose framing paragraph | 4 / 121 |
| `Camera:` one-line format alone | **0 / 121** |
| **+ padded input + `end_image_url` pin** | **121 / 121** |

Text alone does not hold the frame. Seedance re-crops the *subject* regardless of the
camera line — a different failure from camera *movement*. Two fixes, used together:

1. **Pad the reference** so the character is ~60% of frame height. Seedance dollies by
   a roughly fixed *percentage*, so the crop lands in the padding.
2. **Set `end_image_url = image_url` even on one-shots.** `i2v_clip()` only does this
   for `loop=True`, so pass it explicitly. It forces framing to resolve back to the
   start, confining drift to mid-clip.

---

## 3. Check canon *before* packing

`media/polished-candidates/<fighter>/identity-true.txt` is the fighter's lock:
palette, weapon count, and the FORBIDDEN list. Open it before packing, not after.

Ember shipped with **four** claws per hand across three commits because that file —
which says three — was read too late. It is the cheapest check available.

Where a doc and the identity file disagree, the identity file and the master art win.
Doc 17 claimed Kael carried "two equal long swords" while `kael.json` had said
*Katana & Wakizashi* all along. The doc was wrong.

---

## 4. Harvesting frames

Extract at 24fps for attacks, 12–16fps for cycles, then **measure**. Do not eyeball.

- **Edge clipping** — ink on the first or last column, or the top row, means the frame
  is cropped. The bottom row is the ground line and is expected.
- **Pose collapse** — compute pairwise distance across the chosen cells. A pair an
  order of magnitude closer than the rest is a duplicate, not a beat. Hand-picking a
  "recover" frame failed three times running on one clip whose entire tail was a
  single held guard.
- **Automate the pick, then look anyway.** A farthest-point search over clean
  candidates beats choosing by eye — but a motion-blur swoosh passed every numeric
  filter and only the eye caught it. Use both.
- Downsample to ~180px before pairwise comparison; full-res over 20 frames times out.

---

## 5. Read the flaw before you "fix" it

A frame is only broken relative to what you intended it for. Triage before salvaging —
some defects are worth more used than corrected.

| Defect | Better read as |
|---|---|
| Blade missing from the hand | a **speed frame** — real 2D fighting games omit the weapon on the fastest cell of a cut and let the arc carry it; it returns next cell |
| Motion blur smearing a limb | a **smear frame** between two clean keys |
| Character mid-rotation | a **turnaround** or dodge beat |
| Pose collapsed toward idle | a **recovery / zanshin** hold |

Worked example: Executioner's stance clip was rejected because "the blade vanished". He
is holding the **hilt** with the saya at his back, body already coiled and side-on —
which is *nukitsuke*, the instant the blade clears the scabbard. It is a better draw beat
than anything generated deliberately for that slot.

Send only the genuinely wrong frames to §7.

---

## 6. Blade wielders use real technique

Every blade pose must resolve to a **named technique from that fighter's school**, never
a generic swing. "A sword rotating around a man standing still" is the exact defect this
rule exists to prevent — it shipped once on both swordsmen and had to be re-cut.

| Fighter | School | Vocabulary |
|---|---|---|
| executioner | Ittō-ryū · Iaijutsu / Battōjutsu | kamae: Jōdan, Chūdan, Gedan, Hassō, Waki · cuts: kesagiri, gyaku-kesa, tsuki, nukitsuke · chiburi, nōtō, zanshin |
| kael | Niten Ichi-ryū | short blade parries while the long blade cuts, **same instant**, blades at different heights |
| tsubasa | Shōtō Nitōjutsu | reverse grip, elbows tucked, tight inside-range cross-slices — no wide swings |
| mizu | Bōjutsu | strikes from the staff ends via sliding grip and rotation about the centre |
| ember | Tekkō-kagijutsu | raking and trapping; wrist and elbow lead, not a blade arc |

The edge aligns with the cut path, the hips drive it, and weight transfers back leg to
front. `salvage_frames.py` injects this per fighter automatically; write it into
generation prompts too.

Source: `research/opus5-shadowclash-prompts.md`.

---

## 6b. Shop the salvage library FIRST — it is not a last resort

**Owner standing order (Jul 30 2026): "look through the salvage frames to re-edit
them into desired frames. We only use nano banana with absolutely needed."**

`media/salvaged-poses/` holds ~1,975 already-paid-for frames across 8 fighters.
Before writing a single generation prompt, contact-sheet the relevant fighter's
folder and look. A pass over it for a Kael + Executioner move list found, sitting
there unused: an overhead raise (an upward launcher), forward lunges with the
blade extended, airborne dives, and — for Kael — several genuine TWO-BLADE poses
with the short blade forward and the long blade cocked, which is his whole
Niten Ichi-ryū identity.

```bash
# 40-frame contact sheet of what you already own
python3 - <<'PY'
import subprocess, glob
files = sorted(glob.glob('media/salvaged-poses/<fighter>/*.png'))
sel = files[::max(1, len(files)//40)][:40]
# resize -> +append rows of 8 -> -append
PY
```

These render on WHITE with drop shadows, so they need the usual `FUZZ=42`
corner floodfill plus largest-connected-component keying — free, already scripted.
`magick montage` needs an explicit `-font`; build rows with `+append` instead.

Cost check that makes the point: of one seven-move batch, six moves were already
covered by salvage or by an unused on-sheet cell, and exactly one needed a paid
edit. Ordering it the other way round would have been ~$1 of avoidable spend and
several regenerations of poses that already existed.

---

## 6c. Two nano-banana behaviours that cost retries

Both learned the expensive way on the Executioner's light strike.

**The pose reference carries LIMB DIRECTION — prose does not override it.** Asked
for a blade pointing forward while handing it a pose cell whose blade sweeps back,
it returns the blade sweeping back, every time, however emphatic the wording
("⛔ THE BLADE POINTS TO THE LEFT OF THE PICTURE" did not move it). Pick a
reference that already holds the direction you want, then describe the rest.

**It duplicates the character unless explicitly forbidden.** A clean render came
back with a second partial body across the bottom of the frame. "Only this one
character is in the picture" was already in the prompt and was not enough; the
components overlapped, so neither a crop nor largest-connected-component could
separate them. What worked:

> EXACTLY ONE FIGURE IN THE IMAGE… Do NOT repeat, duplicate, mirror, reflect or
> echo the character anywhere in the picture. No second body, no partial body, no
> cropped torso or legs at the bottom or edges… no reflection on the ground.

**Check facing against the sheet, not against intuition.** These sheets author the
fighter facing LEFT with the blade trailing RIGHT (`drawSprite` mirrors with
`scale(-p.facing, 1)`). A frame that looks "backwards" next to the idle cell is
usually correct — compare it to `idle` before calling it a defect.

---

## 7. Salvage before regenerating

`salvage_frames.py` recovers failed clips instead of paying for new ones. Full method:
`syntheses/sprite-frame-salvage-pipeline.md`.

```bash
python3 tools/sprites/salvage_frames.py <fighter> <subdir> frames/*.png
```

It passes **two** references to nano-banana-pro — `[failed frame, canonical master]` —
so the failed frame supplies the *pose* and the master supplies the *identity*. That is
why it recovers frames a single-image edit cannot. Output renders on `#FF00FF` and is
chroma-keyed: magenta because these sprites carry white highlights and near-white
steel, so a white key eats the blade. (`-fuzz` must precede `-transparent`, or the flag
is silently ignored.)

| Failure | Recoverable? |
|---|---|
| Rotated off side profile | **Yes** — limb positions and weapon angle survive |
| Cropped by the frame edge | **Yes** — redrawn full-body |
| Motion blur | **Yes** — resolves to readable steel |
| Oversized or wrong weapon | **No** — read as pose data and preserved |

Salvage can introduce *new* drift: a recovered Kael frame returned two blades of equal
length, losing his long+short pairing. Re-check every output against
`identity-true.txt`.

Recovered frames live in `media/salvaged-poses/<fighter>/` (gitignored) as a reusable
pose library. Start there before going back to Seedance.

---

## 8. Packing

```bash
FUZZ=42 FIXED_SCALE=0.185 python3 tools/sprites/extend_sheet.py <fighter> \
    <frames_dir> <base_png> web/assets/sprites pose1 pose2 …
```

`FUZZ=42`, not 25 — the lower value leaves the i2v drop-shadow behind.

### Choosing a scale

| Use | When |
|---|---|
| `MATCH_HEIGHT` / `MATCH_HEIGHT_PX` | Cells whose bodies must read identical — idles, walk and run cycles. Flattens per cell; the engine's bob supplies the bounce. |
| `FIXED_SCALE` | Frames from **one** clip where pose height legitimately varies — attacks, jumps. The clip's own registration is the size guarantee. |

Getting this backwards manufactures the frame-to-frame shrink the owner keeps
rejecting. When a long weapon changes angle across the window, bbox height changes
without the *body* changing, and per-cell flattening pushes that swing into the torso.

### Sheet rules

- **Append-only.** Add cells, repoint names in the JSON, keep old cells addressable
  (`*_old`, `*_v309`). A revert is then a JSON edit, not a regeneration.
- **Verify byte-identity** of the pre-existing region after every pack —
  `magick compare -metric AE` must return `0`. Crop at the sheet's *own* width; a check
  run at the wrong width once reported 36,320 phantom diffs.
- **Bump `SHEET_V`** in `web/index.html` in the same commit as any sprite change.
- **Grow the cell, never shrink the fighter.** `extend_sheet.py` clamps anything larger
  than the cell box, silently shrinking that pose. Ember's cell went 300→340 for a wide
  claw pose; Executioner's went 320→327 for a jump.

### Geometry is per-fighter

Never assume `300×320`:

| | frameW | frameH | footY |
|---|---|---|---|
| ember | **340** | **377** | 369 |
| executioner | 300 | 327 | 319 |
| kael · mizu · shin | 300 | 320 | 312 |
| mokurai | 300 | 226 | 218 |
| exile | **200** | 226 | 218 |
| tsubasa | **301** | 320 | 312 |

Read it from the manifest, every time.

---

## 9. Gates before shipping a cell

- `components == 1` — a detached blob is a surviving drop shadow or FX fragment. Fix by
  largest-connected-component keying on the **source** frame.
- `edge alpha == 0` on sides and top.
- Bottom row sits exactly on `footY`.
- No off-palette colour. A generator once invented 43 purple pixels on Kael, whose
  palette is black and gold.
- **Never colour-correct a packed cell by tolerance.** A 300px cell has no colour
  headroom — every dark tone is within tolerance of every other. One attempt matched
  1,852 px of legitimate armour and flattened it to black. Fix the source and re-pack.

---

## 10. Known generator failure modes

Seedance holds a camera far better than it holds a character. It will:

- drop the far arm entirely — no shoulder, no upper arm;
- keep the arm but delete its weapon, returning an off-hand as a bare fist;
- invent a second weapon, violating a one-weapon lock;
- balloon a blade into a giant crescent or scythe;
- bake drop shadows that survive a 42% key as detached blobs;
- add FX overlays — crossed-blade symbols, arc swooshes — that area filters miss;
- place *another character's* body part in frame. A sprite cell holds one fighter;
  contact FX belongs to the engine (`processWeaponClash`), never to the art.

State counts and sizes explicitly in the subject block, then verify on the packed cell.

---

## 11. Files

```
fal_models.py        model IDs + i2v_clip / still_edit — the only place IDs live
gen_attack_i2v.py    windup seed → i2v; the seed step is what produces a committed swing
gen_run_i2v.py       run cycles (loop=True pins the cycle closed)
salvage_frames.py    recover failed frames (§5)
extend_sheet.py      append cells, key, scale, pack (§6)
pack_*.py            per-batch packers
```

fal downloads use **curl**, not urllib — the proxy here breaks Python's SSL.

Engine integration: `drawSprite()` in `web/index.html`; see `docs/SPRITE-HANDOFF.md`.
