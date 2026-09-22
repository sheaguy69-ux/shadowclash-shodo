#!/usr/bin/env python3
"""Compare runtime pages with original atlases and replay real, deterministic fights.

Run against the designated :9101 server, with its original HTML snapshot:
  python3 tools/check_runtime_sprites.py --baseline media/game-polish-20260920/index.before.html --out media/game-polish-20260920/runtime-check

The source oracle is the baseline's actual keyer/outline code, isolated from the
candidate caches. Every original cell is compared byte-for-byte in Canvas before
and after keying, including blank/unreferenced cells and Ember's shorter crop.
Outlined samples and Shin's raw projectile transformations are compared too.
Real gameLoop replays use the same seeded randomness, clock, and key events on
both HTML versions; the script saves every combat state and sampled filmstrips.
It launches only its own Chrome on debug port 9395 and never kills another run.
"""
import argparse
import asyncio
import base64
import hashlib
import json
import socket
import subprocess
import tempfile
from pathlib import Path

import websockets
import watch_game as browser

ROOT = Path(__file__).resolve().parent.parent
URL = 'http://127.0.0.1:9101/index.html'


class Probe(browser.CDP):
    def __init__(self, ws, html=None):
        super().__init__(ws)
        self.html, self.aux, self.errors = html, 100000, []

    async def send(self, method, **params):
        self.n += 1
        wanted = self.n
        await self.ws.send(json.dumps({'id': wanted, 'method': method, 'params': params}))
        while True:
            msg = json.loads(await asyncio.wait_for(self.ws.recv(), 90))
            if msg.get('method') == 'Fetch.requestPaused':
                self.aux += 1
                await self.ws.send(json.dumps({'id': self.aux, 'method': 'Fetch.fulfillRequest', 'params': {
                    'requestId': msg['params']['requestId'], 'responseCode': 200,
                    'responseHeaders': [{'name': 'Content-Type', 'value': 'text/html'}],
                    'body': base64.b64encode(self.html.encode()).decode()}}))
            if msg.get('method') == 'Runtime.exceptionThrown':
                self.errors.append(msg['params']['exceptionDetails'])
            if msg.get('id') == wanted:
                if 'error' in msg:
                    raise RuntimeError(msg['error'])
                return msg.get('result', {})

    async def checked(self, source):
        result = await self.js(source)
        if isinstance(result, dict) and '__error' in result:
            raise RuntimeError(result['__error'])
        return result


ORACLE_SETUP = r'''
paused=true;
window.requestAnimationFrame=()=>0;
window.runtimeOracle=ORACLE;
window.runtimeComparison={};
window.pixelDiff=(a,b)=>{
    if(a.length!==b.length)return {different:-1,maxDelta:-1};
    let different=0,maxDelta=0;
    for(let i=0;i<a.length;i++)if(a[i]!==b[i]){different++;maxDelta=Math.max(maxDelta,Math.abs(a[i]-b[i]));}
    return {different,maxDelta};
};
return NINJA_ROSTER.filter(n=>!n.benched).map(n=>n.name.toLowerCase());
'''

CELL_SETUP = r'''
const man=SPRITES[NAME];
if(!man?.ready || !man.img.shodoRuntime)throw new Error(NAME+' did not use runtime pages');
const source=new Image();
source.src=new URL('assets/sprites/'+NAME+'.png?runtime-oracle=1',location.href).href;
await source.decode();
// A single pinned source avoids reproducing giant-atlas decode eviction in the
// oracle itself. It is closed before the next fighter, never retained as a pair.
const original=await createImageBitmap(source);
original.src=original.currentSrc=source.currentSrc;
if(original.width!==man.frameW*man.cols || original.height!==man.frameH)throw new Error(NAME+' original geometry differs');
const verify=document.createElement('canvas');verify.width=man.frameW;verify.height=man.frameH;
const vg=verify.getContext('2d',{willReadFrequently:true});
for(const idx of [...new Set([0,man.frames.idle,man.cols-1])]){
    vg.clearRect(0,0,verify.width,verify.height);vg.drawImage(source,idx*man.frameW,0,man.frameW,man.frameH,0,0,man.frameW,man.frameH);
    const a=vg.getImageData(0,0,verify.width,verify.height).data;
    vg.clearRect(0,0,verify.width,verify.height);vg.drawImage(original,idx*man.frameW,0,man.frameW,man.frameH,0,0,man.frameW,man.frameH);
    if(pixelDiff(a,vg.getImageData(0,0,verify.width,verify.height).data).different)throw new Error(NAME+' bitmap differs from original Image');
}
original.shodoClearRects=man.frameClear;
original.shodoFrameOffsetX=man.frameOffsetX;
original.shodoWeaponRegions=man.weaponNoOutline;
window.runtimeComparison={name:NAME,man,original,originalImage:source};
return {name:NAME,cols:man.cols,frameW:man.frameW,frameH:man.frameH,
    runtimeCells:man.img.shodoRuntime.cells.length,pages:man.img.shodoPages.length,
    rawWireRouteLive:man.frames.wire1!==undefined};
'''

