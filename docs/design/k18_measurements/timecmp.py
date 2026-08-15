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

THE FLOOR IS SUBTRACTED, and it has to be. Every figure here includes one
process spawn, which is ~0.9 ms on this box; over a 622-pattern corpus that is
0.57 s of a 0.575 s total, so an un-subtracted aggregate compares the two arms'
`fork` and reports a ratio of 1.00 whatever the compilers do. The floor is
MEASURED per binary and per run (min over 15 compiles of the pattern `a`,
which does no closure work) rather than assumed, so it tracks the box it is
running on. Both totals are reported: raw, and net of the floor.

AND THE NET IS ONLY MEANINGFUL WHEN THE SIGNAL BEATS THE FLOOR'S OWN NOISE.
Subtracting a floor does not create resolution it did not have. On the 555
compiling corpus patterns the per-pattern closure work is ~0.1 ms against a
~0.9 ms spawn, and three repeated trials of the same measurement (each
against a matched null corpus of 555 compiles of `a`) gave nets of 0.089,
0.121 and -0.053 s for the shipped compiler and 0.138, -0.266 and 0.341 s for
prototype A2 -- swinging through zero and changing sign. So: use this for
patterns whose compile is milliseconds or more (the nesting ladder, the
bounded-repeat family, anything in the note's cost tables), and DO NOT use it
to price a corpus of cheap patterns. For that question the counters are the
instrument -- k18_stats.py plus inflation.py, which are exact and have a
denominator.

Do not use a shell loop with `date` for this. The design note's original cost
table read 0.12 s for every pattern that did no measurable work, including the
shipped compiler at the parser's own nesting cap; that 0.12 s was the shell
harness's own overhead, not pcrec's, and it hid a 100x prototype defect by
making everything cheap look identical (R23 S16).
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


def floor_of(binary):
    """One process spawn plus a compile that does no closure work."""
    return min(once(binary, "a")[0] for _ in range(15))


fb, fp = floor_of(base), floor_of(proto)
print("# measured per-invocation floor: base=%.2f ms proto=%.2f ms" % (fb * 1e3,
                                                                       fp * 1e3))
print("pattern\tbase_s\tproto_s\tratio\tsame_output")
dropped = 0
tb_tot = tp_tot = 0.0
nb_tot = np_tot = 0.0
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
    nb_tot += max(0.0, tb - fb)
    np_tot += max(0.0, tp - fp)
    ratio = tp / tb if tb else 0.0
    print("%s\t%.5f\t%.5f\t%.3f\t%d" % (p.replace("\t", "\\t"), tb, tp, ratio,
                                        1 if ob == op else 0))
    worst.append((ratio, tb, tp, p))

worst.sort(reverse=True)
print("TOTAL base=%.3fs proto=%.3fs ratio=%.3f  compared=%d dropped=%d"
      % (tb_tot, tp_tot, tp_tot / tb_tot if tb_tot else 0,
         len(worst), dropped), file=sys.stderr)
print("NET (floor %.2f/%.2f ms subtracted) base=%.3fs proto=%.3fs ratio=%.3f"
      % (fb * 1e3, fp * 1e3, nb_tot, np_tot,
         np_tot / nb_tot if nb_tot else 0), file=sys.stderr)
for r, tb, tp, p in worst[:10]:
    print("  worst ratio=%.2f base=%.4f proto=%.4f  %s" % (r, tb, tp, p[:70]),
          file=sys.stderr)
