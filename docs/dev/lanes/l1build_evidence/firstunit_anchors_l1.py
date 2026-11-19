"""The r50 anchor map (docs/dev/reviews/2026-11-18-r50-archlook/firstunit_anchors.py),
extended by lane l1build with the RM-6 and remodel-3 range groups. usage: python3 THIS DIR
(DIR/src/<basename> for each file, DIR/sab/ the sabotage rows)."""
import sys, os, re
D = sys.argv[1]
ranges = {
 'RM1': ('req.c', [(530,800),(880,950)]),
 'RM2': ('facts.c', [(104,108),(345,357),(864,871)]),
 'RM2e': ('emit_dfa.c', [(8984,8992),(9080,9087),(9150,9176),(9356,9362),(1636,1645)]),
 'RM3': ('emit_dfa.c', [(1083,1134),(7909,7945)]),
 'RM4a': ('req.c', [(1278,1290),(410,425)]),
 'RM4b': ('emit_dfa.c', [(11329,11350)]),
 'RM4c': ('kset.c', [(300,340)]),
 'RM5': ('emit_dfa.c', [(3636,3645)]),
 # lane l1build (span_arms §14.4 L1): the range groups RM-6 and remodel 3 add,
 # line numbers at the unit's base e121371b2
 'RM6': ('derive.c', [(142,295)]),
 'RM6k': ('kindrow.def', [(1,81)]),
 'RM6h': ('internal.h', [(2510,2577)]),
 'REM3': ('altnf.c', [(160,250)]),
 'REM3d': ('desc.c', [(190,260)]),
}
srcs = {n: open(os.path.join(D,'src',n), encoding='utf-8', errors='replace').read().split('\n') for n in ['req.c','facts.c','kset.c','emit_dfa.c','derive.c','kindrow.def','internal.h','altnf.c','desc.c']}
def field(txt, name):
    m = re.search(r'^'+name+r"=(['\"])", txt, re.M)
    if not m: return None
    q = m.group(1); i = m.end(); out=[]
    while i < len(txt):
        c = txt[i]
        if q == "'" and txt.startswith("'\\''", i): out.append("'"); i += 4; continue
        if q == '"' and c == '\\' and i+1 < len(txt): out.append(txt[i+1]); i += 2; continue
        if c == q: break
        out.append(c); i += 1
    return ''.join(out)
res = {k: [] for k in ranges}
for fn in sorted(os.listdir(os.path.join(D,'sab'))):
    txt = open(os.path.join(D,'sab',fn), encoding='utf-8', errors='replace').read()
    sf = field(txt, 'SAB_FILE') or ''
    b = field(txt, 'SAB_BEFORE')
    if not b: continue
    base = os.path.basename(sf)
    lines = [l for l in b.split('\n') if l.strip()]
    if not lines: continue
    first = lines[0]
    for k,(n,rs) in ranges.items():
        if n != base: continue
        src = srcs[n]
        hits = [i+1 for i,l in enumerate(src) if l == first]
        for h in hits:
            last = h + len(b.split('\n')) - 1
            if any(lo <= h <= hi or lo <= last <= hi for lo,hi in rs):
                res[k].append(f"{fn.split('_')[0]}@{h}"); break
for k,v in res.items(): print(k, len(v), ' '.join(v))
