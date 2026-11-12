#!/usr/bin/env python3
"""tests/ci/cloud_plan.py -- derive the cloud `test` kind's shard table from CI's recorded per-section times
([CLOUD-SUITE] B, requirements 9-11).

  python3 tests/ci/cloud_plan.py (--units tests/ci/measured_test.tsv | --measured sections-*.tsv) [--note TEXT] [--target 600] [--slots 20] [--setup 70]
                                 [--max-shards 60] [--write]

Inputs: --units = the committed measured file tests/ci/cloud_measure.py writes (the reweigh process,
tests/ci/cloud_reweight.sh; a section with no measurement keeps its previous table weight, flagged ESTIMATE, or the
default); or --measured = the `build/ci/sections.tsv` files of recent GREEN CI runs (`gh run download RUN -p 'pcrec-ci-sections-*'`;
scripts/sectiontimes report output). Each section's weight is its MEDIAN complete wall over every file.
The section names and order come from the table being regenerated (--out, cloud_test_shards.tsv); a new TEST_SECTIONS member
is added there by hand first (make test-ci-shards names it), then this reweighs it.

The FLOOR: every section whose own time plus setup exceeds the target cannot be helped by sharding -- no shard
can finish before it does. Each floor section gets a shard of its own (the run's wall is then that section's wall,
named, not a shard that merely happens to hold it). The other sections are balanced by greedy LPT
(tests/ci/shard_rebalance.py) into the SMALLEST number of shards whose estimated wall -- shards started longest
first onto `slots` runners, each paying `setup` seconds (checkout, python, libpcre2 cache, build) -- meets the
target, so more shards than slots appear exactly when setup is small enough that waves still fit. If no count
meets it the best count is used and the report says so.

EXTRAS: the existing table's `# extras=NAME..` header (opt-in gates that are make targets but not TEST_SECTIONS members:
cloudgate-strict, cloudgate-lint) is carried over: they are weighed like sections (measured, else the previous row's weight)
and placed together in ONE extra shard after the balanced ones (tests/ci/check_shards.sh holds that shape).

Output: the table (stdout, or tests/ci/cloud_test_shards.tsv with --write) in the table's own format with an added
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
    ap.add_argument("--measured", nargs="+", default=[])
    ap.add_argument("--units", help="the committed measured file (tests/ci/measured_KIND.tsv)")
    ap.add_argument("--default-s", type=float, default=30.0, help="weight of a section with neither measurement nor old row")
    ap.add_argument("--target", type=float, default=600)
    ap.add_argument("--slots", type=int, default=20)
    ap.add_argument("--setup", type=float, default=70)
    ap.add_argument("--max-shards", type=int, default=60)
    ap.add_argument("--out", default=os.path.join(here, "cloud_test_shards.tsv"))
    ap.add_argument("--note", default="", help="provenance line for the table header (e.g. the CI run ids)")
    ap.add_argument("--write", action="store_true")
    a = ap.parse_args()
    head, rows = sr.load(a.out)
    names = {r[0] for r in rows}
    extras = []
    if os.path.exists(a.out):
        for line in open(a.out):
            if line.startswith("# extras="):
                extras = line.rstrip("\n").split("=", 1)[1].split()
    names |= set(extras)
    m = sr.measured(a.measured, names, True) if a.measured else {}
    if a.units:
        for line in open(a.units):
            c = line.rstrip("\n").split("\t")
            if len(c) >= 6 and c[0] in names and not line.startswith("#") and c[0] != "unit":
                m[c[0]] = (True, float(c[1]), "%s n=%s %s" % (os.path.basename(a.units), c[2], c[5]))
    if not m:
        sys.exit("cloud_plan: give --units FILE or --measured FILE..")
    if a.units and not a.note:
        a.note = " ".join(l[2:].strip() for l in open(a.units) if l.startswith("# runs"))
    old = {}
    if os.path.exists(a.out):
        old = {x[0]: x[2] for x in sr.load(a.out)[1]}
    xrows = []
    for x in extras:
        if x in m:
            xrows.append([x, 0, max(round(m[x][1], 1), 0.5), "ci-measured %s" % m[x][2]])
        else:
            xrows.append([x, 0, old.get(x, a.default_s), "ESTIMATE (no measurement; %s)" % ("previous table weight" if x in old else "default %gs" % a.default_s)])
    missing = [r[0] for r in rows if r[0] not in m] + [x[0] for x in xrows if x[0] not in m]
    for r in rows:
        if r[0] in m:
            complete, wall, label = m[r[0]]
            r[2] = max(round(wall, 1), 0.5)
            r[3] = "ci-measured %s" % label
        else:
            r[2] = old.get(r[0], a.default_s)
            r[3] = "ESTIMATE (no measurement; %s)" % ("previous table weight" if r[0] in old else "default %gs" % a.default_s)
    floor_names = {r[0] for r in rows if r[2] + a.setup > a.target}
    est, nonfloor = {}, {}
    for k in range(max(len(floor_names), 1) + 1, a.max_shards + 1):
        rr, tt = balanced(rows, k, floor_names)
        est[k] = makespan(tt, a.slots, a.setup)
        nonfloor[k] = makespan(tt[len(floor_names):], a.slots, a.setup)
    meet = [k for k in est if nonfloor[k] <= a.target]
    n = min(meet) if meet else min(est, key=lambda k: (nonfloor[k], k))
    n0 = n
    rows, tot = balanced(rows, n, floor_names)
    best = est[n]
    if xrows:    # the extras' own shard, after the balanced ones; its work is one more shard in the wave estimate
        for x in xrows:
            x[1] = n + 1
        rows += xrows
        tot = tot + [sum(x[2] for x in xrows)]
        best = makespan(tot, a.slots, a.setup)
        n += 1
    total = sum(r[2] for r in rows)
    floor = sorted(((r[2], r[0]) for r in rows if r[0] in floor_names), reverse=True)
    if missing:
        print("cloud_plan: UNMEASURED (estimate kept): " + " ".join(missing), file=sys.stderr)
    big = max(rows, key=lambda r: r[2])
    rep = ["cloud_plan: %d sections, %.0f s of section time (%d unmeasured)" % (len(rows), total, len(missing)),
           "cloud_plan: N=%d shards on %d slots, setup %.0f s: estimated wall %.0f s (%.1f min); target %.0f s"
           % (n, a.slots, a.setup, best, best / 60, a.target),
           "cloud_plan: without the floor shards the run would end at %.0f s (%.1f min)%s"
           % (nonfloor[n0], nonfloor[n0] / 60, "" if meet else " -- TARGET NOT MET at any N")]
    for k, t in enumerate(tot, 1):
        rep.append("cloud_plan: shard %d/%d work %.0f s (%.1f min)" % (k, n, t, t / 60))
    rep.append("cloud_plan: INDIVISIBLE FLOOR %.0f s = setup %.0f s + largest unit %s %.0f s" % (a.setup + big[2], a.setup, big[0], big[2]))
    rep.append("cloud_plan: FLOOR (section alone + setup > target %.0f s): %s"
               % (a.target, ", ".join("%s %.0f s" % (nm, w) for w, nm in floor) or "none"))
    out = ["# tests/ci/cloud_test_shards.tsv -- the cloud `test` kind's shard table ([CLOUD-SUITE] B), GENERATED by",
           "# tests/ci/cloud_plan.py from CI's recorded per-section times; same columns and `make test-shard` reader as",
           "# shards.tsv (CISHARD_TABLE=this file). tests/ci/cloud_check.sh holds it to TEST_SECTIONS exactly.",
           "# plan: target=%.0fs slots=%d setup=%.0fs estimated_wall=%.0fs sections_total=%.0fs"
           % (a.target, a.slots, a.setup, best, total),
           "# predicted_shard_s=%d" % round(max(tot)),
           "# indivisible_floor_s=%d (setup %.0fs + largest unit %s %.0fs)" % (round(a.setup + big[2]), a.setup, big[0], big[2]),
           "# unmeasured: %d section(s)%s" % (len(missing), (" -- " + " ".join(missing)) if missing else ""),
           "# measured from: " + (a.note or "(no --note given)"),
           "# floor: " + ("; ".join("%s %.0fs" % (nm, w) for w, nm in floor) or "none"),
           "# ci_scale=1.0"] + (["# extras=" + " ".join(extras)] if extras else []) + ["# shards=%d" % n, "section\tshard\tweight_s\tweight_source"]
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
