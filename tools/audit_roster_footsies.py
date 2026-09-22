#!/usr/bin/env python3
"""Real-input roster frame audit. Reuses the production exporter and isolated CDP browser."""
import argparse
import asyncio
import base64
import hashlib
import json
import os
import re
import io
from PIL import Image, ImageDraw
import tempfile
from pathlib import Path

import websockets
import watch_game as browser
from export_footsies_frames import CAPTURE, validate

ROOT = Path(__file__).resolve().parents[1]


def capture_script():
    code = CAPTURE.replace("const axis=", """if(options.airborne){key('KeyW',true);updateGame(1/(60*COMBAT_TEMPO));key('KeyW',false);
for(let n=0;n<8;n++)updateGame(1/(60*COMBAT_TEMPO));}
const axis=""")
    code = code.replace("run:face>0?'KeyD':'KeyA'", "run:face>0?'KeyD':'KeyA',crouch:'KeyS',guard:'KeyC'")
    code = code.replace("const command=commands[options.move];key(command,true);", "const command=commands[options.move];if(!keys[command])key(command,true);")
    code = code.replace("if(options.move!=='run'&&options.move!=='jump')key(command,false);", "if(!['run','jump','crouch','guard'].includes(options.move))key(command,false);")
    code = code.replace("cell:authored?.hurtbox===null?null:p.drawCell,", "cell:authored?.hurtbox===null?null:p.drawCell,is_grounded:p.isGrounded,source_scale:man.scale*SHODO_DISPLAY_SCALE*(p.spec.renderScale||1)*(man.frameScale?.[p.drawCell]??1),attack_t:p.attackT,attack_anim:p.attackAnim?structuredClone(p.attackAnim):null,move_art:p.moveArt?{...p.moveArt}:null,queued_hitboxes:p.hitboxes.map(h=>({delay:h.delay,duration:h.duration})),")
    # Air moves remain in view; fixed world dimensions and pivot-relative framing are retained.
    code = code.replace("GROUND_Y-180", "p.y+p.height-180")
    # Specials include the actual scene's orbit/corridor FX, beyond body sprites.
    code = code.replace("scene_filmstrip:sceneStrip.toDataURL().split(',')[1],", "scene_filmstrip:options.move==='special'?sceneStrip.toDataURL().split(',')[1]:null,")
    code=code.replace("let probes=[],transforms=[],contacts=[];", """let probes=[],transforms=[],contacts=[],projectileProbes=[],readyFrames=0;
const oldProjectile=d.projectileTouches;
d.projectileTouches=function(proj,radius=4){const result=oldProjectile.apply(this,arguments);
 projectileProbes.push({kind:proj.kind??'star',x:proj.x,y:proj.y,radius,velocity:{x:proj.vx,y:proj.vy},eligible:!proj.fx,touches:result,defender_hurtbox:hurt(this)});return result;};""")
    code=code.replace("probes=[];transforms=[];contacts=[];const before", "probes=[];transforms=[];contacts=[];projectileProbes=[];const before")
    code=code.replace("const hb=hurt(p);", "for(const q of projectileProbes){g.strokeStyle='#ef4444';g.beginPath();g.arc(q.x,q.y,q.radius,0,2*Math.PI);g.stroke();}const hb=hurt(p);")
    code=code.replace("hitboxes:active,hurtbox:hb,", "hitboxes:active,hurtbox:hb,projectile_probes:projectileProbes,projectiles:p.projectiles.map(q=>({kind:q.kind??'star',x:q.x,y:q.y,vx:q.vx,vy:q.vy,eligible:!q.fx})),")
    code=code.replace("sceneG.fillText('F'+(i+1)+' '+frames.at(-1).phase,(i%6)*320+8,Math.floor(i/6)*250+14);", """sceneG.fillText('F'+(i+1)+' '+frames.at(-1).phase,(i%6)*320+8,Math.floor(i/6)*250+14);
  if(['light','medium','heavy','special'].includes(options.move)){
   readyFrames=(!p.isAttackingState()&&p.recoveryTimer<=0&&!p.projectiles.length&&!p.hitboxes.length)?readyFrames+1:0;
   if(i>=4&&readyFrames>=4)break;
  }""")
    code=code.replace("d.takeDamage=oldDamage;paused=true;", "d.takeDamage=oldDamage;d.projectileTouches=oldProjectile;paused=true;")
    return code


def source_hashes():
    text = (ROOT/'web/index.html').read_text()
    return {'source_sha256': hashlib.sha256(text.encode()).hexdigest(),
            'source_without_sheet_version_sha256': hashlib.sha256(re.sub(r'const SHEET_V[^\n]*', '', text).encode()).hexdigest()}


