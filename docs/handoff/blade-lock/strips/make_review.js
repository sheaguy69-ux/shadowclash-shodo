const fs = require('fs');
const path = require('path');
const sharp = require('sharp');
const { createCanvas, loadImage } = require('@napi-rs/canvas');

const root = __dirname;
const fighters = [
  ['kael', 'kael-10-frame-sheet.png', 'Long katana binds · short wakizashi remains live'],
  ['executioner', 'executioner-10-frame-sheet.png', 'One nodachi · two-handed bind'],
  ['tsubasa', 'tsubasa-10-frame-sheet.png', 'Two tanto · reverse grip'],
  ['ember', 'ember-10-frame-sheet.png', 'Two tekkō-kagi · three claws per hand'],
  ['mizu', 'mizu-10-frame-sheet.png', 'One wooden bō · both hands'],
  ['shin', 'shin-10-frame-sheet.png', 'One held kunai · never thrown'],
  ['exile', 'exile-10-frame-sheet.png', 'Sickle binds · chain stays secondary'],
  ['oni', 'oni-10-frame-sheet-3-claws.png', 'RIGHT hand only · EXACTLY THREE claws'],
];

function fit(sw, sh, x, y, w, h) {
  const s = Math.min(w / sw, h / sh);
  return { x: x + (w - sw * s) / 2, y: y + (h - sh * s) / 2, w: sw * s, h: sh * s };
}

async function review() {
  const canvas = createCanvas(1500, 2020);
  const ctx = canvas.getContext('2d');
  ctx.fillStyle = '#111116'; ctx.fillRect(0, 0, canvas.width, canvas.height);
  ctx.fillStyle = '#202027'; ctx.fillRect(0, 0, canvas.width, 120);
  ctx.font = '800 48px Arial'; ctx.fillStyle = '#f8f8fa'; ctx.fillText('SHADOWCLASH — BLADE LOCK ROSTER', 32, 58);
  ctx.font = '700 23px Arial'; ctx.fillStyle = '#ffbd2e'; ctx.fillText('10 frames each · review candidates · not packed into the live game', 34, 94);
  const margin = 28, gap = 22, cardW = 711, cardH = 440;
  for (let i = 0; i < fighters.length; i++) {
    const [name, file, rule] = fighters[i];
    const col = i % 2, row = Math.floor(i / 2);
    const x = margin + col * (cardW + gap), y = 145 + row * (cardH + gap);
    ctx.fillStyle = '#202027'; ctx.strokeStyle = name === 'oni' ? '#ff334d' : '#4b4e59'; ctx.lineWidth = name === 'oni' ? 4 : 2;
    ctx.beginPath(); ctx.roundRect(x, y, cardW, cardH, 14); ctx.fill(); ctx.stroke();
    ctx.font = '800 28px Arial'; ctx.fillStyle = '#ffffff'; ctx.fillText(name.toUpperCase(), x + 18, y + 36);
    ctx.font = '600 16px Arial'; ctx.fillStyle = name === 'oni' ? '#ff5267' : '#bfc3ce'; ctx.fillText(rule, x + 18, y + 63);
    const img = await loadImage(path.join(root, name, file));
    const box = fit(img.width, img.height, x + 12, y + 78, cardW - 24, cardH - 90);
    ctx.fillStyle = '#ffffff'; ctx.fillRect(box.x, box.y, box.w, box.h);
    ctx.drawImage(img, box.x, box.y, box.w, box.h);
  }
  ctx.fillStyle = '#202027'; ctx.fillRect(0, 1980, 1500, 40);
  ctx.font = '600 17px Arial'; ctx.fillStyle = '#bfc3ce'; ctx.fillText('Order inside every sheet: CATCH · SETTLE · STRAIN ×6 · WIN · LOSE', 32, 2007);
  fs.writeFileSync(path.join(root, 'blade-lock-all-characters-review.png'), canvas.toBuffer('image/png'));
}

