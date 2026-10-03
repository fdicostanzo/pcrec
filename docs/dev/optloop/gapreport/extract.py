#!/usr/bin/env python3
"""[OPT-GAPREPORT] step 1: the bench's published report .tsv -> cells.json.

Reads ONLY the `rank` section (the mixed-class ranking every report group
renders; the `.matrix.tsv` the bench derives is the same query at set grain)
of each report group named on the command line, and keeps every testee's
median/min/max/status per timing cell.  Nothing is re-derived from the
bench's raw ledgers or store (D144 addendum 2 item 1).

    python3 extract.py OUT.json REPORT.tsv [REPORT.tsv ...]

A cell key is (subbench, pattern, regime, form, fact).  `n` is the number of
subjects the set-grain median sums over (the bench's set-grain median is the
SUM over the regime's subjects, cycle1_analysis.md §0).
"""
import json
import re
import sys


def testee_short(t):
    # pcrec_fc719ca4_auto-caps-simdna_utf8 -> pcrec:auto-caps
    # libpcre2_10.46_jit-caps-simdna_utf8 -> libpcre2:jit-caps
    m = re.match(r"([a-z0-9]+)_[^_]+_(.*?)-(?:simdna|simd)(.*)$", t)
    if not m:
        return t
    eng, cfg, tail = m.groups()
    tail = tail.lstrip("_-")
    tail = re.sub(r"(^|[_-])utf8$", "", tail)
    return f"{eng}:{cfg}" + (f"+{tail}" if tail else "")


def main():
    out, paths = sys.argv[1], sys.argv[2:]
    cells = {}
    meta = {}
    for p in paths:
        with open(p, encoding="utf8") as fh:
            head = fh.readline()
            sb = re.search(r"subbench=([^,;]+)", head).group(1)
            ver = re.search(r"version=([^,;]+)", head).group(1)
            floor = re.search(r"floor_pattern: ([^;]+)", head)
            meta[sb] = {"version": ver, "report": p.rsplit("/", 1)[-1],
                        "floor_pattern": floor.group(1).strip() if floor else None}
            fh.readline()
            for line in fh:
                f = line.rstrip("\n").split("\t")
                if len(f) < 13 or f[0] != "rank":
                    continue
                pat, _subj, regime, form, fact, testee, status = f[1:8]
                metric, value, n = f[10], f[11], f[12]
                if metric not in ("median_ns", "min_ns", "max_ns"):
                    continue
                key = "\t".join((sb, pat, regime, form, fact))
                c = cells.setdefault(key, {"n": int(n), "t": {}})
                t = c["t"].setdefault(testee_short(testee),
                                      {"status": status, "id": testee})
                t[metric] = float(value)
    json.dump({"meta": meta, "cells": cells}, open(out, "w"), indent=0,
              sort_keys=True)
    print(f"{len(cells)} cells from {len(paths)} reports", file=sys.stderr)


if __name__ == "__main__":
    main()
