#!/usr/bin/env python3
"""Exercise corner defense through actual combat, input, and physics in Chrome.

This owns only debug port 9395. The optional original HTML is intercepted without
changing the server, so the before/after replay uses the same verified assets.
Contact fixtures isolate the threshold/edge cases; the replay uses real key
events, gameLoop, and the actual fighter attacks rather than scripted damage.
"""
import argparse
import asyncio
import base64
import hashlib
import io
import json
import socket
import tempfile
from pathlib import Path

from PIL import Image, ImageDraw
import websockets
import watch_game as browser
from check_runtime_sprites import Probe

ROOT = Path(__file__).resolve().parent.parent
URL = 'http://127.0.0.1:9101/index.html'

SETUP = r'''
dismissTitle(); window.requestAnimationFrame=()=>0;
window.cornerChecks=[];
window.check=(name,ok,detail=null)=>cornerChecks.push({name,ok:!!ok,detail});
window.key=(code,down)=>window.dispatchEvent(new KeyboardEvent(down?'keydown':'keyup',{code,bubbles:true}));
window.fixture=(id=5,side=1,seat=1)=>{
    releaseAllKeys(); gameMode='2p';cpuMode=false;spectate=false;drillIdx=0;
    p1Pick=seat===1?id:5;p2Pick=seat===2?id:1;stagePick='bamboo';
    startNewGame();cutscene=null;roundIntroTimer=0;hitstopRemaining=0;paused=false;
    document.getElementById('pause-screen').classList.add('hidden');
    const d=seat===1?player1:player2,a=seat===1?player2:player1;
    d.x=side===1?canvas.width-10-d.width:10;
    a.x=d.x-side*92;a.facing=side;d.facing=-side;
    for(const p of [a,d]){p.y=GROUND_Y-p.height;p.isGrounded=true;p.vx=p.vy=0;p.hp=10000;}
    return {a,d,side,guard:seat===1?'KeyC':'KeyM'};
};
window.contact=(f,block=false,extra={})=>{
    f.d.state=block?STATE.BLOCKING:STATE.STUNNED;
    f.d.takeDamage(8,f.a,{pushback:80,tier:STATE.ATTACK_LIGHT,...extra});
    hitstopRemaining=0;
};
window.arm=(f,block=false)=>{for(let i=0;i<4;i++)contact(f,block);};
window.tick=(n=1)=>{for(let i=0;i<n;i++){animClock+=1/60;hitstopRemaining=0;updateGame(1/60);}};
window.breakHeld=f=>{key(f.guard,true);tick();};
return NINJA_ROSTER.filter(n=>!n.benched).map(n=>({id:n.id,name:n.name}));
'''

