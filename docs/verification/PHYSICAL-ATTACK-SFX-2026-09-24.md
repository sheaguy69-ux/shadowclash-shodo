# Physical attack sound pass — 2026-09-24

ElevenLabs Sound Effects v2 flow: https://elevenlabs.io/app/flows/sTPVUmNRRl4C2eaS8NW1

Sixteen takes were generated (four per category). Reported total: 45.3288 credits / USD 0.0082416. Raw MP3s remain in `raw/`. `build.py` trims silence, adds a short fade, and levels chosen takes to 0.8 peak as 44.1 kHz mono WAV in `web/assets/sfx/`.

| Category | Game event | Installed takes | Remaining raw take |
| --- | --- | --- | --- |
| Light body hit | `hit_light` | `light-body-01/02/03` | `light-body-04` (very quiet) |
| Heavy body hit | `hit_heavy` | `heavy-body-01/02/03/04` | — |
| Attack swing / miss | `whoosh` | `missed-swing-01/02/03` | `missed-swing-04` (quiet) |
| Blade-on-blade clash | `clash` | `blade-clash-01/02/03/04` | — |

The game starts loading the small WAVs at the first audio unlock. It plays a random variation for each event; the original synthesis is the fallback until loading finishes or if an asset cannot be fetched. The sampled swing has a quieter synthetic air layer for continuity. The wood and dull clash, block, and parry categories retain their separate sounds.

Browser verification: fourteen WAVs loaded into the live WebAudio context (3 light, 4 heavy, 3 swing, 4 clash); actual sample playback peaks were 0.189, 0.262, 0.168, and 0.237 at the game master bus for light, heavy, swing, and clash respectively. Delayed swing ended at 331 ms. Existing SFX self-check passed; the game remained live at 57–61 rAF/sec. Review player: `web/_review/physical-attack-sfx-20260924/index.html`.
