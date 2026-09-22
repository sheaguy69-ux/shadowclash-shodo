#!/usr/bin/env python3
"""Pose-fidelity gate: does each generated frame actually FOLLOW its pose guide?

Catches pose-collapse (model repeats the identity ref's standing pose and
ignores the guide) — the failure class that shipped 33 identical Tsubasa
frames. Frame-level canon/floater gates cannot see it by design.

Per frame:  guide-IoU   = overlap of bbox-normalized ink silhouettes (guide vs output)
            idle-drift  = similarity of this output to the set's own idle output
Verdict POSE-FAIL when guide-IoU < --min-iou (default 0.55) AND the frame is
not idle-family. Set verdict COLLAPSED when mean pairwise variance < --min-var.
Usage: pose_gate.py <model_guides_dir> <raw_dir> [--min-iou 0.55] [--min-var 0.13]
Exit 1 on any POSE-FAIL or set collapse. --selftest runs synthetic checks.
"""
import sys, pathlib, itertools
import numpy as np
from PIL import Image

def ink(path, size=(96, 128)):
    im = Image.open(path).convert("L")
    m = (np.array(im) < 200)
    ys, xs = np.where(m)
    if len(ys) == 0: return np.zeros(size[::-1], bool)
    crop = m[ys.min():ys.max()+1, xs.min():xs.max()+1]
    return np.array(Image.fromarray(crop.astype(np.uint8)*255).resize(size)) > 127

def iou(a, b):
    u = (a | b).sum()
    return float((a & b).sum() / u) if u else 0.0

def run(gdir, rdir, min_iou=0.55, min_var=0.13):
    gdir, rdir = pathlib.Path(gdir), pathlib.Path(rdir)
    fails, rows, sils = [], [], {}
    names = sorted(p.stem for p in rdir.glob("*.png"))
    for n in names:
        sils[n] = ink(rdir / f"{n}.png")
    idle = sils.get("idle")
    for n in names:
        g = gdir / f"{n}.png"
        score = iou(ink(g), sils[n]) if g.exists() else None
        drift = iou(idle, sils[n]) if idle is not None and n != "idle" else None
        idle_family = n.startswith("idle") or n in ("block", "hurt", "kneel")
        bad = (drift is not None and drift > 0.92 and not idle_family) or \
              (score is not None and score < 0.35 and not idle_family)
        rows.append((n, score, drift, bad))
        if bad: fails.append(n)
    var = np.mean([np.mean(np.abs(sils[a].astype(float) - sils[b].astype(float)))
                   for a, b in itertools.combinations(names[:28], 2)]) if len(names) > 1 else 1.0
    for n, s, d, bad in rows:
        print(f"{n:18s} guideIoU={'--' if s is None else f'{s:.3f}'}  idleSim={'--' if d is None else f'{d:.3f}'}  {'POSE-FAIL' if bad else 'ok'}")
    collapsed = var < min_var
    print(f"SET pose-variance={var:.4f} {'COLLAPSED' if collapsed else 'ok'}  pose-fails={len(fails)}: {','.join(fails)}")
    return 1 if (fails or collapsed) else 0

def selftest():
    import tempfile
    t = pathlib.Path(tempfile.mkdtemp())
    (t/"g").mkdir(); (t/"r").mkdir()
    def blob(p, box):
        a = np.full((200,150), 255, np.uint8); a[box[0]:box[1], box[2]:box[3]] = 0
        Image.fromarray(a).save(p)
    blob(t/"g"/"idle.png", (40,180,50,100)); blob(t/"r"/"idle.png", (40,180,50,100))
    blob(t/"g"/"jump.png", (10,80,30,120));  blob(t/"r"/"jump.png", (40,180,50,100))  # ignored guide -> idleSim 1.0
    blob(t/"g"/"roll.png", (60,120,20,130)); blob(t/"r"/"roll.png", (60,120,20,130))  # followed
    assert run(t/"g", t/"r") == 1
    print("SELF_TEST_OK (jump flagged, roll passed)")

if __name__ == "__main__":
    if "--selftest" in sys.argv: selftest(); sys.exit(0)
    a = [x for x in sys.argv[1:] if not x.startswith("--")]
    kw = {}
    if "--min-iou" in sys.argv: kw["min_iou"] = float(sys.argv[sys.argv.index("--min-iou")+1])
    if "--min-var" in sys.argv: kw["min_var"] = float(sys.argv[sys.argv.index("--min-var")+1])
    sys.exit(run(a[0], a[1], **kw))
