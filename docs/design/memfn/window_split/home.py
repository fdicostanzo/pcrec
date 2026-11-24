#!/usr/bin/env python3
# home.py SRC SPEC NAME... : the new file of each window.c / presence.c top-level name (by its definition's first line).
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from ents import entities
src, spec = sys.argv[1], sys.argv[2]
rng = {}
for l in open(spec):
    l = l.split('#')[0].strip()
    if not l: continue
    lhs, rhs = l.split('<-'); p = rhs.split()
    for r in p[1:]:
        rng.setdefault(p[0], []).append((r, lhs.strip()))
def home(sf, e):
    for r, f in rng.get(sf, []):
        if r.startswith('ent:'):
            if r[4:] == e[1]: return f
        else:
            a, b = map(int, r.split('-'))
            if a <= e[2] <= b: return f
    return sf
defs = {}
for sf in ('window.c', 'presence.c'):
    for e in entities(os.path.join(src, sf))[0]:
        if e[0] != 'proto': defs.setdefault(e[1], (sf, e))
for line in sys.stdin:
    n = line.strip()
    base = n.split(':')[0]
    if base in defs: print(f'{n}\t{defs[base][0]}\t{home(*defs[base])}')
    else: print(f'{n}\t?\t?')
