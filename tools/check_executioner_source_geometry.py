#!/usr/bin/env python3
"""Compare the staged original-source repair with776; --served checks installed code/assets.

Uses the existing real-key exporter at60Hz game-time boundaries. All four requested
routes run center/left/right whiffs and center hit/block, both faces, cold/warm caches.
The saved776 functions and original manifest are the baseline; original cells remain
inside the appended sheet. Only observed visual cell remaps and neutral slashes may differ.
"""
import argparse
import asyncio
import base64
import hashlib
import importlib.util
import json
import tempfile
from pathlib import Path

import watch_game as browser
import websockets
from audit_roster_footsies import capture_script
from export_footsies_frames import validate

ROOT = Path(__file__).resolve().parents[1]
HERE = ROOT / 'media/weapon-readability-20260909/executioner/source-recovery'
BASE = HERE / 'qa/baseline-source-geometry.json'
MAP = {351: 82, 352: 85, 353: 86, 354: 261}


def replace_once(code, old, new):
    assert code.count(old) == 1, old
    return code.replace(old, new)


def script():
    code = capture_script()
    code = replace_once(code, "x:face>0?450:canvas.width-450-p.width", "x:options.edge==='left'?0:options.edge==='right'?canvas.width-p.width:canvas.width/2-p.width/2")
    code = replace_once(code, "x:p.x+face*(options.scenario==='whiff'?300:55)", "x:options.scenario==='whiff'?(p.x<canvas.width/2?canvas.width-50:20):p.x+face*55")
    code = replace_once(code, 'frames.push({frame_index:', '''const pose=combatPose(p),source=man.combatSource?.[pose.idx]??pose.idx;
  frames.push({combat_pose:{idx:pose.idx,S:pose.S,sign:pose.sign,originX:pose.originX,originY:pose.originY,shiftX:pose.shiftX,bodyHeight:pose.bodyHeight,body:pose.body,core:man.hurtCore?.get(source)},
   strike_cells:p.hitboxes.map(h=>h.strikeCell??null),strike_fits:[...(man.strikeFits??[])],
   particles:particles.map(q=>Object.fromEntries(Object.entries(q).filter(([k,v])=>v===null||['string','boolean','number'].includes(typeof v)))),
   slashes:slashes.map(s=>({heavy:s.heavy,x:s.x,y:s.y,facing:s.facing,r:s.r,life:s.life,maxLife:s.maxLife})),frame_index:''')
    # Preserve drawSprite and its actual transform checks; omit image export and the
    # redundant scene redraw. This check produces records, not a new visual approval.
    start = code.index("  t.fillStyle='#e8e3d9'")
    end = code.index("  if(['light','medium','heavy','special']", start)
    code = code[:start] + code[end:]
    code = replace_once(code, "scene_filmstrip:options.move==='special'?sceneStrip.toDataURL().split(',')[1]:null,filmstrip:strip.toDataURL().split(',')[1]", "scene_filmstrip:null,filmstrip:null")
    return code


def normalized(value, key=None):
    if isinstance(value, dict):
        return {k: normalized(v, k) for k, v in value.items()}
    if isinstance(value, list):
        if key in ('cells', 'strike_cells'):
            return [MAP.get(v, v) for v in value]
        return [normalized(v) for v in value]
    return MAP.get(value, value) if key in ('cell', 'idx', 'strikeCell') else value


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def renderer_script():
    """Reuse the775 shared-buffer source/mask/cache ruler without duplicating it."""
    path = HERE.parents[1]/'check_render_regions.py'
    spec = importlib.util.spec_from_file_location('executioner_source_renderer', path)
    qa = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(qa)
    code = qa.CHECK.replace('__BASELINE_DRAW__', (qa.OUT/'original-draw-shodo-frame.js').read_text().strip())
    for old, new in {
        'Object.keys(SPRITES.tsubasa.img.shodoWeaponRegions??{})': 'Object.keys(SPRITES.executioner.img.shodoWeaponRegions??{})',
        "[['tsubasa',[...new Set([...declared,370,235])].sort((a,b)=>a-b)],['executioner',[296]]]": "[['executioner',[...new Set([...declared,65,71,81,82,85,86,261,296])].sort((a,b)=>a-b)]]",
        'p1Pick=3;p2Pick=0;': 'p1Pick=0;p2Pick=1;',
        'cells370/235 and wide Executioner296 are untouched controls': 'sheathed65/71/81, retained originals82/85/86/261 and wide Drive296 are untouched controls',
    }.items():
        code = replace_once(code, old, new)
    return code


