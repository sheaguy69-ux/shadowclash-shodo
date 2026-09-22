#!/usr/bin/env python3
"""Verify the game zoom: world size + fighter screen footprint."""
import pathlib, sys
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from watch_game import drive
REPO = pathlib.Path(__file__).resolve().parents[1]
OUT = REPO / 'media/audit/zoom'
PROBE = r'''
const frame = () => new Promise(r => requestAnimationFrame(r));
gameMode = '2p'; cpuMode = false; attractMode = false;
p1Pick = 8; p2Pick = 0; stagePick = 'bamboo'; startNewGame(); roundIntroTimer = 0;
matchActive = true;
await frame(); await frame(); await frame();
const R = {};
R.canvasW = canvas.width; R.canvasH = canvas.height; R.groundY = GROUND_Y;
R.gameZoom = GAME_ZOOM;
R.p1x = player1.x; R.p1y = player1.y; R.p1w = player1.width; R.p1h = player1.height;
R.p2x = player2.x; R.p2y = player2.y;
// fighter visual height (Oni idle ink, scaled) = cellInk height * S
const man = SPRITES['oni'];
R.oniScale = man.scale;
R.oniCellInkH = (() => { const b = cellInk(man, man.frames.idle); return b.y1 - b.y0 + 1; })();
R.oniScreenH = Math.round((cellInk(man, man.frames.idle).y1 - cellInk(man, man.frames.idle).y0 + 1) * man.scale);
return JSON.stringify(R);
'''
def main():
    R = drive([{"wait": 3.2}, {"key": "Space"}, {"wait": 0.8}, {"eval": PROBE, "label": "ZOOM"}], OUT, "ZOOM")
    print("GAME ZOOM probe:")
    for k in ("gameZoom","canvasW","canvasH","groundY","p1x","p1y","p1w","p1h","p2x","p2y","oniScale","oniCellInkH","oniScreenH"):
        print(f"  {k} = {R.get(k)}")
    # oni world height / world height = % of screen
    try:
        pct = R['oniScreenH'] / R['canvasH'] * 100
        print(f"  Oni visual height = {pct:.1f}% of screen height")
    except Exception: pass
    return 0
if __name__ == '__main__':
    sys.exit(main())