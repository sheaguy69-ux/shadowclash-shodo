# Owner-corrected SHODO trio review — provenance

Status: **visual review only; no live integration**.

Built with the built-in image generator after Anthony marked exact defects on the three
review images. His direct correction request controls over the earlier handoff's statement
that no redraw was requested.

## Mizu — first-form full-staff poke

Final board was generated fresh from one approved identity/style/weapon reference only:

- `art/shodo-source/mizu/mizu-shodo-exact-style-idle-8f-v1-codex-review/frame-01.png`
  — SHA-256 `8104f872058e6252983d855571df91e767add608a6915556a57aa60a2cdbee6a`

Prompt: replace the mistaken twin-hanbo concept with six new first-form full-bo beats:
READY, COIL, DRIVE, CONTACT, RETRACT, GUARD. Exactly one continuous full-length staff in
both hands; two flat inset eyes; new written choreography; one scale. An earlier correction
attempt that also used a staff-move frame was discarded after the newer handoff prohibited
move-frame references.

Final SHA-256: `0b44ea4150e43bedb1216dd902f2207606283196891e7f25e3d24ebd7a76d870`.

## Shin — eye plus frame-1 shuriken/hand correction

Anthony explicitly requested correction of the supplied board and consistency with the
approved art, so the edit used:

- edit target: `exec-5fce57c1-c19b-4498-b58b-a3e597dbb808.png`
- identity/style: `art/shodo-source/shin/shin-shodo-exact-style-idle-8f-v1-codex-review/frame-01.png`
  — SHA-256 `73000d8d7c7c65a0ca323630a6ee75951d432e59aefb4333b4b23d6f87544f2c`
- hand/shuriken construction: `art/shodo-source/shin/shin-shodo-single-shuriken-fingertip-taunt-8f-v1-review/frame-01.png`
  — SHA-256 `07f3a1d05625d4ba130fa5009264ceee29645f1e41a5046539b70cbb157c882a`

Prompt: make the eye one flat narrow ice-cyan shape fully inside the mask in all six beats;
redraw frame 1's front hand with coherent fingers holding a clean four-point shuriken; keep
the other five poses; match the approved SHODO rendering; add captions.

The first corrected candidate, SHA-256
`b8a68d9a80dab59c9d2dac458d4c4c243307025e202e7526552a12b7703a7f5e`, was superseded
after Anthony marked deformed arms in DRAW and READY. A targeted anatomy pass rebuilt those
two shoulder-to-hand chains; a final pass restored READY's two held weapons after the
anatomy edit dropped them.

Current final: `candidates/shin-flat-eye-arms-corrected-6f-v3-RGB-REVIEW.png`

Final SHA-256: `4a7285154b109143aaf9db323a1c12d67aec76a625770b3347499e2abf550a6b`.

## Tsubasa — approved knife and rendering consistency

Anthony explicitly requested use of previously approved frames to keep her features and
art style consistent, so the edit used:

- edit target: `exec-3c27c338-1524-40ff-9944-133f79084328.png`
- identity/style: `art/shodo-source/tsubasa/tsubasa-shodo-exact-style-idle-8f-v1-codex-review/frame-01.png`
  — SHA-256 `6b8619f58f73392c34e1247bd124412cca0a8d1a053f73226b26ee681e0d7ad5`
- knife/rendering construction: `art/shodo-source/tsubasa/tsubasa-shodo-light-combo1-8f-v2/frame-01.png`
  — SHA-256 `1e95540da99cf488bedbbde89d904a06fee5b50229350a3910b28871e3945151`

Prompt: redraw the complete row in the approved SHODO art family; lock the same hair, mask,
flat eye, scarf, proportions, texture, and broad curved black-and-silver tanto in every beat;
keep both knives reverse-gripped; preserve motion and add captions.

Final SHA-256: `c35cd68356739ac66b571c3d4760fd860f03ba71cae4fd371456bb5d93ce60d6`.

All three final boards are RGB with baked checkerboards and remain review-only. Alpha/frame
preparation waits for Anthony's visual approval.
