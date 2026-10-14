#!/usr/bin/env python3
"""R-17 revision 2 (lane r17r5): read the follow-up run (setfind.md §13.4).
WRITTEN, NOT RUN.

    python3 -I summarize_r2.py <L>          (L = run_time_r2.sh's output dir)

Prints, from <L>/times.tsv and <L>/perf/:
  1. THE NOISE BAND: the 95th percentile of med/min over every row (step 2's
     was <= 1.05 on 898 of 910 rows). A ratio inside the band is a TIE.
  2. Per form, per regime group, form/table on RAW ns per call (the verdict
     basis: both forms pay the same driver) and on d_floor, median and worst
     over the cells, with every row where raw and d_floor disagree in sign
     named (C2-6).
  3. THE PER-CELL LOSING SET: for each (cell, form), every regime point where
     it loses to table beyond the band (C2-7); memchr at 800k per cell (C2-8).
  4. THE VERDICT QUESTION: does each stateful/adaptive form beat table at the
     dense controls (dig, lc, bkn, bpr; >= 100k ppm; reset=inf) while keeping
     its sparse wins (0-70k ppm, every cell, every reset)? A form is a
     CANDIDATE iff it has no LOSS beyond the band in any row and a WIN beyond
     the band somewhere (K-1). SIMD forms are also read against the best
     SIMD-off form (D147).
  5. K from the synthetic cells: the largest term count whose best SIMD-off
     form wins in every syn row (the measured boundary, setfind.md §3.3).
  6. The branch counters per call, (form - floor) / calls, where perf ran.
"""
import csv
import os
import statistics
import sys
from collections import defaultdict

DENSE_CONTROLS = {"dig", "lc", "bkn", "bpr"}
STATEFUL = ("mask8_swar", "mask64_swar", "mask64i_swar", "mask64_sse2", "mask64_avx2",
            "ring_swar", "ring_avx2", "adapt_swar", "adapt_avx2", "adapt_mask")
SIMD = {"sse2", "avx2", "mask64_sse2", "mask64_avx2", "ring_avx2", "adapt_avx2"}
SYN_K = {"syn4": 4, "syn5": 5, "syn6": 6, "syn8": 8}


def key_of(r):
    return (r["cell"], r["regime"], r["n"], r["ppm"], r["span"], r["reset"], r["g"], r["align"])


def group_of(r):
    ppm = int(r["ppm"])
    if r["regime"] == "percall":
        return "percall L%s%s" % (r["span"], " odd" if r["align"] == "1" else "")
    if float(r["g"]) > 0:
        return "clustered g%s" % r["g"]
    reset = {"0": "inf", "1": "call"}.get(r["reset"], "k" + r["reset"])
    dens = "sparse" if 0 <= ppm <= 70000 else "dense" if ppm >= 100000 else "subject"
    return "findall %s %s n%s" % (reset, dens, r["n"])


