#!/usr/bin/env python3
"""LIVE proof that every fighter's crouch and ground roll are drawn, and grounded.

Two halves, and neither of them re-implements the engine:

  SHEET (no browser) — measured straight off the packed PNG + manifest. Every new cell's
  lowest ink row must sit exactly on footY, and the deepest crouch beat must be visibly
  below that fighter's own idle.

  LIVE (real game on 9101) — boots a real match per fighter and calls the engine's OWN
  spriteFrameIndex() on the real player object while walking rollTimer and crouchAt
  across their real ranges, so what is checked is the shipped picker. Then it inputs an
  actual roll and reads the CTM out of a hooked drawImage: drawSprite works in a
  FEET-ANCHORED local frame, so a drawn roll that is ALSO being spun by the fallback
  windmill shows up as rotation terms in that matrix. That is the bug this art exists to
  kill, and it is the one thing a static check cannot see.

⛔ Never starts a server. Checks 9101 and fails with instructions.
"""
import json
import os
import sys
import urllib.request

import numpy as np
from PIL import Image
from playwright.sync_api import sync_playwright

Image.MAX_IMAGE_PIXELS = None
# Two designated ports are law (AGENTS.md rule 8). Same override every harness uses:
#   SHADOWCLASH_URL=http://localhost:9101/index.html python3 tools/check_roll_crouch.py
URL = os.environ.get('SHADOWCLASH_URL', 'http://127.0.0.1:9101/').replace('index.html', '')
SPR = 'web/assets/sprites'
ROSTER = ['executioner', 'mizu', 'shin', 'tsubasa', 'ember', 'kael', 'mokurai', 'exile']
NO_ROLL = {'mokurai', 'exile'}     # they own authored dodges (mroll1-4 / slide1-4)
ROLL_TIME = 0.28
# leanSmooth measured on this build after a real 900ms held sprint in training mode.
# The run lean is what warps a roll, so the warp test has to start from a real one.
SPRINT_LEAN = 0.2751

# ⛔ IDENTIFY THE SHEET, NOT JUST "A BIG IMAGE". The first version of this hook took any
# 8-arg drawImage of an image wider than 4000px, which also catches STAGE BACKGROUNDS —
# and sx/sw on a backdrop is a meaningless number that can land inside a fighter's roll
# cell range by coincidence. That produced four phantom "warped roll frames" on the
# Executioner that no amount of staring at the transform could explain, because they were
# never his sprite. Record the source width and match it to the fighter's own sheet.
HOOK = """
(() => {
  const P = CanvasRenderingContext2D.prototype;
  if (P.__scHook) return; P.__scHook = true;
  window.__ctm = [];
  const orig = P.drawImage;
  P.drawImage = function (img, ...a) {
    if (window.__watch && a.length === 8 && img && img.width > 4000) {
      const m = this.getTransform();
      window.__ctm.push({ b: m.b, c: m.c, a: m.a, d: m.d,
                          cell: Math.round(a[0] / a[2]), sw: img.width });
    }
    return orig.apply(this, [img, ...a]);
  };
})()
"""

# Walk the real picker over a real player. Mutates and restores the fields it drives.
PROBE = """
([who, rollTime]) => {
  const p = who === 1 ? player1 : player2;
  const man = SHEET_MAN(p);
  const F = man.frames;
  const save = { state: p.state, rollTimer: p.rollTimer, crouchAt: p.crouchAt,
                 animPhase: p.animPhase, tumbleT: p.tumbleT, landT: p.landT,
                 meditateTimer: p.meditateTimer, sakate: p.sakate };
  const out = { crouch: [], roll: [], land: null, name: p.spec.name };
  try {
    p.tumbleT = 0; p.landT = 0; p.meditateTimer = 0; p.sakate = false;
    // --- CROUCH: enter it now, then run 0.6s of ticks through sink + hold
    p.state = STATE.CROUCH; p.rollTimer = 0;
    p.crouchAt = animClock;
    for (let i = 0; i < 36; i++) {
      p.animPhase = i * 0.20;
      const t = animClock + i / 60;
      const keep = p.crouchAt; p.crouchAt = keep - (t - animClock);   // advance the sink clock
      out.crouch.push(spriteFrameIndex(p, F));
      p.crouchAt = keep;
    }
    // --- ROLL: walk rollTimer down exactly as handleMovement does
    p.state = STATE.ROLL;
    for (let rt = rollTime; rt > 0; rt -= 1 / 120) {
      p.rollTimer = rt;
      out.roll.push(spriteFrameIndex(p, F));
    }
    // --- LANDING squash
    p.state = STATE.IDLE; p.rollTimer = 0; p.landT = 0.05;
    out.land = spriteFrameIndex(p, F);
  } finally { Object.assign(p, save); }
  const uniq = a => [...new Set(a)].sort((x, y) => x - y);
  return { name: out.name, crouch: uniq(out.crouch), roll: uniq(out.roll),
           land: out.land,
           want_crouch: [1,2,3,4].map(i => F['crouch_' + i]),
           want_roll: [1,2,3,4,5,6].map(i => F['roll_' + i]) };
}
"""

