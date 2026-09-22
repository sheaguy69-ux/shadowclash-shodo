#!/usr/bin/env python3
"""Shadow Clash local dev server — the ONE way to serve web/ for review.

Identical to `python3 -m http.server` except every response carries
Cache-Control: no-store. That header is the whole point: plain http.server sends
no cache headers, so browsers fall back to heuristic caching off Last-Modified
and will happily pin a weeks-old index.html and stale sprite PNGs. On a project
where the deliverable IS the sprite bytes, that makes a landed fix look broken
and sends you chasing a bug that isn't there.

Adopted from /tmp/nocache_server.py so it survives a reboot and every agent
reaches for the same thing. Wired as the only entry in .claude/launch.json.

Usage:  python3 tools/serve.py [PORT] [DIRECTORY]
Default: port 9101, directory web/  (this Shodō worktree)

Edition ports: recovered rollback :9100, this Shodō playable edition :9101, and
the approved-art gallery :9102. Explicit ports remain supported for each edition.
Use one server per edition and verify its identity before review.

WHICH TREE AM I LOOKING AT?  ->  curl -s localhost:9101/whoami

That question is not academic. This repo has several worktrees, every one of
them holds a full web/, and any of them can bind an edition port — but the page looks
identical whichever wins. On 2026-08-10 a lane worktree holding the finished
Oni was removed from disk, :9100 fell back to a tree carrying his RETIRED
349-cell sheet, and the owner reloaded the URL he always reloads and saw a
character he had deleted. He reasonably concluded an agent had resurrected it.
Nothing had: one port, many trees, and no way to tell them apart.

So /whoami reports the tree, branch, HEAD and SHEET_V actually being served.
Ask it before believing anything about what is or isn't in the build.
"""
import http.server
import json
import os
import re
import subprocess
import sys

PORT = int(sys.argv[1]) if len(sys.argv) > 1 else 9101
DIRECTORY = sys.argv[2] if len(sys.argv) > 2 else "web"


def _identity():
    """Tree, branch, HEAD and SHEET_V of what this process is actually serving."""
    root = os.path.abspath(os.curdir)

    def git(*a):
        try:
            return subprocess.run(("git",) + a, cwd=root, capture_output=True,
                                  text=True, timeout=5).stdout.strip() or None
        except Exception:
            return None

    sheet_v = None
    try:
        # SHEET_V's line carries a ~1.3MB changelog comment, so scan line by line
        # rather than reading the whole file in.
        with open(os.path.join(DIRECTORY, "index.html"), encoding="utf8",
                  errors="replace") as fh:
            for line in fh:
                m = re.search(r"const SHEET_V = (\d+)", line)
                if m:
                    sheet_v = int(m.group(1))
                    break
    except OSError:
        pass

    return {"tree": root, "branch": git("rev-parse", "--abbrev-ref", "HEAD"),
            "head": git("log", "-1", "--format=%h %s"), "sheet_v": sheet_v,
            "directory": DIRECTORY, "pid": os.getpid()}


class NoStoreHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *a, **kw):
        super().__init__(*a, directory=DIRECTORY, **kw)

    def do_GET(self):
        if self.path.split("?")[0] == "/whoami":
            body = json.dumps(_identity(), indent=2).encode()
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
            return
        super().do_GET()

    def end_headers(self):
        self.send_header("Cache-Control", "no-store")
        # Visible in devtools' Network tab without needing to hit /whoami.
        self.send_header("X-ShadowClash-Tree", os.path.basename(os.path.abspath(os.curdir)))
        # Lets a harness on another origin fetch sprite bytes / whoami.
        # ⛔ No COOP/COEP here: index.html loads Tailwind/FontAwesome/Google Fonts
        # from CDNs, and COEP: require-corp would block them (no wasm needs it).
        self.send_header("Access-Control-Allow-Origin", "*")
        super().end_headers()

    def log_message(self, *a):
        pass


if __name__ == "__main__":
    me = _identity()
    http.server.ThreadingHTTPServer.allow_reuse_address = True
    with http.server.ThreadingHTTPServer(("", PORT), NoStoreHandler) as srv:
        print("serving %s on :%d with Cache-Control: no-store" % (DIRECTORY, PORT))
        print("  tree    %s" % me["tree"])
        print("  branch  %s  @ %s" % (me["branch"], me["head"]))
        print("  SHEET_V %s        <- this is the build the browser will show" % me["sheet_v"])
        srv.serve_forever()
