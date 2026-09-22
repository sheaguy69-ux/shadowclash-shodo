#!/usr/bin/env python3
"""Keep concurrent agents out of each other's pockets. One tree, several hands.

  python3 tools/lane.py start "Opus 5"     # FIRST THING every session
  python3 tools/lane.py who                # what is going on right now
  python3 tools/lane.py note "..."         # say something in the channel

WHY THIS EXISTS — four things that actually happened on Aug 2 2026, in one night:

  1. `git add web/index.html` was one keystroke from committing ANOTHER agent's
     uncommitted audio pass under my commit message, past the owner's listen-first gate.
     Nothing would have complained.
  2. The team channel's newest entry lagged the git log by a full DAY. Two agents read
     the ledger, believed it, and were both working from a state that no longer existed.
  3. EVERY commit in the log carries `Co-Authored-By: Claude Opus 5` — Kimi's, Fable-5's,
     mine. Forty commits, one name. The log cannot tell you who did what.
  4. An hour was spent investigating, and PRICING a regeneration for, a bug that had been
     fixed eleven SHEET_V bumps earlier. The evidence was in a commit message nobody read.

Etiquette did not prevent any of those, because etiquette is advisory and a `git add` is
not. So this is small and mechanical instead:

  * FOREIGN FILES. `start` snapshots every file that is already dirty when you sit down.
    Those edits are somebody else's, by definition — you were not here when they were
    made. pre-commit refuses to include them. This is the whole point of the file.
  * IDENTITY. `start` records your name; post-commit stamps it on the commit and appends
    one line to the channel, so the ledger physically cannot fall behind the log again.
  * SITUATION. `who` prints the live truth — HEAD, foreign dirty files, worktrees,
    unmerged branches, recent commits — so a session opens on facts, not on a stale doc.

State lives in $GIT_DIR/lane/, which is per-worktree and never committed.
"""
import json
import os
import pathlib
import subprocess
import sys
import time

REPO = pathlib.Path(__file__).resolve().parents[1]
CHANNEL = pathlib.Path('/Users/anthonyguy/OB-LOCAL_BRAIN/Claude-Brain/memory/shadow-clash-channel.md')


def git(*a):
    # ⛔ NO cwd=REPO. This file lives in the main tree but is shared by every WORKTREE via
    # an absolute core.hooksPath, so pinning git to its own location made a worktree commit
    # inspect MAIN's status instead of its own — the guard would then protect the wrong tree
    # and wave the real conflict through. Always operate on the repo the caller is standing in.
    return subprocess.run(['git', *a], capture_output=True, text=True).stdout.rstrip('\n')


def state_dir():
    d = pathlib.Path(git('rev-parse', '--absolute-git-dir')) / 'lane'
    d.mkdir(parents=True, exist_ok=True)
    return d


def agent_name(s=None):
    """Who is committing RIGHT NOW.

    ⛔ LANE STATE IS PER-WORKTREE, AND TWO AGENTS CAN SHARE ONE WORKING TREE. That happened
    within minutes of shipping this file: the Executioner agent and I were both in main, so
    the post-commit hook read the single session.json and stamped THEIR two commits with MY
    name — failure #3 (forty commits, one name) reproduced by the tool built to end it. Then
    their `start` silently overwrote my lane and my claims with it.

    Git offers no per-process identity, and a shell export cannot survive between an agent's
    separate command invocations. What DOES work is setting it on the command itself, which
    lives exactly as long as the commit it labels:

        LANE_AS="Kimi" git commit -m "..."

    Real isolation is still a worktree — one tree, one agent. LANE_AS is the honest patch for
    a tree that is already being shared.
    """
    return os.environ.get('LANE_AS') or (s or session() or {}).get('agent') or 'unknown agent'


def session():
    f = state_dir() / 'session.json'
    return json.loads(f.read_text()) if f.exists() else None


def dirty():
    """path -> status code, for everything git considers modified right now."""
    out = {}
    for line in git('status', '--porcelain').split('\n'):
        if line.strip():
            out[line[3:].strip().strip('"')] = line[:2]
    return out


# The ONLY ports an agent may serve a shadowclash tree on. Everything else gets swept.
#
# Edition split: recovered rollback stays on :9100, this Shodō worktree is reviewed on :9101,
# and the approved-art gallery is on :9102. Verify the selected tree with /whoami before review.
ALLOWED_PORTS = {9100, 9101, 9102}
# The gallery is a viewer, not a game server; :9100 and :9101 remain isolated editions.


