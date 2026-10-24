#!/usr/bin/env python3
# docs/dev/lanes/r27b_evidence/read_581.py — job 581: r27b_results.tsv (+ pop.tsv) -> the tables.
#
# usage: python3 -I read_581.py OUT HEADER_FILE
#
# THE READING RULE is 580's (read_r27.py), per arm X in COV, PRO, PRO2, SHF, HRS, PRR, PRF:
#   R = med(X)/med(DEF); AA = med(AA)/med(DEF);
#   floor = max(|AA - 1|, IQR(DEF)/med(DEF), IQR(X)/med(X), 0.02 (UNMEASURED DEFAULT, D149));
#   FASTER if R < 1 - floor, SLOWER if R > 1 + floor, else NULL.
# PAIR reading (X against PRO, the no-shift form): R = med(X)/med(PRO), floor = max(|PRO2/PRO - 1|
#   (the A/A pair of the NEW text), IQR(PRO)/med(PRO), IQR(X)/med(X), 0.02).
# R-27.1's bar, read here per arm: no real/none throughput or search_short cell SLOWER than DEF, and
# the dense class not slower than COV; and, new in 581 (T9), the `match` regime is flagged by the
# same SLOWER test (any class).
# Absolute columns: ns/pass is the median ns of one pass; ns/B divides by the subject bytes (for the
# record regimes, the sum of the record bytes). The floor is also printed in absolute terms.
# The PREDICTOR section ties pop.tsv's class-independent default-prior predictions to which cells
# the shifted forms (SHF, HRS) win or lose against PRO.
import csv
import statistics
import sys
from collections import defaultdict

out = sys.argv[1]
header = open(sys.argv[2]).read().rstrip("\n")
REG = ("throughput", "search_short", "match")
CLS = ("real", "none", "dense")
ARMS = ("COV", "AA", "PRO", "PRO2", "SHF", "HRS", "PRR", "PRF")


def q(v):
    v = sorted(v)
    m = statistics.median(v)
    qs = statistics.quantiles(v, n=4, method="inclusive") if len(v) >= 4 else [v[0], m, v[-1]]
    return m, qs[2] - qs[0]


d = defaultdict(list)
nbytes = {}
cells = []
for r in csv.DictReader(open(out + "/r27b_results.tsv"), delimiter="\t"):
    d[(r["cell"], r["regime"], r["class"], r["arm"])].append(float(r["ns"]))
    nbytes[(r["cell"], r["regime"], r["class"])] = int(r["bytes"])
    if r["cell"] not in cells:
        cells.append(r["cell"])


def has(c, g, cl, x):
    return (c, g, cl, x) in d


def word(R, fl):
    return "F" if R < 1 - fl else "S" if R > 1 + fl else "-"


print(header)
print()
rows = []        # (c, g, cl, info)
bad = defaultdict(list)
matchbad = defaultdict(list)
pairs = defaultdict(lambda: defaultdict(lambda: [0, 0]))     # cell -> arm -> [FASTER, SLOWER] vs PRO
vsdef = defaultdict(lambda: defaultdict(lambda: [0, 0]))
for c in cells:
    for g in REG:
        for cl in CLS:
            md, idf = q(d[(c, g, cl, "DEF")])
            AA = q(d[(c, g, cl, "AA")])[0] / md
            mc, ic = q(d[(c, g, cl, "COV")])
            mp, ip = q(d[(c, g, cl, "PRO")])
            AAp = q(d[(c, g, cl, "PRO2")])[0] / mp
            nb = nbytes[(c, g, cl)]
            info = {"md": md, "nb": nb, "AA": AA, "AAp": AAp}
            for x in ARMS:
                if not has(c, g, cl, x):
                    continue
                mx, ix = q(d[(c, g, cl, x)])
                fl = max(abs(AA - 1), idf / md, ix / mx, 0.02)
                R = mx / md
                info[x] = {"R": R, "fl": fl, "w": word(R, fl), "ns": mx}
                if x in ("PRO", "SHF", "HRS", "PRR", "PRF", "PRO2"):
                    flp = max(abs(AAp - 1), ip / mp, ix / mx, 0.02)
                    info[x]["RP"], info[x]["flp"], info[x]["wp"] = mx / mp, flp, word(mx / mp, flp)
                if x in ("PRO", "SHF", "HRS", "PRR", "PRF"):
                    if g == "match":
                        if info[x]["w"] == "S":
                            matchbad[x].append("%s/%s/%s %s/DEF %.3f" % (c, g, cl, x, R))
                    elif cl == "dense":
                        flc = max(abs(AA - 1), ic / mc, ix / mx, 0.02)
                        if mx / mc > 1 + flc:
                            bad[x].append("%s/%s/%s %s/COV %.3f" % (c, g, cl, x, mx / mc))
                    elif info[x]["w"] == "S":
                        bad[x].append("%s/%s/%s %s/DEF %.3f" % (c, g, cl, x, R))
                    if g != "match" and x in ("SHF", "HRS", "PRR", "PRF"):
                        pairs[c][x][0] += info[x]["wp"] == "F"
                        pairs[c][x][1] += info[x]["wp"] == "S"
                        vsdef[c][x][0] += info[x]["w"] == "F"
                        vsdef[c][x][1] += info[x]["w"] == "S"
            rows.append((c, g, cl, info))

