#!/usr/bin/env python3
"""Targeted micro-scrub for visual-gate defects.

Removes:
- tiny residue ticks / specks around the silhouette edges
- duplicate staff / blade artifacts by keeping only the largest staff-colored blob
- soft gray ground shadows in the bottom region
- small edge blobs left over from prior scrubs

Usage:
    python3 tools/sprites/micro_scrub.py <input-dir> <output-dir>
"""
import os
import sys

import numpy as np
from PIL import Image

WHITE_THRESHOLD = 245
TICK_MAX_PX = 120            # residue ticks are tiny
SHADOW_MAX_BRIGHTNESS = 180  # soft gray shadows
SHADOW_MIN_Y_PCT = 0.72      # only bottom 28% of canvas
STAFF_MIN_BRIGHTNESS = 60
STAFF_MAX_BRIGHTNESS = 180
STAFF_MIN_SATURATION = 20    # brown has some saturation


def connected_components(mask):
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


def scrub_frame(path):
    img = Image.open(path).convert("RGBA")
    arr = np.array(img).astype(np.float32)
    h, w = arr.shape[:2]

    # Non-white mask
    nonwhite = np.any(arr[:, :, :3] < WHITE_THRESHOLD, axis=2)

    # 1. Remove tiny residue ticks / specks from silhouette edges
    labels, n = connected_components(nonwhite)
    sizes = np.bincount(labels.ravel())
    sizes[0] = 0
    main_label = int(np.argmax(sizes))
    main_mask = labels == main_label

    for lbl in range(1, n + 1):
        if lbl == main_label:
            continue
        area = int(sizes[lbl])
        if area <= TICK_MAX_PX:
            arr[labels == lbl] = [255, 255, 255, 255]

    # Recompute after tick removal
    nonwhite = np.any(arr[:, :, :3] < WHITE_THRESHOLD, axis=2)

    # 2. Remove soft gray ground shadows in bottom region
    gray = np.all(arr[:, :, :3] < SHADOW_MAX_BRIGHTNESS, axis=2) & np.all(arr[:, :, :3] > 40, axis=2)
    saturation = np.ptp(arr[:, :, :3], axis=2)  # max - min across RGB
    gray &= saturation < 25
    gray &= np.indices((h, w))[0] > h * SHADOW_MIN_Y_PCT
    # Only remove gray that is not part of the main body silhouette
    # (ground shadows are separate low components)
    labels, _ = connected_components(gray)
    sizes = np.bincount(labels.ravel())
    for lbl in range(1, len(sizes)):
        if 20 < sizes[lbl] < 8000:  # shadow-sized
            arr[labels == lbl] = [255, 255, 255, 255]

    # 3. Remove duplicate staff-colored blobs (keep largest)
    # brown/tan staff color range
    brightness = np.mean(arr[:, :, :3], axis=2)
    saturation = np.ptp(arr[:, :, :3], axis=2)
    staff_color = (brightness > STAFF_MIN_BRIGHTNESS) & (brightness < STAFF_MAX_BRIGHTNESS) & (saturation > STAFF_MIN_SATURATION)
    # Exclude very dark body / very bright eyes
    staff_color &= arr[:, :, 0] > arr[:, :, 2] * 0.8  # R and G dominate over B for brown
    staff_color &= arr[:, :, 1] > arr[:, :, 2] * 0.7
    staff_color &= arr[:, :, 0] < 200
    staff_color &= arr[:, :, 1] < 170

    labels, n = connected_components(staff_color)
    sizes = np.bincount(labels.ravel())
    if n > 1 and sizes.max() > 0:
        largest_staff = int(np.argmax(sizes[1:])) + 1
        for lbl in range(1, n + 1):
            if lbl != largest_staff and sizes[lbl] > 80:
                # Only erase if it's staff-colored and detached from main body
                comp_mask = labels == lbl
                # Check if it overlaps main silhouette
                overlap = comp_mask & nonwhite
                if overlap.sum() / comp_mask.sum() < 0.9:  # mostly detached artifact
                    arr[comp_mask] = [255, 255, 255, 255]

    return Image.fromarray(arr.astype(np.uint8)), True


def main():
    if len(sys.argv) != 3:
        print(__doc__)
        sys.exit(1)
    input_dir = sys.argv[1]
    output_dir = sys.argv[2]
    os.makedirs(output_dir, exist_ok=True)

    for fname in sorted(os.listdir(input_dir)):
        if not fname.lower().endswith(".png"):
            continue
        in_path = os.path.join(input_dir, fname)
        out_path = os.path.join(output_dir, fname)
        cleaned, _ = scrub_frame(in_path)
        cleaned.save(out_path)
        print(f"cleaned {fname}")

    print(f"\nWrote {output_dir}")


if __name__ == "__main__":
    main()
