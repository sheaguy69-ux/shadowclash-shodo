---
type: agent-handoff
for: Kimi K3
from: Fabel (Claude, merge lead)
status: active
created: 2026-07-28
priority: CRITICAL — repo loss recovery
---

# K3 REBUILD HANDOFF — piece the game back together

## What happened (do not re-investigate, it is settled)
`/Users/anthonyguy/SHADOWCLASH-1.0` and `/Users/anthonyguy/shadowclash-preview`
were deleted from disk Jul 28. Internal Apple SSD + TRIM + FileVault + no Time
Machine + no APFS snapshots = the blocks are gone. Forensics done; recovery via
software is impossible. Do not waste cycles on undelete tools.

## YOUR WORKING BASE (already assembled + verified)
`/Users/anthonyguy/SHADOWCLASH-RECOVERED` — git initialized, commit b3ce328.
- Game code at **SHEET_V 228** (newest surviving copy; Jul 26 snapshot of main @ 748bfed)
- All 10 sprite sheets + JSON maps (oni 129 cells, buddha 93, exile 69 — all parse)
- **12 stage backdrops** in `web/assets/stages/` (6 wired + 6 NEW awaiting code)
- `RECOVERY/brain-assets/` — identity true-refs, approved gates, generated archive
- `RECOVERY/ledgers/` — full pass history including everything lost
- VERIFIED RUNNING: `python3 -m http.server` in web/, all 9 rigs load, CPU match runs.

GitHub `sheaguy69-ux/SHADOWCLASH-1.0` main stops at SHEET_V **216** — the
recovered folder is NEWER. Use the folder, not a fresh clone. NEVER push to the
public demo (shadowclash-peach.vercel.app) — standing owner order.

## WHAT WAS LOST (your rebuild queue, in priority order)

### 1. Jul 28 STAGE SYSTEM (SHEET_V 254 work) — full spec in ledger, rebuild first
Read `RECOVERY/ledgers/shadow-clash-sync.md`, entry "2026-07-28 — STAGES".
Owner APPROVED this; it shipped and was verified before the loss. Rebuild onto 228:
- STAGES[] goes 6 → 12, ordered as the story climb (grudge boards → three doors
  → Lantern → Breaking Stair). The 6 new PNGs are ALREADY in web/assets/stages/:
  drowned-far, village-far, warrant-far, tollgate-far, lantern-far, abyss-far.
- `hasFloorAt(cx)` = ONE floor rule read by physics AND renderer.
  `ledge:N` (rooftops 74, keep 62, drowned 66, lantern 80) carves the ground
  line N px short of each wall; `abyss:true` = no floor at all.
- TRAP 1: the pit gap must be actively DARKENED in the renderer — the floor
  band is translucent, so a hole drawn as "nothing" reads as floor.
- Breaking Stair: rising debris slabs (ABYSS_RISE 34, seedAbyss/updateAbyss,
  slabs recycle at top→bottom), slabs CARRY riders (`this.x += plat.vx*dt` on
  land). `roll:false` — F7/explicit pick only, never the random roll.
- TRAP 2: abyss TOP kill line = feet < ~4px above screen (NOT 70) — must fire
  before a slab recycles at -46 or a camper gets dropped back in alive.
- `plunge(p)` = the one leave-the-world KO (hp=0, koTimer 0.95, routes into
  normal endRound). Bottom kill: y > canvas.height + 60.
- Spawn fix: fighters spawn at GROUND_Y - height (was fixed 48 — the abyss has
  no ground snap to correct it).
- HAZARDS: `wind:{peak,period}` sine gust — POSITIONAL drag (this.x += wind*dt,
  ×0.35 grounded, ×0.5 projectiles), NEVER vx (movement is a zero-friction vx
  override that wipes vx every frame). bamboo 30/7.5, rooftops 78/6, snow 52/5,
  lantern 58/8, abyss 92/5. `debris:{every,dmg}` falling rocks (keep 3.2/6,
  volcano 4.2/7) — apply damage DIRECTLY (takeDamage's parry/counter paths
  dereference an attacker that doesn't exist), 0.25s stagger, dodgeable.
- CPU: survival-first block at top of cpuThink (EVERY frame, not reaction-timer
  — a fall is decided in frames), gated on `currentStage.abyss||ledge`: find
  nearest slab preferring BELOW (climb cap 150px), feet<120 counts current slab
  UNSAFE (or the brain rides a rock off the top), held Down to drop through,
  EDGE BRAKE cancels any movement key stepping into a hole (probe ±30px).
  Verified numbers to beat: abyss CPU-vs-CPU rounds 12-55s, no self-falls on
  ledge boards (rooftops x-range 122-562 at ledge 74).

### 2. Post-228 sprite passes (229→253) — regenerate, ledger describes each
Biggest items from the sync ledger:
- **251-253 BLADE FAMILY**: ~130 weapon cells — Executioner/Kael/Tsubasa/Shin
  traditional blade anatomy (sori, kissaki, hamon, tsuba, tsuka-ito) across
  attacks, runs, wallslide, roll, hurt cells; Shin's kunai cells 50/51.
  Owner directive doc: docs/BLADE-SPEC-2026-07-28.md (LOST — the ledger entry
  is the surviving spec).
- **252 KUNOICHI==EXILE fold**: owner ruling — same character. Fix her arcade
  win quote (quotes map had Kunoichi key, no Exile key → her wins show
  NOTHING at 228), credit Down+S floor chain (SERPENT'S TONGUE) to Exile in
  the 2P help line, rename stale comments.
- **253 transparency purge**: 41,976px off oni.png, 17,859 off exile.png
  (sub-visible alpha, halo fog, white specks); Exile idle hole-fill fix.
- Work through 229-250 ledger entries in order; anything ambiguous → flag me
  in the channel, do NOT guess at art.

### 3. Verification gates (unchanged laws)
- kinetics_check.mjs + node --check after every code pass (tools/ has them).
- Canvas-pixel or live-render confirmation before ANY slab/artifact claim
  (K3 gate rule from the false-slab postmortem).
- Owner SEES animation/frame changes in motion BEFORE commit.
- No neon ever. No engine-credit taglines in shipped UI.
- Small commits in the RECOVERED repo, one lane at a time.

## SPEND
Stage art already paid ($0.30, session ~$13.70 vs $15 standing cap). Sprite
regen for the blade family will need fresh budget — get owner sign-off on the
estimate BEFORE generating, report running total as you go.

— Fabel
