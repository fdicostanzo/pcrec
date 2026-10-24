#!/usr/bin/env python3
# docs/dev/lanes/s3_evidence/read_588.py — job 588 (lane s3): s3t_results.tsv -> D172 S3's
# acceptance reading (docs/design/memfn/window_site.md rev 3.3 §6 and Goal 2).
#
# usage: python3 -I read_588.py OUT HEADER_FILE R581_TABLE
#
# THE BAR (Goal 2, §6, the SCALAR layer): per (cell, regime, class), R = med(RTE)/med(DEF); the
#   cell PASSES when R <= 1 + floor, where floor is job 581's floor(PRO) for that cell
#   (R581_TABLE's Table A, column "floor(PRO) rel": a committed artifact, not this run), OR when
#   its per-call delta (med(RTE) - med(DEF)) / calls is within THE PER-CALL LAYOUT ALLOWANCE of its
#   regime (below). NO CAPS: no cell has a limit of its own. The dense-hex KNOWN GAP (window_site.md
#   Goals, a D176 witness: hex8-bounded throughput/dense and search_short/dense) is printed with
#   its reading, KNOWN-GAP, and does not fail the bar. Any other result FAILS; one failing cell
#   fails the bar. Every regime and class is read, `match` included.
# THE PER-CALL LAYOUT ALLOWANCE (Goal 2), measured in THIS run: the DEF arm's text compiled again
#   with other layouts (measure_588.sh's DV1..DV3: function and loop alignment variants, the same C),
#   timed beside it; per regime, A = the largest |med(DVk) - med(DEF)| / calls over every variant,
#   cell and class, in ns per call (calls per pass: one per record in search_short and match, the
#   find-all's rx_search calls, hits + 1, in throughput; read off the subjects' .expect). Printed
#   with the variant and cell that set it; a regime with no variant timed has no allowance (0).
# REPORTED, NOT THE BAR: the SIMD-on layer, Rs = med(RTEs)/med(DEFs), with the same floor and
#   allowance (a SIMD-on loss is a finding for the SIMD thread, §6).
# THE A/A: med(RT2)/med(RTE), this run's own noise beside 581's floor.
# G1 ALPHA of each deny row at both layers (memfn/CLAUDE.md: pcrec's timing vs its own deny):
#   window-search  med(RTE)/med(DEF)    (its deny IS the DEF arm), and RTEs/DEFs
#   window-skip  med(RTE)/med(NOH)    where NOH was timed (its text differs: D-hors fires), and
#            RTEs/NOHs; elsewhere "same text".
# THE MOVER SAMPLE (the S3 review's item E; PART OF THE BAR since the S3 code review r1, main
#   agreed, C10): s3t_sample.tsv, printed under "Mover sample (part of the bar)": per (row,
#   regime, class) R = med(RTE)/med(DEF) and Rs = med(RTEs)/med(DEFs), where an arm built once for
#   both layers (same text) is read for both; its floor is THIS run's A/A in that regime (the
#   largest |med(RT2)/med(RTE) - 1| over §6's cells and classes). Every cell prints PASS (R <= 1 +
#   floor, or its per-call delta within the regime's allowance) or FAIL, every row PASS iff all its
#   cells pass, and every STRATUM (the committed pick's, sample_588.tsv) PASS iff its cells'
#   geometric-mean R is <= 1 + the largest floor of its regimes, or every cell of it passes:
#   NO STRATUM SLOWER THAN DEF BEYOND ITS FLOOR is the bar's sample term (scalar layer; the SIMD
#   layer reported). A row of sample.tsv with no timed cell (dropped by a premise, a compile or the
#   answer gate) FAILS the bar too: a dropped row is never a pass.
# THE D-HORS ADMISSION READING (Frank's ruling 2026-10-23; FINDINGS, NEVER the bar, no default
#   moves): s3t_esh.tsv over esh_588.tsv's sites, printed under "D-hors admission (E[sh])": per
#   site E[sh], max(sh) and the stop mass (esh_588.py, committed in the site file), and per
#   (regime, class) the window-skip G1 alpha med(RTE)/med(NOH) (D-hors over D-one; < 1: D-hors is
#   faster) at the scalar layer and med(RTEs)/med(NOHs) at the SIMD layer, with the same floor as
#   the mover sample; then each site's alphas summarized and SORTED BY E[sh], so a cut-off (if
#   any) is visible.
import csv
import os
import statistics
import sys
from collections import defaultdict

