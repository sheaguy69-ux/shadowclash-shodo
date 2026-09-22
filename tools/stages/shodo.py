#!/usr/bin/env python3
"""SHODO STAGES — the fourteen boards repainted as sumi ink on washi.

⛔ NO SPEND. Every stroke here is a distance field with brush texture on it;
nothing calls out to a generator. Deterministic per board (seeded), so a
re-run reproduces the exact same paper.

The look it is chasing is the real vocabulary, not "black and white":
  nijimi  — ink bleeding into wet paper (blurred underlay under every layer)
  kasure  — the dry brush skipping, hairs opening as the stroke runs out
  yohaku  — negative space carries the picture; the centre-bottom stays EMPTY
            because that is where two fighters stand.

ponytail: one density buffer per ink COLOUR, composited in a fixed order
(wash, sumi, accent, seal). A per-stroke colour would need a real painter's
algorithm and no board in the set wants black over red over black.
"""
import math
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFont

W, H = 2048, 1536          # 4:3, matching the boards these replace
# ⛔ THE GRAY — 灰色 (haiiro). Owner, Aug 27 2026: the game's theme is THE
# IN-BETWEEN REALM, so the sheet is neither the white world nor the black void.
# It is pitched between them, and BOTH ends still show on it: sumi stays at full
# black and the light stays at full bone, because the in-between is the only
# place where the two can appear on the same page. Every board is desaturated
# toward ash and keeps only a whisper of its own hue — enough to tell apart,
# never enough to leave the realm.
HAIIRO = (0.505, 0.505, 0.520)   # the ash the whole set is pitched at
HUE_KEEP = 0.34                  # how much of a board's own colour survives
VAL_KEEP = 0.45                  # ...and how much of its own lightness
TONE = 1.00                # multiplier on the ash (1.0 = haiiro as written)
VIGNETTE = 0.28            # how hard the sheet falls off at its corners
RUBBING = False            # True = takuhon: dark ground, strokes lifted pale
GROUND = 0.87              # stage `anchor`: image y that lands on the play floor
OUT = Path(__file__).resolve().parents[2] / "web/assets/stages"

# ---------------------------------------------------------------- primitives
def _box1(a, r):
    k = 2 * r + 1
    p = np.pad(a, ((0, 0), (r + 1, r)), mode="edge")
    c = np.cumsum(p, axis=1, dtype=np.float32)
    return (c[:, k:] - c[:, :-k]) / k


def _box0(a, r):
    k = 2 * r + 1
    p = np.pad(a, ((r + 1, r), (0, 0)), mode="edge")
    c = np.cumsum(p, axis=0, dtype=np.float32)
    return (c[k:, :] - c[:-k, :]) / k


def blur(a, r, passes=3):
    """Three box passes ~= a gaussian. ponytail: no scipy for one blur."""
    r = max(1, int(r))
    for _ in range(passes):
        a = _box1(a, r)
        a = _box0(a, r)
    return a


def vnoise(rng, cells, octaves=4, gain=0.5, w=W, h=H):
    out = np.zeros((h, w), np.float32)
    amp, tot, c = 1.0, 0.0, float(cells)
    for _ in range(octaves):
        gh = max(2, int(round(c * h / w)) + 1)
        gw = max(2, int(round(c)) + 1)
        g = (rng.random((gh, gw)) * 255).astype(np.uint8)
        out += amp * (np.asarray(Image.fromarray(g).resize((w, h), Image.BICUBIC),
                                 dtype=np.float32) / 255.0)
        tot += amp
        amp *= gain
        c *= 2
    return out / tot


