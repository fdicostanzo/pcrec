#!/usr/bin/env python3
"""docs/dev/optloop/et1twin/summarize.py -- reads time.sh's times.tsv.
Per (cell, regime, subject): the median over rounds of each variant's
ns/call, the twin/today ratio; per (cell, regime): the summed ns over the
regime's subjects (the bench's cell is the sum over its subjects' calls)
and its ratio, plus the count matched (o and t must agree)."""
import statistics, sys
from collections import defaultdict

rows = [l.rstrip("\n").split("\t") for l in open(sys.argv[1]) if l and not l.startswith("#")]
h = {k: i for i, k in enumerate(rows[0])}
v = defaultdict(list); cnt = {}
for r in rows[1:]:
    k = (r[h["cell"]], r[h["regime"]], r[h["subject"]], r[h["variant"]])
    v[k].append(float(r[h["ns_call"]].split()[0]))
    cnt[k] = r[h["cnt"]]
subj = sorted({k[:3] for k in v})
tot = defaultdict(lambda: [0.0, 0.0]); worst = defaultdict(lambda: (0, ""))
print("cell\tregime\tsubject\tn_o_ns\tt_ns\tt/o\tcnt_o\tcnt_t")
for c, rg, s in subj:
    o = statistics.median(v[(c, rg, s, "o")]); t = statistics.median(v[(c, rg, s, "t")])
    tot[(c, rg)][0] += o; tot[(c, rg)][1] += t
    if t / o > worst[(c, rg)][0]:
        worst[(c, rg)] = (t / o, s)
    if rg == "throughput":
        print("%s\t%s\t%s\t%.1f\t%.1f\t%.3f\t%s\t%s" % (c, rg, s, o, t, t / o, cnt[(c, rg, s, "o")], cnt[(c, rg, s, "t")]))
print()
print("cell\tregime\tsum_o_ns\tsum_t_ns\tt/o\tworst_subject_ratio")
for (c, rg), (o, t) in sorted(tot.items()):
    print("%s\t%s\t%.0f\t%.0f\t%.3f\t%.3f %s" % (c, rg, o, t, t / o, worst[(c, rg)][0], worst[(c, rg)][1]))
