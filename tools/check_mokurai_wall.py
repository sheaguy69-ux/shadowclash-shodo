#!/usr/bin/env python3
"""Verify Mokurai's held wall pose and actual hand/sole contact on both sides."""
import asyncio,base64,json,tempfile
from pathlib import Path
import websockets
import watch_game as b
async def main():
 out=Path('media/mokurai-audit-20260906/wall');out.mkdir(parents=True,exist_ok=True)
 b.assert_serving_this_tree('http://localhost:9101/index.html')
 with tempfile.TemporaryDirectory() as profile:
  proc,address=b.launch('http://localhost:9101/index.html',profile)
  try:
   async with websockets.connect(address,max_size=12000000) as ws:
    c=b.CDP(ws)
    for _ in range(400):
     if await c.js("return typeof SPRITES!=='undefined'&&SPRITES.mokurai?.ready"):break
     await asyncio.sleep(.1)
    r=await c.js(r'''
    dismissTitle();p1Pick=6;p2Pick=0;startNewGame();paused=true;roundIntroTimer=0;
    const p=player1,m=SPRITES.mokurai,checks=[];
    const board=document.createElement('canvas');board.width=800;board.height=600;const g=board.getContext('2d');g.fillStyle='#87959d';g.fillRect(0,0,800,600);
    for(const side of [-1,1])for(const vy of [0,180]){
      const tile=document.createElement('canvas');tile.width=400;tile.height=400;const t=tile.getContext('2d',{willReadFrequently:true});
      Object.assign(p,{x:170,y:190-p.height,vx:0,vy,facing:-side,wallDir:side,state:STATE.WALL_CLING,isGrounded:false,animPhase:6,attackAnim:null,hitFlashT:0,landSquash:0,ghosts:[],clone:null,lean:0});
      drawSprite(t,p);const cell=p.drawCell,S=m.scale*SHODO_DISPLAY_SCALE*(p.spec.renderScale||1),wall=p.x+(side>0?p.width:0),pixels=t.getImageData(0,0,400,400).data;
      const gaps=[];
      for(const [a,z] of [[90,112],[154,179],[190,216]]){
        let gap=Infinity;
        for(let y=Math.floor(190+(a-218)*S);y<=Math.ceil(190+(z-218)*S);y++)for(let x=0;x<400;x++)if(pixels[(y*400+x)*4+3]>128)gap=Math.min(gap,Math.abs(x-wall));
        gaps.push(gap);
      }
      checks.push({side,vy,cell,gaps});
      const ox=(side+1)/2*400,oy=vy?300:0;g.save();g.translate(ox+200-wall*2,oy-100);g.scale(2,2);g.drawImage(tile,0,0);g.fillStyle='#ebce8d';g.fillRect(wall,0,side*2,400);g.restore();g.fillStyle='#111';g.font='15px sans-serif';g.fillText((side<0?'Left':'Right')+' wall / '+(vy?'slide':'catch'),ox+20,oy+290);
    }
    return {checks,png:board.toDataURL().split(',')[1]};
    ''')
    (out/'contacts.png').write_bytes(base64.b64decode(r.pop('png')));(out/'checks.json').write_text(json.dumps(r,indent=2));print(r)
    assert all(x['cell']==387 and max(x['gaps'])<=3 for x in r['checks']),r
  finally:proc.kill();proc.wait()
if __name__=='__main__':asyncio.run(main())
