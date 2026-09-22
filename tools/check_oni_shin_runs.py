#!/usr/bin/env python3
"""Check Oni/Shin run playback, source preservation and physical travel through real input."""
import argparse
import asyncio
import base64
import hashlib
import json
import os
import subprocess
import tempfile
from pathlib import Path

import websockets
from PIL import Image
import watch_game as browser

Image.MAX_IMAGE_PIXELS = None  # the local append-only Oni atlas intentionally exceeds Pillow's default limit


def sources():
    result = {'index_sha256': hashlib.sha256(Path('web/index.html').read_bytes()).hexdigest()}
    for name in ['oni', 'shin']:
        path = Path(f'web/assets/sprites/{name}')
        man = json.loads(path.with_suffix('.json').read_text())
        sheet = Image.open(path.with_suffix('.png')).convert('RGBA')
        cells = []
        for n in range(1, 33):
            cell = man['frames'].get(f'run_clean{n}')
            if cell is None:
                break
            x, y = cell % man['cols'] * man['frameW'], cell // man['cols'] * man['frameH']
            rgba = sheet.crop((x, y, x + man['frameW'], y + man['frameH']))
            cells.append({'cell': cell, 'rgba_sha256': hashlib.sha256(rgba.tobytes()).hexdigest()})
        result[name] = {'manifest_sha256': hashlib.sha256(path.with_suffix('.json').read_bytes()).hexdigest(),
                        'sheet_sha256': hashlib.sha256(path.with_suffix('.png').read_bytes()).hexdigest(), 'cells': cells}
    return result