f3 = lambda x: "%.3f" % x
print("## Table A: ratio to DEF (and the reading F=FASTER S=SLOWER -=NULL) ; floor in absolute terms\n")
print("| cell | regime | class | DEF ns/pass | DEF ns/B | floor(PRO) rel | floor(PRO) ns/pass | floor(PRO) ns/B | " +
      " | ".join(x + "/DEF" for x in ARMS) + " | HRS/PRO | SHF/PRO | PRR/PRO | PRF/PRO | PRO2/PRO (A/A) |")
print("|" + "---|" * (8 + len(ARMS) + 5))
for c, g, cl, i in rows:
    fp = i["PRO"]["fl"]
    cols = []
    for x in ARMS:
        cols.append("%s%s" % (f3(i[x]["R"]), i[x]["w"]) if x in i else "")
    pc = []
    for x in ("HRS", "SHF", "PRR", "PRF"):
        pc.append("%s%s" % (f3(i[x]["RP"]), i[x]["wp"]) if x in i else "")
    pc.append(f3(i["PRO2"]["RP"]) if "PRO2" in i else "")
    print("| %s | %s | %s | %.0f | %.4f | %.3f | %.1f | %.4f | %s | %s |" % (
        c, g, cl, i["md"], i["md"] / i["nb"], fp, fp * i["md"], fp * i["md"] / i["nb"], " | ".join(cols), " | ".join(pc)))
print("\n## Table B: absolute, ns/pass / ns per byte (median of the launches)\n")
print("| cell | regime | class | DEF | " + " | ".join(ARMS) + " |")
print("|" + "---|" * (4 + len(ARMS)))
for c, g, cl, i in rows:
    cols = ["%.0f / %.4f" % (i[x]["ns"], i[x]["ns"] / i["nb"]) if x in i else "" for x in ARMS]
    print("| %s | %s | %s | %.0f / %.4f | %s |" % (c, g, cl, i["md"], i["md"] / i["nb"], " | ".join(cols)))

print("\n## R-27.1's bar per arm (non-match: real/none vs DEF SLOWER, dense vs COV slower)\n")
for x in ("PRO", "SHF", "HRS", "PRR", "PRF"):
    print("%s: %d miss(es)%s" % (x, len(bad[x]), "".join("\n- " + b for b in bad[x])))
print("\n## match regime flagged by the SLOWER test (T9; any class, vs DEF)\n")
for x in ("PRO", "SHF", "HRS", "PRR", "PRF"):
    print("%s: %d SLOWER%s" % (x, len(matchbad[x]), "".join("\n- " + b for b in matchbad[x])))

# ---- the predictor ----------------------------------------------------------------------------
pop = list(csv.DictReader(open(out + "/pop.tsv"), delimiter="\t"))
print("\n## Population counts (measured, per cell and subject class) against the PREDICTOR\n")
print("Predictor: pcrec's default byte-rate prior (tests/findings/default_ppm.tsv) summed per set as "
      "memfn/src/presence.c set_mass does; class-independent. Survival = positions (chain tests) passed "
      "before the first failure.\n")