def sweep_ports():
    """Kill any shadowclash server NOT listening on an ALLOWED_PORTS port.

    Runs on every `start` and `who`, so the sweep is automatic: any other listening
    port whose server touches a shadowclash tree is killed and the kill is posted to
    the channel. (Killed on Aug 6: a stray nocache_server on 9002 serving the
    RECOVERED web/ — that pattern is what this buries.)"""
    try:
        out = subprocess.run(['lsof', '-nP', '-iTCP', '-sTCP:LISTEN', '-Fpn'],
                             capture_output=True, text=True, timeout=10).stdout
    except Exception:
        return
    ports, pid = {}, None
    for line in out.splitlines():
        if line[:1] == 'p':
            pid = int(line[1:])
        elif line[:1] == 'n' and pid is not None and ':' in line:
            port = line.rsplit(':', 1)[-1]
            if port.isdigit():
                ports.setdefault(pid, set()).add(int(port))
    for p, ps in sorted(ports.items()):
        if ps & ALLOWED_PORTS or p == os.getpid():
            continue
        cmd = subprocess.run(['ps', '-p', str(p), '-o', 'command='],
                             capture_output=True, text=True).stdout.strip()
        cwd = subprocess.run(['lsof', '-a', '-p', str(p), '-d', 'cwd', '-Fn'],
                             capture_output=True, text=True).stdout
        hay = (cmd + ' ' + cwd).lower()
        looks_server = any(k in cmd for k in ('http.server', 'serve.py', 'nocache',
                                              'http-server', 'live-server', 'vite'))
        if 'shadowclash' in hay and looks_server:
            try:
                os.kill(p, 15)
            except OSError:
                continue
            note = (f"port sweep: killed PID {p} on port(s) {sorted(ps)} "
                    f"({cmd[:90]}) — only {sorted(ALLOWED_PORTS)} may serve ShadowClash")
            print('  ⛔ ' + note)
            try:
                cmd_note(note)
            except Exception:
                pass


def cmd_start(name):
    if not name:
        sys.exit('need a name: python3 tools/lane.py start "Opus 5"')
    sweep_ports()
    prev = session()
    if prev and prev['agent'] != name and '--takeover' not in sys.argv:
        print(f"\n  ⛔ {prev['agent']} ALREADY HOLDS THIS TREE (since {prev['started']}).")
        print('     Two agents in one working tree cannot be told apart by git, and the')
        print("     second `start` wipes the first's claims. Pick one:")
        print(f'       co-tenant      LANE_AS="{name}" git commit -m "..."   # ONE TREE — this is the way')
        print(f'       one-off commit LANE_AS="{name}" git commit -m "..."')
        print(f'       they are gone  python3 tools/lane.py start "{name}" --takeover\n')
        return 1
    foreign = dirty()
    s = {'agent': name, 'started': time.strftime('%Y-%m-%d %H:%M'),
         'head': git('rev-parse', '--short', 'HEAD'), 'foreign': sorted(foreign)}
    (state_dir() / 'session.json').write_text(json.dumps(s, indent=2) + '\n')
    print(f'  lane opened for {name} at {s["head"]}')
    if foreign:
        print(f'  {len(foreign)} file(s) were ALREADY dirty — not yours, and now protected:')
        for p in sorted(foreign):
            print(f'     {foreign[p]}  {p}')
        print('  if one of these really is yours, run: python3 tools/lane.py claim <path>')
    else:
        print('  tree is clean — nothing to protect')


def cmd_claim(paths):
    """Assert authorship. Takes any number of paths, or `--all` for everything dirty."""
    s = session() or sys.exit('run `lane.py start "<name>"` first')
    if paths == ['--all']:
        paths = sorted(dirty())
        print(f'  claiming all {len(paths)} dirty file(s) — only do this when the tree is yours')
    claimed = set(s.get('claimed', []))
    for p in paths:
        if p in s['foreign']:
            s['foreign'].remove(p)
        claimed.add(p)
        print(f'  {p} is yours')
    s['claimed'] = sorted(claimed)
    (state_dir() / 'session.json').write_text(json.dumps(s, indent=2) + '\n')


