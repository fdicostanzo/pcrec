#!/usr/bin/env python3
"""summarize.py BENCH.tsv [OUT.tsv] -- medians, per-round ranges, ratios against
the all-byte / VM arm as emitted today (bb), the null-control noise floor
(bc vs bb: the same source under another prefix), and answer-identity check.

ratio = median(arm) / median(bb): below 1 the arm is FASTER than what pcrec
emits today.  The noise floor of a cell is the larger of |bc/bb - 1| and the
relative spread of bb's own rounds; a ratio inside it is a tie, not a win.
"""
import collections
import statistics
import sys

path = sys.argv[1]
outp = sys.argv[2] if len(sys.argv) > 2 else None
hdr = []
rows = []
for line in open(path):
    if line.startswith("#"):
        hdr.append(line.rstrip())
    elif not line.startswith("case\t"):
        rows.append(line.rstrip("\n").split("\t"))
cell = collections.defaultdict(lambda: collections.defaultdict(list))
ck = collections.defaultdict(set)
meta = {}
for c, rg, arm, rnd, ns, cnt, chk, l, reps, chars in rows:
    cell[(c, rg)][arm].append(float(ns))
    ck[(c, rg)].add((cnt, chk))
    meta[(c, rg)] = (reps, chars, cnt, l)
ORDER = ["bb", "bc", "bd", "bv", "ia", "ib", "ic"]
out = []
for (c, rg), arms in cell.items():
    med = {a: statistics.median(v) for a, v in arms.items()}
    base = med.get("bb")
    nf = None
    if base:
        spread = (max(arms["bb"]) - min(arms["bb"])) / base
        nc = abs(med["bc"] / base - 1) if "bc" in med else 0.0
        nf = max(spread / 2, nc)
    for a in ORDER:
        if a not in arms:
            continue
        v = arms[a]
        ratio = (med[a] / base) if base else float("nan")
        verdict = ""
        if base and a not in ("bb", "bc"):
            verdict = "FASTER" if ratio < 1 - nf else ("SLOWER" if ratio > 1 + nf else "tie")
        out.append((c, rg, a, "%.3f" % med[a], "%.3f" % min(v), "%.3f" % max(v), "%.3f" % ratio,
                    "%.1f%%" % (100 * nf) if nf is not None else "", verdict,
                    "ok" if len(ck[(c, rg)]) == 1 else "ANSWER-MISMATCH", meta[(c, rg)][2]))
head = "case\tregime\tarm\tmedian_ns_per_char\tmin\tmax\tratio_vs_bb\tnoise_floor\tverdict\tanswers\tmatches"
lines = [head] + ["\t".join(r) for r in out]
txt = "\n".join(hdr + lines) + "\n"
if outp:
    open(outp, "w").write(txt)
print(txt)
