#!/usr/bin/env python3
"""Verify Oni's new 10-frame run cycle is live."""
import pathlib, sys
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from watch_game import drive
REPO = pathlib.Path(__file__).resolve().parents[1]
OUT = REPO / 'media/audit/oni-run10'
PROBE = r'''
const frame = () => new Promise(r => requestAnimationFrame(r));
gameMode = '2p'; cpuMode = false; attractMode = false;
p1Pick = 8; p2Pick = 0; stagePick = 'bamboo'; startNewGame(); roundIntroTimer = 0;
matchActive = true;
await frame(); await frame();
const F = SPRITES['oni'].frames;
const R = {};
const rc = runCells(F);
R.runCells = rc;
R.runCellCount = rc.length;
R.runUnique = new Set(rc).size;
R.runAnimScale = NINJA_ROSTER[8].runAnimScale;
// the run frame resolver cycles through them
const p = player1; p.state = STATE.RUN; p.isGrounded = true;
const seen = [];
for (let s = 0; s < 12; s++) { p.animPhase = s; seen.push(spriteFrameIndex(p, F)); }
R.sampled = [...new Set(seen)];
return JSON.stringify(R);
'''
def main():
    R = drive([{"wait": 3.2}, {"key": "Space"}, {"wait": 0.8}, {"eval": PROBE, "label": "ONI-RUN10"}], OUT, "ONI-RUN10")
    print('Oni run cycle probe:')
    print(f'  runCells length = {R.get("runCellCount")} (unique {R.get("runUnique")})')
    print(f'  runCells = {R.get("runCells")}')
    print(f'  runAnimScale = {R.get("runAnimScale")}')
    print(f'  sampled distinct cells = {R.get("sampled")}')
    return 0
if __name__ == '__main__':
    sys.exit(main())