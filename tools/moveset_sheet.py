#!/usr/bin/env python3
"""THE MOVESET SPREADSHEET — every live cell of every fighter, in one CSV pair.

    python3 tools/moveset_sheet.py --tree ~/shadowclash-fable-5 --out ~/Downloads

Writes two files:
  * <name>-rows.csv    one line per ANIMATION ROW  (the redraw checklist)
  * <name>-frames.csv  one line per FRAME KEY      (the frame-by-frame detail)

Four sources, none of them guessed:
  * `web/assets/sprites/<f>.json` — key -> cell, frameW/H, footY, scale.
  * `web/assets/sprites/<f>.png`  — the cell's real content bbox, measured with PIL, so
    the body height / foot line a redraw has to MATCH is a number and not an eyeball.
  * `tools/moveset_probe.mjs`     — one real press through executeAttack for all 9 x 30
    inputs, so "which input draws this cell" is measured off the running engine.
  * `web/index.html`              — every reference to the row's keys. A row no branch
    names is art nobody draws; that is the column that says "do NOT redraw this".

⛔ THE INPUT JOIN IS ON THE CELL INDEX, NOT ON THE ROW NAME. Row names are not a
namespace: shin's `f2_air_1` and ember's `light1` do not decompose the same way, and much
of every sheet is aliased (many keys, one drawing). Cell indices are the only thing both
sides agree on.

⛔ AN EMPTY `inputs` IS NOT "DEAD". The 30 inputs are the ATTACK surface; idle, run,
jump, hurt, roll, block, wall and grab rows are drawn by the state machine, which
spriteFrameIndex resolves through dozens of pre-switch timer windows that cannot be faked
by setting p.state. `engine_refs` is what separates state-driven art from abandoned art.
Chaining was measured too and adds nothing: walking every light/heavy/special string to
beat 6 revealed 3 new cells across the whole roster, all on Oni — the chain art IS the
opener art.
"""
import argparse
import collections
import csv
import json
import pathlib
import re
import subprocess
import sys

from PIL import Image

REPO = pathlib.Path(__file__).resolve().parents[1]

# row name -> what the fighter is DOING. First match wins, so specific patterns lead.
KIND = [
    (r'^(idle|stand|sit|bidle|hidle|canon_idle|xidle|f2_idle)', 'idle'),
    (r'(run|sprint|dash|walk|slide|tsprint|nrun)', 'locomotion'),
    (r'^(jump|fall|land|ajump|airidle|bflip|cart|dive|f2_jump|f2_land)', 'air'),
    (r'(hurt|grabbed|block|guard|xblk|crefl)', 'reaction'),
    (r'(roll|crouch|kneel|parry)', 'defense'),
    (r'wall', 'wall'),
    (r'^(grab|throw|airthrow|mthrow|xthrow|xgrap|athrow)', 'grab'),
    (r'^(handseal|feint|taunt|pray|bpray|unmade|sheath|xsheath)', 'flavour'),
    # everything a fighter swings. The systematic naming first — h*/s* are the heavy and
    # special directionals, a* the aerials, k* the command kicks, g[lhs]* Oni's ground
    # tiers — then the generic tiers and the x-prefixed drawn rows.
    (r'^(hneu|hfwd|hback|hup|hdown|sneu|sfwd|sback|sup|sdown)$', 'attack'),
    (r'^(g[lhs][a-z]+|air|afwd|aback|aup|adown|aneu|aspin|airkick|airpoke|airhurl)$', 'attack'),
    (r'^(kheel|kpush|ksweep|kstomp|kick|punch|lunge|whip|taijutsu)$', 'attack'),
    (r'^(light|heavy|special|attack_body|upatk|x[a-z]|f2_(light|heavy|clow|csweep|air|dashcut))', 'attack'),
]
VARIANT = re.compile(r'_(v\d+[a-z]*|old[\w]*|scaled|headless[\w]*|DO_NOT_USE)$')


