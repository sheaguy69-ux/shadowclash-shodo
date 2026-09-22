#!/usr/bin/env python3
"""Retired Mokurai wire routes; existing neutral/catch and Shin wire stay playable."""
import asyncio
import json
import tempfile
from pathlib import Path

import websockets
import watch_game as browser


async def main():
    url = 'http://localhost:9101/index.html'
    browser.assert_serving_this_tree(url)
    browser.PORT = 9371
    with tempfile.TemporaryDirectory(prefix='mokurai-no-wire-') as profile:
        proc, address = browser.launch(url, profile)
        try:
            async with websockets.connect(address, max_size=10_000_000) as ws:
                c = browser.CDP(ws)
                for _ in range(400):
                    if await c.js("return typeof SPRITES!=='undefined'&&NINJA_ROSTER.every(s=>SPRITES[s.name.toLowerCase()]?.ready)"):
                        break
                    await asyncio.sleep(.1)
                result = await c.js(r'''
                dismissTitle(); const failures=[],rows=[];
                const check=(ok,label)=>{if(!ok)failures.push(label);};
                const key=(code,on)=>window.dispatchEvent(new KeyboardEvent(on?'keydown':'keyup',{code,bubbles:true}));
                const reset=(id,cracked,face,air='ground')=>{
                    gameMode='2p';cpuMode=false;spectate=false;p1Pick=id;p2Pick=0;stagePick='bamboo';
                    startNewGame();paused=false;roundIntroTimer=0;cutscene=null;hitstopRemaining=0;releaseAllKeys();
                    const p=player1,d=player2;
                    Object.assign(p,{x:500,y:GROUND_Y-p.height-(air==='ground'?0:180),
                        isGrounded:air==='ground',vx:0,vy:air==='rise'?-300:air==='fall'?160:0,
                        facing:face,cracked,crackTimer:cracked?10:0,state:STATE.IDLE,stamina:100});
                    Object.assign(d,{x:500+face*240,y:GROUND_Y-d.height,isGrounded:true,vx:0,vy:0,facing:-face});
                    return p;
                };
                const command=(axis=0,up=false)=>({type:STATE.ATTACK_SPECIAL,
                    dir:up?'up':axis>0?'fwd':axis<0?'back':null,axis,up,down:false,ttl:ATTACK_BUFFER});
                const sample=(p,label)=>{
                    let boxes=0;const wires=new Set(),cells=new Set();
                    for(let f=0;f<100;f++){
                        p.projectiles.filter(x=>x.kind==='wire').forEach(x=>wires.add(x));
                        boxes+=p.hitboxes.length;
                        if(p.isAttackingState())cells.add(spriteFrameIndex(p,SPRITES[p.spec.name.toLowerCase()].frames));
                        updateGame(1/(60*COMBAT_TEMPO));
                    }
                    check(!wires.size,label+' launched wire');
                    check(boxes>0,label+' lost its hand attack');
                    rows.push({label,boxes,cells:[...cells],wireCount:wires.size});
                };
                const signature=p=>JSON.stringify({state:p.state,dir:p.attackDir,dur:p.attackAnim?.dur,
                    recovery:p.recoveryTimer,stamina:p.stamina,halo:p.hollowHaloAnim,
                    cell:spriteFrameIndex(p,SPRITES.mokurai.frames),
                    boxes:p.hitboxes.map(h=>[h.ox,h.oy,h.w,h.h,h.damage,h.delay,h.duration])});
                for(const cracked of [false,true])for(const face of [-1,1]){
                    let p=reset(6,cracked,face);p.executeAttack(STATE.ATTACK_SPECIAL,null,command());
                    const neutral=signature(p);
                    for(const air of ['ground','rise','fall'])for(const axis of [-1,0,1]){
                        p=reset(6,cracked,face,air);
                        p.executeAttack(STATE.ATTACK_SPECIAL,null,command(axis,true));
                        const label=`${cracked?'cracked':'base'} face${face} ${air} axis${axis}`;
                        if(air==='ground')check(signature(p)===neutral,label+' differs from neutral');
                        sample(p,label);
                    }
                    for(const delay of [0,1,8]){
                        p=reset(6,cracked,face);key('KeyW',true);
                        for(let f=0;f<delay;f++)updateGame(1/(60*COMBAT_TEMPO));
                        key('KeyH',true);key('KeyH',false);key('KeyW',false);
                        sample(p,`keyboard cracked${cracked} face${face} delay${delay}`);
                    }
                    p=reset(6,cracked,face);p.stunTimer=.05;p.state=STATE.STUNNED;
                    p.executeAttack(STATE.ATTACK_SPECIAL,null,command(1,true));
                    check(p.bufferedAttack?.up===false&&p.bufferedAttack?.dir===null,'buffer must store neutral');
                    sample(p,`buffer cracked${cracked} face${face}`);
                }
                for(const face of [-1,1])for(const kage of [false,true]){
                    const p=reset(2,false,face);p.kageNui=kage;
                    p.executeAttack(STATE.ATTACK_SPECIAL,null,command(kage?0:1));
                    let wire=false,latch=false;
                    for(let f=0;f<140;f++){
                        wire ||= p.projectiles.some(x=>x.kind==='wire');
                        updateGame(1/(60*COMBAT_TEMPO));
                        latch ||= !!p.tether;
                    }
                    check(wire,`Shin face${face} kage${kage} lost wire`);
                    check(player2.hp<150,`Shin face${face} kage${kage} wire failed to hit`);
                    if(kage)check(latch,`Shin face${face} lost Kage latch`);
                    rows.push({label:`Shin face${face} kage${kage}`,wire,opponentHP:player2.hp});
                }
                const random=Math.random;
                try{Math.random=()=>.01;
                    for(const cracked of [false,true])for(const face of [-1,1]){
                        const p=reset(6,cracked,face);p.stamina=60;cpuBrains[0].timer=0;
                        cpuThink(1/60,0);
                        check(!p.projectiles.some(x=>x.kind==='wire'),'CPU used retired opener');
                        rows.push({label:`CPU cracked${cracked} face${face}`,state:p.state,action:cpuBrains[0].action});
                    }
                }finally{Math.random=random;}
                paused=true;releaseAllKeys();return {failures,rows};
                ''')
                assert result and '__error' not in result, result
                out = Path('media/mokurai-wire-removal-20260908/check.json')
                out.parent.mkdir(parents=True, exist_ok=True)
                out.write_text(json.dumps(result, indent=2))
                assert not result['failures'], result['failures']
                print(f"PASS: {len(result['rows'])} Mokurai input/buffer and Shin wire cases")
        finally:
            proc.terminate()
            proc.wait(timeout=10)


if __name__ == '__main__':
    asyncio.run(main())
