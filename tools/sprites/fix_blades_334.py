"""Edit the two identity breaks off the Aug 1 sheets. No redraw, no regeneration.

1. EMBER — four blades per gauntlet again, on all 18 frames. His lock says THREE.
   This is the THIRD time (315 fixed the espec cells, 332 fixed the attack sheets),
   so the wording below is 332's wording verbatim, because it worked.

2. KAEL — the Twin Rising Fang row draws two swords of EQUAL length. Owner ruling,
   Aug 1 2026: one LONG katana + one SHORT wakizashi. His other row (ktrav) already
   has it right, so only kfang is touched.
   His black cape is NOT a defect — the shipped idle cell has one. Left alone.

Method is 315's and 332's: nano-banana-pro STILL EDIT, weapon only, pose frozen.
One edit per frame so a fan of blades is never inferred from a neighbouring pose.

The cut cells carry alpha; nano-banana is fed a flat-white composite because that is
what the whole pipeline keys off, and hands back the same.

Re-runnable: an existing output is skipped, so one bad frame can be deleted and
redone without paying for the other 23.
"""
import concurrent.futures as cf
import os
import pathlib
import re
import subprocess
import sys

from PIL import Image

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import fal_models

env = pathlib.Path('/Users/anthonyguy/WILDCOMIKS.2.0/.env.local')
os.environ['FAL_KEY'] = re.search(r'^FAL_KEY=["\']?([^"\'\n]+)', env.read_text(), re.M).group(1).strip()
import fal_client  # noqa: E402

ROOT = pathlib.Path(__file__).resolve().parents[2]
CUT = ROOT / 'media/handoff/all-moves-2026-08-01/cut'

EMBER = (
    'Edit this 2D cel-illustration fighting-game sprite frame. The green-hooded chibi '
    'ninja wears tekko-kagi claw gauntlets, and each gauntlet currently shows FOUR '
    'parallel silver blades. Remove exactly ONE blade from EACH gauntlet so that THREE '
    'parallel silver blades remain on each hand. Keep the three remaining blades the '
    'same length, angle, spacing and position they already have, with the same black '
    'outlines and silver shading. '
    'CHANGE NOTHING ELSE: identical pose, identical body, identical green hood, scarf '
    'and wraps, identical glowing pale-green eye, identical colours, identical line '
    'weight, identical framing and size, flat pure white background. Do not redraw or '
    'restyle the character, do not move a limb, do not add a weapon, do not add text, '
    'shadow or background detail.'
)

KAEL = (
    'Edit this 2D cel-illustration fighting-game sprite frame. The black-clad chibi '
    'ninja with gold trim holds a sword in each hand, and both swords are currently '
    'the SAME LENGTH. Shorten exactly ONE of them — the sword held in the LOWER or '
    'further-back hand — so its blade is roughly HALF the length of the other. The '
    'result must read as ONE LONG KATANA and ONE SHORT WAKIZASHI. The short blade '
    'must be UNMISTAKABLY shorter: measured from guard to tip it is HALF, not '
    'three-quarters, of the long blade. A viewer glancing at the frame must '
    'immediately see a long sword and a stubby short sword, never a matched pair. '
    'Keep the shortened blade in the same hand, at the same angle, with the same '
    'hilt, guard, black outline and silver shading — only the blade gets shorter. '
    'CHANGE NOTHING ELSE: identical pose, identical body, identical black hood, gold '
    'scarf, gold trim and BLACK CAPE, identical glowing gold eyes, identical colours, '
    'identical line weight, identical framing and size, flat pure white background. '
    'Do not redraw or restyle the character, do not move a limb, do not remove the '
    'cape, do not add text, shadow or background detail.'
)

JOBS = [(CUT / 'ember', EMBER, ('eshred', 'erip', 'ehook')),
        (CUT / 'kael', KAEL, ('kfang',))]


def one(src, prompt, out):
    if out.exists():
        return f'  skip {out.name}'
    white = Image.new('RGB', Image.open(src).size, (255, 255, 255))
    white.paste(Image.open(src).convert('RGBA'), mask=Image.open(src).convert('RGBA'))
    tmp = out.parent / f'_w_{src.name}'
    white.save(tmp)
    try:
        r = fal_models.still_edit(fal_client, prompt, tmp, resolution='2K')
        subprocess.run(['curl', '-sL', '-o', str(out), r['images'][0]['url']], check=True)
    finally:
        tmp.unlink(missing_ok=True)
    return f'  {out.name} ok'


def main():
    tasks = []
    for d, prompt, rows in JOBS:
        dst = d.parent / f'{d.name}-fixed'
        dst.mkdir(parents=True, exist_ok=True)
        for row in rows:
            for p in sorted(d.glob(f'{row}_*.png')):
                tasks.append((p, prompt, dst / p.name))
    print(f'{len(tasks)} frames')
    with cf.ThreadPoolExecutor(6) as ex:
        for line in ex.map(lambda t: one(*t), tasks):
            print(line, flush=True)


if __name__ == '__main__':
    main()
