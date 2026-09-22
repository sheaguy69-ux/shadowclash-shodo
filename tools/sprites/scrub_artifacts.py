#!/usr/bin/env python3
"""Post-generation artifact scrub for sprite candidates.

Removes isolated non-body components (adjacent-cell bleed, hallucinated
shuriken, duplicate limbs, stray blades) while preserving the main character
silhouette, weapon, and garment elements.

Usage:
    python3 tools/sprites/scrub_artifacts.py <input-dir> <output-dir>
"""
import os
import sys

import numpy as np
from PIL import Image

WHITE_THRESHOLD = 240
MIN_AREA_PCT = 0.05
GAP_PCT = 2.0
EDGE_MARGIN_PX = 2


def connected_components(mask):
    """8-connected labeling via row-run union-find. Pure numpy/python."""
    h, w = mask.shape
    labels = np.zeros((h, w), dtype=np.int32)
    parent = [0]

    def find(x):
        r = x
        while parent[r] != r:
            r = parent[r]
        while parent[x] != r:
            parent[x], x = r, parent[x]
        return r

    def union(a, b):
        ra, rb = find(a), find(b)
        if ra != rb:
            if ra < rb:
                parent[rb] = ra
            else:
                parent[ra] = rb

    next_label = 1
    prev_runs = []
    for y in range(h):
        row = mask[y]
        if not row.any():
            prev_runs = []
            continue
        d = np.diff(row.astype(np.int8))
        starts = list(np.where(d == 1)[0] + 1)
        if row[0]:
            starts = [0] + starts
        ends = list(np.where(d == -1)[0] + 1)
        if row[-1]:
            ends = ends + [w]
        cur_runs = []
        for s, e in zip(starts, ends):
            lbl = next_label
            next_label += 1
            parent.append(lbl)
            labels[y, s:e] = lbl
            for ps, pe, plbl in prev_runs:
                if s <= pe and ps <= e:
                    union(lbl, plbl)
            cur_runs.append((s, e, lbl))
        prev_runs = cur_runs

    remap = np.zeros(next_label, dtype=np.int32)
    roots = {}
    nxt = 1
    for lbl in range(1, next_label):
        r = find(lbl)
        if r not in roots:
            roots[r] = nxt
            nxt += 1
        remap[lbl] = roots[r]
    out = np.zeros((h, w), dtype=np.int32)
    fg = labels > 0
    out[fg] = remap[labels[fg]]
    return out, nxt - 1


def bbox(ys, xs):
    return int(xs.min()), int(ys.min()), int(xs.max()), int(ys.max())


def _boundary(mask2d):
    e = mask2d.copy()
    e[1:, :] &= mask2d[:-1, :]
    e[:-1, :] &= mask2d[1:, :]
    e[:, 1:] &= mask2d[:, :-1]
    e[:, :-1] &= mask2d[:, 1:]
    return mask2d & ~e


def _sample_points(mask2d, cap):
    ys, xs = np.where(mask2d)
    if len(ys) == 0:
        return ys, xs
    if len(ys) > cap:
        idx = np.linspace(0, len(ys) - 1, cap).astype(int)
        ys, xs = ys[idx], xs[idx]
    return ys, xs


def gap_distance(comp_mask, main_mask, comp_bbox, h, w, search_margin, cap=600):
    cx0, cy0, cx1, cy1 = comp_bbox
    x0, x1 = max(0, cx0 - search_margin), min(w, cx1 + search_margin + 1)
    y0, y1 = max(0, cy0 - search_margin), min(h, cy1 + search_margin + 1)
    mcrop = main_mask[y0:y1, x0:x1]
    if not mcrop.any():
        return float("inf")
    fcrop = comp_mask[y0:y1, x0:x1]
    mys, mxs = _sample_points(_boundary(mcrop), cap)
    if len(mys) == 0:
        mys, mxs = _sample_points(mcrop, cap)
    fys, fxs = _sample_points(_boundary(fcrop), cap)
    if len(fys) == 0:
        fys, fxs = _sample_points(fcrop, cap)
    fpts = np.stack([fys, fxs], axis=1).astype(np.float64)
    mpts = np.stack([mys, mxs], axis=1).astype(np.float64)
    d2 = ((fpts[:, None, :] - mpts[None, :, :]) ** 2).sum(-1)
    return float(np.sqrt(d2.min()))


def scrub_frame(path):
    img = Image.open(path).convert("RGBA")
    arr = np.array(img)
    h, w = arr.shape[:2]
    mask = np.any(arr[:, :, :3] < WHITE_THRESHOLD, axis=2)
    if not mask.any():
        return img, 0

    labels, n = connected_components(mask)
    sizes = np.bincount(labels.ravel())
    sizes[0] = 0
    largest = int(np.argmax(sizes))
    lys, lxs = np.where(labels == largest)
    lx0, ly0, lx1, ly1 = bbox(lys, lxs)
    diag = ((lx1 - lx0) ** 2 + (ly1 - ly0) ** 2) ** 0.5
    gap_threshold_px = max(1, int(round(diag * GAP_PCT / 100.0)))
    main_mask = labels == largest
    search_margin = gap_threshold_px + 40

    image_area = h * w
    min_area_px = image_area * MIN_AREA_PCT / 100.0

    removed = 0
    for lbl in range(1, n + 1):
        if lbl == largest:
            continue
        area = int(sizes[lbl])
        if area < min_area_px:
            continue
        comp = labels == lbl
        cys, cxs = np.where(comp)
        cx0, cy0, cx1, cy1 = bbox(cys, cxs)
        gap = gap_distance(comp, main_mask, (cx0, cy0, cx1, cy1), h, w, search_margin)
        if gap > gap_threshold_px:
            arr[comp] = [255, 255, 255, 255]
            removed += 1

    return Image.fromarray(arr), removed


def main():
    if len(sys.argv) != 3:
        print(__doc__)
        sys.exit(1)
    input_dir = sys.argv[1]
    output_dir = sys.argv[2]
    os.makedirs(output_dir, exist_ok=True)

    total_removed = 0
    for fname in sorted(os.listdir(input_dir)):
        if not fname.lower().endswith(".png"):
            continue
        in_path = os.path.join(input_dir, fname)
        out_path = os.path.join(output_dir, fname)
        cleaned, n = scrub_frame(in_path)
        cleaned.save(out_path)
        total_removed += n
        print(f"{fname}: removed {n} artifact(s)")

    print(f"\nWrote {output_dir}; total artifacts removed: {total_removed}")


if __name__ == "__main__":
    main()
