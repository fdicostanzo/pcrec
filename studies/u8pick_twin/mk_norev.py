#!/usr/bin/env python3
"""mk_norev.py CELL_DIR OUT_DIR WIDTH -- hand-twin of the `-e byte` artifact (pa.c):
the reverse-pass start recovery is replaced by `start = end - WIDTH`, valid
only because the pattern is ONE fixed-width literal.  Everything else (pb.c,
pc.c, pd.c, lit.bin) is copied unchanged, so the driver's arm A is the twin and
arm B the unmodified `-e utf8` artifact: answer identity is checked in-process."""
import re, shutil, sys, os
src, out, w = sys.argv[1], sys.argv[2], int(sys.argv[3])
os.makedirs(out, exist_ok=True)
for f in os.listdir(src):
    if f.endswith(('.c', '.h', '.bin')): shutil.copy(os.path.join(src, f), out)
t = open(os.path.join(src, 'pa.c')).read()
pat = re.compile(r'size_t match_start_position = \(size_t\)-1;.*?if \(match_start_position == \(size_t\)-1\) return 0;', re.S)
assert len(pat.findall(t)) == 1, 'search-body reverse block not unique'
t2 = pat.sub('size_t match_start_position = match_end_position - %d;   /* HAND TWIN: fixed-width literal, no reverse pass */' % w, t, count=1)
assert t2 != t
open(os.path.join(out, 'pa.c'), 'w').write(t2)
