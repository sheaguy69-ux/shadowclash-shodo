#!/usr/bin/env node
// tools/check_zero_legacy.mjs — static zero-legacy / reachability check over the nine
// shipped fighter sheets (web/assets/sprites/<fighter>.json + .png), reading the LIVE
// engine (web/index.html) for the key names it probes.
//
// What it proves (the static half of the atlas-editions plan; the live half is
// check-live-routing.mjs / check_it_actually_plays.py on :9100):
//   1. GEOMETRY  — every json frame value is an in-range cell; png dims == frameW*cols x frameH
//   2. PURGED    — no json reintroduces a key the owner ordered deleted (PURGED-KEYS refusal)
//   3. CENSUS    — every cell is referenced by >=1 key, or is reported as an orphan
//                  (append-only keeps orphans; --strict makes any orphan a failure =
//                  the post-compaction "zero legacy" gate)
//   4. IDLE STUBS— keys whose cell == the idle cell: states that would draw the idle
//                  pose instead of their own art (the fallback-triggering census)
//   5. ROW GAPS  — numbered rows (f2_underscore and form-1 plain spellings) must start
//                  at beat 1 and be contiguous; a hole silently truncates the collector
//                  (info; FAIL in --strict)
//   6. STUTTERS  — rows whose beats repeat the same cell consecutively (info; eyes required)
//   7. DEAD ROWS — row bases the engine probes that NO fighter packs (owed art / dead code)
//
// Per-fighter reachability of a specific row (is row X drawn for fighter Y?) is NOT
// provable statically — the engine guards rows per fighter across many lines. That is
// check-live-routing.mjs territory. This checker reports what sheets alone can prove.
//
// Usage: node tools/check_zero_legacy.mjs [--strict]
import { readFileSync, readdirSync } from 'node:fs';
import path from 'node:path';
import zlib from 'node:zlib';

const ROOT = path.resolve(path.dirname(process.argv[1]), '..');
const SP = path.join(ROOT, 'web/assets/sprites');
const HTML = path.join(ROOT, 'web/index.html');
const STRICT = process.argv.includes('--strict');

const FIGHTERS = readdirSync(SP).filter(f => f.endsWith('.json') && f !== 'PURGED-KEYS.json')
  .map(f => f.replace(/\.json$/, '')).sort();

