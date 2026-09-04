const VYS=[-450,-380,-300,-260,-200,-120,-75,-40,0,40,75,120,200,260,300,340,380,430,500,600];
const PROG=[0,0.2,0.4,0.6,0.8,0.95];
const DIRS=[null,'up','down','fwd','back'];
const KICKS=[null,'down','back','fwd','up'];
const STS=Object.values(STATE);
const out={};
for(const spec of NINJA_ROSTER){
  const man=SPRITES[spec.name.toLowerCase()];
  if(!man||!man.ready){out[spec.name]={err:'not ready'};continue;}
  const F=man.frames;
  const hit={};
  const base=player1;
  for(const st of STS)for(const vy of VYS)for(const ad of DIRS)for(const aa of [false,true])
  for(const kk of KICKS)for(const pr of PROG)for(const ch of [false,true]){
    const p=Object.assign(Object.create(Object.getPrototypeOf(base)),base);
    p.spec=spec; p.isGrounded=false; p.state=st; p.vy=vy; p.vx=0;
    p.attackDir=ad; p.attackAir=aa; p.kickKind=kk; p.chudan=ch;
    p.attackAnim={start:animClock*1000-pr*600,dur:600}; p.animPhase=0;
    p.recoveryTimer=0; p.recoveryTotal=0; p.stunTimer=0; p.rollTimer=0;
    p.grappleT=0; p.tumbleT=0; p.landT=0; p.dashTimer=0; p.jumpDir=null;
    let i; try{i=spriteFrameIndex(p,F);}catch(e){continue;}
    if(typeof i!=='number'||!isFinite(i))continue;
    if(hit[i]===undefined) hit[i]=st+'|vy'+vy+'|d'+ad+'|air'+aa+'|k'+kk+'|p'+pr+'|c'+ch;
  }
  const rev={};
  for(const k in F){const v=F[k]; if(rev[v]===undefined)rev[v]=[]; rev[v].push(k);}
  out[spec.name]={cols:man.cols,cells:Object.keys(hit).map(Number).sort((a,b)=>a-b),
                  how:hit, names:Object.fromEntries(Object.keys(hit).map(c=>[c,(rev[c]||[]).join(',')]))};
}
return JSON.stringify(out);
