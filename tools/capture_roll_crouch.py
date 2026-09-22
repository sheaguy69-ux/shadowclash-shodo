#!/usr/bin/env python3
"""Owner-review capture: the crouch and the ground roll, AS THE GAME DRAWS THEM.

Screenshots the live canvas on 9100 beat by beat while the engine holds each state, so
the strips and GIFs are the shipped render — the drawn cell plus every transform on top
of it — and not a Python re-render of the sheet. A static re-render cannot see a ghost,
and it cannot see the spin.

A red ground line is drawn at the fighter's own foot plane on every panel: that is the
line the whole job is about, and it makes floating visible instead of arguable.

Out: media/roll-crouch-2026-08-13/<fighter>-{crouch,roll}.{png,gif} + CONTACT.png
⛔ Never starts a server.
"""
import os
import pathlib

import sys
import urllib.request

from PIL import Image, ImageDraw
from playwright.sync_api import sync_playwright

# Two designated ports are law (AGENTS.md rule 8). Same override every harness uses:
#   SHADOWCLASH_URL=http://localhost:9101/index.html python3 tools/capture_roll_crouch.py
URL = os.environ.get('SHADOWCLASH_URL', 'http://127.0.0.1:9100/').replace('index.html', '')
OUT = pathlib.Path('media/roll-crouch-2026-08-13')
PAIRS = [('Executioner', 'Mizu'), ('Shin', 'Tsubasa'), ('Ember', 'Kael'), ('Mokurai', 'Exile')]
NO_ROLL = {'mokurai', 'exile'}
PANEL = (170, 170)      # crop around the fighter, in canvas px

POSE = """
([who, mode, i, n]) => {
  const p = who === 1 ? player1 : player2;
  const q = who === 1 ? player2 : player1;
  // ⛔ FREEZE THE SIM. gameLoop's pause branch still calls drawScene(), so a paused
  // match renders the pose I set and nothing else moves — without it the CPUs kept
  // fighting between shots and the first capture came back with the opponent walking
  // through frame and a slash burst over the fighter being reviewed.
  paused = true;
  // ⛔ RESET BOTH TO THEIR SPAWNS EVERY BEAT — never shove the opponent "out of the way".
  // Parking them at p.x + 2400 ACCUMULATED: posing P1 threw P2 to +2400, then posing P2
  // threw P1 to +4800, and the pair walked off the board, which is why every player-2
  // strip came back black while every player-1 strip was fine. The spawns are already
  // ~500 canvas px apart and the crop is 170 wide, so nobody needs moving.
  if (!window.__home) window.__home = { a: player1.x, b: player2.x };   // fallback only
  player1.x = window.__home.a; player2.x = window.__home.b;
  q.vx = 0; q.vy = 0; q.state = STATE.IDLE; q.attackAnim = null;
  particles.length = 0; slashes.length = 0; smokeFields.length = 0; logs.length = 0;
  screenShakeAmount = 0; screenShakeDX = 0; screenShakeDY = 0;
  flashAmount = 0; blackoutAmount = 0; hitstopRemaining = 0;
  p.vx = 0; p.vy = 0; p.isGrounded = true;
  p.tumbleT = 0; p.landT = 0; p.meditateTimer = 0; p.sakate = false;
  p.attackAnim = null; p.landSquash = 0; p.stunTimer = 0;
  p.fxSched && (p.fxSched.length = 0);
  p.hitboxes && (p.hitboxes.length = 0);
  // hitFlashT is the victim's white blink. Freezing the sim mid-decay froze the
  // blink too, and the Executioner's whole crouch strip came back as a white
  // silhouette. Cosmetic, so clear it on both fighters.
  p.hitFlashT = 0; q.hitFlashT = 0;
  p.invulnTimer = 0; p.hurtFlash = 0; p.parryFlashTimer = 0;
  if (mode === 'crouch') {
    p.state = STATE.CROUCH; p.rollTimer = 0;
    // beat i of n: first three ride the sink clock, the last is the breath beat
    p.crouchAt = animClock - (i < 3 ? (i + 0.5) / 3 * CROUCH_SINK_T : 9);
    p.animPhase = i === 3 ? 3 : 0;
  } else {
    p.state = STATE.ROLL;
    p.rollTimer = ROLL_TIME * (1 - (i + 0.5) / n);
  }
  return spriteFrameIndex(p, SPRITES[p.spec.name.toLowerCase()].frames);
}
"""

