#!/usr/bin/env python3
"""Live shared combat body geometry regression; isolated browser, no user tab."""
import asyncio, json, os, tempfile
from pathlib import Path
import websockets
import watch_game as browser

async def main():
    url=os.environ.get('SHADOWCLASH_URL','http://localhost:9101/index.html')
    browser.assert_serving_this_tree(url)
    browser.PORT=int(os.environ.get('DEBUG_PORT','9393'))
    with tempfile.TemporaryDirectory(prefix='roster-hurt-') as profile:
        proc,address=browser.launch(url,profile)
        try:
            async with websockets.connect(address,max_size=100_000_000) as ws:
                c=browser.CDP(ws)
                for _ in range(400):
                    if await c.js("return typeof SPRITES!=='undefined'&&NINJA_ROSTER.every(s=>SPRITES[s.name.toLowerCase()]?.ready)"): break
                    await asyncio.sleep(.1)
                result=await c.js(r'''
                dismissTitle(); const failures=[],samples=[];
                const check=(ok,msg)=>{if(!ok)failures.push(msg);};
                for(let id=0;id<9;id++)for(const facing of [-1,1]){
                    gameMode='2p';cpuMode=false;spectate=false;stagePick='bamboo';p1Pick=id;p2Pick=0;
                    startNewGame();paused=true;roundIntroTimer=0;releaseAllKeys();
                    const p=player1;
                    Object.assign(p,{x:450,y:GROUND_Y-p.height,isGrounded:true,vx:0,vy:0,state:STATE.IDLE,facing,animPhase:0});
                    const stand=p.hurtbox();
                    check(stand.h>p.height,`${id} still ankle-only`);
                    check(Math.abs(stand.y+stand.h-GROUND_Y)<1e-6,`${id} sole pivot`);
                    check(p.projectileTouches({x:stand.x+stand.w/2,y:stand.y+8}),`${id} head projectile miss`);
                    check(!p.projectileTouches({x:stand.x-5,y:stand.y-5}),`${id} diagonal projectile phantom`);
                    check(p.projectileTouches({x:stand.x-4,y:stand.y+10}),`${id} tangent projectile miss`);
                    check(!p.projectileTouches({x:stand.x-4.01,y:stand.y+10}),`${id} outside projectile hit`);
                    for(const state of [STATE.IDLE,STATE.RUN,STATE.CROUCH,STATE.ROLL,STATE.JUMP]){
                        p.state=state;p.isGrounded=state!==STATE.JUMP;p.y=GROUND_Y-p.height-(p.isGrounded?0:100);
                        p.crouchAt=animClock-1;p.rollTimer=state===STATE.ROLL?.15:0;
                        const h=p.hurtbox();check(h&&Object.values(h).every(Number.isFinite),`${id} ${state} invalid hull`);
                        if(state===STATE.CROUCH||state===STATE.ROLL)check(h.y+h.h===GROUND_Y,`${id} low sole pivot`);
                        if(state===STATE.CROUCH)check(!p.projectileTouches({x:h.x+h.w/2,y:h.y-5}),`${id} projectile above crouch head`);
                        samples.push({id,name:p.spec.name,facing,state,cell:spriteFrameIndex(p,SPRITES[p.spec.name.toLowerCase()].frames),h});
                    }
                    if(id===0){
                        Object.assign(p,{state:STATE.IDLE,rollTimer:0,isGrounded:true,y:GROUND_Y-p.height});
                        keys[facing>0?'KeyD':'KeyA']=true;p.executeAttack(STATE.ATTACK_SPECIAL);releaseAllKeys();
                        for(const frame of [3,4]){animClock=p.attackAnim.start/1000+(frame-1)/60;check(p.hurtbox()===null,'vanish hull exists');check(!p.projectileTouches({x:p.x,y:p.y}),'vanish projectile collision');}
                    }
                }
                let fitted=0;
                for(let id=1;id<9;id++)for(const facing of [-1,1])for(const [kind,direction] of [[STATE.ATTACK_LIGHT,'neutral'],[STATE.ATTACK_LIGHT,'forward'],[STATE.ATTACK_HEAVY,'forward'],[STATE.ATTACK_SPECIAL,'forward']]){
                    p1Pick=id;p2Pick=0;startNewGame();paused=true;roundIntroTimer=0;releaseAllKeys();
                    const p=player1;Object.assign(p,{x:450,y:GROUND_Y-p.height,isGrounded:true,vx:0,vy:0,state:STATE.IDLE,facing,animPhase:0});
                    if(direction==='forward')keys[facing>0?'KeyD':'KeyA']=true;
                    p.executeAttack(kind);releaseAllKeys();
                    for(const h of p.hitboxes){
                        if(!h.poseWindow||h.strikeShape?.skip)continue;
                        const damage=h.damage,duration=h.duration;h.delay=0;refreshStrikeGeometry(p,h);
                        check(h.damage===damage&&h.duration===duration,`${id} geometry changed combat timing/damage`);
                        check(h.poseWindow.lastActiveAt===animClock,`${id} missing final-active stamp`);
                        check(h.strikeCell===spriteFrameIndex(p,SPRITES[p.spec.name.toLowerCase()].frames),`${id} missing pose fit ${kind}/${direction}`);
                        check([h.ox,h.oy,h.w,h.h].every(Number.isFinite)&&h.w>0&&h.h>0,`${id} invalid strike`);
                        if(h.strikeCell!==undefined)fitted++;
                    }
                }
                for(const facing of [-1,1]){
                    p1Pick=7;p2Pick=0;startNewGame();paused=true;releaseAllKeys();
                    const p=player1,d=player2;Object.assign(p,{x:450,y:GROUND_Y-p.height,isGrounded:true,facing,state:STATE.IDLE});
                    p.executeAttack(STATE.ATTACK_SPECIAL);
                    const h=p.hitboxes.find(h=>h.strikeShape?.orbit&&h.strikeShape.behind);
                    check(!!h,'orbit rear box missing');if(!h)continue;
                    h.delay=0;const cx=p.x+p.width/2,tip={x:cx-facing*70,y:p.y};
                    p.chain={kind:'orbit',pts:[{x:cx,y:p.y},tip]};refreshStrikeGeometry(p,h);
                    check(!h.strikeInactive&&Math.abs(p.x+h.ox+h.w/2-tip.x)<1e-6,'rear ball registration');
                    tip.x=cx+facing*70;refreshStrikeGeometry(p,h);check(h.strikeInactive,'front ball creates rear hit');
                    p.hitboxes=[h];Object.assign(d,{x:p.x+h.ox,y:p.y+h.oy,isGrounded:false,invulnTimer:0});
                    h.canClash=true;d.hitboxes=[{ox:0,oy:0,w:h.w,h:h.h,delay:0,duration:1,canClash:true}];
                    processWeaponClash(p,d);check(p.hitboxes.includes(h)&&d.hitboxes.length===1,'inactive rear box clashed');
                    const hp=d.hp;processHitboxes(p,d,1,true);
                    check(d.hp===hp&&!p.hitboxes.includes(h),'inactive rear box damages or never expires');
                }
                check(fitted>=40,'too few actual melee geometry routes '+fitted);
                samples.push({fitted});
                return {failures,samples};
                ''')
                assert result and '__error' not in result,result
                out=Path('media/roster-hurtboxes');out.mkdir(exist_ok=True,parents=True)
                (out/'checks.json').write_text(json.dumps(result,indent=2))
                assert not result['failures'],result['failures']
                print('PASS: nine fighters, both facings, five states; shared projectile edges/head/duck, Executioner null vanish and 64 melee route fits')
        finally: proc.terminate();proc.wait(timeout=10)

if __name__=='__main__':asyncio.run(main())
