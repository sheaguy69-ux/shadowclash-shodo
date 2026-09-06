#!/usr/bin/env python3
"""Check curated jump art through the live picker; capture real key/rAF arcs on :9101."""
import asyncio, base64, json, os, tempfile
from pathlib import Path
import websockets
import watch_game as browser

async def main():
    url=os.environ.get('SHADOWCLASH_URL','http://localhost:9101/index.html')
    browser.assert_serving_this_tree(url)
    out=Path(os.environ.get('OUT','media/ninja-jumps-20260906/live'));out.mkdir(parents=True,exist_ok=True)
    results=[]
    with tempfile.TemporaryDirectory(prefix='ninja-jump-check-') as profile:
        proc,addr=browser.launch(url,profile)
        try:
            async with websockets.connect(addr,max_size=40*1024*1024) as ws:
                c=browser.CDP(ws)
                for _ in range(400):
                    if await c.js("return typeof SPRITES!=='undefined'&&NINJA_ROSTER.every(s=>SPRITES[s.name.toLowerCase()]?.ready)"):break
                    await asyncio.sleep(.1)
                for fighter in ([int(os.environ['FIGHTER'])] if 'FIGHTER' in os.environ else range(9)):
                    r=await c.js('const id='+str(fighter)+r''';
                    dismissTitle();gameMode='2p';spectate=false;cpuMode=false;stagePick='bamboo';p1Pick=id;p2Pick=id===0?1:0;startNewGame();roundIntroTimer=0;paused=true;cutscene=null;
                    const p=player1,m=SPRITES[p.spec.name.toLowerCase()],F=m.frames,failures=[];
                    const flight=Array.from({length:6},(_,i)=>F['jflight'+(i+1)]);
                    if(flight.some(i=>!Number.isInteger(i))||!Number.isInteger(F.jland))failures.push('missing flight/landing art');
                    // Independently inspected artwork, not an inferred ordinal cutoff.
                    const allowed=[[276,277,278,279],[228,229,230,231,232],[301,304,303,305,306],
                        [347,348,349,350,351,352],[303,304,305,306],[299,300,301,302,303,304],
                        [291,292,293],[105,106,107,108],[403,404,405,406]][id];
                    if(flight.some(i=>!allowed.includes(i))||flight.includes(F.jland))failures.push('unreviewed/ground art in flight map');
                    Object.assign(p,{state:STATE.JUMP,isGrounded:false,wallDir:0,wallJumpLock:0,grappleT:0});
                    let swept=0;
                    for(const facing of [-1,1])for(const dir of [null,'fwd','back'])for(let vy=-600;vy<=900;vy++){
                        Object.assign(p,{vy,facing,jumpDir:dir});const idx=spriteFrameIndex(p,F);swept++;
                        if(!flight.includes(idx)){if(failures.length<10)failures.push('non-flight cell '+idx+' at '+vy);}
                    }
                    p.vy=0;p.isGrounded=true;
                    if(spriteFrameIndex(p,F)!==F.jland)failures.push('grounded jump does not land');
                    p.isGrounded=false;p.wallJumpLock=.1;
                    if(F.walljump!==undefined&&spriteFrameIndex(p,F)!==F.walljump)failures.push('wall kick lost precedence');
                    p.wallJumpLock=0;
                    if(id===2){p.vy=250;if(spriteFrameIndex(p,F)!==306)failures.push('Shin still inverted on descent');}
                    if(id===6){p.vy=-450;if(spriteFrameIndex(p,F)!==291)failures.push('Mokurai ground launch still in air');}
                    if(id===8){p.vy=-450;if(spriteFrameIndex(p,F)!==403)failures.push('Oni ground crouch still in air');}
                    if(id===7){p.grappleT=.2;p.grappleT0=.4;if(spriteFrameIndex(p,F)!==F.xanchor5)failures.push('grapple lost precedence');}
                    return {name:p.spec.name,flight,land:F.jland,swept,failures};
                    ''')
                    assert r and '__error' not in r,r
                    if not r['failures'] and '--static' not in os.sys.argv:
                        for mode in ['full','short','reverse','double','wall']:
                            live=await c.js('const id='+str(fighter)+',mode='+json.dumps(mode)+r''';
                            const errors=[];window.onerror=(msg)=>errors.push(String(msg));
                            gameMode='2p';spectate=false;cpuMode=false;stagePick='bamboo';p1Pick=id;p2Pick=id===0?1:0;startNewGame();roundIntroTimer=0;paused=false;cutscene=null;hitstopRemaining=0;
                            for(const k in keys)keys[k]=false;physKeys.clear();
                            const p=player1,m=SPRITES[p.spec.name.toLowerCase()],F=m.frames;
                            player2.x=canvas.width-80;p.x=mode==='reverse'?canvas.width-330:160;
                            for(const q of [p,player2]){q.y=GROUND_Y-q.height;q.isGrounded=true;q.vy=0;}
                            if(mode==='wall'){keys.KeyA=true;physKeys.add('KeyA');p.x=1;p.y=GROUND_Y-p.height-90;p.isGrounded=false;p.wallDir=-1;p.state=STATE.WALL_CLING;}
                            const key=(code,down)=>window.dispatchEvent(new KeyboardEvent(down?'keydown':'keyup',{code,bubbles:true}));
                            const warm=document.createElement('canvas').getContext('2d');
                            for(const idx of new Set([F.idle,F.jland,F.walljump,...Array.from({length:6},(_,i)=>F['jflight'+(i+1)])]))
                                if(Number.isInteger(idx))drawShodoFrame(warm,m.img,idx*m.frameW,0,m.frameW,m.frameH,0,0,m.frameW,m.frameH);
                            const snaps=[],trace=[];let frame=0;
                            await new Promise(resolve=>{function tick(){
                                const cell=spriteFrameIndex(p,F);trace.push({frame,cell,state:p.state,ground:p.isGrounded,vy:p.vy,x:p.x,y:p.y,facing:p.facing,wall:p.wallJumpLock,grapple:p.grappleT});
                                const shot=document.createElement('canvas');shot.width=230;shot.height=330;const g=shot.getContext('2d');g.fillStyle='#73a2b0';g.fillRect(0,0,230,330);
                                g.save();g.translate(115-p.x-p.width/2,305-GROUND_Y);drawSprite(g,p);g.restore();snaps.push(shot);
                                if(frame===3){if(mode==='reverse')key('KeyA',true);key('KeyW',true);if(mode==='wall')key('KeyA',false);}
                                if(frame===(mode==='short'?5:mode==='full'?60:18))key('KeyW',false);
                                if(mode==='double'&&frame===22)key('KeyW',true);
                                if(mode==='double'&&frame===35)key('KeyW',false);
                                if(frame===40)key('KeyA',false);
                                if(++frame<85)requestAnimationFrame(tick);else resolve();
                            }requestAnimationFrame(tick);});
                            paused=true;key('KeyW',false);key('KeyA',false);
                            const flight=Array.from({length:6},(_,i)=>F['jflight'+(i+1)]),air=trace.filter(t=>!t.ground&&t.state===STATE.JUMP&&t.wall<=0&&t.grapple<=0);
                            if(!air.length)errors.push('jump did not start');
                            if(!trace.some((t,i)=>i>5&&t.ground&&!trace[i-1].ground))errors.push('no landing observed');
                            if(air.some(t=>!flight.includes(t.cell)))errors.push('non-flight cell during live jump');
                            if(mode==='reverse'&&!air.some(t=>t.facing===-1))errors.push('leftward jump never faced left');
                            if(mode==='full'&&new Set(air.map(t=>t.cell)).size<new Set(flight).size)errors.push('full jump skipped a distinct beat');
                            // Every tick is retained; the long strip is a consecutive live filmstrip.
                            const board=document.createElement('canvas');board.width=10*230;board.height=Math.ceil(snaps.length/10)*355;
                            const g=board.getContext('2d');g.fillStyle='#73a2b0';g.fillRect(0,0,board.width,board.height);
                            snaps.forEach((s,i)=>{const x=i%10*230,y=Math.floor(i/10)*355;g.drawImage(s,x,y+25);g.fillStyle='#12252a';g.font='12px sans-serif';g.fillText(i+' cell '+trace[i].cell+' vy '+Math.round(trace[i].vy),x+5,y+16);});
                            return {mode,trace,errors,png:board.toDataURL().split(',')[1]};
                            ''')
                            assert live and '__error' not in live,live
                            (out/(r['name'].lower()+'-'+mode+'.png')).write_bytes(base64.b64decode(live.pop('png')))
                            r.setdefault('live',[]).append(live);r['failures']+=live['errors']
                    results.append(r);print(r['name'],r['failures'],flush=True)
        finally:
            proc.terminate();proc.wait(timeout=10)
    (out/'checks.json').write_text(json.dumps(results,indent=2))
    assert not any(r['failures'] for r in results),str(out/'checks.json')
    print('PASS:',sum(r['swept'] for r in results),'picker cases;',sum(len(r.get('live',[])) for r in results),'live jump arcs')

if __name__=='__main__':asyncio.run(main())
