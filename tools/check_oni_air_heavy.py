"""Watch Oni's airborne forward Heavy and guard the two grounded Heavy routes."""
import asyncio, base64, json, os, tempfile
from pathlib import Path
import websockets
import watch_game as browser

SAMPLE = r'''
dismissTitle();gameMode='2p';spectate=false;cpuMode=false;stagePick='bamboo';p1Pick=8;p2Pick=0;
startNewGame();roundIntroTimer=0;paused=true;cutscene=null;hitstopRemaining=0;
for(const k in keys)keys[k]=false;physKeys.clear();
const p=player1,m=SPRITES.oni,F=m.frames,failures=[],trace=[],snaps=[],unique=[];
const row=prefix=>{const a=[];for(let i=1;F[prefix+i]!==undefined;i++)a.push(F[prefix+i]);return a;};
const air=row('airhfwd'),legacy=row('hfwd'),groundForward=row('ghfwd');
if(air.length!==4||new Set(air).size!==4||air.some(i=>!Number.isInteger(i)||i<0||i>=m.cols))
    return{...cfg,failures:['four distinct valid airhfwd cells are required'],air,cols:m.cols};
Object.assign(p,{x:canvas.width/2-p.width/2,y:GROUND_Y-p.height,vx:0,vy:0,isGrounded:true,facing:cfg.facing,state:STATE.IDLE});
Object.assign(player2,{x:p.x+cfg.facing*330,y:GROUND_Y-player2.height,vx:0,vy:0,isGrounded:true,facing:-cfg.facing,state:STATE.IDLE});
const groundNeutral=heavyCells(p,F),expected=cfg.mode==='air-forward'?air:cfg.mode==='ground-forward'?groundForward:groundNeutral;
const warm=document.createElement('canvas');warm.width=m.frameW;warm.height=m.frameH;
for(const i of new Set([...air,...groundForward,...groundNeutral]))
    drawShodoFrame(warm.getContext('2d'),m.img,i*m.frameW,0,m.frameW,m.frameH,0,0,m.frameW,m.frameH);
await new Promise(requestAnimationFrame);
if(cfg.mode==='air-forward')Object.assign(p,{y:p.y-220,vy:-160,isGrounded:false,state:STATE.JUMP});
const dir=cfg.mode==='ground-neutral'?'neutral':'fwd',axis=dir==='fwd'?1:0,type=STATE.ATTACK_HEAVY;
p.executeAttack(type,dir,{type,dir,axis,up:false,down:false,ttl:ATTACK_BUFFER});
const start={state:p.state,attackAir:p.attackAir,attackDir:p.attackDir,dur:p.attackAnim?.dur,recovery:p.recoveryTimer,
    boxes:p.hitboxes.map(h=>({delay:h.delay,duration:h.duration,tier:h.tier})),airTrack:trackFor(p,'airheavy')};
if(p.state!==STATE.ATTACK_HEAVY)failures.push('actual Heavy input did not start Heavy');
if(start.attackAir!==(cfg.mode==='air-forward'))failures.push('incorrect press-time air latch');
if(cfg.mode==='air-forward'){
    const h=start.boxes.find(h=>h.tier===STATE.ATTACK_HEAVY),dur=start.dur/1000;
    if(!h||Math.abs(h.delay-dur*FRAME_DATA.heavy.startup)>1e-8||Math.abs(h.duration-FRAME_DATA.heavy.active)>1e-8)
        failures.push('generic Heavy hitbox timing changed');
    if(h)for(const elapsed of [h.delay,h.delay+h.duration/2,h.delay+h.duration-1e-8])
        if(air[attackCellIndex(elapsed/dur,air.length,start.airTrack)]!==air[2])
            failures.push('contact drawing does not cover the unchanged active window');
}
const shot=()=>{
    const cell=spriteFrameIndex(p,F),s=document.createElement('canvas');s.width=360;s.height=390;
    const g=s.getContext('2d');g.fillStyle='#91a6af';g.fillRect(0,0,s.width,s.height);
    g.save();g.translate(180-p.x-p.width/2,350-p.y-p.height);
    const render=drawShodoFrame,calls=[];
    drawShodoFrame=function(...a){if(a[0]===g&&a[1]===m.img)calls.push({cell:Math.round(a[2]/m.frameW),a:g.getTransform().a});return render(...a);};
    try{drawSprite(g,p);}finally{drawShodoFrame=render;g.restore();}
    const body=calls.filter(c=>c.cell===p.drawCell).at(-1);
    const r={frame:trace.length,clock:animClock,cell,drawCell:p.drawCell,state:p.state,ground:p.isGrounded,
        vy:p.vy,y:p.y,facing:p.facing,mirror:p.drawMirror,renderA:body?.a,recovery:p.recoveryTimer,
        activeHeavy:p.hitboxes.filter(h=>h.tier===STATE.ATTACK_HEAVY&&h.delay<=0&&h.duration>0).length};
    if(!body)failures.push('shared native renderer did not draw body');
    if(p.isAttackingState()&&p.facing!==cfg.facing)failures.push('direction changed during Heavy');
    if(cfg.mode==='air-forward'&&!p.isGrounded&&p.state===STATE.ATTACK_HEAVY){
        if(!air.includes(cell))failures.push('air forward Heavy drew another family: '+cell);
        if(legacy.includes(cell))failures.push('grounded Severance art appeared airborne: '+cell);
        if(r.activeHeavy&&cell!==air[2])failures.push('live Heavy active window drew windup/recovery: '+cell);
    }
    // All four source drawings were independently reviewed as left-authored.
    if(air.includes(cell)&&(!body||-Math.sign(body.a)!==p.facing))failures.push('air Severance rendered backward');
    if(cfg.mode!=='air-forward'&&air.includes(cell))failures.push('ground Heavy was replaced by airborne art');
    if(!unique.some(u=>u.cell===cell))unique.push({cell,index:trace.length,s});
    trace.push(r);snaps.push(s);
};
shot();paused=false;
await new Promise(resolve=>{let n=0,done=-1;function tick(){
    shot();if(p.isGrounded&&!p.isAttackingState()&&done<0)done=n;
    if(++n<125&&(done<0||n<done+10))requestAnimationFrame(tick);else resolve();
}requestAnimationFrame(tick);});paused=true;
const seen=[...new Set(trace.map(r=>r.cell))],missing=[...new Set(expected)].filter(i=>!seen.includes(i));
if(missing.length)failures.push('authored Heavy cells not reached: '+missing.join(','));
if(cfg.mode==='air-forward'&&!trace.some(r=>r.activeHeavy))failures.push('live Heavy active window was not sampled');
if(!trace.some(r=>r.ground&&r.state===STATE.IDLE))failures.push('move did not settle on floor');
const board=(tiles,cols,scale)=>{
    const w=360*scale,h=390*scale,c=document.createElement('canvas');c.width=cols*w;c.height=Math.ceil(tiles.length/cols)*(h+25);
    const g=c.getContext('2d');g.fillStyle='#91a6af';g.fillRect(0,0,c.width,c.height);
    tiles.forEach((u,i)=>{const x=i%cols*w,y=Math.floor(i/cols)*(h+25),r=trace[u.index];
        g.drawImage(u.s,x,y+25,w,h);g.fillStyle='#17262e';g.font='12px sans-serif';
        g.fillText(cfg.mode+' '+cfg.facing+' f'+u.index+' #'+u.cell+' '+(r.ground?'floor':'air'),x+4,y+16);});
    return c.toDataURL().split(',')[1];
};
return{...cfg,cols:m.cols,sheetVersion:SHEET_V,air,legacy,expected,start,seen,missing,
    failures:[...new Set(failures)],trace,nativePng:board(unique,4,1),livePng:board(snaps.map((s,index)=>({s,index,cell:trace[index].cell})),8,.5)};
'''