# ⛔ READ THE ANCHOR FROM THE FRAME THAT ACTUALLY DREW, NOT FROM ENGINE STATE READ EARLIER.
# Two separate bugs taught this. First: reading a camera transform BEFORE the pose rendered
# gave the previous frame's value, and parking the opponent far away moved the camera, so
# the crop pointed somewhere else — four black strips, always player 2, because posing him
# is the case that moves player 1. Second: the engine global this used to read was later
# DELETED outright by another agent and the capture died with a ReferenceError. Both are
# fixed by taking the anchor out of the draw call itself. Paused, nothing changes between
# the draw and the screenshot.
WHERE = """
(who) => {
  // ⛔ THE FEET ARE THE MATRIX ORIGIN. drawSprite works in a feet-anchored local frame,
  // so whatever transform it drew this fighter under maps local (0,0) to his soles —
  // the CTM's (e, f) IS the foot point, in canvas px. This used to read the engine's
  // `camMatrix` global, which another agent DELETED from the engine mid-session; the
  // capture died with a ReferenceError. Deriving it from the draw call needs no global
  // and cannot go stale that way again.
  const p = who === 1 ? player1 : player2;
  const sw = SPRITES[p.spec.name.toLowerCase()].img.width;
  const hits = (window.__ctm || []).filter(m => m.sw === sw);
  const last = hits[hits.length - 1];
  return last ? { x: last.e, y: last.f } : null;
}
"""