CASES = r'''
const roster=NINJA_ROSTER.filter(n=>!n.benched);
for(const fighter of roster)for(const side of [-1,1])for(const block of [false,true]){
    const f=fixture(fighter.id,side);f.d.stamina=block?100:0;f.d.windedTimer=1;
    key(f.guard,true);
    let genuineBlocks=true;
    for(let i=0;i<3;i++){contact(f,block);if(block)genuineBlocks=genuineBlocks&&f.d.state===STATE.BLOCKING;tick();}
    if(block)check(`${fighter.name} ${side}: block fixture really blocks`,genuineBlocks);
    check(`${fighter.name} ${side} ${block?'block':'hit'}: three contacts preserve pressure`,f.d.cornerBreakCount===0 && f.d.stunTimer>0);
    contact(f,block);tick();
    check(`${fighter.name} ${side} ${block?'block':'zero-chakra hit'}: held Guard breaks fourth`,f.d.cornerBreakCount===1 && f.d.stunTimer<=0 && f.d.cornerGrace>0,
      {count:f.d.cornerBreakCount,pressure:f.d.cornerPressure,grace:f.d.cornerGrace,stun:f.d.stunTimer});
    check(`${fighter.name} ${side}: break does no damage`,f.a.hp===10000);
}
let f=fixture();arm(f);check('four contacts offer a choice, never auto-break',f.d.cornerBreakReady() && f.d.cornerBreakCount===0);
breakHeld(f);check('Guard pressed after threshold also breaks',f.d.cornerBreakCount===1);
check('break consumes pressure once',f.d.cornerPressure===0);
tick(2);check('holding Guard cannot repeat break without new contacts',f.d.cornerBreakCount===1);
f.d.cornerGrace=0;f.a.stunTimer=0;f.a.cornerRecoilT=0;
for(let i=0;i<4;i++)contact(f);tick();check('another four contacts rearm without a cooldown',f.d.cornerBreakCount===2);

f=fixture();f.d.x=canvas.width/2;arm(f);breakHeld(f);
check('midscreen combo remains intact',!f.d.cornerBreakReady() && f.d.cornerBreakCount===0 && f.d.stunTimer>0);
f=fixture();f.d.armorTimer=2;arm(f);check('armored contacts do not arm escape',f.d.cornerPressure===0);
f=fixture();f.d.invulnTimer=2;arm(f);check('invulnerable overlaps do not arm escape',f.d.cornerPressure===0);
f=fixture();f.d.vanishTimer=2;arm(f);check('vanished overlaps do not arm escape',f.d.cornerPressure===0);
f=fixture();f.d.state=STATE.PARRY_STANCE;f.d.parryFlashTimer=1;
f.d.takeDamage(8,f.a,{pushback:80,tier:STATE.ATTACK_LIGHT});
check('successful parry does not count as corner pressure',f.d.cornerPressure===0);

f=fixture();contact(f);contact(f);f.d.stunTimer=0;f.d.recoveryTimer=0;f.d.state=STATE.IDLE;
f.d.updateCornerDefense(.4);check('short actionable gap retains pressure',f.d.cornerPressure===2);
f.d.updateCornerDefense(.41);check('full actionable gap resets pressure',f.d.cornerPressure===0);
f=fixture();contact(f);contact(f);f.d.stunTimer=1;f.d.updateCornerDefense(.81);
check('hitstun is not counted as safe recovery time',f.d.cornerPressure===2);
f=fixture();contact(f);contact(f);f.d.x=canvas.width/2;f.d.updateCornerDefense(1/60);
check('leaving the wall resets stored corner pressure',f.d.cornerPressure===0);

f=fixture();arm(f);breakHeld(f);const hp=f.d.hp;
f.a.hitConfirmed=false;f.d.takeDamage(30,f.a,{pushback:150,tier:STATE.ATTACK_SPECIAL},true);
check('grace denies projectile damage and hit-confirm riders',f.d.hp===hp && !f.a.hitConfirmed && f.d.stunTimer<=0);
f.a.stunTimer=f.a.cornerRecoilT=f.a.recoveryTimer=0;f.a.state=STATE.IDLE;f.a.x=f.d.x-20;
f.a.executeThrow();check('opponent cannot grab through grace',!f.d.grabbedBy);
f.d.cornerGrace=.01;f.d.updateCornerDefense(.02);f.d.takeDamage(8,f.a,{pushback:80});
check('grace expires and restores ordinary vulnerability',f.d.hp<hp && f.d.stunTimer>0);

for(const [label,action] of [['light',p=>p.executeAttack(STATE.ATTACK_LIGHT)],['heavy',p=>p.executeAttack(STATE.ATTACK_HEAVY)],['special',p=>p.executeAttack(STATE.ATTACK_SPECIAL)],['throw',p=>p.executeThrow()]]){
    f=fixture();arm(f);breakHeld(f);key(f.guard,false);f.d.stamina=100;
    action(f.d);check('offense ends grace: '+label,!f.d.isCornerProtected(),{grace:f.d.cornerGrace,state:f.d.state});
}
f=fixture();arm(f);breakHeld(f);key(f.guard,false);key('KeyA',true);const x=f.d.x;tick(3);
check('break permits immediate movement away from corner',f.d.x<x);
f=fixture();arm(f);breakHeld(f);key(f.guard,false);f.d.executeJump();tick(8);
check('break permits jump escape',!f.d.isGrounded || f.d.vy<0);
f=fixture();arm(f);breakHeld(f);key('KeyA',true);tick();
check('guard-direction roll remains a legal escape',f.d.rollTimer>0 || f.d.x<canvas.width-10-f.d.width);
f=fixture();f.d.isGrounded=false;f.d.y-=150;f.d.vy=-200;f.a.y=f.d.y;arm(f);breakHeld(f);
check('airborne corner pressure allows escape',f.d.cornerBreakCount===1 && f.d.stunTimer<=0 && !f.d.isGrounded && f.d.vy>=0);
key(f.guard,false);key('KeyA',true);tick(6);
check('air escape retains grace while drifting away',f.d.cornerGrace>0 && f.d.x<canvas.width-10-f.d.width);
f=fixture();arm(f);const foeX=f.a.x;breakHeld(f);tick(16);
check('recoil creates lasting room despite held aggressor movement',Math.abs(f.a.x-foeX)>100,{start:foeX,end:f.a.x});

f=fixture();arm(f);
f.d.bufferedAttack={type:STATE.ATTACK_LIGHT,ttl:.2};f.d.jumpBufferTimer=.12;
f.d.pendingSlash={type:'heavy'};f.d.recoveryTimer=1;f.d.groundBounce=true;
f.d.skySlam=true;f.d.tumbleOnLand=.3;f.d.flooredT=.8;f.d.rapidFire={n:3,t:1};
f.d.hitboxes.push({delay:1,duration:1});f.d.fxSched.push({t:1,kind:'palmshot'});
f.a.tether={target:f.d,t:2};
breakHeld(f);
check('break clears buffered and delayed offense',!f.d.bufferedAttack && !f.d.pendingSlash && f.d.hitboxes.length===0 && f.d.fxSched.length===0 && !f.d.rapidFire);
check('break clears landing/stun riders',!f.d.groundBounce && !f.d.skySlam && !f.d.tumbleOnLand && !f.d.flooredT && !f.d.jumpBufferTimer);
check('break releases incoming tether',!f.a.tether);

f=fixture();arm(f);breakHeld(f);
stageWires.push({x0:f.d.x-20,y0:f.d.y+f.d.height/2,x1:f.d.x+f.d.width+20,y1:f.d.y+f.d.height/2,hot:0});
f.d.wireCd=0;updateStageWires(1/60);
check('stage wire cannot immediately re-stun protected escape',f.d.stunTimer<=0);stageWires.length=0;
f=fixture();arm(f);key(f.guard,true);paused=true;
for(let i=0;i<10;i++)gameLoop(lastTime+1000/60);
check('paused frames cannot consume charged escape',f.d.cornerBreakCount===0 && f.d.cornerPressure===4);paused=false;
f=fixture();arm(f);f.d.hp=0;breakHeld(f);check('KO cannot break out',f.d.cornerBreakCount===0);
f=fixture();arm(f);f.d.grabbedBy=f.a;key(f.guard,true);
check('grab remains owned by throw tech',!f.d.tryCornerBreak());
f=fixture();arm(f);f.d.lockT=.4;key(f.guard,true);
check('blade lock retains its own escape rules',!f.d.tryCornerBreak());

f=fixture();contact(f,false,{wallsplat:true});const first=f.d.stunTimer;
contact(f,false,{wallsplat:true});const second=f.d.stunTimer;
check('only first wall-splat in a continuous combo extends stun',first-second>.29,{first,second});
f.d.stunTimer=0;f.d.state=STATE.IDLE;f.d.updateCornerDefense(1/60);
contact(f,false,{wallsplat:true});check('new combo restores one wall-splat bonus',Math.abs(f.d.stunTimer-first)<1e-8,{first,next:f.d.stunTimer});
f=fixture(5,-1);f.d.x=60;contact(f,false,{wallsplat:true});
check('near-corner pressure does not widen original wall-splat trigger',!f.d.wallSplatUsed && f.d.stunTimer<.6,{stun:f.d.stunTimer,used:f.d.wallSplatUsed});

f=fixture();currentStage={...currentStage,ledge:74};check('open outer ledge is not a solid corner',f.d.cornerWallSide()===0);
f=fixture();currentStage={...currentStage,abyss:true};check('abyss edge is not a solid corner',f.d.cornerWallSide()===0);
f=fixture();currentStage={...currentStage,walls:[{x:400,w:44,y0:50,y1:GROUND_Y-60}]};
f.d.x=400-f.d.width;f.d.y=120;f.d.isGrounded=false;check('interior wall left face counts',f.d.cornerWallSide()===1);
f.d.x=444;check('interior wall right face counts',f.d.cornerWallSide()===-1);
f.d.y=GROUND_Y-50;check('root arch under interior wall stays open',f.d.cornerWallSide()===0);

f=fixture(5,1,2);arm(f);key('KeyM',true);tick();check('P2 keyboard Guard uses same escape',f.d.cornerBreakCount===1);
f=fixture();arm(f);
document.getElementById('btn-t-p1-poof').dispatchEvent(new Event('touchstart',{bubbles:true,cancelable:true}));tick();
check('touch Guard uses same escape',f.d.cornerBreakCount===1);
document.getElementById('btn-t-p1-poof').dispatchEvent(new Event('touchend',{bubbles:true,cancelable:true}));
f=fixture();arm(f);const getPads=navigator.getGamepads;
const pad={connected:true,mapping:'standard',axes:[0,0],buttons:Array.from({length:16},()=>({pressed:false}))};
Object.defineProperty(navigator,'getGamepads',{configurable:true,value:()=>[pad,null]});pollGamepads();pad.buttons[4].pressed=true;pollGamepads();tick();
check('controller shoulder Guard uses same escape',f.d.cornerBreakCount===1);pad.buttons[4].pressed=false;pollGamepads();
Object.defineProperty(navigator,'getGamepads',{configurable:true,value:getPads});

f=fixture(5,1,2);arm(f);gameMode='1p';cpuMode=true;cpuThink(1/60,1);tick();
check('CPU uses the shared escape during a corner lock',f.d.cornerBreakCount===1,{count:f.d.cornerBreakCount,keys:{M:keys.KeyM,poof:keys.p2_poof}});
f=fixture();arm(f);breakHeld(f);gameMode='training';trainingReset(false);
check('training reset clears corner defense state',player1.cornerPressure===0 && player1.cornerGrace===0 && player1.cornerRecoilT===0 && !player1.wallSplatUsed);
check('corner-defense training drill exists',DRILLS.some(d=>/corner|escape/i.test(d.name)));
f=fixture();arm(f);gameMode='brawl';
const friend=new Player(3,f.d.x-60,f.d.y,f.d.spec,true),enemy=new Player(4,f.d.x-150,f.d.y,f.a.spec,false);
friend.opponent=f.a;enemy.opponent=f.d;friend.isGrounded=enemy.isGrounded=true;
brawlAll=[f.d,f.a,friend,enemy];key(f.guard,true);f.d.tryCornerBreak();
check('brawl break repels both nearby enemies',f.a.cornerRecoilT>0 && enemy.cornerRecoilT>0);
check('brawl break never stuns teammate',friend.cornerRecoilT===0 && friend.stunTimer===0);
f=fixture();arm(f);gameMode='brawl';
const thrower=new Player(3,f.a.x-10,f.a.y,f.d.spec,true);
thrower.throwVictim=f.a;thrower.throwTimer=.4;f.a.grabbedBy=thrower;f.a.state=STATE.THROWN;
brawlAll=[f.d,f.a,thrower];key(f.guard,true);f.d.tryCornerBreak();
check('brawl break preserves teammate paired throw',f.a.grabbedBy===thrower && f.a.state===STATE.THROWN && thrower.throwVictim===f.a && thrower.throwTimer===.4);
f=fixture();gameMode='training';drillIdx=1;key('KeyC',true);f.d.hp=f.a.hp=MAX_HP;
let attacks=0,drillContacts=0;const normalDamage=f.d.takeDamage;
f.d.takeDamage=function(...args){const oldHP=this.hp;normalDamage.apply(this,args);if(this.hp<oldHP)drillContacts++;};
for(let i=0;i<600;i++){gameLoop(lastTime+1000/60);if(f.a.isAttackingState())attacks++;}
check('training drill creates real corner contacts',attacks>0 && drillContacts>=4,{attackingFrames:attacks,contacts:drillContacts});
check('training drill pressure earns a held-Guard escape',f.d.cornerBreakCount>0,{breaks:f.d.cornerBreakCount});
drillIdx=0;
f=fixture();gameMode='teams';
const partner=new Player(3,300,GROUND_Y-f.d.height,f.d.spec,true);
teamP1=[f.d,partner];teamP2=[f.a,null];tagCd[0]=0;
for(const p of teamP1){p.cornerPressure=4;p.cornerSafeT=.2;p.cornerGrace=.3;p.cornerRecoilT=.1;p.cornerRecoilV=680;p.wallSplatUsed=true;}
const swapped=teamSwap(1);
check('successful team swap clears both partners corner defense',swapped && teamP1.every(p=>!p.cornerPressure&&!p.cornerSafeT&&!p.cornerGrace&&!p.cornerRecoilT&&!p.cornerRecoilV&&!p.wallSplatUsed));
return {checks:cornerChecks,failures:cornerChecks.filter(c=>!c.ok)};
'''

