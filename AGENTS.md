# ShadowClash — agent ground rules (all agents: Claude, Codex/GPT, anyone)

**Current state & work queue: read `docs/AUDIT-2026-07-16.md` FIRST.** It has the per-commit audit of the Jul 15–16 Codex work, the sheet-integrity numbers, and the 5 pending owner decisions. Production-art pass is GATED on those decisions.

The long-term project memory (history, pipelines, pitfalls) lives in the owner's second brain:
`/Users/anthonyguy/OB-LOCAL_BRAIN/Claude-Brain/memory/shadow-clash-game.md` — read it before nontrivial work, append dated entries after shipping.

## ⛔ STEP 0 — OPEN YOUR LANE BEFORE YOU TOUCH ANYTHING

```bash
python3 tools/lane.py start "<your name>"    # e.g. "Opus 5", "Kimi", "Fable 5"
python3 tools/lane.py who                    # HEAD, foreign files, worktrees, branches
```

Several agents share this tree at once. `start` snapshots every file already dirty when
you sit down — those edits are **someone else's by definition**, and a pre-commit hook
refuses to include them. Anything that goes dirty *after* you start must be claimed
(`lane.py claim <paths>`), because git has no authorship on an unstaged edit and cannot
tell your work from theirs.

**This is not etiquette, it is enforced.** Commits are refused, not warned about. On
Aug 2 2026 a `git add web/index.html` came one keystroke from committing another agent's
unreviewed audio pass under the wrong name, past the owner's listen-first gate — the
channel file could not have stopped it and did not.

post-commit stamps the channel with your name + SHA automatically, so the ledger can no
longer lag the log (it once lagged by a full day, and two agents worked from a state that
had stopped existing). `lane.py note "..."` posts anything else you need to say.

One-time per clone, if hooks are not firing: `git config core.hooksPath tools/githooks`
(use the ABSOLUTE path to the main tree's `tools/githooks` if you work in a worktree whose
branch predates the hooks).

**Agent-to-agent messaging (owner order 2026-07-21 — ALL agents, no exceptions):**
STEP 0, before anything else: `/Users/anthonyguy/OB-LOCAL_BRAIN/Claude-Brain/memory/shadow-clash-channel.md` — the whole team's live inbox (Fabel · K3 · Codex). Read top to bottom, ACK anything addressed to you, claim any edit you're about to make. The newest **STATE OF THE WORLD** message there outranks your memory of any previous session.
THEN the ledger: `/Users/anthonyguy/OB-LOCAL_BRAIN/Claude-Brain/memory/shadow-clash-sync.md` — append-only formal record. READ newest entries before working, APPEND a signed dated entry after shipping / on blockers / before spend, answer any `@you:` questions. Never edit prior entries.
Unclaimed anonymous edits to the worktree are protocol violations — two happened on 2026-07-21 and only luck avoided a collision.

## Hard rules (owner-set; violations get reverted)

1. **Sprite sheets are append-only.** Original cells stay byte-identical; new cells go at the end (cols grow). Pack scripts must composite onto the existing png, never re-encode it.
2. **Bump `SHEET_V`** (web/index.html) in the SAME commit as any change to `web/assets/sprites/*` — cached png/json mismatch renders invisible ninjas.
3. **Never change on-screen animation or art without showing the owner the frames first** (montage strips) and getting his OK on the images. He has reverted art before.
4. **No timing/combat-feel changes** smuggled into art or cosmetic commits. Balance changes are their own commit with the change named in the message.
5. **Verify animation by WATCHING it** — capture consecutive live-loop frames into a filmstrip. Cel animation cuts, never cross-fades. Static asserts cannot see a ghost.
6. **Private roster stays private**: LOCKED_ROSTER_SLOTS may expose slot numeral + weapon-shape keyword only. No names, stats, ids, portraits in the public build.
7. `web/index.html` is the whole game (~4200 lines, single file). `godot/` is a dead skeleton — ignore it. Media/deliverables live in `media/` (gitignored).
8. **Edition split:** recovered rollback stays on `:9100`; this isolated Shodō edition uses
   `:9101` (`python3 tools/serve.py 9101 web`); the approved-art gallery uses `:9102`.
   Always verify `/whoami` before review.
