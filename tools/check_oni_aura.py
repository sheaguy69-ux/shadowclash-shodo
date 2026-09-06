#!/usr/bin/env python3
"""Check Oni's native moving aura, frozen clock and roster isolation on :9101."""
import asyncio
import base64
import io
import json
import os
import tempfile
from pathlib import Path

from PIL import Image
import websockets
import watch_game as browser


async def main():
    url = 'http://localhost:9101/index.html'
    browser.assert_serving_this_tree(url)
    out = Path(os.environ.get('OUT', 'media/oni-aura-cutoff-20260906/live'))
    out.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='oni-aura-check-') as profile:
        proc, addr = browser.launch(url, profile)
        try:
            async with websockets.connect(addr, max_size=50*1024*1024) as ws:
                c = browser.CDP(ws)
                for _ in range(500):
                    if await c.js("return typeof SPRITES!=='undefined'&&FX_ONI_AURA.ready&&NINJA_ROSTER.every(s=>SPRITES[s.name.toLowerCase()]?.ready)"):
                        break
                    await asyncio.sleep(.1)
                else:
                    raise AssertionError('roster did not load')
                result = await c.js(r'''
                dismissTitle();gameMode='2p';spectate=false;cpuMode=false;stagePick='bamboo';
                p1Pick=8;p2Pick=2;startNewGame();roundIntroTimer=0;paused=true;cutscene=null;hitstopRemaining=0;
                const p=player1,m=SPRITES.oni,failures=[],calls=[],original=drawOniAura;
                drawOniAura=function(g,p,...rest){calls.push(p.spec.id);return original(g,p,...rest);};
                const shot=()=>{
                    const s=document.createElement('canvas');s.width=300;s.height=250;
                    const g=s.getContext('2d');g.fillStyle='#25323a';g.fillRect(0,0,300,250);
                    g.save();g.translate(150-p.x-p.width/2,223-p.y-p.height);drawSprite(g,p);g.restore();return s;
                };
                const g=document.createElement('canvas').getContext('2d');drawSprite(g,player2);shot();
                if(calls.length!==1||calls[0]!==8)failures.push('aura is not isolated to Oni');
                const fixed=shot().toDataURL();
                if(shot().toDataURL()!==fixed)failures.push('aura changes with frozen combat clock');
                const auraAt=t=>{
                    const s=document.createElement('canvas');s.width=300;s.height=250;
                    const g=s.getContext('2d');g.translate(150,223);animClock=t;
                    drawOniAura(g,p,m,m.frames.idle,m.scale*SHODO_DISPLAY_SCALE);return s.toDataURL();
                };
                // Aura follows actual air-pose registration, not the floor beneath it.
                for (const idx of [m.frames.idle,m.frames.dive3,m.frames.airhurt2]) {
                    const s=document.createElement('canvas'),g=s.getContext('2d'),moves=[];
                    const shift=g.translate.bind(g);g.translate=(x,y)=>{moves.push([x,y]);shift(x,y);};
                    const scale=m.scale*SHODO_DISPLAY_SCALE*(m.frameScale?.[idx]??1),b=cellInk(m,idx);
                    original(g,p,m,idx,scale);
                    const cy=((b.y0+b.y1+1)/2-m.footY+(m.footAdj?.[idx]||0))*scale;
                    if(Math.abs(moves[0][1]-cy)>.01)failures.push('aura below airborne pose '+idx);
                }
                const drawn=drawShodoFrame;let oldGlow=false;
                drawShodoFrame=(...a)=>{oldGlow ||= a[0].shadowBlur>0;return drawn(...a);};
                shot();drawShodoFrame=drawn;
                if(oldGlow)failures.push('old Oni shadow aura still draws');
                const saved=animClock,stages=[0,.15,.3,.45,.6,.75].map(t=>auraAt(t));animClock=saved;
                if(new Set(stages).size!==stages.length)failures.push('aura is static');
                for(const k in keys)keys[k]=false;physKeys.clear();p.x=420;player2.x=850;
                const frames=[],trace=[];paused=false;
                await new Promise(resolve=>{let n=0;function tick(){
                    if(n%4===0){frames.push(shot().toDataURL().split(',')[1]);trace.push({clock:animClock,cell:p.drawCell,x:p.x,y:p.y});}
                    if(++n<96)requestAnimationFrame(tick);else resolve();
                }requestAnimationFrame(tick);});paused=true;drawOniAura=original;
                if(trace[trace.length-1].clock<=trace[0].clock)failures.push('live combat clock did not advance');
                return {failures,trace,frames};
                ''')
                assert result and '__error' not in result, result
                frames = [Image.open(io.BytesIO(base64.b64decode(s))).convert('RGB') for s in result.pop('frames')]
                trace = result['trace']
                durations = [max(20, round((b['clock']-a['clock'])*1000/1.2)) for a,b in zip(trace,trace[1:])]
                durations.append(durations[-1])
                frames[0].save(out/'aura.gif', save_all=True, append_images=frames[1:], duration=durations, loop=0)
                board = Image.new('RGB', (300*6, 250*4))
                for i, frame in enumerate(frames):
                    board.paste(frame, (i%6*300, i//6*250))
                board.save(out/'consecutive.png')
                (out/'checks.json').write_text(json.dumps(result, indent=2)+'\n')
                print(json.dumps({'frames':len(frames),'failures':result['failures']}))
                assert not result['failures'], result['failures']
        finally:
            proc.terminate()
            proc.wait(timeout=10)


if __name__ == '__main__':
    asyncio.run(main())
