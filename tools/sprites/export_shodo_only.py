#!/usr/bin/env python3
"""Build character atlases containing only post-baseline Shodō cells.

The recovered game is read-only input. This standalone edition receives exact
RGBA cell copies; legacy cells, history aliases, and second-form aliases are
never copied.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import tempfile
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "web/assets/sprites"
FIGHTERS = {
    "executioner": 338,
    "kael": 226,
    "tsubasa": 321,
    "ember": 456,
    "shin": 414,
    "mizu": 281,
    "exile": 125,
    "mokurai": 221,
    "oni": 407,
}
SCALES = {
    "executioner": 0.269517,
    "kael": 0.411765,
    "tsubasa": 0.368254,
    "ember": 0.344776,
    "shin": 0.350526,
    "mizu": 0.385185,
    "exile": 0.448387,
    "mokurai": 0.485235,
    "oni": 0.568182,
}
HISTORY = re.compile(r"_v\d{3}(?:_\d+)?$|_old$")
SECOND_FORM = re.compile(r"^(?:f2_|hb|gk)")
INDEX_KEYED = ("mirror", "footAdj", "handAnchor")


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def atomic_png(image: Image.Image, path: Path) -> None:
    with tempfile.NamedTemporaryFile(dir=path.parent, suffix=".png", delete=False) as tmp:
        staged = Path(tmp.name)
    try:
        image.save(staged, optimize=True)
        reopened = Image.open(staged).convert("RGBA")
        assert reopened.size == image.size and reopened.tobytes() == image.tobytes()
        os.replace(staged, path)
    finally:
        staged.unlink(missing_ok=True)


def atomic_json(data: object, path: Path) -> None:
    with tempfile.NamedTemporaryFile("w", dir=path.parent, suffix=".json", delete=False) as tmp:
        json.dump(data, tmp, indent=1)
        tmp.write("\n")
        staged = Path(tmp.name)
    try:
        assert json.loads(staged.read_text()) == data
        os.replace(staged, path)
    finally:
        staged.unlink(missing_ok=True)


def export_fighter(source: Path, fighter: str, baseline: int) -> dict:
    src_json = source / f"{fighter}.json"
    src_png = source / f"{fighter}.png"
    manifest = json.loads(src_json.read_text())
    frames = manifest["frames"]
    live = {
        key: cell for key, cell in frames.items()
        if isinstance(cell, int)
        and cell >= baseline
        and not HISTORY.search(key)
        and not SECOND_FORM.match(key)
    }
    assert live, f"{fighter}: no Shodō cells at/after baseline {baseline}"
    keep = sorted(set(live.values()))
    remap = {old: new for new, old in enumerate(keep)}
    fw, fh = manifest["frameW"], manifest["frameH"]
    source_image = Image.open(src_png).convert("RGBA")
    assert source_image.size == (manifest["cols"] * fw, fh)
    output = Image.new("RGBA", (len(keep) * fw, fh), (0, 0, 0, 0))
    for old, new in remap.items():
        cell = source_image.crop((old * fw, 0, (old + 1) * fw, fh))
        output.paste(cell, (new * fw, 0))

    manifest["frames"] = {key: remap[cell] for key, cell in live.items()}
    manifest["cols"] = len(keep)
    manifest["scale"] = SCALES[fighter]
    for field in INDEX_KEYED:
        if field not in manifest:
            continue
        values = manifest[field]
        items = enumerate(values) if isinstance(values, list) else ((int(k), v) for k, v in values.items())
        manifest[field] = {str(remap[index]): value for index, value in items if index in remap}

    atomic_png(output, OUT / f"{fighter}.png")
    atomic_json(manifest, OUT / f"{fighter}.json")
    omitted = sorted(key for key, cell in frames.items() if isinstance(cell, int) and key not in live)
    return {
        "fighter": fighter,
        "baseline_cell": baseline,
        "source_atlas_sha256": sha256(src_png),
        "source_manifest_sha256": sha256(src_json),
        "kept_source_cells": keep,
        "runtime_aliases": sorted(live),
        "omitted_aliases": omitted,
        "output_atlas_sha256": sha256(OUT / f"{fighter}.png"),
        "output_manifest_sha256": sha256(OUT / f"{fighter}.json"),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("source", type=Path, help="source web/assets/sprites directory")
    args = parser.parse_args()
    source = args.source.resolve()
    records = [export_fighter(source, name, baseline) for name, baseline in FIGHTERS.items()]
    receipt = {
        "edition": "Shodo first form",
        "baseline_commit": "535d5f39c22a362083622d9fd9b2860a5d696a99",
        "rule": "Only referenced cells appended after the legacy baseline are copied.",
        "fighters": records,
    }
    atomic_json(receipt, ROOT / "docs/SHODO-EXPORT-MANIFEST.json")
    for record in records:
        print(f'{record["fighter"]}: {len(record["kept_source_cells"])} cells, '
              f'{len(record["runtime_aliases"])} aliases; legacy cells copied: 0')
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
