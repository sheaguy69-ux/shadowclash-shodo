#!/usr/bin/env python3
"""Give a hard-keyed cell the ramped rim that key_white.py gives a raw white page.

    python3 tools/sprites/soft_rim.py <cut_strip_outdir> <outdir>

WHY THIS EXISTS — neither existing tool can do this pair of boards alone:

  cut_strip.py  gets the SILHOUETTE right (pitch cuts, caption drop, neighbour-stub
                drop) but hands back a BINARY alpha. A hard cut off a white sheet keeps
                the 90%-page edge pixels at full opacity, and on the game's dark stage
                that reads as a lit outline traced round the character — the halo
                key_white.py's own docstring warns about.

  key_white.py  gets the RIM right (ramp + un-premultiply) but decides foreground by
                distance from white, so PURE-NEUTRAL WHITE ART IS BACKGROUND TO IT.
                The Sep-2 shodo trio draws Mizu's and Tsubasa's eyes at ~250 neutral,
                so key_white punches both eyes out as holes in every beat.

So take the silhouette from one and the rim from the other: cut_strip's mask is the
AUTHORITY on what is figure (it already survived the enclosed-white question), and the
ramp is applied only where that mask meets the page. Interior stays fully opaque, which
is what keeps a white eye a white eye.

The blend is undone the same way key_white does it — c = (p - (1-a)*page) / a — so a
half-covered pixel gets the ink's own colour at half alpha rather than a washed-out
colour at full alpha.
"""
import argparse
import pathlib
import tempfile

import numpy as np
from PIL import Image
from scipy import ndimage as nd

TOL = 34       # colour distance from page white that counts as ink at all
KNEE = 150     # ...and where the ramp reaches full opacity
MIN_BLOB = 400  # a detached piece smaller than this is a speck, not a limb or FX
BRIGHT_ART = 180  # nearest-sure-ink luminance above which the art itself is bright,
                  # so a pale pixel there is paint and not page bleed
PAGE = np.array([255.0, 255.0, 255.0])


