#!/usr/bin/env python3
# kitgraph.py SRC SPEC : the kit's file-level call graph AFTER the cut (function bodies only; a name a
# function body uses that another file defines non-static), then its cycles. Split files per SPEC.
import re, sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from ents import entities
src, spec = sys.argv[1], sys.argv[2]
rng = {}
for l in open(spec):
    l = l.split('#')[0].strip()
    if not l: continue
    lhs, rhs = l.split('<-'); p = rhs.split()
    for r in p[1:]: rng.setdefault(p[0], []).append((r, lhs.strip()))
def home(sf, e):
    for r, f in rng.get(sf, []):
        if r.startswith('ent:'):
            if r[4:] == e[1]: return f
        else:
            a, b = map(int, r.split('-'))
            if a <= e[2] <= b: return f
    return sf
ID = re.compile(r'(?<![A-Za-z0-9_])([A-Za-z_][A-Za-z0-9_]*)')
defs = {}; bodies = []; local = {}
split = set(rng)
for fn in sorted(os.listdir(src)):
    if not fn.endswith('.c'): continue
    ents, L = entities(os.path.join(src, fn))
    for e in ents:
        k, nm, a, b, s = e
        if k in ('fn', 'table', 'obj', 'inst'):
            f = home(fn, e)
            # a split source's statics are visible across its new files (they lose `static`)
            if not s or fn in split: defs.setdefault(nm, set()).add(f)
            local.setdefault(fn, set()).add(nm)
            if k == 'fn':
                ids = set()
                for i in range(a, b + 1):
                    t = re.sub(r'(->|\.)\s*[A-Za-z_]\w*', ' ', L[i - 1])
                    ids.update(m.group(1) for m in ID.finditer(t))
                bodies.append((f, fn, ids))
E = {}
for f, fn, ids in bodies:
    for n in ids:
        if fn not in split and n in local.get(fn, ()): continue
        for g in defs.get(n, ()):
            if g != f and not (fn not in split and n not in defs): E.setdefault(f, {}).setdefault(g, set()).add(n)
# statics of unsplit files with a same name in a split file are not edges: keep only names the
# definer exports or that the split made cross
def real(f, g, n):
    return True
drop = set(os.environ.get('DROP', '').split())
E = {a: {b: v for b, v in bs.items() if b not in drop} for a, bs in E.items() if a not in drop}
nodes = sorted(set(E) | {g for v in E.values() for g in v})
idx, low, st, on, sccs, c = {}, {}, [], set(), [], [0]
sys.setrecursionlimit(10000)
def sc(v):
    idx[v] = low[v] = c[0]; c[0] += 1; st.append(v); on.add(v)
    for w in E.get(v, {}):
        if w not in idx: sc(w); low[v] = min(low[v], low[w])
        elif w in on: low[v] = min(low[v], idx[w])
    if low[v] == idx[v]:
        comp = []
        while True:
            w = st.pop(); on.discard(w); comp.append(w)
            if w == v: break
        sccs.append(comp)
for v in nodes:
    if v not in idx: sc(v)
drop = set(os.environ.get('DROP', '').split())
want = [a for a in sys.argv[3:]] or None
for comp in sccs:
    if len(comp) > 1:
        print('CYCLE: ' + ' '.join(sorted(comp)))
        for a in sorted(comp):
            for b in sorted(E.get(a, {})):
                if b in comp: print(f'   {a} -> {b}: {" ".join(sorted(E[a][b])[:10])}')
if want:
    for a in want:
        print(a, '->', ', '.join(f'{b}({len(v)})' for b, v in sorted(E.get(a, {}).items())))
