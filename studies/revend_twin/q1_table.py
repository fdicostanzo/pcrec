#!/usr/bin/env python3
"""q1_table.py TIMING.tsv -> markdown table. Per cell (name,size,kind): W1 = o,
B = t, denied = d. Values: median over passes of each pass's median (ns);
[lo-hi] = min of mins .. max of per-pass medians (run-to-run range of the pass
medians). ratio = B/W1 on those medians. FLAG: 'within20' if |ratio-1|<=0.20,
'overlap' if the pass-median ranges of the two arms overlap."""
import sys, csv, statistics as st, collections
rows = collections.defaultdict(list); loads = []
for r in csv.DictReader(open(sys.argv[1]), delimiter="\t"):
    rows[(r["name"], r["size"], r["kind"])].append(r); loads.append(float(r["load1"]))
print(f"load1 over the run: min {min(loads):.2f} max {max(loads):.2f} median {st.median(loads):.2f}\n")
print("| pattern | size | tail | W1 today ns | form B ns | W1-denied ns | B/W1 | B-W1 ns | flag |")
print("|---|---|---|---|---|---|---|---|---|")
for k, rs in rows.items():
    def arm(a):
        m = [float(r[a + "_med"]) for r in rs]
        return st.median(m), min(m), max(m)
    o, t, d = arm("o"), arm("t"), arm("d")
    ratio = t[0] / o[0]
    fl = []
    if abs(ratio - 1) <= 0.20: fl.append("within20")
    if not (t[2] < o[1] or o[2] < t[1]): fl.append("overlap")
    f = lambda a: f"{a[0]:.1f} [{a[1]:.1f}-{a[2]:.1f}]"
    print(f"| `{k[0]}` | {k[1]} | {k[2]} | {f(o)} | {f(t)} | {d[0]:.0f} | {ratio:.2f} | {t[0]-o[0]:+.1f} | {','.join(fl)} |")
