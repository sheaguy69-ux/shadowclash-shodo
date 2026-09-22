#!/usr/bin/env python3
"""Mokurai's real counter inputs, contact art and stored-force damage paths."""
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
    with tempfile.TemporaryDirectory(prefix='mokurai-counter-') as profile:
        proc, address = browser.launch(url, profile)
        try:
            async with websockets.connect(address, max_size=20_000_000) as ws:
                c = browser.CDP(ws)
                for _ in range(400):
                    if await c.js("return typeof SPRITES!=='undefined'&&NINJA_ROSTER.every(s=>SPRITES[s.name.toLowerCase()]?.ready)"):
                        break
                    await asyncio.sleep(.1)
                result = await c.js(r'''
                dismissTitle();const failures=[],rows=[];
                const check=(ok,msg)=>{if(!ok)failures.push(msg);};
                const near=(a,b,msg)=>check(Math.abs(a-b)<.001,`${msg}: ${a} != ${b}`);
                const tick=()=>{updateGame(1/(60*COMBAT_TEMPO));hitstopRemaining=0;};
                const key=(code,on)=>window.dispatchEvent(new KeyboardEvent(on?'keydown':'keyup',{code,bubbles:true}));
                const reset=(cracked=false,side=1,gap=0)=>{
                    gameMode='2p';cpuMode=false;spectate=false;p1Pick=6;p2Pick=4;stagePick='bamboo';
                    startNewGame();paused=false;roundIntroTimer=0;cutscene=null;hitstopRemaining=0;releaseAllKeys();
                    const p=player1,d=player2;
                    Object.assign(p,{x:500,y:GROUND_Y-p.height,isGrounded:true,state:STATE.IDLE,vx:0,vy:0,
                        facing:side,cracked,crackTimer:cracked?10:0,karma:0,stamina:100});
                    Object.assign(d,{x:side>0?500+p.width+gap:500-d.width-gap,y:GROUND_Y-d.height,
                        isGrounded:true,state:STATE.IDLE,vx:0,vy:0,facing:-side,stamina:100});
                    return [p,d];
                };
                const special=(p,axis=0,down=false)=>p.executeAttack(STATE.ATTACK_SPECIAL,null,
                    {type:STATE.ATTACK_SPECIAL,dir:down?'down':axis>0?'fwd':axis<0?'back':null,
                     axis,up:false,down,ttl:ATTACK_BUFFER});
                for(const cracked of [false,true]){
                    for(const path of ['normal','projectile','guard','armor','throw','slam','reflect','invulnerable','vanish','enlightened','grabbed','roll']){
                        const [p,d]=reset(cracked);let expected=10;
                        if(path==='guard')p.state=STATE.BLOCKING;
                        if(path==='armor')p.armorTimer=1;
                        if(path==='invulnerable'){p.invulnTimer=1;expected=0;}
                        if(path==='vanish'){p.vanishTimer=1;expected=0;}
                        if(path==='enlightened'){p.enlightenTimer=1;expected=0;}
                        if(path==='grabbed'){p.grabbedBy=d;expected=0;}
                        if(path==='roll'){p.rollIFrames=()=>true;expected=0;}
                        if(path==='throw'){p.grabbedBy=d;d.throwReleased=false;d.releaseThrow(p);expected=THROW_DMG*KARMA_GAIN;}
                        else if(path==='slam'){
                            Object.assign(p,{skySlam:true,isGrounded:false,y:GROUND_Y-p.height-1,vy:500,stunTimer:.2});
                            p.applyPhysics(1/60);expected=8*KARMA_GAIN;
                        }else{
                            if(path==='reflect'){special(p,-1);expected=6;}
                            p.takeDamage(20,d,['projectile','reflect'].includes(path)?null:{tier:STATE.ATTACK_HEAVY,pushback:100});
                        }
                        near(p.karma,expected,`cracked${cracked} ${path}`);
                        rows.push({cracked,path,karma:p.karma,hp:p.hp});
                    }
                    let [p,d]=reset(cracked);p.karma=14;p.takeDamage(20,d,{});near(p.karma,15,'charge capped');
                    for(const kind of ['star','kunai','needle','palm','wave','wire','kagenui']){
                        [p,d]=reset(cracked,1,300);special(p,-1);
                        d.projectiles.push({kind:kind==='kagenui'?'wire':kind,kagenui:kind==='kagenui',
                            x:p.x+p.width/2,y:p.y+p.height/2,vx:0,vy:0});
                        d.update(1/60,p);
                        near(p.hp,150,kind+' counter protects');near(p.karma,6,kind+' counter charges');
                        near(d.stunTimer,0,kind+' cannot stun distant thrower');
                        check(p.projectiles.length===1,kind+' reflection exists');
                        check(!d.tether,kind+' counter must prevent tether');
                        rows.push({cracked,path:'reflect '+kind,karma:p.karma});
                    }
                    for(const type of [STATE.ATTACK_LIGHT,STATE.ATTACK_HEAVY]){
                        [p,d]=reset(cracked);p.karma=15;p.executeAttack(type);near(p.karma,15,'ordinary attack preserves charge');
                    }
                    for(const axis of [0,1])for(const down of [false,true]){
                        [p,d]=reset(cracked);special(p,axis,down);const raw=p.hitboxes.map(h=>h.damage);
                        [p,d]=reset(cracked);p.karma=15;special(p,axis,down);
                        near(p.karma,0,'offensive special consumes charge');
                        near(p.hitboxes.reduce((n,h,i)=>n+h.damage-raw[i],0),15,'special spends bonus exactly once');
                    }
                    [p,d]=reset(cracked);p.karma=15;p.state=STATE.ATTACK_SPECIAL;
                    p.spawnHitbox(30,30,5,.1,50,{echo:true});near(p.karma,15,'old echo cannot spend charge');
                    for(const side of [-1,1])for(const charge of [0,15]){
                        [p,d]=reset(cracked,side);p.karma=charge;
                        const back=side>0?'KeyA':'KeyD';key(back,true);key('KeyH',true);key('KeyH',false);key(back,false);
                        check(p.state===STATE.PARRY_STANCE,'Back+Special enters counter');
                        check(spriteFrameIndex(p,SPRITES.mokurai.frames)===SPRITES.mokurai.frames.mblock1,'counter guard art');
                        near(p.karma,charge,'whiff stance preserves charge');
                        key('KeyI',true);key('KeyI',false);
                        const cells=new Set();let caught=false,registered=false,launched=false,counterDamage=null;
                        for(let f=0;f<90;f++){
                            tick();
                            if(p.state===STATE.ATTACK_SPECIAL){
                                caught=true;
                                for(const h of p.hitboxes){
                                    registered ||= !!h.poseWindow;counterDamage??=h.damage;
                                }
                                if(p.attackAnim?.strikeWindows?.some(w=>w.lastActiveAt===animClock))
                                    cells.add(spriteFrameIndex(p,SPRITES.mokurai.frames));
                            }
                            launched ||= d.vy<0&&!d.isGrounded;
                        }
                        const label=`counter cracked${cracked} face${side} charge${charge}`;
                        check(caught&&registered,label+' must enter registered palm answer');
                        near(p.hp,150,label+' must catch incoming strike');
                        check(d.hp<150&&launched,label+' must hit and launch');
                        check(cells.size>0&&[...cells].every(c=>[391,392,393].includes(c)),label+' contact must use palm cells');
                        near(counterDamage,20+charge,label+' counter power');near(p.karma,6,label+' new counter charge');
                        rows.push({label,caught,registered,cells:[...cells],hp:p.hp,opponentHP:d.hp,counterDamage});
                    }
                    [p,d]=reset(cracked);special(p,-1);for(let f=0;f<45;f++)tick();
                    check(!p.isAttackingState()&&p.state!==STATE.PARRY_STANCE,'missed counter recovers');
                    [p,d]=reset(cracked);special(p,-1);for(let f=0;f<15;f++)tick();
                    check(p.recoveryTimer>0&&p.parryFlashTimer<=0,'counter leaves a punish window');
                    p.takeDamage(20,d,{});check(p.hp<150,'late hit must punish missed counter');
                }
                const [p,d]=reset();d.gainKarma(15);near(d.karma,0,'other fighters cannot gain Karma');
                paused=true;releaseAllKeys();return {failures,rows};
                ''')
                assert result and '__error' not in result, result
                out = Path('media/mokurai-counter-karma-20260908/check.json')
                out.parent.mkdir(parents=True, exist_ok=True)
                out.write_text(json.dumps(result, indent=2))
                assert not result['failures'], result['failures']
                print('PASS: both-form Karma gain/cap/spend and real-input counter art/contact/launch/whiff')
        finally:
            proc.terminate()
            proc.wait(timeout=10)


if __name__ == '__main__':
    asyncio.run(main())