def matte(rgb, mask, min_blob=MIN_BLOB, bright_art=BRIGHT_ART):
    """Return (alpha 0..1, un-premultiplied rgb) on the SAME canvas as the input.

    Split out of soften() so the selftest can measure it against analytic ground truth
    without re-placing a cropped result — that alignment guesswork silently reported a
    working matte as broken (0.4578 error against a true 0.0011).
    """

    # ⛔ DROP SPECKS BY SIZE, KEEP DETACHED FX. Same rule key_white.py uses: the largest
    # component always survives, and so does anything big enough to be a limb, a blade or
    # a dust plume. Below that floor it is generator noise — on this trio exactly one
    # piece qualified, a 45px grey speck floating beside Mizu's hanbo on INVITE.
    lab, n = nd.label(mask, np.ones((3, 3)))
    if n > 1:
        sizes = nd.sum(mask, lab, range(1, n + 1))
        biggest = int(sizes.argmax())
        keep = np.zeros_like(mask)
        for i, sz in enumerate(sizes):
            if sz >= min_blob or i == biggest:
                keep |= lab == i + 1
        mask = keep

    # ⛔ SOLVE THE BLEND, DO NOT GUESS IT WITH A RAMP. key_white.py's TOL/KNEE ramp is
    # calibrated for its own job and is far too steep for an edge: a pixel 84 luminance
    # below the page is 33% covered by black ink, but the ramp scores its colour distance
    # at 145 and calls it 96% opaque. Composited on the stage that pixel lands at 164
    # where it belongs at 66 — a pale rim traced round the whole figure, which is exactly
    # the halo this file exists to prevent. Verified by an 18-cell adversarial pass:
    # 11 of 18 beats carried it, measured p99 ~110-132 against a 98 stage.
    #
    # The blend has a closed form. An edge pixel is p = a*C + (1-a)*PAGE for some ink
    # colour C, so a is the projection of (PAGE - p) onto (PAGE - C). Take C from the
    # nearest pixel the silhouette is sure about; that is the ink actually bleeding into
    # this pixel.
    core = nd.binary_erosion(mask, np.ones((3, 3)), iterations=1)
    if not core.any():
        core = mask
    _, (iy, ix) = nd.distance_transform_edt(~core, return_indices=True)
    C = rgb[iy, ix]                       # nearest sure-ink colour, per pixel

    dPC = PAGE - C                        # page -> ink
    dPp = PAGE - rgb                      # page -> this pixel
    denom = (dPC ** 2).sum(2)
    a_true = np.where(denom > 1e-6, (dPp * dPC).sum(2) / np.maximum(denom, 1e-6), 0.0)
    a_true = np.clip(a_true, 0, 1)

    # ⛔ WHERE THE SOLVE IS ALLOWED TO REDUCE ALPHA. a_true reads any near-page pixel as
    # ~0, and on its own it cannot tell a 5%-covered blend from a pixel of BRIGHT ART
    # sitting on the outline — a blade tip, a specular streak, a lit hood edge. Applied
    # to the whole silhouette rim it punched ~200 pinholes per cell, 92% of them landing
    # on source pixels brighter than 200.
    #
    # But retreating to "the mask is simply opaque" reinstates the very halo this file
    # exists to prevent, INSIDE the mask: the border flood keeps a pixel that is 14%
    # covered and 86% page at full opacity, and that composites 135 luminance too bright.
    # An analytic ground-truth test (a supersampled disc plus a thin spike, rendered at
    # known coverage, run through this exact pipeline) measures it: keeping the mask
    # opaque gives mean alpha error 0.3008 and 412 halo pixels; solving gives 0.0011 and
    # zero. Both failures are real and they pull in opposite directions.
    #
    # What separates them is the LOCAL ART, not the pixel. Take C, the nearest colour the
    # silhouette is sure about. If C is dark, a bright pixel there can only be page
    # bleeding in, so solve it. If C is bright, the art itself is bright there and the
    # solve has nothing to say — leave it opaque. On the same ground truth this scores
    # identically to solving everywhere on dark ink (0.0011, zero halo) and identically to
    # keeping opaque on bright art, which is exactly the intent.
    Clum = C.mean(2)
    outer = nd.binary_dilation(mask, np.ones((3, 3)), iterations=2) & ~mask
    solvable = mask & ~core & (Clum < bright_art)
    al = np.zeros(mask.shape, float)
    al[mask] = 1.0                       # the silhouette's claim stands by default
    al[solvable] = a_true[solvable]      # ...except where only page can be lightening it
    al[outer] = np.clip(a_true[outer], 0, 1)   # blend pixels the hard key threw away
    al[core] = 1.0                       # interior is opaque whatever colour it is

    # ⛔ PURGE SUB-VISIBLE ALPHA LAST. The engine's own keyer treats alpha >= 8 as ink
    # (keyer_emu.keyed_cell), so anything under that is invisible in game but still
    # counts as a component to every QC scan downstream — it shows up as a phantom
    # "detached piece" nobody can see or fix. Measured on Mizu INVITE: one 1px pixel at
    # alpha 6 survived the ramp and read as a second component.
    al[al < 8 / 255] = 0.0

    # ...and re-run the speck filter on the FINISHED alpha, not just the input mask. The
    # ramp mints its own specks: it lifts a faint near-white pixel the hard key had
    # dropped up to alpha 9-15, which clears the threshold above and lands as a 1-3px
    # island (measured on Shin PIERCE and READY). Same size rule, applied where it can
    # see everything.
    vis = al > 0
    lab, n = nd.label(vis, np.ones((3, 3)))
    if n > 1:
        sizes = nd.sum(vis, lab, range(1, n + 1))
        biggest = int(sizes.argmax())
        for i, sz in enumerate(sizes):
            if sz < min_blob and i != biggest:
                al[lab == i + 1] = 0.0

    out = np.clip((rgb - (1 - al)[..., None] * PAGE) / np.maximum(al, 1e-3)[..., None], 0, 255)
    return al, out


def soften(path, tol=TOL, knee=KNEE, min_blob=MIN_BLOB, pad=4, bright_art=BRIGHT_ART):
    a = np.array(Image.open(path).convert('RGBA')).astype(float)
    al, out = matte(a[:, :, :3], a[:, :, 3] > 0, min_blob=min_blob, bright_art=bright_art)
    im = Image.fromarray(np.dstack([out, al * 255]).astype('uint8'), 'RGBA')
    im = im.crop(im.getbbox())
    # A tight crop puts ink on all four borders, which every downstream scan reads as a
    # straight cut-off. Pad it back out so the cell carries its own clear margin.
    if pad:
        padded = Image.new('RGBA', (im.width + 2 * pad, im.height + 2 * pad), (0, 0, 0, 0))
        padded.paste(im, (pad, pad))
        im = padded
    return im


