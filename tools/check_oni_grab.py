#!/usr/bin/env python3
"""Verify Oni grab + adown + per-fighter grabbed reactions."""
import pathlib, sys, json
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from watch_game import drive
REPO = pathlib.Path(__file__).resolve().parents[1]
OUT = REPO / 'media/audit/oni-grab'
PROBE = r'''
const frame = () => new Promise(r => requestAnimationFrame(r));
gameMode = '2p'; cpuMode = false; attractMode = false;
async function load(key) {
  if (!SPRITES[key]) {
    const man = await (await fetch('assets/sprites/'+key+'.json?v='+SHEET_V)).json();
    await new Promise((res,rej)=>{const i=new Image();i.onload=()=>{man.img=i;man.ready=true;SPRITES[key]=man;res();};i.onerror=rej;i.src='assets/sprites/'+key+'.png?v='+SHEET_V;});
  } return SPRITES[key];
}
p1Pick = 8; p2Pick = 0; stagePick = 'bamboo'; startNewGame(); roundIntroTimer = 0;
matchActive = true;
await frame(); await frame();
const oni = await load('oni');
const R = {};
R.adown = [oni.frames.adown1,oni.frames.adown2,oni.frames.adown3,oni.frames.adown4,oni.frames.adown5,oni.frames.adown6,oni.frames.adown7,oni.frames.adown8];
R.grab = (()=>{const a=[];for(let i=1;oni.frames['grab'+i]!==undefined;i++)a.push(oni.frames['grab'+i]);return a;})();
// victims manifest
R.victims = {};
for (const key of ['tsubasa','shin','mokurai','mizu','kael','exile','executioner','ember']) {
  const m = await load(key);
  const a = []; for (let i=1; m.frames['grabbed'+i]!==undefined; i++) a.push(m.frames['grabbed'+i]);
  R.victims[key] = a;
}
// draw: Oni throw (THROWING)
const p = player1;
p.isGrounded = true; p.state = STATE.THROWING; p.throwTimer = THROW_TIME * 0.5; p.throwVictim = player2;
const gcells = []; for (let s=0;s<=8;s++){ p.throwTimer = THROW_TIME*(1-s/8); gcells.push(spriteFrameIndex(p, oni.frames)); }
R.grabDraw = [...new Set(gcells)];
// draw: victim THROWN (executioner = player2)
const q = player2; const ef = await load('executioner');
q.state = STATE.THROWN; q.grabbedBy = player1; player1.throwTimer = THROW_TIME * 0.5;
const vcells = []; for (let s=0;s<=8;s++){ player1.throwTimer = THROW_TIME*(1-s/8); vcells.push(spriteFrameIndex(q, ef.frames)); }
R.victimDraw = [...new Set(vcells)];
return JSON.stringify(R);
'''
def main():
    R = drive([{"wait": 3.2}, {"key": "Space"}, {"wait": 0.8}, {"eval": PROBE, "label": "ONI-GRAB"}], OUT, "ONI-GRAB")
    fails = []
    def ok(c, m):
        print(f"  {'ok  ' if c else 'FAIL'}  {m}")
        if not c: fails.append(m)
    print('\nONI GRAB + ADOWN + GRABBED\n')
    ok(R.get('adown') == [355,356,357,358,359,360,None,None], f'adown1-6 -> 355-360 (got {R.get("adown")})')
    ok(R.get('grab') == list(range(361,371)), f'grab1-10 -> 361-370 (got {R.get("grab")})')
    vexp = {'tsubasa':list(range(298,306)),'shin':list(range(261,269)),'mokurai':list(range(212,220)),'mizu':list(range(192,200)),'kael':list(range(209,217)),'exile':list(range(117,125)),'executioner':list(range(301,309)),'ember':list(range(224,232))}
    for k,exp in vexp.items():
        ok(R.get('victims',{}).get(k) == exp, f'{k} grabbed1-8 -> {exp[0]}-{exp[-1]} (got {R.get("victims",{}).get(k)})')
    gd = R.get('grabDraw') or []
    ok(len(gd) >= 4 and all(361 <= c <= 370 for c in gd), f'Oni THROWING draws grab1-10: {gd}')
    vd = R.get('victimDraw') or []
    ok(len(vd) >= 4 and all(301 <= c <= 308 for c in vd), f'victim THROWN draws grabbed1-8: {vd}')
    if fails:
        print(f'\n{len(fails)} FAILED'); return 1
    print('\nall good'); return 0
if __name__ == '__main__':
    sys.exit(main())