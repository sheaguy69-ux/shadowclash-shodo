#!/usr/bin/env python3
"""Verify Oni's run-only trailing aura through the actual shared sprite renderer."""
import argparse
import asyncio
import base64
import hashlib
import json
import os
import subprocess
import tempfile
from pathlib import Path

import websockets
import watch_game as browser


async def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--out', type=Path, default=Path('media/oni-run-aura-20260907/after/runtime.json'))
    ap.add_argument('--compare', type=Path, help='Compare body and movement samples to the pre-change run')
    ap.add_argument('--record-baseline', action='store_true', help='Save the expected failing old-aura baseline')
    ap.add_argument('--previous-renderer', type=Path, help='Replay only drawOniAura from a saved index in browser memory')
    ap.add_argument('--film', action='store_true')
    args = ap.parse_args()
    previous = ''
    if args.previous_renderer:
        saved = args.previous_renderer.read_text()
        start = saved.index('function drawOniAura(')
        end = saved.index('function drawSprite(', start)
        previous = 'drawOniAura = '+saved[start:end].strip()+';\n'
    before = hashlib.sha256(Path('web/index.html').read_bytes()).hexdigest()
    browser.assert_serving_this_tree('http://localhost:9101/index.html')
    browser.PORT = int(os.environ.get('DEBUG_PORT', '9372'))
    with tempfile.TemporaryDirectory(prefix='oni-run-aura-') as profile:
        proc, address = browser.launch('http://localhost:9101/index.html', profile)
        try:
            async with websockets.connect(address, max_size=100_000_000) as ws:
                c = browser.CDP(ws)
                for _ in range(400):
                    if await c.js("return typeof SPRITES!=='undefined'&&NINJA_ROSTER.every(s=>SPRITES[s.name.toLowerCase()]?.ready)&&FX_ONI_AURA.ready&&(typeof FX_ONI_RUN_AURA==='undefined'||FX_ONI_RUN_AURA.ready)"):
                        break
                    await asyncio.sleep(.1)
                result = await c.js(previous+'const film='+json.dumps(args.film)+';\n'+r'''
                dismissTitle();const failures=[],runs=[],probes=[],coverageSamples=[];
                const check=(ok,message)=>{if(!ok&&!failures.includes(message))failures.push(message);};
                const nextAura=typeof FX_ONI_RUN_AURA==='undefined'?null:FX_ONI_RUN_AURA;
                check(nextAura?.ready,'new run aura is missing or not ready');
                const boundsCache=new Map(),inkCanvas=document.createElement('canvas');
                const inkRange=(img,e,offset=0)=>{
                    const [sx,sy,sw,sh,dx,dy,dw,dh]=e.args,key=[img.src,sx,sy,sw,sh].join('|');
                    let box=boundsCache.get(key);
                    if(!box){
                        inkCanvas.width=sw;inkCanvas.height=sh;const c=inkCanvas.getContext('2d',{willReadFrequently:true});
                        c.drawImage(img,sx,sy,sw,sh,0,0,sw,sh);const pixels=c.getImageData(0,0,sw,sh).data;
                        box=[sw,sh,0,0];for(let y=0;y<sh;y++)for(let x=0;x<sw;x++)if(pixels[(y*sw+x)*4+3]>32){box[0]=Math.min(box[0],x);box[1]=Math.min(box[1],y);box[2]=Math.max(box[2],x+1);box[3]=Math.max(box[3],y+1);}
                        boundsCache.set(key,box);
                    }
                    if(box[0]>=box[2]||box[1]>=box[3])return [Infinity,-Infinity];
                    const [,b,,d,,f]=e.matrix,ys=[];
                    for(const x of [box[0],box[2]])for(const y of [box[1],box[3]])ys.push(b*(dx+(x+offset)*dw/sw)+d*(dy+y*dh/sh)+f);
                    return [Math.min(...ys),Math.max(...ys)];
                };
                const key=(code,down)=>window.dispatchEvent(new KeyboardEvent(down?'keydown':'keyup',{code,bubbles:true}));
                const plate=document.createElement('canvas');plate.width=640;plate.height=300;const g=plate.getContext('2d');
                const preview=document.createElement('canvas');preview.width=640;preview.height=300;const pg=preview.getContext('2d');
                const setup=(id,side=1)=>{
                    gameMode='2p';cpuMode=false;spectate=false;stagePick='bamboo';p1Pick=id;p2Pick=id===0?1:0;
                    animClock=0;startNewGame();paused=false;roundIntroTimer=0;hitstopRemaining=0;cutscene=null;releaseAllKeys();
                    const p=player1;Object.assign(p,{x:side>0?500:400,y:GROUND_Y-p.height,isGrounded:true,_wasGrounded:true,vx:0,vy:0,state:STATE.IDLE,facing:side,landT:0});
                    player2.x=side>0?940:20;return p;
                };
                const motion=p=>[p.x,p.y,p.vx,p.vy,p.state,p.facing,p.animPhase,p.jumpsLeft];
                const signature=p=>{
                    const man=SPRITES[p.spec.name.toLowerCase()],events=[],original=g.drawImage,body=drawShodoFrame;
                    const oldMotion=JSON.stringify(motion(p));g.setTransform(1,0,0,1,0,0);g.clearRect(0,0,640,300);g.translate(300-p.x,260-GROUND_Y);
                    g.drawImage=function(...a){
                        const kind=a[0]===FX_ONI_AURA.img?'old':a[0]===nextAura?.img?'trail':null;
                        if(kind){const m=this.getTransform(),d=a.length===9?a.slice(5):a.length===5?a.slice(1):[a[1],a[2],a[0].width,a[0].height];
                            const cx=d[0]+d[2]/2,cy=d[1]+d[3]/2;events.push({kind,alpha:this.globalAlpha,args:a.slice(1),matrix:[m.a,m.b,m.c,m.d,m.e,m.f],centerX:m.a*cx+m.c*cy+m.e,centerY:m.b*cx+m.d*cy+m.f});}
                        return original.apply(this,a);
                    };
                    drawShodoFrame=function(...a){if(a[1]===man.img){const m=a[0].getTransform();events.push({kind:'body',cell:p.drawCell,args:a.slice(2),matrix:[m.a,m.b,m.c,m.d,m.e,m.f]});}return body.apply(this,a);};
                    try{drawSprite(g,p);}finally{g.drawImage=original;drawShodoFrame=body;}
                    check(oldMotion===JSON.stringify(motion(p)),'aura draw mutated movement or body animation state');
                    return events;
                };
                const bodyHash=p=>{
                    const old=drawOniAura;drawOniAura=()=>{};
                    try{signature(p);}finally{drawOniAura=old;}
                    const pixels=g.getImageData(0,0,640,300).data;let h=2166136261;
                    for(const byte of pixels)h=Math.imul(h^byte,16777619);return (h>>>0).toString(16);
                };
                const grade=(p,events,label)=>{
                    const old=events.filter(e=>e.kind==='old'),trail=events.filter(e=>e.kind==='trail');
                    if(p.spec.id!==8){check(!old.length&&!trail.length,'another fighter inherited Oni aura');return;}
                    if(p.state===STATE.RUN){
                        check(!old.length,'RUN still draws the old encircling aura');check(trail.length>0,'RUN does not draw the new trail');
                        const direction=Math.abs(p.vx)>1?Math.sign(p.vx):p.facing,bodyX=300+p.width/2;
                        for(const e of trail){check((e.centerX-bodyX)*direction<0,'run aura sits ahead of movement');check(events.indexOf(e)<events.findIndex(v=>v.kind==='body'),'run aura draws in front of the body');}
                        const body=events.find(e=>e.kind==='body'),visible=trail.filter(e=>e.alpha>0.02);
                        if(body&&visible.length){
                            const man=SPRITES.oni,pose=inkRange(man.img,body,man.img.shodoFrameOffsetX?.[body.cell]??0),ranges=visible.map(e=>inkRange(nextAura.img,e));
                            const top=Math.min(...ranges.map(r=>r[0])),bottom=Math.max(...ranges.map(r=>r[1]));
                            const coverage=Math.max(0,Math.min(bottom,pose[1])-Math.max(top,pose[0]))/(pose[1]-pose[0]);
                            coverageSamples.push(coverage);
                            check(coverage>=0.9,'run aura ink covers less than 90% of the rendered pose height');
                        }
                    }else{check(old.length>0,'non-run Oni lost the original aura');check(!trail.length,'new trail leaked outside RUN');}
                };
                for(const side of [-1,1]){
                    const p=setup(8,side),records=[],first=side>0?'KeyA':'KeyD',second=side>0?'KeyD':'KeyA';
                    for(let tick=0;tick<96;tick++){
                        if(tick===8)key(first,true);
                        if(tick===48){key(first,false);key(second,true);}
                        if(tick===88)key(second,false);
                        updateGame(1/(60*COMBAT_TEMPO));
                        const events=signature(p);grade(p,events,'input');
                        const body=events.find(e=>e.kind==='body'),without=bodyHash(p),bodyControl=signature(p).find(e=>e.kind==='body');
                        check(JSON.stringify(body)===JSON.stringify(bodyControl),'aura changed body source or transform');
                        const record={tick,clock:animClock,motion:motion(p),body,body_hash:without,events};
                        if(film){drawScene();pg.fillStyle='#16181c';pg.fillRect(0,0,640,300);pg.drawImage(canvas,p.x-300,GROUND_Y-260,640,270,0,30,640,270);pg.fillStyle='#fff';pg.font='14px sans-serif';pg.fillText('Oni · '+p.state+' · vx '+p.vx.toFixed(0)+' · cell '+p.drawCell,12,20);record.png=preview.toDataURL().split(',')[1];}
                        records.push(record);
                    }
                    runs.push({side,records});
                }
                const p=setup(8),man=SPRITES.oni;p.state=STATE.RUN;p.animPhase=0.1;
                const idx=spriteFrameIndex(p,man.frames),previous=man.mirror?.[idx];man.mirror??={};
                for(const velocity of [-525,525])for(const facing of [-1,1])for(const mirrored of [false,true]){
                    p.vx=velocity;p.facing=facing;man.mirror[idx]=mirrored;
                    const events=signature(p);grade(p,events,'direction');probes.push({velocity,facing,mirrored,events});
                }
                if(previous===undefined)delete man.mirror[idx];else man.mirror[idx]=previous;
                p.vx=525;p.facing=1;const savedClock=animClock,first=signature(p),second=signature(p);
                check(JSON.stringify(first)===JSON.stringify(second),'frozen combat clock changes the aura');
                animClock+=1/30;const advanced=signature(p);animClock=savedClock;
                check(JSON.stringify(first.filter(e=>e.kind==='trail'))!==JSON.stringify(advanced.filter(e=>e.kind==='trail')),'moving combat clock does not animate the new aura');
                const ready=nextAura?.ready;if(nextAura)nextAura.ready=false;
                const unloaded=signature(p);check(!unloaded.some(e=>e.kind==='old'),'RUN falls back to old aura while new texture loads');
                if(nextAura)nextAura.ready=ready;
                p.vx=0;const stopped=signature(p);
                check(!stopped.some(e=>e.kind==='old'||e.kind==='trail'),'zero-velocity RUN draws an aura');
                for(const state of [STATE.IDLE,STATE.CROUCH,STATE.JUMP,STATE.ATTACK_LIGHT]){
                    p.state=state;p.vx=0;if(state===STATE.ATTACK_LIGHT)p.attackAnim={start:animClock*1000,dur:300};
                    grade(p,signature(p),'non-run');
                }
                for(let id=0;id<8;id++){const q=setup(id);q.state=STATE.RUN;q.vx=525;grade(q,signature(q),'non-Oni');}
                paused=true;releaseAllKeys();return {failures,runs,probes,coverage:{samples:coverageSamples.length,min:Math.min(...coverageSamples)},tempo:COMBAT_TEMPO,aura_sources:{old:FX_ONI_AURA.img.src,trail:nextAura?.img.src??null}};
                ''')
                assert result and '__error' not in result, result
        finally:
            proc.terminate()
            proc.wait(timeout=10)
    result['index_sha256'] = before
    if args.previous_renderer:
        result['previous_renderer_sha256'] = hashlib.sha256(args.previous_renderer.read_bytes()).hexdigest()
        result['previous_renderer_scope'] = 'Only drawOniAura restored in browser memory; all production files untouched.'
    if args.compare:
        baseline = json.loads(args.compare.read_text())
        for old_run, new_run in zip(baseline['runs'], result['runs']):
            assert old_run['side'] == new_run['side']
            for old, new in zip(old_run['records'], new_run['records']):
                for field in ['motion', 'body', 'body_hash']:
                    assert old[field] == new[field], (field, old['tick'], old_run['side'])
    args.out.parent.mkdir(parents=True, exist_ok=True)
    if args.film:
        for run in result['runs']:
            folder = args.out.parent/('opponent-right' if run['side']>0 else 'opponent-left')
            frames = folder/'frames';frames.mkdir(parents=True, exist_ok=True)
            for record in run['records']:
                (frames/f"{record['tick']:03}.png").write_bytes(base64.b64decode(record.pop('png')))
            for name, start, end in [('start-reverse-stop',0,96),('retreat',8,48),('approach',48,88)]:
                subprocess.run(['ffmpeg','-y','-loglevel','error','-framerate','72','-i',str(frames/'%03d.png'),
                    '-filter_complex',f'trim=start_frame={start}:end_frame={end},setpts=PTS-STARTPTS,fps=30,split[a][b];[a]palettegen[p];[b][p]paletteuse',
                    '-loop','0',str(folder/(name+'.gif'))],check=True,timeout=30)
    args.out.write_text(json.dumps(result, indent=2))
    print(('BASELINE' if args.record_baseline else 'CHECK')+f": 192 input samples, 8 movement/facing/mirror cases; {len(result['failures'])} failures → {args.out}")
    for failure in result['failures']:
        print('  '+failure)
    if not args.record_baseline:
        assert not result['failures'], result['failures']


if __name__ == '__main__':
    asyncio.run(main())
