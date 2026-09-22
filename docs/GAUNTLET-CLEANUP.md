# GAUNTLET CLEANUP — ShadowClash edition

**For:** Claude Code (Opus 5 / Fable 5), run this in the main tree
(`/Users/anthonyguy/SHADOWCLASH-RECOVERED`), lane up first (`python3 tools/lane.py start "..."`).
**Owner order:** Aug 6 2026 — adapt the Gauntlet Loop to ShadowClash and use it to
clean **everything that has not been created yet** in the game. 2D fighting platform.

---

## THE MISSION (paste verbatim into Claude Code)

```
I want you to finish ShadowClash, a 2D fighting-platform game, so that every
single move, state and frame that is supposed to exist actually exists and looks
on-model with the owner's approved art. It should be utterly complete: no
stand-in cells, no move that draws the wrong pose, no page of the kit missing.

Fan out sub-agents and have sub-agents tackle each gap individually so the game
is utterly complete. You should /loop on each item and have a separate sub-agent
check it visually — run the real game headlessly, capture the fighter mid-move
in full HD, compare blind against the owner's approved reference frames — to
ensure every state is drawn and on-model. That separate sub-agent should be a
really harsh critic, and if the pose is missing, wrong, or off-model, it should
keep going.

Don't stop until each sub-agent is utterly wowed with the completeness and
quality when compared side by side, blind, against the owner-approved frames
(RECOVERY/brain-assets/approved/), and ours wins. /loop until it's utterly
complete. Fan out sub-agents and ultracode.
```

## THE BAR (what "done" means here)

1. **Zero gaps from `docs/WHAT-IS-MISSING.md`** — Exile page 5 (slides + crouch),
   Mokurai pages M1–M6 (jump/fall arc, air attacks, hurt/guard, ground movement,
   heavy chain, meditation channel). Six of nine fighters are already healthy.
2. **No stand-in cells.** A cell doing 14 jobs (Mokurai cell 47) is a missing
   frame, not a feature. Sweep every state reachable in play and verify each
   draws its own art.
3. **On-model vs owner-approved refs.** Blind A/B against
   `RECOVERY/brain-assets/approved/*.png` (owner-corrected + polished refs).
   Critic picks the better; ours must win or the art goes back.
4. **Frames the owner supplied that are not yet implemented** — plug them in:
   the wash, the predator-thread kit, and the attack sheets the owner gave
   (see `~/Downloads/`: `mizu new attacks.png`, `ex attacks.png`,
   `Executioner new special attacks.png`, `exile new air grapple.png`,
   `oni def:react.png`, `oni changing weapons frames.png`, etc.).
   ⛔ **MODE 3 IS EXCLUDED** — owner: "dont plugin mode 3". Do not touch,
   wire, or draw mode-3 content in this pass.

## THE HARNESS (already built — use it, don't rebuild it)

```bash
# Real game, headless Chromium, full HD, CPU-vs-CPU so every state appears:
python3 tools/gauntlet/capture_views.py --p1 exile --p2 mokurai --duration 45 --fps 2
# -> media/gauntlet/<timestamp>/  (frames + meta.json with live state per frame)
```

- Game URL is **ONE: http://localhost:9100** (`python3 tools/serve.py`). No other ports.
- Capture frames are labeled with each fighter's live state (IDLE / RUN / JUMP /
  ATTACK_LIGHT / ATTACK_HEAVY / ATTACK_SPECIAL / BLOCKING / STUNNED /
  SUBSTITUTION / THROWING / ...) so the critic can demand the right pose per state.
- For targeted single-move captures use the proven CDP driver:
  `python3 tools/watch_game.py --script tools/watch_scripts/<your>.json --out /tmp/x`.
- **Verify by WATCHING**: filmstrip the loop, never trust static asserts
  (rule 5 in AGENTS.md).

## THE CRITIC PROTOCOL (per gap)

1. Fresh subagent, no builder history (rule 4 of the loop — never let the
   builder grade itself).
2. Show it: our capture frame(s) of the fighter in that state + the approved
   reference frame for that fighter. Blind — it does not know which is which.
3. Verdict must name: (a) which looks better, (b) the single biggest gap, in
   drawing terms (missing cell / wrong pose / off-model / stand-in), not vibes.
4. If ours loses → back to the builder with the critic's note. No arbitrary
   round cap — loop until ours wins or the owner stops it.

## HOUSE RULES (violations get reverted — AGENTS.md)

- **Sprite sheets are append-only.** New cells go at the END of the sheet
  (cols grow). Never re-encode an existing png; composite onto it.
- **Bump `SHEET_V`** (web/index.html) in the SAME commit as any sprite change.
- **FACING LEFT.** `drawSprite` mirrors by `-p.facing` — a right-facing cell
  renders backwards in play. This has bitten three fighters already.
- **No baked ground shadow** (engine draws its own), **no second character in
  the frame** (engine draws the opponent).
- **Leave gaps between drawings on a page** — overlapping FX arcs make pages
  unsplittable.
- Identity strings for new pages: Exile + Mokurai are in `docs/WHAT-IS-MISSING.md`
  section 3. Paste them into every generation prompt.
- FAL models live ONLY in `tools/sprites/fal_models.py` — import, never hardcode.
- **Lane protocol**: claim what you edit (`lane.py claim <paths>`); unclaimed
  edits are protocol violations. Commit only your own work.

## THE LOOP

```
for each gap in WHAT-IS-MISSING + owner-supplied unplugged frames (minus mode 3):
    builder draws/wires it (subagent, own lane claim)
    harness captures it live (capture_views.py or watch_game.py)
    fresh critic blind-A/Bs against approved refs
    while ours loses: hand critic's note back to builder, re-capture, re-judge
after all gaps: full-roster sweep — every fighter, every state, filmstrip verify
```
