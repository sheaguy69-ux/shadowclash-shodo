#!/usr/bin/env python3
"""Drive contact stays rigid without the rejected white trail; preserve Footsies FX."""
import asyncio
import hashlib
import json
import os
import tempfile
from pathlib import Path

import websockets
import watch_game as browser


CHECK = r'''
dismissTitle();const failures=[],cases=[];
const check=(ok,message)=>{if(!ok)failures.push(message);};
const near=(a,b)=>Math.abs(a-b)<1e-4;
const key=(code,on)=>window.dispatchEvent(new KeyboardEvent(on?'keydown':'keyup',{code,bubbles:true}));
const plate=document.createElement('canvas');plate.width=1200;plate.height=900;const g=plate.getContext('2d');
const nativeDraw=g.drawImage,oldShodo=drawShodoFrame,oldProcess=processHitboxes;
let fx=[],bodies=[],probes=[],subject=null;
g.drawImage=function(...args){
 if(args[0]===FX_CRESCENT.img){
  const m=g.getTransform(),[x,y,w,h]=args.slice(-4);
  const xs=[m.a*x+m.c*y+m.e,m.a*(x+w)+m.c*(y+h)+m.e];
  const ys=[m.b*x+m.d*y+m.f,m.b*(x+w)+m.d*(y+h)+m.f];
  fx.push({x:Math.min(...xs),y:Math.min(...ys),w:Math.abs(xs[1]-xs[0]),h:Math.abs(ys[1]-ys[0]),mirror:m.a});
 }
 return nativeDraw.apply(this,args);
};
drawShodoFrame=function(...args){
 if(args[0]===g){const m=g.getTransform(),sx=args[8]/args[4],sy=args[9]/args[5];
  const u=[m.a*sx,m.b*sx],v=[m.c*sy,m.d*sy];
  bodies.push({cell:args[2]/args[4],scaleX:Math.hypot(...u),scaleY:Math.hypot(...v),dot:u[0]*v[0]+u[1]*v[1]});}
 return oldShodo.apply(this,args);
};
processHitboxes=function(a,b,dt,advance=true){
 const hits=a===subject?a.hitboxes.filter(h=>h.delay<=0&&h.duration>0):[];
 const out=oldProcess.apply(this,arguments);
 for(const h of hits)if(!h.strikeInactive)probes.push({x:a.x+h.ox,y:a.y+h.oy,w:h.w,h:h.h,
  damage:h.damage,push:h.pushback,lastActiveAt:h.poseWindow?.lastActiveAt});
 return out;
};
const render=()=>{fx=[];bodies=[];g.clearRect(0,0,1200,900);drawSprite(g,subject);return {fx:structuredClone(fx),bodies:structuredClone(bodies)};};
try{
 for(const route of ['drive','footsies'])for(const face of [-1,1])for(const scenario of route==='drive'?['whiff','hit','block']:['whiff']){
  gameMode='2p';cpuMode=false;spectate=false;stagePick='bamboo';p1Pick=0;p2Pick=1;startNewGame();
  paused=false;roundIntroTimer=0;cutscene=null;hitstopRemaining=0;releaseAllKeys();
  const p=subject=player1,d=player2;
  Object.assign(p,{x:face>0?450:canvas.width-450-p.width,y:GROUND_Y-p.height,vx:0,vy:0,isGrounded:true,facing:face});
  Object.assign(d,{x:p.x+face*(scenario==='whiff'?300:55),y:GROUND_Y-d.height,vx:0,vy:0,isGrounded:true,facing:-face});
  if(scenario==='block'){key('KeyM',true);for(let k=0;k<20;k++)updateGame(1/(60*COMBAT_TEMPO));}
  key(face>0?'KeyD':'KeyA',true);key(route==='drive'?'KeyG':'KeyF',true);key(route==='drive'?'KeyG':'KeyF',false);
  const label=`${route}/${face}/${scenario}`,frames=[];let active=0,removed=0,frozen=0;
  for(let n=1;n<=32;n++){
   probes=[];updateGame(n===1?0:1/(60*COMBAT_TEMPO));
   const art=footsiesFrame(p),expected=route==='footsies'&&art?.hitbox?footsiesRect(p,art.hitbox):route==='drive'?probes[0]:null;
   const r=render(),tag=label+'/F'+n,expectedTrail=route==='footsies'&&!!expected;
   check(r.fx.length===(expectedTrail?1:0),tag+': expected '+(expectedTrail?1:0)+' trail, got '+r.fx.length);
   if(expected){active++;const f=r.fx[0];if(f)for(const k of ['x','y','w','h'])check(near(f[k],expected[k]),tag+': trail/contact '+k);
    if(f)check(Math.sign(f.mirror)===face,tag+': wrong trail facing');
    if(route==='drive'){
     check(p.drawCell===296,tag+': contact drawing '+p.drawCell);
     check(near(expected.w,158)&&near(expected.h,24)&&near(expected.damage,21)&&near(expected.push,160),tag+': changed authored offense');
     check(expected.lastActiveAt===animClock,tag+': stale contact stamp');
     if(!p.hitboxes.length)removed++;
    }
    if(hitstopRemaining>0){const again=render();check(JSON.stringify(again)===JSON.stringify(r),tag+': frozen contact draw drift');frozen++;}
   }
   for(const b of r.bodies)check(near(b.scaleX,b.scaleY)&&Math.abs(b.dot)<1e-6,tag+': non-rigid body');
   if(route==='drive')check(slashes.length===0,tag+': duplicate generic W02 trail');
   frames.push({sample:n,clock:animClock,state:p.state,cell:p.drawCell,hp:d.hp,hitstop:hitstopRemaining,
    position:{x:p.x,y:p.y},velocity:{x:p.vx,y:p.vy},recovery:p.recoveryTimer,attackDuration:p.attackAnim?.dur??null,
    expected,expectedTrail,render:r,queued:p.hitboxes.length});
  }
  check(active>0,label+': no active samples');
  if(route==='drive'&&scenario==='whiff')check(removed>0,label+': final removed-hitbox tick untested');
  if(route==='drive'&&scenario!=='whiff')check(frozen>0,label+': no real hitstop exercised');
  cases.push({route,face,scenario,active,removed,frozen,frames});releaseAllKeys();
 }
}finally{g.drawImage=nativeDraw;drawShodoFrame=oldShodo;processHitboxes=oldProcess;paused=true;releaseAllKeys();}
return {sheetVersion:SHEET_V,failures,cases,timing:'32 consecutive 60Hz game-time samples. Repeated unchanged-clock draw during engine-created hitstop verifies frozen contact rendering; no visual timer is forced.'};
'''