async function oniCard() {
  const canvas = createCanvas(1900, 1120); const ctx = canvas.getContext('2d');
  ctx.fillStyle = '#111116'; ctx.fillRect(0, 0, 1900, 1120);
  ctx.fillStyle = '#202027'; ctx.fillRect(0, 0, 1900, 120);
  ctx.font = '800 54px Arial'; ctx.fillStyle = '#f7f7f9'; ctx.fillText('ONI — BLADE LOCK IDENTITY CARD', 34, 68);
  ctx.font = '700 24px Arial'; ctx.fillStyle = '#ff334d'; ctx.fillText('CORRECTED OWNER RULE — EXACTLY THREE RIGHT-HAND CLAWS', 36, 104);
  ctx.fillStyle = '#fff'; ctx.beginPath(); ctx.roundRect(30, 145, 940, 790, 14); ctx.fill();
  const main = await loadImage(path.join(root, 'oni', 'oni-corrected-reference-3-claws.png'));
  let b = fit(main.width, main.height, 45, 160, 910, 665); ctx.drawImage(main, b.x, b.y, b.w, b.h);
  ctx.fillStyle = '#17171d'; ctx.beginPath(); ctx.roundRect(54, 832, 892, 82, 8); ctx.fill();
  ctx.font = '800 25px Arial'; ctx.fillStyle = '#fff'; ctx.fillText('APPROVED CORRECTION: 3 CLAWS — RIGHT HAND ONLY', 78, 868);
  ctx.font = '20px Arial'; ctx.fillStyle = '#aeb3c0'; ctx.fillText('Left hand wrapped and clawless · two swords stay sheathed on back', 78, 898);
  ctx.font = '800 32px Arial'; ctx.fillStyle = '#fff'; ctx.fillText('NON-NEGOTIABLE CONTINUITY', 1010, 178);
  ctx.fillStyle = '#202027'; ctx.beginPath(); ctx.roundRect(1010, 200, 850, 350, 12); ctx.fill();
  const cropBuf = await sharp(path.join(root, 'oni', 'oni-corrected-reference-3-claws.png')).extract({left:430,top:20,width:470,height:520}).png().toBuffer();
  const close = await loadImage(cropBuf); b = fit(close.width, close.height, 1030, 215, 430, 315); ctx.drawImage(close, b.x, b.y, b.w, b.h);
  ctx.font = '800 30px Arial'; ctx.fillStyle = '#ffbd2e'; ctx.fillText('COUNT: 1 · 2 · 3', 1490, 260);
  ctx.font = '700 23px Arial'; ctx.fillStyle = '#fff'; ctx.fillText('RIGHT HAND ONLY', 1490, 305);
  ctx.font = '21px Arial'; ctx.fillStyle = '#d6d8df'; ctx.fillText('Three long, separated,', 1490, 342); ctx.fillText('dark-gunmetal blades.', 1490, 371);
  ctx.font = '700 21px Arial'; ctx.fillStyle = '#ff5267'; ctx.fillText('Never 4. Never 5.', 1490, 417); ctx.fillText('Never mirror the claw.', 1490, 451);
  ctx.fillStyle = '#202027'; ctx.beginPath(); ctx.roundRect(1010, 575, 850, 360, 12); ctx.fill();
  ctx.font = '800 28px Arial'; ctx.fillStyle = '#fff'; ctx.fillText('ASSET CHECKLIST', 1040, 620);
  const checks = ['Exactly three claws in every frame','Claw remains on right hand only','Left hand wrapped and clawless','White horned mask and red eye preserved','Two swords remain sheathed on back','No extra limbs, claws, weapons, or effects'];
  ctx.font = '22px Arial'; checks.forEach((t,i)=>{ const y=670+i*45; ctx.strokeStyle='#ff334d';ctx.lineWidth=3;ctx.strokeRect(1040,y-21,19,19);ctx.fillStyle='#e8e9ed';ctx.fillText(t,1084,y-3); });
  ctx.fillStyle='#202027';ctx.fillRect(0,970,1900,150);ctx.font='800 27px Arial';ctx.fillStyle='#ffbd2e';ctx.fillText('LOCK ACTION',34,1015);
  ctx.font='22px Arial';ctx.fillStyle='#e8e9ed';ctx.fillText('Right claw traps the opponent’s edge at a fixed high 45° contact for frames 01–08.',34,1055);
  ctx.font='20px Arial';ctx.fillStyle='#aeb3c0';ctx.fillText('Frames 09–10 resolve WIN / LOSE. The back swords never become the binding weapon.',34,1090);
  fs.writeFileSync(path.join(root, 'oni', 'oni-CARD-3-claws.png'), canvas.toBuffer('image/png'));
}

Promise.all([review(), oniCard()]).catch(e => { console.error(e); process.exit(1); });
