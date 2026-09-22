#!/usr/bin/env python3
"""Real input check for grounded Up+Heavy access; optional candidate stays in browser memory."""
import argparse
import asyncio
import hashlib
import json
import os
import tempfile
from pathlib import Path

import websockets
import watch_game as browser

ROOT = Path(__file__).resolve().parents[1]
JS = r'''
dismissTitle(); const rows=[], failures=[];
const key=(code,down=true)=>window.dispatchEvent(new KeyboardEvent(down?'keydown':'keyup',{code,bubbles:true}));
const step=(n=1)=>{for(let i=0;i<n;i++){hitstopRemaining=0;updateGame(1/(60*COMBAT_TEMPO));}};
const reset=(id,seat=0,facing=1)=>{
    releaseAllKeys(); gameMode='2p';cpuMode=false;spectate=false;stagePick='bamboo';
    p1Pick=seat?0:id;p2Pick=seat?id:(id===0?1:0);startNewGame();
    paused=false;roundIntroTimer=0;hitstopRemaining=0;cutscene=null;
    for(const id of MENU_IDS)document.getElementById(id)?.classList.add('hidden');
    const p=seat?player2:player1,foe=seat?player1:player2;
    Object.assign(p,{x:facing===1?150:canvas.width-150-p.width,y:GROUND_Y-p.height,
      vx:0,vy:0,state:STATE.IDLE,isGrounded:true,jumpsLeft:2,facing});
    Object.assign(foe,{x:facing===1?canvas.width-80-foe.width:80,y:GROUND_Y-foe.height,
      vx:0,vy:0,isGrounded:true,facing:-facing});
    return p;
};
const snap=p=>({state:p.state,ground:p.isGrounded,air:p.attackAir,dir:p.attackDir,
    art:p.moveArt||null,dur:p.attackAnim?.dur||0,recovery:p.recoveryTimer,
    x:p.x,y:p.y,vx:p.vx,vy:p.vy,jumps:p.jumpsLeft,buffer:p.jumpBufferTimer,
    stamina:p.stamina,hanbo:p.hanbo,kageNui:p.kageNui,sakate:p.sakate,throwTimer:p.throwTimer,throwAir:p.throwAir,
    flags:['gyakuAnim','upAtkAnim','highParryAnim','airHurlAnim','slamPhase'].filter(k=>p[k]),
    boxes:p.hitboxes.map(h=>({w:h.w,h:h.h,ox:h.ox,oy:h.oy,damage:h.damage,delay:h.delay,
      duration:h.duration,push:h.pushback,launch:h.launch,launchVy:h.launchVy}))});
const record=(id,seat,facing,mode,p,extra={})=>rows.push({id,seat,facing,mode,...extra,value:snap(p)});
for(let id=0;id<9;id++)for(const seat of [0,1])for(const facing of [1,-1]){
    const up=seat?'ArrowUp':'KeyW',heavy=seat?'KeyO':'KeyG';
    // Reference ground command: Up held through the existing listeners after an
    // ordinary landing. Heavy must equal this already-implemented move.
    let p=reset(id,seat,facing);key(up);step(75);key(heavy);
    record(id,seat,facing,'ground-reference',p);
    for(const delay of [0,1,2,3,8]){
        p=reset(id,seat,facing);const origin=p.y;key(up);step(delay);const beforeY=p.y;
        key(heavy);record(id,seat,facing,'chord-'+delay,p,{rewind:p.y-beforeY,origin});
        key(up,false);key(heavy,false);const initial=snap(p);step(75);
        record(id,seat,facing,'released-'+delay,p,{initial});
    }
    p=reset(id,seat,facing);key(up);step();key(heavy);key(heavy,false);step(75);
    record(id,seat,facing,'held-up',p);
    for(const mode of ['jump-full','jump-tap','double','wall','expired','released-up']){
        p=reset(id,seat,facing);const origin=p.y;key(up);
        if(mode==='jump-tap')key(up,false);
        if(mode==='double'){key(up,false);step();key(up);key(heavy);}
        if(mode==='wall'){
            key(up,false);Object.assign(p,{wallDir:facing,y:GROUND_Y-p.height-180,isGrounded:false});
            key(up);key(heavy);
        }
        if(mode==='expired'){step(4);key(heavy);}
        if(mode==='released-up'){key(up,false);key(heavy);}
        const trace=[];for(let n=0;n<75;n++){trace.push(snap(p));step();}
        record(id,seat,facing,mode,p,{trace,origin});
    }
}
for(const [id,stance] of [[1,'hanbo'],[2,'kageNui'],[3,'sakate']])for(const seat of [0,1])for(const facing of [1,-1]){
    const up=seat?'ArrowUp':'KeyW',heavy=seat?'KeyO':'KeyG';
    for(const mode of ['reference','chord','late']){
        const p=reset(id,seat,facing);p[stance]=true;key(up);step(mode==='reference'?75:mode==='late'?4:1);key(heavy);
        record(id,seat,facing,'stance-'+stance+'-'+mode,p);
    }
}
for(const id of [1,2,3,8])for(const seat of [0,1]){
    const up=seat?'ArrowUp':'KeyW',heavy=seat?'KeyO':'KeyG';
    // A touch pad uses virtual held keys and the same combat funnel.
    let p=reset(id,seat),pad=document.getElementById(seat?'pad-p2':'pad-p1');
    const target=pad.querySelector('[data-dir="up"]'),oldPoint=document.elementFromPoint;
    const touch=new Touch({identifier:91,target,clientX:0,clientY:0});
    try{
        document.elementFromPoint=()=>target;
        pad.dispatchEvent(new TouchEvent('touchstart',{changedTouches:[touch],touches:[touch],bubbles:true,cancelable:true}));
        step();const button=document.getElementById(seat?'btn-t-p2-heavy':'btn-t-p1-heavy');
        button.dispatchEvent(new TouchEvent('touchstart',{changedTouches:[touch],touches:[touch],bubbles:true,cancelable:true}));
        record(id,seat,1,'touch',p);
        button.dispatchEvent(new TouchEvent('touchend',{changedTouches:[touch],touches:[],bubbles:true,cancelable:true}));
        pad.dispatchEvent(new TouchEvent('touchend',{changedTouches:[touch],touches:[],bubbles:true,cancelable:true}));
    }finally{document.elementFromPoint=oldPoint;}
    // Releasing, interrupting or resetting cannot leave a reusable takeoff latch.
    for(const mode of ['hit','reset','second','support-lost','platform']){
        p=reset(id,seat);const foe=seat?player1:player2;
        let platform;
        if(mode==='platform'){platform={x:p.x-20,y:GROUND_Y-100,w:p.width+80,h:8};PLATFORMS.push(platform);p.y=platform.y-p.height;}
        key(up);step();
        if(mode==='hit'){
            p.takeDamage(2,foe,0,{tier:STATE.ATTACK_LIGHT});
            if(p.groundJumpStart)failures.push(id+' '+seat+' hit retained takeoff');
        }
        if(mode==='reset'){
            trainingReset(false);
            if(p.groundJumpStart)failures.push(id+' '+seat+' reset retained takeoff');
        }
        if(mode==='second'){key(up,false);key(up);}
        if(mode==='support-lost'){currentStage={...currentStage,abyss:true};abyssSlabs=[];}
        key(heavy);record(id,seat,1,mode,p);
    }
}
// A same-poll controller direction must be visible to every attack strength,
// including reversal of a previously held horizontal direction.
const originalPads=navigator.getGamepads;
try{
  for(const seat of [0,1])for(const dir of ['up','down','left','right'])for(const button of [0,1,2,3]){
    const map=PAD_KEYS[seat];let p=reset(3,seat);
    key(map[dir]);key(map[PAD_BUTTONS[button]]);const keyboard=snap(p);
    p=reset(3,seat);const make=(bs=[])=>({connected:true,mapping:'standard',axes:[0,0],buttons:Array.from({length:16},(_,i)=>({pressed:bs.includes(i)}))});
    let pads=[make(),make()];Object.defineProperty(navigator,'getGamepads',{configurable:true,value:()=>pads});
    pollGamepads();const d={up:12,down:13,left:14,right:15}[dir];pads[seat]=make([d,button]);pollGamepads();
    record(3,seat,1,'pad-'+dir+'-'+button,p,{keyboard});
    const a=p.attackAnim;pollGamepads();if(p.attackAnim!==a)failures.push('pad hold repeated '+dir+' '+button);
    pads[seat]=make();pollGamepads();
  }
  for(const id of [3,7])for(const seat of [0,1]){
    const map=PAD_KEYS[seat];const near=p=>{const foe=seat?player1:player2;foe.x=p.x+p.width+5;};
    let p=reset(id,seat);near(p);key(map.up);key(map.light);key(map.heavy);const keyboard=snap(p);
    p=reset(id,seat);near(p);const make=(bs=[])=>({connected:true,mapping:'standard',axes:[0,0],buttons:Array.from({length:16},(_,i)=>({pressed:bs.includes(i)}))});
    let pads=[make(),make()];Object.defineProperty(navigator,'getGamepads',{configurable:true,value:()=>pads});pollGamepads();
    pads[seat]=make([12,6]);pollGamepads();record(id,seat,1,'pad-up-throw',p,{keyboard});
    pads[seat]=make();pollGamepads();
  }
}finally{Object.defineProperty(navigator,'getGamepads',{configurable:true,value:originalPads});}
paused=true;releaseAllKeys();return {rows,failures};
'''


