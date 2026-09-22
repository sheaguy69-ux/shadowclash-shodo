"""Pack the Aug 1 sheets — 8 moves, the last empty inputs on four originals.

  python3 tools/sprites/pack_moves_334.py --dry     # previews only, sheets untouched
  python3 tools/sprites/pack_moves_334.py

Append-only: the existing png is composited into a wider one and every original cell
stays byte-identical, so nothing already shipped can move.

⛔ ONE FIXED SCALE PER FIGHTER, PICKED ON THE HEAD — never MATCH_HEIGHT per cell.
332 settled this and these rows would have broken it again: erip is a prone floor
tear and ehook is a full airborne stretch, so per-cell height flattening would scale
the crouch ~2x against the reach and boil the character. The numbers below come from
rendering each sheet against that fighter's own idle at 0.80/0.90/1.00/1.10 of a
height-matched guess and reading the HEAD, which is the anchor the eye checks.

The automatic eye-span metric was tried first and is NOT what set these. It answered
2.27 for the executioner (a scarf fold read as an eye) and 0.0 for Ember (his eye is
~200px on a 2K still-editor return and the size window rejected it). That is the same
contamination the Kael packer records for four other metrics — the ladder is the
method that survives.

Sources are already keyed RGBA:
  * mizu / executioner come from cut_sheet_bleed.py, which recovers the weapons that
    cross the cell rules on these sheets.
  * ember / kael come through key_white.py, because their frames were repaired by the
    still editor and come back 2K on a white page.
"""
import json
import pathlib
import sys

import numpy as np
from PIL import Image

REPO = pathlib.Path(__file__).resolve().parents[2]
CUT = REPO / 'media/handoff/all-moves-2026-08-01/cut'
PREV = pathlib.Path('/private/tmp/claude-501/-Users-anthonyguy-SHADOWCLASH-RECOVERED/'
                    'bdb3d676-eaee-44e7-8aa3-b905c4a26f9e/scratchpad/packprev')

# fighter -> (scale, [(source dir, file prefix, sheet key prefix, raw dir or None), ...])
#
# ⛔ THE SCALE IS ONE NUMBER PER FIGHTER, AND IT IS APPLIED IN THE *SHEET'S* LINEAGE.
# Ember's and Kael's repaired rows went through the still editor, which hands back a
# 2K frame REFRAMED around the character — so those frames are ~11x the size of the
# rows that came straight off the cutter, and a single multiplier applied to both
# packed Kael's ktrav row at 15px tall. Each edited frame is therefore first
# normalised back to the size its own un-edited original had (`raw`), and only then
# does the fighter's one scale apply. Normalisation measures the BODY, not the ink
# box: the edit deliberately changed the blades and claws, so those are the one thing
# that cannot be used to compare before with after.
JOBS = {
    'executioner': (1.12,  [('executioner', 'xsheath', 'xsheath', None),
                            ('executioner', 'xsky', 'xsky', None)]),
    'mizu':        (0.58,  [('mizu', 'mback', 'mback', None)]),
    'ember':       (1.35,  [('ember-keyed', 'eshred', 'echarge', 'ember'),
                            ('ember-keyed', 'erip', 'erip', 'ember'),
                            ('ember-keyed', 'ehook', 'ehook', 'ember')]),
    'kael':        (0.95,  [('kael-keyed', 'kfang', 'kfang', 'kael'),
                            ('kael', 'ktrav', 'ktrav', None)]),
}


def body_h(im):
    """Height of the character WITHOUT its steel — silver is bright and unsaturated,
    and it is the only part of these frames the repair pass was allowed to change."""
    a = np.array(im.convert('RGBA'))
    op = a[..., 3] > 128
    rgb = a[..., :3].astype(int)
    mx, mn = rgb.max(2), rgb.min(2)
    sat = np.where(mx > 0, (mx - mn) / np.maximum(mx, 1), 0)
    body = op & ~((mx > 110) & (sat < 0.30))
    ys = np.nonzero(body.any(1))[0]
    return int(np.ptp(ys) + 1) if ys.size else 0


def cells(fighter, scale, rows, meta):
    fw, fh, footY = meta['frameW'], meta['frameH'], meta['footY']
    out = []
    for src, pre, key, raw in rows:
        got = []
        for i in range(6):
            im = Image.open(CUT / src / f'{pre}_{i + 1}.png').convert('RGBA')
            s = scale
            if raw:
                ref = Image.open(CUT / raw / f'{pre}_{i + 1}.png')
                s *= body_h(ref) / max(body_h(im), 1)
            im = im.resize((max(1, round(im.width * s)), max(1, round(im.height * s))),
                           Image.LANCZOS)
            a = np.array(im)[..., 3]
            ys, xs = np.nonzero(a > 16)
            assert ys.size, f'{key}{i+1} keyed to nothing'
            assert ys.max() - ys.min() + 1 <= fh, \
                f'{key}{i+1} is {ys.max()-ys.min()+1}px tall, frame is {fh} — grow frameH, never shrink the pose'
            cell = Image.new('RGBA', (fw, fh), (0, 0, 0, 0))
            cell.alpha_composite(im, (fw // 2 - (xs.min() + xs.max()) // 2, footY - ys.max()))
            got.append(cell)
        out.append((key, got))
        print(f'  {fighter}/{key}: ' + ' '.join(
            str(np.ptp(np.nonzero(np.array(c)[..., 3] > 16)[0]) + 1) for c in got))
    return out


def main():
    dry = '--dry' in sys.argv
    PREV.mkdir(parents=True, exist_ok=True)
    for fighter, (scale, rows) in JOBS.items():
        jf = REPO / f'web/assets/sprites/{fighter}.json'
        pf = REPO / f'web/assets/sprites/{fighter}.png'
        meta = json.loads(jf.read_text())
        packed = cells(fighter, scale, rows, meta)

        for key, got in packed:
            strip = Image.new('RGBA', (meta['frameW'] * 6, meta['frameH']), (38, 40, 54, 255))
            for i, c in enumerate(got):
                strip.alpha_composite(c, (i * meta['frameW'], 0))
            strip.convert('RGB').save(PREV / f'{fighter}_{key}.png')
        if dry:
            continue

        sheet = Image.open(pf).convert('RGBA')
        fw, fh, cols = meta['frameW'], meta['frameH'], meta['cols']
        assert sheet.width == cols * fw, f'{fighter}: sheet is {sheet.width}px, json says {cols * fw}'
        add = [c for _, got in packed for c in got]
        new = Image.new('RGBA', ((cols + len(add)) * fw, fh), (0, 0, 0, 0))
        new.paste(sheet, (0, 0))
        n = cols
        for key, got in packed:
            for i, c in enumerate(got):
                new.alpha_composite(c, (n * fw, 0))
                meta['frames'][f'{key}{i + 1}'] = n
                n += 1
        new.save(pf)
        meta['cols'] = n
        jf.write_text(json.dumps(meta, indent=2) + '\n')
        print(f'  {fighter}: packed {len(add)} cells at {cols}-{n - 1}; cols -> {n}')
    print(f'  previews -> {PREV}')


if __name__ == '__main__':
    main()
