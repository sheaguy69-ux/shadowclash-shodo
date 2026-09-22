#!/usr/bin/env python3
"""Live engine regression for authored Footsies frame windows and shared physics."""
import asyncio
import json
import os
import tempfile
from pathlib import Path
import websockets
import watch_game as browser

async def main():
    url=os.environ.get('SHADOWCLASH_URL','http://localhost:9101/index.html')
    browser.assert_serving_this_tree(url)
    browser.PORT=int(os.environ.get('DEBUG_PORT','9382'))
    with tempfile.TemporaryDirectory(prefix='footsies-check-') as profile:
        proc,address=browser.launch(url,profile)
        try:
            async with websockets.connect(address,max_size=100_000_000) as ws:
                c=browser.CDP(ws)
                for _ in range(400):
                    if await c.js("return typeof SPRITES!=='undefined'&&NINJA_ROSTER.every(s=>SPRITES[s.name.toLowerCase()]?.ready)&&FX_CRESCENT.ready"):
                        break
                    await asyncio.sleep(.1)
                result=await c.js(r'''
                dismissTitle(); const failures=[],samples=[];
                const check=(ok,msg)=>{if(!ok)failures.push(msg);};
                const setup=(id=0,facing=1)=>{
                    gameMode='2p';cpuMode=false;spectate=false;stagePick='bamboo';p1Pick=id;p2Pick=5;
                    startNewGame();paused=false;roundIntroTimer=0;hitstopRemaining=0;cutscene=null;releaseAllKeys();
                    for(const [p,x] of [[player1,450],[player2,facing>0?850:100]])
                        Object.assign(p,{x,y:GROUND_Y-p.height,isGrounded:true,_wasGrounded:true,vx:0,vy:0,state:STATE.IDLE,jumpsLeft:2});
                    player1.facing=facing;return player1;
                };
                const begin=(p)=>{keys[p.facing>0?'KeyD':'KeyA']=true;p.executeAttack(STATE.ATTACK_LIGHT);releaseAllKeys();check(p.attackAnim?.moveId===SHADOW_SLICE.move_id,'forward Light not routed');};
                const tick=()=>{hitstopRemaining=0;updateGame(1/(60*COMBAT_TEMPO));};
                for(const facing of [-1,1]){
                    let p=setup(0,facing);begin(p);
                    const start=animClock;
                    for(let frame=1;frame<=9;frame++){
                        const f=footsiesFrame(p);check(f?.frame_index===frame,'frame clock '+frame+' got '+f?.frame_index);
                        check(spriteFrameIndex(p,SPRITES.executioner.frames)===SPRITES.executioner.frames[SHADOW_SLICE.frames[frame-1].sprite],'source cell '+frame);
                        if(frame===3||frame===4)check(spriteFrameIndex(p,SPRITES.executioner.frames)===296,'approved forward strike source');
                        const hurt=p.hurtbox(), r=footsiesRect(p,SHADOW_SLICE.frames[frame-1].hurtbox);
                        check(JSON.stringify(hurt)===JSON.stringify(r),'hurtbox mismatch '+frame);
                        const h=p.hitboxes[0];check(!!h,'missing shared hitbox '+frame);
                        if(h){const b=footsiesRect(p,{x:12,y:15,width:50,height:20});
                            // Put the defender inside the authored strike, without a physics/pushbox tick.
                            player2.x=b.x;player2.y=b.y;player2.isGrounded=false;player2.invulnTimer=0;
                            const hp=player2.hp;processHitboxes(p,player2,0,false);
                            const did=player2.hp<hp;check(did===(frame===3||frame===4),'hit window '+frame);
                            if(did){check(Math.abs(player2.stunTimer-14/60)<1e-9,'hitstun14');check(Math.abs(player2.vx-facing*350)<1e-8&&Math.abs(player2.vy)<1e-8,'hit vector');}
                        }
                        samples.push({facing,frame,hurt,cell:spriteFrameIndex(p,SPRITES.executioner.frames)});
                        // Fresh move at each sample avoids once-per-victim suppression without altering its age.
                        p=setup(0,facing);begin(p);animClock=p.attackAnim.start/1000+frame/60;
                    }
                    p=setup(0,facing);begin(p);for(let i=0;i<9;i++)tick();
                    check(!p.isAttackingState()&&!footsiesFrame(p),'nine-frame recovery never ends');
                }
                for(const kind of ['JUMP','SMOKE_DASH','SPECIAL_MOVE'])for(const frame of [2,3,4,5,6])for(const clean of [false,true]){
                    const p=setup();begin(p);animClock=p.attackAnim.start/1000+(frame-1)/60;p.attackAnim.cleanHit=clean;
                    p.attackHasConnected=true;p.connectTime=animClock;
                    if(kind==='JUMP')p.executeJump();
                    if(kind==='SMOKE_DASH')p.executeShunshin(1);
                    if(kind==='SPECIAL_MOVE')p.executeAttack(STATE.ATTACK_SPECIAL);
                    const canceled=p.attackAnim?.moveId!==SHADOW_SLICE.move_id;
                    check(canceled===(clean&&frame>=3&&frame<=5),kind+' cancel '+frame+' clean '+clean);
                    if(canceled)check(!p.hitboxes.some(h=>h.frameMove),'cancel left phantom hitbox');
                }
                // Actual block confirms cannot unlock this move's hit-only cancels.
                {const p=setup();begin(p);animClock=p.attackAnim.start/1000+2/60;
                    const r=footsiesRect(p,{x:12,y:15,width:50,height:20});
                    Object.assign(player2,{x:r.x,y:GROUND_Y-player2.height,state:STATE.BLOCKING,isGrounded:true,facing:-1});
                    processHitboxes(p,player2,0,false);check(p.attackHasConnected&&!p.attackAnim.cleanHit,'block confirm mistaken for clean hit');}
                for(let id=0;id<NINJA_ROSTER.length;id++){
                    const p=setup(id);keys.KeyD=true;p.handleMovement(1/60);check(p.vx>0,'instant start '+id);
                    releaseAllKeys();p.handleMovement(1/60);check(p.vx===0,'instant stop '+id);
                    p.executeShunshin(1);for(let i=0;i<3;i++)p.handleMovement(1/60);
                    check(p.dashTimer>0,'microdash stopped before minimum '+id);p.handleMovement(1/60);
                    check(p.dashTimer===0&&p.vx===0,'microdash failed brake '+id);
                    p.recoveryTimer=0;p.state=STATE.IDLE;p.y=GROUND_Y-p.height-1;p.isGrounded=false;p.vy=900;p.applyPhysics(1/60);
                    check(p.isGrounded&&p.recoveryTimer===0,'landing control tax '+id);
                    const launches=[];
                    for(const axis of [-1,0,1]){
                        const q=setup(id);q.isGrounded=false;q.y=200;keys[axis>0?'KeyD':'KeyA']=axis!==0;
                        q.takeDamage(8,player2,{pushback:100,launch:true,launchVy:-430});
                        launches.push({vx:q.vx,vy:q.vy,speed:Math.hypot(q.vx,q.vy)});
                    }
                    check(Math.abs(launches[0].speed-launches[1].speed)<1e-7&&Math.abs(launches[2].speed-launches[1].speed)<1e-7,'DI adds energy '+id);
                    check(launches[0].vx<launches[1].vx&&launches[1].vx<launches[2].vx,'DI directions '+id);
                    check(Math.abs(launches[1].speed-Math.hypot(200,430*JUMP_GRAVITY_SCALE)/FOOTSIES.weightById[id])<1e-7,'weight scale '+id);  // ⛔ 430 IS SCALED. Build 857 took gravity 1100->1650 and scaled the ONE site that applies a launch ((launchVy ?? -430) * JUMP_GRAVITY_SCALE), so a raw 430 here expects a launch the engine stopped producing. Mirror the engine's own multiply or this fails on every fighter for a change that was deliberate.
                }

                // Live collision progression: two startup ticks, one contact per victim, finite whiff tail.
                {const p=setup();begin(p);const r=footsiesRect(p,{x:12,y:15,width:50,height:20});
                    player2.x=r.x;const damage=[];let hp=player2.hp;
                    for(let i=0;i<10;i++){tick();damage.push(hp-player2.hp);hp=player2.hp;}
                    check(damage[0]===0&&damage[1]>0&&damage.filter(d=>d>0).length===1,'live hit boundaries/repeat '+damage);
                    check(p.state===STATE.IDLE,'live move recovery ended');}
                // Existing ordinary Light still cancels immediately on actual hit OR block.
                for(const block of [false,true]){
                    const p=setup(5);p.executeAttack(STATE.ATTACK_LIGHT);
                    Object.assign(player2,{x:p.x+p.width+5,y:GROUND_Y-player2.height,state:block?STATE.BLOCKING:STATE.IDLE,facing:-1});
                    for(let i=0;i<8&&!p.attackHasConnected;i++){
                        animClock+=1/60;processHitboxes(p,player2,1/60);
                    }
                    check(p.attackHasConnected,'existing confirm '+block);
                    p.executeAttack(STATE.ATTACK_HEAVY);check(p.state===STATE.ATTACK_HEAVY,'existing immediate cancel '+block);
                }
                // Neutral aerial Light cancels on landing; Heavy keeps its punishable recovery.
                for(const type of [STATE.ATTACK_LIGHT,STATE.ATTACK_HEAVY]){
                    const p=setup(5);p.isGrounded=false;p.y=GROUND_Y-p.height-1;p.executeAttack(type);
                    p.vy=900;p.applyPhysics(1/60);
                    check(p.isGrounded,'air landing setup');
                    check(type===STATE.ATTACK_LIGHT?!p.isAttackingState()&&p.recoveryTimer===0:p.isAttackingState()&&p.recoveryTimer>0,'air landing cancel '+type);
                }
                // The new global pull keeps finite, distinct roster jump arcs and wall-jump lift.
                const arcs=[];
                for(let id=0;id<NINJA_ROSTER.length;id++){
                    const p=setup(id);p.executeJump();const foot=GROUND_Y;let peak=0,steps=0;
                    // ⛔ JUMP_SQUAT IS 0.05 AND executeJump ONLY ARMS IT. The launch fires in
                    // handleMovement ~3 ticks later, so an applyPhysics-only loop watched a fighter
                    // who never left the floor and called a correct jump broken on all 8. Same defect
                    // check_jump_commit.mjs carried until 847 — drive the squat out first.
                    for(let s=0;s<8&&p.jumpSquatT>0;s++)p.handleMovement(1/60);
                    while(!p.isGrounded&&steps++<180){p.applyPhysics(1/60);peak=Math.max(peak,foot-p.y-p.height);}
                    check(p.isGrounded&&peak>40&&Number.isFinite(peak),'profile jump '+id);
                    arcs.push(peak);
                }
                check(arcs[arcs.length-1]>arcs[0],'profile preserves jump ranking');  // ⛔ WAS arcs[7]>arcs[8]&&arcs[8]>arcs[0] on a roster of NINE. Oni retired, arcs is 8 long, and arcs[8] is undefined — every comparison against it is false, so this asserted nothing but its own failure.
                samples.push({arcs});

                // Second owner-authored move: all16 frames, nullable hull, strike7–9, hit-only8–10.
                const smoke=FOOTSIES_DATA.moves.find(m=>m.move_id==='smoke_bomb_shadow_strike');
                const beginSmoke=p=>{keys[p.facing>0?'KeyD':'KeyA']=true;p.executeAttack(STATE.ATTACK_SPECIAL);releaseAllKeys();check(p.attackAnim?.moveId===smoke.move_id,'forward Special not routed');};
                for(const facing of [-1,1])for(let frame=1;frame<=16;frame++){
                    const p=setup(0,facing);beginSmoke(p);animClock=p.attackAnim.start/1000+(frame-1)/60;
                    const f=footsiesFrame(p);check(f?.frame_index===frame,'smoke frame '+frame);
                    const hurt=p.hurtbox();check((hurt===null)===(frame===3||frame===4),'vanish hull '+frame);
                    const hp=p.hp;p.takeDamage(8,player2,{pushback:0,tier:STATE.ATTACK_LIGHT});
                    check((p.hp===hp)===(frame===3||frame===4),'vanish immunity '+frame);
                    const q=setup(0,facing);beginSmoke(q);animClock=q.attackAnim.start/1000+(frame-1)/60;
                    const r=footsiesRect(q,f.hitbox||{x:10,y:10,width:55,height:25});
                    Object.assign(player2,{x:r.x,y:r.y,isGrounded:false});
                    const before=player2.hp;processHitboxes(q,player2,0,false);
                    const hit=player2.hp<before;check(hit===(frame>=7&&frame<=9),'smoke strike window '+frame);
                    if(hit){check(Math.abs(player2.stunTimer-22/60)<1e-8,'smoke hitstun');check(Math.abs(player2.vx-facing*500)<1e-8&&Math.abs(player2.vy+400)<1e-8,'smoke vector');}
                }
                for(const kind of ['JUMP','SMOKE_DASH','SPECIAL_MOVE'])for(const frame of [7,8,9,10,11])for(const clean of [false,true]){
                    const p=setup();beginSmoke(p);animClock=p.attackAnim.start/1000+(frame-1)/60;p.attackAnim.cleanHit=clean;
                    p.attackHasConnected=true;p.connectTime=animClock;
                    if(kind==='JUMP')p.executeJump();if(kind==='SMOKE_DASH')p.executeShunshin(1);if(kind==='SPECIAL_MOVE')p.executeAttack(STATE.ATTACK_SPECIAL);
                    check((p.attackAnim?.moveId!==smoke.move_id)===(clean&&frame>=8&&frame<=10),'smoke '+kind+' cancel '+frame+' '+clean);
                }
                {const p=setup();beginSmoke(p);animClock=p.attackAnim.start/1000+6/60;
                    const r=footsiesRect(p,{x:10,y:10,width:55,height:25});
                    Object.assign(player2,{x:r.x,y:GROUND_Y-player2.height,state:STATE.BLOCKING,isGrounded:true,facing:-1});
                    processHitboxes(p,player2,0,false);check(Math.abs(player2.stunTimer-12/60)<1e-8,'smoke blockstun12');check(!p.attackAnim.cleanHit,'smoke block unlocks cancel');}


                // Null hulls suppress contact but never freeze the opposing swing's lifetime.
                for(const facing of [-1,1]){
                    const p=setup(0,facing);beginSmoke(p);const enemy=player2;
                    enemy.spawnHitbox(500,500,8,2/60,80,{tier:STATE.ATTACK_LIGHT,canClash:false});
                    const h=enemy.hitboxes.at(-1);Object.assign(h,{ox:p.x-enemy.x-100,oy:p.y-enemy.y-100,w:500,h:500,delay:0});
                    enemy.attackHasConnected=false;enemy.hitConfirmed=false;const hp=p.hp;
                    for(const frame of [3,4]){
                        animClock=p.attackAnim.start/1000+(frame-1)/60;
                        const before=h.duration;processHitboxes(enemy,p,1/60);
                        check(Math.abs(h.duration-(before-1/60))<1e-9,'null hull paused opposing active timer '+frame);
                        check(p.hp===hp&&!enemy.attackHasConnected&&!enemy.hitConfirmed,'null hull granted damage/confirm '+frame);
                    }
                    check(!enemy.hitboxes.includes(h),'opposing box survived null hull expiry');
                }
                // Inspect the real draw call: the approved crescent exists only during authored active frames.
                const fxCanvas=document.createElement('canvas');fxCanvas.width=1280;fxCanvas.height=720;
                const fxCtx=fxCanvas.getContext('2d');let fxSamples=0;
                for(const move of [SHADOW_SLICE,smoke])for(const facing of [-1,1])for(const frame of move.frames){
                    const p=setup(0,facing);if(move===smoke)beginSmoke(p);else begin(p);
                    animClock=p.attackAnim.start/1000+(frame.frame_index-1)/60;
                    const calls=[],original=fxCtx.drawImage;
                    fxCtx.drawImage=function(...args){if(args[0]===FX_CRESCENT.img){const m=this.getTransform();calls.push({x:m.e,y:m.f,sx:m.a,w:args[3],h:args[4]});}return original.apply(this,args);};
                    try{drawSprite(fxCtx,p);}finally{fxCtx.drawImage=original;}
                    check(calls.length===(frame.hitbox?1:0),'crescent active-only '+move.move_id+' '+frame.frame_index);
                    if(frame.hitbox&&calls.length){const r=footsiesRect(p,frame.hitbox),draw=calls[0];
                        check(Math.abs(draw.x-(facing>0?r.x:r.x+r.w))<1e-3&&Math.abs(draw.y-r.y)<1e-3&&draw.sx===facing&&Math.abs(draw.w-r.w)<1e-8&&Math.abs(draw.h-r.h)<1e-8,'crescent/strike envelope '+move.move_id+' '+frame.frame_index+' '+JSON.stringify({draw,r}));}
                    fxSamples++;
                }
                samples.push({fxSamples});
                const liveSmoke=[];
                for(const facing of [-1,1])for(const distance of [55,300])for(const wall of [false,true]){
                    const p=setup(0,facing);if(wall)p.x=facing>0?canvas.width-180:150;
                    player2.x=Math.max(10,Math.min(canvas.width-player2.width-10,p.x+facing*distance));
                    const actualDistance=Math.abs(player2.x-p.x),start=p.x;
                    // Keyboard route, not a direct branch invocation.
                    const code=facing>0?'KeyD':'KeyA';
                    window.dispatchEvent(new KeyboardEvent('keydown',{code,bubbles:true}));
                    window.dispatchEvent(new KeyboardEvent('keydown',{code:'KeyH',bubbles:true}));
                    window.dispatchEvent(new KeyboardEvent('keyup',{code:'KeyH',bubbles:true}));
                    window.dispatchEvent(new KeyboardEvent('keyup',{code,bubbles:true}));
                    check(p.attackAnim?.moveId===smoke.move_id,'live keyboard Smoke route');
                    let hp=player2.hp;const hits=[],path=[];
                    for(let i=0;i<18;i++){
                        tick();if(player2.hp<hp)hits.push({tick:i+1,damage:hp-player2.hp});hp=player2.hp;
                        path.push({frame:footsiesFrame(p)?.frame_index??null,x:p.x,vx:p.vx,facing:p.facing});
                        if(i===15)check(!p.isAttackingState()&&!footsiesFrame(p),'Smoke extra recovery frame17');
                        check(Number.isFinite(p.x+p.y+p.vx+p.vy)&&p.x>=10&&p.x+p.width<=canvas.width-10,'live Smoke wall/finite');
                    }
                    check(hits.length<=1,'Smoke repeated damage');
                    if(!wall)check((hits.length===1)===(distance===55),'Smoke near/far hit '+facing+' '+distance);
                    check(!p.isAttackingState()&&p.recoveryTimer<=0,'Smoke never recovers');
                    liveSmoke.push({facing,distance,wall,actualDistance,start,hits,path});
                }
                samples.push({liveSmoke});
                check(GRAVITY===-FOOTSIES_DATA.engine_settings.gravity*100,'profile gravity');
                paused=true;releaseAllKeys();return {failures,samples,gravity:GRAVITY,tempo:COMBAT_TEMPO};
                ''')
                assert result and '__error' not in result,result
                out=Path(os.environ.get('OUT','media/footsies-physics'));out.mkdir(exist_ok=True,parents=True)
                (out/'checks.json').write_text(json.dumps(result,indent=2))
                assert not result['failures'],result['failures']
                print('PASS: both authored moves, 25 frames both facings, hit/block/cancel windows, 8 live Smoke near/far/wall routes; nine-roster snap/microdash/landing/weight/DI and jump reach')
        finally:
            proc.terminate();proc.wait(timeout=10)

if __name__=='__main__':asyncio.run(main())
