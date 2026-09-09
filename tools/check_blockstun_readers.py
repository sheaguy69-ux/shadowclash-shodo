#!/usr/bin/env python3
"""Blockstun rides stunTimer (Sep 7 guard rework), so `stunTimer > 0` no longer means
"a hit landed". This is the runnable check for the three readers that were fixed on
2026-09-08: a GUARDED Shin wire must push the blocker AWAY (not reel her in), a clean
wire hit must still reel, and a held guard must stay BLOCKING through blockstun expiry
(no one-tick IDLE hole). Runs against :9101 through the project's own exporter.

    python3 tools/check_blockstun_readers.py

Stage 1 uses the exporter (Shin wire vs block / vs hit, both facings). Stage 2 drives the
live page over CDP: a held guard under a rapid Light string never reads IDLE and never eats
a clean hit; the Executioner's Iron Guard Reprisal fires from blockstun through the real
hitstop queue and still refuses from HIT stun.
"""
import asyncio
import json, subprocess, sys, tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent

def export(scenario, facing):
    out = Path(tempfile.mkdtemp(prefix=f'blockstun-{scenario}-{facing}-'))
    cmd = [sys.executable, str(HERE / 'export_footsies_frames.py'), '--fighter', '2', '--move', 'special',
           '--direction', 'forward', '--facing', str(facing), '--scenario', scenario, '--frames', '30', '--out', str(out)]
    r = subprocess.run(cmd, capture_output=True, text=True, cwd=HERE.parent)
    assert r.returncode == 0, r.stdout[-800:] + r.stderr[-800:]
    return json.load(open(out / 'frame_breakdown.json'))['frames']

failures = []
for facing in (1, -1):
    # Shin faces `facing`; the wire travels that way; "toward Shin" is -facing.
    fr = export('block', facing)
    contact = next((i for i, f in enumerate(fr) if f.get('contacts')), None)
    assert contact is not None, f'block facing {facing}: no contact'
    tail = fr[contact:contact + 12]
    outcomes = {c['outcome'] for f in tail for c in (f.get('contacts') or [])}
    if outcomes != {'BLOCK'}:
        failures.append(f'block facing {facing}: outcomes {outcomes}')
    vx = [f['defender']['velocity']['x'] for f in tail]
    if any(v * facing < -1 for v in vx):            # any velocity TOWARD Shin = reeled
        failures.append(f'block facing {facing}: blocker pulled toward Shin, vx={[round(v) for v in vx]}')
    states = {f['defender']['state'] for f in fr[contact:]}
    if states != {'BLOCKING'}:                        # the one-tick IDLE hole
        failures.append(f'block facing {facing}: guard dropped to {states - {"BLOCKING"}} while held')

    fr = export('hit', facing)
    contact = next((i for i, f in enumerate(fr) if f.get('contacts')), None)
    assert contact is not None, f'hit facing {facing}: no contact'
    f0 = fr[contact]
    if f0['defender']['state'] != 'STUNNED' or f0['defender']['velocity']['x'] * facing > -200:
        failures.append(f"hit facing {facing}: no reel — state {f0['defender']['state']} vx {f0['defender']['velocity']['x']:.0f}")


# ---- stage 2: held guard vs rapid string, reprisal in / out of blockstun --------------
sys.path.insert(0, str(HERE))
import websockets, watch_game as browser