# spriteFrameIndex needs the fighter's manifest; the engine looks it up per draw.
SHEET_MAN = """
() => { window.SHEET_MAN = p => SPRITES[p.spec.name.toLowerCase()]; }
"""


def sheet_checks():
    fails, rows = [], []
    for f in ROSTER:
        man = json.load(open(f'{SPR}/{f}.json'))
        cw, ch, footy, F = man['frameW'], man['frameH'], man['footY'], man['frames']
        sh = np.array(Image.open(f'{SPR}/{f}.png').convert('RGBA'))

        def ink(idx):
            a = sh[:, idx * cw:(idx + 1) * cw, 3] > 0
            ys, xs = np.where(a)
            return ys.min(), ys.max(), xs.min(), xs.max()

        stand = footy - ink(F['idle'])[0]
        keys = [f'crouch_{i}' for i in range(1, 5)]
        if f not in NO_ROLL:
            keys += [f'roll_{i}' for i in range(1, 7)]
        for k in keys:
            if k not in F:
                fails.append(f'{f}: sheet has no {k}')
                continue
            y0, y1, x0, x1 = ink(F[k])
            if y1 != footy:
                fails.append(f'{f} {k}: ink bottom row {y1}, footY {footy} — {footy - y1}px of float')
            if x0 <= 0 or x1 >= cw - 1:
                fails.append(f'{f} {k}: clipped at the canvas edge ({x0}..{x1} of {cw})')
            rows.append((f, k, footy - y0, round((footy - y0) / stand * 100)))
        if 'crouch_3' in F:
            deep = footy - ink(F['crouch_3'])[0]
            if deep >= stand:
                fails.append(f'{f}: crouch_3 is {deep}px against a {stand}px idle — not a crouch')
    return fails, rows


