#!/usr/bin/env python3
"""Drive the real game in a real browser and record what happens. No hidden-pane throttle.

  python3 tools/watch_game.py --script tools/watch_scripts/roll.json --out /tmp/roll

WHY THIS EXISTS: the in-app Browser pane renders only while it is visible. With it
hidden the page gets ZERO animation frames (measured: 0 rAF callbacks in 2.5s), so the
game loop never advances, the round-intro timer never reaches 0, and every input handler
gated behind it is unreachable. That made a whole class of work — "does it LOOK right",
"does this keypress actually fire" — impossible to verify from here.

Chrome headless with backgrounding disabled runs the loop at full speed, and CDP gives
real key events (Input.dispatchKeyEvent) rather than synthetic ones, so this exercises
the same listeners a human hits. Frames come back as PNGs; ffmpeg turns them into a GIF.

A script is a JSON list of steps, run in order:
  {"wait": 1.5}                      seconds of real game time
  {"key": "KeyD", "hold": 0.4}       press, hold, release
  {"down": "KeyC"} / {"up": "KeyC"}  hold a modifier across other steps
  {"eval": "player1.x"}              run JS, result is printed and recorded
  {"shoot": "label"}                 grab one frame immediately
  {"record": 1.2, "fps": 30}         capture a clip
  {"record": 0.8, "key": "KeyD", "at": 0.15}   ...and press KeyD 0.15s into it
"""
import argparse
import base64
import json
import os
import pathlib
import shutil
import subprocess
import sys
import time
import urllib.request

import asyncio
import websockets

CHROME = '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome'
PORT = 9333

# ⛔ :9101 IS THE TREE (owner, Sep 22 2026). This defaulted to :9100 while serve.py
# defaulted to :9101, so every harness in tools/ graded the ROLLBACK tree while the work
# was being committed to the Shodo one — and an agent whose tree was on :9101 had to STEAL
# 9100 from whoever held it just to run a probe. The comment here even described that as
# normal. The default follows the owner's tree now; :9100 stays reachable by override.
#
# `drive()` re-invokes this file as a subprocess, so the child inherits this env var and
# every check_*.py / audit_*.py in tools/ follows the same override with no change of its own:
#
#     SHADOWCLASH_URL=http://localhost:9100/index.html python3 tools/audit_moves.py
#
# assert_serving_this_tree() still voids the run if the chosen URL is not serving this tree,
# so the override cannot be used to grade someone else's work by accident.
GAME_URL = os.environ.get('SHADOWCLASH_URL', 'http://localhost:9101/index.html')