def catmull(pts, n=260):
    P = np.asarray(pts, dtype=np.float32)
    if len(P) < 3:
        t = np.linspace(0, 1, n, dtype=np.float32)[:, None]
        return P[0] * (1 - t) + P[-1] * t
    Q = np.vstack([P[0], P, P[-1]])
    per = max(6, n // (len(P) - 1))
    out = []
    for i in range(len(P) - 1):
        p0, p1, p2, p3 = Q[i], Q[i + 1], Q[i + 2], Q[i + 3]
        t = np.linspace(0, 1, per, endpoint=(i == len(P) - 2), dtype=np.float32)[:, None]
        out.append(0.5 * ((2 * p1) + (-p0 + p2) * t
                          + (2 * p0 - 5 * p1 + 4 * p2 - p3) * t * t
                          + (-p0 + 3 * p1 - 3 * p2 + p3) * t * t * t))
    return np.vstack(out)


class Board:
    """One painting: a paper ground plus a few ink layers."""

    def __init__(self, seed, paper=(0.949, 0.920, 0.851), grain=1.0):
        self.rng = np.random.default_rng(seed)
        self.layers = {}                      # name -> density buffer
        # pitch every sheet at the ash, keeping a trace of its own hue and value
        t = np.array(paper, np.float32)
        self.paper_rgb = np.clip(np.array(HAIIRO, np.float32) * TONE
                                 + (t - t.mean()) * HUE_KEEP
                                 + (t.mean() - 0.925) * VAL_KEEP, 0, 1)
        self.grain = grain
        # paper tooth — the sheet's surface, which is what makes an ink edge ragged
        self.tooth = (vnoise(self.rng, 300, 3) - 0.5).astype(np.float32)

    def buf(self, name):
        if name not in self.layers:
            self.layers[name] = np.zeros((H, W), np.float32)
        return self.layers[name]

    # -- the brush -------------------------------------------------------
    def stroke(self, layer, pts, width, ink=1.0, prof=(0.22, 1.0, 0.10),
               dry=0.5, wobble=1.0, n=260):
        """A tapered brush stroke. prof = width at entry / belly / exit —
        (thin, full, thin) is a harai sweep, (1,1,1) a blunt tome."""
        P = catmull(pts, n)
        m = len(P)
        t = np.linspace(0, 1, m, dtype=np.float32)
        r = 0.5 * width * np.interp(t, [0.0, 0.5, 1.0], prof).astype(np.float32)
        if wobble:
            d = np.gradient(P, axis=0)
            L = np.hypot(d[:, 0], d[:, 1]) + 1e-6
            nx, ny = -d[:, 1] / L, d[:, 0] / L
            k = np.cumsum(self.rng.normal(0, 1, m).astype(np.float32))
            k = blur(k[None, :], max(2, m // 14))[0]
            k -= k.mean()
            k *= wobble * width * 0.10 / (np.abs(k).max() + 1e-6)
            P = P + np.stack([nx * k, ny * k], 1)

        D = np.full((H, W), 1e9, np.float32)
        T = np.zeros((H, W), np.float32)
        U = np.zeros((H, W), np.float32)
        for i in range(m - 1):
            x0, y0 = float(P[i, 0]), float(P[i, 1])
            x1, y1 = float(P[i + 1, 0]), float(P[i + 1, 1])
            rr = max(r[i], r[i + 1]) + 3.0
            xa = int(max(0, min(x0, x1) - rr)); xb = min(W, int(max(x0, x1) + rr) + 1)
            ya = int(max(0, min(y0, y1) - rr)); yb = min(H, int(max(y0, y1) + rr) + 1)
            if xb <= xa or yb <= ya:
                continue
            xs = np.arange(xa, xb, dtype=np.float32)[None, :]
            ys = np.arange(ya, yb, dtype=np.float32)[:, None]
            dx, dy = x1 - x0, y1 - y0
            L2 = dx * dx + dy * dy
            s = np.clip(((xs - x0) * dx + (ys - y0) * dy) / L2, 0, 1) if L2 > 1e-9 \
                else np.zeros((yb - ya, xb - xa), np.float32)
            d = np.hypot(xs - (x0 + s * dx), ys - (y0 + s * dy))
            rl = r[i] + (r[i + 1] - r[i]) * s
            sd = (d - rl).astype(np.float32)
            win = D[ya:yb, xa:xb]
            hit = sd < win
            win[hit] = sd[hit]
            D[ya:yb, xa:xb] = win
            tv = (t[i] + (t[i + 1] - t[i]) * s).astype(np.float32)
            side = np.sign((xs - x0) * dy - (ys - y0) * dx).astype(np.float32)
            uv = (np.clip(d / np.maximum(rl, 1e-3), 0, 1) * side).astype(np.float32)
            T[ya:yb, xa:xb][hit] = tv[hit]
            U[ya:yb, xa:xb][hit] = uv[hit]

        a = np.clip(0.5 - (D + self.tooth * 2.6) / 2.6, 0, 1)
        live = a > 0
        if not live.any():
            return
        if dry > 0:
            # KASURE. Hairs run ACROSS the width (signed, so the two sides differ),
            # broken up ALONG the length so they dash instead of engraving a comb.
            u, tv = U[live], T[live]
            ph = self.rng.random(5).astype(np.float32) * 6.283
            fr = np.array([2.5, 4.0, 6.5, 10.0, 16.0], np.float32)
            hv = np.zeros(u.shape, np.float32)
            for k in range(5):
                hv += np.cos(u * fr[k] * math.pi + ph[k])
            hv = hv / 5.0 * 0.5 + 0.5
            lp = self.rng.random(4).astype(np.float32) * 6.283
            lf = np.array([5.0, 9.0, 17.0, 27.0], np.float32)
            lv = np.zeros(tv.shape, np.float32)
            for k in range(4):
                lv += np.cos(tv * lf[k] * math.pi + lp[k])
            lv = lv / 4.0 * 0.5 + 0.5
            g = 0.62 * hv + 0.38 * lv
            thr = dry * (0.18 + 0.82 * tv)                # the head is wet, the tail dry
            f = np.ones((H, W), np.float32)
            f[live] = np.clip((g - thr) * 6.0 + 1.0 - dry * 0.55, 0, 1)
            a *= f
            a *= 1.0 - 0.26 * dry * T                     # the brush runs out of ink
        self.buf(layer)[:] = np.maximum(self.buf(layer), a * ink)

    def fill(self, layer, pts, ink=1.0, dry=0.30, ragged=1.6, closed=True, smooth=True):
        """A filled ink mass with a brush edge. Outline-only shapes read as
        diagrams; a silhouette reads as a roof, a mountain, a man."""
        P = (catmull(list(pts) + ([pts[0]] if closed else []), 420)
             if smooth else np.asarray(pts, np.float32))
        im = Image.new("L", (W, H), 0)
        ImageDraw.Draw(im).polygon([(float(x), float(y)) for x, y in P], fill=255)
        soft = blur(np.asarray(im, np.float32) / 255.0, 4)
        band = 4.0 * soft * (1.0 - soft)          # 1 on the boundary, 0 either side
        a = np.clip((soft - 0.5) * 6.0 + 0.5 + self.tooth * ragged * band * 3.0, 0, 1)
        if dry > 0:
            n = vnoise(self.rng, 130, 3)
            a *= np.clip(1.0 - dry * 0.9 * (0.58 - n), 0, 1)
        self.buf(layer)[:] = np.maximum(self.buf(layer), a * ink)

    def wash(self, layer, pts, width, ink=0.30, soft=26, n=180):
        """Soft ink wash — mist, rock mass, sky. No hairs, heavy bleed."""
        tmp = Board.__new__(Board)
        tmp.rng, tmp.layers, tmp.grain, tmp.tooth = self.rng, {}, 1.0, self.tooth
        tmp.stroke("w", pts, width, 1.0, prof=(1, 1, 1), dry=0.0, wobble=0.6, n=n)
        self.buf(layer)[:] = np.clip(self.buf(layer) + blur(tmp.layers["w"], soft) * ink, 0, 1.6)

    def halo(self, layer, cx, cy, r, ink=0.34, soft=40):
        """A reserved disc: sky wash around it, paper left inside. The moon."""
        ys, xs = np.mgrid[0:H, 0:W].astype(np.float32)
        d = np.hypot(xs - cx, ys - cy)
        ring = np.clip((d - r) / (r * 0.10), 0, 1) * np.exp(-np.clip((d - r) / (r * 0.62), 0, 9) ** 1.3)
        self.buf(layer)[:] = np.clip(self.buf(layer) + blur(ring, soft) * ink * 1.5, 0, 1.6)

    def flecks(self, layer, n, cx, cy, sx, sy, r0, r1, ink=0.6):
        for _ in range(n):
            x = self.rng.normal(cx, sx); y = self.rng.normal(cy, sy)
            rr = self.rng.uniform(r0, r1)
            self.stroke(layer, [(x - rr, y), (x + rr, y)], rr * 1.9,
                        ink * self.rng.uniform(0.5, 1.0), prof=(0.5, 1, 0.4),
                        dry=0.25, wobble=0.4, n=14)

    # -- output ----------------------------------------------------------
    def paper(self):
        rng = self.rng
        base = np.repeat(self.paper_rgb[None, None, :], H, 0).repeat(W, 1).copy()
        fib = (vnoise(rng, 40, 5) - 0.5) * 0.042 * self.grain
        fib += (_box1(rng.random((H, W)).astype(np.float32) - 0.5, 26)) * 0.075 * self.grain
        fib += (_box0(rng.random((H, W)).astype(np.float32) - 0.5, 22)) * 0.06 * self.grain
        mot = (vnoise(rng, 6, 3) - 0.5) * 0.030
        base += (fib + mot)[..., None]
        ys, xs = np.mgrid[0:H, 0:W].astype(np.float32)
        vig = np.clip(1 - (np.hypot((xs - W / 2) / (W * 0.60), (ys - H / 2) / (H * 0.64)) ** 2.6) * VIGNETTE, 0, 1)
        base *= vig[..., None]
        # kozo fibres: a few dark hairs in the sheet
        for _ in range(90):
            x, y = rng.uniform(0, W), rng.uniform(0, H)
            ang, ln = rng.uniform(0, 6.28), rng.uniform(14, 90)
            x2, y2 = x + math.cos(ang) * ln, y + math.sin(ang) * ln
            for f in np.linspace(0, 1, int(ln)):
                px, py = int(x + (x2 - x) * f), int(y + (y2 - y) * f)
                if 0 <= px < W and 0 <= py < H:
                    base[py, px] *= 0.955
        return np.clip(base, 0, 1)

    def render(self, order):
        img = self.paper()
        for name, rgb, bleed in order:
            if name not in self.layers:
                continue
            d = self.layers[name]
            a = np.clip(d + blur(d, 7) * bleed, 0, 1)
            col = np.array(rgb, np.float32)
            # thin ink is warmer and greyer than a loaded stroke
            lift = float(self.paper_rgb.mean()) * 0.70
            warm = col + (np.array([lift, lift * 0.98, lift * 0.94], np.float32) - col) * 0.52
            c = warm[None, None, :] + (col - warm)[None, None, :] * np.clip(a * 1.4, 0, 1)[..., None]
            img = img * (1 - a[..., None]) + c * a[..., None]
        return np.clip(img, 0, 1)

    def save(self, path, order):
        arr = (self.render(order) * 255 + 0.5).astype(np.uint8)
        # ponytail: these sheets are ~4 hues over a paper grain, so a 255-colour
        # palette is visually identical (measured RMSE 0.7%) at half the bytes.
        # Upgrade path if a board ever wants a true gradient: drop the quantize.
        img = Image.fromarray(arr).quantize(colors=255, dither=Image.Dither.FLOYDSTEINBERG)
        img.save(path, optimize=True)
        return path


# ------------------------------------------------------------------ motifs
SUMI = "sumi"; WASH = "wash"; ACC = "acc"; LITE = "lite"; SEAL = "seal"
MINCHO = "/System/Library/Fonts/ヒラギノ明朝 ProN.ttc"


def seal(b, cx, cy, size, chars, grit=1.0):
    """The vermillion hanko, top-right. hakubun: characters carved OUT of the red."""
    im = Image.new("L", (size, size), 0)
    d = ImageDraw.Draw(im)
    d.rectangle([0, 0, size - 1, size - 1], fill=255)
    d.rectangle([0, 0, size - 1, size - 1], outline=0, width=max(2, size // 26))
    try:
        f = ImageFont.truetype(MINCHO, int(size * (0.60 if len(chars) == 1 else 0.44)), index=0)
    except OSError:
        f = ImageFont.load_default()
    n = len(chars)
    for i, ch in enumerate(chars):
        y = size * (0.5 if n == 1 else (0.27 + 0.46 * i))
        d.text((size * 0.5, y), ch, font=f, fill=0, anchor="mm")
    a = np.asarray(im, np.float32) / 255.0
    # a stone seal never prints evenly
    n2 = vnoise(b.rng, 26, 3, w=size, h=size)
    a *= np.clip(1.0 - grit * (1.0 - np.clip((n2 - 0.30) * 5.0, 0.35, 1.0)), 0, 1)
    edge = np.zeros((size, size), np.float32)
    e = max(2, size // 22)
    edge[e:-e, e:-e] = 1.0
    a *= np.clip(blur(edge, e) + (0.25 + 0.4 * (1 - grit)) * (vnoise(b.rng, 9, 2, w=size, h=size) - 0.2), 0, 1)
    x0, y0 = int(cx - size / 2), int(cy - size / 2)
    b.buf(SEAL)[y0:y0 + size, x0:x0 + size] = np.maximum(
        b.buf(SEAL)[y0:y0 + size, x0:x0 + size], np.clip(a, 0, 1))


def culm(b, x, ybase, ytop, w, ink=1.0, dry=0.45, layer=SUMI, lean=0.0):
    """One bamboo stalk: segments with a gap and a node bar between each."""
    n = max(3, int((ybase - ytop) / 230))
    for i in range(n):
        y0 = ybase - (ybase - ytop) * i / n
        y1 = ybase - (ybase - ytop) * (i + 1) / n + 16
        f0, f1 = i / n, (i + 1) / n
        b.stroke(layer, [(x + lean * f0, y0), (x + lean * (f0 + f1) / 2, (y0 + y1) / 2),
                         (x + lean * f1, y1)], w * (1 - 0.34 * f0), ink * (1 - 0.12 * f0),
                 prof=(1, 0.97, 0.90), dry=dry, wobble=0.55, n=70)
        b.stroke(layer, [(x + lean * f1 - w * 0.75, y1 - 8), (x + lean * f1 + w * 0.75, y1 - 12)],
                 w * 0.30, ink, prof=(0.4, 1, 0.4), dry=dry * 0.5, wobble=0.4, n=20)


def leaves(b, x, y, size, n=7, ink=0.95, layer=SUMI, spread=1.0, down=1.0):
    for i in range(n):
        a = b.rng.uniform(-2.4, -0.7) if down > 0 else b.rng.uniform(0.7, 2.4)
        a += b.rng.normal(0, 0.5) * spread
        L = size * b.rng.uniform(0.6, 1.25)
        dx, dy = math.cos(a) * L, -math.sin(a) * L * down
        b.stroke(layer, [(x, y), (x + dx * 0.45, y + dy * 0.40), (x + dx, y + dy)],
                 size * 0.20, ink, prof=(0.9, 0.55, 0.03), dry=0.35, wobble=0.7, n=44)


def roof(b, cx, y, w, h, ink=1.0, layer=SUMI, dry=0.30):
    """A temple roof: a short ridge, slopes out to deep eaves, and the corners
    flicking UP past the eaves line. Shallow — an umbrella is the failure mode."""
    hw = w / 2
    right = [(cx + hw * 0.16, y), (cx + hw * 0.56, y + h * 0.54),
             (cx + hw * 0.92, y + h * 0.86), (cx + hw * 1.05, y + h * 0.80),
             (cx + hw * 0.99, y + h * 0.99), (cx + hw * 0.52, y + h * 1.03)]
    left = [(2 * cx - x, yy) for x, yy in reversed(right)]
    b.fill(layer, [(cx - hw * 0.16, y)] + [(cx + hw * 0.16, y)] + right[1:]
           + [(cx, y + h * 1.05)] + left[:-1], ink, dry)
    b.stroke(layer, [(cx - hw * 0.30, y + h * 0.03), (cx, y - h * 0.02),
                     (cx + hw * 0.30, y + h * 0.03)],
             h * 0.20, ink, prof=(0.9, 1, 0.9), dry=dry * 0.5, wobble=0.3, n=80)
    b.stroke(layer, [(cx - hw * 1.06, y + h * 0.78), (cx - hw * 0.58, y + h * 1.01),
                     (cx, y + h * 1.06), (cx + hw * 0.58, y + h * 1.01),
                     (cx + hw * 1.06, y + h * 0.78)],
             h * 0.09, ink, prof=(0.40, 1, 0.40), dry=dry, wobble=0.4, n=180)


def body(b, cx, ytop, ybot, w, ink=0.24, layer=SUMI, bays=4, dark=0.75):
    """The building UNDER the roof. Without it a roof is a mushroom on sticks."""
    hw = w / 2
    b.fill(layer, [(cx - hw, ytop), (cx + hw, ytop), (cx + hw * 0.97, ybot),
                   (cx - hw * 0.97, ybot)], ink, 0.5)
    for i in range(bays + 1):
        x = cx - hw + w * i / bays
        b.stroke(layer, [(x, ytop), (x, ybot)], w * 0.020, dark, prof=(1, 1, 1),
                 dry=0.45, wobble=0.3, n=40)
    b.stroke(layer, [(cx - hw * 1.02, ybot), (cx, ybot + 4), (cx + hw * 1.02, ybot)],
             w * 0.024, dark, prof=(0.4, 1, 0.4), dry=0.5, wobble=0.4, n=50)


def pillar(b, x, y0, y1, w, ink=1.0, layer=SUMI, dry=0.25, base=True, edge=SUMI):
    b.fill(layer, [(x - w * 0.46, y0), (x + w * 0.46, y0),
                   (x + w * 0.54, y1), (x - w * 0.54, y1)], ink, dry)
    for sgn in (-1, 1):                       # the two edges take the ink darkest
        b.stroke(edge, [(x + sgn * w * 0.48, y0), (x + sgn * w * 0.55, y1)],
                 w * 0.15, 0.85, prof=(1, 1, 1), dry=dry * 0.6, wobble=0.3, n=50)
    if base:
        b.stroke(edge, [(x - w * 0.95, y1 - 4), (x, y1 - 12), (x + w * 0.95, y1 - 4)],
                 w * 0.30, 0.88, prof=(0.5, 1, 0.5), dry=dry, wobble=0.3, n=40)


def ridge(b, pts, w, ink=0.9, layer=SUMI, dry=0.6, fill=0.0, base=None, smooth=True):
    if fill:
        P = list(pts)
        foot = base if base is not None else P[0][1] + fill
        b.fill(layer, P + [(P[-1][0], foot), (P[0][0], foot)], ink * fill, 0.45, smooth=smooth)
    b.stroke(layer, pts, w, ink, prof=(0.15, 1.0, 0.10), dry=dry, wobble=0.8, n=240)


def pine(b, x, ybase, h, ink=1.0, layer=SUMI):
    b.stroke(layer, [(x, ybase), (x + h * 0.05, ybase - h * 0.5), (x - h * 0.03, ybase - h)],
             h * 0.055, ink, prof=(1, 0.8, 0.25), dry=0.5, wobble=0.9, n=70)
    for i in range(4):
        f = 0.30 + 0.22 * i
        yy = ybase - h * f
        s = h * (0.34 - 0.06 * i)
        for sgn in (-1, 1):
            b.stroke(layer, [(x, yy), (x + sgn * s * 0.55, yy - s * 0.10),
                             (x + sgn * s, yy - s * 0.32)],
                     h * 0.045, ink * 0.92, prof=(0.9, 0.7, 0.05), dry=0.55, wobble=1.0, n=46)


def torii(b, cx, ytop, w, h, ink=1.0, layer=ACC):
    """Myojin style: the kasagi LIFTS at both tips, the nuki runs straight
    beneath it, and the columns lean in at the top and splay at the foot."""
    hw, lw = w / 2, w * 0.050
    b.stroke(layer, [(cx - hw * 1.20, ytop + h * 0.055), (cx - hw * 0.62, ytop - h * 0.012),
                     (cx, ytop - h * 0.030), (cx + hw * 0.62, ytop - h * 0.012),
                     (cx + hw * 1.20, ytop + h * 0.055)],
             lw * 1.45, ink, prof=(0.30, 1, 0.30), dry=0.34, wobble=0.5, n=210)
    b.stroke(layer, [(cx - hw * 1.06, ytop + h * 0.082), (cx, ytop + h * 0.058),
                     (cx + hw * 1.06, ytop + h * 0.082)],
             lw * 0.80, ink * 0.95, prof=(0.5, 1, 0.5), dry=0.30, wobble=0.4, n=170)
    b.stroke(layer, [(cx - hw * 1.00, ytop + h * 0.205), (cx, ytop + h * 0.200),
                     (cx + hw * 1.00, ytop + h * 0.205)],
             lw * 1.00, ink, prof=(0.65, 1, 0.65), dry=0.32, wobble=0.4, n=160)
    b.stroke(layer, [(cx, ytop + h * 0.085), (cx, ytop + h * 0.205)],
             lw * 0.70, ink, prof=(1, 1, 1), dry=0.22, wobble=0.2, n=22)
    for sgn in (-1, 1):
        b.stroke(layer, [(cx + sgn * hw * 0.815, ytop + h * 0.065),
                         (cx + sgn * hw * 0.880, ytop + h * 0.52),
                         (cx + sgn * hw * 0.975, ytop + h)],
                 lw * 1.30, ink, prof=(0.84, 1, 1.06), dry=0.30, wobble=0.35, n=150)


def arcring(b, cx, cy, rx, ry, a0, a1, w, ink=1.0, layer=SUMI, dry=0.55, prof=(0.10, 1, 0.06)):
    """An enso arc. Sweep it in one breath — the gap is part of the form."""
    t = np.linspace(a0, a1, 26)
    pts = [(cx + rx * math.cos(a), cy + ry * math.sin(a)) for a in t]
    b.stroke(layer, pts, w, ink, prof=prof, dry=dry, wobble=0.8, n=300)


def water(b, y, n=7, ink=0.55, layer=SUMI, spread=200, x0=60, x1=W - 60):
    for i in range(n):
        yy = y + i * spread / n + b.rng.normal(0, 6)
        a = x0 + b.rng.uniform(0, 260)
        c = x1 - b.rng.uniform(0, 260)
        b.stroke(layer, [(a, yy), ((a + c) / 2, yy + b.rng.normal(0, 7)), (c, yy)],
                 9 + 7 * i / n, ink * (0.5 + 0.5 * i / n), prof=(0.05, 1, 0.05),
                 dry=0.75, wobble=1.2, n=140)


def flame(b, x, ybase, h, ink=1.0, layer=ACC, n=5):
    """Fire licks. Thin, fast, tapering to nothing — never a blob."""
    for i in range(n):
        w = h * b.rng.uniform(0.045, 0.085)
        sway = b.rng.uniform(-0.42, 0.42)
        hh = h * b.rng.uniform(0.50, 1.0)
        xx = x + b.rng.normal(0, h * 0.13)
        b.stroke(layer, [(xx, ybase),
                         (xx + sway * hh * 0.20, ybase - hh * 0.40),
                         (xx - sway * hh * 0.16, ybase - hh * 0.72),
                         (xx + sway * hh * 0.10, ybase - hh)],
                 w, ink * b.rng.uniform(0.55, 1.0), prof=(0.95, 0.55, 0.015),
                 dry=0.55, wobble=1.2, n=120)


def stair(b, cx, ytop, ybot, wtop, wbot, n, ink=0.9, layer=SUMI, dry=0.4):
    """A flight seen head-on: the mass converging away, treads across it."""
    b.fill(layer, [(cx - wtop / 2, ytop), (cx + wtop / 2, ytop),
                   (cx + wbot / 2, ybot), (cx - wbot / 2, ybot)], ink * 0.30, 0.5)
    for i in range(n):
        f = i / (n - 1)
        y = ytop + (ybot - ytop) * f
        hw = (wtop + (wbot - wtop) * f) / 2
        b.stroke(layer, [(cx - hw, y + 3), (cx, y), (cx + hw, y + 3)],
                 8 + 12 * f, ink * (0.45 + 0.55 * f), prof=(0.35, 1, 0.35),
                 dry=dry, wobble=0.6, n=70)
    for sgn in (-1, 1):
        b.stroke(layer, [(cx + sgn * wtop / 2, ytop), (cx + sgn * wbot / 2, ybot)],
                 16, ink * 0.85, prof=(0.4, 1, 0.9), dry=dry, wobble=0.4, n=70)


def house(b, x, ybase, w, h, ink=1.0, layer=SUMI):
    """Machiya: heavy roof, light plaster body, dark posts holding it up."""
    roof(b, x, ybase - h, w, h * 0.48, ink, layer, dry=0.34)
    body(b, x, ybase - h + h * 0.46, ybase, w * 0.66, ink * 0.22, layer, 4, ink * 0.78)


# ------------------------------------------------------------------ boards
# THE FRAME IS MEASURED, NOT GUESSED. drawStage() cover-fits at 1.16 overscan
# onto a 1024x800 canvas with GROUND_Y 712, so of this 2048x1536 sheet the
# player only ever sees x 200..1850, y 170..1470 (parallax swings x by ~100).
# The ground line lands on y 1337. A fighter is ~116 image px tall and jumps
# to ~330, so y 1010..1340 is where two bodies stand: that band stays QUIET.
G = 1337
FX0, FX1 = 200, 1850
FY0 = 170
QUIET = 1010

VERM = (0.686, 0.161, 0.118)      # shu — seal and torii vermillion
INDIGO = (0.129, 0.204, 0.333)
OCHRE = (0.573, 0.412, 0.129)
MOSS = (0.243, 0.322, 0.220)
EMBER = (0.757, 0.302, 0.086)


def sky(b, y=600, ink=0.13, soft=110):
    """Weather, not a filter: heaviest at the top edge, gone by mid-sheet."""
    b.wash(WASH, [(-200, y * 0.30), (W / 2, y * 0.06), (W + 200, y * 0.34)], y * 1.25, ink, soft)


def mist(b, amt=1.0, y0=430, y1=1240, n=5, layer=LITE):
    """THE GRAY breathes. Bands of haze lying across the middle distance, each
    one starting and ending at a different place so the sheet never shows a
    stripe — plus one low bank that eats the feet of everything standing in it."""
    if amt <= 0:
        return
    for i in range(n):
        f = i / max(1, n - 1)
        y = y0 + (y1 - y0) * f + b.rng.normal(0, 30)
        x0 = -320 + b.rng.uniform(0, 520)
        x1 = W + 320 - b.rng.uniform(0, 520)
        b.wash(layer, [(x0, y), ((x0 + x1) / 2, y + b.rng.normal(0, 26)), (x1, y)],
               b.rng.uniform(110, 230),
               amt * (0.055 + 0.075 * f) * b.rng.uniform(0.7, 1.25),
               int(b.rng.uniform(64, 116)))
    b.wash(layer, [(-320, G - 74), (W / 2, G - 104), (W + 320, G - 68)],
           250, amt * 0.115, 96)


def ground(b, ink=0.18):
    b.wash(WASH, [(-80, G - 26), (W / 2, G - 56), (W + 80, G - 20)], 150, ink, 46)


def bamboo(b):
    sky(b, 620, 0.10, 120)
    for x, yt, w, ik in [(880, 430, 24, 0.26), (1130, 500, 20, 0.22), (700, 470, 22, 0.24),
                         (1330, 450, 22, 0.24)]:
        culm(b, x, G - 30, yt, w, ik, dry=0.5, layer=WASH)
        leaves(b, x + 8, yt + 40, 120, 4, ik, layer=WASH)
    for x, w, ln, ik in [(250, 74, 26, 0.94), (415, 58, -16, 0.90), (1560, 56, -14, 0.90),
                         (1720, 72, 18, 0.94), (1840, 60, -10, 0.86)]:
        culm(b, x, G + 40, FY0 - 120, w, ik, dry=0.46, lean=ln)
    for x, y in [(268, 330), (430, 500), (250, 700), (1548, 380), (1740, 280), (1846, 560)]:
        leaves(b, x, y, 240, 8, 0.92)
    # THE SEVERED CULM — the board's name, and it has to read as a CUT: a short
    # stump, and the whole top length lying across the sheet above it.
    culm(b, 760, G + 30, 980, 62, 0.95, dry=0.42)
    b.stroke(SUMI, [(730, 992), (762, 950), (800, 986)], 22, 1.0, prof=(0.2, 1, 0.2), dry=0.3, n=40)
    b.stroke(SUMI, [(812, 916), (1120, 760), (1430, 610), (1660, 470)], 56, 0.95,
             prof=(0.98, 1, 0.34), dry=0.5, wobble=0.7, n=200)
    for i, xx in enumerate((1000, 1230, 1470)):
        b.stroke(SUMI, [(xx - 44, 862 - i * 108), (xx + 40, 838 - i * 108)], 18, 0.9,
                 prof=(0.4, 1, 0.4), dry=0.4, n=24)
    leaves(b, 1660, 470, 220, 8, 0.9)
    leaves(b, 1180, 720, 170, 5, 0.85)
    b.flecks(SUMI, 20, 1150, 900, 480, 260, 5, 12, 0.30)
    ground(b, 0.16)
    seal(b, 1720, 300, 140, "竹")


def rooftops(b):
    b.halo(WASH, 1500, 380, 180, 0.34, 26)
    sky(b, 560, 0.09, 120)
    b.stroke(SUMI, [(FX0 - 160, 1000), (700, 972), (1330, 990), (FX1 + 160, 960)], 24, 0.42,
             prof=(0.25, 1, 0.25), dry=0.65, n=200)           # the far skyline
    roof(b, 1020, 856, 720, 132, 0.22, WASH, dry=0.5)
    roof(b, 250, 330, 1060, 190, 0.94, SUMI, dry=0.28)        # you are in the street
    body(b, 250, 522, G + 30, 700, 0.24, SUMI, 5, 0.82)
    roof(b, 1810, 300, 1080, 195, 0.94, SUMI, dry=0.28)
    body(b, 1810, 498, G + 30, 720, 0.24, SUMI, 5, 0.82)
    roof(b, 690, 700, 520, 112, 0.86, SUMI, dry=0.34)
    body(b, 690, 812, G - 60, 330, 0.17, SUMI, 3, 0.66)
    roof(b, 1370, 730, 500, 108, 0.86, SUMI, dry=0.34)
    body(b, 1370, 838, G - 50, 320, 0.17, SUMI, 3, 0.66)
    for x, y in [(470, 690), (900, 852), (1180, 862), (1600, 664), (300, 700), (1760, 656)]:
        b.stroke(SUMI, [(x, y - 58), (x, y - 8)], 8, 0.7, prof=(0.6, 1, 0.6), dry=0.35, n=20)
        b.stroke(ACC, [(x, y), (x, y + 46)], 28, 0.90, prof=(0.7, 1, 0.6), dry=0.25, n=24)
        b.stroke(SUMI, [(x - 20, y - 8), (x + 20, y - 8)], 10, 0.75, prof=(0.4, 1, 0.4), dry=0.3, n=14)
        # wet stone: the lantern comes back up off the street, broken by the ripple
        for i in range(3):
            b.stroke(ACC, [(x - 26 - i * 6, 1140 + i * 62), (x + 26 + i * 6, 1146 + i * 62)],
                     9, 0.30 - 0.07 * i, prof=(0.2, 1, 0.2), dry=0.6, n=26)
    for i in range(5):
        b.stroke(SUMI, [(FX0 - 200, 1120 + i * 58), (1024, 1112 + i * 58), (FX1 + 200, 1122 + i * 58)],
                 10, 0.16, prof=(0.2, 1, 0.2), dry=0.7, n=140)
    ground(b, 0.20)
    seal(b, 1720, 300, 140, "江戸")


def rooftemple(b):
    b.halo(WASH, 1440, 320, 155, 0.34, 24)
    sky(b, 620, 0.11, 130)
    for i, (y, w) in enumerate([(900, 300), (740, 252), (590, 202), (450, 154)]):
        roof(b, 980, y, w, w * 0.28, 0.24 - 0.03 * i, WASH, dry=0.5)      # the far pagoda
    b.stroke(WASH, [(980, 450), (980, 910)], 20, 0.20, prof=(0.8, 1, 0.8), dry=0.5, n=60)
    roof(b, 300, 500, 1140, 235, 0.95, SUMI, dry=0.26)
    body(b, 300, 736, G + 30, 700, 0.20, SUMI, 5, 0.78)
    roof(b, 1780, 470, 1160, 240, 0.95, SUMI, dry=0.26)
    body(b, 1780, 712, G + 30, 720, 0.20, SUMI, 5, 0.78)
    roof(b, 700, 916, 740, 152, 0.84, SUMI, dry=0.34)
    body(b, 700, 1070, G - 26, 470, 0.15, SUMI, 4, 0.62)
    ground(b, 0.18)
    seal(b, 1720, 300, 140, "甍")


def hall(b):
    sky(b, 380, 0.16, 100)
    # THE ROOF THEY CAME THROUGH — a heavy beam with a hole torn in it, and the
    # only daylight in the board falling out of the hole onto the floor.
    b.fill(SUMI, [(FX0 - 300, 250), (700, 206), (1300, 236), (FX1 + 300, 196),
                  (FX1 + 300, 320), (1300, 356), (700, 326), (FX0 - 300, 370)], 0.97, 0.35)
    b.wash(WASH, [(-200, 700), (300, 760), (620, 900)], 620, 0.30, 110)
    b.wash(WASH, [(1300, 900), (1700, 760), (W + 200, 700)], 620, 0.30, 110)
    b.fill(LITE, [(692, 316), (872, 316), (992, 1250), (612, 1250)], 0.55, 0.45,
           ragged=0.7, smooth=False)
    b.fill(LITE, [(742, 316), (816, 316), (886, 1210), (716, 1210)], 0.40, 0.5,
           ragged=0.7, smooth=False)
    b.flecks(LITE, 60, 800, 780, 90, 300, 3, 7, 0.7)
    b.stroke(SUMI, [(660, 300), (700, 214), (790, 306), (868, 222), (940, 300)], 28, 1.0,
             prof=(0.25, 1, 0.25), dry=0.5, n=120)
    # two rows of pillars going away from you: the far pair is SHORTER, so the
    # hall has a length instead of being six bars on a wall
    for x, w, y0, y1, ik in [(280, 66, 330, G + 30, 1.0), (1790, 66, 330, G + 30, 1.0),
                             (560, 46, 400, 1250, 0.90), (1510, 46, 400, 1250, 0.90),
                             (752, 32, 452, 1188, 0.74), (1318, 32, 452, 1188, 0.74)]:
        pillar(b, x, y0, y1, w, ik, ACC, dry=0.34)
        b.stroke(SUMI, [(x - w * 1.15, y0 + 54), (x + w * 1.15, y0 + 48)], w * 0.42, ik * 0.8,
                 prof=(0.5, 1, 0.5), dry=0.35, n=26)
    # the altar at the far end: a seated figure, small, and not the point
    b.fill(WASH, [(940, 800), (1108, 800), (1150, 1040), (898, 1040)], 0.34, 0.5)
    b.fill(SUMI, [(996, 700), (1024, 676), (1052, 700), (1058, 748), (1024, 766), (990, 748)], 0.55, 0.4)
    b.fill(SUMI, [(966, 776), (1082, 776), (1112, 900), (936, 900)], 0.48, 0.45)
    b.stroke(SUMI, [(880, 1046), (1024, 1030), (1168, 1046)], 32, 0.62, prof=(0.3, 1, 0.3), dry=0.5, n=80)
    for f, y in ((0.30, 1130), (0.55, 1220), (0.85, 1310)):     # the floor running away
        b.stroke(SUMI, [(1024 - 900 * f, y), (1024, y - 14), (1024 + 900 * f, y)],
                 14, 0.30, prof=(0.2, 1, 0.2), dry=0.7, n=120)
    ground(b, 0.22)
    seal(b, 1720, 300, 140, "堂")


def drowned(b):
    b.halo(WASH, 1480, 430, 205, 0.36, 28)
    sky(b, 560, 0.09, 120)
    ridge(b, [(FX0 - 300, 800), (560, 690), (980, 790)], 22, 0.22, WASH, 0.7)
    ridge(b, [(1280, 780), (1700, 660), (W + 200, 780)], 20, 0.20, WASH, 0.7)
    torii(b, 1010, 470, 1300, 830, 0.98, ACC)
    torii(b, 380, 890, 280, 210, 0.26, WASH)
    water(b, 1130, 8, 0.42, SUMI, 210, FX0 - 140, FX1 + 140)
    for x in (330, 1700):                       # stone lanterns standing in the shallows
        pillar(b, x, 1120, 1240, 40, 0.82, dry=0.35, base=False)
        b.stroke(SUMI, [(x - 46, 1114), (x, 1104), (x + 46, 1114)], 26, 0.90,
                 prof=(0.45, 1, 0.45), dry=0.3, n=26)
        b.stroke(ACC, [(x, 1082), (x, 1056)], 30, 0.85, prof=(0.8, 1, 0.7), dry=0.2, n=16)
    ground(b, 0.18)
    seal(b, 1720, 300, 140, "水")


def village(b):
    b.wash(ACC, [(-100, 300), (W / 2, 214), (W + 100, 316)], 300, 0.13, 100)
    sky(b, 620, 0.10, 120)
    ridge(b, [(FX0 - 300, 680), (620, 570), (1180, 660), (1660, 580), (W + 200, 670)],
          20, 0.26, WASH, 0.75, fill=0.28, base=880)
    for x, w, h in [(340, 680, 420), (1780, 700, 430)]:
        house(b, x, G - 6, w, h, 0.95)
    house(b, 900, G - 22, 470, 290, 0.62)
    for x, y in [(520, 1186), (1556, 1194), (964, 1246)]:
        b.stroke(ACC, [(x, y), (x, y + 36)], 24, 0.88, prof=(0.7, 1, 0.6), dry=0.25, n=24)
    # the dead tree — the only thing on this board still standing straight up
    b.stroke(SUMI, [(1600, G - 16), (1636, 940), (1614, 620)], 42, 1.0, prof=(1, 0.82, 0.22),
             dry=0.5, wobble=1.1, n=100)
    for a, L in [(-0.85, 320), (-2.25, 360), (-1.55, 260), (-0.35, 210), (-2.75, 200)]:
        b.stroke(SUMI, [(1624, 790), (1624 + math.cos(a) * L * 0.5, 790 + math.sin(a) * L * 0.5),
                        (1624 + math.cos(a) * L, 790 + math.sin(a) * L)],
                 20, 0.95, prof=(0.9, 0.58, 0.03), dry=0.65, wobble=1.2, n=64)
    b.flecks(SUMI, 170, W / 2, 680, 660, 400, 3, 9, 0.26)      # ash, and it is grey
    ground(b, 0.22)
    seal(b, 1720, 300, 140, "灰")


def warrant(b):
    sky(b, 820, 0.14, 150)
    roof(b, 1420, 560, 920, 195, 0.95, SUMI, dry=0.28)         # the gatehouse, behind the wall
    body(b, 1420, 752, 906, 620, 0.20, SUMI, 4, 0.78)
    # THE WALL — a mass with a tiled coping on it, running the whole board
    b.fill(SUMI, [(FX0 - 300, 906), (760, 890), (1400, 898), (FX1 + 300, 882),
                  (FX1 + 300, 1140), (FX0 - 300, 1150)], 0.22, 0.5)
    b.stroke(SUMI, [(FX0 - 300, 898), (760, 882), (1400, 890), (FX1 + 300, 874)], 34, 0.95,
             prof=(0.65, 1, 0.65), dry=0.32, n=230)
    for x in range(180, 1900, 126):
        b.stroke(SUMI, [(x, 916), (x + 5, 1010)], 11, 0.34, prof=(0.6, 1, 0.4), dry=0.65, n=22)
    b.stroke(SUMI, [(FX0 - 300, 1148), (900, 1136), (FX1 + 300, 1142)], 20, 0.55,
             prof=(0.4, 1, 0.4), dry=0.5, n=180)
    # the notice board: a warrant yard is named for what is nailed up in it
    for x in (424, 548):
        b.stroke(SUMI, [(x, 1220), (x, 800)], 22, 0.96, prof=(1, 1, 1), dry=0.3, n=54)
    b.fill(LITE, [(346, 782), (626, 774), (624, 978), (348, 970)], 0.62, 0.35,
           ragged=0.8, smooth=False)
    for a, c in (((346, 782), (626, 774)), ((626, 774), (624, 978)),
                 ((624, 978), (348, 970)), ((348, 970), (346, 782))):
        b.stroke(SUMI, [a, c], 13, 0.90, prof=(0.7, 1, 0.7), dry=0.35, n=40)
    b.stroke(SUMI, [(340, 780), (486, 774), (632, 770)], 22, 1.0, prof=(0.6, 1, 0.6), dry=0.3, n=60)
    b.stroke(SUMI, [(342, 974), (486, 980), (630, 972)], 18, 1.0, prof=(0.6, 1, 0.6), dry=0.3, n=60)
    for i in range(4):
        b.stroke(SUMI, [(392, 820 + i * 36), (566, 816 + i * 36)], 11, 0.72,
                 prof=(0.3, 1, 0.2), dry=0.5, n=30)
    seal(b, 486, 940, 62, "令")
    ground(b, 0.20)
    seal(b, 1720, 300, 140, "捕")


def snow(b):
    sky(b, 760, 0.14, 150)
    ridge(b, [(FX0 - 300, 720), (400, 330), (760, 570), (1080, 380), (1460, 660)],
          22, 0.62, SUMI, 0.85, fill=0.34, base=1100)
    ridge(b, [(1080, 780), (1480, 520), (1760, 700), (W + 200, 590)],
          18, 0.44, SUMI, 0.9, fill=0.22, base=1080)
    b.wash(WASH, [(-100, 960), (W / 2, 918), (W + 100, 950)], 210, 0.12, 60)
    for x, h in [(380, 340), (1780, 310), (600, 230), (250, 220)]:
        pine(b, x, 1080, h, 0.88)
    # the little shrine, alone on its ledge
    roof(b, 1380, 790, 380, 96, 0.96, ACC, dry=0.25)
    for x in (1268, 1492):
        pillar(b, x, 878, 1040, 26, 0.92, ACC, dry=0.25, base=False)
    b.stroke(SUMI, [(1218, 1046), (1380, 1038), (1542, 1046)], 22, 0.78,
             prof=(0.4, 1, 0.4), dry=0.4, n=50)
    b.stroke(SUMI, [(1120, 1092), (1380, 1074), (1640, 1094)], 26, 0.40,
             prof=(0.2, 1, 0.2), dry=0.7, n=70)
    b.flecks(LITE, 280, W / 2, 700, 660, 430, 4, 13, 0.85)
    ground(b, 0.13)
    seal(b, 1720, 300, 140, "雪")


def keep(b):
    b.wash(ACC, [(-100, G - 20), (W / 2, G - 240), (W + 100, G - 20)], 430, 0.17, 120)
    sky(b, 560, 0.13, 130)
    for sgn, x in ((-1, 300), (1, 1750)):                      # what is left standing
        b.fill(SUMI, [(x - 70, 330 + sgn * 40), (x + 20, 250), (x + 68, 340 - sgn * 30),
                      (x + 74, G + 40), (x - 76, G + 40)], 0.94, 0.34)
        for i in range(6):
            b.stroke(LITE, [(x - 66, 400 + i * 165), (x + 64, 392 + i * 165)], 12, 0.40,
                     prof=(0.3, 1, 0.3), dry=0.5, n=30)
    roof(b, 1024, 400, 1180, 215, 0.95, SUMI, dry=0.28)        # the gate, broken open
    body(b, 1024, 612, 1080, 780, 0.16, SUMI, 3, 0.62)
    pillar(b, 660, 600, 1090, 78, 0.90, dry=0.35)
    pillar(b, 1390, 600, 1090, 78, 0.90, dry=0.35)
    b.stroke(SUMI, [(690, 646), (900, 636), (1150, 652), (1370, 640)], 36, 0.90,
             prof=(0.4, 1, 0.4), dry=0.45, n=130)
    for x0, y0, x1, y1 in [(700, 1150, 790, 940), (1330, 1160, 1250, 950), (1024, 1180, 1060, 1000)]:
        b.stroke(SUMI, [(x0, y0), ((x0 + x1) / 2 + 30, (y0 + y1) / 2), (x1, y1)], 16, 0.72,
                 prof=(0.9, 0.5, 0.02), dry=0.7, wobble=1.4, n=90)     # the cracks
    for x, h in [(300, 460), (1750, 480), (540, 330), (1500, 340)]:
        flame(b, x, G - 10, h, 1.0, ACC, 6)
    b.flecks(ACC, 80, W / 2, 780, 620, 340, 3, 9, 0.6)
    ground(b, 0.24)
    seal(b, 1720, 300, 140, "焔")


def tollgate(b):
    sky(b, 480, 0.12, 120)
    for sgn, x in ((-1, 268), (1, 1782)):
        b.fill(SUMI, [(x - 82, FY0 - 140), (x + 78, FY0 - 140), (x + 84, 760),
                      (x + 74, G + 40), (x - 76, G + 40), (x - 88, 760)], 0.90, 0.30)
        for i in range(7):
            b.stroke(LITE, [(x - 72, 300 + i * 150), (x + 70, 292 + i * 150)], 11, 0.34,
                     prof=(0.3, 1, 0.3), dry=0.5, n=30)
    b.wash(WASH, [(1024, 320), (1024, 660), (1024, 930)], 620, 0.18, 80)
    # THE DOOR — the only way on, and it is shut
    b.fill(SUMI, [(742, 950), (742, 500), (860, 386), (1024, 356), (1188, 386),
                  (1306, 500), (1306, 950)], 0.55, 0.42)
    b.stroke(SUMI, [(742, 950), (742, 500), (860, 386), (1024, 356), (1188, 386),
                    (1306, 500), (1306, 950)], 44, 0.98, prof=(0.9, 1, 0.9), dry=0.26,
             wobble=0.4, n=240)
    for i in range(5):
        f = 0.18 + 0.16 * i
        b.stroke(SUMI, [(742 + 564 * f, 942), (742 + 564 * f, 470 + abs(0.5 - f) * 170)],
                 14, 0.85, prof=(0.7, 1, 0.5), dry=0.5, n=60)
    b.stroke(SUMI, [(1024, 690), (1024, 700)], 74, 0.95, prof=(1, 1, 1), dry=0.2, n=12)
    b.stroke(SUMI, [(700, 960), (1024, 944), (1348, 960)], 40, 0.98,
             prof=(0.5, 1, 0.5), dry=0.3, n=110)
    stair(b, 1024, 1000, G - 6, 640, 1180, 9, 0.88, SUMI, 0.42)
    for x in (610, 1438):                                      # the two lanterns
        b.stroke(SUMI, [(x, 500), (x, 664)], 11, 0.80, prof=(0.5, 1, 0.5), dry=0.4, n=30)
        b.stroke(ACC, [(x, 686), (x, 786)], 78, 0.92, prof=(0.55, 1, 0.55), dry=0.3, n=40)
        b.stroke(SUMI, [(x - 48, 682), (x, 672), (x + 48, 682)], 18, 0.9, prof=(0.4, 1, 0.4), dry=0.3, n=26)
        b.stroke(SUMI, [(x - 40, 790), (x, 800), (x + 40, 790)], 16, 0.9, prof=(0.4, 1, 0.4), dry=0.3, n=26)
    ground(b, 0.20)
    seal(b, 1720, 300, 140, "門")


def temple(b):
    sky(b, 520, 0.11, 120)
    b.halo(ACC, 1024, 640, 390, 0.24, 60)                      # the nimbus
    # THE GREAT BUDDHA — a silhouette, not a smudge: topknot, head, shoulders,
    # folded arms, the lap. No face. He is what the fighters happen to stand in
    # front of, so he is grey and he never competes with them.
    b.fill(WASH, [(1010, 396), (1038, 396), (1046, 424), (1002, 424)], 0.52, 0.4)
    b.fill(WASH, [(1024, 420), (1096, 452), (1114, 540), (1080, 610), (1024, 628),
                  (968, 610), (934, 540), (952, 452)], 0.52, 0.4)
    b.fill(WASH, [(1024, 636), (1150, 690), (1216, 830), (1230, 968),
                  (818, 968), (832, 830), (898, 690)], 0.46, 0.45)
    b.fill(WASH, [(760, 968), (1288, 968), (1330, 1078), (718, 1078)], 0.50, 0.45)
    b.stroke(SUMI, [(934, 540), (952, 452), (1024, 420), (1096, 452), (1114, 540)], 22, 0.60,
             prof=(0.3, 1, 0.3), dry=0.5, wobble=0.6, n=140)
    b.stroke(SUMI, [(832, 830), (898, 690), (1024, 636), (1150, 690), (1216, 830)], 26, 0.55,
             prof=(0.25, 1, 0.25), dry=0.55, wobble=0.7, n=170)
    b.stroke(SUMI, [(700, 1096), (1024, 1052), (1348, 1096)], 48, 0.80,
             prof=(0.35, 1, 0.35), dry=0.4, n=150)             # the lotus base
    for x, w in ((286, 58), (566, 40), (1482, 40), (1762, 58)):
        pillar(b, x, 360, G + 30, w, 0.80, ACC, dry=0.40)
        b.stroke(SUMI, [(x - w * 1.2, 430), (x + w * 1.2, 424)], w * 0.40, 0.85,
                 prof=(0.5, 1, 0.5), dry=0.35, n=26)
    b.fill(SUMI, [(FX0 - 300, 268), (700, 226), (1400, 232), (FX1 + 300, 204),
                  (FX1 + 300, 330), (1400, 358), (700, 352), (FX0 - 300, 394)], 0.96, 0.35)
    ground(b, 0.22)
    seal(b, 1720, 300, 140, "佛")


def volcano(b):
    b.wash(ACC, [(-100, G + 40), (W / 2, 780), (W + 100, G + 40)], 560, 0.26, 130)
    sky(b, 420, 0.18, 120)
    L = [(FX0 - 400, 300), (250, 214), (390, 470), (520, 250), (660, 620),
         (830, 400), (900, 720), (960, 1056), (FX0 - 400, 1056)]
    R = [(1090, 1056), (1130, 760), (1210, 470), (1330, 690), (1470, 250),
         (1620, 620), (1760, 400), (1880, 196), (FX1 + 400, 430), (FX1 + 400, 1056)]
    b.fill(SUMI, L, 0.92, 0.40, smooth=False)
    b.fill(SUMI, R, 0.92, 0.40, smooth=False)
    ridge(b, L[:-1], 20, 0.98, SUMI, 0.55)
    ridge(b, R[:-1], 20, 0.98, SUMI, 0.55)
    # THE FACE IN THE ROCK — two lit eyes and a lit seam, cut INTO the left mass.
    # No horns: on a jagged ridge the peaks ARE the horns.
    b.stroke(ACC, [(430, 640), (516, 676)], 38, 0.95, prof=(0.3, 1, 0.2), dry=0.4, n=30)
    b.stroke(ACC, [(600, 690), (686, 654)], 38, 0.95, prof=(0.2, 1, 0.3), dry=0.4, n=30)
    b.stroke(ACC, [(468, 810), (560, 840), (654, 806)], 18, 0.70, prof=(0.2, 1, 0.2), dry=0.6, n=50)
    b.stroke(SUMI, [(FX0 - 260, 1058), (560, 1018), (1024, 1052), (1500, 1016), (FX1 + 260, 1054)],
             40, 0.96, prof=(0.65, 1, 0.65), dry=0.35, n=240)  # the cauldron rim
    for x, h in [(380, 400), (1680, 420), (700, 300), (1360, 320)]:
        flame(b, x, G - 20, h, 1.0, ACC, 7)
    b.flecks(ACC, 130, W / 2, 800, 680, 360, 3, 10, 0.7)
    seal(b, 1720, 300, 140, "獄")


def lantern(b):
    """The emptiest board in the set. A vault, one light, and the pit it hangs
    over — three marks, and the rest of the sheet left alone. Yohaku."""
    b.wash(WASH, [(-100, 230), (W / 2, 150), (W + 100, 240)], 300, 0.24, 90)
    for sgn, x in ((-1, 264), (1, 1794)):                      # the vault springs from walls
        b.fill(SUMI, [(x - 92, 520), (x + 88, 560), (x + 84, G + 40), (x - 96, G + 40)], 0.88, 0.32)
        for i in range(5):
            b.stroke(LITE, [(x - 80, 640 + i * 160), (x + 76, 632 + i * 160)], 12, 0.34,
                     prof=(0.3, 1, 0.3), dry=0.5, n=30)
    b.fill(SUMI, [(172, 560), (520, 340), (1024, 268), (1528, 340), (1876, 560),
                  (1876, 470), (1528, 258), (1024, 184), (520, 258), (172, 470)], 0.86, 0.35)
    b.stroke(SUMI, [(300, 520), (700, 366), (1024, 322), (1348, 366), (1748, 520)],
             16, 0.40, prof=(0.2, 1, 0.2), dry=0.6, wobble=0.8, n=220)
    LX = 1330                                                  # OFF centre. Never centred.
    b.stroke(SUMI, [(LX, 300), (LX, 640)], 11, 0.88, prof=(0.6, 1, 0.6), dry=0.35, n=60)
    b.halo(LITE, LX, 736, 240, 0.52, 46)
    b.fill(ACC, [(LX - 62, 668), (LX + 62, 668), (LX + 70, 748), (LX + 56, 812),
                 (LX - 56, 812), (LX - 70, 748)], 0.94, 0.30)
    b.stroke(SUMI, [(LX - 78, 662), (LX, 650), (LX + 78, 662)], 24, 0.92, prof=(0.4, 1, 0.4), dry=0.3, n=40)
    b.stroke(SUMI, [(LX - 60, 818), (LX, 830), (LX + 60, 818)], 20, 0.92, prof=(0.4, 1, 0.4), dry=0.3, n=40)
    for i in range(3):
        b.stroke(SUMI, [(LX - 58, 700 + i * 42), (LX + 58, 700 + i * 42)], 8, 0.55,
                 prof=(0.4, 1, 0.4), dry=0.4, n=20)
    # THE PIT — one enso, swept in a single breath, its gap left open
    arcring(b, 1024, 1210, 700, 168, 0.62, 6.52, 44, 0.95, SUMI, 0.6)
    b.wash(WASH, [(440, 1236), (1024, 1300), (1610, 1236)], 250, 0.22, 70)
    ground(b, 0.10)
    seal(b, 1720, 300, 140, "燈")


def abyss(b):
    """No floor. The sheet says so: the bottom third is flooded ink, and the
    stair walks down into it and stops."""
    b.fill(SUMI, [(-200, 1460), (W / 2, 1330), (W + 200, 1460),
                  (W + 200, H + 200), (-200, H + 200)], 0.92, 0.45)
    b.wash(WASH, [(-200, H + 120), (W / 2, 1180), (W + 200, H + 120)], 700, 1.0, 150)
    b.wash(WASH, [(-200, 520), (W / 2, 700), (W + 200, 520)], 800, 0.42, 180)
    for sgn, x in ((-1, 268), (1, 1790)):
        for xx, w, ik in [(x, 220, 0.92), (x + sgn * 246, 136, 0.54), (x + sgn * 420, 88, 0.30)]:
            pillar(b, xx, FY0 - 130, 1360, w, ik, dry=0.32, base=False)
            b.stroke(SUMI, [(xx - w * 0.8, FY0 + 40), (xx + w * 0.8, FY0 + 30)], w * 0.34,
                     ik, prof=(0.5, 1, 0.5), dry=0.35, n=26)
    stair(b, 1024, 960, 1420, 1420, 300, 11, 0.85, SUMI, 0.5)
    b.halo(LITE, 1024, 1010, 62, 0.30, 22)
    b.fill(SUMI, [(FX0 - 300, 250), (700, 206), (1400, 232), (FX1 + 300, 196),
                  (FX1 + 300, 320), (1400, 356), (700, 326), (FX0 - 300, 370)], 0.97, 0.35)
    b.flecks(SUMI, 60, W / 2, 860, 620, 300, 4, 13, 0.40)
    seal(b, 1720, 440, 140, "淵")


BOARDS = {   # fn, sheet tone (re-pitched to haiiro), accent, grain, mist
    "bamboo":    (bamboo,     (0.949, 0.926, 0.858), MOSS  , 1.00, 1.05),
    "rooftops":  (rooftops,   (0.910, 0.902, 0.882), VERM  , 1.00, 0.95),
    "roof":      (rooftemple, (0.902, 0.902, 0.894), INDIGO, 1.00, 1.10),
    "hall":      (hall,       (0.945, 0.906, 0.835), VERM  , 1.00, 0.70),
    "drowned":   (drowned,    (0.906, 0.918, 0.910), VERM  , 1.00, 1.30),
    "village":   (village,    (0.929, 0.894, 0.851), EMBER , 1.15, 0.85),
    "warrant":   (warrant,    (0.914, 0.902, 0.867), VERM  , 1.00, 0.80),
    "snow":      (snow,       (0.953, 0.957, 0.953), VERM  , 0.75, 1.20),
    "keep":      (keep,       (0.937, 0.894, 0.835), EMBER , 1.10, 0.60),
    "tollgate":  (tollgate,   (0.906, 0.906, 0.898), OCHRE , 1.00, 0.95),
    "temple":    (temple,     (0.945, 0.914, 0.843), OCHRE , 1.00, 0.85),
    "volcano":   (volcano,    (0.922, 0.882, 0.835), EMBER , 1.10, 0.55),
    "lantern":   (lantern,    (0.933, 0.902, 0.827), OCHRE , 1.00, 0.75),
    "abyss":     (abyss,      (0.859, 0.851, 0.859), INDIGO, 1.20, 1.15),
}
SEEDS = {k: 4700 + i * 97 for i, k in enumerate(BOARDS)}
ACC_TONE = 0.95            # accents dim with the sheet, but less than it does
LITE_TONE = 1.00           # the highlights (snow, a light shaft) hold their value


def paint(bid):
    fn, tone, accent, grain, haze = BOARDS[bid]
    if RUBBING:
        # TAKUHON. The sheet is the ink and the strokes are the stone showing
        # through, so sumi and paper trade places. The accent stays where it is —
        # vermillion on black is the one thing that gets BRIGHTER in this mode.
        b = Board(SEEDS[bid], tuple(c * 0.115 for c in tone), grain)
        fn(b)
        mist(b, haze)
        return b, [(WASH, tuple(c * 0.42 for c in tone), 0.10),
                   (SUMI, tuple(c * 0.92 for c in tone), 0.30),
                   (ACC,  tuple(min(1.0, c * 1.25) for c in accent), 0.26),
                   (LITE, (0.996, 0.988, 0.965), 0.14),
                   (SEAL, tuple(min(1.0, c * 1.30) for c in VERM), 0.08)]
    b = Board(SEEDS[bid], tone, grain)
    fn(b)
    mist(b, haze)
    return b, [(WASH, tuple(c * TONE for c in (0.184, 0.192, 0.212)), 0.10),
               (SUMI, (0.055, 0.052, 0.062), 0.30),
               (ACC,  tuple(c * ACC_TONE for c in accent), 0.26),
               (LITE, tuple(c * LITE_TONE for c in (0.996, 0.988, 0.965)), 0.14),
               (SEAL, tuple(c * ACC_TONE for c in VERM), 0.08)]


def main(ids):
    OUT.mkdir(parents=True, exist_ok=True)
    for bid in ids:
        b, order = paint(bid)
        p = OUT / f"{bid}-far.png"
        b.save(p, order)
        print(f"  {bid:9s} -> {p}  {p.stat().st_size // 1024} KB")


def selfcheck():
    """The one thing that has actually gone wrong here: ink escaping the shape.
    The first fill() added its edge noise EVERYWHERE, so any pixel whose paper
    tooth was high took ink — a thousand px from the shape — and peppered all
    fourteen sheets. Run: python3 tools/stages/shodo.py --selfcheck"""
    b = Board(1)
    b.fill(SUMI, [(900, 700), (1150, 700), (1150, 860), (900, 860)], 1.0, 0.3)
    d = b.layers[SUMI]
    far = np.concatenate([d[:400].ravel(), d[1200:].ravel(),
                          d[:, :600].ravel(), d[:, 1500:].ravel()])
    assert far.max() < 1e-6, f"fill() leaked ink outside the shape: max {far.max():.3f}"
    assert d[780, 1020] > 0.9, "fill() did not ink its own interior"

    b2 = Board(2)
    b2.stroke(SUMI, [(400, 700), (1600, 700)], 60, 1.0, prof=(1, 1, 1), dry=0.0)
    e = b2.layers[SUMI]
    assert e[:640].max() < 1e-6 and e[760:].max() < 1e-6, \
        "stroke() inked well outside its own width"
    assert e[700, 1000] > 0.9, "stroke() did not ink its own spine"

    # G is where the boards put their ground; GROUND is the `anchor` written
    # into every STAGES entry. If they drift, every board floats off the floor.
    assert abs(H * GROUND - G) < 2, f"anchor {GROUND} puts the ground at {H * GROUND}, not {G}"
    print("selfcheck ok — no leak, no stray ink, ground line lands on", G)


if __name__ == "__main__":
    if "--selfcheck" in sys.argv:
        selfcheck()
        raise SystemExit
    ids = sys.argv[1:] or list(BOARDS)
    bad = [i for i in ids if i not in BOARDS]
    if bad:
        sys.exit(f"unknown board(s): {bad}\nknown: {list(BOARDS)}")
    main(ids)