MIDSCREEN = r'''
const results=[];
for(const fighter of NINJA_ROSTER.filter(n=>!n.benched)){
    const f=fixture(fighter.id);f.d.x=canvas.width*.5;f.a.x=f.d.x-100;
    const rows=[];
    for(let i=0;i<8;i++){
        contact(f,false,{launch:i===2});tick(4);
        rows.push({hp:f.d.hp,x:f.d.x,y:f.d.y,vx:f.d.vx,vy:f.d.vy,stun:f.d.stunTimer,combo:f.d.comboHits,state:f.d.state});
    }
    results.push({fighter:fighter.name,rows});
}
return results;
'''

REPLAY = r'''
const f=fixture(5,1,2);
// Recreate by normal picks so every fighter-dependent constructor field is genuine.
p1Pick=2;p2Pick=5;startNewGame();cutscene=null;roundIntroTimer=0;hitstopRemaining=0;paused=false;
const a=player1,d=player2;a.x=canvas.width-10-d.width-90;d.x=canvas.width-10-d.width;
for(const p of [a,d]){p.y=GROUND_Y-p.height;p.isGrounded=true;p.hp=10000;p.vx=p.vy=0;}
releaseAllKeys();key('KeyD',true);
let seed=2137;Math.random=()=>((seed=Math.imul(seed,1664525)+1013904223>>>0)/4294967296);
const states=[],frames=[];let continuous=0,maxContinuous=0,peakCombo=0;
for(let n=0;n<480;n++){
    if(n%8===0){key('KeyF',false);key('KeyF',true);}
    if(n===45)key('KeyM',true);
    if(n===250)key('ArrowLeft',true);
    gameLoop(lastTime+1000/60);
    continuous=d.stunTimer>0?continuous+1:0;maxContinuous=Math.max(maxContinuous,continuous);peakCombo=Math.max(peakCombo,d.comboHits);
    const row={frame:n,hp:d.hp,x:d.x,stun:d.stunTimer,combo:d.comboHits,breaks:d.cornerBreakCount||0,grace:d.cornerGrace||0,state:d.state};
    states.push(row);
    if([0,44,45,55,75,150,270,479].includes(n)){drawScene();frames.push({frame:n,png:canvas.toDataURL('image/png')});}
}
releaseAllKeys();paused=true;
return {states,frames,maxContinuous,peakCombo,breaks:d.cornerBreakCount||0,damage:10000-d.hp};
'''