out, header, t581 = sys.argv[1], open(sys.argv[2]).read().rstrip("\n"), sys.argv[3]
REG = ("throughput", "search_short", "match")
CLS = ("real", "none", "dense")
# the dense-hex KNOWN GAP (window_site.md rev 3.3 Goals; a D176 witness, Frank 2026-10-24): read
# and printed, never a pass and never a FAIL of the bar
KNOWN_GAP = {
    ("hex8-bounded", "throughput", "dense"),
    ("hex8-bounded", "search_short", "dense"),
}
VARIANTS = ("DV1", "DV2", "DV3")   # measure_588.sh's DEF layout variants

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


def calls_of(path, g):
    """Calls per pass from a subject's .expect ("ops N hits H hash X"), None if unreadable."""
    try:
        f = open(path).read().split()
        return int(f[1]) if g != "throughput" else int(f[3]) + 1
    except (OSError, IndexError, ValueError):
        return None


def calls(c, g, cl):
    return calls_of("%s/subj/%s.%s.%s.expect" % (out, c, cl, g), g)


# THE PER-CALL LAYOUT ALLOWANCE per regime: (ns per call, variant, cell, class)
allow = {}
for g in REG:
    best = (0.0, None, None, None)
    for c in cells:
        for cl in CLS:
            k, x = calls(c, g, cl), med(c, g, cl, "DEF")
            if not k or x is None:
                continue
            for v in VARIANTS:
                y = med(c, g, cl, v)
                if y is not None and abs(y - x) / k > best[0]:
                    best = (abs(y - x) / k, v, c, cl)
    allow[g] = best


def per_call_ok(c, g, cl, a, b, k=None):
    """(delta ns per call of a over b, within the regime's allowance)."""
    k = k if k is not None else calls(c, g, cl)
    x, y = med(c, g, cl, a), med(c, g, cl, b)
    if not k or x is None or y is None:
        return None, False
    dl = (x - y) / k
    return dl, dl <= allow[g][0]


print(header)
print()
print("## The per-call layout allowance (Goal 2: the DEF arm's own layout variants, this run)")
print()
for g in REG:
    a, v, c, cl = allow[g]
    print("- %s: %.3f ns per call%s" % (g, a, "" if v is None else " (%s on %s/%s)" % (v, c, cl)))
print()
print("## Table: the bar (SCALAR) and the SIMD-on reading")
print()
print("| cell | regime | class | DEF ns/pass | calls | RTE/DEF | floor(581) | delta ns/call | verdict | RT2/RTE (A/A) "
      "| RTEs/DEFs (SIMD-on) | SIMD-on reading | G1 window-search (RTE/DEF) | G1 window-search SIMD (RTEs/DEFs) "
      "| G1 window-skip (RTE/NOH) | G1 window-skip SIMD (RTEs/NOHs) |")
print("|" + "---|" * 16)
fails, sfails, missing, gaps = [], [], [], []
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
            dl, aok = per_call_ok(c, g, cl, "RTE", "DEF")
            ok = R <= 1 + fl or aok
            gap = (c, g, cl) in KNOWN_GAP
            if gap:
                gaps.append("%s %s/%s %.3f" % (c, g, cl, R))
            elif not ok:
                fails.append("%s %s/%s %.3f > %.3f, %s ns/call > %.3f" % (
                    c, g, cl, R, 1 + fl, fmt(dl), allow[g][0]))
            Rs = ratio(c, g, cl, "RTEs", "DEFs")
            dls, saok = per_call_ok(c, g, cl, "RTEs", "DEFs")
            sok = Rs is not None and (Rs <= 1 + fl or saok)
            if Rs is not None and not sok and not gap:
                sfails.append("%s %s/%s %.3f > %.3f" % (c, g, cl, Rs, 1 + fl))
            hors = ratio(c, g, cl, "RTE", "NOH")
            hors_s = ratio(c, g, cl, "RTEs", "NOHs")
            verdict = "KNOWN-GAP" if gap else ("PASS" if R <= 1 + fl else "PASS (allowance)" if ok else "FAIL")
            print("| %s | %s | %s | %.0f | %s | %s | %.3f | %s | %s | %s | %s | %s | %s | %s | %s | %s |" % (
                c, g, cl, med(c, g, cl, "DEF"), calls(c, g, cl), fmt(R), fl, fmt(dl), verdict,
                fmt(ratio(c, g, cl, "RT2", "RTE")), fmt(Rs),
                "-" if Rs is None else ("within" if sok else "SLOWER"), fmt(R), fmt(Rs),
                fmt(hors) if hors is not None else "same text",
                fmt(hors_s) if hors_s is not None else "same text"))
