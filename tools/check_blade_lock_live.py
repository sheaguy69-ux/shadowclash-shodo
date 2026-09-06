#!/usr/bin/env python3
"""Exercise the shipped blade-lock picker, inputs and renderer on :9101."""
import asyncio
import base64
import json
import os
import tempfile
from pathlib import Path

import websockets
import watch_game as browser


async def main():
    url = 'http://localhost:9101/index.html'
    browser.assert_serving_this_tree(url)
    out = Path(os.environ.get('OUT', 'media/blade-lock-20260906/live'))
    out.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='blade-lock-check-') as profile:
        proc, addr = browser.launch(url, profile)
        try:
            async with websockets.connect(addr, max_size=60*1024*1024) as ws:
                c = browser.CDP(ws)
                for _ in range(600):
                    if await c.js("return typeof SPRITES!=='undefined'&&NINJA_ROSTER.every(p=>SPRITES[p.name.toLowerCase()]?.ready)"):
                        break
                    await asyncio.sleep(.1)
                else:
                    raise AssertionError('roster did not load')
                result = await c.js(r'''
                dismissTitle();gameMode='2p';spectate=false;cpuMode=false;stagePick='bamboo';
                p1Pick=0;p2Pick=5;startNewGame();roundIntroTimer=0;paused=true;cutscene=null;hitstopRemaining=0;
                for(const k in keys)keys[k]=false;physKeys.clear();
                window.lockCheck={failures:[],trace:[],pairs:[]};
                const fail=s=>lockCheck.failures.push(s),ids=[0,1,3,4,5,7,8];
                window.lockCheckSetup=(ai,bi,side=1)=>{
                    p1Pick=ai;p2Pick=bi;startNewGame();roundIntroTimer=0;paused=true;cutscene=null;hitstopRemaining=0;
                    const a=player1,b=player2;
                    for(const p of [a,b])Object.assign(p,{y:GROUND_Y-p.height,isGrounded:true,vx:0,vy:0,state:STATE.IDLE});
                    a.x=canvas.width/2-side*70-a.width/2;b.x=canvas.width/2+side*70-b.width/2;
                    a.facing=side;b.facing=-side;return [a,b];
                };
                window.lockCheckShot=(label,a,b)=>{
                    const s=document.createElement('canvas');s.width=440;s.height=280;const g=s.getContext('2d');
                    g.fillStyle='#e6e0d5';g.fillRect(0,0,s.width,s.height);
                    const center=(a.x+a.width/2+b.x+b.width/2)/2;
                    g.save();g.translate(s.width/2-center,s.height-22-GROUND_Y);
                    for(const p of [a,b]){
                        const m=SPRITES[p.spec.name.toLowerCase()];
                        if(!drawSprite(g,p))fail('invisible '+p.spec.name+' '+label);
                        lockCheck.trace.push({label,name:p.spec.name,cell:p.drawCell,facing:p.facing,x:p.x,state:p.state,lock:p.lockT});
                        if(!Object.keys(m.frames).some(k=>/^lock\d+$/.test(k)&&m.frames[k]===p.drawCell))fail('nonlock art '+p.spec.name+' '+label+' '+p.drawCell);
                    }
                    g.restore();g.fillStyle='#171717';g.font='12px sans-serif';g.fillText(label,6,16);return s;
                };
                const board=document.createElement('canvas');board.width=440*6;board.height=280*ids.length*2;
                const g=board.getContext('2d');let row=0;
                for(const ai of ids)for(const side of [1,-1]){
                    const [a,b]=lockCheckSetup(ai,ai===5?0:5,side);
                    enterBladeLock(a,b,ai===1);
                    const m=SPRITES[a.spec.name.toLowerCase()],F=m.frames;
                    const times=[.02,.12,.20,.30];
                    for(let k=0;k<4;k++){
                        a.lockT=b.lockT=LOCK_DUR-times[k];
                        const want=F['lock'+(k+1)];
                        if(spriteFrameIndex(a,F)!==want)fail('phase '+a.spec.name+' '+k);
                        g.drawImage(lockCheckShot(a.spec.name+' / '+side+' / phase '+(k+1),a,b),k*440,row*280);
                    }
                    a.lockMash=8;b.lockMash=0;resolveBladeLock(a,b);
                    g.drawImage(lockCheckShot(a.spec.name+' win',a,b),4*440,row*280);
                    const [loser,winner]=lockCheckSetup(ai,ai===5?0:5,side);enterBladeLock(loser,winner,ai===1);
                    loser.lockMash=0;winner.lockMash=8;resolveBladeLock(loser,winner);
                    g.drawImage(lockCheckShot(loser.spec.name+' lose',loser,winner),5*440,row*280);
                    row++;
                }
                const pairs=document.createElement('canvas');pairs.width=440*3;pairs.height=280*7;const pg=pairs.getContext('2d');let n=0;
                for(let i=0;i<ids.length;i++)for(let j=i+1;j<ids.length;j++){
                    const [a,b]=lockCheckSetup(ids[i],ids[j]);enterBladeLock(a,b,ids[i]===1||ids[j]===1);
                    a.lockT=b.lockT=LOCK_DUR-.22;
                    const label=a.spec.name+' / '+b.spec.name;pg.drawImage(lockCheckShot(label,a,b),n%3*440,Math.floor(n/3)*280);
                    lockCheck.pairs.push({label,separation:Math.abs(a.x+a.width/2-b.x-b.width/2)});n++;
                }
                for(const ai of ids)for(const wall of [-1,1]){
                    const [a,b]=lockCheckSetup(ai,ai===5?0:5);
                    a.x=wall<0?10:canvas.width-75;b.x=wall<0?40:canvas.width-40;
                    enterBladeLock(a,b,ai===1);
                    const sep=SPRITES[a.spec.name.toLowerCase()].lockReach+SPRITES[b.spec.name.toLowerCase()].lockReach;
                    if(Math.abs(Math.abs(a.x+a.width/2-b.x-b.width/2)-sep)>.01)fail('wall contact spacing '+ai);
                    const s=document.createElement('canvas');s.width=canvas.width+200;s.height=300;const cg=s.getContext('2d');
                    for(const t of [.02,.12,.20,.30,'win']){
                        if(t==='win'){a.lockMash=8;b.lockMash=0;resolveBladeLock(a,b);}else a.lockT=b.lockT=LOCK_DUR-t;
                        cg.clearRect(0,0,s.width,s.height);cg.save();cg.translate(100,280-GROUND_Y);
                        drawSprite(cg,a);drawSprite(cg,b);cg.restore();
                        const px=cg.getImageData(0,0,s.width,s.height).data;
                        let outside=0;for(let y=0;y<s.height;y++)for(let x=0;x<s.width;x++)
                            if((x<100||x>=100+canvas.width)&&px[(y*s.width+x)*4+3]>40)outside++;
                        if(outside)fail('clipped lock at wall '+a.spec.name+' '+wall+' '+t+' ('+outside+' pixels)');
                    }
                }
                return {board:board.toDataURL().split(',')[1],pairs:pairs.toDataURL().split(',')[1]};
                ''')
                assert result and '__error' not in result, result
                for key, data in result.items():
                    (out/(key+'.png')).write_bytes(base64.b64decode(data))
                # Consecutive real rAFs, not sampled pose substitution.
                result = await c.js(r'''
                const [a,b]=lockCheckSetup(0,5);gameMode='watch';a.executeAttack(STATE.ATTACK_HEAVY,'fwd');
                b.executeAttack(STATE.ATTACK_HEAVY,'fwd');
                for(const p of [a,b])p.spawnHitbox(150,120,1,1,0,{tier:STATE.ATTACK_HEAVY,canClash:true});
                clashCd=0;processWeaponClash(a,b);
                if(a.state!==STATE.BLADE_LOCK||b.state!==STATE.BLADE_LOCK)lockCheck.failures.push('active weapons did not enter lock');
                const origin=[a.x,b.x],seen=[],frames=[];
                const bar=document.createElement('canvas');bar.width=440*6;bar.height=280*4;const g=bar.getContext('2d');
                paused=false;
                await new Promise(resolve=>{let n=0;function tick(){
                    if(a.lockT>0){
                        if(Math.abs(a.x-origin[0])>.01||Math.abs(b.x-origin[1])>.01)lockCheck.failures.push('drift during live bind');
                        seen.push(spriteFrameIndex(a,SPRITES.executioner.frames));
                        if(n%3===0&&frames.length<24){const s=lockCheckShot('live '+n,a,b);g.drawImage(s,frames.length%6*440,Math.floor(frames.length/6)*280);frames.push(n);}
                    }
                    if(++n<100)requestAnimationFrame(tick);else resolve();
                }requestAnimationFrame(tick);});paused=true;
                if(new Set(seen).size<2)lockCheck.failures.push('no live phase progression');
                if(a.lockT>0||b.lockT>0)lockCheck.failures.push('lock never resolved');
                const cpuResults={p1:0,p2:0,tie:0};
                for(let i=0;i<32;i++){
                    const [p,q]=lockCheckSetup(0,5);gameMode='watch';enterBladeLock(p,q);
                    if(!p.isCpuDriven()||!q.isCpuDriven()||isP2Human())lockCheck.failures.push('wrong watch seats');
                    for(let t=0;t<80&&(p.lockT>0||q.lockT>0);t++)updateBladeLock(p,q,1/60);
                    cpuResults[p.lockOutcome==='win'?'p1':q.lockOutcome==='win'?'p2':'tie']++;
                }
                if(cpuResults.tie===32)lockCheck.failures.push('watch CPUs still always tie');
                return {...lockCheck,seen,cpuResults,png:bar.toDataURL().split(',')[1]};
                ''')
                assert result and '__error' not in result, result
                (out/'consecutive.png').write_bytes(base64.b64decode(result.pop('png')))
                (out/'checks.json').write_text(json.dumps(result, indent=2))
                print(json.dumps({'samples':len(result['trace']),'pairs':len(result['pairs']),'failures':result['failures']}))
                assert not result['failures'], result['failures']
        finally:
            proc.terminate()
            proc.wait(timeout=10)


if __name__ == '__main__':
    asyncio.run(main())