def inject(html):
    def block(start, end):
        a = html.index(start)
        return html[a:html.index(end, a) + len(end)]
    return '\n'.join([
        'Player = (' + block('class Player {', '\n        }') + ');',
        'pollGamepads = (' + block('function pollGamepads()', '\n        }') + ');',
        'trainingReset = (' + block('function trainingReset(', '\n        }') + ');',
    ])


def verify(result):
    failures = list(result['failures'])
    rows = result['rows']
    keyed = {(r['id'], r['seat'], r['facing'], r['mode']): r for r in rows}
    changed = {1: 'ristaff', 2: 'ghup', 3: 'ristwin', 8: 'ghup'}
    for r in rows:
        i, seat, face, mode, p = (r[k] for k in ('id', 'seat', 'facing', 'mode', 'value'))
        if i in changed and mode in ('chord-0', 'chord-1', 'chord-2', 'touch', 'platform'):
            if p['air'] or p['art'] != changed[i]:
                failures.append(f'{i}/{seat}/{face}/{mode} wrong route {p["art"]}, air={p["air"]}')
            ref = keyed[i, seat, face, 'ground-reference']['value']
            for key in ('dur', 'recovery', 'boxes', 'vy', 'ground', 'flags'):
                if p[key] != ref[key]: failures.append(f'{i}/{seat}/{face}/{mode} changed {key}')
        if i in changed and mode in ('chord-3','chord-8','double','wall','expired','support-lost','second'):
            first = r.get('trace', [p])[0]
            if not first['air']: failures.append(f'{i}/{seat}/{face}/{mode} stole an aerial input')
        if mode.startswith('released-') or mode == 'held-up':
            if not p['ground'] or p['buffer'] or p['state'].startswith('ATTACK'):
                failures.append(f'{i}/{seat}/{face}/{mode} failed to settle or repeated jump')
        if mode.startswith('pad-'):
            if p != r['keyboard']: failures.append(f'{seat}/{mode} differs from equivalent keyboard chord')
        if mode == 'stance-kageNui-chord':
            ref = keyed[i, seat, face, 'stance-kageNui-reference']['value']
            for key in ('air','art','dur','recovery','boxes','vy','ground','flags','stamina'):
                if p[key] != ref[key]: failures.append(f'{seat}/{face}/kageNui changed {key}')
    return failures


