# SHADOW CLASH

**2D local 2-player competitive ninja brawler.**
Hollow Knight movement snap × simplified Skullgirls chain cancels, starring nine chibi ninjas.

## Play it now

Open [`web/index.html`](./web/index.html) in any browser — no build step, no install.
Character select for all nine fighters, then local versus on one keyboard, a controller, or touch.

| | P1 | P2 | Controller |
| --- | --- | --- | --- |
| Move / Jump | `W A S D` | Arrow keys | Left stick or D-pad |
| Light | `F` | `I` | **South** face button (A / ✕) |
| Medium | `J` | `U` | **West** face button (X / □) |
| Heavy | `G` | `O` | **North** face button (Y / △) |
| Special | `H` | `P` | **East** face button (B / ○) |
| Kawarimi (Poof) / Block | `C` | `M` | Either shoulder |
| Throw | Light + Heavy | Light + Heavy | Either trigger |
| Second Form / Stance | `V` | `K` | Back / Share |
| Pause | `Escape` | `Escape` | Start / Options |

Controller buttons are named by **physical position**, because Nintendo prints A/B and X/Y
mirrored against Xbox — the letters in brackets are the Xbox and PlayStation faces sitting in
that spot. Plug a pad in and the select screen tells you it was seen. Standard mapping only
(Xbox, DualSense, Switch Pro, 8BitDo all report it); a second pad drives P2 in 2 PLAYERS and
TRAINING and can never puppet a CPU opponent.

## The roster

| Ninja | Weapon | Archetype |
| --- | --- | --- |
| Executioner | Long sword | Heavy / Berserk — massive hitstop, slow recovery |
| Mizu | Bo staff | Zoning / Support — long pokes, smoke fields |
| Shin | Hand-to-hand / wire tool | Speed / Assassin — projectiles, shadow-step backstab |
| Tsubasa | Twin daggers (tantō) | Precision / Counter — 8-frame parry stance |
| Ember | Tekko-kagi claws | Brawler / Rushdown — multi-hit lunges |
| Kael | Short + long sword | Starter / All-rounder |
| Mokurai | Prayer beads / bare hands | Sage of Nothingness / Area — the monk, no staff |
| Exile | Kusarigama | Speed / Agility — chain to the wall, iaijutsu cross |
| Oni | Tekko-kagi claw | Acrobat / Rushdown — the founder behind the white mask |

## Core systems

- **Magic series chains** — Light → Medium → Heavy → Special cancels on hit or block, never on whiff
- **Kawarimi** — tap Poof at the frame of impact to negate the hit and teleport 80px behind the attacker (35% chakra)
- **Sword pogo** — down + attack in mid-air bounces off opponents and refreshes your jumps
- **Game juice** — hitstop, screenshake, sparks, smoke (see [docs/game-juice-freeze-frame.md](./docs/game-juice-freeze-frame.md))

## Repo layout

| Path | What |
| --- | --- |
| [`web/`](./web) | Playable canvas/JS prototype — the current reference implementation of every mechanic |
| [`godot/`](./godot) | Godot 4.4 project (early skeleton: input map, hitstop autoload, FSM base) — the production build target |
| [`docs/`](./docs) | Game design doc + technique deep-dives |

## Roadmap

See [docs/ninja-brawler-gdd.md](./docs/ninja-brawler-gdd.md). Near-term: frame-by-frame sprite sheets
(Wildcomiks art generator) to replace the procedural fighters, round system, audio pass, then the
full Godot port with proper frame data.
