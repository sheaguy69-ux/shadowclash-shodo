#!/usr/bin/env python3
"""Validate captured neutral moves and export measured contact-relative advantage.
Capture first: python3 media/neutral-combat-pass-20260908/capture.py
"""
import csv,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
SRC=ROOT/'media/roster-footsies-20260907/neutral-final-20260908'
OUT=ROOT/'media/neutral-combat-pass-20260908'

def main():
    summary=json.loads((SRC/'summary.json').read_text())
    assert summary['complete'] and not summary['source_changed']
    assert len(summary['sequences'])==162
    rows=[]
    for item in summary['sequences']:
        data=json.loads((ROOT/item['path']/'frame_breakdown.json').read_text());o=data['options'];frames=data['frames']
        active=[f for f in frames if f['hitboxes']]
        utility=o['fighter'] in [1,3] and o['move']=='special'
        assert active or utility,(o,'no active offense')
        if not utility:assert active[0]['frame_index']>=4,(o,'missing preparation')
        if o['fighter']==0:
            expected={'light':265,'heavy':261,'special':296}[o['move']]
            assert all(f['cell']==expected for f in active),(o,'damage outside contact pose')
        if o['move']=='heavy' and o['fighter'] in [2,3,4,8]:
            expected={2:[319],3:[280],4:[222],8:[674,675]}[o['fighter']]
            assert all(f['cell'] in expected for f in active),(o,'heavy impact drawing misaligned')
            assert frames[0]['cell'] not in expected,(o,'attack starts extended')
        assert not item['observation_truncated'],(o,'capture incomplete')
        contacts=[f for f in frames if f['contacts']]
        if o['scenario'] in ['hit','block'] and not utility:assert contacts and item['damage']>0,(o,'failed expected contact')
        hit=contacts[0] if contacts else None
        a_free=next((f['frame_index'] for f in frames if f['can_act'] and (not hit or f['frame_index']>=hit['frame_index'])),None)
        d_free=next((f['frame_index'] for f in frames if hit and f['frame_index']>=hit['frame_index'] and f['defender']['can_act']),None)
        if hit:assert a_free is not None and d_free is not None,(o,'readiness not observed')
        rows.append(dict(fighter=data['reference']['fighter'],move=o['move'],facing=o['facing'],scenario=o['scenario'],first_active=active[0]['frame_index'] if active else None,contact=hit['frame_index'] if hit else None,attacker_ready=a_free,defender_ready=d_free,advantage=d_free-a_free if hit else None,damage=item['damage'],frames=len(frames)))
    with (OUT/'frame-advantage.csv').open('w') as f:
        writer=csv.DictWriter(f,fieldnames=rows[0]);writer.writeheader();writer.writerows(rows)
    (OUT/'verified.json').write_text(json.dumps(rows,indent=2))
    print('PASS: 162 neutral sequences; contact poses, preparation, contacts, full recovery and frame advantage')

if __name__=='__main__':main()
