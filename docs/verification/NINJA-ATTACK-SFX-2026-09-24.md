# Ninja attack sound review — 2026-09-24

Anthony requested attack sounds with a more suitable shinobi character after reviewing the installed physical attack set. Sixteen new candidates were generated with ElevenLabs Sound Effects v2 in flow `sTPVUmNRRl4C2eaS8NW1`, four each for a cloth-wrapped light strike, heavy kick, short-blade/sleeve swing, and quick steel parry. The reported generation total is 37.3296 credits / USD 0.0067872.

The original MP3s and processing script are in ignored local `media/ninja-attack-sfx-20260924/`. The A/B listening page is `web/_review/ninja-attack-sfx-20260924/index.html`, with sixteen level-controlled 44.1 kHz mono WAV previews. All sixteen previews decode and are served successfully by the Shodō :9101 review server.

Anthony selected these exact takes for the game:

| Game event | Installed WAVs | Selection |
| --- | --- | --- |
| `hit_light` | `ninja-light-04.wav` | Light body hit 4 |
| `hit_heavy` | `ninja-heavy-03.wav` | Heavy hit 3 |
| `whoosh` | `ninja-swing-02.wav`, `ninja-swing-04.wav` | Blade swing miss 2 and 4 |
| `clash` | `ninja-clash-03.wav`, `ninja-clash-04.wav` | Blade clash 3 and 4 |

The six reviewed WAVs were copied byte for byte into `web/assets/sfx/`. Other ninja candidates remain on the review page and are not used by the game. Earlier physical-attack samples are preserved in `web/_review/physical-attack-sfx-20260924/audio/` and are no longer active runtime assets.

`web/index.html` loads one light and one heavy sound, then chooses randomly between the two selected swing and clash variations. Synthesis remains the load-failure fallback. The sampled swing plays alone, without an extra synthetic air layer, so it matches the selected preview.

Live browser check: all six selected assets loaded (`1/1/2/2`), the manifest matched the selection, actual sample playback was recorded for each event, and the delayed swing ended at 374 ms. The game ran at 58 rAF/sec during this check.