def main():
    if len(sys.argv) != 2:
        sys.exit("usage: summarize_r2.py <L>")
    L = sys.argv[1]
    rows = list(csv.DictReader(open(os.path.join(L, "times.tsv")), delimiter="\t"))
    rows = [r for r in rows if r.get("cell") and r["cell"] != "cell"]
    void = [r for r in rows if r["ck"] != "ok"]
    print("rows %d, void %d" % (len(rows), len(void)))
    ratios = [float(r["ns_per_call_med"]) / float(r["ns_per_call_min"])
              for r in rows if float(r["ns_per_call_min"]) > 0]
    ratios.sort()
    band = ratios[int(0.95 * (len(ratios) - 1))] if ratios else 1.05
    print("noise band (p95 of med/min over %d rows): %.3f" % (len(ratios), band))

    by_key = defaultdict(dict)
    for r in rows:
        by_key[key_of(r)][r["form"]] = r

    # 2. per form, per group: raw and d_floor ratios against table
    agg = defaultdict(lambda: defaultdict(list))
    disagree = []
    losing = defaultdict(list)
    wins = defaultdict(int)
    for k, forms in by_key.items():
        t = forms.get("table")
        if not t:
            continue
        traw, tdf = float(t["ns_per_call_min"]), float(t["d_floor_ns_min"])
        for f, r in forms.items():
            if f in ("table", "floor"):
                continue
            raw = float(r["ns_per_call_min"]) / traw if traw > 0 else float("nan")
            dfl = float(r["d_floor_ns_min"]) / tdf if tdf > 0 else float("nan")
            g = group_of(r)
            agg[f][g].append(raw)
            if (raw - 1) * (dfl - 1) < 0 and abs(raw - 1) > band - 1:
                disagree.append((f, k, raw, dfl))
            if raw > band:
                losing[(k[0], f)].append((g, k[3], round(raw, 3)))
            elif raw < 1 / band:
                wins[f] += 1
    print("\n== form / table, raw ns per call: median / worst per group ==")
    for f in sorted(agg):
        print(f)
        for g in sorted(agg[f]):
            v = agg[f][g]
            print("   %-28s %.2f / %.2f  (%d rows)" % (g, statistics.median(v), max(v), len(v)))
    if disagree:
        print("\n== raw and d_floor disagree in sign (beyond the band) ==")
        for f, k, raw, dfl in disagree:
            print("   %s %s raw %.3f d_floor %.3f" % (f, "/".join(k), raw, dfl))

    print("\n== per-cell losing set (beyond the band) ==")
    for (cell, f), v in sorted(losing.items()):
        print("   %-6s %-13s %s" % (cell, f, ", ".join("%s@%s=%.3f" % x for x in v)))
    print("\n== memchr at 800k per cell ==")
    for k, forms in sorted(by_key.items()):
        if k[3] == "800000" and "memchr" in forms and "table" in forms:
            print("   %-6s %s/%s: %.3f" % (k[0], k[1], k[5],
                  float(forms["memchr"]["ns_per_call_min"]) / float(forms["table"]["ns_per_call_min"])))

    # 4. the verdict question
    print("\n== VERDICT: candidates (no loss beyond the band anywhere, a win somewhere) ==")
    forms_all = sorted({f for fs in by_key.values() for f in fs} - {"table", "floor"})
    for f in forms_all:
        lost = [x for (c, ff), x in losing.items() if ff == f]
        dense_ok = all(not [y for y in losing.get((c, f), []) if "dense" in y[0] and "inf" in y[0]]
                       for c in DENSE_CONTROLS)
        sparse_keep = all(not [y for y in losing.get((c, f), []) if "sparse" in y[0]]
                          for c in {k[0] for k in by_key})
        verdict = "CANDIDATE" if not lost and wins[f] else "no"
        print("   %-13s %-9s dense-controls-ok=%s sparse-kept=%s wins=%d losing-cells=%d%s"
              % (f, verdict, dense_ok, sparse_keep, wins[f], len(lost),
                 "  (stateful)" if f in STATEFUL else ""))
    print("   (SIMD forms: re-read against the best SIMD-off form per row, D147)")
    for k, forms in sorted(by_key.items()):
        base = [float(r["ns_per_call_min"]) for f, r in forms.items()
                if f not in SIMD and f not in ("floor",)]
        if not base:
            continue
        best = min(base)
        for f in SIMD & set(forms):
            x = float(forms[f]["ns_per_call_min"]) / best
            if x > band:
                print("   SIMD loss vs best SIMD-off: %s %s %.3f" % (f, "/".join(k), x))

    # 5. K from the synthetic cells
    print("\n== K: synthetic cells, best SIMD-off non-table form / table, worst row ==")
    for cell, kk in sorted(SYN_K.items(), key=lambda x: x[1]):
        worst = None
        for k, forms in by_key.items():
            if k[0] != cell or "table" not in forms:
                continue
            cand = [float(r["ns_per_call_min"]) for f, r in forms.items()
                    if f not in SIMD and f not in ("table", "floor")]
            if cand:
                x = min(cand) / float(forms["table"]["ns_per_call_min"])
                worst = x if worst is None else max(worst, x)
        print("   %s (K=%d): worst %.3f -> %s" % (cell, kk, worst or float("nan"),
              "wins everywhere" if worst is not None and worst < 1 / band else "does not"))

    # 6. branch counters
    pdir = os.path.join(L, "perf")
    if os.path.isdir(pdir) and any(f.endswith(".csv") for f in os.listdir(pdir)):
        print("\n== branch misses per call, (form - floor) / calls ==")
        data = {}
        for f in os.listdir(pdir):
            if not f.endswith(".csv"):
                continue
            cell, rest = f[:-4].split("_", 1)
            form, ppm = rest.rsplit("_", 1)
            ev = {}
            for line in open(os.path.join(pdir, f)):
                parts = line.strip().split(",")
                if len(parts) > 2 and parts[0].replace(".", "").isdigit():
                    ev[parts[2]] = float(parts[0])
            out = open(os.path.join(pdir, f[:-4] + ".out")).read().split("\t")
            calls = float(out[7]) * float(out[6]) if len(out) > 7 else 1.0   # calls/iter x reps
            data[(cell, form, ppm)] = (ev, calls)
        for (cell, form, ppm), (ev, calls) in sorted(data.items()):
            if form == "floor":
                continue
            fl = data.get((cell, "floor", ppm))
            if not fl:
                continue
            bm = (ev.get("branch-misses", 0) - fl[0].get("branch-misses", 0)) / calls
            br = (ev.get("branches", 0) - fl[0].get("branches", 0)) / calls
            print("   %-4s %-12s %7s ppm: %.3f misses/call, %.2f branches/call" % (cell, form, ppm, bm, br))
    else:
        print("\n(no perf counters in %s)" % pdir)


if __name__ == "__main__":
    main()
