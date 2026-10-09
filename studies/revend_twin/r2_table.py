#!/usr/bin/env python3
"""r2_table.py TIMING.tsv -> markdown tables (revision 2, lane revrev).
Per cell (name, subject): each arm's value is the median over passes of the
pass's median ns/call, [lo-hi] = the range of the pass medians. Ratios are
form/W1-today and C/B on those medians. Also prints load1 and SMT-sibling
busy ranges over the run."""
import sys, csv, statistics as st, collections
rows = collections.defaultdict(list); loads = []; sib = []
for r in csv.DictReader(open(sys.argv[1]), delimiter="\t"):
    if r.get("rc", "").startswith("ANSWER"): continue
    rows[(r["name"], r["subject"])].append(r); loads.append(float(r["load1"])); sib.append(float(r["sib_busy"]))
print(f"passes: {max(len(v) for v in rows.values())}; load1 per cell min {min(loads):.2f} median {st.median(loads):.2f} max {max(loads):.2f}; "
      f"SMT-sibling busy per cell min {min(sib):.2f} median {st.median(sib):.2f} max {max(sib):.2f}\n")
def arm(rs, a):
    m = [float(r[a + "_med"]) for r in rs if r[a + "_med"] != "-"]
    return (st.median(m), min(m), max(m)) if m else None
def f(x):
    if not x: return "—"
    v = lambda y: f"{y:,.0f}" if y >= 1000 else f"{y:.1f}"
    return f"{v(x[0])} [{v(x[1])}-{v(x[2])}]"
print("| pattern | subject | span | W1-today ns | form C ns | form A ns | form B ns | C/W1 | C/B | C/A |")
print("|---|---|---|---:|---:|---:|---:|---:|---:|---:|")
for (n, s), rs in rows.items():
    o, c, a, b = (arm(rs, k) for k in "ocab")
    q = lambda x, y: f"{x[0]/y[0]:.2f}" if x and y else "—"
    print(f"| `{n}` | {s} | {rs[0]['span']} | {f(o)} | {f(c)} | {f(a)} | {f(b)} | {q(c,o)} | {q(c,b)} | {q(c,a)} |")
