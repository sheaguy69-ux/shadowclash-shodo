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
a second agent), then re-measured after the two bugs it found were fixed:

- **art lost: 0 px on every cell** — measured as figure pixels the cut claimed that the
  key then dropped, in place, with no alignment guesswork
- **halo: 5 pixels total across all 18** (was 284-483 per cell), measured as the ring just
  outside the silhouette composited on the stage grey; p99 now sits exactly on the stage
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
