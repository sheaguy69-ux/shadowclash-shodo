#!/usr/bin/env python3
"""Verify the spin correction: aneu extended 16 cells, aspin back to 6."""
import pathlib, sys
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from watch_game import drive
REPO = pathlib.Path(__file__).resolve().parents[1]
OUT = REPO / 'media/audit/oni-spin-fix'
PROBE = r'''
const frame = () => new Promise(r => requestAnimationFrame(r));
gameMode = '2p'; cpuMode = false; attractMode = false;
if (!SPRITES['oni']) {
  const man = await (await fetch('assets/sprites/oni.json?v=' + SHEET_V)).json();
  await new Promise((res, rej) => { const i = new Image();
    i.onload = () => { man.img = i; man.ready = true; SPRITES['oni'] = man; res(); };
    i.onerror = rej; i.src = 'assets/sprites/oni.png?v=' + SHEET_V; });
}
p1Pick = 8; p2Pick = 0; stagePick = 'bamboo'; startNewGame(); roundIntroTimer = 0;
matchActive = true;
await frame(); await frame();
const p = player1, F = SPRITES['oni'].frames;
const R = {};
R.aneu = (() => { const a=[]; for(let i=1;F['aneu'+i]!==undefined;i++)a.push(F['aneu'+i]); return a; })();
R.aspin = (() => { const a=[]; for(let i=1;F['aspin'+i]!==undefined;i++)a.push(F['aspin'+i]); return a; })();
// trigger neutral air light and read its duration
p.isGrounded = false; p.state = STATE.IDLE; p.vy = -200; p.attackAir = false;
p.executeAttack(STATE.ATTACK_LIGHT);
R.attackDir = p.attackDir; R.attackAir = p.attackAir;
R.dur = p.attackAnim ? p.attackAnim.dur : null;
return JSON.stringify(R);
'''
def main():
    R = drive([{"wait": 3.2}, {"key": "Space"}, {"wait": 0.8}, {"eval": PROBE, "label": "ONI-SPIN-FIX"}], OUT, "ONI-SPIN-FIX")
    print('spin correction probe:')
    print(f'  aneu cells = {R.get("aneu")} (count {len(R.get("aneu") or [])})')
    print(f'  aspin cells = {R.get("aspin")} (count {len(R.get("aspin") or [])})')
    print(f'  air light attackDir={R.get("attackDir")} attackAir={R.get("attackAir")} dur={R.get("dur")}ms')
    return 0
if __name__ == '__main__':
    sys.exit(main())