"""Make a fighter's cell TALLER without moving anything already drawn in it.

  python3 tools/sprites/grow_frame.py executioner 410
  python3 tools/sprites/grow_frame.py tsubasa 332 --down

Owner recipe, rule 7: "Pose doesn't fit? GROW frameH/footY. Never shrink the body,
never cut the pose." Ember went 320/312 -> 377/369 this way. The Executioner's Sky
Cleave raises the odachi straight overhead and needs 402px in a 327px cell, so the
cell grows rather than the sword getting cropped.

Every cell is re-seated at the SAME distance above the floor line: footY moves by the
same delta as frameH, so a sprite's contact point with the ground is bit-for-bit where
it was and no existing animation shifts by a pixel. Only the empty headroom changes.

--down grows the other way: the new rows go BELOW the floor line and footY does NOT
move, so the headroom appears UNDER the boots instead of over the head. That is the
side a board needs when the FIGHTER HIMSELF reaches past his own standing foot line -
Crimson Talon Ascension beat 4 hangs his trailing leg 12px below it, measured, and
this sheet offered 8. Existing cells are still bit-for-bit where they were relative to
BOTH the top edge and footY, so nothing already drawn shifts either way.

frameW and the cell ORDER are untouched, so every index in the json stays valid.
"""
import json
import pathlib
import sys

from PIL import Image

REPO = pathlib.Path(__file__).resolve().parents[2]


def main():
    down = '--down' in sys.argv
    argv = [a for a in sys.argv if a != '--down']
    fighter, new_h = argv[1], int(argv[2])
    jf = REPO / f'web/assets/sprites/{fighter}.json'
    pf = REPO / f'web/assets/sprites/{fighter}.png'
    m = json.loads(jf.read_text())
    old_h, footY, fw, cols = m['frameH'], m['footY'], m['frameW'], m['cols']
    assert new_h > old_h, f'{new_h} is not taller than {old_h}'
    d = new_h - old_h

    sheet = Image.open(pf).convert('RGBA')
    assert sheet.size == (cols * fw, old_h), f'sheet {sheet.size} != {(cols * fw, old_h)}'
    out = Image.new('RGBA', (cols * fw, new_h), (0, 0, 0, 0))
    out.paste(sheet, (0, 0 if down else d))   # the floor never moves either way
    out.save(pf)

    new_foot = footY if down else footY + d
    m['frameH'], m['footY'] = new_h, new_foot
    jf.write_text(json.dumps(m, indent=2) + '\n')
    print(f'  {fighter}: frameH {old_h} -> {new_h}, footY {footY} -> {new_foot} '
          f'({cols} cells re-seated, floor line unchanged, '
          f'{new_h - new_foot} px below it was {old_h - footY})')


if __name__ == '__main__':
    main()
