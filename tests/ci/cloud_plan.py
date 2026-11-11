#!/usr/bin/env python3
"""tests/ci/cloud_plan.py -- derive the cloud `test` kind's shard table from CI's recorded per-section times
([CLOUD-SUITE] B, requirements 9-11).

  python3 tests/ci/cloud_plan.py --measured sections-*.tsv [--note TEXT] [--target 600] [--slots 20] [--setup 70]
                                 [--max-shards 60] [--write]

Inputs: the `build/ci/sections.tsv` files of recent GREEN CI runs (`gh run download RUN -p 'pcrec-ci-sections-*'`;
scripts/sectiontimes report output). Each section's weight is its MEDIAN complete wall over every file.
The section names and order come from tests/ci/shards.tsv (CI's table, never changed here).

The FLOOR: every section whose own time plus setup exceeds the target cannot be helped by sharding -- no shard
can finish before it does. Each floor section gets a shard of its own (the run's wall is then that section's wall,
named, not a shard that merely happens to hold it). The other sections are balanced by greedy LPT
(tests/ci/shard_rebalance.py) into the SMALLEST number of shards whose estimated wall -- shards started longest
first onto `slots` runners, each paying `setup` seconds (checkout, python, libpcre2 cache, build) -- meets the
target, so more shards than slots appear exactly when setup is small enough that waves still fit. If no count
meets it the best count is used and the report says so.

Output: the table (stdout, or tests/ci/cloud_test_shards.tsv with --write) in shards.tsv's format with an added
`# plan ...` comment block; the report goes to stderr.
"""
import argparse
import heapq
import importlib.util
import os
import sys

here = os.path.dirname(os.path.abspath(__file__))
spec = importlib.util.spec_from_file_location("shard_rebalance", os.path.join(here, "shard_rebalance.py"))
sr = importlib.util.module_from_spec(spec)
spec.loader.exec_module(sr)


def makespan(works, slots, setup):
    """Estimated wall: shards (longest first) run on `slots` runners, each costing setup + its work."""
    free = [0.0] * min(slots, len(works))
    heapq.heapify(free)
    end = 0.0
    for w in sorted(works, reverse=True):
        t = heapq.heappop(free) + setup + w
        end = max(end, t)
        heapq.heappush(free, t)
    return end


def balanced(rows, n, floor_names):
    """Floor sections alone in shards 1..F; the rest LPT-balanced into shards F+1..n."""
    r = [list(x) for x in rows]
    fl = [x for x in r if x[0] in floor_names]
    rest = [x for x in r if x[0] not in floor_names]
    for i, x in enumerate(sorted(fl, key=lambda x: -x[2]), 1):
        x[1] = i
    tot = [x[2] for x in sorted(fl, key=lambda x: -x[2])]
    if rest:
        m = n - len(fl)
        if m < 1:
            return None, None
        t = sr.lpt(rest, m)
        for x in rest:
            x[1] += len(fl)
        tot += t
    return r, tot


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--measured", nargs="+", required=True)
    ap.add_argument("--target", type=float, default=600)
    ap.add_argument("--slots", type=int, default=20)
    ap.add_argument("--setup", type=float, default=70)
    ap.add_argument("--max-shards", type=int, default=60)
    ap.add_argument("--out", default=os.path.join(here, "cloud_test_shards.tsv"))
    ap.add_argument("--note", default="", help="provenance line for the table header (e.g. the CI run ids)")
    ap.add_argument("--write", action="store_true")
    a = ap.parse_args()
    head, rows = sr.load(os.path.join(here, "shards.tsv"))
    names = {r[0] for r in rows}
    m = sr.measured(a.measured, names, True)
    missing = [r[0] for r in rows if r[0] not in m]
    if missing:
        sys.exit("cloud_plan: sections with no measurement in the given files: " + " ".join(missing))
    for r in rows:
        complete, wall, label = m[r[0]]
        r[2] = max(round(wall, 1), 0.5)
        r[3] = "ci-measured %s" % label
    floor_names = {r[0] for r in rows if r[2] + a.setup > a.target}
    est, nonfloor = {}, {}
    for k in range(max(len(floor_names), 1) + 1, a.max_shards + 1):
        rr, tt = balanced(rows, k, floor_names)
        est[k] = makespan(tt, a.slots, a.setup)
        nonfloor[k] = makespan(tt[len(floor_names):], a.slots, a.setup)
    meet = [k for k in est if nonfloor[k] <= a.target]
    n = min(meet) if meet else min(est, key=lambda k: (nonfloor[k], k))
    rows, tot = balanced(rows, n, floor_names)
    best = est[n]
    total = sum(r[2] for r in rows)
    floor = sorted(((r[2], r[0]) for r in rows if r[0] in floor_names), reverse=True)
    rep = ["cloud_plan: %d sections, %.0f s of section time (median of %d files)" % (len(rows), total, len(a.measured)),
           "cloud_plan: N=%d shards on %d slots, setup %.0f s: estimated wall %.0f s (%.1f min); target %.0f s"
           % (n, a.slots, a.setup, est[n], est[n] / 60, a.target),
           "cloud_plan: without the floor shards the run would end at %.0f s (%.1f min)%s"
           % (nonfloor[n], nonfloor[n] / 60, "" if meet else " -- TARGET NOT MET at any N")]
    for k, t in enumerate(tot, 1):
        rep.append("cloud_plan: shard %d/%d work %.0f s (%.1f min)" % (k, n, t, t / 60))
    rep.append("cloud_plan: FLOOR (section alone + setup > target %.0f s): %s"
               % (a.target, ", ".join("%s %.0f s" % (nm, w) for w, nm in floor) or "none"))
    out = ["# tests/ci/cloud_test_shards.tsv -- the cloud `test` kind's shard table ([CLOUD-SUITE] B), GENERATED by",
           "# tests/ci/cloud_plan.py from CI's recorded per-section times; same columns and `make test-shard` reader as",
           "# shards.tsv (CISHARD_TABLE=this file). tests/ci/cloud_check.sh holds it to TEST_SECTIONS exactly.",
           "# plan: target=%.0fs slots=%d setup=%.0fs estimated_wall=%.0fs sections_total=%.0fs"
           % (a.target, a.slots, a.setup, est[n], total),
           "# measured from: " + (a.note or "(no --note given)"),
           "# floor: " + ("; ".join("%s %.0fs" % (nm, w) for w, nm in floor) or "none"),
           "# ci_scale=1.0", "# shards=%d" % n, "section\tshard\tweight_s\tweight_source"]
    out += ["%s\t%d\t%g\t%s" % tuple(r) for r in rows]
    text = "\n".join(out) + "\n"
    print("\n".join(rep), file=sys.stderr)
    if a.write:
        with open(a.out, "w") as f:
            f.write(text)
        print("cloud_plan: wrote %s" % a.out, file=sys.stderr)
    else:
        sys.stdout.write(text)


if __name__ == "__main__":
    main()
