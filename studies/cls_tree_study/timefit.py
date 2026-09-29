#!/usr/bin/env python3
"""timefit.py — does the DP's probe-op model predict the MEASURED ns/char?
(docs/design/cls_tree_design.md §1.2; lane clsdes88, 2026-09-28).

Reads the committed ubuntubudu timing (results/bench_ubuntubudu_20260911.tsv,
gcc, load1 0.10, 11 interleaved rounds) and the committed k53 sweep
(results/sweep_k53.tsv, which carries each policy's `model_ops` and section
count), and reports, per regime:

  * Pearson r and Spearman rho of median ns/char against model_ops and
    against log2(sections), over the 12 sets x 3 policies;
  * WITHIN each set, how often the policy with FEWER model ops is FASTER
    (18 of 36 is a coin);
  * the geometric-mean ratio of each arm to the flat binary search.

Analysis only: no timing is taken here, so it runs anywhere.
"""
import collections
import csv
import math
import statistics as st

COLS = ("set intervals members span lam policy sections text rodata total "
        "model_ro model_ops verify mismatches discovery_s forms").split()


def rows(path, **kw):
    with open(path) as f:
        return list(csv.DictReader((l for l in f if not l.startswith("#")),
                                   delimiter="\t", **kw))


def pearson(x, y):
    mx, my = st.mean(x), st.mean(y)
    sx = sum((a - mx) ** 2 for a in x) ** .5
    sy = sum((b - my) ** 2 for b in y) ** .5
    return sum((a - mx) * (b - my) for a, b in zip(x, y)) / (sx * sy)


def ranks(v):
    s = sorted(v)
    return [s.index(a) for a in v]


def main():
    ns = collections.defaultdict(list)
    for r in rows("results/bench_ubuntubudu_20260911.tsv"):
        ns[(r["set"], r["regime"], r["arm"])].append(float(r["ns_per_char"]))
    sw = {(r["set"], r["lam"]): r
          for r in rows("results/sweep_k53.tsv", fieldnames=COLS)
          if r["set"] != "set"}
    sets = sorted({k[0] for k in ns})
    lams = ("0", "16", "256")
    for reg in ("member", "mixed", "full", "ascii"):
        ops, secs, t = [], [], []
        for s in sets:
            for lam in lams:
                ops.append(float(sw[(s, lam)]["model_ops"]))
                secs.append(math.log2(int(sw[(s, lam)]["sections"])))
                t.append(st.median(ns[(s, reg, "lam" + lam)]))
        wins = n = 0
        for s in sets:
            v = {l: st.median(ns[(s, reg, "lam" + l)]) for l in lams}
            o = {l: float(sw[(s, l)]["model_ops"]) for l in lams}
            for a, b in (("0", "16"), ("16", "256"), ("0", "256")):
                if o[a] != o[b]:
                    n += 1
                    wins += (o[a] > o[b]) == (v[a] > v[b])
        geo = {}
        for arm in ("bitmap1", "lam0", "lam16", "lam256"):
            rs = [st.median(ns[(s, reg, arm)]) / st.median(ns[(s, reg, "refbs")])
                  for s in sets]
            geo[arm] = math.exp(sum(map(math.log, rs)) / len(rs))
        print("%-7s r(ns,ops)=%+.2f rho=%+.2f | r(ns,log2 sec)=%+.2f "
              "rho=%+.2f | fewer-ops-is-faster %d/%d | geo vs refbs: %s"
              % (reg, pearson(ops, t), pearson(ranks(ops), ranks(t)),
                 pearson(secs, t), pearson(ranks(secs), ranks(t)), wins, n,
                 " ".join("%s %.3f" % kv for kv in geo.items())))


if __name__ == "__main__":
    main()
