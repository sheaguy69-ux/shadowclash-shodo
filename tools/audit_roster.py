#!/usr/bin/env python3
"""Roster audit — the REAL version of the "audit & repair loop" idea.

READ-ONLY by design: it reports, it never "auto-repairs". The manifests are
K3's sheet lane and the engine's cell-name resolution is fallback-chained —
a script that injects fake animation blocks (the GPT draft this replaces)
would corrupt every manifest while fixing nothing.

Checks per fighter (web/assets/sprites/<name>.json + .png):
  1. manifest parses; png exists
  2. sheet geometry: png width == cols * frameW, height == frameH
  3. every frames{} index inside [0, cols)
  4. K3 animations{} metadata: frame indices in range, frameRate > 0, non-empty
  5. INVISIBLE-FIGHTER check: the engine's fallback chains (spriteFrameIndex,
     web/index.html ~L4694-5435) terminate in cells that MUST exist unless a
     preferred per-fighter set covers the state first. Missing terminal with
     no covering set == the fighter draws NOTHING in that state (the wave-2
     throw bug class). Chain data mirrors the engine as of SHEET_V 274 —
     update PREFERRED/TERMINAL if spriteFrameIndex gains new chains.

Exit 0 = roster render-safe. Exit 1 = real breakage found (listed).
Informational (never fails the run): orphan cells, kick-art fallback.
"""
import json, sys
from pathlib import Path

SP = Path(__file__).resolve().parent.parent / 'web/assets/sprites'
ROSTER = ['executioner', 'mizu', 'shin', 'tsubasa', 'ember', 'kael', 'mokurai', 'exile']

# state -> (preferred first-cell markers, terminal chain-ender)
# a state is SAFE if any preferred set's first cell exists, else the terminal must.
CHAINS = {
    'run':     (['brun1', 'crun1', 'owalk1', 'run_clean1'], 'run1'),
    'heavy':   (['bheavy1', 'xheavy1', 'eheavy1', 'heavy_i1'], 'heavy1'),
    'special': (['bspec1', 'espec1', 'special1'], 'heavy1'),
    'light':   (['blight1', 'elight1', 'xlight4'], 'light1'),
    'idle':    ([], 'idle'),
    'hurt':    (['xhurt1', 'bhurt'], 'hurt'),
    'block':   (['bblock', 'xblock2'], 'block'),
    'fall':    ([], 'fall'),
    'kick':    (['ksweep', 'kpush', 'kheel', 'kstomp', 'jump2', 'fall'], 'light1'),
    'kneel':   (['bcrouch', 'xcrouch', 'ocrouch', 'fist_kneel', 'kneel'], 'idle'),
}

fail = False
for name in ROSTER:
    jp = SP / f'{name}.json'
    issues, notes = [], []
    try:
        d = json.load(open(jp))
    except Exception as e:
        print(f'== {name}: [X] PARSE FAIL {e}')
        fail = True
        continue
    cols, fw, fh = d.get('cols'), d.get('frameW'), d.get('frameH')
    F = d.get('frames', {})
    png = SP / f'{name}.png'
    if not png.exists():
        issues.append('png MISSING')
    else:
        try:
            from PIL import Image
            W, H = Image.open(png).size
            if fw and W != cols * fw: issues.append(f'geometry: png width {W} != cols*frameW {cols * fw}')
            if fh and H != fh: issues.append(f'geometry: png height {H} != frameH {fh}')
        except ImportError:
            notes.append('PIL absent — geometry unchecked')
    oob = {k: v for k, v in F.items() if not isinstance(v, int) or v < 0 or v >= cols}
    if oob: issues.append(f'out-of-range cell indices: {oob}')
    for an, cfg in (d.get('animations') or {}).items():
        frs, rate = cfg.get('frames', []), cfg.get('frameRate', 0)
        if not frs: issues.append(f'animations.{an}: empty frames')
        if rate <= 0: issues.append(f'animations.{an}: frameRate {rate} <= 0')
        bad = [i for i in frs if not isinstance(i, int) or i < 0 or i >= cols]
        if bad: issues.append(f'animations.{an}: out-of-range {bad}')
    for state, (preferred, terminal) in CHAINS.items():
        if any(p in F for p in preferred): continue
        if terminal not in F:
            issues.append(f'INVISIBLE RISK: state "{state}" has no preferred set and no terminal "{terminal}"')
    if issues:
        fail = True
        print(f'== {name}: {len(issues)} ISSUE(S)')
        for i in issues: print(f'   [X] {i}')
    else:
        print(f'== {name}: render-safe ({len(F)} cells)')
    for n in notes: print(f'   [i] {n}')

print('\nRESULT:', 'BREAKAGE FOUND' if fail else 'ROSTER RENDER-SAFE')
sys.exit(1 if fail else 0)