async def main():
    root = Path(__file__).resolve().parents[1]
    url = os.environ.get('SHADOWCLASH_URL', 'http://localhost:9101/index.html')
    browser.assert_serving_this_tree(url)
    source = (root / 'web/index.html').read_bytes()
    browser.PORT = int(os.environ.get('DEBUG_PORT', '9392'))
    with tempfile.TemporaryDirectory(prefix='executioner-drive-trail-') as profile:
        proc, address = browser.launch(url, profile)
        try:
            async with websockets.connect(address, max_size=100_000_000) as ws:
                c = browser.CDP(ws)
                for _ in range(400):
                    if await c.js("return typeof SPRITES!=='undefined'&&NINJA_ROSTER.every(s=>SPRITES[s.name.toLowerCase()]?.ready)&&FX_CRESCENT.ready"):
                        break
                    await asyncio.sleep(.1)
                else:
                    raise AssertionError('roster/FX failed to load')
                result = await c.js(CHECK)
                assert result and '__error' not in result, result
                assert source == (root / 'web/index.html').read_bytes(), 'source changed during test'
                result['source_sha256'] = hashlib.sha256(source).hexdigest()
                out = root / 'media/executioner-drive-reach-20260908/trail-removed-check.json'
                out.parent.mkdir(parents=True, exist_ok=True)
                out.write_text(json.dumps(result, indent=2, allow_nan=False))
                assert not result['failures'], result['failures']
                print(f"PASS: {len(result['cases'])} real-input cases,256 samples; no Drive white trail, contact pose/removed tick/hitstop/rigid body/offense preserved, original Footsies trail intact")
        finally:
            proc.terminate()
            proc.wait(timeout=10)


if __name__ == '__main__':
    asyncio.run(main())
