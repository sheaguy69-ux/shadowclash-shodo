#!/usr/bin/env python3
"""Refuse a commit that guts a fighter's sprite manifest.

    python3 tools/check_sheets_whole.py            # check the STAGED sheets
    python3 tools/check_sheets_whole.py --worktree # check the files on disk

Four times in one day a sheet went from whole to nearly empty and it was committed:
mizu 204 keys -> 0, executioner 335 -> 0, ember 284 -> 84, shin 273 -> 43, tsubasa
318 -> 44. A fighter with no keys draws NOTHING — the roster loads, the character
is selectable, and then there is no picture. Every one of those was a purge or an
orphan strip re-running against a manifest another lane had already rewritten: each
process read before the other wrote, and the loser's keys were gone without an error.

⛔ THIS IS NOT A STYLE RULE, IT IS A CRASH GUARD, so the threshold is deliberately
loose. A real strip removes a handful of dead keys. Losing THIRTY PERCENT of a
fighter's manifest in one commit has never once been intentional here. Legitimate
big deletions still ship — with --allow-shrink, which is the point: it makes the
person deleting say out loud that they meant it.

It also refuses a manifest that no longer matches its own png, because the two are
written separately and a half-applied pack points every key after the break at the
wrong picture — which looks like corrupted art, not like a bad commit.
"""
import argparse, json, subprocess, sys, pathlib

# ⛔ THE REPO IS THE ONE BEING COMMITTED, NOT THE ONE THIS FILE SITS IN. core.hooksPath
# here is an ABSOLUTE path into SHADOWCLASH-RECOVERED, so every worktree runs the hook
# out of that tree — and a check that resolved the repo from __file__ would grade
# RECOVERED's sheets no matter which tree was actually committing. Ask git instead: the
# hook runs with the committing worktree as cwd.
REPO = pathlib.Path(subprocess.run(['git', 'rev-parse', '--show-toplevel'],
                                   capture_output=True, text=True).stdout.strip()
                    or pathlib.Path(__file__).resolve().parents[1])
SHEETS = REPO / 'web/assets/sprites'
FLOOR = 0.70          # a commit may not cut a manifest below 70% of its committed size
MIN_KEYS = 40         # ...and never below this, whatever the ratio says

# Key names the owner ordered destroyed; a commit bringing one back is refused.
# Underscore entries are prose, not fighters.
_pk = SHEETS / 'PURGED-KEYS.json'
PURGED = {k: v for k, v in (json.loads(_pk.read_text()).items() if _pk.exists() else [])
          if not k.startswith('_')}


def head_manifest(name):
    r = subprocess.run(['git', '-C', str(REPO), 'show', f'HEAD:web/assets/sprites/{name}.json'],
                       capture_output=True, text=True)
    return json.loads(r.stdout) if r.returncode == 0 else None


def staged_manifest(name):
    r = subprocess.run(['git', '-C', str(REPO), 'show', f':web/assets/sprites/{name}.json'],
                       capture_output=True, text=True)
    return json.loads(r.stdout) if r.returncode == 0 else None