CELL_BATCH = r'''
const {name,man,original,originalImage}=runtimeComparison,fw=man.frameW,fh=man.frameH;
const make=(w,h)=>{const c=document.createElement('canvas');c.width=w;c.height=h;return c.getContext('2d',{willReadFrequently:true});};
const left=make(fw,fh),right=make(fw,fh),failures=[];
let raw=0,keyed=0,outlined=0,wire=0;
const compare=(kind,idx,a,b,extra={})=>{
    const diff=pixelDiff(a,b);if(diff.different)failures.push({kind,idx,...extra,...diff});
};
if(START===0){
    const idx=man.img.shodoRuntime.cells.findIndex(c=>c&&c[4]>20);
    if(idx>=0){
        const cell=man.img.shodoRuntime.cells[idx],sy=cell[6]+Math.floor(cell[4]/2),height=fh-sy;
        left.clearRect(0,0,fw,fh);right.clearRect(0,0,fw,fh);
        left.drawImage(original,idx*fw,sy,fw,height,0,0,fw,height);
        drawSpriteSource(right,man.img,idx*fw,sy,fw,height,0,0,fw,height);
        compare('partial-source-crop',idx,left.getImageData(0,0,fw,fh).data,right.getImageData(0,0,fw,fh).data,{sy,height});
    }
}
for(let idx=START;idx<END;idx++){
    for(const height of (name==='ember'&&idx<385?[fh,419]:[fh])){
        left.clearRect(0,0,fw,fh);right.clearRect(0,0,fw,fh);
        left.drawImage(original,idx*fw,0,fw,height,0,0,fw,height);
        drawSpriteSource(right,man.img,idx*fw,0,fw,height,0,0,fw,height);
        compare('raw',idx,left.getImageData(0,0,fw,fh).data,right.getImageData(0,0,fw,fh).data,{height});raw++;
        const a=runtimeOracle.keyedShodoCell(original,idx*fw,0,fw,height);
        const b=keyedShodoCell(man.img,idx*fw,0,fw,height);
        compare('keyed',idx,a.getContext('2d').getImageData(0,0,fw,height).data,b.getContext('2d').getImageData(0,0,fw,height).data,{height});keyed++;
    }
    const sample=idx===man.frames.idle || idx===man.cols-1 || idx%Math.max(1,Math.floor(man.cols/12))===0
        || man.weaponNoOutline?.[idx] || man.frameOffsetX?.[idx];
    // Current Shin has wallthrow cells but no wire1 alias. Probe those real
    // packed cells through the raw projectile transform as well as future wire rows.
    const isWire=name==='shin'&&Object.entries(man.frames).some(([k,v])=>/^(?:wire|wallthrow)\d+$/.test(k)&&v===idx);
    if(sample||isWire){
        const a=make(640,640),b=make(640,640);
        for(const facing of [-1,1]){
            const paint=(g,fn,img,scale)=>{g.resetTransform();g.clearRect(0,0,640,640);g.save();
                g.translate(319.375,347.625);g.scale(facing,1);g.globalAlpha=.73;
                fn(g,img,idx*fw,0,fw,fh,-fw*scale/2,-fh*scale/2,fw*scale,fh*scale);g.restore();};
            if(sample){
                const scale=man.scale*SHODO_DISPLAY_SCALE*(man.frameScale?.[idx]??1);
                paint(a,runtimeOracle.drawShodoFrame,original,scale);
                paint(b,drawShodoFrame,man.img,scale);
                compare('outlined',idx,a.getImageData(0,0,640,640).data,b.getImageData(0,0,640,640).data,{facing});outlined++;
            }
            if(isWire){
                // The current manifest has no wire1. Simulate the conditional
                // original-image companion that a future wire-enabled sheet gets,
                // without changing the production descriptor used by cell tests.
                const rawDescriptor=Object.assign({},man.img,{shodoRawImage:originalImage});
                paint(a,(g,img,...args)=>g.drawImage(img,...args),originalImage,.35);
                paint(b,drawSpriteSource,rawDescriptor,.35);
                compare('wire-transform',idx,a.getImageData(0,0,640,640).data,b.getImageData(0,0,640,640).data,{facing});wire++;
            }
        }
    }
    // Keep the exhaustive oracle bounded; these caches are rebuilt by the game.
    runtimeOracle.clear();shodoCellCache.clear();shodoFrameCache.clear();
}
return {raw,keyed,outlined,wire,failures};
'''

