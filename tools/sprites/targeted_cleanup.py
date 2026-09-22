#!/usr/bin/env python3
"""Targeted manual cleanup for specific frame defects.

Usage:
    python3 tools/sprites/targeted_cleanup.py <input-dir> <output-dir>
"""
import os
import sys

import numpy as np
from PIL import Image, ImageDraw


def cleanup_run_clean3(src):
    """Erase the duplicate staff/sliver in the upper-right of run_clean3.

    The duplicate staff + its white highlight runs from the upper-right tip
    down toward the hands. Polygon bounds the whole object; main staff is
    safely to the left.
    """
    img = src.copy()
    draw = ImageDraw.Draw(img)
    poly = [
        (804, 60), (844, 10), (879, 50), (874, 150),
        (824, 280), (744, 400), (684, 380), (714, 280),
        (764, 160)
    ]
    draw.polygon(poly, fill=(255, 255, 255, 255))
    return img


def cleanup_kheel_shadow(src):
    """Erase the soft gray ground shadow under kheel's feet."""
    img = src.copy()
    draw = ImageDraw.Draw(img)
    w, h = img.size
    # Ellipse shadow under both feet, bottom-center
    draw.ellipse([w * 0.18, h * 0.82, w * 0.72, h * 0.92], fill=(255, 255, 255, 255))
    return img


TARGETS = {
    "run_clean3.png": cleanup_run_clean3,
    "kheel.png": cleanup_kheel_shadow,
}


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
        img = Image.open(in_path).convert("RGBA")
        if fname in TARGETS:
            img = TARGETS[fname](img)
            print(f"targeted cleanup: {fname}")
        else:
            print(f"copied: {fname}")
        img.save(out_path)

    print(f"\nWrote {output_dir}")


if __name__ == "__main__":
    main()
