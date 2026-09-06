#!/usr/bin/env python3
"""Run the all-nine live facing/wall regression (replaces the obsolete equal-sign probe).

Cling poses face the wall; ordinary attacks and wall jumps face the arena.
The former probe required identical mirror signs for both, enforcing backward attacks.
"""
import os
from pathlib import Path
import subprocess
import sys
from urllib.parse import urlsplit

repo = Path(__file__).resolve().parents[1]
env = dict(os.environ)
if "SHADOWCLASH_URL" in env:
    env["PORT"] = str(urlsplit(env["SHADOWCLASH_URL"]).port or 9101)
sys.exit(subprocess.call(["node", str(repo / "tools/check_direction_compass.mjs")], cwd=repo, env=env))
