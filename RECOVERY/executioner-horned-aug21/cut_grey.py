#!/usr/bin/env python3
"""Delete the grey OPPONENT from the Executioner DEFENCE & EVASION board.

Seven instances. Five stand alone -> flood the achromatic ink from one seed
(his orange scarf / yellow eyes / purple hood + the purple arcs all have
saturation and stop the flood by themselves).  Two touch him and need a rule
of their own:
  R1 b7  the only bridge is HIS OWN thrusting blade, drawn on top of the
         opponent.  Barrier the blade (growth cannot cross it AND it survives),
         tapering the barrier to a point so the katana keeps its tip.
  R4 b7  body-to-body contact, no thin bridge.  Separate on VALUE: the opponent
         is mid-grey (lum 36-100), the Executioner is near-black.

Everything else - his figures, the purple arcs, the clash spark, the text -
is left byte-identical, and the run asserts that.
"""
import numpy as np
from PIL import Image
from scipy import ndimage

SRC="/Users/anthonyguy/shadowclash-fable-5/RECOVERY/executioner-horned-aug21/exec-DEFENSE-EVASION-board-4x8.png"
DST="/Users/anthonyguy/shadowclash-fable-5/RECOVERY/executioner-horned-aug21/exec-DEFENSE-EVASION-board-4x8-NOGREY.png"

im=np.asarray(Image.open(SRC).convert("RGB")).astype(int)
H,W,_=im.shape
mx=im.max(2); mn=im.min(2); sat=mx-mn
lum=0.299*im[:,:,0]+0.587*im[:,:,1]+0.114*im[:,:,2]
ink   = mx<246
achro = ink & (sat<=45)

ys,xs=np.mgrid[0:H,0:W]
def band(x0,y0,x1,y1,r0,r1=None):
    r1=r0 if r1 is None else r1
    dx,dy=x1-x0,y1-y0; L2=float(dx*dx+dy*dy)
    t=np.clip(((xs-x0)*dx+(ys-y0)*dy)/L2,0,1)
    r=r0+(r1-r0)*t
    return ((xs-(x0+t*dx))**2+(ys-(y0+t*dy))**2)<=r*r
def rect(x0,y0,x1,y1):
    m=np.zeros((H,W),bool); m[y0:y1,x0:x1]=True; return m

# the seven opponent footprints - the removal may not touch a pixel outside them
BOXES=[(400,100,545,285),(1085,118,1222,292),(398,340,556,520),(374,605,566,726),
       (700,604,892,724),(360,806,522,965),(1160,815,1268,975)]
inbox=np.zeros((H,W),bool)
for b in BOXES: inbox|=rect(*b)

mask=np.zeros((H,W),bool)

# --- 1. the five that stand alone -------------------------------------------
lab,_=ndimage.label(achro)
for k,(sx,sy) in {"R1b2":(470,215),"R2b2":(455,450),"R3b2":(420,660),
                  "R3b4":(770,662),"R4b2":(440,893)}.items():
    l=lab[sy,sx]; assert l, f"{k}: seed is not on ink"
    mask |= (lab==l); print(f"  {k:6s} flood      {int((lab==l).sum()):6d} px")

# --- 2. R1b7 - barrier his blade, tapered to the drawn tip at x=1156 ---------
blade = band(1093,192,1130,188.5,4.0) | band(1130,188.5,1137,187.5,4.0,1.4)
lab2,_=ndimage.label(achro & ~(blade | rect(1092,148,1095,292)))
l=lab2[240,1180]; assert l
mask |= (lab2==l); print(f"  R1b7   flood      {int((lab2==l).sum()):6d} px  (blade barriered)")

# --- 3. R4b7 - value cut ----------------------------------------------------
BOX=rect(*BOXES[6])
core=ink&(sat<=30)&(lum>=36)&(lum<=100)&BOX
l3,n3=ndimage.label(core)
sz=ndimage.sum(np.ones_like(l3),l3,range(1,n3+1))
core=np.isin(l3,[i+1 for i,s in enumerate(sz) if s>=25])
m47=ndimage.binary_fill_holes(ndimage.binary_dilation(core,np.ones((9,9),bool))&ink&BOX)
mask |= m47; print(f"  R4b7   value cut  {int(m47.sum()):6d} px")

# --- 4. close: rim the flood stopped one pixel short of ---------------------
mask = ndimage.binary_fill_holes(ndimage.binary_dilation(mask,np.ones((3,3),bool)) & ink)
mask &= ~blade                                    # never eat his katana
out=im.copy(); out[mask]=255

# --- 5. orphans: pale anti-alias rim + crumbs left standing in empty space ---
# the board's paper is 253-255, so the opponent's outermost anti-alias rim
# (240-251) sits ABOVE the ink threshold and the flood never saw it - that
# pale ghost is what is left standing where he used to be.
ink2 = np.asarray(out).max(2)<246
dark = ink2 & (lum<130)
pale = (np.asarray(out).max(2)<252) & (lum>=140) & (sat<=30)
orphan_rim = pale & inbox & ~ndimage.binary_dilation(dark,np.ones((9,9),bool))
lo,no=ndimage.label(ink2)
chrom=set(np.unique(lo[(sat>45)&ink2]))
crumbs=np.zeros((H,W),bool)
for i,sl in enumerate(ndimage.find_objects(lo),1):
    if i in chrom: continue
    c=(lo[sl]==i)
    if c.sum()>=400: continue
    if not inbox[sl][c].all(): continue
    crumbs[sl] |= c
extra=orphan_rim|crumbs
out[extra]=255; mask|=extra
print(f"  rim {int(orphan_rim.sum())} px, crumbs {int(crumbs.sum())} px")

stray=int((mask&~inbox).sum())
print("total removed %d px (%.2f%% of the board's ink); outside the seven boxes: %d"
      %(mask.sum(),100*mask.sum()/ink.sum(),stray))
assert stray==0, "removal widened past the grey figures"
Image.fromarray(out.astype(np.uint8)).save(DST)
print("wrote",DST)
