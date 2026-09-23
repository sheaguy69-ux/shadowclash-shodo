#!/usr/bin/env python3
"""Owner's Sep 7 roster hierarchy and shared damage/guard regression checks."""
import asyncio, json, tempfile
from pathlib import Path
import websockets
import watch_game as browser

async def main():
    browser.PORT = 9358
    url = 'http://localhost:9101/index.html'
    browser.assert_serving_this_tree(url)
    with tempfile.TemporaryDirectory(prefix='roster-balance-') as profile:
        proc, addr = browser.launch(url, profile)
        try:
            async with websockets.connect(addr, max_size=10_000_000) as ws:
                c = browser.CDP(ws)
                for _ in range(200):
                    if await c.js("return typeof SPRITES!=='undefined'&&NINJA_ROSTER.every(s=>SPRITES[s.name.toLowerCase()]?.ready)"): break
                    await asyncio.sleep(.1)
                result = await c.js(r'''
                dismissTitle();paused=true;
                const failures=[], rows=[];
                const check=(ok,label)=>{if(!ok)failures.push(label);};
                const near=(a,b,label)=>check(Math.abs(a-b)<.001,label+': '+a+' != '+b);
                const reset=(a=5,b=5,side=1,gap=20)=>{
                    gameMode='2p';cpuMode=false;spectate=false;p1Pick=a;p2Pick=b;stagePick='bamboo';
                    startNewGame();roundIntroTimer=0;cutscene=null;hitstopRemaining=0;
                    for(const k in keys)keys[k]=false;physKeys.clear();
                    for(const p of [player1,player2])Object.assign(p,{y:GROUND_Y-p.height,isGrounded:true,state:STATE.IDLE,vx:0,vy:0,stamina:100,invulnTimer:0,armorTimer:0,stunTimer:0,comboHits:0});
                    player1.x=500;player2.x=side>0?500+player1.width+gap:500-player2.width-gap;
                    player1.facing=side;player2.facing=-side;return [player1,player2];
                };
                const speed=NINJA_ROSTER.map(s=>s.stats.speed),power=NINJA_ROSTER.map(s=>s.stats.power);
                // ⛔ INDEX 8 IS ONI AND HE IS RETIRED. Every assertion below that names him
                // is PARKED, not deleted: the claims are his, and repointing them at whoever
                // now sits in his slot would invent balance the owner never ruled. They wake
                // up on their own the day he is back on the roster. The live half of each
                // mixed claim is split out and still runs.
                // ⛔ d.maxHp, NEVER A LITERAL 150. Max HP is 180 now and this file hardcoded
                // 150 in six places, so every damage assertion came out exactly 30 low — the
                // Executioner "lost -16.84 HP". A health-bar change must not be able to make
                // a balance gate lie about damage.
                const ONI=NINJA_ROSTER.findIndex(s=>s.name==='Oni');
                if(ONI>=0){
                  check(speed[7]>speed[ONI]&&speed[ONI]>speed[2]&&speed[2]>Math.max(...speed.filter((_,i)=>![7,ONI,2].includes(i))),'strict top-three speed order');
                  check(power[ONI]>Math.max(...power.filter((_,i)=>i!==ONI)),'power order: Oni on top');
                }
                // ⛔ "EXECUTIONER SLOWEST" IS OVERRULED BY THE ROSTER ITSELF. His own entry
                // reads "TANK AT MID SPEED (owner, Aug 2 2026)", and Mokurai has sat at
                // speed 5 against his 6 since the Sep 10 2026 pass that moved Mokurai's
                // POWER and deliberately left his speed alone ("if he still reads weak the
                // lever is RECOVERY"). So this asserted the opposite of two dated rulings,
                // and it was the ONLY thing still red here once the gate could run at all.
                // Pin the ruling that exists: mid means neither end of the roster.
                check(speed[0]!==Math.min(...speed)&&speed[0]!==Math.max(...speed),
                      'Executioner is a TANK AT MID SPEED, not an extreme');
                check(power[0]>Math.max(...power.slice(1,6)),'power order: Executioner over the middle');
                for(let id=0;id<NINJA_ROSTER.length;id++){
                    let [a,d]=reset(5,id);const factor=id===7?1.25:1+(6-d.spec.stats.defense)*.03;
                    for(const branch of ['normal','armor','throw','guard']){
                        [a,d]=reset(5,id);if(branch==='armor')d.armorTimer=1;
                        if(branch==='throw'){d.grabbedBy=a;a.throwReleased=false;a.releaseThrow(d);}
                        else {if(branch==='guard')d.state=STATE.BLOCKING;d.takeDamage(20,a,{tier:STATE.ATTACK_HEAVY,pushback:100});}
                        near(d.maxHp-d.hp,(branch==='throw'?12:20)*.7*factor*(branch==='guard'?.15:1),id+' '+branch);
                        if(branch==='armor')near(d.stunTimer,0,'armor retains stagger immunity');
                        if(branch==='guard'){near(d.stamina,95,'guard costs stamina');near(d.stunTimer,9/60,'heavy blockstun');}
                        rows.push({id,branch,loss:d.maxHp-d.hp});
                    }
                    [a,d]=reset(5,id);d.state=STATE.BLOCKING;d.stamina=0;d.takeDamage(20,a,{tier:STATE.ATTACK_LIGHT,pushback:100});
                    near(d.maxHp-d.hp,14*factor,'empty guard cannot absorb '+id);
                    [a,d]=reset(5,id);d.invulnTimer=1;d.takeDamage(20,a);near(d.hp,d.maxHp,'invulnerability '+id);
                    [a,d]=reset(5,id);d.stunTimer=1;d.comboHits=3;d.takeDamage(20,a);near(d.maxHp-d.hp,14*factor*SCALE_PER_HIT,'combo scaling '+id);
                }
                for(const [id,flag,value,factor] of [[2,'kageNui',true,1.06*.75],[6,'cracked',true,.94*1.2],[7,'frenzyTimer',5,1.09],[5,'muki',5,1.5]]){
                    for(const armor of [false,true]){const [a,d]=reset(5,id);d[flag]=value;d.armorTimer=armor?1:0;d.takeDamage(20,a,{tier:STATE.ATTACK_HEAVY});near(d.maxHp-d.hp,14*factor,flag+' armor='+armor);}
                }
                for(const side of [-1,1])for(let target=0;target<NINJA_ROSTER.length;target++)for(const gap of [20,70,140]){
                    const [a,d]=reset(2,target,side,gap);a.executeAttack(STATE.ATTACK_SPECIAL,null,{type:STATE.ATTACK_SPECIAL,dir:null,axis:0,up:false,down:false,ttl:ATTACK_BUFFER});
                    for(let t=0;t<90;t++){updateGame(1/(60*COMBAT_TEMPO));hitstopRemaining=0;}
                    check(d.hp<d.maxHp,'Shin kick target='+target+' side='+side+' gap='+gap);
                }
                const timing=[];
                // The medium-speed ORDER is a three-way claim with Oni in the middle, so it
                // parks whole — two thirds of an ordering proves nothing.
                if(ONI>=0){
                  for(const id of [7,ONI,2]){const [a,d]=reset(id);d.x=10000;a.executeAttack(STATE.ATTACK_MEDIUM);timing.push(a.recoveryTimer);}
                  check(timing[0]<timing[1]&&timing[1]<timing[2],'medium speed order');
                  let [a,d]=reset(ONI);a.executeAttack(STATE.ATTACK_HEAVY);check(a.recoveryTimer<.4,'Oni heavy no old slowdown');
                  const raw=[];for(const id of [0,ONI]){[a,d]=reset(id);a.executeAttack(STATE.ATTACK_HEAVY);raw.push(a.hitboxes[0].damage);}check(raw[1]>raw[0],'Oni actual heavy stronger than Executioner');
                }
                return {failures,rows,timing};
                ''')
                assert isinstance(result,dict) and '__error' not in result, result
                out=Path(__file__).resolve().parents[1]/'media/combat-balance-fix-20260907'
                out.mkdir(exist_ok=True);(out/'regression.json').write_text(json.dumps(result,indent=2))
                assert not result['failures'], result['failures']
                print('PASS: roster hierarchy, damage branches, guard, combo scaling, and 54 Shin kick matchups')
        finally:
            proc.terminate();proc.wait(timeout=10)

if __name__=='__main__':asyncio.run(main())
