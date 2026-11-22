#!/usr/bin/env python3
"""K159 evidence: the `width` fact, BEFORE vs AFTER, in all four cells
(byte/utf8 x default/--engine=vm), over emit_sweep.py's own corpus
population plus patterns files. Reuses emit_sweep's enumeration; compares
only the `width` row (status, value, why) of `--emit-facts=byte,utf8`.
usage: width_cells.py BASE_BIN NEW_BIN TREE [PATTERNS_FILE...]"""
import os, sys
from concurrent.futures import ThreadPoolExecutor
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "..", "..", "scripts"))
import emit_sweep as es

base, new, tree = sys.argv[1:4]
pats = es.enumerate_corpus(new, tree, 60)
for f in sys.argv[4:]:
    pats += es.read_patterns_file(f)
pats = es.distinct_patterns(pats)

def width_rows(binary, pat, engine):
    argv = [binary, "--features", "all"] + (["--engine=vm"] if engine == "vm" else [])
    argv += ["--emit-facts=byte,utf8", "--pattern", pat]
    rc, out, _ = es.run(argv, 120)
    rows = {}
    for line in out.decode("utf-8", "surrogateescape").splitlines():
        f = line.split("\t")
        if len(f) >= 8 and f[1] == "width":
            rows[f[0]] = (f[4], f[6], f[7])
    return rc, rows

def one(pat):
    res = []
    for eng in ("default", "vm"):
        ra, a = width_rows(base, pat, eng)
        rb, b = width_rows(new, pat, eng)
        res.append((eng, ra, rb, a, b))
    return pat, res

cells = derived = differ = rcdiff = 0
with ThreadPoolExecutor(12) as ex:
    for pat, res in ex.map(one, pats):
        for eng, ra, rb, a, b in res:
            if ra != rb:
                rcdiff += 1
                print(f"RC-DIFF {eng} {ra} {rb} {pat!r}")
            for enc in sorted(set(a) | set(b)):
                cells += 1
                if a.get(enc, ("",))[0] == "derived":
                    derived += 1
                if a.get(enc) != b.get(enc):
                    differ += 1
                    print(f"DIFFER {eng}/{enc} {a.get(enc)} {b.get(enc)} {pat!r}")
print(f"width_cells: DONE patterns={len(pats)} cells={cells} derived={derived} "
      f"differ={differ} rc_diff={rcdiff}")
sys.exit(1 if differ or rcdiff else 0)