def filmstrip(frames, path, label):
    tiles=[]
    for frame in frames:
        raw=Image.open(io.BytesIO(base64.b64decode(frame['png'].split(',')[1]))).convert('RGB')
        raw.thumbnail((480,270))
        tile=Image.new('RGB',(480,294),'#111111')
        tile.paste(raw,((480-raw.width)//2,24+(270-raw.height)//2))
        ImageDraw.Draw(tile).text((8,5),f'{label} — gameLoop frame {frame["frame"]}',fill='white')
        tiles.append(tile)
    strip=Image.new('RGB',(480*4,294*2),'#111111')
    for i,tile in enumerate(tiles):strip.paste(tile,((i%4)*480,(i//4)*294))
    strip.save(path)


async def run_one(html, label, out, cases):
    browser.PORT=9395
    # Freeze the exact candidate too: a concurrent edit cannot change what the
    # recorded hash claims was loaded into this browser.
    html = html if html is not None else (ROOT/'web/index.html').read_text()
    with tempfile.TemporaryDirectory(prefix='corner-break-') as profile:
        proc,address=browser.launch('about:blank',profile)
        try:
            async with websockets.connect(address,max_size=64*1024*1024) as ws:
                c=Probe(ws,html)
                await c.send('Runtime.enable')
                if html:
                    await c.send('Fetch.enable',patterns=[{'urlPattern':'*index.html*','resourceType':'Document'}])
                await c.send('Page.navigate',url=URL)
                for _ in range(600):
                    if await c.js("return typeof SPRITES!=='undefined' && NINJA_ROSTER.filter(n=>!n.benched).every(n=>SPRITES[n.name.toLowerCase()]?.ready)") is True:break
                    await asyncio.sleep(.1)
                else:raise RuntimeError('roster did not load')
                await c.checked(SETUP)
                midscreen=await c.checked(MIDSCREEN)
                result=await c.checked(CASES) if cases else {}
                await c.checked(SETUP)
                replay=await c.checked(REPLAY)
                filmstrip(replay.pop('frames'),out/f'{label}-filmstrip.jpg',label)
                result['replay']=replay
                result['midscreen']=midscreen
                result['browserErrors']=c.errors
                result['sourceSHA256']=hashlib.sha256(html.encode()).hexdigest()
                (out/f'{label}.json').write_text(json.dumps(result,indent=2)+'\n')
                return result
        finally:
            proc.terminate();proc.wait(timeout=10)


async def main(args):
    browser.assert_serving_this_tree(URL)
    with socket.socket() as sock:
        if sock.connect_ex(('127.0.0.1',9395))==0:raise RuntimeError('debug port 9395 is in use; refusing to interrupt another run')
    args.out.mkdir(parents=True,exist_ok=True)
    baseline=await run_one(args.baseline.read_text(),'before',args.out,False) if args.baseline else None
    candidate=await run_one(None,'after',args.out,True)
    if baseline:
        for before,after in zip(baseline['midscreen'],candidate['midscreen']):
            candidate['checks'].append({'name':before['fighter']+' midscreen states exactly match original',
                                        'ok':before==after,'detail':None if before==after else {'before':before,'after':after}})
        candidate['checks'].append({'name':'real input reproduces old corner loop',
                                    'ok':baseline['replay']['maxContinuous']>=400,'detail':baseline['replay']['maxContinuous']})
        candidate['checks'].append({'name':'same real input escapes corrected corner loop',
                                    'ok':candidate['replay']['breaks']>0 and candidate['replay']['maxContinuous']<120,
                                    'detail':{k:v for k,v in candidate['replay'].items() if k!='states'}})
    candidate['failures']=[c for c in candidate['checks'] if not c['ok']]
    (args.out/'after.json').write_text(json.dumps(candidate,indent=2)+'\n')
    result={'baseline':{k:v for k,v in (baseline or {}).items() if k!='replay'},'candidate':candidate}
    if baseline:result['baselineReplay']={k:v for k,v in baseline['replay'].items() if k!='states'}
    for row in candidate['checks']:print(('PASS' if row['ok'] else 'FAIL')+': '+row['name'])
    print('Replay:',json.dumps({k:v for k,v in candidate['replay'].items() if k!='states'}))
    (args.out/'result.json').write_text(json.dumps(result,indent=2)+'\n')
    if candidate['failures'] or candidate['browserErrors']:raise SystemExit(1)


if __name__=='__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('--baseline',type=Path)
    parser.add_argument('--out',type=Path,required=True)
    asyncio.run(main(parser.parse_args()))
