#!/usr/bin/env python3
"""THE REDRAW PACK — one labelled reference strip per animation row, plus the worklist.

    python3 tools/moveset_sheet.py --tree ~/shadowclash-fable-5 --out ~/Downloads
    python3 tools/redraw_pack.py  --tree ~/shadowclash-fable-5 \
        --rows ~/Downloads/ShadowClash-moveset-SHEET_V575-rows.csv --out ~/Downloads

EVERY row ships. The whole roster is being redrawn in a new style, so nothing here is
filtered out for being superseded or unreferenced — those rows carry a tag in the caption
and keep their place in the queue.

Each strip is the row's real cells at full sheet resolution, side by side, in frame order,
captioned with what a redraw has to match: cell box, the body height range measured off
the art, the foot line, and the input that fires it. Cells are cut from the packed sheet,
which is the only picture the engine ever draws — a strip and the game cannot disagree.

The queue is ordered the way a fighter is built: idle first, then locomotion, air,
defense, reactions, wall, grabs, flavour, and the attack kit last.
"""
import argparse
import collections
import csv
import json
import pathlib
import re

from PIL import Image, ImageDraw

ORDER = ['idle', 'locomotion', 'air', 'defense', 'reaction', 'wall', 'grab',
         'flavour', 'attack', 'other']
PAD, BAR, GAP = 8, 34, 6
INK, BG, DIM = (240, 240, 240), (24, 24, 28), (150, 150, 158)
CELLBG, FOOT = (52, 52, 58), (200, 90, 90)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--tree', required=True)
    ap.add_argument('--rows', required=True, help='the rows CSV from moveset_sheet.py')
    ap.add_argument('--out', default=str(pathlib.Path.home() / 'Downloads'))
    a = ap.parse_args()
    tree = pathlib.Path(a.tree).expanduser().resolve()
    rows = list(csv.DictReader(open(pathlib.Path(a.rows).expanduser())))
    ver = pathlib.Path(a.rows).stem.split('-')[-2]           # ...-SHEET_V575-rows
    out = pathlib.Path(a.out).expanduser().resolve() / f'shadowclash-redraw-{ver}'

    sheets, frames = {}, {}
    queue = collections.defaultdict(int)
    work = []
    for r in sorted(rows, key=lambda r: (r['fighter'], ORDER.index(r['kind']), r['row'], r['variant'])):
        f = r['fighter']
        if f not in sheets:
            sheets[f] = Image.open(tree / f'web/assets/sprites/{f}.png').convert('RGBA')
            frames[f] = json.loads((tree / f'web/assets/sprites/{f}.json').read_text())['frames']
        sheet = sheets[f]
        cw, ch = int(r['cell_w']), int(r['cell_h'])
        # the manifest, not the CSV's sorted cell list: a row can draw the same cell
        # twice and its frames are not always in ascending cell order, so only key->cell
        # gets the strip in true frame order.
        strip_keys = r['keys'].split()
        per_key = [frames[f][k] for k in strip_keys]
        queue[f] += 1
        name = f"{queue[f]:03d}_{r['kind']}_{r['row']}{'_' + r['variant'] if r['variant'] else ''}.png"
        dst = out / f / name
        dst.parent.mkdir(parents=True, exist_ok=True)

        n = len(strip_keys)
        img = Image.new('RGBA', (PAD * 2 + n * cw + (n - 1) * GAP, BAR + PAD * 2 + ch + 18), BG)
        d = ImageDraw.Draw(img)
        # An UPRIGHT row that does not measure the idle's height is drawn at the wrong
        # size — kael sprints at 76% of his own standing height. Only idle and the
        # run/walk family are judged: a crouch, roll, jump tuck or dash is SUPPOSED to be
        # shorter, so flagging those would be noise. 9 rows roster-wide trip this.
        upright = ((r['kind'] == 'idle' and r['row'] != 'sit')   # sitting is short on purpose
                   or re.search(r'run|walk|sprint', r['row']))
        scale_flag = ('OFF-SCALE vs idle — redraw at idle height'
                      if upright and not 92 <= int(r['pct_of_idle']) <= 108 else '')
        tag = {'superseded': '  [SUPERSEDED VARIANT]', 'UNREFERENCED': '  [UNREFERENCED BY THE ENGINE]'}
        d.text((PAD, 8), f"{f.upper()}  {r['row']}{'/' + r['variant'] if r['variant'] else ''}"
                         f"  ·  {r['kind']}  ·  {n} frames  ·  cell {cw}x{ch}, foot line y={r['foot_line']}"
                         f"  ·  body h {r['body_h_min']}-{r['body_h_max']}px ({r['pct_of_idle']}% of idle)"
                         + tag.get(r['status'], '')
                         + ('   ⛔ ' + scale_flag if scale_flag else ''), fill=INK)
        d.text((PAD, 21), (f"input: {r['inputs']}  ·  {r['dmg']} dmg  ·  {r['dur_ms']}ms"
                           if r['inputs'] else 'drawn by the state machine, not by an attack input'),
               fill=DIM)
        for j, (k, c) in enumerate(zip(strip_keys, per_key)):
            x = PAD + j * (cw + GAP)
            cell = sheet.crop((c * cw, 0, c * cw + cw, ch))
            d.rectangle([x, BAR + PAD, x + cw - 1, BAR + PAD + ch - 1], fill=CELLBG)
            img.paste(cell, (x, BAR + PAD), cell)   # mask=cell, or the paste punches the
            # backdrop out and every transparent pixel reads as a white hole
            d.line([(x, BAR + PAD + int(r['foot_line'])), (x + cw, BAR + PAD + int(r['foot_line']))],
                   fill=FOOT, width=1)
            d.text((x + 2, BAR + PAD + ch + 3), f'{k}  cell {c}', fill=DIM)
        img.save(dst)
        work.append(dict(draw_no=queue[f], fighter=f, kind=r['kind'], row=r['row'],
                         variant=r['variant'], frames=r['frames'], unique_cells=r['unique_cells'],
                         inputs=r['inputs'], engine_status=r['status'],
                         cell_w=cw, cell_h=ch, foot_line=r['foot_line'],
                         body_h_min=r['body_h_min'], body_h_max=r['body_h_max'],
                         pct_of_idle=r['pct_of_idle'], scale_flag=scale_flag,
                         cells=r['cells'], keys=r['keys'],
                         reference=str(dst), redrawn='', new_art_file='', notes=''))

    wl = out / f'REDRAW-WORKLIST-{ver}.csv'
    with open(wl, 'w', newline='') as fh:
        w = csv.DictWriter(fh, fieldnames=list(work[0]))
        w.writeheader()
        w.writerows(work)
    per = collections.Counter(r['fighter'] for r in work)
    print(f'  {wl}')
    cells = {(r['fighter'], c) for r in work for c in r['cells'].split(',')}
    print(f'  {len(work)} strips, {sum(int(r["frames"]) for r in work)} frames, {len(cells)} cells')
    for f in per:
        print(f'    {f:12} {per[f]:3} rows  ->  {out / f}')


if __name__ == '__main__':
    main()
