# Claude Code handoff — SHODO missing boards (SHEET_V 674)

Anthony approved this 29-board set. Implement it in:

`/Users/anthonyguy/SHADOWCLASH.1.0*2/SHODO-EDITION`

## Non-negotiable source rule

Use only art copied from `/Users/anthonyguy/SHADOWCLASH.1.0*2/art/production`. Do not use an existing runtime atlas, RECOVERY, another worktree, Downloads, or any legacy frame. The archive is deliberately limited to the selected 29 SHODO masters.

## Package contents

- `MANIFEST.csv`: the 29 moves, selected master, engine row, frame status, and notes.
- `masters/new20`: the 20 newly generated review masters Anthony approved.
- `masters/existing9`: the nine previously existing review masters Anthony approved.
- `frames/ready`: eight clean, reflowed alpha frames for each of the new 20 boards.
- `frames/source-only-bordered`: exact eight-way source cuts for the existing nine. These still contain drawn card borders and are **not pack-ready**.
- `qc`: contact sheets for visual review.

## Implementation contract

1. Read `MANIFEST.csv` and pack every move frame-by-frame in authored order. Do not replace an eight-frame move with repeated idle or fallback art.
2. Strip every panel border and all parchment to true alpha before packing. Never pack anything from `frames/source-only-bordered` unchanged.
3. Use one fighter-wide scale derived from that fighter's approved idle board. Do not fit or normalize individual poses. Required neutral in-game heights: Oni 153.1px, Executioner 126.9px, Exile 126.5px, Kael 122.5px, Tsubasa 121.8px, Ember 121.3px, Shin 116.5px, Mizu 109.2px, Mokurai 131.2px.
4. Grounded animation rows share a stable foot/world anchor. Air rows keep pose motion but do not bake world jump height into the cell. No frame may clip the figure or FX, and no frame may contain visible card/background whitespace.
5. Fighters face LEFT. Oni wall-cling and Mokurai wall-cling must contain no painted wall. Mokurai bell-ringer contains no literal bell prop.
6. Preserve gameplay: do not change damage, hitboxes, physics, move duration, or input timing during the art pass. Extend a hard-coded frame collector to `1..N` when needed so all eight authored beats can play.
7. Trace each live input through `web/index.html`; do not trust a similarly named dead alias. Raise `SHEET_V` only after all gates and live recordings pass.

Use the existing packers and keyer: `tools/sprites/pack_shodo_row.py`, `tools/sprites/pack_shodo_air.py`, `tools/sprites/pack_rows.py`, and `tools/sprites/key_sheet_cells.py`. The nine bordered sources need an inner-panel crop/border-removal pass before the keyer can reach the parchment.

## Decisions already made

- Exile Back+Special uses `grave-chain-reversal-parry-counter`, not `gravehound-chain-pursuit`.
- The four standing-medium boards stay archive-only because the engine has no medium tier.
- Excluded takes are listed in `REJECTED.md`; do not copy, key, or pack them.
- Runtime packing was intentionally not changed during generation. Claude owns implementation and live verification.

## Required gates

```sh
cd '/Users/anthonyguy/SHADOWCLASH.1.0*2/SHODO-EDITION'
python3 tools/sprites/key_sheet_cells.py selftest
python3 tools/check_shodo_roster.py
node tools/check_zero_legacy.mjs
node tools/check_first_form_gate.mjs
```

Then record consecutive frames from the real input path at `http://127.0.0.1:9101/` for all 29 routes and inspect scale, footing, left-facing direction, smooth progression, clipping, borders, and negative whitespace.
