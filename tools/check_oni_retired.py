"""Run Oni removal checks in a separate browser; optional candidate is intercepted in memory."""
import argparse,asyncio,base64,hashlib,json,os,sys,tempfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools'))
import watch_game as browser
import websockets
JS=r'''
dismissTitle();paused=true;cutscene=null;releaseAllKeys();
const roster=NINJA_ROSTER.map(n=>({id:n.id,name:n.name}));
const saved={p1:attractSaved?.p1,p2:attractSaved?.p2};
const modes=[];
for(const mode of ['2p','cpu','training','watch','tag','teams','brawl','arcade','story']){
 gameMode=mode;cpuMode=mode==='cpu';spectate=false;p1Pick=5;p2Pick=1;p1PickB=0;p2PickB=2;stagePick='bamboo';
 beginFight();paused=true;cutscene=null;roundIntroTimer=0;
 modes.push({mode,ids:[...teamP1,...teamP2].filter(Boolean).map(p=>p.spec.id),queue:arcadeQueue?.slice()});
}
const rows=[]; const key=(code,down)=>window.dispatchEvent(new KeyboardEvent(down?'keydown':'keyup',{code,bubbles:true}));
const snap=p=>({state:p.state,air:p.attackAir,art:p.moveArt||null,hp:p.hp,stamina:p.stamina,rec:p.recoveryTimer,
 x:p.x,y:p.y,vx:p.vx,vy:p.vy,ground:p.isGrounded,foeHp:p.opponent.hp,
 boxes:p.hitboxes.map(h=>({w:h.w,h:h.h,ox:h.ox,oy:h.oy,damage:h.damage,delay:h.delay,duration:h.duration}))});
for(let id=0;id<8;id++)for(const face of [1,-1])for(const air of [false,true])for(const code of ['KeyF','KeyJ','KeyG','KeyH'])for(const dir of ['neutral','fwd','back','up','down']){
 releaseAllKeys();gameMode='2p';cpuMode=false;spectate=false;p1Pick=id;p2Pick=id===0?1:0;stagePick='bamboo';startNewGame();
 paused=false;cutscene=null;roundIntroTimer=0;animClock=100;
 const p=player1,q=player2;Object.assign(p,{x:face===1?300:650,y:GROUND_Y-p.height-(air?80:0),vx:0,vy:0,isGrounded:!air,facing:face});
 Object.assign(q,{x:p.x+face*75,y:p.y,vx:0,vy:0,isGrounded:!air,facing:-face});
 if(dir==='up')keys.KeyW=true;else if(dir==='down')keys.KeyS=true;else if(dir!=='neutral')keys[(dir==='fwd')===(face===1)?'KeyD':'KeyA']=true;
 key(code,true);key(code,false);const trace=[snap(p)];
 for(let t=0;t<32;t++){hitstopRemaining=0;updateGame(1/(60*COMBAT_TEMPO));if([0,7,15,31].includes(t))trace.push(snap(p));}
 rows.push({id,face,air,code,dir,trace});
}
paused=true;releaseAllKeys();
return {roster,saved,modes,rows,errors:window.__oniErrors||[],resources:performance.getEntriesByType('resource').map(r=>r.name).filter(n=>/\/oni(?:[.\-])/.test(n)),spriteNames:Object.keys(SPRITES)};
'''
class Intercept(browser.CDP):
 def __init__(self,ws,html):super().__init__(ws);self.html=html;self.aux=100000
 async def send(self,method,**params):
  self.n+=1;wanted=self.n
  await self.ws.send(json.dumps({'id':wanted,'method':method,'params':params}))
  while True:
   m=json.loads(await asyncio.wait_for(self.ws.recv(),90))
   if m.get('method')=='Fetch.requestPaused':
    self.aux+=1
    await self.ws.send(json.dumps({'id':self.aux,'method':'Fetch.fulfillRequest','params':{'requestId':m['params']['requestId'],'responseCode':200,'responseHeaders':[{'name':'Content-Type','value':'text/html'}],'body':base64.b64encode(self.html.encode()).decode()}}))
   if m.get('id')==wanted:
    if 'error'in m:raise RuntimeError(m['error'])
    return m.get('result',{})
async def main(a):
 url='http://127.0.0.1:9101/index.html';browser.assert_serving_this_tree(url);browser.PORT=9401
 with tempfile.TemporaryDirectory(prefix='oni-retirement-') as profile:
  proc,address=browser.launch(url,profile)
  try:
   async with websockets.connect(address,max_size=64*1024*1024) as ws:
    c=Intercept(ws,a.html.read_text() if a.html else '')
    await c.js("localStorage.setItem('shadowclash_save_v1',JSON.stringify({prefs:{p1Pick:8,p2Pick:8}}));return true;")
    await c.send('Page.addScriptToEvaluateOnNewDocument',source="window.__oniErrors=[];window.addEventListener('error',e=>window.__oniErrors.push(e.message));window.addEventListener('unhandledrejection',e=>window.__oniErrors.push(String(e.reason)));")
    if a.html:await c.send('Fetch.enable',patterns=[{'urlPattern':'*index.html*','resourceType':'Document'}])
    await c.send('Page.reload',ignoreCache=True)
    for _ in range(400):
     ready=await c.js("return typeof SPRITES!=='undefined'&&NINJA_ROSTER.every(n=>SPRITES[n.name.toLowerCase()]?.ready)")
     if ready is True:break
     await asyncio.sleep(.1)
    assert ready is True,ready
    out=await c.js(JS);assert out and '__error' not in out,out
    a.out.parent.mkdir(parents=True,exist_ok=True);a.out.write_text(json.dumps(out))
    if a.compare:
     before=json.loads(a.compare.read_text());assert before['rows']==out['rows'],'retained fighter behavior changed'
    assert not out['errors'],out['errors']
    if not a.baseline:
     assert [n['id'] for n in out['roster']]==list(range(8)),out['roster']
     assert out['saved']=={'p1':5,'p2':1},out['saved']
     assert 'oni'not in out['spriteNames'] and not out['resources'],out['resources']
     assert all(8 not in m['ids'] and 8 not in (m.get('queue')or[])for m in out['modes'])
    print('PASS',len(out['rows']),'attack cases,',len(out['modes']),'modes; errors',out['errors'],flush=True)
  finally:proc.terminate();proc.wait(timeout=10)
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--html',type=Path);p.add_argument('--out',type=Path,required=True);p.add_argument('--baseline',action='store_true');p.add_argument('--compare',type=Path);asyncio.run(main(p.parse_args()))
