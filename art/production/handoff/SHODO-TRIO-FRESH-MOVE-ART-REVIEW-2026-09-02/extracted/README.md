# Extracted frames — the trio, cut and keyed

**Review only. Nothing here is packed, and nothing may be packed until the owner answers
the `FIRST_FORM_ONLY` question in `../REVIEW-GRADE-TABLE.md`** — all three of these moves
are second-mode moves that the engine currently gates off at seven call sites.

Cut from the approved RGB review boards in `../candidates/` (hashes verified against
`../PROVENANCE.md` before the cut). The source boards were not modified.

## How

    python3 tools/sprites/cut_strip.py <board> <dir> --n 6 --title 0 --keep-enclosed-white
    python3 tools/sprites/soft_rim.py <dir> <outdir>

`--keep-enclosed-white` is new and exists because of these boards: the page-white key
could not tell Mizu's and Tsubasa's pure-neutral white EYES from the page, and keyed both
eyes out of every beat. It keeps enclosed white in the figure's top 45 percent — the eyes,
Shin's pale shoulder plate — and still drops it lower down, where Tsubasa has a real page
gap at his hip.

`soft_rim.py` is new: it gives the hard cut the ramped, un-premultiplied rim that
`key_white.py` gives a raw page, without that tool's habit of punching neutral-white art
out as holes.

## What was removed

One 45px grey speck floating beside Mizu's hanbō on INVITE — the only genuine debris on
any of the three boards. Two 1-3px islands the ramp itself minted on Shin were purged.

**Correction to the first review:** its "floating kunai with no hand" on Shin's DRIVE and
"floating stub" on Mizu's PIVOT were NOT real. Both were artifacts of cutting the board at
the midpoint between caption centres, which slices through a neighbour's forward-thrust
weapon. Measured on the whole board with no cuts, shin and tsubasa carry **zero** detached
components and mizu carries exactly one.

## Verified on all 18

One connected component each · eyes intact (mizu 389-701px, shin 407-414px, tsubasa
634-708px) · no canvas-edge ink · no halo on the stage grey · captions and neighbour stubs
gone · sub-visible alpha purged to the engine's own floor of 8.

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
