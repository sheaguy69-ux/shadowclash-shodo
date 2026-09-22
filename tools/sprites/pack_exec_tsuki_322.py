"""Executioner CHUDAN TSUKI — three real cells to replace the headless xstab2.

WHY THIS EXISTS: cell 54 (xstab2) is not a pose, it is a FRAGMENT — a torso and
two arms with no head and no legs, floating 81px off the ground (measured:
bodyH 95 where every other cell is ~177, footGap 81 where every other cell is
<=12). Both the Drive Stab (Fwd+Heavy) AND the neutral special were drawing it,
and the special held it for THREE of its five exposures. Owner saw it:
"the frame of the special attack, like his head disappeared."

The fix is at the cell, not at either caller — one bad cell, two broken moves.

No generation spend: A_09 / A_14 / A_15 are already-approved frames from the
sheets the owner signed off on, and they happen to be a textbook tsuki —
blade level and pointed forward through all three, arm extending.

ONE UNIFORM SCALE for the sequence (never per-cell MATCH_HEIGHT — that scales a
compact frame against an extended one and boils the body size). Anchored on the
most upright frame vs the 177px the other new-sheet cells were packed at.
"""
import json, pathlib, numpy as np
from PIL import Image

REPO = pathlib.Path('/Users/anthonyguy/SHADOWCLASH-RECOVERED')
NF = pathlib.Path('/private/tmp/claude-501/-Users-anthonyguy-SHADOWCLASH-RECOVERED/'
                  'b474c4d4-46d9-4af5-8aa7-777bd55635a8/scratchpad/newframes')
OUT = pathlib.Path(__file__).parent
SRC = ['A_14', 'A_15', 'A_09']   # load (blade back, level) -> full extension -> zanshin
KEYS = ['xtsuki1', 'xtsuki2', 'xtsuki3']
BODY_H = 177          # what xlight1..4 and idle_chudan were packed at
ANCHOR = 'A_09'       # most upright of the three


# NO de-white pass here, and that is a MEASURED decision, not an oversight.
# Kael's parry cells needed one because 1,392px of white were trapped between his
# arm and his torso. These three were checked the same way — every near-white
# pixel (120/203/224 per frame) was painted red and looked at, and 100% of it sits
# ON THE BLADE'S HIGHLIGHT. Running the Kael fix here moth-eats the sword: it
# punched 125px of holes down A_09's blade and nothing else. Check before keying.


def bbox(im):
    ys, xs = np.nonzero(np.array(im.convert('RGBA'))[..., 3] > 16)
    return xs.min(), ys.min(), xs.max(), ys.max()


def main():
    d = json.loads((REPO / 'web/assets/sprites/executioner.json').read_text())
    fw, fh, cols, footY = d['frameW'], d['frameH'], d['cols'], d['footY']
    sheet = Image.open(REPO / 'web/assets/sprites/executioner.png').convert('RGBA')
    assert sheet.width == cols * fw, (sheet.width, cols * fw)

    cleaned = {n: Image.open(NF / f'{n}.png').convert('RGBA') for n in SRC}

    x0, y0, x1, y1 = bbox(cleaned[ANCHOR])
    scale = BODY_H / (y1 - y0 + 1)
    print(f'  uniform scale {scale:.4f} (anchor {ANCHOR} {y1-y0+1}px -> {BODY_H})')

    new = Image.new('RGBA', ((cols + len(SRC)) * fw, fh), (0, 0, 0, 0))
    new.paste(sheet, (0, 0))
    for i, n in enumerate(SRC):
        im = cleaned[n]
        im = im.resize((max(1, round(im.width * scale)), max(1, round(im.height * scale))),
                       Image.LANCZOS)
        bx0, by0, bx1, by1 = bbox(im)
        cx = (cols + i) * fw + fw // 2 - (bx0 + bx1) // 2   # body centred in its cell
        cy = footY - by1                                     # soles ON the floor line
        new.alpha_composite(im, (cx, cy))
        print(f'  cell {cols+i} <- {n}  h={by1-by0+1}')

    new.save(REPO / 'web/assets/sprites/executioner.png')
    for i, k in enumerate(KEYS):
        d['frames'][k] = cols + i
    d['cols'] = cols + len(SRC)
    (REPO / 'web/assets/sprites/executioner.json').write_text(json.dumps(d, indent=2) + '\n')
    print(f'  cols {cols} -> {d["cols"]}')


if __name__ == '__main__':
    main()
