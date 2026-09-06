#!/usr/bin/env python3
"""Exercise Shin's directional heavies and reject the retired 354–377 artwork."""
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
    out = Path(os.environ.get('OUT', 'media/shin-old-frame-20260906/check'))
    out.mkdir(parents=True, exist_ok=True)
    results = []
    with tempfile.TemporaryDirectory(prefix='shin-art-check-') as profile:
        proc, addr = browser.launch(url, profile)
        try:
            async with websockets.connect(addr, max_size=50*1024*1024) as ws:
                c = browser.CDP(ws)
                for _ in range(400):
                    if await c.js("return typeof SPRITES!=='undefined'&&SPRITES.shin?.ready&&SPRITES.executioner?.ready"):
                        break
                    await asyncio.sleep(.1)
                else:
                    raise AssertionError('Shin sheets did not load')
                for stance in [False, True]:
                    for side in [-1, 1]:
                        for direction in (['fwd', 'back', 'up'] if stance else ['fwd', 'back', 'down', 'up']):
                            result = await c.js('const cfg='+json.dumps(dict(stance=stance, side=side, direction=direction))+r''';
                            dismissTitle();gameMode='2p';spectate=false;cpuMode=false;stagePick='bamboo';p1Pick=2;p2Pick=0;
                            startNewGame();roundIntroTimer=0;paused=true;cutscene=null;hitstopRemaining=0;
                            for(const k in keys)keys[k]=false;physKeys.clear();
                            const p=player1,m=SPRITES.shin,F=m.frames,failures=[],trace=[],snaps=[];
                            Object.assign(p,{x:canvas.width/2-p.width/2,y:GROUND_Y-p.height,isGrounded:true,
                                vx:0,vy:0,facing:cfg.side,kageNui:cfg.stance,state:STATE.IDLE});
                            player2.x=cfg.side>0?canvas.width-70:20;
                            // These existing mechanics must survive an artwork-only removal.
                            const expected={
                                fwd:{art:'ghfwd',dur:420,rec:.40,vx:140,box:[[46,44,5,.08,50,{}],[44,40,5,.16,60,{}],[52,46,7,.26,150,{}]],track:[0,.10,.19,.38,.62,.84]},
                                back:{art:'ghback',dur:400,rec:.42,vx:-220,box:[[120,24,8,.16,110,{}]],track:[0,.10,.22,.40,.62,.84]},
                                down:{art:'ghdown',dur:340,rec:.36,vx:40,box:[[76,20,9,.10,90,{low:true,trip:true}]],track:[0,.12,.29,.50,.70,.88]},
                                up:{art:'ghup',dur:380,rec:.44,vx:30,vy:-300,box:[[40,96,11,.11,100,{up:true,launch:true,launchVy:-360}]],track:[0,.10,.29,.48,.68,.86]}
                            }[cfg.direction],actual=DIR_MOVES['2:'+cfg.direction];
                            for(const k of Object.keys(expected))if(JSON.stringify(actual[k])!==JSON.stringify(expected[k]))failures.push('mechanics changed: '+k);
                            // Use the same executor as CPU combat, including its captured stick.
                            // Up is supplied atomically so a separate jump key cannot preempt it.
                            p.executeAttack(STATE.ATTACK_HEAVY,cfg.direction,{type:STATE.ATTACK_HEAVY,dir:cfg.direction,
                                axis:cfg.direction==='fwd'?1:cfg.direction==='back'?-1:0,
                                up:cfg.direction==='up',down:cfg.direction==='down',ttl:ATTACK_BUFFER});
                            if(p.moveArt!==expected.art||p.state!==STATE.ATTACK_HEAVY)failures.push('wrong move route: '+p.moveArt);
                            if(p.attackAnim?.dur!==expected.dur||p.vx!==cfg.side*expected.vx||p.vy!==(expected.vy||0))failures.push('execution timing or momentum changed');
                            if(p.hitboxes.length!==expected.box.length)failures.push('hit count changed');
                            const row=[];for(let i=1;F[expected.art+i]!==undefined;i++)row.push(F[expected.art+i]);
                            if(row.length!==6||row.some(i=>i>=354&&i<=377))failures.push('retired artwork remains in '+expected.art);
                            // Authored directions were read from full-size source cells,
                            // independently of mirror metadata or gameplay facing.
                            const rightAuthored=new Set([245,246,247,248,317,318,319,320,332,333,334,335,336]);
                            const shot=(label,actor=p)=>{
                                const s=document.createElement('canvas');s.width=240;s.height=240;const g=s.getContext('2d');
                                g.fillStyle='#e6e0d5';g.fillRect(0,0,240,240);g.save();g.translate(120-actor.x-actor.width/2,220-GROUND_Y);
                                const render=drawShodoFrame,transforms=[];
                                drawShodoFrame=function(...args){
                                    if(args[0]===g&&args[1]===m.img)transforms.push({cell:Math.round(args[2]/m.frameW),a:g.getTransform().a});
                                    return render(...args);
                                };
                                try{drawSprite(g,actor);}finally{drawShodoFrame=render;g.restore();}
                                const pix=g.getImageData(0,0,240,240).data;let ink=0;
                                for(let i=0;i<pix.length;i+=4)if(pix[i]!==230||pix[i+1]!==224||pix[i+2]!==213)ink++;
                                const body=transforms.filter(t=>t.cell===actor.drawCell).at(-1);
                                const visualFacing=body?Math.sign(body.a)*(rightAuthored.has(actor.drawCell)?1:-1):null;
                                const sample={label,cell:actor.drawCell,state:actor.state,ground:actor.isGrounded,
                                    facing:actor.facing,mirror:actor.drawMirror,renderA:body?.a,visualFacing,ink};
                                if(ink<100)failures.push('invisible body: '+label);
                                if(actor.drawCell>=354&&actor.drawCell<=377)failures.push('retired cell '+actor.drawCell+' at '+label);
                                if(actor.isAttackingState()&&visualFacing!==cfg.side)failures.push('rendered facing '+visualFacing+' at '+label+' cell '+actor.drawCell);
                                snaps.push(s);trace.push(sample);return sample;
                            };
                            // Related source-row siblings must also face correctly through
                            // their actual picker routes (neutral Heavy, rising Special, kick).
                            if(!cfg.stance&&cfg.direction==='fwd'){
                                for(const [family,beat,state] of [['hneu',4,STATE.ATTACK_HEAVY],['hneu',5,STATE.ATTACK_HEAVY],
                                    ['srisaa',5,STATE.ATTACK_SPECIAL],['kpush',2,STATE.ATTACK_LIGHT],
                                    ['kpush',3,STATE.ATTACK_LIGHT],['kpush',4,STATE.ATTACK_LIGHT]]){
                                    const row=[];for(let n=1;F[family+n]!==undefined;n++)row.push(F[family+n]);
                                    const count=row.length,t=count===5
                                        ?(ATTACK_EXPOSURES_5[beat-1]+(ATTACK_EXPOSURES_5[beat]??1))/2
                                        :(beat-.5)/count;
                                    const actor=Object.assign(Object.create(p),{state,kageNui:false,attackAir:false,
                                        attackDir:family==='srisaa'?'up':null,moveArt:family==='srisaa'?'srisaa':null,
                                        moveTrack:null,kickKind:family==='kpush'?'push':null,attackAnim:{start:animClock*1000-t*1000,dur:1000},
                                        isGrounded:family!=='srisaa',ghosts:[],clone:null});
                                    const s=shot(family+' sibling '+beat,actor);
                                    if(s.cell!==row[beat-1])failures.push('wrong sibling route '+family+' beat '+beat+' cell '+s.cell);
                                }
                            }
                            const original=p.attackAnim&&{...p.attackAnim};
                            if(original){
                                for(let i=0;i<6;i++){
                                    const t=(expected.track[i]+(expected.track[i+1]??1))/2;
                                    p.attackAnim={...original,start:animClock*1000-t*original.dur};
                                    const s=shot('slot '+(i+1));if(s.cell!==row[i])failures.push('slot '+(i+1)+' routed '+s.cell);
                                }
                                p.attackAnim={...original,start:animClock*1000};
                                paused=false;
                                await new Promise(resolve=>{let n=0;function tick(){shot('live '+n);if(++n<42)requestAnimationFrame(tick);else resolve();}requestAnimationFrame(tick);});
                            }
                            paused=true;
                            const board=document.createElement('canvas');board.width=6*240;board.height=Math.ceil(snaps.length/6)*262;
                            const g=board.getContext('2d');g.fillStyle='#e6e0d5';g.fillRect(0,0,board.width,board.height);
                            snaps.forEach((s,i)=>{const x=i%6*240,y=Math.floor(i/6)*262;g.drawImage(s,x,y+22);g.fillStyle='#151515';g.font='12px sans-serif';g.fillText(trace[i].label+' / cell '+trace[i].cell,x+4,y+15);});
                            return {cfg,row,failures:[...new Set(failures)],trace,png:board.toDataURL().split(',')[1]};
                            ''')
                            assert result and '__error' not in result, result
                            label = f"{'stance' if stance else 'base'}-{side}-{direction}"
                            (out/(label+'.png')).write_bytes(base64.b64decode(result.pop('png')))
                            results.append(result)
                            print(label, result['failures'], flush=True)
        finally:
            proc.terminate()
            proc.wait(timeout=10)
    (out/'checks.json').write_text(json.dumps(results, indent=2))
    assert not any(r['failures'] for r in results), str(out/'checks.json')


if __name__ == '__main__':
    asyncio.run(main())
