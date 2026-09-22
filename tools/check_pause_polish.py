#!/usr/bin/env python3
"""Exercise pause/focus boundaries in the actual browser and game input handlers."""
import argparse
import asyncio
import base64
import json
import tempfile
from pathlib import Path

import websockets
import watch_game as browser

JS = r'''
dismissTitle();
const checks = [];
const check = (name, ok, detail = null) => checks.push({name, ok: !!ok, detail});
const key = (code, down) => window.dispatchEvent(new KeyboardEvent(down ? 'keydown' : 'keyup', {code, bubbles:true}));
const nativeRAF = window.requestAnimationFrame;
window.requestAnimationFrame = () => 0;
const reset = () => {
    gameMode='2p'; cpuMode=false; spectate=false; p1Pick=5; p2Pick=1; stagePick='bamboo';
    startNewGame(); cutscene=null; roundIntroTimer=0; hitstopRemaining=0; paused=false;
    document.getElementById('pause-screen').classList.add('hidden'); releaseAllKeys();
    player1.x=180; player2.x=800;
    for (const p of [player1,player2]) {p.y=GROUND_Y-p.height;p.isGrounded=true;p.vy=0;}
    return player1;
};
try {
    let p=reset(); key('KeyD', true); setPaused(true);
    check('pause clears held keyboard input', !keys.KeyD && !physKeys.has('KeyD'));
    p=reset(); hitstopRemaining=60; pressCombat('KeyF'); p.bufferedAttack={ttl:.12}; setPaused(true);
    check('pause clears queued combat input', hitstopQueue.length===0 && !p.bufferedAttack);
    p=reset(); p._tapDir=1;p._tapT=performance.now();p._lt=performance.now();p._ht=performance.now();setPaused(true);
    check('pause clears dash and throw pairing', !p._tapDir && !p._tapT && !p._lt && !p._ht);
    p=reset(); key('KeyW', true); p.vy=-400; p.isGrounded=false; p.state=STATE.JUMP; p.jumpSquatT=0; setPaused(true); key('KeyW', false);
    check('jump release cannot change paused velocity', p.vy===-400, p.vy);
    p=reset(); window.dispatchEvent(new Event('blur'));
    check('focus loss pauses a live match', paused);
    window.dispatchEvent(new Event('focus')); check('focus return waits for Resume', paused);
    p=reset(); Object.defineProperty(document,'hidden',{configurable:true,value:true});
    document.dispatchEvent(new Event('visibilitychange'));
    check('hidden tab pauses a live match', paused);
    delete document.hidden;
    document.dispatchEvent(new Event('visibilitychange'));
    check('visible tab waits for Resume', paused);
    p=reset(); setPaused(true);
    document.getElementById('btn-t-p1-light').dispatchEvent(new Event('touchstart',{bubbles:true,cancelable:true}));
    check('touch cannot latch attacks while paused', !keys.p1_light && !p.attackAnim);
    p=reset(); keys.p1_up=true; p.vy=-400;p.isGrounded=false;p.state=STATE.JUMP;p.jumpSquatT=0;setPaused(true);
    // A real pad touch still in contact when the menu opens must not steer or cut jump.
    const pad=document.getElementById('pad-p1') || document.getElementById('dpad-p1');
    const touch=new Event('touchstart',{bubbles:true,cancelable:true});
    Object.defineProperty(touch,'changedTouches',{value:[{identifier:17,clientX:0,clientY:0}]});
    if(pad) pad.dispatchEvent(touch);
    check('paused touch release preserves jump', !!pad && p.vy===-400, {pad:pad?.id,vy:p.vy});
    p=reset();
    const originalPoint=document.elementFromPoint;
    document.elementFromPoint=()=>pad.querySelector('[data-dir="right"]');
    const gesture=type=>{const e=new Event(type,{bubbles:true,cancelable:true});
        Object.defineProperty(e,'changedTouches',{value:[{identifier:23,clientX:0,clientY:0}]});pad.dispatchEvent(e);};
    gesture('touchstart');setPaused(true);setPaused(false);gesture('touchmove');
    check('old touch cannot revive movement after Resume', !keys.p1_right);
    gesture('touchend');gesture('touchstart');
    check('fresh touch steers after Resume', keys.p1_right);
    gesture('touchend');document.elementFromPoint=originalPoint;

    p=reset(); setPaused(true); const frozen={x:p.x,y:p.y,vy:p.vy,hp:p.hp,clock:roundTimer,anim:animClock};
    for(let n=0;n<60;n++) gameLoop(lastTime+1000/60);
    check('paused frames freeze combat and round clock', JSON.stringify(frozen)===JSON.stringify({x:p.x,y:p.y,vy:p.vy,hp:p.hp,clock:roundTimer,anim:animClock}));
    lastTime=performance.now()-3000;setPaused(false);
    check('resume resets frame clock after background gap', performance.now()-lastTime<20);
    key('KeyD',true);const x=p.x;updateGame(1/60);key('KeyD',false);
    check('fresh movement works after Resume', p.x>x);
    p=reset();mouseMode=true;mouseCX=1000;mouseCY=0;mouseWasAbove=false;
    setPaused(true);setPaused(false);mouseControl();
    check('mouse waits for a fresh cursor update after Resume', mouseAxis===0 && !p.jumpSquatT);
    const rect=canvas.getBoundingClientRect();
    canvas.dispatchEvent(new MouseEvent('mousemove',{clientX:rect.left+rect.width*.8,clientY:rect.top+rect.height*.8}));
    mouseControl();check('fresh mouse movement resumes steering',mouseAxis===1);mouseMode=false;
    p=reset();setPaused(true);
    const landmarks=Array.from({length:21},()=>({x:.2,y:.9}));
    onHandResults({multiHandLandmarks:[landmarks]});
    check('webcam callback cannot latch inputs while paused',!keys.KeyS&&!keys.KeyC&&handTargetX===null);
    p=reset();matchActive=false;window.dispatchEvent(new Event('blur'));
    check('focus loss does not open pause outside a match', !paused);
    p=reset();cutscene={t:0};window.dispatchEvent(new Event('blur'));
    check('cutscene keeps its own input ownership', !paused);cutscene=null;
    p=reset();attractMode=true;window.dispatchEvent(new Event('blur'));check('title demo never acquires pause overlay',!paused);attractMode=false;
    p=reset();let fake={connected:true,mapping:'standard',axes:[0,0],buttons:Array.from({length:16},()=>({pressed:false}))};
    const getPads=navigator.getGamepads;
    Object.defineProperty(navigator,'getGamepads',{configurable:true,value:()=>[fake,null]});
    pollGamepads();fake.buttons[9].pressed=true;pollGamepads();pollGamepads();
    check('held controller Start pauses once', paused);
    fake.buttons[9].pressed=false;pollGamepads();fake.buttons[9].pressed=true;pollGamepads();
    check('second controller Start resumes', !paused);
    fake.buttons[9].pressed=false;pollGamepads();
    for(const button of [0,1]) {
        p=reset();setPaused(true);padMenuId=null;padMenuPrev[0].clear();pollGamepads();
        fake.buttons[button].pressed=true;pollGamepads();pollGamepads();
        check('controller '+button+' Resume does not attack', !paused && !p.attackAnim);
        fake.buttons[button].pressed=false;pollGamepads();fake.buttons[button].pressed=true;pollGamepads();
        check('controller '+button+' fires on a fresh press', !!p.attackAnim);
        fake.buttons[button].pressed=false;pollGamepads();
    }
    p=reset();setPaused(true);padMenuId=null;padMenuPrev[0].clear();pollGamepads();
    fake.axes[1]=-.9;pollGamepads();fake.buttons[0].pressed=true;pollGamepads();pollGamepads();
    check('held menu stick cannot jump on Resume', !paused && !keys.KeyW && !p.jumpSquatT);
    fake.buttons[0].pressed=false;fake.axes[1]=0;pollGamepads();fake.axes[1]=-.9;pollGamepads();
    check('stick re-arms after returning to neutral', !!p.jumpSquatT);
    fake.axes[1]=0;pollGamepads();
    Object.defineProperty(navigator,'getGamepads',{configurable:true,value:getPads});
    p=reset();setPaused(true);drawScene();
} finally { window.requestAnimationFrame=nativeRAF; }
return {checks,failures:checks.filter(c=>!c.ok),roster:NINJA_ROSTER.map(s=>s.name)};
'''

