#!/usr/bin/env python3
"""Erase soft gray ground shadows from white-bg sprite candidates.

Targets disconnected, low-saturation gray blobs in the bottom portion of the
image that survive white-bg keying and would show as ground shadows in-game.

Usage:
    python3 tools/sprites/erase_ground_shadows.py <input-dir> <output-dir> <frame1> [frame2 ...]
"""
import os
import sys

import numpy as np
from PIL import Image

WHITE_THRESHOLD = 240
MIN_SHADOW_AREA = 30       # px; ignore tiny specks
BOTTOM_CROP_PCT = 0.35     # only look for shadows in bottom 35% of canvas
GRAY_MAX_SAT = 35          # RGB variance threshold for "gray"
GRAY_MAX_BRIGHT = 230      # must be darker than white
GRAY_MIN_BRIGHT = 100      # must be brighter than dark body outlines


def connected_components(mask):
    """8-connected labeling via row-run union-find."""
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


def erase_shadows(in_path, out_path):
    img = Image.open(in_path).convert("RGBA")
    arr = np.array(img)
    h, w = arr.shape[:2]

    bottom_y = int(h * (1 - BOTTOM_CROP_PCT))
    region = arr[bottom_y:, :, :3]

    brightness = region.mean(axis=2)
    variance = region.var(axis=2)
    gray_mask = (
        (brightness > GRAY_MIN_BRIGHT)
        & (brightness < GRAY_MAX_BRIGHT)
        & (variance < GRAY_MAX_SAT ** 2)
    )

    # Remove tiny isolated specks by connected-component filtering
    labels, n = connected_components(gray_mask)
    for lbl in range(1, n + 1):
        mask = labels == lbl
        if mask.sum() < MIN_SHADOW_AREA:
            gray_mask[mask] = False

    removed = int(gray_mask.sum())
    if removed:
        arr[bottom_y:, :][gray_mask] = [255, 255, 255, 255]

    Image.fromarray(arr).save(out_path)
    return removed


def main():
    if len(sys.argv) < 4:
        print(__doc__)
        sys.exit(1)
    in_dir = sys.argv[1]
    out_dir = sys.argv[2]
    frames = sys.argv[3:]
    os.makedirs(out_dir, exist_ok=True)
    total = 0
    for name in frames:
        in_path = os.path.join(in_dir, f"{name}.png")
        out_path = os.path.join(out_dir, f"{name}.png")
        if not os.path.exists(in_path):
            print(f"SKIP {name}: not found")
            continue
        removed = erase_shadows(in_path, out_path)
        print(f"{name}: removed {removed} px")
        total += removed
    print(f"Total shadow pixels removed: {total}")


if __name__ == "__main__":
    main()
