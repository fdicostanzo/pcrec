#!/usr/bin/env python3
"""Parse the syntax@0.1 fullroster report TSV for median_ns per
(pattern, regime, testee), split by capture class (rank_yes=caps,
rank_no=nocaps). Read-only against pcrec-bench."""
import csv
import json
import sys
from collections import defaultdict

TSV = "/Users/fdicostanzo/pcrec-bench/reports/2026-09-27-syntax-0.1-budu-ryzen1600-fullroster-751b9c6d.tsv"

# section -> cap_class
SECTION_CAP = {"rank_yes": "caps", "rank_no": "nocaps"}

data = defaultdict(dict)  # (cap_class, pattern, regime) -> {testee: {"median_ns":..., "rank":..., "status":...}}

with open(TSV, newline="") as f:
    r = csv.reader(f, delimiter="\t")
    header = None
    for row in r:
        if not row:
            continue
        if row[0] == "section":
            header = row
            continue
        sect = row[0]
        if sect not in SECTION_CAP:
            continue
        cap = SECTION_CAP[sect]
        (_, pattern, subject_or_na, regime, form, fact, testee, status, tier,
         rank_or_na, metric, value, n, pass_rate, n_gave_up, n_wrong,
         gave_up_summary, delta_verdict) = row
        if metric not in ("median_ns", "ratio_vs_baseline", "ratio_vs_best"):
            continue
        key = (cap, pattern, regime)
        d = data[key].setdefault(testee, {})
        d["status"] = status
        d["form"] = form
        d["rank"] = rank_or_na
        try:
            d[metric] = float(value)
        except ValueError:
            d[metric] = value

out = {}
for (cap, pattern, regime), testees in data.items():
    out.setdefault(cap, {}).setdefault(pattern, {})[regime] = testees

print(json.dumps(out, indent=1))
print(f"# groups: {len(data)}", file=sys.stderr)