async def main(args):
    source = (ROOT / 'web/index.html').read_bytes()
    url = os.environ.get('SHADOWCLASH_URL', 'http://127.0.0.1:9101/index.html')
    browser.assert_serving_this_tree(url)
    browser.PORT = int(os.environ.get('DEBUG_PORT', '9398'))
    args.out.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='up-heavy-') as profile:
        proc, address = browser.launch(url, profile)
        try:
            async with websockets.connect(address, max_size=30_000_000) as ws:
                c = browser.CDP(ws)
                for _ in range(400):
                    if await c.js("return typeof SPRITES!=='undefined'&&NINJA_ROSTER.every(s=>SPRITES[s.name.toLowerCase()]?.ready)"):
                        break
                    await asyncio.sleep(.1)
                baseline = await c.js(JS)
                assert baseline and '__error' not in baseline, baseline
                (args.out / 'baseline.json').write_text(json.dumps(baseline))
                result = baseline
                if args.candidate:
                    installed = await c.js(inject(args.candidate.read_text()) + '\nreturn true;')
                    assert installed is True, installed
                    result = await c.js(JS)
                    assert result and '__error' not in result, result
                result['source_sha256'] = hashlib.sha256(source).hexdigest()
                result['checks'] = verify(result)
                # Unchanged roster branches and ordinary movement remain byte-for-byte equal.
                if args.candidate:
                    assert len(baseline['rows']) == len(result['rows'])
                    for old, new in zip(baseline['rows'], result['rows']):
                        if old['mode'].startswith('pad-'): continue
                        if old['id'] not in (1,2,3,8) or old['mode'] in ('jump-full','jump-tap','double','wall','expired','released-up') or old['mode'].startswith(('stance-hanbo','stance-sakate')):
                            if old != new: result['checks'].append('changed sibling '+str((old['id'],old['seat'],old['facing'],old['mode'])))
                (args.out / 'result.json').write_text(json.dumps(result))
                assert (ROOT / 'web/index.html').read_bytes() == source, 'production source changed during check'
                assert not result['checks'], result['checks'][:35]
                print(f'PASS: {len(result["rows"])} input/lifecycle samples; max chord Y rewind {max(r.get("rewind",0) for r in result["rows"]):.3f}px')
        finally:
            proc.terminate()
            proc.wait(timeout=10)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--candidate', type=Path)
    parser.add_argument('--out', type=Path, default=ROOT / 'media/up-heavy-routing-20260909/check')
    asyncio.run(main(parser.parse_args()))
