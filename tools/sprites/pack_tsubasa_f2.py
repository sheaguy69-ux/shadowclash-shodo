#!/usr/bin/env python3
# ponytail: append Tsubasa Form 2 (attacks 190-237, locomotion 238-287) to the sheet.
# Same compose transforms the owner approved in the GIFs: attacks anchor the settle
# beat to 193 (hamstring 148), locomotion rows use the ink-area cross-row scale.
import numpy as np, os, glob, json
from PIL import Image

REPO='/Users/anthonyguy/Desktop/SHADOWCLASH-RECOVERED'
ATK=os.path.join(REPO,'media/pages/tsubasa-form2/cut')
LOCO=os.path.join(REPO,'media/pages/tsubasa-form2-loco/cut')
SHEET=os.path.join(REPO,'web/assets/sprites/tsubasa.png')
JSON=os.path.join(REPO,'web/assets/sprites/tsubasa.json')
CW,CH,FOOTY=301,320,312

def bodyH(img):
    a=np.array(img)[...,3]>0
    ys=np.where(a.any(axis=1))[0]
    return ys[-1]-ys[0]+1
def ink(img): return int((np.array(img)[...,3]>0).sum())
def load(d):
    fs=sorted(glob.glob(os.path.join(d,'b*.png')),key=lambda p:int(os.path.basename(p)[1:-4]))
    return [Image.open(p) for p in fs]
def cell_of(f,s):
    fs=f.resize((int(round(f.width*s)),int(round(f.height*s))),Image.LANCZOS)
    a=np.array(fs)[...,3]>0
    ys,xs=np.where(a)
    band=a[max(0,a.shape[0]-int(a.shape[0]*.12)):,:]
    bx=np.where(band.any(axis=0))[0]
    fx=(bx.min()+bx.max())/2 if len(bx) else (xs.min()+xs.max())/2
    cell=Image.new('RGBA',(CW,CH),(0,0,0,0))
    cell.paste(fs,(int(round(CW/2-fx)), FOOTY-ys.max()-1),fs)
    return cell

new=[]   # (frame_name, cell_image)

# --- attacks: settle-beat anchor, exactly as the approved GIFs ---
ATK_MAP=[('page1-backhand-rake','f2_light1'),('page2-inward-rip','f2_light2'),
         ('page3-scissor-cut','f2_light3'),('page4-turning-slash','f2_heavy1'),
         ('page5-double-drive','f2_heavy2'),('page6-the-answer','f2_heavy3'),
         ('page7-hamstring-rake','f2_clow'),('page8-the-read','f2_parry')]
for d,key in ATK_MAP:
    figs=load(os.path.join(ATK,d))
    s=(148 if 'hamstring' in d else 193)/bodyH(figs[-1])
    for i,f in enumerate(figs,1): new.append((f'{key}_{i}',cell_of(f,s)))

# --- locomotion: ink-area cross-row scale, idle pinned to 193 ---
LOCO_MAP=[('page9-idle','f2_idle'),('page10-run','f2_run'),('page11-jump','f2_jump'),
          ('page12-crouch','f2_crouch'),('page13-dash','f2_dash'),('page14-roll','f2_roll'),
          ('page15-land','f2_land'),('page16-block','f2_block')]
idle=load(os.path.join(LOCO,'page9-idle'))
s_idle=193/max(bodyH(f) for f in idle)
target=np.median([ink(f) for f in idle])*s_idle**2
for d,key in LOCO_MAP:
    figs=load(os.path.join(LOCO,d))
    s=s_idle if d=='page9-idle' else float(np.sqrt(target/np.median([ink(f) for f in figs])))
    for i,f in enumerate(figs,1): new.append((f'{key}_{i}',cell_of(f,s)))

assert len(new)==98, len(new)

sheet=Image.open(SHEET)
assert sheet.size==(190*CW,CH), sheet.size
orig=np.array(sheet)
out=Image.new('RGBA',((190+98)*CW,CH),(0,0,0,0))
out.paste(sheet,(0,0))
for k,(name,cell) in enumerate(new):
    out.paste(cell,((190+k)*CW,0))
# append-only law: original region byte-identical
assert np.array_equal(np.array(out)[:, :190*CW], orig), 'original cells changed!'
out.save(SHEET)
check=np.array(Image.open(SHEET))
assert np.array_equal(check[:, :190*CW], orig), 'post-save mismatch!'

j=json.load(open(JSON))
for k,(name,_) in enumerate(new):
    assert name not in j['frames'], name
    j['frames'][name]=190+k
j['cols']=190+98
json.dump(j,open(JSON,'w'),indent=1)
print('packed', len(new), 'cells; sheet', out.size, '; cols', j['cols'])
print('first/last:', new[0][0], 190, '->', new[-1][0], 287)
