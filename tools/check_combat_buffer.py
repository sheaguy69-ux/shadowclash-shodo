#!/usr/bin/env python3
"""Exercise early/released combat presses on the live :9101 engine."""
import asyncio
import json
import os
import tempfile
from pathlib import Path

import websockets
import watch_game as browser


async def main():
    url = os.environ.get('SHADOWCLASH_URL', 'http://localhost:9101/index.html')
    browser.assert_serving_this_tree(url)
    with tempfile.TemporaryDirectory(prefix='combat-buffer-') as profile:
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
                result = await cdp.js(r"""
                dismissTitle(); paused=true;
                const failures=[], rows=[];
                const clear=()=>{for(const k in keys)keys[k]=false;physKeys.clear();};
                const reset=(id)=>{
                    gameMode='2p';cpuMode=false;spectate=false;stagePick='bamboo';p1Pick=id;p2Pick=id===0?1:0;
                    startNewGame();roundIntroTimer=0;hitstopRemaining=0;cutscene=null;paused=true;clear();
                    player1.x=180;player2.x=canvas.width-100;
                    for(const p of [player1,player2]){p.y=GROUND_Y-p.height;p.isGrounded=true;p.vy=0;}
                    return player1;
                };
                const hold=(codes)=>{clear();for(const c of codes){keys[c]=true;physKeys.add(c);}};
                const press=code=>{window.dispatchEvent(new KeyboardEvent('keydown',{code,bubbles:true}));
                    window.dispatchEvent(new KeyboardEvent('keyup',{code,bubbles:true}));};
                // Use the real key funnel while freezing only autonomous rAF between probes.
                const fire=code=>{paused=false;press(code);paused=true;};
                const tick=(p,dt)=>{animClock+=dt;p.update(dt,player2);};
                const signature=p=>({state:p.state,dir:p.attackDir,kick:p.kickKind,art:p.moveArt,
                    cell:spriteFrameIndex(p,SPRITES[p.spec.name.toLowerCase()].frames),
                    boxes:p.hitboxes.map(h=>[h.ox,h.oy,h.w,h.h,!!h.low,!!h.launch,!!h.spike]),
                    tsuki:!!p.tsukiAnim,up:!!p.upAtkAnim,airUp:!!p.airUpAnim});
                const directions=[[],['KeyA'],['KeyD'],['KeyS'],['KeyW'],['KeyA','KeyS'],['KeyD','KeyS'],['KeyA','KeyW'],['KeyD','KeyW']];
                for(let id=0;id<NINJA_ROSTER.length;id++){
                    const name=NINJA_ROSTER[id].name;
                    let p=reset(id);fire('KeyG');const first=p.attackAnim;fire('KeyJ');
                    for(let n=0;n<100;n++)tick(p,.01);
                    const expired=!p.bufferedAttack && (!p.attackAnim||p.attackAnim===first);
                    if(!expired)failures.push(name+': expired press fired or remains queued');
                    for(const code of ['KeyF','KeyJ','KeyG','KeyH'])for(const dirs of directions){
                        p=reset(id);hold(dirs);fire(code);const expected=signature(p);
                        if(!p.attackAnim){failures.push(name+' '+code+' did not start reference');continue;}
                        p=reset(id);p.rollRecover=.07;p.state=STATE.CROUCH;hold(dirs);fire(code);clear();
                        let n=0;while(!p.attackAnim&&n++<12)tick(p,.01);
                        const actual=signature(p),ok=!!p.attackAnim&&JSON.stringify(actual)===JSON.stringify(expected);
                        if(!ok)failures.push(name+' '+code+' '+dirs.join('+')+': queued input differs '+JSON.stringify({expected,actual}));
                    }
                    for(const gate of ['stunTimer','rollRecover','sayaLock'])for(const duration of [.06,.35]){
                        p=reset(id);p[gate]=duration;if(gate==='stunTimer')p.state=STATE.STUNNED;
                        fire('KeyJ');let started=false;
                        for(let n=0;n<60;n++){tick(p,.01);if(p.attackAnim)started=true;}
                        if(started!==(duration<.133))failures.push(name+' '+gate+' '+duration+': wrong expiry/start');
                    }
                    rows.push({name,directional:36,expiry:expired,recoveryGates:6});
                }
                let p=reset(0);fire('KeyH');const anim=p.attackAnim,star=p.tsukiAnim;fire('KeyJ');
                if(!star||p.tsukiAnim!==star||p.attackAnim!==anim)failures.push('buffered press changed active thrust');
                return {rows,failures};
                """)
                if not result or '__error' in result:
                    raise RuntimeError(result)
        finally:
            proc.terminate()
            proc.wait(timeout=10)
    out=Path(os.environ.get('OUT','media/combat-buffer-20260906/checks.json'))
    out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({'fighters':len(result['rows']),'failures':len(result['failures']),'first':result['failures'][:5]},indent=2))
    assert not result['failures'], str(out)
    print('PASS: 324 released-direction presses, 54 recovery gates, nine expirations, thrust continuity')


if __name__=='__main__':
    asyncio.run(main())
