# KAEL — GEDAN-GAMAE (lower stance), Aug 21 2026

Owner: *"can you edit his short blade at the tip to make it short, GPT messed up at that point."*

| | as delivered | after the edit |
|---|---:|---:|
| short blade, tip → tsuba | 298px | **251px** |
| vs the long sword's 416px | 0.72× | **0.60×** |
| tip | blunt squared stump | pointed kissaki |

Edited in place by `tools/shorten_blade.py` — no generator, no paid call. Verified on the
OUTPUT, not on intent: the tip moved from d=−4 to d=+42 along the blade axis, and **0 pixels
changed outside the sword's own region.**

## Why it stops at 0.60× and not the ~0.45× the canon pair sits at

Past the old tip there is only **~44px of open paper** before the blade lies across his
shoulder and sleeve. Erasing further does not remove a blade, it removes his arm — the
silhouette and its outline run directly alongside, and every attempt to fill behind it either
smeared (cross-fading between white on one side and robe on the other) or bit a notch out of
the shoulder. **Taking this blade to 0.45× is a repaint of his sleeve, which is a redraw, not
an edit.**

## What the tool does, and three things it does NOT

The point is made by drawing converging edges with the blade's own band structure — outline
weight held constant, mune facet, shinogi line, ha facet — all sampled from a clean slice of
this very blade at 120px from the old tip. Asymmetric on purpose: the ha runs on nearly
straight while the mune curves in, which is what reads as a katana point rather than a
spearhead.

Rejected, each after trying it:

1. **Harvest the long sword's kissaki and rotate it here.** That tip is curved; an affine map
   does not carry the curve, and compositing it over the robe left dark banding.
2. **Fill the erased band by interpolating across it.** Where the blade has white on one side
   and his shoulder on the other, a cross-fade is a visible smear. Filling each pixel from the
   side it is *nearer* is exact wherever the two sides agree.
3. **Squeeze the whole cross-section into the taper.** The outline bands squeeze with it and
   stripe.

Two sizing traps are also recorded in the tool: a fixed ±26px erase band is **wider than the
blade** and ate the sleeve outline running beside it, and the reference slice at 25px from the
old tip has a **gold cuff crossing it**, which poisoned the first tips with a gold streak.

## Noted while measuring, not changed

The tsuka is **126px against the now-251px blade — 0.50**. A katana sits near 0.30; a
one-handed short sword runs longer, so this is on the long side rather than wrong. Flagging it
because it is the next thing that will read as "off" once the blade is right.
