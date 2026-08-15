#!/usr/bin/env python3
"""Drop patterns whose python-`re` oracle backtracks catastrophically."""
import re as _re, sys, multiprocessing as mp
from itertools import product
patfile, alpha, maxlen, budget = sys.argv[1], sys.argv[2], int(sys.argv[3]), float(sys.argv[4])
subj = [""]
for n in range(1, maxlen+1):
    subj += ["".join(t) for t in product(alpha, repeat=n)]
def work(p, q):
    try:
        c = _re.compile(p)
        for s in subj: c.search(s)
        q.put(True)
    except Exception:
        q.put(False)
if __name__ == "__main__":
    pats = [l.rstrip("\n") for l in open(patfile) if l.strip()]
    keep = []
    for p in pats:
        q = mp.Queue(); pr = mp.Process(target=work, args=(p, q)); pr.start(); pr.join(budget)
        if pr.is_alive(): pr.terminate(); pr.join(); continue
        try:
            if q.get_nowait(): keep.append(p)
        except Exception: pass
    sys.stderr.write("kept %d of %d\n" % (len(keep), len(pats)))
    print("\n".join(keep))
