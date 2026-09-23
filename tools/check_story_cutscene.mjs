import { spawn, spawnSync } from 'node:child_process';
import { mkdtemp } from 'node:fs/promises';
import { tmpdir } from 'node:os';
import path from 'node:path';

// Story-cutscene check (docs/STORY-CUTSCENE-SYSTEM-DESIGN.md §9). Drives the REAL code path:
// startCutscene -> advance/typewriter/skip -> handoff, plus static hooks (beginFight/gameLoop/resetRound).
const port = 9101, dbg = 9344;
const profile = await mkdtemp(path.join(tmpdir(), 'sc-cutscene-'));
spawnSync('pkill', ['-f', `remote-debugging-port=${dbg}`], { stdio: 'ignore' });
// ⛔ WAIT FOR IT TO ACTUALLY DIE — the same loop check_jump_commit and check_air_art_holds
// already run. pkill returns before the old Chrome is gone, so /json/list handed back the
// DYING instance's tab and every eval died with 'Execution context was destroyed'. Read as
// a code failure; it was two Chromes on one debug port.
for (let i = 0; i < 60; i++) {
  const s = spawnSync('pgrep', ['-f', `remote-debugging-port=${dbg}`], { encoding: 'utf8' });
  if (!s.stdout || !s.stdout.trim()) break;
  await new Promise(r => setTimeout(r, 100));
}
const alive = await fetch(`http://127.0.0.1:${port}/`).then(r => r.ok).catch(() => false);
if (!alive) { console.error('CHECK FAIL: start the shared server first — python3 tools/serve.py 9101 web'); process.exit(1); }
const chrome = spawn('/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',
  ['--headless=new','--disable-gpu','--no-first-run','--no-sandbox',`--remote-debugging-port=${dbg}`,`--user-data-dir=${profile}`,`http://127.0.0.1:${port}/`], { stdio: 'ignore' });
const sleep = ms => new Promise(r => setTimeout(r, ms));
let page;
for (let i=0;i<100&&!page;i++){try{const l=await fetch(`http://127.0.0.1:${dbg}/json/list`).then(r=>r.json());page=l.find(t=>t.type==='page'&&t.url.includes(String(port)));}catch{} if(!page) await sleep(100);}
if (!page) { console.error('CHECK FAIL: no page'); process.exit(1); }
const ws = new WebSocket(page.webSocketDebuggerUrl);
await new Promise((r,j)=>{ws.addEventListener('open',r,{once:true});ws.addEventListener('error',j,{once:true});});
let id=1;const pend=new Map();
ws.addEventListener('message',e=>{const m=JSON.parse(e.data);if(m.id&&pend.has(m.id)){const p=pend.get(m.id);pend.delete(m.id);m.error?p.rej(new Error(m.error.message)):p.res(m.result);}});
const ev = x => new Promise((res,rej)=>{const n=id++;pend.set(n,{res,rej});ws.send(JSON.stringify({id:n,method:'Runtime.evaluate',params:{expression:x,awaitPromise:true,returnByValue:true,timeout:15000}}));}).then(r=>{if(r.exceptionDetails)throw new Error(r.exceptionDetails.exception?.description||r.exceptionDetails.text);return r.result.value;});

const expr = String.raw`(async () => {
  const wait = async (t, m) => { for (let i=0;i<200;i++){ if(t()) return; await new Promise(r=>setTimeout(r,50)); } throw new Error(m); };
  await wait(() => typeof CUTSCENES !== 'undefined' && typeof startCutscene === 'function', 'cutscene globals');
  const res = [];
  const t = (name, cond) => res.push({ name, pass: !!cond });
  const screen = document.getElementById('cutscene-screen');
  const text = document.getElementById('cutscene-text');

  t('prologue: 7 beats', Array.isArray(CUTSCENES.prologue) && CUTSCENES.prologue.length === 7);
  t('doors: Exile + Mokurai', !!(CUTSCENES.door_intro && CUTSCENES.door_intro[7] && CUTSCENES.door_intro[6]));

  let done = false;
  startCutscene('prologue', () => { done = true; });
  t('start: cutscene set', cutscene !== null);
  t('start: overlay shown', !screen.classList.contains('hidden'));
  t('start: first beat lantern narrator', cutscene.beats[0].board === 'lantern' && cutscene.beats[0].who === null);
  let guard = 0;
  while (cutscene && guard++ < 20) advanceCutscene();
  t('advance: drains to null', cutscene === null);
  t('advance: onDone fired', done === true);
  t('advance: overlay re-hidden', screen.classList.contains('hidden'));

  startCutscene(CUTSCENES.door_intro[7], null);
  t('door: Exile beat', cutscene && cutscene.beats[0].who === 'Exile');
  updateCutsceneTypewriter(1.0);
  t('typewriter: types text', text.textContent.length > 0);
  endCutscene();
  t('skip: ends scene', cutscene === null);

  t('hook: beginFight -> prologue', /startCutscene\('prologue'/.test(beginFight.toString()));
  t('hook: gameLoop freeze', /if \(cutscene\)/.test(gameLoop.toString()));
  t('hook: resetRound door', /CUTSCENES\.door_intro/.test(resetRound.toString()));

  return { results: res, fail: res.filter(r => !r.pass).map(r => r.name) };
})()`;

let result;
try { result = await ev(expr); }
catch (e) { console.error('CHECK FAILED: ' + (e && e.message || e)); process.exit(1); }
console.log(JSON.stringify(result, null, 2));
if (result.fail && result.fail.length) { console.error('CUTSCENE CHECK FAILED: ' + result.fail.join(', ')); process.exit(1); }
console.log('CUTSCENE CHECK OK — ' + result.results.length + ' assertions green');
process.exit(0);
