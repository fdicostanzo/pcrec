#!/usr/bin/env python3
"""[START-LANDING] rev 2: totals over run_check.sh logs (STUDY).
    sumcheck.py LOG...   -> one line per log: rows, cells, calls, call_diff,
twin_diff, libpcre2 (artifact / twin / NEW_BAD), find-all calls / diffs, and
the rows (name, cfg) with any difference (a control must have some), and
the VACUITY counts: (row, pool) lines that compared no DFA-body call
(`calls=0`), and rows with no call on ANY pool (a row that never exercised
the row's start is no evidence for it)."""
import re, sys
K = ("subjects", "cells", "twin_diff", "calls", "call_diff", "oracle_cells", "orig_vs_pcre2",
     "twin_vs_pcre2", "NEW_BAD", "findall_calls", "findall_diff")
for log in sys.argv[1:]:
    t = dict.fromkeys(K, 0); rows = set(); bad = set(); other = []; zero = 0; rc = {}
    for ln in open(log):
        if "subjects=" not in ln:
            if ln.strip() and not ln.startswith("  "): other.append(ln.strip()[:100])
            continue
        f = ln.split()
        rows.add((f[0], f[1]))
        c = int(re.search(r"\bcalls=(\d+)", ln).group(1)); zero += c == 0
        rc[(f[0], f[1])] = rc.get((f[0], f[1]), 0) + c
        for k in K:
            m = re.search(r"\b%s=(\d+)" % k, ln)
            if m: t[k] += int(m.group(1))
        if any(int(re.search(r"\b%s=(\d+)" % k, ln).group(1)) for k in ("twin_diff", "call_diff", "NEW_BAD", "findall_diff")):
            bad.add((f[0], f[1]))
    print("%s rows=%d %s | rows-with-a-difference=%d | vacuous pool-lines=%d rows=%d%s" % (
        log.rsplit("/", 1)[-1], len(rows), " ".join("%s=%d" % (k, t[k]) for k in K), len(bad),
        zero, sum(v == 0 for v in rc.values()),
        (" other: " + "; ".join(other[:4])) if other else ""))