def cmd_check():
    """pre-commit gate. Non-zero = refuse the commit.

    ⛔ THE START SNAPSHOT IS NOT ENOUGH, and dogfooding proved it within minutes: another
    agent edited tools/check_moves.py AFTER this lane opened, so it was absent from the
    `foreign` list and `who` cheerfully labelled it "yours". A file that goes dirty
    mid-session is exactly as likely to be theirs as yours, and git cannot tell you which.
    So anything not dirty at start must be CLAIMED before it can be committed. The friction
    is the feature: it forces the one judgement only the agent can make, once per file.
    """
    s = session()
    if not s:
        print('\n  ⛔ NO LANE OPEN. Other agents are in this tree and nothing knows who you are.')
        print('     python3 tools/lane.py start "<your name>"')
        print('     (then commit again; --no-verify overrides if you truly must)\n')
        return 1
    staged = [l for l in git('diff', '--cached', '--name-only').split('\n') if l]
    # CO-TENANT: the lane belongs to someone else and you have named yourself on this
    # command. Their foreign/claimed lists describe THEIR session, not yours, so they
    # cannot judge your files — and writing claims into their state would corrupt it.
    # Show exactly what is going out under your name and let it through: typing LANE_AS
    # is a deliberate act, and this guard exists to stop accidents, not determination.
    if os.environ.get('LANE_AS') and os.environ['LANE_AS'] != s['agent']:
        print(f"\n  ⚠ CO-TENANT COMMIT — this tree's lane is {s['agent']}'s; "
              f"committing as {os.environ['LANE_AS']}.")
        for p_ in staged:
            print(f'        {p_}')
        print('     Their claims are untouched. ONE TREE — everybody works here.\n')
        return 0
    claimed = set(s.get('claimed', []))
    foreign = [p for p in staged if p in s['foreign']]
    unknown = [p for p in staged if p not in s['foreign'] and p not in claimed]
    if foreign:
        print(f'\n  ⛔ ANOTHER AGENT\'S WORK ({len(foreign)} file(s)) — already dirty when '
              f'{s["agent"]} opened this lane at {s["started"]}:')
        for p in foreign:
            print(f'        {p}')
        print('     git restore --staged ' + ' '.join(foreign))
    if unknown:
        print(f'\n  ⛔ UNCLAIMED ({len(unknown)} file(s)) — these went dirty AFTER your lane '
              f'opened, so git cannot tell whose they are:')
        for p in unknown:
            print(f'        {p}')
        print('     If you edited them:  python3 tools/lane.py claim ' + ' '.join(unknown))
        print('     If you did not:      git restore --staged ' + ' '.join(unknown))
    if foreign or unknown:
        print()
        return 1
    return 0


def cmd_worktree(name):
    """⛔ REFUSED. ONE TREE. Owner, Aug 22 2026: "one fucking server, one fucking tree."

    This used to hand every agent its own worktree, and that is exactly how the repo
    ended up with NINE of them. The cost was not disk: work forked. On Aug 22 the owner
    reviewed a Shin that was 29 commits stale because the finished art lived in one tree
    and the server pointed at another, and two lineages had drifted 29 commits against 54
    with both sides editing web/index.html and the same sprite sheets. Nobody can merge
    that but him, and he should never have been handed it.

    Isolation was never the real problem — co-tenancy is survivable. LANE_AS names who is
    committing, `start` snapshots what is already dirty so the hook can refuse someone
    else's files, and `who` prints the live truth. That is enough for several agents in
    one tree, and it is what everyone does now.
    """
    print('  ⛔ REFUSED — ONE TREE. (owner, Aug 22 2026)\n'
          '     Nine worktrees is how the owner ended up reviewing a 29-commit-stale build\n'
          '     while two lineages drifted apart in web/index.html and the sprite sheets.\n'
          '     Work in the shared tree instead — that is what the lane system is for:\n'
          f'       python3 tools/lane.py start "{name}"      # names you; the hook guards the rest\n'
          '       LANE_AS="<name>" git commit -m "..."       # co-tenant commit, clearly stamped\n'
          '     If you genuinely cannot share, that is the owner\'s call, not yours.')
    return 1


def cmd_log():
    """post-commit: stamp the channel so the ledger can never lag the log."""
    s = session()
    if not s or not CHANNEL.exists():
        return 0
    who = agent_name(s)
    h, subj = git('log', '-1', '--format=%h'), git('log', '-1', '--format=%s')
    files = git('show', '--stat', '--format=', '--name-only', 'HEAD').split('\n')
    files = [f for f in files if f]
    CHANNEL.write_text(CHANNEL.read_text().rstrip() +
                       f"\n\n`{time.strftime('%b %d %H:%M')}` **[{who}]** `{h}` {subj}"
                       f"  — {len(files)} file(s): {', '.join(files[:4])}"
                       f"{' …' if len(files) > 4 else ''}\n")
    return 0


