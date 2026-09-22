# Shadow Clash — Ninja Art Handoff

**Purpose:** hand this to the Hermes MOA system to correct and improve the
generated ninja art. It is self-contained: current state, exact file map, the
reproducible generation pipeline (model + prompts + scripts), the engine
integration, the known-issue list from an adversarial QA pass, and a
prioritized improvement backlog.

Author: Claude Code · Date: 2026-07-03 · Repo: `sheaguy69-ux/SHADOWCLASH-1.0`

---

## 1. Status & links

| | |
|---|---|
| **Live game** | https://sheaguy69-ux.github.io/SHADOWCLASH-1.0/web/ |
| Repo | https://github.com/sheaguy69-ux/SHADOWCLASH-1.0 |
| Landed via | PR #2 (squash-merged to `main`), commit `72e989e` |
| Deploy | GitHub Pages (Jekyll, served from repo root); the game is under `/web/` |
| Playable build | `web/index.html` — self-contained HTML5 canvas (Tailwind CDN) |
| Godot port | `godot/` — **does NOT yet consume these sprites** (see backlog #9) |

Controls: **P1** WASD move/jump, `F`/`G`/`H` light/heavy/special, `C` kawarimi.
**P2** arrows, `I`/`O`/`P`/`M`. Local 2-player.

---

## 2. What exists

Two layers of Fal-generated art, both with a procedural fallback (nothing hard-depends on the assets):

1. **Character-select portraits** — `web/assets/ninjas/<name>.png` (6 transparent full-body illustrations). Wired into the roster cards + P1/P2 badges via `portraitSrc()`; falls back to a procedurally-drawn head (`makePortrait`) if missing.
2. **In-fight animation sprite sheets** — `web/assets/sprites/<name>.{png,json}` (6 sheets, 13 poses each). Rendered by `drawSprite()` in place of the old procedural "doll"; the doll (`drawChibiNinja`) remains the fallback.

`<name>` ∈ `executioner, mizu, shin, tsubasa, ember, kael` (roster order 0–5).

### File map
```
web/index.html                       # game + sprite loader + drawSprite (see §4)
web/assets/ninjas/<name>.png         # select-screen portraits (transparent)
web/assets/sprites/<name>.png        # 12-cell sprite sheet (single row, transparent)
web/assets/sprites/<name>.json       # manifest: geometry + feet line + scale + frame index map
tools/sprites/base/<name>.png        # IDENTITY ANCHOR: clean full-body illustration on white
tools/sprites/gen_frames.py          # generate 12 poses for one ninja (validated/retried)
tools/sprites/pack_sheet.py          # key→trim→normalize→pack sheet + manifest
tools/sprites/gen_all.py             # regenerate + pack all six (or a subset)
tools/sprites/README.md              # pipeline quickstart
docs/ninja-brawler-gdd.md            # game design document (roster + mechanics)
```

---

## 3. The 12 poses & sheet format

Poses (cell order): `idle, idle2, run1, run2, jump, fall, light1, light2, heavy1, heavy2, block, hurt, wallslide`.

Manifest (`web/assets/sprites/<name>.json`):
```json
{ "name":"executioner", "frameW":186, "frameH":226, "cols":12,
  "footY":218, "scale":0.3804,
  "frames":{"idle":0,"idle2":1,"run1":2,"run2":3,"jump":4,"fall":5,
            "light1":6,"light2":7,"heavy1":8,"heavy2":9,"block":10,"hurt":11} }
```
* Single-row sheet; cell `i` occupies `[i*frameW, 0, frameW, frameH]`.
* Frames are **bottom-aligned** (feet at `footY`) and **horizontally centered on content**.
* `scale` maps sheet px → canvas px so the idle stands ≈70px tall in the 800×500 arena. `frameW/frameH/footY/scale` differ per character (poses have different extents).

---

## 4. Engine integration (`web/index.html`)

* **Loader** — on startup a `SPRITES` registry `fetch()`es each `assets/sprites/<name>.json` + `.png`; a missing sheet is silently skipped → the procedural doll is used.
* **Hook** — inside `Player.draw(ctx)`: `if (!drawSprite(ctx, this)) drawChibiNinja(ctx, this);`
* **State → frame** — `spriteFrameIndex(p, frames)` maps the FSM `STATE`:
  | STATE | frames used |
  |---|---|
  | `IDLE` (+`SUBSTITUTION`) | `idle`,`idle2` (2-cycle) |
  | `RUN` | `run1`,`run2` (cycle, speed ∝ `|vx|`) |
  | `JUMP` | `jump` if `vy<0` else `fall` |
  | `ATTACK_LIGHT` | `light1`→`light2` across `attackAnim` (140ms) |
  | `ATTACK_HEAVY` | `heavy1`→`heavy2` across `attackAnim` (220ms) |
  | `ATTACK_SPECIAL` | **reuses** `heavy1`/`heavy2` |
  | `PARRY_STANCE` | `block` |
  | `STUNNED` | `hurt` |
  | `WALL_CLING` | `wallslide` (falls back to `fall`) |
* **Draw math** — anchor at the player's feet `(x+width/2, y+height)`, mirror by `scale(facing,1)`, then `drawImage(cell)` offset by `-footY*scale`. Adds light *juice* the static frames lack: idle/run bob, run lean, and a forward **lunge** during attacks.
* **Untouched:** hitboxes, hurtboxes, frame data, physics — sprites are purely visual. Changing art will not change balance.

---

## 5. Generation pipeline (reproducible)

Model: **`fal-ai/flux-pro/kontext`** — image-edit *repose* of the base illustration (`image_url`) with a pose prompt, so the character's identity is preserved and only the pose changes. `guidance_scale: 4.0`, `output_format: png`, `safety_tolerance: "6"`.

Run (see `tools/sprites/README.md`):
```bash
export FAL_KEY=...
python3 tools/sprites/gen_all.py                # all six  →  web/assets/sprites/*
python3 tools/sprites/gen_all.py ember kael     # subset
```
Per-character **identity phrases** live in `tools/sprites/gen_all.py`. The 12 **pose prompts** live in `tools/sprites/gen_frames.py` (`POSES`), each suffixed with the identity phrase + "bold black outlines, flat cel shading, full body, single character, centered, plain white background".

Packing (`pack_sheet.py`): key white→transparent (ImageMagick border-floodfill, fuzz 25% — survives interior white like Mizu's eyes), trim, uniform-downscale (tallest frame → 210px), bottom-center normalize into cells, pack single-row sheet, emit manifest, recompress.

**Validation:** every generated frame's mean luminance must be `0.2..0.97`; solid-black fal failures and blank frames are rejected and retried (≤4×).

---

## 6. Known issues / QA findings — the correction targets

An adversarial vision-QA pass (6 agents, one per character, comparing every frame to its base) was run. **5 identity-drift frames were found and already fixed** (Ember's claws had become a sword/knife/shield in `light1/light2/heavy1/block`; Kael's `light2` had a forked blade). The remaining items are **pose-softness** — usable but weaker than intended, a consequence of Kontext's conservatism (it resists large limb/leg reposes). They were left as-is because in-engine juice (lunge/bob/lean) compensates, but they are the natural improvement list:

- **executioner:** run2 too upright; fall reads neutral (no descent); light2 no forward thrust; heavy2 downswing not completed; hurt reads neutral (no recoil).
- **mizu:** idle2 not a near-copy of idle; jump staff looks doubled/broken; fall reads as a floating leap; light2 staff not thrusting; heavy2 no downswing; block not crouched; hurt reads as idle.
- **shin:** run2 weak lean; light1 not clearly drawn-back; light2 no forward lunge; heavy2 neutral.
- **tsubasa:** idle2 reads like an attack, not an idle variant; light1 blade already extended (not wound back); light2 no thrust.
- **ember:** jump weak rising thrust; heavy2 one fist missing claws + weak downswing; hurt no recoil.
- **kael:** fall reads like jump; heavy2 no downswing; block upright (not a crouched guard).

Other notes:
- **Only 2 frames per animation** → motion reads but isn't buttery. More frames = smoother.
- **Special move reuses the heavy frames** — no per-character special sprite (Shin teleport, Mizu smoke, Tsubasa parry-counter, Ember lunge, etc.).
- **No dedicated kawarimi/substitution frames** (engine just fades alpha over idle).
- **Sheet sizes ~0.3–0.5 MB each** (PNG). `pngquant`/WebP would cut this materially.
- Front-3/4 orientation is kept (not true side-view); facing is handled by horizontal mirror.

---

## 7. Prioritized improvement backlog (for Hermes)

1. **Pose fidelity** (biggest visual win). Kontext under-reposes legs/thrusts. Options, best-first:
   a. Add a pose-conditioning step (ControlNet/OpenPose or a pose-transfer model) so the target stance is enforced, then Kontext/img2img for identity+style.
   b. Curate: generate N candidates per weak pose and keep the best (add a candidate loop + the existing vision-QA verdict as the selector).
   c. Prompt tuning only: even more explicit limb language + `guidance_scale` 4.5–5 (diminishing returns; watch for identity drift/black frames).
2. **More frames per anim** (2 → 3–4 for run/attacks) for smoother cycles; extend `POSES`, the manifest, and the `spriteFrameIndex` cycles.
3. **Per-character special-move sprites** (currently `ATTACK_SPECIAL` reuses heavy). One or two poses each, mapped in `spriteFrameIndex`.
4. **Dedicated kawarimi / hurt / KO frames** and a death/again pose for the game-over screen.
5. **Asset weight:** run `pngquant` (or export WebP) on `web/assets/sprites/*.png`; consider a 2×N grid instead of 1×12 to cap texture width.
6. **Weapon/VFX alignment:** hit-sparks and slash trails are emitted at generic offsets — align them to each frame's actual weapon tip.
7. **Per-character scale/anchor tuning:** `scale`/`footY` are auto-derived; a couple may want hand-tuning so all six read at a consistent fighting height.
8. **Godot port (`godot/`)** does not yet load these sheets — wire an `AnimatedSprite2D`/`SpriteFrames` from the same manifests so the "real" engine matches the web prototype.
9. **Consistency polish:** enforce exact weapon counts (Tsubasa = 2 katanas everywhere, Ember = claws only) and a single light source; re-run the QA pass after any regen.

---

## 8. Gotchas (environment)

- **Kontext holds identity strongly but reposes conservatively** — force poses with imperative "Repose into …" wording + `guidance_scale` 4.0.
- **fal sometimes returns a solid-black frame** — always validate (done in `gen_frames.py`) and retry.
- **Downloads:** on a proxied machine Python's `urllib` may fail TLS on `fal.media`; the scripts download result URLs with **curl** (trusts the system root). Always capture the result URL before downloading so a hiccup doesn't waste a paid generation.
- **`FAL_KEY`** must be in the environment (or a local `.env.local`).
- **Verifying real-time play in a headless browser:** `requestAnimationFrame` is throttled when the tab isn't focused; step frames manually (`updateGame(dt)` in a loop, then `drawScene()`) to observe logic, or just open the page in a real tab (runs at 60fps).

---

## 9. How to verify after changes

```bash
# regenerate a character, then serve the game and check assets return 200
python3 tools/sprites/gen_all.py ember
cd web && python3 -m http.server 4599    # open http://localhost:4599/
```
Confirm: sheet `<name>.png`/`.json` load (network 200), the character renders at
the feet line at the right size across idle/run/jump/attack/block/hurt, facing
mirror is correct, and transparency is clean (no white box, eyes intact).
Re-run the adversarial frame QA (compare each new frame to `tools/sprites/base/<name>.png`).
