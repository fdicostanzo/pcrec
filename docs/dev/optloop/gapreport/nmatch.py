#!/usr/bin/env python3
"""[OPT-GAPREPORT]: per-cell subject bytes and expected match counts.

Reads the bench's own INPUT files (never its ledgers): each set's
`manifest_throughput.tsv` (subject lengths) and `expectations.tsv` (the
oracle's `nmatches` per (pattern, subject, regime)), and writes, per
(set, pattern), the throughput regime's total bytes and total matches -- the
denominators for ns/byte and ns/match.  Short-subject-search is one leftmost
search per subject, so its denominator is the subject count the report
already carries.

    python3 nmatch.py /path/to/pcrec-bench/bench > nmatch.json
"""
import csv
import json
import os
import sys

bench = sys.argv[1]
out = {}
for sb in sorted(os.listdir(bench)):
    man = os.path.join(bench, sb, "manifest_throughput.tsv")
    exp = os.path.join(bench, sb, "expectations.tsv")
    if not (os.path.exists(man) and os.path.exists(exp)):
        continue
    size = {r["id"]: int(r["len"]) for r in
            csv.DictReader(open(man), delimiter="\t")}
    acc = {}
    seen = set()
    for r in csv.DictReader(open(exp), delimiter="\t"):
        if r["regime"] != "throughput" or r["subject"] not in size:
            continue
        k = (r["pattern"], r["subject"])
        if k in seen:          # expectations.tsv repeats some rows
            continue
        seen.add(k)
        a = acc.setdefault(r["pattern"], {"bytes": 0, "matches": 0, "subjects": 0})
        a["bytes"] += size[r["subject"]]
        a["subjects"] += 1
        nm = r["nmatches"]
        a["matches"] += int(nm) if nm.isdigit() else 0
    out["email-specimen" if sb == "email" else sb] = acc
json.dump(out, sys.stdout, indent=0, sort_keys=True)