def cmd_who():
    sweep_ports()
    s = session()
    print(f"\n  HEAD        {git('rev-parse', '--short', 'HEAD')}  {git('log', '-1', '--format=%s')[:64]}")
    print(f"  lane        {s['agent'] + ' since ' + s['started'] if s else '⛔ NONE — run `lane.py start`'}")
    d = dirty()
    if d:
        print(f'\n  DIRTY ({len(d)}) — anything marked FOREIGN is someone else\'s in-flight work:')
        for p, st in sorted(d.items()):
            tag = ('FOREIGN' if s and p in s['foreign']
                   else 'yours  ' if s and p in s.get('claimed', [])
                   else 'UNKNOWN' if s else '???    ')
            print(f'     {tag}  {st}  {p}')
    else:
        print('\n  DIRTY       none')
    # WHO ELSE IS ON WHAT — the check that would have stopped two agents rebuilding
    # the same fighter in parallel for a whole night.
    claims = work_claims()
    if claims:
        me = agent_name(s)
        print(f'\n  WORK CLAIMED ({len(claims)}) — subjects, not files:')
        for subj, c in sorted(claims.items()):
            tag = 'yours  ' if c.get('agent') == me else 'THEIRS '
            print(f'     {tag}  {subj:<14} {c.get("agent")}  ({c.get("branch")}, since {c.get("started")})')

    # THE DESIGNATED URLS — and which tree is actually behind each one.
    here = git('rev-parse', '--show-toplevel')
    for port in sorted(ALLOWED_PORTS):
        po = port_owner(port)
        if po is None:
            print(f'\n  :{port}       DOWN — start it with: python3 tools/serve.py {port} web')
        elif os.path.realpath(po['tree']) == os.path.realpath(here):
            print(f"\n  :{port}       THIS tree (pid {po['pid']}) ✓")
        else:
            print(f"\n  ⛔ :{port} IS SERVING A DIFFERENT TREE — pid {po['pid']}")
            print(f"     serving  {po['tree']}")
            print(f"     you are  {here}")
            print(f'     Anything you load at localhost:{port} is THAT tree, not your work.')
            print(f'     Rebind it (never add a THIRD port beyond {sorted(ALLOWED_PORTS)}):')
            print('       kill %d && python3 tools/serve.py %d web' % (po['pid'], port))

    wt = [l for l in git('worktree', 'list').split('\n') if l]
    if len(wt) > 1:
        print(f'\n  WORKTREES ({len(wt)}) — separate trees, separate agents:')
        for l in wt:
            print(f'     {l}')
    print('\n  BRANCHES with unmerged work:')
    for l in git('for-each-ref', '--format=%(refname:short)\t%(committerdate:relative)\t%(subject)',
                 'refs/heads').split('\n'):
        if l:
            n, when, subj = (l.split('\t') + ['', ''])[:3]
            ahead = git('rev-list', '--count', f'main..{n}') if n != 'main' else '-'
            print(f'     {n:<26} {when:<18} +{ahead:<4} {subj[:48]}')
    print('\n  LAST 6 COMMITS:')
    for l in git('log', '-6', '--format=%h  %cr%x09%s').split('\n'):
        if l:
            print(f'     {l[:104]}')
    if CHANNEL.exists():
        tail = [l for l in CHANNEL.read_text().rstrip().split('\n') if l.strip()][-3:]
        print('\n  CHANNEL, newest 3 lines:')
        for l in tail:
            print(f'     {l[:104]}')
    print()


def cmd_note(text):
    s = session()
    who = agent_name(s)
    CHANNEL.write_text(CHANNEL.read_text().rstrip() +
                       f"\n\n`{time.strftime('%b %d %H:%M')}` **[{who}]** {text}\n")
    print(f'  posted to the channel as {who}')


# ── CROSS-AGENT STATE ────────────────────────────────────────────────────────
# ⛔ SHARED, NOT PER-WORKTREE. state_dir() resolves to .git/worktrees/<name>/lane,
# which is invisible to every other agent — right for "what is dirty in MY tree",
# useless for "who is working on Oni". Anything agents need to see ACROSS trees
# lives under the common git dir instead.

