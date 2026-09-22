#!/usr/bin/env python3
"""Chudan board: there is NO grey opponent on it - all 8 beats are the
Executioner alone (measured: every one of the 8 figure components carries
1,400-2,200 orange pixels).  The only thing on the board that is not him is
the ENEMY'S INCOMING CUT - a black ink-brush slash in beats 4 and 5.  This
cuts that, and only that.

Beat 4's slash is already its own component.  Beat 5's runs into the parry
spark, whose black spikes are the same value, so a barrier is dropped across
the slash just above the spark: the slash goes, the spark stays - the spark
is HIS, it is the deflection landing."""
import numpy as np
from PIL import Image
from scipy import ndimage

SRC="exec-CHUDAN-no-kamae-board-8f.png"
DST="exec-CHUDAN-no-kamae-board-8f-NOENEMY.png"
im=np.asarray(Image.open(SRC).convert("RGB")).astype(int)
H,W,_=im.shape
mx=im.max(2); mn=im.min(2); sat=mx-mn
ink=mx<246; ach=ink&(sat<=45)
ys,xs=np.mgrid[0:H,0:W]
def band(x0,y0,x1,y1,r):
    dx,dy=x1-x0,y1-y0; L2=float(dx*dx+dy*dy)
    t=np.clip(((xs-x0)*dx+(ys-y0)*dy)/L2,0,1)
    return ((xs-(x0+t*dx))**2+(ys-(y0+t*dy))**2)<=r*r

# the cut line sits perpendicular to the slash, just above the spark
bar=band(873,528,957,562,2)
lab,_=ndimage.label(ach&~bar)
mask=np.zeros((H,W),bool)
for name,(sx,sy) in {"b4":(725,451),"b5":(948,464)}.items():
    l=lab[sy,sx]; assert l, f"{name}: seed off ink"
    mask|=(lab==l); print(f"  {name} slash {int((lab==l).sum()):6d} px")

# the brush throws a trail of splatter dots that the flood cannot reach - they
# are their own little components.  Anything small and grey inside the two slash
# footprints is splatter; he is one big component and never qualifies.
zone=np.zeros((H,W),bool); zone[365:525,670:800]=True; zone[375:645,840:1005]=True
lz,nz=ndimage.label(ach)
szs=ndimage.sum(np.ones_like(lz),lz,range(1,nz+1))
# ...but the parry spark's black spikes are ALSO small grey components, and the
# spark is HIS - it is the deflection landing.  Sweep only what sits well clear
# of any orange.
yy,xx=np.mgrid[-35:36,-35:36]; disk=(xx*xx+yy*yy)<=35*35
far=~ndimage.binary_dilation(ink&(sat>45),disk)
for i in np.unique(lz[zone&ach]):
    if i==0 or szs[i-1]>=400: continue
    c=(lz==i)
    if not far[c].all(): continue
    mask|=c
mask=ndimage.binary_dilation(mask,np.ones((3,3),bool))&ink
out=im.copy(); out[mask]=255
# the pale rim sits at 240-251 against 253-255 paper, above any ink threshold
lum=0.299*im[:,:,0]+0.587*im[:,:,1]+0.114*im[:,:,2]
ink2=np.asarray(out).max(2)<246
dark=ink2&(lum<130)
near=ndimage.binary_dilation(mask,np.ones((17,17),bool))
rim=(np.asarray(out).max(2)<252)&(lum>=140)&(sat<=30)&near& \
    ~ndimage.binary_dilation(dark,np.ones((9,9),bool))
out[rim]=255; mask|=rim
print(f"  rim   {int(rim.sum()):6d} px")

# nothing outside the two slash footprints may move
ok=ndimage.binary_dilation(zone,np.ones((21,21),bool))
stray=int((mask&~ok).sum()); print("changed outside the two slash boxes:",stray)
assert stray==0
warm=(sat>60)&(im[:,:,0]>im[:,:,2]+30)&ink
print("orange px changed: %d of %d"%(int((mask&warm).sum()),int(warm.sum())))
assert int((mask&warm).sum())==0, "an orange pixel of his moved"
# every one of the 8 figures must keep all of its own ink
lf,nf=ndimage.label(ndimage.binary_closing(ink,np.ones((3,3),bool)))
figs=[i for i in np.unique(lf[warm]) if i and (lf==i).sum()>=8000]
print("figure components:",len(figs),"| ink lost per figure:",
      [int((mask&(lf==i)).sum()) for i in figs])
Image.fromarray(out.astype(np.uint8)).save(DST)
print("total %d px (%.2f%% of ink) -> %s"%(mask.sum(),100*mask.sum()/ink.sum(),DST))
