#!/usr/bin/env python3
"""Head-to-head compile-TIME comparison of two pcrec binaries over a pattern list.

Usage: timecmp.py <base-binary> <proto-binary> <patterns-file> [reps]

Each pattern is compiled `reps` times with each binary, ALTERNATING between
them so a machine that drifts warmer or busier during the run drifts under
both arms equally; the reported figure is the MINIMUM of the reps, which is
the standard estimator for "how long does this work take" under noise that can
only add time. Output is TSV; the last stderr line is the aggregate.

A pattern either binary refuses is dropped from BOTH arms and counted, so the
totals compare the same denominator.
"""
import os
import subprocess
import sys
import time

base, proto, patfile = sys.argv[1], sys.argv[2], sys.argv[3]
reps = int(sys.argv[4]) if len(sys.argv) > 4 else 5

pats = [l.rstrip("\n") for l in open(patfile, errors="replace") if l.strip()]
env = dict(os.environ)
env.pop("PCREC_K18_STATS", None)


def once(binary, p):
    t0 = time.perf_counter()
    r = subprocess.run([binary, "-o", "-", "--", p],
                       capture_output=True, env=env, timeout=120)
    return time.perf_counter() - t0, r.returncode, r.stdout


print("pattern\tbase_s\tproto_s\tratio\tsame_output")
dropped = 0
tb_tot = tp_tot = 0.0
worst = []
for p in pats:
    tb = tp = None
    ob = op = None
    bad = False
    for _ in range(reps):
        d, rc, out = once(base, p)
        if rc != 0:
            bad = True
            break
        tb = d if tb is None else min(tb, d)
        ob = out
        d, rc, out = once(proto, p)
        if rc != 0:
            bad = True
            break
        tp = d if tp is None else min(tp, d)
        op = out
    if bad:
        dropped += 1
        continue
    tb_tot += tb
    tp_tot += tp
    ratio = tp / tb if tb else 0.0
    print("%s\t%.5f\t%.5f\t%.3f\t%d" % (p.replace("\t", "\\t"), tb, tp, ratio,
                                        1 if ob == op else 0))
    worst.append((ratio, tb, tp, p))

worst.sort(reverse=True)
print("TOTAL base=%.3fs proto=%.3fs ratio=%.3f  compared=%d dropped=%d"
      % (tb_tot, tp_tot, tp_tot / tb_tot if tb_tot else 0,
         len(worst), dropped), file=sys.stderr)
for r, tb, tp, p in worst[:10]:
    print("  worst ratio=%.2f base=%.4f proto=%.4f  %s" % (r, tb, tp, p[:70]),
          file=sys.stderr)
