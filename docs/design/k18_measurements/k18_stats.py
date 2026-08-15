#!/usr/bin/env python3
"""Run a prototype binary over a pattern list and collect its K18STATS lines.

Usage: k18_stats.py <pcrec-binary> <patterns-file> [--engine=dfa] > stats.tsv

Emits one TSV row per pattern that compiled, with the counters the prototype
prints on stderr under PCREC_K18_STATS=1, plus wall time for the compile.
Patterns pcrec refuses (unimplemented modules, caps) are counted and reported
on stderr, never silently dropped: a measurement whose denominator is unknown
is not a measurement.
"""
import os
import re
import subprocess
import sys
import time

binary = sys.argv[1]
patfile = sys.argv[2]
extra = sys.argv[3:]

pats = [l.rstrip("\n") for l in open(patfile, errors="replace") if l.strip()]

env = dict(os.environ, PCREC_K18_STATS="1")
rx = re.compile(r"K18STATS (.*)")

cols = ["nfa", "dfa", "closures", "visits", "expansions",
        "redirects", "nonstacktop", "maxdepth", "ctxs"]
print("\t".join(["pattern", "secs"] + cols))

refused = 0
nostats = 0
for p in pats:
    t0 = time.time()
    try:
        r = subprocess.run([binary, "-o", "-"] + extra + ["--", p],
                           capture_output=True, env=env, timeout=60)
    except subprocess.TimeoutExpired:
        print("TIMEOUT\t%s" % p, file=sys.stderr)
        continue
    dt = time.time() - t0
    if r.returncode != 0:
        refused += 1
        continue
    # A pattern can build TWO machines (forward + the D7 reverse one); the
    # prototype zeroes its counters per build, so counters are SUMMED and
    # ceilings (maxdepth, ctxs) are MAXed across the builds.
    agg = {}
    nlines = 0
    for line in r.stderr.decode(errors="replace").splitlines():
        mm = rx.search(line)
        if not mm:
            continue
        nlines += 1
        kv = dict(x.split("=", 1) for x in mm.group(1).split())
        for c in cols:
            v = int(kv.get(c, 0))
            if c in ("maxdepth", "ctxs", "nfa", "dfa"):
                agg[c] = max(agg.get(c, 0), v)
            else:
                agg[c] = agg.get(c, 0) + v
    if not nlines:
        nostats += 1
        continue
    print("\t".join([p.replace("\t", "\\t"), "%.4f" % dt] +
                    [str(agg.get(c, 0)) for c in cols]))

print("patterns=%d refused=%d nostats=%d" % (len(pats), refused, nostats),
      file=sys.stderr)