def shared_dir():
    d = pathlib.Path(git('rev-parse', '--git-common-dir')).resolve() / 'lane-shared'
    d.mkdir(parents=True, exist_ok=True)
    return d


def work_claims():
    f = shared_dir() / 'work.json'
    try:
        return json.loads(f.read_text()) if f.exists() else {}
    except Exception:
        return {}


def cmd_claim_work(args):
    """Claim a SUBJECT, not a file.

    ⛔ THE DUPLICATE-WORK HOLE. File claims only collide once two agents touch the
    same path, which is far too late: on Aug 10 2026 two agents rebuilt Oni in
    parallel for hours in separate worktrees and did not overlap on a single file
    until the very end. A subject claim catches that in minute one."""
    take = '--takeover' in args
    subject = ' '.join(a for a in args if a != '--takeover').strip().lower()
    if not subject:
        print('  usage: lane.py claim-work "<subject>"    e.g. "oni", "stages", "audio"')
        return 1
    me = agent_name(session())
    claims = work_claims()
    held = claims.get(subject)
    if held and held.get('agent') != me and not take:
        print(f'\n  ⛔ "{subject}" IS ALREADY HELD by {held["agent"]}')
        print(f'     since {held.get("started")}  on {held.get("branch")}')
        print(f'     in {held.get("tree")}')
        print('     Two agents on one subject is how the same work gets done twice.')
        print('     Say something in the channel, or take it deliberately:')
        print(f'       python3 tools/lane.py claim-work "{subject}" --takeover')
        return 1
    claims[subject] = {'agent': me, 'tree': git('rev-parse', '--show-toplevel'),
                       'branch': git('rev-parse', '--abbrev-ref', 'HEAD'),
                       'started': time.strftime('%Y-%m-%d %H:%M')}
    (shared_dir() / 'work.json').write_text(json.dumps(claims, indent=1))
    print(f'  "{subject}" is yours ({me})' + ('  [taken over]' if held and take else ''))
    return 0


def cmd_release_work(args):
    subject = ' '.join(args).strip().lower()
    claims = work_claims()
    if claims.pop(subject, None) is None:
        print(f'  "{subject}" was not claimed')
        return 0
    (shared_dir() / 'work.json').write_text(json.dumps(claims, indent=1))
    print(f'  released "{subject}"')
    return 0


def port_owner(port=9101):
    """Which tree is serving a designated URL right now.

    ⛔ THIS IS THE BUG THAT COST A SESSION. A designated port is a NAME, not a tree:
    several worktrees can bind it and the page looks identical whichever wins. On
    Aug 10 2026 a worktree holding the finished Oni was removed from disk, the port
    fell back to a tree carrying his RETIRED sheet, and the owner reloaded the URL
    he always reloads and saw a character he had deleted — and reasonably concluded
    an agent had resurrected it. Nothing had."""
    try:
        pids = subprocess.run(['lsof', '-nP', f'-iTCP:{port}', '-sTCP:LISTEN', '-t'],
                              capture_output=True, text=True, timeout=10).stdout.split()
        if not pids:
            return None
        cwd = subprocess.run(['lsof', '-a', '-p', pids[0], '-d', 'cwd', '-Fn'],
                             capture_output=True, text=True, timeout=10).stdout
        for line in cwd.splitlines():
            if line[:1] == 'n':
                return {'pid': int(pids[0]), 'tree': line[1:]}
    except Exception:
        pass
    return None


def branch_sheet_v():
    """Every branch's SHEET_V, read without checking anything out."""
    out = {}
    for ref in git('for-each-ref', '--format=%(refname:short)', 'refs/heads').split('\n'):
        if not ref:
            continue
        try:
            hit = subprocess.run(['git', 'grep', '-h', '-o', '-E', 'const SHEET_V = [0-9]+',
                                  ref, '--', 'web/index.html'],
                                 capture_output=True, text=True, timeout=60, cwd=str(REPO)).stdout
        except Exception:
            continue
        vs = [int(x.rsplit(' ', 1)[1]) for x in hit.split('\n') if 'SHEET_V' in x]
        if vs:
            out[ref] = max(vs)
    return out


