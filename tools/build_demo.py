#!/usr/bin/env python3
"""Build the public SHODO demo from web/ into an output folder. Never touches web/.

  python3 tools/build_demo.py <out-dir> [--terser <path-to-terser>]

What the demo build does:
  * flips DEMO_BUILD so Exile and Mokurai are benched and drawn as black silhouettes
  * leaves their portraits, sprite sheets and manifests OUT of the output entirely
  * leaves out review folders and the boss art sheets
  * removes their lines from the in-game help text
  * strips every HTML / CSS / JS comment (design notes, dated rulings) and minifies the script
  * bakes the silhouettes (tools/bake_locked_silhouettes.py)
Needs terser (https://www.npmjs.com/package/terser) and Pillow + SciPy for the baker.
"""
import os, re, shutil, subprocess, sys, tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
WEB = os.path.join(ROOT, 'web')
LOCKED = ['exile', 'mokurai']

def skip(path):
    rel = os.path.relpath(path, WEB).replace(os.sep, '/')
    base = os.path.basename(rel)
    if rel == '_review' or rel.startswith('_review/'): return True
    if base.startswith('bosses-'): return True
    if base.startswith('.'): return True
    if base == 'PURGED-KEYS.json': return True
    if any(base.startswith(n + '.') or base.startswith(n + '-') for n in LOCKED):
        return rel.startswith('assets/')
    return False

def copy_tree(out):
    for d, dirs, files in os.walk(WEB):
        dirs[:] = [x for x in dirs if not skip(os.path.join(d, x))]
        for f in files:
            src = os.path.join(d, f)
            if skip(src): continue
            dst = os.path.join(out, os.path.relpath(src, WEB))
            os.makedirs(os.path.dirname(dst), exist_ok=True)
            shutil.copy2(src, dst)

def must_replace(s, old, new, count=1):
    if s.count(old) != count:
        sys.exit(f'build_demo: expected {count}x {old[:70]!r}, found {s.count(old)} - help text changed, update tools/build_demo.py')
    return s.replace(old, new)

def scrub_help(s):
    s = must_replace(s, 'Champion Mode (Exile, needs a full CHAIN bar) ·\n                            ', '', 2)
    s = must_replace(s, ' · Mokurai <kbd>Down+S</kbd> temple bell (hits BOTH sides)', '')
    s = re.sub(r" · Exile <kbd>Down\+S</kbd> SERPENT'S TONGUE floor chain \(long low, trips\)", '', s, count=1)
    s = re.sub(r'\s*<li><b class="text-gray-200">Exile · [^\n]*</li>', '', s)          # Exile move lists
    s = re.sub(r'\s*<li><b class="text-gray-200">Chain Anchor \(Exile\):</b>[^\n]*</li>', '', s)
    s = re.sub(r'\s*<li><b class="text-gray-200">Throw From The Wall:</b>[^\n]*</li>', '', s)
    s = must_replace(s, '(Mokurai drives a bead-wrapped fist skyward, Ember rakes claws)', '(Ember rakes claws)')
    return s

def strip_html_css(part):
    part = re.sub(r'<!--.*?-->', '', part, flags=re.S)
    part = re.sub(r'(<style\b[^>]*>)(.*?)(</style>)',
                  lambda m: m.group(1) + re.sub(r'/\*.*?\*/', '', m.group(2), flags=re.S) + m.group(3), part, flags=re.S)
    return part

def minify_js(js, terser):
    with tempfile.NamedTemporaryFile('w', suffix='.js', delete=False, encoding='utf-8') as t:
        t.write(js); src = t.name
    try:
        r = subprocess.run(terser + [src, '--compress', '--mangle', '--format', 'comments=false'],
                           capture_output=True, text=True, encoding='utf-8')
    finally:
        os.unlink(src)
    if r.returncode: sys.exit('terser failed:\n' + r.stderr[:2000])
    return r.stdout.replace('</script', '<\\/script')

def build_html(out, terser):
    p = os.path.join(out, 'index.html')
    s = open(p, encoding='utf-8').read()
    s = must_replace(s, 'const DEMO_BUILD = false;', 'const DEMO_BUILD = true;')
    s = scrub_help(s)
    pieces = re.split(r'(<script\b[^>]*>.*?</script>)', s, flags=re.S)
    res = []
    for piece in pieces:
        m = re.match(r'(<script\b[^>]*>)(.*?)(</script>)$', piece, flags=re.S)
        if not m:
            res.append(strip_html_css(piece)); continue
        head, body, tail = m.groups()
        if 'src=' in head or not body.strip() or 'type="application/json"' in head:
            res.append(piece)
        else:
            res.append(head + minify_js(body, terser) + tail)
    open(p, 'w', encoding='utf-8').write(''.join(res))

def fix_runtime_index(out):
    import json
    p = os.path.join(out, 'assets', 'runtime-sprites', 'index.json')
    d = json.load(open(p))
    for n in LOCKED: d['fighters'].pop(n, None)
    json.dump(d, open(p, 'w'), separators=(',', ':'))

def main():
    args = sys.argv[1:]
    terser = ['npx', '--yes', 'terser']
    if '--terser' in args:
        i = args.index('--terser'); terser = [args[i + 1]]; del args[i:i + 2]
    if len(args) != 1: sys.exit(__doc__)
    out = os.path.abspath(args[0])
    if os.path.exists(out): shutil.rmtree(out)
    copy_tree(out)
    fix_runtime_index(out)
    build_html(out, terser)
    subprocess.check_call([sys.executable, os.path.join(ROOT, 'tools', 'bake_locked_silhouettes.py'), WEB, out] + LOCKED)
    print('demo built:', out)

if __name__ == '__main__':
    main()
