#!/usr/bin/env python3
"""Per-cell set-grain medians and IQRs for capability@0.1 at four pcrec pins
(25b1984f = batch-1 BEFORE, 8d716693, b1885a83, 6ef76820) x four testees, read from pcrec-bench's own
committed records with pcrec-bench's OWN reducer (`pcrecbench.reduce`, the
functions report.py calls for --grain set), imported read-only
(sys.dont_write_bytecode, so nothing is written into that tree).

IQR: Type-7 over the per-trial set sums; with n = 5, Q1 = x[1], Q3 = x[3]
(the [B84] ledger's own §0.2 convention).  Writes $SCR/cells.json:
  {"pin|testee|pattern|regime": {median, iqr, n_trials, failing: [...],
                                  giveup_codes, per_subject_median: {...}}}
"""
import os, sys, glob, json
sys.dont_write_bytecode = True
BENCH = "/Users/fdicostanzo/pcrec-bench"
sys.path.insert(0, BENCH)
from pcrecbench import reduce as R
SCR = os.environ["SCR"]
PINS = ("25b1984f", "8d716693", "b1885a83", "6ef76820")
TESTEES = ("auto-caps", "auto-nocaps", "vm-caps", "vm-in-caps")
def iqr(xs):
    xs = sorted(xs); n = len(xs)
    def q(p):
        h = (n - 1) * p; lo = int(h); hi = min(lo + 1, n - 1)
        return xs[lo] + (h - lo) * (xs[hi] - xs[lo])
    return q(0.75) - q(0.25) if n else None
out = {}
for pin in PINS:
    for t in TESTEES:
        # 25b1984f has two windows; the batch-1 ledger's BEFORE is the later
        # (2026-09-22) one, so the LATEST record per testee is read.
        path = sorted(glob.glob(f"{BENCH}/store/records/capability@0.1/pcrec_{pin}_{t}-simdna/*.jsonl"))[-1]
        _setup, rows = R.read_record(path)
        for (pat, regime, form), by_subj in R.cells_from_record(rows).items():
            if form != "plain": continue
            c = R.reduce_set_cell(by_subj)
            per = {sid: R.reduce_match_cell(rs) for sid, rs in by_subj.items()}
            out[f"{pin}|{t}|{pat}|{regime}"] = {
                "median": c.median_ns, "iqr": iqr(c.sums) if c.sums else None,
                "n_trials": c.n_trials, "failing": c.failing_subjects,
                "giveup_codes": c.giveup_codes,
                "per_subject_median": {s: m.median_ns for s, m in per.items()},
                "per_subject_outcomes": {s: m.outcome_counts for s, m in per.items()
                                         if m.expectation_failing}}
json.dump(out, open(f"{SCR}/cells.json", "w"), indent=0, sort_keys=True)
print(len(out), "cells")
