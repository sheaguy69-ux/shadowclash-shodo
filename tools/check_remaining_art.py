"""Replay repaired moves in both directions and check shared-renderer registration."""
import asyncio,base64,json,tempfile
from pathlib import Path
import websockets,watch_game as browser
async def main():
 browser.PORT=9344;url='http://localhost:9101/index.html';browser.assert_serving_this_tree(url);out=Path('media/remaining-repairs-20260906/live');out.mkdir(parents=True,exist_ok=True)
 with tempfile.TemporaryDirectory(prefix='remaining-art-') as profile:
  proc,addr=browser.launch(url,profile)
  try:
   async with websockets.connect(addr,max_size=60000000) as ws:
    c=browser.CDP(ws)
    for _ in range(400):
     if await c.js("return typeof SPRITES!=='undefined'&&SPRITES.executioner?.ready&&SPRITES.tsubasa?.ready"):break
     await asyncio.sleep(.1)
    result=await c.js(r'''
    dismissTitle();const failures=[],rows=[],strips=[];
    for(const [name,bad] of [['executioner',[127,240,241,247,268]],['tsubasa',[261,292,293,341,342,343,344,345,346]]])for(const [key,cell] of Object.entries(SPRITES[name].frames))if(bad.includes(cell))failures.push(name+' stale damaged mapping '+key);
    const key=(code,down)=>window.dispatchEvent(new KeyboardEvent(down?'keydown':'keyup',{code,bubbles:true}));
    const reset=(id,facing)=>{gameMode='2p';cpuMode=false;spectate=false;stagePick='bamboo';p1Pick=id;p2Pick=id===0?1:0;startNewGame();roundIntroTimer=0;hitstopRemaining=0;paused=false;cutscene=null;for(const k in keys)keys[k]=false;physKeys.clear();const p=player1;p.x=facing===1?250:700;player2.x=facing===1?900:100;for(const f of [p,player2]){f.y=GROUND_Y-f.height;f.isGrounded=true;}p.facing=facing;return p;};
    for(const [id,move,button,direction] of [[0,'neutral-special','KeyH','neutral'],[0,'forward-light','KeyF','fwd'],[3,'evasive-flick','KeyG','back']])for(const facing of [-1,1]){
      const p=reset(id,facing),m=SPRITES[p.spec.name.toLowerCase()],F=m.frames,trace=[],samples=[];
      let arrow=direction==='neutral'?null:((direction==='fwd'?facing:-facing)>0?'KeyD':'KeyA');if(arrow)key(arrow,true);key(button,true);key(button,false);if(arrow)key(arrow,false);
      for(let tick=0;tick<75;tick++){
        const board=document.createElement('canvas');board.width=320;board.height=260;const g=board.getContext('2d');g.fillStyle='#83b7c0';g.fillRect(0,0,320,260);g.save();g.translate(160-p.x-p.width/2,235-p.y-p.height);drawSprite(g,p);g.restore();
        const idx=p.drawCell,active=p.isAttackingState();trace.push({tick,cell:idx,state:p.state,active,facing:p.facing,mirror:p.drawMirror,art:p.moveArt});
        if(tick%3===0&&samples.length<20)samples.push({board,idx});
        if(active&&id===0){const right=new Set([97,238,239,103,104,329,296,341]);const sign=p.drawMirror*(m.mirror?.[idx]?-1:1)*(right.has(idx)?1:-1);if(sign!==p.facing)failures.push(move+' wrong direction '+idx);}
        updateGame(1/60);
      }
      const played=new Set(trace.filter(t=>t.active).map(t=>t.cell));const required=move==='neutral-special'?[329,296]:move==='forward-light'?[341]:[85,86,87];for(const idx of required)if(!played.has(idx))failures.push(move+' missing '+idx);
      for(const idx of (id===0?[127,240,241,268]:[261,293,341,342,343,344,345,346]))if(played.has(idx))failures.push(move+' damaged art reached '+idx);
      const b=document.createElement('canvas');b.width=5*320;b.height=4*260;const bg=b.getContext('2d');samples.forEach((s,i)=>{bg.drawImage(s.board,i%5*320,Math.floor(i/5)*260);bg.fillStyle='#142125';bg.fillText('t'+i*3+' cell '+s.idx,i%5*320+5,Math.floor(i/5)*260+15);});
      strips.push({name:move+'-'+facing,png:b.toDataURL().split(',')[1]});rows.push({move,facing,trace});
    }
    // The optional registration must translate the complete rendered cell, on both sides.
    const m=SPRITES.executioner,offset=m.img.shodoFrameOffsetX;
    for(const facing of [-1,1]){const bounds=[];for(const enabled of [false,true]){m.img.shodoFrameOffsetX=enabled?offset:{};const b=document.createElement('canvas');b.width=1200;b.height=600;const g=b.getContext('2d');g.translate(600,0);g.scale(facing,1);drawShodoFrame(g,m.img,341*m.frameW,0,m.frameW,m.frameH,-194,0,388,496);const a=g.getImageData(0,0,1200,600).data;let lo=1200,hi=0;for(let y=0;y<600;y++)for(let x=0;x<1200;x++)if(a[(y*1200+x)*4+3]>40){lo=Math.min(lo,x);hi=Math.max(hi,x);}bounds.push([lo,hi]);}if(bounds[1][0]-bounds[0][0]!==90*facing||bounds[1][1]-bounds[0][1]!==90*facing)failures.push('wide blade registration failed '+facing);}
    m.img.shodoFrameOffsetX=offset;paused=true;return{failures,rows,strips};
    ''');assert result and '__error' not in result,result
    for s in result.pop('strips'):(out/(s['name']+'.png')).write_bytes(base64.b64decode(s['png']))
    (out/'checks.json').write_text(json.dumps(result,indent=2));print(json.dumps({'failures':result['failures'],'scenarios':len(result['rows'])}));assert not result['failures'],result['failures']
  finally:proc.terminate();proc.wait(timeout=10)
asyncio.run(main())
