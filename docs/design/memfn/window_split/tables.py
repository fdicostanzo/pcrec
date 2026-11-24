#!/usr/bin/env python3
# tables.py DIR FILE.c.. : Goal 1's census (window_split.md rev 2 §1, W36). Every declared TABLE
# or OBJECT (ents.py kinds table/obj, static or not) defined at file scope in one of the FILEs,
# and every function body of the FILEs (and of window.h) that names it outside the file that
# defines it (comments and strings blanked). Prints `CROSS table deffile -> userfile:fn` and a
# last line `tables: N declared, K named in another file's function bodies`. The population is
# stated here once and is the same at both ends: run it over T's window.c (one file: 0 cross by
# construction, so T is measured over the pure-move cut by census.py instead) and over the
# assembled tip's family files.
import os, re, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from ents import entities

d = sys.argv[1]; fs = sys.argv[2:]
E = {f: entities(os.path.join(d, f)) for f in fs}
decl = {}
for f, (ents, L) in E.items():
    for k, nm, a, b, s in ents:
        if k in ('table', 'obj') and f.endswith('.c'): decl.setdefault(nm, f)
cross = set()
for f, (ents, L) in E.items():
    for k, nm, a, b, s in ents:
        if k != 'fn': continue
        body = ' '.join(L[a-1:b])
        body = re.sub(r'(->|\.)\s*\w+', ' ', body)
        for t, df in decl.items():
            if df != f and re.search(r'(?<!\w)' + re.escape(t) + r'(?!\w)', body):
                cross.add((t, df, f, nm))
for t, df, f, nm in sorted(cross): print(f'CROSS {t} {df} -> {f}:{nm}')
print(f'tables: {len(decl)} declared, {len({c[0] for c in cross})} named in another file\'s function bodies')