print()
print("## The dense-hex Known gap (D176 witness; reported, not the bar)")
print()
for c, g, cl in sorted(KNOWN_GAP):
    print("- %s %s/%s: RTE/DEF %s, RTEs/DEFs %s" % (c, g, cl, fmt(ratio(c, g, cl, "RTE", "DEF")),
                                                   fmt(ratio(c, g, cl, "RTEs", "DEFs"))))
print()
print("## G1 alpha summary (pcrec's timing vs its own deny; < 1: the row is faster)")
print()
for a, b, name in (("RTE", "DEF", "window-search, scalar"), ("RTEs", "DEFs", "window-search, SIMD-on"),
                   ("RTE", "NOH", "window-skip, scalar"), ("RTEs", "NOHs", "window-skip, SIMD-on")):
    rs = [ratio(c, g, cl, a, b) for c in cells for g in REG for cl in CLS]
    rs = [x for x in rs if x is not None]
    if rs:
        print("- %s: %d cells, geometric mean %.3f, min %.3f, max %.3f" % (
            name, len(rs), statistics.geometric_mean(rs), min(rs), max(rs)))
    else:
        print("- %s: no cell timed (the deny's text equals the routed text everywhere)" % name)
print()
sfile = out + "/s3t_sample.tsv"
sample_fails = []
if not os.path.exists(sfile):
    sample_fails.append("no s3t_sample.tsv (the sample is part of the bar)")
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

    def sdelta(sid, g, cl, a, b):
        """(delta ns per call of a over b, within the regime's allowance)."""
        k = calls_of("%s/ssubj/%s.%s.%s.expect" % (out, sid, cl, g), g)
        x, y = smed(sid, g, cl, a), smed(sid, g, cl, b)
        if not k or x is None or y is None:
            return None, False
        return (x - y) / k, (x - y) / k <= allow.get(g, (0.0,))[0]

    print("## Mover sample (part of the bar)")
    print()
    print("Other cover movers (sample_588.tsv, pick_588.py's stratified pick), each DEF vs routed at both "
          "layers; floor = this run's A/A in the regime. PART OF THE BAR (scalar): every stratum's "
          "geometric-mean RTE/DEF within 1 + its floor, every sample.tsv row timed; cells and rows "
          "print PASS/FAIL; the SIMD layer is reported.")
    print()
    print("| row | stratum | pattern | regime | class | DEF ns/pass | RTE/DEF | floor | delta ns/call | verdict "
          "| RTEs/DEFs (SIMD) | SIMD reading |")
    print("|" + "---|" * 12)
    slow, ssl, nrow = [], [], 0
    rowfail = defaultdict(list)
    strat = defaultdict(list)        # stratum -> [(R, floor)]
    strat_s = defaultdict(list)
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
                dl, aok = sdelta(sid, g, cl, "RTE", "DEF")
                _, saok = sdelta(sid, g, cl, "RTEs", "DEFs")
                rd = "-" if fl is None else ("PASS" if R <= 1 + fl else "PASS (allowance)" if aok else "FAIL")
                sr = "-" if fl is None or Rs is None else ("within" if Rs <= 1 + fl or saok else "SLOWER")
                if fl is not None:
                    strat[st].append((R, fl, rd != "FAIL"))
                    if Rs is not None:
                        strat_s[st].append((Rs, fl))
                if rd == "FAIL" or rd == "-":
                    slow.append("%s %s/%s %.3f" % (sid, g, cl, R))
                    rowfail[sid].append("%s/%s %.3f" % (g, cl, R))
                if sr == "SLOWER":
                    ssl.append("%s %s/%s %.3f" % (sid, g, cl, Rs))
                print("| %s | %s | `%s` | %s | %s | %.0f | %s | %s | %s | %s | %s | %s |" % (
                    sid, st, pat.replace("|", "\\|"), g, cl, smed(sid, g, cl, "DEF"), fmt(R), fmt(fl),
                    fmt(dl), rd, fmt(Rs), sr))
    print()
    print("### Sample rows (PASS iff every cell passes)")
    print()
    for sid in sorted(set(meta) | set(sids)):
        st, pat = meta.get(sid, ("?", "?"))
        if sid not in sids:
            print("- %s %s `%s`: FAIL (no timed cell: dropped by a premise, a compile or the gate)"
                  % (sid, st, pat))
            sample_fails.append("%s dropped" % sid)
        else:
            print("- %s %s `%s`: %s" % (sid, st, pat, "PASS" if not rowfail.get(sid) else
                                        "FAIL (" + "; ".join(rowfail[sid]) + ")"))
    print()
    print("### Sample strata: the bar's term (no stratum slower than DEF beyond its floor or the allowance)")
    print()
    print("| stratum | cells | RTE/DEF gmean [min, max] | floor | verdict | RTEs/DEFs gmean (SIMD, reported) |")
    print("|" + "---|" * 6)
    for st in sorted(strat):
        v = [r for r, _, _ in strat[st]]
        fl = max(f for _, f, _ in strat[st])
        gmv = statistics.geometric_mean(v)
        ok = gmv <= 1 + fl or all(p for _, _, p in strat[st])
        if not ok:
            sample_fails.append("stratum %s %.3f > %.3f" % (st, gmv, 1 + fl))
        vs = [r for r, _ in strat_s.get(st, [])]
        print("| %s | %d | %.3f [%.3f, %.3f] | %.3f | %s | %s |" % (
            st, len(v), gmv, min(v), max(v), fl, "PASS" if ok else "FAIL",
            "%.3f" % statistics.geometric_mean(vs) if vs else "-"))
    print()
    rs = [x for x in (sratio(s_, g, cl, "RTE", "DEF") for s_ in sids for g in REG
                      for cl in ("real", "none", "random")) if x]
    if rs:
        print("- sample, scalar RTE/DEF: %d rows over %d patterns, geometric mean %.3f, min %.3f, max %.3f"
              % (len(rs), len(sids), statistics.geometric_mean(rs), min(rs), max(rs)))
    print("- sample cells FAIL (beyond floor), scalar: %s" % ("; ".join(slow) if slow else "none"))
    print("- sample SLOWER beyond floor, SIMD layer: %s" % ("; ".join(ssl) if ssl else "none"))
    print()
