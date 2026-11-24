#!/usr/bin/env python3
# bucket.py SPEC  < "row<TAB>line" lines (window.c lines) : the new file of each line, and counts.
import sys, re
spec = sys.argv[1]; src = sys.argv[2] if len(sys.argv) > 2 else 'window.c'
rng = []
for l in open(spec):
    l = l.split('#')[0].strip()
    if not l: continue
    lhs, rhs = l.split('<-'); p = rhs.split()
    if p[0] != src: continue
    for r in p[1:]:
        if r.startswith('ent:'): continue
        a, b = r.split('-'); rng.append((int(a), int(b), lhs.strip()))
def home(n):
    for a, b, f in rng:
        if a <= n <= b: return f
    return '?'
cnt = {}
for l in sys.stdin:
    row, ln = l.rstrip('\n').split('\t')[:2]
    f = home(int(ln)); cnt.setdefault(f, []).append(row)
    print(f'{row}\t{ln}\t{f}')
for f in sorted(cnt): print(f'# {f}\t{len(cnt[f])}', file=sys.stderr)