def matrix(baseline):
    for fighter in range(9):
        if baseline:
            for direction, move in [('neutral','light'),('forward','light'),('forward','heavy'),('forward','special')]:
                yield dict(fighter=fighter,move=move,direction=direction,facing=1,scenario='whiff',airborne=False)
            continue
        for facing in (1, -1):
            for airborne in (False, True):
                for direction in ('neutral','forward','back','down','up'):
                    for move in ('light','medium','heavy','special'):
                        yield dict(fighter=fighter,move=move,direction=direction,facing=facing,scenario='whiff',airborne=airborne)
            for move in ('run','jump','crouch','guard'):
                yield dict(fighter=fighter,move=move,direction='neutral',facing=facing,scenario='whiff',airborne=False)
            for scenario in ('hit','block'):
                for move in ('light','medium','heavy','special'):
                    yield dict(fighter=fighter,move=move,direction='forward',facing=facing,scenario=scenario,airborne=False)


def write_montage(film, data, dest):
    image=Image.open(io.BytesIO(film)).convert('RGB')
    draw=ImageDraw.Draw(image)
    for i,frame in enumerate(data['frames']):
        x,y=(i%6)*320,(i//6)*250
        draw.rectangle((x,y,x+320,y+29),fill='#e8e3d9')
        draw.text((x+8,y+9),f"F{i+1} {frame['phase']} cell {frame['cell']}",fill='#15171b')
    image=image.crop((0,0,1920,250*((len(data['frames'])+5)//6)))
    image.save(dest/'filmstrip.png')
    active=[i for i,f in enumerate(data['frames']) if f['hitboxes']]
    selected=sorted(set([0]+([max(0,active[0]-1),active[0],active[len(active)//2],active[-1],min(len(data['frames'])-1,active[-1]+1)] if active else [len(data['frames'])//4,len(data['frames'])//2,len(data['frames'])-1])))
    board=Image.new('RGB',(320*len(selected),250),'white')
    for j,i in enumerate(selected):
        x,y=(i%6)*320,(i//6)*250
        board.paste(image.crop((x,y,x+320,y+250)),(j*320,0))
    board.save(dest/'contact-montage.png')


def summarize(data):
    frames=data['frames']
    # A route may create its box only at release. A no-box entry sample is startup,
    # not recovery; use the first observed collision-active sample for that route.
    first=next((i for i,f in enumerate(frames) if f['hitboxes'] or any(p['eligible'] for p in f.get('projectile_probes',[]))),None)
    if first is not None:
        for f in frames[:first]:
            if f['phase']=='RECOVERY':f['phase']='STARTUP'
    phases={p:[f['frame_index'] for f in frames if f['phase']==p] for p in ('STARTUP','ACTIVE','RECOVERY','MOVEMENT')}
    return {'name':data['sequence_name'],'options':data['options'],
            'phase_frames':phases,'unique_actual_cells':sorted({f['cell'] for f in frames if f['cell'] is not None}),
            'contact_samples':[f['frame_index'] for f in frames if f['contacts']],
            'projectile_samples':[f['frame_index'] for f in frames if f.get('projectile_probes')],
            'damage':sum(f['defender']['damage_delta'] for f in frames),
            'end_state':frames[-1]['state'],'end_recovery_seconds':frames[-1]['recovery_seconds'],
            'active_reached':first is not None,'frame_count':len(frames),
            'offense_kind':('MELEE' if any(f['hitboxes'] for f in frames) else 'PROJECTILE' if any(f.get('projectile_probes') for f in frames) else 'NO_OFFENSE_OBSERVED'),
            'observation_truncated':frames[-1]['recovery_seconds']>0 or bool(frames[-1].get('projectiles'))}


async def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--baseline',action='store_true')
    parser.add_argument('--label',default='final')
    parser.add_argument('--core',action='store_true',help='Only both-facing core4 attacks plusrun/jump/crouch/guard')
    parser.add_argument('--frames',type=int,default=90)
    parser.add_argument('--fighters',type=int,nargs='+',default=list(range(1,9)))
    parser.add_argument('--moves',nargs='+',choices=['light','medium','heavy','special','run','jump','crouch','guard'])
    args=parser.parse_args()
    assert 1<=args.frames<=180
    out=ROOT/'media/roster-footsies-20260907'/args.label
    out.mkdir(parents=True,exist_ok=True)
    begin=source_hashes()
    url=os.environ.get('SHADOWCLASH_URL','http://localhost:9101/index.html')
    browser.assert_serving_this_tree(url)
    browser.PORT=int(os.environ.get('DEBUG_PORT','9390'))
    summaries=[]
    with tempfile.TemporaryDirectory(prefix='roster-footsies-') as profile:
        proc,address=browser.launch(url,profile)
        try:
            async with websockets.connect(address,max_size=100_000_000) as ws:
                cdp=browser.CDP(ws)
                for _ in range(400):
                    if await cdp.js("return typeof SPRITES!=='undefined'&&FX_CRESCENT.ready&&NINJA_ROSTER.every(s=>SPRITES[s.name.toLowerCase()]?.ready)") is True:break
                    await asyncio.sleep(.1)
                else:raise RuntimeError('roster did not load')
                loaded_scripts=await cdp.js("return Array.from(document.scripts,s=>s.textContent).join('\\n/* SCRIPT */\\n')")
                begin['loaded_inline_scripts_sha256']=hashlib.sha256(loaded_scripts.encode()).hexdigest()
                script=capture_script()
                def core(o):
                    return not o['airborne'] and o['scenario']=='whiff' and (o['move'] in ('run','jump','crouch','guard') or (o['direction'],o['move']) in [('neutral','light'),('forward','light'),('forward','heavy'),('forward','special')])
                cases=sorted(matrix(args.baseline),key=lambda o:not core(o))
                for options in cases:
                    if args.core and not core(options):continue
                    if args.moves and options['move'] not in args.moves:continue
                    if options['fighter'] not in args.fighters:continue
                    options['frames']=min(args.frames,32 if options['move']=='run' else 20) if options['move'] in ('run','guard','crouch') else min(args.frames,90) if options['move']=='jump' else args.frames
                    data=await cdp.js('const options='+json.dumps(options)+';\n'+script)
                    assert data and '__error' not in data,data
                    validate(data)
                    if options['fighter']==0 and options['move']=='heavy' and options['direction']=='forward' and not options['airborne']:
                        for frame in data['frames']:
                            if frame['hitboxes']:
                                assert frame['cell']==296, 'Executioner drive stab returned to recovery during contact'
                    if options['fighter']==3 and options['move']=='light' and options['direction']=='forward' and not options['airborne']:
                        for frame in data['frames']:
                            for render in frame['render']:
                                if render['cell'] in (314,321):
                                    assert render['matrix'][0]*options['facing']<0, 'Tsubasa ready/recovery art faces away from travel'
                    if options['fighter']==1 and options['move']=='crouch':
                        for frame in data['frames']:
                            assert frame['cell']==81, 'Mizu crouch fell back to her upright idle'
                            for render in frame['render']:
                                assert abs(render['scale_x']-render['scale_y'])<1e-6, 'Mizu drawn crouch was squashed'
                                assert abs(render['scale_x']-frame['source_scale'])<1e-6, 'Mizu crouch changed body scale'
                    if options['move']=='jump':
                        assert any(f['velocity']['y']<0 for f in data['frames']), 'jump never launched'
                        assert min(f['position']['y'] for f in data['frames'])<data['frames'][0]['position']['y']-1, 'jump never left floor'
                        for frame in data['frames']:
                            # Preserve source proportions through apex, descent, touchdown and idle too.
                            if frame['attack_anim']:
                                continue
                            for render in frame['render']:
                                assert abs(render['scale_x']-render['scale_y'])<1e-6, f"jump art has nonuniform scale at frame {frame['frame_index']}: {render}"
                                assert abs(render['scale_x']-frame['source_scale'])<1e-6, f"jump art differs from approved source scale at frame {frame['frame_index']}"
                    tag=f"{options['fighter']}-{'air' if options['airborne'] else 'ground'}-{options['direction']}-{options['move']}-{'R' if options['facing']==1 else 'L'}-{options['scenario']}"
                    dest=out/tag;dest.mkdir(exist_ok=True)
                    film=base64.b64decode(data.pop('filmstrip'))
                    # Labels are drawn after route-aware phase correction below.
                    scene=data.pop('scene_filmstrip',None)
                    if scene:
                        scene_image=Image.open(io.BytesIO(base64.b64decode(scene)))
                        scene_image.crop((0,0,1920,250*((len(data['frames'])+5)//6))).save(dest/'scene-filmstrip.png')
                    data['source_at_browser_load']=begin
                    summary=summarize(data);summary['path']=str(dest.relative_to(ROOT))
                    write_montage(film,data,dest)
                    (dest/'frame_breakdown.json').write_text(json.dumps(data,indent=2,allow_nan=False))
                    summaries.append(summary)
                    (out/'summary.json').write_text(json.dumps({'complete':False,'source_at_browser_load':begin,'source_current':source_hashes(),'sequences':summaries},indent=2))
                    print(tag,summary['name'],'active',summary['phase_frames']['ACTIVE'],'cells',summary['unique_actual_cells'],flush=True)
        finally:
            proc.terminate();proc.wait(timeout=10)
    end=source_hashes()
    (out/'summary.json').write_text(json.dumps({'complete':True,'source_at_browser_load':begin,'source_end':end,'source_changed':begin['source_sha256']!=end['source_sha256'],'sequences':summaries},indent=2))
    browser.assert_serving_this_tree(url,'after roster capture')
    print(f'PASS: {len(summaries)} real-input sequences; source_changed={begin['source_sha256']!=end['source_sha256']} → {out}',flush=True)


if __name__=='__main__':
    asyncio.run(main())
