"""Cut a move off one of Kael's two owner-supplied spreadsheets and pack it.

  python3 tools/sprites/pack_kael_spreadsheet.py dark 1 krise
  python3 tools/sprites/pack_kael_spreadsheet.py light 0 kohigh --dry

Both sheets are a 6x6 table of 6-frame moves. They key CLEANLY, which is not
obvious for a black-robed character on a near-black field: the background is a
flat [16,17,22] and his outline black runs 0-15, so the outline is DARKER than
the field and a colour-distance cut separates them. The light sheet is white,
which is trivially safe.

⛔ GRID GEOMETRY IS MEASURED, NOT GUESSED. The column and row rules are found by
scanning for lines that run the full height/width of the table, because eyeballed
offsets put the MOVE-NAME column in frame 1's slot on the first attempt and
silently dropped frame 6.

⛔ THE SCALE IS PICKED BY EYE, ON PURPOSE. Four automatic metrics were run on
this character and answered the same question with 1.61 / 1.38 / 1.12 / 0.97:
bbox ink (a raised blade inflates it), eye-pair AREA (his gold trim reads as
eye), eyes-above-feet (that is POSE, not size — it is what made me wrongly
report his whole sheet as 60% inconsistent), and hood width at eye level (his
crossed blades sit exactly there, and the new art draws a rounder hood). Every
one is contaminated by something different. So the sheet art was rendered at a
range of scales against his idle and the owner picked: 1.45 for the dark sheet.
The light sheet was then checked the same way, heads cropped to a common zoom
against the approved kspin/krise cells: 1.50 is plainly bigger, 1.35 still a
touch big, 1.25 matches. It is drawn LARGER on the page than the dark sheet, so
it needs a SMALLER factor — the opposite of the guess that used to sit here.
"""
import json, pathlib, sys
import numpy as np
from PIL import Image
from scipy import ndimage

REPO = pathlib.Path('/Users/anthonyguy/SHADOWCLASH-RECOVERED')
OUT = pathlib.Path('/private/tmp/claude-501/-Users-anthonyguy-SHADOWCLASH-RECOVERED/'
                   '092847ce-5b36-4748-bf48-cc27f4a37237/scratchpad')

SHEETS = {
    'dark':  dict(path='/Users/anthonyguy/Downloads/kael 2.png',
                  bg=(16, 17, 22), tol=14, scale=1.45,
                  cols=[(391, 533), (535, 675), (677, 831), (833, 982), (984, 1129), (1131, 1274)],
                  rows=[(96, 259), (261, 424), (426, 589), (592, 755), (757, 920), (922, 1076)]),
    # knee: see cut(). Only the WHITE sheet needs it — a dark halo on the dark
    # sheet is invisible, a white one on the light sheet is a lit outline.
    'light': dict(path='/Users/anthonyguy/Downloads/kael .png',
                  bg=(255, 255, 255), tol=30, knee=150, scale=1.25,
                  cols=[(395, 532), (533, 676), (678, 828), (830, 969), (971, 1114), (1116, 1257)],
                  rows=[(48, 225), (227, 403), (405, 581), (583, 744), (746, 908), (910, 1072)]),
}


def cut(sheet, row):
    s = SHEETS[sheet]
    a = np.array(Image.open(s['path']).convert('RGB')).astype(int)
    bg = np.array(s['bg'])
    y0, y1 = s['rows'][row]
    frames = []
    for x0, x1 in s['cols']:
        sub = a[y0 + 3:y1 - 2, x0 + 3:x1 - 2]
        dist = np.sqrt(((sub - bg) ** 2).sum(2))
        fg = dist > s['tol']
        lab, n = ndimage.label(fg)
        if n:
            sizes = ndimage.sum(fg, lab, range(1, n + 1))
            # keep the body AND every part big enough to be a limb, arc or blade;
            # drop the specks the grid lines leave behind
            keep = np.zeros_like(fg)
            for i, sz in enumerate(sizes):
                if sz > 120 or i == sizes.argmax():
                    keep |= (lab == i + 1)
            fg = keep
        ys, xs = np.nonzero(fg)
        if s.get('knee'):
            # ⛔ A HARD CUT OFF A WHITE SHEET LEAVES A WHITE HALO. Every edge pixel
            # is a blend of ink and page; a binary key keeps the 90%-page ones at
            # full opacity, and on the game's dark stage that reads as a lit
            # outline traced round him. Raising the threshold instead is worse —
            # it eats the pale-yellow swoosh, which is ALSO near-white.
            # So: ramp the alpha over the blend range, then undo the blend
            # (c = (p - (1-a)*page) / a) so a half-covered pixel carries the
            # ink's own colour at half alpha instead of a washed-out one at full.
            al = np.clip((dist - s['tol']) / (s['knee'] - s['tol']), 0, 1) * fg
            rgb = np.clip((sub - (1 - al)[..., None] * bg) / np.maximum(al, 1e-3)[..., None], 0, 255)
            rgba = np.dstack([rgb, al * 255]).astype('uint8')
        else:
            rgba = np.dstack([sub, np.where(fg, 255, 0)]).astype('uint8')
        frames.append(Image.fromarray(rgba, 'RGBA').crop((xs.min(), ys.min(), xs.max() + 1, ys.max() + 1)))
    return frames


def main():
    sheet, row, prefix = sys.argv[1], int(sys.argv[2]), sys.argv[3]
    dry = '--dry' in sys.argv
    frames = cut(sheet, row)
    scale = SHEETS[sheet]['scale']
    print(f'  {sheet} row {row}: {len(frames)} frames, sheet scale {scale:.4f}')

    d = json.loads((REPO / 'web/assets/sprites/kael.json').read_text())
    fw, fh, cols, footY = d['frameW'], d['frameH'], d['cols'], d['footY']
    cells = []
    for i, im in enumerate(frames):
        im = im.resize((round(im.width * scale), round(im.height * scale)), Image.LANCZOS)
        ys, xs = np.nonzero(np.array(im)[..., 3] > 16)
        cell = Image.new('RGBA', (fw, fh), (0, 0, 0, 0))
        cell.alpha_composite(im, (fw // 2 - (xs.min() + xs.max()) // 2, footY - ys.max()))
        cells.append(cell)
        print(f'    frame {i+1}: ink {ys.max()-ys.min()+1}')

    strip = Image.new('RGBA', (fw * len(cells), fh), (38, 40, 54, 255))
    for i, c in enumerate(cells):
        strip.alpha_composite(c, (i * fw, 0))
    strip.convert('RGB').save(OUT / f'{prefix}_preview.png')
    print(f'  preview -> {OUT / (prefix + "_preview.png")}')
    if dry:
        return

    sheet_img = Image.open(REPO / 'web/assets/sprites/kael.png').convert('RGBA')
    assert sheet_img.width == cols * fw
    new = Image.new('RGBA', ((cols + len(cells)) * fw, fh), (0, 0, 0, 0))
    new.paste(sheet_img, (0, 0))
    for i, c in enumerate(cells):
        new.alpha_composite(c, ((cols + i) * fw, 0))
        d['frames'][f'{prefix}{i+1}'] = cols + i
    new.save(REPO / 'web/assets/sprites/kael.png')
    d['cols'] = cols + len(cells)
    (REPO / 'web/assets/sprites/kael.json').write_text(json.dumps(d, indent=2) + '\n')
    print(f'  packed {prefix}1..{len(cells)} at cells {cols}-{cols+len(cells)-1}; cols -> {d["cols"]}')


if __name__ == '__main__':
    main()
