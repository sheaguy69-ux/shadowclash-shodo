#!/usr/bin/env node
// Compare cached Shodo output with the approved pre-cache renderer in real Canvas.
import { spawn, spawnSync } from 'node:child_process';
import { mkdtemp } from 'node:fs/promises';
import { tmpdir } from 'node:os';
import path from 'node:path';

const port = +(process.env.PORT || 9101), dbg = 9382;
const who = await fetch(`http://127.0.0.1:${port}/whoami`).then(r => r.json()).catch(() => null);
if (!who) { console.error(`no server on :${port}`); process.exit(1); }
if (path.resolve(who.tree) !== path.resolve(process.cwd())) {
  console.error(`:${port} serves ${who.tree} — rebind before trusting this`); process.exit(1);
}
spawnSync('pkill', ['-f', `remote-debugging-port=${dbg}`], { stdio: 'ignore' });
for (let i = 0; i < 60; i++) {
  const s = spawnSync('pgrep', ['-f', `remote-debugging-port=${dbg}`], { encoding: 'utf8' });
  if (!s.stdout || !s.stdout.trim()) break;
  await new Promise(r => setTimeout(r, 100));
}
const profile = await mkdtemp(path.join(tmpdir(), 'sg-'));
const chrome = spawn('/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',
  ['--headless=new', '--disable-gpu', '--no-first-run', `--remote-debugging-port=${dbg}`,
   `--user-data-dir=${profile}`, `http://127.0.0.1:${port}/`], { stdio: 'ignore' });
const sleep = ms => new Promise(r => setTimeout(r, ms));
let page = null;
for (let i = 0; i < 100 && !page; i++) {
  try {
    const l = await fetch(`http://127.0.0.1:${dbg}/json/list`).then(r => r.json());
    page = l.find(t => t.type === 'page' && t.url.includes(String(port)));
  } catch {}
  if (!page) await sleep(100);
}
if (!page) { console.error('chrome never came up'); process.exit(1); }
const ws = new WebSocket(page.webSocketDebuggerUrl);
await new Promise(r => ws.addEventListener('open', r, { once: true }));
let id = 1; const pend = new Map();
ws.addEventListener('message', e => {
  const m = JSON.parse(e.data);
  if (m.id && pend.has(m.id)) { const p = pend.get(m.id); pend.delete(m.id); m.error ? p.rej(new Error(m.error.message)) : p.res(m.result); }
});
const ev = x => new Promise((res, rej) => {
  const n = id++; pend.set(n, { res, rej });
  ws.send(JSON.stringify({ id: n, method: 'Runtime.evaluate', params: { expression: x, awaitPromise: true, returnByValue: true } }));
}).then(r => { if (r.exceptionDetails) throw new Error(r.exceptionDetails.exception?.description || r.exceptionDetails.text); return r.result.value; });