STAGE2 = r"""
dismissTitle();
const fails=[], out={};
const key=(code,down)=>window.dispatchEvent(new KeyboardEvent(down?'keydown':'keyup',{code,bubbles:true}));
const dt=1/(60*COMBAT_TEMPO);
const step=()=>{hitstopRemaining=0;updateGame(dt);};   // exporter-style: no cinematic crawl
const setup=(p1,p2)=>{gameMode='2p';cpuMode=false;spectate=false;stagePick='bamboo';p1Pick=p1;p2Pick=p2;startNewGame();
  paused=false;roundIntroTimer=0;cutscene=null;hitstopRemaining=0;releaseAllKeys();
  Object.assign(player1,{x:450,y:GROUND_Y-player1.height,vx:0,vy:0,isGrounded:true,facing:1});
  Object.assign(player2,{x:505,y:GROUND_Y-player2.height,vx:0,vy:0,isGrounded:true,facing:-1});};
// A: Executioner holds guard (KeyM) under Shin's Light string — the one-tick IDLE hole
setup(2,0); key('KeyM',true); for(let n=0;n<20;n++)step();
const A={idle:0,stunned:0,blocks:0,clean:0,maxCombo:0}; let hp=player2.hp;
for(let t=0;t<420;t++){ if(t%6===0){key('KeyF',true);key('KeyF',false);} step();
  if(player2.state==='IDLE')A.idle++; if(player2.state==='STUNNED')A.stunned++;
  const d=hp-player2.hp; if(d>0){ if(d<1.5)A.blocks++; else A.clean++; } hp=player2.hp;
  A.maxCombo=Math.max(A.maxCombo,player2.comboHits||0); }
if(A.idle||A.stunned||A.clean||A.maxCombo>1||A.blocks<10)fails.push('held guard: '+JSON.stringify(A));
out.A=A;
// B: Executioner holds guard (KeyC); Kael Heavy (KeyO) into it; KeyG DURING blockstun,
//    through the real frame loop so the press rides the hitstop queue like a real one
setup(0,5); key('KeyC',true); for(let n=0;n<20;n++)step(); key('KeyO',true);key('KeyO',false);
let ts=performance.now(); lastTime=ts; const frame=()=>{ts+=1000/60; gameLoop(ts);};
const B={pressed:null,fired:null,stamBefore:0,stamAfter:null,second:null};
for(let t=0;t<200;t++){ frame(); const p=player1;
  if(B.pressed===null&&p.state==='BLOCKING'&&p.stunTimer>0){B.pressed=t;B.stamBefore=p.stamina;key('KeyG',true);key('KeyG',false);}
  if(B.pressed!==null&&B.fired===null&&p.reprisalAnim){B.fired=t;B.stamAfter=p.stamina;B.stun=p.stunTimer;B.boxes=p.hitboxes.length;}
  if(B.fired!==null&&t===B.fired+1&&B.second===null){const s0=p.stamina;key('KeyG',true);key('KeyG',false);frame();B.second=s0-p.stamina;} }
if(B.pressed===null)fails.push('reprisal: never in blockstun');
else if(B.fired===null)fails.push('reprisal: did not fire from blockstun');
else { if(B.stun!==0||!B.boxes)fails.push('reprisal: fired without clearing stun / spawning a box '+JSON.stringify(B));
  if(B.stamBefore-B.stamAfter<REPRISAL_COST-0.01)fails.push('reprisal: stamina not charged');
  if(B.second>=REPRISAL_COST-0.01)fails.push('reprisal: fired twice on one block'); }
out.B=B;
// C: negative control — from HIT stun the riposte must refuse
setup(0,5); for(let n=0;n<5;n++)step(); key('KeyO',true);key('KeyO',false);
let hit=false, rep=false;
for(let t=0;t<120;t++){ step(); if(!hit&&player1.state==='STUNNED'){hit=true;key('KeyG',true);key('KeyG',false);} if(hit&&player1.reprisalAnim)rep=true; }
if(!hit)fails.push('control: no clean hit'); if(rep)fails.push('control: reprisal fired from HIT stun');
out.fails=fails; return out;
"""

async def stage2():
    url = 'http://localhost:9101/index.html'
    browser.assert_serving_this_tree(url)
    with tempfile.TemporaryDirectory(prefix='blockstun-live-') as profile:
        proc, address = browser.launch(url, profile)
        try:
            async with websockets.connect(address, max_size=16 * 1024 * 1024) as ws:
                cdp = browser.CDP(ws)
                for _ in range(400):
                    if await cdp.js("return typeof SPRITES !== 'undefined' && NINJA_ROSTER.every(s=>SPRITES[s.name.toLowerCase()]?.ready)") is True:
                        break
                    await asyncio.sleep(.1)
                else:
                    raise RuntimeError('roster did not load')
                return await cdp.js(STAGE2)
        finally:
            proc.terminate(); proc.wait(timeout=10)

live = asyncio.run(stage2())
failures += live['fails']

if failures:
    print('FAIL\n  ' + '\n  '.join(failures)); sys.exit(1)
print(f"PASS: guarded wire pushes away and keeps the guard up both facings; clean wire still reels; "
      f"{live['A']['blocks']} rapid-string blocks with no hole; reprisal fires from blockstun (frame {live['B']['fired']}) and refuses from hitstun")
