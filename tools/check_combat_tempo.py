#!/usr/bin/env python3
"""Check the live simulation's pace, round clock, and all-nine attack commitments."""
import asyncio
import json
import os
import pathlib
import tempfile

import websockets
import watch_game as browser


async def main():
    url = os.environ.get('SHADOWCLASH_URL', 'http://localhost:9101/index.html')
    browser.assert_serving_this_tree(url)
    with tempfile.TemporaryDirectory(prefix='shodo-tempo-') as profile:
        proc, address = browser.launch(url, profile)
        try:
            async with websockets.connect(address, max_size=8 * 1024 * 1024) as ws:
                cdp = browser.CDP(ws)
                for _ in range(120):
                    if await cdp.js("return typeof SPRITES !== 'undefined' && NINJA_ROSTER.every(s => SPRITES[s.name.toLowerCase()]?.ready)") is True:
                        break
                    await asyncio.sleep(0.1)
                else:
                    raise RuntimeError('sprite sheets did not load')
                result = await cdp.js(r"""
                dismissTitle();
                const rows = [], failures = [], dt = 1 / 60;
                const near = (a,b,tol,msg) => { if (Math.abs(a-b)>tol) failures.push(msg+': '+a+' != '+b); };
                const key = (code,down) => window.dispatchEvent(new KeyboardEvent(down?'keydown':'keyup',{code,bubbles:true}));
                const reset = id => {
                    gameMode='2p';cpuMode=false;spectate=false;stagePick='bamboo';p1Pick=id;p2Pick=id===0?1:0;
                    startNewGame();roundIntroTimer=0;hitstopRemaining=0;paused=false;cutscene=null;
                    for(const k in keys) keys[k]=false;physKeys.clear();
                    player1.x=150;player2.x=canvas.width-100;
                    for(const p of [player1,player2]){p.y=GROUND_Y-p.height;p.isGrounded=true;}
                    return player1;
                };
                for(let id=0;id<9;id++){
                    let p=reset(id);const name=p.spec.name,x=p.x,a=animClock,t=roundTimer,phase=p.animPhase;
                    key('KeyD',true);for(let i=0;i<30;i++)updateGame(dt);key('KeyD',false);
                    const distance=p.x-x,sim=animClock-a,clock=t-roundTimer;
                    near(sim,0.6,0.0001,name+' simulation seconds');
                    near(clock,0.5,0.0001,name+' round seconds');
                    near(distance,350*(p.curSpeed/6)*0.6,0.1,name+' travel');
                    const cycles=(p.animPhase-phase)/runCells(SPRITES[name.toLowerCase()].frames).length;
                    if(cycles<.6||cycles>1.8*(p.spec.runAnimScale||1)+.01)failures.push(name+' excessive/missing stride cadence: '+cycles);
                    rows.push({name,kind:'run',distance,sim,clock,cycles});
                    for(const code of ['KeyF','KeyJ','KeyG','KeyH']){
                        p=reset(id);key(code,true);key(code,false);
                        const rec=p.recoveryTimer,anim=p.attackAnim?.dur||0;
                        if(!(rec>0))failures.push(name+' '+code+' never started');
                        let frames=0;
                        while(p.isAttackingState()&&frames<180){updateGame(dt);frames++;}
                        const elapsed=frames*dt;
                        near(elapsed,rec/1.2,dt*2,name+' '+code+' recovery pace');
                        if(p.isAttackingState())failures.push(name+' '+code+' stuck');
                        rows.push({name,kind:code,rec,anim,elapsed});
                    }
                }
                // A slow frame keeps the existing 100ms integration ceiling.
                reset(5);const before=animClock;updateGame(0.1);
                near(animClock-before,0.1,0.0001,'long-frame simulation cap');
                return {rows,failures};
                """)
                if not result or '__error' in result:
                    raise RuntimeError(result)
        finally:
            proc.kill()
            proc.wait(timeout=10)
    browser.assert_serving_this_tree(url, 'after the run')
    if os.environ.get('OUT'):
        pathlib.Path(os.environ['OUT']).write_text(json.dumps(result, indent=2))
    for row in result['rows']:
        if row['kind'] == 'run':
            print(f"{row['name']}: {row['distance']:.1f}px / {row['clock']:.3f}s on round clock; {row['sim']:.3f}s action")
    for failure in result['failures']:
        print('FAIL:', failure)
    assert not result['failures'], f"{len(result['failures'])} tempo failures"
    print('PASS: nine movement/clock cases, 36 attack recoveries, long-frame cap')


if __name__ == '__main__':
    asyncio.run(main())
