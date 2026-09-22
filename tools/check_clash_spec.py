#!/usr/bin/env python3
"""Actual browser clash, freeze, particle and no-ghost regression. Run with python3."""
import asyncio, json, tempfile, base64, io, os, hashlib
from PIL import Image, ImageDraw
from pathlib import Path
import websockets
import watch_game as browser

async def main():
    url='http://localhost:9101/index.html'
    browser.assert_serving_this_tree(url)
    browser.PORT=int(os.environ.get('DEBUG_PORT','9391'))
    out=Path(os.environ.get('OUT','media/contact-sparks-20260908/final-check'))
    out.mkdir(parents=True,exist_ok=True)
    source=Path(__file__).resolve().parents[1]/'web/index.html'
    source_hash=hashlib.sha256(source.read_bytes()).hexdigest()
    with tempfile.TemporaryDirectory(prefix='clash-spec-') as profile:
        proc,address=browser.launch(url,profile)
        try:
            async with websockets.connect(address,max_size=100_000_000) as ws:
                c=browser.CDP(ws)
                for _ in range(400):
                    if await c.js("return typeof SPRITES!=='undefined'&&NINJA_ROSTER.every(s=>SPRITES[s.name.toLowerCase()]?.ready)"):break
                    await asyncio.sleep(.1)
                else:raise AssertionError('roster did not load')
                result=await c.js(r'''
                dismissTitle();gameMode='2p';cpuMode=false;spectate=false;stagePick='bamboo';p1Pick=5;p2Pick=0;
                startNewGame();paused=false;roundIntroTimer=0;cutscene=null;releaseAllKeys();
                const failures=[],checks=[],check=(ok,msg)=>{checks.push({ok:!!ok,msg});if(!ok)failures.push(msg);};
                const a=player1,b=player2;
                function setup(reverse=false){
                    cancelBladeLock(a);cancelBladeLock(b);a.lock=b.lock=null;
                    hitstopRemaining=clashFreezeRemaining=clashShakeRemaining=0;clashCd=1;particles.length=0;fxSprites.length=0;
                    for(const [p,x] of [[a,reverse?520:480],[b,reverse?480:520]]){
                        p.clearMoveArt();Object.assign(p,{x,y:GROUND_Y-p.height,isGrounded:true,state:STATE.ATTACK_HEAVY,
                        vx:0,vy:0,stunTimer:0,recoveryTimer:.4,bufferedAttack:{type:STATE.ATTACK_HEAVY},pendingChainStarter:1,
                        facing:p===a?(reverse?-1:1):(reverse?1:-1),fistMode:false,gyakute:false,parryFlashTimer:0,kawarimiWindow:0,invulnTimer:0,rollTimer:0,armorTimer:0,stamina:100});
                        p.hitboxes=[{ox:500-x,oy:20,w:30,h:20,canClash:true,mat:'steel',duration:.1,delay:0}];
                    }
                }
                for(const reverse of [false,true]){
                    setup(reverse);check(processWeaponClash(a,b),'active overlap');
                    check(a.state===STATE.IDLE&&b.state===STATE.IDLE,'both neutral');
                    check(a.vx===(reverse?480:-480)&&b.vx===-a.vx,'outward velocity regardless of player slot');
                    check([a,b].every(p=>!p.hitboxes.length&&!p.recoveryTimer&&!p.bufferedAttack&&!p.pendingChainStarter&&!p.attackAnim),'cleared attack and queue');
                    check(particles.length===30&&particles.every(p=>p.bladeSpark),'30 tagged clash sparks');check(particles.every(p=>p.x===515&&p.y===a.y+30),'intersection center');
                    check(!processWeaponClash(a,b),'no repeat clash');
                }
                for(const field of ['delay','duration','canClash','separate']){
                    setup();if(field==='delay')a.hitboxes[0].delay=.1;if(field==='duration')b.hitboxes[0].duration=0;
                    if(field==='canClash')a.hitboxes[0].canClash=false;if(field==='separate')b.hitboxes[0].ox+=100;
                    check(!processWeaponClash(a,b),'excluded '+field);
                }
                for(const [amount,defBox,n] of [[1,null,10],[.85,null,18],[1,{canClash:true,mat:'steel'},30],[.3,null,5]]){
                    particles.length=0;fxSprites.length=0;createBladeSparks(500,300,a,b,{canClash:true,mat:'steel'},defBox,amount);
                    check(particles.length===n,'spark count '+n);
                    const grind=amount<.5,k=grind?.55:1,extra=defBox&&!grind?.06:0;
                    check(particles.every(p=>p.bladeSpark&&p.shard&&p.gravity&&p.life>=.18+extra&&p.life<=.30+extra
                        &&p.life===p.maxLife&&Math.hypot(p.vx,p.vy)>=200*k-1e-6&&Math.hypot(p.vx,p.vy)<=500*k+1e-6
                        &&p.len>=8*(grind?.6:1)&&p.len<=24*(grind?.6:1)
                        &&[SPARK_GOLD,'#fff1bc','#d89b3c'].includes(p.color)),'Shodo spark units/palette '+n);
                    check(grind?fxSprites.length===0:fxSprites.some(f=>f.id==='W06'&&f.life===.14&&Math.abs(f.scale*FX_RECTS.W06[2]-(defBox?48:36))<1e-9), 'contact flare only on burst '+n);
                }
                for(const mat of ['steel','wood','flesh','mail','chain']){
                    setup();clashCd=0;a.hitboxes[0].mat=mat;
                    processWeaponClash(a,b);
                    check((a.lockT>0&&b.lockT>0)===(mat==='steel'),'automatic blade-only lock '+mat);
                    if(mat==='steel')check(particles.filter(p=>p.bladeSpark).length===30,'lock catches with30sparks');
                    else check(!particles.some(p=>p.bladeSpark),'no metal sparks for '+mat);
                    cancelBladeLock(a);cancelBladeLock(b);
                }
                // Guards use the real damage receiver, including its per-attack material gate.
                const guardResults=[];
                for(const reverse of [false,true])for(const kind of ['steel','iron','wood','flesh','mail','chain','kick','bare-guard','avoided']){
                    setup(reverse);b.state=STATE.BLOCKING;b.fistMode=kind==='bare-guard';
                    if(kind==='avoided')b.invulnTimer=.2;
                    const hb={canClash:kind!=='kick',mat:['kick','bare-guard','avoided'].includes(kind)?'steel':kind,tier:STATE.ATTACK_LIGHT,pushback:0};
                    const hp=b.hp,stamina=b.stamina;
                    b.takeDamage(10,a,hb);const contact=bladeGuardPoint(a,b,hb);
                    const shards=particles.filter(p=>p.bladeSpark),want=kind==='steel'||kind==='iron';
                    check(shards.length===(want?18:0),'actual guard material '+kind+' reverse='+reverse);
                    check(kind==='avoided'?b.hp===hp:b.hp<=hp,'guard HP/avoidance '+kind);
                    if(want)check(hitstopRemaining===3*1000/60,'metal guard retains three-frame hitstop');
                    if(want)check(shards.every(p=>p.x===contact.x&&p.y===contact.y),'guard uses registered contact '+reverse);
                    guardResults.push({reverse,kind,hpBefore:hp,hp:b.hp,staminaBefore:stamina,stamina:b.stamina,hitstop:hitstopRemaining,shards:shards.map(p=>({x:p.x,y:p.y,life:p.life}))});
                }
                const counterResults=[];
                for(const reverse of [false,true])for(const kind of ['counter','saya'])for(const mat of ['steel','wood','flesh']){
                    setup(reverse);b.state=kind==='saya'?STATE.BLOCKING:STATE.PARRY_STANCE;b.parryFlashTimer=.2;b.gyakute=kind==='saya';b.sayaParryCd=0;
                    const hb={canClash:mat!=='flesh',mat,tier:STATE.ATTACK_LIGHT,pushback:0},hp=b.hp;
                    const emitter=createBladeSparks;let event=null;
                    createBladeSparks=(...args)=>{const q=combatPose(b);event={x:args[0],y:args[1],point:bladeGuardPoint(a,b,hb),cell:q.idx,body:q.body};return emitter(...args);};
                    try{b.takeDamage(10,a,hb);}finally{createBladeSparks=emitter;}
                    check(particles.filter(p=>p.bladeSpark).length===(mat==='steel'?18:0),'actual '+kind+' material '+mat+' reverse='+reverse);
                    if(kind==='counter'||mat==='steel')check(b.hp===hp,'counter still negates damage '+kind+mat);
                    if(mat==='steel')check(event&&event.x===event.point.x&&event.y===event.point.y,'counter registered at emission '+kind+reverse);
                    counterResults.push({reverse,kind,mat,event,hpBefore:hp,hp:b.hp});
                }
                // Guard contact uses the actual incoming rectangle when one intersects the body.
                for(const reverse of [false,true]){
                    setup(reverse);b.state=STATE.BLOCKING;const body=combatPose(b).body;
                    const hb={ox:body.x-a.x+5,oy:body.y-a.y+8,w:12,h:10};
                    const point=bladeGuardPoint(a,b,hb);
                    check(Math.abs(point.x-(body.x+11))<1e-8&&Math.abs(point.y-(body.y+13))<1e-8,'live rectangle guard intersection '+reverse);
                }
                const bindResults=[];
                for(const reverse of [false,true])for(const edge of ['center','left','right']){
                    setup(reverse);const left=edge==='left'?-20:edge==='right'?canvas.width-60:460;
                    a.x=left+(reverse?40:0);b.x=left+(reverse?0:40);clashCd=0;
                    const center=(a.x+a.width/2+b.x+b.width/2)/2;
                    for(const p of [a,b])p.hitboxes=[{ox:center-p.x-10,oy:20,w:20,h:20,canClash:true,mat:'steel',duration:.1,delay:0}];
                    check(processWeaponClash(a,b),'automatic bind '+edge+reverse);
                    const point=bladeLockPoint(a,b),entry=particles.filter(p=>p.bladeSpark);
                    check(entry.length===30&&entry.every(p=>p.x===point.x&&p.y===point.y),'post-fit bind contact '+edge+reverse);
                    check(point.x>=0&&point.x<=canvas.width&&point.y>=0&&point.y<=canvas.height,'bind contact inside viewport '+edge+reverse);
                    const stamp=()=>[a,b].map(p=>{const q=combatPose(p);return {name:p.spec.name,x:p.x,y:p.y,idx:q.idx,body:q.body,originX:q.originX,originY:q.originY,scale:q.S,shiftX:q.shiftX,reach:q.man.lockReach};});
                    const start=stamp(),pulses=[];particles.length=fxSprites.length=0;
                    // Advance the real pair update beyond one game second. No CPU inputs.
                    for(let i=0;i<66;i++){
                        updateBladeLock(a,b,1/60);
                        const fresh=particles.filter(p=>p.bladeSpark);
                        if(fresh.length){const q=bladeLockPoint(a,b);pulses.push({tick:i+1,count:fresh.length,x:fresh[0].x,y:fresh[0].y});
                            check(fresh.length===5&&fresh.every(p=>p.x===q.x&&p.y===q.y),'small registered grind pulse '+edge+reverse);}
                        check(!fxSprites.length,'no repeated flare in bind '+edge+reverse);
                        particles.length=0;
                    }
                    check(pulses.length===6,'six pair pulses in 1.1 game seconds '+edge+reverse);
                    const releasePoint=bladeLockPoint(a,b);a.lockMash=2;b.lockMash=0;resolveBladeLock(a,b);
                    check(particles.filter(p=>p.bladeSpark).every(p=>p.x===releasePoint.x&&p.y===releasePoint.y),'release retains pre-crossup contact '+edge+reverse);
                    const count=particles.length;updateBladeLock(a,b,.2);
                    check(particles.length===count,'no grind after lock resolves '+edge+reverse);
                    bindResults.push({reverse,edge,point,start,pulses});
                }
                setup();particles.length=0;fxSprites.length=0;
                for(const [hb,defHb] of [[null,null],[{canClash:false,mat:'steel'},null],[{canClash:true,mat:'steel'},{canClash:false,mat:'steel'}]])
                    createBladeSparks(500,300,a,b,hb,defHb);
                check(!particles.length&&!fxSprites.length,'no unconfirmed contact effect');
                createSparks(500,300,'#fff');
                check(particles.length>0&&particles.every(p=>p.type==='smoke'&&!p.bladeSpark),'generic contact dust preserved');
                // Age only the new spark with drag; legacy shards retain their exact integration.
                setup();particles.length=0;fxSprites.length=0;a.hitboxes.length=b.hitboxes.length=0;
                const plain={x:500,y:300,vx:300,vy:-100,life:1,maxLife:1,shard:true,gravity:true,radius:1,color:'#fff'};
                const gold={...plain,bladeSpark:true,len:12};particles.push(plain,gold);
                const dt=1/60;updateGame(dt/COMBAT_TEMPO);
                check(Math.abs(plain.vx-300)<1e-8&&Math.abs(plain.vy-(-100+420*dt))<1e-8,'legacy shard integration unchanged');
                check(Math.abs(gold.vx-300*Math.exp(-3*dt))<1e-8&&Math.abs(gold.vy-(-100+420*dt)*Math.exp(-3*dt))<1e-8,'tagged drag and gravity units');
                const trace=traceLenticular;let strokes=0;
                traceLenticular=(...v)=>{check(v.every(Number.isFinite),'finite tapered spark geometry');strokes++;return trace(...v);};
                try{drawScene();gold.vx=gold.vy=0;drawScene();}finally{traceLenticular=trace;}
                check(strokes>=4,'tapered spark renderer reached including stationary particle');
                setup();processWeaponClash(a,b);
                const raf=window.requestAnimationFrame;window.requestAnimationFrame=()=>0;
                const start={x:a.x,y:a.y,bx:b.x,clock:animClock,hp:a.hp,particles:JSON.stringify(particles),fx:JSON.stringify(fxSprites)};
                const frames=[],captures=[];
                try{
                    for(let i=0;i<6;i++){
                        gameLoop(lastTime+1000/60);
                        check(a.x===start.x&&a.y===start.y&&b.x===start.bx&&animClock===start.clock&&a.hp===start.hp,'true freeze tick '+i);
                        check(JSON.stringify(particles)===start.particles&&JSON.stringify(fxSprites)===start.fx,'contact effects freeze tick '+i);
                        frames.push({tick:i+1,freeze:clashFreezeRemaining,shake:clashShakeRemaining});
                        captures.push(canvas.toDataURL());
                    }
                    check(clashFreezeRemaining<1e-6&&clashShakeRemaining===0,'six freeze/four shake frames');
                    for(let i=0;i<28;i++){gameLoop(lastTime+1000/60);captures.push(canvas.toDataURL());}
                    check(a.x<start.x&&b.x>start.bx,'both recoil after thaw');
                    check(!a.hitboxes.length&&!b.hitboxes.length,'no delayed follow-up');
                    check(!particles.some(p=>p.bladeSpark),'expired sparks removed');
                    check(!fxSprites.length,'expired contact flare removed');
                }finally{window.requestAnimationFrame=raf;}
                paused=true;drawScene();
                return {version:SHEET_V,failures,checks,frames,guardResults,counterResults,bindResults,captures};
                ''')
                assert result and '__error' not in result,result
                captures=result.pop('captures')
                images=[Image.open(io.BytesIO(base64.b64decode(v.split(',')[1]))).convert('RGB') for v in captures]
                crops=[im.crop((300,500,800,740)) for im in images]
                board=Image.new('RGB',(500*4,260*((len(crops)+3)//4)),'#15151a');labels=ImageDraw.Draw(board)
                for i,im in enumerate(crops):
                    images[i].save(out/f'{i:03}.png')
                    board.paste(im,(i%4*500,i//4*260+20));labels.text((i%4*500+8,i//4*260+3),f'Consecutive clash frame {i+1}',fill='white')
                board.save(out/'native-filmstrip.jpg',quality=95)
                result['sourceSHA256']=source_hash
                result['sourceStable']=source_hash==hashlib.sha256(source.read_bytes()).hexdigest()
                (out/'result.json').write_text(json.dumps(result,indent=2))
                print(json.dumps(result,indent=2))
                assert not result['failures'],result['failures']
                assert result['sourceStable'],'production changed during this check; rerun stable version'
        finally:proc.terminate();proc.wait(timeout=10)

if __name__=='__main__':asyncio.run(main())
