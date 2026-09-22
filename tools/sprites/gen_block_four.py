"""Guard + at-impact block frames for the four originals: mizu, tsubasa, ember, shin.

Owner picked this job (Jul 31 2026) after approving the same pair for the
executioner and Kael. The engine already swaps them —
`p.blockPushTimer > 0 ? F.block2 : F.block` (web/index.html) — so each fighter
needs a CALM GUARD and an AT-IMPACT beat, nothing else.

⛔ WHAT IS ACTUALLY BROKEN, measured before spending a cent. All four `block2`
cells are the wrong pose AND damaged: mizu 54, tsubasa 57, shin 63, ember 48 are
crouched LUNGES (a slide or dash beat, not a hit reaction), each with a hard
vertical cut edge and a dark slab bleeding off the right side — a keying failure
from a clip crop — plus white motion-smear at the feet. mizu carries 12 columns of
opaque near-black, tsubasa 68. So this is not a polish pass; those cells show a
black slab on screen every time one of them is hit while blocking.

SEED = THE PACKED `block` CELL, NOT THE MASTER. Two reasons. (1) Shin's master
truecolor-raw/idle.png draws him HOLDING A DAGGER against an identity lock that
forbids blades — that contamination is why every shin clip inherited them (see
the channel, SHEET_V 318). (2) A packed cell is already in the sheet's size
lineage, so the repack scale lands near 1.0 instead of being guessed.

Identity strings are the per-fighter locks verbatim from
media/polished-candidates/<name>/identity-true.txt, FORBIDDEN clauses included —
those are harvest gates, not flavour.
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
import fal_client  # noqa: E402  (needs FAL_KEY in env first)
import json  # noqa: E402
from PIL import Image  # noqa: E402

ROOT = pathlib.Path(__file__).resolve().parents[2]
OUT = ROOT / 'media/polished-candidates/block-four-331'
OUT.mkdir(parents=True, exist_ok=True)

IDENTITY = {
    'mizu': ('Purple-robed tall-hooded chibi ninja, long purple robe with lighter purple scarf, '
             'white featureless angled eyes inside a black faceless hood, LONG tan wooden bo staff '
             'held in BOTH hands. FORBIDDEN: bladed weapons, short staff, a second character.'),
    'tsubasa': ('Black-clad chibi ninja with NO HOOD: spiky black hair with red streaks fully visible, '
                'black face mask, red scarf and red sash wraps, TWO SMALL silver daggers (one per hand), '
                'white featureless angled eyes. FORBIDDEN: a hood of any kind, full-length swords, purple.'),
    'ember': ('Green-clad hooded chibi ninja, layered mid-green hood and scarf over darker green body '
              'wraps, glowing pale-green featureless angled eyes inside a black faceless hood, '
              'TEKKO-KAGI CLAWS: three parallel silver blades on the back of EACH hand. '
              'FORBIDDEN: swords or daggers of any kind (claws only), purple.'),
    'shin': ('Dark-green hooded chibi ninja in a low crouch, deep-teal scarf, glowing pale-cyan '
             'featureless angled eyes inside a black faceless hood, wrapped forearms and shins, '
             'ONE four-point wire shuriken. FORBIDDEN: any sword or dagger, standing tall, purple.'),
}
# what each one actually raises to catch a blow — a guard has to hold the weapon it owns
GUARD = {
    'mizu': 'the long bo staff held VERTICALLY in both hands, close in front of the face and chest, forearms tight behind it',
    'tsubasa': 'both daggers raised and CROSSED in an X in front of the face, blades outward, elbows tucked',
    'ember': 'both clawed hands raised and CROSSED in front of the face, the six blades forming a barrier, elbows tucked',
    'shin': 'both wrapped forearms raised and CROSSED in front of the face, the wire shuriken gripped in the near hand, staying in the low crouch',
}

TAIL = ('2D cel illustration in a clean high-contrast vector style, heavy black outlines, '
        'controlled dark palette, readable silhouette, pure side profile facing LEFT, '
        'full body with both feet flat on the same ground line, '
        'solid pure white background, no ground, no shadow, no motion blur, no speed lines, '
        'no second character, no text, no logo, no border, no cropping of the body.')


def prompt_guard(name):
    return (f'Edit this 2D cel-illustration fighting-game sprite. {IDENTITY[name]} '
            f'Redraw the SAME character in a tight DEFENSIVE GUARD: {GUARD[name]}. '
            'Shoulders lowered, weight even on both feet, braced and still — bracing to receive a '
            'blow, NOT attacking and NOT stepping. Keep the costume, colours, weapon, eyes and '
            f'proportions exactly as in the reference. {TAIL}')


def prompt_hit(name):
    return (f'Edit this 2D cel-illustration fighting-game sprite. {IDENTITY[name]} '
            f'Redraw the SAME character in the SAME defensive guard — {GUARD[name]} — at the '
            'EXACT INSTANT a heavy blow lands ON the guard: head snapped slightly back, weight '
            'driven onto the back foot, arms compressed toward the body, and a burst of bright '
            'yellow-white impact sparks radiating from the point of contact on the guard itself. '
            'The guard HOLDS — it is not broken open and the character is not knocked down. '
            f'Keep the costume, colours, weapon, eyes and proportions exactly as in the reference. {TAIL}')


def main():
    only = sys.argv[1:] or list(IDENTITY)
    for name in only:
        d = json.loads((ROOT / f'web/assets/sprites/{name}.json').read_text())
        fw, fh = d['frameW'], d['frameH']
        sheet = Image.open(ROOT / f'web/assets/sprites/{name}.png').convert('RGBA')
        # ⛔ SHIN SEEDS FROM HIS IDLE, NOT HIS BLOCK. His lock says "permanent low
        # crouch, FORBIDDEN: standing-tall posture" — and his block cell 10 STANDS
        # TALL, so the first pass inherited the violation and came back upright.
        # Cell 77 is the crouched stance 316 turned him into.
        c = d['frames']['idle' if name == 'shin' else 'block']
        seed = OUT / f'{name}-seed-cell{c}.png'
        cell = sheet.crop((c * fw, 0, c * fw + fw, fh))
        flat = Image.new('RGBA', cell.size, (255, 255, 255, 255))
        flat.alpha_composite(cell)          # white field: the key recipe floodfills white
        flat.convert('RGB').save(seed)
        for tag, prompt in (('guard', prompt_guard(name)), ('hit', prompt_hit(name))):
            dst = OUT / f'{name}-{tag}.png'
            if dst.exists():
                print(f'  skip {dst.name} (exists)')
                continue
            r = fal_models.still_edit(fal_client, prompt, seed, resolution='2K')
            url = r['images'][0]['url']
            subprocess.run(['curl', '-sL', '-o', str(dst), url], check=True)
            print(f'  {name} {tag} -> {dst}')


if __name__ == '__main__':
    main()
