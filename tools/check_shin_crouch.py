#!/usr/bin/env python3
"""Verify Shin's approved low crouch and rigid crouch rendering through real inputs."""
import asyncio
import base64
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

import websockets
import watch_game as browser


async def main():
    url = os.environ.get('SHADOWCLASH_URL', 'http://localhost:9101/index.html')
    browser.assert_serving_this_tree(url)
    browser.PORT = int(os.environ.get('DEBUG_PORT', '9372'))
    with tempfile.TemporaryDirectory(prefix='shin-crouch-') as profile:
        proc, address = browser.launch(url, profile)
        try:
            async with websockets.connect(address, max_size=100_000_000) as ws:
                c = browser.CDP(ws)
                for _ in range(400):
                    if await c.js("return typeof SPRITES!=='undefined'&&NINJA_ROSTER.every(s=>SPRITES[s.name.toLowerCase()]?.ready)"):
                        break
                    await asyncio.sleep(.1)
                result = await c.js(r'''
                dismissTitle();const failures=[],samples=[],idle=[];
                const check=(ok,msg)=>{if(!ok&&!failures.includes(msg))failures.push(msg);};
                const key=(code,down)=>window.dispatchEvent(new KeyboardEvent(down?'keydown':'keyup',{code,bubbles:true}));
                const plate=document.createElement('canvas');plate.width=1200;plate.height=850;
                const ctx=plate.getContext('2d');
                const setup=(id=2,facing=1)=>{
                    gameMode='2p';cpuMode=false;spectate=false;stagePick='bamboo';p1Pick=id;p2Pick=id===0?1:0;
                    startNewGame();paused=false;roundIntroTimer=0;hitstopRemaining=0;cutscene=null;releaseAllKeys();
                    Object.assign(player1,{x:450,y:GROUND_Y-player1.height,vx:0,vy:0,state:STATE.IDLE,isGrounded:true,jumpsLeft:2,facing});
                    player2.x=facing>0?800:150;return player1;
                };
                const sample=(p,label,expectCell)=>{
                    const man=SPRITES[p.spec.name.toLowerCase()],calls=[],original=drawShodoFrame;
                    drawShodoFrame=function(...a){
                        if(a[1]===man.img){const m=a[0].getTransform();calls.push({cell:a[2]/man.frameW,x:Math.hypot(m.a,m.b)*a[8]/a[4],y:Math.hypot(m.c,m.d)*a[9]/a[5],mirror:Math.sign(m.a),shear:m.b+m.c});}
                        return original.apply(this,a);
                    };
                    try{ctx.clearRect(0,0,plate.width,plate.height);drawSprite(ctx,p);}finally{drawShodoFrame=original;}
                    const actual=calls.at(-1),scale=man.scale*SHODO_DISPLAY_SCALE*(p.spec.renderScale||1)*(man.frameScale?.[p.drawCell]??1);
                    check(!!actual,label+' no sprite draw');if(!actual)return;
                    if(expectCell!==undefined)check(p.drawCell===expectCell,label+' wrong pose '+p.drawCell);
                    check(Math.abs(actual.x-scale)<1e-8&&Math.abs(actual.y-scale)<1e-8,label+' nonuniform crouch scale');
                    check(Math.abs(actual.shear)<1e-8,label+' crouch shear');
                    samples.push({label,cell:p.drawCell,scaleX:actual.x,scaleY:actual.y,scale,facing:p.facing,mirror:actual.mirror,landSquash:p.landSquash});
                };
                for(const facing of [-1,1]){
                    let p=setup(2,facing);key('KeyS',true);
                    for(let tick=0;tick<90;tick++){
                        updateGame(1/60);check(p.state===STATE.CROUCH,'Shin Down failed to crouch');
                        check(p.facing===facing,'Shin crouch faces away');
                        if([0,1,3,5,15,45,89].includes(tick))sample(p,'Shin held '+facing+' '+tick,346);
                    }
                    key('KeyS',false);updateGame(1/60);check(p.state===STATE.IDLE,'Shin Down release stuck');
                    const F=SPRITES.shin.frames;
                    for(let phase=0;phase<12;phase+=2){p.animPhase=phase;idle.push(spriteFrameIndex(p,F));}
                    p=setup(2,facing);key('KeyW',true);
                    for(let n=0;n<8;n++)updateGame(1/60);key('KeyW',false);key('KeyS',true);
                    let landed=false;
                    for(let n=0;n<80;n++){
                        updateGame(1/60);
                        if(p.state===STATE.CROUCH){
                            check(p.landSquash>0,'landing setup has no squash');sample(p,'Shin landing '+facing,346);landed=true;break;
                        }
                    }
                    check(landed,'Shin landing never crouched');
                    for(let n=0;n<8;n++){updateGame(1/60);sample(p,'Shin settle '+facing+' '+n,346);}
                }
                check(JSON.stringify(idle)===JSON.stringify([346,347,348,349,348,347,346,347,348,349,348,347]),'Shin idle loop changed');
                // Landing must not flatten any authored crouch. Mizu's idle fallback is a separate art choice.
                for(let id=0;id<9;id++){
                    const p=setup(id);if(SPRITES[p.spec.name.toLowerCase()].frames.crouch_1===undefined)continue;
                    key('KeyS',true);for(let n=0;n<12;n++)updateGame(1/60);
                    sample(p,'roster '+id);p.landSquash=1;sample(p,'roster landing '+id);
                }
                paused=true;releaseAllKeys();return{failures,idle,samples};
                ''')
                assert result and '__error' not in result, result
                out = Path(os.environ.get('OUT', 'media/shin-crouch-20260907'))
                out.mkdir(parents=True, exist_ok=True)
                (out/'checks.json').write_text(json.dumps(result, indent=2))
                assert not result['failures'], result['failures']
                print(f"PASS: {len(result['samples'])} crouch render samples; real Down hold/release and landing both facings; authored crouch transforms; unchanged Shin idle")
                if '--film' in sys.argv:
                    clips = await c.js(r'''
                    const clips={},key=(code,down)=>window.dispatchEvent(new KeyboardEvent(down?'keydown':'keyup',{code,bubbles:true}));
                    const preview=document.createElement('canvas');preview.width=1000;preview.height=470;
                    const g=preview.getContext('2d');
                    for(const kind of ['hold-release','landing']){
                        gameMode='2p';cpuMode=false;spectate=false;stagePick='bamboo';p1Pick=p2Pick=2;
                        startNewGame();paused=false;roundIntroTimer=0;hitstopRemaining=0;cutscene=null;releaseAllKeys();
                        for(const [p,x,facing] of [[player1,350,1],[player2,610,-1]])
                            Object.assign(p,{x,y:GROUND_Y-p.height,isGrounded:true,_wasGrounded:true,state:STATE.IDLE,vx:0,vy:0,facing,landT:0});
                        const frames=[];
                        for(let tick=0;tick<84;tick++){
                            if(kind==='hold-release'){
                                if(tick===12){key('KeyS',true);key('ArrowDown',true);}
                                if(tick===60){key('KeyS',false);key('ArrowDown',false);}
                            }else{
                                if(tick===3){key('KeyW',true);key('ArrowUp',true);}
                                if(tick===13){key('KeyW',false);key('ArrowUp',false);key('KeyS',true);key('ArrowDown',true);}
                            }
                            updateGame(1/60);drawScene();
                            if(tick%2===0){
                                g.drawImage(canvas,245,GROUND_Y-220,500,235,0,0,1000,470);
                                g.fillStyle='rgba(8,12,18,0.8)';g.fillRect(0,0,1000,38);
                                g.fillStyle='#f0eee5';g.font='18px sans-serif';g.textAlign='center';
                                g.fillText('SHIN · '+(kind==='landing'?'jump → crouch landing':'crouch entry · hold · release')+' · game render at 2×',500,25);
                                frames.push(preview.toDataURL().split(',')[1]);
                            }
                        }
                        clips[kind]=frames;
                    }
                    paused=true;releaseAllKeys();return clips;
                    ''')
                    for name, encoded in clips.items():
                        frames = out/name
                        frames.mkdir(exist_ok=True)
                        for i, png in enumerate(encoded):
                            (frames/f'{i:03}.png').write_bytes(base64.b64decode(png))
                        subprocess.run(['ffmpeg','-y','-loglevel','error','-framerate','30','-i',str(frames/'%03d.png'),
                                        '-filter_complex','split[a][b];[a]palettegen[p];[b][p]paletteuse',
                                        '-loop','0',str(out/f'{name}.gif')],check=True)
                    (out/'approved-crouch.png').write_bytes(base64.b64decode(clips['hold-release'][20]))
                    print(f'Previews: {out}/hold-release.gif, {out}/landing.gif, {out}/approved-crouch.png')
        finally:
            proc.terminate()
            proc.wait(timeout=10)


if __name__ == '__main__':
    asyncio.run(main())
