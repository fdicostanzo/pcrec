#!/usr/bin/env python3
"""build_twins.py CASE... -- write out/<case>/tw_<provider>.c for each case.

F1 cases (c1, nd, l, xwd): the machine is computed from the case's flat.c
(f1.py).  F2 cases (x1, x2, x3): hand-derived machines (f2.py).
Providers: kit4 -> prefix ia, page3w -> ib, bitmap1 -> ic.
"""
import os
import sys

import cm
import f1
import providers

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "out")
PROV = {"kit4": "ia", "page3w": "ib", "bitmap1": "ic"}


def write_case(case, fwd, rev, iv, info=None):
    d = os.path.join(OUT, case)
    os.makedirs(d, exist_ok=True)
    for kind, P in PROV.items():
        src = cm.emit(P, fwd, rev) + "\n" + providers.provider_c(kind, P, iv)
        open(os.path.join(d, "tw_%s.c" % kind), "w").write(src)
    open(os.path.join(d, "twin.info"), "w").write(repr((info, iv[:6], len(iv))) + "\n")


def build_f1(case):
    fwd, rev, iv, info = f1.build_twin(os.path.join(OUT, case, "flat.c"))
    write_case(case, fwd, rev, iv, info)
    print(case, info, "non-ASCII set: %d intervals" % len(iv))


if __name__ == "__main__":
    for c in sys.argv[1:]:
        if c in ("c1", "c3", "nd", "l", "xwd"):
            build_f1(c)
        else:
            import f2
            f2.build(c, write_case)
