#!/usr/bin/env python3
"""Exercise wall entry/release on both sides and verify Ember-only debris."""
import asyncio,base64,json,tempfile
from pathlib import Path
import websockets
import watch_game as b
async def main():
 out=Path('media/ember-wall-20260906');out.mkdir(exist_ok=True,parents=True)
 b.assert_serving_this_tree('http://localhost:9101/index.html');b.PORT=9338
 with tempfile.TemporaryDirectory() as profile:
  proc,address=b.launch('http://localhost:9101/index.html',profile)
  try:
   async with websockets.connect(address,max_size=12000000) as ws:
    c=b.CDP(ws)
    for _ in range(400):
     if await c.js("return typeof SPRITES!=='undefined'&&SPRITES.ember?.ready"):break
     await asyncio.sleep(.1)
    r=await c.js('''
    dismissTitle();gameMode='2p';spectate=false;cpuMode=false;p1Pick=4;p2Pick=0;startNewGame();paused=true;roundIntroTimer=0;
    const checks=[],board=document.createElement('canvas');board.width=800;board.height=400;const g=board.getContext('2d');g.fillStyle='#87959d';g.fillRect(0,0,800,400);
    for(const p of [player1,player2])for(const side of [-1,1]){
      particles.length=0;
      Object.assign(p,{x:side<0?10:canvas.width-10-p.width,y:GROUND_Y-p.height-150,vx:side*60,vy:0,wallDir:0,inputAxis:side,isGrounded:false,state:STATE.JUMP,stunTimer:0,stamina:100,clingTime:0,anchorTimer:0,attackAnim:null});
      p.applyPhysics(1/60);
      const first=particles.filter(q=>q.type==='gravel').length;
      const inward=particles.every(q=>q.type!=='gravel'||q.vx*side<0);
      for(let i=0;i<12;i++)p.applyPhysics(1/60);
      const hold=particles.filter(q=>q.type==='gravel').length;
      if(p.spec.id===4){
        const wall=p.x+(side>0?p.width:0);g.save();g.translate((side<0?180:620)-wall*2,310-(p.y+p.height)*2);g.scale(2,2);drawSprite(g,p);g.fillStyle='#ddc391';g.fillRect(wall,0,side*3,1000);g.restore();
      }
      p.inputAxis=0;p.applyPhysics(1/60);p.inputAxis=side;p.applyPhysics(1/60);
      checks.push({id:p.spec.id,side,first,hold,inward,regrip:particles.filter(q=>q.type==='gravel').length,wall:p.wallDir});
    }
    return {checks,png:board.toDataURL().split(',')[1]};
    ''')
    (out/'contacts.png').write_bytes(base64.b64decode(r.pop('png')));print(r)
    for x in r['checks']:
     n=10 if x['id']==4 else 0
     assert x['first']==n and x['hold']==n and x['regrip']==2*n and x['inward'] and x['wall']==x['side'],x
    (out/'checks.json').write_text(json.dumps(r,indent=2))
    clip=await c.js("""
    const p=player1;for(const k in keys)keys[k]=false;
    keys.KeyA=true;physKeys.clear();physKeys.add('KeyA');
    Object.assign(p,{x:11,y:GROUND_Y-p.height-150,vx:-100,vy:0,wallDir:0,inputAxis:-1,isGrounded:false,state:STATE.JUMP,stamina:100,clingTime:0});
    particles.length=0;const strip=document.createElement('canvas');strip.width=1600;strip.height=240;const t=strip.getContext('2d');
    for(let i=0;i<8;i++){for(let j=0;j<3;j++)updateGame(1/60);drawScene();t.drawImage(canvas,0,Math.max(0,p.y-80),200,240,i*200,0,200,240);}
    return strip.toDataURL().split(',')[1];
    """)
    (out/'live-strip.png').write_bytes(base64.b64decode(clip))
  finally:proc.kill();proc.wait()
if __name__=='__main__':asyncio.run(main())
