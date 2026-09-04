import json,re,glob,sys
AIR=re.compile(r'^(ajump|aneu|adown|air|fall|jump|xjump|bjump|xanchor|bflip|cart|dive|divecut|airthrow|kxcut|mdive|airpoke|bair|xair|mairf|kstomp|wallslide|walljump|mwall)')
def load(pat):
    out={}
    for p in sorted(glob.glob(pat)):
        raw=open(p).read().strip()
        if not raw: continue
        d=json.loads(json.loads(raw.split('AIRLOG: ',1)[1].strip()))
        bad={}
        for k,v in d['hits'].items():
            st,idx=k.split('#')
            ns=v['names'].split(',') if v['names'] else ['(orphan)']
            if any(AIR.match(n) for n in ns): continue
            bad[(st,v['names'])]=v['n']
        out[d['f']]=bad
    return out
A=load('/tmp/airlog_*.txt'); B=load('/tmp/airlog2_*.txt')
print(f"{'FIGHTER':13s} {'BEFORE':>18s} {'AFTER':>18s}")
ta=tb=0
for f in sorted(A):
    a=sum(A[f].values()); b=sum(B.get(f,{}).values()); ta+=a; tb+=b
    print(f"{f:13s} {len(A[f]):3d} rows {a:5d}f  {len(B.get(f,{})):3d} rows {b:5d}f")
print(f"{'TOTAL':13s} {'':10s}{ta:5d}f {'':10s}{tb:5d}f   ({100*(ta-tb)/ta:.1f}% gone)")
print("\nWHAT IS LEFT:")
for f in sorted(B):
    if not B[f]: print(f"  {f}: CLEAN"); continue
    for (st,nm),n in sorted(B[f].items(),key=lambda x:-x[1]):
        print(f"  {f:12s} {st:16s} {nm:30s} {n:4d}f")
