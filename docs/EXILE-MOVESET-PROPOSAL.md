# Exile — the rest of the moveset

**STATUS: all seven BUILT and verified in-engine at SHEET_V 222 (2026-07-26).**
Owner approved 1-5, then "I still wanna fill up the empty slots" — so 6 and 7 were
built too. This file is kept as the design record; see the SHEET_V 222 changelog in
`web/index.html` for what shipped and the three bugs found by playing it.

Design brief for the owner. Not lore, not UI text — mechanics only.

## The frame: her stats already say what she should be

| stat | Exile | roster context |
|---|---|---|
| speed | **10** | highest (Shin 9, Ember 8, Executioner 3.5) |
| reach | **9** | joint-longest with Mizu's 10 |
| power | 5 | below average — Executioner 9, Oni heavy |
| defense | **3** | lowest, and she also takes a flat **1.25x** damage |
| jumpScale | **1.12** | the only fighter with one — highest jumper |

Read together: she is the fastest body with the longest reach, the lowest per-hit
damage, and the thinnest health in the game. Speed 10 divides every recovery by
1.67, so she acts ~40% faster than baseline. That is a **space-controller who
converts on volume**, not a bruiser — she should win by owning ranges nobody
else can touch and by being somewhere else before the answer arrives.

**The headline gap: her best stat is attached to her worst moveset.** She is the
highest jumper in the roster and her entire air kit is generic fallbacks — her
air heavy literally plays her *grounded* heavy while she floats, and all three
air-light beats are one picture. Fixing the air is worth more than adding any
new ground button.

**The thing NOT to give her:** a strong close-range reversal. Defense 3 plus
1.25x damage means losing the up-close guessing game is supposed to be her
weakness. Every proposal below either extends her reach, moves her, or converts
— none of it is a panic button.

## Source art already on disk (so these are $0)

`WILDCOMIKS.2.0/media/shadow-clash/exile_frames/`

| file | what it draws | proposed use |
|---|---|---|
| `atk_aerial.png` | airborne kama slash | AIR neutral+Heavy |
| `lr_skydown.png` / `atk_down_air.png` | ball driven straight down | AIR down+Heavy — SKY DOWN-SMASH |
| `lr_side.png` | fundo hurled horizontally, chain fully out, counter-weight lean-back | GND fwd+Heavy — SIDE REACH |
| `grapple_wide/w1..w6` | throw → anchor → reel → swing, drawn at true long reach | fwd+Special — CHAIN-GRAPPLE SWING |
| `cartwheel/` (5) | sideways aerial rotation | air evasion / the swing's exit |

⚠️ Every one of these sources runs off its own 816px canvas, same as the 24
cells already softened at SHEET_V 220. Anything packed from them inherits a cut
edge and needs the same taper. The only clean fix is regenerating with padding.

## The seven, as built

### 1. SKY DOWN-SMASH — AIR down+Heavy `$0` ✅ BUILT
Today: the generic meteor slam every fighter has.
Proposed: her spec's named move. Ball driven straight down, **spikes** airborne
victims into a ground bounce (`spike: true` already exists in spawnHitbox),
landing shockwave both sides, heavier hitstop. Cell 22 (`kstomp`) is already
this exact pose.
*Why first:* she jumps highest, so she reaches the air-to-ground angle better
than anyone, and it converts her air game into damage. Biggest play-feel change
per line of code.

### 2. CHAIN-GRAPPLE SWING — fwd+Special `$0` ✅ BUILT
Her spec calls this her "signature mobility + fastest-mover identity" and flags
it PENDING. Never built.
Throw the kama at a wall → it bites → she is **reeled** along the chain at high
speed → swing-around at the end carries a hitbox.
The engine already has every piece: the rope sim, the anchor pin, `anchorTimer`,
and the ghost trail.
**Kept distinct from the iaijutsu cross** — that one is an *attack* that cuts the
whole path, ends far side, and pays a long recovery. The grapple is *mobility*:
hits nothing on the way, low recovery, works **in the air**, and can go
up-diagonal for vertical traversal the iaijutsu can't do.

### 3. Unify Up+Special as "chain to the wall" `$0` ✅ BUILT
Airborne Up+Special already anchors her to a wall. Grounded Up+Special is
currently a duplicate of the heli spin — make it **launch** her to the wall
instead (throw the chain up-diagonal, yank herself up). One input, one meaning,
grounded or airborne, and it feeds the star-throwing position she already has.

### 4. SIDE REACH — GND fwd+Heavy `$0` ✅ BUILT
Today: identical to her neutral heavy.
Her neutral heavy is a 90px mid swing. This is the **full extension** — a ~200px
horizontal fundo hurl with the lean-back, her long poke. Fills a real hole: she
currently has no way to threaten 150–200px without spending chakra on the
special.

### 5. Real air-light beats — AIR Light `needs art or a harvest` ✅ BUILT (xair2, cell 30)
Today: `air1/air2/air3` all cell 10, one picture, and identical whether you hold
forward, back or nothing.
Proposed: three beats, plus directional variants — fwd = a diving kama slash
(approach), back = a retreating cut that covers her as she leaves.

### 6. COUNTER-WEIGHT SNAP — GND back+Heavy `no art needed` ✅ BUILT
Today: identical to her neutral heavy.
Proposed: a **gap hitbox** — she leans back and snaps the chain so it hits only
between ~120–180px and nothing closer. Punishes someone walking into her range
and rewards her for holding space rather than retreating blindly. Uses the rope
sim; no new cell.

### 7. Quick up-flick — GND up+Light `no art needed` ✅ BUILT
Today: identical to her neutral light.
Her UP REACH anti-air is a committal 420ms move. She needs a ~140ms short
upward kama poke for a jump-in that is already on top of her. Small box, fast,
no launch.

## Build order I'd recommend

1. **Sky down-smash** — biggest feel change, art ready, one branch.
2. **Grapple swing** — her identity, art ready, engine pieces all exist.
3. **Up+Special unification** + **side reach** — cheap, remove duplicate inputs.
4. The rest as polish.

## Bloat warning (kept — it still applies)

Seven additions on top of a kit that already had eighteen distinct inputs. I
flagged 6 and 7 as the most droppable because they fill *input* gaps rather than
*gameplay* gaps; the owner chose to build them anyway. If the kit ever starts
feeling wide rather than deep, those two are still where to cut first.

## What is still recycled on her (not a slot, a gap)

- **hurt / thrown** — cell 2, which is a confident fighting stance that also
  serves run_clean2/6. She does not recoil when hit. No source art exists.
- **block** — cell 12, shared with `block2`.
- **throwing** — cell 7, shared with three heavy names.
- Her old air light cell 10 measures an 87x65 body against her idle's 138x107.
  Some of that is a legitimate tuck, but it is worth an eye on.
