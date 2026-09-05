#!/usr/bin/env python3
"""Interleaved A/B trial driver: for a list of (label, binary+args) arms,
runs ROUNDS rounds, each round invoking every arm once in order (never two
trials of the same arm back to back), collecting one median-per-round
value is wrong -- we want per-CALL ns, so each invocation is trials=1 and
we collect the raw ns across rounds, then report the median over rounds
per arm. Checks load1 before each round; aborts (prints a note, keeps
already-collected rounds) if load1 > 2.0."""
import subprocess
import sys
import re
import statistics
import time

def load1():
    out = subprocess.run(["uptime"], capture_output=True, text=True).stdout
    m = re.search(r"load averages?:\s*([0-9.]+)", out)
    return float(m.group(1)) if m else None

def run_one(argv):
    out = subprocess.run(argv, capture_output=True, text=True).stdout
    m = re.search(r"median_ns_per_set=([0-9.]+)", out)
    return float(m.group(1))

def main():
    import json
    arms = json.loads(sys.argv[1])  # list of [label, [argv...]]
    rounds = int(sys.argv[2]) if len(sys.argv) > 2 else 7
    results = {label: [] for label, _ in arms}
    for r in range(rounds):
        l1 = load1()
        if l1 is not None and l1 > 2.0:
            print("ABORT round %d: load1=%.2f > 2.0" % (r, l1))
            break
        for label, argv in arms:
            v = run_one(argv + ["1"])
            results[label].append(v)
    for label, vals in results.items():
        vals_sorted = sorted(vals)
        med = statistics.median(vals_sorted)
        print("%-20s n=%d median_ns=%.1f min=%.1f max=%.1f spread_pct=%.2f" % (
            label, len(vals_sorted), med, vals_sorted[0], vals_sorted[-1],
            100.0 * (vals_sorted[-1]-vals_sorted[0]) / med if med else 0.0))

if __name__ == "__main__":
    main()
