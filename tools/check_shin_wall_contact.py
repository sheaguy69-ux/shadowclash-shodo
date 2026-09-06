"""Capture real Shin wall contact, grip and kick-off in both directions."""
import asyncio, base64, json, os, tempfile
from pathlib import Path
import websockets, watch_game as browser

async def main():
    browser.PORT=int(os.environ.get('SHADOWCLASH_DEBUG_PORT','9333'))
    url='http://localhost:9101/index.html'
    browser.assert_serving_this_tree(url)
    out=Path(os.environ.get('OUT','media/shin-wallcling-20260906/before'))
    out.mkdir(parents=True,exist_ok=True)
    results=[]
    with tempfile.TemporaryDirectory(prefix='shin-wall-contact-') as profile:
        proc,addr=browser.launch(url,profile)
        try:
            async with websockets.connect(addr,max_size=35*1024*1024) as ws:
                c=browser.CDP(ws)
                for _ in range(400):
                    if await c.js("return typeof SPRITES!=='undefined'&&SPRITES.shin?.ready&&SPRITES.executioner?.ready"):break
                    await asyncio.sleep(.1)
                for side in [-1,1]:
                    r=await c.js('const side='+str(side)+r''';
                        dismissTitle();gameMode='2p';spectate=false;cpuMode=false;stagePick='bamboo';p1Pick=2;p2Pick=0;
                        startNewGame();roundIntroTimer=0;paused=true;cutscene=null;hitstopRemaining=0;
                        for(const k in keys)keys[k]=false;physKeys.clear();
                        const p=player1,m=SPRITES.shin,traces=[],shots=[],failures=[];
                        if(m.wallContactX?.[338]!==42)failures.push('wallContactX metadata not loaded');
                        if(m.frames.walljump!==301)failures.push('wall kick still uses painted wall art');
                        Object.assign(p,{x:side<0?11:canvas.width-11-p.width,y:GROUND_Y-p.height-210,
                            isGrounded:false,vx:0,vy:0,facing:-side,state:STATE.JUMP,landSquash:0});
                        player2.x=canvas.width/2;player2.y=GROUND_Y-player2.height;player2.isGrounded=true;
                        const key=(code,down)=>window.dispatchEvent(new KeyboardEvent(down?'keydown':'keyup',{code,bubbles:true}));
                        const take=label=>{
                            const cv=document.createElement('canvas');cv.width=320;cv.height=370;
                            const g=cv.getContext('2d');g.fillStyle='#dfdace';g.fillRect(0,0,320,370);
                            const wx=side<0?10:canvas.width-10,sx=side<0?40:280,ty=338-p.y-p.height;
                            g.fillStyle='#68747b';g.fillRect(side<0?0:sx,0,40,370);
                            g.save();g.translate(sx-wx,ty);
                            let draw=null;const render=drawShodoFrame;
                            drawShodoFrame=function(...a){if(a[0]===g&&a[1]===m.img){const t=g.getTransform();draw={a:t.a,d:t.d,e:t.e,f:t.f,dx:a[6],dy:a[7],dw:a[8],dh:a[9]};}return render(...a);};
                            try{drawSprite(g,p);}finally{drawShodoFrame=render;g.restore();}
                            const row={label,cell:p.drawCell,state:p.state,side,wallDir:p.wallDir,facing:p.facing,
                                x:p.x,y:p.y,vx:p.vx,vy:p.vy,wallJumpLock:p.wallJumpLock,wallScreenX:sx,
                                ink:cellInk(m,p.drawCell),draw};
                            if(label.startsWith('contact')&&p.wallDir===side
                                &&(p.state!==STATE.WALL_CLING||p.drawCell!==338||p.vy!==0))
                                failures.push(label+' collision did not immediately select stable cling338');
                            if(p.state===STATE.WALL_CLING&&draw){
                                const gap=x=>side*(sx-(draw.a*(draw.dx+x/m.frameW*draw.dw)+draw.e));
                                row.handGap=gap(40);row.supportBootGap=gap(45);
                                if(Math.abs(row.handGap)>2.6||Math.abs(row.supportBootGap)>2.6)failures.push(label+' hand/boot misses wall');
                                if(row.ink.y0<120)failures.push(label+' painted wall stroke remains');
                                if(Math.sign(draw.a)!==-side)failures.push(label+' cling faces away from wall');
                            }
                            if(label.startsWith('kick')&&p.wallJumpLock>0){
                                if(p.drawCell!==301||p.wallDir!==0||Math.sign(p.vx)!==-side||p.facing!==-side)failures.push(label+' bad wall kick route/momentum');
                                if(draw&&Math.sign(draw.a)!==side)failures.push(label+' wall kick points toward wall');
                            }
                            traces.push(row);shots.push(cv);
                        };
                        paused=false;key(side<0?'KeyA':'KeyD',true);
                        for(let i=0;i<9;i++){await new Promise(r=>requestAnimationFrame(r));take('contact'+i);}
                        key('KeyW',true);key('KeyW',false);
                        const kickoff={wallJumpLock:p.wallJumpLock,wallDir:p.wallDir,facing:p.facing,vx:p.vx,vy:p.vy};
                        for(let i=0;i<6;i++){await new Promise(r=>requestAnimationFrame(r));take('kick'+i);}
                        key(side<0?'KeyA':'KeyD',false);paused=true;
                        const board=document.createElement('canvas');board.width=5*320;board.height=3*394;
                        const b=board.getContext('2d');b.fillStyle='#dfdace';b.fillRect(0,0,board.width,board.height);
                        shots.forEach((s,i)=>{const x=i%5*320,y=Math.floor(i/5)*394;b.drawImage(s,x,y+24);b.fillStyle='#111';b.font='13px sans-serif';b.fillText(traces[i].label+' / '+traces[i].cell+' '+traces[i].state,x+5,y+17);});
                        if(!traces.some(r=>r.state===STATE.WALL_CLING))failures.push('no live wall cling');
                        const firstContact=traces.find(r=>r.label.startsWith('contact')&&r.wallDir===side);
                        if(!firstContact||firstContact.state!==STATE.WALL_CLING||firstContact.cell!==338||firstContact.vy!==0)
                            failures.push('first actual collision has stale air state/art/velocity');
                        if(!traces.some(r=>r.label.startsWith('kick')&&r.wallJumpLock>0))failures.push('no live kick momentum window');
                        if(kickoff.wallJumpLock<=0||kickoff.wallDir!==0||kickoff.facing!==-side||Math.sign(kickoff.vx)!==-side||kickoff.vy!==-WALL_LIFT)failures.push('wall kick impulse changed');
                        return {side,traces,kickoff,failures,png:board.toDataURL().split(',')[1]};
                    ''')
                    assert r and '__error' not in r,r
                    (out/f'wall-{side}.png').write_bytes(base64.b64decode(r.pop('png')))
                    results.append(r)
                    print(side,r['failures'],[(x['label'],x['cell'],x['wallDir']) for x in r['traces']],flush=True)
        finally:proc.terminate();proc.wait(timeout=10)
    (out/'checks.json').write_text(json.dumps(results,indent=2)+'\n')
    assert not any(r['failures'] for r in results),str(out/'checks.json')

if __name__=='__main__':asyncio.run(main())
