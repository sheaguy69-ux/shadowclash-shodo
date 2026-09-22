#!/usr/bin/env python3
"""Actual idle picker must exclude the owner's rejected standing peaks."""
import asyncio,base64,tempfile
from pathlib import Path
import websockets
import watch_game as b
async def main():
 b.PORT=9338;b.assert_serving_this_tree('http://localhost:9101/index.html')
 with tempfile.TemporaryDirectory() as profile:
  proc,address=b.launch('http://localhost:9101/index.html',profile)
  try:
   async with websockets.connect(address,max_size=12000000) as ws:
    c=b.CDP(ws)
    for _ in range(400):
     if await c.js("return typeof SPRITES!=='undefined'&&SPRITES.shin?.ready"):break
     await asyncio.sleep(.1)
    r=await c.js('''
    dismissTitle();p1Pick=2;p2Pick=0;startNewGame();paused=true;roundIntroTimer=0;
    const p=player1,board=document.createElement('canvas');board.width=1200;board.height=200;const g=board.getContext('2d');g.fillStyle='#87959d';g.fillRect(0,0,1200,200);const cells=[];
    Object.assign(p,{x:70,y:170-p.height,state:STATE.IDLE,isGrounded:true,vx:0,vy:0,attackAnim:null});
    for(let i=0;i<12;i++){p.animPhase=i*2;g.save();g.translate(i*100-35,0);drawSprite(g,p);g.restore();cells.push(p.drawCell);}
    return {cells,png:board.toDataURL().split(',')[1]};
    ''')
    assert r['cells']==[346,347,348,349,348,347]*2,r['cells']
    out=Path('media/shin-idle-trim');out.mkdir(exist_ok=True,parents=True);(out/'loop.png').write_bytes(base64.b64decode(r['png']));print(r['cells'])
  finally:proc.kill();proc.wait()
if __name__=='__main__':asyncio.run(main())