async def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--served', action='store_true')
    parser.add_argument('--renderer-only', action='store_true', help='Only the final source/mask/renderer invariant checks, preserving the earlier move records.')
    parser.add_argument('--fx', type=Path, default=ROOT/'media/executioner-next-20260909/neutral-remap/neutral-preview.js')
    args = parser.parse_args()
    args.fx = args.fx.resolve()
    baseline = json.loads(BASE.read_text())
    inputs = [ROOT/'web/index.html', ROOT/'web/assets/sprites/executioner.png', ROOT/'web/assets/sprites/executioner.json', BASE,
        HERE.parents[1]/'qa/original-draw-shodo-frame.js']
    if not args.served:
        inputs += [HERE/'executioner-proposed.png', HERE/'executioner-preserved.json', HERE/'geometry-preview.js', args.fx]
    hashes = {str(p.relative_to(ROOT)): digest(p) for p in inputs}
    out = HERE/'qa'/('served-preserved-' if args.served else 'preview-preserved-')
    out = out.with_name(out.name + hashes['web/index.html'][:8])
    if args.renderer_only:
        out = out.with_name(out.name + '-renderer')
    out.mkdir(parents=True, exist_ok=True)
    variants = 'window.sourceGeometryQA={candidate:{man:SPRITES.executioner,pose:combatPose,strike:refreshStrikeGeometry,spawn:spawnSlash}};return true;'
    functions = baseline['functions']
    setup = 'const baselineManifest=' + json.dumps(baseline['manifest']) + ';\n'
    setup += 'const funcs={pose:(' + functions['pose'] + '),strike:(' + functions['strike'] + '),spawn:(' + functions['spawn'] + ')};\n'
    setup += r'''
const api=sourceGeometryQA;
api.original={man:{...baselineManifest,img:api.candidate.man.img,ready:true},...funcs};
api.select=(variant,cold)=>{
 const q=api[variant];SPRITES.executioner=q.man;combatPose=q.pose;refreshStrikeGeometry=q.strike;spawnSlash=q.spawn;
 if(cold){shodoCellCache.clear();shodoFrameCache.clear();inkBoxCache.clear();q.man.hurtCore?.clear();q.man.strikeFits?.clear();}
};
for(const [to,from] of Object.entries(api.candidate.man.combatSource??{})){
 for(const field of ['frameScale','footAdj','mirror','frameOffsetX','frameClear','wallContactX','handAnchor'])
  if(JSON.stringify(api.candidate.man[field]?.[to])!==JSON.stringify(api.candidate.man[field]?.[from]))throw Error('registration metadata mismatch '+field+'/'+to);
}
if(JSON.stringify(api.candidate.man.combatSource)!==JSON.stringify({'351':82,'352':85,'353':86,'354':261}))throw Error('missing reviewed combatSource');
return true;
'''
    browser.PORT = 9397
    url = 'http://localhost:9101/index.html'
    browser.assert_serving_this_tree(url)
    cases, failures, seen = [], [], set()
    code = script()
    with tempfile.TemporaryDirectory(prefix='executioner-source-geometry-') as profile:
        proc, address = browser.launch(url, profile)
        try:
            async with websockets.connect(address, max_size=100_000_000) as ws:
                c = browser.CDP(ws)
                for _ in range(400):
                    if await c.js("return typeof SPRITES!=='undefined'&&FX_CRESCENT.ready&&NINJA_ROSTER.every(s=>SPRITES[s.name.toLowerCase()]?.ready)") is True:
                        break
                    await asyncio.sleep(.1)
                else:
                    raise RuntimeError('roster did not load')
                if not args.served:
                    load = 'const proposedManifest=' + (HERE/'executioner-preserved.json').read_text() + ';const proposedBase64=' + json.dumps(base64.b64encode((HERE/'executioner-proposed.png').read_bytes()).decode()) + ';\n'
                    load += (HERE/'install_appended_preview.js').read_text()
                    result = await c.js(load)
                    assert result and '__error' not in result, result
                    assert await c.js('executionerAppendedPreview.enabled=true;return true;') is True
                    result = await c.js((HERE/'geometry-preview.js').read_text())
                    assert result.get('combatSourceReady'), result
                    result = await c.js(args.fx.read_text())
                    assert result is True, result
                    assert await c.js('executionerNeutralPreview.enabled=true;return true;') is True
                assert await c.js(variants) is True
                assert await c.js(setup) is True
                routes = [] if args.renderer_only else [('heavy','neutral'),('heavy','back'),('heavy','down'),('light','neutral')]
                for move, direction in routes:
                    for face in (-1, 1):
                        for edge, scenario in [('center','whiff'),('left','whiff'),('right','whiff'),('center','hit'),('center','block')]:
                            first = None
                            for cache in ('cold', 'warm'):
                                options = dict(fighter=0, move=move, direction=direction, facing=face, scenario=scenario, edge=edge, airborne=False, frames=90)
                                tag = f'{move}-{direction}-{face}-{edge}-{scenario}-{cache}'
                                pair = []
                                for variant in ('original','candidate'):
                                    prefix = 'sourceGeometryQA.select('+json.dumps(variant)+','+str(cache=='cold').lower()+');AudioSys.unlock();AudioSys.muted=true;animClock=0;let seed=17;Math.random=()=>((seed=(seed*1664525+1013904223)>>>0)/4294967296);const options='+json.dumps(options)+';'
                                    data = await c.js(prefix + code)
                                    assert isinstance(data, dict) and '__error' not in data, data
                                    validate(data)
                                    for f in data['frames']:
                                        if variant == 'candidate':
                                            seen.add(f['cell'])
                                    data.pop('filmstrip'); data.pop('scene_filmstrip')
                                    pair.append(data)
                                assert len(pair[0]['frames']) == len(pair[1]['frames']), tag
                                slash_frames = []
                                for old, new in zip(pair[0]['frames'], pair[1]['frames']):
                                    a, b = normalized(old), normalized(new)
                                    oldslashes, newslashes = a.pop('slashes'), b.pop('slashes')
                                    if oldslashes != newslashes:
                                        slash_frames.append(old['frame_index'])
                                        if (move,direction)!=('heavy','neutral') or newslashes:
                                            failures.append({'case':tag,'frame':old['frame_index'],'field':'unexpected slash change'})
                                    for key in a:
                                        if a[key] != b[key]:
                                            failures.append({'case':tag,'frame':old['frame_index'],'field':key,'before':a[key],'after':b[key]})
                                if (move,direction)==('heavy','neutral') and not slash_frames:
                                    failures.append({'case':tag,'field':'neutral suppression never observed'})
                                # Warm results must match the cold timeline, excluding cache
                                # inventory (which deliberately retains additional fit entries).
                                comparable = [[{k:v for k,v in f.items() if k!='strike_fits'} for f in d['frames']] for d in pair]
                                if first is None:
                                    first = comparable
                                elif first != comparable:
                                    failures.append({'case':tag,'field':'cold/warm timeline differs'})
                                row = dict(case=tag, frames_per_variant=len(pair[0]['frames']), slash_frames=slash_frames,
                                    contacts=[f['frame_index'] for f in pair[1]['frames'] if f['contacts']],
                                    damage=sum(f['defender']['damage_delta'] for f in pair[1]['frames']),
                                    cells=list(dict.fromkeys(f['cell'] for f in pair[1]['frames'])))
                                cases.append(row)
                                (out/(tag+'.json')).write_text(json.dumps({'options':options,'current':pair[0]['frames'],'candidate':pair[1]['frames']}, separators=(',',':'), allow_nan=False))
                            print(move,direction,face,edge,scenario,'paired cold/warm complete',flush=True)
                await c.js('sourceGeometryQA.select("candidate",false);paused=true;releaseAllKeys();return true;')
                renderer = await c.js(renderer_script())
                assert isinstance(renderer, dict) and '__error' not in renderer, renderer
                failures += [{'field':'renderer','detail':failure} for failure in renderer['failures']]
                for row in renderer['rows']:
                    for key in ('before','after'):
                        filename = f'renderer-{row["cell"]}-{row["face"]}-{key}.png'
                        (out/filename).write_bytes(base64.b64decode(row.pop(key).split(',')[1]))
                        row[key] = filename
                (out/'renderer-result.json').write_text(json.dumps(renderer,indent=2,allow_nan=False))
        finally:
            proc.terminate(); proc.wait(timeout=10)
    assert hashes == {str(p.relative_to(ROOT)): digest(p) for p in inputs}, 'audited inputs changed during check'
    browser.assert_serving_this_tree(url, 'after Executioner source geometry check')
    if not args.renderer_only and not set(MAP).issubset(seen):
        failures.append({'field':'appended cells not all reached','missing':sorted(set(MAP)-seen)})
    result = dict(hashes=hashes,served=args.served,baseline_html_sha256=baseline['source_sha256'],unchanged_inputs=True,
        paired_cases=len(cases),records=sum(2*r['frames_per_variant'] for r in cases),cases=cases,failures=failures,
        renderer_comparisons=len(renderer['rows']),renderer_geometry_samples=len(renderer['geometry']),
        timing='Existing exporter real-key60Hz game-time sampling; cinematic crawl not remeasured.',
        scope='Rendering/pose/body/hurtbox/contact/probes/particles/timing and cold/warm caches; authored cell indices normalized only for comparison. No new visual score.')
    (out/'result.json').write_text(json.dumps(result,indent=2,allow_nan=False))
    print('PASS' if not failures else 'FAIL',len(cases),'paired cases;',result['records'],'records;',len(renderer['rows']),
        'renderer comparisons;',len(renderer['geometry']),'render/geometry samples;',len(failures),'failures',flush=True)
    assert not failures, str(failures[:3])


if __name__ == '__main__':
    asyncio.run(main())
