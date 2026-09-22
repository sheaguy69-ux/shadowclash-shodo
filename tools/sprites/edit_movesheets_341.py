"""Edit the identity breaks off the three rejected Aug 2 move sheets. No redraw.

Owner ruling, Aug 2 2026: "why do we gotta redraw them? Just edit them." So the same
method that shipped 315, 332 and 334: nano-banana-pro STILL EDIT, one frame at a time,
pose frozen, only the named break touched.

1. EXECUTIONER (66 frames) — a sword in EACH hand, some frames a red tanto too.
   He carries ONE long katana; checked against 25 shipped cells.
2. KAEL (48 frames) — two EQUAL straight blades. One LONG katana + one SHORT wakizashi
   is his whole style. Worded as a REPLACEMENT, not a shortening: two straight prompt
   attempts at "make it shorter" came back unchanged (that failure built
   shorten_wakizashi.py) — a still editor will not change a measurement it does not
   consider wrong, but it will swap an object for a different one. His shipped idle
   rides along as a second reference image so the weapons are copied, not invented.
3. EMBER (54 frames, the sheet titled TSUBASA) — Shin's teal scarf, Shin's cyan eyes,
   FOUR claw blades. His lock: his own GREEN scarf, PALE GREEN eyes, THREE blades —
   the blade count is the same break 315 and 332 fixed, so that wording is verbatim.

The cut cells are RGB on the sheet's white page — fed as-is. Outputs come back 2K,
which is a free upscale: these sheets drew the body at ~100px and the packer needs
156-194px, so the extra pixels survive as edge quality.

Re-runnable: an existing output is skipped, so one bad frame can be deleted and
redone without paying for the rest.
"""
import concurrent.futures as cf
import json
import os
import pathlib
import re
import sys

import subprocess

from PIL import Image

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import fal_models

env = pathlib.Path('/Users/anthonyguy/WILDCOMIKS.2.0/.env.local')
os.environ['FAL_KEY'] = re.search(r'^FAL_KEY=["\']?([^"\'\n]+)', env.read_text(), re.M).group(1).strip()
import fal_client  # noqa: E402

ROOT = pathlib.Path(__file__).resolve().parents[2]
SHEETS = pathlib.Path(os.environ.get(
    'SHEETS_DIR',
    '/private/tmp/claude-501/-Users-anthonyguy-SHADOWCLASH-RECOVERED/'
    'bdb3d676-eaee-44e7-8aa3-b905c4a26f9e/scratchpad/sheets'))

LOCK = ('CHANGE NOTHING ELSE: identical pose, identical body and limb positions, '
        'identical colours everywhere not named above, identical heavy black outlines '
        'and cel shading, identical framing, size and position in the frame, flat pure '
        'white background. Do not redraw or restyle the character, do not move a limb, '
        'do not add text, shadow, ground, or background detail.')

EXEC = (
    'Edit this 2D cel-illustration fighting-game sprite frame. The chibi ninja in '
    'purple hooded armour with two curved horns and an orange scarf currently holds a '
    'sword in EACH hand. He must carry exactly ONE long katana. Remove the sword from '
    'one hand — keep the katana that is most prominent or most extended, and turn the '
    'other hand into an empty black-gloved fist, redrawing only the small area the '
    'removed blade covered. If a small red-hilted dagger or tanto is tucked at his hip '
    'or belt, remove that too. Exactly one sword must remain anywhere in the frame. ' + LOCK
)

KAEL = (
    'The FIRST image is a 2D cel-illustration fighting-game sprite frame to edit. The '
    'SECOND image is the same character\'s official reference. In the first image the '
    'black-and-gold chibi ninja holds two swords of the SAME length. Replace the sword '
    'in his LOWER or further-back hand with a SHORT WAKIZASHI like the shorter blade '
    'in the reference: measured guard to tip it is HALF the other sword\'s length, '
    'unmistakably a stubby short sword next to a long one, never a matched pair. Keep '
    'it in the same hand at the same angle with the same grip, hilt and guard — only '
    'the blade is different. The other hand\'s long katana stays exactly as drawn. ' + LOCK
)

EMBER = (
    'Edit this 2D cel-illustration fighting-game sprite frame of a green-hooded chibi '
    'ninja with claw gauntlets. Three fixes, nothing more. FIRST: his scarf is '
    'currently TEAL BLUE — recolour the scarf to the same muted green as his hood, '
    'keeping every fold and outline. SECOND: his glowing angled eyes are currently '
    'CYAN BLUE — recolour them to a soft PALE GREEN glow. THIRD: each claw gauntlet '
    'currently shows FOUR parallel silver blades — remove exactly ONE blade from EACH '
    'gauntlet so that THREE parallel silver blades remain on each hand, keeping the '
    'three remaining blades the same length, angle, spacing and position they already '
    'have, with the same black outlines and silver shading. ' + LOCK
)


def kael_ref():
    """His shipped idle on flat white — the reference the wakizashi is copied from."""
    man = json.loads((ROOT / 'web/assets/sprites/kael.json').read_text())
    sheet = Image.open(ROOT / 'web/assets/sprites/kael.png').convert('RGBA')
    w, h, i = man['frameW'], man['frameH'], man['frames']['idle']
    cell = sheet.crop((i * w, 0, (i + 1) * w, h))
    flat = Image.new('RGBA', cell.size, (255, 255, 255, 255))
    flat.alpha_composite(cell)
    p = SHEETS / 'kael/_ref_idle.png'
    flat.convert('RGB').save(p)
    return p


def one(src, prompt, out, refs):
    if out.exists():
        return f'  skip {out.name}'
    try:
        r = fal_models.still_edit(fal_client, prompt, [src] + refs, resolution='2K')
        subprocess.run(['curl', '-sL', '-o', str(out), r['images'][0]['url']], check=True)
        return f'  {out.parent.parent.name}/{out.name} ok'
    except Exception as e:
        return f'  {out.parent.parent.name}/{out.name} FAILED: {e}'


def main():
    only = sys.argv[1:] or ['exec', 'kael', 'ember']
    jobs = {'exec': (EXEC, []), 'kael': (KAEL, [kael_ref()]), 'ember': (EMBER, [])}
    tasks = []
    for name in only:
        prompt, refs = jobs[name]
        dst = SHEETS / name / 'edited'
        dst.mkdir(parents=True, exist_ok=True)
        for p in sorted((SHEETS / name / 'cut').glob('*.png')):
            tasks.append((p, prompt, dst / p.name, refs))
    print(f'{len(tasks)} frames to edit')
    done = 0
    with cf.ThreadPoolExecutor(6) as ex:
        for line in ex.map(lambda t: one(*t), tasks):
            done += 1
            print(f'{done:3d}/{len(tasks)}{line}', flush=True)


if __name__ == '__main__':
    main()