def main():
    try:
        if urllib.request.urlopen(URL, timeout=5).status != 200:
            raise OSError
    except Exception:
        sys.exit('⛔ 9100 is not serving the game.  python3 tools/serve.py 9100 web')
    OUT.mkdir(parents=True, exist_ok=True)

    with sync_playwright() as pw:
        b = pw.chromium.launch(
            headless=True,
            executable_path='/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',
            args=['--mute-audio', '--disable-background-timer-throttling',
                  '--disable-renderer-backgrounding', '--no-first-run'])
        # ⛔ THE CANVAS IS 1280x1000 INTERNAL and lays out `w-full h-auto` beside a
        # 265px controller panel, so on a 720-tall viewport its CSS box runs off the
        # bottom of the page — a screenshot clipped to that box came back BLACK below
        # the fold, which is where the fighter stands. Give the page room for the whole
        # element and map through its real bounding box instead of assuming 1280.
        pg = b.new_page(viewport={'width': 1600, 'height': 1400}, device_scale_factor=2)
        pg.goto(URL, wait_until='domcontentloaded')
        pg.wait_for_timeout(1500)
        # Assert the FIX TEXT, never a SHEET_V number: several agents share this repo,
        # 9100 has twice been taken over by another worktree mid-run, and a version pin
        # goes stale the moment somebody else bumps it (487 -> 488 during this job).
        src = pg.content()
        missing = [m for m in ('F.crouch_1 !== undefined', 'F.roll_1 !== undefined',
                               'p.state === STATE.ROLL) { lean = 0') if m not in src]
        if missing:
            b.close()
            sys.exit(f'⛔ 9100 is serving a TREE WITHOUT THIS WORK — missing {missing}.\n'
                     f'   Rebind 9100 to this repo (never stand up a second port).')

        def to_select():
            pg.keyboard.press('Enter'); pg.wait_for_timeout(400)
            pg.click('.mode-btn[data-mode="watch"]'); pg.wait_for_timeout(250)

        to_select()
        made = []
        for pair in PAIRS:
            for nm in pair:
                c = pg.locator(f"#character-selection .sc-card:has(.nm:text-is('{nm}'))").first
                c.wait_for(state='visible', timeout=15000); c.click(); pg.wait_for_timeout(150)
            pg.click('#btn-fight')
            # ⛔ STAMP THE SPAWNS DURING THE ROUND INTRO, before either CPU can move.
            # Taking them lazily at the first pose meant 2.5s of fighting had already
            # happened and the pair had closed to overlapping, so the subject was
            # captured with the opponent standing on top of him.
            pg.wait_for_timeout(1100)
            pg.evaluate("() => { window.__home = { a: player1.x, b: player2.x }; }")
            pg.wait_for_timeout(1400)
            # freeze the match clock so the round cannot end or the CPUs act between shots
            pg.evaluate("() => { try { matchTimer = 999; } catch (e) {} }")

            for who, nm in ((1, pair[0]), (2, pair[1])):
                f = nm.lower()
                for mode, n in (('crouch', 4), ('roll', 6)):
                    if mode == 'roll' and f in NO_ROLL:
                        continue
                    shots = []
                    for i in range(n):
                        pg.evaluate(POSE, [who, mode, i, n])
                        pg.evaluate("() => { window.__watch = true; window.__ctm = []; }")
                        pg.wait_for_timeout(140)
                        pg.evaluate("() => { window.__watch = false; }")
                        where = pg.evaluate(WHERE, who)
                        assert where, f'{f} {mode} beat {i}: no sprite draw captured'
                        info = {'screen': where}
                        box = pg.locator('#game-canvas').first.bounding_box()
                        png = OUT / f'.{f}-{mode}-{i}.png'
                        pg.screenshot(path=str(png))
                        shots.append((Image.open(png).convert('RGB'), info, box))
                    build(f, mode, shots, made)
            pg.evaluate("() => { paused = false; window.__home = null;"
                        " try { quitToSelect(); } catch (e) { location.reload(); } }")
            pg.wait_for_timeout(1300)
            if 'character-selection' not in pg.content():
                pg.goto(URL, wait_until='domcontentloaded'); pg.wait_for_timeout(1500)
            to_select()
        b.close()

    for p in OUT.glob('.*.png'):
        p.unlink()
    strips = sorted(OUT.glob('*-crouch.png')) + sorted(OUT.glob('*-roll.png'))
    imgs = [Image.open(s) for s in strips]
    W = max(i.width for i in imgs)
    contact = Image.new('RGB', (W, sum(i.height + 8 for i in imgs)), (16, 16, 20))
    y = 0
    for i in imgs:
        contact.paste(i, (0, y)); y += i.height + 8
    contact.save(OUT / 'CONTACT.png')
    print('\n'.join(str(m) for m in made))
    print(f'\ncontact sheet -> {OUT / "CONTACT.png"}')


def build(f, mode, shots, made):
    """Crop each panel around the fighter, rule the foot plane, strip + GIF."""
    pw_, ph = PANEL
    panels = []
    for img, info, box in shots:
        # camMatrix put the fighter in CANVAS px (1280x1000 internal). Walk that through
        # the element's real bounding box, then through device_scale_factor.
        dsf = img.width / 1600
        k = box['width'] / 1280 * dsf                       # canvas px -> screenshot px
        cx = (box['x'] * dsf) + info['screen']['x'] * k
        fy = (box['y'] * dsf) + info['screen']['y'] * (box['height'] / 1000 * dsf)
        left, top = int(cx - pw_ * k / 2), int(fy - ph * k * 0.80)
        panel = img.crop((left, top, left + int(pw_ * k), top + int(ph * k)))
        d = ImageDraw.Draw(panel)
        gy = int(fy - top)
        d.line([(0, gy), (panel.width, gy)], fill=(255, 60, 60), width=2)
        panels.append(panel)
    w, h = panels[0].size
    strip = Image.new('RGB', (w * len(panels), h), (16, 16, 20))
    for i, p in enumerate(panels):
        strip.paste(p, (i * w, 0))
    sp = OUT / f'{f}-{mode}.png'
    strip.save(sp)
    gp = OUT / f'{f}-{mode}.gif'
    ms = 280 // len(panels) * 10 if mode == 'roll' else 120
    panels[0].save(gp, save_all=True, append_images=panels[1:], duration=ms, loop=0)
    made.append(f'{sp}   {gp}')


if __name__ == '__main__':
    main()
