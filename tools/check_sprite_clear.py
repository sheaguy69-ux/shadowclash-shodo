#!/usr/bin/env python3
"""Verify reviewed sprite holes in the real :9101 keyer; capture outlined comparisons.

--before disables frameClear only inside the isolated browser to reproduce the defect.
"""
import asyncio
import base64
import json
import os
from pathlib import Path
import sys
import tempfile

import websockets
import watch_game as browser


async def main():
    url = os.environ.get('SHADOWCLASH_URL', 'http://localhost:9101/index.html')
    browser.assert_serving_this_tree(url)
    out = Path(os.environ.get('OUT', 'media/negative-space-20260906/runtime'))
    out.mkdir(parents=True, exist_ok=True)
    failures, results = [], []
    with tempfile.TemporaryDirectory(prefix='sprite-clear-') as profile:
        proc, address = browser.launch(url, profile)
        try:
            async with websockets.connect(address, max_size=32 * 1024 * 1024) as ws:
                cdp = browser.CDP(ws)
                for _ in range(400):
                    if await cdp.js("return typeof NINJA_ROSTER !== 'undefined' && NINJA_ROSTER.every(s=>SPRITES[s.name.toLowerCase()]?.ready)") is True:
                        break
                    await asyncio.sleep(0.1)
                else:
                    raise RuntimeError('roster did not load')
                await cdp.js("paused=true;window.clearBefore=" + str('--before' in sys.argv).lower())
                names = await cdp.js('return NINJA_ROSTER.map(s=>s.name.toLowerCase())')
                for name in names:
                    result = await cdp.js('const name=' + json.dumps(name) + r""";
                    const m=SPRITES[name],w=m.frameW,h=m.frameH,cells=[...new Set(Object.values(m.frames))];
                    const errors=[],declared=m.frameClear??{},raw=document.createElement('canvas');
                    raw.width=w;raw.height=h;const g=raw.getContext('2d',{willReadFrequently:true});
                    if(clearBefore)m.img.shodoClearRects={};
                    shodoCellCache.clear();shodoFrameCache.clear();
                    let cleared=0,changed=0;
                    for(const cell of cells){
                        const mask=new Uint8Array(w*h),rects=declared[cell]??[];
                        for(const [x,y,rw,rh] of rects){
                            if(![x,y,rw,rh].every(Number.isInteger)||x<0||y<0||rw<=0||rh<=0||x+rw>w||y+rh>h)
                                throw new Error(name+' invalid cleanup rectangle '+cell);
                            for(let yy=y;yy<y+rh;yy++)mask.fill(1,yy*w+x,yy*w+x+rw);
                        }
                        g.clearRect(0,0,w,h);g.drawImage(m.img,cell*w,0,w,h,0,0,w,h);
                        const a=g.getImageData(0,0,w,h).data;
                        const b=keyedShodoCell(m.img,cell*w,0,w,h).getContext('2d').getImageData(0,0,w,h).data;
                        let erased=0,retained=0,bad=0;
                        for(let p=0;p<w*h;p++){
                            const i=p*4;
                            if(mask[p]){if(b[i+3])bad++;if(a[i+3])erased++;}
                            else{if(a[i+3])retained++;for(let k=0;k<4;k++)if(a[i+k]!==b[i+k]){bad++;break;}}
                        }
                        if(bad)errors.push(cell+': '+bad+' pixels disagree with reviewed cleanup');
                        if(!retained)errors.push(cell+': empty body');
                        if(rects.length){changed++;cleared+=erased;if(!erased)errors.push(cell+': cleanup selects no source pixels');}
                    }
                    if(!changed)errors.push('no reviewed cleanup loaded');
                    // Source-scale comparisons use the same outlined renderer as body/copies.
                    const examples=Object.keys(declared).map(Number).slice(0,12),c=document.createElement('canvas');
                    c.width=1200;c.height=Math.ceil(examples.length/3)*300;const cg=c.getContext('2d');
                    cg.fillStyle='#81bcc5';cg.fillRect(0,0,c.width,c.height);
                    examples.forEach((cell,j)=>{
                        const x=j%3*400,y=Math.floor(j/3)*300,s=Math.min(190/w,260/h);
                        for(let side=0;side<2;side++){
                            m.img.shodoClearRects=side?declared:{};shodoCellCache.clear();shodoFrameCache.clear();
                            drawShodoFrame(cg,m.img,cell*w,0,w,h,x+side*200,y+30,w*s,h*s);
                        }
                        cg.fillStyle='#111';cg.font='13px sans-serif';cg.fillText(name+' '+cell+' / before | after',x+5,y+17);
                    });
                    m.img.shodoClearRects=declared;shodoCellCache.clear();shodoFrameCache.clear();
                    return {name,cells:cells.length,changed,cleared,errors,png:c.toDataURL().split(',')[1]};
                    """)
                    (out / f'{name}.png').write_bytes(base64.b64decode(result.pop('png')))
                    failures.extend(f'{name}: {e}' for e in result['errors'])
                    results.append(result)
                    print(json.dumps(result), flush=True)
        finally:
            proc.terminate()
            proc.wait(timeout=10)
    (out / 'checks.json').write_text(json.dumps(results, indent=2) + '\n')
    if failures:
        raise SystemExit('\n'.join(failures[:30]))
    print(f'PASS: {sum(r["cells"] for r in results)} active cells; '
          f'{sum(r["changed"] for r in results)} cleaned; outside pixels preserved')


if __name__ == '__main__':
    asyncio.run(main())