print("| cell | class | K | stop@ | stop hits/KiB (pred) | verify-fail frac (pred) | mean survival (pred) | pred HRS advance |")
print("|---|---|---|---|---|---|---|---|")
for p in pop:
    print("| %s | %s | %s | %s | %s (%s) | %s (%s) | %s (%s) | %s |" % (
        p["cell"], p["class"], p["K"], p["stop"], p["hits_per_KiB"], p["pred_hits_per_KiB"],
        p["verify_fail"], p["pred_fail"], p["mean_survival"], p["pred_survival"], p["pred_hrs_advance"]))

pred = {}
for p in pop:
    pred[p["cell"]] = (float(p["pred_survival"]), float(p["pred_stop_mass_ppm"]), float(p["pred_hrs_advance"]),
                       float(p["pred_fail"]))
print("\n### Which cells do SHF and HRS win or lose (against PRO; six non-match rows per cell)\n")
print("net = (rows pair-FASTER) - (rows pair-SLOWER) against PRO, pair floor from PRO2/PRO; "
      "vsDEF is the same count of the arm's own reading against DEF.\n")
print("| cell | pred survival | pred stop mass ppm | pred HRS advance | SHF F/S vs PRO | HRS F/S vs PRO | PRR F/S | PRF F/S | SHF F/S vs DEF | HRS F/S vs DEF |")
print("|---|---|---|---|---|---|---|---|---|---|")
lab = {"SHF": {}, "HRS": {}}
for c in cells:
    fs = lambda x: "%d/%d" % tuple(pairs[c][x]) if x in pairs[c] else ""
    fd = lambda x: "%d/%d" % tuple(vsdef[c][x]) if x in vsdef[c] else ""
    for x in ("SHF", "HRS"):
        f, s = pairs[c][x]
        lab[x][c] = "WIN" if f > s else "LOSE" if s > f else "TIE"
    print("| %s | %.4f | %.0f | %.3f | %s %s | %s %s | %s | %s | %s | %s |" % (
        c, pred[c][0], pred[c][1], pred[c][2], fs("SHF"), lab["SHF"][c], fs("HRS"), lab["HRS"][c],
        fs("PRR"), fs("PRF"), fd("SHF"), fd("HRS")))


def best_split(vals, labels):
    """The threshold rule 'WIN iff value >= t' (or <= t) with the fewest contradictions."""
    pts = sorted((vals[c], labels[c], c) for c in vals if labels[c] != "TIE")
    if not pts:
        return None
    cands = sorted(set(v for v, _l, _c in pts))
    best = None
    for t in cands + [max(cands) + 1]:
        for sign in (1, -1):
            wrong = [c for v, l, c in pts if (("WIN" if sign * (v - t) >= 0 else "LOSE") != l)]
            if best is None or len(wrong) < len(best[0]):
                best = (wrong, t, sign)
    return best, len(pts)


print("\n### Separation by a static rule from the masses (honest count of the contradicting cells)\n")
names = (("pred survival", 0), ("pred stop mass", 1), ("pred HRS advance", 2), ("pred fail frac", 3))
for x in ("SHF", "HRS"):
    for nm, k in names:
        vals = {c: pred[c][k] for c in cells}
        r = best_split(vals, lab[x])
        if not r:
            print("- %s by %s: no WIN/LOSE cell" % (x, nm))
            continue
        (wrong, t, sign), npts = r
        nw = sum(1 for c in cells if lab[x][c] == "WIN")
        nl = sum(1 for c in cells if lab[x][c] == "LOSE")
        print("- %s by %s: best threshold rule 'WIN iff value %s %.4g' leaves %d of %d decided cells "
              "contradicting%s  [no-rule baseline: %d contradicting; %s]" % (
                  x, nm, ">=" if sign > 0 else "<=", t, len(wrong), npts,
                  ": " + ", ".join(wrong) if wrong else "", min(nw, nl),
                  "TRIVIAL, all decided cells alike" if min(nw, nl) == 0 else "a rule only counts if it beats this"))
    print("  decided: " + ", ".join("%s=%s" % (c, lab[x][c]) for c in cells))
