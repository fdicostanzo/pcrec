#!/usr/bin/env python3
# docs/dev/lanes/s3_evidence/read_588.py — job 588 (lane s3): s3t_results.tsv -> D172 S3's
# acceptance reading (docs/design/memfn/window_site.md rev 3.2 §6).
#
# usage: python3 -I read_588.py OUT HEADER_FILE R581_TABLE
#
# THE BAR (§6, the SCALAR layer): per (cell, regime, class), R = med(RTE)/med(DEF); the cell PASSES
#   when R <= 1 + floor, where floor is job 581's floor(PRO) for that cell (R581_TABLE's Table A,
#   column "floor(PRO) rel": a committed artifact, not this run); the FIVE NAMED cells instead pass
#   when R <= their cap (581's ratio plus its floor, §6's table). Any other result FAILS; one
#   failing cell fails the bar. Every regime and class is read, `match` included.
# REPORTED, NOT THE BAR: the SIMD-on layer, Rs = med(RTEs)/med(DEFs), with the same floor and caps
#   (a SIMD-on loss is a finding for the SIMD thread, §6).
# THE A/A: med(RT2)/med(RTE), this run's own noise beside 581's floor.
# G1 ALPHA of each deny row at both layers (memfn/CLAUDE.md: pcrec's timing vs its own deny):
#   wf-find  med(RTE)/med(DEF)    (its deny IS the DEF arm), and RTEs/DEFs
#   wf-hors  med(RTE)/med(NOH)    where NOH was timed (its text differs: D-hors fires), and
#            RTEs/NOHs; elsewhere "same text".
# THE MOVER SAMPLE (the S3 review's item E; FINDINGS, NEVER the bar): s3t_sample.tsv, printed under
#   "Mover sample (not the §6 bar)": per (row, regime, class) R = med(RTE)/med(DEF) and
#   Rs = med(RTEs)/med(DEFs), where an arm built once for both layers (same text) is read for both;
#   its floor is THIS run's A/A in that regime (the largest |med(RT2)/med(RTE) - 1| over §6's
#   cells and classes), and a ratio above 1 + floor is flagged SLOWER.
import csv
import os
import statistics
import sys
from collections import defaultdict

out, header, t581 = sys.argv[1], open(sys.argv[2]).read().rstrip("\n"), sys.argv[3]
REG = ("throughput", "search_short", "match")
CLS = ("real", "none", "dense")
# §6's five named cells: (cell, regime, class) -> cap (581's ratio + its floor)
CAPS = {
    ("hex8-bounded", "throughput", "dense"): 1.551,
    ("hex8-bounded", "search_short", "dense"): 1.159,
    ("file-ext-order", "search_short", "none"): 1.053,
    ("file-ext-order", "match", "real"): 1.059,
    ("file-ext-order", "match", "none"): 1.085,
}

# job 581's floor(PRO) per cell, from its committed Table A
floor581 = {}
cols = None
in_a = False
for ln in open(t581):
    if ln.startswith("## "):
        in_a = ln.startswith("## Table A")
        continue
    if not in_a or not ln.startswith("| "):
        continue
    f = [x.strip() for x in ln.strip().strip("|").split("|")]
    if f[0] == "cell":
        cols = f
        continue
    if cols and len(f) == len(cols) and f[1] in REG and f[2] in CLS:
        floor581[(f[0], f[1], f[2])] = float(f[cols.index("floor(PRO) rel")])

d = defaultdict(list)
cells = []
for r in csv.DictReader(open(out + "/s3t_results.tsv"), delimiter="\t"):
    d[(r["cell"], r["regime"], r["class"], r["arm"])].append(float(r["ns"]))
    if r["cell"] not in cells:
        cells.append(r["cell"])


def med(c, g, cl, a):
    v = d.get((c, g, cl, a))
    return statistics.median(v) if v else None


def ratio(c, g, cl, a, b):
    x, y = med(c, g, cl, a), med(c, g, cl, b)
    return x / y if x and y else None


def fmt(v):
    return "" if v is None else "%.3f" % v


print(header)
print()
print("## Table: the bar (SCALAR) and the SIMD-on reading")
print()
print("| cell | regime | class | DEF ns/pass | RTE/DEF | floor(581) | cap | verdict | RT2/RTE (A/A) "
      "| RTEs/DEFs (SIMD-on) | SIMD-on reading | G1 wf-find (RTE/DEF) | G1 wf-find SIMD (RTEs/DEFs) "
      "| G1 wf-hors (RTE/NOH) | G1 wf-hors SIMD (RTEs/NOHs) |")
print("|" + "---|" * 15)
fails, sfails, missing = [], [], []
n = 0
for c in cells:
    for g in REG:
        for cl in CLS:
            R = ratio(c, g, cl, "RTE", "DEF")
            if R is None:
                missing.append((c, g, cl))
                continue
            n += 1
            fl = floor581.get((c, g, cl))
            if fl is None:
                missing.append((c, g, cl, "no 581 floor"))
                fl = 0.02
            cap = CAPS.get((c, g, cl))
            limit = cap if cap is not None else 1 + fl
            ok = R <= limit
            if not ok:
                fails.append("%s %s/%s %.3f > %.3f" % (c, g, cl, R, limit))
            Rs = ratio(c, g, cl, "RTEs", "DEFs")
            sok = Rs is not None and Rs <= limit
            if Rs is not None and not sok:
                sfails.append("%s %s/%s %.3f > %.3f" % (c, g, cl, Rs, limit))
            hors = ratio(c, g, cl, "RTE", "NOH")
            hors_s = ratio(c, g, cl, "RTEs", "NOHs")
            print("| %s | %s | %s | %.0f | %s | %.3f | %s | %s | %s | %s | %s | %s | %s | %s | %s |" % (
                c, g, cl, med(c, g, cl, "DEF"), fmt(R), fl, fmt(cap), "PASS" if ok else "FAIL",
                fmt(ratio(c, g, cl, "RT2", "RTE")), fmt(Rs),
                "-" if Rs is None else ("within" if sok else "SLOWER"), fmt(R), fmt(Rs),
                fmt(hors) if hors is not None else "same text",
                fmt(hors_s) if hors_s is not None else "same text"))
