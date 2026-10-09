#!/usr/bin/env python3
"""docs/design/dec_fallback/collapse_waste/timing.py -- [DEC-COLLAPSE-WASTE]
compile-time measurement (lane decattr, 2026-10-09).

For every case (variant, argv) in CASES_TSV, compile it with the PARENT and
the CHILD compiler of that variant, alternating, REPS times each, and record
each compile's user+sys CPU (RUSAGE_CHILDREN deltas; output to a scratch
file). Prints one row per case: median parent, median child, saving, ratio.
SCRATCH TIER: one box, its load uncontrolled, `taskset` set by the caller.

usage: timing.py BINMAP CASES_TSV OUTDIR [REPS]
  BINMAP: variant=PARENT_BIN,CHILD_BIN[;variant=...]
  CASES_TSV: variant<TAB>json list of the compile's own args (attempt_hist's
             census.py key rendered as argv: flags, features, encoding,
             engine, --pattern-esc and the quoted pattern; cases.py writes it)
"""
import json, os, resource, statistics, subprocess, sys


def cpu_of(argv):
    b = resource.getrusage(resource.RUSAGE_CHILDREN)
    rc = subprocess.run(argv, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL).returncode
    a = resource.getrusage(resource.RUSAGE_CHILDREN)
    return rc, (a.ru_utime - b.ru_utime) + (a.ru_stime - b.ru_stime)


def main():
    binmap = {}
    for part in sys.argv[1].split(";"):
        v, bins = part.split("=", 1)
        binmap[v] = bins.split(",")
    out = sys.argv[3]
    reps = int(sys.argv[4]) if len(sys.argv) > 4 else 9
    print("variant\tpattern\targs\tparent_s\tchild_s\tsaved_s\tratio\trc")
    tot_p = tot_c = 0.0
    for line in open(sys.argv[2], encoding="utf-8", errors="surrogateescape"):
        line = line.rstrip("\n")
        if not line or line.startswith("#"):
            continue
        v, js = line.split("\t", 1)
        cargs = json.loads(js)
        pat, extra = cargs[-1], " ".join(cargs[:-1])
        par, chi = binmap[v]
        res = {0: [], 1: []}
        rcs = set()
        for _ in range(reps):
            for i, b in enumerate((par, chi)):
                argv = [b, "-p", "rx", "-o", os.path.join(out, "t.c")] + cargs
                rc, t = cpu_of(argv)
                rcs.add(rc)
                res[i].append(t)
        p, c = statistics.median(res[0]), statistics.median(res[1])
        tot_p += p; tot_c += c
        print(f"{v}\t{pat}\t{extra}\t{p:.4f}\t{c:.4f}\t{p - c:.4f}\t{p / c if c else 0:.2f}\t"
              f"{','.join(map(str, sorted(rcs)))}", flush=True)
    print(f"#TOTAL\t\t\t{tot_p:.3f}\t{tot_c:.3f}\t{tot_p - tot_c:.3f}\t{tot_p / tot_c if tot_c else 0:.2f}")


if __name__ == "__main__":
    main()