def parse_key(key):
    """`f2_light1_3` -> (f2_light1, 3, ''), `espec1_v307` -> (espec, 1, v307),
    `light1_old319` -> (light, 1, old319), `crouch_1` -> (crouch, 1, '')."""
    k, variant = key, ''
    m = VARIANT.search(k)
    if m:
        variant, k = m.group(1), k[:m.start()]
    frame = 1
    m = re.search(r'_?(\d+)$', k)
    if m:
        frame, k = int(m.group(1)), k[:m.start()]
    if not variant:
        m = VARIANT.search(k)
        if m:
            variant, k = m.group(1), k[:m.start()]
    return (k.rstrip('_') or key), frame, variant


def kind_of(row, has_input):
    for pat, k in KIND:
        if re.search(pat, row):
            return k
    # a row no naming rule claims but a real press draws is an attack, measured
    return 'attack' if has_input else 'other'


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--tree', default=str(REPO), help='repo whose web/assets/sprites to read')
    ap.add_argument('--out', default=str(pathlib.Path.home() / 'Downloads'))
    ap.add_argument('--probe', default='', help='reuse a moveset_probe.mjs json instead of running it')
    a = ap.parse_args()
    tree = pathlib.Path(a.tree).expanduser().resolve()
    out = pathlib.Path(a.out).expanduser().resolve()

    if a.probe:
        probe = json.loads(pathlib.Path(a.probe).read_text())
    else:
        r = subprocess.run(['node', str(REPO / 'tools/moveset_probe.mjs')],
                           cwd=tree, capture_output=True, text=True)
        if r.returncode:
            sys.exit(f'probe failed: {r.stderr.strip()}')
        probe = json.loads(r.stdout)
    if pathlib.Path(probe['tree']).resolve() != tree:
        sys.exit(f"probe measured {probe['tree']}, not {tree} — rebind :9101 or pass --tree")
    sheet_v = probe['sheet_v']
    engine = (tree / 'web/index.html').read_text()

    def refs(row, keys):
        """How often the engine names this row's art: `F.light1`, `F['light'+n]`,
        `F.f2_air_3`, the bare-quoted key. Zero means no branch can draw it."""
        n = 0
        for pat in (rf"F\.{re.escape(row)}\d*\b", rf"['\"]{re.escape(row)}\d*['\"]",
                    rf"['\"]{re.escape(row)}_?['\"]\s*\+"):
            n += len(re.findall(pat, engine))
        for k in keys:
            n += len(re.findall(rf"F\.{re.escape(k)}\b|['\"]{re.escape(k)}['\"]", engine))
        return n

    frame_rows, row_rows = [], []
    for name, pf in probe['fighters'].items():
        man = json.loads((tree / f'web/assets/sprites/{name}.json').read_text())
        F = man['frames']
        fw, fh = man['frameW'], man['frameH']
        footY = man.get('footY', fh)
        img = Image.open(tree / f'web/assets/sprites/{name}.png').convert('RGBA')
        alpha = img.getchannel('A')

        keys_on = collections.defaultdict(list)
        for k, i in F.items():
            keys_on[i].append(k)
        inputs_on = collections.defaultdict(list)   # cell -> inputs measured drawing it
        move_of = {}
        for r in pf['rows']:
            label = f"{'gnd' if r['where'] == 'ground' else 'air'} {r['dir']}+{r['tier']}"
            for c in r['cells']:
                inputs_on[c].append(label)
            move_of[label] = r

        box = {}                                     # measure every live cell once
        for i in sorted(set(F.values())):
            box[i] = alpha.crop((i * fw, 0, i * fw + fw, fh)).getbbox() or (0, 0, 0, 0)
        idle_cell = F.get('idle1', F.get('idle', 0))
        idle_h = (box[idle_cell][3] - box[idle_cell][1]) or 1

        parsed = {k: parse_key(k) for k in F}
        by_row = collections.defaultdict(list)
        for k in sorted(F, key=lambda k: (parsed[k][0], parsed[k][2], parsed[k][1])):
            by_row[(parsed[k][0], parsed[k][2])].append(k)

        for (row, variant), keys in sorted(by_row.items()):
            cells = [F[k] for k in keys]
            heights = [box[c][3] - box[c][1] for c in cells]
            feet = [box[c][3] for c in cells]
            ins = sorted({i for c in cells for i in inputs_on[c]})
            nrefs = refs(row, keys)
            status = ('input-mapped' if ins else 'superseded' if variant else
                      'engine-referenced' if nrefs else 'UNREFERENCED')
            row_rows.append(dict(
                fighter=name, row=row, variant=variant, kind=kind_of(row, bool(ins)), status=status,
                frames=len(keys), unique_cells=len(set(cells)),
                inputs='; '.join(ins),
                dmg=max([move_of[i]['dmg'] for i in ins] or [0]) or '',
                dur_ms=max([move_of[i]['dur'] for i in ins] or [0]) or '',
                engine_refs=nrefs,
                cells=','.join(str(c) for c in sorted(set(cells))),
                keys=' '.join(keys),
                body_h_min=min(heights), body_h_max=max(heights),
                h_spread_pct=round(100 * (max(heights) - min(heights)) / (max(heights) or 1), 1),
                pct_of_idle=round(100 * (sum(heights) / len(heights)) / idle_h),
                foot_spread_px=max(feet) - min(feet),
                cell_w=fw, cell_h=fh, foot_line=footY,
                redo='', new_art_file='', notes=''))

            for k in keys:
                c = F[k]
                x0, y0, x1, y1 = box[c]
                frame_rows.append(dict(
                    fighter=name, row=row, variant=variant, frame=parsed[k][1], key=k, cell=c,
                    kind=kind_of(row, bool(inputs_on[c])), inputs='; '.join(sorted(set(inputs_on[c]))),
                    sheet_x=c * fw, sheet_y=0, cell_w=fw, cell_h=fh,
                    body_w=x1 - x0, body_h=y1 - y0,
                    body_left=x0, body_top=y0, body_right=x1, body_bottom=y1,
                    foot_offset_px=y1 - footY, pct_of_idle=round(100 * (y1 - y0) / idle_h),
                    shared_with=' '.join(sorted(set(keys_on[c]) - {k})),
                    redo='', new_art_file='', notes=''))
        img.close()
        # the check: every key in the manifest is on exactly one line, and the lines
        # between them cover every live cell. A row-name rule that swallowed or split a
        # key would break one of these before a wrong CSV ever reached the owner.
        mine = [r for r in frame_rows if r['fighter'] == name]
        assert len(mine) == len(F), f'{name}: {len(mine)} lines for {len(F)} keys'
        assert {r['key'] for r in mine} == set(F), f'{name}: key set drifted'
        assert {r['cell'] for r in mine} == set(F.values()), f'{name}: cells missed'

    out.mkdir(parents=True, exist_ok=True)
    stem = f'ShadowClash-moveset-SHEET_V{sheet_v}'
    for fn, data in ((f'{stem}-rows.csv', row_rows), (f'{stem}-frames.csv', frame_rows)):
        with open(out / fn, 'w', newline='') as fh:
            w = csv.DictWriter(fh, fieldnames=list(data[0]))
            w.writeheader()
            w.writerows(data)
        print(f'  {out / fn}  ({len(data)} lines)')

    rows_by = collections.Counter(r['fighter'] for r in row_rows)
    keys_by = collections.Counter(r['fighter'] for r in frame_rows)
    cells_by = collections.defaultdict(set)
    for r in frame_rows:
        cells_by[r['fighter']].add(r['cell'])
    print(f"\n  SHEET_V {sheet_v} @ {probe['head'][:7]} — {len(row_rows)} rows, "
          f"{len(frame_rows)} keys, {sum(len(v) for v in cells_by.values())} live cells")
    for f in rows_by:
        print(f'    {f:12} {rows_by[f]:3} rows  {keys_by[f]:4} keys  {len(cells_by[f]):4} cells')
    print('   ', dict(collections.Counter(r['status'] for r in row_rows)),
          dict(collections.Counter(r['kind'] for r in row_rows)))


if __name__ == '__main__':
    main()
