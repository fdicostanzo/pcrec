#!/usr/bin/env python3
# unused.py DIR FILE.c.. : every file-static function/table/object of each FILE (in DIR) that its
# own file never names outside its definition (comments and strings blanked). gcc's
# -Wunused-function / -Wunused-const-variable fire in a real compile but NOT under
# -fsyntax-only (probed with gcc-16 16.2.0: a defined, unused static function passes
# `-Wall -Werror -fsyntax-only`), so this is syncheck.sh's stand-in for that half of `make
# strict`: a static the cut left behind its callers. Prints `UNUSED file name`; exit 1 iff any.
import os, re, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from ents import entities

d = sys.argv[1]; bad = 0
for f in sys.argv[2:]:
    ents, L = entities(os.path.join(d, f))
    for k, nm, a, b, s in ents:
        if not s or k not in ('fn', 'table', 'obj', 'inst'): continue
        rx = re.compile(r'(?<![\w.])' + re.escape(nm) + r'(?!\w)')
        n = sum(len(rx.findall(L[i])) for i in range(len(L)) if not (a - 1 <= i <= b - 1))
        if n == 0:
            print(f'UNUSED {f} {nm}'); bad = 1
sys.exit(bad)
