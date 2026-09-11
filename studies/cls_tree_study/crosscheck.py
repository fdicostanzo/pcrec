#!/usr/bin/env python3
"""crosscheck.py — the two implementations of the sectioning DP, compared
over the real populations.

`section.partition` (Python) and `discover.c` (C) implement the same cost
model and the same dynamic program, written separately.  The sweeps use the
C one because it is ~600x faster; this is what makes that safe.  It compares,
per (set, lam):

    the SECTION BOUNDARIES, the per-section FORM CHOICES, and the totals.

A disagreement is reported, never smoothed: the first run of this script is
what found the `BSEARCH` op-count divergence (an integer floor log2 in the C
against `math.log2` in the Python) that moved `L` at lam=16 from 28 sections
to 27.  Both were "working"; neither was wrong on its own terms; only the
comparison could see it.

`--time` additionally reports the C discovery time per set — DELIVERABLE (3)'s
number, and the one CONSTITUTIONAL CONSTRAINT 2's cache is gated on.
"""

import argparse
import os
import subprocess
import sys
import time

import clsets
import kit
import section

HERE = os.path.dirname(os.path.abspath(__file__))
EXE = os.path.join(HERE, "discover")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--population", default="k53")
    ap.add_argument("--lams", default="0,16,256")
    ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--time-reps", type=int, default=10)
    ap.add_argument("--no-tier2", action="store_true",
                    help="disable the Python-only exact cube minimizer, which "
                         "the C side does not implement (see the memo's "
                         "tier-1/tier-2 measurement)")
    ap.add_argument("--out", default=None)
    args = ap.parse_args()

    if not os.path.exists(EXE):
        sys.exit("crosscheck: %s missing — run `make discover`" % EXE)
    if args.no_tier2:
        kit.FormCubes.TIER2 = False

    pop = clsets.population(args.population)
    if args.limit:
        pop = pop[:args.limit]
    lams = [float(x) for x in args.lams.split(",")]
    ivdir = os.path.join(HERE, "build", "iv", args.population)
    os.makedirs(ivdir, exist_ok=True)

    path = args.out or os.path.join(HERE, "results",
                                    "crosscheck_%s.tsv" % args.population)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    agree = differ = 0
    with open(path, "w") as out:
        out.write("# population=%s lams=%s tier2=%s date=%s\n"
                  % (args.population, args.lams, kit.FormCubes.TIER2,
                     time.strftime("%Y-%m-%dT%H:%M:%S")))
        out.write("set\tintervals\tlam\tverdict\tpy_sections\tc_sections\t"
                  "py_rodata\tc_rodata\tc_discovery_ms\tpy_discovery_s\t"
                  "speedup\tdetail\n")
        for name, iv in pop:
            tag = "".join(c if c.isalnum() else "_" for c in name)
            ivf = os.path.join(ivdir, tag + ".iv")
            with open(ivf, "w") as f:
                for l, h in iv:
                    f.write("%x %x\n" % (l, h))
            for lam in lams:
                t0 = time.perf_counter()
                psec, pro, pops, pfo = section.partition(iv, lam)
                pyt = time.perf_counter() - t0

                csec, cro, cops, cfo = section.partition_c(iv, lam, EXE, ivf)

                ct = float("nan")
                if args.time_reps:
                    r = subprocess.run([EXE, ivf, repr(float(lam)),
                                        "--time", str(args.time_reps)],
                                       capture_output=True, text=True)
                    for ln in r.stdout.splitlines():
                        if ln.startswith("TIME "):
                            kv = dict(p.split("=", 1) for p in ln.split()[1:])
                            ct = float(kv["per_call_ms"])

                same = (psec == csec and pfo == cfo)
                detail = ""
                if not same:
                    if psec != csec:
                        detail = "boundaries differ first at %s" % next(
                            (str(z) for z in range(min(len(psec), len(csec)))
                             if psec[z] != csec[z]), "length")
                    else:
                        detail = "forms differ: %s vs %s" % (
                            next(f for f, g in zip(pfo, cfo) if f != g),
                            next(g for f, g in zip(pfo, cfo) if f != g))
                    differ += 1
                else:
                    agree += 1
                out.write("%s\t%d\t%g\t%s\t%d\t%d\t%d\t%d\t%.4f\t%.4f\t"
                          "%.0f\t%s\n"
                          % (name, len(iv), lam, "AGREE" if same else "DIFFER",
                             len(psec), len(csec), pro, cro, ct, pyt,
                             (pyt * 1000.0 / ct) if ct == ct and ct > 0 else 0,
                             detail))
                out.flush()
    print("wrote %s: AGREE=%d DIFFER=%d" % (path, agree, differ))
    return 1 if differ else 0


if __name__ == "__main__":
    sys.exit(main())