RAW_PROBE = r'''
const {man,originalImage}=runtimeComparison,fw=man.frameW,fh=man.frameH,idx=338;
const make=(w,h)=>{const c=document.createElement('canvas');c.width=w;c.height=h;return c.getContext('2d',{willReadFrequently:true});};
const cropped=make(fw,fh);cropped.drawImage(originalImage,idx*fw,0,fw,fh,0,0,fw,fh);
const strip=make(1920,1280),results=[];
for(const [row,facing] of [-1,1].entries()){
    const canvases=[make(640,640),make(640,640),make(640,640)];
    for(const [i,g] of canvases.entries()){
        g.translate(319.375,347.625);g.scale(facing,1);g.globalAlpha=.73;
        const dst=[-fw*.35/2,-fh*.35/2,fw*.35,fh*.35];
        if(i===0)g.drawImage(originalImage,idx*fw,0,fw,fh,...dst);
        if(i===1)g.drawImage(cropped.canvas,0,0,fw,fh,...dst);
        if(i===2)drawSpriteSource(g,man.img,idx*fw,0,fw,fh,...dst);
        strip.drawImage(g.canvas,i*640,row*640);
    }
    const arrays=canvases.map(g=>g.getImageData(0,0,640,640).data);
    const detail=(a,b)=>{let alphaPixels=0,alphaMax=0,premultMax=0,premultSum=0,visiblePixels=0;
        for(let i=0;i<a.length;i+=4){const da=Math.abs(a[i+3]-b[i+3]);if(da){alphaPixels++;alphaMax=Math.max(alphaMax,da);}
            let differs=da>0;for(let c=0;c<3;c++){const delta=Math.abs(a[i+c]*a[i+3]-b[i+c]*b[i+3])/255;
                premultMax=Math.max(premultMax,delta);premultSum+=delta;differs ||= delta>.5;}
            if(differs&&Math.max(a[i+3],b[i+3])>=8)visiblePixels++;}
        return {...pixelDiff(a,b),alphaPixels,alphaMax,premultMax,premultSum,visiblePixels};};
    results.push({facing,directVsOriginalCrop:detail(arrays[0],arrays[1]),originalCropVsRuntime:detail(arrays[1],arrays[2])});
}
return {results,image:strip.canvas.toDataURL('image/png')};
'''

REPLAY_SETUP = r'''
dismissTitle();window.requestAnimationFrame=()=>0;
window.probeClock=10000;
Object.defineProperty(performance,'now',{configurable:true,value:()=>probeClock});
Date.now=()=>1800000000000+probeClock;
window.probeSeed=1;
Math.random=()=>{probeSeed=(Math.imul(1664525,probeSeed)+1013904223)>>>0;return probeSeed/4294967296;};
window.probeKey=(code,down)=>window.dispatchEvent(new KeyboardEvent(down?'keydown':'keyup',{code,bubbles:true}));
window.probeSnapshot=p=>({name:p.spec.name,x:p.x,y:p.y,vx:p.vx,vy:p.vy,hp:p.hp,stamina:p.stamina,
    state:p.state,grounded:p.isGrounded,facing:p.facing,recovery:p.recoveryTimer,attackT:p.attackT,
    attackDir:p.attackDir,attackAir:p.attackAir,drawCell:p.drawCell,hurtbox:p.hurtbox(),
    hitboxes:p.hitboxes.map(h=>({ox:h.ox,oy:h.oy,w:h.w,h:h.h,delay:h.delay,life:h.life,damage:h.damage,low:h.low,launch:h.launch,spike:h.spike}))});
return NINJA_ROSTER.filter(n=>!n.benched).map(n=>({id:n.id,name:n.name}));
'''

