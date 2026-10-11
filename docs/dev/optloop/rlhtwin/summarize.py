#!/usr/bin/env python3
"""docs/dev/optloop/rlhtwin/summarize.py -- reads time.sh's times.tsv.
Per (cell, regime, subject, variant) the median over rounds of ns/call;
per (cell, regime) each variant's summed ns over the regime's subjects and
its ratio to today (o); the CAPTURE of each handoff variant, i.e. the
fraction of the reverse-inner twin's saving (o - r) it achieves,
(o - v) / (o - r); per-subject throughput ratios; and a count check (every
variant's match count must equal today's on every line)."""
import statistics, sys
from collections import defaultdict

rows = [l.rstrip("\n").split("\t") for l in open(sys.argv[1]) if l.strip() and not l.startswith("#")]
h = {k: i for i, k in enumerate(rows[0])}
v = defaultdict(list); cnt = defaultdict(set)
for r in rows[1:]:
    k = (r[h["cell"]], r[h["regime"]], r[h["subject"]], r[h["variant"]])
    v[k].append(float(r[h["ns_call"]].split()[0]))
    cnt[k[:3]].add(r[h["cnt"]])
vars_ = [x for x in ["o", "h1", "h1m", "h2", "r"] if any(k[3] == x for k in v)]
subj = sorted({k[:3] for k in v})
bad = [s for s in subj if len(cnt[s]) != 1]
tot = defaultdict(lambda: defaultdict(float))
print("cell\tregime\tsubject\t" + "\t".join(vars_) + "\t" + "\t".join(x + "/o" for x in vars_[1:]))
for s in subj:
    med = {x: statistics.median(v[s + (x,)]) for x in vars_}
    for x in vars_: tot[s[:2]][x] += med[x]
    if s[1] == "throughput":
        print("\t".join(s) + "\t" + "\t".join("%.0f" % med[x] for x in vars_) + "\t" +
              "\t".join("%.3f" % (med[x] / med["o"]) for x in vars_[1:]))
print()
print("cell\tregime\t" + "\t".join("sum_" + x for x in vars_) + "\t" +
      "\t".join(x + "/o" for x in vars_[1:]) + "\t" +
      "\t".join("capture_" + x for x in vars_[1:-1]))
for (c, rg), t in sorted(tot.items()):
    o, r = t["o"], t["r"]
    print("%s\t%s\t" % (c, rg) + "\t".join("%.0f" % t[x] for x in vars_) + "\t" +
          "\t".join("%.3f" % (t[x] / o) for x in vars_[1:]) + "\t" +
          "\t".join("%.2f" % ((o - t[x]) / (o - r)) if o != r else "-" for x in vars_[1:-1]))
print()
print("count check: %d subject lines, %d with differing match counts across variants%s"
      % (len(subj), len(bad), (": " + ", ".join("/".join(b) for b in bad)) if bad else ""))
