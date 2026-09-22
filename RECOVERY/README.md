# SHADOWCLASH-RECOVERED — salvage after repo loss (Jul 28 2026)

`/Users/anthonyguy/SHADOWCLASH-1.0` and `/Users/anthonyguy/shadowclash-preview`
vanished from disk Jul 28. Internal Apple SSD + TRIM + FileVault + no Time
Machine + no APFS snapshots = the deleted blocks are unrecoverable. This folder
is everything that survived, from the second brain + GitHub + session scratchpad.

## What this is
- **Game code**: second-brain snapshot at **SHEET_V 228** (Jul 26, HEAD was
  `748bfed` on `main`) — the newest surviving copy. All 10 sprite sheets included.
- **web/assets/stages/**: the original 6 backdrops PLUS the 6 new story boards
  generated Jul 28 (drowned/village/warrant/tollgate/lantern/abyss) — rescued
  from the session scratchpad before /tmp cleanup.
- **RECOVERY/brain-assets/**: identity true-reference art, approved gates,
  generated archive — the sprite pipeline's source-of-truth images.
- **RECOVERY/ledgers/**: complete pass-by-pass history including everything
  AFTER 228 (229–253: blade family, Kunoichi→Exile fold, transparency purge)
  and the full stage/hazard/CPU design from Jul 28 (SHEET_V 254 work).

## What is LOST
- Git history 217→253 as commits (GitHub main stops at 216; local was 253).
- The packed sheet deltas 229→253 (blade-family weapon cells etc.) — the
  ledger describes them; the pixels must be regenerated.
- Jul 28 stage/hazard/CPU-brain CODE (commits b710312, 22dd78b) — fully
  described in RECOVERY/ledgers/shadow-clash-sync.md; rebuild onto this base.

## Next steps
1. `git init` here or clone sheaguy69-ux/SHADOWCLASH-1.0 and overlay this.
2. Re-apply the Jul 28 stage system from the sync ledger entry.
3. Regenerate 229–253 sprite passes from brain-assets references.
4. CONFIGURE TIME MACHINE.
