# KAEL — NITŌ SEIHŌ 1–5 (the two-sword guards)

Five boards, **8 beats each = 40 frames**, each beat carrying its own written caption on the
board. Archived, not packed.

| # | guard | element | median body | vs Kael's 260px |
|---|---|---|---:|---:|
| 1 | **CHŪDAN** | middle / earth | 204px | 0.78× |
| 2 | **JŌDAN** | high / fire | 226px | 0.87× |
| 3 | **GEDAN** | low / water | 190px | 0.73× |
| 4 | **HIDARI-WAKI-GAMAE** | left side / wind | 188px | 0.72× |
| 5 | **MIGI-WAKI-GAMAE** | right side / void | 196px | 0.75× |

Background corner 248–253, **zero edge contact on all five**.

This is his **nitō** (two-sword) curriculum — distinct from the **kodachi seiho** set
(short-sword, 7 techniques × 6 beats) archived under `../new-style-actionsets-aug20/aug21-batch/`.

## Why these five matter more than the count suggests

**Five guards, five directions.** The engine gives every fighter exactly five directional
slots per tier — neutral, fwd, back, up, down — and these five guards land on them naturally:
chūdan is the middle/neutral, jōdan the high, gedan the low, and the two waki-gamae are the
left and right sides. That is not a coincidence to design around later; it is the shape of
his input matrix, already drawn.

**Each beat is captioned.** The boards carry per-beat text — "short sword catches and traps
the incoming line", "long sword drives instantly through the created opening". That is the
pose brief written by the person who designed the move, which is better than anything
reconstructed from old cells.

## ⛔ EIGHT BEATS COLLIDES WITH HIS AUTHORED TIMING — decide before packing

Verified in the engine, not assumed. `attackCellIndex` applies an authored timing track
**only when `track.length === cellCount`**; otherwise it silently falls back to generic even
exposure, and the contact frame lands on the wrong cell with no error anywhere.

Kael has **nine** authored tracks in `ANIM_TRACKS`, and eight of them are **6 entries**:

| track | entries | row | cells | applies? |
|---|---:|---|---:|---|
| spin, cyclone, scissor, heavy, dual, xcut, trav, fang | 6 | kspin, kcyc, kscis, kcross, kdual, kxcut, ktrav, kfang | 6 | ✅ |
| **rise** | **5** | **krise** | **6** | ❌ **already broken today** |

So delivering these as 8-cell rows means either **rewriting the track to 8 entries** (cheap,
one line each) or **cutting each guard to 6 beats**. Packing 8 against a 6-entry track is the
one option that fails silently.

### ⛔ And `rise` is already mismatched — a live bug, unrelated to the redraw

`krise1..6` holds **six** cells while its `rise` track holds **five** entries, so **Kael's
Rising Twin Fang has been ignoring its authored timing** and running generic exposure. The
repo's `check_dir_moves.mjs` exists to catch exactly this class, but it only walks the
`DIR_MOVES` / `DIR_SPECIALS` tables — and Kael has **zero** entries in either, because all his
directionals are hardcoded branches. That is why it slipped through.

Fix is one of: add a sixth entry to the `rise` track, or drop `krise` to five cells. Owner's
call which, since it changes the move's feel.
