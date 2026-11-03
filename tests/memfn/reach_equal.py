#!/usr/bin/env python3
"""tests/memfn/reach_equal.py -- REACH EQUALITY between two MF_TRACE pcrec
builds (span_pick.md rev 5.2 §Staging, Witness: "REACH EQUALITY, not
floors"; a stage-1 unit's witness beside byte identity). Opt-in, no make
target; a corpus run is heavy (it takes the box lock through its caller).

  reach_equal.py --ref-bin BASE --bin HEAD --tree TREE
                 [--patterns-file F]... [--gone TABLE:ROW,...] [--arms A;B;...]
                 [--jobs N] [--timeout S] [--limit N]

Both binaries are built with -DMF_TRACE (`make BUILD_DIR=D CFLAGS="-O2 -g
-DMF_TRACE"`). Each compiles every distinct pattern of the corpus (the
working tree's, scripts/emit_sweep.py's enumerate_corpus) plus the patterns
files, at each arm, exactly as emit_sweep's c-default stream does
(`-p rx --features all ARM -o - --pattern P`). Every `MFTRACE REACH` line a
process prints at exit is summed per (arm, line key): a row's `chosen` and
`asked`, and each field/class cell's `n`. The verdict:

  - every key of a SURVIVING row has the same sum at BASE and HEAD, per arm;
  - a row named by --gone has lines at BASE (the declared difference is
    real) and none at HEAD;
  - REACH_DROPPED is 0 on both sides;
  - K35: compiles counted per arm, and fewer than POP_FLOOR distinct
    patterns, or a side whose rows were never chosen, is red.

Independent control: the population is the tree's own corpus and the
committed patterns files; the counts are the kit's own reach counters on
both sides, so a defect that moves a decision moves a sum (a counter both
sides lack is invisible: the --gone control is the one row set this
script expects to differ).
Last line: `== reach_equal DONE rc=N keys=K differ=D ==`.
"""
import argparse
import collections
import concurrent.futures
import os
import re
import subprocess
import sys

POP_FLOOR = 1000
DEFAULT_ARMS = ["", "--engine=vm", "-fmemfn-simd", "-e utf8"]
LINE = re.compile(r"^MFTRACE REACH table=(\S+) row=(\S+) (.*)$")


def load_emit_sweep(tree):
    sys.path.insert(0, os.path.join(tree, "scripts"))
    import emit_sweep
    return emit_sweep


def reach_of(binary, pat, arm, timeout):
    argv = [binary, "-p", "rx", "--features", "all"] + arm.split() + ["-o", "-", "--pattern", pat]
    try:
        r = subprocess.run(argv, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE, timeout=timeout)
    except subprocess.TimeoutExpired:
        return None, "timeout"
    out = collections.Counter()
    dropped = 0
    for ln in r.stderr.decode("utf-8", "replace").splitlines():
        if ln.startswith("MFTRACE REACH_DROPPED n="):
            dropped += int(ln.split("=", 1)[1])
            continue
        m = LINE.match(ln)
        if not m:
            continue
        table, row, rest = m.groups()
        kv = dict(t.split("=", 1) for t in rest.split())
        if "field" in kv:
            out[(table, row, "field=%s class=%s" % (kv["field"], kv["class"]))] += int(kv["n"])
        else:
            out[(table, row, "chosen")] += int(kv["chosen"])
            out[(table, row, "asked")] += int(kv["asked"])
    return out, dropped


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--ref-bin", required=True)
    ap.add_argument("--bin", required=True)
    ap.add_argument("--tree", required=True)
    ap.add_argument("--patterns-file", action="append", default=[])
    ap.add_argument("--gone", default="", help="TABLE:ROW,... rows deleted at HEAD")
    ap.add_argument("--arms", default=";".join(DEFAULT_ARMS), help="`;`-separated arm flag strings")
    ap.add_argument("--jobs", type=int, default=8)
    ap.add_argument("--timeout", type=int, default=60)
    ap.add_argument("--limit", type=int, default=0)
    a = ap.parse_args()
    es = load_emit_sweep(a.tree)
    pats = es.enumerate_corpus(a.bin, a.tree, 60)
    for f in a.patterns_file:
        pats += es.read_patterns_file(f)
    pats = sorted(set(bytes(p[2]) if not isinstance(p[2], str) else p[2].encode("utf-8", "surrogateescape")
                      for p in pats))
    if a.limit:
        pats = pats[:a.limit]
    arms = a.arms.split(";")
    gone = {tuple(g.split(":", 1)) for g in a.gone.split(",") if g}
    problems = []
    if len(pats) < POP_FLOOR and not a.limit:
        problems.append("population %d distinct patterns under POP_FLOOR %d" % (len(pats), POP_FLOOR))
    print("population: %d distinct patterns x %d arms" % (len(pats), len(arms)))
    sums = {s: collections.defaultdict(collections.Counter) for s in ("base", "head")}
    dropped = collections.Counter()
    fails = collections.Counter()
    tasks = [(s, b, arm, p) for arm in arms for p in pats
             for s, b in (("base", a.ref_bin), ("head", a.bin))]
    with concurrent.futures.ThreadPoolExecutor(a.jobs) as ex:
        futs = {ex.submit(reach_of, b, p.decode("utf-8", "surrogateescape"), arm, a.timeout): (s, arm)
                for s, b, arm, p in tasks}
        for f in concurrent.futures.as_completed(futs):
            s, arm = futs[f]
            c, d = f.result()
            if c is None:
                fails[(s, arm)] += 1
                continue
            sums[s][arm].update(c)
            dropped[s] += d
    differ = nkeys = 0
    for arm in arms:
        b, h = sums["base"][arm], sums["head"][arm]
        keys = set(b) | set(h)
        nkeys += len(keys)
        armd = 0
        for k in sorted(keys):
            if (k[0], k[1]) in gone:
                continue
            if b.get(k, 0) != h.get(k, 0):
                armd += 1
                problems.append("arm %r %s/%s %s: base %d head %d" % (arm, k[0], k[1], k[2], b.get(k, 0), h.get(k, 0)))
        differ += armd
        chosen = sum(v for k, v in h.items() if k[2] == "chosen")
        print("arm %-14r keys %d, differing %d, head chosen total %d, timeouts base %d head %d"
              % (arm, len(keys), armd, chosen, fails[("base", arm)], fails[("head", arm)]))
        if chosen == 0:
            problems.append("arm %r: no row chosen at HEAD (an empty population)" % arm)
        if fails[("base", arm)] != fails[("head", arm)]:
            problems.append("arm %r: timeouts differ (base %d, head %d)" % (arm, fails[("base", arm)], fails[("head", arm)]))
    for t, r in sorted(gone):
        at_base = any((t, r) == k[:2] for arm in arms for k in sums["base"][arm])
        at_head = any((t, r) == k[:2] for arm in arms for k in sums["head"][arm])
        print("declared gone %s/%s: lines at base %s, at head %s" % (t, r, at_base, at_head))
        if not at_base:
            problems.append("declared-gone row %s/%s has no line at BASE: the declared difference is vacuous" % (t, r))
        if at_head:
            problems.append("declared-gone row %s/%s still has lines at HEAD" % (t, r))
    for s in ("base", "head"):
        if dropped[s]:
            problems.append("%s: REACH_DROPPED %d" % (s, dropped[s]))
    for p in problems[:200]:
        print("FAIL: " + p)
    rc = 1 if problems else 0
    print("== reach_equal DONE rc=%d keys=%d differ=%d ==" % (rc, nkeys, differ))
    return rc


if __name__ == "__main__":
    sys.exit(main())