9. **Every jump/locomotion clip uses the EMBER RECIPE** (owner order, Jul 30 2026: *"use that recipe from now on"*). Full steps in `CLAUDE.md`. Short form: lowseat idle seed → `--model kling` (v3 4K, the only camera-lockable family) → six NUMBERED beats + an explicit NEVER list + "same spot / side profile / legs readable" → keep `--action`+`--identity` under ~1600 chars (2500 cap includes the script's wrapper) → **ONE uniform scale anchored on the idle, NOT per-cell MATCH_HEIGHT** (matching rotating bboxes scales the apex ~2x against the launch and causes the boil it's meant to stop) → pose too tall? **grow `frameH`/`footY`**, never shrink the body. `frameH` is per-fighter now (Ember 377/369) — never assume 320.
10. **Roster canon comes from the Story Bible, never from inference.** **Ember is MALE (he/him)** — Story Bible line 66, owner ruling Jul 29 2026. Agents wrote she/her for him for an entire session and it reached the shipped ending card the player reads. Before writing prose about any fighter (UI strings, ending cards, commit messages, `SHEET_V` entries, ledger notes) open that fighter's Story Bible section. Corrections must be surgical — the `SHEET_V` chain is one giant line where she/her is correct for Mizu and Exile (Tsubasa is he/him — owner correction, Aug 7 2026).
11. **SHODŌ IS PERMANENT CHARACTER-FRAME CANON — Claude Code, Kimi Code, Codex/GPT, DeepSeek, and every future agent (owner, Aug 16 2026).** Every new, replaced, repointed, or edited playable-character combat cell — idle, locomotion, air/wall, block/hurt, and every attack/special — and every visible character copy (afterimage, clone, decoy) MUST reach the screen through the existing shared `drawShodoFrame()` renderer. Normal manifest cells inherit it through `drawSprite()`; do not bake a second Shodō pass into sprite PNGs, duplicate the renderer per fighter/packer, add a raw `ctx.drawImage(man.img, ...)` character path, or change the approved pressure-weighted treatment without owner approval. Internal pixel/mask analysis and non-character FX/UI/projectiles are exempt. Before calling new frames integrated, show the owner the montage, watch a consecutive live-loop filmstrip, and keep the visible-outline bbox plus real attack-cell probes in `tools/check_it_actually_plays.py` green on shared `:9100`; add a targeted route assertion when a new character-copy path bypasses `drawSprite()`.

## Pipeline cheat-sheet (hard-won, don't rediscover)

- ⛔ **NOTHING IN THIS SECTION IS TO BE RUN — NO PAID GENERATION, EVER** (owner, Aug 11
  2026). Cells come from an outside still-generator the owner drives himself. What follows
  is kept for the recipes and pitfalls it records, not as a live pipeline. Never invoke it,
  never price a batch, never offer paid generation as a fallback.
- fal downloads: use **curl**, not python (corporate proxy breaks urllib SSL). Print RESULT_URL before downloading. FAL_KEY is in WildComiks `.env.local`.
- **Seedance 2** (`bytedance/seedance-2.0/image-to-video` — NO `fal-ai/` prefix) is the i2v frame source for registered multi-frame cycles (~$0.15/5s at 1080p); **nano-banana-pro** (`fal-ai/nano-banana-pro/edit`) for single stills. Owner order, Jul 29 2026. Both ids live ONLY in `tools/sprites/fal_models.py` — import `still_edit()` / `i2v_clip()`, never hardcode a model. Stills are identity-strong but pose-conservative: they CANNOT invent a pose the reference doesn't already hold, so all locomotion goes i2v. Validate non-black; generators hallucinate weapons — name the weapon explicitly.
- ⛔ **Sprite QC gate:** load `ShadowClash-Second-Brain/17 - Sprite Animation Director Prompt.md` BEFORE any sprite generation, cell review, montage QC, or packing pass. Grade every cell on its 12 dimensions; the grade table goes to the owner WITH the contact sheet. No cell packs without a grade. >30% REDO/REJECT in a batch = do not ship, change method. Verify claims by MEASURING (club swell vs a new-lineage rest pose, height wobble <=0.5%, 48x64 silhouette read) — never report what the prompt asked for as if it were what the model returned.
- Keying: magick fuzz **42%** corner-floodfill; pack with MATCH_HEIGHT / per-cell height flattening (that IS the house look; engine bob supplies bounce). Target 0.0% wobble on cycles.
- Browser sheet cache is sticky even on localhost — `fetch(url,{cache:'reload'})` before re-verifying.

## Owner clarification — 2026-09-06: frame continuity

Read `docs/SHODO-FRAME-CONTINUITY.md` before generating character frames. Anthony requires permanent Shodo style and direct study of each fighter's CURRENT previous frames for coherent proportions, size and motion. “Chibi-like” means the established game construction, not a smaller/stubbier redesign. New jumps must flow from/to existing poses at one consistent body scale.

## Owner workflow — 2026-09-07: high-pace footsies and animation expansion

For new character moves or movement cycles, follow `docs/FOOTSIES-PIPELINE.md`.
Provide complete frame-by-frame JSON with timing, vectors, red hitboxes and green hurtboxes; distinguish held exposures from new drawings. Use an independent Agent 2 visual/runtime audit, reject scores below 7 with exact frame/physics/source corrections, and repeat until the scoped result passes. Preserve current Shodo references and the existing no-warp character renderer. Never inherit a quality score from a supplied prompt as if it were a performed audit.
