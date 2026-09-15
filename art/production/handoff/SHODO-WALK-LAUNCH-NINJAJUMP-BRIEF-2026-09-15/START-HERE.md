# START HERE — how to run this with GPT

Three new animation rows, eight fighters. **24 boards** if the whole roster ships — plus one
replacement row: **Kael's run cycle** (`prompts/kael.md`, Row D), added Sep 15.

## The loop, per board

1. **Open `prompts/<fighter>.md`.** One self-contained file per character, carrying all three
   rows: **Row A `walk1..8`**, **Row B `airhurt1..8`** (the launched hurt), **Row C `njump1..8`**
   (the second jump — the curl into a ball). Kael also has **Row D `run_clean1..8`**, a
   replacement for a run cycle that is measurably four poses drawn twice.
2. **Paste the `Prompt` block for the row you want** into the generator. It is written to be
   used verbatim. Attach `refs/<fighter>-refs.png` so it can match the body, and
   `refs/ROSTER-true-scale.png` so it gets the size right.
3. **Check it against the `Pitfalls` list** in the same file before accepting. Wrong weapon
   count is the failure that costs a whole board.
4. **Deliver it as eight files** — `frame-01.png … frame-08.png` in one folder. Generate as a
   row (one pass holds one body size), then slice. See `BOARD-SPEC.md`.
5. **Send me the folder path.** I key it, pack it, make the engine change the row needs, and
   drive it live before it counts as done.

## Read once, before the first board

- **`PROMPTS.md` §0** — the canon table. Weapon count, hood or no hood, palette, per fighter.
  This is the law and it is short.
- **`BOARD-SPEC.md`** — the eight hard rules. The one that bites most: **no ground shadow, no
  floor bar, no cast shadow, ever.** The packer welds the board's lowest ink to the floor
  line, so a painted shadow *becomes* the feet and the fighter hovers above it.
- **`PROMPTS.md` §5** — for Row C, block the rotation in Blender first, then style it. A
  rotation is where stills drift, and the packer applies one scale to the whole board, so
  drift ships as a fighter who changes size mid-tumble.

## Where I'd start

**Tsubasa, Row B.** One board. It proves the whole pipeline end to end, and it fixes the
ugliest thing in the game: right now every fighter's air-hit art **is their throw-grab pose**,
and Tsubasa has two distinct drawings covering his entire airborne arc while launchers pop him
92–192px. See `refs/PROOF-airhurt-is-the-grab-pose.png`.

Then the rest of Row B, then Row C (Mokurai and the Executioner first — they have the fewest
distinct flight poses today), then Row A.

## What I have already done so the art lands clean

- **`WALK_TIME` is ruled and shipped** — each fighter now walks exactly one full cycle before
  breaking into a run, derived per fighter. All eight beats play, in order, every push, so the
  walk boards must be true loops with every beat equally strong.
- **Row B needs one engine line**, Row C needs two lines and a small block. Both written up in
  `ENGINE-CONTRACT.md`. Neither is your problem.
- **Every number in the brief is measured**, not estimated — `MEASUREMENTS.md` says how, with
  the command that produced it.
