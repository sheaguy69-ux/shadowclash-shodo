#!/usr/bin/env python3
"""Key + pack 4 extracted i2v run frames into a ninja's sprite sheet as the
size-consistent run cycle (nrun_i1..i4). Frames come from gen_run_i2v.py's
side-profile window; keying uses fuzz 42% to strip the white bg AND the clip's
soft drop-shadow (25% leaves a grey blob under the feet).

Usage: python3 pack_i2v_run.py <name> <frames_dir> <f1> <f2> <f3> <f4>
  e.g. python3 pack_i2v_run.py mizu <dir>/mizu/frames 6 9 12 15
Packs with MATCH_HEIGHT=nrun1 so all four match the existing run height -> 0% wobble.
"""
import sys, subprocess, tempfile, pathlib, os

name, fdir = sys.argv[1], sys.argv[2]
picks = sys.argv[3:7]
HERE = pathlib.Path(__file__).resolve().parent
REPO = HERE.parent.parent
tmp = pathlib.Path(tempfile.mkdtemp())

for i, fr in enumerate(picks, 1):
    src = f"{fdir}/f_{int(fr):03d}.png"
    dst = tmp / f"nrun_i{i}.png"
    subprocess.run(["magick", src, "-alpha", "set", "-bordercolor", "white", "-border", "1",
                    "-fuzz", "42%", "-fill", "none", "-floodfill", "+0+0", "white",
                    "-shave", "1x1", "-trim", "+repage", str(dst)], check=True)

env = dict(os.environ, MATCH_HEIGHT="nrun1")
subprocess.run([sys.executable, str(HERE / "extend_sheet.py"), name, str(tmp),
                str(HERE / "base" / f"{name}.png"), str(REPO / "web" / "assets" / "sprites"),
                "nrun_i1", "nrun_i2", "nrun_i3", "nrun_i4"], check=True, env=env)
print(f"packed {name} i2v run from frames {picks}")
