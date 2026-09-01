#!/usr/bin/env python3
"""Is the ART inside a packed cell clean — or did the source board come with it?

  python3 tools/audit_frame_hygiene.py

check_moves.py asks whether a cell is REACHABLE. This asks whether it is CLEAN. Oni's
dash1/dash2/dash3 carried the source board's caption text as art for months —
"5. FORWARD DASH MID", "BACKSTEP PREP", panel border rules, and a sliver of the
neighbouring panel's figure. Every runtime probe in tools/ passed the whole time,
because every one of them measures whether a move FIRES.

⛔ AND THEY NEVER FIRED. Earlier notes here and in the SHEET_V chain said Oni "drew the
caption text on screen"; measured, that is false. No dash key was ever read — not one
literal F.<key> access, not one dirCells stem — and six driven executeShunshin dashes
drew cells 0-8, 40, 41, 42 and 67 and never the dash cells. Which is the real argument
for this tool: REACHABILITY and CLEANLINESS are independent, a cell can be filthy and
invisible at the same time, and the cheapest moment to fix one is while it is still the
other. Do not "downgrade" a dirty cell because nothing draws it.

TWO DETECTORS, both chosen by measuring the roster rather than guessing a threshold.

1. DETACHED TOP BAND. A caption sits at the top of the panel, is thin, and is separated
   from the figure by empty rows. Real art is either connected to the body or is a big
   mass of its own. So: the topmost opaque band, the empty gap under it, and the band's
   height against the body's.

   A flat-top ratio (top row width / widest row) was tried first and is WEAKER — it
   ranked legitimate wide FX (Mokurai's hollow halo, Exile's air arcs, Ember's motion
   smears) alongside the contaminated cells, because a halo genuinely is a wide bar at
   the top of the frame. Measured over 1941 referenced cells: median 5.2%, p90 19.2%,
   p99 58.8% — the tail is real art, not junk, so the ratio has no clean cut point.

2. COLLAPSED FAMILY. A `name_1..n` family whose every frame resolves to ONE cell is a
   multi-frame move drawing a single static picture. This is how Mokurai's guard shipped
   with no reaction (block/block2/bblock all cell 225) and how Exile's shipped before it.

KNOWN_OK is the other half of the tool. A detector that reports legitimate art is a
detector nobody runs twice, so every false positive found during the Aug 11 sweep is
listed below WITH the reason it is fine and how that was established — not silently
thresholded away.
"""
import glob
import json
import os
import pathlib
import re
import sys
from collections import defaultdict

from PIL import Image

Image.MAX_IMAGE_PIXELS = None
REPO = pathlib.Path(__file__).resolve().parents[1]
SPR = REPO / 'web/assets/sprites'

ALPHA = 8            # a pixel counts as art above this
MIN_GAP = 8          # empty rows between the top band and the body
MAX_BAND = 0.25      # ...and the band is at most this fraction of the body's height

# Verified by eye on 2026-08-11. Each entry is art, not contamination.
#
# ⛔ KEYED BY FRAME NAME, NOT BY CELL INDEX. An index is not an identity: it is wherever
# the last pack happened to put the art, and it moves whenever a sheet is re-packed or two
# lanes are consolidated. These entries were originally filed by index and every one of
# them silently stopped matching when lane/opus5-oni-frames merged in — airthrow3 108->96,
# attack_body6 34->31, exile's four 127-130 -> 77-80 — so the audit failed with six
# findings that had all been verified as real art weeks earlier. A suppression that
# expires on a re-pack is worse than none: it turns a green check red for no reason, and
# the fix looks like "re-verify everything". The frame key is stable, so suppress on that.
# A cell carrying several keys (exile 77 is air1/air2/air3) is cleared if ANY of them
# is listed here.
KNOWN_OK = {
    ('tsubasa', 'airthrow3'):    'the detached band IS the thrown dagger in flight. '
                                 'Rendered and confirmed: he has released one knife and '
                                 'still holds the other. Correct art for an air throw.',
    ('ember', 'heavy_i4'):       'grey motion-smear FX, not un-keyed page white. '
                                 'Measured: 0.4% neutral-bright pixels, and the '
                                 'known-good heavy1 carries a LONGER straight edge run '
                                 '(60px) than any heavy_i cell.',
    ('ember', 'attack_body6'):   '1px rule, an FX filament, not a panel border.',
    ('ember', 'light2'):         'same 1px FX filament.',
    ('exile', 'air1'):           '1px FX filament above her air arc.',
    ('exile', 'xair2'):          'same.',
    ('exile', 'xairf'):          'same.',
    ('exile', 'xairb'):          'same.',
}

# A family may resolve to one cell when nothing DRAWS it as a sequence. Verified against
# the engine, not assumed.
KNOWN_FLAT = {
    ('mokurai', 'run_clean'): 'the engine reads run_clean only for id 5 (Kael, the '
                              'bunshin cells at index 2361). Mokurai is id 6, so his '
                              'run_clean1..8 are dead aliases with no draw path. His '
                              'real run is run1/run2, his cracked run is brun1..4.',
    ('mokurai', 'air'):       'air2/air3 are read only under `p.spec.id <= 5`. Mokurai '
                              'is 6; his air draws mairf/mairb/bair, which are distinct.',
    ('exile', 'air'):         'air2/air3 likewise unreachable at id 7. Her air light is a '
                              'real 3-beat — [air1, xairf|xairb|xair2, air1] — so air1 is '
                              'the bookend by design and 128/129/130 carry the middle.',
    ('exile', 'hurt'):        'hurt/hurt2/hurt3 are shadowed by xhurt1 for id 7.',
    ('mokurai', 'hurt'):      'shadowed by his own mhurt cells.',
    ('mokurai', 'mdive'):     'single-cell dive by design; the mechanic bands on airtime.',
    ('mokurai', 'mwall'):     'single-cell wall contact, same reason.',
}