async def main():
    browser.PORT=int(os.environ.get('SHADOWCLASH_DEBUG_PORT','9333'))
    url=os.environ.get('SHADOWCLASH_URL','http://localhost:9101/index.html')
    browser.assert_serving_this_tree(url)
    out=Path(os.environ.get('OUT','media/oni-aura-cutoff-20260906/air-heavy-final'))
    out.mkdir(parents=True,exist_ok=True)
    results=[]
    with tempfile.TemporaryDirectory(prefix='oni-air-heavy-') as profile:
        proc,addr=browser.launch(url,profile)
        try:
            async with websockets.connect(addr,max_size=65*1024*1024) as ws:
                c=browser.CDP(ws)
                for _ in range(500):
                    if await c.js("return typeof SPRITES!=='undefined'&&NINJA_ROSTER.every(s=>SPRITES[s.name.toLowerCase()]?.ready)"):break
                    await asyncio.sleep(.1)
                else:raise AssertionError('roster did not load')
                for mode in ['air-forward','ground-neutral','ground-forward']:
                    for facing in [-1,1]:
                        r=await c.js('const cfg='+json.dumps({'mode':mode,'facing':facing})+';\n'+SAMPLE)
                        assert r and '__error' not in r,r
                        for key,kind in [('nativePng','native'),('livePng','consecutive')]:
                            if key in r:(out/f'{mode}-{facing}-{kind}.png').write_bytes(base64.b64decode(r.pop(key)))
                        results.append(r)
                        print(mode,facing,len(r.get('trace',[])),'rAF samples',r['failures'],flush=True)
        finally:proc.terminate();proc.wait(timeout=10)
    (out/'checks.json').write_text(json.dumps(results,indent=2)+'\n')
    assert not any(r['failures'] for r in results),str(out/'checks.json')
    print('PASS',len(results),'actual Heavy routes;',sum(len(r['trace']) for r in results),'consecutive samples')

if __name__=='__main__':asyncio.run(main())
