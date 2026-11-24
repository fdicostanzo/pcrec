#!/usr/bin/env python3
# plants.py ROOT : every G2 plant keyed window.c@@ / presence.c@@ in the G2 runners, with the
# first line of its FROM text in that file (0 = stale: matches no line).
import re, sys, os
root = sys.argv[1]
files = ['memfn/tests/run_g2_win.sh', 'memfn/tests/run_g2_pres.sh', 'tests/memfn/run_proof.sh']
src = {f: open(os.path.join(root, 'memfn/src', f)).read() for f in ('window.c', 'presence.c')}
for rf in files:
    lines = open(os.path.join(root, rf)).read().split('\n')
    label = '?'
    for i, l in enumerate(lines, 1):
        m = re.match(r'\s*([A-Za-z0-9_|-]+)\)\s*$', l) or re.match(r'\s*([A-Za-z0-9_|-]+)\)', l)
        if m: label = m.group(1)
        for m in re.finditer(r'(window|presence)\.c@@(.*?)@@', l):
            f = m.group(1) + '.c'
            frm = m.group(2).replace('\\&', '&').replace('\\n', '\n').replace("'\"'\"'", "'").replace('\\\\', '\\')
            k = src[f].find(frm)
            ln = src[f][:k].count('\n') + 1 if k >= 0 else 0
            print(f'{rf}:{i}\t{label}\t{f}\t{ln}')
