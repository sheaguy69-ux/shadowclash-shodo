"""Real wall-Light inputs, both walls, projectile type/origin, animation, ammo and sheet preservation."""
import asyncio,base64,json,tempfile,hashlib
from pathlib import Path
from PIL import Image
Image.MAX_IMAGE_PIXELS=None
import websockets,watch_game as browser
async def main():
 out=Path('media/wall-projectiles-20260906');browser.PORT=9351
 for n in ['exile','oni','shin']:
  m=json.loads((out/f'{n}-before.json').read_text());im=Image.open(f'web/assets/sprites/{n}.png').convert('RGBA');assert hashlib.sha256(im.crop((0,0,m['cols']*m['frameW'],m['frameH'])).tobytes()).hexdigest()==(out/f'{n}-original.sha256').read_text()
 url='http://localhost:9101/index.html';browser.assert_serving_this_tree(url)
 with tempfile.TemporaryDirectory(prefix='wall-projectiles-') as profile:
  proc,addr=browser.launch(url,profile)
  try:
   async with websockets.connect(addr,max_size=60_000_000) as ws:
    c=browser.CDP(ws)
    for _ in range(300):
     if await c.js("return typeof SPRITES!=='undefined'&&['exile','oni','shin'].every(n=>SPRITES[n]?.ready)"):break
     await asyncio.sleep(.1)
    r=await c.js(r'''
    dismissTitle();const failures=[],rows=[],strips=[];const key=(code,down)=>window.dispatchEvent(new KeyboardEvent(down?'keydown':'keyup',{code,bubbles:true}));
    for(const id of [2,7,8])for(const side of [-1,1]){
      gameMode='2p';cpuMode=false;spectate=false;stagePick='bamboo';p1Pick=id;p2Pick=0;startNewGame();paused=false;cutscene=null;roundIntroTimer=0;hitstopRemaining=0;for(const k in keys)keys[k]=false;physKeys.clear();
      const p=player1,m=SPRITES[p.spec.name.toLowerCase()],name=p.spec.name.toLowerCase();Object.assign(p,{x:side<0?10:canvas.width-10-p.width,y:GROUND_Y-p.height-170,isGrounded:false,state:STATE.JUMP,vx:side*60,vy:0,inputAxis:side,wallDir:0,clingTime:0,stars:ANCHOR_STARS,starCd:0,chakra:100});player2.x=canvas.width/2;p.applyPhysics(1/60);key(side<0?'KeyA':'KeyD',true);
      key('KeyF',true);key('KeyF',false);const q=p.projectiles[0],trace=[],samples=[];
      if(!q||q.kind!==(id===7?'kunai':'star'))failures.push(name+' wrong projectile '+q?.kind);
      if(p.stars!==ANCHOR_STARS-1||p.wallThrowT<=0)failures.push(name+' Light did not throw');
      if(q&&q.vx*side>=0)failures.push(name+' projectile aimed into wall');
      const initial=q?{...q}:null;
      if(p.throwWallProjectile())failures.push(name+' cooldown bypass');
      for(let tick=0;tick<32;tick++){
        const b=document.createElement('canvas');b.width=300;b.height=280;const g=b.getContext('2d');g.fillStyle='#87959d';g.fillRect(0,0,300,280);const wx=p.x+(side>0?p.width:0),screenWall=side<0?30:270;
        g.save();g.translate(screenWall-wx,250-p.y-p.height);drawSprite(g,p);g.fillStyle='#ddc391';g.fillRect(wx-1,p.y-300,2,1000);if(tick===0&&q){const pt=g.getTransform().transformPoint(new DOMPoint(q.x,q.y)),a=g.getImageData(Math.round(pt.x)-4,Math.round(pt.y)-4,9,9).data;let ink=0;for(let k=0;k<a.length;k+=4)if(a[k]!==135||a[k+1]!==149||a[k+2]!==157)ink++;if(ink<3)failures.push(name+' projectile misses drawn hand');g.fillStyle='#ff386b';g.beginPath();g.arc(q.x,q.y,3,0,Math.PI*2);g.fill();}g.restore();
        trace.push({tick,cell:p.drawCell,wall:p.wallDir,throwT:p.wallThrowT});if(tick%2===0)samples.push(b);
        updateGame(1/60);
      }
      const expected=[m.frames.wallthrow1,m.frames.wallthrow3,m.frames.wallslide];for(const cell of expected)if(!trace.some(x=>x.cell===cell))failures.push(name+' missing cell '+cell);
      if(trace.some(x=>x.wall!==side))failures.push(name+' detached during throw');
      p.starCd=0;p.throwWallProjectile();p.starCd=0;p.throwWallProjectile();p.starCd=0;if(p.stars!==0||p.throwWallProjectile())failures.push(name+' ammo cap');
      key(side<0?'KeyA':'KeyD',false);Object.assign(p,{wallDir:0,isGrounded:true,state:STATE.IDLE,y:GROUND_Y-p.height,vy:0});updateGame(1/60);if(p.stars!==ANCHOR_STARS)failures.push(name+' landing refill');
      const board=document.createElement('canvas');board.width=1200;board.height=1120;const g=board.getContext('2d');samples.forEach((b,i)=>{g.drawImage(b,i%4*300,Math.floor(i/4)*280);g.fillStyle='white';g.fillText('tick '+i*2+' cell '+trace[i*2].cell,i%4*300+6,Math.floor(i/4)*280+14);});strips.push({name:name+'-'+side,png:board.toDataURL().split(',')[1]});rows.push({name,side,initial,trace});
    }
    paused=true;return{failures,rows,strips};
    ''');assert r and '__error' not in r,r
    for x in r.pop('strips'):(out/(x['name']+'-live.png')).write_bytes(base64.b64decode(x['png']))
    (out/'checks.json').write_text(json.dumps(r,indent=2));print(json.dumps({'failures':r['failures'],'scenarios':len(r['rows'])}));assert not r['failures'],r['failures']
  finally:proc.terminate();proc.wait(timeout=10)
if __name__=='__main__':asyncio.run(main())
