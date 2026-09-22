#!/usr/bin/env python3
"""Capture real input, collision probes and consecutive Shodo frames for Agent 2."""
import argparse
import asyncio
import base64
import hashlib
import json
import os
import tempfile
from pathlib import Path

import websockets
import watch_game as browser


CAPTURE = r'''
dismissTitle();gameMode='2p';cpuMode=false;spectate=false;stagePick='bamboo';
p1Pick=options.fighter;p2Pick=options.fighter===0?1:0;startNewGame();
paused=false;roundIntroTimer=0;cutscene=null;hitstopRemaining=0;releaseAllKeys();
const p=player1,d=player2,face=options.facing;
Object.assign(p,{x:face>0?450:canvas.width-450-p.width,y:GROUND_Y-p.height,vx:0,vy:0,isGrounded:true,facing:face});
Object.assign(d,{x:p.x+face*(options.scenario==='whiff'?300:55),y:GROUND_Y-d.height,
 vx:0,vy:0,isGrounded:true,facing:-face});
const key=(code,down)=>window.dispatchEvent(new KeyboardEvent(down?'keydown':'keyup',{code,bubbles:true}));
if(options.scenario==='block') { key('KeyM',true); for(let n=0;n<20;n++)updateGame(1/(60*COMBAT_TEMPO)); }
const axis=options.direction==='forward'?face:options.direction==='back'?-face:0;
if(axis)key(axis>0?'KeyD':'KeyA',true);
if(options.direction==='down')key('KeyS',true);
if(options.direction==='up')key('KeyW',true);
const commands={light:'KeyF',medium:'KeyJ',heavy:'KeyG',special:'KeyH',jump:'KeyW',run:face>0?'KeyD':'KeyA'};
const command=commands[options.move];if(!keys[command])key(command,true); // no duplicate run/up keydown: that is a dash/double-jump input
if(options.move!=='run'&&options.move!=='jump')key(command,false);
const plate=document.createElement('canvas');plate.width=1200;plate.height=900;
const g=plate.getContext('2d'),tile=document.createElement('canvas');tile.width=320;tile.height=250;
const t=tile.getContext('2d'),strip=document.createElement('canvas');
strip.width=320*6;strip.height=250*Math.ceil(options.frames/6);const sg=strip.getContext('2d');
const frames=[],oldProcess=processHitboxes,oldDraw=drawShodoFrame;
const sceneStrip=document.createElement('canvas');sceneStrip.width=320*6;sceneStrip.height=250*Math.ceil(options.frames/6);
const sceneG=sceneStrip.getContext('2d');
let probes=[],transforms=[],contacts=[];
const oldDamage=d.takeDamage;
d.takeDamage=function(damage,attacker,h){const hp=this.hp;const result=oldDamage.apply(this,arguments);
 contacts.push({base_damage:damage,hp_lost:hp-this.hp,confirmed:!!attacker?.hitConfirmed,
 outcome:this.hp<hp?(this.state===STATE.BLOCKING?'BLOCK':'HIT'):'NO_DAMAGE',
 stun_seconds:this.stunTimer,velocity:{x:this.vx,y:this.vy}});return result;};
const box=(a,h)=>({x:a.x+h.ox,y:a.y+h.oy,width:h.w,height:h.h});
const hurt=a=>{const r=a.hurtbox();return r?{x:r.x,y:r.y,width:r.w,height:r.h}:null;};
processHitboxes=function(a,b,dt,advance=true){
 // Sample the same resolver the collision pass calls at this exact active tick.
 for(const h of a.hitboxes)refreshStrikeGeometry(a,h);
 if(a===p)probes.push({simulation_dt:dt,advance,defender_hurtbox:hurt(b),
   boxes:a.hitboxes.map(h=>{const frame=h.frameMove?footsiesFrame(a):null;
    const r=frame?.hitbox?footsiesRect(a,frame.hitbox):null;
    return {...(r?{x:r.x,y:r.y,width:r.w,height:r.h}:box(a,h)),eligible:!h.strikeInactive&&h.delay<=0&&(!h.frameMove||!!frame?.hitbox),delay:h.delay,duration:h.duration,
     damage:h.damage,pushback:h.pushback,launch:!!h.launch,launch_vy:h.launchVy??null};})});
 return oldProcess.apply(this,arguments);
};
drawShodoFrame=function(...a){
 if(a[1]===SPRITES[p.spec.name.toLowerCase()].img){const m=a[0].getTransform();
  transforms.push({cell:a[2]/a[4],scale_x:Math.hypot(m.a,m.b)*a[8]/a[4],
   scale_y:Math.hypot(m.c,m.d)*a[9]/a[5],matrix:[m.a,m.b,m.c,m.d,m.e,m.f]});}
 return oldDraw.apply(this,a);
};
try{
 for(let i=0;i<options.frames;i++){
  probes=[];transforms=[];contacts=[];const before={clock:animClock,vx:p.vx,vy:p.vy,hp:d.hp};
  // Frame 1 is the input-entry boundary; subsequent samples advance one authored game frame.
  if(i!==0||options.move!=='jump')updateGame(i===0?0:1/(60*COMBAT_TEMPO));
  const authored=footsiesFrame(p);
  g.clearRect(0,0,plate.width,plate.height);drawSprite(g,p);drawSprite(g,d);
  const active=probes.flatMap(q=>q.boxes.filter(b=>b.eligible));
  const hb=hurt(p);g.strokeStyle='#22c55e';g.lineWidth=1;if(hb)g.strokeRect(hb.x,hb.y,hb.width,hb.height);
  g.strokeStyle='#ef4444';for(const b of active)g.strokeRect(b.x,b.y,b.width,b.height);
  const man=SPRITES[p.spec.name.toLowerCase()];
  frames.push({frame_index:i+1,sample_time_seconds:i/60,simulation_time:animClock,
   simulation_dt:animClock-before.clock,state:p.state,cell:authored?.hurtbox===null?null:p.drawCell,authored_frame:authored?.frame_index??null,
   aliases:authored?.hurtbox===null?[]:Object.keys(man.frames).filter(k=>man.frames[k]===p.drawCell),
   phase:authored?.phase??(active.length?'ACTIVE':p.hitboxes.some(h=>h.delay>0)?'STARTUP':p.isAttackingState()?'RECOVERY':'MOVEMENT'),
   position:{x:p.x,y:p.y},velocity:{x:p.vx,y:p.vy},velocity_delta:{x:p.vx-before.vx,y:p.vy-before.vy},
   acceleration:animClock===before.clock?null:{x:(p.vx-before.vx)/(animClock-before.clock),y:(p.vy-before.vy)/(animClock-before.clock)},
   hitboxes:active,hurtbox:hb,collision_probes:probes,contacts,render:transforms,
   hit_confirmed:!!p.hitConfirmed,connected:!!p.attackHasConnected,recovery_seconds:p.recoveryTimer,
   hitstop_ms:hitstopRemaining,defender:{hp:d.hp,damage_delta:before.hp-d.hp,state:d.state,
    velocity:{x:d.vx,y:d.vy},hurtbox:hurt(d)}});
  t.fillStyle='#e8e3d9';t.fillRect(0,0,320,250);
  t.drawImage(plate,p.x-130,GROUND_Y-180,320,220,0,30,320,220);
  t.fillStyle='#15171b';t.font='12px sans-serif';t.fillText('F'+(i+1)+' '+frames.at(-1).phase+' cell '+p.drawCell,8,18);
  sg.drawImage(tile,(i%6)*320,Math.floor(i/6)*250);
  transforms=[];drawScene();sceneG.drawImage(canvas,p.x-130,GROUND_Y-180,320,220,(i%6)*320,Math.floor(i/6)*250+30,320,220);
  sceneG.fillStyle='#111';sceneG.fillRect((i%6)*320,Math.floor(i/6)*250,320,20);sceneG.fillStyle='#fff';
  sceneG.fillText('F'+(i+1)+' '+frames.at(-1).phase,(i%6)*320+8,Math.floor(i/6)*250+14);
 }
}finally{processHitboxes=oldProcess;drawShodoFrame=oldDraw;d.takeDamage=oldDamage;paused=true;releaseAllKeys();}
const man=SPRITES[p.spec.name.toLowerCase()];
return {schema_version:1,sequence_name:p.spec.name+' '+options.direction+' '+options.move,
 frame_rate_target:60,total_frames:frames.length,options,
 timing_policy:'60 Hz GAME-time boundary samples; frame 1 at input entry, updateGame delta=1/(60*COMBAT_TEMPO) thereafter; cinematic gameLoop hitstop crawl bypassed; runtime remains variable-step',
 units:{position:'world pixels, x right/y down',velocity:'pixels/game-second',acceleration:'pixels/game-second squared; includes collision/input impulses, not physical force'},
 reference:{fighter:p.spec.name,frame_width:man.frameW,frame_height:man.frameH,foot_y:man.footY,scale:man.scale},
 contract:JSON.parse(document.getElementById('footsies-data').textContent),frames,
 scene_filmstrip:sceneStrip.toDataURL().split(',')[1],filmstrip:strip.toDataURL().split(',')[1]};
'''


