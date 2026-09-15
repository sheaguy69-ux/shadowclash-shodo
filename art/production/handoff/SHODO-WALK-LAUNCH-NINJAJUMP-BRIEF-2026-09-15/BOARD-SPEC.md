# Board spec — what a finished board has to be

This is the delivery contract. A board that satisfies it packs in one command with no
rework. A board that misses any of it costs a round trip.

---

## File shape

```
<row-name>/
  frame-01.png
  frame-02.png
  ...
  frame-08.png
```

- **Exactly 8 files**, named `frame-01` … `frame-08`, zero-padded. The packer globs
  `frame-*.png` and sorts by name; `frame-1.png` next to `frame-10.png` sorts wrong.
- **Either** RGBA with a transparent background (binary alpha is fine and preferred),
  **or** RGB on a clean white page. Both are handled — the white-page route runs through
  `key_review_card.py` first. Do not deliver a checkerboard screenshot: that is a picture
  *of* transparency, not transparency, and it has bitten this project before.
- Square-ish and generous — 416×416 or 512×512 per frame is what the existing boards use.
  Resolution above the final cell size is free quality; below it is unrecoverable.
- **One row per prompt.** Eight beats generated together in one pass hold one body size.
  Eight beats generated in two passes do not, and the packer applies **one scale to the
  whole board** — so a size drift between beats 4 and 5 lands in the game as a fighter who
  changes size mid-animation.

---

## The eight hard rules

Every one of these is a rule the sheets already enforce. Breaking one either fails the pack
or ships a visible defect.

### 1. No ground shadow. No floor bar. No cast shadow. Ever.

Every drawn ground shadow was deleted from this game at `SHEET_V 798`, and again off Ember's
idle at `837`. The packer welds the board's **lowest ink** to the floor line, so a painted
floor stroke *becomes* the feet and the fighter hovers above his own shadow.

If a board comes back with one, `tools/sprites/erase_ground_bar.py` can lift a thin
horizontal brush stroke out of the floor band — it separates by **shape**, not colour,
because the bar is as dark as the boots. It cannot rescue a soft airbrushed pool.

### 2. Full body, both feet visible, inside the frame

Three separate Tsubasa rows arrived cropped this year because the generator framed them as
close-ups and ran off its own canvas. The recoveries cost days. **Nothing may touch the
canvas edge** — not a foot, not a blade tip, not a scarf.

### 3. One character scale across all eight frames, identical camera

Say it in the prompt, explicitly. The packer measures ink area on **one** anchor beat
(beat 1 unless told otherwise) and applies that scale to the whole row. Per-cell size
matching is forbidden — it makes a curled beat the same height as an extended one and the
row boils.

### 4. Feet land on the floor line — except where the drawing genuinely goes below it

Packed cells measure 3–5px of ink above `footY`. If a beat's **body** reaches below the
standing foot line (a trailing leg on a launch, a dropped knee), that is legal and the cell
grows downward to hold it — `grow_frame.py --down`, which is how Tsubasa's frame went 320→332.
What is *not* legal is cropping the limb to make it fit.

### 5. Keep enclosed white — it is the eyes

The keyer preserves enclosed not-page regions and restores them at full alpha. A hard cut
off white punches a hole through the face — the documented `708` defect, 24 cells repaired.
Near-white eyes, blade highlights and the white core of a slash crescent all survive.
Large pale slabs trapped **between the boots** at 0.88+ of figure height are paper and are
dropped. Do not hand-key the board yourself; deliver it clean and let the tool do it.

### 6. No straight cutoffs

If an effect has to leave the frame, delete the effect entirely. Never fade it, never slice
it flat at the edge, and never touch the body to make room.

### 7. Canon is law, and the sheet wins over any document

Wrong weapon count is the single most common failure. Before generating, re-read the fighter's
line in `PROMPTS.md` §0 and look at `refs/<fighter>-refs.png`. Specifically:

- **Ember** — claws only. Never a sword. **Four** blades per hand; a doc saying three is stale.
- **Tsubasa** — exactly **two** small tantō, reverse grip, and **no hood** (spiky hair).
- **Kael** — one **long** and one **short** blade, and the difference must be obvious.
- **Mokurai** — **bare hands with prayer beads**. Never a staff.
- **Shin** — no blades at all, and **one eye** is canon. Never "fix" it.
- **Exile** — **unhooded**, one eye behind a cloth wrap, red iris, **spiked** ball.
- **Purple** belongs to the Executioner and Mizu **only**. It is forbidden on the other six.

### 8. Sumi-e, side-on, fighting-game read

Ink-brush *shodō* styling on an ash-grey palette — full-black sumi and full-bone light, the
in-between realm the game is named for. Side-on 2D fighting-game view, the same camera as
every existing row. A beat that cannot be read as a silhouette will not read at 120px tall.

---

## How it gets packed

```bash
# only if it came back on a white page
python3 tools/sprites/key_review_card.py   <board>      /tmp/keyed
# only if a floor bar was drawn anyway
python3 tools/sprites/erase_ground_bar.py  <board>      /tmp/scrub

# always: dry run first, read the deviation column, then commit
python3 tools/sprites/pack_keyed_board.py  <fighter> /tmp/keyed <prefix> --dry
python3 tools/sprites/pack_keyed_board.py  <fighter> /tmp/keyed <prefix>
```

Useful flags:

| flag | when |
|---|---|
| `--anchor N` | beat 1 is not a stance. Anchor the scale on a beat that **is** — never on the biggest beat, a slash arc adds ink far from the body |
| `--canon-area N` | hold a size the owner already approved, so a re-pack does not move it |
| `--floor-beat N` | the board draws FX or a limb below the feet. Welds the floor to **one named beat's** ink bottom instead of the union of all eight |
| `--wire k=n` | point an existing key at a new beat instead of creating `prefix1..8` |
| `--dry` | always, first |

The dry run prints per-beat ink area, deviation from canon, bbox and `footY-bottom`. A healthy
row reads **±2% deviation** and `footY-bottom` of 3–5 on every grounded beat. Anything else,
stop and read it.

**Append-only.** Cells go on the end of the sheet, keys are repointed, nothing already packed
moves — the commit hook proves it (`art guard: <fighter> N/N existing cells byte-identical,
8 appended`). Old cells become orphans and are **not deleted**; stripping them is a separate,
deliberate second step that needs the owner's word.
