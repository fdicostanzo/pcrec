#!/usr/bin/env python3
"""docs/dev/optloop/rlhbuild/summarize.py -- reads time.sh's times.tsv. Per
(cell, regime, subject, variant) the median over rounds of ns/call; per
(cell, regime) each variant's summed ns over the regime's subjects and its
ratio to base; the R-15 delta new/newm; per-subject extremes of new/base; and
a count check (every variant's match count equals base's on every line)."""
import statistics, sys
from collections import defaultdict

rows = [l.rstrip("\n").split("\t") for l in open(sys.argv[1]) if l.strip() and not l.startswith("#")]
rows = [r for r in rows if len(r) == len(rows[0])]
h = {k: i for i, k in enumerate(rows[0])}
v = defaultdict(list); cnt = defaultdict(set)
for r in rows[1:]:
    k = (r[h["cell"]], r[h["regime"]], r[h["subject"]], r[h["variant"]])
    v[k].append(float(r[h["ns_call"]].split()[0]))
    cnt[k[:3]].add(r[h["cnt"]])
vars_ = [x for x in ["base", "new", "deny", "newm"] if any(k[3] == x for k in v)]
subj = sorted(s for s in {k[:3] for k in v} if all(s + (x,) in v for x in vars_))
bad = [s for s in subj if len(cnt[s]) != 1]
tot = defaultdict(lambda: defaultdict(float)); per = defaultdict(list)
for s in subj:
    med = {x: statistics.median(v[s + (x,)]) for x in vars_}
    for x in vars_: tot[s[:2]][x] += med[x]
    per[s[:2]].append((med["new"] / med["base"], s[2], med))
print("cell\tregime\tn\t" + "\t".join("sum_" + x for x in vars_) + "\tnew/base\tdeny/base\tnewm/base\tnew/newm\tworst_new/base\tbest_new/base\tslower>3%")
for k in sorted(tot):
    t = tot[k]; p = sorted(per[k])
    slow = sum(1 for r, _, _ in p if r > 1.03)
    print("%s\t%s\t%d\t%s\t%.3f\t%.3f\t%.3f\t%.3f\t%.3f (%s)\t%.3f (%s)\t%d" % (
        k[0], k[1], len(p), "\t".join("%.0f" % t[x] for x in vars_),
        t["new"] / t["base"], t["deny"] / t["base"], t["newm"] / t["base"], t["new"] / t["newm"],
        p[-1][0], p[-1][1], p[0][0], p[0][1], slow))
print("count check: %d subject lines, %d with differing match counts across variants" % (len(subj), len(bad)))
for s in bad: print("  COUNT MISMATCH", s, cnt[s])
