#!/usr/bin/env python3
"""docs/design/memfn/r17b_prime/fdb2/routed_census.py -- R17-b' B2's ROUTED-
RECORD COUNT (lane fdb2; r17b_prime.md §1.6 [rev3 B5] item 1, §8.1 "the
routed-record floors per (kind, row) from B2").

    routed_census.py --bin TRACE_PCREC --ls-bin PCREC [--every N] [--jobs J]
                     [--floors FILE] [--write FILE] [--arm FLAGS]...

WHAT IT COUNTS. Every corpus pattern (emit_sweep's population, imported from
scripts/emit_sweep.py: `--list-source` over tests/**/*.rxt) compiled by a
pcrec built with -DPCREC_CAND_TRACE, PCREC_MF_ROUTE_TRACE set, under each arm
(default: no flag, `-e utf8`, `--engine=vm`): pcrec's OWN `MFROUTED<TAB>site
<TAB>kind<TAB>row` records, one per defined FIND/PRE site, printed from the
define's REPORT (mf_result.row), never from the kit's trace or counters.

WHAT IT CHECKS (both ways, so a row that stops routing and a row that routes
early are each red; byte identity cannot see either, §1.6):
  - every (site, kind, row) routed cell named in FLOORS holds at least its
    floor (a count that FALLS: SN-1, a routed bit left 0 after its step);
  - every routed record names a row in ROUTED (the rows routed at this step);
    a record from any other row is a row ROUTING EARLY (S922);
  - a record with row `-` (a site rendered by its pre-table form) is counted
    per (site, kind) and printed, never held (that population is the set
    sites and the presence sites, routed at B3b/B4).
--write FILE writes the measured cells as floor(0.9 x measured) (the row
floors' own rule) for a reviewed pin.
"""
import argparse
import collections
import concurrent.futures
import os
import subprocess
import sys

ROUTED = {"D1", "D1c", "D1w"}


def corpus(ls_bin, tree):
    """emit_sweep's own population (scripts/emit_sweep.py `enumerate_corpus`:
    --list-source over tests/**/*.rxt, its escape decode), imported, never
    re-derived."""
    import importlib.util
    spec = importlib.util.spec_from_file_location("emit_sweep", os.path.join(tree, "scripts/emit_sweep.py"))
    es = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(es)
    return sorted({pat for _, _, pat in es.enumerate_corpus(ls_bin, tree, 120)})


def one(binp, tmp, pat, arm, k):
    d = os.path.join(tmp, "c%d" % k)
    os.makedirs(d, exist_ok=True)
    env = dict(os.environ, PCREC_MF_ROUTE_TRACE="1")
    argv = [binp, "-p", "rx", "--features", "all"] + arm + ["-o", os.path.join(d, "o.c"),
                                                            "--pattern", pat]
    try:
        r = subprocess.run(argv, capture_output=True, timeout=60, env=env)
    except subprocess.TimeoutExpired:
        return []
    return [tuple(ln.split("\t")[1:4]) for ln in r.stderr.decode("utf-8", "replace").splitlines()
            if ln.startswith("MFROUTED\t")]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--bin", required=True)
    ap.add_argument("--ls-bin", required=True)
    ap.add_argument("--tree", default=os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../../..")))
    ap.add_argument("--every", type=int, default=1)
    ap.add_argument("--jobs", type=int, default=4)
    ap.add_argument("--floors")
    ap.add_argument("--write")
    ap.add_argument("--arm", action="append")
    ap.add_argument("--tmp", default=os.environ.get("TMPDIR", "/tmp"))
    a = ap.parse_args()
    arms = [x.split() for x in (a.arm or ["", "-e utf8", "--engine=vm"])]
    pats = corpus(a.ls_bin, a.tree)[::a.every]
    cnt = collections.Counter()
    jobs = [(p, arm) for p in pats for arm in arms]
    with concurrent.futures.ThreadPoolExecutor(a.jobs) as ex:
        futs = [ex.submit(one, a.bin, a.tmp, p, arm, k % (a.jobs * 4)) for k, (p, arm) in enumerate(jobs)]
        for f in futs:
            for rec in f.result():
                cnt[rec] += 1
    print("routed_census: %d patterns x %d arms" % (len(pats), len(arms)))
    fails = 0
    for (site, kind, row), n in sorted(cnt.items()):
        print("CELL\t%s\t%s\t%s\t%d" % (site, kind, row, n))
        if row != "-" and row not in ROUTED:
            print("FAIL: row %s decided %d %s/%s site(s): it is not routed at B2 (routing early)"
                  % (row, n, site, kind))
            fails += 1
    if a.floors:
        for ln in open(a.floors):
            if ln.startswith("#") or not ln.strip():
                continue
            site, kind, row, fl = ln.split("\t")[:4]
            got = cnt.get((site, kind, row), 0)
            if got < int(fl):
                print("FAIL: %s/%s/%s routed %d, under its floor %s (a row that stopped routing)"
                      % (site, kind, row, got, fl))
                fails += 1
    if a.write:
        with open(a.write, "w") as fh:
            fh.write("# site\tkind\trow\tfloor (floor(0.9 x measured), routed_census.py)\n")
            for (site, kind, row), n in sorted(cnt.items()):
                if row in ROUTED:
                    fh.write("%s\t%s\t%s\t%d\n" % (site, kind, row, max(1, (9 * n) // 10)))
    print("routed cells %d, failures %d" % (sum(1 for k in cnt if k[2] != "-"), fails))
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