def validate(data):
    """Mechanical gate only. An independent visual score is still required."""
    assert len(data['frames']) == data['total_frames'] > 0
    for i, frame in enumerate(data['frames'], 1):
        assert frame['frame_index'] == i
        hidden = frame['hurtbox'] is None and frame['authored_frame'] is not None
        assert hidden or isinstance(frame['cell'], int), f'frame {i}: missing rendered cell'
        assert hidden or frame['render'], f'frame {i}: bypassed Shodo renderer'
        if hidden:
            assert frame['cell'] is None and not frame['render'], f'frame {i}: vanish body still rendered'
        for render in frame['render']:
            a, b, c, d, _, _ = render['matrix']
            assert abs(a*c + b*d) < 1e-6, f'frame {i}: character art is sheared'
            assert abs(render['scale_x'] - render['scale_y']) < 1e-6, f'frame {i}: character art is stretched'
        for box in ([frame['hurtbox']] if frame['hurtbox'] else []) + frame['hitboxes']:
            assert box['width'] > 0 and box['height'] > 0, (i, box)
        assert all(b['eligible'] for b in frame['hitboxes'])


async def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--fighter', type=int, choices=range(9), default=0)
    parser.add_argument('--move', choices=['light', 'medium', 'heavy', 'special', 'jump', 'run'], default='light')
    parser.add_argument('--direction', choices=['neutral', 'forward', 'back', 'up', 'down'], default='forward')
    parser.add_argument('--facing', type=int, choices=[-1, 1], default=1)
    parser.add_argument('--scenario', choices=['whiff', 'hit', 'block'], default='whiff')
    parser.add_argument('--frames', type=int, default=24)
    parser.add_argument('--out', type=Path, default=Path('media/footsies/shadow-slice'))
    args = parser.parse_args()
    if not 1 <= args.frames <= 180:
        parser.error('--frames must be 1..180')
    root = Path(__file__).resolve().parents[1]
    source_hash = hashlib.sha256((root/'web/index.html').read_bytes()).hexdigest()
    url = os.environ.get('SHADOWCLASH_URL', 'http://localhost:9101/index.html')
    browser.assert_serving_this_tree(url)
    browser.PORT = int(os.environ.get('DEBUG_PORT', '9387'))
    with tempfile.TemporaryDirectory(prefix='footsies-frames-') as profile:
        proc, address = browser.launch(url, profile)
        try:
            async with websockets.connect(address, max_size=100_000_000) as ws:
                cdp = browser.CDP(ws)
                for _ in range(400):
                    ready = await cdp.js("return typeof SPRITES!=='undefined'&&FX_CRESCENT.ready&&NINJA_ROSTER.every(s=>SPRITES[s.name.toLowerCase()]?.ready)")
                    if ready is True:
                        break
                    await asyncio.sleep(.1)
                else:
                    raise RuntimeError('roster did not load')
                options = {k: v for k, v in vars(args).items() if k != 'out'}
                result = await cdp.js('const options=' + json.dumps(options) + ';\n' + CAPTURE)
                assert result and '__error' not in result, result
        finally:
            proc.terminate()
            proc.wait(timeout=10)
    browser.assert_serving_this_tree(url, 'after capture')
    validate(result)
    root = Path(__file__).resolve().parents[1]
    assert source_hash == hashlib.sha256((root/'web/index.html').read_bytes()).hexdigest(), 'game source changed during capture; rerun'
    result['source_sha256'] = source_hash
    args.out.mkdir(parents=True, exist_ok=True)
    (args.out/'scene-filmstrip.png').write_bytes(base64.b64decode(result.pop('scene_filmstrip')))
    (args.out/'filmstrip.png').write_bytes(base64.b64decode(result.pop('filmstrip')))
    (args.out/'frame_breakdown.json').write_text(json.dumps(result, indent=2, allow_nan=False))
    print(f'PASS: {result["total_frames"]} consecutive simulation/render samples → {args.out}')


if __name__ == '__main__':
    asyncio.run(main())