def touched_by_this_commit():
    """The sheets THIS commit actually changes.

    ⛔ THE INDEX IS NOT THE DIFF. staged_manifest() reads `git show :path`, which returns a
    blob for EVERY tracked file whether or not the commit touches it — so `new is None` never
    fires and the "not staged in this commit; not our business" test below is dead. The guard
    then grades all nine sheets on every commit, which means ONE lane's broken fighter blocks
    EVERY OTHER LANE from committing anything at all. That has now happened twice: four
    fighters at 0 keys mid-purge, and later executioner alone, each time blocking commits that
    were REPAIRING a fighter. A crash guard that blocks the repair is worse than no guard.
    """
    r = subprocess.run(['git', '-C', str(REPO), 'diff', '--cached', '--name-only'],
                       capture_output=True, text=True)
    return {pathlib.Path(f).stem for f in r.stdout.split('\n')
            if f.startswith('web/assets/sprites/') and f.endswith(('.json', '.png'))}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--worktree', action='store_true', help='check the files on disk, not the index')
    ap.add_argument('--allow-shrink', action='store_true', help='I meant to delete this much')
    a = ap.parse_args()
    touched = set() if a.worktree else touched_by_this_commit()

    # PURGED-KEYS.json lives beside the manifests but is not one — it is the list of
    # names the owner ordered destroyed. Glob it in and the loop reads it as a fighter.
    names = sorted(p.stem for p in SHEETS.glob('*.json') if p.name != 'PURGED-KEYS.json')
    if not a.worktree:
        # ⛔ GRADE ONLY WHAT THIS COMMIT TOUCHES. `git show :path` returns the index copy
        # of every TRACKED file, not just the staged ones, so the loop was grading all nine
        # sheets on every commit — and one fighter left broken by another lane then refused
        # every commit in the repo, including the commits trying to fix him. Measured:
        # executioner sat at 0 keys and blocked a two-file change to a python script.
        touched = subprocess.run(['git', '-C', str(REPO), 'diff', '--cached', '--name-only'],
                                 capture_output=True, text=True).stdout.split()
        staged = {pathlib.Path(t).stem for t in touched
                  if t.startswith('web/assets/sprites/') and t.endswith(('.json', '.png'))}
        names = [n for n in names if n in staged]
    bad = []
    for n in names:
        new = json.loads((SHEETS / f'{n}.json').read_text()) if a.worktree else staged_manifest(n)
        if new is None or (not a.worktree and n not in touched):
            continue                      # not staged in this commit; not our business
        old = head_manifest(n)
        k = len(new['frames'])

        # 1. the manifest must still describe its own sheet
        from PIL import Image
        Image.MAX_IMAGE_PIXELS = None
        png = SHEETS / f'{n}.png'
        if png.exists():
            cols = Image.open(png).size[0] // new['frameW']
            if cols != new['cols']:
                bad.append(f'{n}: manifest says {new["cols"]} cols, the png has {cols} — '
                           f'half-applied pack, every key past the break draws the wrong cell')
            elif new['frames'] and max(new['frames'].values()) >= cols:
                bad.append(f'{n}: a key points at cell {max(new["frames"].values())} '
                           f'but the sheet only has {cols}')
            else:
                # ⛔ AND THE CELLS MUST NOT BE BLANK. Matching column counts are not enough,
                # which is the expensive lesson: a purge BLANKED cells in place instead of
                # removing columns, so a manifest and a png agreed on `cols`, every index was
                # in range, and 193 of Ember's 277 referenced cells were empty. The guard
                # passed it. He loaded, he was selectable, and he was INVISIBLE. All nine
                # sheets carry zero empty referenced cells today, so the rule can be absolute.
                import numpy as np
                arr = np.array(Image.open(png).convert('RGBA'))
                w = new['frameW']
                blank = [i for i in sorted(set(new['frames'].values()))
                         if not (arr[:, i * w:(i + 1) * w, 3] > 64).any()]
                if blank:
                    where = ', '.join(k for k, v in new['frames'].items() if v in set(blank[:4]))
                    bad.append(f'{n}: {len(blank)} referenced cells are EMPTY — those moves draw '
                               f'nothing at all (e.g. {where})')

        # ⛔ 1b. AND A PURGED KEY MUST NEVER COME BACK. Deleting the old frames is not
        # enough on its own. A lane that believes a sheet is gutted restores it wholesale
        # from an older commit: the manifest matches its png, no index is out of range, no
        # key count drops, and every rule above passes — the old art is simply back. That
        # is exactly what happened to Kael at 20:51 on Aug 22, while the owner was playing
        # and telling us for the third time to delete it. The shrink rule cannot catch this
        # because a restore GROWS the manifest.
        purged = PURGED.get(n)
        if purged:
            back = sorted(set(purged) & set(new['frames']))
            if back:
                bad.append(f'{n}: {len(back)} PURGED key(s) are back — the owner ordered '
                           f'these deleted (e.g. {", ".join(back[:6])}). You are restoring '
                           f'an old sheet over the current one.')

        # 2. and it must not have been gutted
        if k < MIN_KEYS:
            bad.append(f'{n}: {k} keys — a fighter this empty draws nothing')
        elif old and len(old['frames']) and k < len(old['frames']) * FLOOR:
            bad.append(f'{n}: {len(old["frames"])} keys -> {k} '
                       f'({100 * k / len(old["frames"]):.0f}% kept). Losing this much has never '
                       f'been intentional in this repo.')

    if bad and not a.allow_shrink:
        print('\n  ⛔ SPRITE SHEET GUARD — commit refused\n')
        for b in bad:
            print(f'     {b}')
        print('\n     Another lane almost certainly rewrote the manifest between your read and'
              '\n     your write. Re-read the sheet and re-apply, or if you truly meant it:'
              '\n         python3 tools/check_sheets_whole.py --allow-shrink\n')
        return 1
    if bad:
        print('  sheet guard OVERRIDDEN with --allow-shrink:')
        for b in bad:
            print(f'     {b}')
        return 0
    print(f'  sheet guard: {len(names)} sheets whole and consistent')
    return 0


if __name__ == '__main__':
    sys.exit(main())
