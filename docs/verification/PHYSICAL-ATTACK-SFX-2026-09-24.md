# Physical attack sound pass — 2026-09-24

ElevenLabs Sound Effects v2 flow: https://elevenlabs.io/app/flows/sTPVUmNRRl4C2eaS8NW1

Twelve takes were generated (four per category). Reported total: 34.6632 credits / USD 0.0063024. Raw MP3s remain in `raw/`. `build.py` trims silence, adds a short fade, and levels chosen takes to 0.8 peak as 44.1 kHz mono WAV in `web/assets/sfx/`.

| Category | Game event | Installed takes | Remaining raw take |
| --- | --- | --- | --- |
| Light body hit | `hit_light` | `light-body-01/02/03` | `light-body-04` (very quiet) |
| Heavy body hit | `hit_heavy` | `heavy-body-01/02/03/04` | — |
| Attack swing / miss | `whoosh` | `missed-swing-01/02/03` | `missed-swing-04` (quiet) |

The game starts loading the small WAVs at the first audio unlock. It plays a random variation for each event; the original synthesis is the fallback until loading finishes or if an asset cannot be fetched. The sampled swing has a quieter synthetic air layer for continuity. The metal, wood, dull clash, block, and parry categories retain their separate sounds.

Browser verification: ten WAVs loaded into the live WebAudio context (3 light, 4 heavy, 3 swing); actual sample playback peaks were 0.191, 0.261, and 0.136 at the game master bus for light, heavy, and swing respectively. Existing SFX self-check passed; page remained at 59–60 rAF/sec. Review player: `web/_review/physical-attack-sfx-20260924/index.html`.
