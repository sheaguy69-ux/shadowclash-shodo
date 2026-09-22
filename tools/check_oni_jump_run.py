#!/usr/bin/env python3
"""Verify Oni's jump height + run animation slowdown."""
import pathlib, sys
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from watch_game import drive
REPO = pathlib.Path(__file__).resolve().parents[1]
OUT = REPO / 'media/audit/oni-jump-run'
PROBE = r'''
const frame = () => new Promise(r => requestAnimationFrame(r));
gameMode = '2p'; cpuMode = false; attractMode = false;
p1Pick = 8; p2Pick = 7; stagePick = 'bamboo'; startNewGame(); roundIntroTimer = 0;
matchActive = true;
await frame(); await frame();
const R = {};
R.oni = { jumpScale: NINJA_ROSTER[8].jumpScale || 1, runAnimScale: NINJA_ROSTER[8].runAnimScale || 1, speed: NINJA_ROSTER[8].stats.speed };
R.exile = { jumpScale: NINJA_ROSTER[7].jumpScale || 1, speed: NINJA_ROSTER[7].stats.speed };
// measure jump vy: ground a fighter and call executeJump
function jumpVy(p) { p.isGrounded = true; p.jumpsLeft = 2; p.state = STATE.IDLE; p.vy = 0;
  p.executeJump(); const v = p.vy; p.isGrounded = true; p.vy = 0; p.jumpsLeft = 2; return v; }
R.oniVy = jumpVy(player1);
R.exileVy = jumpVy(player2);
R.gravity = GRAVITY;
R.oniJumpPx = Math.round(R.oniVy*R.oniVy / (2*GRAVITY));
R.exileJumpPx = Math.round(R.exileVy*R.exileVy / (2*GRAVITY));
return JSON.stringify(R);
'''
def main():
    R = drive([{"wait": 3.2}, {"key": "Space"}, {"wait": 0.8}, {"eval": PROBE, "label": "ONI-JUMP-RUN"}], OUT, "ONI-JUMP-RUN")
    print("Oni jump + run animation probe:")
    for k in ("oni","exile","oniVy","exileVy","gravity","oniJumpPx","exileJumpPx"):
        print(f"  {k} = {R.get(k)}")
    return 0
if __name__ == '__main__':
    sys.exit(main())