class Intercept(browser.CDP):
    def __init__(self, ws, html):
        super().__init__(ws)
        self.html, self.aux = html, 100000

    async def send(self, method, **params):
        self.n += 1
        wanted = self.n
        await self.ws.send(json.dumps({'id': wanted, 'method': method, 'params': params}))
        while True:
            msg = json.loads(await asyncio.wait_for(self.ws.recv(), 30))
            if msg.get('method') == 'Fetch.requestPaused':
                self.aux += 1
                await self.ws.send(json.dumps({'id': self.aux, 'method': 'Fetch.fulfillRequest', 'params': {
                    'requestId': msg['params']['requestId'], 'responseCode': 200,
                    'responseHeaders': [{'name': 'Content-Type', 'value': 'text/html'}],
                    'body': base64.b64encode(self.html.encode()).decode()}}))
            if msg.get('id') == wanted:
                if 'error' in msg: raise RuntimeError(msg['error'])
                return msg.get('result', {})


async def main(args):
    url='http://127.0.0.1:9101/index.html'
    browser.assert_serving_this_tree(url)
    browser.PORT=9391
    with tempfile.TemporaryDirectory(prefix='pause-polish-') as profile:
        proc,address=browser.launch(url,profile)
        try:
            async with websockets.connect(address,max_size=32*1024*1024) as ws:
                c=Intercept(ws,args.html.read_text()) if args.html else browser.CDP(ws)
                if args.html:
                    await c.send('Fetch.enable',patterns=[{'urlPattern':'*index.html*','resourceType':'Document'}])
                    await c.send('Page.reload',ignoreCache=True)
                for _ in range(400):
                    if await c.js("return typeof SPRITES!=='undefined' && NINJA_ROSTER.every(n=>SPRITES[n.name.toLowerCase()]?.ready)") is True:
                        break
                    await asyncio.sleep(.1)
                else: raise RuntimeError('active roster did not load')
                result=await c.js(JS)
                if not result or '__error' in result: raise RuntimeError(result)
                for width,height in [(1280,720),(390,844),(844,390)]:
                    await c.send('Emulation.setDeviceMetricsOverride',width=width,height=height,deviceScaleFactor=1,mobile=False)
                    layout=await c.js("const p=document.getElementById('pause-screen'),r=p.getBoundingClientRect(),c=p.firstElementChild.getBoundingClientRect();return {width:innerWidth,height:innerHeight,inside:r.top>=0&&r.left>=0&&r.bottom<=innerHeight+.5&&r.right<=innerWidth+.5&&c.top>=0&&c.bottom<=innerHeight+.5};")
                    row={'name':f'pause dialog fits {width}x{height}','ok':layout['inside'],'detail':layout}
                    result['checks'].append(row)
                    if not row['ok']:result['failures'].append(row)
                    await c.shot(args.out.with_name(args.out.stem+f'-{width}x{height}.png'))
        finally:
            proc.terminate();proc.wait(timeout=10)
    args.out.write_text(json.dumps(result,indent=2)+'\n')
    for row in result['checks']: print(('PASS' if row['ok'] else 'FAIL')+': '+row['name'])
    if result['failures']: raise SystemExit(1)

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--out',type=Path,required=True)
    parser.add_argument('--html',type=Path,help='Intercept page with a saved baseline; assets stay on the verified server')
    asyncio.run(main(parser.parse_args()))
