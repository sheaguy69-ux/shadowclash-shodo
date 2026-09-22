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
                check(speed[7]>speed[8]&&speed[8]>speed[2]&&speed[2]>Math.max(...speed.filter((_,i)=>![7,8,2].includes(i))),'strict top-three speed order');
                check(speed[0]===Math.min(...speed),'Executioner slowest');
                check(power[8]>Math.max(...power.slice(0,8))&&power[0]>Math.max(...power.slice(1,6)),'power order');
                for(let id=0;id<9;id++){
                    let [a,d]=reset(5,id);const factor=id===7?1.25:1+(6-d.spec.stats.defense)*.03;
                    for(const branch of ['normal','armor','throw','guard']){
                        [a,d]=reset(5,id);if(branch==='armor')d.armorTimer=1;
                        if(branch==='throw'){d.grabbedBy=a;a.throwReleased=false;a.releaseThrow(d);}
                        else {if(branch==='guard')d.state=STATE.BLOCKING;d.takeDamage(20,a,{tier:STATE.ATTACK_HEAVY,pushback:100});}
                        near(150-d.hp,(branch==='throw'?12:20)*.7*factor*(branch==='guard'?.15:1),id+' '+branch);
                        if(branch==='armor')near(d.stunTimer,0,'armor retains stagger immunity');
                        if(branch==='guard'){near(d.stamina,95,'guard costs stamina');near(d.stunTimer,9/60,'heavy blockstun');}
                        rows.push({id,branch,loss:150-d.hp});
                    }
                    [a,d]=reset(5,id);d.state=STATE.BLOCKING;d.stamina=0;d.takeDamage(20,a,{tier:STATE.ATTACK_LIGHT,pushback:100});
                    near(150-d.hp,14*factor,'empty guard cannot absorb '+id);
                    [a,d]=reset(5,id);d.invulnTimer=1;d.takeDamage(20,a);near(d.hp,150,'invulnerability '+id);
                    [a,d]=reset(5,id);d.stunTimer=1;d.comboHits=3;d.takeDamage(20,a);near(150-d.hp,14*factor*SCALE_PER_HIT,'combo scaling '+id);
                }
                for(const [id,flag,value,factor] of [[2,'kageNui',true,1.06*.75],[6,'cracked',true,.94*1.2],[7,'frenzyTimer',5,1.09],[5,'muki',5,1.5]]){
                    for(const armor of [false,true]){const [a,d]=reset(5,id);d[flag]=value;d.armorTimer=armor?1:0;d.takeDamage(20,a,{tier:STATE.ATTACK_HEAVY});near(150-d.hp,14*factor,flag+' armor='+armor);}
                }
                for(const side of [-1,1])for(let target=0;target<9;target++)for(const gap of [20,70,140]){
                    const [a,d]=reset(2,target,side,gap);a.executeAttack(STATE.ATTACK_SPECIAL,null,{type:STATE.ATTACK_SPECIAL,dir:null,axis:0,up:false,down:false,ttl:ATTACK_BUFFER});
                    for(let t=0;t<90;t++){updateGame(1/(60*COMBAT_TEMPO));hitstopRemaining=0;}
                    check(d.hp<150,'Shin kick target='+target+' side='+side+' gap='+gap);
                }
                const timing=[];
                for(const id of [7,8,2]){const [a,d]=reset(id);d.x=10000;a.executeAttack(STATE.ATTACK_MEDIUM);timing.push(a.recoveryTimer);}
                check(timing[0]<timing[1]&&timing[1]<timing[2],'medium speed order');
                let [a,d]=reset(8);a.executeAttack(STATE.ATTACK_HEAVY);check(a.recoveryTimer<.4,'Oni heavy no old slowdown');
                const raw=[];for(const id of [0,8]){[a,d]=reset(id);a.executeAttack(STATE.ATTACK_HEAVY);raw.push(a.hitboxes[0].damage);}check(raw[1]>raw[0],'Oni actual heavy stronger than Executioner');
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
