#!/usr/bin/env python3
# ponytail: give Form 2 its OWN dash-cut and air-cut rows WITHOUT new art.
#
# rgrush (88-93) and divecut (76-81) are Form 1 cells that Form 2 borrows. Form 1
# is drawn at 1.55x Form 2's ink at the same 193px body height, so borrowing them
# makes Tsubasa visibly BULK UP on those two moves. The cells cannot be edited in
# place — they are shared with Form 1 and the sheet is append-only — so this
# appends DOWNSCALED copies matched to the Form 2 attack band. Downscale only:
# both factors are < 1, nothing is interpolated up.
import json, numpy as np
from PIL import Image

REPO='/Users/anthonyguy/SHADOWCLASH-RECOVERED'
SHEET=f'{REPO}/web/assets/sprites/tsubasa.png'
JSON=f'{REPO}/web/assets/sprites/tsubasa.json'
CW,CH,FOOTY=301,320,311

sheet=Image.open(SHEET); j=json.load(open(JSON)); F=j['frames']
cols=j['cols']
assert sheet.size==(cols*CW,CH), sheet.size
orig=np.array(sheet)

def cell(c): return sheet.crop((c*CW,0,(c+1)*CW,CH))
def ink(im): return int((np.array(im)[...,3]>0).sum())

# target = the Form 2 ATTACK band (these are attack rows, not idles)
atk_rows=['f2_light1','f2_light2','f2_light3','f2_heavy1','f2_heavy2','f2_heavy3',
          'f2_clow','f2_parry']
atk_ink=[ink(cell(F[f'{r}_{i}'])) for r in atk_rows for i in range(1,7)]
target=float(np.median(atk_ink))
print(f'Form 2 attack band: median ink {target:.0f}  (range {min(atk_ink)}-{max(atk_ink)})')

def build(src_key, out_key, n=6):
    src=[cell(F[f'{src_key}{i}']) for i in range(1,n+1)]
    cur=float(np.median([ink(s) for s in src]))
    s=float(np.sqrt(target/cur))                     # ONE uniform scale for the row
    assert s < 1.0, f'{src_key} would UPSCALE ({s:.3f}) — refused'
    out=[]
    for im in src:
        a=np.array(im)[...,3]>0
        ys,xs=np.where(a)
        crop=im.crop((xs.min(),ys.min(),xs.max()+1,ys.max()+1))
        w,h=max(1,int(round(crop.width*s))),max(1,int(round(crop.height*s)))
        fs=crop.resize((w,h),Image.LANCZOS)
        aa=np.array(fs)[...,3]>0
        yy,xx=np.where(aa)
        band=aa[max(0,aa.shape[0]-int(aa.shape[0]*.12)):,:]
        bx=np.where(band.any(axis=0))[0]
        fx=(bx.min()+bx.max())/2 if len(bx) else (xx.min()+xx.max())/2
        c=Image.new('RGBA',(CW,CH),(0,0,0,0))
        c.paste(fs,(int(round(CW/2-fx)), FOOTY-yy.max()-1),fs)
        out.append(c)
    print(f'{src_key} -> {out_key}: ink {cur:.0f} -> {np.median([ink(o) for o in out]):.0f}, scale {s:.3f}')
    return out

new=[]
for src,dst in [('rgrush','f2_dashcut'),('divecut','f2_air')]:
    for i,c in enumerate(build(src,dst),1): new.append((f'{dst}_{i}',c))

out=Image.new('RGBA',((cols+len(new))*CW,CH),(0,0,0,0))
out.paste(sheet,(0,0))
for k,(name,c) in enumerate(new): out.paste(c,((cols+k)*CW,0))
assert np.array_equal(np.array(out)[:, :cols*CW], orig), 'existing cells changed!'
out.save(SHEET)
assert np.array_equal(np.array(Image.open(SHEET))[:, :cols*CW], orig), 'post-save mismatch!'

for k,(name,_) in enumerate(new):
    assert name not in F, name
    F[name]=cols+k
j['cols']=cols+len(new)
json.dump(j,open(JSON,'w'),indent=1)
print(f'appended {len(new)} cells {cols}-{cols+len(new)-1}; cols {j["cols"]}')
