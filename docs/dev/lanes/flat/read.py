#!/usr/bin/env python3
"""flat/read.py TIME_LOG -- the slot's reading: one markdown table row per (cell, subject), then per-cell and
overall sums. Reads grid2/time.sh's printed rows (cell subject mode arm ns base delta floor aac spread per_match
verdict). Per arm: ns, % vs the walk, and the letter of time.sh's own verdict (R = LOSS, N = NULL, W = WIN;
NULL when |arm - walk| <= the A/A floor |walk#b - walk|). Floor % = floor / walk.
"""
import sys
from collections import defaultdict

ARMS = ["V1", "F8", "F64", "M64"]
LET = {"LOSS": "R", "NULL": "N", "WIN": "W"}


def main():
    rows = defaultdict(dict)
    base = {}
    for ln in open(sys.argv[1]):
        f = ln.split()
        if len(f) != 12 or f[0] == "cell" or f[0].startswith("#"):
            continue
        c, s, _m, a, ns, b, _d, fl, _aac, _sp, _pm, vd = f
        if a in ARMS:
            rows[(c, s)][a] = (float(ns), LET.get(vd, vd))
            base[(c, s)] = (float(b), float(fl))
    print("| cell | subject | walk ns | floor % | " + " | ".join("%s %% (v)" % a for a in ARMS) + " |")
    print("|---|---|---|---|" + "---|" * len(ARMS))
    cellsum = defaultdict(lambda: defaultdict(float))
    letters = defaultdict(lambda: defaultdict(str))
    for (c, s) in sorted(rows):
        w, fl = base[(c, s)]
        cells = []
        cellsum[c]["walk"] += w
        for a in ARMS:
            ns, v = rows[(c, s)].get(a, (float("nan"), "?"))
            cellsum[c][a] += ns
            letters[c][a] += v
            cells.append("%+.1f %s" % (100 * (ns - w) / w, v))
        print("| %s | %s | %.0f | %.2f | %s |" % (c, s.split("__")[-1], w, 100 * fl / w, " | ".join(cells)))
    print()
    print("| cell | walk ns (sum) | " + " | ".join("%s sum %% / verdicts" % a for a in ARMS) + " |")
    print("|---|---|" + "---|" * len(ARMS))
    tot = defaultdict(float)
    for c in sorted(cellsum):
        w = cellsum[c]["walk"]
        tot["walk"] += w
        out = []
        for a in ARMS:
            tot[a] += cellsum[c][a]
            out.append("%+.1f %s" % (100 * (cellsum[c][a] - w) / w, letters[c][a]))
        print("| %s | %.0f | %s |" % (c, w, " | ".join(out)))
    w = tot["walk"]
    print("| ALL | %.0f | %s |" % (w, " | ".join("%+.1f" % (100 * (tot[a] - w) / w) for a in ARMS)))
    print()
    for a in ARMS:
        n = defaultdict(int)
        for c in letters:
            for ch in letters[c][a]:
                n[ch] += 1
        print("%s: R=%d N=%d W=%d" % (a, n["R"], n["N"], n["W"]))


if __name__ == "__main__":
    main()