efile = out + "/s3t_esh.tsv"
if os.path.exists(efile):
    ed = defaultdict(list)
    for r in csv.DictReader(open(efile), delimiter="\t"):
        ed[(r["cell"], r["regime"], r["class"], r["arm"])].append(float(r["ns"]))
    emeta = {}
    if os.path.exists(out + "/esh.tsv"):
        for ln in open(out + "/esh.tsv", encoding="utf-8"):
            if ln.strip() and not ln.startswith("#"):
                f = ln.rstrip("\n").split("\t")
                emeta[f[0]] = {"st": f[1], "pat": f[2], "esh": float(f[3]), "max": f[4], "mass": f[5]}
    eaa = {}
    for g in REG:
        v = [abs(x - 1) for x in (ratio(c, g, cl, "RT2", "RTE") for c in cells for cl in CLS) if x]
        eaa[g] = max(v) if v else None

    def emed(sid, g, cl, a):
        v = ed.get((sid, g, cl, a)) or ed.get((sid, g, cl, a.rstrip("s")))
        return statistics.median(v) if v else None

    def eratio(sid, g, cl, a, b):
        x, y = emed(sid, g, cl, a), emed(sid, g, cl, b)
        return x / y if x and y else None

    def flag(x, fl):
        if x is None or fl is None:
            return "-"
        return "SLOWER" if x > 1 + fl else ("FASTER" if x < 1 - fl else "within")

    ESHREG = ("throughput", "search_short")
    ECLS = ("real", "none", "random")
    esids = sorted({k[0] for k in ed}, key=lambda s_: (emeta.get(s_, {}).get("esh", 0), s_))
    print("## D-hors admission (E[sh]) (not the §6 bar)")
    print()
    print("D-hors sites (esh_588.tsv, pick_esh_588.py's pick stratified by E[sh], the expected shift per "
          "probe under the default byte-rate prior), D-hors (RTE) vs D-one (NOH, `--memfn=no-window-skip`) at "
          "both layers; alpha = window-skip's G1 ratio (< 1: D-hors faster); floor = this run's A/A in the "
          "regime; where a site's SIMD-layer text equals its scalar text (a cover artifact carries no SIMD "
          "form) the arm was built and timed once and the SIMD alpha IS the scalar one; FINDINGS for the "
          "manager and Frank, never the bar, no default moves.")
    print()
    print("| site | pattern | E[sh] | max(sh) | stop mass ppm | regime | class | NOH ns/pass | alpha scalar "
          "(RTE/NOH) | floor | reading | alpha SIMD (RTEs/NOHs) | SIMD reading |")
    print("|" + "---|" * 13)
    summ = []
    for sid in esids:
        m = emeta.get(sid, {"pat": "?", "esh": float("nan"), "max": "?", "mass": "?"})
        al, als = [], []
        for g in ESHREG:
            for cl in ECLS:
                A = eratio(sid, g, cl, "RTE", "NOH")
                if A is None:
                    continue
                As = eratio(sid, g, cl, "RTEs", "NOHs")
                fl = eaa.get(g)
                al.append((A, flag(A, fl)))
                if As is not None:
                    als.append((As, flag(As, fl)))
                print("| %s | `%s` | %.3f | %s | %s | %s | %s | %.0f | %s | %s | %s | %s | %s |" % (
                    sid, m["pat"].replace("|", "\\|"), m["esh"], m["max"], m["mass"], g, cl,
                    emed(sid, g, cl, "NOH"), fmt(A), fmt(fl), flag(A, fl), fmt(As), flag(As, fl)))
        summ.append((m["esh"], sid, m, al, als))
    print()
    print("### alpha sorted by E[sh] (geometric mean over regimes and classes; counts of SLOWER/FASTER cells)")
    print()
    print("| E[sh] | site | pattern | max(sh) | stop mass ppm | scalar alpha gmean [min, max] | scalar SLOWER/FASTER "
          "| SIMD alpha gmean [min, max] | SIMD SLOWER/FASTER |")
    print("|" + "---|" * 9)

    def gm(v):
        x = [a for a, _ in v]
        return "%.3f [%.3f, %.3f]" % (statistics.geometric_mean(x), min(x), max(x)) if x else "-"

    def cnt(v):
        return "%d/%d of %d" % (sum(1 for _, f in v if f == "SLOWER"), sum(1 for _, f in v if f == "FASTER"), len(v))

    for e, sid, m, al, als in sorted(summ, key=lambda t: (t[0], t[1])):
        print("| %.3f | %s | `%s` | %s | %s | %s | %s | %s | %s |" % (
            e, sid, m["pat"].replace("|", "\\|"), m["max"], m["mass"], gm(al), cnt(al), gm(als), cnt(als)))
    print()
    print("- E[sh] reading: %d sites live of %d in esh.tsv (findings only; no part of the bar)"
          % (len(esids), len(emeta)))
    print()
if missing:
    print("MISSING: %s" % "; ".join(" ".join(m) for m in missing))
print("SIMD-on reading (reported, not the bar): %s" % (
    "every cell within its scalar limit" if not sfails else "SLOWER: " + "; ".join(sfails)))
print("Known gap (D176 witness, reported, not the bar): %s" % ("; ".join(gaps) if gaps else "none read"))
print("== s3t BAR %s: %d cells read on the scalar layer (allowance ns/call: %s)%s; sample %s" % (
    "PASS" if not fails and not missing and not sample_fails else "FAIL", n,
    ", ".join("%s %.3f" % (g, allow[g][0]) for g in REG),
    "" if not fails else "; FAILING: " + "; ".join(fails),
    "PASS" if not sample_fails else "FAIL: " + "; ".join(sample_fails)))
