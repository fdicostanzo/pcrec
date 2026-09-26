#!/usr/bin/env python3
"""[OPT-LITSCAN] S1 sabotage row (j)'s REACHABILITY RUN (litscan_s1.md §7.1
row (j), R3-11: build it, run it, log the outcome).

Row (j) plants `reseeds = false` on the run-pinned rows. Its only possible
effect is through `src/opt/scanedge.c`'s precondition (8): a chain head may
not be a seed target on a machine whose prefilter reseeds. So the plant is
REACHABLE exactly on an artifact that (1) takes a run-pinned row, (2) has a
forward seed table, and (3) whose forward machine gains a scan edge once
(8) stops firing. This sweeps every distinct corpus `pattern` line and every
pcrec-bench pattern (both auto configs) through the REAL compiler and a
compiler built with the plant, and counts each population.

  REAL=<pcrec> SAB=<pcrec with the (j) plant> BENCH=<pcrec-bench>
  CORPUS=<tree> SCR=<scratch> python3 rowj_reach.py
"""
import os, sys, re, glob, subprocess, collections
from concurrent.futures import ThreadPoolExecutor
E = os.environ


def emit(binp, pat, extra, out):
    r = subprocess.run([binp, "-p", "rx", "--features", "all", "-fcomments", "-o", out]
                       + extra + ["--pattern", pat], capture_output=True, timeout=180)
    return open(out, "rb").read().decode("latin-1") if r.returncode == 0 else None


def fwd_edges(t):
    n, pend = 0, False
    for ln in t.split("\n"):
        if "[OPT-5] SCAN EDGE" in ln:
            pend = True
            continue
        if pend and re.search(r"if \(forward_state ==", ln):
            n += 1
            pend = False
    return n


def one(job):
    i, key, pat, extra = job
    # the SAME basename in two directories: the artifact names its own header
    for d in ("r", "s"):
        os.makedirs(f"{E['SCR']}/{d}/{i}", exist_ok=True)
    a = emit(E["REAL"], pat, extra, f"{E['SCR']}/r/{i}/a.c")
    b = emit(E["SAB"], pat, extra, f"{E['SCR']}/s/{i}/a.c")
    if a is None:
        return key, None
    m = re.search(r'^#define RX_DFA_PREFILTER "([^"]*)"', a, re.M)
    pf = m.group(1) if m else "-"
    return key, dict(pf=pf, seeded="rx_forward_seed_state" in a,
                     real=fwd_edges(a), sab=None if b is None else fwd_edges(b),
                     same=(a == b))


def jobs():
    n = 0
    for p in sorted(glob.glob(os.path.join(E["BENCH"], "bench", "*", "patterns", "*.rx"))):
        pat = open(p, "rb").read().rstrip(b"\n")
        for cfg, extra in (("caps", []), ("nocaps", ["--no-captures"])):
            n += 1
            yield (n, ("bench", p.split(os.sep)[-3] + "/" + os.path.basename(p)[:-3], cfg), pat, extra)
    seen = set()
    for path in sorted(glob.glob(f"{E['CORPUS']}/tests/**/*.rxt", recursive=True)):
        for ln in open(path, "rb").read().split(b"\n"):
            if ln.startswith(b"pattern ") and ln[8:] not in seen:
                seen.add(ln[8:])
                n += 1
                yield (n, ("corpus", ln[8:].decode("latin-1"), "caps"), ln[8:], [])


def main():
    with ThreadPoolExecutor(max_workers=int(E.get("PROCS", "4"))) as ex:
        res = [r for r in ex.map(one, jobs()) if r[1]]
    c = collections.Counter()
    for (pop, key, cfg), d in res:
        run = d["pf"].startswith("run-pinned")
        c[(pop, "P1 run-pinned")] += run
        c[(pop, "P2 run-pinned + forward seed table")] += run and d["seeded"]
        c[(pop, "P3 ... + plant gives a forward scan edge")] += run and d["seeded"] and (d["sab"] or 0) > d["real"]
        c[(pop, "any artifact the plant moves at all")] += not d["same"]
        if run and d["seeded"]:
            print(f"P2 {pop} {cfg} {key!r} pf={d['pf']} edges real={d['real']} sab={d['sab']}")
    for k in sorted(c):
        print(f"{k[0]:7s} {k[1]:45s} {c[k]}")


if __name__ == "__main__":
    main()
