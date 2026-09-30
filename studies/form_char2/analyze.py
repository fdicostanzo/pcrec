#!/usr/bin/env python3
"""[FORM-CHAR2] summarize run.py's TSV: per (witness, mode) median ns/char per arm, the fold/table and
fold/bitmap ratios (median of per-round paired ratios), the fold-vs-foldB NULL ratio (= the noise floor), the
round-to-round IQR/median, and the win count.  Also checks every arm's checksum equals fold's.
Usage: analyze.py RAW.tsv [SIZES.tsv]"""
import csv, sys, statistics as st, collections
rows = list(csv.DictReader(open(sys.argv[1]), delimiter="\t"))
D = collections.defaultdict(lambda: collections.defaultdict(dict))   # (w,mode) -> arm -> round -> ns
CK = collections.defaultdict(set)
for r in rows:
    D[(r["witness"], r["mode"])][r["arm"]][int(r["round"])] = float(r["ns_per_char"])
    CK[(r["witness"], r["mode"], r["round"])].add(r["checksum"])
bad = [k for k, v in CK.items() if len(v) != 1]
print(f"# answer identity: {len(CK)-len(bad)}/{len(CK)} (witness,mode,round) cells have one checksum across all arms; mismatches: {bad[:5]}")
def q(xs, p):
    xs = sorted(xs); i = (len(xs) - 1) * p; lo = int(i); hi = min(lo + 1, len(xs) - 1); return xs[lo] + (xs[hi] - xs[lo]) * (i - lo)
def paired(a, b):  # median of per-round a/b
    return st.median([a[r] / b[r] for r in a if r in b])
print("witness\tmode\tfold_ns\ttable_ns\tbitmap_ns\tfold/table\tfold/bitmap\tnull(foldB/fold)\tfold_IQR%\tfold<table rounds")
agg = collections.defaultdict(list)
for (w, m), arms in D.items():
    f, t, b, fb = arms["fold"], arms["table"], arms["bitmap"], arms["foldB"]
    mf = st.median(f.values()); iqr = (q(list(f.values()), .75) - q(list(f.values()), .25)) / mf * 100
    wins = sum(1 for r in f if f[r] < t[r])
    print(f"{w}\t{m}\t{mf:.3f}\t{st.median(t.values()):.3f}\t{st.median(b.values()):.3f}\t{paired(f,t):.4f}\t{paired(f,b):.4f}\t{paired(fb,f):.4f}\t{iqr:.2f}\t{wins}/{len(f)}")
    agg[m].append((paired(f, t), paired(f, b), abs(paired(fb, f) - 1)))
print("# geometric-ish summary (median across witnesses of the per-witness median paired ratio)")
for m, v in agg.items():
    print(f"{m}\tfold/table median {st.median(x[0] for x in v):.4f}\tfold/bitmap median {st.median(x[1] for x in v):.4f}\tnull |foldB/fold-1| median {st.median(x[2] for x in v):.4f}")
