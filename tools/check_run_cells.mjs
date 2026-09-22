import assert from 'node:assert/strict';
import fs from 'node:fs';
import vm from 'node:vm';
import { ROSTER } from './roster.mjs';
const source=fs.readFileSync('web/index.html','utf8');
const fn=source.slice(source.indexOf('function runCells(F)'),source.indexOf('function attackBodyCells(F)'));
const run=vm.runInNewContext(fn+';runCells');
for(const n of ROSTER){
 const m=JSON.parse(fs.readFileSync(`web/assets/sprites/${n}.json`));const cells=Array.from(run(m.frames));
 assert(cells.length>0&&cells.every(c=>Number.isInteger(c)&&c>=0&&c<m.cols),n);
}
for(const size of [1,2,4,8,10])assert.equal(run(Object.fromEntries(Array.from({length:size},(_,i)=>['run_clean'+(i+1),i]))).length,size);
console.log(`${ROSTER.length} roster run collectors and 5 sequence lengths pass`);
