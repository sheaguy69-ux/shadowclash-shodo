#!/usr/bin/env python3
"""The public battle build's six gates, asserted against web/index.html.

This branch is a SNAPSHOT, so the risk is not that someone argues with the gates —
it is that a later merge from main quietly reopens one and nobody notices until the
public link is already serving it. Each assert below is a thing that was actually
found open during the build (four of them only turned up when the behaviour was
measured, not when the source was read), so each one earns its line.

    python3 tools/test_public_battle.py
"""
import re
import sys
import pathlib

SRC = pathlib.Path(__file__).resolve().parent.parent / "web" / "index.html"
html = SRC.read_text()

# The dispatch reads no input at all. Both routes matter: the axis/down/up locals AND
# the DIR_SPECIALS table, which reaches the stick through heldDir() instead and so
# survived the first pass with Shin's anti-air and Tsubasa's dive cut still live.
i = html.index("triggerSpecialAction(opponent) {")
j = html.index("const de = DIR_SPECIALS[", i)
dispatch = html[i:j]
leaks = re.findall(r"this\.(?:getInputAxis|isUpPressed|isDownPressed)\(\)", dispatch)
assert not leaks, f"directional Special leak: dispatch reads input {len(leaks)}x"
assert "const axis = 0, down = false, up = false;" in dispatch, "neutral pin missing"
assert "DIR_SPECIALS[specId + ':' + null]" in html, "DIR_SPECIALS table not pinned neutral"
assert "heldDir(this)" not in html[i:html.index("\n        }", j)], "heldDir still read in dispatch"

# The Executioner's Back+S quick-draw converts the input BEFORE the dispatch, so the
# neutral pin cannot reach it; without this gate it is the lone surviving directional.
assert "if (false && type === STATE.ATTACK_SPECIAL && this.spec.id === 0" in html, \
    "Executioner Back+S quick-draw route is open again"

# Six fighters. The pair is benched by data, and the grid honours the flag.
benched = re.findall(r'name: "(Mokurai|Exile)",\s*\n\s*benched: true', html)
assert len(benched) == 2, f"expected Mokurai/Exile benched, got {benched}"
assert "if (ninja.benched) return;" in html, "roster grid no longer honours benched"

# ...and three side doors that let a benched fighter back in anyway.
assert "NINJA_ROSTER.filter(n => !n.benched).map(n => n.id)" in html, \
    "title-screen attract can pick a benched fighter again"
assert "NINJA_ROSTER[i].benched" in html, "saved-pick guard no longer rejects benched"

# Battle modes only: no ladder, and no saved pref that can restore one.
assert "['cpu', '2p', 'watch', 'training']" in html, "story/arcade back on the mode allowlist"
assert 'data-mode="story"' not in html and 'data-mode="arcade"' not in html, \
    "STORY/ARCADE buttons are back in the mode menu"

# The bench must be a CONTENT gate, not just a UI gate. This loop walked the raw
# roster, so every visitor downloaded 6.2MB of parked sheets for fighters the
# build cannot spawn.
assert "if (n.benched) return;" in html, "preloader fetches benched sprite sheets again"

# ...and the files themselves stay off the host, so a guessed URL finds nothing.
IGNORE = SRC.parent / ".vercelignore"
assert IGNORE.exists(), "web/.vercelignore is missing — parked art would deploy"
ign = IGNORE.read_text()
for pat in ("assets/sprites/mokurai.*", "assets/sprites/exile.*",
            "bosses-fullbody.png", "_review/"):
    assert pat in ign, f".vercelignore no longer excludes {pat}"

print("public battle build: 6 fighters, neutral Special only, no ladder — all gates hold")
