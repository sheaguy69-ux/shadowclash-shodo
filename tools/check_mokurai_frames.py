#!/usr/bin/env python3
"""Check real sprite visibility at both walls; capture complete live run loops on :9101."""
import asyncio, base64, json, os, tempfile
from pathlib import Path
import websockets
import sys
sys.path.insert(0,str(Path.cwd()/'tools'))
import watch_game as browser

async def main():
    url='http://localhost:9101/index.html';browser.assert_serving_this_tree(url)
    out=Path(os.environ.get('OUT','media/mokurai-audit-20260906/live'));out.mkdir(parents=True,exist_ok=True)
    meta=json.loads(Path('web/assets/sprites/mokurai.json').read_text())
    assert not ({355,362} & set(meta['frames'].values())), 'nearly empty guard cells are active'
    assert [meta['frames']['mpalm'+str(i)] for i in range(1,6)] == [372,373,374,375,377], 'palm mapped to slam'
    results=[]
    with tempfile.TemporaryDirectory(prefix='roster-visual-check-') as profile:
        proc,addr=browser.launch(url,profile)
        try:
            async with websockets.connect(addr,max_size=50*1024*1024) as ws:
                c=browser.CDP(ws)
                for _ in range(400):
                    if await c.js("return typeof SPRITES!=='undefined'&&NINJA_ROSTER.every(s=>SPRITES[s.name.toLowerCase()]?.ready)"):break
                    await asyncio.sleep(.1)
                for id in [6]:
                    r=await c.js('const id='+str(id)+r''';
                    dismissTitle();gameMode='2p';spectate=false;cpuMode=false;stagePick='bamboo';p1Pick=id;p2Pick=id===0?1:0;startNewGame();roundIntroTimer=0;paused=true;cutscene=null;
                    const p=player1,m=SPRITES[p.spec.name.toLowerCase()],failures=[],walls=[];
                    const target=document.createElement('canvas');target.width=canvas.width+1000;target.height=canvas.height+1000;
                    const g=target.getContext('2d',{willReadFrequently:true});
                    for(const interior of [false,true])for(const side of [-1,1]){
                        Object.assign(p,{x:interior?canvas.width/2-p.width/2:side<0?10:canvas.width-10-p.width,y:GROUND_Y-p.height-180,vx:0,vy:70,state:STATE.WALL_CLING,isGrounded:false,wallDir:side,facing:-side,attackAnim:null,hitFlashT:0,landSquash:0,ghosts:[],clone:null});
                        g.clearRect(0,0,target.width,target.height);g.save();g.translate(500,500);drawSprite(g,p);g.restore();
                        const a=g.getImageData(0,0,target.width,target.height).data;let total=0,visible=0;
                        for(let y=0;y<target.height;y++)for(let x=0;x<target.width;x++)if(a[(y*target.width+x)*4+3]>128){total++;if(x>=500&&x<500+canvas.width&&y>=500&&y<500+canvas.height)visible++;}
                        const fraction=visible/Math.max(1,total);walls.push({interior,side,cell:p.drawCell,total,visible,fraction});
                        if(total<100||fraction<.98)failures.push('wall '+side+' only '+Math.round(fraction*100)+'% visible');
                    }
                    return {name:p.spec.name,walls,failures};
                    ''')
                    assert r and '__error' not in r,r
                    if '--static' not in os.sys.argv:
                        for side in [-1,1]:
                            live=await c.js('const id='+str(id)+',side='+str(side)+r'''
                            gameMode='2p';spectate=false;cpuMode=false;stagePick='bamboo';p1Pick=id;p2Pick=id===0?1:0;startNewGame();roundIntroTimer=0;paused=false;cutscene=null;hitstopRemaining=0;
                            for(const k in keys)keys[k]=false;physKeys.clear();
                            const p=player1,m=SPRITES[p.spec.name.toLowerCase()],run=runCells(m.frames),snaps=[],trace=[];
                            p.x=side>0?120:canvas.width-170;player2.x=side>0?canvas.width-80:20;
                            const key=(code,down)=>window.dispatchEvent(new KeyboardEvent(down?'keydown':'keyup',{code,bubbles:true}));
                            const warm=document.createElement('canvas').getContext('2d');for(const idx of run)drawShodoFrame(warm,m.img,idx*m.frameW,0,m.frameW,m.frameH,0,0,m.frameW,m.frameH);
                            let frame=0;const began=performance.now();
                            await new Promise(resolve=>{function tick(){
                                const idx=spriteFrameIndex(p,m.frames);trace.push({frame,ms:performance.now()-began,idx,state:p.state,vx:p.vx,x:p.x,phase:p.animPhase});
                                const shot=document.createElement('canvas');shot.width=230;shot.height=240;const sg=shot.getContext('2d');sg.fillStyle='#83b7c0';sg.fillRect(0,0,230,240);sg.save();sg.translate(115-p.x-p.width/2,220-GROUND_Y);drawSprite(sg,p);sg.restore();snaps.push(shot);
                                const pixels=sg.getImageData(0,0,230,240).data;let visibleInk=0;
                                for(let i=0;i<pixels.length;i+=4)if(pixels[i]!==131||pixels[i+1]!==183||pixels[i+2]!==192)visibleInk++;
                                trace[trace.length-1].visibleInk=visibleInk;
                                if(frame===2)key(side>0?'KeyD':'KeyA',true);
                                if(frame===56)key(side>0?'KeyD':'KeyA',false);
                                if(++frame<67)requestAnimationFrame(tick);else resolve();
                            }requestAnimationFrame(tick);});paused=true;key('KeyA',false);key('KeyD',false);
                            const active=trace.filter(t=>t.state===STATE.RUN&&Math.abs(t.vx)>100),failures=[];
                            if(trace.some(t=>t.visibleInk<100))failures.push('live loop contains an invisible body');
                            if(new Set(active.map(t=>t.idx)).size!==run.length)failures.push('live run omitted stride cells');
                            for(let i=1;i<active.length;i++){const step=(run.indexOf(active[i].idx)-run.indexOf(active[i-1].idx)+run.length)%run.length;if(step>1)failures.push('skipped '+step+' cells at '+active[i].frame);}
                            const board=document.createElement('canvas');board.width=10*230;board.height=7*260;const bg=board.getContext('2d');bg.fillStyle='#83b7c0';bg.fillRect(0,0,board.width,board.height);
                            snaps.forEach((snap,i)=>{const x=i%10*230,y=Math.floor(i/10)*260;bg.drawImage(snap,x,y+20);bg.fillStyle='#102a30';bg.font='12px sans-serif';bg.fillText(i+' cell '+trace[i].idx+' vx '+Math.round(trace[i].vx),x+3,y+14);});
                            return {side,trace,failures,png:board.toDataURL().split(',')[1]};
                            ''')
                            assert live and '__error' not in live,live
                            (out/(r['name'].lower()+'-run-'+str(side)+'.png')).write_bytes(base64.b64decode(live.pop('png')))
                            r.setdefault('runs',[]).append(live);r['failures']+=live['failures']
                    results.append(r);print(r['name'],r['failures'],flush=True)
        finally:proc.terminate();proc.wait(timeout=10)
    (out/'checks.json').write_text(json.dumps(results,indent=2))
    assert not any(r['failures'] for r in results),str(out/'checks.json')
if __name__=='__main__':asyncio.run(main())