def live_checks():
    try:
        if urllib.request.urlopen(URL, timeout=5).status != 200:
            raise OSError
    except Exception:
        sys.exit('⛔ 9101 is not serving the game.  python3 tools/serve.py 9101 web')

    fails = []
    with sync_playwright() as pw:
        b = pw.chromium.launch(
            headless=True,
            executable_path='/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',
            args=['--mute-audio', '--disable-background-timer-throttling',
                  '--disable-renderer-backgrounding', '--no-first-run'])
        pg = b.new_page(viewport={'width': 1280, 'height': 720})
        errs = []
        pg.on('pageerror', lambda e: errs.append(str(e)))
        pg.goto(URL, wait_until='domcontentloaded')
        pg.wait_for_timeout(1500)
        # ⛔ PROVE 9100 IS SERVING THE TREE THIS CHECK IS ABOUT, by looking for the FIX
        # TEXT — not for a SHEET_V number. Several agents share this repo and 9100 has
        # twice been taken over by another worktree mid-verification; a version number
        # also goes stale the moment somebody else bumps it (487 -> 488 while this was
        # being written), which turns a real guard into a false alarm. The code either
        # is in the served source or it is not.
        src = pg.content()
        missing = [m for m in ('F.crouch_1 !== undefined', 'F.roll_1 !== undefined',
                               'MF.roll_1 !== undefined', 'p.state === STATE.ROLL) { lean = 0')
                   if m not in src]
        if missing:
            b.close()
            sys.exit(f'⛔ 9101 is serving a TREE WITHOUT THIS WORK — missing {missing}.\n'
                     f'   Rebind 9101 to this repo (never stand up a second port).')

        # WATCH mode: two CPUs, both players real, no input needed to keep a match alive.
        pg.keyboard.press('Enter')
        pg.wait_for_timeout(400)
        pg.click('.mode-btn[data-mode="watch"]')
        pg.wait_for_timeout(250)

        for pair in [('Executioner', 'Mizu'), ('Shin', 'Tsubasa'),
                     ('Ember', 'Kael'), ('Mokurai', 'Exile')]:
            for nm in pair:
                card = pg.locator(f"#character-selection .sc-card:has(.nm:text-is('{nm}'))").first
                card.wait_for(state='visible', timeout=15000)
                card.click()
                pg.wait_for_timeout(150)
            pg.click('#btn-fight')
            pg.wait_for_timeout(2200)
            pg.evaluate(SHEET_MAN)
            pg.evaluate(HOOK)

            for who, nm in ((1, pair[0]), (2, pair[1])):
                f = nm.lower()
                r = pg.evaluate(PROBE, [who, ROLL_TIME])
                if r['name'].lower() != f:
                    fails.append(f'{f}: probe landed on {r["name"]} instead')
                    continue
                if r['crouch'] != sorted(r['want_crouch']):
                    fails.append(f'{f}: crouch drew {r["crouch"]}, all four are {sorted(r["want_crouch"])}')
                if r['land'] != r['want_crouch'][2]:
                    fails.append(f'{f}: landing drew {r["land"]}, crouch_3 is {r["want_crouch"][2]}')
                if f in NO_ROLL:
                    if None in r['want_roll'] and r['roll'] == []:
                        fails.append(f'{f}: roll picker returned nothing at all')
                else:
                    if r['roll'] != sorted(r['want_roll']):
                        fails.append(f'{f}: roll drew {r["roll"]}, all six are {sorted(r["want_roll"])}')

            # ⛔ NO WARPING AND NO STRETCHING ON ANY ROLLING FRAME (owner, Aug 13 2026).
            # A REAL sprint-into-roll, run live at full speed — not a frozen pose. Rolling
            # out of a run is the only way anyone ever rolls, and the run lean is a
            # spring that is UNGATED BY STATE: it decays across the whole 0.28s roll and
            # then overshoots past zero. Measured before the fix: 17 of 17 drawn frames
            # sheared, worst c = 0.275. So this has to load the spring for real.
            #
            # Every term of the matrix is checked, not just rotation:
            #   b  rotation  — the fallback windmill spinning over drawn art
            #   c  shear     — the run lean skewing the ball
            #   a  x-scale   — stretch (|a| is 1 under the pure facing mirror)
            #   d  y-scale   — squash, e.g. a landing absorb bleeding into a dodge
            # SPRINT_LEAN is not invented: it is leanSmooth measured on this build after
            # holding a real sprint for 900ms in training mode. Seeding it and then
            # running the roll LIVE keeps everything that matters real — the spring
            # decays and overshoots through the engine's own update, rollTimer advances
            # through the engine's own clock, and the picker and transform are the
            # shipped ones. Seeding rather than key-pressing is what lets this run in
            # WATCH mode, where both seats are CPUs and a keypress moves nobody.
            for who, nm in ((1, pair[0]), (2, pair[1])):
                f = nm.lower()
                # The sim stays LIVE so the spring really decays — but a CPU mid-swing or
                # mid-stagger never enters ROLL at all, which reads back as "no frame
                # captured". Clear what outranks movement on BOTH fighters and make the
                # roll untouchable for its duration, then retry: interference is random,
                # so a retry distinguishes a flaky probe from a real failure.
                sheetw = pg.evaluate("(n) => SPRITES[n].img.width", f)
                want = pg.evaluate("""(n) => {
                    const F = SPRITES[n].frames;
                    const pick = ks => ks.map(k => F[k]).filter(v => v !== undefined);
                    const drawn = pick([1,2,3,4,5,6].map(i => 'roll_' + i));
                    if (drawn.length) return drawn;
                    return pick(['mroll1','mroll2','mroll3','mroll4',
                                 'slide1','slide2','slide3','slide4']);
                }""", f)
                lean, mine = 0, []
                for _ in range(3):
                    lean = pg.evaluate("""(who) => {
                        const p = who === 1 ? player1 : player2;
                        const q = who === 1 ? player2 : player1;
                        paused = false;
                        for (const x of [p, q]) {
                            x.stunTimer = 0; x.tumbleT = 0; x.flooredT = 0;
                            x.attackAnim = null; x.grappleT = 0; x.lockT = 0;
                            if (x.hitboxes) x.hitboxes.length = 0;
                        }
                        p.dashTimer = 0; p.rollRecover = 0; p.rollTimer = 0;
                        p.isGrounded = true; p.vy = 0;
                        p.invulnTimer = 1;              // nothing may interrupt the roll
                        p.leanSmooth = SPRINT_LEAN; p.leanVel = 0;
                        window.__watch = true; window.__ctm = [];
                        p.startRoll(1);
                        p.state = STATE.ROLL;
                        return p.leanSmooth;
                    }""".replace('SPRINT_LEAN', str(SPRINT_LEAN)), who)
                    pg.wait_for_timeout(340)      # a whole 0.28s roll, live
                    ctm = pg.evaluate("() => { window.__watch = false; return window.__ctm; }")
                    mine = [m for m in ctm if m['sw'] == sheetw and m['cell'] in want]
                    if mine:
                        break
                warped = [m for m in mine
                          if abs(m['b']) > 1e-6 or abs(m['c']) > 1e-6
                          or abs(abs(m['a']) - 1) > 0.02 or abs(m['d'] - 1) > 0.02]
                if abs(lean) < 0.05:
                    fails.append(f'{f}: lean spring not loaded (leanSmooth {lean:.4f}) — '
                                 f'this test would prove nothing')
                elif not mine:
                    fails.append(f'{f}: no roll frame captured during a live roll')
                elif warped:
                    w = warped[0]
                    fails.append(
                        f'{f}: WARPED ROLL FRAMES — {len(warped)}/{len(mine)} '
                        f'(rotate b={w["b"]:.4f}, shear c={w["c"]:.4f}, '
                        f'scale a={w["a"]:.4f} d={w["d"]:.4f}); lean carried in was {lean:.4f}')

            # THE DOUBLE-SQUASH TEST. drawSprite still flattens a fighter's crouch cell
            # down to CROUCH_H, and it must NOT do that to art already drawn at 65-70% —
            # 0.68 of 0.68 is 46%, a fighter folded to less than half his height. The
            # exemption is implicit (the squash tests the CELL against kneel/xcrouch/
            # bcrouch and crouch_3 is none of them), and an implicit exemption is exactly
            # the kind that a later edit re-breaks in silence. So measure it.
            for who, nm in ((1, pair[0]), (2, pair[1])):
                f = nm.lower()
                want = pg.evaluate("(n) => SPRITES[n].frames.crouch_3", f)
                pg.evaluate("""(who) => {
                    const p = who === 1 ? player1 : player2;
                    paused = true;
                    window.__watch = true; window.__ctm = [];
                    p.meditateTimer = 0;       // Mokurai's channel outranks the crouch row
                    p.state = STATE.CROUCH; p.crouchAt = animClock - 9; p.animPhase = 0;
                }""", who)
                pg.wait_for_timeout(120)
                ctm = pg.evaluate("() => { window.__watch = false; return window.__ctm; }")
                sheetw = pg.evaluate("(n) => SPRITES[n].img.width", f)
                mine = [m for m in ctm if m['sw'] == sheetw and m['cell'] == want]
                squashed = [m for m in mine if abs(m['d'] - 1) > 0.02 or abs(abs(m['a']) - 1) > 0.02]
                if not mine:
                    fails.append(f'{f}: crouch_3 (cell {want}) never drew during STATE.CROUCH')
                elif squashed:
                    fails.append(f'{f}: crouch_3 is being SQUASHED AGAIN on top of drawn art — '
                                 f'{len(squashed)}/{len(mine)} draws scaled '
                                 f'(a={squashed[0]["a"]:.3f}, d={squashed[0]["d"]:.3f})')

            pg.evaluate("() => { paused = false;"
                        " try { quitToSelect(); } catch (e) { location.reload(); } }")
            pg.wait_for_timeout(1200)
            if 'character-selection' not in pg.content():
                pg.goto(URL, wait_until='domcontentloaded')
                pg.wait_for_timeout(1500)
                pg.keyboard.press('Enter')
                pg.wait_for_timeout(400)
                pg.click('.mode-btn[data-mode="watch"]')
                pg.wait_for_timeout(250)

        b.close()
    fails += [f'PAGE ERROR: {e}' for e in errs]
    return fails


def main():
    sf, rows = sheet_checks()
    lf = live_checks()
    print(f'{"fighter":<12}{"cell":<10}{"px":>5}{"% standing":>12}')
    for r in rows:
        print(f'{r[0]:<12}{r[1]:<10}{r[2]:>5}{r[3]:>11}%')
    print(f'\n{len(rows)} cells measured on the sheets')
    for x in sf + lf:
        print('FAIL', x)
    ok = not (sf or lf)
    print('\n' + ('PASS — everybody crouches, everybody rolls, nobody floats'
                  if ok else f'{len(sf) + len(lf)} FAILURES'))
    sys.exit(0 if ok else 1)


if __name__ == '__main__':
    main()