def selftest():
    """Analytic ground truth: a shape whose true coverage we KNOW, through this matte.

    This is the check that catches the two failures this file has already shipped once
    each — a halo (alpha too high on page-contaminated edge pixels) and punched art
    (alpha too low on bright paint). Both are invisible on a contact sheet.
    """
    H, W, S = 200, 160, 8
    Y, X = np.mgrid[0:H * S, 0:W * S] / S
    shape = (((Y - 110) ** 2 + (X - 80) ** 2) < 55 ** 2) | (
        (np.abs(X - 80) < (0.6 + (Y - 30) * 0.05)) & (Y > 30) & (Y < 60))
    true = shape.astype(float).reshape(H, S, W, S).mean((1, 3))
    STAGE = 98.0
    aa = (true > 0.001) & (true < 0.999)
    # A bright-paint case has to carry its own dark outline, the way an eye or a blade
    # does. A pure-white shape sitting on a white page with no outline is not something
    # any keyer can find — the border flood simply swallows it — so testing that would
    # measure the synthetic, not the tool.
    ring = (nd.binary_dilation(true > 0.5, np.ones((3, 3)), iterations=3)
            & ~nd.binary_erosion(true > 0.5, np.ones((3, 3)), iterations=1))
    for ink, name in [([28, 34, 40], 'dark ink'), ([250, 250, 250], 'bright art')]:
        INK = np.array(ink, float)
        rgb = np.round(true[..., None] * INK + (1 - true[..., None]) * PAGE)
        if name == 'bright art':
            rgb[ring] = np.array([20.0, 20.0, 20.0])   # the outline that makes it findable
        white = rgb.min(2) >= 224                      # cut_strip's border flood
        lab, _ = nd.label(white)
        e = set(lab[0, :]) | set(lab[-1, :]) | set(lab[:, 0]) | set(lab[:, -1])
        e.discard(0)
        mask = ~np.isin(lab, list(e))
        al, col = matte(rgb, mask)
        comp = (al[..., None] * col + (1 - al[..., None]) * STAGE).mean(2)
        truth = (true[..., None] * INK + (1 - true[..., None]) * STAGE).mean(2)
        halo = int(((comp - truth) > 25).sum())
        err = float(np.abs(al - true)[aa].mean())
        print(f'  {name:11s} alpha err on the AA band {err:.4f} | halo px {halo}')
        if name == 'dark ink':
            assert err < 0.05, f'matte broken on dark ink: alpha error {err:.4f}'
            assert halo == 0, f'halo is back on dark ink: {halo} px'
        else:
            # Bright paint on a white page is genuinely ambiguous. The one thing that
            # must hold is that we never delete it.
            inner = (true > 0.5) & ~ring
            kept = float((al[inner] > 0.5).mean())
            assert kept > 0.99, f'bright art is being punched out: only {kept:.1%} kept'
    print('  soft_rim selftest OK')


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('src', nargs='?')
    ap.add_argument('dst', nargs='?')
    ap.add_argument('--selftest', action='store_true',
                    help='run the analytic ground-truth check and exit')
    ap.add_argument('--min-blob', type=int, default=MIN_BLOB)
    ap.add_argument('--pad', type=int, default=4, help='transparent margin around the cut')
    ap.add_argument('--bright-art', type=float, default=BRIGHT_ART,
                    help='local-ink luminance above which the art is bright and the matte '
                         'solve must not reduce alpha (default 180)')
    a = ap.parse_args()
    if a.selftest:
        selftest()
        return
    src, dst = pathlib.Path(a.src), pathlib.Path(a.dst)
    dst.mkdir(parents=True, exist_ok=True)
    for p in sorted(src.glob('*.png')):
        before = np.array(Image.open(p).convert('RGBA'))[:, :, 3] > 0
        im = soften(p, min_blob=a.min_blob, pad=a.pad, bright_art=a.bright_art)
        after = np.array(im)[:, :, 3] > 0
        print(f'  {p.name}: {im.width}x{im.height}  '
              f'solid {int(before.sum())} -> covered {int(after.sum())} '
              f'(+{int(after.sum()) - int(before.sum())} rim px)')
        im.save(dst / p.name)


if __name__ == '__main__':
    main()
