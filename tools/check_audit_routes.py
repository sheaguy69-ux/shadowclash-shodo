#!/usr/bin/env python3
"""Exercise the audit's repaired attack routes in both directions."""
import asyncio,base64,json,tempfile
from pathlib import Path
import websockets
import watch_game as browser
async def main():
 url='http://localhost:9101/index.html';browser.assert_serving_this_tree(url)
 out=Path('media/audit-fixes-20260906/routes');out.mkdir(parents=True,exist_ok=True);results=[]
 with tempfile.TemporaryDirectory() as profile:
  proc,addr=browser.launch(url,profile)
  try:
   async with websockets.connect(addr,max_size=50*1024*1024) as ws:
    c=browser.CDP(ws)
    for _ in range(200):
     if await c.js("return typeof SPRITES!=='undefined'&&SPRITES.mokurai?.ready&&SPRITES.executioner?.ready"):break
     await asyncio.sleep(.1)
    held=await c.js("dismissTitle();p1Pick=6;p2Pick=0;startNewGame();paused=true;player1.state=STATE.CROUCH;player1.isGrounded=true;player1.crouchAt=animClock-2;const cells=[];for(let i=0;i<20;i++){player1.animPhase=i;cells.push(spriteFrameIndex(player1,SPRITES.mokurai.frames));}return cells;")
    assert set(held)=={99},held
    cases=[(0,'SPECIAL',None,False),(0,'HEAVY','fwd',False),(1,'HEAVY',None,False),(1,'HEAVY','fwd',False),(1,'HEAVY','back',False),(1,'MEDIUM',None,False),(1,'MEDIUM','up',True),(2,'SPECIAL',None,False),(3,'HEAVY','back',False),(4,'HEAVY','down',False),(5,'HEAVY','up',False),(6,'SPECIAL','back',False),(6,'MEDIUM','up',True),(7,'SPECIAL',None,False),(7,'SPECIAL','fwd',False),(7,'HEAVY','up',True),(7,'HEAVY','up',False),(8,'HEAVY',None,False),(8,'HEAVY','back',False),(8,'HEAVY','down',False)]
    for fighter,tier,direction,air in cases:
     for side in [-1,1]:
       cfg=json.dumps(dict(fighter=fighter,side=side,tier=tier,direction=direction,air=air))
       r=await c.js('const cfg='+cfg+''';
       dismissTitle();gameMode='2p';spectate=false;cpuMode=false;p1Pick=cfg.fighter;p2Pick=cfg.fighter===0?1:0;startNewGame();roundIntroTimer=0;paused=true;cutscene=null;hitstopRemaining=0;for(const k in keys)keys[k]=false;physKeys.clear();
       const p=player1;Object.assign(p,{x:canvas.width/2,y:GROUND_Y-p.height-(cfg.air?160:0),facing:cfg.side,isGrounded:!cfg.air});player2.x=cfg.side>0?canvas.width-70:20;
       const type=STATE['ATTACK_'+cfg.tier];p.executeAttack(type,cfg.direction,{type,dir:cfg.direction,axis:cfg.direction==='fwd'?1:cfg.direction==='back'?-1:0,up:cfg.direction==='up',down:cfg.direction==='down',ttl:ATTACK_BUFFER});
       const frames=[],failures=[],trace=[];let last=-1;
       for(let tick=0;tick<65;tick++){
        const cell=spriteFrameIndex(p,SPRITES[p.spec.name.toLowerCase()].frames);trace.push(cell);if(p.spec.id===6&&!p.isGrounded&&[233,237,239,240].includes(cell))failures.push('ground artwork airborne '+cell);
        if(cell!==last){const s=document.createElement('canvas');s.width=200;s.height=220;const g=s.getContext('2d');g.fillStyle='#87959d';g.fillRect(0,0,200,220);g.save();g.translate(100-p.x-p.width/2,205-p.y-p.height);drawSprite(g,p);const reviewedRight={0:[329,296],7:[169,170,171,173,175,176,257,258]};if(reviewedRight[p.spec.id]?.includes(cell)&&p.drawMirror*(SPRITES[p.spec.name.toLowerCase()].mirror?.[cell]?-1:1)!==p.facing)failures.push('reviewed attack faces away '+cell);g.restore();const pix=g.getImageData(0,0,200,220).data;let ink=0;for(let i=0;i<pix.length;i+=4)if(pix[i]!==135||pix[i+1]!==149||pix[i+2]!==157)ink++;if(ink<100)failures.push('invisible '+cell);if(p.spec.id===6&&(cell===355||cell===362))failures.push('corrupt guard');frames.push({s,cell,tick});last=cell;}
        updateGame(1/60);
       }
       const board=document.createElement('canvas');board.width=200*frames.length;board.height=240;const g=board.getContext('2d');frames.forEach((f,i)=>{g.drawImage(f.s,i*200,20);g.fillStyle='#fff';g.font='12px sans-serif';g.fillText(f.cell+' tick '+f.tick,i*200+4,14)});return {cfg,trace,failures,png:board.toDataURL().split(',')[1]};''')
       assert r and '__error' not in r,r
       (out/f'{fighter}-{tier}-{direction}-{side}{"-air" if air else ""}.png').write_bytes(base64.b64decode(r.pop('png')));results.append(r)
  finally:proc.kill();proc.wait()
 # A passing animation must actually have selected the repaired contact family.
 required={(1,'HEAVY',None,False):233,(1,'MEDIUM',None,False):234,(7,'HEAVY','up',False):409,(8,'HEAVY',None,False):674}
 for r in results:
  cfg=r['cfg'];expected=required.get((cfg['fighter'],cfg['tier'],cfg['direction'],cfg['air']))
  if expected is not None:assert expected in r['trace'],(cfg,expected,r['trace'])
 (out/'checks.json').write_text(json.dumps(results,indent=2));assert not any(r['failures'] for r in results),results
 print('PASS:',len(results),'actual attack routes, 65 simulation ticks each')
if __name__=='__main__':asyncio.run(main())
