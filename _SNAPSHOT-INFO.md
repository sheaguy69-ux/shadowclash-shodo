# GAME-CODE-PRIVATE-DEV — ShadowClash playable code snapshot

> # ⛔ HARD RULE — THE PUBLIC DEMO IS LIVE
> **`https://shadowclash-peach.vercel.app` is the PUBLIC build the public is playing right now.**
> It is the **demo** — it does **NOT** include the new characters.
> **NEVER push, deploy, promote, or publish anything to it.** Owner's standing order.
> Do not run `vercel`, `vercel --prod`, or any deploy command against it.
> This snapshot folder is the **private dev** code and must never reach that URL.



**This is a COPY, not the working repo.** Edit the repo, then run `./refresh.sh` to update this folder.

| | |
|---|---|
| **Snapshot taken** | 2026-07-26 |
| **SHEET_V at snapshot** | 228 |
| **HEAD commit** | `748bfed fix(exile): her crouch was a shrunken copy of her — never do that again (SHEET_V 228)` |
| **Snapshot branch** | `main` (this is what the dormant Pages workflow would publish) |
| **Source of truth** | `/Users/anthonyguy/shadowclash-preview` — repo is checked out on `main`; `preview/polished-art` is a separate line at `b57fcef` / SHEET_V 203 |
| **Second local copy** | `/Users/anthonyguy/SHADOWCLASH-1.0` (branch `main`) |
| **GitHub** | `https://github.com/sheaguy69-ux/SHADOWCLASH-1.0.git` — **PRIVATE** |
| **Publicly reachable?** | This snapshot: **No** (repo private, Pages off). But a SEPARATE public demo IS live at **https://shadowclash-peach.vercel.app** — never push to it. |

## What's in here

| Path | What |
|---|---|
| `web/index.html` | **The entire game.** Single-file canvas 2D fighter, ~5,400 lines — engine, state machine, physics, hitboxes, sprite router, UI, audio. |
| `web/assets/sprites/*.json` | Frame manifests per fighter (`frameW`, `frameH`, `footY`, `cols`, `frames{name→cell}`, `scale`). |
| `web/assets/sprites/*.png` | The packed sprite sheets. |
| `web/assets/ninjas/*.png` | Character-select portraits. |
| `web/assets/stages/*` | Stage backgrounds. |
| `tools/` | Art pipeline — sheet packers, i2v generators, extractors, `kinetics_check.mjs`. |
| `README.md`, `AGENTS.md`, `CLAUDE.md` | The repo's own docs (copied as-is). |

## Run it

```bash
cd /Users/anthonyguy/OB-LOCAL_BRAIN/ShadowClash-Second-Brain/GAME-CODE-PRIVATE-DEV/web && python3 -m http.server 8777
```
Then open `http://localhost:8777/index.html`.

## Refresh this snapshot

```bash
cd /Users/anthonyguy/OB-LOCAL_BRAIN/ShadowClash-Second-Brain/GAME-CODE-PRIVATE-DEV && ./refresh.sh
```

## Two laws that break the game if ignored

1. **Loader law** — `img.width === manifest.frameW * manifest.cols`, or the sheet is silently rejected and that fighter renders invisible.
2. **Bump `SHEET_V`** on every sheet/manifest change; it's the cache-buster.

## Note on `../runtime-reference/`

That older folder is a **Jul 16 / SHEET_V 6** snapshot — 208 sheet versions behind, predates Oni entirely. Kept for history. **This folder is the current one.**

## Public exposure — read before enabling anything

- The repo is **private** and **GitHub Pages is not enabled**. Nothing here is reachable by anyone but you.
- There IS a dormant workflow at `.github/workflows/jekyll-gh-pages.yml` that triggers on **push to `main`** and would serve the repo root with the game under `/web/`. It does nothing today because Pages is off. **Turning Pages on would publish `main` — the exact branch this snapshot came from.**
- The old `../runtime-reference/` folder shows there used to be two builds (`public/index.html` 240 KB, `private/index.html` 258 KB). **That split no longer exists** — the repo now has a single `web/index.html`. If you want a public build with private content stripped (story/lore, debug keys), it has to be rebuilt; there is no public variant today.
- Owner rules that bear on a public release: story/lore is a **private design brief**, never expose AI model names or the stack, and no engine-credit / "inspired by" taglines in shipped UI (the repo `README.md` still carries one).