def cells(name):
    """Referenced cell index -> the keys pointing at it."""
    man = json.loads((SPR / f'{name}.json').read_text())
    fr = man.get('frames', man)
    used = defaultdict(list)
    for k, v in fr.items():
        if isinstance(v, int):
            used[v].append(k)
    return man, fr, used


def detached_band(px, x0, W, H):
    """(gap, band height, body height) for a top band separated from the body."""
    occ = [sum(1 for x in range(x0, x0 + W) if px[x, y] > ALPHA) for y in range(H)]
    live = [y for y, c in enumerate(occ) if c]
    if not live:
        return None
    top = live[0]
    y = top
    while y < H and occ[y]:
        y += 1
    band_end = y
    while y < H and not occ[y]:
        y += 1
    if y >= H:
        return None                      # one mass only — nothing detached
    return band_end - y, band_end - top, live[-1] - y + 1


def main():
    fails, orphans = [], []
    checked = 0
    for jf in sorted(glob.glob(str(SPR / '*.json'))):
        if jf.endswith('PURGED-KEYS.json'):
            continue   # key tombstones, not a fighter manifest
        name = os.path.basename(jf)[:-5]
        man, fr, used = cells(name)
        W, H = man['frameW'], man['frameH']
        im = Image.open(jf[:-5] + '.png').convert('RGBA')
        px = im.split()[3].load()

        for idx in sorted(used):
            x0 = idx * W
            if x0 + W > im.width:
                continue
            checked += 1
            if any((name, k) in KNOWN_OK for k in used[idx]):
                continue
            got = detached_band(px, x0, W, H)
            if not got:
                continue
            gap, band_h, body_h = -got[0], got[1], got[2]
            if gap >= MIN_GAP and band_h <= body_h * MAX_BAND:
                fails.append(
                    f'{name}: cell {idx} ({",".join(sorted(used[idx]))}) has a DETACHED '
                    f'TOP BAND — {band_h}px of art, {gap}px of nothing, then a {body_h}px '
                    f'body. That is the caption/border signature. Render it and look; if '
                    f'it is real art, add it to KNOWN_OK with the reason.')

        # ⛔ AND SWEEP THE CELLS NOTHING POINTS AT. Walking `used` alone is a blind spot
        # with a real example behind it: 12771e6 fixed Oni's dash the append-only way,
        # packing clean beats at 153-155 and repointing the keys, which is correct — but
        # it leaves the contaminated originals at 10-12 sitting in the png. They stopped
        # being drawn, so this audit stopped LOOKING at them, and it reported "zero
        # contaminated" over three cells still measuring a 100% flat top. Nothing renders
        # them, so this is a WARNING and not a failure — append-only means orphans are
        # legitimate and failing here would red a suite over a non-regression — but the
        # caption art still ships in the file, and an audit that cannot see it is worse
        # than one that never claimed to.
        for idx in range(im.width // W):
            if idx in used:      # an orphan has no key, so KNOWN_OK cannot speak for it
                continue
            got = detached_band(px, idx * W, W, H)
            if not got:
                continue
            gap, band_h, body_h = -got[0], got[1], got[2]
            if gap >= MIN_GAP and band_h <= body_h * MAX_BAND:
                orphans.append(
                    f'{name}: cell {idx} is UNREFERENCED but still carries the '
                    f'caption/border signature ({band_h}px band, {gap}px gap, {body_h}px '
                    f'body). Nothing draws it, so nobody sees it — but it ships in the '
                    f'png. Blank it in a pass that says so, or add it to KNOWN_OK.')

        fam = defaultdict(dict)
        for k, v in fr.items():
            if not isinstance(v, int):
                continue
            m = re.match(r'^(.*?)_?(\d+)$', k)
            if m and m.group(1):
                fam[m.group(1)][int(m.group(2))] = v
        for base, seq in sorted(fam.items()):
            if len(seq) > 1 and len(set(seq.values())) == 1 \
                    and (name, base) not in KNOWN_FLAT:
                fails.append(
                    f'{name}: {base}_1..{len(seq)} ALL resolve to cell '
                    f'{next(iter(seq.values()))} — a {len(seq)}-frame move drawing one '
                    f'static picture. Point the frames at their own cells, or record in '
                    f'KNOWN_FLAT which engine path shadows this family.')

    print(f'checked {checked} referenced cells across '
          f'{len(glob.glob(str(SPR / "*.json")))} sheets')
    if orphans:
        print(f'\n⚠ {len(orphans)} UNREFERENCED cell(s) still carrying caption art '
              f'(not drawn, so not a failure — but still in the png):')
        for o in orphans:
            print(f'  - {o}')
    if fails:
        print(f'\n{len(fails)} FAILED:')
        for f in fails:
            print(f'  - {f}')
        return 1
    print('all good — no contaminated cells, no collapsed families')
    return 0


if __name__ == '__main__':
    sys.exit(main())
