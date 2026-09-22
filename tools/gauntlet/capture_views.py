#!/usr/bin/env python3
"""Gauntlet Loop capture harness for ShadowClash.

Runs the REAL game (localhost:9100) in headless Chromium at full HD and
samples frames while a CPU-vs-CPU (WATCH) match plays itself, so every
reachable state — idle, run, jump, attack, hurt, block, special — appears
naturally. Each frame is labeled with both fighters' live states so a harsh
critic subagent can blind-A/B them against the owner-approved reference
frames (RECOVERY/brain-assets/approved/) and name the biggest gap.

Usage:
  python3 tools/gauntlet/capture_views.py [--p1 exile] [--p2 mokurai]
      [--duration 60] [--fps 2] [--out media/gauntlet]

Exit 0 = frames captured; prints the out dir + a state table on stdout.
"""
import argparse
import json
import pathlib
import subprocess
import sys
import time

from playwright.sync_api import sync_playwright

GAME_URL = "http://localhost:9100/"
STATE_EVAL = """
(() => {
  const nm = s => {
    try { return Object.entries(STATE).find(([k, v]) => v === s)?.[0] ?? String(s); }
    catch { return String(s); }
  };
  return JSON.stringify({
    p1: player1 ? { name: player1.spec.name, state: nm(player1.state),
                    x: Math.round(player1.x), y: Math.round(player1.y),
                    anim: player1.animPhase, hp: Math.round(player1.hp) } : null,
    p2: player2 ? { name: player2.spec.name, state: nm(player2.state),
                    x: Math.round(player2.x), y: Math.round(player2.y),
                    anim: player2.animPhase, hp: Math.round(player2.hp) } : null,
    matchActive: !!matchActive, roundIntro: roundIntroTimer ?? null,
  });
})()
"""


def pick_fighter(page, name):
    """Click the roster card whose fighter name matches (case-insensitive)."""
    card = page.locator(f"#character-selection .sc-card:has(.nm:text-is('{name}'))").first
    card.wait_for(state="visible", timeout=15000)
    card.click()
    page.wait_for_timeout(250)


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--p1", default="Exile", help="P1 fighter name (WATCH mode)")
    ap.add_argument("--p2", default="Mokurai", help="P2 fighter name (WATCH mode)")
    ap.add_argument("--duration", type=float, default=45.0, help="match seconds to sample")
    ap.add_argument("--fps", type=float, default=2.0, help="samples per second")
    ap.add_argument("--out", default="media/gauntlet", help="output directory")
    args = ap.parse_args()

    out = pathlib.Path(args.out) / time.strftime("%Y-%m-%d_%H%M%S")
    out.mkdir(parents=True, exist_ok=True)

    with sync_playwright() as pw:
        browser = pw.chromium.launch(
            headless=True,
            executable_path="/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
            args=[
                "--disable-background-timer-throttling",
                "--disable-renderer-backgrounding",
                "--disable-backgrounding-occluded-windows",
                "--autoplay-policy=no-user-gesture-required",
                "--mute-audio",
                "--no-first-run",
            ],
        )
        ctx = browser.new_context(viewport={"width": 1920, "height": 1080}, device_scale_factor=1)
        page = ctx.new_page()
        page.goto(GAME_URL, wait_until="domcontentloaded")
        page.wait_for_timeout(1200)

        # Dismiss the title (any key), then set WATCH mode so both CPUs fight.
        page.keyboard.press("Enter")
        page.wait_for_timeout(500)
        page.click('.mode-btn[data-mode="watch"]')
        page.wait_for_timeout(300)
        pick_fighter(page, args.p1)
        pick_fighter(page, args.p2)
        page.click("#btn-fight")
        page.wait_for_timeout(1500)

        interval = 1.0 / max(args.fps, 0.5)
        n = int(args.duration / interval)
        frames, states = [], []
        for i in range(n):
            shot = out / f"f{i:04d}.png"
            page.screenshot(path=str(shot))
            st = page.evaluate(STATE_EVAL)
            frames.append(shot.name)
            states.append(json.loads(st))
            sys.stdout.write(f"\r{shot.name}  p1={states[-1]['p1']['state'] if states[-1]['p1'] else '?'}"
                             f"  p2={states[-1]['p2']['state'] if states[-1]['p2'] else '?'}   ")
            sys.stdout.flush()
            if not (states[-1].get("matchActive") or states[-1].get("roundIntro")):
                break  # match over / never started — stop sampling
            page.wait_for_timeout(int(interval * 1000))

        meta = {
            "game_url": GAME_URL,
            "viewport": "1920x1080",
            "p1": args.p1, "p2": args.p2,
            "reference_frames": "RECOVERY/brain-assets/approved/ (owner-corrected + polished refs)",
            "frames": frames,
            "states": states,
        }
        (out / "meta.json").write_text(json.dumps(meta, indent=2))
        browser.close()

    sys.stdout.write("\n")
    print(f"GAUNTLET CAPTURE DONE -> {out}  ({len(frames)} frames)")
    print(f"States seen: {sorted({s['p1']['state'] for s in states if s['p1']})}")
    print(f"             {sorted({s['p2']['state'] for s in states if s['p2']})}")
    print("Critic: blind-A/B each frame vs the approved refs; name the biggest gap; loop until ours wins.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