async def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--out', type=Path, default=Path('media/oni-shin-runs-20260907/after/runtime.json'))
    parser.add_argument('--baseline', type=Path)
    parser.add_argument('--fighter', type=int, choices=[2, 8])
    parser.add_argument('--candidate-map', type=Path, help='Preview packed run cells in browser memory only')
    parser.add_argument('--film', action='store_true')
    args = parser.parse_args()
    before = sources()
    options = {'fighters': [args.fighter] if args.fighter is not None else [8, 2], 'film': args.film}
    if args.candidate_map:
        candidate_rows = json.loads(args.candidate_map.read_text())
        options['candidateFighter'] = 'shin' if args.fighter == 2 else 'oni'
        if isinstance(candidate_rows, dict):
            candidate_rows = [{**row, 'path': str(args.candidate_map.parent/row['cell_file']),
                               'new_slot': row['slot'], 'phase': row['role'], 'mirror': False}
                              for row in candidate_rows['candidates']]
        options['candidates'] = [{**row, 'png': base64.b64encode(Path(row['path']).read_bytes()).decode(),
                                  'sha256': hashlib.sha256(Path(row['path']).read_bytes()).hexdigest()}
                                 for row in candidate_rows]
    browser.assert_serving_this_tree('http://localhost:9101/index.html')
    browser.PORT = int(os.environ.get('DEBUG_PORT', '9372'))
    with tempfile.TemporaryDirectory(prefix='oni-shin-runs-') as profile:
        proc, address = browser.launch('http://localhost:9101/index.html', profile)
        try:
            async with websockets.connect(address, max_size=100_000_000) as ws:
                c = browser.CDP(ws)
                for _ in range(400):
                    if await c.js("return typeof SPRITES!=='undefined'&&NINJA_ROSTER.every(s=>SPRITES[s.name.toLowerCase()]?.ready)"):
                        break
                    await asyncio.sleep(.1)
                result = await c.js('const options='+json.dumps(options)+';\n'+r'''
                dismissTitle();const failures=[],runs=[];
                if(options.candidates){
                    const man=SPRITES[options.candidateFighter],old=man.img,oldF=man.frames,keep=[...new Set(Object.entries(oldF).filter(([k])=>/idle|stand|crouch|jland/.test(k)).map(([,v])=>v))];
                    const atlas=document.createElement('canvas');atlas.width=(8+keep.length)*man.frameW;atlas.height=man.frameH;
                    const ag=atlas.getContext('2d'),F={},mirror={},scale={},foot={},originalSlot={};
                    const copy=(src,to)=>{ag.drawImage(keyedShodoCell(old,src*man.frameW,0,man.frameW,man.frameH),to*man.frameW,0);mirror[to]=!!man.mirror?.[src];scale[to]=man.frameScale?.[src]??1;foot[to]=man.footAdj?.[src]??0;originalSlot[src]=to;};
                    const base=runCells(oldF);
                    for(let i=0;i<8;i++)if(!options.candidates.some(row=>row.new_slot===i+1))copy(base[i],i);
                    for(const row of options.candidates){const img=new Image();img.src='data:image/png;base64,'+row.png;await img.decode();ag.drawImage(img,(row.new_slot-1)*man.frameW,0);mirror[row.new_slot-1]=row.mirror;}
                    keep.forEach((src,i)=>copy(src,8+i));
                    for(const [k,src] of Object.entries(oldF))if(originalSlot[src]!==undefined)F[k]=originalSlot[src];
                    for(let n=1;n<=8;n++)F['run_clean'+n]=n-1;
                    const img=new Image();img.src=atlas.toDataURL();await img.decode();
                    Object.assign(man,{img,frames:F,cols:8+keep.length,mirror,frameScale:scale,footAdj:foot});
                }
                const check=(ok,msg)=>{if(!ok&&!failures.includes(msg))failures.push(msg);};
                const key=(code,down)=>window.dispatchEvent(new KeyboardEvent(down?'keydown':'keyup',{code,bubbles:true}));
                const plate=document.createElement('canvas');plate.width=1200;plate.height=850;const g=plate.getContext('2d');
                const preview=document.createElement('canvas');preview.width=320;preview.height=250;const pg=preview.getContext('2d');
                for(const id of options.fighters)for(const facing of [-1,1]){
                    gameMode='2p';cpuMode=false;spectate=false;stagePick='bamboo';p1Pick=id;p2Pick=0;
                    startNewGame();paused=false;roundIntroTimer=0;hitstopRemaining=0;cutscene=null;releaseAllKeys();
                    const p=player1,man=SPRITES[p.spec.name.toLowerCase()],cells=runCells(man.frames),frames=[];
                    const x=facing>0?100:820,move=facing>0?'KeyD':'KeyA';
                    Object.assign(p,{x,y:GROUND_Y-p.height,isGrounded:true,_wasGrounded:true,vx:0,vy:0,state:STATE.IDLE,facing,landT:0});
                    player2.x=facing>0?940:20;let runStart,runEnd;
                    for(let tick=0;tick<100;tick++){
                        if(tick===12){runStart={x:p.x,phase:p.animPhase};key(move,true);}
                        if(tick===72){runEnd={x:p.x,phase:p.animPhase};key(move,false);}
                        updateGame(1/(60*COMBAT_TEMPO));
                        let draw=null;const original=drawShodoFrame;
                        drawShodoFrame=function(...a){if(a[1]===man.img){const m=a[0].getTransform();draw={x:Math.hypot(m.a,m.b)*a[8]/a[4],y:Math.hypot(m.c,m.d)*a[9]/a[5],mirror:Math.sign(m.a),b:m.b,c:m.c};}return original.apply(this,a);};
                        try{g.clearRect(0,0,1200,850);drawSprite(g,p);}finally{drawShodoFrame=original;}
                        const idx=p.drawCell,scale=man.scale*SHODO_DISPLAY_SCALE*(p.spec.renderScale||1)*(man.frameScale?.[idx]??1);
                        check(Number.isInteger(idx)&&idx>=0&&idx<man.cols,id+' missing cell');
                        check(draw&&Math.abs(draw.x-scale)<1e-8&&Math.abs(draw.y-scale)<1e-8&&!draw.b&&!draw.c,id+' warped locomotion');
                        if(tick>=12&&tick<72){check(p.state===STATE.RUN,id+' run input state');check(p.facing===facing,id+' run facing');check(cells.includes(idx),id+' run chose another row');check(draw?.mirror===-facing*(man.mirror?.[idx]?-1:1),id+' render facing');}
                        const ink=cellInk(man,idx);
                        const record={tick,frame_number:tick+1,sample_time_seconds:tick/60,state:p.state,cell:idx,x:p.x,vx:p.vx,facing:p.facing,phase:p.animPhase,
                            aliases:Object.keys(man.frames).filter(k=>man.frames[k]===idx),run_slot:cells.indexOf(idx)+1,
                            draw,scale,lowest_ink_from_ground:(ink.y1+1-man.footY+(man.footAdj?.[idx]||0))*scale};
                        if(options.film){drawScene();pg.fillStyle='#16181c';pg.fillRect(0,0,320,250);pg.drawImage(canvas,p.x-130,GROUND_Y-180,320,220,0,30,320,220);pg.fillStyle='#fff';pg.font='12px sans-serif';pg.fillText(p.spec.name+' F'+(tick+1)+' '+p.state+' cell '+idx,8,18);record.png=preview.toDataURL().split(',')[1];}
                        frames.push(record);
                    }
                    const active=frames.slice(12,72),cycleRate=Math.min(3,Math.abs(active[0].vx)/150)*(p.spec.runAnimScale||1);
                    // Phase advances before handleMovement, so the entry tick still uses idle cadence.
                    const measuredRate=(runEnd.phase-active[0].phase)/cells.length/(59/60);
                    check(Math.abs(measuredRate-cycleRate)<1e-8,id+' length changed loop cadence');
                    check(Math.abs(Math.abs(runEnd.x-runStart.x)-Math.abs(active[0].vx))<.001,id+' obstructed run travel');
                    check(new Set(active.map(f=>f.cell)).size===new Set(cells).size,id+' missing run exposures');
                    check(p.state===STATE.IDLE&&Math.abs(p.vx)<1,id+' stop stayed running');
                    runs.push({id,name:p.spec.name,facing,cells,world_speed:Math.abs(active[0].vx),run_distance:Math.abs(runEnd.x-runStart.x),
                        cycles_per_game_second:cycleRate,measured_cycles_per_game_second:measuredRate,stop_distance:Math.abs(p.x-runEnd.x),frames});
                }
                if(options.film)for(const run of runs){
                    const starts=run.frames.filter((f,i,a)=>i&&f.state===STATE.RUN&&f.run_slot===1&&a[i-1].run_slot===run.cells.length).map(f=>f.tick);
                    const cycle=run.frames.slice(starts[0],starts[1]),groups=[];
                    for(const f of cycle){if(!groups.length||groups.at(-1).cell!==f.cell)groups.push({cell:f.cell,slot:f.run_slot,frames:[]});groups.at(-1).frames.push(f.tick);}
                    const board=document.createElement('canvas');board.width=1280;board.height=40+250*Math.ceil(groups.length/4);const bg=board.getContext('2d');
                    bg.fillStyle='#12151a';bg.fillRect(0,0,board.width,board.height);bg.fillStyle='#eee';bg.font='18px sans-serif';
                    bg.fillText(run.name+' · one complete cycle · '+(run.facing>0?'right':'left')+' · exact game-rendered poses',12,24);
                    for(let i=0;i<groups.length;i++){const group=groups[i],f=run.frames[group.frames[Math.floor(group.frames.length/2)]],im=new Image();im.src='data:image/png;base64,'+f.png;await im.decode();const x=i%4*320,y=40+Math.floor(i/4)*250;bg.fillStyle='#eee';bg.font='13px sans-serif';bg.fillText('Slot '+group.slot+' · cell '+group.cell+' · '+group.frames.length+' game frames',x+8,y+18);bg.drawImage(im,0,30,320,220,x,y+26,320,220);}
                    run.cycle_exposures=groups;run.cycle_contact_sheet=board.toDataURL().split(',')[1];
                }
                paused=true;releaseAllKeys();return{failures,runs};
                ''')
                assert result and '__error' not in result, result
        finally:
            proc.terminate()
            proc.wait(timeout=10)
    assert before == sources(), 'source changed during run check; rerun'
    result['sources'] = before
    if args.candidate_map:
        result['candidate_sources'] = [{k:v for k,v in row.items() if k!='png'} for row in options['candidates']]
        result['preview_only'] = True
    if args.baseline:
        baseline = json.loads(args.baseline.read_text())
        for old, new in zip(baseline['runs'], result['runs']):
            for field in ['id','facing','world_speed','run_distance','cycles_per_game_second','stop_distance']:
                assert abs(old[field]-new[field]) < 1e-8, (field, old[field], new[field])
        for name in ['oni', 'shin']:
            old, new = baseline['sources'][name]['cells'], before[name]['cells']
            assert len(new) == 8, (name, new)
            preserved = [0,4] if name == 'oni' else [0,1,3,5,6,7]
            for target in preserved:
                source = target//4 if name == 'oni' else target
                assert new[target] == old[source], (name, target, 'changed preserved drawing')
            if name == 'shin':
                assert new[2]['cell'] != 279 and new[4]['cell'] != 281, 'rejected Shin phases remain active'
    args.out.parent.mkdir(parents=True, exist_ok=True)
    if args.film:
        for run in result['runs']:
            folder=args.out.parent/(run['name'].lower()+('-right' if run['facing']>0 else '-left'))
            frames=folder/'frames';frames.mkdir(parents=True,exist_ok=True)
            (folder/'cycle-contact-sheet.png').write_bytes(base64.b64decode(run.pop('cycle_contact_sheet')))
            for i,frame in enumerate(run['frames']):
                (frames/f'{i:03}.png').write_bytes(base64.b64decode(frame.pop('png')))
            breakdown={**run,'sequence_name':run['name']+' idle-run-stop','total_frames':len(run['frames']),'frame_rate_target':60,
                       'timing_policy':'Consecutive60Hz game-time samples; GIF plays at current1.2 tempo, resampled30fps; all100 original screenshots retained.',
                       'sources':before,'candidate_sources':result.get('candidate_sources'), 'preview_only':bool(args.candidate_map)}
            (folder/'frame_breakdown.json').write_text(json.dumps(breakdown,indent=2))
            subprocess.run(['ffmpeg','-y','-loglevel','error','-framerate','72','-i',str(frames/'%03d.png'),
                            '-filter_complex','fps=30,scale=640:500:flags=neighbor,split[a][b];[a]palettegen[p];[b][p]paletteuse',
                            '-loop','0',str(folder/'run-preview.gif')],check=True,timeout=30)
            run_end=12+round(120/run['cycles_per_game_second'])
            subprocess.run(['ffmpeg','-y','-loglevel','error','-framerate','72','-i',str(frames/'%03d.png'),
                            '-filter_complex',f'trim=start_frame=12:end_frame={run_end},setpts=PTS-STARTPTS,fps=30,scale=640:500:flags=neighbor,split[a][b];[a]palettegen[p];[b][p]paletteuse',
                            '-loop','0',str(folder/'run-loop.gif')],check=True,timeout=30)
    args.out.write_text(json.dumps(result, indent=2))
    assert not result['failures'], result['failures']
    print(f"PASS: {sum(len(r['frames']) for r in result['runs'])} real-input run/idle transition samples, both directions; travel, normalized cadence and rigid transforms → {args.out}")


if __name__ == '__main__':
    asyncio.run(main())
