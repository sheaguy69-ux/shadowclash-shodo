#!/usr/bin/env python3
"""Verify the 6 new Oni move boards resolve to their own cells."""
import pathlib, sys, json
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from watch_game import drive
REPO = pathlib.Path(__file__).resolve().parents[1]
OUT = REPO / 'media/audit/oni-moves6'
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
const reset = () => { p.hp = 100; p.stamina = 100; p.chakra = 100; p.stunTimer = 0;
  p.state = STATE.IDLE; p.isGrounded = true; p.vx = 0; p.vy = 0; p.rollTimer = 0;
  p.recoveryTimer = 0; p.recoveryTotal = 0; p.dashTimer = 0; p.blockPushTimer = 0;
  p.wallJumpLock = 0; p.flooredT = 0; p.grabbedBy = null; p.throwTimer = 0;
  p.attackAnim = null; p.kickKind = null; p.attackHasConnected = false;
  p.chainComboTier = 0; p.connectTime = -1e9; p.windedTimer = 0;
  p.attackAir = false; p.attackDir = null; p.airUpAnim = false; p.upAtkAnim = false;
  p.dashAtkAnim = false; p.spinAnim = false; p.moveArt = null; p.slamPhase = 0; p.slamRecover = 0;
  p.stringStep = 0; p.attackT = 0;
  if (p.clearMoveArt) p.clearMoveArt();
  for (const k in keys) keys[k] = false; };
const across = () => { const t0 = animClock, out = [];
  for (let s = 0; s <= 12; s++) { animClock = t0 + s * 0.04; out.push(spriteFrameIndex(p, F)); }
  animClock = t0; return [...new Set(out)]; };

// manifest keys
R.manifest = {
  aback: [F.aback1, F.aback2, F.aback3, F.aback4, F.aback5, F.aback6, F.aback7, F.aback8],
  dashatk: [F.dashatk1, F.dashatk2, F.dashatk3, F.dashatk4, F.dashatk5, F.dashatk6, F.dashatk7, F.dashatk8],
  hdown: [F.hdown1, F.hdown2, F.hdown3, F.hdown4, F.hdown5, F.hdown6, F.hdown7, F.hdown8, F.hdown9, F.hdown10],
  sdown: [F.sdown1, F.sdown2, F.sdown3, F.sdown4, F.sdown5, F.sdown6, F.sdown7, F.sdown8, F.sdown9, F.sdown10],
  aspin: (() => { const a=[]; for(let i=1;F['aspin'+i]!==undefined;i++)a.push(F['aspin'+i]); return a; })(),
  airkick: [F.airkick1, F.airkick2, F.airkick3, F.airkick4, F.airkick5, F.airkick6],
};

// draw resolution: air back light (aback)
reset(); p.isGrounded = false; p.state = STATE.ATTACK_LIGHT; p.attackAir = true; p.attackDir = 'back';
p.attackAnim = { start: animClock*1000, dur: 396 };
R.abackDraw = across();

// dash attack (dashatk)
reset(); p.state = STATE.ATTACK_LIGHT; p.dashAtkAnim = true; p.dashTimer = 0.1;
p.attackAnim = { start: animClock*1000, dur: 300 };
R.dashatkDraw = across();

// air down heavy (hdown)
reset(); p.isGrounded = false; p.state = STATE.ATTACK_HEAVY; p.attackAir = true; p.attackDir = 'down';
p.attackAnim = { start: animClock*1000, dur: 800 };
R.hdownDraw = across();

// special air down (sdown)
reset(); p.isGrounded = false; p.state = STATE.ATTACK_SPECIAL; p.attackAir = true; p.attackDir = 'down';
p.attackAnim = { start: animClock*1000, dur: 700 };
R.sdownDraw = across();

// air spin (aspin) — neutral air special
reset(); p.isGrounded = false; p.state = STATE.ATTACK_SPECIAL; p.spinAnim = true;
p.attackAnim = { start: animClock*1000, dur: 560 };
R.aspinDraw = across();

// air up high kick (airkick)
reset(); p.isGrounded = false; p.state = STATE.ATTACK_LIGHT; p.airUpAnim = true;
p.attackAnim = { start: animClock*1000, dur: 396 };
R.airkickDraw = across();

R.inv = (() => { const o = {}; for (const k in F) (o[F[k]] = o[F[k]] || []).push(k); return o; })();
return JSON.stringify(R);
'''
def main():
    R = drive([{"wait": 3.2}, {"key": "Space"}, {"wait": 0.8}, {"eval": PROBE, "label": "ONI-MOVES6"}], OUT, "ONI-MOVES6")
    inv = {int(k): v for k, v in (R.get('inv') or {}).items()}
    def nm(c): return ','.join(sorted(inv.get(c, ['?'])))
    fails = []
    def ok(cond, msg):
        print(f"  {'ok  ' if cond else 'FAIL'}  {msg}")
        if not cond: fails.append(msg)
    print('\nONI 6 MOVE BOARDS\n')
    M = R.get('manifest', {})
    ok(M.get('aback') == [307,308,309,310,311,312,313,314], f'aback1-8 -> 307-314 (got {M.get("aback")})')
    ok(M.get('dashatk') == [315,316,317,318,319,320,321,322], f'dashatk1-8 -> 315-322 (got {M.get("dashatk")})')
    ok(M.get('hdown') == [323,324,325,326,327,328,329,330,None,None], f'hdown1-8 -> 323-330, 9/10 gone (got {M.get("hdown")})')
    ok(M.get('sdown') == [331,332,333,334,335,336,337,338,339,340], f'sdown1-10 -> 331-340 (got {M.get("sdown")})')
    ok(M.get('aspin') == [147,148,149,150,151,152,341,342,343,344,345,346,347,348], f'aspin 14 cells = 147-152 + 341-348 (got {M.get("aspin")})')
    ok(M.get('airkick') == [349,350,351,352,353,354], f'airkick1-6 -> 349-354 (got {M.get("airkick")})')
    print()
    # draw checks: the drawn cells must be inside each move's OWN range
    def within(cells, lo, hi): return all(c is not None and lo <= c <= hi for c in cells)
    ab = R.get('abackDraw') or [];
    ok(len(ab) >= 3 and within(ab, 307, 314), f'air back light draws aback (307-314): {[nm(c) for c in ab][:4]}')
    dk = R.get('dashatkDraw') or [];
    ok(len(dk) >= 3 and within(dk, 315, 322), f'dash attack draws dashatk (315-322): {[nm(c) for c in dk][:4]}')
    hd = R.get('hdownDraw') or [];
    ok(len(hd) >= 3 and within(hd, 323, 330), f'air down heavy draws hdown (323-330): {[nm(c) for c in hd][:4]}')
    sd = R.get('sdownDraw') or [];
    ok(len(sd) >= 3 and within(sd, 331, 340), f'special down draws sdown (331-340): {[nm(c) for c in sd][:4]}')
    sp = R.get('aspinDraw') or [];
    ok(len(sp) >= 4 and within(sp, 147, 348), f'air spin draws 147-348 (extended): {[nm(c) for c in sp][:5]}')
    ak = R.get('airkickDraw') or [];
    ok(len(ak) >= 3 and within(ak, 349, 354), f'air up light draws airkick (349-354): {[nm(c) for c in ak][:4]}')
    if fails:
        print(f'\n{len(fails)} FAILED'); return 1
    print('\nall good'); return 0
if __name__ == '__main__':
    sys.exit(main())