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

  - every (pattern, arm) has the same key->count map at BASE and HEAD
    (per PATTERN, not per sum, so compensating moves between patterns do
    not cancel), a key absent on one side and 0 on the other differing;
  - the ROW SET (rows with any line) of each arm is the same at BASE and
    HEAD less the declared gone rows; the GONE set is DERIVED (rows with
    lines at BASE and none at HEAD, over all arms) and must equal --gone
    exactly, both directions; each gone row's BASE chosen/asked per arm
    is printed (a "zero reach" claim is read from it, not typed);
  - the compile return codes and timeouts: the SETS of failing patterns
    per arm are equal at BASE and HEAD (a pattern failing on both sides
    is counted and printed);
  - REACH_DROPPED is 0 on both sides;
  - K35: compiles counted per arm, and fewer than POP_FLOOR distinct
    patterns, or a side whose rows were never chosen, is red.

Independent control: the population is the tree's own corpus and the
committed patterns files; the counts are the kit's own reach counters on
both sides, so a defect that moves a decision moves a count. The gone set
is derived from the two traces and compared with the declaration.
A --limit run is a SMOKE run: it skips the population floor, so its last
line is `reach_equal: LIMITED rc=N ...` and it exits 0 never (3 when clean,
1 when not): it cannot be read as the verdict.
D187's count rides along: a trace build prints one `MFTRACE KITMASS calls=C
cubes=Q nonnormal=N mask0=M` line at exit (memfn/src/presence.c, trace builds
only; no other MFTRACE reader matches the tag). The lines of every run are
summed and printed as `nonnormal-cubes N mask0-cubes M` before the trailer;
informational, never a verdict (BASE prints none).
Last line: `reach_equal: DONE rc=N keys=K differ=D` (scripts/verdict's trailer).
"""
import argparse
import collections
import concurrent.futures
import os
import re
import subprocess
import sys
import threading

POP_FLOOR = 1000
DEFAULT_ARMS = ["", "--engine=vm", "-fmemfn-simd", "-e utf8"]
LINE = re.compile(r"^MFTRACE REACH table=(\S+) row=(\S+) (.*)$")
KITMASS_LOCK = threading.Lock()
KITMASS = collections.Counter()   # the summed `MFTRACE KITMASS` lines of every trace run (both sides)


def load_emit_sweep(tree):
    sys.path.insert(0, os.path.join(tree, "scripts"))
    import emit_sweep
    return emit_sweep


def reach_of(binary, pat, arm, timeout):
    argv = [binary, "-p", "rx", "--features", "all"] + arm.split() + ["-o", "-", "--pattern", pat]
    try:
        r = subprocess.run(argv, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE, timeout=timeout)
    except subprocess.TimeoutExpired:
        return None, 0, "timeout"
    out = collections.Counter()
    dropped = 0
    for ln in r.stderr.decode("utf-8", "replace").splitlines():
        if ln.startswith("MFTRACE KITMASS "):        # D187's count (HEAD only; BASE has none)
            with KITMASS_LOCK:
                for t in ln.split()[2:]:
                    k, v = t.split("=", 1)
                    KITMASS[k] += int(v)
                KITMASS["runs"] += 1
            continue
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
    return out, dropped, "rc%d" % r.returncode if r.returncode else ""


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--ref-bin", required=True)
    ap.add_argument("--bin", required=True)
    ap.add_argument("--tree", required=True)
    ap.add_argument("--patterns-file", action="append", default=[])
    ap.add_argument("--gone", default="", help="TABLE:ROW,... rows deleted at HEAD (must equal the derived set)")
    ap.add_argument("--arms", default=";".join(DEFAULT_ARMS), help="`;`-separated arm flag strings")
    ap.add_argument("--jobs", type=int, default=8)
    ap.add_argument("--timeout", type=int, default=60)
    ap.add_argument("--limit", type=int, default=0, help="SMOKE: first N patterns; skips the floor, trailer LIMITED")
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
    print("population: %d distinct patterns x %d arms%s" % (len(pats), len(arms), " (LIMITED smoke run)" if a.limit else ""))
    rows = {s: {arm: set() for arm in arms} for s in ("base", "head")}
    gone_base = {arm: collections.Counter() for arm in arms}    # (table,row,chosen|asked) summed at BASE
    chosen_head = collections.Counter()
    dropped = collections.Counter()
    fails = {s: collections.defaultdict(dict) for s in ("base", "head")}   # arm -> {pattern: why}
    pending = {}                       # (arm, pattern) -> (side, counter) of the side that arrived first
    perpat = collections.Counter()     # arm -> patterns whose maps differ
    examples = []
    tasks = [(s, b, arm, p) for arm in arms for p in pats
             for s, b in (("base", a.ref_bin), ("head", a.bin))]
    with concurrent.futures.ThreadPoolExecutor(a.jobs) as ex:
        futs = {ex.submit(reach_of, b, p.decode("utf-8", "surrogateescape"), arm, a.timeout): (s, arm, p)
                for s, b, arm, p in tasks}
        for f in concurrent.futures.as_completed(futs):
            s, arm, p = futs[f]
            c, d, why = f.result()
            dropped[s] += d
            if why:
                fails[s][arm][p] = why
            if c is None:
                continue
            rows[s][arm].update((k[0], k[1]) for k in c)
            if s == "base":
                for k, v in c.items():
                    if (k[0], k[1]) in gone and k[2] in ("chosen", "asked"):
                        gone_base[arm][k] += v
            else:
                chosen_head[arm] += sum(v for k, v in c.items() if k[2] == "chosen")
            other = pending.pop((arm, p), None)
            if other is None:
                pending[(arm, p)] = (s, c)
                continue
            b, h = (c, other[1]) if s == "base" else (other[1], c)
            b = {k: v for k, v in b.items() if (k[0], k[1]) not in gone}
            h = {k: v for k, v in h.items() if (k[0], k[1]) not in gone}
            if b != h:
                perpat[arm] += 1
                if len(examples) < 20:
                    diff = sorted((k, b.get(k), h.get(k)) for k in set(b) | set(h) if b.get(k) != h.get(k))
                    examples.append("arm %r pattern %r: %s" % (arm, p[:60], "; ".join(
                        "%s/%s %s base %s head %s" % (k[0], k[1], k[2], x, y) for k, x, y in diff[:3])))
    differ = nkeys = 0
    for arm in arms:
        armd = perpat[arm]
        differ += armd
        nb, nh = len(rows["base"][arm]), len(rows["head"][arm])
        nkeys += nh
        print("arm %-14r rows base %d head %d, patterns differing %d, head chosen total %d, failing base %d head %d"
              % (arm, nb, nh, armd, chosen_head[arm], len(fails["base"][arm]), len(fails["head"][arm])))
        if armd:
            problems.append("arm %r: %d patterns have a different reach map at HEAD" % (arm, armd))
        if rows["base"][arm] - gone != rows["head"][arm]:
            miss = sorted(rows["base"][arm] - gone - rows["head"][arm])
            new = sorted(rows["head"][arm] - rows["base"][arm])
            problems.append("arm %r: row sets differ beyond the declared gone rows: lost %s, new %s" % (arm, miss, new))
        if chosen_head[arm] == 0:
            problems.append("arm %r: no row chosen at HEAD (an empty population)" % arm)
        fb, fh = fails["base"][arm], fails["head"][arm]
        if fb != fh:
            problems.append("arm %r: failing patterns differ (base %d, head %d; %d only at base, %d only at head, %d differing cause)"
                            % (arm, len(fb), len(fh), len(set(fb) - set(fh)), len(set(fh) - set(fb)),
                               sum(1 for q in set(fb) & set(fh) if fb[q] != fh[q])))
        elif fb:
            print("  arm %r: %d patterns fail identically on both sides (%s)" % (arm, len(fb), ",".join(sorted(set(fb.values())))))
    union_b = set().union(*rows["base"].values())
    union_h = set().union(*rows["head"].values())
    derived = union_b - union_h
    print("derived gone rows (lines at BASE, none at HEAD): %s" % (", ".join("%s/%s" % g for g in sorted(derived)) or "none"))
    if derived != gone:
        problems.append("derived gone set %s != declared %s" % (sorted(derived), sorted(gone)))
    for t, r in sorted(derived | gone):
        for arm in arms:
            print("gone %s/%s arm %r: BASE chosen %d asked %d" % (
                t, r, arm, gone_base[arm][(t, r, "chosen")], gone_base[arm][(t, r, "asked")]))
    for s in ("base", "head"):
        if dropped[s]:
            problems.append("%s: REACH_DROPPED %d" % (s, dropped[s]))
    print("kitmass: runs %d calls %d cubes %d" % (KITMASS["runs"], KITMASS["calls"], KITMASS["cubes"]))
    print("nonnormal-cubes %d mask0-cubes %d" % (KITMASS["nonnormal"], KITMASS["mask0"]))
    for e in examples:
        print("DIFF: " + e)
    for p in problems[:200]:
        print("FAIL: " + p)
    rc = 1 if problems else 0
    if a.limit:
        print("reach_equal: LIMITED rc=%d keys=%d differ=%d (smoke run, not a verdict)" % (rc, nkeys, differ))
        return 1 if rc else 3
    print("reach_equal: DONE rc=%d keys=%d differ=%d" % (rc, nkeys, differ))
    return rc


if __name__ == "__main__":
    sys.exit(main())
