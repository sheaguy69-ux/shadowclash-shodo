# Extracted frames — the trio, cut and keyed

**Review only. Nothing here is packed, and nothing may be packed until the owner answers
the `FIRST_FORM_ONLY` question in `../REVIEW-GRADE-TABLE.md`** — all three of these moves
are second-mode moves that the engine currently gates off at seven call sites.

Cut from the approved RGB review boards in `../candidates/` (hashes verified against
`../PROVENANCE.md` before the cut). The source boards were not modified.

## How

    python3 tools/sprites/cut_strip.py <board> <dir> --n 6 --title 0 --keep-enclosed-white \
        [--drop-pocket X,Y ...]
    python3 tools/sprites/soft_rim.py <dir> <outdir>

Pockets dropped, each one looked at first: mizu `513,422`; tsubasa `1321,387` `1978,386`
`239,444` `1884,401`. Shin needed none.

`--keep-enclosed-white` is new and exists because of these boards: the page-white key
could not tell Mizu's and Tsubasa's pure-neutral white EYES from the page, and keyed both
eyes out of every beat. It now keeps EVERY enclosed pocket and prints the list, and
`--drop-pocket` removes the few a human looked at and confirmed were page. A position
rule was tried first and rejected — see the tool's own comment.

`soft_rim.py` is new: it gives the hard cut the ramped, un-premultiplied rim that
`key_white.py` gives a raw page, without that tool's habit of punching neutral-white art
out as holes.

## What was removed

One 45px grey speck floating beside Mizu's hanbō on INVITE — the only genuine debris on
any of the three boards. Five sealed page pockets (one on Mizu, four on Tsubasa, all at
an arm-to-torso gap) were dropped by name after being inspected.

**Correction to the first review:** its "floating kunai with no hand" on Shin's DRIVE and
"floating stub" on Mizu's PIVOT were NOT real. Both were artifacts of cutting the board at
the midpoint between caption centres, which slices through a neighbour's forward-thrust
weapon. Measured on the whole board with no cuts, shin and tsubasa carry **zero** detached
components and mizu carries exactly one.

## Verified on all 18

Checked by an 18-cell adversarial pass (one inspector per beat, every flag re-checked by
a second agent), then re-measured after the bugs it found were fixed. `soft_rim.py
--selftest` now proves the matte against analytic ground truth — a supersampled shape at
known coverage — and asserts both failure modes: alpha error 0.0006 on dark ink with zero
halo, and bright paint kept intact.

- **art lost: 0 px on every cell** — measured as figure pixels the cut claimed that the
  key then dropped, in place, with no alignment guesswork
- **halo, OUTSIDE the outline: 21 px total across all 18** (was 284-483 per cell)
- **halo, INSIDE the outline: 587 px total, was 18,186** — this is the one that mattered
  and the first fix missed it, because the metric only looked outside the silhouette. The
  hard key keeps a pixel that is 14% covered and 86% page at full opacity; inner-rim p90
  on the stage went from ~190 to ~40
- one connected component each · no canvas-edge ink · captions and neighbour stubs gone ·
  sub-visible alpha purged to the engine's own floor of 8 · eyes intact on all three

**Size registration is NOT verified.** No ruler passed a known-answer check on these
boards — the eye reads a real x1.05 as x1.167 on Shin, and bbox height is contaminated by
hair and weapon tips. The only size evidence that holds is the foot line: mizu 6px, shin
3px, tsubasa 4px of spread on figures 430 / 310 / 350px tall.

## Files

| Fighter | Cell | Beat |
|---|---|---|
| mizu | c1-c6 | VEIL · INVITE · CATCH · PIVOT · RETURN · GUARD |
| shin | c1-c6 | COIL · SIGHT · DRIVE · PIERCE · DRAW · READY |
| tsubasa | c1-c6 | STALK · LOAD · RAKE · BITE · FOLD · READY |

`CONTACT-ON-STAGE-GREY.png` shows all 18 composited on the game's mid-grey.
`SHA256SUMS.txt` covers the 18 frames.
`<fighter>/registration.json` carries each cell's ORIGIN ON THE BOARD and the board foot
line. Every cell is cropped to its own ink, so the shared baseline the six poses were
drawn against does not survive into the files and cannot be re-derived from them — the
packer should read footY from here rather than guess. Board foot spread: mizu 6px,
shin 4px, tsubasa 5px.

## Checks run on the final set

| Check | Result |
|---|---|
| runtime keyer (`keyer_emu`) | **no-op on all 18** — the card path never arms, so what you see is what the engine draws |
| figure gate (`gate_fragments` principle) | no fragments — body height 0.93-1.04 of each row's median, feet 0-6px off the floor |
| alpha floor | 0 pixels with `0 < alpha < 8` on any cell |
| art removed by the key | 6 px across all 18, every one pure page-white (254-255) in the source |
| inner-rim halo | 587 px total, from 18,186 |
| `soft_rim --selftest` | passes: 0.0006 alpha error and zero halo on dark ink, bright paint kept |
| ink-area size spread | mizu 6.0%, shin 4.0%, tsubasa 13.2% — tsubasa's orders exactly by pose (extend 1.042 > neutral 1.000 > tuck 0.961), the signature of a pose confound, not size drift |
