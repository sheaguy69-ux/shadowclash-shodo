"""Verify airborne reaction routing, native poses, landing and independent sheet bounds."""
import asyncio, base64, json, os, tempfile
from pathlib import Path
import websockets, watch_game as browser

async def main():
    browser.PORT=int(os.environ.get('SHADOWCLASH_DEBUG_PORT','9333'))
    url=os.environ.get('SHADOWCLASH_URL','http://localhost:9101/index.html')
    browser.assert_serving_this_tree(url)
    out=Path(os.environ.get('OUT','media/air-hurt-20260906/final'))
    out.mkdir(parents=True,exist_ok=True)
    ids=[int(x) for x in os.environ.get('FIGHTERS','0,1,2,3,4,5,6,7').split(',')]
    results=[]
    with tempfile.TemporaryDirectory(prefix='air-hurt-check-') as profile:
        proc,addr=browser.launch(url,profile)
        try:
            async with websockets.connect(addr,max_size=55*1024*1024) as ws:
                c=browser.CDP(ws)
                for _ in range(400):
                    if await c.js("return typeof SPRITES!=='undefined'&&NINJA_ROSTER.every(s=>SPRITES[s.name.toLowerCase()]?.ready)"):break
                    await asyncio.sleep(.1)
                else:raise AssertionError('Sprite sheets did not load')
                cache=await c.js(r'''
                    const names=['mizu','exile','mokurai'],cold={},warm=[],failures=[];
                    const bounds=n=>{const b=cellInk(SPRITES[n],180);return{x0:b.x0,y0:b.y0,x1:b.x1,y1:b.y1,reach:Array.from(b.reach||[])};};
                    for(const n of names){inkBoxCache.clear();cold[n]=bounds(n);}
                    for(const order of [names,[...names].reverse(),['exile','mizu','mokurai']]){
                        inkBoxCache.clear();const rows={};
                        for(const n of order){rows[n]=bounds(n);if(JSON.stringify(rows[n])!==JSON.stringify(cold[n]))failures.push(n+' bounds reused from another nameless sheet');}
                        warm.push({order,rows});
                    }
                    if(new Set(names.map(n=>JSON.stringify(cold[n]))).size!==3)failures.push('Fixture cells do not distinguish the three sheet bounds');
                    return{cell:180,names:names.map(n=>({sheet:n,manifestName:SPRITES[n].name??null,src:SPRITES[n].img.currentSrc||SPRITES[n].img.src})),cold,warm,failures};
                ''')
                assert cache and '__error' not in cache,cache
                (out/'bounds-cache.json').write_text(json.dumps(cache,indent=2)+'\n')
                for fighter in ids:
                    r=await c.js('const id='+str(fighter)+r''';
                        dismissTitle();gameMode='2p';spectate=false;cpuMode=false;stagePick='bamboo';p1Pick=id;p2Pick=id===0?1:0;
                        startNewGame();roundIntroTimer=0;paused=true;cutscene=null;hitstopRemaining=0;
                        for(const k in keys)keys[k]=false;physKeys.clear();
                        const p=player1,m=SPRITES[p.spec.name.toLowerCase()],F=m.frames,failures=[],matrix=[],held=[],ground=[];
                        const eight=F.airhurt8!==undefined,air=Array.from({length:eight?8:3},(_,i)=>F['airhurt'+(i+1)]);
                        const airExpected=vy=>air[eight
                            ? vy< -150?0:vy<0?1:vy<80?2:vy<140?3:vy<195?4:vy<250?5:vy<305?6:7
                            : vy< -80?0:vy>100?2:1];
                        // Authored directions were independently reviewed from full-size
                        // source art, including the rotation across Mokurai's tumble.
                        const rightAuthored=new Set(({kael:[18,161,162],mokurai:[180,181,183],exile:[183,345],oni:[649,650,651]})[p.spec.name.toLowerCase()]||[]);
                        const landingCell=({kael:18,exile:345})[p.spec.name.toLowerCase()];
                        if(air.some(x=>!Number.isInteger(x)||x<0||x>=m.cols))return{name:p.spec.name,failures:['missing/invalid airhurt family'],matrix};
                        const mode=alt=>Object.assign(p,{kageNui:alt&&id===2,sakate:alt&&id===3,hanbo:alt&&id===1,
                            cracked:alt&&id===6,gyakute:alt,chudan:alt,muki:alt?2:0});
                        const reset=()=>Object.assign(p,{x:canvas.width/2-p.width/2,y:GROUND_Y-p.height-70,isGrounded:false,
                            vx:0,vy:0,facing:1,state:STATE.STUNNED,stunTimer:.5,stunPeak:.5,grabbedBy:null,
                            attackAnim:null,wallDir:0,wallJumpLock:0,landSquash:0,hitSquashT:0,hitFlashT:0,
                            flooredT:0,tumbleT:0,slamPhase:0,slamRecover:0,moveArt:null,moveTrack:null,
                            rollTimer:0,dashTimer:0,f2Air:false,f2Low:false,clone:null,ghosts:[]});
                        const board=document.createElement('canvas');board.width=6*210;board.height=4*270;
                        const b=board.getContext('2d');b.fillStyle='#829da6';b.fillRect(0,0,board.width,board.height);
                        const drawCell=(g,x,y,label)=>{g.fillStyle='#132127';g.font='12px sans-serif';g.fillText(label,x+5,y+17);
                            g.save();g.translate(x+105-p.x-p.width/2,y+251-p.y-p.height);const transforms=[],render=drawShodoFrame;
                            drawShodoFrame=function(...args){if(args[0]===g&&args[1]===m.img)transforms.push({cell:Math.round(args[2]/m.frameW),a:g.getTransform().a});return render(...args);};
                            try{drawSprite(g,p);}finally{drawShodoFrame=render;g.restore();}
                            const body=transforms.filter(t=>t.cell===p.drawCell).at(-1);
                            if(!body)failures.push('character did not use shared Shodo renderer');
                            const visualFacing=body?Math.sign(body.a)*(rightAuthored.has(p.drawCell)?1:-1):null;
                            if(visualFacing!==p.facing)failures.push('air reaction faces backward: cell '+p.drawCell+' intended '+p.facing+' rendered '+visualFacing);
                            return{renderA:body?.a,visualFacing,mirror:p.drawMirror};
                        };
                        for(const alt of [false,true])for(const state of [STATE.STUNNED,STATE.THROWN])for(const facing of [-1,1])for(const [beat,vy] of [-250,0,220].entries()){
                            reset();mode(alt);Object.assign(p,{state,facing,vy,flooredT:.5,tumbleT:.3,tumbleT0:.6,
                                slamRecover:.1,moveArt:'gsfwd',f2Air:true,f2Low:true});
                            const cell=spriteFrameIndex(p,F),expected=airExpected(vy);
                            if(cell!==expected)failures.push('air reaction lost to stale floor/move/stance: '+[alt,state,facing,vy,cell]);
                            const fixture={alt,state,facing,vy,cell,expected};matrix.push(fixture);
                            // Stale floor flags are routing fixtures; render the actual reaction
                            // without an unrelated old attack transform or debug-only timers.
                            Object.assign(p,{flooredT:0,tumbleT:0,slamRecover:0,moveArt:null,f2Air:false,f2Low:false});
                            Object.assign(fixture,drawCell(b,(facing<0?0:3)*210+beat*210,(Number(alt)*2+Number(state===STATE.THROWN))*270,
                                (alt?'alt ':'base ')+state+' '+facing+' vy'+vy+' #'+cell));
                        }
                        if(id===1)for(let beat=1;beat<=8;beat++){
                            reset();mode(false);p.vy=[-240,-75,57,110,163,215,268,321][beat-1];
                            const cell=spriteFrameIndex(p,F),expected=air[beat-1];
                            if(cell!==expected)failures.push('Mizu eight-beat velocity selector missed '+beat);
                        }
                        for(const alt of [false,true])for(const facing of [-1,1]){
                            reset();mode(alt);Object.assign(p,{state:STATE.THROWN,facing,grabbedBy:player2,vy:0});
                            const row=[];for(let i=1;F['grabbed'+i]!==undefined;i++)row.push(F['grabbed'+i]);
                            for(const t of [.05,.45,.8]){player2.throwTimer=THROW_TIME*(1-t);const expected=row[attackCellIndex(t,row.length)],cell=spriteFrameIndex(p,F);
                                if(cell!==expected)failures.push('held throw replaced by air hurt');held.push({alt,facing,t,cell,expected});}
                            reset();mode(alt);Object.assign(p,{state:STATE.STUNNED,isGrounded:true,facing,vy:0,y:GROUND_Y-p.height});
                            const cell=spriteFrameIndex(p,F);if(air.includes(cell))failures.push('grounded hit uses airborne art');ground.push({alt,facing,cell});
                        }
                        // Real incoming hit while airborne: use takeDamage, preserve its actual
                        // hitstop/launch/stun clocks, and capture every rAF through landing.
                        reset();mode(false);player2.throwTimer=0;player2.x=170;player2.facing=1;
                        p.x=canvas.width/2-p.width/2;p.y=GROUND_Y-p.height-65;p.vy=80;p.facing=-1;
                        p.state=STATE.JUMP;p.stunTimer=0;p.stunPeak=0;p.hp=p.maxHp;
                        const hp=p.hp;p.takeDamage(18,player2,{pushback:80,tier:STATE.ATTACK_HEAVY});
                        const hit={hpBefore:hp,hpAfter:p.hp,state:p.state,vy:p.vy,stun:p.stunTimer};
                        if(p.hp>=hp||p.state!==STATE.STUNNED||p.vy>=0)failures.push('takeDamage did not create an airborne reaction');
                        const trace=[],snaps=[];let frame=0,landed=-1;paused=false;
                        await new Promise(resolve=>{function tick(){
                            const cell=spriteFrameIndex(p,F),row={frame,cell,state:p.state,ground:p.isGrounded,vy:p.vy,x:p.x,y:p.y,stun:p.stunTimer};
                            if(!p.isGrounded&&!p.grabbedBy&&(p.state===STATE.STUNNED||p.state===STATE.THROWN)){
                                const expected=airExpected(p.vy);if(cell!==expected)failures.push('live hit draws ground/move art');
                            }
                            if(p.isGrounded&&landed<0)landed=frame;
                            const s=document.createElement('canvas');s.width=210;s.height=390;const g=s.getContext('2d');
                            g.fillStyle='#829da6';g.fillRect(0,0,210,390);g.strokeStyle='#374f4e';g.beginPath();g.moveTo(0,362);g.lineTo(210,362);g.stroke();
                            g.save();g.translate(105-p.x-p.width/2,362-GROUND_Y);
                            const render=drawShodoFrame,transforms=[];
                            drawShodoFrame=function(...args){if(args[0]===g&&args[1]===m.img)transforms.push({cell:Math.round(args[2]/m.frameW),a:g.getTransform().a});return render(...args);};
                            try{drawSprite(g,p);}finally{drawShodoFrame=render;g.restore();}
                            const body=transforms.filter(t=>t.cell===cell).at(-1);
                            if(air.includes(cell)||cell===landingCell){
                                row.facing=p.facing;row.renderA=body?.a;
                                row.visualFacing=body?Math.sign(body.a)*(rightAuthored.has(cell)?1:-1):null;
                                if(row.visualFacing!==row.facing)failures.push('live reaction faces backward: cell '+cell);
                            }
                            trace.push(row);snaps.push(s);
                            if(++frame<110&&(landed<0||frame<landed+12))requestAnimationFrame(tick);else resolve();
                        }requestAnimationFrame(tick);});paused=true;
                        if(!trace.some(t=>!t.ground&&t.state===STATE.STUNNED))failures.push('no live airborne hit captured');
                        if(landed<0)failures.push('reaction never landed');
                        if(landingCell!==undefined&&!trace.some(t=>t.ground&&t.cell===landingCell))failures.push('grounded transition fixture not reached');
                        if(trace.some(t=>t.ground&&air.includes(t.cell)))failures.push('air reaction persisted after landing');
                        const live=document.createElement('canvas');live.width=8*210;live.height=Math.ceil(snaps.length/8)*414;
                        const g=live.getContext('2d');g.fillStyle='#829da6';g.fillRect(0,0,live.width,live.height);
                        snaps.forEach((s,i)=>{const x=i%8*210,y=Math.floor(i/8)*414;g.drawImage(s,x,y+24);g.fillStyle='#132127';g.font='12px sans-serif';g.fillText(i+' #'+trace[i].cell+' '+trace[i].state+' vy'+Math.round(trace[i].vy),x+4,y+16);});
                        return{name:p.spec.name,air,failures:[...new Set(failures)],matrix,held,ground,hit,landed,trace,
                            matrixPng:board.toDataURL().split(',')[1],livePng:live.toDataURL().split(',')[1]};
                    ''')
                    assert r and '__error' not in r,r
                    for key,kind in [('matrixPng','poses'),('livePng','live')]:
                        if key in r:(out/(r['name'].lower()+'-'+kind+'.png')).write_bytes(base64.b64decode(r.pop(key)))
                    results.append(r)
                    print(r['name'],len(r.get('matrix',[])),'poses',len(r.get('trace',[])),'live',r['failures'],flush=True)
        finally:proc.terminate();proc.wait(timeout=10)
    report={'boundsCache':cache,'fighters':results}
    (out/'checks.json').write_text(json.dumps(report,indent=2)+'\n')
    assert not cache['failures'] and not any(r['failures'] for r in results),str(out/'checks.json')
    print('PASS',sum(len(r['matrix']) for r in results),'air fixtures;',sum(len(r['trace']) for r in results),'live reaction frames')

if __name__=='__main__':asyncio.run(main())
