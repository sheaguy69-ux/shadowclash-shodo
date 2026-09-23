#!/usr/bin/env python3
"""Check live wall contact, visible kick-off art and shared body registration."""
import asyncio,base64,hashlib,json,os,tempfile,urllib.request
from pathlib import Path
import websockets
import watch_game as b
async def main():
 b.PORT=int(os.environ.get('DEBUG_PORT','9338'));b.assert_serving_this_tree('http://localhost:9101/index.html')
 who=json.loads(urllib.request.urlopen('http://localhost:9101/whoami').read())
 assert Path(who['tree']).resolve()==Path.cwd().resolve(),who
 source_before=hashlib.sha256(Path('web/index.html').read_bytes()).hexdigest()
 with tempfile.TemporaryDirectory() as profile:
  proc,address=b.launch('http://localhost:9101/index.html',profile)
  try:
   async with websockets.connect(address,max_size=12000000) as ws:
    c=b.CDP(ws)
    for _ in range(400):
     if await c.js("return typeof SPRITES!=='undefined'&&NINJA_ROSTER.every(s=>SPRITES[s.name.toLowerCase()]?.ready)"):break
     await asyncio.sleep(.1)
    r=await c.js("""
    dismissTitle();gameMode='2p';const board=document.createElement('canvas');board.width=1350;board.height=520;const g=board.getContext('2d');g.fillStyle='#87959d';g.fillRect(0,0,1350,520);const rows=[];
    for(let id=0;id<NINJA_ROSTER.length;id++){p1Pick=id;p2Pick=id===0?1:0;startNewGame();paused=true;roundIntroTimer=0;const p=player1;
    for(const side of [-1,1]){Object.assign(p,{x:60,y:180-p.height,vx:0,vy:0,facing:-side,wallDir:side,state:STATE.WALL_CLING,isGrounded:false,attackAnim:null,lean:0,landSquash:0});
    const m=SPRITES[p.spec.name.toLowerCase()], S=m.scale*SHODO_DISPLAY_SCALE*(p.spec.renderScale||1)*(m.frameScale?.[spriteFrameIndex(p,m.frames)]??1);
    const wall=p.x+(side>0?p.width:0);g.save();g.translate(id*150+(side<0?10:140)-wall,(side<0?30:285));drawSprite(g,p);g.fillStyle='#ddc391';g.fillRect(wall,0,side*2,240);g.restore();g.fillStyle='#111';g.font='12px sans-serif';g.fillText(p.spec.name+' '+p.drawCell,id*150+5,side<0?15:275);const tile=document.createElement('canvas');tile.width=300;tile.height=300;const t=tile.getContext('2d',{willReadFrequently:true});drawSprite(t,p);
    const a=t.getImageData(0,0,300,300).data,idx=p.drawCell,anchor=m.footY-(m.footAdj?.[idx]||0);
    const bands={0:[[311,327],[450,480]],1:[[207,251],[273,307]],2:[[165,225],[265,325]],3:[[174,187],[282,310]],4:[[233,249],[329,365]],5:[[198,236],[261,305]],6:[[90,112],[190,216]],7:[[170,230],[283,340]],8:[[205,220],[301,327]]}[id];
    const gaps=bands.map(([lo,hi])=>{let gap=Infinity;for(let y=Math.max(0,Math.floor(180+(lo-anchor)*S));y<Math.min(300,Math.ceil(180+(hi-anchor)*S));y++)for(let x=0;x<300;x++)if(a[(y*300+x)*4+3]>128)gap=Math.min(gap,Math.abs(x-wall));return gap;});
    Object.assign(p,{x:side<0?9:canvas.width-9-p.width,y:GROUND_Y-p.height-180,vx:side*60,wallDir:0,inputAxis:side,state:STATE.JUMP,isGrounded:false,stunTimer:0,stamina:100,clingTime:0});
    p.applyPhysics(1/60);const entry=p.state;for(let i=0;i<20;i++)p.applyPhysics(1/60);drawSprite(t,p);
    rows.push({id,side,cell:p.drawCell,gaps,entry,held:p.state,wall:p.wallDir,expected:m.frames.wallslide});}}
    return {rows,png:board.toDataURL().split(',')[1]};
    """)
    out=Path(os.environ.get('OUT','media/wall-roster-contact'));out.mkdir(exist_ok=True,parents=True);(out/'current.png').write_bytes(base64.b64decode(r['png']));print(r['rows']);assert all(x['cell']==x['expected'] and x['wall']==x['side'] and max(x['gaps'])<=4 for x in r['rows']),r['rows']
    live=await c.js("""
    const rows=[],strip=document.createElement('canvas');strip.width=960;strip.height=9*180;const g=strip.getContext('2d');
    for(let id=0;id<NINJA_ROSTER.length;id++)for(const side of [-1,1]){
      p1Pick=id;p2Pick=id===0?1:0;startNewGame();paused=true;roundIntroTimer=0;hitstopRemaining=0;cutscene=null;
      for(const k in keys)keys[k]=false;physKeys.clear();const code=side<0?'KeyA':'KeyD';keys[code]=true;physKeys.add(code);
      const p=player1;Object.assign(p,{x:side<0?11:canvas.width-11-p.width,y:GROUND_Y-p.height-180,vx:side*100,vy:0,isGrounded:false,state:STATE.JUMP,stamina:100});
      for(let tick=0;tick<24;tick++){
        updateGame(1/60);
        if(tick%6===5){drawScene();const sx=side<0?0:canvas.width-120;g.drawImage(canvas,sx,p.y-70,120,180,(side<0?0:480)+Math.floor(tick/6)*120,id*180,120,180);}
        if(tick>2)rows.push({id,side,tick,state:p.state,wall:p.wallDir});
      }
    }
    for(const k in keys)keys[k]=false;physKeys.clear();return {rows,png:strip.toDataURL().split(',')[1]};
    """)
    (out/'live.png').write_bytes(base64.b64decode(live.pop('png')))
    failures=[x for x in live['rows'] if x['state']!='WALL_CLING' or x['wall']!=x['side']]
    print('live input failures',failures[:5]);assert not failures
    kicks=await c.js("""
    const rows=[],key=(code,down)=>window.dispatchEvent(new KeyboardEvent(down?'keydown':'keyup',{code,bubbles:true}));
    // Extra horizontal room exposes ink that the real viewport would clip.
    const pad=320,tile=document.createElement('canvas');tile.width=canvas.width+2*pad;tile.height=canvas.height;const g=tile.getContext('2d',{willReadFrequently:true});g.translate(pad,0);
    const original=drawShodoFrame;let actual=null,man=null;
    drawShodoFrame=function(...a){
      if(a[0]!==g||a[1]!==man.img)return original.apply(this,a);
      // Inspect the actual outlined canvas draw, including shared frameOffsetX.
      // Clear earlier aura ink so visibility measures this body alone.
      g.save();g.resetTransform();g.clearRect(0,0,tile.width,tile.height);g.restore();
      const draw=g.drawImage;
      g.drawImage=function(...v){const t=g.getTransform(),padX=(v[3]-a[4])/2,padY=(v[4]-a[5])/2;
        const x=v[5]+padX*v[7]/v[3],y=v[6]+padY*v[8]/v[4];
        actual={originX:t.a*x+t.c*y+t.e-pad,originY:t.b*x+t.d*y+t.f,
          axisX:t.a*v[7]/v[3],axisY:t.d*v[8]/v[4]};return draw.apply(this,v);};
      try{return original.apply(this,a);}finally{g.drawImage=draw;}
    };
    const sample=(p,id,side,tick,action)=>{
      actual=null;drawSprite(g,p);
      const pixels=g.getImageData(0,0,tile.width,tile.height).data;let visible=0,x0=Infinity,x1=-Infinity;
      for(let i=3;i<pixels.length;i+=4)if(pixels[i]>32){visible++;const x=((i-3)/4)%tile.width-pad;x0=Math.min(x0,x);x1=Math.max(x1,x);}
      const pose=combatPose(p),error=actual&&pose?Math.max(Math.abs(actual.originX-pose.originX),Math.abs(actual.originY-pose.originY),Math.abs(actual.axisX-pose.sign*pose.S),Math.abs(actual.axisY-pose.S)):null;
      const ha=man.handAnchor?.[p.drawCell],hand=ha?p.handAnchorPt():null;
      const handError=ha&&actual&&hand?Math.max(Math.abs(hand.x-actual.originX-ha[0]*actual.axisX),Math.abs(hand.y-actual.originY-ha[1]*actual.axisY)):null;
      rows.push({id,side,tick,action,state:p.state,cell:p.drawCell,wallDir:p.wallDir,wallJumpLock:p.wallJumpLock,facing:p.facing,vx:p.vx,visible,
        inkX:visible?[x0,x1]:null,viewportWidth:canvas.width,handError,
        actual,geometry:pose?{cell:pose.idx,originX:pose.originX,originY:pose.originY,sign:pose.sign,scale:pose.S,shiftX:pose.shiftX}:null,error});
    };
    try{for(let id=0;id<NINJA_ROSTER.length;id++)for(const side of [-1,1])for(const action of ['jump','heavy','release','idle']){
      dismissTitle();gameMode='2p';cpuMode=false;spectate=false;stagePick='bamboo';p1Pick=id;p2Pick=id===0?1:0;startNewGame();
      paused=false;roundIntroTimer=0;hitstopRemaining=0;cutscene=null;releaseAllKeys();
      const p=player1;man=SPRITES[p.spec.name.toLowerCase()];
      p.y=GROUND_Y-p.height;p.isGrounded=true;updateGame(1/(60*COMBAT_TEMPO));
      Object.assign(p,{x:side<0?10:canvas.width-10-p.width,y:GROUND_Y-p.height-(action==='idle'?0:180),vx:0,vy:0,isGrounded:action==='idle',state:action==='idle'?STATE.IDLE:STATE.JUMP,stamina:100,facing:-side});
      const toward=side<0?'KeyA':'KeyD';
      if(action!=='idle'){
        key(toward,true);for(let i=0;i<12;i++)updateGame(1/(60*COMBAT_TEMPO));
        if(p.wallDir!==side||p.state!==STATE.WALL_CLING)throw Error(p.spec.name+' never clung');
        if(action==='jump'){key('KeyW',true);key('KeyW',false);key(toward,false);}
        else if(action==='heavy'){key('KeyG',true);key('KeyG',false);}
        else key(toward,false);
      }
      const count=action==='jump'?14:action==='idle'?16:48;
      for(let tick=0;tick<count;tick++){if(tick)updateGame(1/(60*COMBAT_TEMPO));sample(p,id,side,tick,action);}
    }
    // Exercise every authored Exile chain-hand anchor through the real frame picker.
    for(const side of [-1,1]){
      p1Pick=7;p2Pick=0;startNewGame();releaseAllKeys();const p=player1;man=SPRITES.exile;
      Object.assign(p,{x:side<0?10:canvas.width-10-p.width,y:GROUND_Y-p.height-180,facing:-side,isGrounded:false,state:STATE.JUMP,grappleT0:1,wallDir:0,wallJumpLock:0});
      for(let tick=0;tick<8;tick++){p.grappleT=1-(tick+0.1)/8;sample(p,7,side,tick,'chain-hand');}
    }}finally{drawShodoFrame=original;paused=true;releaseAllKeys();}
    return rows;
    """)
    failures=[r for r in kicks if not r['visible'] or r['error'] is None or r['error']>0.001
              or r['cell']!=r['geometry']['cell'] or r['inkX'][0]<0 or r['inkX'][1]>=r['viewportWidth']
              or (r['action']=='chain-hand' and (r['handError'] is None or r['handError']>0.001))
              or (r['wallJumpLock']>0 and (r['wallDir']!=0 or r['facing']!=-r['side'] or r['vx']*r['side']>=0))]
    source_after=hashlib.sha256(Path('web/index.html').read_bytes()).hexdigest()
    (out/'kickoff.json').write_text(json.dumps({'whoami':who,'source_before':source_before,'source_after':source_after,'source_changed':source_before!=source_after,'frames':kicks,'failures':failures},indent=2))
    b.assert_serving_this_tree('http://localhost:9101/index.html','after wall regression')
    assert source_before==source_after,'source changed during wall regression'
    print('wall/edge samples',len(kicks),'failures',len(failures));assert not failures,failures[:5]
  finally:proc.kill();proc.wait()
if __name__=='__main__':asyncio.run(main())