REPLAY = r'''
probeSeed=123456;probeClock=10000;animClock=0;
gameMode='2p';cpuMode=false;spectate=false;p1Pick=ID;p2Pick=ID===0?4:0;stagePick='bamboo';
startNewGame();cutscene=null;roundIntroTimer=0;hitstopEase=0;paused=false;releaseAllKeys();
document.getElementById('pause-screen').classList.add('hidden');
for(const p of [player1,player2]){p.y=GROUND_Y-p.height;p.isGrounded=true;p.vy=0;}
player1.x=220;player2.x=475;lastTime=probeClock;
const sheet=document.createElement('canvas');sheet.width=1440;sheet.height=540;
const film=sheet.getContext('2d'),states=[],samples=[];
const captures=[0,12,24,36,48,64,80,100,128,150,180,220];
const press=code=>{probeKey(code,true);probeKey(code,false);};
for(let frame=0;frame<240;frame++){
    probeClock=10000+(frame+1)*1000/60;
    if(frame===0)probeKey('KeyD',true);
    if(frame===24)probeKey('KeyD',false);
    if(frame===36)press('KeyF');
    if(frame===64)press('KeyG');
    if(frame===100)press('KeyH');
    if(frame===150)probeKey('KeyW',true);
    if(frame===158)probeKey('KeyW',false);
    if(frame===180)press('KeyJ');
    gameLoop(probeClock);
    states.push({frame,clock:roundTimer,anim:animClock,hitstop:hitstopRemaining,
        fighters:[probeSnapshot(player1),probeSnapshot(player2)]});
    const shot=captures.indexOf(frame);
    if(shot>=0){
        const col=shot%6,row=Math.floor(shot/6),fit=Math.min(240/canvas.width,246/canvas.height);
        const width=canvas.width*fit,height=canvas.height*fit;
        film.fillStyle='#10151f';film.fillRect(col*240,row*270,240,270);
        film.drawImage(canvas,0,0,canvas.width,canvas.height,col*240+(240-width)/2,row*270+(246-height)/2,width,height);
        film.fillStyle='#10151f';film.fillRect(col*240,row*270+246,240,24);film.fillStyle='white';film.font='12px sans-serif';
        film.fillText(player1.spec.name+' · frame '+frame,col*240+7,row*270+262);
        samples.push({frame,cell:player1.drawCell,state:player1.state});
    }
}
paused=true;
return {name:player1.spec.name,states,samples,filmstrip:sheet.toDataURL('image/png')};
'''


def oracle_source(baseline):
    start = baseline.index('function keyedShodoCell(')
    end = baseline.index('// The INK box of one cell', start)
    functions = baseline[start:end]
    return ('(()=>{const shodoCellCache=new Map(),shodoFrameCache=new Map();' + functions
            + ';return {keyedShodoCell,drawShodoFrame,clear(){shodoCellCache.clear();shodoFrameCache.clear();}};})()')


async def run_variant(label, out, baseline, compare_cells, pixels_only=False, raw_probe=False):
    with socket.socket() as sock:
        if sock.connect_ex(('127.0.0.1', 9395)) == 0:
            raise RuntimeError('Debug port 9395 is occupied; refusing to attach to another run')
    browser.PORT = 9395
    with tempfile.TemporaryDirectory(prefix='runtime-sprite-check-') as profile:
        proc, address = browser.launch(URL, profile)
        try:
            async with websockets.connect(address, max_size=48*1024*1024) as ws:
                c = Probe(ws, baseline if label == 'baseline' else None)
                await c.send('Runtime.enable')
                if label == 'baseline':
                    await c.send('Fetch.enable', patterns=[{'urlPattern': '*index.html*', 'resourceType': 'Document'}])
                    await c.send('Page.reload', ignoreCache=True)
                for _ in range(600):
                    if await c.checked("return typeof SPRITES!=='undefined'&&NINJA_ROSTER.filter(n=>!n.benched).every(n=>SPRITES[n.name.toLowerCase()]?.ready)"):
                        break
                    await asyncio.sleep(.1)
                else:
                    raise RuntimeError(label + ' roster never became ready')
                cells = []
                if compare_cells:
                    names = await c.checked(ORACLE_SETUP.replace('ORACLE', oracle_source(baseline)))
                    if raw_probe:
                        await c.checked(CELL_SETUP.replace('NAME',json.dumps('shin')))
                        result=await c.checked(RAW_PROBE)
                        (out/'raw-source-paired.png').write_bytes(base64.b64decode(result.pop('image').split(',',1)[1]))
                        (out/'raw-source-paired.json').write_text(json.dumps(result,indent=2)+'\n')
                        print(json.dumps(result,indent=2),flush=True)
                        return result
                    for name in names:
                        info = await c.checked(CELL_SETUP.replace('NAME', json.dumps(name)))
                        counts = dict(raw=0, keyed=0, outlined=0, wire=0, failures=[])
                        for start in range(0, info['cols'], 24):
                            part = await c.checked(CELL_BATCH.replace('START', str(start)).replace('END', str(min(start+24, info['cols']))))
                            for kind in ('raw', 'keyed', 'outlined', 'wire'):
                                counts[kind] += part[kind]
                            counts['failures'].extend(part['failures'])
                            if part['failures']:
                                failure={'fighter':name,'start':start,'failures':part['failures']}
                                (out/'pixels-first-failure.json').write_text(json.dumps(failure,indent=2)+'\n')
                                print(json.dumps(failure),flush=True)
                                raise RuntimeError('Pixel mismatch; stopped before continuing the exhaustive run')
                        cells.append({**info, **counts})
                        print(f"{name}: {counts['raw']} raw, {counts['keyed']} keyed, {counts['outlined']} outlined, {counts['wire']} wire; {len(counts['failures'])} mismatches", flush=True)
                        await c.checked("runtimeComparison.original.close();runtimeComparison.originalImage.src='';runtimeComparison={};return true")
                    (out/'pixels.json').write_text(json.dumps(cells, indent=2)+'\n')
                if pixels_only:
                    return {'cells':cells,'replays':[],'browserErrors':c.errors}
                roster = await c.checked(REPLAY_SETUP)
                replays = []
                for fighter in roster:
                    result = await c.checked(REPLAY.replace('ID', str(fighter['id'])))
                    film = result.pop('filmstrip')
                    (out/f"{label}-{fighter['name'].lower()}-filmstrip.png").write_bytes(base64.b64decode(film.split(',', 1)[1]))
                    replays.append(result)
                    print(f"{label}: {fighter['name']} 240 real-loop frames captured", flush=True)
                (out/f'{label}-replays.json').write_text(json.dumps(replays, indent=2)+'\n')
                return {'cells': cells, 'replays': replays, 'browserErrors': c.errors}
        finally:
            proc.terminate()
            try:
                proc.wait(timeout=10)
            except subprocess.TimeoutExpired:
                proc.kill();proc.wait()


