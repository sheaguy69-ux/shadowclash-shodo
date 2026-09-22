#!/usr/bin/env python3
"""Live input → contact-pose regression for eight roster kits, both facings."""
import asyncio, json, os, tempfile
from pathlib import Path
import websockets
import watch_game as browser

async def main():
    url=os.environ.get('SHADOWCLASH_URL','http://localhost:9101/index.html')
    browser.assert_serving_this_tree(url)
    browser.PORT=int(os.environ.get('DEBUG_PORT','9392'))
    with tempfile.TemporaryDirectory(prefix='roster-strikes-') as profile:
        proc,address=browser.launch(url,profile)
        try:
            async with websockets.connect(address,max_size=100_000_000) as ws:
                c=browser.CDP(ws)
                for _ in range(400):
                    if await c.js("return typeof SPRITES!=='undefined'&&NINJA_ROSTER.every(s=>SPRITES[s.name.toLowerCase()]?.ready)"):break
                    await asyncio.sleep(.1)
                result=await c.js(r'''
                dismissTitle();const failures=[],samples=[];
                const check=(ok,msg)=>{if(!ok)failures.push(msg);};
                const expected={
                  1:[[11,12,13],[113],[193],[168,169,170,171,172]],
                  2:[[261],[246],[261,246],null],
                  3:[[368],[355,356],[176,177,178],null],
                  4:[[269],[150,151],[287,288],[277,278,279]],
                  5:[[236],[236],[205,206,207],[257,258,259]],
                  6:[[374,375],[374,375],[375],[360]],
                  7:[[325],[396],[332],[394]],
                  8:[[527,528],[584,585],[657,658],null]
                };
                const oldProcess=processHitboxes;let probe=[];
                processHitboxes=function(a,b,dt,advance=true){
                  const hits=a===player1?a.hitboxes.filter(h=>h.delay<=0&&h.duration>0):[];
                  const out=oldProcess.apply(this,arguments);
                  if(a===player1)probe.push(...hits);return out;
                };
                try{for(let id=1;id<=8;id++)for(const facing of [-1,1])for(let route=0;route<4;route++){
                  gameMode='2p';cpuMode=false;spectate=false;stagePick='bamboo';p1Pick=id;p2Pick=0;
                  startNewGame();paused=false;roundIntroTimer=0;cutscene=null;hitstopRemaining=0;releaseAllKeys();
                  const p=player1,d=player2,man=SPRITES[p.spec.name.toLowerCase()];
                  Object.assign(p,{x:facing>0?450:canvas.width-450-p.width,y:GROUND_Y-p.height,vx:0,vy:0,isGrounded:true,facing});
                  Object.assign(d,{x:p.x+facing*400,y:GROUND_Y-d.height,vx:0,vy:0,isGrounded:true,facing:-facing});
                  const key=(code,on)=>window.dispatchEvent(new KeyboardEvent(on?'keydown':'keyup',{code,bubbles:true}));
                  if(route)key(facing>0?'KeyD':'KeyA',true);
                  const code=['KeyF','KeyF','KeyG','KeyH'][route];key(code,true);key(code,false);
                  let first=null,contacts=0;const cells=[];let initialAnim=p.attackAnim;
                  for(let frame=1;frame<=90;frame++){
                    probe=[];updateGame(frame===1?0:1/(60*COMBAT_TEMPO));
                    if(frame===1)initialAnim=p.attackAnim;
                    else if(p.attackAnim!==initialAnim && contacts>0)break;
                    probe=probe.filter(h=>!h.strikeInactive);
                    if(!probe.length)continue;
                    const cell=spriteFrameIndex(p,man.frames);cells.push(cell);first??=frame;contacts++;
                    const label=`${p.spec.name} route${route} face${facing} F${frame}`;
                    if(expected[id][route])check(expected[id][route].includes(cell),`${label}: recovery/wrong cell ${cell}`);
                    for(const h of probe){
                      check([h.ox,h.oy,h.w,h.h].every(Number.isFinite)&&h.w>0&&h.h>0,`${label}: invalid geometry`);
                      check(!h.poseWindow||h.poseWindow.lastActiveAt===animClock,`${label}: missing contact stamp`);
                    }
                  }
                  if(expected[id][route])check(contacts>0,`${id}/${route}/${facing} never attacks`);
                  if(route===0)check(first!==null&&first>=3&&first<=5,`${id}: basic light startup ${first-1}`);
                  samples.push({id,facing,route,first,contacts,cells});
                }}finally{processHitboxes=oldProcess;paused=true;releaseAllKeys();}
                return {failures,samples};
                ''')
                assert result and '__error' not in result,result
                out=Path('media/roster-footsies-20260907/strike-check.json');out.parent.mkdir(parents=True,exist_ok=True)
                out.write_text(json.dumps(result,indent=2))
                assert not result['failures'],result['failures']
                print('PASS: 64 real-input core attacks; contact poses, finite strike geometry, fast ground lights')
        finally:proc.terminate();proc.wait(timeout=10)

if __name__=='__main__':asyncio.run(main())
