#!/usr/bin/env python3
"""run_bench.py -- ns/char of every arm, per (case, regime), on a QUIET box.

  run_bench.py [--cc gcc] [--rounds 11] [--reps 0] [--cases c1,nd,...]
               [--regimes ascii,latin1,cjk,mixed] [--out results/NAME.tsv]
               [--max-load-wait 600] [--load-threshold 0.5]

Protocol (house, studies/cls_tree_study/bench.py): all arms for all cases are
BUILT before any timing; the 1-minute load average is polled for quiet
immediately before EACH timed unit (one case x regime), for up to
--max-load-wait seconds, every reading logged; rounds interleaved, medians,
per-round range, every round's answer checksummed.  Self-contained (no
imports from other studies) so the same file runs from a bundle on the timing
box.  Reads out/<case>/{base,basec,bigcap,vm,tw_*}.c and out/subj_*.bin.
"""
import argparse
import os
import platform
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "out")

# arm name (also the C prefix) -> source file
ARMFILES = [("bb", "base.c"), ("bc", "basec.c"), ("bd", "bigcap.c"), ("bv", "vm.c"),
            ("ia", "tw_kit4.c"), ("ib", "tw_page3w.c"), ("ic", "tw_bitmap1.c")]
LABEL = {"bb": "all-byte/VM as emitted today", "bc": "null control (same source as bb, other prefix)",
         "bd": "all-byte, size cap raised", "bv": "forced VM",
         "ia": "island + kit(lambda=4)", "ib": "island + page3w", "ic": "island + bitmap1"}


def loadavg():
    try:
        return os.getloadavg()[0]
    except OSError:
        return 0.0


def wait_for_quiet(threshold, max_wait, log):
    t0 = time.time()
    while True:
        l = loadavg()
        log.append((time.time(), l))
        if l < threshold:
            return l
        if time.time() - t0 > max_wait:
            raise SystemExit("REFUSED: load1 stayed >= %.2f for %ds (last %.2f); readings: %s" %
                             (threshold, max_wait, l, ", ".join("%.2f" % x[1] for x in log[-12:])))
        time.sleep(5)


def build(case, cc):
    d = os.path.join(OUT, case)
    arms = [(a, os.path.join(d, f)) for a, f in ARMFILES if os.path.exists(os.path.join(d, f))]
    hdr = ["#include <stddef.h>", "typedef int (*sfn)(const unsigned char *, size_t, size_t, ptrdiff_t (*)[2]);"]
    for a, _ in arms:
        hdr.append("int %s_search(const unsigned char *, size_t, size_t, ptrdiff_t (*)[2]);" % a)
    hdr.append("#define NARMS %d" % len(arms))
    hdr.append("static const struct { const char *name; sfn fn; } arms[] = { %s };" %
               ", ".join('{"%s", %s_search}' % (a, a) for a, _ in arms))
    bd = os.path.join(d, "bench_build")
    os.makedirs(bd, exist_ok=True)
    open(os.path.join(bd, "arms_gen.h"), "w").write("\n".join(hdr) + "\n")
    exe = os.path.join(bd, "bench")
    cmd = [cc, "-O2", "-std=gnu11", "-w", "-I" + bd, "-I" + d, os.path.join(HERE, "bench.c")] + [p for _, p in arms] + ["-o", exe]
    subprocess.check_call(cmd)
    return exe, [a for a, _ in arms]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--cc", default=os.environ.get("CC", "gcc"))
    ap.add_argument("--rounds", type=int, default=11)
    ap.add_argument("--reps", type=int, default=0)
    ap.add_argument("--cases", default="c1,nd,l,xwd,x1,x2,x3")
    ap.add_argument("--regimes", default="ascii,latin1,cjk,mixed")
    ap.add_argument("--out", default=os.path.join(HERE, "results", "bench.tsv"))
    ap.add_argument("--max-load-wait", type=int, default=600)
    ap.add_argument("--load-threshold", type=float, default=0.5)
    ap.add_argument("--no-gate", action="store_true", help="SMOKE ONLY: skip the load gate")
    a = ap.parse_args()
    cases = a.cases.split(",")
    regimes = a.regimes.split(",")
    built = {c: build(c, a.cc) for c in cases}            # ALL arms built before ANY timing
    os.makedirs(os.path.dirname(a.out), exist_ok=True)
    try:
        cpu = [l.split(":", 1)[1].strip() for l in open("/proc/cpuinfo") if l.startswith("model name")][0]
    except Exception:
        cpu = platform.processor()
    ccv = subprocess.run([a.cc, "--version"], capture_output=True, text=True).stdout.splitlines()[0]
    gatelog = []
    with open(a.out, "w") as f:
        f.write("#host\t%s\t%s\n#cpu\t%s\n#cc\t%s -O2\n#date\t%s\n#rounds\t%d\t#load_threshold\t%.2f%s\n" %
                (platform.node(), platform.platform(), cpu, ccv, time.strftime("%Y-%m-%d %H:%M:%S"),
                 a.rounds, a.load_threshold, "\t#NO-GATE-SMOKE" if a.no_gate else ""))
        f.write("case\tregime\tarm\tround\tns_per_char\tmatches\tchecksum\tload1_before\treps\tchars\n")
        for c in cases:
            exe, arms = built[c]
            for rg in regimes:
                l = loadavg() if a.no_gate else wait_for_quiet(a.load_threshold, a.max_load_wait, gatelog)
                r = subprocess.run([exe, os.path.join(OUT, "subj_%s.bin" % rg), str(a.reps), str(a.rounds)],
                                   capture_output=True, text=True)
                if r.returncode:
                    raise SystemExit("bench %s/%s failed rc=%d: %s" % (c, rg, r.returncode, r.stderr[-800:]))
                head = r.stdout.splitlines()[0]
                kv = dict(x.split("=") for x in head.split()[1:])
                for line in r.stdout.splitlines()[1:]:
                    arm, rnd, ns, cnt, ck = line.split("\t")
                    f.write("\t".join([c, rg, arm, rnd, ns, cnt, ck, "%.2f" % l, kv["reps"], kv["chars"]]) + "\n")
                f.flush()
                print("%s/%s done (load1 %.2f, reps %s)" % (c, rg, l, kv["reps"]), flush=True)
    print("wrote", a.out)


if __name__ == "__main__":
    main()