// ---- comment-stripped engine text (the SHEET_V changelog lives in comments) ----
const raw = readFileSync(HTML, 'utf8');
const code = raw
  .replace(/\/\*[\s\S]*?\*\//g, ' ')
  .replace(/\/\/[^\n]*/g, ' ');

// ---- literal key extraction -------------------------------------------------------
const bare = new Map();   // key -> [{line, guarded}]
const bareRe = /\b(?:F|MF|frames|man\.frames|wman\.frames|kman\.frames|dsh\.frames|SPRITES\.\w+\.frames)\s*\.\s*([A-Za-z_][A-Za-z0-9_]*)/g;
const bareBracketRe = /\b(?:F|frames|wman\.frames|man\.frames)\s*\[\s*['"]([A-Za-z_][A-Za-z0-9_]*)['"]\s*\]/g;
const lines = code.split('\n');
const guardedOn = ln => /undefined\b/.test(ln) || /\?\?|\|\|/.test(ln);
for (let i = 0; i < lines.length; i++) {
  const ln = lines[i];
  let m;
  const re1 = new RegExp(bareRe.source, 'g');
  while ((m = re1.exec(ln)) !== null) { if (!bare.has(m[1])) bare.set(m[1], []); bare.get(m[1]).push({ line: i + 1, guarded: guardedOn(ln) }); }
  const re2 = new RegExp(bareBracketRe.source, 'g');
  while ((m = re2.exec(ln)) !== null) { if (!bare.has(m[1])) bare.set(m[1], []); bare.get(m[1]).push({ line: i + 1, guarded: guardedOn(ln) }); }
}
// row bases: row('f2_dash') and F['run_clean' + i] / F[bt f2_vanish_N bt] template reads
const rowBases = new Set();
const rowCallRe = /\brow\(\s*['"]([A-Za-z_][A-Za-z0-9_]*)['"]\s*\)/g;
const rowConcatRe = /\b(?:F|frames|wman\.frames)\s*\[\s*['"]([A-Za-z_][A-Za-z0-9_]*)['"]\s*\+\s*[a-z]/g;
const rowTplRe = /\bF\s*\[\s*\x60([A-Za-z_][A-Za-z0-9_]*)_\$\{/g;
for (const ln of lines) {
  let m;
  const r1 = new RegExp(rowCallRe.source, 'g'); while ((m = r1.exec(ln)) !== null) rowBases.add(m[1]);
  const r2 = new RegExp(rowConcatRe.source, 'g'); while ((m = r2.exec(ln)) !== null) rowBases.add(m[1]);
  const r3 = new RegExp(rowTplRe.source, 'g'); while ((m = r3.exec(ln)) !== null) rowBases.add(m[1]);
}
for (const b of Array.from(rowBases)) if (b.length < 2) rowBases.delete(b);

// ---- minimal PNG RGBA decoder (8-bit, color type 6, non-interlaced) ---------------
// returns the set of wanted cells that contain ink (any alpha >= 8)
function cellInk(pngPath, frameW, cols, wanted) {
  const buf = readFileSync(pngPath);
  if (buf.readUInt32BE(0) !== 0x89504e47) throw new Error('not a PNG');
  let pos = 8, w = 0, h = 0, interlace = 0;
  const idat = [];
  while (pos < buf.length) {
    const len = buf.readUInt32BE(pos);
    const type = buf.toString('ascii', pos + 4, pos + 8);
    if (type === 'IHDR') {
      w = buf.readUInt32BE(pos + 8); h = buf.readUInt32BE(pos + 12);
      const depth = buf[pos + 8 + 8], ctype = buf[pos + 8 + 9];
      interlace = buf[pos + 8 + 12];
      if (depth !== 8 || ctype !== 6) throw new Error('only 8-bit RGBA supported');
    } else if (type === 'IDAT') idat.push(buf.subarray(pos + 8, pos + 8 + len));
    pos += 12 + len;
  }
  if (interlace !== 0) throw new Error('interlaced PNG not supported');
  const px = zlib.inflateSync(Buffer.concat(idat));
  const bpp = 4, stride = w * bpp;
  const ink = new Set();
  let prev = new Uint8Array(stride), cur = new Uint8Array(stride), off = 0;
  for (let y = 0; y < h; y++) {
    const filt = px[off++];
    for (let x = 0; x < stride; x++) {
      const rawB = px[off++];
      const a = x >= bpp ? cur[x - bpp] : 0, b = prev[x], c = x >= bpp ? prev[x - bpp] : 0;
      let v;
      switch (filt) {
        case 0: v = rawB; break;
        case 1: v = rawB + a; break;
        case 2: v = rawB + b; break;
        case 3: v = rawB + ((a + b) >> 1); break;
        case 4: { const p = a + b - c, pa = Math.abs(p - a), pb = Math.abs(p - b), pc = Math.abs(p - c);
                  v = rawB + (pa <= pb && pa <= pc ? a : pb <= pc ? b : c); break; }
        default: throw new Error('bad filter ' + filt);
      }
      cur[x] = v & 0xff;
    }
    for (let x = 0; x < w; x++) {
      if (cur[x * 4 + 3] >= 8) {
        const cell = Math.floor(x / frameW);
        if (cell < cols && wanted.has(cell)) ink.add(cell);
      }
    }
    const t = prev; prev = cur; cur = t;
  }
  return ink;
}

// ---- per-fighter checks ----------------------------------------------------------
const purged = JSON.parse(readFileSync(path.join(SP, 'PURGED-KEYS.json'), 'utf8'));
let failures = 0, orphanInkTotal = 0, orphanBlankTotal = 0, idleStubTotal = 0;
const allPacked = new Set();

for (const name of FIGHTERS) {
  const d = JSON.parse(readFileSync(path.join(SP, name + '.json'), 'utf8'));
  const frameW = d.frameW, frameH = d.frameH, cols = d.cols, frames = d.frames;
  for (const k of Object.keys(frames)) allPacked.add(k);
  const row = [];
  function fail(msg) { failures++; row.push('  FAIL ' + msg); }
  function info(msg) { row.push('  ' + msg); }

  // 1. geometry: png dims must equal frameW*cols x frameH exactly (audit rule)
  try {
    const png = readFileSync(path.join(SP, name + '.png'));
    const pw = png.readUInt32BE(16), ph = png.readUInt32BE(20);
    if (pw !== frameW * cols || ph !== frameH)
      fail('png ' + pw + 'x' + ph + ' != frameW*cols x frameH = ' + (frameW * cols) + 'x' + frameH);
  } catch (e) { fail('png unreadable: ' + e.message); }

  // 2. every frame value in range; collect cell->keys
  const cellKeys = new Map();
  for (const k of Object.keys(frames)) {
    const v = frames[k];
    if (typeof v !== 'number' || !Number.isInteger(v) || v < 0 || v >= cols) {
      fail('key ' + k + ' -> cell ' + v + ' out of range [0,' + cols + ')'); continue;
    }
    if (!cellKeys.has(v)) cellKeys.set(v, []);
    cellKeys.get(v).push(k);
  }
  const purgedList = purged[name];
  if (Array.isArray(purgedList)) {
    for (const k of Object.keys(frames)) if (purgedList.indexOf(k) !== -1)
      fail('PURGED key reintroduced: ' + k + ' (owner ordered deleted — restore refused)');
  }

  // 3. census: orphan cells (referenced by no key)
  const orphans = [];
  for (let c = 0; c < cols; c++) if (!cellKeys.has(c)) orphans.push(c);
  let oInk = 0, oBlank = 0;
  if (orphans.length) {
    try {
      const inkCells = cellInk(path.join(SP, name + '.png'), frameW, cols, new Set(orphans));
      oInk = inkCells.size; oBlank = orphans.length - oInk;
    } catch (e) { info('png ink scan skipped: ' + e.message); oInk = -1; }
  }
  orphanInkTotal += oInk > 0 ? oInk : 0; orphanBlankTotal += oBlank;
  let orphanNote;
  if (orphans.length) {
    orphanNote = orphans.length + ' orphan cell' + (orphans.length > 1 ? 's' : '') + ' (' +
      (oInk >= 0 ? oInk + ' with ink, ' + oBlank + ' blank' : 'ink unknown') +
      ') — append-only keeps them; strip candidates: ' + orphans.slice(0, 12).join(',') +
      (orphans.length > 12 ? '...' : '');
  } else orphanNote = 'every cell is referenced (zero legacy)';
  if (STRICT && orphans.length) fail('orphans present: ' + orphanNote);
  else info(orphanNote);

  // 4. idle stubs: keys that draw the idle cell instead of their own art
  const idleCell = frames.idle;
  if (typeof idleCell === 'number') {
    // exclude keys that are themselves idle aliases (xidle1, idle_stance1, idle_v335...)
    // from the STUB count — an alias pointing at its own cell is not a fallback.
    const stubs = Object.keys(frames).filter(k => frames[k] === idleCell && k.indexOf('idle') === -1);
    if (stubs.length) {
      idleStubTotal += stubs.length;
      info('idle-cell stubs (' + stubs.length + ' — these states draw the idle pose): ' +
           stubs.slice(0, 12).join(',') + (stubs.length > 12 ? '...' : ''));
    }
  }

  // 5. numbered-row contiguity (both spellings, deduped) + stutter detection.
  //    A row family must START at beat 1 (hand-seal dial keys like kick21/punch31
  //    are NOT rows and do not start at 1 — do not flag them).
  const fam = new Map(); // base -> Set(indices)
  for (const k of Object.keys(frames)) {
    const m = /^(.*[^0-9_])_?([0-9]+)$/.exec(k);
    if (m && /^[a-z]/.test(m[1])) {
      if (!fam.has(m[1])) fam.set(m[1], new Set());
      fam.get(m[1]).add(Number(m[2]));
    }
  }
  for (const base of Array.from(fam.keys())) {
    const idxs = Array.from(fam.get(base)).sort((a, b) => a - b);
    if (idxs.length < 2 || idxs[0] !== 1) continue; // not a row
    const contiguous = idxs[idxs.length - 1] === idxs.length; // 1..n dense
    if (!contiguous) {
      const msg = 'row ' + base + ' has a gap: ' + idxs.join(',') + ' — collector truncates at the hole';
      if (STRICT) fail(msg); else info('GAP ' + msg);
    }
    const cells = idxs.map(n => frames[base + '_' + n] !== undefined ? frames[base + '_' + n] : frames[base + n]);
    let stut = 0;
    for (let i = 1; i < cells.length; i++) if (cells[i] === cells[i - 1]) stut++;
    if (stut > cells.length / 2) info('row ' + base + ' stutters (' + stut + '/' + cells.length + ' beats repeat the same cell) — eyes required');
  }

  console.log(name.padEnd(12) + ' cols=' + String(cols).padEnd(4) +
    ' ' + String(Object.keys(frames).length).padEnd(4) + ' keys ' +
    String(cellKeys.size).padEnd(4) + ' live cells ' +
    (row.length ? '\n' + row.join('\n') : 'CLEAN'));
}

// 7. dead rows: engine probes a row base no fighter packs (owed art / dead code)
const deadRows = [];
for (const b of Array.from(rowBases)) {
  const packed = Array.from(allPacked).some(k => k.indexOf(b + '_') === 0 || k.indexOf(b) === 0);
  if (!packed) deadRows.push(b);
}
if (deadRows.length) {
  console.log('\nDEAD ROWS — engine probes these row bases but NO sheet packs them (owed art or dead code):');
  console.log('  ' + deadRows.join(', '));
}

console.log('\norphan census: ' + orphanInkTotal + ' cells with ink (strip candidates), ' +
  orphanBlankTotal + ' blank (dead space); idle-cell stubs: ' + idleStubTotal);
console.log(failures
  ? failures + ' FAILURES' + (STRICT ? ' (strict)' : '')
  : STRICT ? 'OK — strict zero-legacy'
           : 'OK — hard checks pass; orphans are pre-strip append-only cells (run --strict post-compaction)');
process.exit(failures ? 1 : 0);
