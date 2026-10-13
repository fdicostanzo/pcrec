#!/usr/bin/env python3
"""tests/ci/shard_rebalance.py -- replace tests/ci/shards.tsv's first-pass LOCAL
weights with the runner's MEASURED section times, and re-balance ([CI-SHARD]).

  python3 tests/ci/shard_rebalance.py --measured sections-1.tsv sections-2.tsv ...
  python3 tests/ci/shard_rebalance.py --assign-only      # keep weights, re-balance
  ... add --write to rewrite the table (default: print the proposal, change nothing)

Each --measured file is a CI `build/ci/sections.tsv` (scripts/sectiontimes
report output; the three `pcrec-ci-sections-*` artifacts of one run). A row
with `state` open is a section a timeout killed: its wall is a LOWER bound, so
it is used only if no complete measurement exists and is labeled as such. The
`test-shard` wrapper row itself and make's non-section targets are ignored: only
names already in the table are read. A measured section gets weight_s = wall
seconds ON THE RUNNER and weight_source `ci-measured <file basename>`; a
section not measured keeps its row, so mixed units are possible until every
section has been measured once -- the script says so, and ci_scale is set to 1.0
only when ALL rows are measured (then weights ARE runner seconds).

Balancing is greedy longest-processing-time into N shards (N from the table's
`# shards=` line, or --shards N), ties to the lower shard number; within a
shard rows keep table order (= TEST_SECTIONS order). The table's check
(tests/ci/check_shards.sh) is run by `make test-ci-shards` on the result.
"""
import argparse
import sys

TABLE = __file__.rsplit("/", 1)[0] + "/shards.tsv"


def load(path):
    head, rows = [], []
    with open(path) as f:
        for line in f:
            line = line.rstrip("\n")
            if line.startswith("#"):
                head.append(line)
            elif line.startswith("section\t"):
                continue
            elif line:
                sec, shard, w, src = line.split("\t", 3)
                rows.append([sec, int(shard), float(w), src])
    return head, rows


def measured(paths, names):
    best = {}  # name -> (complete, wall, label)
    for p in paths:
        label = p.rsplit("/", 1)[-1]
        with open(p) as f:
            for line in f:
                c = line.rstrip("\n").split("\t")
                if len(c) < 4 or c[0] not in names:
                    continue
                try:
                    wall = float(c[3])
                except ValueError:
                    continue
                complete = not (len(c) > 4 and c[4] == "open")
                old = best.get(c[0])
                if old is None or (complete and not old[0]):
                    best[c[0]] = (complete, wall, label)
    return best


def lpt(rows, n):
    tot = [0.0] * n
    for r in sorted(rows, key=lambda r: -r[2]):
        k = tot.index(min(tot))
        r[1] = k + 1
        tot[k] += r[2]
    return tot


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--measured", nargs="*", default=[])
    ap.add_argument("--assign-only", action="store_true")
    ap.add_argument("--shards", type=int)
    ap.add_argument("--table", default=TABLE)
    ap.add_argument("--write", action="store_true")
    a = ap.parse_args()
    if not a.measured and not a.assign_only:
        sys.exit("shard_rebalance: give --measured FILE... or --assign-only")
    head, rows = load(a.table)
    n = a.shards
    for h in head:
        if h.startswith("# shards=") and n is None:
            n = int(h.split("=")[1])
    if not n:
        sys.exit("shard_rebalance: no shard count (table has no '# shards=' line; pass --shards)")
    names = {r[0] for r in rows}
    unmeasured = []
    if a.measured:
        m = measured(a.measured, names)
        for r in rows:
            if r[0] in m:
                complete, wall, label = m[r[0]]
                r[2] = max(round(wall, 1), 0.5)
                r[3] = "ci-measured %s%s" % (label, "" if complete else " (OPEN: killed, lower bound)")
            else:
                unmeasured.append(r[0])
    tot = lpt(rows, n)
    all_measured = a.measured and not unmeasured
    out = []
    for h in head:
        if h.startswith("# ci_scale=") and all_measured:
            h = "# ci_scale=1.0"
        if h.startswith("# shards="):
            h = "# shards=%d" % n
        out.append(h)
    # keep table order (rows were loaded in file order; lpt only set the shard)
    out.append("section\tshard\tweight_s\tweight_source")
    for sec, shard, w, src in rows:
        out.append("%s\t%d\t%g\t%s" % (sec, shard, w, src))
    text = "\n".join(out) + "\n"
    if unmeasured:
        print("shard_rebalance: %d of %d sections NOT measured (weights mix runner and local units): %s"
              % (len(unmeasured), len(rows), " ".join(unmeasured)), file=sys.stderr)
    for k, t in enumerate(tot, 1):
        print("shard %d: weight %.0f s" % (k, t), file=sys.stderr)
    if a.write:
        with open(a.table, "w") as f:
            f.write(text)
        print("wrote %s" % a.table, file=sys.stderr)
    else:
        sys.stdout.write(text)


if __name__ == "__main__":
    main()