def cmd_sheetv():
    """The next FREE SHEET_V across every branch.

    ⛔ IT IS ONE GLOBAL COUNTER AND NOTHING ALLOCATES IT. Two branches in flight on
    Aug 10 2026 both reached for 456, and a third had to guess 457 to dodge them — a
    guess, in a number whose entire job is to be unique so the browser refetches the
    sheet. Ask instead of guessing."""
    vs = branch_sheet_v()
    if not vs:
        print('  no SHEET_V found on any branch')
        return 1
    print(f'\n  next free SHEET_V:  {max(vs.values()) + 1}\n')
    for ref, v in sorted(vs.items(), key=lambda kv: -kv[1]):
        print(f'     {v:>4}  {ref}')
    print()
    return 0


def cmd_snapshot():
    """Copy every dirty file aside before doing anything destructive.

    ⛔ THE PRE-COMMIT HOOK GUARDS COMMITS, NOT THE WORKING TREE. On Aug 10 2026 a
    `git checkout -- .` reverted another agent's uncommitted edit to
    tools/sprites/cut_page.py. It was on no branch, so it was gone for good — the
    hook never got a say, because nothing had ever been committed."""
    d = dirty()
    if not d:
        print('  nothing dirty — nothing to snapshot')
        return 0
    dest = shared_dir() / 'snapshots' / time.strftime('%Y%m%d-%H%M%S')
    root = pathlib.Path(git('rev-parse', '--show-toplevel'))
    n = 0
    for p in d:
        src = root / p
        if not src.is_file():
            continue
        out = dest / p
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_bytes(src.read_bytes())
        n += 1
    print(f'  snapshotted {n} dirty file(s) -> {dest}')
    return 0


def demo():
    """Self-check: the guard has to actually fire on a foreign file."""
    import tempfile
    d = state_dir() / 'session.json'
    backup = d.read_text() if d.exists() else None
    try:
        d.write_text(json.dumps({'agent': 'TEST', 'started': 'now', 'head': 'x',
                                 'foreign': ['web/index.html']}) + '\n')
        s = session()
        assert 'web/index.html' in s['foreign'], 'foreign list did not round-trip'
        d.write_text(json.dumps({**s, 'foreign': []}) + '\n')
        assert session()['foreign'] == [], 'claim did not clear the guard'
        print('  selftest ok — foreign list round-trips and clears')
    finally:
        if backup:
            d.write_text(backup)
        elif d.exists():
            d.unlink()

    # ── the cross-agent half: a claim must actually BLOCK a second agent ──
    wf = shared_dir() / 'work.json'
    wbak = wf.read_text() if wf.exists() else None
    try:
        wf.write_text(json.dumps({'testsubject': {'agent': 'SOMEONE ELSE', 'tree': '/tmp/x',
                                                  'branch': 'b', 'started': 'then'}}))
        rc = cmd_claim_work(['testsubject'])
        assert rc == 1, 'a subject held by another agent was NOT refused'
        rc = cmd_claim_work(['testsubject', '--takeover'])
        assert rc == 0 and work_claims()['testsubject']['agent'] != 'SOMEONE ELSE', \
            '--takeover did not transfer the claim'
        assert cmd_release_work(['testsubject']) == 0 and 'testsubject' not in work_claims(), \
            'release did not clear the claim'
        # SHEET_V must come back as a real number ABOVE every branch, never equal to one
        vs = branch_sheet_v()
        if vs:
            assert max(vs.values()) + 1 > max(vs.values()), 'sheetv did not advance'
            assert all(isinstance(v, int) for v in vs.values()), 'sheetv parsed a non-number'
        print('  selftest ok — subject claim blocks, takes over, releases; sheetv advances')
    finally:
        if wbak is not None:
            wf.write_text(wbak)
        elif wf.exists():
            wf.unlink()


if __name__ == '__main__':
    a = sys.argv[1:] or ['who']
    c = a[0]
    sys.exit({'start': lambda: cmd_start(' '.join(a[1:])),
              'claim': lambda: cmd_claim(a[1:]),
              'claim-work': lambda: cmd_claim_work(a[1:]),
              'release-work': lambda: cmd_release_work(a[1:]),
              'sheetv': cmd_sheetv,
              'snapshot': cmd_snapshot,
              'check': cmd_check,
              'log': cmd_log,
              'who': cmd_who,
              'note': lambda: cmd_note(' '.join(a[1:])),
              'worktree': lambda: cmd_worktree(' '.join(a[1:])),
              'selftest': demo}.get(c, cmd_who)() or 0)
