"""Edit the FOURTH blade off every claw on Ember's new attack sheet.

Owner, Jul 31 2026: "you are a professional editor so edit whoever mistake that
ember just removed the fourth claw." His sheet came back with four blades per
gauntlet on all 24 frames; his lock says three ("TEKKO-KAGI CLAWS: three parallel
silver blades on the back of EACH hand"), and this is the SECOND time the roster
has drifted to four — SHEET_V 315 fixed the same thing on the espec cells.

Method is 315's, which worked: nano-banana-pro STILL EDIT, claws only, pose
frozen, no clip regenerated. One edit per frame so a wide fan of blades never has
to be inferred from a neighbouring pose.

Re-runnable: an existing output is skipped, so a single bad frame can be deleted
and redone without paying for the other 23.
"""
import os
import pathlib
import re
import subprocess
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import fal_models

env = pathlib.Path('/Users/anthonyguy/WILDCOMIKS.2.0/.env.local')
os.environ['FAL_KEY'] = re.search(r'^FAL_KEY=["\']?([^"\'\n]+)', env.read_text(), re.M).group(1).strip()
import fal_client  # noqa: E402

ROOT = pathlib.Path(__file__).resolve().parents[2]
SRC = ROOT / 'media/handoff/attack-sheets-2026-07-31/cut/ember'
DST = ROOT / 'media/handoff/attack-sheets-2026-07-31/cut/ember-3blade'

PROMPT = (
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


def main():
    DST.mkdir(parents=True, exist_ok=True)
    frames = sorted(SRC.glob('*.png'))
    only = sys.argv[1:]
    for p in frames:
        if only and not any(o in p.name for o in only):
            continue
        out = DST / p.name
        if out.exists():
            print(f'  skip {p.name}')
            continue
        r = fal_models.still_edit(fal_client, PROMPT, p, resolution='2K')
        subprocess.run(['curl', '-sL', '-o', str(out), r['images'][0]['url']], check=True)
        print(f'  {p.name} -> {out.name}')


if __name__ == '__main__':
    main()
