"""The r50 anchor map (docs/dev/reviews/2026-11-18-r50-archlook/firstunit_anchors.py),
extended by lane l1build with the RM-6 and remodel-3 range groups. usage: python3 THIS DIR [base|subject]
(DIR/src/<basename> for each file, DIR/sab/ the sabotage rows).

Two range sets (review r53 F4, lane l1fix): `base` is line-numbered at the unit's base e121371b2 and
is run on a base tree; `subject` is line-numbered at lane/l1build after the r53 fixes (39981a9d1) and
is run on that tree, so the map shows each moved anchor at its NEW site. A range set read against
the other tree's lines is meaningless. Default: base."""
import sys, os, re
D = sys.argv[1]
AT = sys.argv[2] if len(sys.argv) > 2 else 'base'
assert AT in ('base', 'subject'), AT
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
# review r53 F4: the RM-6 / remodel-3 groups at the SUBJECT (lane/l1build 39981a9d1). RM6 now spans
# qp_walk too (S1190, which §14.4 names binding); RM6h the KindRow block through pcrec_never_by_row;
# REM3 anf_head (the walk left behind); REM3d ph_wmul/ph_body/ph_leaf and pcrec_ph_node. The RM1-RM5
# groups (the r50 note's ranges for req.c/facts.c/kset.c/emit_dfa.c) are NOT in the subject set:
# RM-1's 15 rows are evidenced at the subject by the anchor tripwire and their REACH tokens, and
# L3/L2 re-number their own groups when they re-run this map.
if AT == 'subject':
    ranges = {
     'RM6': ('derive.c', [(150,362)]),
     'RM6k': ('kindrow.def', [(1,101)]),
     'RM6h': ('internal.h', [(2511,2607)]),
     'REM3': ('altnf.c', [(176,228)]),
     'REM3d': ('desc.c', [(252,348)]),
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
