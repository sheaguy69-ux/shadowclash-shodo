# EVENING BATCH — Aug 20 2026

Archived, not packed. SHEET_V stays 575.

| file | frames | body px | vs target | what it is |
|---|---:|---:|---|---|
| `executioner-gedan-counter-8f.png` | 8 | 272 | **1.01× ✅** | duck under an overhead → rising counter-slash. This is **Gedan-no-Kamae** from the katana board, realised: *"sword low, invites an attack from above, which the ninja counters with an upward slash."* Beat 3 carries a **black arrow annotation** marking the incoming attack — not his art. |
| `horned-gold-KNOCKDOWN-GETUP-8f.png` | 8 | 252 | 0.93× ❌ | **beat 4 is a body lying flat on the ground.** Knockdown → getup → counter. |
| `hooded-gold-DISARM-staff-8f.png` | 8 | 172 | 0.64× ❌ | a parry that **knocks a weapon away** — sparks on beat 3, the staff tumbling off on beat 6. No horns; may be Kael. |
| `horned-gold-dualsword-8f.png` | 8 | 214 | 0.79× ❌ | twin-blade X-slash string |
| `horned-gold-dualsword-alt-8f.png` | 7 | 204 | 0.76× ❌ | twin-blade string, alt take |
| `horned-gold-technique-board.png` | 28 | 111 | **0.41× ❌** | technique board — same layout failure as the katana board |

All six: background corner 252–253 (fuzz-42 lifts them), **zero edge contact**.

## Two of these are content the game actively needs

**Knockdown/getup is the single highest-visibility gap in the game.** Today the loser stands
straight back up into idle under the KO banner — `getup`/`getup2` keys exist and the picker
branch is already live on `flooredT`. `horned-gold-KNOCKDOWN-GETUP-8f` is the first drawn
downed pose delivered for the new style.

**The disarm strip lands the same week Ember's Ghost Killer disarm shipped** (commit
`89d2bca`) — same idea drawn for a blade fighter rather than the claws.

## ⛔ Still undersized, and the layout lesson repeated

Five of six are under target; only the Gedan counter passes. The board is 0.41× — the
identical failure as `executioner-long-katana-8rows.png`, from the same cause: many frames
in one 1536×1024 image. Full-width strips at 2172×724 pass; boards do not. All five are in
`SHADOWCLASH-RESIZE-PACKAGE.zip` with per-file multipliers.

## ⛔ The horned fighter's palette has moved three times in one day

Ships **purple + orange, yellow eye** → new-look idle came back **yellow-eyed** → katana
board **purple/black, RED eyes** → this batch **black + GOLD**. Red eyes are Oni's tell and
gold is Kael's. Owner ruling needed before more frames are generated against any of them.