async def main(args):
    browser.assert_serving_this_tree(URL)
    args.out.mkdir(parents=True, exist_ok=True)
    baseline = args.baseline.read_text()
    source_hash = hashlib.sha256((ROOT/'web/index.html').read_bytes()).hexdigest()
    if args.replays_only:
        prior=json.loads((args.out/'result.json').read_text())
        if prior['candidateSHA256']!=source_hash or prior['baselineSHA256']!=hashlib.sha256(baseline.encode()).hexdigest():
            raise RuntimeError('Cannot reuse pixel oracle: source versions changed')
    after = await run_variant('candidate', args.out, baseline, not args.replays_only, args.pixels_only, args.raw_probe)
    if args.pixels_only or args.raw_probe:
        return
    if args.replays_only:
        after['cells']=json.loads((args.out/'pixels.json').read_text())
    before = await run_variant('baseline', args.out, baseline, False)
    diffs = []
    for a, b in zip(before['replays'], after['replays']):
        for x, y in zip(a['states'], b['states']):
            if x != y:
                diffs.append({'name': a['name'], 'frame': x['frame'], 'before': x, 'after': y})
    failures = sum(len(row['failures']) for row in after['cells'])
    summary = {'baselineSHA256': hashlib.sha256(baseline.encode()).hexdigest(), 'candidateSHA256': source_hash,
               'reusedPixelOracleForIdenticalSource': args.replays_only,
               'sourceUnchangedDuringCheck': source_hash == hashlib.sha256((ROOT/'web/index.html').read_bytes()).hexdigest(),
               'cellComparisons': {k: sum(row[k] for row in after['cells']) for k in ('raw','keyed','outlined','wire')},
               'pixelFailures': failures, 'combatFrames': sum(len(r['states']) for r in after['replays']),
               'combatDifferences': diffs, 'browserErrors': {'baseline': before['browserErrors'], 'candidate': after['browserErrors']}}
    (args.out/'result.json').write_text(json.dumps(summary, indent=2)+'\n')
    print(json.dumps({k:v for k,v in summary.items() if k not in ('combatDifferences','browserErrors')}, indent=2))
    print(f'Combat differences: {len(diffs)}', flush=True)
    if failures or diffs or not summary['sourceUnchangedDuringCheck'] or before['browserErrors'] or after['browserErrors']:
        raise SystemExit(1)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--baseline', type=Path, required=True)
    parser.add_argument('--out', type=Path, required=True)
    parser.add_argument('--pixels-only', action='store_true')
    parser.add_argument('--raw-probe', action='store_true')
    parser.add_argument('--replays-only', action='store_true', help='Reuse saved pixel oracle only when both source hashes match')
    asyncio.run(main(parser.parse_args()))
