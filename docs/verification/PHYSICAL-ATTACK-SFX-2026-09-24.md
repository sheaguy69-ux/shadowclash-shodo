# Earlier physical attack sound pass — 2026-09-24

ElevenLabs Sound Effects v2 flow: https://elevenlabs.io/app/flows/sTPVUmNRRl4C2eaS8NW1

This was the first physical-attack pass. Anthony later selected the ninja sounds documented in `docs/verification/NINJA-ATTACK-SFX-2026-09-24.md`; those are now active in `web/assets/sfx/`. The earlier fourteen WAVs remain in `web/_review/physical-attack-sfx-20260924/audio/` for comparison.

Sixteen takes were generated (four per category). Reported total: 45.3288 credits / USD 0.0082416. Raw MP3s remain in the original local `raw/` directory. `build.py` trimmed silence, added fades, and leveled the fourteen earlier takes to 0.8 peak as 44.1 kHz mono WAVs.

| Category | Game event | Earlier takes | Remaining raw take |
| --- | --- | --- | --- |
| Light body hit | `hit_light` | `body-light-1/2/3` | Fourth take (very quiet) |
| Heavy body hit | `hit_heavy` | `body-heavy-1/2/3/4` | — |
| Attack swing / miss | `whoosh` | `attack-air-1/2/3` | Fourth take (quiet) |
| Blade-on-blade clash | `clash` | `blade-clash-1/2/3/4` | — |

At the time of this pass, fourteen WAVs loaded into the live WebAudio context; the game remained live at 57–61 rAF/sec. Review player: `web/_review/physical-attack-sfx-20260924/index.html`.
