#!/usr/bin/env python3
"""gen_bases.py -- generate the BASE artifacts (today's all-byte / VM forms)
into out/<case>/.  Slow on \\p{L}/\\p{Xwd} (a minute-plus of pcrec time each),
so it skips anything already present.

  base.c/.h    default axes, prefix bb           (the arm the box is timed on)
  basec.c/.h   the same source, prefix bc        (NULL CONTROL: identical code,
                                                  different address)
  flat.c       -fno-scan-edge -fno-premul-table -fno-anchored-dfa
               -fno-prefilter, prefix bb         (the complete byte tables the
                                                  twin's machine is computed from)
  bigcap.c/.h  --max-emit-bytes raised so the premultiplied table survives
               where the default cap drops it     (prefix bd), when it differs
  vm.c/.h      --engine=vm, prefix bv             (the VM arm, F2 cases)
"""
import concurrent.futures as cf
import os
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
PCREC = os.environ.get("PCREC", os.path.join(HERE, "..", "..", "build", "pcrec"))
OUT = os.path.join(HERE, "out")

# name, pattern, extra pcrec args for the base
CASES = {
    "c1":  (r"[\x{100}-\x{2000}]+", []),
    "c3":  (r"[\x{100}-\x{FFFF}]+", []),
    "nd":  (r"\p{Nd}+", []),
    "l":   (r"\p{L}+", []),
    "xwd": (r"\p{Xwd}+", []),
    "x1":  (r"(?<=[\x{100}-\x{2000}])x", ["--features", "all"]),
    "x2":  (r"(?<![\w\x{C0}-\x{24F}\x{370}-\x{52F}])[\w\x{C0}-\x{24F}\x{370}-\x{52F}]+(?![\w\x{C0}-\x{24F}\x{370}-\x{52F}])", ["--features", "all"]),
}


def run(cmd, log):
    t = time.time()
    r = subprocess.run(cmd, capture_output=True, text=True)
    open(log, "w").write("$ %s\nrc=%d wall=%.1fs\n%s%s" % (" ".join(cmd), r.returncode, time.time() - t, r.stdout, r.stderr))
    return r.returncode


def gen(name, pat, extra, what):
    d = os.path.join(OUT, name)
    os.makedirs(d, exist_ok=True)
    base = [PCREC, "-e", "utf8"] + extra
    jobs = {
        "base": (["-p", "bb", "-o", os.path.join(d, "base.c"), "--pattern", pat], "base.c"),
        "basec": (["-p", "bc", "-o", os.path.join(d, "basec.c"), "--pattern", pat], "basec.c"),
        "flat": (["-p", "bb", "-fno-scan-edge", "-fno-premul-table", "-fno-anchored-dfa", "-fno-prefilter",
                  "-o", os.path.join(d, "flat.c"), "--pattern", pat], "flat.c"),
        "bigcap": (["-p", "bd", "--max-emit-bytes=5000000", "--max-emit-code-bytes=5000000",
                    "-o", os.path.join(d, "bigcap.c"), "--pattern", pat], "bigcap.c"),
        "vm": (["-p", "bv", "--engine=vm", "-o", os.path.join(d, "vm.c"), "--pattern", pat], "vm.c"),
    }
    rcs = {}
    for w in what:
        args, fn = jobs[w]
        if os.path.exists(os.path.join(d, fn)):
            continue
        rcs[w] = run(base + args, os.path.join(d, w + ".log"))
    return name, rcs


if __name__ == "__main__":
    sel = sys.argv[1].split(",") if len(sys.argv) > 1 and sys.argv[1] != "all" else list(CASES)
    plan = {
        "c1": ["base", "basec", "flat"], "c3": ["base", "flat"], "nd": ["base", "basec", "flat"],
        "l": ["base", "basec", "flat"], "xwd": ["base", "basec", "flat"],
        "x1": ["vm", "base"], "x2": ["vm", "base"],
    }
    extra_what = sys.argv[2].split(",") if len(sys.argv) > 2 else []
    with cf.ThreadPoolExecutor(4) as ex:
        futs = [ex.submit(gen, n, CASES[n][0], CASES[n][1], plan[n] + extra_what) for n in sel]
        for f in futs:
            print(f.result(), flush=True)
