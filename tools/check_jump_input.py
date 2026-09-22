#!/usr/bin/env python3
"""Exercise real keyboard/touch jumps and wall escapes for every fighter on :9101."""
import asyncio
import json
import os
import tempfile
from pathlib import Path

import websockets
import watch_game as browser


async def main():
    url = os.environ.get('SHADOWCLASH_URL', 'http://localhost:9101/index.html')
    browser.assert_serving_this_tree(url)
    browser.PORT = int(os.environ.get('DEBUG_PORT', '9372'))
    with tempfile.TemporaryDirectory(prefix='jump-input-') as profile:
        proc, address = browser.launch(url, profile)
        try:
            async with websockets.connect(address, max_size=20_000_000) as ws:
                c = browser.CDP(ws)
                for _ in range(400):
                    if await c.js("return typeof SPRITES!=='undefined'&&NINJA_ROSTER.every(s=>SPRITES[s.name.toLowerCase()]?.ready)"):
                        break
                    await asyncio.sleep(.1)
                result = await c.js(r'''
                dismissTitle();const failures=[],arcs=[],walls=[],resets=[];let inputs=0;
                const check=(ok,message)=>{if(!ok)failures.push(message);};
                const key=(code,down)=>window.dispatchEvent(new KeyboardEvent(down?'keydown':'keyup',{code,bubbles:true}));
                const reset=(id,seat=0)=>{
                    gameMode='2p';cpuMode=false;spectate=false;stagePick='bamboo';
                    p1Pick=seat?0:id;p2Pick=seat?id:(id===0?1:0);startNewGame();
                    paused=false;roundIntroTimer=0;hitstopRemaining=0;cutscene=null;
                    for(const k in keys)keys[k]=false;physKeys.clear();
                    const p=seat?player2:player1,foe=seat?player1:player2;
                    Object.assign(p,{x:60,y:GROUND_Y-p.height,vx:0,vy:0,state:STATE.IDLE,isGrounded:true,jumpsLeft:2});
                    foe.x=canvas.width-50-foe.width;return p;
                };
                for(let id=0;id<9;id++){
                    for(const seat of [0,1]){
                        let p=reset(id,seat);const code=seat?'ArrowUp':'KeyW',lift=(570*JUMP_GRAVITY_SCALE+JUMP_GRAVITY_BIAS)*(p.spec.jumpScale||1);
                        key(code,true);check(p.state===STATE.JUMP&&Math.abs(p.vy+lift)<.01,id+' immediate takeoff '+seat);
                        key(code,false);check(Math.abs(p.vy+lift*.5)<.01,id+' immediate release '+seat);inputs++;
                        for(const ending of ['touchend','touchcancel','slide']){
                            p=reset(id,seat);const pad=document.getElementById(seat?'pad-p2':'pad-p1');
                            let target=pad.querySelector('[data-dir="up"]');const original=document.elementFromPoint;
                            document.elementFromPoint=()=>target;
                            const t=new Touch({identifier:17,target,clientX:0,clientY:0});
                            const touch=type=>pad.dispatchEvent(new TouchEvent(type,{changedTouches:[t],touches:type==='touchend'||type==='touchcancel'?[]:[t],bubbles:true,cancelable:true}));
                            try{
                                touch('touchstart');for(let n=0;n<3;n++)updateGame(1/60);
                                const vy=p.vy;touch('touchmove');check(p.vy===vy,id+' moving within Up cut the jump');
                                if(ending==='slide'){target=pad.querySelector('[data-dir="right"]');touch('touchmove');}else touch(ending);
                                check(Math.abs(p.vy-vy*.5)<.01,id+' '+ending+' did not cut '+seat);
                                const cut=p.vy;touch('touchend');check(p.vy===cut,id+' release cut twice '+seat);inputs++;
                            }finally{document.elementFromPoint=original;}
                        }
                    }
                    for(const mode of ['full','tap','double','release-direction'])for(const axis of [0,1]){
                        const p=reset(id),startY=p.y,startX=p.x;
                        // Extra empty width measures travel without the arena ending long double jumps.
                        canvas.width=2400;player2.x=2300;if(axis)key('KeyD',true);key('KeyW',true);
                        let top=p.y,ticks=0,doubled=false;
                        for(;ticks<180;ticks++){
                            if(mode==='tap'&&ticks===1)key('KeyW',false);
                            if(mode==='release-direction'&&ticks===6)key('KeyD',false);
                            if(mode==='double'&&!doubled&&ticks>5&&p.vy>=0){key('KeyW',false);key('KeyW',true);doubled=true;}
                            updateGame(1/60);top=Math.min(top,p.y);
                            check(Number.isFinite(p.x+p.y+p.vy),id+' nonfinite arc');
                            if(p.isGrounded)break;
                        }
                        const height=startY-top;check(p.isGrounded&&ticks<179,id+' did not land '+mode);
                        if(mode==='full')check(height>140*(p.spec.jumpScale||1)**2,id+' short full arc');
                        if(mode==='full'&&id===0)check((ticks+1)/60>=.80&&(ticks+1)/60<=.90,'old-style full-jump airtime');
                        if(mode==='double')check(height>280*(p.spec.jumpScale||1)**2,id+' short double arc');
                        if(mode==='tap')check(height<65,id+' tap became full jump');
                        arcs.push({id,mode,axis,height,seconds:(ticks+1)/60,range:p.x-startX});
                    }
                    // The ordinary jump budget still refuses a third press.
                    let p=reset(id);for(let n=0;n<2;n++){key('KeyW',true);updateGame(1/60);key('KeyW',false);}
                    const vy=p.vy;key('KeyW',true);check(p.jumpsLeft===0&&p.vy===vy,id+' third jump escaped budget');
                    p=reset(id);key('KeyF',true);check(p.isAttackingState(),id+' commitment check never attacked');
                    key('KeyW',true);check(p.isGrounded&&p.vy===0,id+' jump canceled an attack');
                    // A thin platform catches the head on ascent and permits a drop/landing.
                    p=reset(id);const under=p.y-110;PLATFORMS.push({x:20,y:under-10,w:canvas.width-40,h:10});key('KeyW',true);
                    for(let n=0;n<50&&p.ceilLatch<=0;n++){updateGame(1/60);check(p.y>=under-.1,id+' ceiling tunneling');}
                    check(p.ceilLatch>0,id+' no ceiling latch');key('KeyW',false);key('KeyW',true);
                    check(p.ceilLatch===0&&p.vy>0,id+' ceiling release failed');key('KeyW',false);
                    for(let n=0;n<90;n++)updateGame(1/60);check(p.isGrounded,id+' latch release did not land');
                    for(const side of [-1,1])for(const mode of ['hold','release','kick-neutral','kick-away','kick-into']){
                        p=reset(id);
                        // Disable head-hops on the observer so this measures the wall arc alone.
                        Object.assign(player2,{x:canvas.width/2,state:STATE.STUNNED,stunTimer:10});
                        const toward=side<0?'KeyA':'KeyD',away=side<0?'KeyD':'KeyA';
                        Object.assign(p,{x:side<0?11:canvas.width-11-p.width,y:GROUND_Y-p.height-160,vy:0,isGrounded:false,state:STATE.JUMP});
                        key(toward,true);for(let n=0;n<3;n++)updateGame(1/60);
                        check(p.wallDir===side&&p.state===STATE.WALL_CLING,id+' wall catch');
                        const startY=p.y;let top=p.y;
                        if(mode==='release'||mode==='kick-neutral'||mode==='kick-away')key(toward,false);
                        if(mode==='kick-away')key(away,true);
                        if(mode.startsWith('kick')){key('KeyW',true);check(p.vy===-WALL_LIFT&&p.vx*side<0,id+' kick impulse');}
                        for(let n=0;n<80;n++){updateGame(1/60);top=Math.min(top,p.y);check(p.x>=9.9&&p.x+p.width<=canvas.width-9.9,id+' wall tunneling');}
                        if(mode==='hold'||mode==='kick-into')check(p.wallDir===side&&p.state===STATE.WALL_CLING,id+' wall hold/regrip');
                        else check(p.isGrounded,id+' wall release did not land '+mode);
                        if(mode==='kick-neutral'||mode==='kick-away')check(startY-top>130,id+' wall arc too low');
                        walls.push({id,side,mode,rise:startY-top});
                    }
                }
                // R must cancel real in-flight actions without replacing the fighter or refunding round caps.
                const assertReset=(p,label)=>{
                    const saved={smokeUsed:2,enlightenUsed:true,bossEnlightUsed:true,bossFrenzyUsed:true,karma:2,dread:2,champion:2};
                    if(p.spec.id===6)Object.assign(saved,{cracked:true,crackTimer:3});
                    if(p.spec.id===7)Object.assign(saved,{frenzyTimer:3});
                    Object.assign(p,saved);const object=p;
                    key('KeyR',true);key('KeyR',false);
                    check(p===object&&(p===player1||p===player2),label+' replaced the fighter');
                    for(const [name,value] of Object.entries(saved))check(p[name]===value,label+' reset '+name);
                    check(p.isGrounded&&p.jumpsLeft===2&&p.state===STATE.IDLE,label+' stale ground/jump state');
                    check(!p.dashTimer&&!p.rollTimer&&!p.rollRecover&&!p.wallDir&&!p.wallJumpLock&&!p.ceilLatch&&!p.grappleT,label+' stale movement');
                    check(!p.attackAnim&&!p.recoveryTimer&&!p.bufferedAttack&&!p.wireBindFoe&&!p.chain&&!p.projectiles.length&&!p.hitboxes.length,label+' stale attack');
                    check(!Object.values(keys).some(Boolean)&&!physKeys.size&&!hitstopQueue.length,label+' queued input');
                    const x=p.x,y=p.y;for(let n=0;n<5;n++)updateGame(1/60);
                    check(p.x===x&&p.y===y&&p.isGrounded,label+' moved after neutral reset');
                    key('KeyW',true);check(p.state===STATE.JUMP&&p.jumpsLeft===1,label+' first jump blocked');
                    key('KeyW',false);key('KeyW',true);check(p.jumpsLeft===0,label+' second jump blocked');
                    const vy=p.vy;key('KeyW',false);key('KeyW',true);check(p.jumpsLeft===0&&p.vy===vy*.5,label+' third jump allowed');
                    key('KeyW',false);resets.push(label);
                };
                for(let id=0;id<9;id++)for(const action of ['dash','roll','wall','attack']){
                    const p=reset(id);gameMode='training';drillIdx=0;
                    if(action==='dash'||action==='roll'){
                        if(action==='roll')key('KeyS',true);
                        key('KeyD',true);key('KeyD',false);key('KeyD',true);
                        check(action==='dash'?p.dashTimer>0:p.rollTimer>0,id+' reset setup '+action);
                    }else if(action==='wall'){
                        Object.assign(p,{x:11,y:GROUND_Y-p.height-160,isGrounded:false,state:STATE.JUMP});
                        key('KeyA',true);for(let n=0;n<3;n++)updateGame(1/60);key('KeyW',true);
                        check(p.wallJumpLock>0&&!p.isGrounded,id+' reset setup wall');
                    }else{
                        key('KeyF',true);key('KeyH',true);
                        check(p.isAttackingState()&&p.recoveryTimer>0,id+' reset setup attack');
                    }
                    assertReset(p,id+' '+action);
                }
                let p=reset(7);gameMode='training';p.x=600;key('KeyD',true);key('KeyH',true);
                check(p.grappleT>0,'Exile reset setup grapple');assertReset(p,'Exile grapple');
                // A released air throw must not detonate on the newly reset victim's feet.
                p=reset(7);gameMode='training';const victim=player2;
                Object.assign(p,{x:250,y:GROUND_Y-p.height-180,isGrounded:false,state:STATE.JUMP});
                Object.assign(victim,{x:280,y:p.y,isGrounded:false,state:STATE.JUMP});
                key('KeyF',true);key('KeyG',true);check(p.throwTimer>0&&p.throwAir,'air-throw reset setup');
                for(let n=0;n<40&&!victim.skySlam;n++)updateGame(1/60);
                check(victim.skySlam,'air-throw release setup');hitstopRemaining=0;
                key('KeyR',true);key('KeyR',false);check(!victim.skySlam&&!victim.grabbedBy&&!p.throwVictim,'air throw survived reset');
                for(let n=0;n<20;n++)updateGame(1/60);
                check(victim.hp===victim.maxHp&&victim.isGrounded,'air throw detonated after reset');resets.push('air-throw victim');
                for(const stage of ['abyss','lantern']){
                    p=reset(0);gameMode='training';stagePick=stage;startNewGame();paused=false;roundIntroTimer=0;
                    const originals=[player1,player2];key('KeyR',true);key('KeyR',false);
                    for(const q of originals){
                        check(q.isGrounded&&q.jumpsLeft===2,stage+' reset airborne '+q.id);
                        check(currentStage.abyss?q.riding&&abyssSlabs.includes(q.riding):hasFloorAt(q.x+q.width/2),stage+' reset no footing '+q.id);
                    }
                    for(let n=0;n<15;n++)updateGame(1/60);
                    for(const q of originals)check(q.isGrounded&&q.hp===q.maxHp&&q.y<GROUND_Y,stage+' fell after reset '+q.id);
                    resets.push(stage+' footing');
                }
                // A virtual pad must never shorten a CPU-controlled fighter's jump.
                for(const seat of [0,1]){
                    const p=reset(0,seat);gameMode='watch';cpuMode=true;spectate=true;
                    Object.assign(p,{isGrounded:false,state:STATE.JUMP,vy:-300});
                    const pad=document.getElementById(seat?'pad-p2':'pad-p1'),target=pad.querySelector('[data-dir="up"]');
                    const t=new Touch({identifier:18,target,clientX:0,clientY:0});
                    keys[(seat?'p2_':'p1_')+'up']=true;
                    pad.dispatchEvent(new TouchEvent('touchstart',{changedTouches:[t],touches:[t],bubbles:true,cancelable:true}));
                    check(p.vy===-300,'touch altered CPU jump '+seat);
                }
                paused=true;for(const k in keys)keys[k]=false;physKeys.clear();
                return {failures,inputs,arcs,walls,resets};
                ''')
                assert result and '__error' not in result, result
                out = Path(os.environ.get('OUT', 'media/jump-functionality-20260907'))
                out.mkdir(parents=True, exist_ok=True)
                (out/'checks.json').write_text(json.dumps(result, indent=2))
                assert not result['failures'], result['failures']
                print(f"PASS: {result['inputs']} keyboard/touch cases, {len(result['arcs'])} arcs, {len(result['walls'])} walls, {len(result['resets'])} training resets; all nine ceiling and jump-budget checks")
        finally:
            proc.terminate()
            proc.wait(timeout=10)


if __name__ == '__main__':
    asyncio.run(main())
