#!/usr/bin/env python3
"""Reject incomplete authoring data before runtime/visual review; stdlib only."""
import copy
import json
import math
import re
from pathlib import Path


def validate(data):
    ids = set()
    for move in data['moves']:
        assert move['move_id'] not in ids, 'duplicate move'
        ids.add(move['move_id'])
        timing, frames = move['timing'], move['frames']
        assert all(type(timing[k]) is int and timing[k] > 0 for k in ('startup', 'active', 'recovery'))
        assert sum(timing.values()) == move['total_frames'] == len(frames), 'missing exposures'
        assert move['frame_rate'] == 60
        props = move['properties']
        for key in ('cancel_window_on_hit', 'invulnerable_frames', 'self_velocity_frames'):
            assert all(type(n) is int and 1 <= n <= len(frames) for n in props.get(key, []))
        for i, frame in enumerate(frames, 1):
            assert frame['frame_index'] == i, 'gapped/duplicate frame indices'
            phase = 'STARTUP' if i <= timing['startup'] else 'ACTIVE' if i <= timing['startup'] + timing['active'] else 'RECOVERY'
            assert frame['phase'] == phase, 'phase disagrees with timing'
            assert (frame['hitbox'] is not None) == (phase == 'ACTIVE'), 'phantom/missing hitbox'
            assert (frame['hurtbox'] is None) == (i in props.get('invulnerable_frames', [])), 'invulnerability mismatch'
            for box in (frame['hurtbox'], frame['hitbox']):
                if box is not None:
                    assert all(type(box[k]) in (int, float) and math.isfinite(box[k]) for k in ('x', 'y', 'width', 'height'))
                    assert box['width'] > 0 and box['height'] > 0, 'invalid rectangle'
        assert props['damage'] > 0 and props['hitstun_frames'] > 0
    return sum(len(m['frames']) for m in data['moves'])


if __name__ == '__main__':
    source = (Path(__file__).resolve().parents[1]/'web/index.html').read_text()
    data = json.loads(re.search(r'<script id="footsies-data" type="application/json">(.*?)</script>', source, re.S)[1])
    count = validate(data)
    # These are the actual defects in the supplied sparse authoring examples.
    for defect in ('missing', 'phantom', 'invulnerability', 'nan'):
        bad = copy.deepcopy(data)
        frames = bad['moves'][0]['frames']
        if defect == 'missing':
            frames.pop()
        elif defect == 'phantom':
            frames[-1]['hitbox'] = frames[2]['hitbox']
        elif defect == 'invulnerability':
            frames[0]['hurtbox'] = None
        else:
            frames[0]['hurtbox']['width'] = float('nan')
        try:
            validate(bad)
        except AssertionError:
            pass
        else:
            raise AssertionError(f'validator accepted {defect}')
    print(f'PASS: {len(data["moves"])} moves, {count} complete exposures; four malformed cases rejected')
