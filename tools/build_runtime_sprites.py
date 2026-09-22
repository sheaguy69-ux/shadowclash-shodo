#!/usr/bin/env python3
"""Pack lossless runtime pages without modifying any authored sprite sheet.

The authored sheets are single rows hundreds of thousands of pixels wide. Chrome
repeatedly decodes the largest rows during synchronous Canvas readback. Small PNG
pages retain every nontransparent source pixel and original cell coordinates,
while avoiding that large-image decode path. This is packaging, not art editing.

Run normally to build, or with --check to verify existing pages against sources.
The check reconstructs every cell and compares alpha plus every visible RGBA
pixel. RGB under alpha zero is immaterial to Canvas and is intentionally omitted.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path

import numpy as np
from PIL import Image

Image.MAX_IMAGE_PIXELS = None
ROOT = Path(__file__).resolve().parents[1]
FIGHTERS = ('executioner', 'mizu', 'shin', 'tsubasa', 'ember', 'kael', 'mokurai', 'exile')
PAGE_SIZE = 2048
BORDER = 1


def sha256(path: Path) -> str:
    with path.open('rb') as f:
        return hashlib.file_digest(f, 'sha256').hexdigest()


def write_json(path: Path, value: dict) -> None:
    path.write_text(json.dumps(value, separators=(',', ':')) + '\n')


def sheet_version() -> int:
    source = (ROOT / 'web/index.html').read_text()
    match = re.search(r'\bconst\s+SHEET_V\s*=\s*[\"\']?(\d+)', source)
    if not match:
        raise ValueError('Cannot find the current SHEET_V')
    return int(match.group(1))


def read_source(name: str):
    path = ROOT / 'web/assets/sprites' / f'{name}.png'
    manifest_path = path.with_suffix('.json')
    manifest = json.loads(manifest_path.read_text())
    source_hash, manifest_hash = sha256(path), sha256(manifest_path)
    image = Image.open(path).convert('RGBA')
    if image.size != (manifest['frameW'] * manifest['cols'], manifest['frameH']):
        raise ValueError(f'{name}: source geometry does not match its manifest')
    return path, manifest_path, manifest, image, source_hash, manifest_hash


def pack(name: str, out: Path) -> None:
    path, manifest_path, source, image, source_hash, manifest_hash = read_source(name)
    fw, fh, cols = source['frameW'], source['frameH'], source['cols']
    alpha = image.getchannel('A')
    cells = [None] * cols
    unique = {}
    records = []
    for idx in range(cols):
        box = alpha.crop((idx * fw, 0, (idx + 1) * fw, fh)).getbbox()
        if box is None:
            continue
        x0, y0, x1, y1 = box
        crop = image.crop((idx * fw + x0, y0, idx * fw + x1, y1))
        identity = (crop.size, hashlib.sha256(crop.tobytes()).digest())
        record = unique.get(identity)
        if record is None:
            record = {'crop': crop, 'uses': []}
            unique[identity] = record
            records.append(record)
        record['uses'].append((idx, x0, y0))
    image.close()
    del alpha

    pages = []
    # Height-sorted shelves keep the implementation deterministic and reviewable.
    records.sort(key=lambda item: (-item['crop'].height, -item['crop'].width))
    for record in records:
        crop = record['crop']
        rw, rh = crop.width + BORDER * 2, crop.height + BORDER * 2
        if rw > PAGE_SIZE or rh > PAGE_SIZE:
            raise ValueError(f'{name}: a source cell exceeds the page limit')
        candidates = []
        for page_idx, page in enumerate(pages):
            for shelf in page['shelves']:
                if rh <= shelf['h'] and shelf['x'] + rw <= PAGE_SIZE:
                    candidates.append((PAGE_SIZE - shelf['x'] - rw, page_idx, shelf))
        if candidates:
            _, page_idx, shelf = min(candidates, key=lambda item: (item[0], item[1]))
            page = pages[page_idx]
        else:
            page_idx = next((i for i, p in enumerate(pages) if p['h'] + rh <= PAGE_SIZE), len(pages))
            if page_idx == len(pages):
                pages.append({'image': Image.new('RGBA', (PAGE_SIZE, PAGE_SIZE)), 'shelves': [], 'h': 0, 'w': 0})
            page = pages[page_idx]
            shelf = {'x': 0, 'y': page['h'], 'h': rh}
            page['shelves'].append(shelf)
            page['h'] += rh
        x, y = shelf['x'] + BORDER, shelf['y'] + BORDER
        page['image'].paste(crop, (x, y))  # no mask: preserve original alpha exactly
        shelf['x'] += rw
        page['w'] = max(page['w'], shelf['x'])
        for idx, ox, oy in record['uses']:
            cells[idx] = [page_idx, x, y, crop.width, crop.height, ox, oy]
        crop.close()

    out.mkdir(parents=True, exist_ok=True)
    filenames = []
    for idx, page in enumerate(pages):
        filename = f'{name}-{source_hash[:16]}-{idx}.png'
        page['image'].crop((0, 0, page['w'], page['h'])).save(out / filename, compress_level=6)
        page['image'].close()
        filenames.append(filename)
    write_json(out / f'{name}.json', {
        'version': 1,
        'sourceSHA256': source_hash,
        'sourceManifestSHA256': manifest_hash,
        'sourceManifest': source,
        'frameW': fw, 'frameH': fh, 'cols': cols,
        'pages': filenames,
        'cells': cells,
    })
    if sha256(path) != source_hash or sha256(manifest_path) != manifest_hash:
        raise ValueError(f'{name}: source changed while pages were being built')


def check(name: str, out: Path) -> dict:
    path, manifest_path, source, image, source_hash, manifest_hash = read_source(name)
    packed = json.loads((out / f'{name}.json').read_text())
    assert packed['version'] == 1, f'{name}: unsupported runtime format'
    assert packed['sourceSHA256'] == source_hash, f'{name}: source PNG has changed'
    assert packed['sourceManifestSHA256'] == manifest_hash, f'{name}: source manifest has changed'
    assert packed['sourceManifest'] == source, f'{name}: source metadata differs'
    fw, fh, cols = source['frameW'], source['frameH'], source['cols']
    assert (packed['frameW'], packed['frameH'], packed['cols']) == (fw, fh, cols)
    assert len(packed['cells']) == cols, f'{name}: missing runtime cells'
    pages = [Image.open(out / filename).convert('RGBA') for filename in packed['pages']]
    assert all(0 < p.width <= PAGE_SIZE and 0 < p.height <= PAGE_SIZE for p in pages)
    for idx, cell in enumerate(packed['cells']):
        restored = Image.new('RGBA', (fw, fh))
        if cell is not None:
            pi, x, y, w, h, ox, oy = cell
            assert 0 <= pi < len(pages) and w > 0 and h > 0
            page = pages[pi]
            assert BORDER <= x and BORDER <= y and x + w + BORDER <= page.width and y + h + BORDER <= page.height
            assert 0 <= ox and 0 <= oy and ox + w <= fw and oy + h <= fh
            border = page.getchannel('A').crop((x - BORDER, y - BORDER, x + w + BORDER, y + h + BORDER))
            border.paste(0, (BORDER, BORDER, BORDER + w, BORDER + h))
            assert border.getbbox() is None, f'{name} cell {idx}: nontransparent padding'
            restored.paste(page.crop((x, y, x + w, y + h)), (ox, oy))
        expected = np.asarray(image.crop((idx * fw, 0, (idx + 1) * fw, fh)))
        actual = np.asarray(restored)
        assert np.array_equal(expected[:, :, 3], actual[:, :, 3]), f'{name} cell {idx}: alpha differs'
        visible = expected[:, :, 3] != 0
        assert np.array_equal(expected[visible], actual[visible]), f'{name} cell {idx}: visible pixels differ'
    stats = {
        'fighter': name, 'cells': cols, 'pages': len(pages),
        'sourceBytes': path.stat().st_size,
        'runtimeBytes': sum((out / filename).stat().st_size for filename in packed['pages']) + (out / f'{name}.json').stat().st_size,
        'sourceDecodedBytes': image.width * image.height * 4,
        'runtimeDecodedBytes': sum(p.width * p.height * 4 for p in pages),
        'identicalVisiblePixels': True,
    }
    image.close()
    for page in pages:
        page.close()
    assert sha256(path) == source_hash and sha256(manifest_path) == manifest_hash, f'{name}: source changed during verification'
    return stats


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check', action='store_true', help='Verify existing pages without writing anything')
    parser.add_argument('--fighter', choices=FIGHTERS, action='append', help='Build/check only this fighter (repeatable)')
    parser.add_argument('--out', type=Path, default=ROOT / 'web/assets/runtime-sprites')
    args = parser.parse_args()
    fighters = args.fighter or FIGHTERS
    stats = []
    for name in fighters:
        if not args.check:
            pack(name, args.out)
        report = check(name, args.out)
        stats.append(report)
        print(json.dumps(report), flush=True)
    if not args.check:
        index_path = args.out / 'index.json'
        previous = json.loads(index_path.read_text()).get('fighters', {}) if index_path.exists() else {}
        index = {'sheetVersion': sheet_version(), 'fighters': {}}
        # A scoped rebuild must not bless another fighter's stale pages with a
        # newer SHEET_V. Retain old entries only while BOTH source hashes match.
        for name in set(previous) | set(fighters):
            if name not in FIGHTERS:
                continue
            packed_path = args.out / f'{name}.json'
            if not packed_path.exists():
                continue
            packed = json.loads(packed_path.read_text())
            source_path = ROOT / 'web/assets/sprites' / f'{name}.png'
            if (packed.get('sourceSHA256') == sha256(source_path)
                    and packed.get('sourceManifestSHA256') == sha256(source_path.with_suffix('.json'))):
                index['fighters'][name] = f'{name}.json'
        index['fighters'] = {name: index['fighters'][name] for name in FIGHTERS if name in index['fighters']}
        write_json(index_path, index)
    else:
        index = json.loads((args.out / 'index.json').read_text())
        assert index['sheetVersion'] == sheet_version(), 'Runtime index uses a stale SHEET_V'
        assert all(index['fighters'].get(name) == f'{name}.json' for name in fighters)
    totals = {key: sum(s[key] for s in stats) for key in ('cells', 'pages', 'sourceBytes', 'runtimeBytes', 'sourceDecodedBytes', 'runtimeDecodedBytes')}
    print(json.dumps({'total': totals}), flush=True)


if __name__ == '__main__':
    main()
