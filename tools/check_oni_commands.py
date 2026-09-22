#!/usr/bin/env python3
"""Oni command regression through the actual keyboard funnel on :9101."""
import asyncio
import json
import os
import tempfile
from pathlib import Path

import websockets
import watch_game as browser


CHECK = r'''
dismissTitle();gameMode='2p';spectate=false;cpuMode=false;stagePick='bamboo';
p1Pick=8;p2Pick=0;startNewGame();roundIntroTimer=0;paused=true;cutscene=null;
const failures=[],cases=[];let checks=0;
const check=(ok,message)=>{checks++;if(!ok)failures.push(message);};
const setup=({air=false,facing=1,dir='neutral',stamina=100,smoke=0,winded=0,seat=1}={})=>{
    for(const k in keys)keys[k]=false;physKeys.clear();smokeFields.length=0;logs.length=0;
    animClock=10;hitstopRemaining=0;blackoutAmount=0;
    player1=new Player(1,500,GROUND_Y-48,NINJA_ROSTER[seat===1?8:0],true);
    player2=new Player(2,500+facing*60,GROUND_Y-48,NINJA_ROSTER[seat===2?8:0],false);
    const p=seat===1?player1:player2,foe=seat===1?player2:player1;
    p.opponent=foe;foe.opponent=p;
    Object.assign(p,{x:500,y:GROUND_Y-p.height-(air?180:0),facing,isGrounded:!air,
        state:air?STATE.JUMP:STATE.IDLE,vy:air?100:0,vx:0,stamina,smokeUsed:smoke,windedTimer:winded});
    Object.assign(foe,{x:500+facing*60,y:p.y,facing:-facing,isGrounded:!air,state:STATE.IDLE,
        vy:0,vx:0,hp:1000,invulnTimer:0});
    const key=dir==='fwd'?(facing===1?'right':'left'):dir==='back'?(facing===1?'left':'right'):dir;
    if(dir!=='neutral')keys['p'+seat+'_'+key]=true;
    return{p,foe,seat};
};
const press=(c,type='special')=>fireCombatKey(({1:{special:'KeyH',light:'KeyF',medium:'KeyJ',heavy:'KeyG'},
    2:{special:'KeyP',light:'KeyI',medium:'KeyU',heavy:'KeyO'}})[c.seat][type]);
for(const seat of [1,2])for(const facing of [-1,1])for(const air of [false,true])
for(const dir of ['neutral','fwd','back','up'])for(const stamina of [0,24,25]){
    const c=setup({seat,facing,air,dir,stamina});press(c);
    const label=`P${seat} ${facing} ${air?'air':'floor'} ${dir} chakra${stamina}`,p=c.p;
    if(stamina<25)check(!p.isAttackingState()&&p.hitboxes.length===0&&p.stamina===stamina,
        label+' cast an unaffordable Special');
    else check(p.state===STATE.ATTACK_SPECIAL&&p.stamina===0,label+' must spend exactly25');
    cases.push({label,state:p.state,stamina:p.stamina,boxes:p.hitboxes.length});
}
for(const air of [false,true])for(const dir of ['neutral','fwd','back','up']){
    const c=setup({air,dir,winded:1});press(c);
    check(!c.p.isAttackingState()&&c.p.stamina===100,`winded ${air} ${dir} cast`);
}
for(const air of [false,true])for(const smoke of [0,1,2])for(const stamina of [0,24,25]){
    const c=setup({air,dir:'down',smoke,stamina});press(c);
    if(smoke<2){
        check(c.p.smokeUsed===smoke+1&&smokeFields.length===1&&c.p.hitboxes.length===0
            &&c.p.stamina===stamina,`free smoke ${air}/${smoke}/${stamina} changed`);
    }else{
        check(smokeFields.length===0&&c.p.smokeUsed===2,'third smoke bypassed cap');
        if(stamina<25)check(!c.p.isAttackingState()&&c.p.stamina===stamina,'unaffordable smoke fallback cast');
        else{
            const actual=c.p.hitboxes.map(h=>[h.ox,h.oy,h.w,h.h,h.damage,h.delay,h.duration]);
            const neutral=setup({air,stamina});press(neutral);
            const expected=neutral.p.hitboxes.map(h=>[h.ox,h.oy,h.w,h.h,h.damage,h.delay,h.duration]);
            check(c.p.attackDir===null&&c.p.stamina===0&&JSON.stringify(actual)===JSON.stringify(expected),
                `third smoke ${air?'air':'floor'} did not execute neutral fallback`);
        }
    }
}
// The old dial must neither collect these presses nor replace the final Light.
{
    const c=setup();c.p.dial='HHHLHHL';c.p.dialAt=animClock;press(c,'light');
    check(c.p.state===STATE.ATTACK_LIGHT&&c.p.moveArt!=='handseal','retired handseal dial intercepted Light');
}
for(const facing of [-1,1])for(const distance of [60,220])
for(const [air,dir] of [[false,'neutral'],[false,'fwd'],[false,'back'],[true,'neutral']]){
    const c=setup({facing,dir,air,stamina:0}),{p,foe}=c;
    foe.x=p.x+facing*distance;
    p.wireBind=.5;p.wireBindFoe=foe;press(c);
    const box=p.hitboxes[0],x0=p.x,hp0=foe.hp;
    check(p.wireConv&&p.stamina===0&&box?.delay===.1&&box.duration===.1,'conversion must be free with .1s startup');
    for(let i=0;i<5;i++){
        animClock+=1/60;p.update(1/60,foe);processHitboxes(p,foe,1/60);
        check(foe.hp===hp0,'wire conversion hit before approach completed');
    }
    check((p.x-x0)*facing>0,'wire conversion did not approach opponent');
    for(let i=0;i<8&&foe.hp===hp0;i++){
        animClock+=1/60;p.update(1/60,foe);processHitboxes(p,foe,1/60);
    }
    check(foe.hp<hp0,'wire conversion missed after approach');
    cases.push({label:'wire '+facing+' '+dir+' '+(air?'air':'floor')+' '+distance,travel:p.x-x0,damage:hp0-foe.hp});
}

// The current neutral and forward air-Light share the same eight-cell drawing.
// A retired sixteen-cell row must not add a second duration multiplier.
{
    const read=dir=>{
        const c=setup({air:true,dir});press(c,'light');
        const dur=c.p.attackAnim.dur,frames=[];
        for(const t of [.02,.16,.30,.44,.58,.72,.86]){
            animClock=10+dur*t/1000;frames.push(spriteFrameIndex(c.p,SPRITES.oni.frames));
        }
        return{dur,frames};
    };
    const neutral=read('neutral'),forward=read('fwd');
    check(neutral.dur===forward.dur&&JSON.stringify(neutral.frames)===JSON.stringify(forward.frames),
        'neutral air-Light still uses obsolete timing for the same current row');
    cases.push({label:'air-Light neutral/forward timing',neutral,forward});
}
const tick=(c,contact=true)=>{
    animClock+=1/60;c.p.update(1/60,c.foe);
    if(contact)processHitboxes(c.p,c.foe,1/60);
};
const wire=opts=>{
    const c=setup(opts);c.foe.x=c.p.x+c.p.facing*220;
    c.p.wireBind=.5;c.p.wireBindFoe=c.foe;press(c);return c;
};
for(const facing of [-1,1])for(const air of [false,true]){
    // Small real movement remains catchable; a large escape is a fair whiff,
    // never an unbounded homing lunge past the destination booked on the press.
    for(const escape of [false,true]){
        const c=wire({facing,air}),{p,foe}=c,hp=foe.hp,to=p.attackAnim.wireApproach.x;
        for(let i=0;i<14;i++){
            if(escape&&i===2)foe.x+=facing*300;
            if(!escape)foe.x+=facing*100/60;
            tick(c);
        }
        check(escape?foe.hp===hp:foe.hp<hp,'moving target wire contact/escape mismatch');
        check((p.x-to)*facing<=.01&&!p.attackAnim?.wireApproach,'wire approach chased/overshot moving target');
    }
    // Death, vanish and grab invalidate only the committed approach. Getting
    // hit uses the real interruption path and must keep the knockback it earns.
    for(const reason of ['dead','vanished','grabbed','hit','moveExit']){
        const c=wire({facing,air}),{p,foe}=c;tick(c,false);const x=p.x;
        if(reason==='dead')foe.hp=0;
        if(reason==='vanished')foe.vanishTimer=.3;
        if(reason==='grabbed')foe.grabbedBy=p;
        if(reason==='hit')p.takeDamage(5,foe,{pushback:80,tier:STATE.ATTACK_LIGHT});
        if(reason==='moveExit')p.state=STATE.IDLE;
        tick(c,false);
        check(!p.attackAnim?.wireApproach&&p.wireBindFoe===null,'wire approach survived '+reason);
        if(reason==='hit')check(p.stunTimer>0&&(p.x-x)*facing<0,'wire cancellation swallowed hit knockback');
        else if(reason!=='moveExit')check(p.x===x&&p.vx===0,'wire cancellation drifted after '+reason);
    }
    // Public art/reset cleanup must remove conversion flags, leaving no target
    // for a later move to inherit (trainingReset calls this shared clear).
    {
        const c=wire({facing,air});c.p.clearMoveArt();
        check(c.p.attackAnim===null&&c.p.wireBindFoe===null&&c.p.wireConv===null,'wire data survived clearMoveArt');
    }
    // Arena edge: the approach lands on the near side of the bound opponent.
    {
        const c=setup({facing,air}),{p,foe}=c;
        foe.x=facing>0?canvas.width-10-foe.width:10;p.x=foe.x-facing*220;
        p.wireBind=.5;p.wireBindFoe=foe;press(c);const hp=foe.hp;
        for(let i=0;i<14;i++)tick(c);
        check(foe.hp<hp&&p.x>=10&&p.x+p.width<=canvas.width-10,'near-wall conversion missed or crossed bounds');
    }
    // An actual solid interior wall still stops the approach before contact.
    {
        const c=wire({facing,air}),{p,foe}=c,walls=currentStage.walls;
        const wx=facing>0?p.x+p.width+60:p.x-80;
        currentStage.walls=[{x:wx,w:20,y0:0,y1:GROUND_Y+100}];
        for(let i=0;i<14;i++)tick(c,false);
        check(facing>0?p.x+p.width<=wx+.01:p.x>=wx+20-.01,'wire approach crossed interior wall');
        check(!p.attackAnim?.wireApproach,'wall collision retained wire approach');
        currentStage.walls=walls;
    }
}

// Whole paid starter -> confirmed bind -> free directional finisher, with both
// bodies taking their normal physics and hitstun ticks (no seeded bind here).
for(const facing of [-1,1])for(const dir of ['neutral','fwd','back']){
    const c=setup({facing,stamina:25}),{p,foe}=c;
    foe.x=p.x+facing*220;press(c);
    for(let i=0;i<30&&p.wireBind<=0;i++){
        animClock+=1/60;p.update(1/60,foe);foe.update(1/60,p);processHitboxes(p,foe,1/60);
    }
    check(p.wireBind>0,'paid starter did not open real bind');
    if(dir!=='neutral')keys['p1_'+(dir==='fwd'?(facing>0?'right':'left'):(facing>0?'left':'right'))]=true;
    const remaining=p.stamina,hp=foe.hp;press(c);
    check(p.wireConv==={neutral:'slice',fwd:'katana',back:'claw'}[dir]&&p.stamina===remaining,
        'real bind finisher changed direction or charged twice');
    for(let i=0;i<15&&foe.hp===hp;i++){
        animClock+=1/60;p.update(1/60,foe);foe.update(1/60,p);processHitboxes(p,foe,1/60);
    }
    check(foe.hp<hp,'real bound target escaped ordinary finisher approach');
    cases.push({label:'paid starter to '+dir+' '+facing,stamina:remaining,damage:hp-foe.hp});
}

// The help recommends Special for conversions. A late Back+Light can still be
// the command heel kick, while Medium has no directional normal variants.
{
    const c=setup({dir:'back'});c.p.wireBind=.5;c.p.wireBindFoe=c.foe;press(c,'light');
    check(c.p.kickKind==='heel'&&!c.p.wireConv,'late Back+Light help exception changed');
    const normals=[];
    for(const dir of ['neutral','fwd','back','up','down']){
        const c=setup({dir});press(c,'medium');
        normals.push(JSON.stringify(c.p.hitboxes.map(h=>[h.ox,h.oy,h.w,h.h,h.damage,h.delay,h.duration])));
    }
    check(normals.every(n=>n===normals[0]),'Medium directional hitbox behavior changed');
}
// Training R in the middle of actual travel must cancel the approach and box.
{
    const c=wire({air:true}),{p,foe}=c;tick(c,false);
    gameMode='training';paused=false;roundIntroTimer=0;hitstopRemaining=0;
    window.dispatchEvent(new KeyboardEvent('keydown',{code:'KeyR',bubbles:true}));
    window.dispatchEvent(new KeyboardEvent('keyup',{code:'KeyR',bubbles:true}));
    paused=true;
    const x=p.x,hp=foe.hp;
    for(let i=0;i<14;i++)tick(c);
    check(!p.attackAnim?.wireApproach&&p.wireBindFoe===null&&!p.wireConv&&p.hitboxes.length===0
        &&p.x===x&&foe.hp===hp,'training R left a deferred wire arrival/hit');
}
return{sheetVersion:SHEET_V,checks,failures,cases};
'''


async def main():
    browser.PORT = int(os.environ.get('SHADOWCLASH_DEBUG_PORT', '9349'))
    url = os.environ.get('SHADOWCLASH_URL', 'http://localhost:9101/index.html')
    browser.assert_serving_this_tree(url)
    with tempfile.TemporaryDirectory(prefix='oni-commands-') as profile:
        proc, addr = browser.launch(url, profile)
        try:
            async with websockets.connect(addr, max_size=8*1024*1024) as ws:
                c = browser.CDP(ws)
                for _ in range(500):
                    if await c.js("return typeof SPRITES!=='undefined'&&SPRITES.oni?.ready"): break
                    await asyncio.sleep(.1)
                else: raise AssertionError('Oni did not load')
                result = await c.js(CHECK)
                assert result and '__error' not in result, result
        finally:
            proc.terminate()
            proc.wait(timeout=10)
    out = Path(os.environ.get('OUT', 'media/functionality-scan-20260907/oni-commands.json'))
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(result, indent=2)+'\n')
    print(json.dumps({'checks':result['checks'], 'failures':result['failures']}))
    assert not result['failures'], str(out)


if __name__ == '__main__':
    asyncio.run(main())
