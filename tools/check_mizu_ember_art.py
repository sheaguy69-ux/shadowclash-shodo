"""Replay repaired moves in both directions and check shared-renderer registration."""
import asyncio,base64,json,tempfile,hashlib
from PIL import Image
from pathlib import Path
import websockets,watch_game as browser
async def main():
 for name in ['mizu','ember']:
  root=Path('media/mizu-ember-repairs-20260906');m=json.loads((root/f'{name}-install-before.json').read_text());im=Image.open(f'web/assets/sprites/{name}.png').convert('RGBA');assert hashlib.sha256(im.crop((0,0,m['cols']*m['frameW'],m['frameH'])).tobytes()).hexdigest()==(root/f'{name}-install-original.sha256').read_text()
 browser.PORT=9346;url='http://localhost:9101/index.html';browser.assert_serving_this_tree(url);out=Path('media/mizu-ember-repairs-20260906/live');out.mkdir(parents=True,exist_ok=True)
 with tempfile.TemporaryDirectory(prefix='remaining-art-') as profile:
  proc,addr=browser.launch(url,profile)
  try:
   async with websockets.connect(addr,max_size=60000000) as ws:
    c=browser.CDP(ws)
    for _ in range(400):
     if await c.js("return typeof SPRITES!=='undefined'&&SPRITES.mizu?.ready&&SPRITES.ember?.ready"):break
     await asyncio.sleep(.1)
    result=await c.js(r'''
    dismissTitle();const failures=[],rows=[],strips=[];
    for(const bad of [184,185,186,192,204,218])if(Object.values(SPRITES.mizu.frames).includes(bad))failures.push('damaged Mizu cell '+bad);
    const key=(code,down)=>window.dispatchEvent(new KeyboardEvent(down?'keydown':'keyup',{code,bubbles:true}));
    const reset=(id,facing)=>{gameMode='2p';cpuMode=false;spectate=false;stagePick='bamboo';p1Pick=id;p2Pick=id===0?1:0;startNewGame();roundIntroTimer=0;hitstopRemaining=0;paused=false;cutscene=null;for(const k in keys)keys[k]=false;physKeys.clear();const p=player1;p.x=facing===1?250:700;player2.x=facing===1?900:100;for(const f of [p,player2]){f.y=GROUND_Y-f.height;f.isGrounded=true;}p.facing=facing;return p;};
    for(const [id,move,button,direction] of [[1,'medium','KeyJ','neutral'],[1,'heavy','KeyG','neutral'],[4,'getup','KeyJ','neutral']])for(const facing of [-1,1]){
      const p=reset(id,facing),m=SPRITES[p.spec.name.toLowerCase()],F=m.frames,trace=[],samples=[];
      let arrow=direction==='neutral'?null:((direction==='fwd'?facing:-facing)>0?'KeyD':'KeyA');if(arrow)key(arrow,true);key(button,true);key(button,false);if(arrow)key(arrow,false);
      if(move==='getup'){p.state=STATE.STUNNED;p.flooredT=.68;p.stunTimer=1;p.hitstun=1;}
      for(let tick=0;tick<75;tick++){
        const board=document.createElement('canvas');board.width=320;board.height=260;const g=board.getContext('2d');g.fillStyle='#83b7c0';g.fillRect(0,0,320,260);g.save();g.translate(160-p.x-p.width/2,235-p.y-p.height);drawSprite(g,p);g.restore();
        const idx=p.drawCell,active=p.isAttackingState();trace.push({tick,cell:idx,state:p.state,active,facing:p.facing,mirror:p.drawMirror,art:p.moveArt});
        if(tick%3===0&&samples.length<20)samples.push({board,idx});
        updateGame(1/60);
      }
      const played=new Set(trace.map(t=>t.cell));for(const idx of (move==='medium'?[234]:move==='heavy'?[233]:[310,311,312]))if(!played.has(idx))failures.push(move+' missing '+idx);
      const b=document.createElement('canvas');b.width=5*320;b.height=4*260;const bg=b.getContext('2d');samples.forEach((s,i)=>{bg.drawImage(s.board,i%5*320,Math.floor(i/5)*260);bg.fillStyle='#142125';bg.fillText('t'+i*3+' cell '+s.idx,i%5*320+5,Math.floor(i/5)*260+15);});
      strips.push({name:move+'-'+facing,png:b.toDataURL().split(',')[1]});rows.push({move,facing,trace});
    }
    paused=true;return{failures,rows,strips};
    ''');assert result and '__error' not in result,result
    for s in result.pop('strips'):(out/(s['name']+'.png')).write_bytes(base64.b64decode(s['png']))
    (out/'checks.json').write_text(json.dumps(result,indent=2));print(json.dumps({'failures':result['failures'],'scenarios':len(result['rows'])}));assert not result['failures'],result['failures']
  finally:proc.terminate();proc.wait(timeout=10)
asyncio.run(main())