// Frozen pre-cache renderer: visual oracle, independent of cache behavior.
const baseline = "        function drawShodoFrame(ctx, img, sx, sy, sw, sh, dx, dy, dw, dh) {\n            const kx = sw / Math.abs(dw), ky = sh / Math.abs(dh);\n            const pad = Math.ceil(5 * Math.max(kx, ky));\n            const tw = sw + pad * 2, th = sh + pad * 2;\n            if (shodoScratch.width < tw) shodoScratch.width = tw;\n            if (shodoScratch.height < th) shodoScratch.height = th;\n            const g = shodoScratch.getContext('2d');\n            g.filter = 'none';\n            g.clearRect(0, 0, tw, th);\n            g.filter = `drop-shadow(${-1.55 * kx}px ${-0.06 * ky}px 0 #080604) `\n                     + `drop-shadow(${1.95 * kx}px ${0.10 * ky}px 0 #080604) `\n                     + `drop-shadow(${0.08 * kx}px ${-1.35 * ky}px 0 #080604) `\n                     + `drop-shadow(${-0.06 * kx}px ${1.72 * ky}px 0 rgba(8,6,4,0.90))`;\n            g.drawImage(keyedShodoCell(img, sx, sy, sw, sh), 0, 0, sw, sh, pad, pad, sw, sh);\n            g.filter = 'none';\n            const px = pad / kx, py = pad / ky;\n            ctx.drawImage(shodoScratch, 0, 0, tw, th,\n                          dx - px, dy - py, dw + px * 2, dh + py * 2);\n        }";
// Initial navigation can replace the JavaScript context while Chrome is opening.
let ready=false;
for(let n=0;n<600&&!ready;n++){
 ready=await ev("typeof SPRITES!=='undefined' && typeof NINJA_ROSTER!=='undefined' && NINJA_ROSTER.every(s=>SPRITES[s.name.toLowerCase()]?.ready)").catch(()=>false);
 if(!ready)await sleep(50);
}
if(!ready){ws.close();chrome.kill('SIGKILL');throw new Error('roster did not load');}
let out;
try {
 out = await ev(`(async()=>{
  for(let i=0;i<600;i++){if(typeof SPRITES!=='undefined' && NINJA_ROSTER.every(s=>SPRITES[s.name.toLowerCase()]?.ready))break;await new Promise(r=>setTimeout(r,50));}
  const shodoScratch=document.createElement('canvas');
  const reference=eval('('+${JSON.stringify(baseline)}+')');
  const make=()=>{const c=document.createElement('canvas');c.width=700;c.height=600;return c.getContext('2d',{willReadFrequently:true});};
  const old=make(), current=make();
  let compared=0;const failures=[];
  for(const name of NINJA_ROSTER.map(s=>s.name.toLowerCase())){
   const man=SPRITES[name],S=man.scale*SHODO_DISPLAY_SCALE;
   for(const frame of [man.frames.idle,man.frames.kxcut1??man.frames.light1,man.frames.medium1].filter(x=>x!==undefined)){
    for(const transform of ['plain','mirror','fractional']){
     const scale=transform==='fractional'?.83:1;
     const paint=(g,fn)=>{g.resetTransform();g.clearRect(0,0,700,600);g.save();g.translate(350.25,350.75);
      if(transform==='mirror')g.scale(-1,1);
      if(transform==='fractional'){g.rotate(.07);g.scale(1.03,.98);g.globalAlpha=.43;}
      fn(g,man.img,frame*man.frameW,0,man.frameW,man.frameH,-man.frameW*S/2,-man.footY*S,man.frameW*S*scale,man.frameH*S*scale);g.restore();};
     // A fresh scratch defines the approved cell. The old shared scratch could
     // leak another cell's stale bottom-edge ink when sampled at fractional sizes.
     shodoScratch.width=shodoScratch.height=1;
     paint(old,reference);paint(current,drawShodoFrame);
     const a=old.getImageData(0,0,700,600).data,b=current.getImageData(0,0,700,600).data;
     let differences=0;for(let i=0;i<a.length;i++)if(a[i]!==b[i])differences++;
     compared++;if(differences)failures.push({name,frame,transform,differences});
    }
   }
  }
  const man=SPRITES.kael,frame=man.frames.idle,S=man.scale*SHODO_DISPLAY_SCALE;
  const native=CanvasRenderingContext2D.prototype.drawImage;let filtered=0;
  CanvasRenderingContext2D.prototype.drawImage=function(...args){if(this.filter!=='none')filtered++;return native.apply(this,args);};
  try {for(let n=0;n<12;n++)drawShodoFrame(current,man.img,frame*man.frameW,0,man.frameW,man.frameH,10,10,man.frameW*S,man.frameH*S);}
  finally {CanvasRenderingContext2D.prototype.drawImage=native;}
  if(filtered>1)failures.push({reason:'held pose rebuilt its outline',filtered});
  for(let n=0;n<70;n++)drawShodoFrame(current,man.img,frame*man.frameW,0,man.frameW,man.frameH,10,10,200+n,240);
  const retained=shodoFrameCache.size;
  if(retained>64)failures.push({reason:'outlined-frame cache is unbounded',retained});
  return {compared,filtered,retained,failures};
 })()`);
} finally { ws.close();chrome.kill('SIGKILL'); }
console.log(JSON.stringify(out,null,2));
process.exit(out.failures.length?1:0);