def launch(url, profile):
    args = [CHROME, '--headless=new', f'--remote-debugging-port={PORT}',
            f'--user-data-dir={profile}', '--window-size=1280,720',
            # the whole point: keep the renderer foregrounded so rAF runs
            '--disable-background-timer-throttling',
            '--disable-renderer-backgrounding',
            '--disable-backgrounding-occluded-windows',
            '--autoplay-policy=no-user-gesture-required',
            '--mute-audio', '--no-first-run', '--no-default-browser-check', url]
    proc = subprocess.Popen(args, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    # ⛔ WAIT ON A CLOCK, NOT A COUNT. This was `for _ in range(100)` with a 0.1s sleep,
    # and a refused connection fails instantly — so the real budget was ~10 seconds. On a
    # loaded machine (several agents packing sheets, another harness mid-run) Chrome takes
    # longer than that to bind, and the run died with a bare "chrome never came up" that
    # reads like a broken install. It is not: launched by hand the same binary comes up
    # fine a second later. 60s wall-clock, and the error now says what to check.
    deadline = time.time() + 60
    while time.time() < deadline:
        if proc.poll() is not None:
            raise SystemExit(f'chrome exited immediately (code {proc.returncode}) — '
                             f'stale profile? try: rm -rf {profile}')
        try:
            tabs = json.loads(urllib.request.urlopen(f'http://localhost:{PORT}/json', timeout=1).read())
            page = next((t for t in tabs if t['type'] == 'page' and t.get('webSocketDebuggerUrl')), None)
            if page:
                return proc, page['webSocketDebuggerUrl']
        except Exception:
            pass
        time.sleep(0.2)
    proc.kill()
    raise SystemExit(
        f'chrome never came up on debug port {PORT} within 60s.\n'
        f'  another headless run may still hold it:  '
        f'ps aux | grep "[h]eadless" ; lsof -nP -iTCP:{PORT}\n'
        f'  or the profile is stale:                 rm -rf {profile}')


class CDP:
    def __init__(self, ws):
        self.ws, self.n = ws, 0

    async def send(self, method, **params):
        self.n += 1
        await self.ws.send(json.dumps({'id': self.n, 'method': method, 'params': params}))
        while True:
            # A wedged command used to hang the whole capture forever with no output,
            # which reads as "the game froze". Fail loudly instead.
            msg = json.loads(await asyncio.wait_for(self.ws.recv(), 20))
            if msg.get('id') == self.n:
                if 'error' in msg:
                    raise RuntimeError(f'{method}: {msg["error"]}')
                return msg.get('result', {})

    async def js(self, expr):
        # async wrapper + awaitPromise: a step can `await` a scene that runs over real
        # frames, instead of guessing a `wait` long enough to cover it.
        r = await self.send('Runtime.evaluate', expression=f'(async()=>{{{expr}}})()',
                            returnByValue=True, awaitPromise=True)
        # ⛔ SURFACE PAGE EXCEPTIONS. Without this a thrown error came back as a bare
        # null, indistinguishable from a step that legitimately returned nothing — so a
        # broken probe reads as "the feature is broken" and you debug the wrong thing.
        if 'exceptionDetails' in r:
            ex = r['exceptionDetails']
            desc = (ex.get('exception') or {}).get('description') or ex.get('text')
            return {'__error': str(desc).split('\n')[0]}
        return r.get('result', {}).get('value')

    async def key(self, code, down=True):
        # a real key event through the same path a human's goes
        kind = 'keyDown' if down else 'keyUp'
        await self.send('Input.dispatchKeyEvent', type=kind, code=code, key=key_of(code),
                        windowsVirtualKeyCode=vk_of(code))

    async def shot(self, path, fast=False, clip=None):
        # PNG full-page grabs run ~2s each over CDP, which made a 36-frame clip take
        # longer than the whole run budget. JPEG at q70 is ~10x faster and a GIF is
        # getting quantised to 256 colours anyway.
        #
        # ⛔ EVEN JPEG, A FULL 1280x720 GRAB CAPS THE REAL RATE AROUND 8fps. Ask for 30
        # and you still get 8 — so a move with 8 frames of startup lands inside ONE
        # captured frame and a before/after looks identical when it isn't. `clip` grabs
        # only the region that matters, which is what makes 30fps actually 30fps.
        kw = {'format': 'jpeg', 'quality': 70} if fast else {'format': 'png'}
        if clip:
            x, y, w, h = clip
            kw['clip'] = {'x': x, 'y': y, 'width': w, 'height': h, 'scale': 1}
        r = await self.send('Page.captureScreenshot', **kw)
        path.write_bytes(base64.b64decode(r['data']))


# ⛔ NEVER SEND nativeVirtualKeyCode. On macOS Chrome reads it as a *macOS* virtual
# keycode, not a Windows one, and it WINS over the `code` string you asked for:
#   Enter -> vk 13 -> macOS 13 is 'w'  -> the page saw a KeyW storm
#   KeyC  -> vk 67 -> macOS 67 is kVK_ANSI_KeypadMultiply -> the page saw NumpadMultiply
# KeyF/KeyG (vk 70/71 = macOS keypad clear/= ) don't merely mistranslate, they WEDGE the
# CDP connection — a dispatch that never returns, which reads as "the game hung".
# Measured on this machine: with it, 1 of 14 codes even arrived before the run froze;
# windowsVirtualKeyCode alone, 14/14 correct with no phantom events. Puppeteer omits it
# for the same reason. `text` was measured too and changes nothing about `code`.
_NAMED = {'Enter': ('Enter', 13), 'Space': (' ', 32), 'Escape': ('Escape', 27),
          'Tab': ('Tab', 9), 'Backspace': ('Backspace', 8), 'ShiftLeft': ('Shift', 16),
          'ArrowUp': ('ArrowUp', 38), 'ArrowDown': ('ArrowDown', 40),
          'ArrowLeft': ('ArrowLeft', 37), 'ArrowRight': ('ArrowRight', 39)}


def key_of(code):
    """DOM `key` for a code — derived, so no letter can be missing from a table."""
    if code in _NAMED:
        return _NAMED[code][0]
    if code.startswith('Key') and len(code) == 4:
        return code[3].lower()
    if code.startswith('Digit') and len(code) == 6:
        return code[5]
    return code


def vk_of(code):
    if code in _NAMED:
        return _NAMED[code][1]
    if code.startswith('Key') and len(code) == 4:
        return ord(code[3])
    if code.startswith('Digit') and len(code) == 6:
        return ord(code[5])
    if code.startswith('F') and code[1:].isdigit():
        return 111 + int(code[1:])          # F1 = 112
    return 0


def _port(base):
    """The port out of a base URL, for error text that names the port actually in use."""
    tail = base.rsplit(':', 1)[-1].split('/')[0]
    return tail if tail.isdigit() else '9100'


def _served_now(url):
    """What the graded URL is serving RIGHT NOW — the page AND every sprite manifest.

    The manifests matter as much as the page and are the half that was missing. Chrome
    loads index.html ONCE, so a port stolen after that does not change the engine already
    running — but every probe in tools/ fetches `assets/sprites/<name>.json` LAZILY, in
    the middle of the run, to preload a fighter. Steal the port in that window and the
    probe grades THIS tree's engine against ANOTHER tree's sheets, where the same cell
    index is a different picture and `cols` is a different number.

    That is not hypothetical. It produced a run reporting DEAD 7->12, ECHO 28->63 and one
    fighter's whole Special row drawn from another fighter's cells, with the page itself
    checking out correctly at both ends.
    """
    root = pathlib.Path(__file__).resolve().parents[1]
    base = url.rsplit('/', 1)[0]
    want = {'index.html': root / 'web/index.html'}
    for jf in sorted((root / 'web/assets/sprites').glob('*.json')):
        want[f'assets/sprites/{jf.name}'] = jf
    out = {}
    for rel, disk in want.items():
        try:
            out[rel] = (urllib.request.urlopen(f'{base}/{rel}', timeout=5).read(),
                        disk.read_bytes())
        except urllib.error.HTTPError as e:
            # ⛔ A 404 FOR A FILE THAT EXISTS ON DISK IS THE WRONG TREE, NOT A DEAD SERVER.
            # Reporting it as "no server" sends the operator to start one that is already
            # running. It is also the LOUDEST form of the bug: the other worktree does not
            # merely have different bytes, it does not carry this file at all — which is
            # exactly what a rename looks like from here (this tree's mokurai.json is
            # buddha.json over there).
            raise SystemExit(
                f'⛔ {base} IS NOT SERVING THIS TREE — THE RUN IS VOID.\n'
                f'   {rel} is HTTP {e.code} there, but exists here ({disk}).\n'
                f'   A server IS running; it is pointed at another worktree. Do NOT trust\n'
                f'   any number this run printed. Rebind THIS port (never add a third):\n'
                f'     kill $(lsof -nP -iTCP:{_port(base)} -sTCP:LISTEN -t) '
                f'&& python3 tools/serve.py {_port(base)} web &\n'
                f'   Or grade the other designated port instead:\n'
                f'     SHADOWCLASH_URL=http://localhost:<9100|9101>/index.html <this command>')
        except Exception as e:
            raise SystemExit(f'no server on {base}/{rel} ({e})\n'
                             f'  start it:  python3 tools/serve.py {_port(base)} web')
    return out


def assert_serving_this_tree(url, when='before the run'):
    """⛔ THE DESIGNATED PORTS ARE SHARED. Refuse to grade a tree that is not the one on disk here.

    Several agents share this repo across worktrees and all of them use :9100 or :9101, so a
    port gets rebound out from under a probe. Comparing BYTES is the whole check — a version
    string would not catch it (two trees both said SHEET_V 456), and neither would a
    timestamp.

    ⛔ CALLED TWICE, BEFORE AND AFTER. Checking only at the start is the gap this closes:
    it proves the tree was right when Chrome booted and proves nothing about the moment a
    manifest was fetched thirty seconds later. A steal anywhere in between used to pass
    both end checks and hand back numbers that looked like findings.
    """
    bad = [rel for rel, (served, disk) in _served_now(url).items() if served != disk]
    if bad:
        raise SystemExit(
            f'⛔ {url} IS NOT SERVING THIS TREE ({when}) — THE RUN IS VOID.\n'
            f'   mismatched: {", ".join(bad[:6])}{" ..." if len(bad) > 6 else ""}\n'
            f'   Another worktree has this port. Do NOT trust any number this run printed.\n'
            f'   Rebind it (never add a third port):\n'
            f'     kill $(lsof -nP -iTCP:{_port(url)} -sTCP:LISTEN -t) '
            f'&& python3 tools/serve.py {_port(url)} web &\n'
            f'   Or point the run at the other designated port:\n'
            f'     SHADOWCLASH_URL=http://localhost:<9100|9101>/index.html <this command>')


async def run(url, steps, out):
    assert_serving_this_tree(url, 'before the run')
    out.mkdir(parents=True, exist_ok=True)
    profile = out / '_chrome'
    proc, wsurl = launch(url, profile)
    log = []
    try:
        async with websockets.connect(wsurl, max_size=64 * 1024 * 1024) as ws:
            c = CDP(ws)
            await c.send('Page.enable')
            await c.send('Runtime.enable')
            await asyncio.sleep(1.5)
            fps_alive = await c.js(
                'let n=0;const t=(()=>{n++;requestAnimationFrame(t)});requestAnimationFrame(t);'
                'return new Promise(r=>setTimeout(()=>r(n),1000));')
            log.append(f'rAF/sec at start: {fps_alive}')
            print(f'  rAF/sec: {fps_alive}  ({"LIVE" if fps_alive else "STILL FROZEN"})')
            shot_i = 0
            for st in steps:
                if 'wait' in st:
                    await asyncio.sleep(st['wait'])
                # ⛔ `record` IS TESTED FIRST. A capture that fires its own key carries
                # BOTH keys, and the `key` branch used to swallow it — the press happened,
                # no frames were written, and the run reported "no frames for roll".
                elif 'record' in st:
                    fps = st.get('fps', 30)
                    n = int(st['record'] * fps)
                    # A key pressed BEFORE the capture is already over by frame 1 — the
                    # roll is 0.28s and the first strip caught only its aftermath. `at`
                    # fires the press partway INTO the clip so the move is filmed from
                    # its own first frame, still through the real key path.
                    at = int(st.get('at', 0) * fps) if 'key' in st else -1
                    t_start = time.time()
                    for i in range(n):
                        if i == at:
                            await c.key(st['key'], True)
                            await c.key(st['key'], False)
                        await c.shot(out / f'f_{st.get("tag","clip")}_{i:04d}.jpg',
                                     fast=True, clip=st.get('clip'))
                        await asyncio.sleep(max(0, 1 / fps - 0.02))
                    # REPORT THE RATE YOU ACTUALLY GOT. Asking for 30 and silently getting
                    # 8 is how a real before/after got filmed as two identical clips.
                    real = n / max(time.time() - t_start, 1e-6)
                    note = f'  record {st.get("tag","clip")}: {n} frames, asked {fps}fps, got {real:.0f}fps'
                    if real < fps * 0.7:
                        note += '  ⚠ under-sampled — add a "clip" region'
                    log.append(note.strip())
                    print(note)
                elif 'key' in st:
                    await c.key(st['key'], True)
                    await asyncio.sleep(st.get('hold', 0.05))
                    await c.key(st['key'], False)
                elif 'down' in st:
                    await c.key(st['down'], True)
                elif 'up' in st:
                    await c.key(st['up'], False)
                elif 'eval' in st:
                    # a step is a full statement list if it contains `return` ANYWHERE —
                    # only wrap bare expressions. Testing for a leading `return` silently
                    # turned every multi-statement step into `return const ...`, a syntax
                    # error that came back as null and made four failed clicks look like
                    # four successful ones.
                    ex = st['eval']
                    v = await c.js(ex if 'return' in ex else f'return {ex}')
                    log.append(f'{st.get("label", "eval")}: {json.dumps(v)}')
                    print(f'  {st.get("label", "eval")}: {json.dumps(v)}')
                elif 'shoot' in st:
                    shot_i += 1
                    await c.shot(out / f'shot_{shot_i:02d}_{st["shoot"]}.png')
    finally:
        proc.terminate()
        shutil.rmtree(profile, ignore_errors=True)
    # ⛔ AND AGAIN AT THE END. This is the whole point of the pair: the start check
    # proves nothing about the manifest fetched mid-run. If the port moved at any
    # point, the log is written but the caller is stopped before it can read it.
    (out / 'log.txt').write_text('\n'.join(log) + '\n')
    assert_serving_this_tree(url, 'AFTER the run — a steal mid-run voids it')
    return log


def to_gif(out, tag, fps=30):
    frames = sorted(out.glob(f'f_{tag}_*.jpg'))
    if not frames:
        return None
    gif = out / f'{tag}.gif'
    subprocess.run(['ffmpeg', '-y', '-framerate', str(fps), '-pattern_type', 'glob',
                    '-i', str(out / f'f_{tag}_*.jpg'),
                    '-vf', 'scale=800:-1:flags=lanczos,split[a][b];[a]palettegen[p];[b][p]paletteuse',
                    str(gif)], check=True, capture_output=True)
    for f in frames:
        f.unlink()
    return gif


async def selftest():
    """Does the page receive the code we asked for? The bug this catches shipped.

    python3 tools/watch_game.py --selftest
    """
    codes = ['KeyA', 'KeyD', 'KeyW', 'KeyS', 'KeyC', 'KeyF', 'KeyG', 'KeyH', 'KeyV',
             'KeyM', 'Enter', 'Space', 'Escape', 'ArrowUp', 'ArrowDown', 'ArrowLeft',
             'ArrowRight']
    tmp = pathlib.Path('/tmp/_watch_selftest')
    proc, wsurl = launch('about:blank', tmp)
    try:
        async with websockets.connect(wsurl, max_size=8 * 1024 * 1024) as ws:
            c = CDP(ws)
            await c.send('Runtime.enable')
            await c.js("window.__k=[];addEventListener('keydown',e=>__k.push(e.code),true);return 1;")
            for code in codes:
                await c.key(code, True)
                await c.key(code, False)
            await asyncio.sleep(0.2)
            got = await c.js('return __k;') or []
    finally:
        proc.terminate()
        shutil.rmtree(tmp, ignore_errors=True)
    assert got == codes, f'page saw {got}\n         wanted {codes}'
    print(f'  selftest ok — all {len(codes)} codes arrive as sent, no phantoms')


# (The single-argument assert_serving_this_tree that used to live here came in with
#  the blade-lock branch and is SUPERSEDED, not merged beside: the version above
#  fingerprints the sprite manifests as well as the page and runs before AND after
#  the steps. Two definitions of the same name silently kept the LAST one, so every
#  2-argument call raised TypeError and the whole runtime suite failed at once.)


def drive(script_steps, out_dir, label):
    """Run a probe and hand back its labelled JSON. Use this from check_*.py.

    Every caller was writing the same subprocess call with `capture_output=True`, which
    swallows stderr — so the wrong-tree guard above printed its fix instructions into a
    pipe nobody read, and the operator saw a bare CalledProcessError traceback. Here the
    child's stderr is re-raised as the message.
    """
    out_dir = pathlib.Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    script = out_dir / 'script.json'
    script.write_text(json.dumps(script_steps, indent=1))
    try:
        subprocess.run([sys.executable, str(pathlib.Path(__file__).resolve()),
                        '--script', str(script), '--out', str(out_dir / 'run')],
                       check=True, capture_output=True, text=True)
    except subprocess.CalledProcessError as e:
        raise SystemExit((e.stderr or e.stdout or '').strip() or
                         f'probe failed with exit {e.returncode}')
    log = (out_dir / 'run/log.txt').read_text()

    def grab(lbl):
        i = log.index(f'{lbl}: ')
        raw = json.JSONDecoder().raw_decode(log[i + len(lbl) + 2:])[0]
        return json.loads(raw) if isinstance(raw, str) else raw

    # A list of labels pulls several evals out of ONE browser run. A probe that does
    # more than ~1000 frames trips the 20s CDP timeout in js(), so the fix is to split
    # it into steps — not to pay for a second page load per step.
    if isinstance(label, (list, tuple)):
        return {l: grab(l) for l in label}
    return grab(label)


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('--url', default=GAME_URL)
    ap.add_argument('--selftest', action='store_true')
    ap.add_argument('--script')
    ap.add_argument('--out')
    ap.add_argument('--gif', action='append', default=[])
    a = ap.parse_args()
    if a.selftest:
        asyncio.run(selftest())
        raise SystemExit(0)
    if not a.script or not a.out:
        raise SystemExit('need --script and --out (or --selftest)')
    assert_serving_this_tree(a.url)
    steps = json.loads(pathlib.Path(a.script).read_text())
    out = pathlib.Path(a.out)
    asyncio.run(run(a.url, steps, out))
    for tag in a.gif:
        g = to_gif(out, tag)
        print(f'  gif -> {g}' if g else f'  no frames for {tag}')
    print(f'  out -> {out}')