print()
print("## The five named cells (§6), each capped at 581's ratio plus its floor")
print()
for (c, g, cl), cap in CAPS.items():
    R = ratio(c, g, cl, "RTE", "DEF")
    print("- %s %s/%s: RTE/DEF %s, cap %.3f: %s" % (c, g, cl, fmt(R), cap,
          "-" if R is None else ("within" if R <= cap else "OVER THE CAP")))
print()
print("## G1 alpha summary (pcrec's timing vs its own deny; < 1: the row is faster)")
print()
for a, b, name in (("RTE", "DEF", "wf-find, scalar"), ("RTEs", "DEFs", "wf-find, SIMD-on"),
                   ("RTE", "NOH", "wf-hors, scalar"), ("RTEs", "NOHs", "wf-hors, SIMD-on")):
    rs = [ratio(c, g, cl, a, b) for c in cells for g in REG for cl in CLS]
    rs = [x for x in rs if x is not None]
    if rs:
        print("- %s: %d cells, geometric mean %.3f, min %.3f, max %.3f" % (
            name, len(rs), statistics.geometric_mean(rs), min(rs), max(rs)))
    else:
        print("- %s: no cell timed (the deny's text equals the routed text everywhere)" % name)
print()
sfile = out + "/s3t_sample.tsv"
if os.path.exists(sfile):
    sd = defaultdict(list)
    for r in csv.DictReader(open(sfile), delimiter="\t"):
        sd[(r["cell"], r["regime"], r["class"], r["arm"])].append(float(r["ns"]))
    meta = {}
    if os.path.exists(out + "/sample.tsv"):
        for ln in open(out + "/sample.tsv", encoding="utf-8"):
            if ln.strip() and not ln.startswith("#"):
                f = ln.rstrip("\n").split("\t")
                meta[f[0]] = (f[1], f[2])
    aa = {}
    for g in REG:
        v = [abs(x - 1) for x in (ratio(c, g, cl, "RT2", "RTE") for c in cells for cl in CLS) if x]
        aa[g] = max(v) if v else None

    def smed(sid, g, cl, a):
        v = sd.get((sid, g, cl, a)) or sd.get((sid, g, cl, a.rstrip("s")))
        return statistics.median(v) if v else None

    def sratio(sid, g, cl, a, b):
        x, y = smed(sid, g, cl, a), smed(sid, g, cl, b)
        return x / y if x and y else None

    print("## Mover sample (not the §6 bar)")
    print()
    print("Other cover movers (sample_588.tsv, pick_588.py's stratified pick), each DEF vs routed at both "
          "layers; floor = this run's A/A in the regime; FINDINGS for the manager, never the bar.")
    print()
    print("| row | stratum | pattern | regime | class | DEF ns/pass | RTE/DEF | floor | reading "
          "| RTEs/DEFs (SIMD) | SIMD reading |")
    print("|" + "---|" * 11)
    slow, ssl, nrow = [], [], 0
    sids = sorted({k[0] for k in sd})
    for sid in sids:
        st, pat = meta.get(sid, ("?", "?"))
        for g in REG:
            for cl in ("real", "none", "random"):
                R = sratio(sid, g, cl, "RTE", "DEF")
                if R is None:
                    continue
                nrow += 1
                fl = aa.get(g)
                Rs = sratio(sid, g, cl, "RTEs", "DEFs")
                rd = "-" if fl is None else ("SLOWER" if R > 1 + fl else "within")
                sr = "-" if fl is None or Rs is None else ("SLOWER" if Rs > 1 + fl else "within")
                if rd == "SLOWER":
                    slow.append("%s %s/%s %.3f" % (sid, g, cl, R))
                if sr == "SLOWER":
                    ssl.append("%s %s/%s %.3f" % (sid, g, cl, Rs))
                print("| %s | %s | `%s` | %s | %s | %.0f | %s | %s | %s | %s | %s |" % (
                    sid, st, pat.replace("|", "\\|"), g, cl, smed(sid, g, cl, "DEF"), fmt(R), fmt(fl),
                    rd, fmt(Rs), sr))
    print()
    rs = [x for x in (sratio(s_, g, cl, "RTE", "DEF") for s_ in sids for g in REG
                      for cl in ("real", "none", "random")) if x]
    if rs:
        print("- sample, scalar RTE/DEF: %d rows over %d patterns, geometric mean %.3f, min %.3f, max %.3f"
              % (len(rs), len(sids), statistics.geometric_mean(rs), min(rs), max(rs)))
    print("- sample SLOWER beyond floor, scalar: %s" % ("; ".join(slow) if slow else "none"))
    print("- sample SLOWER beyond floor, SIMD layer: %s" % ("; ".join(ssl) if ssl else "none"))
    print()
if missing:
    print("MISSING: %s" % "; ".join(" ".join(m) for m in missing))
print("SIMD-on reading (reported, not the bar): %s" % (
    "every cell within its scalar limit" if not sfails else "SLOWER: " + "; ".join(sfails)))
print("== s3t BAR %s: %d cells read on the scalar layer%s" % (
    "PASS" if not fails and not missing else "FAIL", n,
    "" if not fails else "; FAILING: " + "; ".join(fails)))
