#!/usr/bin/env python3
"""Render every mapped Ember cell and check body, trail, clone and flash sizing on :9101.

OUT defaults to media/ember-scale-20260905. Plates use the real drawSprite renderer;
--before disables only the scale/foot metadata in the isolated test browser.
"""
import asyncio
import base64
import hashlib
import json
import os
from pathlib import Path
import sys
import tempfile

import websockets
import watch_game as browser


async def main():
    url = os.environ.get('SHADOWCLASH_URL', 'http://localhost:9101/index.html')
    browser.assert_serving_this_tree(url)
    out = Path(os.environ.get('OUT', 'media/ember-scale-20260905'))
    out.mkdir(parents=True, exist_ok=True)
    before = '--before' in sys.argv
    png = Path('web/assets/sprites/ember.png')
    digest = hashlib.sha256(png.read_bytes()).hexdigest()
    with tempfile.TemporaryDirectory(prefix='ember-scale-') as profile:
        proc, address = browser.launch(url, profile)
        try:
            async with websockets.connect(address, max_size=24 * 1024 * 1024) as ws:
                cdp = browser.CDP(ws)
                for _ in range(300):
                    if await cdp.js("return typeof SPRITES !== 'undefined' && SPRITES.ember?.ready") is True:
                        break
                    await asyncio.sleep(0.1)
                else:
                    raise RuntimeError('Ember sheet did not load')
                result = await cdp.js(r"""
                dismissTitle();gameMode='2p';cpuMode=false;spectate=false;
                p1Pick=4;p2Pick=5;stagePick='bamboo';startNewGame();roundIntroTimer=0;paused=true;
                const man=SPRITES.ember,p=player1, failures=[], draws=[],foot=man.footY;
                const near=(a,b,msg)=>{if(Math.abs(a-b)>1e-6)failures.push(msg+': '+a+' != '+b);};
                const groups={};
                for(const [key,cell] of Object.entries(man.frames)){
                    const group=key.replace(/[_\d]+$/,'');(groups[group]??=[]).push({key,cell});
                }
                const cells=[...new Set(Object.values(man.frames))];
                if(cells.length!==140)failures.push('Ember inventory changed: review new cells');
                for(const cell of cells){
                    const k=man.frameScale?.[cell]??1;
                    if(!(Number.isFinite(k)&&k>=0.5&&k<=2))failures.push('missing/invalid scale '+cell);
                }
                // Independent calibration fixtures: canonical idle, undersized kick,
                // oversized claw-rend, and short/low poses that must stay compact.
                for(const [key,k] of Object.entries({idle:1,kpush1:1.5,clawrend1:0.76,lowrake1:0.8,roll_1:0.9}))
                    near(man.frameScale?.[man.frames[key]]??1,k,key+' calibration');
                const base=man.scale*SHODO_DISPLAY_SCALE*(p.spec.renderScale||1);
                // These inspected rectangles contain disconnected card marks.
                // Verify the keyer removes them and preserves every outside pixel.
                const raw=document.createElement('canvas');raw.width=man.frameW;raw.height=man.frameH;
                const rg=raw.getContext('2d');let erased=0;
                for(const [cell,rects] of Object.entries(man.frameClear??{})){
                    rg.clearRect(0,0,man.frameW,man.frameH);
                    rg.drawImage(man.img,Number(cell)*man.frameW,0,man.frameW,man.frameH,0,0,man.frameW,man.frameH);
                    const a=rg.getImageData(0,0,man.frameW,man.frameH).data;
                    const b=keyedShodoCell(man.img,Number(cell)*man.frameW,0,man.frameW,man.frameH).getContext('2d').getImageData(0,0,man.frameW,man.frameH).data;
                    for(let y=0;y<man.frameH;y++)for(let x=0;x<man.frameW;x++){
                        const i=(y*man.frameW+x)*4,clear=rects.some(([rx,ry,w,h])=>x>=rx&&x<rx+w&&y>=ry&&y<ry+h);
                        if(clear){if(b[i+3])failures.push('card mark remains '+cell);if(a[i+3])erased++;}
                        else for(let j=0;j<4;j++)if(a[i+j]!==b[i+j]){failures.push('outside artwork changed '+cell);break;}
                    }
                }
                if(!erased)failures.push('card-mark fixtures no longer exercise pixels');
                near(man.footAdj?.[133]??0,42,'hurt3 floor');
                near(man.footAdj?.[290]??0,21,'lowrake1 floor');
                const nativePick=spriteFrameIndex,nativeDraw=drawShodoFrame;
                let selected=man.frames.idle;
                spriteFrameIndex=()=>selected;
                const c=document.createElement('canvas');c.width=600;c.height=550;
                const g=c.getContext('2d',{willReadFrequently:true});
                Object.assign(p,{x:280-p.width/2,y:490-p.height,state:STATE.IDLE,isGrounded:true,vx:0,vy:0,
                    attackAnim:null,landSquash:0,hitSquashT:0,hitFlashT:0,rollTimer:0,flipTimer:0,ghosts:[],clone:null});
                drawShodoFrame=(...a)=>{draws.push({cell:a[2]/man.frameW,dx:a[6],dy:a[7],w:a[8],h:a[9]});return nativeDraw(...a);};
                let checked=0;
                try{
                    for(const cell of cells){
                        selected=cell;draws.length=0;g.clearRect(0,0,c.width,c.height);drawSprite(g,p);
                        const actual=draws[0],s=base*(man.frameScale?.[cell]??1);
                        if(!actual){failures.push('not drawn '+cell);continue;}
                        near(actual.w,man.frameW*s,'width '+cell);near(actual.h,man.frameH*s,'height '+cell);
                        near(actual.dx,-man.frameW*s/2,'center '+cell);
                        near(actual.dy,-(foot-(man.footAdj?.[cell]??0))*s,'anchor '+cell);
                        const a=g.getImageData(0,0,c.width,c.height).data;
                        let ink=0,edge=0;
                        for(let y=0;y<c.height;y++)for(let x=0;x<c.width;x++)if(a[(y*c.width+x)*4+3]>8){ink++;if(x<2||y<2||x>=c.width-2||y>=c.height-2)edge++;}
                        if(!ink||edge)failures.push('blank/clipped rendered envelope '+cell);
                        checked++;
                    }
                    // Copies use THEIR stored cell scale even while the live body is idle.
                    selected=man.frames.idle;
                    const copied=man.frames.kpush1,s=base*1.5;
                    p.ghosts=[{idx:copied,x:p.x,y:p.y,facing:1,life:GHOST_LIFE}];
                    p.clone={cell:copied,x:p.x,y:p.y,facing:1,t:1};draws.length=0;drawSprite(g,p);
                    for(const d of draws.filter(d=>d.cell===copied)){
                        near(d.w,man.frameW*s,'copy width');near(d.dy,-(foot-(man.footAdj?.[copied]??0))*s,'copy anchor');
                    }
                    if(draws.filter(d=>d.cell===copied).length!==2)failures.push('missing trail/clone');
                    p.ghosts=[];p.clone=null;
                    // White hit flash must cover the resized body, with the same anchor.
                    selected=copied;p.hitFlashT=FEEL.victimFlash;
                    const nativeImage=g.drawImage,flashes=[];
                    g.drawImage=function(...a){if(a[0]===flashScratch)flashes.push(a.slice(5));return nativeImage.apply(this,a);};
                    try{drawSprite(g,p);}finally{g.drawImage=nativeImage;p.hitFlashT=0;}
                    if(flashes.length!==1)failures.push('missing hit flash');
                    else {near(flashes[0][2],man.frameW*s,'flash width');near(flashes[0][1],-(foot-(man.footAdj?.[copied]??0))*s,'flash anchor');}
                }finally{drawShodoFrame=nativeDraw;spriteFrameIndex=nativePick;}
                window.emberReview={groups,failures,checked,p,cells};
                return {failures,checked,keys:Object.keys(man.frames).length,cells,scale:base};
                """)
                if not result or '__error' in result:
                    raise RuntimeError(result)
                if before:
                    await cdp.js('SPRITES.ember.frameScale={};SPRITES.ember.footAdj={};SPRITES.ember.img.shodoClearRects=null;shodoCellCache.clear();shodoFrameCache.clear();')
                # One plate per four families; no equal-height thumbnail fitting.
                count = await cdp.js('return Object.keys(emberReview.groups).length;')
                for start in range(0, count, 4):
                    data = await cdp.js(r"""
                    const man=SPRITES.ember,p=emberReview.p;
                    const rows=Object.entries(emberReview.groups).slice(START,START+4);
                    const c=document.createElement('canvas');c.width=8*240;c.height=rows.length*270;
                    const g=c.getContext('2d');g.fillStyle='#d5cdbd';g.fillRect(0,0,c.width,c.height);
                    const pick=spriteFrameIndex;let idx; spriteFrameIndex=()=>idx;
                    try{rows.forEach(([name,values],r)=>{
                        const seen=new Set();values=values.sort((a,b)=>a.key.localeCompare(b.key,undefined,{numeric:true})).filter(v=>{if(seen.has(v.cell))return false;seen.add(v.cell);return true;});
                        values.forEach((v,col)=>{
                            idx=v.cell;const x=col*240,y=r*270;
                            g.fillStyle='#191919';g.font='14px sans-serif';g.fillText(v.key+' ['+idx+'] x'+(man.frameScale?.[idx]??1),x+5,y+19);
                            g.strokeStyle='#9b9180';g.beginPath();g.moveTo(x,y+253);g.lineTo(x+239,y+253);g.stroke();
                            Object.assign(p,{x:x+120-p.width/2,y:y+253-p.height});drawSprite(g,p);
                        });
                    });}finally{spriteFrameIndex=pick;}
                    return c.toDataURL('image/png').split(',')[1];
                    """.replace('START', str(start)))
                    if not isinstance(data,str):
                        raise RuntimeError(data)
                    (out / f"{'before' if before else 'after'}-{start//4+1}.png").write_bytes(base64.b64decode(data))
                if not before:
                    for direction, code, family in [('forward','KeyD','clawrend'),('down','KeyS','lowrake'),('back','KeyA','eretreat')]:
                        live = await cdp.js(r"""
                        gameMode='2p';cpuMode=false;spectate=false;p1Pick=4;p2Pick=5;startNewGame();
                        roundIntroTimer=0;hitstopRemaining=0;paused=false;
                        for(const k in keys)keys[k]=false;physKeys.clear();
                        player1.x=300;player2.x=canvas.width-80;
                        for(const p of [player1,player2]){p.y=GROUND_Y-p.height;p.isGrounded=true;}
                        // Let the freshly started stage finish its cold first draw.
                        await new Promise(r=>requestAnimationFrame(()=>requestAnimationFrame(r)));
                        const shots=[],trace=[],key=(code,down)=>window.dispatchEvent(new KeyboardEvent(down?'keydown':'keyup',{code,bubbles:true}));
                        await new Promise(resolve=>{function tick(){
                            if(!shots.length){key('CODE',true);key('KeyG',true);key('KeyG',false);key('CODE',false);}
                            const c=document.createElement('canvas');c.width=240;c.height=240;
                            const g=c.getContext('2d');g.fillStyle='#d5cdbd';g.fillRect(0,0,240,240);
                            g.save();g.translate(120-player1.x-player1.width/2,225-GROUND_Y);drawSprite(g,player1);g.restore();
                            g.fillStyle='#191919';g.font='12px sans-serif';g.fillText('tick '+shots.length+' / cell '+player1.drawCell,5,16);
                            shots.push(c);trace.push({cell:player1.drawCell,state:player1.state,t:animClock});
                            if(shots.length<36)requestAnimationFrame(tick);else resolve();
                        }requestAnimationFrame(tick);});
                        paused=true;const c=document.createElement('canvas');c.width=1440;c.height=1440;const g=c.getContext('2d');
                        shots.forEach((s,i)=>g.drawImage(s,i%6*240,Math.floor(i/6)*240));
                        return {trace,png:c.toDataURL('image/png').split(',')[1],expected:Object.entries(SPRITES.ember.frames).filter(([k])=>k.startsWith('FAMILY')).map(([,i])=>i)};
                        """.replace('CODE',code).replace('FAMILY',family))
                        if not live or '__error' in live:
                            raise RuntimeError(live)
                        (out / f'live-heavy-{direction}.png').write_bytes(base64.b64decode(live.pop('png')))
                        seen={f['cell'] for f in live['trace']}
                        if not set(live['expected']).issubset(seen):
                            result['failures'].append(f"{family}: missed live cells {set(live['expected'])-seen}")
                        (out / f'live-heavy-{direction}.json').write_text(json.dumps(live,indent=2)+'\n')
        finally:
            proc.kill()
            proc.wait(timeout=10)
    browser.assert_serving_this_tree(url, 'after the run')
    assert hashlib.sha256(png.read_bytes()).hexdigest()==digest, 'source PNG changed during review'
    result['png_sha256']=digest
    (out / 'checks.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result,indent=2))
    assert not result['failures'], result['failures']


if __name__=='__main__':
    asyncio.run(main())
